"""Google Analytics (GA4) tag for every page hosted on GitHub Pages.

    python3 build/analytics.py            add the tag to any .html file in the repo that lacks it
    python3 build/analytics.py --check    list pages missing the tag (exit 1 if any)

Builders import `inject()` and call it on the page text before writing, so a rebuild keeps the tag.
The tag goes immediately before the first </head>; running it again changes nothing.
"""
import os, sys

TAG_ID = "G-11YGV11ZES"
SNIPPET = (
    f'<!-- Google tag (gtag.js) -->\n'
    f'<script async src="https://www.googletagmanager.com/gtag/js?id={TAG_ID}"></script>\n'
    f'<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}'
    f'gtag("js",new Date());gtag("config","{TAG_ID}");</script>\n'
)


def inject(html):
    """Return html with the tag added before the first </head> (unchanged if present or no head)."""
    if TAG_ID in html:
        return html
    i = html.find("</head>")
    return html if i < 0 else html[:i] + SNIPPET + html[i:]


def repo_pages(root):
    for d, dirs, files in os.walk(root):
        dirs[:] = [x for x in dirs if x not in (".git", "node_modules", "_superseded", "__pycache__", "Claude outputs")]
        for f in files:
            if f.endswith(".html"):
                yield os.path.join(d, f)


if __name__ == "__main__":
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    missing, changed = [], 0
    for p in sorted(repo_pages(root)):
        t = open(p, encoding="utf-8").read()
        if TAG_ID in t:
            continue
        if "--check" in sys.argv:
            missing.append(p); continue
        n = inject(t)
        if n != t:
            open(p, "w", encoding="utf-8").write(n); changed += 1; print("tagged", os.path.relpath(p, root))
    if "--check" in sys.argv:
        for p in missing: print("missing", os.path.relpath(p, root))
        sys.exit(1 if missing else 0)
    print(f"{changed} page(s) tagged")
