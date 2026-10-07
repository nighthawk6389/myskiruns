# Sugarloaf: rebuild

Sugarloaf's app data is built from the 2025-26 PDF (strokes, outlined glyphs, key circles, a raster inset), the map's reading (`resort.py`) and the decisions settled on crops
(`decisions.py`), by `tools/trailmap/pdf_resort.py`. Its source, the quirks of its map and how it was checked are
in [docs/trail-map-playbook.md, "Sugarloaf"](../../../../docs/trail-map-playbook.md#sugarloaf).

```bash
tools/trailmap/resorts/sugarloaf/regen.sh            # rebuild src/data/resorts/sugarloaf/
IMAGES=1 tools/trailmap/resorts/sugarloaf/regen.sh   # also its map image in public/maps/
FORCE=1 tools/trailmap/resorts/sugarloaf/regen.sh    # on a source whose SHA-256 differs (a new edition: the playbook, "A new season's map")
```

A person's reviews in `trailReviews.json` are kept; Claude's (`"by": "claude"`) are rebuilt, keeping their timestamps
when nothing changed. Never edit the generated files: change `resort.py` or `decisions.py` and re-run (add a
decision with `python3 tools/trailmap/pdf_resort.py sugarloaf add "<crop>" <id>=NAME`).

| file | what it is |
|---|---|
| `regen.sh` | the whole rebuild: downloads the sources into `work/sugarloaf/` (git-ignored), extracts, names every piece, writes `src/data/resorts/sugarloaf/` byte for byte |
| `prepare.py` | the extraction: the map image(s), the line pieces, the printed names and symbols |
| `resort.py` | how this map prints things: the settings `tools/trailmap/pdf_resort.py` reads |
| `decisions.py` | what the crops settled, as points on the map, each with the crop that settled it |
| `letters.json` | the glyph shapes read on contact sheets (`tools/trailmap/pdf_glyphs.py`) |
| `header.txt` | the comment at the top of `trails.ts`: sources, method, decisions, ratings |
