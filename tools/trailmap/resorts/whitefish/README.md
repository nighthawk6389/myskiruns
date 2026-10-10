# Whitefish Mountain Resort: rebuild

Whitefish publishes its trail maps as web JPEGs only (skiwhitefish.com's trail-maps page: the 2025-26 Front Side and
the 2024-25 North Side and Hellroaring Basin insets, James Niehues's paintings), with no PDF and no interactive map.
Their thin lines are blurred by the JPEG and many run in a casing, so line detection finds only part of them: the
map is read instead. `names.py` holds every printed name with its label's position, its symbol and its run's line as
a few waypoints read on zoomed grid crops; `prepare.py` routes each line along the painted one between its waypoints
(`tools/trailmap/route_trace.py`); `tools/trailmap/pdf_resort.py` builds the panels from those named pieces. Its
source, the quirks of its map and how it was checked are in
[docs/trail-map-playbook.md, "Whitefish Mountain"](../../../../docs/trail-map-playbook.md#whitefish-mountain).

```bash
tools/trailmap/resorts/whitefish/regen.sh            # rebuild src/data/resorts/whitefish/
IMAGES=1 tools/trailmap/resorts/whitefish/regen.sh   # also its map images, public/maps/whitefish-<panel>.jpg
FORCE=1 tools/trailmap/resorts/whitefish/regen.sh    # on a source whose SHA-256 differs (a new edition: the playbook, "A new season's map")
```

A person's reviews in `panels/<panel>/trailReviews.json` (in `src/data/resorts/whitefish/`) are kept; Claude's
(`"by": "claude"`) are rebuilt, keeping their timestamps when nothing changed. Never edit the generated files: change
`names.py` (or a panel's `resort.py` or `decisions.py`) and re-run.

| file | what it is |
|---|---|
| `regen.sh` | the whole rebuild: downloads the three JPEGs into `work/whitefish/` (git-ignored), routes the lines, writes `src/data/resorts/whitefish/` byte for byte |
| `names.py` | the map's reading, per panel: each name as printed, its label (map px of the 2x image), its symbol, its run's line as waypoints |
| `prepare.py` | the 2x images and each panel's pieces (one per line of `names.py`, routed, carrying its name) |
| `resort.py` | the panels, the areas, the report's names and sides, the renames to the report's names |
| `panels/<panel>/resort.py` | the panel's settings for `pdf_resort.py`: its names as `EXTRA`, its pieces named by `names.py` (`GROUPED`) |
| `panels/<panel>/decisions.py` | empty: the reading names every piece |
| `report.json` | the trail report: the snow report page's runs by lift (`snow_report.py`) |
| `snow_report.py` | reads that page into `report.json` |
| `header.txt` | the comment at the top of `trails.ts` |

To change a run: read it on a crop (`tools/archive/whitefish/thin_crops.py work/whitefish/<panel> <out> 1.5 x0,y0,x1,y1`
draws the pieces thin over the map, with names and a grid in map px), move its waypoints in `names.py` (one past each
junction where it could take another line), re-run, and look again (`overlay_audit.py --resort whitefish --panel
<panel>`).

The checks (not part of the rebuild):

```bash
python3 tools/trailmap/reports/compare.py --resort whitefish
for p in front-side north-side hellroaring; do
  python3 tools/trailmap/overlay_audit.py --resort whitefish --panel $p --out work/whitefish/audit/$p --per 6 --no-labels
done
```

The report (plain curl; out of season every run is listed, closed):

```bash
curl -sSL -A 'Mozilla/5.0' -o work/whitefish/report/snowreport.html https://skiwhitefish.com/snowreport/
python3 -I tools/trailmap/resorts/whitefish/snow_report.py work/whitefish/report/snowreport.html --source "..." \
  --out tools/trailmap/resorts/whitefish/report.json
```
