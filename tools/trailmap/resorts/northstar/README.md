# Northstar: rebuild

Northstar's 2025-26 trail map (the PDF northstarcalifornia.com's trail-map page links, Alex Tait's painting under a
vector layer) draws every trail line as a filled outline in blue, black or green, prints each name in white capitals on
its own line (each letter haloed in the line's colour) and sets the difficulty symbols on the lines. The app data is
built from the PDF, the map's reading (`resort.py`, `letters.json`) and the decisions settled on crops
(`decisions.py`), by `tools/trailmap/pdf_resort.py`. Its source, the quirks of its map and how it was checked are in
[docs/trail-map-playbook.md, "Northstar"](../../../../docs/trail-map-playbook.md#northstar).

```bash
tools/trailmap/resorts/northstar/regen.sh            # rebuild src/data/resorts/northstar/
IMAGES=1 tools/trailmap/resorts/northstar/regen.sh   # also its map image, public/maps/northstar.jpg
FORCE=1 tools/trailmap/resorts/northstar/regen.sh    # on a source whose SHA-256 differs (a new edition: the playbook, "A new season's map")
```

A person's reviews in `trailReviews.json` are kept; Claude's (`"by": "claude"`) are rebuilt, keeping their timestamps
when nothing changed. Never edit the generated files: change `resort.py` or `decisions.py` and re-run.

| file | what it is |
|---|---|
| `regen.sh` | the whole rebuild: fetches the PDF into `work/northstar/` (git-ignored) from inside its trail-map page (`fetch_pdf.cjs`), extracts, names every piece, writes `src/data/resorts/northstar/` byte for byte |
| `prepare.py` | the extraction: the map image, the line pieces (the outlines' centre lines, less the letters' halos, the hatching and the icons), the names (outlined glyphs and live text) with their halo's colour, the symbols (less the kids' signs' squares) |
| `letters.json` | each outlined glyph shape's letter, read once on `pdf_glyphs.py sheet` contact sheets (`*`: the boundary lettering, logos, icons) |
| `resort.py` | the map's reading: the areas, the report's names and areas, the names printed in parts, the lifts' names dropped, the renames, the names printed some other way (EXTRA), the labels that are their own line, the parks, and the settings `pdf_resort.py` reads |
| `decisions.py` | what the crops settled: where one outline carries several runs (cut), which run each unlabelled piece is, the lines that are no run (leaders, halos, links) |
| `report.json` | the trail report: the terrain feed on the terrain-and-lift-status page, as Common Crawl captured it on 2026-02-19 (`tools/trailmap/reports/feed_trails.py`) |
| `header.txt` | the comment at the top of `trails.ts`: sources, method, decisions, ratings |

The checks (not part of the rebuild):

```bash
python3 tools/trailmap/reports/compare.py --resort northstar       # the trail list against the report
python3 tools/trailmap/overlay_audit.py --resort northstar --out work/northstar/audit --per 6 --max 560
python3 tools/archive/northstar/colour_crops.py work/northstar work/northstar/crops 1.2 1300,100,2200,800   # pieces in colour
python3 tools/archive/northstar/sharp_turns.py                     # where a piece turns back (a cut to check)
python3 tools/archive/northstar/on_points.py 51 1691,179           # a cut's point on its piece, and the points either side
```

The report (the reports README, "Northstar"):

```bash
python3 -I tools/trailmap/reports/cc_lookup.py CC-MAIN-2026-08 \
  'com,northstarcalifornia)/the-mountain/mountain-conditions/terrain-and-lift-status' work/northstar/cc --fetch
python3 -I tools/trailmap/reports/warc_to_html.py work/northstar/cc/CC-MAIN-2026-08_20260219030343.warc \
  work/northstar/cc/page.html
python3 -I tools/trailmap/reports/extract_feed.py work/northstar/cc/page.html work/northstar/cc/feeds
python3 -I tools/trailmap/reports/feed_trails.py work/northstar/cc/feeds/feed_04_FR_TerrainStatusFeed.json \
  --source "..." --out tools/trailmap/resorts/northstar/report.json
```
