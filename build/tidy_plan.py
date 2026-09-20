#!/usr/bin/env python3
"""Propose a tidy-up of the Evidence Organiser folder. Proposes only — moves nothing.

One move per file, at most. Four reasons a file moves:

  RENAME  a url-encoded name (`%20`, `%5B`) becomes what it says
  FILE    a loose document in a folder that sorts by topic goes into the right one
  COPY    a second copy of the same file, in the same format, goes to _duplicates/
  ASIDE   a file that is not Legal Studies goes to _not-legal-studies/

A .docx and a .pdf of the same name are NOT duplicates: the .docx is the editable
source and the .pdf is the handout. Nothing is deleted — a duplicate is moved, not
removed, so the tidy-up is reversible and needs no delete permission.
"""
import json, os, re, sys, urllib.parse
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
lib = json.load(open(f"{ROOT}/data/library.json"))
FILES = lib["files"]

# Both spellings a tag can take: the topic key itself ("family") and the prefix its
# sections use ("fam.2.4"). Missing the first left every FedCFamC case unfiled.
TOPIC_OF = {"crime": "Crime", "hr": "Human Rights", "fam": "Family", "shel": "Shelter",
            "humanrights": "Human Rights", "family": "Family", "shelter": "Shelter"}
SORTS_BY_TOPIC = {"Cases", "News Articles"}
OFF = re.compile(r"\d{2}(eco|maths|hsie|geo|comm)\d|economics", re.I)


# Ten files end in ".pdf-Phillip Pain MacBook" — real PDFs with the extension mangled
# by whatever saved them, so the operating system will not open them.
MANGLED = re.compile(r"^(?P<base>.+\.(?:pdf|docx?|pptx?|rtf|xlsx))[-_ ].*$", re.I)


def decoded(name):
    n = urllib.parse.unquote(name)
    m = MANGLED.match(n)
    if m:
        n = m.group("base")
    return re.sub(r"\s{2,}", " ", n).strip()


def topic_dir(tags):
    for t in tags:
        head = t.split(".")[0]
        if head in TOPIC_OF:
            return TOPIC_OF[head]
    return None


def specificity(tags):
    return max((t.count(".") for t in tags), default=-1)


# ---------------------------------------------- which copy of a pair to keep --
# Same name, same format, two places. Keep the one filed most specifically; then
# the shallower path; then the alphabetically first, so the rule is deterministic.
discard = {}

# 1. A marked copy beside the file it copies — "… 2.pdf" next to "….pdf".
for f in FILES:
    if f.get("copyOf"):
        discard[f["path"]] = f["copyOf"]

# 2. The same file in two folders. Keep the copy filed most specifically, then the
#    shallower path, then the alphabetically first — and never a marked copy.
groups = defaultdict(list)
for f in FILES:
    if f["path"] not in discard:
        groups[(f["dupe"], f["ext"])].append(f)
for g in groups.values():
    if len(g) < 2:
        continue
    g.sort(key=lambda f: (-specificity(f["tags"]), f["path"].count("/"), f["path"]))
    for f in g[1:]:
        discard[f["path"]] = g[0]["path"]

# ------------------------------------------------------------------- plan ----
FBY = {f["path"]: f for f in FILES}
plan, kept = [], []
for f in FILES:
    src = f["path"]
    base = os.path.basename(src)
    reasons = []

    if src in discard:
        plan.append({"action": "COPY", "from": src, "to": f"_duplicates/{src}",
                     "keep": discard[src],
                     "why": ("a marked copy of" if FBY[src].get("copyOf")
                             else "same name and format as") + f" {discard[src]}"})
        continue
    if OFF.search(base):
        plan.append({"action": "ASIDE", "from": src, "to": f"_not-legal-studies/{base}",
                     "why": "does not look like Legal Studies"})
        continue

    parts = src.split("/")
    folder, name = os.path.dirname(src), base
    if "%" in base or MANGLED.match(base):
        name = decoded(base)
        if "%" in base:
            reasons.append("url-encoded name")
        if MANGLED.match(base):
            reasons.append("the file extension is mangled, so it will not open")
    if len(parts) == 2 and parts[0] in SORTS_BY_TOPIC:
        sub = topic_dir(f["tags"])
        if sub:
            folder = f"{parts[0]}/{sub}"
            reasons.append(f"loose in {parts[0]}/, tagged {', '.join(f['tags'])}")
        else:
            kept.append((src, "no topic can be read from the name"))
    dest = os.path.join(folder, name)
    if dest != src:
        plan.append({"action": "RENAME" if folder == os.path.dirname(src) else "FILE",
                     "from": src, "to": dest, "why": "; ".join(reasons)})

# A move must not land on an existing file. Where fixing a name would produce one
# that is already there, the file is not a rename but a second copy of it.
existing = {f["path"] for f in FILES}
for m in plan:
    if m["action"] in ("RENAME", "FILE") and m["to"] != m["from"] and m["to"] in existing:
        m["why"] = f"fixing the name gives {m['to']}, which is already there — so this is a copy of it"
        m["action"] = "COPY"
        m["keep"] = m["to"]
        m["to"] = f"_duplicates/{m['from']}"

taken = set()
for m in sorted(plan, key=lambda m: m["from"]):
    if m["to"] in taken:
        m["why"] += "  ⚠ another file already wants this name — left where it is"
        m["action"] = "KEEP"
        kept.append((m["from"], "two files would end up with the same name"))
    taken.add(m["to"])
plan = [m for m in plan if m["action"] != "KEEP"]

json.dump(plan, open(f"{ROOT}/data/tidy-plan.json", "w"), indent=1, ensure_ascii=False)

# ----------------------------------------------------------- readable plan ---
counts = defaultdict(int)
for m in plan:
    counts[m["action"]] += 1
lines = ["# Evidence Organiser — proposed tidy-up", "",
         f"{len(plan)} files would move. **Nothing has been moved.** No file is deleted: duplicates",
         "go to `_duplicates/` with their original path underneath, so every change is reversible.",
         "", "| Change | Files | What it does |", "|---|---|---|",
         f"| Rename | {counts['RENAME']} | `%20` and `%5B` in a filename become the space and bracket they stand for |",
         f"| File | {counts['FILE']} | a loose document in `Cases/` or `News Articles/` moves into its topic subfolder |",
         f"| Duplicate | {counts['COPY']} | a second copy of the same file in the same format moves to `_duplicates/` |",
         f"| Not Legal Studies | {counts['ASIDE']} | moves to `_not-legal-studies/` |", ""]
if kept:
    lines += [f"{len(kept)} loose files stay where they are because no topic can be read from the name:", ""]
    lines += [f"- `{p}`" for p, _ in kept] + [""]
for a, title in (("RENAME", "Renames"), ("FILE", "Filed into a topic folder"),
                 ("COPY", "Duplicates"), ("ASIDE", "Not Legal Studies")):
    rows = [m for m in plan if m["action"] == a]
    if not rows:
        continue
    lines += [f"## {title} ({len(rows)})", ""]
    for m in rows:
        lines.append(f"- `{m['from']}`  \n  → `{m['to']}`" + (f"  \n  _{m['why']}_" if m["why"] else ""))
    lines.append("")
open(f"{ROOT}/data/tidy-plan.md", "w", encoding="utf-8").write("\n".join(lines))

print("Proposed — nothing has been moved")
for a in ("RENAME", "FILE", "COPY", "ASIDE"):
    print(f"  {a:<8}{counts[a]}")
print(f"  stay      {len(kept)} loose files with no readable topic")
warn = [m for m in plan if "⚠" in m["why"]]
print(f"  conflicts {len(warn)}")
for m in warn[:10]:
    print("    " + m["from"] + "  ->  " + m["to"])
print("\nplan written to data/tidy-plan.md and data/tidy-plan.json")
