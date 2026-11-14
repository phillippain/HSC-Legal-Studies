#!/usr/bin/env python3
"""Build data/whats-new.json, the feed behind the What's New box on the Google Site.

    python3 build/build_whatsnew.py            rebuild the feed
    python3 build/build_whatsnew.py add "Crime 6 explainer pages added" [--date YYYY-MM-DD] [--link URL]
                                               append one site change to data/site-changes.json, then rebuild
    python3 build/build_whatsnew.py status     show what the feed currently holds

Two sources are merged, newest first:
  1. AUTOMATIC  evidence records (evidence/**/*.md): every record's `added:` date within the last
     WINDOW_DAYS becomes a line per day ("3 new evidence items: ..." linking to the Evidence Finder).
     `ingest.py refresh` calls this script, so filing a document updates the feed with no extra step.
  2. LOGGED     data/site-changes.json: changes to the Google Site itself (new pages, slides, booklets,
     tools), which the repo cannot see. Claude appends a line whenever it builds or changes pages;
     `add` does the same by hand. An entry with "hold": true is ignored until the flag is removed
     (use it for pages built but not yet published).

The Home and What's New archive embeds fetch the published file at view time:
    https://phillippain.github.io/HSC-Legal-Studies/data/whats-new.json
so the box updates as soon as the repo is pushed; no one edits the Google Site.
"""
import datetime, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))
CHANGES = os.path.join(ROOT, "data", "site-changes.json")
OUT = os.path.join(ROOT, "data", "whats-new.json")
SITE = "https://phillippain.github.io/HSC-Legal-Studies/"
WINDOW_DAYS = 21      # how far back automatic evidence lines reach
KEEP = 60             # entries kept in the feed (the Home box shows the newest few)
SHOW_NAMES = 3        # evidence names listed in a day's line


def evidence_lines():
    from evidence_lib import load_records
    recs, _ = load_records()
    cutoff = (datetime.date.today() - datetime.timedelta(days=WINDOW_DAYS)).isoformat()
    by_day = {}
    for r in recs:
        d = (r.get("added") or "")[:10]
        if len(d) == 10 and d >= cutoff:
            by_day.setdefault(d, []).append(r)
    out = []
    for d, rs in by_day.items():
        rs.sort(key=lambda r: r["short"])
        names = ", ".join(r["short"] for r in rs[:SHOW_NAMES])
        more = len(rs) - SHOW_NAMES
        if more > 0:
            names += f" and {more} more"
        n = len(rs)
        text = f"{n} new evidence item{'s' if n != 1 else ''} in the Evidence Finder: {names}."
        link = SITE + "evidence.html" + (f"#ev-{rs[0]['id']}" if n == 1 else "")
        out.append({"date": d, "text": text, "link": link, "kind": "evidence", "auto": True})
    return out


def logged_lines():
    if not os.path.exists(CHANGES):
        return []
    items = json.load(open(CHANGES, encoding="utf-8"))
    return [dict(i, kind=i.get("kind", "site")) for i in items if not i.get("hold")]


def build():
    entries = logged_lines() + evidence_lines()
    today = datetime.date.today().isoformat()
    entries = [e for e in entries if e["date"] <= today]
    entries.sort(key=lambda e: (e["date"], e.get("auto", False) is False), reverse=True)
    entries = [{k: v for k, v in e.items() if k not in ("hold", "auto")} for e in entries[:KEEP]]
    feed = {"updated": entries[0]["date"] if entries else today,
            "built": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "entries": entries}
    json.dump(feed, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"whats-new.json: {len(entries)} entries, newest {feed['updated']}")
    return feed


def add(text, date=None, link=None):
    items = json.load(open(CHANGES, encoding="utf-8")) if os.path.exists(CHANGES) else []
    e = {"date": date or datetime.date.today().isoformat(), "text": text}
    if link:
        e["link"] = link
    items.append(e)
    items.sort(key=lambda i: i["date"], reverse=True)
    json.dump(items, open(CHANGES, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    build()


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "add":
        date = a[a.index("--date") + 1] if "--date" in a else None
        link = a[a.index("--link") + 1] if "--link" in a else None
        add(a[1], date, link)
    elif a and a[0] == "status":
        f = json.load(open(OUT))
        print(f["built"], len(f["entries"]), "entries")
        for e in f["entries"][:8]:
            print(" ", e["date"], e["text"][:90])
    else:
        build()
