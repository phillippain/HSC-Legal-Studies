"""Read the Worksheet Maker's question bank (worksheet-maker/bank/*.txt) and write the review page.

The bank is plain text so it can be edited in any text editor. bank/README.md has the full format;
in short, every question starts with a line `=== <type> <id>`, then `key: value` lines, then the body:

    === mc mc-crime2-01
    c: crime.2.5
    lv: 2
    Q: Under the Bail Act 2013 (NSW), who must show cause why their detention is not justified?
    A: The prosecution, for every offence
    B: An accused charged with a show cause offence
    C: The magistrate
    D: The victim
    ANS: B
    WHY: For show cause offences the accused bears the onus; the unacceptable risk test then applies.
"""
import hashlib
import html
import json
import re
from pathlib import Path

FORMATS = {"mc", "sa", "scen", "stim", "er", "teeacl", "tf", "terms", "order", "sort", "compare", "error", "chain"}
DEFAULT_M = {"mc": 1, "sa": 4, "scen": 6, "er": 15, "teeacl": 8, "sort": 4, "compare": 6, "error": 4, "chain": 4}
DEFAULT_K = {"mc": ["recall"], "sa": ["explain"], "scen": ["scenario"], "stim": ["stimulus"], "er": ["evaluate"], "teeacl": ["evaluate", "evidence"],
             "sort": ["compare"], "compare": ["compare"], "error": ["evaluate"], "tf": ["recall"], "terms": ["recall"], "chain": ["explain"], "order": ["describe"]}
KEYS = ("Q", "A", "B", "C", "D", "ANS", "WHY", "LEAD", "TABLE", "PTS", "PLAN", "CATS", "COLS", "TEXT", "DIA", "TITLE", "TRIGGER", "WORDS", "NOTE", "BY")
KEY_RE = re.compile(r"^(" + "|".join(KEYS) + r"):\s?(.*)$")
PART_RE = re.compile(r"^PART\s+(\([a-z]+\)(?:\([ivx]+\))?)\s+(\d+)\s*:\s*(.*)$")
HEAD_RE = re.compile(r"^===\s+(\w+)\s+([\w.\-]+)\s*$")
META_RE = re.compile(r"^(c|m|lv|k|ss|like|checked)\s*:\s*(.*)$")


def _split(v):
    return [x for x in re.split(r"[\s,]+", v.strip()) if x]


def _table(rows):
    out = []
    for r in rows:
        cells = [c.strip() for c in r.strip().strip("|").split("|")]
        out.append(cells)
    return out


def parse_block(fmt, iid, lines, where, problems):
    """One block of lines -> one item (or tf statements). Returns (item or None, [tf statements])."""
    x = {"id": "bk:" + iid, "src": "bank", "f": fmt, "c": [], "k": list(DEFAULT_K.get(fmt, [])), "rev": 1}
    fields, lists, table, parts = {}, {}, None, []
    cur_key, cur_list = None, None
    tfs = []
    for raw in lines:
        ln = raw.rstrip()
        if not ln.strip():
            cur_key = None if cur_key not in ("WHY", "ANS", "Q", "TEXT", "LEAD") else cur_key
            continue
        m = META_RE.match(ln)
        if m and not fields and not parts and cur_list is None:
            k, v = m.group(1), m.group(2).strip()
            if k == "c":
                x["cs"] = _split(v)
                x["c"] = [p for c in x["cs"] for p in (SECPTS.get(c) or [c])]
            elif k == "m":
                x["m"] = int(v)
            elif k == "lv":
                x["lv"] = int(v)
            elif k == "k":
                x["k"] = _split(v)
            elif k == "ss":
                x["ss"] = _split(v)
            elif k == "like":
                x["like"] = _split(v)
            elif k == "checked":
                x["rev"] = 0 if v.strip().lower() in ("yes", "y", "true", "1") else 1
            continue
        pm = PART_RE.match(ln)
        if pm:
            parts.append({"label": pm.group(1), "m": int(pm.group(2)), "q": pm.group(3).strip()})
            cur_key, cur_list = "PARTQ", None
            continue
        km = KEY_RE.match(ln)
        if km:
            k, v = km.group(1), km.group(2)
            cur_list = None
            if k == "TABLE":
                table = {"cap": v.strip(), "rows": []}
                cur_key = "TABLE"
            elif k in ("PTS", "PLAN"):
                target = parts[-1] if parts else fields
                target.setdefault(k, [])
                if v.strip():
                    target[k].append(v.strip())
                cur_key, cur_list = k, target[k]
            else:
                target = parts[-1] if (parts and k in ("ANS", "WHY")) else fields
                target[k] = v.strip()
                cur_key = k
            continue
        if ln.lstrip().startswith("|") and cur_key == "TABLE":
            table["rows"].append(ln)
            continue
        if ln.lstrip().startswith("- "):
            item = ln.lstrip()[2:].strip()
            if cur_list is not None:
                cur_list.append(item)
            else:
                lists.setdefault("-", []).append(item)
            continue
        # a continuation line
        if cur_list is not None and cur_list:
            cur_list[-1] += " " + ln.strip()
        elif cur_key == "PARTQ" and parts:
            parts[-1]["q"] += " " + ln.strip()
        elif cur_key and cur_key not in ("TABLE",):
            target = parts[-1] if (parts and cur_key in ("ANS", "WHY")) else fields
            target[cur_key] = (target.get(cur_key, "") + " " + ln.strip()).strip()
        elif lists.get("-"):
            lists["-"][-1] += " " + ln.strip()
        else:
            problems.append(f"{where}: {iid}: stray line {ln!r}")

    def need(*keys):
        for k in keys:
            if not fields.get(k):
                problems.append(f"{where}: {iid}: missing {k}:")

    if not x["c"]:
        problems.append(f"{where}: {iid}: no dot points (c:)")
    if table:
        x["table"] = {"cap": table["cap"], "rows": _table(table["rows"])}
        if len(x["table"]["rows"]) < 2:
            problems.append(f"{where}: {iid}: a table needs a heading row and at least one row")
    if fields.get("LEAD"):
        x["lead"] = fields["LEAD"]
    if fields.get("NOTE"):
        x["note"] = fields["NOTE"]

    if fmt == "mc":
        need("Q", "A", "B", "C", "D", "ANS")
        x["q"] = fields.get("Q", "")
        x["o"] = [fields.get(L, "") for L in "ABCD"]
        x["key"] = _split(fields.get("ANS", ""))
        if not x["key"] or any(k not in "ABCD" for k in x["key"]):
            problems.append(f"{where}: {iid}: ANS must be A, B, C or D")
        if fields.get("WHY"):
            x["e"] = {"why": fields["WHY"], "not": {}}
        x.setdefault("m", 1)
    elif fmt in ("sa", "scen", "stim"):
        if fmt == "stim":
            need("TITLE", "TEXT")
            x["title"], x["lede"], x["by"] = fields.get("TITLE", ""), fields.get("TEXT", ""), fields.get("BY", "Constructed source for practice")
            if not parts:
                problems.append(f"{where}: {iid}: a source needs PART (a) ... questions")
        if fmt == "scen" and not fields.get("LEAD"):
            problems.append(f"{where}: {iid}: a scenario needs LEAD: (the facts)")
        if parts:
            x["parts"] = [{"label": p["label"], "m": p["m"], "q": p["q"], "pts": p.get("PTS", []), "ans": p.get("ANS", "")} for p in parts]
            x["m"] = sum(p["m"] for p in parts)
            for p in x["parts"]:
                if not p["pts"] and not p["ans"]:
                    problems.append(f"{where}: {iid} {p['label']}: give PTS: or ANS:")
            if fmt == "stim":
                x["qs"] = [{"q": p["q"], "m": p["m"], "pts": p["pts"], "ans": p["ans"]} for p in x.pop("parts")]
        else:
            need("Q")
            x["q"] = fields.get("Q", "")
            x["pts"] = fields.get("PTS", [])
            if fields.get("ANS"):
                x["ans"] = fields["ANS"]
            if not x["pts"] and not x.get("ans"):
                problems.append(f"{where}: {iid}: give PTS: or ANS:")
            x.setdefault("m", DEFAULT_M.get(fmt, 4))
    elif fmt == "er":
        need("Q")
        x["q"] = fields.get("Q", "")
        x["pts"] = fields.get("PTS", [])
        if fields.get("PLAN"):
            x["plan"] = fields["PLAN"]
        x["m"] = x.get("m", 15)
    elif fmt == "teeacl":
        need("Q")
        x["q"] = fields.get("Q", "")
        x["pts"] = fields.get("PTS", [])
        if fields.get("ANS"):
            x["ans"] = fields["ANS"]
        if not x["pts"] and not x.get("ans"):
            problems.append(f"{where}: {iid}: give PTS: (what a strong paragraph includes) or ANS: (a model paragraph)")
        x.setdefault("m", 8)
    elif fmt == "order":
        need("TITLE")
        x["title"], x["blurb"] = fields.get("TITLE", ""), fields.get("LEAD", "")
        x.pop("lead", None)
        x["steps"] = lists.get("-", [])
        if fields.get("NOTE"):
            x["closing"] = fields["NOTE"]
            x.pop("note", None)
        if len(x["steps"]) < 3:
            problems.append(f"{where}: {iid}: put at least three '- step' lines, in the correct order")
        x.setdefault("m", len(x["steps"]))
    elif fmt == "terms":
        out = []
        for it in lists.get("-", []):
            if "=>" not in it:
                problems.append(f"{where}: {iid}: key term lines are '- term => definition': {it!r}")
                continue
            t, d = [s.strip() for s in it.split("=>", 1)]
            out.append({"id": "kt:" + re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-") + ":" + iid, "term": t, "def": d, "c": x["c"], "kt": 1})
        return None, out
    elif fmt == "sort":
        need("Q", "CATS")
        x["q"] = fields.get("Q", "")
        x["cats"] = [c.strip() for c in fields.get("CATS", "").split("|") if c.strip()]
        x["rows"] = []
        for it in lists.get("-", []):
            if "=>" not in it:
                problems.append(f"{where}: {iid}: sort line needs '=> category': {it!r}")
                continue
            t, cat = [s.strip() for s in it.split("=>", 1)]
            if cat not in x["cats"]:
                problems.append(f"{where}: {iid}: {cat!r} is not one of CATS")
            x["rows"].append({"t": t, "cat": cat})
        x.setdefault("m", max(2, round(len(x["rows"]) / 2)))
    elif fmt == "compare":
        need("Q", "COLS")
        x["q"] = fields.get("Q", "")
        x["cols"] = [c.strip() for c in fields.get("COLS", "").split("|")]
        x["rows"] = []
        for it in lists.get("-", []):
            if "=>" not in it:
                problems.append(f"{where}: {iid}: compare line needs 'heading => cell | cell': {it!r}")
                continue
            h, cells = it.split("=>", 1)
            cells = [c.strip() for c in cells.split("|")]
            if len(cells) != len(x["cols"]):
                problems.append(f"{where}: {iid}: row {h.strip()!r} has {len(cells)} cells for {len(x['cols'])} columns")
            x["rows"].append({"h": h.strip(), "cells": [{"t": c.lstrip("!").strip(), "given": c.startswith("!")} for c in cells]})
        x.setdefault("m", len(x["rows"]))
    elif fmt == "error":
        need("TEXT")
        x["q"] = fields.get("Q", "")
        x["text"] = fields.get("TEXT", "")
        errs = re.findall(r"\[\[(.+?)=>(.+?)\]\]", x["text"])
        if not errs:
            problems.append(f"{where}: {iid}: TEXT needs at least one [[wrong => right]]")
        x["n"] = len(errs)
        x.setdefault("m", len(errs))
    elif fmt == "tf":
        for it in lists.get("-", []):
            mm = re.match(r"^(T|F)\s*:\s*(.*)$", it)
            if not mm:
                problems.append(f"{where}: {iid}: true/false lines start '- T:' or '- F:': {it!r}")
                continue
            if mm.group(1) == "T":
                stmt, _, why = mm.group(2).partition("=>")
                tfs.append({"id": f"tf:{iid}:{len(tfs)}", "c": x["c"], "t": stmt.strip(), "f": None, "why": why.strip()})
            else:
                if "=>" not in mm.group(2):
                    problems.append(f"{where}: {iid}: a false statement needs '=> correction': {it!r}")
                    continue
                f, t = [s.strip() for s in mm.group(2).split("=>", 1)]
                tfs.append({"id": f"tf:{iid}:{len(tfs)}", "c": x["c"], "t": t, "f": f, "why": ""})
        return None, tfs
    elif fmt == "chain":
        need("TRIGGER")
        x["title"] = fields.get("TITLE", "")
        x["trigger"] = fields.get("TRIGGER", "")
        x["steps"] = []
        for it in lists.get("-", []):
            v, _, why = it.partition("=>")
            x["steps"].append({"v": v.strip(), "why": why.strip()})
        if len(x["steps"]) < 3:
            problems.append(f"{where}: {iid}: a chain needs at least three '- step => why' lines")
        x.setdefault("m", len(x["steps"]))
    else:
        problems.append(f"{where}: {iid}: unknown type {fmt!r}")
    return x, tfs


SECPTS = {}


def load(folder, points, secpts=None):
    """Every *.txt file in the bank folder. A file whose first line is "# reviewed" has been checked by the
    teacher: its questions lose the "not yet reviewed" flag. One question can be marked with "checked: yes"."""
    SECPTS.clear()
    SECPTS.update(secpts or {})
    items, tfs, problems = [], [], []
    for path in sorted(Path(folder).glob("*.txt")):
        block, head = [], None
        text = path.read_text(encoding="utf8")
        reviewed = text.lstrip().lower().startswith("# reviewed")
        lines = text.splitlines() + ["=== end end"]
        first_item = len(items)
        for i, ln in enumerate(lines, 1):
            m = HEAD_RE.match(ln)
            if m:
                if head:
                    fmt, iid, start = head
                    if fmt not in FORMATS:
                        problems.append(f"{path.name}:{start}: unknown type {fmt!r}")
                    else:
                        x, t = parse_block(fmt, iid, block, f"{path.name}:{start}", problems)
                        if x:
                            items.append(x)
                        tfs.extend(t)
                head, block = (m.group(1), m.group(2), i), []
            elif head:
                block.append(ln)
            elif ln.strip() and not ln.startswith("#"):
                problems.append(f"{path.name}:{i}: text before the first === line")
        if reviewed:
            for x in items[first_item:]:
                x["rev"] = 0
        for x in items[first_item:]:
            x.setdefault("_f", path.name)
        for t in tfs:
            t.setdefault("_f", path.name)
    for x in items:
        if x.get("cs") == x["c"]:
            x.pop("cs")
    terms = [t for t in tfs if t.get("kt")]
    tfs = [t for t in tfs if not t.get("kt")]
    seen = {}
    for t in terms:
        t.pop("kt")
        if t["term"].lower() in seen:
            problems.append(f"{t.get('_f')}: key term {t['term']!r} is in the bank twice")
        seen[t["term"].lower()] = 1
    for x in items + tfs + terms:
        x["h"] = fingerprint(x)
    for x in items + tfs + terms:
        bad = [c for c in x["c"] if c not in points]
        if bad:
            problems.append(f"{x['id']}: unknown dot points {bad}")
    return items, tfs, terms, problems


def fingerprint(x):
    """A short fingerprint of a question's content. A review decision is saved with it, so a question that is
    changed after it was approved (or flagged) goes back to the review list."""
    body = {k: v for k, v in x.items() if k not in ("id", "src", "rev", "h", "_f", "labels")}
    return hashlib.sha1(json.dumps(body, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:10]


# ---------------------------------------------------------------- the teacher's review page
REVIEW_URL = "https://phillippain.github.io/Tools/question-review/"
NAMES = {"mc": "Multiple choice", "sa": "Short answer", "scen": "Scenario", "stim": "Source-based", "er": "Extended response",
         "teeacl": "TEEACL paragraph", "order": "Put in order", "sort": "Sort and classify", "compare": "Compare table",
         "error": "Spot the mistake", "chain": "Cause and effect chain"}


def _tbl(t):
    e = html.escape
    if not t:
        return ""
    rows = t["rows"]
    return ('<table><thead><tr>' + "".join(f"<th>{e(c)}</th>" for c in rows[0]) + "</tr></thead><tbody>"
            + "".join("<tr>" + "".join(f"<td>{e(c)}</td>" for c in r) + "</tr>" for r in rows[1:]) + "</tbody></table>")


def _ul(xs):
    e = html.escape
    return "<ul>" + "".join(f"<li>{e(v)}</li>" for v in xs) + "</ul>" if xs else ""


def _err_html(text):
    return re.sub(r"\[\[(.+?)=&gt;(.+?)\]\]", r'<s>\1</s> <ins>\2</ins>', html.escape(text))


def tf_html(t):
    e = html.escape
    if "term" in t:
        return f"<p><b>{e(t['term'])}</b>: {e(t['def'])}</p>"
    return (f"<p><b>{'False' if t['f'] else 'True'}:</b> {e(t['f'] or t['t'])}</p>"
            + (f"<p class='why'>Corrected: {e(t['t'])}</p>" if t["f"] else "")
            + (f"<p class='why'>{e(t['why'])}</p>" if t.get("why") else ""))


def item_html(x, dias=None):
    """One bank question with its answer, as HTML (escaped)."""
    e = html.escape
    body = ""
    if x["f"] == "stim":
        body += f"<p><b>{e(x['title'])}</b> <small>({e(x.get('by', ''))})</small></p><p>{e(x['lede'])}</p>"
    if x.get("lead"):
        body += f"<p>{e(x['lead'])}</p>"
    body += _tbl(x.get("table"))
    if x.get("dia") and dias and x["dia"] in dias:
        dd = dias[x["dia"]]
        body += f'<div class="dia"><figure>{dd["s"]}<figcaption>Student copy</figcaption></figure><figure>{dd["a"]}<figcaption>Answer</figcaption></figure></div>'
    if x["f"] == "mc":
        body += f"<p>{e(x['q'])}</p><ol type='A'>" + "".join(
            f"<li class='{'k' if L in x['key'] else ''}'>{e(o)}</li>" for L, o in zip("ABCD", x["o"])) + "</ol>"
        if x.get("e"):
            body += f"<p class='why'><b>Why {'/'.join(x['key'])}:</b> {e(x['e']['why'])}</p>"
    elif x.get("parts") or x.get("qs"):
        for p in x.get("parts") or [dict(q, label=f"({'abcdef'[i]})") for i, q in enumerate(x["qs"])]:
            body += f"<p><b>{e(p['label'])}</b> {e(p['q'])} <small>({p['m']} marks)</small></p>{_ul(p['pts'])}"
            if p.get("ans"):
                body += f"<p class='why'>{e(p['ans'])}</p>"
    elif x["f"] in ("sa", "scen", "er", "teeacl"):
        body += f"<p>{e(x.get('q', ''))}</p>{_ul(x.get('pts'))}"
        if x.get("plan"):
            body += "<p><b>Plan</b></p>" + _ul(x["plan"])
        if x.get("ans"):
            body += f"<p class='why'>{e(x['ans'])}</p>"
    elif x["f"] == "sort":
        body += f"<p>{e(x['q'])}</p><table><thead><tr><th>Item</th><th>Category</th></tr></thead><tbody>" + "".join(
            f"<tr><td>{e(r['t'])}</td><td>{e(r['cat'])}</td></tr>" for r in x["rows"]) + "</tbody></table>"
    elif x["f"] == "compare":
        body += f"<p>{e(x['q'])}</p><table><thead><tr><th></th>" + "".join(f"<th>{e(c)}</th>" for c in x["cols"]) + "</tr></thead><tbody>" + "".join(
            "<tr><th>" + e(r["h"]) + "</th>" + "".join(f"<td>{'<i>(given)</i> ' if c['given'] else ''}{e(c['t'])}</td>" for c in r["cells"]) + "</tr>"
            for r in x["rows"]) + "</tbody></table>"
    elif x["f"] == "error":
        body += f"<p>{e(x.get('q') or '')}</p><p class='err'>{_err_html(x['text'])}</p>"
    elif x["f"] == "chain":
        body += f"<p><b>{e(x['title'])}</b>: {e(x['trigger'])}</p><ol>" + "".join(
            f"<li>{e(s['v'])} <small>{e(s['why'])}</small></li>" for s in x["steps"]) + "</ol>"
    elif x["f"] == "order":
        body += f"<p><b>{e(x['title'])}</b> {e(x.get('blurb', ''))}</p><ol>" + "".join(f"<li>{e(s)}</li>" for s in x["steps"]) + "</ol>"
    return body


def review_page(items, tfs, points, dias=None):
    e = html.escape

    out, toc = [], {}
    items = [x for x in items if x.get("rev")]
    for x in items:
        toc.setdefault(x["f"], 0)
        toc[x["f"]] += 1
        body = item_html(x, dias)
        like = f" · modelled on {' '.join(x['like'])}" if x.get("like") else ""
        out.append(f'<section id="{e(x["id"])}"><h2>{e(NAMES.get(x["f"], x["f"]))} <small>{e(x["id"][3:])} · '
                   f'{e(" ".join(x.get("cs") or x["c"]))} · {x.get("m", "")} marks · level {x.get("lv", "-")}{e(like)}</small></h2>{body}</section>')
    tfo = "".join((f"<li><b>{e(t['term'])}</b>: {e(t['def'])}" if "term" in t else f"<li><b>{'False' if t['f'] else 'True'}:</b> {e(t['f'] or t['t'])}"
                  + (f" <ins>→ {e(t['t'])}</ins>" if t["f"] else "")) + f" <small>{e(' '.join(t.get('cs') or t['c'][:4]))}</small></li>" for t in tfs)
    counts = " · ".join(f"{NAMES.get(k, k)} {v}" for k, v in sorted(toc.items()))
    return ('<!doctype html><html lang="en-AU"><head><meta charset="utf-8"><meta name="robots" content="noindex">'
            '<meta name="viewport" content="width=device-width,initial-scale=1"><title>Worksheet Maker: new questions for review</title>'
            '<style>body{font:15px/1.5 system-ui,sans-serif;max-width:900px;margin:24px auto;padding:0 16px;color:#101a3a}'
            'h1{font-size:1.5rem}h2{font-size:1rem;margin:22px 0 6px;border-top:1px solid #d8deee;padding-top:14px}small{font-weight:400;color:#4a5578}'
            'table{border-collapse:collapse;margin:8px 0;font-size:14px}td,th{border:1px solid #c9d2e4;padding:4px 8px;text-align:left;vertical-align:top}'
            'th{background:#eef2fb}li.k{font-weight:700;color:#17693a}.why{background:#eef8f1;border-left:3px solid #17693a;padding:4px 10px}'
            '.err s{color:#b42318}.err ins{color:#17693a;text-decoration:none;font-weight:700}ins{color:#17693a;text-decoration:none}'
            '.dia{display:flex;gap:16px;flex-wrap:wrap}.dia figure{margin:0;width:300px}.dia figcaption{font-size:12px;color:#4a5578}'
            'section{break-inside:avoid}.go{background:#fff6d6;border:1px solid #e8c96a;border-radius:8px;padding:8px 12px}</style></head><body><h1>Worksheet Maker: new questions for review</h1>'
            f'<p class="go"><b>To approve questions, use the <a href="{REVIEW_URL}">Question review</a> page on the staff Tools site</b>: one click to approve, flag for a fix or remove. This page lists every question still marked “not yet reviewed” in the bank files.</p>'
            f'<p>These {len(items)} questions and {len(tfs)} true/false statements and key terms were written for the Worksheet Maker by Claude and have not yet been checked. '
            'Each shows its answer. To change one, edit the file in <code>worksheet-maker/bank/</code> named in the heading and run '
            '<code>python3 worksheet-maker/build.py</code>. When you have checked a whole file, make its first line <code># reviewed</code>; to clear one question, add the line <code>checked: yes</code> under its heading. Checked questions drop off this page and lose the “not yet reviewed” label on the worksheet page.</p>'
            f'<p>{e(counts)}</p>' + "".join(out) + f'<h2>True or false statements and key terms ({len(tfs)})</h2><ul>{tfo}</ul></body></html>')


def review_data(items, tfs, points, dias, files):
    """Everything the Question review page (staff Tools site) shows: each bank question and statement with its
    fingerprint, file, dot points and its question and answer as HTML."""
    used = sorted({c for x in items + tfs for c in x["c"]})
    qs = [{"id": x["id"], "h": x["h"], "f": x["f"], "name": NAMES.get(x["f"], x["f"]), "file": files.get(x["id"], ""),
           "c": x["c"], "m": x.get("m"), "lv": x.get("lv"), "like": x.get("like", []), "pre": 0 if x.get("rev") else 1,
           "html": item_html(x, dias)} for x in items]
    ts = [{"id": t["id"], "h": t["h"], "f": "terms" if "term" in t else "tf", "name": "Key term" if "term" in t else "True or false", "file": files.get(t["id"], ""), "c": t["c"],
           "pre": 0, "html": tf_html(t)} for t in tfs]
    return {"dp": {c: points.get(c, "") for c in used}, "items": qs + ts}
