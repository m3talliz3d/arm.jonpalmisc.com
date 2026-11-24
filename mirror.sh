#!/usr/bin/env bash
# Build a complete local mirror of arm.jonpalmisc.com (only works while the site is online).
set -uo pipefail
cd "$(dirname "$0")"

SITE="https://arm.jonpalmisc.com/"
DIR="arm.jonpalmisc.com"
WGET_OPTS=(--wait=0.3 --random-wait -e robots=off -U "Mozilla/5.0")

echo "==> 1/4 Crawling $SITE"
wget --mirror --convert-links --adjust-extension --page-requisites --no-parent \
     "${WGET_OPTS[@]}" "$SITE" 2>&1 | tee crawl.log

echo "==> 2/4 Finding pages in the site's search index that no page links to"
python3 pagefind_diff.py "$DIR"

if [ -s missing.txt ]; then
  echo "==> 3/4 Fetching $(wc -l < missing.txt) unlinked pages"
  wget -x -E -k -p "${WGET_OPTS[@]}" -i missing.txt 2>&1 | tee -a crawl.log
else
  echo "==> 3/4 No unlinked pages to fetch"
fi

echo "==> 4/4 Rewriting leftover absolute links and checking the mirror"
grep -rlZ --include='*.html' 'https://arm.jonpalmisc.com/' "$DIR" \
  | xargs -0 -r sed -i 's#https://arm\.jonpalmisc\.com/#/#g'
python3 check_mirror.py "$DIR"

echo "Done. Expect ~4276 pages in search after: docker compose up -d --build"