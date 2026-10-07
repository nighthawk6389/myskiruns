# Whiteface's trail data pipeline

Whiteface's 2025-26 map is a PDF that has everything as vectors over one
painting: the trail lines are strokes and every trail name is real text in its
trail's colour, with its symbol beside it. So the pieces come straight from the
strokes, the trail list straight from the text, and each name was matched to
the line it is printed along or in a gap of; about 35 pieces were settled on
zoomed crops, with four strokes cut where two trails share one. No readers and
no review page. This was the first map built this way (2026-09-30). The
scripts here are the ones that built it, moved from the session's scratch
folder; `regen.sh` runs them in order and rebuilds every committed Whiteface
file byte for byte.

## Source

- **Edition:** "Whiteface Mountain Trail Map 2025-26" (the PDF's title; made
  2025-11-17 in Illustrator CS6). One page, 1724.88 x 1434.24 pt.
- **Where from:** whiteface.com links
  `https://whiteface.com/wp-content/uploads/sites/3/2025/12/Whiteface-Mountain-Trail-Map-2025-26.pdf`
  from `https://whiteface.com/mountain/trail-map/`, but the site sits behind
  a Cloudflare bot check: curl gets a 403 "Just a moment..." page, and so does
  headless Chromium through `tools/trailmap/fetch_pdf.cjs` (tried again
  2026-10-07). skimap.org has the map (map 37629, listed under 2025 on its
  Whiteface page): `https://skimap.org/skimaps/view/37629` redirects to
  `https://files.skimap.org/3zz4xytnhpior9rwxwsvb0erylv9.pdf`, which plain
  curl downloads. Its bytes could not be compared with whiteface.com's copy;
  title and date say it is this season's map.
- **File:** 14,473,852 bytes, SHA-256
  `16ec62c740f0b2acba7ac243b854ab86602ec8bf7558eca4711b3b4d311ed018`.
  `regen.sh` downloads it to `$WHITEFACE_WORK/whiteface.pdf` if it isn't
  there (a copy put there by hand is used as is) and stops if the hash differs.
- No CDN image: the map image is the PDF page rendered at 2.2 px/pt.

## Rebuild

```bash
tools/trailmap/resorts/whiteface/regen.sh            # rebuild src/data/resorts/whiteface/ (about 6 s)
IMAGES=1 tools/trailmap/resorts/whiteface/regen.sh   # also public/maps/whiteface.jpg (about 13 s)
FORCE=1 tools/trailmap/resorts/whiteface/regen.sh    # run on a PDF with another SHA-256 (a new edition: see the end)
```

Working files go to `$WHITEFACE_WORK` (default `work/whiteface`,
git-ignored). Needs `pip install pymupdf pillow` and node (for
`trails:apply`). Re-run with nothing changed, it leaves every committed file
as it was. A person's reviews in `trailReviews.json` are kept and outrank
everything; Claude's are rebuilt (`traces_to_reviews.py --replace-claude`),
keeping their timestamps when unchanged. Never hand-edit the generated files
(`trails.ts`, `linePolylines.json`, `trailProposals.json`, `trailPaths.json`,
Claude's reviews): change `decisions.py`, the cuts in `regen.sh` or
`header.txt` and re-run.

## Pipeline

`$W` is `$WHITEFACE_WORK`, `D` is `src/data/resorts/whiteface`.

| step | script | output |
|---|---|---|
| 1 | curl (skimap.org), SHA-256 check | `$W/whiteface.pdf` |
| 2 | inline in `regen.sh`: the page at 2.2 px/pt | `$W/map.png` (3795x3156); with `IMAGES=1` also `public/maps/whiteface.jpg` (quality 82, progressive) |
| 3 | `tools/trailmap/extract_pdf_vectors.py --scale 2.2 --color blue=0,0.46,0.74 --color black=0.14,0.12,0.13 --color green=0,0.52,0.27 --max-width 1.6` | `D/linePolylines.json`: 162 pieces (copied to `$W/linePolylines_before_split.json`) |
| 4 | `tools/trailmap/split_pieces.py`, four `--split`s | `D/linePolylines.json`: 166 pieces (`_splits`); `$W/reading_splits.json` (not used further: `decisions.py` names the parts) |
| 5 | `labels.py` | `$W/wf_labels.json`: every text object |
| 6 | `build.py` | `$W/wf_assign.json`: the trail labels with symbols, and each piece's automatic name(s); report in `$W/build.log` |
| 7 | `reading.py` (+ `decisions.py`) | `$W/tiles/result_whiteface.json` (one reading), `$W/wf_gaps.json` (label-gap stretches, glade markers) |
| 8 | `tools/trailmap/seed_roster.py --areas 'whiteface=Whiteface Mountain=4867'`, then `header.txt` replaces its header | `D/trails.ts`, `$W/labels.json` |
| 9 | `tools/trailmap/render_tiles.py` | `$W/tiles/` (tiles and `index.json`, whose image size and zoom `aggregate_readings.py` reads) |
| 10 | `annotate.py` | `D/linePolylines.json`: `_source`, `_unnamed` |
| 11 | `tools/trailmap/aggregate_readings.py` | `D/trailProposals.json`, `$W/review_data.json` |
| 12 | `stretches.py` | `$W/trace_gaps.json`: 52 trails' pieces plus their stretch |
| 13 | `tools/trailmap/traces_to_reviews.py --replace-claude` | `D/trailReviews.json` (52 reviews by Claude), `$W/recheck.json` |
| 14 | `npm run -s trails:apply -- --resort whiteface` | `D/trailPaths.json`: 52 verified, 44 proposed, 2 label markers |

On 2026-09-30 the trail list's header was replaced last, after
`trails:apply`; `regen.sh` does it right after `seed_roster.py` (nothing in
between reads the header). Every intermediate file above came out identical
to that day's.

## Files

| file | what it is |
|---|---|
| `regen.sh` | the whole rebuild (download, hash check, image, every step above) |
| `labels.py` | the PDF's text objects with layer, colour and character positions (scratch: `wf_labels.py`) |
| `build.py` | trail labels (merging fragments), symbols, and the automatic name-to-piece match (scratch: `wf_build.py`) |
| `decisions.py` | what the crops settled: `OVERRIDE` (piece id: name), `UNNAMED`, the map's typo (`FIX`, `PRINT_FIX`) (scratch: the top of `wf_reading.py`) |
| `reading.py` | automatic names + decisions as one reading; the label-gap stretches (scratch: `wf_reading.py`) |
| `annotate.py` | `linePolylines.json`'s `_source` and `_unnamed` notes |
| `stretches.py` | the stretches as traces for `traces_to_reviews.py` |
| `header.txt` | the comment at the top of `trails.ts` |
| `checks/zoom_pieces.py` | zoomed map crops with every piece tagged `id:NAME` (`id?` none, `id!` two) |
| `checks/sheet.py` | crops side by side on one sheet |
| `checks/pdf_crop.py` | one spot rendered sharp from the PDF |
| `checks/fragments.py` | the labels printed in fragments, on one sheet |
| `checks/path_of.py` | which PDF path each piece came from |
| `checks/diamond_sheet.py` | every black name's label with the difficulty it got |
| `checks/audit.sh` | the 11 region crops every overlay was audited on (`region_audit.py`) |

The decisions are kept by piece id, not as points: the pieces come from the
PDF's strokes in drawing order, so the ids don't move unless the PDF or the
extraction flags change (the hash check guards the first).

## Nuances of this map

- **Layers.** The painting is one embedded image (4788x4000 px, about
  2.8 px/pt). Everything else is vector, on named layers: Green, Blue and
  Black Trails; Lifts; Green, Blue and Black Names; Lift Names; Icons
  (lodges, elevations, signs). The map image is the page rendered at
  2.2 px/pt (3795x3156; 2.5 was tried first): 3.8 MB as a quality-82 JPEG.
- **Lines.** 1.43 and 1.5 pt strokes in blue (0,0.46,0.74), black
  (0.14,0.12,0.13) and green (0,0.52,0.27). Lifts are red strokes
  (0.89,0.12,0.15) of the same widths, left out by their colour;
  `--max-width 1.6` is there because the extractor's default (1 pt) would
  drop every trail stroke.
  A piece's class is its stroke colour, not its layer: three blue strokes sit
  on the Black Trails layer (piece 20, Lower Mackenzie; 31 and 32, On Ramp,
  whose name is blue on the Black Names layer too) and one on Blue Names
  (118, Bobcat Glades). Glade lines are dashed (5.5 to 6 pt dashes), and so
  is Rand's Last Stand's; the extractor takes them like solid ones. Every
  piece is a PDF path of its own (`checks/path_of.py`: 162 paths for 162
  pieces): where a name interrupts a line, the two sides are separate paths.
- **Names.** Real text (CgBernhardtBd, 9 to 10.5 pt) on the three name
  layers, in the trail's colour, so the colour is the difficulty. Each name
  is drawn twice on the same spot, first in another colour (0,0.6,0.86 for
  blue names, 0.01,0.3,0.63 for black, 0,0.65,0.32 for green), then in the
  trail colour; `build.py` keeps the trail-colour copy (`FILL`), on the
  three name layers. Lift names, lodges and elevations are on other
  layers and stay out. 102 labels give 98 names (Bobcat Glades, The
  Wilmington Trail, Boreen and Bobcat are printed twice).
- **Names in a gap of their line.** Most names sit in a gap of their own
  line: the line runs up to the symbol, the name follows, and the line
  resumes after it. So a name printed beside a piece names it, and failing
  that, the pieces that end at either end of its text (within 12 pt) and run
  on along it: 13 of the 102 labels matched the first way, 76 the second and
  13 neither (seven glade labels, The Slides, Upper Thruway, John's Bypass,
  Off Broadway, Mixing Bowl, Round-a-bout: settled on crops, or a stretch). Where
  fewer than half a name's characters lie within 30 px of its pieces, the
  overlay also gets a stretch through the name's own characters (52 trails),
  so a trail whose label is all of its line still has one: five trails have
  no piece at all and are drawn by their stretch alone (John's Bypass, Off
  Broadway, Round-a-bout, Upper Thruway, Yellow Dot). A name printed twice
  gives two stretches, which must lie over 400 px apart (or `trails:apply`
  joins them). Yellow Dot is printed on two lines, so its stretch runs
  through "Yellow", back, and through "Dot".
- **Fragments.** A second line or the end of a curved name is its own text
  object ("Glades", "Cut", "Dot", "Bridge", "Loop"): joined to the nearest
  label of the same colour. "Switchbacks" is printed once between "Upper" and
  "Lower" and goes onto both. Checked on `checks/fragments.py`'s sheet.
- **Symbols.** Fills on the name layers beside each name: green circle (four
  curves), blue square, black diamond (four lines), double diamond (eight
  lines), each given to the nearest label end of its colour within 25 pt.
  Five names get no symbol (none within 25 pt: Ladies' Bridge, Crossover
  Loop, Danny's Bridge, Ilmar's Alley, Fox Island) and are rated by their
  colour, as every name is anyway (the symbols only tell a double diamond
  from a single one). One blue square has no name near it: it sits on The
  Follies' line (piece 47), and `build.py` says so. Seven names have a
  double diamond and are double-black: Sugar Valley,
  Deer Valley, Slide View and Cloudsplitter Glades, Rand's Last Stand, The
  Slides and Slide Out. The trail list: 23 green, 46 blue, 22 black, 7
  double-black.
- **Glades** are the eight names that say "Glades". Six have a dashed line
  beside the name (High Country 23, Sugar Valley 42, Deer Valley 43, Slide
  View 44 and 45, Hoot Owl 93, Bobcat 94 and 118); the match missed four of
  them, settled on crops. Two have no line at all (10th Mt. Division and
  Cloudsplitter Glades): markers at the label (`aggregate_readings.py` marks
  a glade with no pieces).
- **A typo:** the map prints "High County Road"; NY DEC's name for the 2022
  trail is High Country Road (`FIX`, `PRINT_FIX`).
- **Four strokes carry two trails** and are cut (`split_pieces.py` in
  `regen.sh`; the upper part keeps the id): Cloudspin / Niagara (piece 1 at
  2201,855, new 162), The Slides / Slide Out (34 at 2740,836, new 163), Riva
  Ridge / Paron's Run (51 at 2331,670, new 164), Ilmar's Alley / Lower
  Northway (69 at 1818,946, new 165).
- **Settled on crops** (`decisions.py`): of 55 entries, 20 confirm the
  automatic name, 8 change it (Victoria, not Summit Express, on 61; Ladies'
  Bridge, not Lower Gap, on 106; Crossover Loop, not Lower Switchbacks or
  Weber's Way, on 55; Weber's Way, not Yellow Dot, on 56; High Country Road,
  not 2200 Road, on 116; Brookside, not Danny's Bridge, on 109; Lower Empire,
  not Empire Cut, on 71; Bobcat Chute, not Loon, on 126) and 27 name pieces
  the match left unnamed: among them the five lines of The Slides (34-38),
  fanning out up the summit's face, the lines of four glades, two of
  Mountain Run's pieces, 1900 Road and Lower Parkway. Piece 130, a green
  connector from Moose down to Porcupine Pass, prints no name: `UNNAMED`.
- **One area** for the whole mountain (`whiteface`, Whiteface Mountain,
  4,867 ft: the summit's elevation on the map).

## Checks done

On 2026-09-30:

1. The automatic match's report (`build.py`) and its pieces on crops at three
   zooms (`checks/zoom_pieces.py`, run from the scratch folder as
   `piece_regions.py` for the first set):
   ```bash
   C=tools/trailmap/resorts/whiteface/checks; W=work/whiteface
   Z=1.25 python3 $C/zoom_pieces.py $W/pr 1200,480,2000,1150 1900,480,2600,1150 2500,480,3520,1400 \
     1150,1100,1950,1800 1850,1100,2600,1800 500,1700,1400,2850 1300,1750,2150,2600 2050,1650,3000,2850 \
     2500,1350,3520,2300
   Z=2.0 python3 $C/zoom_pieces.py $W/zc 2500,450,3060,860 2150,580,2520,1030 1780,760,1980,1070 \
     1450,1180,1900,1700 1800,1230,2060,1620 1180,1780,1700,2020 1400,2150,1900,2700 2080,2150,2520,2600 \
     1600,1690,1780,2000 600,2330,880,2620 2650,1200,3450,1950
   Z=2.4 python3 $C/zoom_pieces.py $W/zz 2120,820,2280,1120 2130,560,2620,780 1640,760,1960,1080 \
     1900,1180,2100,1480 1780,1150,1900,1330 1560,1250,1900,1420 1650,1330,1800,1520 1850,1450,2080,1680 \
     1380,2050,1650,2350 2000,2050,2300,2450 1600,2450,1850,2700 600,2280,950,2650
   python3 $C/sheet.py $W/sheet_a.jpg $W/zz_0.jpg $W/zz_1.jpg   # b: zz_2-4, c: zz_5-7, d: zz_8-9, e: zz_10-11
   ```
   Those were drawn before the cuts; drawn now, they show the cut pieces.
2. Single spots rendered from the PDF: the label fragments
   (`checks/fragments.py`), the Switchbacks (`checks/pdf_crop.py
   $W/switchbacks.png 2200,693,2486,1034 4.5`) and Victoria
   (`... $W/victoria.png 1860,1150,2120,1480 5`); and `checks/path_of.py`
   (every piece a path of its own).
3. After the build, every overlay on 11 full-resolution region crops, each
   overlay in its own colour and tagged with its name (`checks/audit.sh`).
4. Every black name's label with the difficulty it got, for single vs double
   diamond (`checks/diamond_sheet.py`, 29 labels).
5. The hover check: `npm run build`, `npx vite preview --port 4199` (in its
   own subshell), then `PLAYWRIGHT_PATH=$(npm root -g)/playwright node
   tools/trailmap/hover_check.cjs http://localhost:4199/ --resort whiteface`:
   290/290 hover points show the right name (2026-09-30, and in every
   all-resort run since).

On 2026-10-07 `regen.sh` ran from an empty work folder with `IMAGES=1` and
again with it filled: no change to any committed file. The intermediate
files, the region crops, the diamond and fragment sheets, the Switchbacks
and Victoria renders and `path_of.json` came out identical to 2026-09-30's.

## A new season's map

1. Find the PDF (the trail-map page on whiteface.com; if it is still behind
   the bot check, skimap.org's Whiteface page,
   `https://skimap.org/skiareas/view/295`, lists maps by year). Put it at
   `$WHITEFACE_WORK/whiteface.pdf`, or change the URL in `regen.sh`, and
   record its SHA-256 there.
2. Tally its strokes and text again (colour, width, layer: the commands in
   the playbook's "Pick a route") and check what this map assumes: the three
   trail colours (`--color` in `regen.sh`, `FILL` in `build.py`), the stroke
   widths (`--max-width`), the layer names (`build.py`), the page size
   (`CLIP`), and the 2.2 px/pt scale with its 3795x3156 image size
   (`regen.sh`, `build.py`, `reading.py`).
3. The piece ids will most likely change: empty `OVERRIDE` and `UNNAMED` in
   `decisions.py` and take the `--split`s out of `regen.sh`, then run it with
   `FORCE=1`.
   Read `$W/build.log` (labels with no piece, pieces with two names, pieces
   with none, symbols with no name) and settle each on crops
   (`checks/zoom_pieces.py`, `checks/pdf_crop.py`): record a name in
   `OVERRIDE`, a piece that is no trail in `UNNAMED`, and a stroke carrying
   two trails as a `--split` (re-number the `OVERRIDE` entries of the new
   parts: they are appended after the last id).
4. Check the fragment merges (`TAILS`, "Switchbacks"; `checks/fragments.py`),
   the typo fix, the double diamonds (`checks/diamond_sheet.py`) and rewrite
   `header.txt`.
5. Audit every overlay on crops (`checks/audit.sh`, with boxes covering the
   new map) and run the hover check. Or move the resort onto
   `tools/trailmap/pdf_resort.py` (`pdf_labels.py` labels, decisions as
   points), the shared matcher written after Whiteface.
