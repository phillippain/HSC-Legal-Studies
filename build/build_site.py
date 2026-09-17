#!/usr/bin/env python3
"""Assemble index.html from syllabus.json + the extracted item sets."""

import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
syl = json.load(open(f"{ROOT}/data/syllabus.json"))
items = json.load(open(f"{ROOT}/data/items-extended.json"))
groups = json.load(open(f"{ROOT}/data/groups.json"))
guidelines = json.load(open(f"{ROOT}/data/guidelines.json"))

# Section I and Section II Part A come from the papers themselves and are tagged at
# dot-point level, so they carry no survey-element groups; the page falls back to
# rendering their tag IDs directly.
import importlib.util
spec = importlib.util.spec_from_file_location("merge_papers", f"{ROOT}/build/merge_papers.py")
mp = importlib.util.module_from_spec(spec); spec.loader.exec_module(mp)
papers, problems = mp.build()
if problems:
    raise SystemExit("merge_papers reported problems:\n  " + "\n  ".join(problems))
items = items + papers

# Human Rights and Section I come later; the topic still appears so the coverage
# heatmap shows its elements as unexamined-so-far rather than hiding them.
ORDER = ["crime", "humanrights", "family", "shelter"]
topics = []
for k in ORDER:
    t = syl["topics"][k]
    topics.append({
        "k": k, "label": t["label"], "part": t["part"],
        "themes": t["themes"], "sections": t["sections"],
    })

# Group chips are drawn in the colour of the element they stand for, which is the
# colour of the first tag ID in the group.
colour = {}
for k, t in syl["topics"].items():
    for th in t["themes"]:
        colour[th["id"]] = th["colour"]
    for sec in t["sections"]:
        colour[sec["id"]] = sec["colour"]
        for pt in sec["points"]:
            colour[pt["id"]] = sec["colour"]
GROUPS = {t: {lbl: colour[rep] for lbl, rep in m.items()} for t, m in groups.items()}

data = {
    "meta": {
        "firstYear": min(i["y"] for i in items),
        "lastYear": max(i["y"] for i in items),
        "syllabus": syl["meta"]["syllabus"],
    },
    "bands": syl["demandBands"],
    "groups": GROUPS,
    "crit": guidelines,
    "topics": topics,
    "items": items,
}

tpl = open(f"{ROOT}/build/template.html").read()
out = tpl.replace("__DATA__", json.dumps(data, ensure_ascii=False, separators=(",", ":")))
with open(f"{ROOT}/index.html", "w") as f:
    f.write(out)

print(f"index.html  {len(out):,} bytes  ·  {len(items)} items  ·  {len(topics)} topics")

# ------------------------------------------------------------ sanity checks --
tagids = set()
for t in topics:
    for th in t["themes"]:
        tagids.add(th["id"])
    for s in t["sections"]:
        tagids.add(s["id"])
        for p in s["points"]:
            tagids.add(p["id"])

bad = set()
for it in items:
    for c in it["core"] + it["support"]:
        if c not in tagids:
            bad.add(c)
print("unknown tag ids:", sorted(bad) or "none")
print("items with no core:", sum(1 for i in items if not i["core"]))
print("placeholder left in html:", "__DATA__" in out)
