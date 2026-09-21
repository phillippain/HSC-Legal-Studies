#!/usr/bin/env python3
"""File new evidence from the Drive inbox into the library, and republish.

    python3 build/ingest.py status
        What is waiting in  Evidence Finder/inbox , whether each file has a Drive
        id yet, whether the library already holds a copy, and the library folders
        it could go in.

    python3 build/ingest.py file "<inbox path>" "<library folder>" [--as "<new name>"] [--tags a,b]
        Move one file from the inbox into  library/<folder>/ , carry its Drive id
        across into data/drive-links.json (a file keeps its id when it moves inside
        the shared drive), and — with --tags — record hand tags for it in
        data/library-tags.txt. Tags are checked against the syllabus.

    python3 build/ingest.py refresh [--commit "<message>"]
        Fold in the nightly Drive map, rescan the library, rebuild evidence.html,
        verify it, and report anything still missing a Drive id or a tag.
        --commit also makes a git commit (pushing is left to GitHub Desktop).

The steps a person — or Claude, via the add-evidence skill — takes between
`status` and `refresh` are the judgement calls: which folder, which tags, and
whether the piece earns an evidence record of its own in evidence/.
"""

import datetime, json, os, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))

EF_CANDIDATES = [
    os.environ.get("EVIDENCE_FINDER", ""),
    "/Users/phillip/Library/CloudStorage/GoogleDrive-phillip.pain@education.nsw.gov.au/"
    "Shared drives/HSC_LS_SSCBWB/Evidence Finder",
    os.path.expanduser("~/mnt/Evidence Finder"),
]
EF = next((c for c in EF_CANDIDATES if c and os.path.isdir(os.path.join(c, "library"))), None)
if not EF:
    sys.exit("Cannot find the Evidence Finder folder (one containing `library`). "
             "Set EVIDENCE_FINDER to its path.")
LIBRARY = os.path.join(EF, "library")
INBOX = os.path.join(EF, "inbox")
LOCAL_MAP = os.path.join(ROOT, "data", "drive-links.json")
TAGS_FILE = os.path.join(ROOT, "data", "library-tags.txt")
LOG = os.path.join(ROOT, "data", "ingest-log.jsonl")
VIDEO = {".mov", ".mp4", ".m4v"}
SKIP = {".DS_Store", "Icon\r", "Thumbs.db", "desktop.ini"}


# --------------------------------------------------------------------- bits

def read_json(path, what):
    """Drive for desktop sometimes refuses to read a file it has just synced
    (EDEADLK, 'resource deadlock avoided'). Retry briefly; then say how to get
    round it rather than fail obscurely."""
    for attempt in range(6):
        try:
            with open(path, encoding="utf-8") as fh:
                return json.load(fh)
        except FileNotFoundError:
            return None
        except (OSError, json.JSONDecodeError) as e:
            last = e
            time.sleep(1.5)
    print(f"  !! could not read {what} ({last}).")
    print(f"     STAGE-AND-COPY: {path}")
    print(f"     (copy it to {os.path.relpath(os.path.join(ROOT, 'data', os.path.basename(path)), ROOT)}"
          " and run again — the copy there is used first)")
    return None


def drive_json(name):
    """A copy in data/ (placed there by hand or by the skill) wins over Drive."""
    local = os.path.join(ROOT, "data", name) if name == "inbox-links.json" else None
    if local and os.path.exists(local):
        return read_json(local, name)
    return read_json(os.path.join(EF, name), name)


def load_local_map():
    m = read_json(LOCAL_MAP, "data/drive-links.json") or {}
    m.setdefault("files", {})
    return m


def save_local_map(m):
    m["count"] = len(m["files"])
    with open(LOCAL_MAP, "w", encoding="utf-8") as fh:
        json.dump(m, fh, ensure_ascii=False, indent=1)


def walk(base):
    out = []
    if not os.path.isdir(base):
        return out
    for d, dirs, names in os.walk(base):
        dirs[:] = sorted(x for x in dirs if not x.startswith("."))
        for n in sorted(names):
            if n in SKIP or n.startswith("."):
                continue
            out.append(os.path.relpath(os.path.join(d, n), base))
    return out


def valid_tags():
    import evidence_lib
    syl = json.load(open(os.path.join(ROOT, "data", "syllabus.json")))
    idx = evidence_lib.syllabus_index(syl)
    ok = {k for k, v in idx.items() if v["kind"] != "theme"}
    return ok | set(syl["topics"])


def log(entry):
    entry["at"] = datetime.datetime.now().isoformat(timespec="seconds")
    with open(LOG, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")


# ------------------------------------------------------------------- status

def status():
    import scan_library as sl
    inbox = walk(INBOX)
    links = (drive_json("inbox-links.json") or {}).get("files", {})
    lib = json.load(open(os.path.join(ROOT, "data", "library.json")))["files"]
    by_key = {}
    for f in lib:
        by_key.setdefault(f["dupe"], []).append(f["path"])

    if not os.path.isdir(INBOX):
        print("No inbox folder yet. It is created by the Apps Script (installTriggers),")
        print(f"or make a folder called `inbox` in {EF}.")
        return
    print(f"INBOX  {len(inbox)} file(s)   ({INBOX})")
    for p in inbox:
        full = os.path.join(INBOX, p)
        size = os.path.getsize(full)
        idinfo = links.get(p, {}).get("id")
        same = by_key.get(sl.dupe_key(os.path.basename(p)), [])
        print(f"  - {p}   [{size/1024:.0f} KB]")
        print(f"      drive id: {idinfo or 'NOT YET — the inbox is noted every 5 minutes; wait, or file it anyway'}")
        if same:
            print(f"      already in library as: {'; '.join(same)}")
    stale = sorted(set(links) - set(inbox))
    if stale:
        print(f"  (inbox-links.json also lists {len(stale)} file(s) no longer in the inbox — already filed)")

    print("\nLIBRARY FOLDERS (file into one of these, or a new sub-folder of one):")
    for top in sorted(os.listdir(LIBRARY)):
        tp = os.path.join(LIBRARY, top)
        if not os.path.isdir(tp) or top.startswith("."):
            continue
        n = len(walk(tp))
        subs = sorted(s for s in os.listdir(tp) if os.path.isdir(os.path.join(tp, s)) and not s.startswith("."))
        print(f"  {top}/  ({n} files)")
        for s in subs:
            print(f"      {top}/{s}/")


# --------------------------------------------------------------------- file

def file_one(src_rel, folder, new_name=None, tags=None):
    src = os.path.join(INBOX, src_rel)
    if not os.path.isfile(src):
        sys.exit(f"Not in the inbox: {src_rel}")
    folder = folder.strip("/")
    if folder.startswith("library/"):
        folder = folder[len("library/"):]
    name = new_name or os.path.basename(src_rel)
    if os.path.splitext(name)[1] == "" and os.path.splitext(src_rel)[1]:
        name += os.path.splitext(src_rel)[1]
    rel = f"{folder}/{name}" if folder else name
    dest = os.path.join(LIBRARY, rel)
    if os.path.exists(dest):
        sys.exit(f"Refused: library/{rel} already exists. Choose another name with --as.")

    if tags:
        ok = valid_tags()
        bad = [t for t in tags if t not in ok]
        if bad:
            sys.exit(f"Refused: not syllabus tags: {', '.join(bad)} (themes never go on library files)")

    os.makedirs(os.path.dirname(dest), exist_ok=True)
    try:
        os.rename(src, dest)
    except PermissionError as e:
        sys.exit(f"Could not move the file ({e}). Moving out of the inbox needs delete "
                 "permission on the Evidence Finder folder.")
    print(f"moved   inbox/{src_rel}  ->  library/{rel}")

    links = (drive_json("inbox-links.json") or {}).get("files", {})
    fid = links.get(src_rel, {}).get("id")
    m = load_local_map()
    if fid:
        m["files"][rel] = fid
        save_local_map(m)
        print(f"linked  {rel}  ->  drive id {fid}")
    else:
        print("no id   the inbox had not been noted yet; the nightly map (or running mapDriveIds) "
              "will pick it up — then run refresh again")

    if tags:
        lines = open(TAGS_FILE, encoding="utf-8").read().splitlines()
        lines = [l for l in lines if l.split("|", 1)[0].strip() != rel]
        lines.append(f"{rel} | {', '.join(tags)}")
        open(TAGS_FILE, "w", encoding="utf-8").write("\n".join(lines) + "\n")
        print(f"tagged  {rel}  |  {', '.join(tags)}")

    log({"action": "file", "from": f"inbox/{src_rel}", "to": f"library/{rel}",
         "id": fid, "tags": tags or []})
    print(f"\nFor an evidence record, use   document: {rel}")


# ------------------------------------------------------------------ refresh

def merge_drive_map():
    """The nightly map is authoritative for what it saw; the local map also
    holds ids carried across by `file` since then. Keep both."""
    local = load_local_map()
    drive = read_json(os.path.join(EF, "drive-links.json"), "the Drive map")
    if not drive:
        print("drive:  using data/drive-links.json as it stands")
        return local
    if drive.get("generated", "") > local.get("generated", ""):
        before = len(local["files"])
        merged = dict(local["files"])
        merged.update(drive.get("files", {}))
        local = {"generated": drive["generated"], "root": drive.get("root"), "files": merged}
        save_local_map(local)
        print(f"drive:  folded in the map from {drive['generated']} "
              f"({before} -> {len(merged)} entries)")
    else:
        print("drive:  local map is as new as the Drive one")
    return local


def run(cmd):
    print("\n$ " + " ".join(cmd[1:] if cmd[0] == sys.executable else cmd))
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    out = (r.stdout + r.stderr).rstrip()
    print(out)
    if r.returncode:
        sys.exit(f"\nFAILED ({r.returncode}). Nothing was committed.")
    return out


def refresh(commit_msg=None):
    m = merge_drive_map()
    py = sys.executable
    run([py, "build/scan_library.py", LIBRARY])
    run([py, "build/evidence_lib.py"])
    run([py, "build/build_evidence.py"])
    run([py, "build/verify_evidence.py"])

    lib = json.load(open(os.path.join(ROOT, "data", "library.json")))["files"]
    ids = m["files"]
    no_id = [f["path"] for f in lib
             if f["path"] not in ids and os.path.splitext(f["path"])[1].lower() not in VIDEO]
    untagged = [f["path"] for f in lib if not f["tags"]]
    waiting = walk(INBOX)
    print("\nREPORT")
    print(f"  library files: {len(lib)}   with Drive id: {len(lib) - len(no_id)}")
    if no_id:
        print(f"  no Drive id yet ({len(no_id)}) — link falls back to the Mac path until the nightly map:")
        for p in no_id[:15]:
            print("    " + p)
    if untagged:
        print(f"  untagged ({len(untagged)}):")
        for p in untagged[:15]:
            print("    " + p)
    if waiting:
        print(f"  still in the inbox ({len(waiting)}): " + "; ".join(waiting))

    if commit_msg:
        who = subprocess.run(["git", "log", "-1", "--format=%an%n%ae"], cwd=ROOT,
                             capture_output=True, text=True).stdout.split("\n")
        subprocess.run(["git", "add", "evidence", "evidence.html", "data/library.json",
                        "data/library-tags.txt", "data/drive-links.json", "data/ingest-log.jsonl"],
                       cwd=ROOT, check=False)
        r = subprocess.run(["git", "-c", f"user.name={who[0]}", "-c", f"user.email={who[1]}",
                            "commit", "-m", commit_msg], cwd=ROOT, capture_output=True, text=True)
        print("\n" + (r.stdout + r.stderr).strip())
        if r.returncode == 0:
            print("Committed. Push it with GitHub Desktop (Push origin) to publish.")
    else:
        print("\nBuilt. Commit and push (GitHub Desktop) to publish.")


# --------------------------------------------------------------------- main

def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return
    cmd, rest = argv[0], argv[1:]

    def opt(flag):
        if flag in rest:
            i = rest.index(flag)
            val = rest[i + 1]
            del rest[i:i + 2]
            return val
        return None

    if cmd == "status":
        status()
    elif cmd == "file":
        new = opt("--as")
        tags = opt("--tags")
        tags = [t.strip() for t in tags.split(",") if t.strip()] if tags else None
        if len(rest) != 2:
            sys.exit('usage: ingest.py file "<inbox path>" "<library folder>" [--as NAME] [--tags a,b]')
        file_one(rest[0], rest[1], new, tags)
    elif cmd == "refresh":
        refresh(opt("--commit"))
    else:
        sys.exit(f"unknown command `{cmd}` (status, file, refresh)")


if __name__ == "__main__":
    main(sys.argv[1:])
