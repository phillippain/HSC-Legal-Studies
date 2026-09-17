#!/usr/bin/env python3
"""Merge the Section I / Section II Part A questions with their content-point tags
into the same record shape the extended responses use."""

import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DIRECTIVES = [
    ("to what extent", "evaluate", 4), ("how effective", "evaluate", 4),
    ("critically analyse", "evaluate", 4), ("evaluate", "evaluate", 4), ("assess", "evaluate", 4),
    ("analyse", "analyse", 3), ("discuss", "analyse", 3),
    ("compare", "explain", 2), ("explain", "explain", 2), ("examine", "explain", 2),
    ("how does", "explain", 2), ("how has", "explain", 2), ("how are", "explain", 2),
    ("how can", "explain", 2), ("how is", "explain", 2), ("why is", "explain", 2),
    ("how do", "explain", 2), ("what impact", "explain", 2), ("why are", "explain", 2),
    ("when are", "describe", 1), ("what is", "describe", 1),
    ("describe", "describe", 1), ("outline", "describe", 1),
    ("identify", "describe", 1), ("define", "describe", 1), ("list", "describe", 1),
]

def directive_of(text):
    low = text.lower()
    best = None
    for verb, name, band in DIRECTIVES:
        i = low.find(verb)
        if i >= 0 and (best is None or i < best[0]):
            best = (i, name, band)
    return (best[1], best[2]) if best else (None, None)

def load_tags():
    tags, path = {}, os.path.join(ROOT, "data", "tags-papers.txt")
    for ln in open(path, encoding="utf-8"):
        ln = ln.strip()
        if not ln or ln.startswith("#"):
            continue
        key, rest = re.split(r"\s{2,}|\t", ln, maxsplit=1)
        core, _, sup = rest.partition(">")
        tags[key.strip()] = (
            [c.strip() for c in core.split(",") if c.strip()],
            [s.strip() for s in sup.split(",") if s.strip()],
        )
    return tags

def valid_ids(syl):
    ids = set()
    for t in syl["topics"].values():
        for th in t["themes"]:
            ids.add(th["id"])
        for s in t["sections"]:
            ids.add(s["id"])
            for p in s["points"]:
                ids.add(p["id"])
    return ids

def build():
    syl = json.load(open(f"{ROOT}/data/syllabus.json"))
    raw = json.load(open(f"{ROOT}/data/items-papers.json"))
    tags = load_tags()
    ok = valid_ids(syl)

    problems, out = [], []
    for it in raw["items"]:
        key = f"{it['y']}|{it['s']}|{it['l']}"
        if key not in tags:
            problems.append(f"untagged: {key}")
            continue
        core, sup = tags[key]
        for c in core + sup:
            if c not in ok:
                problems.append(f"unknown tag id {c} on {key}")
        topic = "humanrights" if core and core[0].startswith("hr.") else "crime"
        verb, band = directive_of(it["t"]) if it["s"] == "II-A" else (None, None)
        rec = {
            "s": it["s"], "topic": topic, "y": it["y"], "q": it["q"], "part": None,
            "l": it["l"], "m": it["m"], "t": it["t"],
            "core": core, "support": sup,
            "dir": verb, "band": band,
            "st": it.get("st"),
            "quoted": it["t"].lstrip().startswith(("'", "‘", '"')),
        }
        if it["s"] == "I":
            rec["opts"] = it["opts"]
            rec["ans"] = raw["key"][str(it["y"])].get(str(it["q"]))
            if it.get("needsPaper"):
                rec["needsPaper"] = True
        out.append(rec)

    # The syllabus fixes Section I at 15 marks of Crime and 5 of Human Rights, so
    # every year must come out 15/5. It is the only independent check available on
    # whether a borderline question was filed under the right core.
    from collections import Counter
    split = Counter((i["y"], i["topic"]) for i in out if i["s"] == "I")
    for y in sorted({i["y"] for i in out}):
        hr = split[(y, "humanrights")]
        if hr != 5:
            problems.append(f"{y} Section I is {split[(y, 'crime')]} crime / {hr} human rights, "
                            f"but the syllabus sets 15 marks crime / 5 human rights")

    for key in tags:
        if not any(f"{i['y']}|{i['s']}|{i['l']}" == key for i in out):
            problems.append(f"tag with no question: {key}")

    return out, problems

if __name__ == "__main__":
    items, problems = build()
    with open(f"{ROOT}/data/items-papers-tagged.json", "w") as f:
        json.dump(items, f, ensure_ascii=False, indent=1)
    from collections import Counter
    print("tagged items:", len(items), Counter(i["topic"] for i in items),
          Counter(i["s"] for i in items))
    print("MC without an answer:", [f"{i['y']} {i['l']}" for i in items
                                    if i["s"] == "I" and not i.get("ans")] or "none")
    print("short answers without a directive:",
          [f"{i['y']} {i['l']}" for i in items if i["s"] == "II-A" and not i["dir"]] or "none")
    print("problems:", problems or "none")
