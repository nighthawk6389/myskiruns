# Copper Mountain's trail data pipeline

Copper Mountain's 2025-26 main trail map is a PDF with almost no text: nearly every trail name is a set of
filled glyph outlines, most trail lines are strokes converted to filled outlines, and the painting under them is
only about 1.4 px/pt. This folder holds the scripts that turned it into the app's data (128 trails: 104 on their
lines, 24 markers), the hand-made inputs they read (the glyph letter table, the naming decisions settled on
crops, the trail list's header), and `regen.sh`, which rebuilds every committed file byte for byte.

```bash
tools/trailmap/resorts/copper-mountain/regen.sh            # rebuild src/data/resorts/copper-mountain/ (about 20 s)
IMAGES=1 tools/trailmap/resorts/copper-mountain/regen.sh   # also public/maps/copper-mountain.jpg (about 40 s)
```

The scripts were written as one-offs on 2026-10-01 (`cu_*.py` in a scratch folder; each docstring gives its old
name) and moved here on 2026-10-07 with their logic unchanged: only their paths and docstrings changed.

## Source

- **The PDF**: `https://skimap.org/skimaps/view/36383` (skimap.org's Copper Mountain page lists it as
  "Published in 2025, created by James Niehues"); the URL redirects (302) to
  `https://files.skimap.org/xqtssxiuwd29yhyfxeqtdtzxh5nl.pdf`. Plain curl works. It is the resort's own export:
  title "FY26_Main Trail Map_WEB", Adobe Illustrator 29.6, created 2025-11-06 08:43 -07:00, one page of
  1303.44 x 1052.54 pt, 2,206,732 bytes, SHA-256
  `a9a6134263c29bef51e495b9160467da2b2cf0d5b4fe447437b53c04e2cb49bc`. It was fetched on 2026-10-01 with
  `curl -sL -A "Mozilla/5.0 (X11; Linux x86_64) Chrome/124.0"`, and the same file came back on 2026-10-07.
  `regen.sh` records that SHA-256 and stops if the file differs (`FORCE=1` goes on anyway). A copy placed in the
  work folder by hand as `copper.pdf` is used as it is, after the same check.
- **The resort's own link is now a different file.** coppercolorado.com's winter trail map page
  (`/the-mountain/trail-area-maps/winter-trail-map/`; the PDF link is in its Gatsby page data,
  `/page-data/the-mountain/trail-area-maps/winter-trail-map/page-data.json`) links
  `https://cms.coppercolorado.com/sites/default/files/2025-12/FY26_Main%20Trail%20Map_WEB%20%282%29.pdf`
  (plain curl works): a re-export of 2025-12-17, 2,205,905 bytes, SHA-256
  `73a1ca12d33fba411ee204210ba1377e0b268d95cbea6f3d2a2a80d465c057c5`. It drops one label, THE SNOW MAZE (real
  text, not a trail, plus its 11 white halo strokes), so every later drawing is numbered 13 lower. With the one
  drawing number that matters changed (`lines.py` `SKIP_SEQ`: the snow-maze icon, 5866 here, 5853 there) it gives the
  same 126 pieces and the same reading (checked 2026-10-07); unchanged, the icon becomes a 127th piece and every
  later piece id moves, so `decisions.py` no longer fits and `reading.py` stops on its assert. The data here was
  built from the November file. When the session that built it looked for the PDF on 2026-10-01, the
  coppercolorado.com URLs it tried were 404 pages.
- The same page links the Copper Bowl and Spaulding Bowl insets (`FY25_Copper_Bowl.pdf`, `FY25_Spaulding.pdf`,
  2024-10). They are not used: the main map labels Spaulding Bowl, Copper Bowl and Tucker Mountain "SEE INSET",
  and only the names on the main map are in the trail list.
- **No CDN image.** The map image is made from the PDF itself: its vector layer matted over its own painting
  (xref 258, 1817 x 1465 px over the whole page, about 1.39 px/pt), upscaled with Lanczos. No sharper copy of the
  painting turned up.

## Rebuild

```bash
tools/trailmap/resorts/copper-mountain/regen.sh            # data only; makes the map image only if it is missing
IMAGES=1 tools/trailmap/resorts/copper-mountain/regen.sh   # also rewrites public/maps/copper-mountain.jpg
COPPER_MOUNTAIN_WORK=/tmp/cu tools/.../regen.sh            # another work folder (default work/copper-mountain)
FORCE=1 tools/.../regen.sh                                 # go on with a PDF whose SHA-256 differs
```

It runs from anywhere and needs `pip install pymupdf pillow numpy` and the repo's `npm ci` (for
`trails:apply`). With nothing changed it reproduces `src/data/resorts/copper-mountain/*` and
`public/maps/copper-mountain.jpg` byte for byte, from an empty work folder or a filled one. A person's reviews in
`trailReviews.json` (entries without `"by": "claude"`) are kept: `traces_to_reviews.py --replace-claude` rebuilds
only Claude's, and a decision that comes back unchanged keeps its timestamp.

Never hand-edit the generated files (`trails.ts`, `linePolylines.json`, `trailProposals.json`, `trailPaths.json`,
Claude's entries in `trailReviews.json`). To change a trail's pieces, change `decisions.py` (piece id -> name
as printed) and re-run; to fix one trail by hand, add a person's review (the playbook, "To fix one trail").

## Pipeline

Run by `regen.sh` from the repo root, in this order. `W` is the work folder; PDF points unless noted.

| step | script | reads | writes |
|---|---|---|---|
| 1 | `curl` | skimap.org | `W/copper.pdf` (SHA-256 checked) |
| 2 | `tools/trailmap/matte_pdf_layer.py --scale 3.0 --clip 0,150,1303.44,1052.54 --xref 258` | the PDF | `W/map.png` (3911 x 2708) and, with `IMAGES=1`, `public/maps/copper-mountain.jpg` (JPEG q82, optimized, progressive) |
| 3 | `lines.py` | the PDF | `linePolylines.json` (126 pieces: 49 black, 43 green, 34 blue), `W/piece_src.json` |
| 4 | `tools/trailmap/render_tiles.py` | `map.png`, `linePolylines.json` | `W/tiles/` (23 numbered tiles; `index.json` gives `aggregate_readings.py` the image size) |
| 5 | `glyphs.py` | the PDF | `W/glyphs.json` (1860 glyph fills) |
| 6 | `cluster.py` | `glyphs.json` | `W/clusters.json` (115 shapes) |
| 7 | `labels.py` | `clusters.json`, `letters.json`, the PDF | `W/glyph_labels.json` (151 labels), `W/syms.json` (125 symbols) |
| 8 | `tools/trailmap/pdf_labels.py` | the PDF | `W/text_raw.json` (the few names set as real text) |
| 9 | `names.py` | `glyph_labels.json`, `syms.json`, `text_raw.json` | `W/names.json` (134 labels, 128 names, symbols attached) |
| 10 | `build.py` | `names.json`, `linePolylines.json` | `W/assign.json` (each label's pieces, names spread along continuations) |
| 11 | `reading.py` | `names.json`, `assign.json`, `decisions.py`, `linePolylines.json` | `W/tiles/result_copper.json` (the reading), `W/gaps.json` (stretches, markers) |
| 12 | `tools/trailmap/seed_roster.py --areas 'copper-mountain=Copper Mountain=12441'` | the reading | `trails.ts`, `W/labels.json`; then its header is replaced by `header.txt` |
| 13 | inline in `regen.sh` | `decisions.py` | `linePolylines.json` gets `_unnamed` (UNNAMED: none) and its final `_source` |
| 14 | `tools/trailmap/aggregate_readings.py` | the reading, `trails.ts`, `linePolylines.json`, `labels.json` | `trailProposals.json` (104 trails with pieces, 4 glades as label markers), `W/review_data.json` |
| 15 | `traces.py` | `gaps.json`, `labels.json`, `trailProposals.json` | `W/trace_gaps.json` (24 markers, no stretches) |
| 16 | `tools/trailmap/traces_to_reviews.py --replace-claude` | `trace_gaps.json`, `labels.json`, `map.png` (its size) | `trailReviews.json` (24 "no-line" reviews by Claude), `W/recheck.json` |
| 17 | `npm run -s trails:apply -- --resort copper-mountain` | proposals + reviews | `trailPaths.json` (104 lines, 24 label markers) |

The original map image came from `cu_image.py` (2026-10-01 16:02), the same matte written for this one map;
`matte_pdf_layer.py` was made from it that evening, and with these flags it gives a pixel-identical (and
byte-identical) `map.png`, so `regen.sh` uses the shared tool. Its log reports the matte's mean difference from
MuPDF's own render where there are no vectors: 13.51 levels (the smoother upscale).

## Files

| file | role |
|---|---|
| `regen.sh` | the whole rebuild (above) |
| `common.py` | the paths every script shares: this folder, the repo, the work folder (`$COPPER_MOUNTAIN_WORK`), the PDF, the data folder |
| `lines.py` | line pieces: outline fills rasterised and thinned to centre lines, Tucker Mountain's clip-path lines, the few plain strokes (was `cu_lines.py`) |
| `glyphs.py` | every glyph fill in a name colour with its shape signature (was `cu_glyphs.py`) |
| `cluster.py` | glyphs grouped by shape (was `cu_cluster.py`) |
| `labels.py` | shapes -> letters (`letters.json`) -> labels; the difficulty symbols (was `cu_labels.py`) |
| `names.py` | glyph labels + real-text names, mended (`FIX`), filtered (`NOT`), joined across lines (`JOIN`), symbols attached (`MANUAL` for those set apart) (was `cu_names.py`) |
| `build.py` | each label's pieces by position, then names spread along continuations (was `cu_build.py`) |
| `reading.py` | the reading for `seed_roster.py` / `aggregate_readings.py`, stretches and markers; difficulty rules (`ZONE`, `BY_COLOUR`, `PARKS`), display names (was `cu_reading.py`) |
| `traces.py` | stretches and markers -> `traces_to_reviews.py` input (was `cu_traces.py`) |
| `decisions.py` | hand-made: the 26 pieces settled on crops (`CHECKED`, piece id -> name as printed), `UNNAMED` (was `cu_checked.py`) |
| `letters.json` | hand-made: the letter of each of 74 glyph shapes, keyed by item kinds + signature, read once on contact sheets (was `cu_letters.json`) |
| `header.txt` | hand-made: the comment at the top of `trails.ts` (was `cu_header.txt`) |
| `checks/sheet.py` | contact sheet of glyph shapes, upright, for reading letters (was `cu_sheet.py`) |
| `checks/zoom.py` | region crops with every piece tagged `id:auto-name` (`?` unassigned, `!` several names) (was `cu_zoom.py`) |
| `checks/fine.py` | given pieces drawn thin on the PDF, numbered at both ends (was `cu_fine.py`) |
| `checks/show.py` | a faded PDF crop with the pieces in bright colours and numbered (was `cu_show.py`) |
| `checks/symsheet.py` | every label of a given difficulty with its printed symbol (was `cu_symsheet.py`) |
| `checks/crop.py` | a plain PDF crop |
| `checks/probe.py` | the PDF drawings near a point (to find the drawing numbers `lines.py` leaves out) |

Work files (`$COPPER_MOUNTAIN_WORK`): `copper.pdf`, `map.png`, `piece_src.json`, `tiles/`, `glyphs.json`,
`clusters.json`, `glyph_labels.json`, `syms.json`, `text_raw.json`, `names.json`, `assign.json`, `gaps.json`,
`labels.json`, `review_data.json`, `trace_gaps.json`, `recheck.json`, and a `.log` per chatty step
(`names.log` lists every label with its symbols, `build.log` what the automatic match left open).

## Nuances of this map

- **Names are outlined glyphs**, drawn in reading order in the run's colour (black, blue, green; pure black for
  some). Glyph fills are grouped by shape: the outline's item kinds per subpath plus each item's chord over their
  total, which rotation and size leave unchanged. One letter per shape (`letters.json`, 74 shapes), keyed by that
  signature: cluster ids shift whenever a threshold changes. A label is a run of consecutive same-colour glyphs
  (centres within 9 pt, at most 6 drawings apart); a word gap is an outline gap over max(2.3 x the median letter
  gap, median + 0.9 pt).
- **A few names are real text** (Gotham-Black, 3.7-6 pt): 11 of the 134 labels, High Point Bypass, West
  Village Traverse, Union Bowl, Lower Enchanted Forest, Miner's Progression Park, Pine Cone Alley, Jackstraw
  Trees, Lyman Lane, Timber Road, Kokomo Glade and Log Chute (`pdf_labels.py`; the last copy at a spot).
- **Copies**: glyphs drawn twice (under and over their halo) leave fragment copies; the longest label is kept,
  and of equal copies the last drawn. Names recoloured for this season are drawn over their old colour (Sno Deal
  and the lower Carefree label: green glyphs under blue ones), so the later colour wins.
- **Mended readings** (`names.py` `FIX`): `P ARK`, `F AR EAST`, `THETACO`, `OHNO`, `IGREENACRES`, `ORE DEAL E`,
  `CDL’S TRAIL #2O` (a letter O for the zero); `UNIONPARK`, `TPRK` and a lone dash are dropped. `NOT` drops signs
  and other words (CLOSED TO DOWNHILL TRAFFIC, BOUNDARY, FOREST SUPERVISOR CLOSURE, the highway 91 shields, the
  walking route, WATERFALL ROAD, WEST LAKE, the free sledding zone, THE SNOW MAZE). `JOIN`: 17 names set on two
  or three lines. Lillie G Traverse: the dash between LILLIE and G on the map is
  the line showing through the word gap (drawing 680), not a glyph.
- **Symbols are fills too**: square (blue, 4 even lines), diamond (pure black, 4 even lines), double diamond (an
  8-line outline), EX "Extreme Terrain" (a double diamond holding white E and X fills; rated double-black) and
  circle (green, 4 curves). The map puts a name's symbol where its line meets the label. Symbols set apart from
  their name were settled on crops (`MANUAL`: Sail Away Glade, Union Meadows, Rhapsody, Sno Deal's second
  square, Bridgeway, Hidden Vein, and the two each of Spaulding Bowl and Copper Bowl, EX and double diamond).
  Left unlabelled: the green circle at (531, 561), a one-way arrow, and the logo's six diamonds.
- **Difficulty** = the label's first symbol; a name printed twice with two ratings takes the harder on a tie
  (`seed_roster.py`: Carefree, green above Leap Frog and blue below, is blue). Names with no symbol take the
  colour they are printed in (Clear Cut and Upper Skid Road blue; High Point Bypass, See & Ski, Sluice, West
  Village Traverse and Green Acres green; Union Bowl black), except Buffalo Stampede (Tucker Mountain, where
  every other run is EX: double-black; the lone diamond at its foot ends the LILLIE-G TRAVERSE label) and the Log
  Chute kids' zone (its green outline). The nine parks print no symbol: seed_roster's default, blue.
- **Lines are filled outlines** (strokes converted to fills, at least 10.5 pt long in a trail colour): each is
  rasterised at 6 px/pt (subpaths XORed, so holes stay holes) and thinned to a 1 px skeleton (Zhang-Suen). The
  pixel graph leaves out the diagonal steps a 4-neighbour path already joins (otherwise every staircase forks);
  spurs under 2.5 pt are pruned and polylines traced between forks.
- **Tucker Mountain's lines** (the Three Bears lift) are clip paths filled with a fading image: of each pair of
  clips (line and halo) the one with fewer items is the line; the bowl's area clip and the lift's are skipped.
- **A few lines are plain strokes** (See & Ski / EZ Road, West Village Traverse, Lyman Lane, Timber Road, West
  Ten Mile, Pine Cone Alley), taken as they are; dashed ones are uphill routes (left out), and the Log Chute kids'
  zone outline (drawing 4945) is left out (a marker at its label instead).
- **Left out by drawing number** (`SKIP_SEQ`, numbers of this edition): the closed-area sign, the Green Acres
  and Easy Rider zones, the highway 91 shields, the I-70 arrows and the snow-maze icon; by shape the SEE INSET
  boxes and the slash between a bowl's two symbols; by box the resort logo.
- **Boulderado** runs on under the COPPER MOUNTAIN peak label: its piece is cut at the label's box.
- **Matching**: a label owns the pieces it is printed along, the same-colour piece ending at its symbol and the
  piece running on from the far end of its text; then names spread along unlabelled continuations. The automatic
  match left 20 labels with no piece (bowls, glades, parks, zones: all markers), 12 pieces with two names and 12
  with none; the 26 entries of `decisions.py` settle those. Two names on one piece: Hodson's Cut (not Triple
  Zero), Sawtooth (not Resolution Bowl), Free Fall Glade (not Black Bear Glade), Little Trees and Spillway (one
  each), Scooter (not Peace Park), Slot Car Track (not Oh No), Jacque's Pique (not Copperfield), Liberty (not
  Upper Skid Road), Woodwinds Traverse (not Easy Feelin'), Timber Road (not Fairway), Prospector (not Kokomo
  Glade). No name: Bee Traverse, Lillie G Traverse, Woodwinds, Minor Matter, Woodwinds Traverse, Sno Deal,
  Hidden Vein, Leap Frog, Coppertone and Loverly's dark casing across the coaster. One automatic name overridden:
  piece 92 is Woodwinds Traverse, not Hidden Vein (and 102, already Woodwinds Traverse, is confirmed).
- **No line, so a marker at the label** (24): the bowls (Copper, Spaulding, Resolution, Union), glades and tree
  areas (17 Glade, Cache Glades, Kokomo Glade, Sail Away Glade, Jackstraw Trees, Upper and Lower Enchanted
  Forest, Union Meadows), the nine parks, Green Acres, Log Chute and Upper Skid Road. Every other name is printed
  along its own line, so there are no label-gap stretches here.
- **The map image** mattes the vector layer (rendered twice, with the painting swapped for flat white and flat
  black: alpha = 1 - (white - black) / 255, colour = black render / alpha) over the painting upscaled with Lanczos,
  instead of the renderer's blocky upscale. The page's other image (xref 244, 177 x 240 px with a soft mask,
  over 676-804 x 607-779 pt by the Woodward Express) is a yellow glow: it stays in the vector layer and is matted
  like any other half-transparent drawing.

## Checks done

- 2026-10-01, when the data was made: every piece on region crops (`checks/zoom.py`, `Z=3.2`, 24 boxes of
  220 x 165 pt, each piece tagged `id:auto-name`), every open piece and label on closer crops (`checks/fine.py`,
  `checks/show.py`, `checks/crop.py`: the crops named in `decisions.py`), the symbols set apart from their names
  on a sheet and crops (`MANUAL`), and every label's rating on symbol sheets per difficulty
  (`checks/symsheet.py double-black|black|blue|green`). Then the overlays with `tools/trailmap/region_audit.py`
  over the map image (`--grid 5x4 --area 270,200,3330,2420`, and zoomed boxes `--box 1600,1500,2200,2000
  --zoom 1.3`, `--box 700,1850,1100,2100 --zoom 1.6`), and the hover check: 336/336 hover points show the right
  name. The glyph reading was later repeated with `tools/trailmap/pdf_glyphs.py` (the playbook: it reproduced
  every checked label).
- 2026-10-06: `trails:apply` stopped extending a trail's free end onto a piece it does not point at; at Copper
  that changed Minor Matter's overlay only (a stub back over a line), checked on a crop.
- 2026-10-07: `regen.sh` from an empty work folder (`IMAGES=1`) and again with it filled: no change to any
  committed file, and every intermediate file identical to the original scratch run's. Hover check on that build:
  336/336.

## A new season's map

1. Find the new PDF (the resort page's page data, above; skimap.org may still serve the old one) and put it in
   the work folder as `copper.pdf`. `regen.sh` stops at the SHA-256 check.
2. See what changed: tally the drawings of both PDFs (`page.get_drawings()`: type, colour, box, item count) and
   render the differences. A re-export that only drops or adds a few drawings renumbers everything after them:
   find the shifted numbers of `lines.py`'s `SKIP_SEQ` (the closed-area sign, the zones, the shields, the
   arrows, the snow-maze icon) and of drawing 4945 with `checks/probe.py`, and check `LOGO`, `BOXES`, the clip
   rules for Tucker Mountain (scissor bounds, the Three Bears lift's clip at 499.1, 207.5) and the colours (`COL`).
   If `piece_src.json` and the reading come out the same, only the SHA-256 (and the URL) in `regen.sh` change.
3. Names: a glyph whose shape is not in `letters.json` is skipped (its label loses that letter, or splits). Look at
   `labels.log` and `names.log` for odd or split names, draw the new shapes with `checks/sheet.py` (cluster ids
   from `clusters.json`) and add `{kinds, sig, ch}` for each to `letters.json`; update `FIX`, `NOT` and `JOIN` in
   `names.py`, and `MANUAL` for symbols with no label ("symbols with no label" in `names.log`). The shared
   `tools/trailmap/pdf_glyphs.py` does the same glyph work (its letter table also keys by size): run on this PDF on
   2026-10-07 with these letters, it gave the same labels as `labels.py` except three that `FIX` mends here
   (IGREENACRES and ORE DEAL E come out as GREEN ACRES and ORE DEAL, and TPRK not at all), and the same 125
   symbols.
4. Pieces: a new edition renumbers them, so check every id in `decisions.py` again. Run `build.py`, look at
   what `build.log` leaves open (labels with no piece, pieces with two names or none, colour mismatches) on
   `checks/zoom.py` region crops and `checks/fine.py` close-ups, and record each decision in `CHECKED`.
   `reading.py` stops until every piece is named or `UNNAMED`.
5. Ratings: `ZONE`, `BY_COLOUR` and `PARKS` in `reading.py`; check every rating on `checks/symsheet.py` sheets.
6. Update `header.txt` (its counts and lists), run `IMAGES=1 regen.sh`, audit every overlay
   (`region_audit.py`, `symbol_audit.py`), run the hover check, and update the playbook's Copper notes.
