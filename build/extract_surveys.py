#!/usr/bin/env python3
"""Pull the question text, directives and core/support matrices out of the three
2026 survey documents into a single items.json keyed on syllabus.json tag IDs."""

import json, re, os, sys
import docx
import pdfplumber

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UP = os.path.join(ROOT, "source-documents")
CRIME = os.path.join(UP, "12LS_2026_Crime_HSC_Question_Survey.docx")
FAMILY = os.path.join(UP, "12LS_2026_Family_Past_HSC_Question_Survey.docx")
SHELTER = os.path.join(UP, "12LS_2026_Shelter_Past_HSC_Question_Survey.pdf")

# --- element label -> syllabus.json IDs -------------------------------------
# The survey matrices tag at section/group level, which is right for a 15- or
# 25-mark essay: it draws on a whole syllabus section, not one dot point.
ELEM = {
    "crime": {
        "Discretion": ["crime.t.discretion"],
        "Compliance & non-compliance": ["crime.t.compliance"],
        "Moral & ethical standards": ["crime.t.moral"],
        "Law reform": ["crime.t.reform"],
        "Balancing victims, offenders & society": ["crime.t.balance"],
        "Legal & non-legal effectiveness": ["crime.t.effectiveness"],
        "The nature of crime": ["crime.1"],
        "Criminal investigation process": ["crime.2"],
        "Criminal trial process": ["crime.3"],
        "Sentencing & punishment": ["crime.4"],
        "Young offenders": ["crime.5"],
        "International crime": ["crime.6"],
    },
    "family": {
        "Cooperation & conflict resolution": ["fam.t.cooperation"],
        "Compliance & non-compliance": ["fam.t.compliance"],
        "Changing community values": ["fam.t.values"],
        "Law reform & just outcomes": ["fam.t.reform"],
        "Legal & non-legal effectiveness": ["fam.t.effectiveness"],
        "Nature of family law": ["fam.1.1", "fam.1.2"],
        "Marriage & alternative relationships": ["fam.1.3", "fam.1.4"],
        "Parents & children · adoption": ["fam.1.5", "fam.1.6"],
        "Divorce & separation": ["fam.2.1", "fam.2.2", "fam.2.3"],
        "Domestic violence": ["fam.2.4"],
        "Courts, dispute resolution, NGOs & media": ["fam.2.5", "fam.2.6", "fam.2.7"],
        "Same-sex relationships": ["fam.3.1"],
        "Parental responsibility": ["fam.3.2"],
        "Surrogacy & birth technologies": ["fam.3.3"],
        "Care & protection of children": ["fam.3.4"],
    },
    "shelter": {
        "Cooperation & conflict resolution": ["shel.t.cooperation"],
        "Compliance & non-compliance": ["shel.t.compliance"],
        "Changing values & ethics": ["shel.t.values"],
        "Law reform": ["shel.t.reform"],
        "Legal & non-legal effectiveness": ["shel.t.effectiveness"],
        "Nature of shelter": ["shel.1"],
        "Purchasing": ["shel.2.1"],
        "Leasing": ["shel.2.2", "shel.2.3"],
        "Other shelter types": ["shel.2.4"],
        "Dispute resolution": ["shel.2.5", "shel.2.6", "shel.2.7", "shel.2.8", "shel.2.9", "shel.2.10"],
        "Affordability": ["shel.3.1"],
        "Discrimination": ["shel.3.2"],
        "Homelessness": ["shel.3.3"],
        "Social housing": ["shel.3.4"],
    },
}

# Shelter matrix headers are rotated in the PDF and come back as mojibake, so the
# column order is asserted from the survey's own column key instead.
SHELTER_COLS = [
    "Cooperation & conflict resolution", "Compliance & non-compliance",
    "Changing values & ethics", "Law reform", "Legal & non-legal effectiveness",
    "Nature of shelter", "Purchasing", "Leasing", "Other shelter types",
    "Dispute resolution", "Affordability", "Discrimination", "Homelessness",
    "Social housing",
]

DIRECTIVES = [
    ("to what extent", "evaluate"), ("how effective", "evaluate"),
    ("critically analyse", "evaluate"), ("evaluate", "evaluate"), ("assess", "evaluate"),
    ("analyse", "analyse"), ("discuss", "analyse"),
    ("compare", "explain"), ("explain", "explain"), ("examine", "explain"),
    ("describe", "describe"), ("outline", "describe"),
]

def directive_of(text):
    """First NESA glossary verb in the stem, and its demand band."""
    low = text.lower()
    best = None
    for verb, band in DIRECTIVES:
        i = low.find(verb)
        if i >= 0 and (best is None or i < best[0]):
            best = (i, verb, band)
    return (best[1], best[2]) if best else (None, None)

def mark(sym):
    s = (sym or "").strip()
    if "●" in s: return "core"
    if "○" in s: return "support"
    return None

def split_cell(cell):
    """Survey cells hold the stem, then a tag line of element names. The tag line
    is redundant with the matrix, so only the stem is kept."""
    paras = [p.text.strip() for p in cell.paragraphs if p.text.strip()]
    return paras[0] if paras else ""


def strip_tagline(text, topic):
    """The Shelter survey is a PDF, so a cell's coloured tag line runs on after the
    stem instead of sitting in its own paragraph. Cut at the first element label.
    Built from the labels themselves — an earlier hand-written pattern ended in \\b,
    which cannot match after the '&' of 'Legal & non-legal effectiveness', so that
    one label survived into four stems."""
    labels = sorted(ELEM[topic], key=len, reverse=True)
    pat = r"\s(?=" + "|".join(re.escape(l) for l in labels) + ")"
    return re.split(pat, text)[0].strip().rstrip(" ·-\u2013")


def groups_for(topic, ids):
    """Collapse tag IDs back to the survey's element names for display: 'Dispute
    resolution' is one chip, not the six syllabus points it expands to."""
    out = []
    for label, members in ELEM[topic].items():
        if any(m in ids for m in members):
            out.append(label)
    return out


items = []

# ---------------------------------------------------------------- Crime -----
d = docx.Document(CRIME)
qtable, mtable = d.tables[0], d.tables[1]
cols = [c.text.strip() for c in mtable.rows[1].cells][1:]
cols_crime = cols
tally_crime = [int(x) for x in [c.text.strip() for c in mtable.rows[-1].cells][1:] if x.isdigit()]
crime_rows = {}
for r in mtable.rows[2:]:
    cells = [c.text.strip() for c in r.cells]
    if not re.fullmatch(r"20\d\d", cells[0]):
        continue
    crime_rows[cells[0]] = dict(zip(cols, cells[1:]))

for r in qtable.rows[1:]:
    c = r.cells
    ycell = [p.text.strip() for p in c[0].paragraphs if p.text.strip()]
    year = ycell[0]
    qno = int(re.search(r"(\d+)", ycell[1]).group(1))
    stem = split_cell(c[1])
    meta = [p.text.strip() for p in c[2].paragraphs if p.text.strip()]
    stim = next((m for m in meta if m.lower().startswith("stimulus")), None)
    verb, band = directive_of(stem)
    core, sup = [], []
    for label, sym in crime_rows.get(year, {}).items():
        m = mark(sym)
        if m == "core": core += ELEM["crime"][label]
        elif m == "support": sup += ELEM["crime"][label]
    items.append({
        "s": "II-B", "topic": "crime", "y": int(year), "q": qno, "part": None,
        "l": f"Q{qno}", "m": 15, "t": stem,
        "core": core, "support": sup,
        "dir": verb, "band": band,
        "st": None if not stim else stim.split(":", 1)[1].strip(),
        "quoted": stem.lstrip().startswith(("'", "‘", '"')),
    })

# --------------------------------------------------------------- Family -----
d = docx.Document(FAMILY)
qtable, mtable = d.tables[0], d.tables[1]
cols = [c.text.strip() for c in mtable.rows[1].cells][1:]
cols_family = cols
tally_family = [int(x) for x in [c.text.strip() for c in mtable.rows[-1].cells][1:] if x.isdigit()]
fam_rows = {}
for r in mtable.rows[2:]:
    cells = [c.text.strip() for c in r.cells]
    mm = re.fullmatch(r"(20\d\d)\s*\((a|b)\)", cells[0])
    if not mm:
        continue
    fam_rows[(mm.group(1), mm.group(2))] = dict(zip(cols, cells[1:]))

for r in qtable.rows[1:]:
    c = r.cells
    ycell = [p.text.strip() for p in c[0].paragraphs if p.text.strip()]
    year = ycell[0]
    qno = int(re.search(r"(\d+)", ycell[1]).group(1))
    for idx, part in ((1, "a"), (2, "b")):
        stem = split_cell(c[idx])
        verb, band = directive_of(stem)
        core, sup = [], []
        for label, sym in fam_rows.get((year, part), {}).items():
            m = mark(sym)
            if m == "core": core += ELEM["family"][label]
            elif m == "support": sup += ELEM["family"][label]
        items.append({
            "s": "III", "topic": "family", "y": int(year), "q": qno, "part": part,
            "l": f"Q{qno}({part})", "m": 25, "t": stem,
            "core": core, "support": sup,
            "dir": verb, "band": band, "st": None,
            "quoted": stem.lstrip().startswith(("'", "‘", '"')),
        })

# -------------------------------------------------------------- Shelter -----
with pdfplumber.open(SHELTER) as pdf:
    qrows, mrows = [], []
    for page in pdf.pages:
        for tbl in page.extract_tables():
            if not tbl or not tbl[0]:
                continue
            width = len(tbl[0])
            if width >= 15:
                mrows += tbl
            elif width >= 3:
                qrows += tbl

shel_rows = {}
for row in mrows:
    # Alternate rows in the PDF carry their label in column 0 or column 1 —
    # a shading artefact of the rotated-header table. The fourteen symbol
    # columns are always the last fourteen either way.
    label = next((c for c in row[:2] if c and c.strip()), "")
    mm = re.match(r"(20\d\d)\s*\((a|b)\)", label.replace("\n", " ").strip())
    if not mm:
        continue
    syms = row[-len(SHELTER_COLS):]
    shel_rows[(mm.group(1), mm.group(2))] = dict(zip(SHELTER_COLS, syms))

tally_shelter = []
for row in mrows:
    if (row[0] or "").strip().lower().startswith("core"):
        tally_shelter = [int(x) for x in row[-len(SHELTER_COLS):] if x and x.strip().isdigit()]
year_re = re.compile(r"(20\d\d)")
qno_re = re.compile(r"Question\s*(\d+)")

# In this PDF a wrapped cell spills its continuation lines into the FOLLOWING
# table rows, in the same column — so a stem must be accumulated down the column
# until the next year row, or it comes out truncated at the first line break.
# The year label itself sits in column 0 or column 1 depending on row shading.
records = []
cur = None
for row in qrows:
    cells = [(c or "").replace("\n", " ").strip() for c in row]
    if any(c.startswith("Part (") or c == "Year" for c in cells):
        cur = None
        continue
    yi = next((i for i in (0, 1) if i < len(cells)
               and year_re.search(cells[i]) and qno_re.search(cells[i])), None)
    if yi is not None:
        idxs = [i for i, c in enumerate(cells) if c and i != yi]
        if len(idxs) < 2:
            cur = None
            continue
        cur = {"year": year_re.search(cells[yi]).group(1),
               "qno": int(qno_re.search(cells[yi]).group(1)),
               "cols": idxs[:2],
               "text": [cells[idxs[0]], cells[idxs[1]]]}
        records.append(cur)
    elif cur:
        for k, ci in enumerate(cur["cols"]):
            if ci < len(cells) and cells[ci]:
                cur["text"][k] += " " + cells[ci]

for rec in records:
    for idx, part in enumerate(("a", "b")):
        stem = strip_tagline(re.sub(r"\s+", " ", rec["text"][idx]).strip(), "shelter")
        verb, band = directive_of(stem)
        core, sup = [], []
        for label, sym in shel_rows.get((rec["year"], part), {}).items():
            m = mark(sym)
            if m == "core": core += ELEM["shelter"][label]
            elif m == "support": sup += ELEM["shelter"][label]
        items.append({
            "s": "III", "topic": "shelter", "y": int(rec["year"]), "q": rec["qno"], "part": part,
            "l": f"Q{rec['qno']}({part})", "m": 25, "t": stem,
            "core": core, "support": sup,
            "dir": verb, "band": band, "st": None,
            "quoted": stem.lstrip().startswith(("'", "\u2018", '"')),
        })

for it in items:
    it["cg"] = groups_for(it["topic"], set(it["core"]))
    it["sg"] = [g for g in groups_for(it["topic"], set(it["support"])) if g not in it["cg"]]

items.sort(key=lambda i: (i["topic"], i["y"], i["l"]))
os.makedirs(os.path.join(ROOT, "data"), exist_ok=True)
with open(os.path.join(ROOT, "data", "items-extended.json"), "w") as f:
    json.dump(items, f, ensure_ascii=False, indent=1)

with open(os.path.join(ROOT, "data", "groups.json"), "w") as f:
    json.dump({t: {lbl: ids[0] for lbl, ids in m.items()} for t, m in ELEM.items()},
              f, ensure_ascii=False, indent=1)

from collections import Counter
print("items:", len(items), Counter(i["topic"] for i in items))
print("no core tags:", [f'{i["topic"]} {i["y"]}{i["l"]}' for i in items if not i["core"]])
print("no directive:", [f'{i["topic"]} {i["y"]}{i["l"]}' for i in items if not i["dir"]])
dirty = [f'{i["topic"]} {i["y"]}{i["l"]}' for i in items
         if any(l in i["t"] for l in ELEM[i["topic"]])]
print("stems still carrying a tag label:", dirty or "none")
print("empty stem:", [f'{i["topic"]} {i["y"]}{i["l"]}' for i in items if len(i["t"]) < 25])

# ---------------------------------------------------------- verification ----
# Each survey prints its own core-focus tally. Recomputing it from the extracted
# core[] arrays and comparing is the check that the matrix was read correctly.
INV = {t: {vid: lbl for lbl, ids in m.items() for vid in ids} for t, m in ELEM.items()}
print("\n--- core tally: computed vs published ---")
ok = True
for topic, doc_cols, published in (
    ("crime", cols_crime, tally_crime),
    ("family", cols_family, tally_family),
    ("shelter", SHELTER_COLS, tally_shelter),
):
    got = Counter()
    for it in items:
        if it["topic"] != topic:
            continue
        for lbl in {INV[topic][c] for c in it["core"] if c in INV[topic]}:
            got[lbl] += 1
    for i, lbl in enumerate(doc_cols):
        want = published[i] if i < len(published) else None
        if want is None:
            continue
        flag = "" if got[lbl] == want else "   <-- MISMATCH"
        if flag: ok = False
        print(f"  {topic:8} {lbl:42} computed {got[lbl]:3}  published {want:3}{flag}")
print("ALL TALLIES MATCH" if ok else "TALLY MISMATCHES ABOVE")

# The Shelter stems come out of a PDF, where a wrapped cell spills into later
# rows; they are checked against the transcription verified against the papers.
exp_path = os.path.join(ROOT, "build", "expected-shelter-stems.txt")
if os.path.exists(exp_path):
    import unicodedata
    def norm(x):
        x = unicodedata.normalize("NFKD", x)
        for a, b in (("\u2018", "'"), ("\u2019", "'"), ("\u201c", '"'), ("\u201d", '"')):
            x = x.replace(a, b)
        return re.sub(r"\s+", " ", x).strip().lower()
    got = {(i["y"], i["part"]): i["t"] for i in items if i["topic"] == "shelter"}
    bad = 0
    for line in open(exp_path):
        if not line.strip():
            continue
        y, part, exp = line.rstrip("\n").split("|", 2)
        if norm(got.get((int(y), part), "")) != norm(exp):
            bad += 1
            print(f"  STEM MISMATCH {y}({part}): {got.get((int(y), part), '(missing)')!r}")
    print(f"shelter stems: {30 - bad}/30 match the verified transcription")
