#!/usr/bin/env python3
"""Stamp each evidence record with when it was added and when it last changed.

    python3 build/stamp_records.py              stamp new and changed records (build_evidence.py does this itself)
    python3 build/stamp_records.py --baseline   one-off: give every record without a stamp its file's
                                                last-modified time as `updated_at`, and remember its content
    python3 build/stamp_records.py --absorb     remember the records as they now stand WITHOUT bumping any
                                                time. Use after a bulk maintenance edit (retagging, tidying)
                                                that should not make hundreds of cards look freshly updated
    python3 build/stamp_records.py --check      report what would be stamped; change nothing

Two header fields are written, both in Sydney time as `YYYY-MM-DD HH:MM`:

    added_at:    when the record was first filed            (new records only)
    updated_at:  when its content last changed             (every record)

The existing `added:` date is left alone — the daily digest reads it.

How a change is noticed: data/stamps.json holds a fingerprint of every record's text, with the two
stamp lines left out. A record whose fingerprint differs from the one on file has been edited, by
whoever and however, so it gets a new `updated_at`. A record with no fingerprint is new, so it gets
`added_at` and `updated_at`. Because the stamp lives in the record, it survives a git checkout,
which resets every file's modified time.
"""
import datetime, hashlib, json, os, re, sys
from zoneinfo import ZoneInfo

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVIDENCE = os.path.join(ROOT, "evidence")
STATE = os.path.join(ROOT, "data", "stamps.json")
SYDNEY = ZoneInfo("Australia/Sydney")
FMT = "%Y-%m-%d %H:%M"
STAMP_LINE = re.compile(r"^(added_at|updated_at):.*\n?", re.M)


def now_sydney():
    return datetime.datetime.now(SYDNEY).strftime(FMT)


def mtime_sydney(path):
    return datetime.datetime.fromtimestamp(os.path.getmtime(path), SYDNEY).strftime(FMT)


def record_paths():
    for dirpath, _, names in os.walk(EVIDENCE):
        for n in sorted(names):
            if n.endswith(".md") and n != "README.md":
                yield os.path.join(dirpath, n)


def fingerprint(raw):
    text = STAMP_LINE.sub("", raw.replace("\r\n", "\n"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def header_split(raw):
    m = re.match(r"(﻿?---[ \t]*\r?\n)(.*?)(\r?\n---[ \t]*(?:\r?\n|\Z))", raw, re.S)
    if not m:
        raise SystemExit(f"{raw[:40]!r}: no `---` header block")
    return m.group(1), m.group(2), raw[m.end(2):]


def with_stamps(raw, stamps):
    """Return raw with the given stamp fields set in its header (existing lines replaced in place)."""
    nl = "\r\n" if "\r\n" in raw else "\n"
    opening, head, rest = header_split(raw)
    lines = head.split(nl)
    for key, val in stamps.items():
        line = f"{key}: {val}"
        idx = next((i for i, l in enumerate(lines) if l.lower().startswith(key + ":")), None)
        if idx is None:
            lines.append(line)
        else:
            lines[idx] = line
    return opening + nl.join(lines) + rest


def field(raw, key):
    m = re.search(rf"^{key}:\s*(.+?)\s*$", raw, re.M)
    return m.group(1) if m else ""


def main(argv):
    baseline, absorb, check = "--baseline" in argv, "--absorb" in argv, "--check" in argv
    state = json.load(open(STATE)) if os.path.exists(STATE) else {}
    now = now_sydney()
    new, changed, based, absorbed = [], [], [], []
    seen = {}

    for path in record_paths():
        rid = os.path.splitext(os.path.basename(path))[0]
        raw = open(path, encoding="utf-8", newline="").read()
        fp = fingerprint(raw)
        seen[rid] = fp
        stamps = {}
        if baseline or (rid in state and not field(raw, "updated_at")):
            # carry the file's last-modified time forward as the best evidence there is
            if not field(raw, "updated_at"):
                stamps["updated_at"] = mtime_sydney(path)
                based.append(rid)
        elif rid not in state and not field(raw, "added_at") and not field(raw, "updated_at"):
            if absorb:
                absorbed.append(rid)
            else:
                stamps = {"added_at": now, "updated_at": now}
                new.append(rid)
        elif rid in state and state[rid] != fp:
            if absorb:
                absorbed.append(rid)
            else:
                stamps = {"updated_at": now}
                changed.append(rid)
        if stamps and not check:
            new_raw = with_stamps(raw, stamps)
            open(path, "w", encoding="utf-8", newline="").write(new_raw)
            seen[rid] = fingerprint(new_raw)

    if not check:
        os.makedirs(os.path.dirname(STATE), exist_ok=True)
        json.dump(dict(sorted(seen.items())), open(STATE, "w"), indent=0)
        open(STATE, "a").write("\n")

    verb = "would stamp" if check else "stamped"
    parts = []
    if based:    parts.append(f"{len(based)} baselined from file time")
    if new:      parts.append(f"{len(new)} new")
    if changed:  parts.append(f"{len(changed)} changed")
    if absorbed: parts.append(f"{len(absorbed)} absorbed without a new time")
    print(f"  stamps:   {verb} " + (", ".join(parts) if parts else "nothing — every record is current"))
    for label, ids in (("new", new), ("changed", changed)):
        for rid in ids[:12]:
            print(f"            {label}: {rid}")
        if len(ids) > 12:
            print(f"            … and {len(ids) - 12} more {label}")


if __name__ == "__main__":
    main(sys.argv[1:])
