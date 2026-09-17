#!/usr/bin/env python3
"""Check the built index.html — the last step of the pipeline.

Everything here is an invariant of the examination itself, not of the code, so a
failure means the data is wrong rather than the build. Run it after build_site.py.
"""

import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load():
    html = open(f"{ROOT}/index.html", encoding="utf-8").read()
    m = re.search(r"<script>const DATA = (\{.*?\});</script>", html, re.S)
    if not m:
        sys.exit("could not find the DATA block in index.html")
    return json.loads(m.group(1)), len(html)

def main():
    d, size = load()
    items, crit = d["items"], d["crit"]
    fail = []

    tag_ids = set()
    for t in d["topics"]:
        for th in t["themes"]:
            tag_ids.add(th["id"])
        for s in t["sections"]:
            tag_ids.add(s["id"])
            for p in s["points"]:
                tag_ids.add(p["id"])

    seen = set()
    for it in items:
        qid = f"{it['topic']}{it['y']}{it['l']}"
        if qid in seen:
            fail.append(f"duplicate question id {qid}")
        seen.add(qid)
        if not it["core"]:
            fail.append(f"{qid} has no core tag")
        for c in it["core"] + it["support"]:
            if c not in tag_ids:
                fail.append(f"{qid} carries unknown tag {c}")
        if len(it["t"]) < 10:
            fail.append(f"{qid} has a suspiciously short stem")
        if it["s"] == "I":
            if len(it.get("opts") or []) != 4:
                fail.append(f"{qid} does not have four options")
            if not it.get("ans"):
                fail.append(f"{qid} has no answer")

    # The examination's own shape, year by year.
    for y in range(2011, 2026):
        mc = [i for i in items if i["y"] == y and i["s"] == "I"]
        sa = [i for i in items if i["y"] == y and i["s"] == "II-A"]
        pb = [i for i in items if i["y"] == y and i["s"] == "II-B"]
        s3 = [i for i in items if i["y"] == y and i["s"] == "III"]
        hr = sum(1 for i in mc if i["topic"] == "humanrights")
        if len(mc) != 20:
            fail.append(f"{y}: {len(mc)} objective-response questions, expected 20")
        if hr != 5:
            fail.append(f"{y}: {hr} Human Rights objective-response questions, expected 5 "
                        f"(the syllabus sets 15 marks Crime / 5 Human Rights)")
        if sum(i["m"] for i in sa) != 15:
            fail.append(f"{y}: short answers total {sum(i['m'] for i in sa)} marks, expected 15")
        if len(pb) != 1:
            fail.append(f"{y}: {len(pb)} Crime extended responses, expected 1")
        if len(s3) != 4:
            fail.append(f"{y}: {len(s3)} option alternatives, expected 4 (Family a/b, Shelter a/b)")

    for k in crit:
        y, s, l = k.split("|")
        if not any(i["y"] == int(y) and i["s"] == s and i["l"] == l for i in items):
            fail.append(f"marking material {k} matches no question")

    non_mc = [i for i in items if i["s"] != "I"]
    have = [i for i in non_mc if f"{i['y']}|{i['s']}|{i['l']}" in crit]
    missing_years = sorted({i["y"] for i in non_mc if i not in have})

    print(f"index.html {size:,} bytes · {len(items)} questions · {len(crit)} with marking material")
    print(f"  sections: " + ", ".join(
        f"{s} {sum(1 for i in items if i['s'] == s)}" for s in ("I", "II-A", "II-B", "III")))
    print(f"  topics:   " + ", ".join(
        f"{t} {sum(1 for i in items if i['topic'] == t)}" for t in ("crime", "humanrights", "family", "shelter")))
    print(f"  criteria: {len(have)}/{len(non_mc)} written questions"
          + (f" — none for {', '.join(map(str, missing_years))}" if missing_years else ""))
    n_sample = sum(1 for i in non_mc
                   if (crit.get("{}|{}|{}".format(i["y"], i["s"], i["l"])) or {}).get("sample"))
    print(f"  sample answers: {n_sample}")
    print()
    if fail:
        print("FAILED:")
        for f in fail:
            print("  " + f)
        sys.exit(1)
    print("all checks passed")

if __name__ == "__main__":
    main()
