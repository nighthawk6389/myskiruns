# Snowbasin: rebuild

Snowbasin's 2025-26 trail map (the PDF snowbasin.com's trail-maps page links, James Niehues's painting under vector
lines) draws its trail lines as black, blue and green strokes (four as filled outlines), prints every name as text in
its run's colour along its line, and sets the difficulty symbols on the lines. The app data is built from the PDF, the
map's reading (`resort.py`) and the decisions settled on crops (`decisions.py`), by `tools/trailmap/pdf_resort.py`.
Its source, the quirks of its map and how it was checked are in
[docs/trail-map-playbook.md, "Snowbasin"](../../../../docs/trail-map-playbook.md#snowbasin).

```bash
tools/trailmap/resorts/snowbasin/regen.sh            # rebuild src/data/resorts/snowbasin/
IMAGES=1 tools/trailmap/resorts/snowbasin/regen.sh   # also its map image, public/maps/snowbasin.jpg
FORCE=1 tools/trailmap/resorts/snowbasin/regen.sh    # on a source whose SHA-256 differs (a new edition: the playbook, "A new season's map")
```

A person's reviews in `trailReviews.json` are kept; Claude's (`"by": "claude"`) are rebuilt, keeping their timestamps
when nothing changed. Never edit the generated files: change `resort.py` or `decisions.py` and re-run.

| file | what it is |
|---|---|
| `regen.sh` | the whole rebuild: downloads the PDF into `work/snowbasin/` (git-ignored), extracts, names every piece, writes `src/data/resorts/snowbasin/` byte for byte |
| `prepare.py` | the extraction: the map image, the line pieces (the strokes, and the centre lines of the four drawn as filled outlines), the names with their colours, the symbols |
| `resort.py` | the map's reading: the areas, the report's names and areas, the names printed in parts, the renames, the symbols out of reach, the parks, and the settings `pdf_resort.py` reads |
| `decisions.py` | what the crops settled: which run each piece is, where one path carries two runs (cut), the lines that are no run |
| `report.json` | the trail report: the mountain report page's tables, as Common Crawl captured them in January 2026 (`mountain_report.py`) |
| `mountain_report.py` | reads that page's tables into `report.json` |
| `header.txt` | the comment at the top of `trails.ts`: sources, method, decisions, ratings |

The checks (not part of the rebuild):

```bash
python3 tools/trailmap/reports/compare.py --resort snowbasin       # the trail list against the report
python3 tools/trailmap/overlay_audit.py --resort snowbasin --out work/snowbasin/audit --per 6 --max 560
python3 tools/archive/snowbasin/thin_crops.py work/snowbasin/crops 1.3 1250,400,2050,1050   # pieces drawn thin
```

The report (the reports README, "Snowbasin"):

```bash
python3 -I tools/trailmap/reports/cc_lookup.py CC-MAIN-2026-04 'com,snowbasin)/the-mountain/mountain-report' \
  work/snowbasin/cc --fetch
python3 -I tools/trailmap/reports/warc_to_html.py work/snowbasin/cc/CC-MAIN-2026-04_20260121160328.warc \
  work/snowbasin/cc/page.html
python3 -I tools/trailmap/resorts/snowbasin/mountain_report.py work/snowbasin/cc/page.html --source "..." \
  --out tools/trailmap/resorts/snowbasin/report.json
```
