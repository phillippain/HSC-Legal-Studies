#!/usr/bin/env python3
"""Carry out data/tidy-plan.json. Moves only — nothing is deleted.

Every move is checked twice: the source must be there, the destination must not.
A move that fails either check is skipped and reported rather than forced, and the
`document:` line of any evidence record pointing at a moved file is rewritten so the
finder keeps opening the right document.

    python3 build/apply_tidy.py --dry-run     # default
    python3 build/apply_tidy.py --go
"""
import json, os, re, shutil, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
lib = json.load(open(f"{ROOT}/data/library.json"))
LIB = lib["root"]
plan = json.load(open(f"{ROOT}/data/tidy-plan.json"))
GO = "--go" in sys.argv

done, skipped = [], []
for m in plan:
    src, dst = os.path.join(LIB, m["from"]), os.path.join(LIB, m["to"])
    if not os.path.exists(src):
        skipped.append((m["from"], "source is no longer there"))
        continue
    if os.path.exists(dst):
        skipped.append((m["from"], f"destination already exists: {m['to']}"))
        continue
    if not GO:
        done.append(m)
        continue
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    try:
        shutil.move(src, dst)
        done.append(m)
    except Exception as e:
        skipped.append((m["from"], str(e)))

# ------------------------------------------- keep the records pointing right --
# A record that cites a discarded copy is repointed at the copy being kept, not at
# the one on its way to _duplicates/.
moved = {m["from"]: (m.get("keep") or m["to"]) for m in done}
# A discarded copy may point at a file that is itself being filed elsewhere, so
# follow the chain to where the document actually ends up.
for src in list(moved):
    seen, dest = {src}, moved[src]
    while dest in moved and dest not in seen:
        seen.add(dest)
        dest = moved[dest]
    moved[src] = dest
touched = []
for dirpath, _, names in os.walk(f"{ROOT}/evidence"):
    for n in names:
        if not n.endswith(".md"):
            continue
        p = os.path.join(dirpath, n)
        text = open(p, encoding="utf-8").read()
        m = re.search(r"^document:\s*(.+)$", text, re.M)
        if m and m.group(1).strip() in moved:
            new = moved[m.group(1).strip()]
            if GO:
                open(p, "w", encoding="utf-8").write(
                    text[:m.start(1)] + new + text[m.end(1):])
            touched.append((os.path.relpath(p, ROOT), new))

print(("MOVED " if GO else "WOULD MOVE ") + f"{len(done)} files")
for a in ("RENAME", "FILE", "COPY", "ASIDE"):
    n = sum(1 for m in done if m["action"] == a)
    if n:
        print(f"  {a:<8}{n}")
if touched:
    print(("updated " if GO else "would update ") + f"{len(touched)} record document paths")
    for f, new in touched:
        print(f"    {f} -> {new}")
if skipped:
    print(f"skipped {len(skipped)}:")
    for f, why in skipped:
        print(f"    {f}  ({why})")
if not GO:
    print("\ndry run — pass --go to carry it out")
