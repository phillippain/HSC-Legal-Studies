#!/usr/bin/env python3
"""Make the font files the Worksheet Maker embeds in its PDFs (run once; the results are in fonts/).

    python3 worksheet-maker/build/fonts.py <folder holding the source fonts>

The PDF maker (pdfmake) needs TrueType files. Each family is cut down to the characters an
Economics worksheet uses (Latin, punctuation, arrows, maths signs, subscripts), so the four
families together stay small. fonts/coverage.json lists the characters each file has; the page
uses it to print any character a family lacks in DejaVu Sans instead of an empty box.

  Exam  Liberation Sans (Arial metrics)   SIL Open Font Licence
  Book  Carlito (Calibri metrics)         SIL Open Font Licence
  Lex   Lexend (for the adapted layout)   SIL Open Font Licence
  Sym   DejaVu Sans (symbols fallback)    Bitstream Vera / public domain licence
"""
import json, sys
from pathlib import Path
from fontTools import subset
from fontTools.ttLib import TTFont

SRC = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
OUT = Path(__file__).resolve().parent.parent / "fonts"
RANGES = [(0x20, 0x7E), (0xA0, 0x17F), (0x370, 0x3FF), (0x2000, 0x206F), (0x2070, 0x209F), (0x20A0, 0x20CF),
          (0x2100, 0x218F), (0x2190, 0x21FF), (0x2200, 0x22FF), (0x2300, 0x23FF), (0x25A0, 0x25FF), (0x2600, 0x26FF), (0x2700, 0x27BF)]
FILES = {
    "Exam-R.ttf": "LiberationSans-Regular.ttf", "Exam-B.ttf": "LiberationSans-Bold.ttf",
    "Exam-I.ttf": "LiberationSans-Italic.ttf", "Exam-BI.ttf": "LiberationSans-BoldItalic.ttf",
    "Book-R.ttf": "Carlito-Regular.ttf", "Book-B.ttf": "Carlito-Bold.ttf", "Book-I.ttf": "Carlito-Italic.ttf", "Book-BI.ttf": "Carlito-BoldItalic.ttf",
    "Lex-R.ttf": "lexend-latin-400-normal.woff2", "Lex-B.ttf": "lexend-latin-700-normal.woff2",
    "Sym-R.ttf": "DejaVuSans.ttf", "Sym-B.ttf": "DejaVuSans-Bold.ttf",
}
unicodes = [c for a, b in RANGES for c in range(a, b + 1)]
SYM = [0x20] + [c for a, b in RANGES[2:] for c in range(a, b + 1)]   # the fallback only needs the symbols
cover = {}
for out, src in FILES.items():
    f = TTFont(SRC / src)
    f.flavor = None
    opts = subset.Options()
    opts.layout_features = ["kern", "liga"]
    opts.name_IDs = ["*"]
    opts.notdef_outline = True
    opts.drop_tables += ["DSIG", "FFTM"]
    opts.hinting = False                       # print does not need hinting, and it halves the size
    s = subset.Subsetter(opts)
    s.populate(unicodes=SYM if out.startswith("Sym") else unicodes)
    s.subset(f)
    f.save(OUT / out)
    cps = sorted(f.getBestCmap())
    runs, start, prev = [], None, None
    for c in cps:
        if start is None:
            start = prev = c
        elif c == prev + 1:
            prev = c
        else:
            runs.append([start, prev]); start = prev = c
    runs.append([start, prev])
    cover[out[:-4]] = runs
    print(f"{out}: {(OUT / out).stat().st_size // 1024} KB, {len(cps)} characters")
(OUT / "coverage.json").write_text(json.dumps(cover, separators=(",", ":")))
