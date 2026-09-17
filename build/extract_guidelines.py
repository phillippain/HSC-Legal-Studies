#!/usr/bin/env python3
"""Pull band criteria, sample answers and 'answers could include' out of the NESA
marking guidelines held in this repo (2015-2025).

The criteria are real two-column tables (Criteria | Marks), which is what makes
this reliable: the mark value is vertically centred on its band, so in plain text
it lands in the MIDDLE of the band's bullets and cannot be used to delimit them.
Reading the table cells sidesteps that entirely.
"""

import json, os, re
import pdfplumber

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

GUIDES = {
    2015: "legal-studies-hsc-mg-2015.pdf",
    2016: "2016-hsc-mg-legal-studies.pdf",
    2017: "2017-hsc-mg-legal-studies.pdf",
    2018: "2018-hsc-legal-studies-mg.pdf",
    2019: "2019-hsc-legal-studies-mg.pdf",
    2020: "2020-hsc-legal-studies-mg.pdf",
    2021: "2021-hsc-legal-studies-mg.pdf",
    2022: "2022-hsc-legal-studies-mg.pdf",
    2023: "2023-hsc-legal-studies-mg.pdf",
    2024: "2024-hsc-legal-studies-mg.pdf",
    2025: "2025-hsc-legal-studies-mg.pdf",
}

# Only the options this course teaches are carried into the site.
OPTIONS = {"family": "family", "shelter": "shelter"}

QHEAD = re.compile(r"^Question\s+(\d+)\s*(?:\((a|b)\))?\s*(?:[—–-]\s*(.+))?$")
FOOT = re.compile(r"^(Page \d+ of \d+|NESA \d{4}.*|BOSTES \d{4}.*|\d{4} HSC Legal Studies.*|"
                  r"Marking Guidelines|Section [I]+.*|Part [AB].*|Criteria|Marks)$", re.I)


def page_items(page):
    """Lines and tables on one page, in reading order, with table interiors removed
    from the line stream so a table's text is not read twice."""
    tables = page.find_tables()
    boxes = [t.bbox for t in tables]
    rows = {}
    for w in page.extract_words():
        if any(b[1] - 2 <= w["top"] <= b[3] + 2 and b[0] - 2 <= w["x0"] <= b[2] + 2 for b in boxes):
            continue
        rows.setdefault(round(w["top"]), []).append(w)
    out = []
    for top, ws in rows.items():
        text = " ".join(w["text"] for w in sorted(ws, key=lambda w: w["x0"])).strip()
        if text:
            out.append(("line", top, text))
    for t in tables:
        out.append(("table", t.bbox[1], t.extract()))
    out.sort(key=lambda x: x[1])
    return out


def clean(cell):
    return re.sub(r"\s+", " ", (cell or "").replace("\n", " ")).strip()


def bullets(cell):
    """Split a criteria cell into its bullet points."""
    text = clean(cell)
    parts = [p.strip(" .") for p in re.split(r"\s*•\s*", text) if p.strip(" .")]
    return parts or ([text] if text else [])


def parse(path, year):
    out, cur, mode = {}, None, None
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            for kind, _top, payload in page_items(page):
                if kind == "line":
                    m = QHEAD.match(payload.strip())
                    if m:
                        num, part, tail = m.group(1), m.group(2), (m.group(3) or "").strip()
                        if tail and not part:
                            # "Question 25 — Consumers" names the option for the
                            # (a)/(b) headings that follow it.
                            cur = {"num": int(num), "option": tail.lower(), "part": None}
                            mode = None
                            continue
                        cur = {"num": int(num), "part": part,
                               "option": (cur or {}).get("option") if part else None}
                        mode = None
                        continue
                    if re.match(r"^Sample answer", payload, re.I):
                        mode = "sample"; continue
                    if re.match(r"^Answers? could include", payload, re.I):
                        mode = "could"; continue
                    if FOOT.match(payload.strip()) or not cur or not mode:
                        continue
                    key = qkey(year, cur)
                    if key:
                        out.setdefault(key, {}).setdefault(mode, []).append(payload.strip())
                elif cur:
                    key = qkey(year, cur)
                    if not key:
                        continue
                    bands = []
                    for row in payload:
                        if len(row) < 2:
                            continue
                        crit, marks = clean(row[0]), clean(row[1])
                        if not marks or crit.lower().startswith("criteria"):
                            continue
                        bands.append({"m": marks, "b": bullets(crit)})
                    if bands:
                        out.setdefault(key, {}).setdefault("criteria", []).extend(bands)
                    mode = None
    return out


def qkey(year, cur):
    """Map a guidelines heading onto the question ids the site already uses."""
    if cur.get("option") is not None:
        opt = cur["option"]
        topic = next((v for k, v in OPTIONS.items() if k in opt), None)
        if not topic or not cur.get("part"):
            return None
        return f"{year}|III|Q{cur['num']}({cur['part']})"
    n = cur["num"]
    if n <= 20:
        return None
    return f"{year}|{'II-A' if n < 24 or True else 'II-B'}|Q{n}"


if __name__ == "__main__":
    # Part A runs 21-23 or 21-24 and Part B is the next number, so the split is
    # taken from the questions already extracted rather than guessed.
    items = json.load(open(f"{ROOT}/data/items-papers.json"))["items"]
    parta = {(i["y"], i["q"]) for i in items if i["s"] == "II-A"}

    all_g = {}

    # 2011-2014 are not held here as PDFs. Their guidelines were read from the
    # Board of Studies archive through pdf.js, where the marks column can be
    # separated by x-position and each bullet assigned to its NEAREST mark — which
    # is what the centred mark column actually means. Saved under data/archive/.
    arch_dir = os.path.join(ROOT, "data", "archive")
    if os.path.isdir(arch_dir):
        for fn in sorted(os.listdir(arch_dir)):
            if fn.endswith(".json"):
                all_g.update(json.load(open(os.path.join(arch_dir, fn), encoding="utf-8")))

    for year, fn in sorted(GUIDES.items()):
        g = parse(os.path.join(ROOT, fn), year)
        fixed = {}
        for k, v in g.items():
            y, sec, lab = k.split("|")
            if sec == "II-A":
                n = int(lab[1:])
                sec = "II-A" if (int(y), n) in parta else "II-B"
            fixed[f"{y}|{sec}|{lab}"] = v
        all_g.update(fixed)
        n_crit = sum(1 for k, v in fixed.items() if v.get("criteria"))
        n_samp = sum(1 for k, v in fixed.items() if v.get("sample"))
        print(f"{year}: {len(fixed):>2} questions · {n_crit} with criteria · {n_samp} with a sample answer")

    resolved = {}
    for k, v in all_g.items():
        y, sec, lab = k.split("|")
        if sec in ("II-?", "II-A"):
            sec = "II-A" if (int(y), int(lab[1:])) in parta else "II-B"
        resolved[f"{y}|{sec}|{lab}"] = v
    all_g = resolved

    for v in all_g.values():
        for f in ("sample", "could"):
            if f in v:
                v[f] = [re.sub(r"\s+", " ", x).strip() for x in v[f] if x.strip()]

    with open(f"{ROOT}/data/guidelines.json", "w") as f:
        json.dump(all_g, f, ensure_ascii=False, indent=1)
    print(f"\ntotal: {len(all_g)} questions with marking material")
