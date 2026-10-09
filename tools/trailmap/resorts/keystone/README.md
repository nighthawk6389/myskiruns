# Keystone's trail data pipeline

Keystone's 2025-26 trail map is a PDF whose trail lines are vector strokes and
whose names are outlined glyphs (filled shapes, no text), over a low-resolution
painting. The names were decoded with `tools/trailmap/pdf_glyphs.py` (each
glyph shape read once on a contact sheet: `letters.json`), each line piece was
matched to the name printed along it, and the pieces the match left open were
settled on zoomed crops (`decisions.py`). This folder holds the scripts that
built `src/data/resorts/keystone/` and `public/maps/keystone.jpg` on
2026-10-01 (moved here from the session's scratch folder; each script's
docstring gives its scratch name), and `regen.sh`, which rebuilds those files
byte for byte.

## Source

- **PDF:** `20251028_KY_winter-trail_map_001.pdf`, the 2025-26 winter trail map
  (the name carries its date, 2025-10-28), linked from
  <https://www.keystoneresort.com/the-mountain/about-the-mountain/trail-map.aspx>:
  <https://www.keystoneresort.com/-/aemasset/sitecore/keystone/maps/winter-2025-2026/20251028_KY_winter-trail_map_001.pdf>.
  2,317,618 bytes, SHA-256
  `103978ffe2c7c576e33c9147eb09310e598f84a0072fe4e918353425438de243`. One page,
  1530x1233 pt, PDF 1.6, no metadata. keystoneresort.com returns an error page
  to curl, so `regen.sh` fetches it from inside the trail-map page in headless
  Chromium (`tools/trailmap/fetch_pdf.cjs`; behind this sandbox's agent proxy
  it sets `PIN` from the proxy CA, as the playbook's Part 4, "Getting a source here" says). skimap.org
  has the same file (same SHA-256, checked 2026-10-07) for plain curl:
  <https://skimap.org/skimaps/view/35939> →
  `https://files.skimap.org/i8kvmxp7f2k2oxqtot6roh55vurt.pdf`. A copy placed in
  the work folder by hand is used if its SHA-256 matches.
- **Painting:** the PDF embeds it at only 1610x1201 px (xref 23, a CMYK JPEG
  placed at about 1 px/pt). Vail Resorts' image CDN (scene7, plain curl)
  serves the whole map as one raster, `20251028_KY_winter-trail_map_001`,
  3187x2569 (`?req=imageprops`; its timeStamp is 2025-10-28 19:19 UTC): the
  page at 2.08 px/pt, painting, lines and names flattened. The map image puts
  the PDF's vector layer over it, using
  the JPEG it returns for `?wid=3187&hei=2569&fit=constrain,1&qlt=95`:
  4,061,213 bytes, SHA-256
  `8e836d78ff3d7cf6012ab81f6494ede4c7b376d8c7aa2fa6999e43f0edd20541` (the
  same bytes on 2026-10-01 and 2026-10-07). Stretched to the page, it lies
  within 0.6 of its pixels of a render of the PDF (phase correlation in five
  places, 2026-10-07), so the vector layer covers its own lines and names.

`regen.sh` checks both SHA-256s and stops on a different file (`FORCE=1` goes
on anyway): a new edition needs the checks below redone.

## Rebuild

```bash
tools/trailmap/resorts/keystone/regen.sh             # rebuild src/data/resorts/keystone/ (about 15 s)
IMAGES=1 tools/trailmap/resorts/keystone/regen.sh    # also public/maps/keystone.jpg (about 30 s)
FORCE=1 tools/trailmap/resorts/keystone/regen.sh     # run on a source whose SHA-256 differs
KEYSTONE_WORK=/tmp/ks tools/trailmap/resorts/keystone/regen.sh   # another work folder
```

It downloads the two sources into `$KEYSTONE_WORK` (default `work/keystone`,
git-ignored) when they are missing and writes every Keystone data file. With
nothing changed it reproduces the committed files byte for byte (checked from
an empty work folder and again with it filled, 2026-10-07). It keeps any
person's reviews in `trailReviews.json` (`traces_to_reviews.py
--replace-claude` rebuilds only Claude's, keeping their timestamps when a
decision comes back unchanged). Needs `pip install pymupdf pillow numpy`, and
for the download node with Playwright (`PLAYWRIGHT_PATH`, default
`$(npm root -g)/playwright`). Never hand-edit the generated files
(`trails.ts`, `linePolylines.json`, `trailProposals.json`, `trailPaths.json`,
Claude's entries in `trailReviews.json`): change the inputs here and re-run.

## Pipeline

Run by `regen.sh` in this order (`$W` is the work folder, `D` is
`src/data/resorts/keystone/`):

| step | script | output |
|---|---|---|
| 1 | `tools/trailmap/fetch_pdf.cjs` (if missing), SHA-256 check | `$W/keystone.pdf` |
| 1 | curl from scene7 (if missing), SHA-256 check | `$W/scene7.jpg` |
| 2 | `tools/trailmap/matte_pdf_layer.py --scale 2.8 --clip 0,90,1530,1080 --xref 23 --background scene7.jpg --flattened` (with `IMAGES=1`, or when `map.png` is missing) | `$W/map.png` (4284x2772) |
| 2 | PIL, JPEG quality 82, optimized, progressive (`IMAGES=1` only) | `public/maps/keystone.jpg` |
| 3 | `tools/trailmap/pdf_glyphs.py collect` (the name colours, legend and bottom bar excluded) | `$W/glyphs.json` (2186 glyphs, 140 shapes) |
| 3 | `pdf_glyphs.py labels --letters letters.json --square blue --diamond black --circle green --space 0.75` | `$W/glyph_labels.json` (199 labels, 148 symbols) |
| 3 | `names.py` | `$W/names.json` (156 labels, 145 names, symbols attached) |
| 4 | `tools/trailmap/extract_pdf_vectors.py`: 1.5 pt green/blue/black strokes, then `--append` the 1 pt black ones | `$W/pieces.json` (132 + 2 pieces) |
| 4 | `tools/trailmap/split_pieces.py --split '2@2410.8,890.4=Brahma/Snake Pit'` | `$W/pieces.json` (135 pieces), `$W/splits_reading.json` |
| 4 | inline Python: `_unnamed` (decisions.py) and `_source` | `D/linePolylines.json` |
| 5 | `build.py` | `$W/assign.json` (the automatic match) |
| 5 | `tools/trailmap/render_tiles.py` (only its index is used: the image size) | `$W/tiles/index.json`, 28 tiles |
| 5 | `reading.py` | `$W/tiles/result_keystone.json`, `$W/gaps.json` (9 stretches, 25 markers) |
| 6 | `tools/trailmap/seed_roster.py --areas 'keystone=Keystone=12614'`, then `header.txt` | `D/trails.ts` (145 trails), `$W/labels.json` |
| 7 | `tools/trailmap/aggregate_readings.py` | `D/trailProposals.json` (123 trails, 135 pieces), `$W/review_data.json` |
| 7 | `traces.py` | `$W/trace_gaps.json` (34 entries) |
| 7 | `tools/trailmap/traces_to_reviews.py --replace-claude` | `D/trailReviews.json` (34 Claude reviews), `$W/recheck.json` |
| 7 | `npm run trails:apply -- --resort keystone` | `D/trailPaths.json` (120 lines, 25 markers) |
| 8 | inline Python: `REPORT_NAMES` (decisions.py) | `D/trails.ts`: 16 names shown as the trail report spells them (the ids stay) |

`public/maps/keystone.jpg` was first made by a one-off scratch script,
`k_image.py` (2026-10-01 16:28: `k_source.png`, saved as the JPEG above). Its
code became `tools/trailmap/matte_pdf_layer.py` that evening, which `regen.sh`
uses; since 2026-10-07 with `--flattened` (see "Map image" below).

## Files

| file | role |
|---|---|
| `regen.sh` | the whole rebuild, with the sources' URLs and SHA-256s and every tool's flags |
| `common.py` | the work folder (`$KEYSTONE_WORK`), the data folder and the PDF's path |
| `letters.json` | each glyph shape's character (keyed by shape signature and size), read on `pdf_glyphs.py sheet` contact sheets (scratch `k_letters.json`) |
| `names.py` | glyph labels → trail names: drops non-trail labels (`NOT`), fixes spacing slips (`FIX`), joins two-line names (`JOIN`), attaches each symbol, the two set apart by hand (`MANUAL`) |
| `build.py` | each label → the pieces it is printed along, at its symbol or at its text's far end; names spread along continuations |
| `decisions.py` | `CHECKED`: the 18 pieces settled on crops (piece id → name), with the crop that settled each; `UNNAMED` (empty); `REPORT_NAMES`: the names shown in the trail report's spelling |
| `report.json` | the trail report: Keystone's terrain feed as Common Crawl captured it on 2025-11-18 (name, area, rating; `tools/trailmap/reports/feed_trails.py` wrote it) |
| `reading.py` | names + matches + decisions → the reading for seed_roster/aggregate_readings, stretches along names printed in a gap of their line, markers for names with no line; park and kids' zone ratings |
| `traces.py` | stretches and markers → `trace_gaps.json` for `traces_to_reviews.py` |
| `header.txt` | the comment at the top of `trails.ts` (scratch `k_header.txt`) |
| `checks/crop.py` | a plain render of a PDF box (`out.png x0,y0,x1,y1 [zoom]`) |
| `checks/show.py` | a faded render with every piece drawn and numbered (`out.png box [zoom] [--ids a,b]`) |
| `checks/fine.py` | given pieces drawn thin, numbered at both ends (`out.png box zoom ids...`) |
| `checks/zoom.py` | region crops with every piece tagged `id:auto-name` (`prefix box ...`, `Z` = zoom) |
| `checks/symsheet.py` | contact sheet of every label of a difficulty with its symbol (`green,blue out.jpg`) |
| `checks/probe.py` | the PDF drawings near a point: colour, width, seqno (`x,y ...`) |

The checks scripts work in PDF points and read the PDF and `assign.json` /
`names.json` from the work folder, so run `regen.sh` once first. Not kept from
the scratch folder: `reading_splits.json` and `linePolylines_before_split.json`,
which `regen.sh` remakes byte for byte (`splits_reading.json`, and
`pieces.json` before the cut), and the downloads and crops.

## Nuances of this map

- **Lines:** trails are 1.5 pt strokes in green (0, 0.61, 0.4), blue
  (0, 0.48, 0.76) and black. Two black lines are thinner, 1 pt over a 3 pt
  white casing: Roulette (piece 132, seqno 1688) and Black Jack (133, seqno
  1696). A second `--append` pass at 0.9-1.1 pt picks them up; the other 1 pt
  black strokes are small icon outlines, which the extractor drops. Not
  taken: the lifts (crimson 2 pt strokes over a 4 pt white casing), the
  dashed gold lines and short gold gate marks (closures, restricted gates),
  the dotted black hiking routes along the ridges. No trail line is drawn
  twice (checked: no two pieces overlap).
- **Map area:** the clip 0,90 to 1530,1080 pt leaves out the bar under the map;
  the legend panel at the right (from x 1280, y 590) is excluded from the
  lines and the glyphs.
- **Names** are outlined glyphs in the trail's own colour (green, blue,
  black); one label, Lower Prospector, is in a second green (0, 0.6, 0.4).
  The font is condensed, so a word gap is measured between outlines along the
  reading direction (`--space 0.75`). Its capital I is the l shape: a
  word-initial l is read as I (`names.py`). Comma and apostrophe are one
  shape turned over, told apart by which side of the line they sit on
  (`pdf_glyphs.py`). The glyph shapes left unread are all symbols, icons,
  dots and arrows (`pdf_glyphs.py sheet` shows them).
- **Recoloured names:** 13 trail names are drawn twice: in this season's
  colour over a black copy (Jane's Journey, Ptarmigan, Witchita, Torreys,
  Buffalo, Foxtrot, Gray's, Thorne, Red, Ute in blue; Quandary, Ten Mile,
  Miners in green); a few road names are black over near-black (0.14, 0.12,
  0.13). `collect` keeps the last drawn glyph at each spot, which is the one
  printed on top.
- **Names as printed:** Orfint Boy, Beger (the trail report spells them so
  too), Witchita, "Oh, Bob". Spacing slips fixed: SpringDipper, TheTrap,
  "U neva". Schoolmarm's lower part is also
  labelled "Schoolmarm Family Ski Trail": the same trail. Set on two lines and
  joined: Orfint Boy, Packsaddle Bowl, Ripperoo's Glade. Not trails (dropped):
  roads, places, distances, closing-time notes, the peak names and
  elevations (`NOT` in `names.py`).
- **Difficulty** is the symbol printed with the name, just before it on its
  text line (or just after, when nothing is before): green circle, blue
  square, black diamond, and EX (two diamonds holding a white E and X,
  "Extreme Terrain") = double black; the map has no plain double diamond. The
  PDF has 148 symbols: 21 circles, 49 squares, 67 diamonds, 11 EX. Witchita's
  and Red's squares sit below the start of their rotated names (attached by
  hand, `MANUAL`); the green circle at (157, 1035) is a traffic light.
  Result: 20 green, 50 blue, 64 black, 11 double black.
- **Zones:** names printed in other colours are zones, not runs: the five
  A51 freestyle-terrain runs in orange (Easy Street, Park Lane, Main Street,
  The Alley, I-70: no symbol, seed_roster's default blue) and the four gold
  kids' adventure zones (Lost Mine, Murphy's Mine, Ripperoo's Forest,
  Ripperoo's Glade: no symbol; they sit on green runs, so green). `build.py`
  matches no piece to them: they are markers.
- **Matching:** most names are printed along their own line: a label names
  the pieces under most of its glyphs (median glyph within 7 pt, 60% within
  9 pt), preferring pieces of its symbol's colour; also the piece ending at
  its symbol, or at the far end of its text and running on from it. Then
  names spread along unlabelled continuations. That named 121 of the 135
  pieces; 10 pieces got two names (a second label at their top or end) and 4
  none: those 14 were settled on crops (`decisions.py`, with the crop for
  each), and 4 more confirmed there.
- **One line, two trails:** piece 2 is Brahma above the Outpost Gondola and
  Snake Pit below it: cut at (2410.8, 890.4) px (piece 134 is the lower part).
- **Stretches:** 9 names sit in a gap of their own line (the line stops
  either side of the text): Go Devil, Indy Face, Liberty, Liberty Trees,
  Midnight Ride, Patriot, Revolution, Two If By Sea, Two Sled. Their overlay
  gets a stretch drawn along the name's glyphs, from the symbol, so the line
  runs on through it. A two-line name's first line is the one on the trail.
  Cat South Glades is printed beside its line: no stretch.
- **Markers:** 25 names have no drawn line and get a marker at their label:
  the bowls (Bergman, Erickson, Independence, North, Packsaddle, South),
  glades and tree areas (Bullet Glades, Glades, South Bowl Trees, Tele Trees,
  The Black Forest), Wombat Chutes, The Windows, the learning area's runs
  (Endeavor, Scout, Ski-Daddle), the five parks and the four kids' zones.
- **The trail report** (`report.json`, 142 trails: Keystone's terrain feed of
  2025-11-18, in season; out of season the feed lists none): every rating
  agrees with the map's. 16 runs are shown as the report spells them, with
  their ids kept (`REPORT_NAMES`, applied last in `regen.sh`, since the
  proposals match the reading's names to `trails.ts`): Wichita (printed
  Witchita), Oh Bob, Grays, Two Sled Road, Go Devil - Upper and Go Devil -
  Lower (printed Go Devil and Lower Go Devil), Cat South Glade, Big Horn, Black
  Forest, Diamondback, Hoodoo, Ida Belle, Jack Face, Mineshaft, Powdercap,
  Silverspoon. Kept as printed (each checked on a crop): Jackwhacker (the
  report's Jackwacker drops the h), Ripperoo's Forest and Glade (Riperoo's
  misspells the mascot), The Windows (the report's Lower Windows; the map
  prints "The Windows / Closes at 2:00 p.m."). Not on the map: Discovery and
  H&H Mine (no such label in the learning area or the parks). The legend's
  "Number of Trails 140" is this list of 145 less its five bowls (Bergman,
  Erickson, Independence, North, South), which the report doesn't list.
- **Map image:** the vector layer (lines, names, symbols, icons) is rendered at
  2.8 px/pt from two renders with the painting swapped for flat white and flat
  black (alpha = 1 - (white - black)/255, colour = black render / alpha) and
  matted over the scene7 raster stretched to the page (2.08 px/pt, against the
  embedded painting's 1 px/pt). That raster is the whole map flattened, so it
  already shows the PDF's three translucent layers (form XObjects 16, 17 and
  22: a 75% legend swatch, the 75% Multiply bands and slow zones, a 50% box);
  `--flattened` takes the layer's coverage from renders without them, and
  calibrates the flat stand-ins as they render (the CMYK painting's black
  comes out as 8, 6, 6, not 0). Until 2026-10-07 they were applied twice: the
  map was 10, 4 and 5 levels (R, G, B) lighter than the PDF's own render
  where only the painting shows, and the bands 30, 29 and 11 levels darker;
  now both equal the scene7 raster.

## Checks done

On 2026-10-01, when the data was built (the crop files named in
`decisions.py`'s comments; run `regen.sh` first, then these from the repo
root):

- Every piece on 30 region crops with each piece tagged `id:auto-name`
  (`reg/t_*.jpg`):
  ```bash
  B=$(python3 -c "
  import json
  P = json.load(open('src/data/resorts/keystone/linePolylines.json'))['polylines']
  pts = [(u * 15.3, 90 + v * 9.9) for p in P for u, v in p['points']]
  print(' '.join(f'{x},{y},{x + 210},{y + 150}' for y in (120, 260, 400, 540, 680, 820)
                 for x in (130, 330, 530, 730, 930, 1130, 1330)
                 if any(x <= a <= x + 210 and y <= c <= y + 150 for a, c in pts)))")
  mkdir -p work/keystone/reg && Z=3.4 python3 tools/trailmap/resorts/keystone/checks/zoom.py work/keystone/reg/t $B
  ```
- The doubtful pieces on closer crops (`checks/fine.py out.png box zoom ids`;
  made before the split, so piece 2 was whole and 134 did not exist yet):
  `f_toad.png 1350,210,1510,380 4.5 39`;
  `f_fox.png 1040,320,1220,420 5 123 52 122 50 117 118 48`;
  `f_52.png 1030,355,1100,400 9 52 51 48 50 123 53 115`;
  `f_trunk.png 1150,280,1230,420 7 47 119 120 118 122 117 124`;
  `f_tend.png 1060,180,1260,440 3.6 118 119 120 121 122 117 47 124`;
  `f_tr.png 980,330,1110,420 6 51 52 48 50 115 128 114 53`;
  `f_oh.png 1290,395,1360,470 9 44 45 46 43`;
  `f_brahma.png 815,330,910,480 5 2 132 133`;
  `f_sfe.png 240,425,420,560 4.5 65 69 64 71 73 68 80 70`;
  `f_base.png 180,540,320,680 5 83 82 86 67 85 84 94 87 88 89 92 105 91`;
  `f_jay.png 180,570,340,690 5 89 94 84 93 92`;
  `f_mid.png 255,560,480,700 4 84 89 94 104 90 92 93 97 98 99 102 105 91 101`;
  `f_pay.png 350,540,640,620 3.2 95 100 72 7 94`;
  `f_aca.png 540,570,640,650 6 96 93 94 7`;
  `f_lib.png 870,170,985,270 7 12 13 14 15 16 17 19 20 21 18`;
  `f_csg.png 1100,440,1160,540 7 131`; `f_orf88.png 270,595,305,632 16 88 87`;
  plain ones with `checks/crop.py`: `f_nuchu.png 1160,315,1200,365 16`,
  `f_tend_plain.png 1150,300,1260,440 7`. Quarter sheets with every piece
  numbered: `checks/show.py sh_q0.png 140,100,620,480 2.6` (and
  `600,100,1080,480`, `1060,100,1530,480`, `140,460,620,880`,
  `600,460,1080,880`, `1060,460,1530,880`).
- Every overlay on the region audit, 18 crops over the map:
  `python3 tools/trailmap/region_audit.py --image work/keystone/map.png --paths
  src/data/resorts/keystone/trailPaths.json --trails
  src/data/resorts/keystone/trails.ts --out work/keystone/audit --grid 6x3
  --area 380,0,4284,2400`.
- Every difficulty against its printed symbol, on symbol sheets:
  `checks/symsheet.py double-black k_sym_dbl.jpg`, and `black`, `blue`,
  `green`.
- Hover check (`tools/trailmap/hover_check.cjs --resort keystone`): 385/385
  hover points named their trail.
- `pdf_glyphs.py`, re-run on Copper Mountain, reproduced every label checked
  there.

On 2026-10-07: `regen.sh` from an empty work folder with `IMAGES=1` left `git
status` clean for `src/data/resorts/keystone` and `public/maps/keystone.jpg`,
and so did a second run with the folder filled; every intermediate file
(glyph labels, names, matches, reading, stretches, the 28 tiles, the PNG) is
byte-identical to the scratch copy it replaces, and the checks scripts
reproduce the scratch crops made after the split byte for byte.

On 2026-10-07, later: the trail report compared name by name (above); the 16
shown names and the new map image checked (the image against the PDF's own
render and the scene7 raster, as above, and on crops of the bands). Hover check
385/385.

## A new season's map

1. Find the new PDF's link on the trail-map page (headless Chromium: the
   site refuses curl) and the map's scene7 name in the page's image URLs
   (`?req=imageprops` gives its size). Put both URLs and their SHA-256s in
   `regen.sh`, and delete the old files in the work folder.
2. Tally the strokes' colours and widths again (`checks/probe.py`, the
   playbook's triage): the trail colours, the 1.5 pt and 1 pt widths, the
   clip (0,90 to 1530,1080) and the legend's exclude box may all move. Check
   that the scene7 raster still covers the whole page (it is stretched to the
   page size) and lies on the PDF: a crop of `map.png` should show no second
   copy of a line or name beside the vector one.
3. Glyphs: run `collect` and `labels`, then `pdf_glyphs.py sheet` for the
   shapes still unread and `read` them into `letters.json` (keyed by shape,
   so the old reads still hold for the same font). Check the label colours:
   a recoloured name is drawn over its old copy, and new zone colours need
   `--color` entries.
4. `names.py`: compare its output with the new labels and redo `FIX`, `NOT`,
   `JOIN` and `MANUAL` (MANUAL is keyed by position in PDF points).
5. Piece ids change with any change in the strokes: run `build.py`, settle
   every piece it leaves with no name or two on crops (`checks/zoom.py`, then
   `checks/fine.py`), and rewrite `decisions.py` and the split in
   `regen.sh` (find where one line carries two names again).
6. Update the counts in `header.txt` and the `_source` text in `regen.sh`,
   rebuild with `IMAGES=1`, then redo the checks above: the region audit,
   the symbol sheets, the hover check.
