#!/usr/bin/env python3
"""Walk the Evidence Finder library (in the shared drive) and classify what is in it.

Two things live in that folder and they are not the same: **evidence**, which goes in
front of a marker, and **teaching resources** — decks, question surveys, practice
questions, essay plans — which are how the evidence gets taught. Both are worth
finding; only the first belongs in the evidence list.

Writes data/library.json. Nothing is moved, renamed or deleted.
"""

import json, os, re, sys, unicodedata, urllib.parse
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# The library is the `library` folder inside Evidence Finder in the shared drive:
# the same files the site links to on Drive, so what is scanned is what is
# published. It is found wherever this runs — the Mac itself, or a Cowork session
# with the Evidence Finder folder connected. An argument or EVIDENCE_LIBRARY wins.
DRIVE_LIBRARY = ("/Users/phillip/Library/CloudStorage/GoogleDrive-phillip.pain@education.nsw.gov.au/"
                 "Shared drives/HSC_LS_SSCBWB/Evidence Finder/library")
CANDIDATES = [os.environ.get("EVIDENCE_LIBRARY", ""), DRIVE_LIBRARY,
              os.path.expanduser("~/mnt/Evidence Finder/library")]
args = [a for a in sys.argv[1:] if not a.startswith("--")]
LIB = args[0] if args else next((c for c in CANDIDATES if c and os.path.isdir(c)), DRIVE_LIBRARY)

# Where the folder lives *on the machine that opens the page*. The scan may run
# somewhere else — a mounted copy of the folder, say — and the fallback file://
# links in evidence.html must still point at the real thing, so the path written
# into the data is this one, not the path that was walked. (Online, every
# document opens from its Drive id instead; see data/drive-links.json.)
LINK_ROOT = os.environ.get("LIB_LINK_ROOT", DRIVE_LIBRARY)

SKIP = {".DS_Store", "Icon\r", "Thumbs.db", "desktop.ini"}

# ------------------------------------------------------------------ topics --
# The folder a document sits in is a real, if coarse, statement about what it is
# about. Deeper folders say more, so the longest matching prefix wins.
FOLDER_TAG = {
    "crime": "crime",
    "crime/criminal trial process": "crime.3",
    "crime/sentencing and punishment": "crime.4",
    "crime/young offenders": "crime.5",
    "crime/international crime": "crime.6",
    "crime/media": "crime",
    "crime/revision templates": "crime",
    "international crime": "crime.6",
    "family": "family",
    "family/cases": "family",
    "family/cpoc": "fam.3.4",
    "family/surrogacy and birth tech": "fam.3.3",
    "family/evidence summaries": "family",
    "family/non legal": "fam.2.6",
    "family/essay examples": "family",
    "family/summary notes": "family",
    "family/ppt": "family",
    "family/posters": "family",
    "human rights": "humanrights",
    "human rights/cases": "humanrights",
    "human rights/modern slavery": "hr.3.1",
    "shelter": "shelter",
    "shelter/evidence sheets": "shelter",
    "shelter/shelter powerpoints": "shelter",
    "shelter/shelter videos": "shelter",
    "shelter/slides": "shelter",
    "cases": None,                      # mixed — decided per file below
    "cases/crime": "crime",
    "cases/family": "family",
    "cases/human rights": "humanrights",
    "cases/shelter": "shelter",
    "cases/bocsar": "crime",
    "jade cases": None,
    "jade cases/raw cases": None,
    "jade cases/completed case summaries": None,
    "news articles": None,
    "news articles/family": "family",
    "news articles/human rights": "humanrights",
    "news articles/shelter": "shelter",
    "legal briefs": None,
    "tiktok videos": None,
}

# A case citation says which jurisdiction heard it, which is often the whole answer.
CITATION_TAG = [
    (r"arta.*refugee|refugee.*arta", "hr.3.1"),
    (r"arta.*child support|child support.*arta", "fam.1.5"),
    (r"fedcfamc", "family"),
    (r"\bhca\b|\bfcafc\b|\bfca\b", None),      # decided by subject instead
    (r"nswcatap|\bncat\b", "shel.2.5"),
]

# A filename can be more specific than its folder.
NAME_TAG = [
    (r"refugee|asylum|migration|minister for immigration|citizenship|samuelu|da silva", "hr.3.1"),
    (r"modern slavery|forced marriage|servitude|child soldier|trafficking", "hr.3.1"),
    (r"native title|eastern maar|lalc|land council|terra nullius|mabo|wik", "ls.5.3"),
    (r"child ?support", "fam.1.5"),
    (r"surrogacy|embryo|ivf|birth tech|donor", "fam.3.3"),
    (r"domestic violence|dfv|coercive control|advo|apprehended", "fam.2.4"),
    (r"care and protection|child protection|children.s guardian|cpoc", "fam.3.4"),
    (r"young offender|youth justice|children.s court|doli", "crime.5"),
    (r"sentenc|parole|diversion|custody trend|punishment", "crime.4"),
    (r"bail|remand|arrest|detention|interrogation|police power|search", "crime.2"),
    (r"charge negotiation|jury|trial process|plea", "crime.3"),
    (r"austin v state of victoria|eastern maar", "ls.5.3"),
    (r"clare.s law", "fam.2.4"),
    (r"empty propert|vacan(cy|t) (rate|propert)", "shel.3.1"),
    (r"eviction|evicted", "shel.2.2"),
    (r"aged care", "shel.2.4"),
    (r"sharia|civil law system", "ls.3.4"),
    (r"adoption", "fam.1.6"),
    (r"homeless", "shel.3.3"),
    (r"\btenan|\brental|\bleas(e|ing)|\brenting|landlord", "shel.2.2"),
    (r"affordab|housing supply|planning law", "shel.3.1"),
    (r"transgender|anti.?discrimination act", "hr.3.1"),
    (r"discriminat", "shel.3.2"),
    (r"social housing|public housing|community housing", "shel.3.4"),
]

# ------------------------------------------------------------------- kinds --
RESOURCE = re.compile(
    r"question survey|past hsc question|predicted .*question|practice question|"
    r"question plan|essay plan|essay example|practice essay|marking|criteria|cheat sheet|"
    r"revision t(able|emplate)|syllabus (extract|outline)|slide set|slides?$|teaching deck|lesson|"
    r"response structure|coding example|task \d|student version|poster|"
    r"scaffold|template|worked example|model paragraph|exemplar|glossary|"
    r"summary (notes|sheet)|study guide|exam pack|booklet|"
    r"worksheet|activit(y|ies)|group task|evidence map|answers |intro suggestions|"
    r"judge?ment sheet|student (answer|response)|band \d response|"
    r"overview \(|example paragraph|set \d|lsa update|update\b.*\d{4}|"
    r"^\d+(\.\d+)* - |^\d+\. |unit plan|(unit|teaching|course|scope) program|assessment|rubric|"
    # A deck or a set of notes exported to PDF is still teaching material, and so is
    # anything built around writing an essay. Kept deliberately narrow: "unanswered
    # questions" in the title of a commentary piece must NOT match, so the question
    # patterns all name the kind of question paper they are.
    r"\bpptx\b|\bslides?\b|\bnotes\b|\bessay\b|essay[- ]?plans?|study sheets?|"
    r"textbook|handback|mc questions|check.?.?in questions|questions for practice|"
    r"collation of .*questions", re.I)

# Folders that hold teaching material whatever the file inside them is called.
TEACHING_DIR = re.compile(r"(^|/)(essay examples|summary notes|ppt|slides|posters)(/|$)", re.I)

# Documents that are not Legal Studies at all, or are a journal rather than evidence.
OFF_TOPIC = re.compile(r"\b(eco|maths|hsie|geo|comm)\d|economics|legal briefs", re.I)

EVIDENCE_TYPE = [
    ("case",          re.compile(r"\[\d{4}\]|\(\d{4}\)|fedcfam|hca|fcafc|nswca|nswsc|arta|fca \d|"
                                 r"caselaw|case summary|case card|case study card|v |judgment", re.I)),
    ("report",        re.compile(r"bocsar|cjb\d|report|snapshot|statistic|inquiry|royal commission|"
                                 r"audit|anao|aihw|abs |census|research|evaluation|bulletin|data", re.I)),
    ("media",         re.compile(r"herald|telegraph|abc news|guardian|smh|news\.com|article|"
                                 r"\| .*times|\.com\b", re.I)),
    ("international", re.compile(r"convention|covenant|declaration|treaty|protocol|croc|iccpr|"
                                 r"icescr|udhr|crpd|cedaw|united nations|general comment", re.I)),
    ("legislation",   re.compile(r"\bact\b|\bs \d+|regulation|amendment bill|\bbill\b", re.I)),
]

VIDEO = {".mov", ".mp4", ".m4v"}
DOCS = {".pdf", ".docx", ".doc", ".rtf", ".pptx", ".ppt", ".xlsx", ".txt", ".md"}


def clean(name):
    """The human name: url-decoded, extension dropped, underscores opened out.

    A trailing number is NOT stripped. "Slide Set 4" is the fourth slide set, not a
    copy of the third, and stripping it merged eight decks into one.
    """
    n = urllib.parse.unquote(name)
    n = unicodedata.normalize("NFC", n)
    n = os.path.splitext(n)[0]
    n = re.sub(r"[_]+", " ", n)
    n = re.sub(r"\s{2,}", " ", n).strip()
    return n


def dupe_key(name):
    return re.sub(r"[^a-z0-9]+", "", clean(name).lower())


# A copy is only a copy when the file it copies is actually there. macOS and browsers
# make them as "… 2.pdf" and "… copy.pdf", so the marker is stripped and the result
# looked up — never assumed.
COPY_MARK = re.compile(r"^(?P<base>.+?)[\s_]*(?:\((?:copy|\d)\)|copy(?:\s*\d)?|[2-9])$", re.I)


def copy_of(name):
    m = COPY_MARK.match(clean(name))
    return re.sub(r"[^a-z0-9]+", "", m.group("base").lower()) if m else None


def folder_tag(rel):
    parts = rel.split(os.sep)[:-1]
    best = None
    for i in range(len(parts), 0, -1):
        k = "/".join(p.lower() for p in parts[:i])
        if k in FOLDER_TAG:
            best = FOLDER_TAG[k]
            break
    return best


def classify(rel, name):
    human = clean(name)
    ext = os.path.splitext(name)[1].lower()

    # tags: the folder's, plus anything the filename or the citation says.
    # When the two disagree they are both kept — a murder trial filed under Family
    # is genuinely about both.
    tags = []
    ft = folder_tag(rel)
    if ft:
        tags.append(ft)
    for pat, t in CITATION_TAG:
        if t and re.search(pat, human, re.I):
            tags.append(t)
            break
    for pat, t in NAME_TAG:
        if re.search(pat, human, re.I):
            tags.append(t)
            break
    seen = set()
    tags = [t for t in tags if not (t in seen or seen.add(t))]

    if OFF_TOPIC.search(human) or OFF_TOPIC.search(rel):
        return "resource", "other", tags
    if ext in VIDEO:
        return "resource", "video", tags
    if ext in (".pptx", ".ppt"):
        return "resource", "deck", tags
    if RESOURCE.search(human) or TEACHING_DIR.search(rel.replace(os.sep, "/")):
        return "resource", "teaching", tags
    if ext not in DOCS:
        return "resource", "other", tags

    low = rel.lower()
    if "/cases" in low or low.startswith("cases") or "jade cases" in low:
        return "evidence", "case", tags
    if "news articles" in low or "/media" in low:
        return "evidence", "media", tags
    if "bocsar" in low:
        return "evidence", "report", tags
    for t, pat in EVIDENCE_TYPE:
        if pat.search(human):
            return "evidence", t, tags
    return "evidence", "document", tags


def load_overrides():
    """Hand-written tags for files whose name says nothing — data/library-tags.txt."""
    path = os.path.join(ROOT, "data", "library-tags.txt")
    out = {}
    if not os.path.exists(path):
        return out
    for n, line in enumerate(open(path, encoding="utf-8"), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "|" not in line:
            raise SystemExit(f"library-tags.txt:{n}: no `|` in `{line}`")
        p, tags = line.split("|", 1)
        out[p.strip()] = [t.strip() for t in tags.split(",") if t.strip()]
    return out


def main():
    overrides = load_overrides()
    files = []
    # Folders the tidy-up puts things aside in are not part of the library.
    ASIDE = {"_duplicates", "_not-legal-studies", "inbox"}
    for dirpath, dirnames, names in os.walk(LIB):
        dirnames[:] = [d for d in dirnames if not d.startswith(".") and d not in ASIDE]
        for n in sorted(names):
            if n in SKIP or n.startswith("."):
                continue
            full = os.path.join(dirpath, n)
            rel = os.path.relpath(full, LIB)
            try:
                st = os.stat(full)
            except OSError:
                continue
            bucket, kind, tags = classify(rel, n)
            if rel in overrides:
                tags = overrides[rel]
            files.append({
                "path": rel, "name": clean(n), "file": n,
                "ext": os.path.splitext(n)[1].lower().lstrip("."),
                "bytes": st.st_size, "mtime": int(st.st_mtime),
                "bucket": bucket, "kind": kind, "tags": tags,
                "dupe": dupe_key(n),
            })

    # A file marked "… 2" or "… copy" is a copy only when the original is in the same
    # folder in the same format; otherwise its name simply ends in a number.
    by_dir = defaultdict(dict)
    for f in files:
        by_dir[(os.path.dirname(f["path"]), f["ext"])][f["dupe"]] = f["path"]
    for f in files:
        base = copy_of(f["file"])
        f["copyOf"] = by_dir[(os.path.dirname(f["path"]), f["ext"])].get(base) if base else None
        if f["copyOf"] == f["path"]:
            f["copyOf"] = None

    groups = defaultdict(list)
    for f in files:
        groups[f["dupe"]].append(f)
    # the copy a person should open: pdf first, then docx, then whatever is newest
    rank = {"pdf": 0, "docx": 1, "doc": 2, "rtf": 3, "pptx": 4, "ppt": 5}
    dupes = []
    for k, g in groups.items():
        if len(g) < 2:
            g[0]["primary"] = not g[0]["copyOf"]
            continue
        g.sort(key=lambda f: (bool(f["copyOf"]), rank.get(f["ext"], 9), -f["mtime"]))
        g[0]["primary"] = True
        for f in g[1:]:
            f["primary"] = False
        dupes.append({"name": g[0]["name"], "keep": g[0]["path"],
                      "others": [f["path"] for f in g[1:]]})

    out = {"root": LINK_ROOT, "files": files, "duplicateGroups": sorted(dupes, key=lambda d: -len(d["others"]))}
    os.makedirs(f"{ROOT}/data", exist_ok=True)
    dest = f"{ROOT}/data/library.json"

    # A scan that walked the wrong folder finds nothing, and writing that out
    # replaces a good index with an empty one. Refuse, unless --empty-ok says the
    # folder really is empty.
    if not files and "--empty-ok" not in sys.argv:
        had = 0
        if os.path.exists(dest):
            try:
                had = len(json.load(open(dest)).get("files", []))
            except Exception:
                had = 0
        print(f"  REFUSED: found no files under {LIB}")
        if had:
            print(f"  data/library.json still holds {had} files and has not been touched.")
        print("  Pass the folder as an argument, or --empty-ok if it really is empty.")
        sys.exit(1)

    json.dump(out, open(dest, "w"), ensure_ascii=False, indent=1)

    ev = [f for f in files if f["bucket"] == "evidence"]
    rs = [f for f in files if f["bucket"] == "resource"]
    print(f"{len(files)} files  ·  {len(ev)} evidence  ·  {len(rs)} resources")
    print(f"  duplicate groups: {len(dupes)}  ({sum(len(d['others']) for d in dupes)} extra copies)")
    print(f"  primary copies:   {sum(1 for f in files if f.get('primary'))}")
    by = defaultdict(int)
    for f in ev:
        by[f["kind"]] += 1
    print("  evidence by type: " + " · ".join(f"{k} {v}" for k, v in sorted(by.items(), key=lambda x: -x[1])))
    by = defaultdict(int)
    for f in rs:
        by[f["kind"]] += 1
    print("  resources by kind: " + " · ".join(f"{k} {v}" for k, v in sorted(by.items(), key=lambda x: -x[1])))
    unknown = sorted({p for p in overrides if p not in {f["path"] for f in files}})
    if unknown:
        print(f"  overrides pointing at nothing ({len(unknown)}):")
        for p in unknown:
            print("    " + p)
    untagged = [f for f in files if not f["tags"]]
    print(f"  untagged: {len(untagged)}  ·  hand-tagged: {len(overrides) - len(unknown)}")
    by = defaultdict(int)
    for f in files:
        for t in f["tags"]:
            by[t] += 1
    print("  tags: " + " · ".join(f"{k} {v}" for k, v in sorted(by.items(), key=lambda x: -x[1])[:16]))


if __name__ == "__main__":
    main()
