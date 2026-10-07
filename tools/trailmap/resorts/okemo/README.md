# Okemo's trail data pipeline

Okemo's 2025-26 trail map is a PDF whose trail lines are vector strokes over one painted raster, but whose
names are outlined glyphs, not text. So the lines came straight from the PDF, and the names from six parallel
readers (Claude sub-agents) looking at numbered tiles, then five trace readers for the uncertain trails, then a
person on the Trail Check review page. A rerun of the readers would not give the same answers, so their
outputs are kept here as the record (`readings/`), with Claude's hand-made decisions (`decisions.py`).
`regen.sh` rebuilds every Okemo data file from the PDF, the readings and the decisions, byte for byte.

## Source

- `https://www.okemo.com/-/aemasset/sitecore/okemo/maps/winter-2025-2026/20251120_OK_winter-trail_map_001.pdf`,
  linked from https://www.okemo.com/the-mountain/about-the-mountain/trail-map.aspx: the 2025-26 winter trail map
  (file dated 2025-11-20; okemo.com had no 2026-27 map when Okemo was built, 2026-09-30).
- 3,047,541 bytes, PDF 1.6, two 1458 x 1039.5 pt pages: page 1 the information side, page 2 the map.
  SHA-256 `82a8454dd34c58d4c5731905a7a44a079d9940899aeda85162f5fec8b1c839a1` (checked by `regen.sh`).
- Fetching: okemo.com sends the PDF to curl as it comes, but an error page ("The system cannot process your
  request") to a browser's user agent sent without a browser's other headers (the first download, 2026-09-30,
  used curl with a browser's full header set). `regen.sh` tries plain curl, then
  `tools/trailmap/fetch_pdf.cjs` (headless Chromium, from inside the trail-map page), and otherwise asks for the
  file to be saved by hand as `$OKEMO_WORK/okemo.pdf`. Both ways were checked on 2026-10-07: same SHA-256.
- No CDN image: the map image is page 2 rendered, clipped to `0,0,1458,913` pt (the map down to the white band of
  partner logos) at 3 px/pt, 4374 x 2739 px. `public/maps/okemo.jpg` is the extractor's JPEG of it (quality 88,
  progressive), `okemo_source.png` the lossless copy on the same grid (tiles, crops).

## Rebuild

```bash
tools/trailmap/resorts/okemo/regen.sh            # rebuild src/data/resorts/okemo/ (about 10 s)
IMAGES=1 tools/trailmap/resorts/okemo/regen.sh   # also public/maps/okemo.jpg
FORCE=1 tools/trailmap/resorts/okemo/regen.sh    # on a PDF with another SHA-256 (see "A new season's map")
TILES=1 FORCE=1 tools/trailmap/resorts/okemo/regen.sh   # just its pieces and tiles, no data written
```

Working files go to `$OKEMO_WORK` (default `work/okemo`, git-ignored); run from anywhere. Needs
`pip install pymupdf pillow` and Node (and Playwright only if curl gets no PDF). With nothing changed, it
leaves `git status -- src/data/resorts/okemo public/maps/okemo.jpg` clean, from an empty work folder or a
filled one.

## Pipeline (`regen.sh`, in order)

1. **PDF** → `$W/okemo.pdf` (downloaded if missing; stops on another SHA-256 unless `FORCE=1`).
2. **Line pieces**: `extract_pdf_vectors.py --page 1 --clip 0,0,1458,913 --scale 3` with the three trail colours
   (`--max-width 0.8`), then `--append` the orange park colour → `$W/pieces.json`: 256 pieces (87 green, 84 blue,
   75 black, then 10 freestyle as ids 246-255). With `IMAGES=1` the first pass writes `public/maps/okemo.jpg`.
3. **Tiles**: the lossless render `$W/okemo_source.png`, and `render_tiles.py` → `$W/tiles/` (33 tiles of
   760 x 540 source px at 1.7x, every piece drawn and numbered, and `index.json`): exactly what the readers saw
   (tiles and index checked identical to the originals). `aggregate_readings.py` reads `index.json`. `TILES=1`
   stops here.
4. **Trail list**: `seed_roster.py` on the six readers' files only (`readings/result_[0-9].json`, as when the list
   was made: the overrides and the split came later), areas `okemo-mountain` (3,344 ft) and `jackson-gore`
   (2,725 ft) → `trails.ts` (127 trails) and `$W/labels.json`; then `steps.py trails` applies `TRAILS_TS`
   (Tomahawk Park added, Tree Tap marked a park, 4 header lines) → 128 trails.
5. **linePolylines.json**: the pieces, plus `steps.py unnamed` (`UNNAMED`: piece 239 as `_unnamed`) and
   `steps.py split` (`SPLITS`, by `split_pieces.py`: 210 cut at (1599, 552); the upper part stays 210, Challenger,
   the lower becomes 256, Turkey Shoot; the names go to `$W/readings/result_splits.json`) → 257 pieces.
6. **Proposals**: `aggregate_readings.py --labels` over `$W/readings/result_*.json` (the six readers,
   `result_overrides.json`, `result_splits.json`) → `trailProposals.json` (107 lines at high confidence and the
   Broken Arrow glade marker, 10 medium, 1 low, 9 names with no line) and `$W/review/data.json`.
7. **Claude's reviews**: the trace readers' files copied to `$W/traces/` and `steps.py trace` (`TRACE_FIXES`:
   Turkey Shoot's trace on the cut piece 256); `traces_to_reviews.py --replace-claude`; `steps.py reviews`
   (`MARKERS`, `LINES`, `RECHECK`: markers for Galaxy Bowl, Bright Star Basin and Tree Tap, Challenger on
   61, 62 and 210, and the recheck notes) → `trailReviews.json` and `$W/recheck.json`. Both only add a review
   for a trail no person has decided; today every one of these 23 trails has the reviewer's decision, so the
   file comes back unchanged. `steps.py person` then checks that the person's reviews are exactly as before.
8. **Review page**: `refresh_review_data.py`, `steps.py hints` (label positions for trails with no proposal),
   the page (`tools/trailmap/review/index.html`, titled Okemo Trail Check) and `map.jpg` → `$W/review/`, ready to
   publish as in the playbook's step 4.
9. **Overlays**: `npm run -s trails:apply -- --resort okemo` → `trailPaths.json` (20 reviewed lines, 104
   proposed, 4 markers: 3 reviewed and Broken Arrow).
10. **Check**: `pdf_symbols.py --check` → `$W/symbols.json` (128 symbols) and "120/127 trails have a PDF symbol
    matching their difficulty by the label".

## Files

| file | role |
|---|---|
| `regen.sh` | the rebuild above |
| `decisions.py` | Claude's hand-made decisions, as data: `TRAILS_TS` (by-hand trail-list edits), `UNNAMED`, `SPLITS`, `TRACE_FIXES`, `MARKERS` / `MARKER_NOTE`, `LINES`, `MARKER_RECHECK` / `RECHECK`, `REVIEWS_NOTE` |
| `steps.py` | applies each group of `decisions.py` at its step (`trails`, `unnamed`, `split`, `trace`, `reviews`, `hints`) and checks a person's reviews (`person`); these were one-off scratch edits, now recorded |
| `readings/result_0.json` … `result_5.json` | the six tile readers' outputs (`prompts/0-new-map.md`): a name or verdict for every piece they saw, and every printed label with its symbol, glade icon and area; a column of tiles each (the first reader two: `okemo-readers.json`'s groups) |
| `readings/result_overrides.json` | not a reader's: Claude's reading of pieces 254 and 255 as TOMAHAWK PARK (`certain`) |
| `readings/trace_0.json` … `trace_4.json` | the five trace readers' outputs (`prompts/4-trace.md`), 22 trails; `trace_1.json` as its reader wrote it (Turkey Shoot on part of 210; `steps.py trace` points it at the cut piece) |
| `checks/pieces_overlay.py` | every piece on the map and six zoomed quarters: the extraction check |
| `checks/piece_crop.py` | a crop around given pieces, each tagged with its id: the crops that settled 239, the Tomahawks, the roads, Turkey Shoot's split |
| `checks/symbol_sheet.py` | contact sheets of every symbol `pdf_symbols.py` found |
| `checks/symbol_crops.py` | every diamond trail's label and symbol on one sheet: the single-vs-double check |
| `checks/reader_symbols.py` | each trail's difficulty against the PDF's symbols by every reader's label report |
| `checks/audit_sheets.py` | overlay crops on sheets: the random audit, the 23 pre-filled trails, the 3 trails the reviewer edited |

Elsewhere: `tools/trailmap/runs/okemo-readers.json` and `okemo-trace.json` are the args the two workflows ran
with (paths in `work/okemo/`, which `regen.sh` fills with the same tiles and source image). Generated:
`src/data/resorts/okemo/{trails.ts,linePolylines.json,trailProposals.json,trailPaths.json}`, never edited by
hand. `trailReviews.json` holds the person's 23 decisions (no `"by": "claude"`): an input, kept and checked,
never deleted. The scratch scripts `symbols_from_pdf.py` and `check_symbols.py` became
`tools/trailmap/pdf_symbols.py` (same 128 symbols); the readers' own crop and result-writing scripts are not
kept (their outputs are).

## Nuances of this map

- **Layers**: page 2 is one painted raster (1485 x 995 px, plus a few small icon images) with every trail line,
  symbol and name as vectors on top. The names are outlined glyphs: the page's only text (24 words) is the
  orange park names, Hotdog Hill, Snow Tubing, the carpet numbers and the partners' heading. That is why readers
  named the pieces (`tools/trailmap/pdf_glyphs.py`, written later for Keystone, could be tried on the glyphs).
- **Strokes**: trails are 0.74 pt strokes in green (0.05,0.53,0.26), blue (0.21,0.33,0.65) and black
  (0.01,0.02,0.02); terrain-park lines 0.74 pt orange (0.96,0.51,0.12); lifts and carpets 1.11 pt red
  (0.93,0.12,0.15); the brown loop by Jackson Gore is the Timber Ripper coaster. The legend's hatching is 1.0 pt
  black, kept out with `--max-width 0.8`. A closed loop under 10 pt (a charging-station icon in the legend) came
  out as a piece: `extract_pdf_vectors.py --max-icon` (default 10) was added for it. No piece lies in the legend,
  lift-stats or dining panels printed on the map.
- **Legend** (also in `okemo-readers.json`): difficulty = line colour plus the symbol by the name (circle,
  square, diamond, two diamonds). Names are capitals in the trail's colour with a white halo, along or beside the
  line, often rotated. Glades are shaded bands (blue-violet: square; dark grey: one or two diamonds) with the name,
  the symbol and a tree icon in a box; the thin lines inside a band are that glade's. Not trails: yellow slow
  zones, salmon closed areas, grey-hatched race areas, light-green family learning zones, lilac ski-school
  patches, the smiley Kids Adventure Zones (Red Fox Woods, Fisher Cat Slide), Snow Tubing, the lodge and base
  boxes, the grey roads and condo streets.
- **Difficulty**: every glade prints its symbol (unlike Stowe: no glade default). Terrain parks print an orange
  pill and no symbol, so they take `seed_roster.py`'s default, blue: Gordon's Garden, Halfpipe, Progression Park,
  The Zone, Tree Tap, Tomahawk Park. Easy Street prints no symbol (green from its line). Fairway's circle is drawn
  as another shape, so `pdf_symbols.py` misses it (read as a circle by both readers). 42 green, 48 blue, 29 black,
  9 double-black.
- **Areas**: Okemo Mountain is the main mountain, left and centre, under OKEMO MOUNTAIN PEAK (South Face, Glades
  Peak, the summit, the Solitude side, the Clock Tower base); Jackson Gore is the right-hand mountain, from the
  JACKSON GORE JUNCTION sign east. 108 and 20 trails.
- **TOMAHAWK is printed twice**: a blue-square trail down to Express Lane (117, 118) and an orange park section
  below it (254, 255). The second is its own trail, Tomahawk Park (`TRAILS_TS`, `result_overrides.json`).
- **Piece 239**, a short green spur from Sweet Solitude (137) to the tops of Upper Sapphire and Tomahawk, has no
  label: `_unnamed`, no overlay.
- **Piece 210** runs from Buckhorn down to Countdown, but Turkey Shoot (238, along its two-line label) joins it
  half way: its upper curve is Challenger's lead-in, the lower part Turkey Shoot's (cut at 1599, 552). The
  reviewer then extended Turkey Shoot up the curve too, so the two share 210's top.
- **Names printed with no line** (not glades): 9. Six are runs the trace readers drew as stretches along the
  painted slope by their label (Switchback, Sundog, Scooter, Drop Off, Sidekick, Rt. 103); three are areas with
  no run, so markers at the label (Galaxy Bowl and Bright Star Basin, carpet learning areas; Tree Tap, a small
  park). Broken Arrow, a glade printed with no line, is an automatic marker.
- **Confidence**: readers worked by column, so most pieces had one reader. `aggregate_readings.py` caps a trail at
  its readers' own confidence (added for Okemo): 9 trails went medium/low that way, Tomahawk Park was medium from
  the overrides, and Challenger went medium after the split (readers had called 210 Turkey Shoot).
- **Trace pass** (22 trails: the 9 with no line, the 10 medium/low ones before the split, Tomahawk, and Mountain
  Road / Fast Track for their boundaries with Lower Mountain Road / Inn Bound), plus Challenger: 23 trails
  pre-filled for the review.
- **The person's review** (2026-09-30, 11:06-11:10 UTC, imported with `npm run reviews:import`): all 23
  decided; 20 saved as pre-filled; Turkey Shoot extended up 210's curve, Mountain Road's drawn end moved west to
  where Lower Mountain Road starts by Green Link, and Fast Track's stretch along its label redrawn. The markers
  kept their label positions (the import keeps a stored `labelAt`). The 105 auto-accepted trails were not
  reopened. The committed file is exactly that export imported over Claude's pre-filled reviews (checked).

## Checks done

- Extraction: the whole map on zoomed crops with the pieces drawn on (`checks/pieces_overlay.py`): every drawn
  trail line covered; every one of the 256 pieces got a reader's name or verdict.
- Symbols, by a second method: `pdf_symbols.py --check` (regen step 10): 128 symbols (45 circles, 45 squares,
  29 diamonds, 9 double diamonds), 120 of 127 labelled trails have one of their type by the label; the other 7 are
  the 6 printed with no symbol and Fairway. `checks/reader_symbols.py` gives the same 7. Every diamond trail on
  `checks/symbol_crops.py`'s sheet: 29 single and 9 double, all as read.
- Overlays on crops (`checks/audit_sheets.py`): a random 16 of the auto-accepted trails, all on their own labelled
  line along the full run; all 23 pre-filled trails before the review; the 3 trails the reviewer edited, with
  their neighbours, after the import.
- Hover check (`tools/trailmap/hover_check.cjs --resort okemo`): 376/376 after the review (2026-09-30), 100%
  after `trails:apply`'s 2026-10-06 change (which redrew joins in Rum Run, Searle's Way and Sunset Strip), and
  376/376 again on 2026-10-07.
- This folder (2026-10-07): `IMAGES=1 regen.sh` from an empty work folder, then again with it filled, leaves
  every committed Okemo file byte for byte unchanged; run on an empty review file, the recorded steps reproduce
  Claude's pre-review `trailReviews.json` (commit 74035aa) but for its timestamps, `recheck.json`, and the
  review page's data; the tiles, `index.json`, `labels.json` and the diamond-check sheets match the originals.

## A new season's map

A new PDF changes the piece ids, so the readings and decisions here don't carry over. `regen.sh` stops on its
SHA-256. Then:

1. Save it as `$OKEMO_WORK/okemo.pdf`, tally its stroke colours and widths and draw each class on a blank page
   (playbook step 1), and fix the URL, the SHA-256 and the extraction flags in `regen.sh` (colours, `--clip`,
   widths). `TILES=1 FORCE=1 regen.sh` then writes its pieces and tiles and stops before the data. If its pieces
   are the old ones (a re-export of the same artwork: compare `$W/pieces.json` with `linePolylines.json` before
   the split), the readings still fit: run `regen.sh` and check the git diff. Otherwise:
2. Consider reading the outlined names with `pdf_glyphs.py` and matching them to the pieces with
   `pdf_resort.py` (Hunter's route) instead of readers. With readers: write the legend, areas and column groups
   into `tools/trailmap/runs/okemo-readers.json`, run the `trailmap-readers` workflow (the owner opts in; it writes
   `work/okemo/tiles/result_*.json`), and put those in `readings/` in place of the old ones. Check the symbols
   (`pdf_symbols.py --check`, `checks/symbol_crops.py`) and the trail list on crops, and redo `decisions.py` from
   scratch (names printed twice, unnamed connectors, splits, markers), each settled on a crop.
3. Aggregate, then the trace pass for the trails with no line and the medium/low proposals: a new
   `tools/trailmap/runs/okemo-trace.json`, the `trailmap-trace` workflow (it writes `work/okemo/trace/`), its
   `trace_*.json` into `readings/`.
4. Pre-fill and publish the review page (`$W/review/`), have a person review, `npm run reviews:import`,
   `trails:apply`; audit on crops (`checks/`) and run the hover check.

What carries over: only a person's reviews, and only for trails the new map draws as before. A review lists
piece ids, so its pieces are first mapped to the new ids by position; a trail drawn differently goes back to the
review page. Never delete `trailReviews.json` or a person's entry in it: `trails:apply` draws every reviewed
trail, so a trail the new map no longer prints is marked "Not on this map" on the review page.
