# Heavenly: rebuild

Heavenly's app data is built from the current map as an image, with the lines, names and symbols of an older PDF of its artwork, the map's reading (`resort.py`) and the decisions settled on crops
(`decisions.py`), by `tools/trailmap/pdf_resort.py`. Its source, the quirks of its map and how it was checked are
in [docs/trail-map-playbook.md, "Heavenly"](../../../../docs/trail-map-playbook.md#heavenly).

```bash
tools/trailmap/resorts/heavenly/regen.sh            # rebuild src/data/resorts/heavenly/
IMAGES=1 tools/trailmap/resorts/heavenly/regen.sh   # also its map images in public/maps/
FORCE=1 tools/trailmap/resorts/heavenly/regen.sh    # on a source whose SHA-256 differs (a new edition: the playbook, "A new season's map")
```

A person's reviews in `trailReviews.json` are kept; Claude's (`"by": "claude"`) are rebuilt, keeping their timestamps
when nothing changed. Never edit the generated files: change `resort.py` or `decisions.py` and re-run (add a
decision with `python3 tools/trailmap/pdf_resort.py heavenly/<panel> add "<crop>" <id>=NAME`).

| file | what it is |
|---|---|
| `regen.sh` | the whole rebuild: downloads the sources into `work/heavenly/` (git-ignored), extracts, names every piece, writes `src/data/resorts/heavenly/` byte for byte |
| `prepare.py` | the extraction: the map image(s), the line pieces, the printed names and symbols, per panel |
| `resort.py` | how this map prints things: the settings `tools/trailmap/pdf_resort.py` reads (`PANELS`; each panel's own in `panels/<panel>/resort.py`) |
| `decisions.py` | what the crops settled, as points on the map, each with the crop that settled it (per panel, in `panels/<panel>/`) |
| `letters.json` | the glyph shapes read on contact sheets (`tools/trailmap/pdf_glyphs.py`) |
| `report.json` | the resort's trail report: name, area, rating (`tools/trailmap/reports/`) |
| `header.txt` | the comment at the top of `trails.ts`: sources, method, decisions, ratings |
