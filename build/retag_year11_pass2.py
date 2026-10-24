#!/usr/bin/env python3
"""Second Year 11 support-tag pass (24 Oct 2026): HSC Crime and Human Rights tags imply the
matching 2025 Year 11 points; plus targeted re-tags and two mis-tag fixes. Idempotent."""
import glob, re
IMPLY = {  # old/HSC tag -> Year 11 support tags
 'crime.1.1': ['dis.1.1'], 'crime.1.2': ['dis.1.2'], 'crime.1.4': ['dis.1.2'],
 'crime.1.3': ['dis.1.3'], 'crime.1.5': ['dis.1.3'], 'crime.1.6': ['dis.1.3'],
 'crime.3.6': ['dis.1.4'], 'crime.3.1': ['dis.1.5'], 'crime.3.2': ['dis.1.5', 'inv.4.3'], 'crime.3.5': ['dis.1.5'],
 'crime.3.3': ['dis.1.6'], 'crime.3.9': ['dis.1.6'], 'crime.4.2': ['dis.1.7'], 'crime.4.6': ['dis.1.7'],
 'hr.2.2': ['inv.6.4'], 'hr.2.3': ['inv.6.5'], 'hr.2.4': ['inv.6.6'], 'hr.2.5': ['inv.6.7'],
 'hr.2.7': ['inv.6.3', 'inv.7.2'], 'hr.2.8': ['inv.7.2'], 'hr.2.9': ['inv.7.2', 'inv.7.3'], 'hr.2.10': ['inv.7.2', 'inv.7.3'],
 'hr.2.11': ['inv.7.3'], 'hr.2.1': ['inv.6.2'],
}
ADD = {  # record id -> support tags to add
 'metropolitan-lalc-2026': ['chg.5.1'], 'richards-v-south-australia-2026-far-west-coast-sea': ['chg.5.3', 'chg.5.5'],
 'local-court-act-2007': ['chg.1.5'], 'nsw-break-and-enter-and-covert-stalking-reforms-2026': ['chg.1.5'],
 'early-appropriate-guilty-plea-reforms-2018': ['chg.1.5'],
 'online-safety-act-2021-and-social-media-minimum-age': ['chg.6.1', 'chg.6.4'], 'under-16-social-media-ban-enforcement-2026': ['chg.6.5'],
 'digital-duty-of-care-bill-2026': ['chg.6.3', 'chg.6.4'],
 'mhcifpa-2020-s14': ['exp.5.4'], 'bocsar-cjb279-jas-diversion': ['exp.5.4'], 'crpd-2006': ['exp.5.1'],
 'kathleen-folbigg-wrongful-conviction': ['dis.3.8'], 'taser-bugmy-case-study-2014': ['dis.3.8'], 'ombudsman-wrongful-detention-2026': ['dis.3.8'],
 'croc-1989': ['chg.1.4'], 'commonwealth-v-tasmania-1983': ['chg.1.4'], 'aged-care-act-2024': ['chg.1.4'],
 'bocsar-cjb248-youth-koori-court': ['exp.3.1'], 'youth-on-track-snapshot-2020': ['exp.3.1'],
 'roberts-smith-v-fairfax-no41-2023': ['dis.2.6'],
}
REMOVE = {'guide-to-purchasing-your-home-nsw': ['dis.1.3'], 'richards-v-south-australia-2026-far-west-coast-sea': ['chg.6.5']}
HEAD = re.compile(r'^---\n(.*?)\n---', re.S)
n = 0
for f in sorted(glob.glob('evidence/*/*.md')):
    src = open(f, encoding='utf-8').read(); m = HEAD.match(src); h = m.group(1)
    id = f.split('/')[-1][:-3]
    def get(k):
        mm = re.search(r'^%s: (.*)$' % k, h, re.M); return [t.strip() for t in mm.group(1).split(',') if t.strip()] if mm else []
    core, sup = get('core'), get('support')
    new = list(sup)
    for t in core + sup:
        for x in IMPLY.get(t, []):
            if x not in core and x not in new: new.append(x)
    for x in ADD.get(id, []):
        if x not in core and x not in new: new.append(x)
    for x in REMOVE.get(id, []):
        new = [t for t in new if t != x]
    if new == sup: continue
    line = 'support: ' + ', '.join(new)
    if re.search(r'^support: .*$', h, re.M): h2 = re.sub(r'^support: .*$', line, h, flags=re.M)
    else: h2 = re.sub(r'^(core: .*)$', r'\1\n' + line, h, flags=re.M)
    open(f, 'w', encoding='utf-8').write(src[:m.start(1)] + h2 + src[m.end(1):]); n += 1
print('records changed:', n)
