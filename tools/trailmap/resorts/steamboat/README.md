# Steamboat: rebuild

Steamboat publishes its 2026-27 trail map as an image only; its interactive map's SVG (resorts-interactive.com map
1800) draws the same artwork's trail lines, names and symbols again, grouped by trail name. The app data is built
from the two, the map's reading (`resort.py`) and the decisions settled on crops (`decisions.py`), by
`tools/trailmap/pdf_resort.py`. Its source, the quirks of its map and how it was checked are in
[docs/trail-map-playbook.md, "Steamboat"](../../../../docs/trail-map-playbook.md#steamboat).

```bash
tools/trailmap/resorts/steamboat/regen.sh            # rebuild src/data/resorts/steamboat/
IMAGES=1 tools/trailmap/resorts/steamboat/regen.sh   # also its map image in public/maps/
FORCE=1 tools/trailmap/resorts/steamboat/regen.sh    # on a source whose SHA-256 differs (a new edition: the playbook, "A new season's map")
```

A person's reviews in `trailReviews.json` are kept; Claude's (`"by": "claude"`) are rebuilt, keeping their timestamps
when nothing changed. Never edit the generated files: change `resort.py` or `decisions.py` and re-run.

| file | what it is |
|---|---|
| `regen.sh` | the whole rebuild: downloads the image and the SVG into `work/steamboat/` (git-ignored), extracts, names every piece, writes `src/data/resorts/steamboat/` byte for byte |
| `prepare.py` | the extraction: the SVG parsed (`vicomap.py parse --detail`), its lines put on the image and routed onto the print's own lines, each group's letters and symbols placed where the print shows them |
| `resort.py` | how this map prints things: the settings `tools/trailmap/pdf_resort.py` reads, the registration (`VICOMAP_AFFINE`) |
| `decisions.py` | what the crops settled: the interactive map's lines that are off the print's (left out) and the print's lines traced instead |
| `report.json` | the trail report: the mtnpowder feed (resort 6, `tools/trailmap/reports/feed_trails.py`) |
| `header.txt` | the comment at the top of `trails.ts`: sources, method, decisions, ratings |
| `checks/ink.py` | each line piece's share on the print's own line ink, worst first (where the interactive map is off the print) |
| `checks/missed.py` | the print's blue and green line pixels no piece, name or symbol covers |
| `checks/editions.py` | where the 2026-27 image differs from the 2025-26 one (skimap.org 36311): changed spots, each a pair of crops |

The checks (not part of the rebuild):

```bash
python3 tools/trailmap/reports/compare.py --resort steamboat                  # the trail list against the report
python3 tools/trailmap/resorts/steamboat/checks/ink.py --cut --share 0.85     # pieces off the print's lines
python3 tools/trailmap/resorts/steamboat/checks/missed.py                     # lines no piece covers
python3 tools/trailmap/overlay_audit.py --resort steamboat --out work/steamboat/audit
curl -sSfL -o work/steamboat/skimap/36311.bin https://skimap.org/skimaps/view/36311   # for editions.py
python3 -I tools/trailmap/resorts/steamboat/checks/editions.py
```

The report: the mtnpowder feed, with the bearer token from the site's widget config:

```bash
curl -sS -o work/steamboat/report/cfg.json https://v4.mtnfeed.com/resorts/steamboat.json
TOKEN=$(python3 -c "import json; print(json.load(open('work/steamboat/report/cfg.json'))['bearerToken'])")
curl -sS -o work/steamboat/report/feed.json "https://mtnpowder.com/feed/v3.json?bearer_token=$TOKEN&resortId%5B%5D=6"
python3 -I tools/trailmap/reports/feed_trails.py work/steamboat/report/feed.json --source "..." \
  --out tools/trailmap/resorts/steamboat/report.json
```
