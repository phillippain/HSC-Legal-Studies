# Legal Studies Worksheet Maker

Builds printable Legal Studies worksheets as PDFs, with a matching answer copy, for three courses:
**2009 HSC** (Crime, Human Rights, Family, Shelter), **2025 Year 11** (the four focus areas) and **2025 Year 12**
(The criminal justice system, International relations and human rights, Family law, Housing law).
It is the Legal Studies version of the HSC Economics Worksheet Maker and shares its page, PDF maker and fonts.
First built 28 November 2026.

- **Page:** `index.html` (built from `template.html`; do not edit `index.html` by hand). It loads `data.json`,
  the PDF maker in `lib/` and the fonts in `fonts/` from this folder.
- **Published at:** `/worksheet-maker/` on the GitHub Pages site, once pushed.
- **For teachers only.** It is linked from the staff Tools home page (`Tools/_home/home.html`, group
  *HSC Legal Studies*) and from nowhere else: not the **Other tools** menu (`build/build_sitemenu.py`), not the
  Google Site, not What's New, not the Question Finder. The page asks search engines not to list it (`noindex`)
  and has no site menu. **Anyone who has the address can still open it**, because GitHub Pages has no sign-in:
  do not post the address where students will see it. After editing `home.html`, run
  `Tools/_home/Lock home page.command` to rebuild the locked staff home page.

## The three courses

| Switch | What you tick | Where questions come from |
|---|---|---|
| **2009 HSC** | Dot points (`crime.2.5`), or themes and challenges (`crime.t.discretion`) | Past HSC 2011 to 2025, the HSC bank, the Evidence Finder, the Crime Glossary and the Crime practice multiple choice |
| **2025 Year 11** | Sections (`inv.3`, `dis.1`, `chg.5`, `exp.2`) | Only material tagged to Year 11: the Year 11 bank and the Evidence Finder's Year 11 records. Past HSC questions are an optional extra (step 3), through the crosswalk |
| **2025 Year 12** | Sections (`cj.3`, `ir.4`, `fl.2`, `hl.5`) | `bank/y12-2025.txt` directly; everything else through the crosswalk from the 2009 course |

**The 2025 Year 12 structure and the crosswalk** are in `syllabus25.json`. The content was read from the NSW
Curriculum website on 28 November 2026. NESA does not number the content, so the codes are this site's own.
Only the two options the class studies are held. The crosswalk maps each 2009 section (or a dot point, where it
differs from its section) to the 2025 sections it is closest to, including Year 11 where content has moved
(the elements of crime, courts, young offenders). **It is a class reading, not a NESA mapping: check it.**
Things to know:

- Young offenders (`crime.5`) maps to Year 11 *Experiences with the law*, not to Year 12.
- International crime (`crime.6.1`) maps to nothing; `crime.6.2` maps to `ir.3` (international courts).
- The 2028 HSC examination may not look like the 2011 to 2025 papers.

## The 17 question types

| Group | Types | Where they come from |
|---|---|---|
| HSC exam formats | Multiple choice, short answer, source-based, extended response | Past papers (Question Finder), the bank, Evidence Finder records |
| Legal Studies tasks | Scenario application, match the evidence, LCMID evidence sort, TEEACL paragraph | The bank; made fresh from the Evidence Finder; TEEACL tasks are also made from any essay question, with suggested evidence on the answer copy |
| Knowledge checks | Match terms, fill the gaps, define, true or false | Made fresh from the Crime Glossary and the bank's key terms and statements |
| Thinking tasks | Put in order, cause and effect chain, sort and classify, compare, spot the mistake | The bank |

A source-based question on an Evidence Finder record prints the record's summary and three standard questions
(outline, explain, assess). Edit them on the card to suit the source.

## Building

```
python3 worksheet-maker/build.py            # write data.json, index.html, review.html and review-data.json
python3 worksheet-maker/build.py --check    # change nothing; fail if any of them is out of date
python3 worksheet-maker/build.py --report   # also list how many questions each section has
```

Rebuild after the Question Finder (`index.html`), `data/syllabus.json`, the evidence records, the Crime
Glossary, the Crime practice questions, `syllabus25.json` or the bank change. **Evidence filed after a build does
not appear until the next build** (add the build to the evidence filing routine if you want it kept current).

The build stops with a message if a bank question is malformed, a tag is unknown or the crosswalk names a code
that does not exist.

## The bank

`bank/*.txt` holds the questions, statements and key terms written for this tool; `bank/README.md` explains the
format. Every one shows **not yet reviewed** until it is approved on the **Question review** page of the staff
Tools site (`phillippain.github.io/Tools/question-review/?bank=legal`). That page saves decisions to
`bank/reviews.json` with a GitHub token for this repository; this page reads the file when it opens. Approved
questions lose the label; flagged and removed ones are left out of new worksheets.

## Writing new questions with Claude

The same panel as the Economics page: **More like my worksheet**, a set of one type (twelve types), and on each
card **Look-alike by Claude** and **Simpler wording**. A teacher sets it up once per computer with their own
Anthropic API key. The key is stored under the same browser key as the Economics Worksheet Maker
(`econ-worksheet-maker-v1:claude-key`), so a computer set up for one is set up for both. Without a key the
panel only offers the set-up. Claude's questions are marked **check before printing** and stay in the worksheet,
not in the bank. The prompts tell Claude to cite only law it is sure of, to label made-up sources and to keep
scenarios hypothetical.

## Other details

- Saved worksheets: `localStorage`, key `legal-worksheet-maker-v1:saved`.
- **Add my Question Finder ticks** reads `hsc-ls-done` when the Question Finder was opened at its own address
  in the same browser. `?qf=crime2019Q7,family2016Q27(a)` adds those questions.
- Three multiple-choice questions flagged `needsPaper` are left out (2024 Q7, 2025 Q12, Q16).
- `?embed=1`, `?theme=light|dark` work as in Economics.
- How this was ported: `template.html` began as a copy of `HSC-Economics/worksheet-maker/template.html`.
  The calculation and diagram types were taken out of the menus (their code is still in the file, unused).
