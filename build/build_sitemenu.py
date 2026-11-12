#!/usr/bin/env python3
"""Put the same "All tools" drop-down menu on every sub-site.

    python3 build/build_sitemenu.py           # write the menu into every page and template
    python3 build/build_sitemenu.py --check   # change nothing; fail if any page is out of date

One list, SITES below, feeds every menu. To add, rename or reorder a sub-site, edit SITES
(and PAGES if it is a new page), then run this script.

The menu is written between the SITEMENU:START and SITEMENU:END markers. Templates and the
pages built from them both carry it, so a rebuild of the Question Finder, Evidence Finder,
Topic Map or Crime Glossary keeps the menu without running this again.
"""
import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHECK = "--check" in sys.argv
HOME = "https://sites.google.com/education.nsw.gov.au/hsc-legal-studies-at-sscbwb/home"

# group, key, label, one-line description, path from the repo root, icon (24 x 24 stroke paths)
SITES = [
    ("Finders", "qf", "Question Finder", "Every HSC question, 2011 to 2025", "index.html",
     '<path d="M7 3h7l4 4v14H7z"/><path d="M14 3v4h4M9.5 12h6M9.5 16h6"/>'),
    ("Finders", "ef", "Evidence Finder", "Legislation, cases, media and reports", "evidence.html",
     '<path d="M3 12V4h8l10 10-8 8z"/><circle cx="7.5" cy="8.5" r="1.3"/>'),
    ("Crime tools", "court", "Court Process Explorer", "From arrest to appeal, with real cases", "court-process/",
     '<path d="M12 4v16M7.5 20h9M5 7h14M5 7l-3 7a3 3 0 006 0zM19 7l-3 7a3 3 0 006 0z"/>'),
    ("Crime tools", "sent", "Sentencing Simulator", "You be the judge in six real cases", "sentencing/",
     '<path d="M12.5 4.5l6 6M9.5 7.5l6 6M11 9l-7.5 7.5 2 2L13 11M13 20.5h8"/>'),
    ("Crime tools", "essay", "Extended Response Builder", "Plan a 15-mark Crime response", "essay-builder/",
     '<path d="M4 20l1-4L16 5l3 3L8 19zM14 7l3 3"/>'),
    ("Crime tools", "yo", "Young Offenders Pathway", "How the law deals with young people", "young-offenders/",
     '<circle cx="12" cy="6.5" r="3"/><path d="M12 9.5v6M8 12h8M12 15.5l-3 5M12 15.5l3 5"/>'),
    ("Reference", "gloss", "Crime Glossary", "Key terms, flashcards and a quiz", "glossary/",
     '<path d="M4 5c3-1 6-1 8 1 2-2 5-2 8-1v13c-3-1-6-1-8 1-2-2-5-2-8-1zM12 6v13"/>'),
    ("Reference", "map", "Topic Map", "See how the course fits together", "mind-map/",
     '<circle cx="6" cy="18" r="2.5"/><circle cx="18" cy="6" r="2.5"/><path d="M8.5 18H15a3 3 0 000-6H9a3 3 0 010-6h6.5"/>'),
]

# key -> files that carry the menu, the path back to the repo root, where the button sits,
# and (for the Crime tools) the part of the glossary to open.
PAGES = {
    "qf":    dict(files=["build/template.html", "index.html"], up="", place="pill"),
    "ef":    dict(files=["build/evidence_template.html", "evidence.html"], up="", place="pill"),
    "map":   dict(files=["mind-map/template.html", "mind-map/index.html"], up="../", place="row"),
    "gloss": dict(files=["glossary/template.html", "glossary/index.html"], up="../", place="hub"),
    "court": dict(files=["court-process/index.html"], up="../", place="corner", gloss="#t=3"),
    "sent":  dict(files=["sentencing/index.html"], up="../", place="corner", gloss="#t=4"),
    "essay": dict(files=["essay-builder/index.html"], up="../", place="corner"),
    "yo":    dict(files=["young-offenders/index.html"], up="../", place="corner", gloss="#t=5"),
}

# Where the menu goes the first time a page is patched. After that the markers are used.
FIRST = {
    "qf":    r'[ \t]*<a class="pill" href="evidence\.html">.*?</a>\n[ \t]*<a class="pill" href="mind-map/">.*?</a>\n[ \t]*<a class="pill" href="glossary/">.*?</a>\n',
    "ef":    r'[ \t]*<a class="pill" href="index\.html">.*?</a>\n[ \t]*<a class="pill" href="mind-map/">.*?</a>\n[ \t]*<a class="pill" href="glossary/">.*?</a>\n',
    "gloss": r'[ \t]*<nav class="hub"[^>]*>.*?</nav>\n',
    "tool":  r'[ \t]*<a class="gl-link" href="[^"]*">.*?</a>\n',
}
MM_AFTER = re.compile(r'(<button class="btn" id="btnTheme"[^\n]*</button>\n)')
MARKED = re.compile(r"[ \t]*<!-- SITEMENU:START.*?<!-- SITEMENU:END -->\n", re.S)

CSS = """
.sm{position:relative;display:inline-block;font-size:13px;line-height:1.3;text-align:left}
.sm svg{width:1.15em;height:1.15em;fill:none;stroke:currentColor;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;flex:none}
.sm-btn{list-style:none;cursor:pointer;display:inline-flex;gap:7px;align-items:center;background:#ffd24a;color:#1a1d2b;border-radius:999px;padding:6px 13px;font-weight:700;white-space:nowrap;user-select:none;-webkit-user-select:none}
.sm-btn::-webkit-details-marker{display:none}
.sm-btn:hover{background:#ffe07a}
.sm-btn:focus-visible{outline:3px solid #fff;outline-offset:2px}
.sm[open] .sm-caret{transform:rotate(180deg)}
.sm-list{position:fixed;top:0;left:0;z-index:1000;width:min(340px,calc(100vw - 16px));max-height:calc(100vh - 90px);overflow:auto;background:#fff;color:#1a1d2b;border:1px solid #dcdfea;border-radius:14px;box-shadow:0 12px 34px rgba(10,14,40,.3);padding:8px;display:flex;flex-direction:column;gap:1px;font-weight:400}
.sm-h{font-size:11px;font-weight:800;text-transform:uppercase;letter-spacing:.5px;color:#5a6072;padding:8px 10px 3px}
.sm-a{display:grid;grid-template-columns:22px 1fr;gap:10px;align-items:center;padding:7px 10px;border-radius:9px;color:inherit;text-decoration:none}
.sm-a svg{font-size:18px;color:#3730a3}
.sm-a b{display:block;font-size:14px;font-weight:700;color:inherit}
.sm-a em{display:block;font-style:normal;font-size:12px;color:#5a6072}
a.sm-a:hover,a.sm-a:focus-visible{background:#eceeff;outline:none}
.sm-cur{background:#fff3c9}
.sm-cur em{color:#7d5f00;font-weight:700}
.sm-ext{border-top:1px solid #dcdfea;margin-top:6px;padding-top:10px;border-radius:0 0 9px 9px}
:root[data-theme="dark"] .sm-list{background:#1a1d2c;color:#eceefa;border-color:#313654}
:root[data-theme="dark"] .sm-h,:root[data-theme="dark"] .sm-a em{color:#aab0c8}
:root[data-theme="dark"] .sm-a svg{color:#9b9cf7}
:root[data-theme="dark"] a.sm-a:hover,:root[data-theme="dark"] a.sm-a:focus-visible{background:#24264a}
:root[data-theme="dark"] .sm-cur{background:#3a3010}
:root[data-theme="dark"] .sm-cur em{color:#e6bd45}
:root[data-theme="dark"] .sm-ext{border-color:#313654}
@media (prefers-color-scheme:dark){
:root:not([data-theme="light"]) .sm-list{background:#1a1d2c;color:#eceefa;border-color:#313654}
:root:not([data-theme="light"]) .sm-h,:root:not([data-theme="light"]) .sm-a em{color:#aab0c8}
:root:not([data-theme="light"]) .sm-a svg{color:#9b9cf7}
:root:not([data-theme="light"]) a.sm-a:hover,:root:not([data-theme="light"]) a.sm-a:focus-visible{background:#24264a}
:root:not([data-theme="light"]) .sm-cur{background:#3a3010}
:root:not([data-theme="light"]) .sm-cur em{color:#e6bd45}
:root:not([data-theme="light"]) .sm-ext{border-color:#313654}
}
.sm--corner{position:absolute;top:14px;right:20px}
.sm--row{margin-left:auto}
.sm--hub{margin-bottom:14px}
@media (max-width:900px){.sm--corner{position:static;margin-bottom:10px}}
@media print{.sm{display:none !important}}
""".strip()

# The list is position:fixed and placed under the button by script, so a masthead with
# overflow:hidden (the two finders) cannot clip it. It closes on Escape, an outside click,
# a page scroll or a resize.
JS = ("(function(){var d=document.getElementById('sitemenu');if(!d)return;var s=d.querySelector('summary'),l=d.querySelector('.sm-list');"
      "function place(){var b=s.getBoundingClientRect(),w=l.offsetWidth,x=Math.min(Math.max(8,b.right-w),window.innerWidth-w-8),y=b.bottom+8;"
      "l.style.left=x+'px';l.style.top=y+'px';l.style.maxHeight=Math.max(160,window.innerHeight-y-12)+'px'}"
      "function shut(){if(d.open)d.open=false}"
      "d.addEventListener('toggle',function(){if(d.open)place()});"
      "document.addEventListener('click',function(e){if(d.open&&!d.contains(e.target))shut()});"
      "document.addEventListener('keydown',function(e){if(e.key==='Escape'&&d.open){shut();s.focus()}});"
      "window.addEventListener('scroll',shut,{passive:true});window.addEventListener('resize',shut)})();")


def svg(paths, cls=""):
    return f'<svg{" class=" + chr(34) + cls + chr(34) if cls else ""} viewBox="0 0 24 24" aria-hidden="true">{paths}</svg>'


def menu(key):
    pg = PAGES[key]
    rows, group = [], None
    for g, k, label, desc, path, icon in SITES:
        if g != group:
            rows.append(f'  <span class="sm-h">{g}</span>')
            group = g
        if k == key:
            rows.append(f'  <span class="sm-a sm-cur" aria-current="page">{svg(icon)}<span><b>{label}</b><em>You are here</em></span></span>')
        else:
            href = pg["up"] + path + (pg.get("gloss", "") if k == "gloss" else "")
            rows.append(f'  <a class="sm-a" href="{href}">{svg(icon)}<span><b>{label}</b><em>{desc}</em></span></a>')
    rows.append(f'  <a class="sm-a sm-ext" href="{HOME}">{svg(chr(60) + "path d=" + chr(34) + "M3 11l9-7 9 7M5 10v10h14V10M10 20v-6h4v6" + chr(34) + "/>")}'
                '<span><b>HSC Legal Studies website</b><em>Back to the main class site</em></span></a>')
    grid = '<path d="M4 4h6v6H4zM14 4h6v6h-6zM4 14h6v6H4zM14 14h6v6h-6z"/>'
    return ("<!-- SITEMENU:START built by build/build_sitemenu.py; edit the list of sites there, not here -->\n"
            f"<style>\n{CSS}\n</style>\n"
            f'<details class="sm sm--{pg["place"]}" id="sitemenu"><summary class="sm-btn" aria-label="All tools: open the list of HSC Legal Studies sites">'
            f'{svg(grid)}All tools{svg(chr(60) + "path d=" + chr(34) + "M6 9l6 6 6-6" + chr(34) + "/>", "sm-caret")}</summary>\n'
            '<div class="sm-list">\n' + "\n".join(rows) + "\n</div></details>\n"
            f"<script>{JS}</script>\n"
            "<!-- SITEMENU:END -->\n")


def patch(key, path):
    src = path.read_text(encoding="utf-8")
    block = menu(key)
    if MARKED.search(src):
        return src, MARKED.sub(lambda m: block, src, count=1)
    if PAGES[key]["place"] == "row":            # Topic Map: after the last button in the toolbar
        assert len(MM_AFTER.findall(src)) == 1, f"{path}: cannot find the toolbar"
        return src, MM_AFTER.sub(lambda m: m.group(1) + block, src, count=1)
    first = re.compile(FIRST["tool" if PAGES[key]["place"] == "corner" else key], re.S)
    assert len(first.findall(src)) == 1, f"{path}: cannot find where the old links were"
    return src, first.sub(lambda m: block, src, count=1)


def main():
    stale = []
    for key, pg in PAGES.items():
        for f in pg["files"]:
            p = ROOT / f
            old, new = patch(key, p)
            assert new.count("SITEMENU:START") == 1 and new.count('id="sitemenu"') == 1, f
            if old != new:
                stale.append(f)
                if not CHECK:
                    p.write_text(new, encoding="utf-8")
    print(f"site menu: {len(SITES)} sites plus the class website, on {sum(len(p['files']) for p in PAGES.values())} files")
    if CHECK:
        if stale:
            print("OUT OF DATE: " + ", ".join(stale) + ". Run python3 build/build_sitemenu.py"); sys.exit(1)
        print("up to date"); return
    print("wrote: " + (", ".join(stale) if stale else "nothing, already up to date"))


if __name__ == "__main__":
    main()
