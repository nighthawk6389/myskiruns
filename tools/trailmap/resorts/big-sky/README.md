# Big Sky: rebuild

Big Sky's app data is built from three PDFs of strokes and text, read as three panels, the map's reading (`resort.py`) and the decisions settled on crops
(`decisions.py`), by `tools/trailmap/pdf_resort.py`. Its source, the quirks of its map and how it was checked are
in [docs/trail-map-playbook.md, "Big Sky"](../../../../docs/trail-map-playbook.md#big-sky).

```bash
tools/trailmap/resorts/big-sky/regen.sh            # rebuild src/data/resorts/big-sky/
IMAGES=1 tools/trailmap/resorts/big-sky/regen.sh   # also its map images in public/maps/
FORCE=1 tools/trailmap/resorts/big-sky/regen.sh    # on a source whose SHA-256 differs (a new edition: the playbook, "A new season's map")
```

A person's reviews in `trailReviews.json` are kept; Claude's (`"by": "claude"`) are rebuilt, keeping their timestamps
when nothing changed. Never edit the generated files: change `resort.py` or `decisions.py` and re-run (add a
decision with `python3 tools/trailmap/pdf_resort.py big-sky/<panel> add "<crop>" <id>=NAME`).

| file | what it is |
|---|---|
| `regen.sh` | the whole rebuild: downloads the sources into `work/big-sky/` (git-ignored), extracts, names every piece, writes `src/data/resorts/big-sky/` byte for byte |
| `prepare.py` | the extraction: the map image(s), the line pieces, the printed names and symbols, per panel |
| `resort.py` | how this map prints things: the settings `tools/trailmap/pdf_resort.py` reads (`PANELS`; each panel's own in `panels/<panel>/resort.py`) |
| `decisions.py` | what the crops settled, as points on the map, each with the crop that settled it (per panel, in `panels/<panel>/`) |
| `report.json` | the resort's trail report: name, area, rating (`tools/trailmap/reports/`) |
| `header.txt` | the comment at the top of `trails.ts`: sources, method, decisions, ratings |
