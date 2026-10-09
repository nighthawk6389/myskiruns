# Snowmass: rebuild

Snowmass's 2025-26 trail map (the "layered" PDF aspensnowmass.com links) draws its trail lines as vectors (blue,
black and green strokes; the expert runs a black line in a yellow casing) and prints every name as white text on a
pill in its run's colour, with no symbol by any name: the rating is the pill's colour. The app data, two panels (the
whole mountain and the inset of Hanging Valley), is built from the PDF, the map's reading (`resort.py`,
`panels/<panel>/resort.py`) and the decisions settled on crops (`panels/<panel>/decisions.py`), by
`tools/trailmap/pdf_resort.py`. Its source, the quirks of its map and how it was checked are in
[docs/trail-map-playbook.md, "Snowmass"](../../../../docs/trail-map-playbook.md#snowmass).

```bash
tools/trailmap/resorts/snowmass/regen.sh            # rebuild src/data/resorts/snowmass/
IMAGES=1 tools/trailmap/resorts/snowmass/regen.sh   # also its map images in public/maps/ (snowmass-<panel>.jpg)
FORCE=1 tools/trailmap/resorts/snowmass/regen.sh    # on a source whose SHA-256 differs (a new edition: the playbook, "A new season's map")
```

A person's reviews in `trailReviews.json` are kept; Claude's (`"by": "claude"`) are rebuilt, keeping their timestamps
when nothing changed. Never edit the generated files: change `resort.py` or `decisions.py` and re-run.

| file | what it is |
|---|---|
| `regen.sh` | the whole rebuild: downloads the PDF into `work/snowmass/` (git-ignored), extracts, names every piece, writes `src/data/resorts/snowmass/` byte for byte |
| `prepare.py` | the extraction, per panel: the map image, the line pieces (strokes, the casings' centre lines, the thin yellow casings), the names with their pills' colours and the expert runs (a cased line, an EX mark) |
| `resort.py` | what both panels share: the panels, the areas, the report's names and areas, the names printed in parts or as one object, the renames, the parks |
| `panels/<panel>/resort.py` | each panel's clip and scale and the settings `pdf_resort.py` reads |
| `panels/<panel>/decisions.py` | what the crops settled: which run each piece is, where one path carries two runs (cut), the lines that are no run |
| `report.json` | the trail report: Aspen Snowmass's grooming feed (`tools/trailmap/reports/feed_trails.py`) |
| `header.txt` | the comment at the top of `trails.ts`: sources, method, decisions, ratings |

The checks (not part of the rebuild):

```bash
python3 tools/trailmap/reports/compare.py --resort snowmass                     # the trail list against the report
python3 tools/trailmap/overlay_audit.py --resort snowmass --panel main --out work/snowmass/audit_main
python3 tools/trailmap/overlay_audit.py --resort snowmass --panel hanging-valley --out work/snowmass/audit_hv
python3 tools/trailmap/grid_crop.py --image work/snowmass/main/map.png --box 2000,400,2400,800 --zoom 2 \
  --pieces work/snowmass/main/pieces_cut.json --names work/snowmass/main/names.json --out spot.png
```

The report: the grooming feed, plain curl (the reports README, "Aspen Snowmass"):

```bash
curl -sS -o work/snowmass/report/feed.json 'https://www.aspensnowmass.com/AspenSnowmass/GroomingReport/Feed?mountain=Snowmass'
python3 -I tools/trailmap/reports/feed_trails.py work/snowmass/report/feed.json --source "..." \
  --out tools/trailmap/resorts/snowmass/report.json
```
