# -*- coding: utf-8 -*-
import sys, json, re, importlib, html, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analytics import inject  # GA4 tag
BOOKDIR = sys.argv[1]; OUT = sys.argv[2]
sys.path.insert(0, BOOKDIR); c = importlib.import_module('content')
SITE = 'https://sites.google.com/education.nsw.gov.au/hsc-legal-studies-at-sscbwb'
EV = 'https://phillippain.github.io/HSC-Legal-Studies/evidence.html#ev-'
recs = json.load(open('/mnt/user-data/uploads/HSC Legal Studies/data/records.json'))
short = {v['short'].lower(): k for k, v in recs.items()}
def find(t):
    t = t.lower()
    if t in short: return short[t]
    for s, k in short.items():
        if t in s or s in t: return k
HUB_SLUG = {1:'1-the-nature-of-shelter'}[c.BOOK['n']]
def slug(t): return re.sub(r'[^a-z0-9]+','-',t.lower()).strip('-')
parts = c.PARTS + [c.PART5]
def purl(i): return f"{SITE}/shelter/{HUB_SLUG}/{slug(parts[i]['title'])}"
HUB = f"{SITE}/shelter/{HUB_SLUG}"
OVERVIEW = f"{SITE}/shelter/shelter-overview"
def esc(s): return html.escape(s, quote=False)
HOUSE = lambda col: f'<svg viewBox="0 0 48 44" width="46" height="42" aria-hidden="true"><path d="M24 2 3 20h6v22h30V20h6z" fill="{col}"/><path d="M19 42V28a5 5 0 0 1 10 0v14z" fill="#fff"/></svg>'
CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Lora:wght@500;600;700&display=swap');
*{box-sizing:border-box;margin:0}
:root{--ink:#1E2A2F;--paper:#FBF8F3;--line:#d9d2c5;--c:#1B5E63;--t:#E3EFEF}
body{font:14.5px/1.55 Inter,Segoe UI,system-ui,sans-serif;color:var(--ink);background:transparent;padding:10px}
h1,h2,h3{font-family:Lora,Georgia,serif;line-height:1.2}
a{color:inherit}
.nav{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:12px}
.nav a{border:1.5px solid var(--c);color:var(--c);background:#fff;border-radius:999px;padding:4px 11px;font-weight:600;font-size:13px;text-decoration:none}
.nav a.on{background:var(--c);color:#fff}
.hero{background:var(--c);color:#fff;border-radius:6px;padding:18px 20px;display:flex;gap:16px;align-items:center}
.hero h1{font-size:28px}.hero p{opacity:.95;margin-top:4px}
.plate{background:#fff;border-radius:6px;padding:4px 6px 0;text-align:center;flex:none}
.plate b{display:block;font:700 18px Lora,serif;color:var(--c);margin-top:-6px;padding-bottom:3px}
.box{background:#fff;border:1px solid var(--line);border-top:4px solid var(--c);padding:12px 14px;margin-top:12px}
.box h3{font-size:16px;color:var(--c);margin-bottom:6px}
.box ul{padding-left:20px}
.learn{display:grid;grid-template-columns:1fr 1fr;gap:12px}
@media(max-width:620px){.learn{grid-template-columns:1fr}}
.ican li{list-style:none;margin-left:-18px}
.ican label{cursor:pointer}
.terms{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:8px}
.term{background:var(--t);border-left:4px solid var(--c);padding:8px 10px}
.term b{font-family:Lora,serif;color:var(--c)}
.sub{margin-top:26px}
.sub>h2{display:flex;align-items:center;gap:10px;font-size:21px}
.door{flex:none;background:var(--c);color:#fff;border-radius:18px 18px 3px 3px;min-width:44px;height:34px;display:grid;place-items:center;font:700 14px Inter;padding:0 8px}
.frame{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:10px;margin-top:10px}
.frame>div{background:#fff;border:1px solid var(--line);border-top:3px solid var(--c);padding:9px 11px}
.frame small{display:block;font:700 11px Inter;letter-spacing:.06em;text-transform:uppercase;color:var(--c);margin-bottom:3px}
.vis{margin-top:14px;background:var(--paper);border:1px solid var(--line);padding:12px 14px}
.vis h3{font-size:15px;margin-bottom:8px}
.vis .src{font-size:12px;color:#5c6a70;margin-top:6px}
.seven{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:8px}
.seven div{background:#fff;border:1px solid var(--line);border-top:3px solid var(--c);padding:7px 9px;font-size:13px}
.seven b{display:block;font-family:Lora,serif;color:var(--c)}
.tl{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:0;position:relative}
.tl div{padding:8px 8px 8px 10px;border-left:3px solid var(--c);font-size:13px}
.tl b.y{font:700 18px Lora,serif;color:var(--c);display:block}
.flow{display:flex;flex-direction:column;gap:0}
.flow div{background:#fff;border:1px solid var(--line);border-left:5px solid var(--c);padding:7px 12px;font-weight:600}
.flow i{display:block;text-align:center;color:var(--c);line-height:1;font-style:normal;font-size:18px}
.flow div.brk{background:#fde6e7;border-left-color:#A3262A;color:#A3262A}
.note{margin-top:8px;font-size:13.5px}
.split{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.split>div{background:#fff;border:1px solid var(--line);border-top:3px solid var(--c);padding:8px 12px}
.split h4{font-family:Lora,serif;color:var(--c);margin-bottom:4px}
.mid{grid-column:1/-1;text-align:center;background:var(--t);padding:6px;font-weight:600}
.ladder .r{display:flex;align-items:center;gap:8px;margin:4px 0}
.ladder .bar{background:var(--c);color:#fff;padding:6px 10px;font-weight:600;font-size:13px;border-radius:3px 12px 12px 3px}
.ladder small{color:#5c6a70}
.case{margin-top:14px;background:#fff;border:1px solid var(--line);border-top:4px solid var(--c);padding:12px 14px}
.case .k{display:inline-block;background:var(--c);color:#fff;font:700 11px Inter;letter-spacing:.06em;padding:2px 8px;transform:skewX(-8deg)}
.case h3{font-size:18px;margin:6px 0 0}.case .s{color:#5c6a70;margin-bottom:6px}
.case .stat{float:right;margin:0 0 6px 10px;max-width:210px;background:var(--t);border-left:4px solid var(--c);padding:6px 10px}
.case .stat b{font:700 26px Lora,serif;color:var(--c);display:block}
.case ul{padding-left:20px;margin:6px 0}
.law{font-size:13px;background:var(--paper);padding:5px 9px;margin:6px 0}
.how{background:var(--t);padding:8px 11px;margin-top:8px}
.btns{display:flex;gap:8px;flex-wrap:wrap;margin-top:8px}
.btn,button.rv{font:600 13px Inter;border:1.5px solid var(--c);color:var(--c);background:#fff;border-radius:4px;padding:4px 10px;cursor:pointer;text-decoration:none;display:inline-block}
.btn.f{background:var(--c);color:#fff}
.chk{margin-top:14px;border:1px dashed var(--c);padding:10px 12px;background:#fff}
.chk h3{font-size:15px;color:var(--c);margin-bottom:6px}
.qa{margin:8px 0}.qa .a{display:none;background:#E4EFE6;border-left:4px solid #2E6B3A;padding:6px 10px;margin-top:5px}
.qa.open .a{display:block}
table.t{border-collapse:collapse;width:100%;font-size:13.5px;margin:6px 0}
table.t th{background:var(--c);color:#fff;text-align:left;padding:5px 8px}
table.t td{border:1px solid var(--line);padding:5px 8px;vertical-align:top}
td .ans{display:none;color:#1E6B4F;font-weight:600}
td.open .ans{display:inline}td.open button{display:none}
.card{background:#fff;border:1px solid var(--line);border-top:4px solid var(--c);padding:12px 14px}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:12px;margin-top:14px}
.cards .card{display:block;text-decoration:none}
.cards h3{font-size:18px;color:var(--c)}
.q{margin:10px 0}.q .o{display:block;width:100%;text-align:left;background:#fff;border:1.5px solid var(--line);padding:6px 10px;margin:4px 0;cursor:pointer;font:inherit}
.q .o.right{background:#E4EFE6;border-color:#2E6B3A}.q .o.wrong{background:#fde6e7;border-color:#A3262A}
.teeacl{margin-top:8px}.teeacl div{display:flex;gap:10px;margin:6px 0}
.teeacl b.l{flex:none;width:30px;height:30px;border-radius:15px 15px 3px 3px;color:#fff;display:grid;place-items:center;font-family:Lora,serif}
.ev{columns:2;column-gap:20px;font-size:13.5px}
@media(max-width:620px){.ev{columns:1}}
.ev h4{break-after:avoid;margin-top:8px;color:var(--c)}
"""
JS = """
document.querySelectorAll('.qa>button').forEach(b=>b.onclick=()=>b.parentNode.classList.toggle('open'));
document.querySelectorAll('td button.rv').forEach(b=>b.onclick=()=>b.parentNode.classList.add('open'));
document.querySelectorAll('.q').forEach(q=>{const a=+q.dataset.a;q.querySelectorAll('.o').forEach((o,i)=>o.onclick=()=>{q.querySelectorAll('.o').forEach((x,j)=>{x.classList.toggle('right',j==a);x.classList.toggle('wrong',j==i&&i!=a)})})});
"""
def nav(active):
    items = [f'<a href="{HUB}" target="_blank">⌂ Hub</a>'] + [f'<a class="{"on" if i==active else ""}" href="{purl(i)}" target="_blank">{i+1}. {esc(p["title"])}</a>' for i,p in enumerate(parts)]
    return '<div class="nav">' + ''.join(items) + '</div>'
def wrap(col, tint, body, title):
    return inject(f'<!doctype html><html lang="en-AU"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><base target="_blank"><title>{esc(title)}</title><style>{CSS}:root{{--c:{col};--t:{tint}}}</style></head><body>{body}<script>{JS}</script></body></html>')
def cell(x):
    if isinstance(x, (list,tuple)) and x and x[0]=='?': return f'<button class="rv">Show</button><span class="ans">{x[1]}</span>'
    return x
def visual(v):
    k = v['kind']; h = f'<div class="vis"><h3>{esc(v["title"])}</h3>'
    if k=='seven': h += '<div class="seven">'+''.join(f'<div><b>{esc(a)}</b>{esc(b)}</div>' for a,b in v['items'])+'</div>'
    elif k=='timeline': h += '<div class="tl">'+''.join(f'<div><b class="y">{esc(a)}</b><b>{esc(b)}</b><br>{esc(d)}</div>' for a,b,d in v['items'])+'</div>'
    elif k=='flow':
        st=v['steps']; br=v.get('breakat'); parts_=[]
        for i,s in enumerate(st):
            parts_.append(f'<div class="{"brk" if br==i else ""}">{esc(s)}</div>')
        h += '<div class="flow">'+'<i>▼</i>'.join(parts_)+'</div>'
        if v.get('note'): h += f'<p class="note"><b>{esc(v.get("notehead","Notice"))}:</b> {v["note"]}</p>'
    elif k=='split':
        (lt,ll),(rt,rl)=v['left'],v['right']
        h += '<div class="split"><div><h4>'+esc(lt)+'</h4><ul>'+''.join(f'<li>{esc(x)}</li>' for x in ll)+'</ul></div><div><h4>'+esc(rt)+'</h4><ul>'+''.join(f'<li>{esc(x)}</li>' for x in rl)+'</ul></div>'+(f'<div class="mid">{esc(v["mid"])}</div>' if v.get('mid') else '')+'</div>'
    elif k=='ladder':
        h += '<div class="ladder">'+''.join(f'<div class="r"><div class="bar" style="width:{20+n*14}%">{esc(a)}</div><div><b>{esc(prot)}</b><br><small>{b}</small></div></div>' for a,b,prot,n in v['rungs'])+'</div>'
    if v.get('source'): h += f'<div class="src">Source: {esc(v["source"])}</div>'
    if v.get('use'): h += f'<p class="note"><b>Use it:</b> {esc(v["use"])}</p>'
    return h+'</div>'
def casecard(cd):
    fid = find(cd['finder']); fb = f'<a class="btn f" href="{EV}{fid}" target="_blank" rel="noopener">📚 Open in the Evidence Finder</a>' if fid else ''
    return (f'<div class="case"><span class="k">{esc(cd["kind"])}</span><h3>{esc(cd["title"])}</h3><div class="s">{esc(cd["sub"])}</div>'
      f'<div class="stat"><b>{esc(cd["stat"][0])}</b>{esc(cd["stat"][1])}</div><ul>'+''.join(f'<li>{f}</li>' for f in cd['facts'])+'</ul>'
      f'<div class="law"><b>Law:</b> {cd["law"]}</div><div class="how"><b>{esc(cd["how_title"])}</b><br>{cd["how"]}</div>'
      f'<div class="qa"><b>Your turn:</b> {cd["turn"]}<br><button class="rv">Show a model answer</button><div class="a">{cd["ans"]}</div></div>{fb}</div>')
def tasks(sub):
    out=''
    for kind,title,items in sub['tasks']:
        out += f'<div class="chk"><h3>✏️ Check yourself: {esc(title)}</h3>'
        for it in items:
            t=it[0]
            if t=='table':
                out += f'<p>{it[1]}</p><table class="t"><tr>'+''.join(f'<th>{esc(h)}</th>' for h in it[2])+'</tr>'+''.join('<tr>'+''.join(f'<td>{cell(x)}</td>' for x in row)+'</tr>' for row in it[3])+'</table>'
            elif t=='q':
                out += f'<div class="qa"><p>{it[1]}</p><button class="rv">Show a model answer</button><div class="a">{it[3]}</div></div>'
            elif t=='flowq':
                full=[(s[1] if isinstance(s,(list,tuple)) else s) for s in it[2]]
                out += f'<div class="qa"><p>{it[1]}</p><button class="rv">Show the completed flow</button><div class="a">'+' ▶ '.join(full)+'</div></div>'
            elif t=='ladderq':
                out += f'<div class="qa"><p>{it[1]}</p><button class="rv">Show the answers</button><div class="a"><ul>'+''.join(f'<li><b>{esc(r[0])}:</b> {r[1][1]}; {r[2][1]}</li>' for r in it[2])+'</ul></div></div>'
        out += '</div>'
    return out
def sub_html(s):
    n=s['notes']
    fr=''.join(f'<div><small>{lab}</small>{n[k]}</div>' for lab,k in [('What it is','what'),('The law','law'),('An example','example'),('Why it matters','why')])
    h=f'<div class="sub"><h2><span class="door">{s["id"]}</span>{esc(s["title"])}</h2><div class="frame">{fr}</div>'
    if 'visual' in s: h+=visual(s['visual'])
    if 'card' in s: h+=casecard(s['card'])
    return h+tasks(s)+'</div>'
def part_page(i):
    p=parts[i]; col,tint=p['colour'],p['tint']
    h = nav(i)+f'<div class="hero"><div class="plate">{HOUSE(col)}<b>{p["n"]}</b></div><div><h1>{esc(p["title"])}</h1><p>{esc(p["strap"])}</p></div></div>'
    if i<len(c.PARTS):
        h+=f'<div class="learn"><div class="box"><h3>We are learning to</h3><p>{esc(p["learnto"])}</p><ul>'+''.join(f'<li>{esc(x)}</li>' for x in p['li'])+'</ul></div><div class="box ican"><h3>I can… (tick as you go)</h3><ul>'+''.join(f'<li><label><input type="checkbox"> {esc(x)}</label></li>' for x in p['ican'])+'</ul></div></div>'
        h+='<div class="box"><h3>Key terms</h3><div class="terms">'+''.join(f'<div class="term"><b>{esc(a)}</b><br>{b}</div>' for a,b in p['terms'])+'</div></div>'
        if p.get('recall'):
            rt,rq=p['recall']; h+=f'<div class="chk"><h3>↩ {esc(rt)}</h3>'+''.join(f'<div class="qa"><p>{q}</p><small>{hint}</small><br><button class="rv">Show answer</button><div class="a">{a}</div></div>' for q,hint,a in rq)+'</div>'
        h+=''.join(sub_html(s) for s in p['subs'])
    else:
        sc=p['scenario']; w=p['writing']; ev=p['evidence']
        h+=f'<div class="box"><h3>{esc(sc["worked_title"])}</h3><p>{sc["worked"]}</p><table class="t">'+''.join(f'<tr><td><b>{q}</b></td><td>{a}</td></tr>' for q,a in sc['rows'])+f'</table></div>'
        h+=f'<div class="chk"><h3>🔑 {esc(sc["yours_title"])}</h3><p>{sc["yours"]}</p><table class="t">'+''.join(f'<tr><td><b>{q}</b></td><td>{cell(["?",a])}</td></tr>' for q,a in sc['yrows'])+'</table></div>'
        cols={'T':'#1F3864','E':'#0F6E6E','A':'#6A3D6E','C':'#A8481F','L':'#A3262A'}
        h+=f'<div class="box"><h3>Model paragraph (TEEACL)</h3><p><b>{esc(w["question"])}</b></p><div class="teeacl">'+''.join(f'<div><b class="l" style="background:{cols.get(l,"#444")}">{l}</b><div><small><b>{esc(lab)}</b></small><br>{txt}</div></div>' for l,lab,txt in w['model'])+'</div></div>'
        labs={'L':'Legislation','C':'Cases','M':'Media','I':'International','D':'Documents'}
        h+='<div class="box"><h3>Your evidence list (LCMID)</h3><div class="ev">'+''.join(f'<h4>{labs[k]}</h4><ul>'+''.join(f'<li>{x}</li>' for x in ev[k])+'</ul>' for k in 'LCMID' if ev.get(k))+'</div></div>'
        h+='<div class="chk"><h3>✅ Six questions (click an answer)</h3>'+''.join(f'<div class="q" data-a="{a}"><p><b>{j+1}. {q}</b></p>'+''.join(f'<button class="o">{"ABCD"[k]}. {esc(o)}</button>' for k,o in enumerate(opts))+'</div>' for j,(q,opts,a) in enumerate(p['mcq']))+'</div>'
    nxt = f'<a class="btn f" href="{purl(i+1)}" target="_blank">Next: {esc(parts[i+1]["title"])} →</a>' if i+1<len(parts) else f'<a class="btn f" href="{HUB}" target="_blank">Back to the hub</a>'
    h+=f'<div class="btns" style="margin-top:20px">{"<a class=btn href=%s target=_blank>← Back</a>"%(purl(i-1) if i else HUB)}{nxt}</div>'
    return wrap(col,tint,h,p['title'])
def hub_page():
    B=c.BOOK; col,tint='#1B5E63','#E3EFEF'
    h=f'<div class="hero"><div class="plate">{HOUSE(col)}<b>1</b></div><div><h1>{esc(B["title"])}</h1><p>{esc(B["strap"])}</p><p style="font-size:12.5px;opacity:.85">{esc(B["series"])} · explainer</p></div></div>'
    h+=f'<div class="box"><h3>The big idea</h3><p>{B["idea"]}</p></div>'
    h+='<div class="box"><h3>Five questions to answer</h3><ol style="padding-left:20px">'+''.join(f'<li>{esc(q)}</li>' for q in B['questions'])+'</ol></div>'
    h+='<div class="cards">'
    for i,p in enumerate(parts):
        subs=', '.join(f'{s["id"]} {s["title"]}' for s in p.get('subs',[])) or 'Scenario, model paragraph, evidence list and six questions'
        h+=f'<a class="card" href="{purl(i)}" target="_blank" style="border-top-color:{p["colour"]}"><div style="display:flex;gap:10px;align-items:center"><div class="plate" style="background:{p["tint"]}">{HOUSE(p["colour"])}<b style="color:{p["colour"]}">{p["n"]}</b></div><h3 style="color:{p["colour"]}">{esc(p["title"])}</h3></div><p style="margin-top:6px">{esc(p["strap"])}</p><p style="font-size:12.5px;color:#5c6a70;margin-top:4px">{esc(subs)}</p></a>'
    h+='</div>'
    h+=f'<div class="btns" style="margin-top:16px"><a class="btn" href="{OVERVIEW}" target="_blank">⌂ All Shelter explainers</a><a class="btn" href="https://phillippain.github.io/HSC-Legal-Studies/evidence.html" target="_blank" rel="noopener">📚 Evidence Finder</a></div>'
    return wrap(col,tint,h,B['title'])
import os
os.makedirs(OUT,exist_ok=True)
open(f'{OUT}/hub.html','w').write(hub_page())
for i in range(len(parts)): open(f'{OUT}/p{i+1}.html','w').write(part_page(i))
print('slugs:',[slug(p['title']) for p in parts]); print({f:os.path.getsize(f'{OUT}/{f}') for f in sorted(os.listdir(OUT))})
