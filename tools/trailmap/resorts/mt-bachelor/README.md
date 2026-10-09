# Mt. Bachelor: rebuild

Mt. Bachelor's app data is built from the resort's 2025-26 trail map PDF (its trail lines as filled outlines, its
names as outlined glyphs), with the map's reading (`resort.py`, `letters.json`) and the decisions settled on crops
(`decisions.py`), by `tools/trailmap/pdf_resort.py`. Its source, the quirks of its map and how it was checked are in
[docs/trail-map-playbook.md, "Mt. Bachelor"](../../../../docs/trail-map-playbook.md#mt-bachelor).

```bash
tools/trailmap/resorts/mt-bachelor/regen.sh            # rebuild src/data/resorts/mt-bachelor/
IMAGES=1 tools/trailmap/resorts/mt-bachelor/regen.sh   # also its map image in public/maps/
FORCE=1 tools/trailmap/resorts/mt-bachelor/regen.sh    # on a source whose SHA-256 differs (a new edition: the playbook, "A new season's map")
```

A person's reviews in `trailReviews.json` are kept; Claude's (`"by": "claude"`) are rebuilt, keeping their timestamps
when nothing changed. Never edit the generated files: change `resort.py` or `decisions.py` and re-run (add a
decision with `python3 tools/trailmap/pdf_resort.py mt-bachelor add "<crop>" <id>=NAME`).

| file | what it is |
|---|---|
| `regen.sh` | the whole rebuild: downloads the PDF into `work/mt-bachelor/` (git-ignored), extracts, names every piece, writes `src/data/resorts/mt-bachelor/` byte for byte |
| `prepare.py` | the extraction: the map image (the page right of the legend panel, 3 px per pt), the line pieces (`tools/trailmap/pdf_outline_lines.py`), the printed names and symbols (`tools/trailmap/pdf_glyphs.py`) |
| `resort.py` | how this map prints things: the settings `tools/trailmap/pdf_resort.py` reads |
| `decisions.py` | what the crops settled, as points on the map, each with the crop that settled it |
| `letters.json` | the glyph shapes read on contact sheets (`tools/trailmap/pdf_glyphs.py`) |
| `report.json` | the trail report: the resort's DOR trail list (`tools/trailmap/reports/feed_trails.py`) |
| `header.txt` | the comment at the top of `trails.ts`: source, method, decisions, ratings |
| `checks/missed.py` | the run-coloured outlines no line piece covers (none now; it found the junction outlines the line tool first read wide) |

The checks (not part of the rebuild):

```bash
python3 tools/trailmap/reports/compare.py --resort mt-bachelor        # the trail list against the report
python3 tools/trailmap/resorts/mt-bachelor/checks/missed.py           # drawn lines no piece covers
python3 tools/trailmap/overlay_audit.py --resort mt-bachelor --out work/mt-bachelor/audit
```

The report: the trail list mtbachelor.com's lift and trail report page loads (plain curl), read by `feed_trails.py`
(its `_source` names the day it was fetched; the list carries every winter run, open or not):

```bash
mkdir -p work/mt-bachelor/src
curl -sSf https://api.mtbachelor.com/api/v1/dor/drupal/trails -o work/mt-bachelor/src/dor_trails.json
python3 -I tools/trailmap/reports/feed_trails.py work/mt-bachelor/src/dor_trails.json \
  --source "Mt. Bachelor's trail report: ... as fetched on <date>" --out tools/trailmap/resorts/mt-bachelor/report.json
```
