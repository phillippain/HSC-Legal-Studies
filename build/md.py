#!/usr/bin/env python3
"""The small markdown subset the evidence summaries are written in.

Rendered at build time rather than in the browser, so the page carries no parser
and a malformed record fails the build instead of the page.
"""
import html, re

INLINE = [
    (re.compile(r"`([^`]+)`"), lambda m: f"<code>{m.group(1)}</code>"),
    (re.compile(r"\*\*([^*]+)\*\*"), lambda m: f"<strong>{m.group(1)}</strong>"),
    (re.compile(r"(?<![\w*])\*([^*\n]+)\*(?![\w*])"), lambda m: f"<em>{m.group(1)}</em>"),
    (re.compile(r"\[([^\]]+)\]\((https?://[^)\s]+)\)"),
     lambda m: f'<a href="{m.group(2)}" target="_blank" rel="noopener">{m.group(1)}</a>'),
]


def inline(text):
    out = html.escape(text, quote=False)
    for pat, fn in INLINE:
        out = pat.sub(fn, out)
    return out


def _row(line):
    cells = line.strip().strip("|").split("|")
    return [c.strip() for c in cells]


def render(src):
    lines = src.replace("\r\n", "\n").split("\n")
    out, i = [], 0
    while i < len(lines):
        ln = lines[i]
        s = ln.strip()

        if not s:
            i += 1
            continue

        m = re.match(r"^(#{2,4})\s+(.*)$", s)
        if m:
            lvl = len(m.group(1)) + 1          # `##` in a record is an <h3> on the page
            out.append(f"<h{lvl}>{inline(m.group(2))}</h{lvl}>")
            i += 1
            continue

        # table: a header row, a delimiter row of dashes, then body rows
        if s.startswith("|") and i + 1 < len(lines) and re.fullmatch(
                r"\|[\s:|-]+\|", lines[i + 1].strip()):
            head = _row(s)
            i += 2
            body = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                body.append(_row(lines[i].strip()))
                i += 1
            th = "".join(f"<th>{inline(c)}</th>" for c in head)
            tr = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>"
                         for r in body)
            out.append(f"<div class=tw><table><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table></div>")
            continue

        if re.match(r"^[-*]\s+", s) or re.match(r"^\d+[.)]\s+", s):
            ordered = bool(re.match(r"^\d+[.)]\s+", s))
            items = []
            while i < len(lines):
                cur = lines[i].strip()
                m2 = re.match(r"^(?:[-*]|\d+[.)])\s+(.*)$", cur)
                if not m2:
                    # a wrapped continuation line, indented or not
                    if cur and items and not re.match(r"^(#{2,4}\s|\|)", cur):
                        items[-1] += " " + cur
                        i += 1
                        continue
                    break
                items.append(m2.group(1))
                i += 1
            tag = "ol" if ordered else "ul"
            out.append(f"<{tag}>" + "".join(f"<li>{inline(t)}</li>" for t in items) + f"</{tag}>")
            continue

        if s.startswith(">"):
            quote = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                quote.append(lines[i].strip()[1:].strip())
                i += 1
            out.append(f"<blockquote>{inline(' '.join(quote))}</blockquote>")
            continue

        para = []
        while i < len(lines) and lines[i].strip() and not re.match(
                r"^(#{2,4}\s|[-*]\s|\d+[.)]\s|>|\|)", lines[i].strip()):
            para.append(lines[i].strip())
            i += 1
        out.append(f"<p>{inline(' '.join(para))}</p>")
    return "".join(out)
