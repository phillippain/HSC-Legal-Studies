#!/usr/bin/env python3
"""Check the built evidence.html. Run after build_evidence.py.

Everything here is an invariant of the syllabus or of the page contract, so a
failure means the data or the template is wrong rather than the build script.
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))
from evidence_lib import load_records, syllabus_index, check_tags, TYPES, CRITERIA

def main():
    fail = []
    syl = json.load(open(f"{ROOT}/data/syllabus.json"))
    recs, problems = load_records()
    idx = syllabus_index(syl)
    fail += problems + check_tags(recs, idx)

    html = open(f"{ROOT}/evidence.html", encoding="utf-8").read()
    m = re.search(r"<script>const DATA = (\{.*?\});</script>", html, re.S)
    if not m:
        sys.exit("could not find the DATA block in evidence.html")
    d = json.loads(m.group(1))

    # 1. the page holds exactly the records on disk
    if len(d["items"]) != len(recs):
        fail.append(f"page has {len(d['items'])} records, evidence/ has {len(recs)}")
    if d["meta"]["records"] != len(recs):
        fail.append("meta.records disagrees with the item count")

    # 2. every tag on the page resolves, and core/support never carry a theme
    tag_ids = set(idx)
    theme_ids = {k for k, v in idx.items() if v["kind"] == "theme"}
    for it in d["items"]:
        where = it["id"]
        if not it["core"]:
            fail.append(f"{where}: no core tag")
        if not it["sig"]:
            fail.append(f"{where}: no significance line")
        if len(it["sig"]) > 220:
            fail.append(f"{where}: significance is {len(it['sig'])} characters — it is a one-liner")
        if not it["body"]:
            fail.append(f"{where}: the summary rendered empty")
        for t in it["core"] + it["support"]:
            if t not in tag_ids:
                fail.append(f"{where}: unknown tag {t}")
            elif t in theme_ids:
                fail.append(f"{where}: theme {t} in core/support")
        for t in it["themes"]:
            if t not in theme_ids:
                fail.append(f"{where}: {t} in themes is not a theme")
        for c in it["criteria"]:
            if c not in CRITERIA:
                fail.append(f"{where}: unknown criterion {c}")
        if it["type"] not in TYPES:
            fail.append(f"{where}: unknown type {it['type']}")
        if set(it["core"]) & set(it["support"]):
            fail.append(f"{where}: {', '.join(sorted(set(it['core']) & set(it['support'])))} is both core and supporting")

    ids = {it["id"] for it in d["items"]}
    for it in d["items"]:
        for r in it["related"]:
            if r not in ids:
                fail.append(f"{it['id']}: related {r} does not exist")
            if r == it["id"]:
                fail.append(f"{it['id']}: related to itself")

    # 2b. a record that names a document must name one that is actually there
    try:
        lib = json.load(open(f"{ROOT}/data/library.json"))
        known = {f["path"] for f in lib["files"]}
        for r in recs:
            if r.get("document") and r["document"] not in known:
                fail.append(f"{r['file']}: document `{r['document']}` is not in the library folder")
        if not os.path.isdir(lib["root"]):
            print(f"  note: the library folder is not mounted here ({lib['root']})")
    except FileNotFoundError:
        pass

    # 3. every topic in the syllabus reaches the page, with a colour slot and an icon
    if len(d["topics"]) != len(syl["topics"]):
        fail.append("not every syllabus topic reached the page")
    for t in d["topics"]:
        if t["slot"] not in (1, 2, 3, 4, 5):
            fail.append(f"{t['k']}: colour slot {t['slot']} is outside the validated palette")
        if f'id="{t["icon"]}"' not in html:
            fail.append(f"{t['k']}: icon {t['icon']} is not in the sprite")

    # 4. every icon reference resolves — catches a renamed symbol
    symbols = set(re.findall(r'<symbol id="([^"]+)"', html))
    for ref in set(re.findall(r'href="#(g-[a-z-]+)"', html)):
        if ref not in symbols:
            fail.append(f"icon {ref} is used but not defined in the sprite")

    # 5. the placeholder was substituted and the page is self-contained apart from fonts
    if "__DATA__" in html:
        fail.append("the __DATA__ placeholder is still in the page")
    for src in re.findall(r'<(?:script|link)[^>]*(?:src|href)="(https?://[^"]+)"', html):
        if not src.startswith("https://fonts."):
            fail.append(f"the page loads something other than fonts: {src}")

    # ------------------------------------------------------------- report --
    by_type = {k: sum(1 for i in d["items"] if i["type"] == k) for k in TYPES}
    points = [p for t in d["topics"] for s in t["sections"] for p in s["points"]]
    own = {}
    for i in d["items"]:
        for t in i["core"] + i["support"]:
            own[t] = own.get(t, 0) + 1
    covered = [p for p in points if own.get(p["id"])]
    print(f"evidence.html {len(html):,} bytes · {len(d['items'])} records · {len(d['topics'])} topics")
    print("  by type:  " + " · ".join(f"{TYPES[k]['label']} {v}" for k, v in by_type.items() if v))
    print(f"  coverage: {len(covered)}/{len(points)} dot points, "
          f"{len({t for i in d['items'] for t in i['themes']})} themes, "
          f"{len({c for i in d['items'] for c in i['criteria']})}/{len(CRITERIA)} criteria")
    for t in d["topics"]:
        pts = [p for s in t["sections"] for p in s["points"]]
        print(f"    {t['label']:<28}{sum(1 for p in pts if own.get(p['id'])):>3}/{len(pts):<4} dot points covered")
    print()
    if fail:
        print("FAILED:")
        for f in fail:
            print("  " + f)
        sys.exit(1)
    print("all checks passed")

if __name__ == "__main__":
    main()
