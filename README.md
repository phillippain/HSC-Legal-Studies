# HSC Legal Studies Question Finder

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

## Files

```
index.html                  the site — open this
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

Questions, papers and marking guidelines © NSW Education Standards Authority. Content points and
themes from the Legal Studies Stage 6 Syllabus (Board of Studies NSW, 2009).
