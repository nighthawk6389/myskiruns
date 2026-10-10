# Aspen Mountain: rebuild

Aspen Mountain's 2025-26 trail map (the PDF aspensnowmass.com's trail-maps page links, drawn like Snowmass's) draws
its trail lines as vectors (blue and black strokes; the extreme terrain a black line in a yellow casing) and prints
every name as white text on a pill in its run's colour, with no symbol by any name: the rating is the pill's colour.
The app data, three panels (the whole mountain and its two insets, the summit and Hero's), is built from the PDF,
the map's reading (`resort.py`, `panels/<panel>/resort.py`) and the decisions settled on crops
(`panels/<panel>/decisions.py`), by `tools/trailmap/pdf_resort.py`. Its source, the quirks of its map and how it was
checked are in [docs/trail-map-playbook.md, "Aspen Mountain"](../../../../docs/trail-map-playbook.md#aspen-mountain).

```bash
tools/trailmap/resorts/aspen-mountain/regen.sh            # rebuild src/data/resorts/aspen-mountain/
IMAGES=1 tools/trailmap/resorts/aspen-mountain/regen.sh   # also its map images in public/maps/ (aspen-mountain-<panel>.jpg)
FORCE=1 tools/trailmap/resorts/aspen-mountain/regen.sh    # on a source whose SHA-256 differs (a new edition: the playbook, "A new season's map")
```

A person's reviews in `trailReviews.json` are kept; Claude's (`"by": "claude"`) are rebuilt, keeping their timestamps
when nothing changed. Never edit the generated files: change `resort.py` or `decisions.py` and re-run.

| file | what it is |
|---|---|
| `regen.sh` | the whole rebuild: downloads the PDF into `work/aspen-mountain/` (git-ignored), extracts, names every piece, writes `src/data/resorts/aspen-mountain/` byte for byte |
| `prepare.py` | the extraction, per panel: the map image, the line pieces (strokes, casings, thin yellow casings; each inset's cut at its frame), the names with their pills' colours and the double black runs |
| `resort.py` | what the panels share: the panels, the areas, the names' spellings (no trail report), the renames |
| `panels/<panel>/resort.py` | each panel's clip and scale, its names printed in parts (`JOIN`), and the settings `pdf_resort.py` reads |
| `panels/<panel>/decisions.py` | what the crops settled: which run each piece is, where one path carries several runs (cut), the lines that are no run, Summer Road's traced stretch |
| `header.txt` | the comment at the top of `trails.ts`: sources, method, decisions, ratings |

The checks (not part of the rebuild):

```bash
python3 tools/trailmap/overlay_audit.py --resort aspen-mountain --panel main --out work/aspen-mountain/audit_main
python3 tools/trailmap/overlay_audit.py --resort aspen-mountain --panel summit --out work/aspen-mountain/audit_summit
python3 tools/trailmap/overlay_audit.py --resort aspen-mountain --panel heros --out work/aspen-mountain/audit_heros
python3 tools/archive/aspen-mountain/junctions.py aspen-mountain/main 26    # a piece's junctions and names along it
```

No trail report: out of season Aspen Snowmass's grooming feed lists no trails for Aspen Mountain
(`.../GroomingReport/Feed?mountain=AspenMountain`, the id its grooming-report page uses), and Common Crawl's
January 2026 capture of that page holds no list (the page loads it). In season, the feed can be read as Snowmass's
and Buttermilk's are (the reports README, "Aspen Snowmass") and checked with `compare.py`.
