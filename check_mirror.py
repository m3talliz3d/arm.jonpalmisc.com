#!/usr/bin/env python3
"""Check a wget mirror for broken internal links and links still pointing at the live site."""
import os, sys
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse, unquote

ROOT = sys.argv[1] if len(sys.argv) > 1 else "arm.jonpalmisc.com"
ORIGIN = "https://arm.jonpalmisc.com"

class Links(HTMLParser):
    def __init__(self):
        super().__init__(); self.refs = []
    def handle_starttag(self, tag, attrs):
        for k, v in attrs:
            if k in ("href", "src") and v:
                self.refs.append(v)

def local_path(url_path):
    p = os.path.join(ROOT, unquote(url_path).lstrip("/"))
    if url_path.endswith("/") or os.path.isdir(p):
        return os.path.join(p, "index.html")
    if not os.path.exists(p) and os.path.exists(p + ".html"):
        return p + ".html"
    return p

pages = []
for d, _, files in os.walk(ROOT):
    pages += [os.path.join(d, f) for f in files if f.endswith(".html")]
print(f"HTML pages in mirror: {len(pages)}")

missing, absolute = {}, set()
for page in pages:
    rel = "/" + os.path.relpath(page, ROOT).replace(os.sep, "/")
    parser = Links()
    parser.feed(open(page, encoding="utf-8", errors="ignore").read())
    for ref in parser.refs:
        if ref.startswith(("#", "mailto:", "javascript:", "data:")):
            continue
        u = urlparse(urljoin(ORIGIN + rel, ref))
        if u.netloc and u.netloc != urlparse(ORIGIN).netloc:
            continue                      # external site, ignore
        if ref.startswith(("http://", "https://", "//")):
            absolute.add(ref)             # link still points at the live site
        if not os.path.exists(local_path(u.path)):
            missing.setdefault(u.path, page)

print(f"Broken internal links: {len(missing)}")
for path, page in sorted(missing.items())[:50]:
    print(f"  {path}   (linked from {page})")
print(f"Links still pointing at the live site: {len(absolute)}")
for a in sorted(absolute)[:20]:
    print("  ", a)