#!/usr/bin/env python3
"""Read the examination papers held in this repo and pull out Section I objective
response and Section II Part A short answer, plus the multiple-choice answer key
from the marking guidelines.

Only 2015-2025 are held here. 2011-2014 remain on the Board of Studies archive.
"""

import json, os, re
import pdfplumber

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PAPERS = {
    2015: "legal-studies-hsc-exam-2015.pdf",
    2016: "2016-hsc-legal-studies.pdf",
    2017: "2017-hsc-legal-studies.pdf",
    2018: "2018-hsc-legal-studies.pdf",
    2019: "2019-hsc-legal-studies.pdf",
    2020: "2020-hsc-legal-studies.pdf",
    2021: "2021-hsc-legal-studies.pdf",
    2022: "2022-hsc-legal-studies.pdf",
    2023: "2023-hsc-legal-studies.pdf",
    2024: "2024-hsc-legal-studies.pdf",
    2025: "2025-hsc-legal-studies.pdf",
}
# 2011-2014 are not on NESA's current site and no PDF is held here. Their text was
# read from the Board of Studies archive through pdf.js in the browser pane and
# saved under source-documents/archive-2011-2014/, so the pipeline still runs if
# that archive disappears.
ARCHIVE = {y: f"source-documents/archive-2011-2014/{y}-paper.txt" for y in (2011, 2012, 2013, 2014)}

# Answer keys for those years, transcribed from the archive marking guidelines
# (2011 legal-studies-marking-guide-11.pdf, 2012 legal-studies-marking-guide-12.pdf,
# 2013 2013-marking-guide-legal-studies.pdf, 2014 2014-mg-legal-studies.pdf).
ARCHIVE_KEYS = {
 2011: "DBACABBCACCADBCDACAB",
 2012: "DBADBDBCABCCDAACCDBC",
 2013: "BBDCACDDDBBCAACBDAAB",
 2014: "DBCCBACBCBAACDBBCCDC",
}

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

# Page furniture. NESA answer booklets carry barcodes, "Office Use Only" rules and
# a vertical "Do NOT write in this area" that extracts one word per line, upside
# down. None of it is question text.
NOISE = re.compile(
    r"^(?:\s*$|[–—-]\s*\d+\s*[–—-]$|\d{6,}$|\d{4}\s*[–—-]\s*\d+\s*[–—-]$"
    r"|Office Use Only.*|Do\s*NOT\s*write.*|\.?aera$|siht$|ni$|etirw$|TON$|oD$|Do$|NOT$|write$|in$|this$|area\.?$"
    r"|Please turn over$|Turn over.*|End of .*|©.*|\d{4} HIGHER SCHOOL CERTIFICATE.*|HIGHER SCHOOL.*"
    r"|Legal Studies$|Centre Number$|Student Number$|Section I+.*|Part [AB].*|Question Number$"
    r"|\d\s\d$|BLANK PAGE$|Examination materials.*|Disclaimer.*)",
    re.I,
)

def page_text(path):
    if path.lower().endswith(".txt"):
        return open(path, encoding="utf-8").read()
    with pdfplumber.open(path) as pdf:
        return "\n".join((p.extract_text() or "") for p in pdf.pages)

def clean_lines(block):
    out = []
    for ln in block.split("\n"):
        ln = ln.replace("\xa0", " ").rstrip()
        # answer-space dot leaders
        ln = re.sub(r"\.{5,}", "", ln).strip()
        if not ln or NOISE.match(ln):
            continue
        out.append(ln)
    return out

# ------------------------------------------------------------ Section I -----
# 2015-2016 letter their options "(A)"; 2017 onward use "A.". The bracket or the
# full stop must be required: a bare "^[A-D] " also matches a stem that opens
# "A well-known public figure...", which silently emptied 38 stems.
OPT = re.compile(r"^(?:\(([A-D])\)|([A-D])[.)])\s+(.*)$")

# Several papers set a scenario once and hang three or four questions off it.
# Without this the scenario is swallowed by the previous question's last option.
STIM = re.compile(r"^Use the following information to answer Questions?\s+"
                  r"(\d+)\s*(?:[–—-]|and)\s*(\d+)", re.I)

def section_one(text, year):
    # "Section I" appears first on the cover page, where the instructions for
    # all three sections sit together. The real block is the longest one.
    cands = [mm.group(1) for mm in re.finditer(r"\bSection I\b(.*?)(?=\bSection II\b)", text, re.S)]
    if not cands:
        return []
    lines = clean_lines(max(cands, key=len))

    # Walk the lines picking up question boundaries in order: a line beginning
    # with the next expected number. Numbering is strictly 1..20, so an in-order
    # walk cannot be fooled by a number appearing inside a stem.
    blocks, cur, nxt = [], None, 1
    stims, collecting = [], None
    for ln in lines:
        sm = STIM.match(ln)
        if sm:
            collecting = {"lo": int(sm.group(1)), "hi": int(sm.group(2)), "lines": []}
            stims.append(collecting)
            cur = None
            continue
        mm = re.match(r"^(\d{1,2})\s+(.*)$", ln)
        if mm and int(mm.group(1)) == nxt and not OPT.match(ln):
            collecting = None
            cur = {"q": nxt, "lines": [mm.group(2).strip()]}
            blocks.append(cur)
            nxt += 1
        elif collecting is not None:
            collecting["lines"].append(ln)
        elif cur is not None:
            cur["lines"].append(ln)
    for st in stims:
        st["text"] = re.sub(r"\s+", " ", " ".join(st["lines"])).strip()

    out = []
    for b in blocks:
        stem, opts, letter = [], {}, None
        for ln in b["lines"]:
            om = OPT.match(ln)
            if om:
                letter = om.group(1) or om.group(2)
                opts[letter] = om.group(3).strip()
            elif letter:
                opts[letter] += " " + ln.strip()
            else:
                stem.append(ln)
        shared = next((st["text"] for st in stims if st["lo"] <= b["q"] <= st["hi"]), None)
        out.append({
            "y": year, "s": "I", "q": b["q"], "l": f"Q{b['q']}", "m": 1,
            "t": re.sub(r"\s+", " ", " ".join(stem)).strip(),
            "opts": [[k, re.sub(r"\s+", " ", opts[k]).strip()] for k in "ABCD" if k in opts],
            "st": shared,
        })
        out[-1]["needsPaper"] = bool(
            NEEDS_PAPER.search(out[-1]["t"]) or any(NEEDS_PAPER.search(o[1]) for o in out[-1]["opts"]))
    return out

# A handful of questions are built on a table printed in the paper, which has no
# text layer worth reproducing. They are flagged so the page can send the student
# to the paper rather than showing a stem that makes no sense on its own.
NEEDS_PAPER = re.compile(
    r"\b(the table|the diagram|the graph|the chart|the extract|the source|the figure"
    r"|the image|the cartoon|following table|row of the)\b", re.I)


# ----------------------------------------------------- Section II Part A ----
QHEAD = re.compile(r"^Question\s+(\d+)\s*\((\d+)\s*marks?\)\s*(.*)$", re.I)

def section_two_a(text, year):
    m = re.search(r"Part A\s*[–—-]\s*Human Rights(.*?)(?=Part B\s*[–—-]\s*Crime)", text, re.S)
    if not m:
        return []
    lines = clean_lines(m.group(1))
    blocks, cur = {}, None
    for ln in lines:
        hm = QHEAD.match(ln)
        if hm:
            q, marks = int(hm.group(1)), int(hm.group(2))
            cur = {"q": q, "m": marks, "lines": [hm.group(3)] if hm.group(3) else []}
            # 2015 prints a question head twice, once as a turn-the-page teaser
            # with no stem under it. Keep whichever copy actually carries text.
            if q not in blocks or not blocks[q]["lines"]:
                blocks[q] = cur
            else:
                cur = blocks[q]
        elif cur is not None:
            cur["lines"].append(ln)

    out = []
    for q in sorted(blocks):
        b = blocks[q]
        stem = re.sub(r"\s+", " ", " ".join(b["lines"])).strip()
        # Some years print the mark value again at the end of the stem line.
        stem = re.sub(r"\s*If you require more space.*$", "", stem, flags=re.I).strip()
        # The mark value is printed in the right margin and lands inside the stem
        # text, sometimes mid-sentence ("...another independent 3 statutory authority").
        stem = re.sub(r"(?:^|(?<= ))%d(?= |$)" % b["m"], "", stem, count=1).strip()
        stem = re.sub(r"\s{2,}", " ", stem)
        out.append({"y": year, "s": "II-A", "q": q, "l": f"Q{q}", "m": b["m"], "t": stem})
    return out

# ------------------------------------------------- multiple-choice key ------
def answer_key(text):
    m = re.search(r"Multiple[- ]choice Answer Key(.*?)(?=Section I\s*I|Question\s+21)", text, re.S | re.I)
    block = m.group(1) if m else text[:4000]
    key = {}
    # Most rows are "7 C". A disputed question is recorded as NESA printed it —
    # 2018 has "9 No best answer*" and "19 B and D*", both of which are answers
    # a student should see rather than gaps in the key.
    for qn, ans in re.findall(r"^\s*(\d{1,2})\s+([A-D]|[A-D] and [A-D]\*?|No best answer\*?)\s*$",
                              block, re.M):
        key[int(qn)] = ans.rstrip("*").strip()
    return key

# ------------------------------------------------------------------ run -----
if __name__ == "__main__":
    items, keys, report = [], {}, []
    sources = dict(ARCHIVE)
    sources.update(PAPERS)
    for year, fn in sorted(sources.items()):
        path = os.path.join(ROOT, fn)
        txt = page_text(path)
        mc = section_one(txt, year)
        sa = section_two_a(txt, year)
        if year in ARCHIVE_KEYS:
            k = {i + 1: c for i, c in enumerate(ARCHIVE_KEYS[year])}
        else:
            k = answer_key(page_text(os.path.join(ROOT, GUIDES[year])))
        keys[year] = k
        items += mc + sa
        report.append((year, len(mc), len(sa), sum(i["m"] for i in sa), len(k),
                       sum(1 for i in mc if len(i["opts"]) != 4)))

    with open(os.path.join(ROOT, "data", "items-papers.json"), "w") as f:
        json.dump({"items": items, "key": keys}, f, ensure_ascii=False, indent=1)

    print(f"{'year':>5} {'MC':>3} {'SA':>3} {'SAmarks':>8} {'key':>4} {'badopts':>8}")
    for r in report:
        flag = "" if (r[1] == 20 and r[4] == 20 and r[3] == 15 and r[5] == 0) else "   <-- CHECK"
        print(f"{r[0]:>5} {r[1]:>3} {r[2]:>3} {r[3]:>8} {r[4]:>4} {r[5]:>8}{flag}")
    print(f"\ntotal items: {len(items)}")
