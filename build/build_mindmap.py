#!/usr/bin/env python3
"""Build the syllabus mind map: mind-map/index.html (+ mind-map/links-review.html).

Inputs   data/syllabus.json                  the dot points (stable ids shared with both finders)
         data/items-papers-tagged.json       past questions, Section I and II-A
         data/items-extended.json            extended responses (II-B, III)
         evidence/**/*.md                    evidence records (read through evidence_lib)
         data/drive-links.json               library path -> Google Drive id
         mind-map/src/links-year11.txt       authored links, Year 11   (teacher reviews)
         mind-map/src/links-year12.txt       authored links, Year 12   (teacher reviews)
         mind-map/src/pathways.json          guided pathways
         mind-map/src/themes.py              cross-topic themes and each dot point's primary theme
         mind-map/template.html              the page, __DATA__ substituted

Every check is an invariant: unknown ids, self-links, duplicate links and unmapped themes
stop the build. Run:  python3 build/build_mindmap.py
"""
import collections
import html
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "mind-map", "src"))
import evidence_lib as L  # noqa: E402
import themes as TH  # noqa: E402

SRC = os.path.join(ROOT, "mind-map", "src")
OUT = os.path.join(ROOT, "mind-map")
YEARS = list(range(2011, 2026))
SLOT = {"investigating": 5, "disputes": 5, "changing": 5, "experiences": 5,
        "crime": 1, "humanrights": 2, "family": 3, "shelter": 4}
ICON = {"investigating": "g-book", "disputes": "g-gavel", "changing": "g-route", "experiences": "g-group",
        "crime": "g-scales", "humanrights": "g-globe", "family": "g-family", "shelter": "g-shelter"}
BAND = {1: "describe", 2: "explain", 3: "analyse", 4: "evaluate",
        "describe": "describe", "explain": "explain", "analyse": "analyse", "evaluate": "evaluate"}
DIR2BAND = {}
SYL = json.load(open(os.path.join(ROOT, "data", "syllabus.json"), encoding="utf-8"))
for k, v in SYL["directives"].items():
    for verb in v["verbs"]:
        DIR2BAND[verb] = k
    DIR2BAND[k] = k
BAND_RANK = {"describe": 1, "explain": 2, "analyse": 3, "evaluate": 4}


def short_label(pid, label):
    if pid in TH.SHORT:
        return TH.SHORT[pid]
    s = re.split(r"\s+[—–]\s+", label)[0].strip()
    if len(s) > 88:
        cut = s[:88]
        s = cut[:cut.rfind(" ")].rstrip(",;:") + "…"
    return s


def build_topics():
    topics, nodes, sec_of = [], {}, {}
    for tk, t in SYL["topics"].items():
        course = t.get("course", "hsc")
        topic = {"k": tk, "label": t["label"], "part": t["part"], "course": "y11" if course == "preliminary" else "y12",
                 "slot": SLOT[tk], "icon": ICON[tk], "weight": t["weight"], "focus": t["principalFocus"],
                 "groups": []}
        for sec in t["sections"]:
            groups = collections.OrderedDict()
            for p in sec["points"]:
                gid = sec["id"]
                glabel = sec["label"]
                if sec["id"] == "hr.2":
                    gid = "hr.2." + p.get("scope", "x")
                    glabel = "Promoting and enforcing: " + ("international" if p.get("scope") == "international" else "in Australia")
                groups.setdefault(gid, {"id": gid, "section": sec["id"], "label": glabel, "nodes": []})
                groups[gid]["nodes"].append(p["id"])
                theme = TH.PER_POINT.get(p["id"], TH.SECTION_DEFAULT.get(sec["id"]))
                nodes[p["id"]] = {"l": p["label"], "s": short_label(p["id"], p["label"]), "d": p.get("detail", ""),
                                  "t": tk, "g": gid, "sec": sec["id"], "th": theme}
                sec_of[p["id"]] = sec["id"]
            topic["groups"].extend(groups.values())
        topics.append(topic)
    return topics, nodes, sec_of


def question_stats(nodes):
    items = json.load(open(os.path.join(ROOT, "data", "items-papers-tagged.json"), encoding="utf-8"))
    items += json.load(open(os.path.join(ROOT, "data", "items-extended.json"), encoding="utf-8"))
    for pid, n in nodes.items():
        sec = n["sec"]
        yl = {y: 0 for y in YEARS}
        c = ci = s = si = mc = 0
        bands = collections.Counter()
        verbs = collections.Counter()
        last = 0
        for it in items:
            core, sup = set(it["core"]), set(it["support"])
            lvl = 0
            if pid in core:
                lvl, direct = 3, True
                c += 1
            elif sec in core:
                lvl, direct = 2, False
                ci += 1
            elif pid in sup:
                lvl = 1
                s += 1
            elif sec in sup:
                lvl = 1
                si += 1
            if not lvl:
                continue
            y = it["y"]
            yl[y] = max(yl[y], lvl)
            if lvl >= 2:
                last = max(last, y)
                if it["s"] == "I":
                    mc += 1
                else:
                    b = BAND.get(it.get("band")) or DIR2BAND.get(it.get("dir"))
                    if b:
                        bands[b] += 1
                    if it.get("dir"):
                        verbs[it["dir"]] += 1
        n["q"] = {"c": c, "ci": ci, "s": s, "si": si, "last": last, "yrs": "".join(str(yl[y]) for y in YEARS),
                  "mc": mc, "bands": {k: bands[k] for k in BAND_RANK if bands[k]}, "verbs": dict(verbs.most_common(5))}
        top = max(bands, key=lambda b: BAND_RANK[b]) if bands else None
        n["q"]["top"] = top


def attach_evidence(nodes):
    recs, problems = L.load_records()
    if problems:
        print("record problems:", *problems[:5], sep="\n  ")
    drive = json.load(open(os.path.join(ROOT, "data", "drive-links.json"), encoding="utf-8"))["files"]
    for n in nodes.values():
        n["ev"] = []
    section_level = 0
    mapped = total_doc = 0
    for r in recs:
        doc = r.get("document") or ""
        url = ""
        if doc:
            total_doc += 1
            if doc in drive:
                url = "https://drive.google.com/file/d/%s/view" % drive[doc]
                mapped += 1
        entry = {"id": r["id"], "t": r["type"], "n": r.get("short") or r["title"], "u": url}
        hit = False
        for tag in r.get("core", []):
            if tag in nodes:
                nodes[tag]["ev"].append(entry)
                hit = True
        if not hit:
            section_level += 1
    order = {"case": 0, "legislation": 1, "international": 2, "report": 3, "media": 4, "document": 5}
    for n in nodes.values():
        n["ev"].sort(key=lambda e: (order.get(e["t"], 9), e["n"].lower()))
    print("evidence: %d records, %d with no dot-point core tag, %d/%d documents on Drive"
          % (len(recs), section_level, mapped, total_doc))


Y11 = ("investigating", "disputes", "changing", "experiences")


def is_y11(tk):
    return tk in Y11


def parse_links(nodes):
    edges, seen, problems = [], set(), []
    for fn in ("links-year11.txt", "links-year12.txt"):
        for ln, line in enumerate(open(os.path.join(SRC, fn), encoding="utf-8"), 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            m = re.match(r"^([bstl])\s+([mw])\s+(\S+)\s+(\S+)\s*\|\s*(.+)$", line)
            if not m:
                problems.append("%s:%d unparseable: %s" % (fn, ln, line[:60]))
                continue
            ty, st, a, b, why = m.groups()
            for x in (a, b):
                if x not in nodes:
                    problems.append("%s:%d unknown id %s" % (fn, ln, x))
            if a == b:
                problems.append("%s:%d self-link %s" % (fn, ln, a))
            if a not in nodes or b not in nodes or a == b:
                continue
            key = (ty, a, b) if ty == "b" else (ty,) + tuple(sorted((a, b)))
            if key in seen:
                continue
            seen.add(key)
            lv = 1 if (st == "m" and ty != "s") else 2 if st == "m" else 3
            edges.append({"a": a, "b": b, "ty": ty, "st": st, "lv": lv, "why": why.strip(),
                          "br": 1 if is_y11(nodes[a]["t"]) != is_y11(nodes[b]["t"]) else 0})
    if problems:
        print("LINK PROBLEMS:", *problems, sep="\n  ")
        sys.exit(1)
    return edges


NEEDED_ICONS = ["g-scales", "g-globe", "g-family", "g-shelter", "g-gavel", "g-book", "g-route", "g-group", "g-check",
                "g-search", "g-print", "g-help", "g-close", "g-layers", "g-target", "g-clock"]


def sprite():
    raw = open(os.path.join(HERE, "icons-fa.svg.txt"), encoding="utf-8").read()
    out = []
    for sid in NEEDED_ICONS:
        m = re.search(r'<symbol id="%s".*?</symbol>' % re.escape(sid), raw, re.S)
        if not m:
            sys.exit("icon missing from sprite: " + sid)
        out.append(m.group(0))
    return "".join(out)


def main():
    topics, nodes, _ = build_topics()
    question_stats(nodes)
    attach_evidence(nodes)
    edges = parse_links(nodes)
    pathways = json.load(open(os.path.join(SRC, "pathways.json"), encoding="utf-8"))
    for p in pathways:
        for i in p["ids"]:
            if i not in nodes:
                sys.exit("pathway %r: unknown id %s" % (p["title"], i))
        tk = {nodes[i]["t"] for i in p["ids"]}
        crs = {"y11" if nodes[i]["t"] in ("investigating", "disputes", "changing", "experiences") else "y12" for i in p["ids"]}
        p["course"] = "both" if len(crs) > 1 else crs.pop()
    themes = [{k: v for k, v in t.items()} for t in TH.THEMES]
    tk = {t["k"] for t in themes}
    bad = [i for i, n in nodes.items() if n["th"] not in tk]
    if bad:
        sys.exit("dot points with no theme: %s" % bad)

    linked = collections.Counter()
    for e in edges:
        linked[e["a"]] += 1
        linked[e["b"]] += 1
    orphans = [i for i in nodes if not linked[i]]
    print("nodes %d | links %d %s | bridges %d | orphans %d"
          % (len(nodes), len(edges), dict(collections.Counter(e["ty"] for e in edges)),
             sum(e["br"] for e in edges), len(orphans)))
    if orphans:
        print("  no links:", ", ".join(orphans))

    data = {"meta": {"years": [YEARS[0], YEARS[-1]], "qf": "../index.html#tags=", "ev": "../evidence.html#ev-",
                     "draft": os.environ.get("DRAFT", "0") == "1", "built": SYL["meta"].get("syllabus", ""),
                     "overdueBefore": 2019},
            "topics": topics, "nodes": nodes, "edges": edges, "pathways": pathways, "themes": themes,
            "directives": SYL["directives"], "bands": SYL["demandBands"]}
    blob = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    tpl = open(os.path.join(OUT, "template.html"), encoding="utf-8").read()
    open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(
        tpl.replace("__ICONS__", sprite()).replace("__DATA__", blob))
    print("wrote mind-map/index.html  (%.0f KB)" % (len(blob) / 1024))
    write_review(nodes, edges)


def write_review(nodes, edges):
    names = {"b": "Builds on / leads to", "s": "Same concept elsewhere", "t": "Tension or conflict", "l": "Legal v non-legal"}
    tlabel = lambda i: SYL["topics"][nodes[i]["t"]]["label"]
    rows = []
    for n, e in enumerate(edges, 1):
        arrow = "→" if e["ty"] == "b" else "↔"
        rows.append(
            '<tr data-ty="%s" data-t="%s"><td>%d</td><td><span class="ty %s">%s</span>%s</td>'
            '<td><b>%s</b> %s<br><small>%s</small></td><td class="ar">%s</td>'
            '<td><b>%s</b> %s<br><small>%s</small></td><td>%s</td>'
            '<td><select><option value="">OK</option><option>Change</option><option>Remove</option></select>'
            '<input placeholder="note"></td></tr>'
            % (e["ty"], html.escape(nodes[e["a"]]["t"] + " " + nodes[e["b"]]["t"]), n, e["ty"], names[e["ty"]],
               "" if e["st"] == "m" else " <i>(weaker)</i>",
               e["a"], html.escape(nodes[e["a"]]["s"]), html.escape(tlabel(e["a"])), arrow,
               e["b"], html.escape(nodes[e["b"]]["s"]), html.escape(tlabel(e["b"])), html.escape(e["why"])))
    page = REVIEW.replace("__ROWS__", "\n".join(rows)).replace("__N__", str(len(edges)))
    open(os.path.join(OUT, "links-review.html"), "w", encoding="utf-8").write(page)
    print("wrote mind-map/links-review.html")


REVIEW = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Mind map: links to review</title>
<style>
body{font:14px/1.45 system-ui,Segoe UI,Roboto,sans-serif;margin:0;color:#14161a;background:#f6f7f9}
header{position:sticky;top:0;background:#fff;border-bottom:1px solid #dde1e7;padding:12px 18px;z-index:5;display:flex;flex-wrap:wrap;gap:10px 18px;align-items:center}
h1{font-size:19px;margin:0}
.bar{display:flex;flex-wrap:wrap;gap:8px;align-items:center}
button,select,input{font:inherit}
button{padding:6px 12px;border:1px solid #9aa3b2;border-radius:8px;background:#fff;cursor:pointer}
button.on{background:#14233a;color:#fff;border-color:#14233a}
table{border-collapse:collapse;width:100%;background:#fff}
th,td{padding:7px 9px;border-bottom:1px solid #e6e9ee;text-align:left;vertical-align:top}
th{position:sticky;top:58px;background:#eef1f5;font-size:12px;text-transform:uppercase;letter-spacing:.04em}
td.ar{font-size:18px;color:#6b717c}
small{color:#6b717c}
.ty{display:inline-block;font-size:12px;font-weight:700;padding:1px 8px;border-radius:99px;margin-right:6px;color:#fff}
.ty.b{background:#1f3864}.ty.s{background:#0f766e}.ty.t{background:#b91c1c}.ty.l{background:#b45309}
tr.chg td{background:#fff7e0}tr.rem td{background:#fde8e8}
input[placeholder]{width:150px;margin-left:6px;padding:3px 6px;border:1px solid #ccd2dc;border-radius:6px}
textarea{width:100%;height:160px;margin:10px 18px;max-width:900px}
.wrap{padding:0 18px 40px}
</style></head><body>
<header><h1>Mind map: __N__ links to review</h1>
<div class="bar"><span>Show:</span>
<button data-f="" class="on">All</button><button data-f="b">Builds on</button><button data-f="s">Same concept</button><button data-f="t">Tension</button><button data-f="l">Legal v non-legal</button>
<span style="width:14px"></span><button id="exp">Copy my changes</button><span id="cnt"></span></div></header>
<div class="wrap"><p>For each link choose <b>OK</b>, <b>Change</b> or <b>Remove</b>, add a note if useful, then press <b>Copy my changes</b> and paste the result back to Claude. Your choices are kept in this browser.</p>
<table><thead><tr><th>#</th><th>Kind</th><th>From</th><th></th><th>To</th><th>Reason shown to students</th><th>Your call</th></tr></thead><tbody id="tb">
__ROWS__
</tbody></table>
<textarea id="out" placeholder="Your changes appear here after you press Copy my changes" hidden></textarea></div>
<script>
const rows=[...document.querySelectorAll('#tb tr')], KEY='hsc-ls-map-review';
let saved={};try{saved=JSON.parse(localStorage.getItem(KEY)||'{}')}catch(e){}
rows.forEach((r,i)=>{const s=r.querySelector('select'),n=r.querySelector('input');const v=saved[i];if(v){s.value=v[0];n.value=v[1]||'';}
 const upd=()=>{r.className=s.value=='Change'?'chg':s.value=='Remove'?'rem':'';saved[i]=[s.value,n.value];try{localStorage.setItem(KEY,JSON.stringify(saved))}catch(e){};count();};
 s.onchange=n.oninput=upd;r.className=s.value=='Change'?'chg':s.value=='Remove'?'rem':'';});
function count(){const c=rows.filter(r=>r.querySelector('select').value).length;document.getElementById('cnt').textContent=c?c+' marked':'';}count();
document.querySelectorAll('[data-f]').forEach(b=>b.onclick=()=>{document.querySelectorAll('[data-f]').forEach(x=>x.classList.toggle('on',x===b));
 rows.forEach(r=>r.hidden=b.dataset.f&&r.dataset.ty!==b.dataset.f);});
document.getElementById('exp').onclick=()=>{const out=document.getElementById('out');
 const lines=rows.filter(r=>r.querySelector('select').value).map(r=>{const c=r.cells;return r.querySelector('select').value.toUpperCase()+' #'+c[0].textContent+' ['+c[1].textContent.trim()+'] '+c[2].querySelector('b').textContent+' -> '+c[4].querySelector('b').textContent+(r.querySelector('input').value?' : '+r.querySelector('input').value:'')});
 out.hidden=false;out.value=lines.length?lines.join('\\n'):'No changes marked: all links OK.';out.select();try{navigator.clipboard.writeText(out.value)}catch(e){}};
</script></body></html>"""

if __name__ == "__main__":
    main()
