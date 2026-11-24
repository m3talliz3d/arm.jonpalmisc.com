# arm.jonpalmisc.com — self-hosted mirror tooling

Scripts and a Docker setup to run your own offline copy of
[Jon's Arm Reference](https://arm.jonpalmisc.com/), a fast, searchable reference
for the AArch64 instruction set and system registers (Armv8-A / Armv9-A).

The original site is being discontinued on **4 December 2026** at Arm's request.
This repository exists so people who relied on it can keep a private copy for
internal use.

> **This repository contains no Arm documentation.** It holds only the tooling
> to mirror the site and serve it locally. The mirrored content is excluded by
> `.gitignore`; please keep it that way. All reference content is © Arm Limited.
> This project is not affiliated with Arm or with the original site's author.

## What you get

- Every page of the original site (4,276 pages: A64 base, FP/SIMD, SVE, SME,
  AArch64 and AArch32 system registers)
- Working full-text search (Pagefind index rebuilt from the mirrored HTML)
- A single nginx container, no external dependencies at runtime

## Repository layout

| File | Purpose |
|---|---|
| `mirror.sh` | Crawls the live site, fetches pages that are only reachable via search, fixes links, verifies the result |
| `pagefind_diff.py` | Reads the live site's search index and lists pages missing from the mirror (`missing.txt`) |
| `check_mirror.py` | Reports broken internal links and links still pointing at the live site |
| `Dockerfile` | Stage 1 rebuilds the Pagefind search index; stage 2 serves the site with nginx |
| `compose.yml` | Builds and runs the container on port 8045 |

## Prebuilt image

- Image: [`metallized/arm.jonpalmisc`](https://hub.docker.com/r/metallized/arm.jonpalmisc/tags)
  (the badge at the top shows the newest tag)
- Source and build tooling: [github.com/m3talliz3d/arm.jonpalmisc.com](https://github.com/m3talliz3d/arm.jonpalmisc.com)

```bash
docker run -d --name arm-ref --restart unless-stopped -p 8045:80 \
  metallized/arm.jonpalmisc:2026-11-24-v1
```

Open `http://<host>:8045`.

## Build your own copy

The crawl only works **while the original site is online**.

Requirements: `wget`, `python3` (standard library only), Docker with Compose.

```bash
git clone https://github.com/m3talliz3d/arm.jonpalmisc.com.git
cd arm.jonpalmisc.com
chmod +x mirror.sh
./mirror.sh
```

`mirror.sh` runs four steps:

1. `wget --mirror` the site (about 3,700 pages are reachable by links).
2. `pagefind_diff.py` reads the original search index and lists the pages that
   no other page links to (about 570).
3. `wget -i missing.txt` fetches those pages.
4. Rewrites any leftover `https://arm.jonpalmisc.com/` links to local ones, then
   runs `check_mirror.py`. You want **0 broken internal links** and
   **0 links pointing at the live site**.

Then build and run:

```bash
docker compose up -d --build
```

Open `http://<host>:8045`.

### Verify the copy is complete

The search index records how many pages it covers. It should match the
original's **4,276**:

```bash
docker compose exec arm-ref grep -o '"page_count":[0-9]*' \
  /usr/share/nginx/html/pagefind/pagefind-entry.json
```

## How it works

- **Crawling.** The site is static HTML, so `wget` can copy it. The search box
  loads its index from `/pagefind/` with JavaScript, so `wget` never finds those
  files, and some pages are only reachable through search.
- **Search.** Instead of copying the original index, the Docker build runs
  `npx pagefind --site .` over the mirrored HTML, which writes a fresh
  `/pagefind/` folder (index plus the Component UI files the pages load).
  Node only exists in the build stage; the final image is plain `nginx:alpine`.
- **Content is baked into the image.** No bind mounts, so the image is
  self-contained and can be saved with `docker save` or pushed to a private
  registry.

## Known differences from the original

- Search ranking may differ slightly: the index is built with a newer Pagefind
  release than the original used.
- The original's Cloudflare analytics script is still referenced by the pages.
  It is harmless; strip it in the Dockerfile if you prefer.
- nginx shows its default 404 page for unknown URLs. The original returned its
  homepage for any unknown path.

## Contributing

Issues and pull requests are welcome for the tooling: crawl reliability, the
verification scripts, the Dockerfile, documentation.

- **Do not commit mirrored content** (`arm.jonpalmisc.com/`), generated files
  (`missing.txt`, `crawl.log`) or image exports. `.gitignore` covers these;
  don't force-add them.
- Scripts should stay dependency-free (bash, `wget`, Python standard library).
- Before opening a PR, run `./mirror.sh` or `python3 check_mirror.py` against
  a local mirror and include the summary lines in the PR description.

## Credits

All credit for the original site goes to Jon ([jonpalmisc.com](https://jonpalmisc.com)).
Instruction and register content © Arm Limited.