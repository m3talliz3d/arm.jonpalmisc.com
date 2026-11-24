#!/usr/bin/env python3
"""List pages in the live site's Pagefind index that are missing from the local mirror."""
import gzip, json, os, re, sys, urllib.request
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import unquote

ORIGIN = "https://arm.jonpalmisc.com"
ROOT = sys.argv[1] if len(sys.argv) > 1 else "arm.jonpalmisc.com"
UA = {"User-Agent": "Mozilla/5.0"}          # Cloudflare blocks Python's default UA

def get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30).read()

def unpack(raw):
    if raw[:2] != b"\x1f\x8b":
        return None                          # not a Pagefind file (homepage fallback)
    data = gzip.decompress(raw)
    return data[len(b"pagefind_dcd"):] if data.startswith(b"pagefind_dcd") else data

entry = json.loads(get(f"{ORIGIN}/pagefind/pagefind-entry.json"))
lang = next(iter(entry["languages"].values()))
print(f"Original index: Pagefind {entry['version']}, {lang['page_count']} pages")

meta = unpack(get(f"{ORIGIN}/pagefind/pagefind.{lang['hash']}.pf_meta"))
prefix = lang["hash"].split("_")[0]
hashes = sorted({h.decode() for h in re.findall(rb"%s_[0-9a-f]{6,}" % prefix.encode(), meta)})
print(f"Candidate fragment hashes: {len(hashes)}")

def fragment_url(h):
    try:
        body = unpack(get(f"{ORIGIN}/pagefind/fragment/{h}.pf_fragment"))
        return json.loads(body)["url"] if body else None
    except Exception:
        return None

with ThreadPoolExecutor(max_workers=4) as pool:
    urls = sorted({u for u in pool.map(fragment_url, hashes) if u})
print(f"Page URLs recovered from original index: {len(urls)}")

def have(path):
    p = os.path.join(ROOT, unquote(path).lstrip("/"))
    if path.endswith("/") or os.path.isdir(p):
        p = os.path.join(p, "index.html")
    return os.path.exists(p) or os.path.exists(p + ".html")

missing = [ORIGIN + u for u in urls if not have(u)]
with open("missing.txt", "w") as f:
    f.write("\n".join(missing) + ("\n" if missing else ""))
print(f"Missing from mirror: {len(missing)}  -> missing.txt")
for u in missing[:15]:
    print("  ", u)