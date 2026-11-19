#!/usr/bin/env python3
"""Build the Crime MCQ practice tool: data/mcq-crime.json + crime-mcq/index.html."""
import json, re, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from mcq_content import PAST, NEW
R = pathlib.Path(__file__).resolve().parent.parent
items = json.load(open(R/'data/items-papers-tagged.json'))
items = items if isinstance(items, list) else items.get('items', items)
recs = json.load(open(R/'data/records.json'))
short = {k: v['short'] for k, v in recs.items()}
def clean(s): return re.sub(r'\s+',' ',s).strip()
out = []; per = {}
def ev(ids):
    for i in ids: assert i in short, 'unknown evidence id '+i
    return [{'id': i, 't': short[i]} for i in ids]
for (y, q), (t, exp, ids) in PAST.items():
    it = [x for x in items if x['topic']=='crime' and x['s']=='I' and x['y']==y and x['q']==q]
    assert len(it)==1, (y,q)
    it = it[0]; assert len(it['opts'])==4 and it['ans'] in 'ABCD'
    opts = [clean(o[1]) for o in it['opts']]
    for o in opts: assert not re.search(r'EXAMINATION|^\d{4}$', o), (y,q,o)
    n = per.get(t,0)+1; per[t]=n
    out.append({'id': f'p{y}q{q}', 'tp': t, 'src': f'Past HSC {y} Q{q}', 'q': clean(it['t']),
                'o': opts, 'a': 'ABCD'.index(it['ans']), 'x': exp, 'ev': ev(ids)})
for (t, q, c, w1, w2, w3, exp, ids) in NEW:
    n = per.get(t,0)+1; per[t]=n
    out.append({'id': f'n{t}-{n}', 'tp': t, 'src': 'Practice question', 'q': q, 'o': [c,w1,w2,w3], 'a': 0, 'x': exp, 'ev': ev(ids)})
ids_ = [q['id'] for q in out]; assert len(ids_)==len(set(ids_))
for q in out: assert len(set(q['o']))==4, q['id']
out.sort(key=lambda q:(q['tp'], q['src']!='Practice question', q['id']))
json.dump(out, open(R/'data/mcq-crime.json','w'), ensure_ascii=False, indent=1)
tpl = open(R/'crime-mcq/template.html', encoding='utf-8').read()
html = tpl.replace('/*DATA*/[]', json.dumps(out, ensure_ascii=False, separators=(',',':')))
open(R/'crime-mcq/index.html','w', encoding='utf-8').write(html)
print(len(out), 'questions', {t: sum(1 for q in out if q['tp']==t) for t in range(1,7)})
