# Deer Valley: rebuild

Deer Valley's app data is built from two exports of the 2025-26 map on skimap.org: the vector PDF of 2025-10-16
(strokes, outlined glyph names) registered on the flattened image of 2025-11-04 (the map image), with the map's
reading (`resort.py`) and the decisions settled on crops (`decisions.py`), by `tools/trailmap/pdf_resort.py`. Its
source, the quirks of its map and how it was checked are in
[docs/trail-map-playbook.md, "Deer Valley"](../../../../docs/trail-map-playbook.md#deer-valley).

```bash
tools/trailmap/resorts/deer-valley/regen.sh            # rebuild src/data/resorts/deer-valley/
IMAGES=1 tools/trailmap/resorts/deer-valley/regen.sh   # also its map image in public/maps/
FORCE=1 tools/trailmap/resorts/deer-valley/regen.sh    # on a source whose SHA-256 differs (a new edition: the playbook, "A new season's map")
```

A person's reviews in `trailReviews.json` are kept; Claude's (`"by": "claude"`) are rebuilt, keeping their timestamps
when nothing changed. Never edit the generated files: change `resort.py` or `decisions.py` and re-run (add a
decision with `python3 tools/trailmap/pdf_resort.py deer-valley add "<crop>" <id>=NAME`).

| file | what it is |
|---|---|
| `regen.sh` | the whole rebuild: downloads the sources into `work/deer-valley/` (git-ignored), extracts, names every piece, writes `src/data/resorts/deer-valley/` byte for byte |
| `prepare.py` | the extraction: the map image (the November image's trail area), the line pieces, the printed names and symbols, on the image's grid |
| `resort.py` | how this map prints things: the settings `tools/trailmap/pdf_resort.py` reads; the registration (`AFFINE`) and the interactive map's (`VICOMAP_AFFINE`) |
| `decisions.py` | what the crops settled, as points on the map, each with the crop that settled it |
| `letters.json` | the glyph shapes read on contact sheets (`tools/trailmap/pdf_glyphs.py`) |
| `report.json` | the trail report: the mtnpowder feed's 2025-26 list (`tools/trailmap/reports/feed_trails.py`) |
| `header.txt` | the comment at the top of `trails.ts`: sources, method, decisions, ratings |
| `checks/editions.py` | where the November image differs from the October PDF: labels, lines, symbols, line ink on no piece |

The checks against the interactive map (not part of the rebuild):

```bash
python3 tools/trailmap/vicomap.py fetch 1815 --out work/deer-valley/vicomap
python3 tools/trailmap/vicomap.py parse work/deer-valley/vicomap
python3 tools/trailmap/vicomap.py check deer-valley [--along]       # each piece against the trail covering it
python3 tools/trailmap/vicomap.py show deer-valley Sunrise --out work/deer-valley/sunrise.png
python3 tools/trailmap/reports/compare.py --resort deer-valley     # the trail list against the report
```
