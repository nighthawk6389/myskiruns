# Buttermilk: rebuild

Buttermilk's 2025-26 trail map (the "layered" PDF aspensnowmass.com links, drawn like Snowmass's) draws its trail
lines as vectors (blue, black and green strokes, and the green dots of the "least difficult way down") and prints
every name as white text on a pill in its run's colour, with no symbol by any name: the rating is the pill's colour.
The app data is built from the PDF, the map's reading (`resort.py`) and the decisions settled on crops
(`decisions.py`), by `tools/trailmap/pdf_resort.py`. Its source, the quirks of its map and how it was checked are in
[docs/trail-map-playbook.md, "Buttermilk"](../../../../docs/trail-map-playbook.md#buttermilk).

```bash
tools/trailmap/resorts/buttermilk/regen.sh            # rebuild src/data/resorts/buttermilk/
IMAGES=1 tools/trailmap/resorts/buttermilk/regen.sh   # also its map image, public/maps/buttermilk.jpg
FORCE=1 tools/trailmap/resorts/buttermilk/regen.sh    # on a source whose SHA-256 differs (a new edition: the playbook, "A new season's map")
```

A person's reviews in `trailReviews.json` are kept; Claude's (`"by": "claude"`) are rebuilt, keeping their timestamps
when nothing changed. Never edit the generated files: change `resort.py` or `decisions.py` and re-run.

| file | what it is |
|---|---|
| `regen.sh` | the whole rebuild: downloads the PDF into `work/buttermilk/` (git-ignored), extracts, names every piece, writes `src/data/resorts/buttermilk/` byte for byte |
| `prepare.py` | the extraction: the map image, the line pieces (the solid strokes and the green dots), the names with their pills' colours |
| `resort.py` | the map's reading: the areas, the report's names and areas, the names printed in parts, the renames, the parks, and the settings `pdf_resort.py` reads |
| `decisions.py` | what the crops settled: which run each piece is, where one path carries two runs (cut), the lines that are no run |
| `report.json` | the trail report: Aspen Snowmass's grooming feed (`tools/trailmap/reports/feed_trails.py`) |
| `header.txt` | the comment at the top of `trails.ts`: sources, method, decisions, ratings |

The checks (not part of the rebuild):

```bash
python3 tools/trailmap/reports/compare.py --resort buttermilk       # the trail list against the report
python3 tools/trailmap/overlay_audit.py --resort buttermilk --out work/buttermilk/audit
python3 tools/trailmap/grid_crop.py --image work/buttermilk/map.png --box 1600,600,2000,1200 --zoom 1.6 \
  --pieces work/buttermilk/pieces_cut.json --names work/buttermilk/names.json --out spot.png
```

The report: the grooming feed, plain curl (the reports README, "Aspen Snowmass"):

```bash
curl -sS -o work/buttermilk/report/feed.json 'https://www.aspensnowmass.com/AspenSnowmass/GroomingReport/Feed?mountain=Buttermilk'
python3 -I tools/trailmap/reports/feed_trails.py work/buttermilk/report/feed.json --source "..." \
  --out tools/trailmap/resorts/buttermilk/report.json
```
