#!/usr/bin/env python3
"""Build the Crime glossary site and keep the other sites' definitions in step with it.

    python3 build/build_glossary.py           # write glossary/index.html and sync court-process/
    python3 build/build_glossary.py --check   # change nothing; fail if anything is out of date

One list, data/glossary.json, feeds everything:
  * glossary/index.html  = glossary/template.html with the data dropped in at /*DATA*/
  * court-process/index.html: the hover glossary (const G) between the GLOSSARY:START and
    GLOSSARY:END markers is rewritten from the "hover" block, so a meaning edited in
    glossary.json changes in both places.
Syllabus labels come from data/syllabus.json, so a point renamed there is renamed here.
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHECK = "--check" in sys.argv


def load():
    g = json.loads((ROOT / "data/glossary.json").read_text(encoding="utf-8"))
    crime = json.loads((ROOT / "data/syllabus.json").read_text(encoding="utf-8"))["topics"]["crime"]
    points = {"crime": {"label": "Crime", "kind": "section"}}
    for th in crime["themes"]:
        points[th["id"]] = {"label": th["full"], "kind": "theme"}
    for sec in crime["sections"]:
        points[sec["id"]] = {"label": sec["label"] + " (whole topic)", "kind": "section"}
        for p in sec["points"]:
            points[p["id"]] = {"label": p["label"], "kind": "point"}
    return g, points


def validate(g, points):
    errs, ids = [], set()
    secs = {(t["n"], s["n"]) for t in g["topics"] for s in t["sections"]}
    for t in g["terms"]:
        if t["id"] in ids:
            errs.append(f"duplicate id {t['id']}")
        ids.add(t["id"])
        if not t["senses"]:
            errs.append(f"{t['term']}: no meaning")
        for s in t["senses"]:
            if not s["d"].strip() or not s["refs"]:
                errs.append(f"{t['term']}: a meaning is empty or has no section")
            for r in s["refs"]:
                if (r["t"], r["s"]) not in secs:
                    errs.append(f"{t['term']}: no section Crime {r['t']}.{r['s']}")
                for p in r["points"]:
                    if p not in points:
                        errs.append(f"{t['term']}: {p} is not in data/syllabus.json")
    by = {t["id"]: t for t in g["terms"]}
    for site, keys in g["hover"].items():
        for k, v in keys.items():
            if "term" in v and (v["term"] not in by or v.get("sense", 1) > len(by[v["term"]]["senses"])):
                errs.append(f"hover/{site}/{k}: points at a term or meaning that does not exist")
    for tool in g["tools"]:
        for sid in tool["sections"]:
            if tuple(int(x) for x in sid.split(".")) not in secs:
                errs.append(f"tools/{tool['id']}: no section {sid}")
    return errs


def page(g, points):
    used = {p for t in g["terms"] for s in t["senses"] for r in s["refs"] for p in r["points"]}
    data = {
        "meta": {k: g["meta"][k] for k in ("title", "version", "date")},
        "topics": [{"n": t["n"], "label": t["label"], "icon": t["icon"],
                    "sections": [{"n": s["n"], "name": s["name"]} for s in t["sections"]]} for t in g["topics"]],
        "points": {p: points[p] for p in sorted(used)},
        "tools": g["tools"],
        "terms": g["terms"],
    }
    tpl = (ROOT / "glossary/template.html").read_text(encoding="utf-8")
    assert tpl.count("/*DATA*/") == 1
    blob = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return tpl.replace("/*DATA*/", "/* Built by build/build_glossary.py from data/glossary.json. Edit those, not this file. */\nconst DATA = " + blob + ";")


def hover_js(g, site):
    by = {t["id"]: t for t in g["terms"]}
    lines = []
    for k, v in g["hover"][site].items():
        d = v["d"] if "d" in v else v.get("before", "") + by[v["term"]]["senses"][v.get("sense", 1) - 1]["d"]
        lines.append(" " + json.dumps(k, ensure_ascii=False) + ": " + json.dumps(d, ensure_ascii=False) + ",")
    return ("/* GLOSSARY:START built by build/build_glossary.py from data/glossary.json; edit meanings there */\n"
            "const G = {\n" + "\n".join(lines) + "\n};\n/* GLOSSARY:END */")


def sync_hover(g, site, path):
    src = path.read_text(encoding="utf-8")
    js = hover_js(g, site)
    marked = re.compile(r"/\* GLOSSARY:START.*?/\* GLOSSARY:END \*/", re.S)
    if marked.search(src):
        new = marked.sub(lambda m: js, src, count=1)
    else:  # first run: replace the hand-written object
        a = src.index("const G = {")
        new = src[:a] + js + src[src.index("};", a) + 2:]
    used = set(re.findall(r"\[\[([^\]|\[',]+)(?:\|[^\]]+)?\]\]", new))
    missing = sorted(u for u in used if u not in g["hover"][site])
    return src, new, missing


def main():
    g, points = load()
    errs = validate(g, points)
    out = ROOT / "glossary/index.html"
    html = page(g, points)
    cp = ROOT / "court-process/index.html"
    old, new, missing = sync_hover(g, "court-process", cp)
    errs += [f"court-process uses [[{m}]] but hover/court-process has no such key" for m in missing]
    if errs:
        print("\n".join("ERROR " + e for e in errs)); sys.exit(1)
    stale = []
    if not out.exists() or out.read_text(encoding="utf-8") != html:
        stale.append("glossary/index.html")
    if old != new:
        stale.append("court-process/index.html")
    n = len(g["terms"]); m = sum(len(t["senses"]) for t in g["terms"])
    linked = sum(1 for v in g["hover"]["court-process"].values() if "term" in v)
    print(f"{n} terms, {m} meanings; court-process hover glossary: {len(g['hover']['court-process'])} keys, {linked} from the shared list")
    if CHECK:
        if stale:
            print("OUT OF DATE: " + ", ".join(stale) + ". Run python3 build/build_glossary.py"); sys.exit(1)
        print("up to date"); return
    if "glossary/index.html" in stale:
        out.write_text(html, encoding="utf-8")
    if "court-process/index.html" in stale:
        cp.write_text(new, encoding="utf-8")
    print("wrote: " + (", ".join(stale) if stale else "nothing, already up to date"))


if __name__ == "__main__":
    main()
