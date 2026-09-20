#!/usr/bin/env python3
"""Assemble evidence.html from evidence/*.md + data/syllabus.json.

The question finder is read, not rebuilt: its built page is parsed for the number of
past questions on each syllabus tag, so the evidence finder can say how often a dot
point has been examined. If index.html is missing those counts are simply omitted.
"""

import json, os, re, sys, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))
import md
from evidence_lib import load_records, syllabus_index, check_tags, TYPES, CRITERIA

syl = json.load(open(f"{ROOT}/data/syllabus.json"))
recs, problems = load_records()
idx = syllabus_index(syl)
problems += check_tags(recs, idx)
if problems:
    print("evidence problems:")
    for p in problems:
        print("  " + p)
    raise SystemExit(1)

# ----------------------------------------------- past questions, if built ----
questions = {}
try:
    html_src = open(f"{ROOT}/index.html", encoding="utf-8").read()
    m = re.search(r"<script>const DATA = (\{.*?\});</script>", html_src, re.S)
    if m:
        for it in json.loads(m.group(1))["items"]:
            for t in it["core"] + it["support"]:
                questions[t] = questions.get(t, 0) + 1
except FileNotFoundError:
    pass

# ------------------------------------------------------------- the topics ----
# Colour is carried by the topic within the HSC course, where four hues were
# validated against each other; the Preliminary course is one further validated
# hue and its three parts are told apart by their icons, because seven
# categorical hues cannot be separated for colour-vision deficiency in one band.
SLOT = {"crime": 1, "humanrights": 2, "family": 3, "shelter": 4,
        "legalsystem": 5, "individual": 5, "lawinpractice": 5}
ICON = {"crime": "g-scales", "humanrights": "g-globe", "family": "g-family",
        "shelter": "g-shelter", "legalsystem": "g-columns", "individual": "g-person",
        "lawinpractice": "g-target"}
COURSE = {"preliminary": {"label": "Preliminary", "note": "Year 11 — the legal system, the individual, law in practice"},
          "hsc": {"label": "HSC", "note": "Year 12 — the core, and the two options this school teaches"}}

topics = []
for k, t in syl["topics"].items():
    topics.append({
        "k": k, "label": t["label"], "part": t["part"], "course": t.get("course", "hsc"),
        "slot": SLOT[k], "icon": ICON[k], "focus": t["principalFocus"],
        "themes": [{"id": th["id"], "label": th["label"], "full": th["full"]} for th in t["themes"]],
        "sections": [{"id": s["id"], "label": s["label"],
                      "points": [{"id": p["id"], "label": p["label"]} for p in s["points"]]}
                     for s in t["sections"]],
    })

# ------------------------------------------------- the library, if scanned ---
# Every document in the Evidence Organiser folder, so that a dot point shows both
# the evidence that has been written up and the files still sitting behind it.
# A file a record already summarises is dropped: the record supersedes it.
library, libroot = [], ""
claimed = {r["document"] for r in recs if r.get("document")}

# A second copy of a document a record already covers — the raw judgment beside the
# case card, say — is recognised by its citation rather than its filename, and is
# hidden for the same reason a named document is: the record supersedes it.
def cite_key(s):
    # "and" is dropped because a case card writes "Billings and Clowes" for a record
    # whose short name is "Billings & Clowes", and the two must land on one key.
    return re.sub(r"[^a-z0-9]+", "", re.sub(r"\band\b", " ", s.lower()))

# A medium neutral citation: [year] COURT number. The court code can itself contain
# digits — FedCFamC2F, NSWCATAD — so the number must be preceded by whitespace, or
# `[2026] FedCFamC2F 391` truncates to `[2026] FedCFamC2` and matches every
# FedCFamC2F case in the folder. That bug hid twenty unrelated judgments.
CITATION = re.compile(r"\[(\d{4})\]\s*([A-Za-z]+(?:\d+[A-Za-z]*)*)\s+(\d+)\b")

# Downloaded judgments often arrive with the spaces stripped out of the filename —
# `2112275(Refugee)[2026]ARTA1503(27March2026).rtf` — and case cards are often saved
# without the brackets: `Billings and Clowes (No 2) 2026 FedCFamC2F 1367 - case card`.
# Both forms split safely as long as the court code is required to END in a letter,
# which is what stops `FedCFamC2F 391` being read as court `FedCFamC2`.
CITATION_TIGHT = re.compile(r"\[(\d{4})\]\s*([A-Za-z][A-Za-z0-9]*[A-Za-z])(\d+)(?![A-Za-z0-9])")
CITATION_BARE = re.compile(r"\b(19|20)(\d{2})\s+([A-Za-z][A-Za-z0-9]*[A-Za-z])\s+(\d+)\b")


def citation_keys(text):
    """Every medium neutral citation in a string, as comparable keys."""
    keys = set()
    for m in CITATION.finditer(text):
        keys.add(cite_key("".join(m.groups())))
    for m in CITATION_TIGHT.finditer(text):
        keys.add(cite_key("".join(m.groups())))
    for m in CITATION_BARE.finditer(text):
        y1, y2, court, num = m.groups()
        keys.add(cite_key(y1 + y2 + court + num))
    return keys

cited = {}
for r in recs:
    for c in filter(None, [r.get("citation"), r.get("title"), r.get("short")]):
        ks = citation_keys(c)
        if ks:
            for k in ks:
                cited.setdefault(k, r["id"])
            break

# A case card carries the case name but not always the citation — "Eadgar & Amiri
# Case Summary.pdf". A record's short name is distinctive enough to match on when it
# is long enough to be, which a generic prefix like a court code is not.
named = {}
for r in recs:
    k = cite_key(r.get("short") or r["title"])
    if len(k) >= 10:
        named.setdefault(k, r["id"])
try:
    lib = json.load(open(f"{ROOT}/data/library.json"))
    libroot = lib["root"]
    superseded = 0
    for f in lib["files"]:
        if not f.get("primary") or f["path"] in claimed:
            continue
        if citation_keys(f["name"]) & set(cited):
            superseded += 1
            continue
        # only a document, never a teaching resource: a deck called "The Role of
        # Juries" is not superseded by the notes of the same name, it is a different
        # thing someone may still want
        fk = cite_key(f["name"])
        if f["bucket"] == "evidence" and any(k in fk for k in named):
            superseded += 1
            continue
        library.append({
            "p": f["path"], "n": f["name"], "x": f["ext"],
            "b": f["bucket"], "k": f["kind"], "t": f["tags"],
        })
    library.sort(key=lambda f: (f["b"] != "evidence", f["n"].lower()))
except FileNotFoundError:
    pass

# ------------------------------------------------ Google Drive, if mapped ---
# The documents also live in a shared drive, so that a page served from GitHub
# Pages can open them. `data/drive-links.json` is written by the Apps Script in
# build/map-drive-ids.gs: a path (relative to the library folder) -> file id.
# Any file that is not in the map keeps its local path, so a half-finished map
# degrades file by file rather than breaking the page.
drive_links = {}
# The Apps Script writes the map into the shared drive itself, so the build looks
# there too: run the script, rebuild, done. A copy in data/ wins if both exist.
DRIVE_MAP = [
    f"{ROOT}/data/drive-links.json",
    os.environ.get("DRIVE_LINKS", os.path.expanduser(
        "~/Library/CloudStorage/GoogleDrive-phillip.pain@education.nsw.gov.au/"
        "Shared drives/HSC_LS_SSCBWB/Evidence Finder/drive-links.json")),
]
try:
    src = next((m for m in DRIVE_MAP if os.path.exists(m)), None)
    if not src:
        raise FileNotFoundError
    dl = json.load(open(src, encoding="utf-8"))
    drive_links = dl.get("files", dl)
    have = sum(1 for f in library if f["p"] in drive_links)
    named_have = sum(1 for d in claimed if d in drive_links)
    print(f"  drive:    {len(drive_links)} ids mapped · {have}/{len(library)} library files, "
          f"{named_have}/{len(claimed)} cited documents")
except FileNotFoundError:
    print("  drive:    no data/drive-links.json — links stay local "
          "(run build/map-drive-ids.gs to make one)")

items = []
for r in recs:
    items.append({
        "id": r["id"], "type": r["type"], "title": r["title"], "short": r["short"],
        "cite": r.get("citation", ""), "date": r.get("date", ""),
        "juris": r.get("jurisdiction", ""), "sig": r["significance"],
        "core": r["core"], "support": r["support"], "themes": r["themes"],
        "criteria": r["criteria"], "related": r["related"],
        "source": r.get("source", ""), "file": r["file"],
        "doc": r.get("document", ""),
        "body": md.render(r["body"]),
    })

data = {
    "meta": {
        "built": datetime.date.today().isoformat(),
        "syllabus": syl["meta"]["syllabus"],
        "records": len(items),
    },
    "types": TYPES, "criteria": CRITERIA, "courses": COURSE,
    "topics": topics, "items": items, "questions": questions,
    "libRoot": libroot, "library": library, "driveLinks": drive_links,
}
data["meta"]["library"] = len(library)

tpl = open(f"{ROOT}/build/evidence_template.html", encoding="utf-8").read()
out = tpl.replace("__DATA__", json.dumps(data, ensure_ascii=False, separators=(",", ":")))
with open(f"{ROOT}/evidence.html", "w", encoding="utf-8") as f:
    f.write(out)

by_type = {k: sum(1 for i in items if i["type"] == k) for k in TYPES}
tagged = set()
for i in items:
    tagged |= set(i["core"]) | set(i["support"])
points = [p for t in topics for s in t["sections"] for p in s["points"]]
covered = sum(1 for p in points if p["id"] in tagged)

print(f"evidence.html  {len(out):,} bytes  ·  {len(items)} records  ·  {len(topics)} topics")
print("  by type:  " + " · ".join(f"{TYPES[k]['label']} {v}" for k, v in by_type.items() if v))
print(f"  coverage: {covered}/{len(points)} dot points carry evidence")
if library:
    ev = sum(1 for f in library if f["b"] == "evidence")
    print(f"  library:  {len(library)} files ({ev} evidence, {len(library)-ev} resources), "
          f"{len(claimed)} named by a record, {superseded} more superseded by one")
print("  placeholder left in html:", "__DATA__" in out)
