# Schweitzer: rebuild

Schweitzer's 2025-26 trail maps (schweitzer.com's maps page, images only: James Niehues's paintings of Schweitzer
Bowl and Outback Bowl, two panels) paint the runs as slopes with no line, a name printed along each and its symbol by
it; only the cat tracks are navy lines. The resort's interactive maps (resorts-interactive.com maps 1826 and 1827)
draw the same paintings with every name's letters and most symbols grouped under the run's name: `prepare.py` puts
them on the prints, `names.py` holds what they lack (read on crops), and `tools/trailmap/pdf_resort.py` makes each
run's overlay the stretch along its printed name. Its sources, the quirks of its maps and how they were checked are in
[docs/trail-map-playbook.md, "Schweitzer"](../../../../docs/trail-map-playbook.md#schweitzer).

```bash
tools/trailmap/resorts/schweitzer/regen.sh            # rebuild src/data/resorts/schweitzer/
IMAGES=1 tools/trailmap/resorts/schweitzer/regen.sh   # also its map images, public/maps/schweitzer-<panel>.jpg
FORCE=1 tools/trailmap/resorts/schweitzer/regen.sh    # on a source whose SHA-256 differs (a new edition: the playbook, "A new season's map")
```

A person's reviews in `trailReviews.json` are kept; Claude's (`"by": "claude"`) are rebuilt, keeping their timestamps
when nothing changed. Never edit the generated files: change `resort.py`, `names.py` or a panel's `resort.py` and
re-run.

| file | what it is |
|---|---|
| `regen.sh` | the whole rebuild: downloads the images and the interactive maps into `work/schweitzer/` (git-ignored, plain curl), checks their SHA-256, extracts, names, writes `src/data/resorts/schweitzer/` byte for byte |
| `prepare.py` | per panel: the map image; the labels (each group's letters, moved onto a smooth curve) and symbols from the interactive map, registered on the print, plus `names.py`'s; the cat tracks routed along the print's navy lines |
| `names.py` | what the crops showed: groups named otherwise, labels and symbols the groups lack (most of Outback Bowl's black runs, the parks, Lower Loophole), a symbol not printed, the Outback map's cat tracks as waypoints |
| `resort.py` | the panels, the report's names and areas, the ratings by colour, the parks |
| `panels/<panel>/resort.py` | the panel's registration (`VICOMAP_AFFINE`), its label stretches (`LABEL_LINE`), the names with none (`NO_STRETCH`: two-line names, and the cat tracks, whose line is their overlay), the glades |
| `panels/<panel>/decisions.py` | empty: every piece and label is named by its group or by `names.py` |
| `report.json` | the trail report: the mtnpowder feed (resort 168, fetched 2026-10-10, out of season: every run listed closed; `tools/trailmap/reports/feed_trails.py`) |
| `header.txt` | the comment at the top of `trails.ts`: sources, method, decisions, ratings |

The checks (not part of the rebuild):

```bash
python3 tools/trailmap/reports/compare.py --resort schweitzer      # the trail list against the report
python3 tools/trailmap/overlay_audit.py --resort schweitzer --panel outback-bowl --out work/schweitzer/audit \
  --per 9 --max 420 --image work/schweitzer/outback-bowl/map.png
python3 tools/archive/schweitzer/show.py outback-bowl work/schweitzer/show 0.9 0,250,1100,1050   # labels, symbols
python3 tools/archive/schweitzer/diamonds.py outback-bowl          # the print's black diamonds (names.py SYMBOLS)
python3 tools/archive/schweitzer/editions.py                       # the 2024-25 Outback image against the 2025-26 one
```

The report:

```bash
curl -sS -o work/schweitzer/report/cfg.json https://v4.mtnfeed.com/resorts/schweitzer.json
TOKEN=$(python3 -c "import json; print(json.load(open('work/schweitzer/report/cfg.json'))['bearerToken'])")
curl -sS -o work/schweitzer/report/feed.json "https://mtnpowder.com/feed/v3.json?bearer_token=$TOKEN&resortId%5B%5D=168"
python3 -I tools/trailmap/reports/feed_trails.py work/schweitzer/report/feed.json --source "..." \
  --out tools/trailmap/resorts/schweitzer/report.json
```
