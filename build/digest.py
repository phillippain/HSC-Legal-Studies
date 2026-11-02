#!/usr/bin/env python3
"""Collect what was added to (or changed in) the Evidence Finder since the last digest.

    python3 build/digest.py collect [--since YYYY-MM-DD] [--out PATH] [--site URL]
        Reads evidence/**/*.md, data/syllabus.json, data/drive-links.json and the git
        history, and writes a JSON file of the new and updated cards grouped by course
        topic. Prints a short readable listing to stdout. Read-only: it does not touch
        the saved state, so it can be re-run safely.

    python3 build/digest.py mark PATH_TO_DIGEST.json
        Record the cards in that digest as reported, so the next collect starts after
        them. Run it once the email page has been made.

    python3 build/digest.py status
        Show the saved state (when the digest last ran, how many cards it has reported).

"Since the last digest" means: cards whose `added:` date is on or after the day before
the last run and which have not been reported yet (the one-day look-back catches a card
filed late on the same day as the last run). On the first run it starts from the last
school day, so a Monday run covers Friday to Sunday.

The state lives in data/digest-state.json (git-ignored). Dates are Sydney dates.
"""

import argparse, datetime, json, os, re, subprocess, sys, time, unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVIDENCE = os.path.join(ROOT, "evidence")
STATE = os.path.join(ROOT, "data", "digest-state.json")
DEFAULT_OUT_DIR = os.path.join(ROOT, ".digest")

os.environ["TZ"] = "Australia/Sydney"
try:
    time.tzset()
except AttributeError:
    pass

BULK_COMMIT = 30           # a commit touching more cards than this is a bulk retag, not an edit
HSC_ORDER = ["crime", "humanrights", "family", "shelter"]
Y11_ORDER = ["investigating", "disputes", "changing", "experiences"]
TYPE_LABEL = {"case": "Case law", "legislation": "Legislation", "media": "Media",
              "international": "International instrument", "report": "Report & statistics",
              "document": "Document"}


# ----------------------------------------------------------------- helpers ----
def today():
    return datetime.datetime.now().date()


def prev_school_day(d):
    d = d - datetime.timedelta(days=1)
    while d.weekday() >= 5:
        d -= datetime.timedelta(days=1)
    return d


def git(*args, check=False):
    r = subprocess.run(["git", "-C", ROOT, *args], capture_output=True, text=True)
    if check and r.returncode:
        raise RuntimeError(r.stderr.strip())
    return r.stdout


def norm(s):
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", s or "")).strip().lower()


def load_json(path, default=None):
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def parse_record(text):
    """Header lines between the first two --- fences are `key: value`; values may hold colons."""
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return {}, text
    head, i = {}, 1
    while i < len(lines) and lines[i].strip() != "---":
        if ":" in lines[i] and not lines[i].lstrip().startswith("#"):
            k, v = lines[i].split(":", 1)
            v = v.strip()
            if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
                v = v[1:-1]
            head[k.strip()] = v
        i += 1
    return head, "\n".join(lines[i + 1:]).strip()


def tags(v):
    return [t.strip() for t in (v or "").split(",") if t.strip()]


def sections(body, cap=700):
    """Split a record body into {heading: text}; the text before any heading is 'lead'."""
    out, cur, buf = {}, "lead", []
    for ln in body.split("\n"):
        m = re.match(r"^#{2,3}\s+(.*)", ln)
        if m:
            if buf:
                out[cur] = "\n".join(buf).strip()
            cur, buf = m.group(1).strip(), []
        else:
            buf.append(ln)
    if buf:
        out[cur] = "\n".join(buf).strip()
    return {k: (v[:cap] + "…" if len(v) > cap else v) for k, v in out.items() if v}


# ------------------------------------------------------------ syllabus data ---
def load_syllabus():
    syl = load_json(os.path.join(ROOT, "data", "syllabus.json"), {})
    topics, prefix, labels = {}, {}, {}
    for key, t in syl.get("topics", {}).items():
        topics[key] = {"key": key, "label": t["label"], "part": t.get("part", ""),
                       "course": t.get("course", "hsc")}
        for s in t.get("sections", []):
            for p in s.get("points", []):
                prefix.setdefault(p["id"].split(".")[0], key)
                labels[p["id"]] = p["label"]
        for th in t.get("themes", []):
            prefix.setdefault(th["id"].split(".")[0], key)
            labels[th["id"]] = th.get("label", th["id"])
    return topics, prefix, labels


# --------------------------------------------------------- drive and site -----
def drive_lookup():
    d = load_json(os.path.join(ROOT, "data", "drive-links.json"), {}) or {}
    files = d.get("files", {})
    by_norm = {norm(k): v for k, v in files.items()}

    def url(path):
        if not path:
            return None
        fid = files.get(path) or by_norm.get(norm(path))
        return f"https://drive.google.com/file/d/{fid}/view" if fid else None
    return url


def site_url(override=None):
    if override:
        return override
    if os.environ.get("EVIDENCE_SITE_URL"):
        return os.environ["EVIDENCE_SITE_URL"]
    remote = git("remote", "get-url", "origin").strip()
    m = re.search(r"github\.com[:/]+([^/]+)/([^/.]+?)(?:\.git)?$", remote)
    if m:
        return f"https://{m.group(1).lower()}.github.io/{m.group(2)}/evidence.html"
    return ""


# ------------------------------------------------------------------ records ---
def all_records():
    recs = {}
    for dp, _, fns in os.walk(EVIDENCE):
        for fn in fns:
            if not fn.endswith(".md") or fn == "README.md":
                continue
            p = os.path.join(dp, fn)
            head, body = parse_record(open(p, encoding="utf-8").read())
            if not head:
                continue
            rid = fn[:-3]
            recs[rid] = {"id": rid, "path": os.path.relpath(p, ROOT), "head": head, "body": body}
    return recs


def item_from(rec, topics, prefix, labels, drive, base, status):
    h = rec["head"]
    core = tags(h.get("core"))

    def topic_of(tag):
        return prefix.get(tag.split(".")[0])
    keys = [topic_of(t) for t in core if topic_of(t)]
    primary = keys[0] if keys else None
    also = []
    for k in keys[1:]:
        if k != primary and k not in also:
            also.append(k)
    sec = sections(rec["body"])
    doc, doc11 = h.get("document", ""), h.get("document11", "")
    return {
        "id": rec["id"], "status": status, "type": h.get("type", ""),
        "type_label": TYPE_LABEL.get(h.get("type", ""), h.get("type", "").title()),
        "title": h.get("title", rec["id"]), "short": h.get("short") or h.get("title", rec["id"]),
        "citation": h.get("citation", ""), "date": h.get("date", ""), "added": h.get("added", ""),
        "significance": h.get("significance", ""),
        "topic": primary, "also_topics": also,
        "core": core, "core_labels": [labels.get(t, t) for t in core],
        "card_url": f"{base}#ev-{rec['id']}" if base else "",
        "document": doc, "document_url": drive(doc), "document_missing_id": bool(doc and not drive(doc)),
        "document11": doc11, "document11_url": drive(doc11),
        "document11_missing_id": bool(doc11 and not drive(doc11)),
        "source": h.get("source", ""),
        "lead": sec.get("lead", ""),
        "use_it_for": next((v for k, v in sec.items() if k.lower().startswith("use it for")), ""),
        "caution": next((v for k, v in sec.items() if k.lower().startswith("caution")), ""),
        "sections": {k: v for k, v in sec.items() if k != "lead"},
        "path": rec["path"],
    }


# ------------------------------------------------------------------ updates ---
def updated_cards(since_dt, new_ids, reported_updates, recs):
    """Existing cards edited since `since_dt`, from git. Bulk commits are skipped and counted."""
    ts = since_dt.strftime("%Y-%m-%dT%H:%M:%S")
    log = git("log", f"--since={ts}", "--diff-filter=M", "--name-only",
              "--format=@@%h|%cI|%s", "--", "evidence")
    commits, cur = [], None
    for ln in log.split("\n"):
        if ln.startswith("@@"):
            sha, when, subj = ln[2:].split("|", 2)
            cur = {"sha": sha, "when": when, "subject": subj, "files": []}
            commits.append(cur)
        elif ln.strip() and cur is not None:
            cur["files"].append(ln.strip())
    changed, bulk = {}, 0
    for c in commits:
        if len(c["files"]) > BULK_COMMIT:
            bulk += 1
            continue
        for f in c["files"]:
            rid = os.path.basename(f)[:-3]
            if rid in recs and rid not in new_ids:
                e = changed.setdefault(rid, {"commits": [], "path": f})
                e["commits"].append({"sha": c["sha"], "subject": c["subject"]})
    base = git("rev-list", "-1", f"--before={ts}", "HEAD").strip()
    out = {}
    for rid, e in changed.items():
        if reported_updates.get(rid) == e["commits"][0]["sha"]:
            continue                                  # newest edit already reported
        diff = git("diff", "--unified=0", base, "--", e["path"]) if base else ""
        plus = [ln[1:] for ln in diff.split("\n") if ln.startswith("+") and not ln.startswith("+++")]
        minus = [ln[1:] for ln in diff.split("\n") if ln.startswith("-") and not ln.startswith("---")]
        txt = "\n".join(plus)
        out[rid] = {"commits": e["commits"], "latest_sha": e["commits"][0]["sha"],
                    "added_text": (txt[:1500] + "…") if len(txt) > 1500 else txt,
                    "removed_lines": len(minus), "added_lines": len(plus)}
    return out, bulk


# ------------------------------------------------------------------ commands --
def cmd_collect(a):
    topics, prefix, labels = load_syllabus()
    recs = all_records()
    state = load_json(STATE, {}) or {}
    reported = state.get("reported", {})
    reported_updates = state.get("reported_updates", {})
    now = datetime.datetime.now()
    t = today()

    if a.since:
        start = datetime.date.fromisoformat(a.since)
        basis = f"--since {a.since}"
    elif state.get("last_run"):
        last = datetime.datetime.fromisoformat(state["last_run"]).date()
        start = last - datetime.timedelta(days=1)
        basis = f"the last digest ({state['last_run'][:16].replace('T', ' ')}), looking back a day"
    else:
        start = prev_school_day(t)
        basis = f"first run: from the last school day, {start.strftime('%A %-d %B')}"

    drive, base = drive_lookup(), site_url(a.site)
    new = [r for rid, r in recs.items()
           if r["head"].get("added", "") >= start.isoformat()
           and r["head"].get("added", "") <= t.isoformat()
           and rid not in reported]
    new_ids = {r["id"] for r in new}
    future = sorted(rid for rid, r in recs.items() if r["head"].get("added", "") > t.isoformat())

    since_dt = datetime.datetime.combine(start, datetime.time.min)
    upd, bulk = updated_cards(since_dt, new_ids, reported_updates, recs)

    items = [item_from(r, topics, prefix, labels, drive, base, "new") for r in new]
    for rid, u in upd.items():
        it = item_from(recs[rid], topics, prefix, labels, drive, base, "updated")
        it["update"] = u
        items.append(it)

    site_text = ""
    try:
        site_text = open(os.path.join(ROOT, "evidence.html"), encoding="utf-8").read()
    except OSError:
        pass
    for it in items:
        it["in_site_build"] = bool(site_text) and (f'"{it["id"]}"' in site_text)

    # grouping: HSC topics first, then Year 11 focus areas; newest first inside each
    groups = []
    for key in HSC_ORDER + Y11_ORDER + [None]:
        its = [i for i in items if i["topic"] == key]
        if not its:
            continue
        its.sort(key=lambda i: (i["status"] != "new", i["added"], i["title"]), reverse=False)
        meta = topics.get(key, {"key": "other", "label": "Other", "part": "", "course": "hsc"})
        groups.append({**meta, "items": its})

    notes = []
    ahead = git("rev-list", "--count", "origin/main..HEAD").strip()
    if ahead.isdigit() and int(ahead) > 0:
        notes.append(f"{ahead} commit(s) on this Mac have not been pushed (as of the last fetch): "
                     "card links will not work for those cards until Push origin.")
    dirty = [l for l in git("status", "--porcelain", "--", "evidence").split("\n") if l.strip()]
    if dirty:
        notes.append(f"{len(dirty)} evidence file(s) have uncommitted changes.")
    if site_text and "openFromHash" not in site_text:
        notes.append("evidence.html has no #ev-<id> deep-link code, so card links open the finder's home "
                     "page, not the card. See references/deeplink-patch.md in the skill.")
    miss = [i["id"] for i in items if not i["in_site_build"]]
    if miss:
        notes.append("Not in the current evidence.html build (rebuild before publishing): " + ", ".join(miss))
    nodoc = [i["id"] for i in items if i["document_missing_id"] or i["document11_missing_id"]]
    if nodoc:
        notes.append("Document has no Drive id yet (the nightly Drive map will add it): " + ", ".join(nodoc))
    if bulk:
        notes.append(f"{bulk} bulk commit(s) touching more than {BULK_COMMIT} cards were ignored as retagging, "
                     "not content updates.")
    if future:
        notes.append("Records dated after today were left out: " + ", ".join(future))
    if not base:
        notes.append("Could not work out the site URL; card links are empty. Pass --site.")

    digest = {"generated": now.isoformat(timespec="seconds"), "today": t.isoformat(),
              "window_start": start.isoformat(), "basis": basis, "site_url": base,
              "counts": {"new": sum(i["status"] == "new" for i in items),
                         "updated": sum(i["status"] == "updated" for i in items)},
              "groups": groups, "notes": notes}

    out = a.out or os.path.join(DEFAULT_OUT_DIR, f"digest-{t.isoformat()}.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(digest, f, indent=1, ensure_ascii=False)

    print(f"Digest window: {basis}")
    print(f"{digest['counts']['new']} new, {digest['counts']['updated']} updated  ->  {out}")
    print(f"Site: {base or '(unknown)'}\n")
    for g in groups:
        print(f"== {g['label']} ({g['part']})")
        for i in g["items"]:
            print(f"  [{i['status'].upper()}] {i['id']}  ·  {i['type_label']}  ·  added {i['added']}")
            print(f"    title: {i['title']}")
            print(f"    significance: {i['significance']}")
            if i["lead"]:
                print(f"    lead: {i['lead'][:600].replace(chr(10), ' ')}")
            if i["use_it_for"]:
                print(f"    use it for: {i['use_it_for'][:400].replace(chr(10), ' ')}")
            if i["caution"]:
                print(f"    caution: {i['caution'][:400].replace(chr(10), ' ')}")
            if i["also_topics"]:
                print(f"    also relevant to: {', '.join(topics[k]['label'] for k in i['also_topics'] if k in topics)}")
            if i["status"] == "updated":
                u = i["update"]
                print(f"    updated by: {'; '.join(c['subject'] for c in u['commits'])}")
                print(f"    changed text (+{u['added_lines']}/-{u['removed_lines']} lines): "
                      f"{u['added_text'][:500].replace(chr(10), ' ')}")
        print()
    for n in notes:
        print("NOTE:", n)


def cmd_mark(a):
    digest = load_json(a.digest)
    if not digest:
        sys.exit(f"Cannot read {a.digest}")
    state = load_json(STATE, {}) or {}
    reported = state.setdefault("reported", {})
    ru = state.setdefault("reported_updates", {})
    for g in digest["groups"]:
        for i in g["items"]:
            if i["status"] == "new":
                reported[i["id"]] = digest["today"]
            else:
                ru[i["id"]] = i["update"]["latest_sha"]
    cutoff = (today() - datetime.timedelta(days=90)).isoformat()
    state["reported"] = {k: v for k, v in reported.items() if v >= cutoff}
    state["last_run"] = datetime.datetime.now().isoformat(timespec="seconds")
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    with open(STATE, "w") as f:
        json.dump(state, f, indent=1)
    print(f"Marked {digest['counts']['new']} new and {digest['counts']['updated']} updated card(s) "
          f"as reported. Last run: {state['last_run']}")


def cmd_status(a):
    s = load_json(STATE)
    if not s:
        print("No digest has been marked yet: the next collect starts from the last school day "
              f"({prev_school_day(today()).strftime('%A %-d %B')}).")
        return
    print(f"Last run: {s.get('last_run')}\nReported cards: {len(s.get('reported', {}))}"
          f"\nReported updates: {len(s.get('reported_updates', {}))}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("collect")
    c.add_argument("--since")
    c.add_argument("--out")
    c.add_argument("--site")
    c.set_defaults(fn=cmd_collect)
    m = sub.add_parser("mark")
    m.add_argument("digest")
    m.set_defaults(fn=cmd_mark)
    sub.add_parser("status").set_defaults(fn=cmd_status)
    args = ap.parse_args()
    args.fn(args)
