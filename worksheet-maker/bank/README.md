# The Legal Studies Worksheet Maker's question bank

Plain-text files, one question after another. Edit them in any text editor, then run
`python3 worksheet-maker/build.py`. The build stops and names the file and line if anything is wrong.

| Files | Course |
|---|---|
| `hsc-crime.txt`, `hsc-human-rights.txt`, `hsc-family.txt`, `hsc-shelter.txt` | 2009 HSC (tags such as `crime.2.5`, `hr.2.8`, `fam.2.4`, `shel.3.1`, and themes such as `crime.t.discretion`) |
| `y11-investigating.txt`, `y11-disputes.txt`, `y11-changing.txt`, `y11-experiences.txt` | 2025 Year 11 (tags `inv.`, `dis.`, `chg.`, `exp.`) |
| `y12-2025.txt` | 2025 Year 12, for content that is new or reworded (tags `cj.`, `ir.`, `fl.`, `hl.`; see `../syllabus25.json`) |

The 2009 HSC questions also appear in **2025 Year 12** worksheets through the crosswalk in `../syllabus25.json`.

Every question starts with a heading line, `=== <type> <id>`, followed by details, then the body.
The id must be unique (letters, numbers, dots and hyphens). Lines starting with `#` are comments.
Keep each field on one line.

## Details (all types)

| Line | Meaning |
|---|---|
| `c: crime.2.5 crime.t.balance` | Syllabus tags (required): dot points, themes, or a whole section (`crime.4`, `inv.3`), which counts for every dot point in it |
| `m: 4` | Marks (each type has a sensible default) |
| `lv: 2` | Level: 1 foundation, 2 standard, 3 extension (Band 6) |
| `k: explain scenario` | Skills: recall, describe, explain, analyse, evaluate, scenario, stimulus, evidence, themes, compare |
| `like: crime2019Q7` | Question Finder ids this question is modelled on (used by **Look-alike**) |
| `checked: yes` | The teacher has checked this question (removes "not yet reviewed") |

A file whose first line is `# reviewed` has been checked as a whole. Most reviewing happens on the
**Question review** page (staff Tools site, **Legal Studies** switch), which saves decisions to `reviews.json`
in this folder: `ok` approved, `fix` needs a fix (with a `note`), `out` removed. Each decision holds the
question's fingerprint, so editing a question sends it back for review.

## The body, by type

**Multiple choice** (`mc`)
```
LEAD: an optional short scenario
Q: the stem
A: option
B: option
C: option
D: option
ANS: B
WHY: why B is right
```

**Short answer** (`sa`): one question, or several parts sharing a lead-in.
```
Q: the question                    or   LEAD: a sentence that sets up the parts
PTS:                                    PART (a) 2: the question
- a marking point (1)                   PTS:
ANS: optional model answer              - ...
```

**Scenario application** (`scen`): `LEAD:` holds the facts (required), then `PART (a) 2: ...` questions as above.

**Source-based** (`stim`): `TITLE:`, `BY:` (where the source is from; a made-up source must say
"Constructed source for practice"), `TEXT:` (the source), an optional `TABLE:`, then `PART`s.

**Extended response** (`er`): `Q:`, then `PTS:` (what a top-band response includes) and `PLAN:` (paragraph ideas).
Set `m: 15` for Crime, `m: 25` for an option.

**TEEACL paragraph** (`teeacl`): `Q:` (the essay question), `PTS:` (what a strong paragraph includes) and,
optionally, `ANS:` (a model paragraph).

**Put in order** (`order`): `TITLE:`, optional `LEAD:`, the steps as `- ` lines **in the correct order** (the page
shuffles them), optional `NOTE:` printed on the answer copy.

**Cause and effect chain** (`chain`)
```
TITLE: short title
TRIGGER: the event
- what happens next => why
```

**Sort and classify** (`sort`): `Q:`, `CATS: Heading 1 | Heading 2`, then `- an item => Heading 1`.

**Compare** (`compare`): `Q:`, `COLS: Thing 1 | Thing 2`, then `- Row heading => cell | cell`.
Start a cell with `!` to print it on the student copy as a hint.

**Spot the mistake** (`error`): `Q:` and `TEXT:` a paragraph in which each mistake is written
`[[the mistaken words => the correct words]]`.

**True or false statements** (`tf`): not a question on its own; the page draws 6 to 8 statements for the
chosen content.
```
- T: a true statement => optional reason
- F: a false statement => the corrected statement
```

**Key terms** (`terms`): feed Match terms, Fill the gaps, Define and key-term multiple choice.
The Crime terms come from the Crime Glossary (`data/glossary.json`); the bank holds the other topics.
```
- Term => definition
```

## House rules

Australian spelling; NESA key verbs with marks to suit. Name legislation with its year and jurisdiction and
cases with their year. Cite only law, cases and statistics that are certain; a made-up source or figure must be
labelled as constructed. Scenarios use invented people. Aboriginal and Torres Strait Islander Peoples;
a person with disability; "the accused" before conviction. No dashes used as punctuation in student text.
