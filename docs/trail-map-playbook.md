# Trail map playbook: from a resort map image to clickable, named trails

This is the process that put clickable, correctly named trails on twenty-one
resorts' current trail maps, starting with Killington (135 trails), written so
it can be repeated (and sped up) for other resorts. It records what worked,
what didn't, and what each step cost. Start with **Pick a route**: the source
you can get decides most of the work.

**Goal (definition of done):** every trail in the resort's trail list has an
overlay that lies on that trail's own drawn line along its full length, or a
marker at its label if it has no drawn line (many glades); tapping anywhere on
it shows that trail's name; its difficulty matches the symbol printed on the
map; and the list contains exactly the trails printed on this season's map.

## Pick a route by what the source gives you

Run `extract_pdf_image.py map.pdf map.png` on the resort's PDF first: it
reports any vector text and drawings. Then tally the PDF's stroke and fill
colours and widths with pymupdf (`page.get_drawings()`) and draw each class on
a blank page to see what it is.

| the source gives you | route | done this way |
|---|---|---|
| trail lines as vector strokes, names as text | `extract_pdf_vectors.py` for the pieces, `pdf_labels.py` for the names; match each name to the stroke it is printed along (`pdf_resort.py`), settle the rest on crops yourself (step 3c); no readers | Whiteface, Winter Park (text with no Unicode map), Breckenridge, Hunter Mountain, Big Sky (three PDFs, three panels) |
| vector strokes, names as outlined glyphs | `extract_pdf_vectors.py`; `pdf_glyphs.py` decodes the names (each glyph shape read once on a contact sheet) | Keystone, Sunday River, Sugarloaf, Smugglers' Notch, Whistler Blackcomb (three panels), Park City, Palisades Tahoe (three PDFs, three panels) |
| lines as filled outlines, names as outlined glyphs | rasterise the outline fills and thin them to centre lines (Copper notes in step 1), or read each outline's centre line straight from its path (Heavenly); `pdf_glyphs.py` | Copper Mountain, Heavenly (an older export of the current image's artwork, two panels) |
| vector strokes, names you can't extract | numbered tiles read by parallel readers (step 3) | Stowe, Okemo, Sugarbush |
| a painting with no lines, names as text | the trace pass along the painted cuts (step 3b) | Jay Peak |
| only raster images | `raster_lines.py` + `raster_symbols.py` (or `lineDetector.mjs`), pieces named on review tiles (3c) or by readers | Vail (three panels), Killington |

A low-resolution painting under good vectors: `matte_pdf_layer.py` mattes the
vector layer over a sharper copy of the painting (Breckenridge, Keystone) or a
smooth upscale of the embedded one (Copper).

This season's PDF has outlined names and flattened lines, but an older export
of the same artwork has them live (skimap.org keeps past seasons): register the
two pages on renders, check that every old name lands on the same outlined
name in this season's page and that this season prints no other name, then
take the strokes, text and symbols from the old export (Wildcat). Where the
current map is only an image, the same works with the image (Heavenly): find
every place it differs from the old page, leave out what it no longer prints
and trace what it prints anew.

## Resorts so far

| resort | source | trails (lines + markers) | named and checked by |
|---|---|---|---|
| Killington | flattened raster PDF | 135 (113 + 22) | `lineDetector.mjs`, 6 readers, human review page |
| Stowe | PDF strokes, outlined text | 125 (114 + 11) | readers, human review |
| Okemo | PDF strokes | 128 (124 + 4) | readers, trace pass, human review of 23 |
| Sugarbush | PDF strokes, outlined labels | 138 (111 + 27) | readers; Claude checked every overlay on crops |
| Jay Peak | painting with no lines, names as text | 88 (65 + 23) | trace pass; crops |
| Whiteface | PDF strokes + text | 98 (96 + 2) | names matched to strokes; crops |
| Winter Park | PDF strokes + text with no Unicode map | 172 (114 + 58) | `pdf_labels.py`, matching; crops |
| Breckenridge | PDF strokes + text, low-resolution painting | 197 (157 + 40) | matching; image matted over scene7; crops |
| Copper Mountain | PDF outlined lines + outlined glyphs | 128 (104 + 24) | skeletonised outlines, glyph sheets; crops |
| Keystone | PDF strokes + outlined glyphs | 145 (120 + 25) | `pdf_glyphs.py`, matching; image matted over scene7; crops |
| Vail | three raster panels from scene7 | 194 (173 + 21) | `raster_lines.py`, named on review tiles; crops |
| Hunter Mountain | PDF strokes + text, vector painting | 70 (66 + 4) | `pdf_resort.py` matching, 2 pieces settled on crops; crops |
| Wildcat Mountain | strokes + text of an older export of this season's artwork; scene7 image | 48 (47 + 1) | 31 pieces named by the name printed along them, 20 settled on crops, 9 cuts; crops |
| Sunday River | PDF strokes + outlined glyphs, main map and three insets | 137 (116 + 21) | glyphs read on sheets; 154 pieces named by the name along them, 19 settled on crops, 10 cuts; crops |
| Sugarloaf | PDF strokes + outlined glyphs and text over a low-resolution painting, numbered key circles, a raster inset | 175 (127 + 48) | glyphs read on sheets; 176 pieces named by the name at their end, along them or the key circle on them, 78 settled on crops, the inset's 10 lines traced; crops |
| Smugglers' Notch | PDF strokes + outlined glyphs on label boxes, leader lines, over a low-resolution painting | 82 (68 + 14) | glyphs read on sheets; 73 pieces named by the label on them or the leader ending on them, 26 settled on crops, 1 cut; checked against the resort's trail report; crops |
| Whistler Blackcomb | PDF strokes + outlined glyphs and text over a low-resolution painting, a main map and two insets as three panels | 232 (209 + 23) | glyphs read on sheets; 228 pieces named by the name at their end or along them, 147 settled on crops and 23 found not to be trails, 13 cuts; meeting points checked against the resort's ArcGIS run lines; names and ratings against its trail report; every overlay audited on crops |
| Park City | PDF strokes + outlined glyphs over a low-resolution painting, a main map and a redrawn inset | 345 (252 + 93) | glyphs read on sheets; 446 pieces named by the name at their end or along them, 97 settled on crops and 12 found not to be trails, 5 cuts; names, ratings and sides checked against the resort's trail report, lines two names could share against OpenStreetMap's runs and the PDF's drawing order; every overlay audited on crops |
| Palisades Tahoe | three PDFs (the Palisades side, Alpine's front and back) of strokes + outlined glyphs over a painting, as three panels | 247 (124 + 123) | glyphs read on sheets; 234 pieces named by the name at their end or along them, 54 settled on crops and 4 found not to be trails, 1 cut, 1 stretch traced; names, ratings and mountains checked against the resort's trail report, lines two names could share against the PDF's drawing order and OpenStreetMap's runs; every overlay audited on crops |
| Big Sky | three PDFs (the main map of its three mountains, the South Face and Bowl insets) of strokes + text over a painting, as three panels | 323 (290 + 33) | 343 pieces named by the name at their end or along them, 55 settled on crops and 30 found not to be trails, 15 cuts, 5 trimmed where they run on under another line; names, ratings and mountains checked against the resort's trail report, lines two names could share against the PDF's drawing order and OpenStreetMap's runs; every overlay audited on crops |
| Heavenly | the 2024-25 map as an image only (the California and Nevada sides and the Top of Gondola inset, two panels); its lines, names and symbols from the 2022-23 PDF of the same artwork (lines as filled outlines, names as outlined glyphs), registered on the image | 120 (73 + 47) | glyphs read on sheets; 45 pieces named by the name at their end or along them, 19 settled on crops and 6 found not to be trails, 3 stretches traced (2 labels the image prints elsewhere than the 2022 page, 1 name on two lines); most runs have no line: the stretch along the name printed on the run is its overlay; every change since 2022 checked on the image; names, ratings and areas checked against the resort's trail report, lines two names could share against OpenStreetMap's one-way runs, the PDF's drawing order and an older edition's navigation map; every overlay audited on crops |

Where each resort's decisions live: each piece's name is in
`trailProposals.json` (a vector extraction is deterministic, so a PDF map's
piece ids are stable), stretches and markers in `trailReviews.json`
(`"by": "claude"` unless a person decided). Vail's and Hunter Mountain's
pipelines are in the repo, in `tools/trailmap/resorts/<id>/`, and so are
Wildcat's, Sunday River's, Sugarloaf's, Smugglers' Notch's, Whistler Blackcomb's (per panel), Park City's, Palisades Tahoe's, Big Sky's and Heavenly's (per panel): decisions are kept as points (Vail's raster piece ids change
whenever the detector is re-tuned) and `regen.sh` rebuilds every file of the
resort from them (byte for byte). Hunter's is the template for a PDF map: `resort.py` says how the
map prints things, `decisions.py` holds what the crops settled, and
`tools/trailmap/pdf_resort.py` does the matching and runs the pipeline. The
one-off scripts that built the PDF maps before Hunter were not kept; step 1
records their methods.

**To fix one trail on any resort** without re-running a pipeline: add a review
for it to its `trailReviews.json` (`status: confirmed` with `polylines` ids
and/or `drawn` points in source px, or `no-line` with `labelAt` in percent;
leave out `"by": "claude"`), then
`npm run trails:apply -- --resort <id> [--panel <panel>]`. A person's review
outranks every automatic source, and Vail's `regen.sh` keeps it.

## The short version (Killington: raster map, readers, human review)

1. **Get the best source image** (lossless, from the resort PDF). 5 min.
2. **Detect the colored trail lines** and cut them into numbered pieces
   (existing detector; retune colors per map). 30–60 min per new map style.
3. **Name the pieces with parallel AI readers** looking at zoomed, numbered
   tiles. ~25 min wall-clock, no human.
4. **Human review** on a review page: confirm or fix each trail, draw lines the
   detector missed, mark glades/not-on-map. ~35 min for 166 trails.
5. **Second AI pass** for difficulty symbols and trails nobody placed; then a
   **whole-map search** before removing anything. ~15 min, no human.
6. **Human recheck** of what the AI changed (a handful of trails). ~5 min.
7. **Apply and verify** (scripts + browser hover check). ~5 min.

Steps 3, 5 and the checks are the reusable core; the old fully automatic
approaches all stalled at ~40% (see "What we tried").

**The PDF-first version** (Whiteface onward): get the
PDF or the CDN painting (step 1); extract the pieces and names; match names to
pieces automatically and settle the rest on crops yourself, recording each
decision (step 3c); seed the trail list from the printed names and symbols
(`seed_roster.py`); build proposals, stretches and markers
(`aggregate_readings.py`, `traces_to_reviews.py`); `trails:apply`; then audit
every overlay on crops and run the hover check (step 4).

## Tools in this repo

| file | what it does |
|---|---|
| `tools/trailmap/extract_pdf_image.py` | Lossless raster from the resort PDF; reports any vector text/lines |
| `tools/trailmap/extract_pdf_vectors.py` | Map image + numbered pieces straight from a PDF's vector trail strokes (`--solid`: without the dashed ones) |
| `tools/trailmap/pdf_symbols.py` | Difficulty symbols from a vector PDF; `--check` compares them with the trail list |
| `tools/trailmap/pdf_labels.py` | Trail-name labels from a PDF's text (decodes fonts with no Unicode map) |
| `tools/trailmap/pdf_glyphs.py` | Trail-name labels and symbols from a PDF whose names are outlined glyphs (no text); `--turned` / `--turned-hole` tell apart two characters drawn as one shape turned over (n/u, 6/9); `--rect-squares`, `--rounded` read squares drawn as rectangles and symbols with rounded corners; `--reorder` puts glyphs drawn out of turn back in reading order |
| `tools/trailmap/matte_pdf_layer.py` | A PDF's vector layer matted over a sharper copy (or smooth upscale) of its painting; `--resample` swaps paintings for an upscale and renders the page as it is (keeps an inset's clip) |
| `tools/trailmap/raster_lines.py` | Numbered line pieces from a raster map (no PDF): colour masks, linked dashes, skeleton |
| `tools/trailmap/raster_symbols.py` | Difficulty symbols (square, circle, diamond, double, EX) from a raster map |
| `scripts/lib/lineDetector.mjs`, `scripts/evaluateLines.mjs` | Colored-line detector and its ground-truth scorer |
| `scripts/tracePolylines.mjs` | Detection mask → numbered line pieces (`src/data/resorts/<id>/linePolylines.json`) |
| `tools/trailmap/grid_crop.py` | Zoomed crop with a labelled pixel grid, optionally pieces (`id:name`), overlays and symbols: for reading coordinates and review tiles |
| `tools/trailmap/snap_trace.py` | Rough points read off a grid crop → a stretch on the painted line, for lines the detection missed |
| `tools/trailmap/piece_sheet.py` | Contact sheets with each piece alone on its own crop, for maps where one line carries several runs |
| `tools/trailmap/symbol_audit.py` | Symbols off their trail's overlay or at an overlay end, and a contact sheet of every diamond |
| `tools/trailmap/resorts/vail/` | Vail's pipeline: readings, point-keyed decisions, `regen.sh` (see its README) |
| `tools/trailmap/pdf_resort.py` | A PDF map's names → pieces (auto-match + `decisions.py`), stretches along names printed in a line's gap, then the whole pipeline into `src/data/resorts/<id>/`; `add` records decisions as points |
| `tools/trailmap/resorts/hunter/` | Hunter Mountain's pipeline (`resort.py`, `decisions.py`, `header.txt`, `regen.sh`): the template for a PDF map |
| `tools/trailmap/resorts/wildcat/` | Wildcat Mountain's: a map whose lines carry several runs each, named on crops |
| `tools/trailmap/resorts/sunday-river/` | Sunday River's: outlined glyph names (`letters.json`), a main map and insets at different scales (`prepare.py`) |
| `tools/trailmap/resorts/sugarloaf/` | Sugarloaf's: names printed as numbered circles referring to a key (`ON_CIRCLE`), a raster inset traced on crops (`TRACED`) |
| `tools/trailmap/resorts/smugglers-notch/` | Smugglers' Notch's: names on label boxes whose colour is the rating (`COLOR_SYMBOL`), leader lines to a line or a glade's circle (`prepare.py`) |
| `tools/trailmap/resorts/whistler-blackcomb/` | Whistler Blackcomb's: one PDF page read as three panels (`PANELS` in `resort.py`, each panel's settings and decisions in `panels/<panel>/`), glades as black lines under white dashes (`GLADE_LINES`) |
| `tools/trailmap/resorts/park-city/` | Park City's: a main map and a redrawn inset at another scale (`prepare.py`), the bits of line redrawn over crossings dropped, names in grey ovals with their symbol under the oval (`SYMBOL_OF`) |
| `tools/trailmap/resorts/palisades-tahoe/` | Palisades Tahoe's: three PDFs read as three panels (`prepare.py`: strokes drawn twice give one piece, a stroke hidden under another colour's none), names not printed along their line kept off it (`NO_STRETCH`) |
| `tools/trailmap/resorts/big-sky/` | Big Sky's: three PDFs read as three panels, names as text spelled as the resort's trail report spells them (`report.json`, `NAMES`), lines drawn as filled ribbons read by their centre lines and cut at an inset's frame (`prepare.py`), a name's own line before the one ending at it (`ALONG_FIRST`), thin lines drawn on under wider ones trimmed (`TRIMS`) |
| `tools/trailmap/resorts/heavenly/` | Heavenly's: the current map as an image (two panels) with its lines, names and symbols from an older PDF of the same artwork registered on it (`AFFINE`), what the image no longer prints left out (`GONE`); lines as filled outlines read by their centre lines, dashes chained, branched outlines by their skeletons (`prepare.py`); names printed along runs with no line as the runs' overlays (`LABEL_LINE`); a name's two parts picked by where they are printed (`JOIN`) |
| `tools/trailmap/pdf_overlaps.py` | Overlays lying along another trail's line for a PDF resort (a line drawn on under another, or two runs on one stroke): each to check on a crop |
| `tools/trailmap/fetch_pdf.cjs` | Downloads a PDF from inside the resort's page in headless Chromium (Vail Resorts' sites refuse curl) |
| `tools/trailmap/render_tiles.py` | Zoomed tiles with every piece drawn and numbered, for the readers |
| `tools/trailmap/prompts/*.md` | Reader prompts: name pieces, symbols + missing, whole-map search |
| `tools/trailmap/aggregate_readings.py` | Readers' votes → per-trail proposals + review-page data |
| `tools/trailmap/review/index.html` | The review page (Claude artifact with a database) |
| `tools/trailmap/refresh_review_data.py` | Rebuild page data after fixes; flag trails for recheck |
| `scripts/importReviews.mjs` (`npm run reviews:import`) | Review-page export → `src/data/resorts/<id>/trailReviews.json` |
| `scripts/applyTrailProposals.mjs` (`npm run trails:apply`) | Reviews + proposals → `src/data/resorts/<id>/trailPaths.json` (what the app draws) |
| `tools/trailmap/render_crops.py` | Zoomed crops of overlays for audits and split checks |
| `tools/trailmap/region_audit.py` | Every overlay tagged with its name over map regions, to audit a whole map |
| `tools/trailmap/hover_check.cjs` | Browser check that each overlay shows its own name |

Python tools need `pip install pymupdf pillow` (`pdf_labels.py` also
`fonttools`; the raster tools `numpy opencv-python-headless scikit-image`);
the hover check needs Playwright (in this sandbox:
`PLAYWRIGHT_PATH=$(npm root -g)/playwright`). The pipeline scripts take
`--resort <id>` and, for a resort drawn on several panels, `--panel <id>`.

## Step by step

### 1. Source image

Download the resort's trail map PDF (not the web JPG) and run
`extract_pdf_image.py map.pdf map.png`.

Getting the source in this sandbox:
- **Vail Resorts' sites** (vail.com, breckenridge.com, keystoneresort.com, …)
  return an error page to curl. Open the trail-map page in headless Chromium
  through the agent proxy and fetch the PDF from inside the page (`fetch` in
  `page.evaluate`), or list the links and responses that mention pdf or map.
  Playwright's Chromium needs `proxy: { server: process.env.HTTPS_PROXY }`
  and `--ignore-certificate-errors-spki-list=<pin>`, where the pin is
  `openssl x509 -in /root/.ccr/agent-proxy-ca.crt -pubkey -noout | openssl pkey -pubin -outform der | openssl dgst -sha256 -binary | base64`.
  Load Playwright from `$(npm root -g)/playwright`.
- **Their image CDN (scene7) works with plain curl** and serves the full
  paintings losslessly:
  `https://scene7.vailresorts.com/is/image/vailresorts/<name>?req=imageprops`
  gives the size, `?fmt=png-alpha&wid=<width>&qlt=100` the image. Names seen:
  `20251028_KY_winter-trail_map_001` (Keystone),
  `20251001_VL_winter-{front-side,back-bowls,blue-sky}-trail_map_001` (Vail;
  the `-logos` copies add a header band). Find a resort's name in the image
  URLs of its trail-map page.
- **skimap.org** often has the PDF when the resort's own sits behind a bot
  check (Whiteface). Third-party "PDFs" can be just the rasters again
  (SnowStash's Vail PDF is the same three panels).
- **Out of reach here:** OpenStreetMap's Overpass API (connections reset), so
  there is no cross-check of names against OSM. Vail's terrain-status feed
  lists no trails out of season, so it can't seed a trail list in October.

- If it reports **text words and vector drawings**, stop and extract those
  instead: exact names, positions and line geometry, no CV needed. Worth
  asking the resort for the layered Illustrator/PDF file — Killington's PDF
  metadata shows it was made in Illustrator and flattened.
- **Vector trail lines (Stowe 2025-26):** the painted background was one
  raster and every trail line, label and symbol a vector on top (outlined
  text, so no words). `extract_pdf_vectors.py` renders the map area to
  `public/maps/<id>.jpg` and writes each trail-coloured stroke as a
  numbered piece — exact geometry, no detector, no tuning (165 pieces;
  `--append` adds another colour, e.g. orange freestyle lines, later).
  Find the colours by tallying stroke colours/widths with pymupdf and
  drawing them on a blank page; lifts were the thicker maroon strokes.
  Okemo 2025-26 is built the same way (256 pieces: 0.74 pt green, blue and
  black strokes plus orange park lines; lifts are 1.11 pt red). Its legend's
  hatch pattern is 1.0 pt black strokes (keep them out with `--max-width`),
  and the extractor drops small closed loops (a legend icon had come out as
  a piece). Check the whole map on zoomed crops with the pieces drawn on.
  Sugarbush 2025-26 too (0.75 pt strokes), except three odd trails: two
  drawn in pure black or at 1.0 pt (`--append` with `--min-width`) and one
  as a filled outline (`--filled`); tally every stroke colour/width before
  trusting the first extraction.
- **Labels as real text (Jay Peak 2025-26):** a painted map that draws
  *no trail lines at all*, but every trail name is PDF text (one font and
  size range) with its difficulty symbol drawn just before it. The trail
  list then comes straight from `page.get_text('dict')` spans plus the
  nearest symbol fill (no readers): drop the non-trail spans (lodges,
  first aid), dedupe labels drawn twice (halo + fill), and look for names
  printed only in an inset. With no pieces, every overlay is a trace
  along the painted cut (step 3b), and glades, parks and inset-only names
  are markers at the label. `render_tiles.py` tiles the whole image when
  there are no pieces.
  Jay Peak's trace pass: 9 tracer groups, 71 trails, ~3.9M tokens and ~4 h
  of wall-clock in all (the base-area group alone ran over 2 h: slow zones,
  parks and lifts crowd it). Every trace was checked on a zoomed crop;
  65 kept as lines; 6 whose label sits in painted trees with no cut became
  markers (4 were the tracers' own NO CUT calls; Tuckerman's Chute and
  Deliverance were low-confidence guesses rejected on the crop, one of them
  running 30 px from another trail's line). A session limit killed 8 of the
  first 12 tracer runs mid-way; re-run those groups as fresh workflows
  with their own output directory (resume replays the failures).
- **Both at once (Whiteface 2025-26):** vector trail strokes *and* every
  name as text in the trail's colour, with its symbol beside it. No readers
  were needed: each name was matched to the stroke it is printed along, or
  whose ends sit at the two ends of the text (this map prints most names in
  a gap of their own line), names spread along unlabelled continuations,
  and ~40 unclear pieces were settled on zoomed crops (four strokes cut
  where two trails meet). Where the name fills the gap, the overlay gets a
  stretch drawn along the name's own characters (`page.get_texttrace()`),
  so trails whose only "line" is their label still get one. The official
  PDF sat behind a bot check; skimap.org had the same file.
- **Text with no Unicode map (Winter Park 2025-26):** strokes and names as
  text like Whiteface, but the name font is a subset with no ToUnicode map,
  so `get_text()` gives U+FFFD for every character. `get_texttrace()` still
  gives each glyph's index in the subset, and the subset's CFF charset
  names it `gidNNNNN`, its index in the full font: in the usual Adobe order
  space is 1, 0-9 are 17-26, A-Z 34-59. `pdf_labels.py` decodes that and
  lists the glyphs it can't; check those on a rendered label (here a hyphen
  and an opening quote: `--glyph 316=- --glyph '63=‘'`). The legend has five
  tiers: advanced intermediate (a blue square holding a black diamond, its
  trails drawn as black lines) became black and EX (two diamonds with a
  white E and X inside, told apart from the black rounded-square icons by
  those letters) double-black. Lines run straight into their names, so a
  piece whose end sits on a name's own text line, just before its first or
  after its last character, continues that trail (163 of 232 pieces). The
  PDF's drawing order groups each trail's labels with its pieces (Z to A),
  which settled most of the rest, but it is off by one at group boundaries
  in places: the crop decides. 58 names have no line (parks, bowls, painted
  chutes, the Cirque's numbered runs from its key): markers.
- **Text, painted background at low resolution (Breckenridge 2025-26):**
  strokes and Unicode text like Whiteface, but the PDF's painted background
  is a small 1482x962 image. Vail's image CDN (scene7) serves the same
  painting sharper (`<name>?req=imageprops` gives its size; request
  `?wid=<width>&hei=<height>`), so the map image is the PDF's vector layer
  matted over it: render the page twice with the background image swapped
  for flat white and flat black (`page.replace_image`), alpha =
  1 - (white - black) / 255, colour = black render / alpha. Vail's trail-map
  pages and PDFs return an error page to curl; open the page in headless
  Chromium and fetch the PDF from inside the page (`fetch` in
  `page.evaluate`). The text holds many copies of each name: curved labels
  also as one object per letter, objects holding several names, and two-line
  names both as separate lines and joined; keep one per position and drop
  any label whose characters all belong to other, shorter labels. Lines are
  drawn into their names (the legend's "-◆ Name-"), so a piece ends at the
  name's symbol or text end; the drawing order does not group lines with
  names here. EX is two diamonds holding a white E and X. Chute names inside
  a bowl print no symbol of their own and take the bowl's. Legend, lift-stats
  and ad panels sit on the map: `extract_pdf_vectors.py --exclude` keeps
  their line samples out.
- **Outlined names and outlined lines (Copper Mountain 2025-26):** no text
  at all. Every name is a set of filled glyph outlines, and most trail lines
  are strokes converted to filled outlines; a few are plain strokes, and the
  Tucker Mountain lines are clip paths filled with a fading image. Names:
  group the glyph fills by shape, using the outline's item kinds plus its
  chord lengths over their total (unchanged by rotation and size). Render
  one example per group upright on a contact sheet (rotate by the direction
  to the next glyph) and read each group's letter once. Key that table by
  the shape signature; cluster ids shift whenever a threshold changes.
  Glyphs are drawn in reading order, so a label is a run of consecutive
  same-colour glyphs under ~9 pt apart, and a word gap is an outline gap
  well over the label's median letter gap. Glyphs drawn twice leave
  fragment copies: keep the longest, and of equal copies the last drawn. A
  name recoloured for this season is drawn over its old colour (Sno Deal,
  Carefree). Symbols are fills too: square, diamond, double diamond (an
  8-line outline), EX (a double diamond holding white E and X fills) and
  circle (four curves). Lines: rasterise each outline at 6 px/pt and thin
  it to a 1 px skeleton (Zhang-Suen). Build the pixel graph without the
  diagonal steps a 4-neighbour path already joins (otherwise every
  staircase forks), prune spurs under 2.5 pt and trace polylines between
  forks. Drop the logo, highway shields, arrows and icons by `seqno`. The
  embedded painting is only 1817x1465 and no sharper copy turned up, so the
  map image mattes the vector layer, rendered at 3 px/pt, over the painting
  upscaled with Lanczos instead of the renderer's blocky upscale. Names set
  apart from their symbol were settled on crops.
- **Outlined names, stroked lines (Keystone 2025-26):** names are outlined
  glyphs as at Copper, but the trail lines are plain 1.5 pt strokes
  (`extract_pdf_vectors.py`, plus a pass at 1 pt for two thinner lines).
  `tools/trailmap/pdf_glyphs.py` does the glyph work as a tool:
  - `collect` the fills in the name colours;
  - `sheet` draws each unread shape upright between its grey neighbours;
  - `read` records `shape=char`;
  - `labels` joins the runs and finds the symbols.
  The shape table is keyed by signature and size (o/O, s/S share a shape).
  Re-run on Copper, it reproduced every checked label.

  Keystone specifics:
  - The font is condensed, so a word gap is measured between outlines along
    the reading direction (`--space 0.75`).
  - Its capital I is the l shape: a word-initial l is an I.
  - Comma and apostrophe are one shape turned over, told apart by which side
    of the line they sit on.
  - A label recoloured this season sits over its old copy; keep the last drawn.
  - Most names are printed on their own line, and a few in a gap of it
    (stretches).
  - Names printed in other colours are zones: the orange park runs and the
    gold kids' adventure zones are markers.
  - The map image is the vector layer matted over Vail's CDN raster
    (`20251028_KY_winter-trail_map_001`), as at Breckenridge.
- **Raster panels, no PDF (Vail 2025-26):** Vail publishes no vector map,
  only three paintings on its image CDN
  (`20251001_VL_winter-{front-side,back-bowls,blue-sky}-trail_map_001`,
  PNG at `wid=4990`; the `-logos` copies add a header band), so the resort
  has three map panels (see "Several panels" below).
  - Lines: `raster_lines.py` masks each trail colour strictly and drops text
    (glyph-sized parts crowded by other glyphs, unless thin like a stretch of
    line), symbols, icon fills and sign-box outlines. Dashed roads are linked
    by growing their dashes and arrows until consecutive marks merge (a run
    needs four or more). The mask is skeletonized and the pieces are joined
    straight through junctions. Back Bowls and Blue Sky draw everything
    bigger: `--k 1.75` and `--k 2.7` scale the mark sizes.
  - Symbols: `raster_symbols.py`. A double diamond is a black blob with a
    waist, or two diamonds side by side. Check every one on a contact sheet:
    a single diamond touching the end of its own line passed as a double
    twice, and icons and the village's bus-route marks passed as singles.
  - Vail prints a run's symbol on its line with the name beside it, and the
    line resumes past the name. Where a run's rating changes it prints the
    new symbol on the line with no name; those count toward the run's
    difficulty (majority, harder on a tie).
  - Naming: about a third of the pieces matched a symbol automatically; the
    rest were settled on zoomed review tiles (step 3c). Record each decision
    as a point on the piece, not its id: ids change whenever the extraction
    is re-tuned. The same goes for the symbol readings (keyed by centre).
  - Stretches the detector broke (a name printed in the line, dashes
    through slow-zone hatching, the stub from a symbol to its parent line)
    were traced on crops, snapped to the painted line (`snap_trace.py`) and
    appended to `linePolylines.json` as pieces (listed in `_traced`).
  - Bowls print a name and no symbol: markers, rated black.
  - Everything is in `tools/trailmap/resorts/vail/`: the readings
    (`names.py`), the decisions (`decisions.py`, with the crop that settled
    each), and `regen.sh`, which downloads the panels and rebuilds every Vail
    data file and map image byte for byte. Its README is the template for
    another raster resort.
- **Text names in a gap of each line, vector painting (Hunter Mountain
  2025-26):** the painting is vectors too (246,000 drawings: rendering the
  page takes ~30 s), and every trail is a 0.38 pt stroke in its difficulty
  colour (lifts are thicker maroon strokes) that runs into its name: the
  name is printed in a gap of the line, with its symbol at the uphill end.
  `tools/trailmap/resorts/hunter/` builds it with `pdf_resort.py`:
  - Names: FuturaPTCond-Medium 3.8 pt text. A name is drawn twice (halo),
    curved names also one object per letter, and two names that sit together
    are also drawn as one object (TAYLOR'S RUN WHICH WAY GLADES): keep one
    copy of each, keep the parts. Four names are printed in two parts (UPPER
    EAST / SIDE DRIVE, MAD / BOX, ...): `JOIN` in `resort.py`.
  - Symbols have rounded corners, and a double diamond is one outline
    (`pdf_symbols.py --rounded`): 73 symbols, one per name.
  - Matching: each name end (just past its first or last character, or its
    symbol) takes the nearest piece end within 4 pt, preferring the symbol's
    colour. A piece with one end at a name's text and the other at the next
    name's symbol belongs to the first (the line goes on from its label until
    the next trail starts). Then continuations. That named 127 of 129 pieces;
    2 were settled on crops (Park Avenue West's line below its two-line
    label, Belt Parkway Bypass's line set beside its name), and Upper
    Crossover's line is its label alone.
  - Each name printed in a gap gets a stretch along its own characters, from
    the symbol, so the overlay runs through the label (66 stretches).
  - Glades print a tree icon, a diamond and no line: markers. Extract the
    pieces with `--min-length 0.8`: ten real stubs (the line between a
    symbol and the next trail) are under 4 pt.
- **Names along the line, one line for several runs (Wildcat Mountain
  2025-26):** this season's PDF outlines the names and flattens most lines
  into the painting, but skimap.org's earlier export of the same artwork
  (map 33684) has 3.27 pt strokes and real text. The two pages differ by a
  23.77 pt bleed (registered on renders, scale 1.0000); every old name lands
  on the same outlined name in this season's page, and this season prints no
  other name (only the dining box differs). The map image is this season's
  page from scene7 (`20251226_WC_winter-trail_map_001`, registered to the PDF
  within 0.2 px).
  - The map prints a run's symbol and name along its line (no gap), and one
    stroke often carries several runs: Upper, Middle and Lower Lynx; Top Cat
    and Starr Line; Cat Track, Middle Wildcat and Bobcat (whose join is
    hidden under Wild Kitten's line). So `resort.py` turns the name-end
    matching off (`MATCH_ENDS = False`); a name printed along a piece still
    names it (31 pieces), and the rest was settled piece by piece on contact
    sheets (`piece_sheet.py`: each piece alone on its own crop) and closer
    crops: 20 decisions, 3 unnamed links and 9 cuts.
  - Labels set beside their line point at it with an arrow (Hairball,
    Sphynx, Leo's Leap, Annie's Alley). Lower Cat Track's arrow points at
    Wild Kitten's line: its overlay is that stretch (`TRACED`).
  - Curved names are drawn one object per letter: `pdf_resort.py` joins
    consecutive letters of one colour into a label, taking its spacing from
    the whole-word copy when there is one. Symbols are 10-15 pt and rotated
    (`pdf_symbols.py --max-size 16`); the green FIRST AID CENTER lettering is
    outlined in the trail green (`--exclude`).
  - The tree-skiing areas print a diamond and no name, so they aren't trails
    here; the map's own count is 48 trails, as listed. No double diamonds.
- **Outlined names, insets at their own scales (Sunday River):** the map on
  sundayriver.com's resort maps page (the 2023-24 artwork, still current)
  is one vector page with the main map and three insets (North Peak
  backside, Merrill Hill frontside, the South Ridge base lodge).
  `tools/trailmap/resorts/sunday-river/prepare.py` extracts it:
  - Lines: 1 pt strokes on the main map, 0.49 pt in the North Peak inset,
    1.53 pt in Merrill Hill's and 2.04 pt in the base lodge's, each group cut
    to its own frame (an inset's lines run on under its frame, clipped
    there), and the main map's cut out of the insets. One line (White Heat)
    is a filled-and-stroked path (`--filled`).
  - Names: outlined glyphs, 163 shapes read on four contact sheets
    (`letters.json`). Word gaps are in points and each inset's letters have
    their own size, so labels are joined once per scale. Three names are in
    other shades (BEAR PAW and the inset's ROUNDABOUT in slightly different
    greens, DOUBLE BLIND's diamonds in dark grey): tally every small fill
    colour before trusting the first pass. Labels and symbols drawn outside
    their clip (an inset's names past its frame) are hidden: dropped.
  - A few names are real text (UPPER and LOWER prefixes, Merrill Hill's
    names), joined to their glyph names where printed on two lines.
  - Matching: names sit on label boxes over their lines, so a name names the
    line it is printed along (`MATCH_ENDS = False`), the nearest only in the
    crowded inset (`ALONG_NEAREST`). Black names print a single or double
    diamond (`pdf_glyphs.py --double-dist 1.7`: this map's two diamonds have
    a gap), green and blue names no symbol. A glade's diamonds sit above the
    middle of its name (`SYMBOL_CENTRE`).
  - One line often carries an upper and a lower run (Risky Business, T72,
    Caramba, Vortex, Air Glow): cut between the two labels where another
    line crosses. The inset labels two such lines without Upper or Lower;
    those inset lines are left unnamed rather than made into a third trail.
  - Prism's lower stub is left unnamed: the main map leaves Prism's middle to
    the Merrill Hill inset, and `trails:apply` would bridge the two stubs
    straight across the trees.
  - 18 glades (names in the trees with diamonds, no line) and three other
    names with no line are markers.
- **Numbered key circles and a raster inset (Sugarloaf):** the 2025-26 map on
  sugarloaf.com's trail-map page is one vector page over a painting of only
  1590x1146 px for 1530x1323 pt, so the map image is the vector layer matted
  over a smooth upscale (`matte_pdf_layer.py --xref 159`).
  `tools/trailmap/resorts/sugarloaf/prepare.py` extracts it:
  - Lines: 1.2 pt green and blue strokes, 1.15 pt black ones and the Golden
    Road's orange dashes. The legend's other dashed routes (egresses, the
    King Pine X-Cut, the Burnt Mountain Trail, a cat road) are not in the key
    and are left out; its blue dashed logging roads come in with the blue.
  - Names: outlined glyphs, 222 shapes read on contact sheets
    (`letters.json`); the east side's names are text (GillSansNova-Bold,
    5.1-5.3 pt by its matrix). Double diamonds drawn as one outline are up to
    11.6 pt tall (`pdf_glyphs.py collect --max-size 12`). Glyphs read as `*`
    (lift and lodge icons, the compass) make no names.
  - Glades and connecting trails are red numbered circles referring to the
    key below the map, read off the key into `resort.py` (`KEY`). A one-digit
    circle is a lone glyph (`pdf_glyphs.py labels --single red`), and 6 and 9
    are one outline turned over: the half that holds the loop decides. Each
    circle becomes a name at its centre. A circle printed on a line names the
    unnamed line under it (`ON_CIRCLE`, about the circle's radius in pt); one
    in the trees with no line is a glade (`GLADES` for those whose name
    doesn't say so).
  - Matching: names sit in a gap of their line with the symbol past one end
    of the label (`SYMBOL_REACH` 12 pt), so ends match as on Hunter. 78
    pieces were settled on crops: links between runs, a short stub between
    two labels, a line two runs share (`TRACED` for the second one).
  - The Snowfields (the summit) is drawn again in an inset, a raster with its
    lines baked in. Each of its ten lines is traced from rough points snapped
    onto the black line (`snap_trace.py --rgb 20,20,25 --tol 45 --r 6`),
    through its label (`TRACED`). The main map draws the same runs small,
    each with its key circle.
  - Markers with no symbol and no line take `DEFAULT_SYMBOL`: the back side's
    five chutes (circles 70-74, inset only) a double diamond, as every
    Snowfields run the inset rates; West Sluice Chute a single diamond, as its
    neighbours. Winter's Way Ext.'s double diamond sits above its circle, out
    of reach (`SYMBOL_OF`).
- **Label boxes, leader lines, the box's colour as the rating (Smugglers'
  Notch):** the map smuggs.com links (the 2024-25 artwork, still current) is
  one vector page over a painting of 2356x1596 px for 1695x1147 pt: matted
  over a smooth upscale. `tools/trailmap/resorts/smugglers-notch/prepare.py`
  extracts it:
  - Lines: 3.44 pt green, blue and black strokes; the terrain parks are
    7.46 pt orange lines (class `freestyle`).
  - Names: white outlined glyphs on label boxes in the run's colour, 103
    shapes read on sheets (`letters.json`). In this font n and u are one shape
    turned over, and so are ! and i: `pdf_glyphs.py labels --turned nu
    --turned '!i'` decides each by which half of the glyph its gap is in. Two
    names are white text (Bud's Way, and the Howie's of Howie's Wanderer,
    joined to its glyphs). The parks' names are black, in orange boxes.
  - The rating is the colour of the name's box (`COLOR_SYMBOL`); experts'
    runs print chains of two or three black diamonds on the line (double
    black). The resort's own trail report (smuggs.com, Conditions, Winter
    Report) lists every trail with its rating and mountain: all 80 trails it
    shares with the map have its rating and mountain. Its Burton Riglet Park
    is the map's Burton Treehouse Riglet Park; its Sir Henry's Learning Hill
    is printed only as a place (Sir Henry's Learning & Fun Park, no line or
    label box) and is left out; Bud's Way is on the map only.
  - A box sits on its line or off it with a thin leader (0.99, 1.17 or
    1.46 pt; some drawn filled-and-stroked) to the line or to a hollow circle
    (a glade). Each leader end becomes a name there; a box is tested against
    its outline, not its bounding box (rotated boxes). A leader stops a few
    points short of its line (`ON_CIRCLE` 3.5).
  - One line carries Upper and Lower Drifter: cut between their labels. An
    expert line from the Madonna summit to Catwalk prints a double diamond
    and no name, and the report has no other expert run: left unnamed.
  - Three mountains, grouped as the report groups them (`area()`,
    `AREA_OF` for names that cross between them). Midway prints a green box
    on Morse and a blue one lower down: `RATING` takes the report's Easy.
- **Three panels from one page, names checked against the resort's GIS
  (Whistler Blackcomb):** the 2025-26 PDF (fetched from inside the
  trail-maps page: the site refuses curl) has the main map (both mountains)
  on its second page and, on the first, two insets that draw terrain the main
  map leaves out: the Symphony Amphitheatre and the Blackcomb Glacier (a third
  inset repeats 7th Heaven and is left out). `resorts/whistler-blackcomb/resort.py`
  lists the three in `PANELS`;
  each has its own clip, scale and decisions in `panels/<panel>/`, and
  `pdf_resort.py whistler-blackcomb` reads them all, then writes one trail
  list (a name drawn on no panel gets one marker, on the first panel that
  prints it) and each panel's data. `prepare.py` extracts them:
  - Lines: 1.07 and 1.6 pt strokes in green (two shades), blue, black and
    purple (the family areas' adventure trails and outlines); 0.8 and 0.6 pt
    on the insets. A glade is a black line under white dashes: `prepare.py`
    flags its pieces and `GLADE_LINES` makes their names glades. A stroke
    drawn twice gives one piece; a stroke running on past an inset's frame is
    cut at it. Closed outlines (Tree Fort, Magic Castle) used to collapse to
    a point in `extract_pdf_vectors.py`'s simplification: it now splits a
    loop at its farthest point. The terrain parks' lines are solid orange
    strokes; the same orange dashed is an access route (and at 1.6 pt the
    boundary, at 0.85 pt cliff hatching), so `--solid` takes them without
    the dashed ones.
  - Names: outlined glyphs (252 shapes read on sheets, `letters.json`) and
    some text. Labels hidden under a later one with other text (last
    season's names: Big Bang under Sylvain) are dropped (`hidden()`); one
    glyph run holding two names is cut (`SPLIT`: Glacier Drive / The Bite).
    Diamonds drawn twice made false double diamonds until `pdf_glyphs.py`
    dropped coincident copies; notched double diamonds need `--even 1.6`,
    small diamonds `--sym-min 2.2`, and a rounded double diamond and the
    insets' rectangle squares are found by `odd_symbols()`.
  - Names are printed both ways (in a gap of the line, or beside it), so
    `NO_STRETCH_BESIDE`: no stretch along a name whose own line, as finally
    named, runs along its characters; no stretch through a name printed on
    two lines (it would zigzag).
  - Names printed twice with different symbols are two runs on the report
    (`RENAME_AT`: Seppo's / Seppo's - Lower, Mainline - Upper / Lower); names
    printed twice with the same symbol are one (`RENAME`: Greenline's GREEN
    LINE, Kadenwood Trail's KADENWOOD).
  - The resort publishes its run lines as an ArcGIS layer (Ski_Runs_GDB, with
    names and ratings). Not on the map's projection, but locally an affine
    fit to the named lines around a junction puts them within ~20 px: where
    two trails' pieces meet on the map, their GIS runs should meet too. Ten
    meeting points didn't, and six were naming errors: the line below
    Sunnyside Up's label is Sunset Boulevard's, the one beside the Harmony
    Express Camel Humps', the blue line under Straight Shot's label White
    Light's, Big Easy goes on below Over Easy, Sidewinder starts where Marmot
    ends, and a loop from the Roundhouse the map doesn't name is the GIS's
    Peak Traverse (no overlay). It also settled Secret Bowl, Jolly Green
    Giant and Emerald Forest.
  - Then every overlay was audited on crops, one cell per trail (its overlay,
    the other overlays thin, its labels boxed), which found what the
    meeting-point check can't see: the parks' own orange lines (left out of
    the extraction until then: the parks had been markers); the short line
    above Dave's Day Off's symbol is its top (Brownlie Basin, printed beside
    it, is a basin with no line); the line under the park's pill is Green
    Acres' (Coyote and Bobcat start on it); Upper Whiskey Jack's line turns
    west at the Emerald chair into a link the map doesn't name (the GIS's
    Pig Alley); Rabbit Tracks is printed over its own line (`LABEL_LINE`);
    The Glades is a groomed run, not a glade (`NOT_GLADES`); Expressway is
    a run on each mountain, two trails (`RENAME_AT` plus `DISPLAY`, and
    each named piece now carries its trail id so the two stay apart); on
    the Symphony inset Adagio's stroke also took in the loop from the summit
    (Jeff's Ode to Joy's two upper routes in the GIS); and `trails:apply`
    had bridged a free end sideways onto a parallel line (now only an end
    pointing at the other piece, within 60°).
  - The trail report (the resort's terrain feed) has every printed name; its
    ratings differ for Big Easy (map blue, report green) and Harmony
    Horseshoes (map single, report double): kept as printed. Flute Bowl,
    North Flute Bowl and Glacier Road print two ratings: `RATING` takes the
    report's. Hover check 614/614, 56/56, 22/22.
- **Two names for one line, settled by drawing order and OpenStreetMap
  (Park City):** the 2025-26 PDF (fetched from inside the trail-map page:
  the site returns an error page to curl) is one page: the Park City side,
  Canyons, and the High Meadow Park inset (a kids' area, redrawn larger).
  Its paintings are about 1 px/pt, so `matte_pdf_layer.py --resample` swaps
  each for a Lanczos upscale and renders the page as it is (the inset's
  painting stays clipped to its frame). `prepare.py` extracts it:
  - Lines: 1.14 pt green, blue, black (two near-blacks) and orange (the
    parks) strokes, 1.54 and 1.57 pt in the inset, cut to its frame. An
    easier way down is its run's line drawn dashed and counts. Where lines
    cross the map redraws a short bit of line over the crossing's halo, and
    some dashed lines' first dash is drawn apart: bits under 4 pt lying by a
    longer line of their colour are dropped (90 of them), else each is an
    undecided piece.
  - Names: outlined glyphs (122 shapes read on sheets, `letters.json`), the
    symbol before the name; four small names are text. 6 and 9 are one shape
    turned over: `pdf_glyphs.py labels --turned-hole 69` decides by the half
    the hole is in (CLOUD 9, 94 TURNS). Names in parts (two or three lines)
    are joined (`JOIN`); bowls and tree areas are printed in grey ovals with
    their diamond under the oval, out of reach for one-line names
    (`SYMBOL_OF`). Expert lines through the trees print a double diamond and
    a name and no line: markers, like the ovals.
  - Names are printed in a gap of their line or beside it
    (`NO_STRETCH_BESIDE`). A name on two or three lines gets no stretch
    along it; where one sits between its symbol and its line, the symbol
    lies off the overlay (`symbol_audit.py --mode off`), and a stretch is
    traced from the symbol through the name to the line (`TRACED`: eight,
    Upper First Time and Turtle Trail among them, whose names cover most of
    their line).
    The inset prints Wapiti and Flying Salmon at its top edge with no line
    under them: those labels are dropped (`DROP` by point), or every label
    of a name printed in a gap gets a stretch.
  - The trail report (the resort's terrain feed, in a Common Crawl capture
    of its terrain page, March 2026) lists every name with its rating and
    lift pod: all 345 trails' ratings
    and sides agree with it, and its spellings replace the map's
    abbreviations (`RENAME`: 10TH MTN, MID-MTN, MEN'S SL, LADIES' SL;
    HARMONY, printed low on Upper Harmony's run, is its Lower Harmony).
  - Which run owns a line between two names: the PDF draws one run's
    strokes one after another, so a piece drawn among another run's strokes
    is worth a second look (`seqno` in `page.get_drawings()`), and
    OpenStreetMap's ski runs (`piste:type=downhill` ways, from an Overpass
    mirror), fitted onto the named pieces around a junction by a local
    affine fit (residual ~15-25 px), show where each run goes. Together they
    settled, among others: Sundog goes on below its symbol (10th Mountain is
    an oval), Willow Draw's dashed run-out reaches the base, Panorama's
    dashed line goes on below its second name, Silverado's below its name,
    Elk Dance's line ends at Upper Harmony's arrow, and four links and two
    run-outs the map doesn't name have no overlay. OpenStreetMap is not a
    source of truth where runs lie side by side (the fit can't tell them
    apart) and is checked against the drawing on crops each time.
  - Then every overlay was audited on crops (the Whistler cells), and
    `trails:apply`'s route bridging was watched: a junction that falls
    between two drawn points of a line is reached via the next point, so a
    piece is cut there (`CUTS`: Raptor Way's arc onto Sunrise's line).
    Hover check 849/849.
- **Three PDFs as three panels (Palisades Tahoe):** the resort publishes
  its 2025-26 map as three PDFs, one page each (curl works): the Palisades
  side, and Alpine's front and back sides. `resort.py` lists them as
  `PANELS` and `prepare.py` extracts each panel from its own PDF (its
  settings in `panels/<panel>/resort.py`); the two insets the Palisades
  side refers to (Shirley Lake and Silverado; Gold Coast to High Camp) are
  not published, so their runs are left out. The areas are the two
  mountains, not the panels: an Alpine trail drawn on both Alpine panels
  opens the first that draws it.
  - Lines: 1.26 pt strokes on the Palisades side, 1 to 1.1 pt on Alpine's
    (its front's black runs pure black, unlike the names' near-black).
    Alpine's back side draws every stroke twice: one piece. A stroke drawn
    under a later stroke of another colour along its whole length is
    hidden (a blue line left under Saddle's black one): no piece, or the
    piece and its name would be decided on a line nobody can see.
  - Names: black outlined glyphs in one condensed font on all three maps
    (142 shapes read on sheets, `letters.json`); word gaps differ per map
    (1.8 pt on the Palisades side, 0.9 on Alpine's: `--space`, read off a
    histogram of glyph gaps), d and p are one shape turned over
    (`--turned-hole dp`), and a few glyphs are drawn out of turn
    (`--reorder` sorts a label's glyphs along its line). A name printed
    over two lines or across a wide gap is joined (`JOIN`, `JOIN_GAP`).
  - Symbols: the Palisades side draws its squares as rectangles
    (`--rect-squares`, with `--even 1.8`), Alpine's symbols have rounded
    corners (`--rounded`), and a double diamond is one notched outline up
    to 14 pt across (`collect --max-size 14`). Some print above or below
    the middle of the name (`SYMBOL_CENTRE`). The High Camp gates are a
    number in a box with their symbols, not glyphs: `EXTRA` names them Gate
    1 to Gate 8 at their boxes, as the trail report does.
  - The trail report (the resort's mtnfeed terrain feed: its config at
    v4.mtnfeed.com names the resort id and a bearer token for
    mtnpowder.com's feed) lists every trail with its rating and lift area:
    247 trails' ratings and mountains agree with it but two (Gold Coast
    Ridge, printed with a diamond, isn't in it; the back side's Shooting
    Star, a square, isn't the report's green run at High Camp). Its
    spellings replace the map's (`RENAME`: D-5 to D-8, G.S., Ladies
    Slalom, Face Cliffs as The Face Cliffs). Names on both mountains
    (Rock Garden, Yellow Trail, Sun Bowl, Summer Road; the report lists
    both) are renamed on Alpine's panels to two trails, displayed alike
    (`DISPLAY`).
  - Settled on crops with the PDF's drawing order and OpenStreetMap
    (Park City's method), among others: Jagged Edge's line past its
    diamond (Bullet's ends above it), the arrowed Lost Lake Loop, Home Run
    leaving Mountain Run's line at a fork (`CUTS`), Burkhart's along the
    bottom of the Mountain Run oval past its square, Main Backside's line
    from the ridge to Bottleneck Gully's diamond, and Werner's Schuss's on
    down the Boomerang loop's right branch to East Runout's square. Main,
    Extra, Chimney and National are named in the sky above their chutes,
    each over a short line hanging from its symbol: no stretch along those
    names (`NO_STRETCH`), nor along Attic's (its line runs through its
    one-line name) or Broken Arrow's (a 2 pt stub at its diamond, no line).
    Bottleneck Gully's two-line name sits in a gap of its line between its
    diamond and a short line below: `TRACED` runs through it.
    Hover check 287/287, 149/149, 77/77.
- **Names as text, spelled by the trail report (Big Sky):** the resort's
  trail-maps page (a Sanity site: the PDFs are on cdn.sanity.io, named by
  their SHA-1, and curl works) publishes the main map and its South Face and
  Bowl insets as three PDFs: three panels, as Palisades Tahoe's. The areas
  are the three mountains (Lone Mountain, Andesite Mountain, the Spanish
  Peaks), from the trail report's lift areas (`AREA_OF`).
  - The trail report: the site's own scripts call
    `/api/reportpal?resortName=bs&useReportPal=true` (`true`, or nothing
    comes back), every trail with its lift area and rating (beginner,
    intermediate, advanced intermediate, advanced, expert, high exposure);
    `report.json` keeps name, area and rating. The app has four ratings:
    advanced intermediate (two blue squares) is blue, expert (the double
    diamond) and high exposure (a triple diamond outlined in red) double
    black.
  - Lines: 1.4 pt strokes in the four colours (the parks orange), the main
    green and blue routes 3.5 to 4.9 pt wide with their centre lines drawn
    again (copies, dropped), the insets' lines 2.1 pt and some drawn twice at
    two widths; the real-estate access trails pink, read as green (they are
    the village's beginner runs). A few lines are thin filled ribbons (a dark
    fill outlined in white, or a blue one over a white halo): their centre
    lines, from each point of one side to the nearest of the other (a
    ribbon's two sides are not the same length); a fill's colour matches a
    line colour within 0.01. Lines running on past an inset's frame are cut
    at it.
  - Names are text (`pdf_labels.py`) in the names' font, dark on a white
    halo copy (the parks' orange); a curved name is also drawn a letter at a
    time (`letter_runs` joins them). The map prints capitals: `NAMES` (the
    report's names) matches a printed name to the report's by its letters
    alone, case, spaces and punctuation aside, and shows the report's
    spelling. A name printed twice for two runs is renamed by where it is
    printed (`RENAME_AT`: Calamity Jane, Take a Bough and Powder River upper
    and lower); a run marked only by its symbol is named there (`EXTRA`: PB &
    J Way's blue upper part, its double square on the line).
  - Symbols are fills: a diamond is one path; two or three diamonds are one
    path, or one each overlapping (a cluster of fills); a path of several is
    a symbol of its own even where it touches the next one (the Whitewater
    chutes' triple diamonds). A symbol nearer another name than its own, or
    at the top of its line away from the name, is given to its name
    (`SYMBOL_OF`); two runs that leave one line below a symbol they share
    take it by default (`DEFAULT_SYMBOL`).
  - Names are printed along their own line, the symbol at one end; where one
    name's end or symbol lies at the end of a piece another name runs along,
    the piece is the second name's (`ALONG_FIRST`). Settled on crops with the
    PDF's drawing order and OpenStreetMap: fifteen strokes carrying two runs,
    or a run and a link (`CUTS`), among them Stillwater Traverse and
    Meriwether, Rips and Great Falls Gully, Lazy Jack and Cinnabar. `pdf_overlaps.py` then found the
    lines drawn on under others: Sacajawea's under Yellow Brick Road's wide
    line, Lone Wolf's inside White Wing's, Yellow Mule's under Lupine's, and
    Liberty Bowl's and Ace's along the traverses they leave; each stops where
    it meets the other line (`TRIMS`). Hover check 753/753, 125/125, 138/139
    (the miss: a point of the Turkey Traverse at a gully's foot).
- **The current map as an image, an older PDF of its artwork (Heavenly):**
  skiheavenly.com shows its 2024-25 map (still the current one) as a scene7
  image and links no winter PDF; skimap.org has the 2022-23 PDF of the same
  artwork. Its page registers on the image's two paintings (SIFT matches and
  RANSAC on renders: 5837 inliers on the main painting, median residual
  0.10 px; 0.25 px on the inset), fixed in `resort.py` (`AFFINE`), so a
  regeneration doesn't depend on feature matching.
  - Every place the editions differ: the difference of the warped page and
    the image, every region looked at side by side. A name or symbol the
    image no longer prints is left out (`GONE`: Widow Maker, now Lone Wolf;
    two moved labels and their squares); what it prints anew is `EXTRA`
    (Lakeview Park, Lone Wolf), and a moved label's stretch is traced where
    the image prints it. A check of each line piece and label against the
    image's ink (the share of points with its colour within 2 px) finds the
    rest.
  - Lines are filled outlines (the artwork's strokes outlined), not strokes:
    each outline narrower than the panel's lines is read by its centre line
    (split at its two farthest-apart points, each point of one side paired
    with the nearest of the other); a dashed line is one fill with one
    outline per dash, chained in drawing order. Arrowheads have a shape of
    their own (two curves and a notch); an outline with more area than one
    line of its length (two lines drawn as one, an arrowhead merged into its
    line) is skeletonised (`raster_lines.py`'s graph, junctions joined
    straight). The names' letters are outlines of the dark line colour too:
    a dark outline is a line only if it is long.
  - Names: outlined glyphs (`pdf_glyphs.py`); M and W are one shape turned
    over (`--turned WM`); O and zero match each other (a word with letters
    takes O); circles are drawn with 16 curves (`--circle-curves`); two
    diamonds one above the other are a double diamond (`--double-dist`).
    The trail report: Common Crawl's capture of the terrain-status page (its
    `FR.TerrainStatusFeed`, every trail with its area and rating), this
    season's and 2024-25's (`report.json`); names take this season's
    spelling, else 2024-25's; renamed runs keep the map's name.
  - Most runs have no line: the name is printed along the painted cut, the
    symbol before it. Such a name's stretch, from its symbol along its
    characters, is the run's overlay (`LABEL_LINE`); a name on two lines
    gets a traced stretch instead. Bowls, faces, woods, the canyons' named
    chutes (no symbol: the canyons' double diamond, `DEFAULT_SYMBOL`), the
    parks and the learning areas are markers.
  - `JOIN` takes a part as (text, (x, y)) where the nearest copy of a word
    is another name's (UPPER and MOMBO either side of a lift, another MOMBO
    below).
  - The lines at the top of the gondola were settled with OpenStreetMap's
    one-way runs (where each starts and what it meets: Von Schmidt from the
    Olympic Express top past Bonanza's and Easy Street's starts to
    California Trail) and an older edition's navigation map ("Nevada to the
    Top of Gondola: Comet, then the Von Schmidt traverse"), against the
    auto-match, which had given the hairpin into Von Schmidt's label to the
    name ending at its foot. Hover check 265/266 (the miss: Silver Spur's
    overlay along the stretch of Von Schmidt's label it shares) and 9/9.
- **Several panels:** a resort drawn on more than one map keeps one
  `trails.ts` and, per panel, `panels/<panel>/` with its own
  `linePolylines`, `trailProposals`, `trailReviews` and `trailPaths`; the map
  is `public/maps/<resort>-<panel>.jpg`. `trails:apply`, `hover_check.cjs`
  and the other `resortPaths()` scripts take `--panel <id>`. Make the areas
  (`peaks`) the panels, with the same ids, and give each trail its panel as
  its area: the trail list groups by area, and picking a trail that isn't
  drawn on the open panel opens its area's panel (or any panel that draws
  it). A run drawn at the edge of another panel (Vail's Back Bowls roads
  along Blue Sky's bottom edge) gets an overlay on both.
- Otherwise use the extracted PNG. Killington's repo JPG was a resampled,
  4:2:0 chroma-subsampled copy (PSNR 20.6 dB vs. the PDF raster), which blurs
  2–4 px colored lines and small text.

### 2. Line detection

`scripts/lib/lineDetector.mjs` finds green/blue/black trail lines with
hysteresis color classification, removes sign boxes, lift outlines, text and
markers, links gaps along each line's direction, and skeletonizes to 1 px
centerlines. On Killington it scores 98.6% precision / 95.8% recall against
283 hand-labeled points (`npm run lines:eval`).

For a new map:
1. Write down the **legend** by looking at the printed legend and zoomed
   crops: which colors are trails, lifts, boundaries, highlight bands, park
   features. Three earlier attempts failed by assuming colors (they treated
   pink highlight bands and yellow boundary dots as difficulties).
2. Label ~150–300 points (on-line positives per class plus hard negatives:
   text, lifts, boundary, forest, buildings) and tune thresholds only against
   those points (`evaluateLines.mjs --why` names the stage that dropped each
   miss). Check the whole-map overlay (`npm run lines:overlay`) too.
3. `node scripts/tracePolylines.mjs` → numbered pieces in
   `linePolylines.json`. Pieces break at junctions and markers; that's fine —
   naming happens per piece and a trail is a set of pieces.

Detector recall doesn't need to be perfect: reviewers can draw the lines it
misses (Killington's reviewer hand-drew ~45 stretches).

### 3. Name the pieces (parallel AI readers)

```bash
python3 tools/trailmap/render_tiles.py --image map.png \
  --polylines src/data/resorts/killington/linePolylines.json --out work/tiles
```

Then run the readers as a Claude Code workflow (the user must opt in to
multi-agent runs — say "use a workflow"). The workflow is saved in the repo:

- `.claude/workflows/trailmap-readers.js` (workflow name `trailmap-readers`)
  runs one reader per group of neighbouring tiles; each reader reads
  `prompts/0-new-map.md` itself and fills in the values the workflow passes
  (resort, tile paths, zoom, legend, areas, output file). Group tiles by
  column so readers can follow lines across tile edges. Example args:
  `tools/trailmap/runs/stowe-readers.json` (Stowe: 25 tiles in 6 groups).
- `.claude/workflows/trailmap-trace.js` (`trailmap-trace`) runs the trace
  pass (step 3b), ~5 trails per reader; example args
  `tools/trailmap/runs/stowe-trace.json`.

Write the legend for each map from its printed key and a few zoomed crops
before running (the args carry it). Each reader writes `result_<n>.json`
naming every piece it sees (or LIFT / NOT_A_TRAIL / UNKNOWN / SPLIT) and
listing every printed label. Killington used the older
`prompts/1-name-lines.md` (roster already known); a new map uses
`0-new-map.md`.

```bash
python3 tools/trailmap/aggregate_readings.py --tiles work/tiles \
  --readings 'work/tiles/result_*.json' --roster src/data/resorts/killington/trails.ts \
  --polylines src/data/resorts/killington/linePolylines.json \
  --proposals src/data/resorts/killington/trailProposals.json --review-data work/review/data.json
```

Killington: 6 readers, 37 tiles, ~25 min, ~780k sub-agent tokens. Result: 82
trails at high confidence, 57 pieces flagged as not trails (building
outlines, icons, text), 37 names printed on the map but missing from the app's
list, and 92% of the real trail-line length named (automatic matching had
reached 53% coverage and ~40% correct names).

Spot-check a few proposals with `render_crops.py` before the human review.

**A resort with no trail list yet (Stowe):** use `prompts/0-new-map.md`,
which also records every printed label's symbol, glade icon and area, then
`seed_roster.py` builds `trails.ts` from those labels before
`aggregate_readings.py` runs. Pieces a reader reports as "SPLIT: A / B" are
cut with `split_pieces.py` (the names go in as a "certain" reading). Stowe:
6 readers over 25 tiles, ~15 min, ~620k tokens → 125 trails, 101 with a
unanimous line, 18 printed with no line (11 glades) pre-filled as label
markers for the reviewer to confirm. Watch for trail names that start with a
reader verdict word (LIFTLINE was once dropped as a LIFT).
Okemo: 6 readers over 33 tiles (one per column), ~1.5M tokens, ~69 min
because the runner ran two at a time → 128 trails, 108 with a unanimous
line, 9 printed with no line. Unlike Stowe, Okemo prints a symbol with every
glade (in a box with the tree icon), so read the key before assuming the
glade default; terrain parks print only an orange pill, so they get the
default (blue).
Sugarbush: 5 readers over 26 tiles, ~1.2M tokens, ~53 min → 138 trails:
110 on their lines, 27 glades ("wooded areas": tree icon, no line, no
symbol, so the black default; Sugarbush itself counts them as their own
category). The readers also caught what the extraction missed: Snowball is
drawn as a filled outline (`extract_pdf_vectors.py --outlined`), and three
pieces run past the next trail's symbol (SPLIT, cut with `split_pieces.py`).

**Check the symbols by a second method.** On a vector map,
`pdf_symbols.py --check labels.json --trails trails.ts` pulls every circle,
square and diamond out of the PDF's fills and lists the trails whose
difficulty has no matching symbol by its label (Okemo: 120/127; the other 7
print no symbol, or draw the circle differently). Then look at every
diamond trail on a zoomed crop: single vs double diamond is the easy
misread (Okemo: 29 single and 9 double, all as read). Sugarbush draws its
diamonds inside the outlined label glyphs, so `pdf_symbols.py` finds its
squares and circles but no diamonds: there the crop check is the only
second method (30 single and 8 double, all as read).

### 3b. Accept the easy ones, trace the hard ones (before the review)

What the Stowe review showed: all 101 unanimous proposals and all 11 glades
were accepted unchanged, while the reviewer's time went to (a) short trails
printed with a name but no line and (b) traverses and trails that share
pieces (Crossover, Jake's Ride), which they redrew by hand. So:

- **Auto-accept** (`aggregate_readings.py --labels labels.json`): unanimous
  proposals and glades printed with no line (marker at the label) are
  marked `auto`; the review page leaves them out of "Needs action" (they
  show under All as "auto") and `trails:apply` uses them as proposed.
- **Readers' own confidence counts.** Readers work by column, so most
  pieces are seen by one reader and are "unanimous" by default.
  `aggregate_readings.py` caps a trail at the best confidence its readers
  gave the winning name, so a lone "medium" or "low" goes to the trace pass
  and the reviewer instead of being auto-accepted (Okemo: 9 trails).
- **Trace pass** (`prompts/4-trace.md`, ~5 trails per reader) for trails
  with no line and for medium/low or split proposals; load the result with
  `traces_to_reviews.py` so the reviewer confirms instead of drawing.
  Stowe, blind vs. the reviewer's drawings (`score_traces.py`): 8/13 within
  25 px, ~3 min and ~200k tokens for 3 readers. It gets fall-line cuts and
  multi-piece runs right; the misses were two traverses traced down the
  fall line (prompt since fixed), one trail stopped early and one boundary
  between two names read differently.
  Re-run on the 5 misses after the prompt fix: the two traverses now run
  across the slope (Christiana recall 50% → 100%, West Smugglers 71% →
  93%), Stowe Derby goes further (48% → 71%); traces still run somewhat
  longer than the reviewer drew, and the Crossover / Jake's Ride boundary
  is read the same way (a naming call), so they stay pre-fills.
  Okemo (before its review): 5 readers, 22 trails (9 printed with no line,
  10 medium/low, both halves of a split, 2 boundary neighbours), ~980k
  tokens, ~42 min two at a time. One trail used only part of a piece
  (Turkey Shoot on 210): cut it with `split_pieces.py` before
  `traces_to_reviews.py`, which stores whole pieces. Three names turned out
  to be areas with no run (two carpet learning areas and a small park);
  they became label markers (`no-line` + `labelAt`) rather than invented
  lines.
  Okemo's review: only the 23 pre-filled trails needed action (the other
  105 were auto-accepted and nobody reopened them). 20 were saved as
  pre-filled; the reviewer extended Turkey Shoot up the curve it shares
  with Challenger, moved the Mountain Road / Lower Mountain Road boundary
  and redrew Fast Track's stretch along its label. Hover check 376/376.
- **Unnamed connectors:** short pieces the map prints no name for are
  checked on a crop and recorded in `linePolylines.json` `_unnamed`
  ({id: why}); the aggregator hides them on the review page instead of
  inventing names (Stowe: 5).
- The label's text direction does **not** give a trail's direction (Stowe:
  40-90° off the reviewer's lines); don't use it.
- `trails:apply` snaps a hand-drawn stretch onto a line piece no other
  trail uses when >= 90% of the piece lies within 15 px of the stroke, so
  hand-traced traverses end up on the exact line.

### 3c. Naming the pieces yourself (no readers)

From Whiteface on, the PDF gave the names as text or glyphs, and Claude named
every piece itself; Vail did the same with raster-detected pieces. On a PDF
map, `tools/trailmap/pdf_resort.py <id> build` does the auto-match and writes
the review-tile inputs (`names.json`: `id:name`, `~` a stretch, `?`
undecided); `pdf_resort.py <id> add "crop" 123=NAME` records a decision. The
loop:

1. **Auto-match** names to pieces from where the map prints them, preferring
   pieces of the symbol's colour:
   - a name printed along a piece (most of its glyph centres within ~7 pt of
     it) names that piece (Whiteface, Keystone);
   - a piece ending at a name's own symbol, or at the far end of its text and
     pointing along it, continues that trail (Winter Park, Breckenridge: their
     lines run into the names);
   - Vail draws the symbol on the line with the name beside it: a piece
     through the symbol, starting at it, or whose top end lies the way the
     text runs takes the name (`resorts/vail/build.py`);
   - then names spread along unlabelled continuations (an end that meets
     exactly one other piece of the same colour).
2. **Review tiles:** `grid_crop.py --pieces … --names … --symbols … --grid 0
   --zoom 1.5` in ~850x650 px boxes over the whole map, each piece tagged
   `id:name` and each undecided one `id?`. Settle doubtful pieces on closer
   crops: plain, and with the grid to read coordinates off.
3. **Record each decision as a point** on the piece, with a comment naming the
   crop that settled it (Vail: `add.py` writes `decisions.py`). Record what
   isn't a trail too, and why: icons, creek edges, a bus route, connectors the
   map prints no name for.
4. **One line, two trails:** cut the piece where the second trail starts
   (Vail `CUTS`; for a PDF map's pieces, `split_pieces.py`).
5. **Missing stretches:** read a few rough points off a grid crop and
   `snap_trace.py` puts them on the painted line; add the result as a traced
   piece.
6. Rebuild, then run the crop audit (step 4).

Vail: 550 pieces, about a third matched automatically, the rest settled on
about 30 review tiles and many closer crops, plus 67 traced stretches.

### 4. Human review

Sugarbush, Jay Peak, Whiteface, Winter Park, Breckenridge, Copper Mountain,
Keystone and Vail skipped this step at the owner's call: the readers' labelling
had held up on three maps, the next five needed no readers at all, and Claude
named Vail's raster pieces itself on zoomed tiles. In its place Claude checks
every overlay itself:

1. `region_audit.py` over each map (e.g. `--grid 5x3 --zoom 1.3`), with every
   overlay drawn in its own colour and tagged with its name. Look for lines
   with no overlay, overlays on the wrong line, and gaps.
2. `symbol_audit.py --mode off` and `--mode ends` with the named symbols. It
   lists every symbol that lies off its trail's overlay or at one of its ends.
   Each is either fine (the run starts or ends at its symbol) or a missing
   stub or stretch. On Vail it found 33 gaps after the region audit had
   passed: a short stub doesn't show at 1.3x.
3. `symbol_audit.py --mode diamonds`: every diamond on one sheet with its name
   and type, for the single-vs-double check.
4. Anything unclear on `grid_crop.py`; fix it with a decision or a traced
   stretch, rebuild, and look again.
5. The hover check, per panel on a multi-panel map (step 7). After an app
   change, also drive the UI in a browser (desktop and phone sizes).

The review page is still there for maps where the readers disagree, or when the
owner wants a person to confirm.

Publish `tools/trailmap/review/` (the page, `data.json`, and the map image as
`map.jpg`) as a Claude artifact with the `db` capability. The reviewer, per
trail: confirm the orange line; tap pieces to add/remove; **draw** stretches
the detector missed; or mark **No line** (glade: label only) or **Not on this
map**. Saving jumps to the next trail that needs action (undecided, skipped
or flagged). Decisions are stored in the page's `reviews` collection.

Export and apply:

```bash
# Claude: ArtifactData list reviews --out_dir work/reviews_export
npm run reviews:import -- work/reviews_export/reviews
npm run trails:apply
```

`trails:apply` also joins each trail's pieces into continuous lines: ends
closer than 40 source px always join; ends up to 250 px apart join when both
pieces point at each other (the gap an inline label leaves); an end that stops
just short of another piece, pointing at it (within 60°: not sideways onto a line running beside it), is extended to touch it; remaining gaps up to
400 px are bridged along the map's detected line network (a route no longer
than 1.6× the gap + 80 px), or straight if under 180 px. On Killington this
took 382 pieces to 142 lines, with only 2 trails left in separate parts.

`importReviews` keeps the newer decision per trail and maps the page's
`new-<slug>` ids to clean trail ids (`new-racer-s-edge` → `racers-edge`).

Killington: all 166 trails reviewed in ~35 min: 110 confirmed lines, 22 glades
with no line, 13 not on the map, 21 skipped (mostly upper/lower variants and
liftlines).

### 5. Symbols, unplaced trails, and a second search

Re-run readers over the same tiles with `prompts/2-symbols-and-missing.md`:

- **Job A (symbols):** the circle / square / diamond / double diamond printed
  at each trail. This is the source of truth for difficulty — line color
  can't tell black from double-black, and the app's trail list was wrong for
  34 trails (e.g. Breakaway, Catwalk, Caper, Chute). **Check every proposed
  change on a zoomed crop of the symbol** before applying; all 34 held up.
  Leave trails whose symbol changes along the run (two labels, two symbols)
  at their listed difficulty.
- **Job B (unplaced trails):** where each trail without an overlay is printed,
  if anywhere. It found 2 glades (label, no line) and 2 "upper" sections.

Before removing anything from the list, run the **independent whole-map
search** (`prompts/3-whole-map-search.md`): 4 readers, ~8 names each, each
scanning the entire map. It confirmed 29 of 32 removals and recovered 3
trails printed as a second, unprefixed label — HOME STRETCH, SKYEBURST and
WILDFIRE each appear twice, each section starting at its own difficulty
symbol, which is how the map marks Lower Home Stretch, Upper Skyeburst and
Lower Wildfire. It also reported names the list spelled differently from the
map (Snowshed Crossover vs "Crossover"); rename to the printed name, keep ids.

Data cleanup rules we applied:
- **Duplicates** (same name twice in the list): check both on a crop; if they
  trace the same line, merge geometry into one and delete the other.
- **Upper/Lower splits:** a map section that starts at its own difficulty
  symbol under the same (or unprefixed) name is its own trail. Split the
  pieces at the junction where the second label's symbol sits.
- **Trail area/peak** for new trails: take the area of the nearest original
  trails (majority of 3). Region boxes and nearest-summit both misplaced
  mid-slope glades.
- **Glades:** "no line" + `labelAt` (the label position) → clickable marker.

Everything Claude changes gets `"by": "claude"` in `trailReviews.json` and is
flagged for recheck:

```bash
python3 tools/trailmap/refresh_review_data.py --review-data work/review/data.json \
  --roster src/data/resorts/killington/trails.ts --reviews src/data/resorts/killington/trailReviews.json \
  --page-ids work/page_ids.txt --recheck recheck.json
```

### 6. Human recheck

The reviewer opens the page; "Needs action" lists only the flagged trails,
each pre-filled with Claude's geometry. Killington: 8 trails, then 6.

### 7. Apply and verify

**Register the resort in the app.**
1. Put its map at `public/maps/<id>.jpg`. Save it as a JPEG at quality ~82;
   a 4,000–5,000 px wide map comes to 2–4 MB. Overlays are stored in percent,
   so a panel drawn at a large scale can be saved smaller (Vail's
   `images.py`).
2. List it in `src/resorts.ts`: `oneMap('<id>', '<Name>', ...)` with
   loaders for its `trails.ts` and `trailPaths.json`, or (several panels) a
   `load` that returns one `maps` entry per panel. Each resort's data becomes
   its own chunk, loaded when the resort is opened.
3. Nothing to add for offline use: the service worker's precache list and
   version are filled in by `vite build`, and maps are cached as they're
   viewed.

Then:

```bash
npm run reviews:import -- <export dir> && npm run trails:apply -- --resort <id>
npx tsc -b && npx eslint . && npm run build
(npx vite preview --port 4199 --strictPort > work/preview.log 2>&1 &)   # its own subshell
PLAYWRIGHT_PATH=$(npm root -g)/playwright node tools/trailmap/hover_check.cjs http://localhost:4199/ --resort <id> [--panel <p>]
ps aux | grep "vite preview" | grep -v grep | awk '{print $2}' | xargs -r kill   # stop it by PID
```

The hover check hovers 3 points along every line and each glade marker in the
real app. The map names the NEAREST trail to the pointer (the same test a tap
uses), not whichever trail is drawn on top: that took Killington from
344/361 to 359/361 and Stowe from 343/353 to 351/353. The remaining misses
are stretches two trails genuinely share (Great Eastern / Home Stretch,
Jake's Ride / Crossover), where either name is right. It checks rendering
against the reviewed geometry; it is not evidence the geometry is right (the
review or the crop audit is). It samples only three points on each trail's
longest segment, so it can't catch a missing stub or a wrong short piece.

Every resort after a change to shared app code (the map, `src/resorts.ts`):
run it for all of them; each should match its previous score.

## What we tried, and what it taught us

Seven attempts over six months, most on separate unmerged branches (see the
README's "Prior attempts"):

| attempt | method | outcome |
|---|---|---|
| Mar 2026 | Sweepline tracing + AI-read label positions + Hungarian matching | Claimed 114/115 matched, but keyed on the wrong colors (pink/yellow) |
| Mar–Apr 2026 | Python OpenCV: HSV + heuristic scoring, SAM 2, easyocr | 90%+ on self-defined pixel metrics; naming never ran (needed an API key); OCR 17% |
| Jun 2026 | Snow-surface detector (v1) | F1 92.7% for "is this snow" — the wrong question; trails are lines |
| Jul 2026 | Line detector (v2) + rotation-aware tesseract OCR + nearest-label assignment | 97% F1 on line pixels, 125 labels read, but only **~40% of trails on the right line** when audited |
| Sep 2026 | Tile reading by parallel AI readers + human review page | 110/166 trails confirmed in the first review; 92% of line length named |
| Sep 2026 | Symbol reading + unplaced-trail search + whole-map search | 34 difficulty fixes, 36 map trails added, 29 stale entries removed, 3 recovered |
| Sep 2026 | Import, splits, printed names, hover check | 135 trails, all clickable; 342/361 hover points correct |

Lessons:
- **Measure the actual goal.** Every early attempt optimized a proxy it
  defined itself (pixel precision/recall, coverage, label count) and hit 90%+
  while the user-visible result — the right name on the right line — sat near
  40%. Audit names on zoomed crops, per trail, with a random sample.
- **Avoid circular checks.** An early "26/30 hover" test hovered on whichever
  line had been assigned, so a wrong line still passed.
- **Naming is a reading task, not a CV task.** Labels sit between parallel
  lines, trails change color, glades have no line, names repeat on sections.
  Numbered-tile reading by a vision model handled these; heuristics didn't.
- **Keep a human in the loop, but only where it pays.** Proposals made the
  review ~15 s per trail; the reviewer's decisions outrank every automatic
  source and double as ground truth.
- **Use two independent methods before deleting data** (area-split readers,
  then per-name whole-map scans).
- **The printed symbol is the difficulty.** Line color can't separate black
  from double-black; the app's list was wrong for 34 trails.
- **Write down what you learn in `CLAUDE.md` and merge to `main`.** Earlier
  sessions each restarted from scratch because nothing was merged.

## Gotchas

- Review-page ids are permanent: map-only trails keep `new-<slug>` ids on the
  page; `importReviews` maps them.
- The draw tool records one stroke per trail; `applyTrailProposals` splits a
  stroke where consecutive points jump > 400 source px (a new stretch).
- A tap that opens a sheet on a phone is followed by a synthetic click that
  can hit a button under the finger; the app's sheet ignores input for 350 ms.
- Judge distances on crops at ≥ 1× zoom; judgments on shrunken images were
  wrong often enough to mislead.
- In this sandbox `pkill -f <pattern>` can kill the shell running it when the
  pattern also appears later in the same command line. Stop a server by PID.
- **Raster piece ids are not stable.** Re-tuning `raster_lines.py` renumbers
  every piece, and re-tuning `raster_symbols.py` renumbers the symbols. Key
  every decision by a point on the map (Vail's `decisions.py`, `names.py`);
  `aggregate_readings.py`'s inputs can be rebuilt from those. A PDF map's
  vector extraction is deterministic, so its ids are stable.
- **Symbol detection over-counts.** A single diamond touching the end of its
  own line came out as a double (twice on Vail). Bus-stop dots, a sign's
  border and an info box's icon came out as symbols. Check every symbol on a
  contact sheet before trusting the difficulties.
- **Vail-style labels:** the symbol sits on the line and the name beside it,
  sometimes printed uphill. The line can resume past the name (Northwoods,
  Prima, S. Rim's hook) or the run can simply start at its symbol (N. Rim,
  Gandy Dancer): check each on a crop. A symbol printed on a run's line with
  no name marks a change of rating and counts toward that run's difficulty.
- **Dashes through slow zones.** Pale hatching between a road's dashes breaks
  the "four marks in a row" linking; trace those stretches.
- **`trails:apply` can bridge the wrong way.** It joins a trail's parts when
  their ends point at each other, and on a loop or switchback that can draw a
  straight bridge across the slope (Vail Village Catwalk). Trace the real
  connecting stretch and the bridge goes away.
- **Regenerate without losing people's work.** Drop only the `"by": "claude"`
  reviews before re-adding Claude's. Deleting `trailReviews.json` (as the
  early scratch scripts did) would lose a person's decisions. Vail's
  `regen.sh` does it right and keeps unchanged timestamps, so a re-run with
  no changes leaves the files identical.
- **Several panels:** a trail's marker goes on the panel where its name is
  printed, so `aggregate_readings.py` and `traces_to_reviews.py` get that
  panel's labels only, while `seed_roster.py` gets all of them. A run drawn
  on two panels gets an overlay on each but one area, its home panel (Vail's
  `SHARED`): the list groups it there.

## Scaling to many maps

In rough order of payoff:

1. **One data folder per resort** — done: `src/data/resorts/<id>/`
   (`trails.ts`, `linePolylines.json`, `trailProposals.json`,
   `trailReviews.json`, `trailPaths.json`), map at `public/maps/<id>.jpg`,
   registered in `src/resorts.ts`. `tracePolylines`, `trails:apply`,
   `reviews:import` and `hover_check.cjs` take `--resort <id>` (and
   `--panel <id>` for a map in several panels, kept in `panels/<panel>/`);
   the image size comes from the map file. Still to do: a `legend.json` per
   map.
2. **One label-to-piece matcher for PDF maps** — done from Hunter Mountain
   on: `tools/trailmap/pdf_resort.py` takes `pdf_labels.py`'s or
   `pdf_glyphs.py`'s labels (one format) and a resort folder (`resort.py`,
   `decisions.py`) and runs the whole pipeline. Whiteface, Winter Park,
   Breckenridge, Copper Mountain and Keystone each had a scratch copy of the
   same rules and could be moved onto it.
3. **A per-map legend file** (trail colors, lift color, boundary, highlight
   bands, symbols, text styles) feeding both the detector's color gates and
   the reader prompts.
4. **Run the readers from a script** (`ANTHROPIC_API_KEY` + the prompt
   templates, images attached) instead of an interactive Claude session, so a
   new map is one command. Keep the vote aggregation as is.
5. **Start the trail list from the map, not from memory** — done since
   Stowe: `seed_roster.py` builds `trails.ts` from the printed names and
   symbols (most of Killington's list corrections came from a list written
   before looking at the map).
6. **Auto-accept only unanimous, high-confidence proposals** — done since
   Stowe (`aggregate_readings.py`, step 3b). Still open: also require the
   pieces' colour to match the printed symbol.
7. **Skip OCR** for new maps — done: the readers, and on PDF maps the text
   and glyphs themselves, superseded it.
8. **Reuse the review page** as a template artifact per resort, and ask the
   resort for vector sources — a layered PDF removes steps 2–3 entirely.
