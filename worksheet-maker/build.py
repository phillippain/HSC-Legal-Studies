#!/usr/bin/env python3
"""Build the Legal Studies Worksheet Maker: data.json (every question it can put on a worksheet), index.html,
review.html and review-data.json (what the Question review page on the staff Tools site shows).

    python3 worksheet-maker/build.py           # write data.json, index.html, review.html and review-data.json
    python3 worksheet-maker/build.py --check   # change nothing; fail if any of them is out of date
    python3 worksheet-maker/build.py --report  # also print how many questions each section has, by group

Where the questions come from (nothing is copied by hand, so a rebuild picks up every change):
  * Past HSC questions 2011 to 2025, NESA marking criteria and answer keys: index.html (the Question Finder)
  * The syllabus: data/syllabus.json (2009 HSC and 2025 Year 11) and worksheet-maker/syllabus25.json (2025 Year 12
    and the class crosswalk from the 2009 HSC course)
  * Cases, legislation, media, international instruments, documents and reports: evidence/ (the Evidence Finder)
  * Crime key terms: data/glossary.json;  Crime practice multiple choice: data/mcq-crime.json
  * The new practice questions and key terms written for this tool: worksheet-maker/bank/*.txt (see bank/README.md)

Rebuild after any of those change.
"""
import hashlib, json, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(HERE / "build"))
sys.path.insert(0, str(REPO / "build"))
import bank as BANK            # noqa: E402  the bank parser (worksheet-maker/build/bank.py)
import evidence_lib as EVLIB   # noqa: E402  the Evidence Finder's record reader (build/evidence_lib.py)

QF = REPO / "index.html"
SYL = REPO / "data" / "syllabus.json"
SYL25 = HERE / "syllabus25.json"
GLOSS = REPO / "data" / "glossary.json"
MCQ = REPO / "data" / "mcq-crime.json"

CHECK, REPORT = "--check" in sys.argv, "--report" in sys.argv

H09 = [("crime", "crime", "Crime", "#1F3864"), ("humanrights", "hr", "Human Rights", "#0E7490"),
       ("family", "fam", "Family", "#A31545"), ("shelter", "shel", "Shelter", "#1E6B4F")]
Y11 = [("investigating", "inv", "Investigating", "#8b1a7d"), ("disputes", "dis", "Disputes", "#3A3A9E"),
       ("changing", "chg", "Changing", "#A3480C"), ("experiences", "exp", "Experiences", "#5F7D3F")]
PRAC = [("recall", "Recall key terms"), ("describe", "Describe or outline"), ("explain", "Explain"), ("analyse", "Analyse or discuss"),
        ("evaluate", "Evaluate or assess"), ("scenario", "Apply the law to a scenario"), ("stimulus", "Use a source or quote"),
        ("evidence", "Use evidence (LCMID)"), ("themes", "Themes and challenges"), ("compare", "Compare")]
BANDK = {1: "describe", 2: "explain", 3: "analyse", 4: "evaluate", "describe": "describe", "explain": "explain", "analyse": "analyse", "evaluate": "evaluate"}
EVNAME = {"case": "case", "legislation": "legislation", "media": "media report", "international": "international instrument",
          "document": "document", "report": "report"}


def js_object(src, name):
    m = re.search(r"(?:const|let|var)\s+" + name + r"\s*=\s*", src)
    return json.JSONDecoder().raw_decode(src[m.end():])[0]


def clean(s):
    return re.sub(r"\s+", " ", str(s or "")).strip()


def joined(lines):
    out = ""
    for ln in lines or []:
        ln = ln.strip()
        if not ln:
            continue
        out = out[:-1] + ln if out.endswith("-") and not out.endswith(" -") else (out + " " + ln).strip()
    return out


def trees(syl, s25):
    def topic(key, tid, label, color):
        t = syl["topics"][key]
        secs = [{"id": s["id"], "name": s["label"],
                 "points": [{"id": p["id"], "t": p["label"] + (": " + p["detail"] if p.get("detail") else "")} for p in s["points"]]} for s in t["sections"]]
        secs.append({"id": tid + ".t", "name": "Themes and challenges", "themes": True,
                     "points": [{"id": th["id"], "t": th["label"]} for th in t["themes"]]})
        return {"id": tid, "label": label, "name": t["label"], "color": color, "sections": secs}
    h09 = [topic(*x) for x in H09]
    y11 = [topic(*x) for x in Y11]
    y12 = [{"id": t["id"], "label": t["label"], "name": t["name"], "color": t["color"],
            "sections": [{"id": s["id"], "name": s["name"], "points": [{"id": f"{s['id']}.{i}", "t": p} for i, p in enumerate(s["points"], 1)]} for s in t["sections"]]}
           for t in s25["topics"]]
    return {"h09": h09, "y11": y11, "y12": y12}


def expand(codes, secpts, known):
    """A tag on a whole section (crime.4) counts for every dot point in it."""
    out = []
    for c in codes:
        for x in (secpts.get(c) or [c]):
            if x in known and x not in out:
                out.append(x)
    return out


# ---------------------------------------------------------------- past HSC questions (the Question Finder)
def hsc_items(D, secpts, known):
    items = []
    for it in D["items"]:
        if it.get("needsPaper"):
            continue                                   # built on a table the class collection holds no text for
        y, s, lab = it["y"], it["s"], it["l"]
        core = [c for c in it["core"] if c in known or c in secpts]
        k = []
        if BANDK.get(it.get("band")):
            k.append(BANDK[it["band"]])
        if it.get("st") and s == "I":
            k.append("scenario")
        if it.get("quoted") or (it.get("st") and s != "I"):
            k.append("stimulus")
        if any(".t." in c for c in core):
            k.append("themes")
        base = {"id": it["topic"] + str(y) + lab, "src": "hsc", "y": y, "sec": s, "l": lab, "n": it["q"],
                "c": expand(core, secpts, known), "cs": core, "k": k, "m": it["m"]}
        if s == "I":
            if len(it.get("opts") or []) != 4:
                continue
            x = dict(base, f="mc", q=clean(it["t"]), o=[clean(o[1]) for o in it["opts"]])
            if it.get("ans") in ("A", "B", "C", "D"):
                x["key"] = [it["ans"]]
            else:
                x["note"] = clean(it.get("ans") or "")        # 2018 Q9: NESA accepted no best answer
            if it.get("st"):
                x["lead"] = clean(it["st"])
            if not x["k"]:
                x["k"] = ["recall"]
            items.append(x)
            continue
        x = dict(base, f="sa" if s == "II-A" else "er", q=clean(it["t"]))
        if it.get("st"):
            x["lead"] = clean(it["st"])
        if s == "II-A" and it.get("part"):
            x["grp"], x["part"] = f"{y}-{it['q']}", f"({it['part']})"
        cr = D["crit"].get(f"{y}|{s}|{lab}")
        if cr:
            x["crit"] = cr["criteria"]
            if cr.get("sample"):
                x["samp"] = clean(joined(cr["sample"]))
            if cr.get("could"):
                x["could"] = [clean(a) for a in cr["could"] if clean(a)]
        items.append(x)
    return items


# ---------------------------------------------------------------- the Evidence Finder's records
def md_plain(s):
    s = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", s)
    s = re.sub(r"[*_`>#]+", "", s)
    return clean(s)


MONTHS = "January February March April May June July August September October November December".split()


def nice_date(d):
    m = re.match(r"^(\d{4})-(\d{2})(?:-(\d{2}))?$", str(d).strip())
    if not m:
        return str(d).strip()
    return (f"{int(m.group(3))} " if m.group(3) else "") + f"{MONTHS[int(m.group(2)) - 1]} {m.group(1)}"


def evidence_items(recs, known, label):
    items = []
    for r in recs:
        core = [c for c in (r.get("core") or []) if c in known]
        if not core or not r.get("significance"):
            continue
        body = (r.get("body") or "").split("\n## ")[0]
        paras = [md_plain(p) for p in re.split(r"\n\s*\n", body) if md_plain(p)]
        lede = clean(r["significance"])          # the record's one-line summary, then its opening paragraphs
        for p in paras:
            if re.search(r"library copy|the class holds|this record", p, re.I):
                continue
            if len(lede) + len(p) > 700:
                break
            lede = (lede + " " + p).strip()
        typ = r["type"]
        what = {"case": "what the court decided in this case", "legislation": "what this legislation does",
                "international": "what this international instrument provides"}.get(typ, "what this source reports")
        dot = label[core[0]]
        dot = dot.split(":")[0].split(" — ")[0]
        dot = dot if re.match(r"[A-Z][A-Z]|[A-Z][a-z]+'s|Children|Aboriginal|Australia|United|NSW|Customary|Country", dot) else dot[0].lower() + dot[1:]
        qs = [{"q": f"Outline {what}.", "m": 2},
              {"q": f"Explain what this {EVNAME.get(typ, 'source')} shows about {dot}.", "m": 4},
              {"q": f"Assess how effective the law is in this area. Refer to this {EVNAME.get(typ, 'source')} and at least one other piece of evidence.", "m": 6}]
        x = {"id": "ev:" + r["id"], "src": "ev", "f": "stim", "c": core, "k": ["stimulus", "evidence", "explain", "evaluate"],
             "title": clean(r.get("short") or r["title"]), "full": clean(r["title"]), "typ": typ, "by": clean(" · ".join(v for v in (r.get("citation"), r.get("jurisdiction")) if v and typ == "case") or (EVNAME.get(typ, "source").capitalize() + (", " + nice_date(r["date"]) if r.get("date") else ""))),
             "sig": clean(r["significance"]), "lede": lede, "qs": qs, "guide": clean(r["significance"]), "m": 12}
        items.append(x)
    return items


# ---------------------------------------------------------------- Crime key terms and practice multiple choice
def gloss_terms(G, known):
    out = []
    for t in G["terms"]:
        for i, s in enumerate(t.get("senses") or []):
            c = [p for r in s.get("refs") or [] for p in r.get("points") or [] if p in known]
            if s.get("d") and c:
                out.append({"id": t["id"] + (f"-{i}" if i else ""), "term": t["term"], "def": clean(s["d"]), "c": sorted(set(c)), "from": "gloss"})
                break
    return out


def mcq_items(M, recs, secpts, known):
    core = {r["id"]: [c for c in (r.get("core") or []) + (r.get("support") or []) if c in known] for r in recs}
    items = []
    for q in M:
        if not q["src"].startswith("Practice") or len(q["o"]) != 4:
            continue
        sec = f"crime.{q['tp']}"
        c = sorted({p for e in q.get("ev") or [] for p in core.get(e["id"], []) if p.startswith(sec + ".")})
        items.append({"id": "pm:" + q["id"], "src": "auto", "f": "mc", "c": c or list(secpts[sec]), "cs": c or [sec], "k": ["recall"], "m": 1,
                      "q": clean(q["q"]), "o": [clean(o) for o in q["o"]], "key": ["ABCD"[q["a"]]], "e": {"why": clean(q.get("x")), "not": {}}})
    return items


def main():
    D = js_object(QF.read_text(encoding="utf8"), "DATA")
    syl = json.loads(SYL.read_text(encoding="utf8"))
    s25 = json.loads(SYL25.read_text(encoding="utf8"))
    T = trees(syl, s25)
    secpts = {s["id"]: [p["id"] for p in s["points"]] for k in T for t in T[k] for s in t["sections"]}
    label = {p["id"]: p["t"] for k in T for t in T[k] for s in t["sections"] for p in s["points"]}
    known = set(label)
    xw = s25["xwalk"]
    bad = sorted({c for c in xw if c not in known and c not in secpts} | {y for v in xw.values() for y in v if y not in secpts})
    assert not bad, f"syllabus25.json crosswalk: unknown codes {bad}"

    recs = EVLIB.load_records()[0]
    items = hsc_items(D, secpts, known)
    items += evidence_items(recs, known, label)
    items += mcq_items(json.loads(MCQ.read_text(encoding="utf8")), recs, secpts, known)
    gloss = gloss_terms(json.loads(GLOSS.read_text(encoding="utf8")), known)

    bank_items, bank_tf, bank_terms, problems = BANK.load(HERE / "bank", known, secpts)
    assert not problems, "bank problems:\n  " + "\n  ".join(problems)
    files = {x["id"]: x.pop("_f", "") for x in bank_items + bank_tf + bank_terms}
    items += bank_items
    gloss = gloss + bank_terms          # a Crime Glossary term and a Year 11 bank term can share a name: they carry different tags

    ids = [x["id"] for x in items]
    dup = sorted({i for i in ids if ids.count(i) > 1})
    assert not dup, f"duplicate ids: {dup[:10]}"
    for x in items:
        badc = [c for c in x["c"] if c not in known]
        assert not badc, f"{x['id']}: unknown dot points {badc}"

    data = {"built": "", "prac": [{"k": k, "n": n} for k, n in PRAC], "syl": T, "xwalk": [[k, v] for k, v in xw.items()],
            "gloss": gloss, "tf": bank_tf, "calc": [], "dias": {}, "items": items}
    body = json.dumps({k: v for k, v in data.items() if k != "items"}, ensure_ascii=False, separators=(",", ":"))
    lines = ",\n".join(json.dumps(x, ensure_ascii=False, separators=(",", ":")) for x in items)
    digest = hashlib.sha1((body + lines).encode()).hexdigest()[:10]
    data_txt = body[:-1].replace('"built":""', f'"built":"{digest}"') + ',"items":[\n' + lines + "\n]}\n"

    page = (HERE / "template.html").read_text(encoding="utf8").replace("__DATAVER__", digest)
    review = BANK.review_page(bank_items, bank_tf + bank_terms, label)
    rdata = json.dumps(BANK.review_data(bank_items, bank_tf + bank_terms, label, None, files), ensure_ascii=False, separators=(",", ":")) + "\n"

    outs = {HERE / "data.json": data_txt, HERE / "index.html": page, HERE / "review.html": review, HERE / "review-data.json": rdata}
    if CHECK:
        stale = [p.name for p, t in outs.items() if not p.exists() or p.read_text(encoding="utf8") != t]
        print("worksheet-maker is up to date" if not stale else f"worksheet-maker is OUT OF DATE ({', '.join(stale)}): run worksheet-maker/build.py")
        sys.exit(1 if stale else 0)
    for p, t in outs.items():
        p.write_text(t, encoding="utf8")
    by = {}
    for x in items:
        by[x["src"] + "/" + x["f"]] = by.get(x["src"] + "/" + x["f"], 0) + 1
    print(f"Wrote data.json ({len(data_txt)//1024} KB, version {digest}): {len(items)} questions; {len(gloss)} key terms "
          f"({len(bank_terms)} from the bank), {len(bank_tf)} true/false statements.")
    print("  " + ", ".join(f"{k} {v}" for k, v in sorted(by.items())))
    print(f"Wrote index.html ({len(page)//1024} KB), review.html and review-data.json ({len(bank_items)} questions, {len(bank_tf)} statements, {len(bank_terms)} key terms).")
    if REPORT:
        coverage(T, items, gloss, bank_tf, xw, secpts)


GROUPS = {"exam": ("mc", "sa", "stim", "er"), "legal": ("scen", "teeacl"), "think": ("chain", "order", "sort", "compare", "error")}


def coverage(T, items, gloss, tf, xw, secpts):
    sec_of = {p: s for s, ps in secpts.items() for p in ps}

    def secs(c, fw):
        if fw == "h09":
            return [sec_of.get(c)]
        own = sec_of.get(c, "")
        if own.split(".")[0] in ("cj", "ir", "fl", "hl", "inv", "dis", "chg", "exp"):
            return [own]
        return xw.get(c, xw.get(own, []))
    print("\nSection      past HSC   new exam-style  scenario+TEEACL  thinking  evidence  terms  true/false")
    for fw in ("h09", "y11", "y12"):
        print({"h09": "2009 HSC", "y11": "2025 Year 11", "y12": "2025 Year 12 (direct tags and the crosswalk)"}[fw])
        for t in T[fw]:
            for s in t["sections"]:
                def hit(x):
                    if fw == "y11" and x.get("src") != "hsc" and not any(c.split(".")[0] in ("inv", "dis", "chg", "exp") for c in x["c"]):
                        return False
                    return any(s["id"] in secs(c, fw) for c in x["c"])
                n = lambda fm, src=None: sum(1 for x in items if x["f"] in fm and (src is None or x["src"] == src) and hit(x))
                print(f"  {s['id']:<10} {n(GROUPS['exam'], 'hsc'):>6} {n(GROUPS['exam'], 'bank'):>14} {n(GROUPS['legal']):>14} {n(GROUPS['think']):>10}"
                      f" {n(('stim',), 'ev'):>9} {sum(1 for g in gloss if hit(g)):>6} {sum(1 for g in tf if hit(g)):>8}")


if __name__ == "__main__":
    main()
