# Vail's trail data pipeline

Vail's 2025-26 map has no vector PDF: it is three paintings on Vail Resorts'
image CDN (Front Side, Back Bowls, Blue Sky Basin). So the lines are detected
from the rasters, and every piece's name was settled on zoomed crops. This
folder holds those readings and decisions, and the script that turns them into
the app's data. It is also the template for the next raster-only resort.

```bash
tools/trailmap/resorts/vail/regen.sh             # rebuild src/data/resorts/vail/ (13 s with the detection cached)
IMAGES=1 tools/trailmap/resorts/vail/regen.sh    # also public/maps/vail-<panel>.jpg
FORCE=1 tools/trailmap/resorts/vail/regen.sh     # on a source whose SHA-256 differs (a new edition: the playbook, "A new season's map")
FRESH=1 tools/trailmap/resorts/vail/regen.sh     # re-run line and symbol detection (cached otherwise)
```

It downloads the panels into `$VAIL_WORK` (default `work/vail`, git-ignored)
and writes every Vail data file. Re-run with nothing changed, it reproduces the
committed files byte for byte. It keeps any person's reviews in
`panels/<panel>/trailReviews.json`. Needs
`pip install pillow numpy opencv-python-headless scikit-image`.

| file | what it holds |
|---|---|
| `names.py` | what the map prints: every detected symbol keyed by its centre (name, kind as checked), labels with no symbol (`EXTRA`: bowls, parks, second labels), display spellings |
| `decisions.py` | each piece's name or why it isn't a trail, cuts, traced stretches: all as points, with the crop that settled each |
| `build.py` | auto-matches symbols to pieces, applies the decisions, spreads names along continuations |
| `reading.py` | readings + named pieces → inputs for `seed_roster.py`, `aggregate_readings.py`, `traces_to_reviews.py` |
| `add.py` | records decisions in `decisions.py` (by current piece id or by point) |
| `images.py` | the panels as the app's JPEGs |
| `header.txt` | the comment at the top of `trails.ts` |
| `common.py` | panels, sizes, the working directory, point helpers |

Never hand-edit the generated files: `trails.ts`,
`panels/*/{linePolylines,trailProposals,trailPaths}.json`, or Claude's entries
in `trailReviews.json`. Change the readings or decisions and re-run.

## Fixing or changing a trail

1. Run `regen.sh` once, so `$VAIL_WORK` holds the pieces (`pieces_<panel>.json`),
   their names (`names_<panel>.json`) and the named symbols
   (`named_syms_<panel>.json`).
2. Look at the spot, with every piece tagged `id:name`:
   ```bash
   python3 tools/trailmap/grid_crop.py --image work/vail/front-side.png --box 2550,1830,2780,2110 --zoom 3 \
     --pieces work/vail/pieces_front-side.json --names work/vail/names_front-side.json \
     --symbols work/vail/named_syms_front-side.json --out work/vail/spot.png
   ```
3. Record what you see:
   ```bash
   python3 tools/trailmap/resorts/vail/add.py front-side "spot.png: Head First's line below Gitalong Road" \
     272="HEAD FIRST" 2617,1957="HEAD FIRST" 324=-:"in-town bus route, not a trail"
   ```
4. A stretch the detector missed: read rough points off the grid, snap them,
   and add the result to `TRACED` in `decisions.py`:
   ```bash
   python3 tools/trailmap/snap_trace.py --image work/vail/front-side.png --color black \
     2639,1884 2626,1930 2618,1959 --r 6 --show work/vail/check.png
   ```
   One drawn line carrying two trails: add `(point on it, point to cut at)`
   to `CUTS`.
5. `regen.sh`, then audit (the playbook's Part 4, "Auditing on crops, or the human review page"):
   ```bash
   python3 tools/trailmap/region_audit.py --image work/vail/front-side.png \
     --paths src/data/resorts/vail/panels/front-side/trailPaths.json \
     --trails src/data/resorts/vail/trails.ts --out work/vail/audit --grid 5x3 --area 0,450,4990,2300 --zoom 1.3
   python3 tools/trailmap/symbol_audit.py --symbols work/vail/named_syms_front-side.json \
     --paths src/data/resorts/vail/panels/front-side/trailPaths.json \
     --trails src/data/resorts/vail/trails.ts --image work/vail/front-side.png --out work/vail/symbols
   ```
   and the hover check per panel (`--resort vail --panel front-side`).

## How the map draws things (what the code relies on)

- Lines: green, blue and black solid lines; dashed in the same colours for
  roads and catwalks (with hollow direction arrows). Yellow is the boundary,
  maroon the lifts, pale yellow hatching a slow zone.
- A run's symbol (green circle, blue square, black diamond, double diamond) sits
  on its line, with the name printed beside it. The line resumes past the name.
  The name may run uphill from the symbol. A symbol on a run's line with no
  name marks a change of rating; it counts toward that run's difficulty.
- Bowls and some open slopes print a name and no line: markers. Bowls print
  no symbol and are rated black.
- Back Bowls and Blue Sky are drawn at a bigger scale than Front Side
  (`--k 1.75` and `2.7` in `regen.sh`). Back Bowls' bottom edge repeats Blue
  Sky's roads, and Blue Sky's edge repeats Back Bowls runs. Those trails get
  overlays on both panels; `SHARED` keeps their area at Back Bowls.
- The Game Creek Bowl inset (Front Side, top right) is part of the same
  panel; only its frame lines are excluded.

## Doing another raster-only resort

Copy this folder and change, in order:
1. `common.py`: the panels and their sizes. `regen.sh`: the image URLs (find
   the scene7 names in the resort's trail-map page) and the per-panel
   `raster_lines.py` / `raster_symbols.py` arguments. Tune those with
   `--debug mask.png` until legends, logos and text are out and the dashes
   link up. The colour masks in `raster_lines.py` are Vail's palette: check
   them on the new map first.
2. `names.py`: render the detected symbols (`grid_crop.py --symbols
   syms_<panel>.json --grid 0` over tiles) and write each one's printed name
   and kind. Then add the names printed with no symbol.
3. Run `build.py` to auto-match. Then review every piece on tiles
   (`grid_crop.py --pieces --names --grid 0`), recording decisions with
   `add.py` until `build.py` reports 0 undecided.
4. `reading.py`, `header.txt`, `regen.sh`. Register the resort in
   `src/resorts.ts`: its `load` returns one `maps` entry per panel.
