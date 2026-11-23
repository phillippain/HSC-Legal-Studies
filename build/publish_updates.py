#!/usr/bin/env python3
"""Publish the daily Evidence Finder update to the student-facing web page.

    python3 build/publish_updates.py add <digest.json> <summaries.json>
        Add (or replace) one day in data/daily-updates.json, rebuild updates.html and the What's New feed.
    python3 build/publish_updates.py rebuild     regenerate updates.html (and the feed) from the saved data
    python3 build/publish_updates.py status      list the days held

Inputs are the two files the evidence-daily-summary skill already makes each day:
  <digest.json>     written by `build/digest.py collect` (.digest/digest-<date>.json)
  <summaries.json>  {"<card id>": "Sentence one. Sentence two.", "_skip": ["<id>", ...],
                     "_notes": {"<id>": "Content note text"}}   (_notes is optional)

Outputs (commit and Push origin to make them live):
  data/daily-updates.json   every day's cards, topic by topic, with summaries and links
  updates.html              the page, https://phillippain.github.io/HSC-Legal-Studies/updates.html
                            Embed it in the Google Site with Insert > Embed > By URL.
  data/whats-new.json       rebuilt so the What's New box links to the day's update

The page is written for students. Summaries stay with the legal decision; any card that involves sexual
offences, terrorism, a death or family violence gets a short content note (see NOTE_RULES).
"""
import datetime, html, json, os, re, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analytics import inject  # GA4 tag

ROOT = os.environ.get("EVIDENCE_REPO") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "daily-updates.json")
PAGE = os.path.join(ROOT, "updates.html")
SITE = "https://phillippain.github.io/HSC-Legal-Studies/"

TOPIC = {   # colours and icons match the Evidence Finder and the colleague email
    "crime":         {"c": "#2E5C8A", "bg": "#E8EFF6", "icon": "⚖️", "tag": "HSC · Core Part I"},
    "humanrights":   {"c": "#7B4B94", "bg": "#F1EAF5", "icon": "🌍", "tag": "HSC · Core Part II"},
    "family":        {"c": "#C0612B", "bg": "#FBEDE4", "icon": "👪", "tag": "HSC · Option 3"},
    "shelter":       {"c": "#A23B5A", "bg": "#F7E8ED", "icon": "🏠", "tag": "HSC · Option 5"},
    "investigating": {"c": "#1F7A78", "bg": "#E3F1F0", "icon": "🔍", "tag": "Year 11 · Focus area 1"},
    "disputes":      {"c": "#1F7A78", "bg": "#E3F1F0", "icon": "🔨", "tag": "Year 11 · Focus area 2"},
    "changing":      {"c": "#1F7A78", "bg": "#E3F1F0", "icon": "🔄", "tag": "Year 11 · Focus area 3"},
    "experiences":   {"c": "#1F7A78", "bg": "#E3F1F0", "icon": "👥", "tag": "Year 11 · Focus area 4"},
    "other":         {"c": "#4F5F78", "bg": "#EEF0F4", "icon": "📄", "tag": ""},
}
ORDER = list(TOPIC)
TYPE_COLOR = {"case": "#4A3AA7", "legislation": "#1F3864", "media": "#B4531A",
              "international": "#0F6E6E", "report": "#5A6B2E", "document": "#4F5F78"}

# Content notes: matched against a card's title and summary.
NOTE_RULES = [
    ("sexual offences", r"sexual|indecent|grooming|child abuse material|sexually"),
    ("terrorism", r"terror|islamic state"),
    ("a death or killing", r"murder|manslaughter|homicide|killed|killing|inquest|stabb|fatal|\bdied\b|suicide|deaths? in custody"),
    ("family or domestic violence", r"domestic violence|family violence|coercive control|\bdv\b"),
]


def e(s):
    return html.escape(str(s or ""), quote=True)


def pretty(iso, fmt="%A %-d %B %Y"):
    try:
        return datetime.date.fromisoformat(iso).strftime(fmt)
    except (ValueError, TypeError):
        return iso or ""


def short(text, n=40):
    text = (text or "").split(" — ")[0].strip()
    return text if len(text) <= n else text[: n - 1].rstrip() + "…"


def join_and(parts):
    return parts[0] if len(parts) == 1 else ", ".join(parts[:-1]) + " and " + parts[-1]


def content_note(title, summary):
    text = f"{title} {summary}".lower()
    hits = [name for name, rx in NOTE_RULES if re.search(rx, text)]
    if not hits:
        return ""
    return (f"Content note: this item involves {join_and(hits)}. "
            "The summary describes the legal decision only.")


# ---------------------------------------------------------------- data

def load():
    if os.path.exists(DATA):
        return json.load(open(DATA, encoding="utf-8"))
    return {"updated": "", "days": []}


def save(store):
    store["days"].sort(key=lambda d: d["date"], reverse=True)
    store["updated"] = store["days"][0]["date"] if store["days"] else ""
    os.makedirs(os.path.dirname(DATA), exist_ok=True)
    json.dump(store, open(DATA, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def make_day(digest, summaries):
    skip = set(summaries.get("_skip", []))
    notes = summaries.get("_notes", {})
    labels = {g["key"]: g["label"] for g in digest["groups"]}
    m = re.search(r"\((\d{4}-\d{2}-\d{2})", digest.get("basis", ""))
    groups, n_new, n_upd, missing = [], 0, 0, []
    for g in digest["groups"]:
        items = []
        for it in g["items"]:
            if it["id"] in skip:
                continue
            s = summaries.get(it["id"])
            if not s:
                missing.append(it["id"])
                s = it["significance"]
            items.append({
                "id": it["id"], "status": it["status"], "type": it["type"], "type_label": it["type_label"],
                "title": it["title"], "summary": s,
                "note": notes.get(it["id"]) or content_note(it["title"], s),
                "added": it["added"], "core_labels": [short(l) for l in it["core_labels"][:3]],
                "also": [labels.get(k, k) for k in it.get("also_topics", [])],
                "card_url": it["card_url"], "document_url": it.get("document_url", ""),
                "document11_url": it.get("document11_url", ""), "source": it.get("source", ""),
            })
            n_new += it["status"] == "new"
            n_upd += it["status"] == "updated"
        if items:
            groups.append({"key": g["key"], "label": g["label"], "part": g["part"],
                           "course": g["course"], "items": items})
    for mid in missing:
        print(f"warning: no summary for {mid}; used its significance line", file=sys.stderr)
    return {"date": digest["today"], "since": m.group(1) if m else "", "new": n_new,
            "updated": n_upd, "groups": groups}


# ---------------------------------------------------------------- page

def card_html(it, accent):
    c = accent["c"]
    badge = ('<span class="pill new">New</span>' if it["status"] == "new"
             else '<span class="pill upd">Updated</span>')
    tcol = TYPE_COLOR.get(it["type"], "#4F5F78")
    when = ("first added " if it["status"] == "updated" else "added ") + pretty(it["added"], "%-d %b")
    chips = "".join(f'<span class="chip" style="color:{c};background:{accent["bg"]}">{e(l)}</span>'
                    for l in it["core_labels"])
    also = (f'<div class="also">Also relevant to: <b>{e(", ".join(it["also"]))}</b></div>'
            if it["also"] else "")
    note = f'<div class="note">ℹ️ {e(it["note"])}</div>' if it["note"] else ""
    btns = (f'<a class="btn solid" href="{e(it["card_url"])}" target="_blank" rel="noopener">Open the card →</a>')
    if it["document_url"]:
        btns += f'<a class="btn" href="{e(it["document_url"])}" target="_blank" rel="noopener">Summary PDF</a>'
    if it["document11_url"]:
        btns += f'<a class="btn y11" href="{e(it["document11_url"])}" target="_blank" rel="noopener">Year 11 summary</a>'
    if not it["document_url"] and not it["document11_url"] and it["source"]:
        btns += f'<a class="btn" href="{e(it["source"])}" target="_blank" rel="noopener">Original source</a>'
    search = e(f'{it["title"]} {it["summary"]} {" ".join(it["core_labels"])}'.lower())
    return f"""
<article class="card" style="--c:{c}" data-search="{search}" data-status="{it["status"]}">
<div class="meta">{badge}<span class="pill type" style="background:{tcol}">{e(it["type_label"])}</span><span class="when">{e(when)}</span></div>
<h4><a href="{e(it["card_url"])}" target="_blank" rel="noopener">{e(it["title"])}</a></h4>
<p>{e(it["summary"])}</p>{note}
<div class="chips">{chips}</div>{also}
<div class="btns">{btns}</div>
</article>"""


def day_html(day, open_):
    parts = []
    last_course = None
    for g in day["groups"]:
        a = TOPIC.get(g["key"], TOPIC["other"])
        if g["course"] != last_course:
            last_course = g["course"]
            parts.append(f'<div class="course">{"Year 11 (Preliminary)" if g["course"] == "preliminary" else "HSC"}</div>')
        n = len(g["items"])
        cards = "".join(card_html(it, a) for it in g["items"])
        parts.append(f"""
<section class="topic" data-topic="{e(g["key"])}">
<div class="banner" style="background:{a["c"]}"><span class="ico">{a["icon"]}</span>
<div><div class="tname">{e(g["label"])}</div><div class="ttag">{e(a["tag"] or g["part"])}</div></div>
<div class="tcount">{n} item{"s" if n != 1 else ""}</div></div>
<div class="grid">{cards}</div></section>""")
    dots = "".join(f'<span class="dot" title="{e(g["label"])}" style="background:{TOPIC.get(g["key"], TOPIC["other"])["c"]}"></span>'
                   for g in day["groups"])
    d = datetime.date.fromisoformat(day["date"])
    pills = ""
    if day["new"]:
        pills += f'<span class="pill new">{day["new"]} new</span>'
    if day["updated"]:
        pills += f'<span class="pill upd">{day["updated"]} updated</span>'
    since = f'<span class="since">since {e(pretty(day["since"], "%-d %b"))}</span>' if day["since"] else ""
    return f"""
<details class="day" id="d-{day["date"]}"{" open" if open_ else ""} data-open="{1 if open_ else 0}">
<summary><span class="cal"><b>{d.day}</b><i>{d.strftime("%b")}</i></span>
<span class="dtitle">{e(pretty(day["date"]))}<span class="dsub">{pills}{since}</span></span>
<span class="dots">{dots}</span><span class="chev">▾</span></summary>
<div class="daybody">{"".join(parts)}</div></details>"""


CSS = """
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:#eef1f6;color:#1b2330;font:15px/1.55 -apple-system,'Segoe UI',Helvetica,Arial,sans-serif}
a{color:inherit}
.wrap{max-width:1180px;margin:0 auto;padding:14px max(14px,env(safe-area-inset-left,0px)) 40px}
header{background:linear-gradient(135deg,#0F2A4D,#2E5C8A);color:#fff;border-radius:16px;padding:22px 24px}
.eyebrow{font:700 11px/1 -apple-system,'Segoe UI',Helvetica,Arial,sans-serif;letter-spacing:.16em;text-transform:uppercase;color:#a9c0e0}
h1{font:700 28px/1.2 Georgia,'Times New Roman',serif;margin:8px 0 6px}
header p{margin:0;color:#d6e0ee;max-width:70ch}
.latest{margin-top:14px;display:flex;gap:8px;flex-wrap:wrap;align-items:center;font-size:13px;color:#d6e0ee}
.latest a{background:#fff;color:#0F2A4D;text-decoration:none;font-weight:700;border-radius:999px;padding:7px 13px}
.how{margin:12px 0 0;background:#fff;border:1px solid #e2e5ea;border-radius:12px;padding:11px 14px;font-size:13px;color:#2b3340}
.how b{color:#0F2A4D}
.controls{position:sticky;top:0;z-index:20;margin:12px -4px 0;padding:10px 4px;background:#eef1f6ee;backdrop-filter:blur(4px)}
.search{width:100%;font:15px/1.2 -apple-system,'Segoe UI',Helvetica,Arial,sans-serif;padding:12px 14px;border:1.5px solid #c9d1dd;border-radius:10px;background:#fff;color:#1b2330}
.search:focus,.fchip:focus-visible,.btn:focus-visible,summary:focus-visible{outline:3px solid #2E5C8A;outline-offset:2px}
.filters{display:flex;gap:8px;flex-wrap:wrap;margin-top:10px}
.fchip{font:600 13px/1 -apple-system,'Segoe UI',Helvetica,Arial,sans-serif;border:1.5px solid var(--c);color:var(--c);background:#fff;border-radius:999px;padding:9px 13px;cursor:pointer}
.fchip[aria-pressed=true]{background:var(--c);color:#fff}
.count{margin:8px 2px 0;font-size:13px;color:#5b6472}
.day{margin-top:14px;background:#fff;border:1px solid #dfe3ea;border-radius:14px;overflow:hidden}
summary{list-style:none;cursor:pointer;display:flex;align-items:center;gap:14px;padding:12px 16px;background:#fff}
summary::-webkit-details-marker{display:none}
.cal{flex:none;width:52px;height:56px;border-radius:10px;background:#0F2A4D;color:#fff;text-align:center;display:flex;flex-direction:column;justify-content:center}
.cal b{font:700 22px/1 Georgia,serif}.cal i{font:700 11px/1.4 -apple-system,'Segoe UI',Helvetica,Arial,sans-serif;font-style:normal;letter-spacing:.1em;text-transform:uppercase;color:#a9c0e0}
.dtitle{flex:1;min-width:0;font:700 18px/1.3 Georgia,'Times New Roman',serif}
.dsub{display:flex;gap:6px;flex-wrap:wrap;align-items:center;margin-top:5px;font:12px/1 -apple-system,'Segoe UI',Arial,sans-serif;color:#5b6472}
.dots{display:flex;gap:4px}.dot{width:10px;height:10px;border-radius:50%}
.chev{font-size:18px;color:#5b6472;transition:transform .15s}details[open]>summary .chev{transform:rotate(180deg)}
.daybody{padding:4px 16px 16px;border-top:1px solid #eef0f4;background:#f7f8fb}
.course{margin:16px 0 4px;font:700 11px/1 -apple-system,'Segoe UI',Helvetica,Arial,sans-serif;letter-spacing:.14em;text-transform:uppercase;color:#5b6472}
.banner{display:flex;align-items:center;gap:12px;color:#fff;border-radius:12px;padding:10px 14px;margin:12px 0 12px}
.ico{flex:none;width:38px;height:38px;border-radius:50%;background:#fff;text-align:center;font-size:21px;line-height:38px}
.tname{font:700 18px/1.2 Georgia,'Times New Roman',serif}.ttag{font-size:12px;color:#ffffffcc}
.tcount{margin-left:auto;font-weight:700;font-size:13px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,320px),1fr));gap:14px;align-items:stretch}
.card{min-width:0;display:flex;flex-direction:column;background:#fff;border:1px solid #e2e5ea;border-left:6px solid var(--c);border-radius:10px;padding:14px 16px 8px}
.meta{display:flex;flex-wrap:wrap;gap:6px;align-items:center;margin-bottom:8px}
.pill{font:700 11px/1.2 -apple-system,'Segoe UI',Helvetica,Arial,sans-serif;letter-spacing:.04em;text-transform:uppercase;color:#fff;border-radius:9px;padding:5px 8px;display:inline-block}
.pill.new{background:#1B7F4B}.pill.upd{background:#B7791F}
.when{font-size:12px;color:#5b6472}.since{font-size:12px;color:#5b6472}
h4{font:700 16px/1.35 Georgia,'Times New Roman',serif;margin:0 0 8px}
h4 a{text-decoration:none}h4 a:hover{text-decoration:underline}
.card p{margin:0 0 10px;color:#2b3340;overflow-wrap:anywhere}
.note{margin:0 0 10px;font-size:12.5px;line-height:1.45;color:#6b4a0b;background:#FFF6E0;border-radius:8px;padding:7px 10px}
.chips{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:6px}
.chip{font:700 10.5px/1.2 -apple-system,'Segoe UI',Helvetica,Arial,sans-serif;letter-spacing:.04em;text-transform:uppercase;border-radius:8px;padding:5px 8px}
.also{font-size:12px;color:#5b6472;margin-bottom:6px}.also b{color:#1b2330}
.btns{margin-top:auto;padding-top:6px;display:flex;gap:8px;flex-wrap:wrap}
.btn{display:inline-block;font:600 13px/1 -apple-system,'Segoe UI',Helvetica,Arial,sans-serif;text-decoration:none;color:var(--c);border:1.5px solid var(--c);border-radius:8px;padding:10px 13px;margin-bottom:8px;background:#fff}
.btn.solid{background:var(--c);color:#fff}.btn.y11{color:#1F7A78;border-color:#1F7A78}
.btn:hover{filter:brightness(.94)}
.empty{display:none;margin-top:16px;padding:24px;text-align:center;background:#fff;border-radius:12px;color:#5b6472}
footer{margin-top:22px;font-size:12px;color:#5b6472;text-align:center}
@media (max-width:560px){h1{font-size:23px}.dots{display:none}.dtitle{font-size:16px}}
@media (prefers-reduced-motion:reduce){.chev{transition:none}}
"""

JS = """
(function(){
var days=[].slice.call(document.querySelectorAll('.day')),cards=[].slice.call(document.querySelectorAll('.card'));
var q=document.getElementById('q'),chips=[].slice.call(document.querySelectorAll('.fchip')),topic='all';
var count=document.getElementById('count'),empty=document.getElementById('empty');
function apply(){
  var terms=q.value.toLowerCase().split(/\\s+/).filter(Boolean),active=topic!=='all'||terms.length>0,shown=0;
  cards.forEach(function(c){
    var t=c.closest('.topic').getAttribute('data-topic'),s=c.getAttribute('data-search');
    var ok=(topic==='all'||t===topic||(topic==='year11'&&/^(investigating|disputes|changing|experiences)$/.test(t)))
      &&terms.every(function(w){return s.indexOf(w)>-1});
    c.style.display=ok?'':'none';if(ok)shown++;
  });
  [].slice.call(document.querySelectorAll('.topic')).forEach(function(s){
    s.style.display=s.querySelector('.card:not([style*="none"])')?'':'none';});
  [].slice.call(document.querySelectorAll('.course')).forEach(function(c){
    var n=c.nextElementSibling,vis=false;
    while(n&&!n.classList.contains('course')){if(n.style.display!=='none')vis=true;n=n.nextElementSibling;}
    c.style.display=vis?'':'none';});
  days.forEach(function(d){
    var vis=!!d.querySelector('.card:not([style*="none"])');
    d.style.display=vis?'':'none';
    if(active&&vis)d.open=true;else if(!active)d.open=d.getAttribute('data-open')==='1';
  });
  count.textContent=active?(shown+' item'+(shown===1?'':'s')+' match'):'';
  empty.style.display=shown?'none':'block';
}
q.addEventListener('input',apply);
chips.forEach(function(b){b.addEventListener('click',function(){
  topic=b.getAttribute('data-topic');
  chips.forEach(function(x){x.setAttribute('aria-pressed',x===b?'true':'false')});apply();});});
function openHash(){
  var m=location.hash.match(/^#(d-\\d{4}-\\d{2}-\\d{2})$/);if(!m)return;
  var d=document.getElementById(m[1]);if(d){d.open=true;d.setAttribute('data-open','1');d.scrollIntoView();}
}
window.addEventListener('hashchange',openHash);openHash();
})();
"""


def build_page(store):
    days = store["days"]
    open_n = 2
    topics = []
    for d in days:
        for g in d["groups"]:
            if g["key"] not in topics:
                topics.append(g["key"])
    topics.sort(key=lambda k: ORDER.index(k) if k in ORDER else 99)
    chips = '<button class="fchip" style="--c:#0F2A4D" data-topic="all" aria-pressed="true">All topics</button>'
    hsc = [k for k in topics if k in ("crime", "humanrights", "family", "shelter")]
    for k in hsc:
        a = TOPIC[k]
        label = next(g["label"] for d in days for g in d["groups"] if g["key"] == k)
        chips += f'<button class="fchip" style="--c:{a["c"]}" data-topic="{k}" aria-pressed="false">{a["icon"]} {e(label)}</button>'
    if any(k.startswith(("investigating", "disputes", "changing", "experiences")) for k in topics):
        chips += '<button class="fchip" style="--c:#1F7A78" data-topic="year11" aria-pressed="false">📘 Year 11</button>'
    latest = days[0] if days else None
    latest_html = ""
    if latest:
        bits = []
        if latest["new"]:
            bits.append(f'{latest["new"]} new')
        if latest["updated"]:
            bits.append(f'{latest["updated"]} updated')
        latest_html = (f'<div class="latest"><span>Latest update: <b style="color:#fff">{e(pretty(latest["date"]))}</b>'
                       f' · {" · ".join(bits)}</span><a href="#d-{latest["date"]}">Jump to it ↓</a></div>')
    body = "".join(day_html(d, i < open_n) for i, d in enumerate(days)) or \
        '<p class="empty" style="display:block">No updates yet.</p>'
    built = datetime.datetime.now().strftime("%-d %B %Y")
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>What's new in the Evidence Finder</title>
<style>{CSS}</style></head><body><div class="wrap">
<header><div class="eyebrow">HSC Legal Studies · Evidence Finder</div>
<h1>What's new in the Evidence Finder</h1>
<p>New and updated cases, laws, news stories and reports, each with a short summary and links to the full evidence summary. Newest first.</p>
{latest_html}</header>
<div class="how"><b>How to use each item</b> &nbsp; ① Read the summary &rarr; ② Open the PDF for the full evidence summary &rarr; ③ Open the card to see the syllabus dot points it supports. Cards marked <b>Updated</b> were already in the Finder and have new material.</div>
<div class="controls"><input id="q" class="search" type="search" placeholder="Search by case, topic or key words, for example bail, jury, tenancy" aria-label="Search updates" autocomplete="off">
<div class="filters" role="group" aria-label="Filter by topic">{chips}</div><div class="count" id="count" aria-live="polite"></div></div>
<div id="days">{body}</div>
<div class="empty" id="empty">Nothing matches that search. Try fewer words or choose All topics.</div>
<footer>Summaries are written for study, not as legal advice. Page rebuilt {built}. <a href="{SITE}evidence.html" target="_blank" rel="noopener">Open the full Evidence Finder</a>.</footer>
</div><script>{JS}</script></body></html>"""


def rebuild():
    store = load()
    open(PAGE, "w", encoding="utf-8").write(inject(build_page(store)))
    n = sum(d["new"] + d["updated"] for d in store["days"])
    print(f"updates.html: {len(store['days'])} days, {n} items")
    wn = os.path.join(ROOT, "build", "build_whatsnew.py")
    if os.path.exists(wn):      # keep the What's New box in step
        subprocess.run([sys.executable, wn], check=False)


def main(a):
    if a and a[0] == "add" and len(a) >= 3:
        digest = json.load(open(a[1], encoding="utf-8"))
        summaries = json.load(open(a[2], encoding="utf-8"))
        store = load()
        day = make_day(digest, summaries)
        store["days"] = [d for d in store["days"] if d["date"] != day["date"]] + [day]
        save(store)
        print(f"{day['date']}: {day['new']} new, {day['updated']} updated saved")
        rebuild()
    elif a and a[0] == "append" and len(a) >= 3:
        # add a later batch to a day that already exists (merges items by topic)
        digest = json.load(open(a[1], encoding="utf-8"))
        summaries = json.load(open(a[2], encoding="utf-8"))
        store = load()
        extra = make_day(digest, summaries)
        cur = next((d for d in store["days"] if d["date"] == extra["date"]), None)
        if not cur:
            store["days"].append(extra)
        else:
            have = {it["id"] for g in cur["groups"] for it in g["items"]}
            for g in extra["groups"]:
                items = [it for it in g["items"] if it["id"] not in have]
                tgt = next((x for x in cur["groups"] if x["key"] == g["key"] and x["course"] == g["course"]), None)
                if tgt:
                    tgt["items"] += items
                elif items:
                    cur["groups"].append({**g, "items": items})
            order = {"core": 0, "preliminary": 1}
            cur["groups"].sort(key=lambda g: order.get(g["course"], 2))
            cur["new"] = sum(it["status"] == "new" for g in cur["groups"] for it in g["items"])
            cur["updated"] = sum(it["status"] == "updated" for g in cur["groups"] for it in g["items"])
        save(store)
        print("appended to", extra["date"])
        rebuild()
    elif a and a[0] == "rebuild":
        rebuild()
    elif a and a[0] == "status":
        for d in load()["days"]:
            print(d["date"], d["new"], "new", d["updated"], "updated")
    else:
        print(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
