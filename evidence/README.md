# The evidence files

One piece of evidence is one markdown file in this folder. The header between the `---` fences is
read by the build; everything after it is the summary, written in ordinary markdown.

Nothing here needs YAML: **list values are comma-separated** and no value needs quoting, although
quotes are stripped if you leave them in out of habit.

```
---
type: case
title: Billings & Clowes (No 2) [2026] FedCFamC2F 1367
short: Billings & Clowes (No 2)
citation: [2026] FedCFamC2F 1367
date: 2026-09-01
jurisdiction: Federal Circuit and Family Court of Australia (Division 2), Judge Murdoch
significance: A change of residence ordered where every option harmed the child.
core: fam.2.2, fam.2.4, fam.3.2
support: fam.2.5, fam.3.4, hr.2.4
themes: fam.t.effectiveness, fam.t.cooperation
criteria: enforceability, accessibility, rights, justice
source: https://...
related: bergsma-hyde-2026
added: 2026-09-19
---

## Held

- ...
```

## The fields

| Field | Required | What it is |
|---|---|---|
| `type` | yes | `legislation`, `case`, `media`, `international`, `report` or `document` — the six forms of evidence, and it decides the folder and the colour |
| `title` | yes | The full name, as you would write it in an answer |
| `short` | | A chip-sized name; defaults to the title |
| `citation` | | The formal citation |
| `date` | | `YYYY`, `YYYY-MM` or `YYYY-MM-DD`; sorts the results |
| `jurisdiction` | | NSW, Commonwealth, International, or the court |
| `significance` | yes | **One sentence**, under 220 characters. The build rejects a paragraph — if it takes a paragraph you have not decided what the evidence is for |
| `core` | yes | Syllabus tags the evidence is *about* |
| `support` | | Syllabus tags it is *useful for* |
| `themes` | | Theme tags (`crime.t.reform`) — these never go in `core` or `support` |
| `criteria` | | Any of `resource`, `accessibility`, `enforceability`, `responsiveness`, `rights`, `society`, `ruleoflaw`, `justice` |
| `source` | | A URL |
| `related` | | Other evidence ids, which become "See also" links |
| `added` | | When you filed it |

The **id** is the filename without `.md`. It must be unique across the whole folder.

Syllabus tags are the ids in `data/syllabus.json` — the same ids the question finder uses, so
`crime.4.8` means the same thing in both sites. The build fails on any tag that is not in the
syllabus, so a typo cannot quietly disappear.

## The summary

A small markdown subset, rendered at build time: `##`/`###` headings, `-` and `1.` lists, tables,
`>` quotes, `**bold**`, `*italic*`, `` `code` `` and `[links](https://…)`. Anything else is passed
through as text.

Write it for the person who has to use the evidence under exam conditions. The summaries that earn
their place tend to have a **Use it for** section and a **Caution** section.

## Adding one

Three ways, all producing the same file:

1. **Drop the document in the inbox.** Put it in `Evidence Finder / inbox` in the shared drive and
   run the **add-evidence** skill in Cowork: it files the document in the library, tags it, writes
   the record and rebuilds the page. `build/ingest.py` is the machinery, and the README at the repo
   root describes it.
2. **By hand.** Copy the nearest existing file and edit it.
3. **Ask Claude.** Paste the article, case or report and ask for it to be filed; the conventions are
   in `claude/evidence-finder-build-spec.md` in the project.

Then:

```sh
python3 build/build_evidence.py     # -> evidence.html
python3 build/verify_evidence.py    # checks the built page
```
