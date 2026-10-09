# Sugarbush's trail data pipeline

Sugarbush's 2025-26 map is a PDF whose trail lines are vector strokes, but whose
names are outlined glyphs (no text). So the pieces come straight from the
strokes, and five parallel readers (Claude sub-agents) named every numbered
piece and every printed label on zoomed tiles. Their readings are the record:
a re-run of the readers would not give the same answers, so they are kept in
`readings/`, and `regen.sh` rebuilds every Sugarbush file from the PDF, the
readings and the decisions taken on crops, byte for byte.

## Source

- **PDF:** <https://links.imagerelay.com/cdn/1980/ql/7d66b14e89414d4cb778d19f33660efc/2025-26-Sugarbush_Trail_Map.pdf>
  (`2025-26-Sugarbush_Trail_Map.pdf`, linked from sugarbush.com's terrain and
  maps page), the 2025-26 winter map: 15,554,442 bytes, SHA-256
  `75452599716a0d2d616e94566a5bc476db185d3e28589a686bd081c7d53e0f50`, fetched
  2026-09-30 and again 2026-10-07 (unchanged). Plain curl works (`regen.sh`
  sends a browser user agent).
- One page, 1237.77 x 851.46 pt: a James Niehues painting (one 6933x4800
  raster) under every trail line, label and symbol as vectors.
- **Map image:** the whole page rendered at 3.5 px/pt, 4333x2981, saved as
  JPEG quality 88 by `extract_pdf_vectors.py --image` (`IMAGES=1`). No CDN
  image is used.

## Rebuild

```bash
tools/trailmap/resorts/sugarbush/regen.sh            # src/data/resorts/sugarbush/ (about 20 s)
IMAGES=1 tools/trailmap/resorts/sugarbush/regen.sh   # also public/maps/sugarbush.jpg
```

Working files go to `$SUGARBUSH_WORK` (default `work/sugarbush`, git-ignored);
the PDF is downloaded there if missing (or put it there by hand). The script
stops if the PDF's SHA-256 is not the one above (`FORCE=1` goes on anyway).
Needs `pip install pymupdf pillow` and the repo's `npm ci`.

## Pipeline (regen.sh)

1. `curl` → `$W/sugarbush.pdf`; SHA-256 check.
2. `extract_pdf_vectors.py`, three passes on one grid
   (`--page 0 --clip 0,0,1237.77,851.46 --scale 3.5`) → `$W/linePolylines.json`
   (114 pieces, the ones the readers saw):
   - 0.75 pt strokes in blue `0.08,0.51,0.78`, black `0.14,0.12,0.13` and green
     `0.08,0.65,0.32`, `--max-width 0.8` (lifts and the boundary are red),
     `--filled` (Out Road, piece 52, is a filled path with a stroke): 111
     pieces; with `IMAGES=1` also `--image public/maps/sugarbush.jpg`;
   - `--color black=0.0,0.0,0.0 --max-width 0.8 --append`: Lwr Exterminator (111)
     and Black Diamond Rush (112) are drawn in pure black;
   - `--color black=0.14,0.12,0.13 --min-width 0.9 --max-width 1.1 --append`:
     Hi & Lo Road (113) is 1.0 pt.
   Then the same clip and scale rendered losslessly → `$W/sugarbush_source.png`.
3. `render_tiles.py` → `$W/tiles/` (26 tiles at 1.7x and `index.json`; the
   same bytes the readers read); `readings/result_*.json` copied next to them.
4. `extract_pdf_vectors.py --color blue=… --color green=… --append --outlined
   --min-length 30`: Snowball, drawn as a filled outline (piece 114; its name is
   `readings/result_extra.json`). Then `decisions.py`: `split_pieces.py` cuts
   the three SPLIT pieces (→ 115, 116, 117 and `$W/tiles/result_splits.json`)
   and `_unnamed` / `_source` are written → `src/data/resorts/sugarbush/linePolylines.json`
   (118 pieces).
5. `seed_roster.py --readings "$W/tiles/result_*.json" --areas
   'lincoln-peak=Lincoln Peak=3975,mt-ellen=Mt. Ellen=4083'` → `trails.ts` and
   `$W/labels.json`; `header.txt` replaces its header comment;
   `aggregate_readings.py --labels` → `trailProposals.json` (and
   `$W/review_data.json`, the review page's data); `npm run trails:apply` →
   `trailPaths.json`.

## Files

| file | role |
|---|---|
| `regen.sh` | the whole rebuild, every flag as used on 2026-09-30 |
| `readings/result_0.json` … `result_4.json` | the five tile readers' outputs (trailmap-readers workflow, `tools/trailmap/runs/sugarbush-readers.json`): a name or verdict (LIFT, NOT_A_TRAIL, SPLIT, …) for every piece on their tiles, and every printed label with its symbol, glade flag, area and position |
| `readings/result_extra.json` | Claude's reading of piece 114 (Snowball, which the readers saw on the image but had no piece for) |
| `decisions.py` | settled on crops: the three splits (where and which names), the two unnamed connectors (98, 106), the `_source` note; applies them |
| `header.txt` | the comment at the top of `trails.ts` (written by hand after the seeding) |
| `checks/stroke_tally.py` | stroke colours/widths and fill colours of the PDF: how the trail classes were chosen |
| `checks/uncovered_strokes.py` | every trail-coloured stroke with no piece on it (how the pure black, 1.0 pt and filled ones were found) |
| `checks/piece_crop.py` | given pieces drawn on a crop of the source: the split and unnamed checks |
| `checks/symbol_sheet.py` | every printed label of the given (or every black) trail on a crop: the diamond check |

Generated (never hand-edit): `src/data/resorts/sugarbush/{linePolylines,trailProposals,trailPaths}.json`
and `trails.ts`. Sugarbush has no `trailReviews.json` (see "Checks done").

## Nuances of this map

- Difficulty is both the line colour and the symbol printed just before the
  name: green circle, blue square, black diamond, two small black diamonds
  (expert). A snowflake before a name marks snowmaking, not a difficulty.
- Names are black capitals with a white halo along or beside their line,
  outlined (no text), so the readers read them. The diamonds are drawn inside
  the outlined label glyphs: `pdf_symbols.py` finds the circles and squares
  but no diamonds.
- Lifts are red lines with white text; short red lines with a skier icon are
  surface lifts and carpets; red dashes are the boundary; orange pills are
  park features (a name printed on one is still a trail; Slowpoke, the one a
  reader reported on a pill, is flagged as a terrain park); light-yellow
  shading is a slow zone. Lodges are dark boxes with white icons.
- The odd lines: Lwr Exterminator and Black Diamond Rush in pure black,
  Hi & Lo Road at 1.0 pt, Out Road a two-tone road (a green-filled path with a
  blue stroke edge: its piece is the blue edge, class `blue`; the readers named
  it from its label, green circle), and Snowball a thin filled outline (a
  stroke converted to a fill). `--outlined` takes the outline's first side up
  to its end cap, and only in blue and green: black glyphs are fills too.
  Check every trail-coloured stroke against the pieces
  (`checks/uncovered_strokes.py`) before trusting an extraction; a line drawn
  as a fill only shows on the tiles.
- Three strokes run on past the next trail's symbol (readers' SPLIT): Jester /
  Allyn's Traverse at (800,1234), Northstar / Lwr Northstar at (3581,1520),
  Crackerjack / Lower Crackerjack at (3598,1996). Two short connectors print no
  name (98: a black link from Lift Line to the Rumble line; 106: an arrowed blue
  spur from Lower Downspout to the Castlerock Double base).
- Glades ("wooded areas", red cross-hatched patches with a one- or two-tree
  icon) have no line and no symbol. They default to black (Sugarbush rates
  wooded areas as their own category; the map has no legend for the icons) and
  are markers at their label (27). Murphy's Glade and Sugarbear Forest are
  drawn trails with symbols, not glades. Lower Snowball is also printed on the
  wooded strip beside it.
- Riemergasse prints only a snowflake: green from its line, and its proposal is
  medium (one reader, medium confidence); `trails:apply` uses it.
- Names keep the map's spelling (Lwr, Rd, Water Fall); initials keep their dots
  (F.I.S., Lower F.I.S.: `seed_roster.py`'s rule for them was added for this map).
- 138 trails (Lincoln Peak 87, Mt. Ellen 51): 25 green, 48 blue, 30 black,
  8 double black, 27 glades; 111 lines and 27 markers. Sugarbush's own count is
  26/47/30/8 and 28 wooded areas.

## Checks done

- Extraction: every trail-coloured stroke has a piece (`checks/uncovered_strokes.py`
  prints only `done`), and the whole map was looked at with the pieces drawn on.
- Readers: 5 readers over 26 tiles (grouped by tile column, the sparse Slide
  Brook and far-right columns joined to their neighbours), ~1.2M tokens,
  ~53 min. Their SPLITs and the two unnamed pieces were settled on 3x crops
  (`checks/piece_crop.py`, crops named in `decisions.py`).
- Symbols: every single and double diamond on a zoomed crop of its label
  (`checks/symbol_sheet.py out.png black`): 30 single, 8 double, all as read.
  `pdf_symbols.py $W/sugarbush.pdf --page 0 --clip 0,0,1237.77,851.46 --scale 3.5
  --circle 0.08,0.65,0.32 --square 0.08,0.51,0.78 --diamond 0.14,0.12,0.13
  --max-diamond 3.2 --out $W/pdf_symbols_all.json` gives the circles and
  squares only.
- No human review (the owner's call): every overlay was checked on
  full-resolution region crops with each overlay tagged with its name
  (`region_audit.py --image $W/sugarbush_source.png --paths src/data/resorts/sugarbush/trailPaths.json
  --trails src/data/resorts/sugarbush/trails.ts --grid 4x2 --area 200,840,4140,2440`, and `--box`
  zooms on 800,1000,1220,1260, 1560,940,1880,1500 and 3095,1580,4200,2500).
- Hover check (`tools/trailmap/hover_check.cjs --resort sugarbush`): 360/360
  on 2026-09-30.
- This rebuild (2026-10-07): from an empty work folder, every committed file
  and the map image came out byte for byte, and so did the intermediate files
  of 2026-09-30 (the tiles and their index, `labels.json`,
  `result_splits.json`, `review_data.json`, the source PNG).

## A new season's map

Nothing carries over from the readings: piece ids, tiles and labels all change
with a new PDF. Redo:

1. Put the new PDF's URL and SHA-256 in `regen.sh`. Tally its strokes
   (`checks/stroke_tally.py`), set the extraction passes, and run
   `checks/uncovered_strokes.py` until every trail-coloured stroke has a piece.
   Look for lines drawn as fills.
2. Run `regen.sh` up to step 3 (it renders the tiles), then the readers: the
   `trailmap-readers` workflow (the playbook's Part 4, "Naming pieces with parallel AI readers") with
   `tools/trailmap/runs/sugarbush-readers.json`, its tile groups updated to the
   new `index.json` (one group per column) and its legend checked against the
   new key. Their `result_*.json` replace `readings/`.
3. Settle what the readers flag on crops (SPLIT, UNKNOWN, medium/low, pieces
   with no name): `decisions.py` (splits, unnamed connectors), a reading like
   `result_extra.json` for a line the extraction missed, `header.txt`.
4. Check every diamond (`checks/symbol_sheet.py out.png black`), audit every
   overlay (`region_audit.py`, `symbol_audit.py`, the playbook's Part 4) and run the
   hover check.

A person's reviews, if any are ever added in `trailReviews.json` (entries
without `"by": "claude"`), carry over for trails whose line is unchanged; the
regen never writes that file.
