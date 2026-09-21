# Legal Studies Stage 6

Two sites, one syllabus tree.

| Open | What it is |
|---|---|
| **`index.html`** | The **Question Finder** — every HSC examination question from 2011 to 2025, with NESA's marking criteria |
| **`evidence.html`** | The **Evidence Finder** — the legislation, cases, media, international instruments and reports you have collected, filed against the same syllabus tags, for Preliminary as well as HSC |

Both are single self-contained files. Both read `data/syllabus.json`, so `crime.4.8` means
*post-sentencing considerations* in both, and evidence and questions can be looked up against each
other.

---

## The Question Finder — `index.html`

A past-paper question finder for HSC Legal Studies, built on the same architecture as the
HSC Economics finder. Questions are organised by syllabus content point, by themes and
challenges, and by directive verb and demand band.

Open `index.html`. It is a single self-contained file — no build step needed to use it.
The examination papers and NESA marking guidelines for 2015–2025 sit beside it, so a year link
opens the paper itself and the guidelines are one click from each question. For 2011–2014 the
papers and guidelines live on the Board of Studies archive and the links go there — but their
question text and marking criteria were read from that archive and are held here, so the site
works in full for all fifteen years.

Students who have not used it before should press **How to use this site** in the masthead. The
guide covers the three ways in, how to walk down and back up the three levels of the content tree,
what the counts beside each row mean, and how the worksheet is built. The same guide is linked from
the welcome panel, from the hint under each level of the tree, and from the footer.

## What is in it

Every question from 2011 to 2025, the life of the 2009 syllabus — **426 in all**:

| Section | Topic | Questions |
|---|---|---|
| I | Crime and Human Rights | 300 — 20 a year, with options and NESA's answer key |
| II Part A | Human Rights | 51 short answers — 15 marks a year |
| II Part B | Crime | 15 — one per year, no (a)/(b) alternative |
| III | Family (Option 3) | 30 — fifteen years × parts (a) and (b) |
| III | Shelter (Option 5) | 30 — fifteen years × parts (a) and (b) |

Band criteria are held for **all 126 written questions**, with NESA's sample answers where they
were published and the "answers could include" notes where NESA gave them. They unfold in stages —
criteria first, then the sample answer — so a question can be attempted before the marking is
read. Three gaps are NESA's own rather than this repo's: **2020 published no sample answers at
all**; "answers could include" is a recent practice, rare before 2023 and much fuller from 2024;
and the 2013 guidelines set out their "answers could include" notes without usable bullet
structure, so that year's are deliberately omitted rather than reproduced garbled.

## How questions are tagged

Each question carries a **core** focus — what it is built on, which you cannot answer without —
and **supporting** elements, expected as evidence or context. Tagging runs at two levels, because
the questions do:

- **Section I and Section II Part A** are tagged to a single syllabus **dot point**
  (`crime.5.1` Age of criminal responsibility), because a one- or two-mark question turns on one.
  These were assigned by reading every question; they live in `data/tags-papers.txt`.
- **Extended responses** are tagged to a whole syllabus **section** (`crime.4` Sentencing and
  punishment), because a 15- or 25-mark answer draws on a section rather than a dot point. These
  come from the ●/○ matrices in the 2026 survey documents under `source-documents/`.

Selecting a dot point returns its own questions plus the extended responses tagged to its
section; where a dot point has nothing of its own the count carries an arrow to show the number
is inherited. A theme goes in `core` when the question is built on it.

This is a reading of the questions, not an official NESA mapping.

---

## The Evidence Finder — `evidence.html`

Every piece of evidence you hold, tagged against the syllabus and searchable three ways.

**The record.** One markdown file per piece of evidence in `evidence/`, with a comma-separated
header and a markdown summary. `evidence/README.md` has the field list. The build refuses a tag
that is not in the syllabus and refuses a significance line longer than a sentence.

**Six forms of evidence**, which are the ones outcomes H8 and P8 name: legislation, case law,
international instruments, reports and statistics, media, and documents and non-legal responses.

**Three ways in.**

- **Content** walks course → topic → section → dot point. Choosing a dot point returns its own
  evidence plus anything filed against its whole section, marked as inherited.
- **Themes** lists each topic's themes and challenges, which is how the 25-mark questions are built.
- **Kind** filters by form of evidence, and by the eight **criteria for evaluating effectiveness**
  the syllabus sets out in Law in practice — resource efficiency, accessibility, enforceability,
  responsiveness, protection of individual rights, meeting society's needs, the rule of law, and
  whether justice has been achieved. Those criteria cut across every topic in both courses, so this
  is how you find everything you hold on one line of judgement at once.

**The evidence finder is white.** Its light palette is neutral — white page, white panels separated
by line and shadow rather than by tint, grey `#f4f5f7` for chips, rails and cells — so the topic
colours are the only warmth on the page. The question finder keeps the original cream
(`#f6f3ee`/`#fffdfa`); the two sites no longer share a light surface palette, which is why
`build/template.html` and `build/evidence_template.html` carry their own tokens. Dark mode is
unchanged in both.

**One course at a time.** The switch in the masthead — **Both · Preliminary · HSC** — scopes the
whole page: the syllabus tree, the coverage grid, the search, the counts in the masthead and the
library below the results. The choice is remembered, so a Year 11 class and a Year 12 class each open
the finder where they left it. On **Both**, the grid carries a heading per course with its own
subtotal.

Scoping **does not hide the cross-course evidence**, which is a large part of what the finder is for.
A Crime case tagged to a Preliminary content point still appears under that point while you are in
Preliminary, carrying a dashed **HSC evidence** mark so you can see which course it is really about.
The rule is: a record shows in a course if **any** of its tags belong to that course, and is marked
when **none of its core tags** do. Leaving a course drops a selection that belonged to it, so you
never end up looking at an empty list under the other course's heading.

**The coverage grid is the landing view** — one cell per dot point, darker where you hold more,
dashed where you hold nothing. It is the fastest way to see what a topic is missing before an
assessment.

**Ticking builds an evidence sheet**, printed as title, citation, the one-line significance and the
syllabus tags — the same selection mechanism as the question finder's worksheet builder.

**Adding evidence.** Press **Add evidence** in the masthead: whatever is selected becomes the core
tag, and the dialog emits the whole file, ready to save at the path it names. Or copy the nearest
existing file by hand. Then rebuild.

### The library

`HSC_LS_SSCBWB / Evidence Finder / library` in the shared drive holds the documents themselves —
around 660 cases, articles, reports and decks, the same files the site links to, so what is scanned
is what is published. (`~/Desktop/Evidence Organiser` is where they were gathered and still holds the
videos, which are too big to be worth uploading.) `build/scan_library.py` walks the library and
classifies every file:

- **evidence or teaching resource.** A question survey, a practice question, an essay plan, a slide
  deck and a revision table are how the evidence gets taught, not evidence. They are indexed
  separately so they stay findable without diluting the evidence list.
- **a syllabus tag** from the folder the file sits in, refined by what the filename says and by the
  court its citation names — `ARTA` plus `Refugee` is `hr.3.1`, `FedCFamC` is Family.
- **duplicates.** A `.docx` and a `.pdf` of the same name are *not* duplicates: one is the editable
  source, the other the handout. A second copy in the *same* format is.

The finder shows those files under whatever part of the syllabus they were filed to, below the
written-up evidence, and a link opens the document itself. A record that summarises one of them names
it in a `document:` line, and that file then drops out of the library list — the record supersedes
it. Coarse tags stay where they are honest: a file tagged only to a topic appears at the topic, not
under each of its dot points.

A file the library still holds that a record already covers is recognised by its **medium neutral
citation** and hidden too — the raw judgment beside the case card. The court code can itself contain
digits (`FedCFamC2F`, `NSWCATAD`), so the citation pattern requires whitespace before the number:
without it `[2026] FedCFamC2F 391` truncates to `[2026] FedCFamC2` and matches every FedCFamC2F case
in the folder. That bug hid twenty unrelated judgments before it was caught.

**Tagging by hand.** `data/library-tags.txt` maps a path to a list of tags and overrides whatever the
scanner derived — for files whose name says nothing, like the three *Legal Briefs* journal editions,
which are tagged from each edition's own contents table. The scan reports any line pointing at a file
that is no longer there.

**The coverage grid distinguishes a gap from a lead.** A dashed cell means nothing at all; a dotted,
faintly tinted cell means no record has been written but documents are filed there. Every dot point
now carries at least one record, so no cell is dashed — but coverage is not depth, and the tint still
shows where filed documents are waiting to be written up.

Re-run `scan_library.py` after adding or moving files in the library, then rebuild — or run
`build/ingest.py refresh`, which does both and more. It finds the library by itself (the Drive path
on the Mac, `~/mnt/Evidence Finder/library` in a Cowork session, or `EVIDENCE_LIBRARY=`), and takes
a folder as an argument if you want to point it somewhere else. A scan that finds no files refuses
to write rather than replacing a good index with an empty one (`--empty-ok` overrides that). The
path the page's *fallback* `file://` links are built from is separate — `LIB_LINK_ROOT` — but online
every document opens from its Drive id instead.

### Tidying the folder

`build/tidy_plan.py` proposes changes and writes them to `data/tidy-plan.md` and
`data/tidy-plan.json`; `build/apply_tidy.py --go` carries them out. **Nothing is ever deleted** — a
duplicate is moved to `_duplicates/` with its original path underneath, so every change is
reversible and no delete permission is needed. The `document:` line of any record pointing at a moved
file is rewritten, following the chain if the file it is repointed to is also moving.

Two mistakes the first version of this made, both caught before anything moved and both worth
keeping in mind if the rules are ever changed:

- stripping a trailing digit to catch `… 2.pdf` copies treated **"Slide Set 4" as a copy of "Slide
  Set 3"** and merged eight decks into one. A copy is now only a copy when the file it copies is
  actually there, in the same folder and the same format.
- the keep-rule sorted alphabetically, and `"X 2.pdf"` sorts before `"X.pdf"`, so it proposed
  keeping every copy and discarding every original.

### Preliminary

`data/syllabus.json` carries the **Preliminary** course as well — The legal system (ls.*), The
individual and the law (ind.*) and Law in practice (lip.*), 55 dot points across ten sections, with
each part's themes and challenges. The question finder ignores them: its `ORDER` list names the four
HSC topics, and a full rebuild still produces `index.html` byte-for-byte.

### Colour

The question finder's four HSC topic colours are unchanged. Preliminary needed a fifth, and
**seven categorical hues cannot be separated for colour-vision deficiency inside one lightness
band** — the best seven-colour set that keeps the existing four reaches ΔE 6.6 under deuteranopia,
below the 8.6 the shipped palette already sits at. So colour carries the topic among the HSC four
and the *course* for Preliminary, whose three parts are told apart by their icons instead. The
fifth hue (light `#8b1a7d`, dark `#9b46b4`) passes all five checks against all pairs.

## Adding evidence — drop it in the inbox

New material goes into **`Evidence Finder / inbox`** in the shared drive, from any device: drag a
PDF in from a browser, from email, from a phone. Nothing else is required of whoever drops it.

Filing it is then one Cowork session with the **add-evidence** skill: Claude reads what is waiting,
decides which library folder it belongs in and which syllabus dot points it is about, moves it,
writes an evidence record for it where it deserves one, rebuilds the page and reports what changed.
`build/ingest.py` is what it drives, and it can be driven by hand just as well:

```sh
python3 build/ingest.py status                                  # what is waiting, and where it could go
python3 build/ingest.py file "R v Smith.pdf" "Cases/Crime" --tags crime.3.4
python3 build/ingest.py refresh --commit "Evidence: R v Smith"  # rescan, rebuild, verify, commit
```

Then push (GitHub Desktop → Push origin) and the site has it. Pushing is the one step left by hand,
because the shared drive is inside the school account and the repo credentials are not.

A file **keeps its Drive id when it is moved inside the shared drive**, which is what makes this
work: the inbox is listed every five minutes, so by the time a file is filed its id is already known
and the link on the site is right immediately, without waiting for the nightly re-map.

## Publishing — GitHub Pages for the page, Google Drive for the documents

Google Drive stopped serving HTML as web pages in 2016, so the page itself is published on
**GitHub Pages**. The documents behind it live in the shared drive
`HSC_LS_SSCBWB / Evidence Finder / library` — 665 documents, 1.63 GB, **no videos** and nothing from
`_duplicates/`. Keeping them in Drive keeps them behind the school sign-in: much of the library is
paywalled news, a textbook excerpt and other teachers' material that should not be on the open web.

A page on `github.io` cannot reach a Drive file by path, so every link needs that file's Drive id.
**`build/map-drive-ids.gs`** collects them, and a copy sits in the Drive folder. Set it up once —
script.google.com → open the project → paste the file over what is there → Save → run
`installTriggers`, allowing the permissions it asks for — and from then on it runs itself:

- every **5 minutes** it notes what is in the inbox, into `inbox-links.json` (one folder, a second's
  work, and it writes only when the inbox has changed);
- every **night** it re-maps the whole library into `drive-links.json`, catching anything added,
  renamed or moved by hand. A run that hits Apps Script's 6-minute limit schedules itself to carry
  on a minute later.

`build/ingest.py refresh` folds that map into `data/drive-links.json` in the repo, keeping the ids it
has carried across itself. The `data/` copy is what the build reads (`DRIVE_LINKS=` overrides the
fallback): a file Drive has only just synced can be locked for a while ("Resource deadlock avoided"),
and a copy in the repo also makes the build reproducible without Drive mounted. `mapDriveIds` and
`mapInbox` can still be run by hand; `removeTriggers` turns the automation off.

**`.nojekyll` must stay at the repo root.** Without it GitHub Pages runs every file through
Jekyll, which reads each record's `---` header as YAML front matter. Those headers are deliberately
*not* YAML — a colon inside a title or a significance line is legal here and fatal there — so seven
records were enough to fail the whole deployment, and the live site silently stayed on its last good
build, which predated `evidence.html`. `.nojekyll` tells Pages to serve the files exactly as they
are, which is all this site needs.

Every document link opens `drive.google.com/file/d/<id>/view`. A file missing from the map keeps a
local `file://` link, so a half-finished map degrades one file at a time rather than breaking the
page — and with no map at all, the page works exactly as it always has on this Mac.

**Access.** A Drive link opens for anyone the file is shared with. If students are not members of
the shared drive, share the `library` folder as "anyone at education.nsw.gov.au with the link" or
the links will ask them to request access.

**Videos** stay on the Desktop folder and are not in the library, so they are no longer indexed.
Drag them into `library/` under the same folder names if you want them back: the nightly map picks
them up and their links switch over too.

## Files

```
evidence.html               the evidence finder — open this
evidence/*/*.md             one file per piece of evidence
evidence/README.md          the record format
build/evidence_lib.py       reads and validates the evidence records
build/md.py                 the markdown subset the summaries are written in
build/build_evidence.py     evidence/ + syllabus.json -> evidence.html
build/verify_evidence.py    checks the built evidence.html
build/evidence_template.html  the page, with __DATA__ as the data placeholder
build/check_evidence_page.mjs drives the built page in Playwright, light and dark
build/scan_library.py       the Drive library folder -> data/library.json
build/ingest.py             inbox -> library: file, tag, rebuild, verify, commit
build/map-drive-ids.gs      Apps Script: keeps drive-links.json and inbox-links.json current
build/extract_summaries.py  pulls the text out of the finished case cards and evidence sheets
build/tidy_plan.py          proposes a tidy-up -> data/tidy-plan.md and .json
build/apply_tidy.py         carries the plan out (--go); moves only, never deletes
data/library.json           every document in the folder, classified and tagged
data/library-tags.txt       hand-written tags for files whose name says nothing
data/drive-links.json       library path -> Google Drive file id, for the online links
data/ingest-log.jsonl       every file moved out of the inbox, and when

_superseded/                papers and guidelines kept but no longer linked (git-ignored)

index.html                  the question finder — open this
*.pdf                       examination papers and marking guidelines, 2015-2025
data/syllabus.json          tag taxonomy: topics, themes, sections, dot points, directives
data/items-extended.json    extended responses, with core[]/support[] tag arrays
data/items-papers.json      Section I and Section II Part A, as extracted from the papers
data/items-papers-tagged.json   the same, once merge_papers.py has applied the tags
data/tags-papers.txt        the content-point tag for every Section I and II Part A question
data/guidelines.json        band criteria, sample answers, "answers could include"
data/groups.json            survey element name -> representative tag ID, for the chips
data/archive/               2011-2014 guidelines, read from the Board of Studies archive
build/extract_surveys.py    survey documents -> items-extended.json
build/extract_papers.py     papers -> items-papers.json, plus the answer keys
build/extract_guidelines.py marking guidelines -> guidelines.json
build/merge_papers.py       applies tags-papers.txt to the paper questions
build/build_site.py         everything -> index.html
build/verify_site.py        checks the built index.html
build/template.html         the page, with __DATA__ as the data placeholder
build/expected-shelter-stems.txt   verified Shelter stems, used as a regression check
source-documents/           the three 2026 survey documents the tags come from
source-documents/archive-2011-2014/   2011-2014 question text, read from the archive
```

## Rebuilding

The evidence finder:

```sh
python3 build/ingest.py refresh      # all four of the below, plus the Drive map and a report
python3 build/scan_library.py        # the Drive library folder -> data/library.json
python3 build/build_evidence.py      # evidence/*.md + library -> evidence.html
python3 build/verify_evidence.py     # tags, ids, icons, document paths, self-containment
node build/check_evidence_page.mjs   # optional: drives the page, light and dark
```

The question finder:

```sh
pip install python-docx pdfplumber
python3 build/extract_surveys.py     # survey documents -> extended responses
python3 build/extract_papers.py      # papers -> Section I and Section II Part A
python3 build/extract_guidelines.py  # marking guidelines -> criteria and sample answers
python3 build/merge_papers.py        # applies the content-point tags
python3 build/build_site.py          # rewrites index.html
python3 build/verify_site.py         # checks the result
```

A full rebuild regenerates `index.html` byte-for-byte.

## The checks

Every one of these is an invariant of the examination itself, not of the code, so a failure means
the data is wrong rather than the build.

1. **Survey tallies.** Each survey's core-focus tally is recomputed from the extracted tags and
   compared against the tally printed in that document. **42/42 elements match.**
2. **Shelter stems.** All 30 compared against `build/expected-shelter-stems.txt`, the
   transcription verified against the papers. **30/30 match.**
3. **Tag integrity.** Every question tagged, every tag ID valid, no tag pointing at a question
   that isn't there, no duplicate question ids.
4. **The 15/5 split.** Every year's Section I must come out 15 marks Crime and 5 marks Human
   Rights, as the syllabus specifies. This is the only independent check on a borderline
   Crime-or-Human-Rights question, and it caught three mis-filings: 2011 Q20 (which court
   prosecutes genocide), 2017 Q20 (mandatory sentencing and judicial discretion) and
   2019 Q11 (the ICC and human rights standards).
5. **Paper shape.** Every year: 20 objective-response questions, 15 marks of short answers,
   one Crime extended response, four option alternatives.

## Notes on the sources

**The Shelter survey is a PDF and fights extraction three ways.** Its matrix alternates the year
label between columns 0 and 1, so the reader aligns on the last fourteen columns. Its rotated
column headers come out as reversed text, so column order is asserted from the document's own
column key. And a wrapped question cell spills its continuation lines into the *following* table
rows rather than staying in one cell — reading one row truncates nine of the thirty stems.

**The tag-line stripper** must not end its pattern in `\b`: that cannot match after the `&` of
"Legal & non-legal effectiveness", and the label survived into four stems.

**Option lettering changed.** 2015–2016 use `(A)`, 2017 onward use `A.`. A pattern loose enough
for both also matches a stem opening "A well-known public figure…", which silently emptied 38
stems — the bracket or the full stop has to be required.

**Shared stimulus.** Several papers set one scenario for three or four questions ("Use the
following information to answer Questions 5–8"). Unhandled, the scenario is swallowed by the
previous question's last option. 16 questions carry one, across 2011, 2012, 2014 and 2020.

**Answer booklets** carry barcodes, "Office Use Only" rules and a vertical "Do NOT write in this
area" that extracts one word per line, upside down. The mark value prints in the right margin and
lands inside the stem, sometimes mid-sentence; 2012 glues it on with no space.

**The marks column in the guidelines is vertically centred on its band**, so in plain text the
mark lands in the *middle* of its band's bullets and cannot be used to delimit them. For
2015–2025 the criteria are real tables, so the cells are read directly. For 2011–2014, read
through pdf.js, the marks column is separated by x-position and each bullet assigned to its
nearest mark — which is exactly what a centred mark means. Two further traps there: the criteria
table has to be cut at the y-position of the "Sample answer" / "Answers could include" heading,
or the prose below it is absorbed into the lowest band; and pdf.js emits no space where the PDF
used kerning, so items are joined with a space when the gap between them is real, otherwise
"an outline of how one human right" comes back as "ofhowone".

**2013's text layer drops hyphens** ("selfdetermination", "16yearold", "GovernorGeneral") and
2014 loses the odd space ("Peter,while"). Both are repaired in the saved archive text.

**Three questions** (2024 Q7, 2025 Q12, Q16) are built on a table with no usable text layer. They
are flagged `needsPaper` and the page sends the student to the paper.

**`2025 HSC Exam.pdf`** is a 24-page scan with no text layer. `2025-hsc-legal-studies.pdf` is the
usable copy and is what the page links to.

## The papers at the repo root

Twenty-two of them are linked from the question finder and every link resolves. Of the rest:

- `2025 HSC Exam.pdf` is the 24-page scan with **no text layer**; `2025-hsc-legal-studies.pdf` is the
  usable copy and is what the page links to.
- `HR & Crime Q24 2022 & 2023 HSC.pdf` is a separate 8-page compilation, not a duplicate.
- `2020-hsc-legal-studies-section-II-part-A-extract.pdf` was named `2020-hsc-legal-studies copy.pdf`
  and is **not** a copy — it is a 3-page extract of Section II Part A.
- Four genuine duplicates are in `_superseded/`: the 2022 and 2023 papers re-saved at a different
  compression, and the 2015 paper and guidelines downloaded a second time with a random prefix. Same
  page count, same text, different bytes. Nothing was deleted.

Questions, papers and marking guidelines © NSW Education Standards Authority. Content points and
themes from the Legal Studies Stage 6 Syllabus (Board of Studies NSW, 2009).
