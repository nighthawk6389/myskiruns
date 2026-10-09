# Mammoth Mountain: rebuild

Mammoth's 2025-26 trail map (the resort's PDF, kept by skimap.org) prints its names as text and its symbols as fills
over a painting, and draws no trail lines; the resort's interactive maps (resorts-interactive.com maps 1812 and
1819) draw every run's line over the same paintings, grouped by name. The app data, two panels (the whole mountain
and the back-side inset), is built from the two, the map's reading (`resort.py`, `panels/<panel>/resort.py`) and
the decisions settled on crops (`panels/<panel>/decisions.py`), by `tools/trailmap/pdf_resort.py`. Its source, the
quirks of its map and how it was checked are in
[docs/trail-map-playbook.md, "Mammoth Mountain"](../../../../docs/trail-map-playbook.md#mammoth-mountain).

```bash
tools/trailmap/resorts/mammoth/regen.sh            # rebuild src/data/resorts/mammoth/
IMAGES=1 tools/trailmap/resorts/mammoth/regen.sh   # also its map images in public/maps/ (mammoth-<panel>.jpg)
FORCE=1 tools/trailmap/resorts/mammoth/regen.sh    # on a source whose SHA-256 differs (a new edition: the playbook, "A new season's map")
```

A person's reviews in `trailReviews.json` are kept; Claude's (`"by": "claude"`) are rebuilt, keeping their timestamps
when nothing changed. Never edit the generated files: change `resort.py` or `decisions.py` and re-run.

| file | what it is |
|---|---|
| `regen.sh` | the whole rebuild: downloads the PDF and both SVGs into `work/mammoth/` (git-ignored), extracts, names every piece, writes `src/data/resorts/mammoth/` byte for byte |
| `prepare.py` | the extraction, per panel: the map image, the SVG's lines on it (`vicomap.py parse`), the names (`pdf_labels.py`, plus the two outlined ones) spelled as the groups, the symbols from the fills |
| `resort.py` | what both panels share: the panels, the areas, the report's names and areas, the outlined names, the renames, the parks |
| `panels/<panel>/resort.py` | each panel's clip, scale and registration (`VICOMAP_AFFINE`) and the settings `pdf_resort.py` reads |
| `panels/<panel>/decisions.py` | what the crops settled: where the interactive map's line is another run's (cut and named) or runs on too far (trimmed) |
| `report.json` | the trail report: the mtnpowder feed (resort 60, `tools/trailmap/reports/feed_trails.py`) |
| `header.txt` | the comment at the top of `trails.ts`: sources, method, decisions, ratings |

The checks (not part of the rebuild):

```bash
python3 tools/trailmap/reports/compare.py --resort mammoth                     # the trail list against the report
python3 tools/trailmap/overlay_audit.py --resort mammoth --panel main --out work/mammoth/audit_main
python3 tools/trailmap/overlay_audit.py --resort mammoth --panel back-side --out work/mammoth/audit_back
python3 tools/trailmap/symbol_audit.py --symbols work/mammoth/main/named_syms.json \
  --paths src/data/resorts/mammoth/panels/main/trailPaths.json --trails src/data/resorts/mammoth/trails.ts \
  --image work/mammoth/main/map.png --out work/mammoth/sym_main --mode off
```

The registration (`VICOMAP_AFFINE` in each panel's `resort.py`): the SVG's painting (written by `vicomap.py parse`)
registered on the panel's image, its placement in the SVG folded in (`x' = a (x - tx) + b (y - ty) + c`, the
`<use>` matrix's translation tx, ty):

```bash
python3 -I tools/trailmap/register_pages.py --ref work/mammoth/vicomap/background.jpeg --ref-scale 2.66634 \
  --image work/mammoth/main/map.png
python3 -I tools/trailmap/register_pages.py --ref work/mammoth/vicomap_back/background.jpeg --ref-scale 1.24853 \
  --image work/mammoth/back-side/map.png
```

The report: the mtnpowder feed, with the bearer token from the site's widget config:

```bash
curl -sS -o work/mammoth/report/cfg.json https://v4.mtnfeed.com/resorts/mammoth.json
TOKEN=$(python3 -c "import json; print(json.load(open('work/mammoth/report/cfg.json'))['bearerToken'])")
curl -sS -o work/mammoth/report/feed.json "https://mtnpowder.com/feed/v3.json?bearer_token=$TOKEN&resortId%5B%5D=60"
python3 -I tools/trailmap/reports/feed_trails.py work/mammoth/report/feed.json --source "..." \
  --out tools/trailmap/resorts/mammoth/report.json
```
