#!/usr/bin/env python3
"""Read the evidence records in evidence/ and the syllabus tree they are tagged against.

A record is one markdown file: a header of `key: value` lines between `---` fences,
then the summary itself. List values are comma-separated, so a record can be edited
in any text editor without quoting or indentation rules to remember.
"""

import os, re, sys, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVIDENCE = os.path.join(ROOT, "evidence")

# The six forms of evidence the syllabus itself names (outcome H8/P8), plus the
# research and non-legal material a judgement of effectiveness needs.
TYPES = {
    "legislation":   {"label": "Legislation",             "icon": "g-book",    "colour": "#1F3864"},
    "case":          {"label": "Case law",                "icon": "g-gavel",   "colour": "#4A3AA7"},
    "international": {"label": "International instrument","icon": "g-globe",   "colour": "#0F6E6E"},
    "report":        {"label": "Report & statistics",     "icon": "g-chart",   "colour": "#1E6B4F"},
    "media":         {"label": "Media",                   "icon": "g-news",    "colour": "#A3480C"},
    "document":      {"label": "Document & non-legal",    "icon": "g-doc",     "colour": "#A31545"},
}

# The syllabus's own criteria for evaluating effectiveness (Preliminary Part III),
# which apply to every topic in both courses and are what a judgement is built on.
CRITERIA = {
    "resource":       "Resource efficiency",
    "accessibility":  "Accessibility",
    "enforceability": "Enforceability",
    "responsiveness": "Responsiveness",
    "rights":         "Protection of individual rights",
    "society":        "Meeting society's needs",
    "ruleoflaw":      "Application of the rule of law",
    "justice":        "Has justice been achieved?",
}

REQUIRED = ["type", "title", "significance", "core"]
LISTS = ["core", "support", "themes", "criteria", "related"]
KNOWN = set(REQUIRED + LISTS + ["short", "citation", "date", "jurisdiction",
                                "source", "added", "status", "document"])


class RecordError(Exception):
    pass


def parse(path):
    raw = open(path, encoding="utf-8").read()
    m = re.match(r"﻿?---\s*\n(.*?)\n---\s*\n?(.*)\Z", raw, re.S)
    if not m:
        raise RecordError(f"{os.path.relpath(path, ROOT)}: no `---` header block")
    head, body = m.group(1), m.group(2).strip()

    rec = {k: [] for k in LISTS}
    for n, line in enumerate(head.split("\n"), 2):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            raise RecordError(f"{os.path.relpath(path, ROOT)}:{n}: no colon in `{line.strip()}`")
        k, v = line.split(":", 1)
        k, v = k.strip().lower(), v.strip()
        if k not in KNOWN:
            raise RecordError(f"{os.path.relpath(path, ROOT)}:{n}: unknown field `{k}` "
                              f"(known: {', '.join(sorted(KNOWN))})")
        if k in LISTS:
            rec[k] = [p.strip() for p in v.split(",") if p.strip()]
        else:
            # a value may be wrapped in quotes out of YAML habit; the quotes are not
            # part of the value, and a citation that starts with `[` usually is
            if len(v) > 1 and v[0] == v[-1] and v[0] in "\"'":
                v = v[1:-1].replace('\\"', '"').replace("\\'", "'")
            rec[k] = v

    rec["id"] = os.path.splitext(os.path.basename(path))[0]
    rec["file"] = os.path.relpath(path, ROOT)
    rec["body"] = body
    for k in REQUIRED:
        if not rec.get(k):
            raise RecordError(f"{rec['file']}: `{k}` is required")
    if rec["type"] not in TYPES:
        raise RecordError(f"{rec['file']}: type `{rec['type']}` is not one of "
                          f"{', '.join(TYPES)}")
    if not rec.get("short"):
        rec["short"] = rec["title"]
    for c in rec["criteria"]:
        if c not in CRITERIA:
            raise RecordError(f"{rec['file']}: criterion `{c}` is not one of "
                              f"{', '.join(CRITERIA)}")
    # `document` points at the file in the library folder that this record summarises
    if rec.get("document"):
        rec["document"] = rec["document"].lstrip("/")
    for f in ("date", "added"):
        if rec.get(f) and not re.fullmatch(r"\d{4}(-\d{2}(-\d{2})?)?", rec[f]):
            raise RecordError(f"{rec['file']}: `{f}` must be YYYY, YYYY-MM or YYYY-MM-DD")
    return rec


def load_records():
    recs, problems, seen = [], [], {}
    for dirpath, _, names in os.walk(EVIDENCE):
        for n in sorted(names):
            if not n.endswith(".md") or n == "README.md":
                continue
            p = os.path.join(dirpath, n)
            try:
                r = parse(p)
            except RecordError as e:
                problems.append(str(e))
                continue
            if r["id"] in seen:
                problems.append(f"{r['file']}: id `{r['id']}` already used by {seen[r['id']]}")
                continue
            seen[r["id"]] = r["file"]
            recs.append(r)
    recs.sort(key=lambda r: (r["type"], r.get("date", ""), r["title"]))
    return recs, problems


def syllabus_index(syl):
    """id -> {kind, label, topic, course, section} for every tag a record may carry."""
    idx = {}
    for tk, t in syl["topics"].items():
        common = {"topic": tk, "topicLabel": t["label"], "course": t.get("course", "hsc")}
        for th in t["themes"]:
            idx[th["id"]] = dict(common, kind="theme", label=th["label"], section=None)
        for s in t["sections"]:
            idx[s["id"]] = dict(common, kind="section", label=s["label"], section=s["id"])
            for p in s["points"]:
                idx[p["id"]] = dict(common, kind="point", label=p["label"], section=s["id"])
    return idx


def check_tags(recs, idx):
    problems = []
    for r in recs:
        for field in ("core", "support"):
            for t in r[field]:
                if t not in idx:
                    problems.append(f"{r['file']}: {field} tag `{t}` is not in the syllabus")
                elif idx[t]["kind"] == "theme":
                    problems.append(f"{r['file']}: `{t}` is a theme — put it in `themes:`")
        for t in r["themes"]:
            if t not in idx:
                problems.append(f"{r['file']}: theme `{t}` is not in the syllabus")
            elif idx[t]["kind"] != "theme":
                problems.append(f"{r['file']}: `{t}` is a content tag — put it in `core:` or `support:`")
        ids = {x["id"] for x in recs}
        for t in r["related"]:
            if t not in ids:
                problems.append(f"{r['file']}: related `{t}` is not an evidence id")
    return problems


if __name__ == "__main__":
    import json
    syl = json.load(open(f"{ROOT}/data/syllabus.json"))
    recs, problems = load_records()
    problems += check_tags(recs, syllabus_index(syl))
    print(f"{len(recs)} records")
    for p in problems:
        print("  " + p)
    sys.exit(1 if problems else 0)
