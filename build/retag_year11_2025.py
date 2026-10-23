#!/usr/bin/env python3
"""Replace the 2009 Preliminary topics in data/syllabus.json with the four 2025 Year 11
focus areas and re-tag every evidence record, library tag and scanner rule that used the
old ls./ind./lip. ids. Run from the repo root. Idempotent: a second run finds nothing to do."""
import json, re, os, sys, glob, collections

ROOT = os.getcwd()
SYL = os.path.join(ROOT, 'data', 'syllabus.json')
syl = json.load(open(SYL, encoding='utf-8'))

T = lambda k: [
    {"id": f"{k}.t.justice", "label": "Law, justice & society", "full": "The relationship between law, justice and society", "colour": "#0F6E6E"},
    {"id": f"{k}.t.values", "label": "Law as a reflection of values", "full": "The development of law as a reflection of society's values", "colour": "#A31545"},
    {"id": f"{k}.t.effectiveness", "label": "Legal & non-legal effectiveness", "full": "The effectiveness of legal and non-legal measures in achieving justice for individuals, groups and society", "colour": "#1F3864"},
]
SC = '#8b1a7d'
def sec(id, label, points):
    return {"id": id, "label": label, "colour": SC, "points": [{"id": f"{id}.{i+1}", "label": p} for i, p in enumerate(points)]}

NEW = collections.OrderedDict()
NEW['investigating'] = {
    "label": "Investigating the law", "part": "Year 11 (2025) Focus area 1", "course": "preliminary", "weight": "40 indicative hours",
    "principalFocus": "Australia's legal framework and how it has evolved: what law is and does, the criteria used to judge it, Aboriginal and Torres Strait Islander Customary Lore, the sources and institutions of Australian law, the Constitution, the global legal system and legal rights.",
    "themes": T('inv'),
    "sections": [
        sec('inv.1', 'Legal foundations', ['The meaning and function of the law', 'Characteristics of effective law', 'Ways to classify the law — binding/non-binding, written/unwritten, public/private, criminal/civil, common/statute, domestic/international', 'Principles of justice — equality, access and fairness', 'The relationship between ethics and the law', 'Principles of procedural fairness — a fair hearing and rules against bias', 'The rule of law and its importance to individuals, groups, government and society', 'Consequences of an absence of law or a misuse of law']),
        sec('inv.2', 'Aboriginal and Torres Strait Islander Customary Lore', ['The significance and diversity of Customary Lore', 'The roles of Elders in maintaining and upholding Customary Lore, including mediation and traditional dispute resolution', 'The interconnectedness of Country, Peoples, Cultural Practices and kinship', 'Responsibilities in caring for Country, including land and water management']),
        sec('inv.3', 'Sources of law', ['The origin and development of common law in Australia', 'The doctrine of precedent and its application', 'Statute law and the steps in the legislative process', 'The role and types of delegated legislation']),
        sec('inv.4', 'Legal institutions', ['The role, jurisdiction and hierarchy of courts in NSW and Australia', "Specialist courts — the Children's Court and the Coroner's Court", 'Features of the adversarial system', 'The role and structure of parliament in NSW and Australia', 'The relationship between courts and parliament']),
        sec('inv.5', 'The constitutional framework', ['The creation and function of the Australian Constitution', 'The division of powers between federal, state and territory governments', 'Reasons for the separation of powers', 'The role of the High Court in interpreting the Constitution', 'Amending the Constitution through referendums']),
        sec('inv.6', 'The global legal system', ['The formation of international law through customary law and instruments', 'State sovereignty and its impact on international and domestic law', "Responsibilities of nation-states under international law, including Australia's obligations", 'The purpose of the United Nations and its participation in international law', 'The purpose of intergovernmental organisations in encouraging cooperation', 'The role of international courts and tribunals in resolving disputes', 'The participation of non-government organisations in international law']),
        sec('inv.7', 'Legal rights', ['The relationship between the rights and responsibilities of individuals', 'Sources of rights — the Constitution, statute law, common law and international law', 'Domestic and international protection of rights', 'Consequences of a breach of rights']),
    ]}
NEW['disputes'] = {
    "label": "Disputes under the law", "part": "Year 11 (2025) Focus area 2", "course": "preliminary", "weight": "25 indicative hours",
    "principalFocus": "How disputes are resolved under criminal, civil and administrative law, each examined through a real case or dispute, and the extent to which the outcomes achieve justice.",
    "themes": T('dis'),
    "sections": [
        sec('dis.1', 'Criminal law', ['The purpose and characteristics of criminal law', 'Elements of a crime — actus reus, mens rea and causation', 'Types of crime — strict liability, summary and indictable, crimes against people and property', 'The burden and standard of proof in criminal law', 'Procedures in NSW criminal courts, including legal representation', 'The role of legal personnel and the jury in a criminal trial', 'Types and aims of punishments', 'Key concepts of justice illustrated through a criminal case']),
        sec('dis.2', 'Civil law', ['The purpose and characteristics of civil law', 'Elements of civil law — breach, causation and loss', 'Types of civil law — torts and contracts', 'The burden and standard of proof in civil law', 'Procedures in NSW tribunals and civil courts, including alternative dispute resolution', 'The role of legal personnel and the jury in a civil trial', 'Types and aims of remedies', 'Key concepts of justice illustrated through a civil case']),
        sec('dis.3', 'Disputes with the state', ['The purpose and characteristics of administrative law', 'Reasons individuals and groups have disputes with the state', 'Addressing disputes through non-government organisations and the media', 'Addressing disputes through government reviews, courts and tribunals', 'The role of the Ombudsman in investigating complaints and providing remedies', 'The purpose of a royal commission', 'Findings and recommendations of royal commissions — Aboriginal Deaths in Custody; Banking, Superannuation and Financial Services', 'Key concepts of justice illustrated through a dispute with the state']),
    ]}
NEW['changing'] = {
    "label": "Changing the law", "part": "Year 11 (2025) Focus area 3", "course": "preliminary", "weight": "25 indicative hours",
    "principalFocus": "The reasons, drivers, processes and outcomes of law reform in NSW and Australia, through the recognition of land rights and native title and one other case study of law reform (this school: the social media minimum age).",
    "themes": T('chg'),
    "sections": [
        sec('chg.1', 'Reasons for change', ['Recognising changing values', 'Maintaining relevance in society', 'Adapting to technological change', 'Upholding international standards', 'Amending existing or outdated laws', 'Addressing the needs of individuals, groups or society']),
        sec('chg.2', 'Drivers of change', ['Ways to influence change — activism, advocacy, public opinion, investigations, findings and recommendations', 'Informal methods — individuals, advocacy groups and the media', 'Formal methods — the legislative process, judicial decisions, royal commissions, law reform commissions and inquiries']),
        sec('chg.3', 'Processes of change', ['Legislative methods — bills, amendments, repeals', 'Executive methods — political will, parliamentary debate, ministerial directions', 'Judicial methods — interpreting statutes, creating precedents, identifying outdated laws']),
        sec('chg.4', 'Outcomes of change', ['Benefits of reform', 'Limitations of reform']),
        sec('chg.5', 'Case study 1: Land rights in NSW and native title', ['Overview of land rights — the role and impact of legislation in NSW', 'Overview of native title — overturning terra nullius and the relationship to land rights', 'Drivers of change to native title — Aboriginal Peoples\' initiatives, policy review', 'Developing law through judicial decisions and legislation — the Mabo and Wik decisions', 'Outcomes of change to native title law — benefits and limitations']),
        sec('chg.6', 'Case study 2: An area of law reform (school selection — the social media minimum age)', ['Overview of the area of law reform', 'Reasons for change to the law', 'Drivers of change', 'Processes of change', 'Outcomes of the change — benefits and limitations']),
    ]}
NEW['experiences'] = {
    "label": "Experiences with the law", "part": "Year 11 (2025) Focus area 4", "course": "preliminary", "weight": "30 indicative hours",
    "principalFocus": "The ways the legal system interacts with young people and with one other group in society, and the extent to which justice is achieved: the nature of the experience, access to justice and the responsiveness of the law.",
    "themes": T('exp'),
    "sections": [
        sec('exp.1', 'Young people: the nature of the experience', ['The need for protection under the law', 'Reasons for encountering the legal system', 'Issues arising from contact with the law — evolving capacity, the age of criminal responsibility and recidivism']),
        sec('exp.2', 'Young people: access to justice', ['Protection under domestic and international law', 'Authorities that advocate for the rights of young people', "Contact with legal processes — police and the Children's Court", 'Alternative approaches to justice — justice reinvestment, diversionary programs and Culturally inclusive processes', 'The role of non-government organisations representing young people']),
        sec('exp.3', 'Young people: responsiveness of the legal system', ['Indicators of success in achieving justice', 'Barriers to achieving justice']),
        sec('exp.4', 'Case study 2 group: the nature of the experience', ['The need for protection under the law', 'Reasons for encountering the legal system', 'Issues arising from contact with the law']),
        sec('exp.5', 'Case study 2 group: access to justice', ['Protection under domestic and international law', 'Authorities that advocate for the rights of the group', 'Contact with legal processes — law enforcement, courts or tribunals, dispute resolution', 'Alternative approaches to justice', 'The role of non-government organisations representing the group']),
        sec('exp.6', 'Case study 2 group: responsiveness of the legal system', ['Indicators of success in achieving justice', 'Barriers to achieving justice']),
    ]}

# ------------------------------------------------------------------ tag map --
MAP = {
    'legalsystem': ['investigating'], 'individual': ['disputes'], 'lawinpractice': ['experiences'],
    'ls.1': ['inv.1'], 'ls.1.1': ['inv.1.1'], 'ls.1.2': ['inv.1.1'], 'ls.1.3': ['inv.1.5'], 'ls.1.4': ['inv.1.2'],
    'ls.1.5': ['inv.1.4'], 'ls.1.6': ['inv.1.6'], 'ls.1.7': ['inv.1.7'], 'ls.1.8': ['inv.1.8'],
    'ls.2': ['inv.3'], 'ls.2.1': ['inv.3.1', 'inv.3.2'], 'ls.2.2': ['inv.4.3'], 'ls.2.3': ['inv.4.1'],
    'ls.2.4': ['inv.3.3', 'inv.4.4'], 'ls.2.5': ['inv.3.4'], 'ls.2.6': ['inv.5.1', 'inv.5.2'], 'ls.2.7': ['inv.5.3'],
    'ls.2.8': ['inv.5.4'], 'ls.2.9': ['inv.2.1'], 'ls.2.10': ['inv.2.1', 'inv.2.2'], 'ls.2.11': ['inv.6.2'],
    'ls.2.12': ['inv.6.1'], 'ls.2.13': ['inv.6.4', 'inv.6.6', 'inv.6.7'], 'ls.2.14': ['inv.6.3', 'inv.7.2'],
    'ls.3': ['inv.1.3'], 'ls.3.1': ['inv.1.3', 'dis.3.1'], 'ls.3.2': ['dis.2.3'], 'ls.3.3': ['dis.1.5', 'dis.2.5'], 'ls.3.4': ['inv.1.3'],
    'ls.4': ['changing'], 'ls.4.1': ['chg.1'], 'ls.4.2': ['chg.2'], 'ls.4.3': ['chg.3'],
    'ls.5': ['chg.5'], 'ls.5.1': ['chg.5.2'], 'ls.5.2': ['chg.5.4'], 'ls.5.3': ['chg.5.4'], 'ls.5.4': ['chg.5.4', 'chg.5.5'], 'ls.5.5': ['chg.6'],
    'ind.1': ['inv.7'], 'ind.1.1': ['inv.7.2', 'inv.7.3'], 'ind.1.2': ['inv.7.1'],
    'ind.2': ['disputes'], 'ind.2.1': ['dis.3.2'], 'ind.2.2': ['dis.2.5'], 'ind.2.3': ['dis.2.5'], 'ind.2.4': ['dis.3.3'],
    'ind.2.5': ['dis.3.4'], 'ind.2.6': ['dis.3.4'], 'ind.2.7': ['dis.3.5', 'dis.3.6'],
    'ind.3': ['chg.6'], 'ind.3.1': ['chg.1.3'], 'ind.3.2': ['chg.1.3', 'chg.6.1'], 'ind.3.3': ['chg.6.5'], 'ind.3.4': ['chg.6'],
    'lip.1': ['exp.4'], 'lip.1.1': ['exp.4'], 'lip.1.2': ['chg.2.1'], 'lip.1.3': ['dis.3.2'], 'lip.1.4': ['dis.1.8', 'dis.2.8'], 'lip.1.5': ['inv.6.2'],
    'lip.2': ['exp.5'], 'lip.2.1': ['exp.5'], 'lip.2.2': ['exp.5.5'], 'lip.2.3': ['exp.6'],
}
# HSC young-offender tags also describe the 2025 Experiences case study on young people.
EXTRA_SUPPORT = {'crime.5.1': ['exp.1.3'], 'crime.5.2': ['exp.2.3'], 'crime.5.3': ['exp.2.3'], 'crime.5.4': ['exp.2.4'], 'crime.5.5': ['exp.2.4'], 'crime.5': ['exp.2']}
THEME = {'need': 'justice', 'ruleoflaw': 'justice', 'institutions': 'justice', 'reflection': 'values', 'influences': 'values',
         'justice': 'justice', 'rights': 'justice', 'balance': 'justice', 'technology': 'values', 'effectiveness': 'effectiveness',
         'reform': 'values', 'responsiveness': 'effectiveness'}
PREFIX = {'inv': 'inv', 'dis': 'dis', 'chg': 'chg', 'exp': 'exp', 'investigating': 'inv', 'disputes': 'dis', 'changing': 'chg', 'experiences': 'exp'}
OLD = ('ls.', 'ind.', 'lip.')
OLD_TOPIC = ('legalsystem', 'individual', 'lawinpractice')

def is_old(t): return t.startswith(OLD) or t in OLD_TOPIC
def valid_ids():
    ids = set()
    for k, t in syl['topics'].items():
        ids.add(k)
        for th in t['themes']: ids.add(th['id'])
        for s in t['sections']:
            ids.add(s['id'])
            for p in s['points']: ids.add(p['id'])
    return ids

# ------------------------------------------------------------ syllabus.json --
changed_syl = False
if any(k in syl['topics'] for k in OLD_TOPIC):
    topics = collections.OrderedDict()
    for k, v in NEW.items(): topics[k] = v
    for k, v in syl['topics'].items():
        if k not in OLD_TOPIC: topics[k] = v
    syl['topics'] = topics
    syl['meta']['syllabus'] = 'Legal Studies: Year 11 per the Legal Studies 11–12 Syllabus (2025, first taught 2027); Year 12 per the Stage 6 Syllabus (2009, last examined 2027)'
    syl['meta']['note'] = syl['meta'].get('note', '') + ' Year 11 tags (inv., dis., chg., exp.) follow the 2025 syllabus; the 2009 Preliminary tags (ls., ind., lip.) were retired on 23 October 2026 and every record was re-tagged.'
    syl['outcomes'] = {k: v for k, v in syl['outcomes'].items() if not k.startswith('P')}
    syl['outcomes'].update({'LST-11-01': 'describes legal principles and judicial processes used in the legal system', 'LST-11-02': 'explains the key features of Australian and international law', 'LST-11-03': 'explains the role, formation and reform of law', 'LST-11-04': 'analyses differing perspectives of individuals, groups and society in influencing the law', 'LST-11-05': 'explains methods to resolve conflict and encourage cooperation between individuals, groups and nation-states', 'LST-11-06': 'analyses legal issues to determine the extent to which the law achieves justice for individuals, groups and society', 'LST-11-07': 'uses and analyses a range of sources to assess the effectiveness of the law in addressing issues', 'LST-11-08': 'uses legal concepts to communicate information and legal reasoning to form a judgement'})
    changed_syl = True
IDS = valid_ids()
for v in MAP.values():
    for t in v: assert t in IDS, t
for v in EXTRA_SUPPORT.values():
    for t in v: assert t in IDS, t

def translate(tags):
    out = []
    for t in tags:
        new = MAP.get(t, [t]) if is_old(t) else [t]
        for n in new:
            if n not in out: out.append(n)
    return out

# ----------------------------------------------------------------- records --
HEAD = re.compile(r'^---\n(.*?)\n---', re.S)
nrec = 0
for f in sorted(glob.glob('evidence/*/*.md')):
    src = open(f, encoding='utf-8').read()
    m = HEAD.match(src)
    head = m.group(1)
    lines = head.split('\n')
    fields = {}
    order = []
    for ln in lines:
        if ':' in ln:
            k, v = ln.split(':', 1); fields[k.strip()] = v.strip(); order.append(k.strip())
    core = [t.strip() for t in fields.get('core', '').split(',') if t.strip()]
    sup = [t.strip() for t in fields.get('support', '').split(',') if t.strip()]
    themes = [t.strip() for t in fields.get('themes', '').split(',') if t.strip()]
    if not any(is_old(t) for t in core + sup + themes) and not any(t in EXTRA_SUPPORT for t in core + sup):
        continue
    ncore = translate(core)
    nsup = [t for t in translate(sup) if t not in ncore]
    for t in core + sup:
        for e in EXTRA_SUPPORT.get(t, []):
            if e not in ncore and e not in nsup: nsup.append(e)
    # themes: old Preliminary themes move to the topic of the record's first new Year 11 tag
    first = next((t for t in ncore + nsup if t.split('.')[0] in PREFIX), None)
    pfx = PREFIX[first.split('.')[0]] if first else None
    nthemes = []
    for t in themes:
        if is_old(t):
            if pfx:
                nt = f"{pfx}.t.{THEME[t.split('.')[-1]]}"
                if nt not in nthemes: nthemes.append(nt)
        elif t not in nthemes:
            nthemes.append(t)
    fields['core'] = ', '.join(ncore); fields['support'] = ', '.join(nsup); fields['themes'] = ', '.join(nthemes)
    if 'support' not in order and nsup: order.insert(order.index('core') + 1, 'support')
    if 'themes' not in order and nthemes: order.insert(order.index('support') + 1 if 'support' in order else order.index('core') + 1, 'themes')
    newhead = '\n'.join(f"{k}: {fields[k]}" for k in order if fields.get(k, '') != '' or k not in ('support', 'themes'))
    open(f, 'w', encoding='utf-8').write(src[:m.start(1)] + newhead + src[m.end(1):])
    nrec += 1

# ------------------------------------------------------------ library tags --
LT = 'data/library-tags.txt'
s = open(LT, encoding='utf-8').read()
def fix_line(ln):
    if ln.startswith('#') or '|' not in ln: return ln
    path, tags = ln.rsplit('|', 1)
    tl = [t.strip() for t in tags.split(',') if t.strip()]
    return path + '| ' + ', '.join(translate(tl))
s2 = '\n'.join(fix_line(l) for l in s.split('\n'))
if s2 != s: open(LT, 'w', encoding='utf-8').write(s2)

# ------------------------------------------------------------- scanner rules --
SL = 'build/scan_library.py'
s = open(SL, encoding='utf-8').read()
s = s.replace('"ls.5.3"', '"chg.5.4"').replace('"ls.3.4"', '"inv.1.3"')
if '"preliminary":' not in s:
    s = s.replace('    "tiktok videos": None,\n}', '    "tiktok videos": None,\n    "preliminary": None,            # Year 11 (2025) — decided per file\n}')
    s = s.replace('    (r"adoption", "fam.1.6"),', '    (r"kmart camera glasses|law reform lag", "chg.6"),\n    (r"adoption", "fam.1.6"),')
open(SL, 'w', encoding='utf-8').write(s)

# --------------------------------------------------------------- build file --
BE = 'build/build_evidence.py'
s = open(BE, encoding='utf-8').read()
s = s.replace('        "legalsystem": 5, "individual": 5, "lawinpractice": 5}', '        "investigating": 5, "disputes": 5, "changing": 5, "experiences": 5}')
s = s.replace('        "shelter": "g-shelter", "legalsystem": "g-columns", "individual": "g-person",\n        "lawinpractice": "g-target"}',
              '        "shelter": "g-shelter", "investigating": "g-columns", "disputes": "g-gavel",\n        "changing": "g-route", "experiences": "g-group"}')
s = s.replace('"note": "Year 11 — the legal system, the individual, law in practice"', '"note": "Year 11 (2025 syllabus) — investigating, disputes, changing, experiences"')
s = s.replace('# hue and its three parts are told apart by their icons', '# hue and its four focus areas are told apart by their icons')
open(BE, 'w', encoding='utf-8').write(s)

# --------------------------------------------------------------- page check --
CK = 'build/check_evidence_page.mjs'
s = open(CK, encoding='utf-8').read()
npoints = sum(len(sec['points']) for k in NEW for sec in NEW[k]['sections'])
s = re.sub(r"prelimCells === \d+, scheme \+ ': Preliminary shows ' \+ prelimCells \+ ' cells, expected \d+'",
           f"prelimCells === {npoints}, scheme + ': Preliminary shows ' + prelimCells + ' cells, expected {npoints}'", s)
s = s.replace('.row[data-id="legalsystem"]', '.row[data-id="investigating"]').replace('ls.2.7', 'inv.5.3')
open(CK, 'w', encoding='utf-8').write(s)

if changed_syl: json.dump(syl, open(SYL, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
print(f'syllabus changed: {changed_syl}; records re-tagged: {nrec}; Year 11 points: {npoints}')
