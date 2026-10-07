# Hunter Mountain: rebuild

Hunter Mountain's app data is built from the 2025-26 PDF (strokes and text over a vector painting), the map's reading (`resort.py`) and the decisions settled on crops
(`decisions.py`), by `tools/trailmap/pdf_resort.py`. Its source, the quirks of its map and how it was checked are
in [docs/trail-map-playbook.md, "Hunter Mountain"](../../../../docs/trail-map-playbook.md#hunter-mountain).

```bash
tools/trailmap/resorts/hunter/regen.sh            # rebuild src/data/resorts/hunter/
IMAGES=1 tools/trailmap/resorts/hunter/regen.sh   # also its map image in public/maps/
FORCE=1 tools/trailmap/resorts/hunter/regen.sh    # on a source whose SHA-256 differs (a new edition: the playbook, "A new season's map")
```

A person's reviews in `trailReviews.json` are kept; Claude's (`"by": "claude"`) are rebuilt, keeping their timestamps
when nothing changed. Never edit the generated files: change `resort.py` or `decisions.py` and re-run (add a
decision with `python3 tools/trailmap/pdf_resort.py hunter add "<crop>" <id>=NAME`).

| file | what it is |
|---|---|
| `regen.sh` | the whole rebuild: downloads the sources into `work/hunter/` (git-ignored), extracts, names every piece, writes `src/data/resorts/hunter/` byte for byte |
| `resort.py` | how this map prints things: the settings `tools/trailmap/pdf_resort.py` reads |
| `decisions.py` | what the crops settled, as points on the map, each with the crop that settled it |
| `header.txt` | the comment at the top of `trails.ts`: sources, method, decisions, ratings |
