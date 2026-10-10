# Alta: rebuild

Alta Ski Area's 2025-26 trail map (the PDF alta.com's plan-your-trip page links, James Niehues's painting under an
Illustrator vector layer) draws its runs' lines as black, blue and green strokes (solid, dashed traverses, dotted ways
down), prints every name as outlined black glyphs along its run's line and sets the rounded difficulty symbols by the
names. The app data is built from the PDF, the map's reading (`resort.py`, `letters.json`) and the decisions settled on
crops (`decisions.py`), by `tools/trailmap/pdf_resort.py`. Its source, the quirks of its map and how it was checked are
in [docs/trail-map-playbook.md, "Alta"](../../../../docs/trail-map-playbook.md#alta).

```bash
tools/trailmap/resorts/alta/regen.sh            # rebuild src/data/resorts/alta/
IMAGES=1 tools/trailmap/resorts/alta/regen.sh   # also its map image, public/maps/alta.jpg
FORCE=1 tools/trailmap/resorts/alta/regen.sh    # on a source whose SHA-256 differs (a new edition: the playbook, "A new season's map")
```

A person's reviews in `trailReviews.json` are kept; Claude's (`"by": "claude"`) are rebuilt, keeping their timestamps
when nothing changed. Never edit the generated files: change `resort.py` or `decisions.py` and re-run.

| file | what it is |
|---|---|
| `regen.sh` | the whole rebuild: downloads the PDF into `work/alta/` (git-ignored, plain curl), checks its SHA-256, extracts, names every piece, writes `src/data/resorts/alta/` byte for byte |
| `prepare.py` | the extraction: the map image, the line strokes, the glyph names, the rounded symbols |
| `letters.json` | each outlined glyph shape's letter, read once on `pdf_glyphs.py sheet` contact sheets |
| `resort.py` | the map's reading: the report's lifts, names and areas, the names printed in parts, the labels that are no runs, the renames, the settings `pdf_resort.py` reads |
| `decisions.py` | what the crops settled: the unlabelled lines that go on from a run, the links that are none, a stretch traced |
| `report.json` | the trail report: the lift and terrain status page's runs by lift (`status_report.py`, fetched 2026-10-10) |
| `status_report.py` | reads that page's `window.Alta` into `report.json` |
| `header.txt` | the comment at the top of `trails.ts`: sources, method, decisions, ratings |

The checks (not part of the rebuild):

```bash
python3 tools/trailmap/reports/compare.py --resort alta            # the trail list against the report
python3 tools/trailmap/overlay_audit.py --resort alta --out work/alta/audit --per 9 --max 420
python3 tools/archive/northstar/colour_crops.py work/alta work/alta/crops 1.5 piece 163   # pieces in colour
```

The report:

```bash
curl -sS -o work/alta/status.html https://www.alta.com/lift-terrain-status
python3 -I tools/trailmap/resorts/alta/status_report.py work/alta/status.html --source "..." \
  --out tools/trailmap/resorts/alta/report.json
```
