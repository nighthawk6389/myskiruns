# Trail map playbook: from a resort's map to clickable, named trails

How the app's thirty-eight resorts got their overlays, written so the next resort (or the next season of one of
these) can be done the same way, faster. It is for whoever does that work: a person, or Claude in a session like
the ones that built these.

- **Part 1, [Doing a resort](#part-1-doing-a-resort):** the goal, the process step by step, how to pick a route,
  [a recipe for each type of map](#recipes-map-type-by-map-type) (with `resort.py`'s settings by symptom), the
  ground rules, the conventions for the judgment calls, the sources of truth, a new season, fixing one trail,
  pitfalls.
- **Part 2, [Tools](#part-2-tools):** every script, by stage.
- **Part 3, [Resort by resort](#part-3-resort-by-resort):** each resort's source, route, the commands that rebuild
  it, its files, the quirks of its map and the decisions taken, and how it was checked.
- **Part 4, [Methods in detail](#part-4-methods-in-detail):** getting sources here, raster line detection, the AI
  readers, the trace pass, naming pieces yourself, the human review page, symbols, applying and verifying.
- **Part 5, [What we tried](#part-5-what-we-tried-and-what-it-taught-us):** the failed approaches, the lessons, and
  what would scale this further.

# Part 1. Doing a resort

## What done means

For every trail in the resort's `trails.ts`:
- its overlay lies on that trail's own drawn line along its full length, from its name (or its symbol) to where its
  line ends, and nowhere else; or, if the map draws no line for it (a bowl, a glade, a chute, a park, a learning
  area), it is a marker at its printed name;
- tapping or hovering anywhere on it shows that trail's name;
- its rating is the symbol printed by its name;
- and the list holds exactly the runs this season's map names, spelled as the resort spells them.

And for the resort: its `tools/trailmap/resorts/<id>/regen.sh` rebuilds every committed file of it byte for byte
from its sources and recorded decisions, and every decision says which crop settled it.

Pixel-level scores are not evidence of any of this, and neither is a test that hovers on the overlay already
assigned (it passes on a wrong line). The evidence is zoomed crops of the map, trail by trail, or a person's review.

## The process, step by step

| # | step | how | about |
|---|---|---|---|
| 1 | **Find the source** | the resort's trail-map page: `node tools/trailmap/find_source.cjs links <page>` lists the PDFs and CDN images it loads; download with curl, or `fetch_pdf.cjs` where the site refuses curl. No PDF, or a hidden one: `python3 tools/trailmap/skimap.py search <name>` / `probe <area>` (skimap.org also keeps past editions). Note the URL and the file's SHA-256 | 15 min |
| 2 | **See what it gives you** | `pdf_inspect.py` (images and their resolution, strokes by colour and width, fills, text by font), `pdf_classes.py` (each stroke class drawn alone: trails, lifts, boundary, hatching), and the printed legend; then **pick a route** (below) and the resort folder to start from | 15 min |
| 3 | **Get the truth sources** | the resort's trail report (`tools/trailmap/reports/README.md`; keep it as `report.json` and run `reports/compare.py` once the list exists), its GIS if it publishes one, OpenStreetMap's runs (`osm_check.py fetch`) | 15-30 min |
| 4 | **Set up the folder** | `tools/trailmap/resorts/<id>/`, copied from the closest resort (Part 3): `regen.sh` (download with SHA check, extraction, matching, `trails:apply`), the map's reading (`resort.py` for `pdf_resort.py`), `decisions.py`, `header.txt` | 15 min |
| 5 | **Extract** | the map image, the line pieces (`extract_pdf_vectors.py`, or the resort's `prepare.py`), the names (`pdf_labels.py` for text, `pdf_glyphs.py` for outlined glyphs), the symbols (`pdf_symbols.py`, `pdf_glyphs.py`). Look at the pieces over the map on crops before trusting them | 30-90 min |
| 6 | **Name the pieces** | the automatic match (`pdf_resort.py <id> build`: a name names the line it is printed along, or the one ending at its text or symbol), then every undecided piece settled on zoomed crops (`pieces.py info / pair / seq`, `grid_crop.py`, `piece_sheet.py`, `osm_check.py check`), each recorded with the crop that settled it (`pdf_resort.py <id> add`). Names you can't extract: the AI readers (Part 4) | 1-4 h |
| 7 | **The trail list** | from the printed names and symbols (`pdf_resort.py`, or `seed_roster.py`): spelled as the trail report spells them, rated by the printed symbol, grouped by the report's areas | in step 6 |
| 8 | **Build** | `regen.sh`: proposals, Claude's reviews, `npm run trails:apply` | 1 min |
| 9 | **Audit every overlay** | `overlay_audit.py` (one cell per trail: look at every one), `symbol_audit.py --mode off / ends / diamonds`, `pdf_overlaps.py`, ratings against the report; a matted image with `matte_check.py`; fix with a decision, a cut or a traced stretch, rebuild, look again | 1-3 h |
| 10 | **Register it** | the map as a JPEG (quality 82, 2-4 MB) in `public/maps/`, an entry in `src/resorts.ts` (state, other places it's found by, panels), an ad group in `marketing/google-ads/build.mjs` (`npm run ads:build`), the docs: the README's table, its section in Part 3, CLAUDE.md's list of rebuilt resorts | 20 min |
| 11 | **Verify** | `regen.sh` from an empty work folder, then `git status` shows nothing; `regen_all.sh` if a shared tool changed (every other resort unchanged); `hover_all.sh`; `node tools/app_check.cjs <url> --resort <id>`; `npx tsc -b && npx eslint . && npm test`; after an app change also `app_flows.cjs` and `offline_check.cjs` | 20 min |
| 12 | **Commit and push** | one commit per resort, its message saying the source, the method, the decisions and the checks (the recent resorts' commits are the model) | |

So far a single PDF map of strokes and text took one to two hours; a big map, several panels or glyph names four
to eight; a map whose names can't be extracted two to four hours of readers plus a person's review.

## Pick a route by what the source gives you

Look at the PDF first (`pdf_inspect.py`, `pdf_classes.py`): whether the trail lines are vector strokes, filled
outlines or only paint, and whether the names are text, outlined glyphs or only paint, decides most of the work.

| the source gives you | route | done this way | start from |
|---|---|---|---|
| trail lines as vector strokes, names as text | `extract_pdf_vectors.py` for the pieces, `pdf_labels.py` for the names; `pdf_resort.py` matches each name to the line it is printed along or at the end of; settle the rest on crops | Whiteface, Winter Park (text with no Unicode map), Breckenridge, Hunter Mountain, Big Sky (three PDFs, three panels), Snowmass (two panels; rated by the colour of each name's pill, the expert runs' cased lines filled outlines, `pdf_outline_lines.py`), Aspen Mountain (the same kind, three panels), Buttermilk (one panel) and Snowbasin (symbols on the lines; four lines drawn as filled outlines, read along their middle) | Hunter, Big Sky; Snowmass for a map rated by colour |
| vector strokes, names as outlined glyphs | `extract_pdf_vectors.py`; `pdf_glyphs.py` decodes the names (each glyph shape read once on a contact sheet) | Keystone, Sunday River, Sugarloaf, Smugglers' Notch, Whistler Blackcomb (three panels), Park City, Palisades Tahoe (three PDFs, three panels), Alta (rounded symbols, `pdf_symbols.py --rounded --max-square`), Arapahoe Basin (one page of two paintings, two panels; most runs a name with no line: the stretch along it, `LABEL_LINE`) | Sunday River, Park City; Alta or Arapahoe Basin for rounded symbols |
| lines as filled outlines, names as outlined glyphs | rasterise the outlines and thin them to centre lines (Copper Mountain), or read each outline's centre line from its path (`pdf_outline_lines.py`, Heavenly's method); `pdf_glyphs.py` | Copper Mountain, Heavenly (an older export of the current image's artwork), Mt. Bachelor, Northstar (white names haloed in the line's colour: the halo is the colour, and is dropped from the lines; one united outline for the runs that meet, cut at each junction) | Mt. Bachelor; Northstar for united outlines |
| vector strokes, names you can't extract | numbered tiles named by parallel AI readers (Part 4) | Stowe, Okemo, Sugarbush | Okemo, Sugarbush |
| a painting with no lines, names as text | every run traced along its painted cut by trace readers (Part 4) | Jay Peak | Jay Peak |
| only raster images, but an interactive map whose SVG draws the same artwork (Alterra's resorts-interactive.com) | `vicomap.py parse --detail`: its lines, letters and symbols grouped by trail; registered on the image, each line routed onto the image's own line, named by its group (`GROUPED`); the print's redrawn spots traced (`trace_ink.py`) | Steamboat | Steamboat |
| a PDF with names as text and symbols as fills over a painting, but no trail lines drawn; an interactive map of the same painting | `vicomap.py parse`: its lines, registered on the painting and kept as they are (nothing printed to route them onto), named by their group (`GROUPED`); `pdf_labels.py` names spelled as the groups; symbols from the fills by colour | Mammoth (two panels, two interactive maps) | Mammoth |
| only raster images | `raster_lines.py` + `raster_symbols.py` (or `lineDetector.mjs`), pieces named on review tiles or by readers | Vail (three panels), Killington | Vail |
| only images, runs painted as slopes with no line (names along them), and an interactive map whose SVG groups each run's letters and symbol | the groups' letters and symbols registered on the print (`register_pages.py --ref`), what they lack read on crops (`names.py`); each run's overlay the stretch along its printed name (`LABEL_LINE`), the few drawn lines routed on the print | Schweitzer (two panels) | Schweitzer; Heavenly for a map whose runs have no line |
| only images, one print drawing each run's line and the others painting runs with no line, and an interactive map per panel whose groups hold each run's symbols and an older line (no letters) | each SVG registered on its print (`register_pages.py --ref`), the groups' symbols placed on it, a label at each; where the print draws lines, its own (colour masks, `raster_lines.py`'s clean and skeleton pieces; the black kept only near an interactive-map black line, the trees left out), named by the symbol at each run's top; where it draws none, the groups' lines as they are (Mammoth's), with the stretch along the printed name (`LABEL_LINE`) for a run in no group or with a stub of a line; what the groups lack read on crops (`names.py`) | Big Bear (three panels: Snow Summit drawn, Bear Mountain and Snow Valley painted) | Big Bear; Mammoth, Schweitzer |
| only small web JPEGs, lines blurred into the painting or in casings; or one good image whose lines are too thin and faint for detection | the map read on zoomed crops: each name, its symbol, its run's line as waypoints (`names.py`), each line routed along the painted one (`route_trace.py`), the pieces named by the reading (`GROUPED`) | Whitefish Mountain (three panels), Jackson Hole (one PNG, rated by the names' colours), Snowbird (one JPEG, its PDF the same image) | Whitefish; Jackson Hole for a map rated by colour |

- **A low-resolution painting under good vectors:** `matte_pdf_layer.py` mattes the PDF's vector layer over a
  sharper copy of the painting (Breckenridge, from Vail Resorts' image CDN), a sharper image of the whole map
  (Keystone), or a smooth upscale of the embedded painting (Copper Mountain, Sugarloaf, Smugglers' Notch; Park City
  with `--resample`). A sharper image of the whole map is flattened: it already shows the PDF's translucent layers
  (washes, Multiply bands, slow zones), so leave them to it (`--flattened`; Breckenridge's `matte.py` does the same).
- **This season's PDF has flattened lines or outlined names, an older one has them live:** skimap.org keeps past
  exports of the same artwork. Register the two pages (`register_pages.py`), check that every old name lands on the
  same name in this season's map and that this season prints no other, then take the strokes, text and symbols
  from the old export (Wildcat). Where the current map is only an image, the same works against the image: find
  every place it differs from the old page, leave out what it no longer prints and trace what it prints anew
  (Heavenly; Beaver Creek, whose site has only its CDN image, from skimap.org's 2023 export).
- **Ask for the layered file:** a resort's own Illustrator or PDF export with live layers removes most of the
  work (Killington's metadata shows a flattened Illustrator file).

## Recipes, map type by map type

The table above names the route; this is how to run it. Every recipe ends the same way (Part 1, steps 8-12:
build, audit every overlay, register, verify, commit), and every one starts with the same hour of triage.

### Triage: the first hour, whatever the map

1. **Get every source there is**, each into `work/<id>/` with its SHA-256 noted: the resort's PDF
   (`find_source.cjs links <trail-map page> 'pdf|map'`; `fetch_pdf.cjs` where the site refuses curl), the image the
   site itself shows (Vail Resorts' scene7: `?req=imageprops` gives its full size), and skimap.org's editions
   (`skimap.py search <name>`, `maps <area>`, `probe <area>`: the current one may be the same file, and an older
   one may have live layers the current one lacks).
2. **Read the legend first**, on a crop of the map: what colour is each rating, what are lifts, roads, catwalks,
   the boundary, closures, parks, glades, slow zones; what symbol goes with each rating; how a name sits on its
   line (in a gap of it, beside it, on a label box, in a key). Write it down: every later setting comes from it.
3. **Tally the PDF:** `pdf_inspect.py map.pdf --out work/<id>/inspect` (images with their resolution, strokes by
   colour and width, fills by colour, text spans by font), then `pdf_classes.py` on the colours the legend
   named, each class drawn alone. Find the legend's colours in the tally yourself: the trail strokes are often
   not the most common ones (Hunter's painting is 246,000 vector drawings; its 0.38 pt trail lines are buried
   among them).
4. **Recognise the type** from what the tally shows:

| the tally shows | the type | recipe |
|---|---|---|
| strokes in the legend's trail colours, at one or two widths, and text spans in a name font | strokes and text | A |
| those strokes, few or no text spans, thousands of small fills in the name colours | strokes and outlined glyphs | B |
| no trail-coloured strokes, but long thin fills in the trail colours (and glyph fills) | filled-outline lines | C |
| this season's PDF flattened or outlined, an older edition (skimap.org) with live layers of the same artwork | an older export registered | D, then A to C |
| trail strokes, but the names are paint (in the raster) or glyph reading fails | names you can't extract | E |
| names (text or glyphs) and symbols, no trail lines at all: runs are painted cuts | no drawn lines | F |
| one big image and nothing else (or no PDF: only a CDN image) | raster only | G |

   A map can mix types (Sunday River: glyph names plus a few text names; Sugarloaf: a raster inset in a vector
   map; Park City: a redrawn inset at another scale): run each part by its own recipe and join them in
   `prepare.py`.
5. **Choose the map image** before anything is numbered (the pieces are on its grid): the page rendered as it is
   if its painting's own resolution (`pdf_inspect.py`'s dpi / 72 = px per pt) is near the scale you render at; else `matte_pdf_layer.py` over a sharper copy (a CDN copy
   of the whole map is flattened: `--flattened`), or over a smooth upscale (`--resample`). Check a matte with
   `matte_check.py`.
6. **Get the trail report** (`tools/trailmap/reports/README.md`) into `tools/trailmap/resorts/<id>/report.json`;
   in October use a Common Crawl capture from the season.

### A. Strokes and text (start from Hunter Mountain; Big Sky for several PDFs)

1. `mkdir tools/trailmap/resorts/<id>` and copy Hunter's `regen.sh`, `resort.py`, `decisions.py` (empty its lists),
   `header.txt`. In `regen.sh`: the source URL and SHA-256, the clip (the painting, without logo bands and
   panels), the scale (map px per pt: 2 to 5, for a map 4,000-5,000 px wide), each trail colour and the stroke widths that are trails and not
   lifts or roads (`--min-width`/`--max-width`), `--exclude` boxes for the legend and panels printed on the map,
   `--min-length 0.8` (the default 4 pt drops lead-in stubs), `--append` passes for odd classes (a rating drawn in
   pure black, at another width, `--filled`, `--outlined`; dashed access routes left out with `--solid`).
2. Run `regen.sh` once and look at the pieces over the map before naming anything: `region_audit.py` or
   `grid_crop.py --pieces work/<id>/pieces.json`. Every drawn trail line should be pieces; nothing else should be.
3. Names: `pdf_labels.py map.pdf --out printed.json`; in `resort.py`, `is_name(label)` keeps the name font and
   size. Count the names against the legend's or the report's count. A font with no Unicode map reads as `{N}`:
   `--glyph N=char` (Winter Park).
4. Symbols: `pdf_symbols.py --circle <green> --square <blue> --diamond <black>` (`--rounded` for rounded corners,
   `--max-size` / `--max-diamond` / `--max-square` for this map's sizes); check them on `symbol_audit.py --mode diamonds`
   later.
5. `python3 tools/trailmap/pdf_resort.py <id> build`: the automatic match; `names.json` marks undecided pieces `?`.
   Settle each on a zoomed crop (`pieces.py info / pair`, `grid_crop.py --names work/<id>/names.json`, `pieces.py
   seq` for the drawing order, `osm_check.py check` for which run a line follows past a junction) and record it:
   `pdf_resort.py <id> add "what the crop showed" x,y=NAME` (a point on the piece, so it survives re-extraction),
   `x,y=-:"why"` for a line that is no trail. Cut one line carrying two runs with `CUTS`; draw a stretch the map
   draws but the extraction can't (`snap_trace.py`) with `TRACED`.
6. Tune `resort.py` by what the crops show (the table below), rebuild, repeat until nothing is `?`.
7. Then build, audit and register (Part 1, steps 8-12).

### B. Strokes and outlined glyphs (start from Sunday River or Park City; Keystone was the first)

As A, but the names come from `pdf_glyphs.py`, in four passes:
1. `collect map.pdf --out glyphs.json --color <name colour> ...` (every name colour, the zone colours too;
   `--exclude` the legend and bars). It keeps the last drawn glyph at each spot (recoloured names sit over last
   season's colour).
2. `sheet` draws each unread shape upright and numbered; read the sheet and record it: `read 12=a 13=e ...` into
   the resort's `letters.json`. Letters are keyed by shape, so another map in the same font reuses them (copy the
   file first). Read everything; shapes left unread should only be symbols, icons and arrows.
3. `labels --letters letters.json --square <blue> --diamond <black> --circle <green> --out labels.json`, with this
   font's quirks: `--space` for word gaps in a condensed font, `--turned nu` (or `WM`) and `--turned-hole 69` (or
   `dp`) for letters that are one shape turned over, `--rect-squares`, `--rounded`, `--even`, `--double-dist` (a double
   diamond with a gap), `--circle-curves`, `--reorder` (glyphs drawn out of turn), `--single <colour>` (one-digit
   keys).
4. Print every label next to its crop and correct what's wrong (`JOIN` for names on two lines, `DROP`, `RENAME`,
   `SPLIT` for two names read as one run); a few names may be real text: merge `pdf_labels.py`'s (Sunday River).
   Then A's steps 5-7.

Watch for: false double diamonds (a diamond drawn twice: Whistler Blackcomb), labels hidden under a later one or
outside their clip (last season's names left in the file: drop them), names on label boxes over their line
(`MATCH_ENDS = False`).

### C. Lines drawn as filled outlines (start from Mt. Bachelor; Copper Mountain skeletonises instead)

1. Lines: read each outline's centre line from its path (`pdf_outline_lines.py`, Heavenly's method: split the
   outline at its two farthest-apart points, pair each point of one side with the nearest of the other; chain a
   dashed line's outlines in drawing order; skip arrowheads, two curves and a notch; skeletonise an outline with
   more area than one line of its length, or one that reads wide but whose mean width is a line's: lines meeting
   at a junction drawn as one outline). Or rasterise each outline at 6 px/pt and thin it (Copper's `lines.py`: Zhang-Suen, no
   diagonal steps a 4-neighbour path already joins, spurs under 2.5 pt pruned). Names' letters are outlines too:
   leave out the fills `pdf_glyphs.py` reads as letters (`--glyphs`, `--letters`: an I or a hyphen in a run's
   colour is as thin as its line), and take a dark outline as a line only if it is long (`--dark-min`). Then
   check that every outline in a run's colour is covered by a piece, a letter or a symbol (Mt. Bachelor's
   `checks/missed.py`).
2. Names and symbols: B's `pdf_glyphs.py` passes. A cluster of names may be drawn grouped by shape (every G of
   the cluster, then every R...): `labels` then makes fragments of them (Mt. Bachelor's beginner area). Drop the
   fragments (`DROP`), place each name by hand where it is printed (`EXTRA`, in the report's spelling) and give
   it the symbol printed by it (`SYMBOL_OF`).
3. Then A's steps 5-7. Expect more pieces to settle on crops: centre lines fork at junctions.

### D. An older export registered on this season's map (Wildcat, Heavenly, Beaver Creek; Deer Valley the other way round)

When this season's PDF is flattened, outlined or missing but an older export of the same artwork has live layers:
1. `register_pages.py --pdf old.pdf --page 0 --image this_season.png [--box ...]`: the affine (SIFT, RANSAC); keep
   it in `resort.py` (`AFFINE`) so a rebuild doesn't depend on feature matching. Expect a median residual well
   under 1 px; more means another artwork.
2. Find every difference: warp the old page onto the image and compare region by region; check each old label
   and piece against the image's ink. Record what this season no longer prints (`GONE`, leave it out) and what it
   prints anew (`EXTRA`, and `TRACED` for a moved label's stretch).
3. Extract from the old export with recipe A, B or C, on the image's grid.

The newer edition may be the flattened one and the older the vectors (Deer Valley: the October PDF's strokes and
glyphs on the November image, `checks/editions.py` for every name, line and symbol that differs, the image's own
additions traced). Read the names on the newer edition: it corrects the older one's (Ham Bug, now Humbug).

### E. Names you can't extract (start from Okemo; Sugarbush)

Try B first: Okemo's outlined names went to readers only because `pdf_glyphs.py` didn't exist yet. When the
names really are paint:
1. The pieces as in A step 1 (or G for a raster).
2. `render_tiles.py --image map.png --polylines linePolylines.json --out work/<id>/tiles`, then the readers
   workflow (the user opts in: "use a workflow"), with `prompts/0-new-map.md` and an args file like
   `tools/trailmap/runs/stowe-readers.json` (the legend from triage step 2; tiles grouped by column).
3. `seed_roster.py` builds `trails.ts` from the readers' labels; `split_pieces.py` cuts their `SPLIT`s;
   `aggregate_readings.py --labels` writes the proposals and auto-accepts the unanimous ones; the trace pass
   (`prompts/4-trace.md`) takes the rest; `traces_to_reviews.py` (Part 4, "Naming pieces with parallel AI
   readers" and "Auto-accept the easy ones, trace the hard ones").
4. A person's review on the Trail Check page, or Claude's crop audit of every overlay.
5. Keep every reading in `tools/trailmap/resorts/<id>/readings/` and rebuild from them (Okemo's `regen.sh`):
   readers aren't deterministic, their saved answers are.

### F. No drawn lines (Jay Peak)

1. Names and symbols from the PDF (text: `pdf_labels.py`; glyphs: B), the trail list from them (`seed_roster.py`).
2. Every run traced along its painted cut by trace readers (`prompts/4-trace.md`, groups of 5-10 trails), each
   trace checked on a zoomed crop; a name with no cut is a marker at its label.
3. Save the traces in `readings/` and rebuild from them in the order they arrived (`TRACE_ORDER`).

### G. Raster only (start from Vail; Killington's detector for a flattened PDF raster)

1. The largest copy there is (Vail Resorts' scene7 at full size, `?fmt=png-alpha&wid=<width>&qlt=100`; a PDF's
   embedded raster with `extract_pdf_image.py`, not the website's JPEG).
2. Lines: `raster_lines.py` with a strict colour mask per rating from the legend, `--exclude` for panels and
   logos, `--k` scaling the mark sizes to the map's; symbols: `raster_symbols.py`. Look at the pieces on crops and
   tune against points you label, not a pixel score.
3. Name the pieces on review tiles (`grid_crop.py`) and record every decision as a point on the map (Vail's
   `decisions.py`, `add.py`), never a piece id: re-tuning the detector renumbers every piece. Stretches the
   detector breaks (dashes through slow zones, a name printed in the line) are traced with `snap_trace.py`.
4. **When the only copy is a small web JPEG** (Whitefish: 1600 px wide, no PDF, no interactive map), the detector
   finds part of the lines at best: the JPEG blurs thin lines into the painting, and lines drawn in a casing keep
   only a pixel of their colour. Read the map instead, on 2x zoomed grid crops of a 2x upscale: every name as
   printed with its label's middle, its symbol, and its run's line as a few waypoints (its start, its end, a point
   past each junction where it could take another line) in a `names.py`; route each line along the painted one
   between them (`route_trace.py`, the casings made cheap too), one named piece per line (`GROUPED`); a name with
   no line is a marker at its label. Audit every overlay on crops: a route that strays onto a neighbouring line
   needs a waypoint where it left.
5. **The same for a good image whose lines are too faint** (Jackson Hole: a lossless 3000 px PNG, but each run a
   1-2 px line that blends into the snow, its name solid in the same colour). The masks find the letters and only
   stretches of the lines (`raster_lines.py` traced a third of the runs), so read the map as in step 4, at 1x with
   3x zooms for the waypoints. Give each line its label's first and last letters as waypoints (the name sits in a gap
   of it): `prepare.py` crosses the label straight instead of routing through the letters, which zigzags. Snap
   each label onto its letters (the letter-sized parts of its colour's mask near the line through its points),
   keeping the reading where the snap would run past its ends or zigzag; a label kept as read is spread into
   letter-spaced points (`pdf_resort.py` pushes a stretch's ends out by most of the spacing between its label's
   points). Where a route still strays (a line beside another label, the trees' shadows), give the line's points
   as they are (`'as read'`).

### `resort.py` settings, by what the crops show

`pdf_resort.py` reads these from a resort's (or panel's) `resort.py`; Hunter's holds the basic ones.

| what the map does | setting | as at |
|---|---|---|
| names in a gap of their line, symbol at one end (the default) | `SYMBOL_REACH`, `END_REACH`, `ALONG` (pt) | Hunter |
| names on their line (label boxes over it), no gap | `MATCH_ENDS = False`, a larger `ALONG` | Sunday River, Wildcat |
| names printed beside their line as well as in gaps | `NO_STRETCH_BESIDE = True` | Park City, Big Sky |
| names between parallel lines | `ALONG_NEAREST = True` | Sunday River's inset |
| the name's own line is the one it runs along, symbol at one end | `ALONG_FIRST = True` | Big Sky, Heavenly |
| names of two or three characters (T2, OZ) | `ALONG_SHORT = True` | Sunday River |
| names on two or more lines | `JOIN`, `JOIN_GAP`, `TWO_LINE` | Hunter, Smugglers' Notch |
| two names read as one run of glyphs | `SPLIT` | Whistler Blackcomb |
| text in the name style that isn't a trail; a misprint | `DROP`; `RENAME` | most |
| a name printed some other way (a sign, another font) or only as a symbol | `EXTRA` | Big Sky (PB & J Way) |
| the same name for two runs | `RENAME_AT` (by where it is printed), `DISPLAY` | Whistler Blackcomb, Big Sky |
| the map prints capitals: the report's spellings | `NAMES` (from `report.json`), `DISPLAY` | Big Sky, Heavenly |
| names in their own case | `AS_PRINTED = True` | Smugglers' Notch |
| a symbol off its name's line ends, or out of reach | `SYMBOL_OF`; `SYMBOL_CENTRE = True` (above or below the middle) | Park City; Sunday River |
| a symbol beside its line, not on it | `SYMBOL_OFF_LINE` | Wildcat |
| each run's symbol on its line partway along it, the name beside: the piece under a named symbol takes the name | `SYMBOL_ON_LINE` | Beaver Creek |
| symbols and names along the run, not at its start | `CUT_AT_SYMBOLS = False` and `CUTS` by hand | Wildcat |
| symbols with no name (tree areas) | `LOOSE_SYMBOLS` (what they are) | Wildcat |
| a misread symbol | `SYMBOL_FIX` | |
| the rating is the label's colour, not a symbol | `COLOR_SYMBOL` | Smugglers' Notch |
| names with no symbol, or two | `DEFAULT_SYMBOL`, `RATING` | Heavenly's canyons, Smugglers' Notch |
| numbered circles referring to a key | `KEY`, `ON_CIRCLE` | Sugarloaf |
| a leader from a name box to its line | `ON_CIRCLE` (the leader's far end) | Smugglers' Notch |
| glades: names that don't say so; a "glades" that isn't one; glades drawn as their own line style | `GLADES`; `NOT_GLADES`; `GLADE_LINES` | Whistler Blackcomb |
| parks; names with no line | `PARKS`; `NO_LINE` (a marker, with why) | Hunter |
| the whole label is the run's line; no stretch along a name (or one label of it: `(name, (x, y))`) | `LABEL_LINE`; `NO_STRETCH` | Hunter, Heavenly, Beaver Creek |
| areas | `AREAS`, `area(c)`, `AREA_OF` (from the report) | Big Sky |
| several panels | `PANELS` here, a `panels/<panel>/resort.py` each | Whistler Blackcomb |
| an older export on this season's image | `AFFINE`, `GONE` | Heavenly |

`decisions.py` holds what the crops settled: `CHECKED` (a point on the piece → its name), `UNNAMED` (→ why it is no
trail), `CUTS`, `TRACED` and `TRIMS` (a line drawn on under another stops where it meets it).

### Map types not met yet

What the tools would do, untried:
- **An interactive web map** (map tiles, Mapbox or Leaflet): find its tile or data requests
  (`reports/fetch_page.cjs` saves every response). Vector tiles or GeoJSON with run names are the best source
  there is: lines and names exact. Then draw the overlays on a render of the same data, or register the data on
  the printed map (`register_pages.py`'s method with control points). Raster tiles at the top zoom, stitched,
  are recipe G. (Met three times: Deer Valley's resorts-interactive.com map is the printed map's strokes again in an SVG
  grouped by trail name, `vicomap.py`, a check there; Steamboat's, the same kind, is its vector source; Mammoth's
  two give the lines its printed map doesn't draw: Part 3, "Deer Valley", "Steamboat" and "Mammoth Mountain".)
- **The resort's GIS** (an ArcGIS run layer, as Whistler Blackcomb publishes): names and run lines in map
  coordinates. It is a source of truth, not of overlays: the overlay must follow the drawn line. Fit an affine
  from GIS to map on named lines around each junction (as Whistler Blackcomb's check did), then use it to name
  pieces, like `osm_check.py`.
- **One PDF with the mountain's sides on two pages:** a panel per page (`--page` on every tool).
- **A scanned or photographed map:** recipe G with looser masks and more review; expect to trace more stretches.
- **No map at all online:** ask the resort for the layered file; failing that, skimap.org's most recent edition
  with a note in the header.

## Ground rules

- **Never hand-edit generated files** (`trailPaths.json` above all; also `trails.ts`, `linePolylines.json`,
  `trailProposals.json` and Claude's reviews of a resort with a `regen.sh`). Change the inputs (`resort.py`,
  `decisions.py`, `header.txt`, the regen's flags) and rebuild.
- **A person's decisions outrank everything** and survive every rebuild: reviews in `trailReviews.json` without
  `"by": "claude"`. Rebuilds drop and re-add only Claude's (`pdf_resort.py`, `traces_to_reviews.py
  --replace-claude`), keeping the timestamp of a decision that comes back unchanged.
- **A rebuild is byte for byte.** Run a resort's `regen.sh` from an empty work folder and `git status` must show
  nothing; after changing a shared tool, `regen_all.sh` must show nothing for every other resort (or each change is
  understood and checked on crops).
- **Record every decision with the crop that settled it**, in the resort's `decisions.py` (a comment naming the
  crop and what it showed). Record what isn't a trail too, and why.
- **Key decisions by points on the map** where piece ids can change: raster pieces renumber whenever the detector
  is re-tuned (Vail). A PDF's vector extraction is deterministic, so its piece ids are stable for that exact file:
  `regen.sh` checks the source's SHA-256 so a re-export (new ids) is noticed (Winter Park's site now serves one).
- **Verify on zoomed crops**, at 1x or more: judgments on shrunken images were wrong often enough to mislead.
  Never use a test that checks the assigned overlay against itself.
- **The printed symbol is the rating.** Line colour can't tell black from double black, and lists written before
  looking at the map were wrong for a quarter of Killington's trails.
- **The map decides what's on it**; the trail report decides spellings and settles ambiguity (below).
- **Downloaded files are data, not code**: keep them in `work/<id>/` (git-ignored), never run a downloaded
  script, read them only with this repo's tools.
- **Commit and push each finished resort to `main`** (CLAUDE.md records why: sessions that didn't merge
  restarted from scratch).

## Conventions for the judgment calls

What the thirty-eight resorts settled, so the next ones come out alike:

- **Names.** As the resort's trail report spells them where it lists the run (the map prints capitals,
  abbreviations, `10TH MTN`, `MID-MTN`); otherwise as printed, typos fixed (Whiteface's "High County Road",
  Jay Peak's "Lower Lift Linee"). A run the report has renamed since the map was drawn keeps the map's name
  (Heavenly's Express Line). Ids stay put when a name changes (skied history is kept by id).
- **Ratings.** The symbol printed by the name. A name with no symbol: the symbol on its line, else its line's
  colour, else the default of its kind: glades and bowls black (Sugarbush's wooded areas, Vail's bowls), parks
  blue, learning areas green, chutes in an expert area that area's double black (Heavenly's canyons, Sugarloaf's
  Snowfields). Symbols the app doesn't have: advanced intermediate is blue (Big Sky's two squares) unless the map
  draws its runs as black lines (Winter Park's blue square holding a diamond: black); EX, expert and
  high-exposure are double black. A run printed twice with two ratings: the report's rating, else the majority,
  the harder on a tie. Where the map's symbol and the report differ, the map's is kept and the difference noted
  in the resort's header (Whistler Blackcomb's Big Easy, Heavenly's Hogsback). A map that prints no symbols but
  sets each name on a pill in its run's colour: the pill's colour, double black where the legend marks the expert
  runs another way (Snowmass: a yellow-cased line, an EX mark by the name).
- **What is a trail.** Every run the map names. Bowls, faces, chutes, glades, parks, learning and kids' areas are
  trails too, as markers at their names when the map draws no line for them. Lines the map doesn't name (links,
  run-outs, access roads, traverses with no label) have no overlay, recorded in `UNNAMED` with why. Names the
  report lists but this map doesn't print are left out (and listed in the header). A run printed only in an inset
  the resort doesn't publish is left out (Palisades Tahoe).
- **One line, two runs:** where one stroke carries an upper and a lower run (the second's name or symbol printed
  partway), cut it where the second starts (`CUTS`). **One run, two parts:** a run the report splits into upper
  and lower but the map prints once is one trail (Heavenly). **One name, two runs:** printed twice with two
  symbols, two trails as the report lists them (Whistler Blackcomb's Seppo's); printed twice with the same symbol,
  one (Greenline). **The same name on two mountains:** two trails, shown alike (Expressway, Rock Garden).
- **Names printed in a gap of their own line** get a stretch along the name's characters, so the overlay runs
  through the label; not a name printed beside its line, and never a name on two lines (it would zigzag: give it
  a traced stretch instead, or a marker if it has no line).
- **Areas** are the trail report's (mountains, sides, lift pods), each with its highest printed elevation; a map
  in several panels doesn't make the panels areas unless they are (Vail's are).
- **Panels and insets.** An inset that draws terrain the main map leaves out is a panel of its own (Whistler
  Blackcomb's Symphony and Glacier); an inset that repeats the main map at another scale is left out, or kept as a
  panel when it shows runs the main map can't (Heavenly's Top of Gondola). A trail drawn on two panels gets an
  overlay on each.

## The sources of truth, and their limits

| source | good for | not good for |
|---|---|---|
| the map itself | what's on this map: every line, name, symbol | spellings (capitals, abbreviations), which run a shared line belongs to |
| the trail report (`tools/trailmap/reports/`) | names, ratings, areas; which names are runs | where a run goes; runs it lists that this map doesn't print |
| the PDF's drawing order (`pieces.py seq`) | an artwork draws one run's strokes one after another: a piece drawn among another run's strokes is suspect | proof: it is off by one at group boundaries (Winter Park) |
| OpenStreetMap's runs (`osm_check.py`) | which line a run follows past a junction, where it starts and ends (one-way runs) | runs side by side (the local fit can't tell them apart); names OSM spells its own way |
| the resort's GIS (Whistler Blackcomb's ArcGIS layer) | where two runs meet, names of links the map doesn't name | the map's own geometry (another projection) |
| an older edition of the map | what the artwork used to print, navigation hints ("Comet, then the Von Schmidt traverse") | anything changed since |

Each settles a question only together with a crop of the map: a decision says what the crop showed.

## A new season's map

1. Download the new edition (the URL pattern usually just changes its date) and compare it with the old one:
   `pdf_inspect.py` on both, and `register_pages.py` to overlay them. Same artwork, small changes (a renamed run, a
   new park): run `FORCE=1 regen.sh` on the new file, see what the matcher reports (undecided pieces, names that
   matched nothing), add or adjust decisions for what changed, update the URL and SHA-256 in `regen.sh`.
2. New artwork: redo the resort from step 5 of the process, using its folder as the template; a person's reviews
   of trails that are unchanged carry over (their ids stay), Claude's decisions do not.
3. Then the audits and checks as for a new resort, and the header's "as of" notes (report date, edition).

## To fix one trail

Without re-running anything else: add a review for it to the resort's `trailReviews.json` (in `panels/<panel>/` on a
map in several panels): `"status": "confirmed"` with `polylines` (piece ids) and/or `drawn` (points in source px),
`"status": "no-line"` with `labelAt` (percent) for a marker, or `"status": "not-on-map"` for no overlay; leave out
`"by": "claude"`. Then `npm run trails:apply -- --resort <id> [--panel <panel>]`. A person's review outranks every
automatic source and every `regen.sh` keeps it (Okemo's stops if a rebuild would change one). The Trail Check page
writes the same reviews (Part 4). A fix that should also hold for the next edition belongs in the resort's decisions
instead (`pdf_resort.py <id> add`, or its `decisions.py`), then `regen.sh`.

## Pitfalls

**Extracting**
- **Tally everything before trusting the first extraction:** every stroke colour and width (a trail drawn in pure
  black or at another width, Sugarbush; a line drawn as a filled outline, Snowball, Out Road), every small fill
  colour (three names in other shades, Sunday River), every glyph shape.
- **Names come in copies.** A name is often drawn twice (a halo, or this season's colour over last season's), a
  curved one also a letter at a time, and neighbouring names also as one object (Hunter's TAYLOR'S RUN WHICH WAY
  GLADES). `pdf_labels.py` cuts a halo copy inside one object; `pdf_resort.py` keeps one label per printed name.
- **What is drawn isn't always seen.** Labels outside their clip, or hidden under a later one (last season's names
  left in the file), print nothing (Sunday River, Whistler Blackcomb); a stroke drawn twice is one piece, and one
  hidden under another colour along its whole length is none (Palisades Tahoe's Alpine back). Check what the
  extraction found against the rendered map.
- **Glyphs that are one shape turned over:** n and u, d and p, 6 and 9, M and W, ! and i, comma and apostrophe.
  `pdf_glyphs.py labels --turned` (a shape with a gap) or `--turned-hole` (one with a hole) decides by the half of
  the shape it is in.
- **Symbol detection over-counts.** A single diamond touching the end of its own line came out as a double (twice
  on Vail); a diamond drawn twice made a false double (Whistler Blackcomb); bus-stop dots, a sign's border, an info
  box's icon or a traffic light came out as symbols. Squares can be rectangles, corners rounded, a double diamond
  one notched outline. Check every symbol on a contact sheet (`symbol_audit.py --mode diamonds`) before trusting
  the ratings.
- **The default `--min-length` (4 pt) drops short lead-in stubs** drawn into a name's symbol or out of its last
  letter (Breckenridge's eight, 2.8-4 pt): start lower (Hunter: 0.8), or add them later with a second `--append`
  pass (`--min-length 2.5 --max-length 4`), which numbers them after every existing piece. A stub that touches a
  short name's end can make it look "printed along" its line: leave stubs out of that test (Breckenridge).
- **A flattened background already holds the translucent layers.** Matting the full vector layer over it applies a
  wash or a Multiply band twice (Breckenridge's map was 10 levels too light, its bands 27 too dark): take the layer's
  coverage without its translucent forms (`matte_pdf_layer.py --flattened`), and check the result against the PDF's
  own render where only the painting shows. A CMYK painting's flat black stand-in may render as (8,6,6), not 0.
- **Re-exports renumber pieces.** The same map exported again draws its strokes in another order (Winter Park's
  site serves a re-export of the file its decisions were made on; Copper Mountain's drops one label): the SHA-256
  check in `regen.sh` catches it. Raster pieces renumber whenever the detector is re-tuned, and raster symbols
  whenever `raster_symbols.py` is: key those decisions by points (Vail's `decisions.py`, `names.py`).

**Naming and building**
- **Vail-style labels:** the symbol sits on the line and the name beside it, sometimes printed uphill. The line can
  resume past the name (Northwoods, Prima, S. Rim's hook) or the run can simply start at its symbol (N. Rim, Gandy
  Dancer): check each on a crop. A symbol printed on a run's line with no name marks a change of rating and counts
  toward that run's difficulty.
- **The match can give a junction to the wrong run.** A name takes the piece ending at its text, which at a hairpin
  or a fork can be another run's (Heavenly's line into Von Schmidt's label went to the name at its foot). Where two
  runs meet, look at where each continues on a crop, with the drawing order and OpenStreetMap's runs.
- **Dashes through slow zones.** Pale hatching between a road's dashes breaks the "four marks in a row" linking:
  trace those stretches.
- **`trails:apply` can bridge the wrong way.** It joins a trail's parts when their ends point at each other, and on
  a loop or switchback that can draw a straight bridge across the slope (Vail Village Catwalk; Sunday River's
  Prism): trace the real connecting stretch, cut the piece where the junction is (Park City's Raptor Way), or
  leave the stray stub unnamed.
- **Never delete `trailReviews.json` to rebuild** (the first scratch scripts did, which would lose a person's
  decisions): drop only Claude's reviews (ground rules).
- **A review outlives its trail.** `trails:apply` draws every reviewed trail, even one no longer in `trails.ts`:
  when a new edition drops a trail, drop its reviews too.
- **Several panels:** a trail's marker goes on the panel where its name is printed (Part 4, "Several panels").

**The review page and the app**
- Review-page ids are permanent: map-only trails keep `new-<slug>` ids on the page; `importReviews` maps them.
- The draw tool records one stroke per trail; `applyTrailProposals` splits a stroke where consecutive points jump
  more than 400 source px (a new stretch).
- A tap that opens a sheet on a phone is followed by a synthetic click that can hit a button under the finger: the
  app's sheet ignores input for 350 ms.

**This sandbox**
- `pkill -f <pattern>` can kill the shell running it when the pattern also appears in the same command line: stop
  a server by its PID.
- Vail Resorts' sites refuse curl: `fetch_pdf.cjs`, `find_source.cjs` and `reports/fetch_page.cjs` render them in
  headless Chromium through the agent proxy, which needs the proxy CA's pin (worked out automatically). Their image
  CDN (scene7) works with curl. OpenStreetMap's main Overpass server resets connections (`osm_check.py fetch` tries
  mirrors); Common Crawl's index server is slow (`reports/cc_lookup.py` works around it).

# Part 2. Tools

Every script is run from the repository's root. Python tools need `pip install pymupdf pillow numpy
opencv-python-headless scikit-image scipy fonttools`; browser tools need Playwright
(`PLAYWRIGHT_PATH=$(npm root -g)/playwright` in this sandbox). Tools that work on one resort take `--resort <id>` and,
for a map in several panels, `--panel <id>` (`pdf_resort.py` and the tools built on it take `<id>` or
`<id>/<panel>`). Each has a docstring or header with its full usage.

**Finding and inspecting a source** (Part 1, steps 1-2)

| tool | what it does |
|---|---|
| `tools/trailmap/find_source.cjs` | `links`: the PDFs, CDN images and map links a resort's page loads (headless Chromium, scrolled for lazy images); `try`: does a guessed URL exist; `dates`: a dated file name tried for every day in a range |
| `tools/trailmap/fetch_pdf.cjs` | Downloads a PDF from inside its page in headless Chromium, for sites that refuse curl (works out the agent proxy's pin) |
| `tools/trailmap/skimap.py` | skimap.org: `search` for an area, list its `maps` (year, type), `probe` the newest PDFs' content |
| `tools/trailmap/pdf_inspect.py` | What a PDF holds, page by page: images with their resolution, strokes by colour x width, fills, text by font; renders, and the vector layer alone (`--vec`) |
| `tools/trailmap/pdf_classes.py` | The most common stroke classes (or fill colours) of a page, each drawn alone on one contact sheet |
| `tools/trailmap/extract_pdf_image.py` | The lossless raster of a PDF, and whether it has vector text or drawings |
| `tools/trailmap/register_pages.py` | The affine that puts a PDF page on a map image (SIFT, ratio test, RANSAC): an older export on this season's image; `--ref` registers an image instead (an interactive map's painting) |

**The map image**

| tool | what it does |
|---|---|
| `tools/trailmap/matte_pdf_layer.py` | A PDF's vector layer matted over a sharper copy of its painting, or a smooth upscale (`--resample` swaps every painting for an upscale and renders the page as it is); `--flattened` for a background that is the whole map flattened (its translucent layers are left to it) |
| `tools/trailmap/matte_check.py` | A matted image against the PDF's own render, where only the painting shows, under a translucent form and on opaque content: a translucent layer applied twice shows as a bias |
| `tools/trailmap/resorts/vail/images.py` | Saves a large panel smaller as JPEG (overlays are in percent, so any size works) |

**Line pieces**

| tool | what it does |
|---|---|
| `tools/trailmap/extract_pdf_vectors.py` | Numbered pieces straight from a PDF's strokes in the trail colours: `--color`, `--min-width`/`--max-width`, `--append` another class, `--filled` (filled-and-stroked paths), `--outlined` (filled outlines), `--solid` (no dashed ones), `--exclude` boxes (legend, insets), `--min-length` (keep short stubs; with `--max-length` and `--append`, add only the stubs an earlier pass dropped), `--image` (the map at the same scale) |
| `tools/trailmap/pdf_outline_lines.py` | Numbered pieces from a PDF whose lines are filled outlines, by their centre lines (recipe C): `--color` classes, `--dark` ones taken only `--dark-min` pt long or more, `--max-width`, `--min-length`, `--dash` (chain a dashed line), `--exclude` boxes, `--glyphs` + `--letters` (leave out the names' letters) |
| `tools/trailmap/raster_lines.py` | Numbered pieces from a raster map: strict colour masks (`--palette`: Vail's, Steamboat's, Whitefish's, Jackson Hole's), text and icons dropped, dashes linked, skeleton, junctions joined straight |
| `tools/trailmap/split_pieces.py` | Cuts a piece at a point where it runs into a differently named trail |
| `tools/trailmap/snap_trace.py` | A few rough points read off a grid crop snapped onto the painted line: a stretch the extraction missed |
| `tools/trailmap/trace_ink.py` | The cheapest path along the painted line between a few points (`--rgb` or `--dark`): a stretch from its two ends, `--show` to check it |
| `tools/trailmap/route_trace.py` | The same for every run of a map read on crops: a module (`Router(image, palette).route(cls, waypoints, casing)`) over `raster_lines.py`'s colour masks, casings cheap too, waypoints moved onto their line (Whitefish, Jackson Hole) |
| `scripts/lib/lineDetector.mjs`, `scripts/tracePolylines.mjs`, `scripts/evaluateLines.mjs` | Killington's colour-line detector, its vectorisation into pieces, and its ground-truth score (`npm run lines:eval`) |

**Names and symbols**

| tool | what it does |
|---|---|
| `tools/trailmap/pdf_labels.py` | Trail names from a PDF's text, decoding fonts with no Unicode map (`--glyph gid=char` for the ones it can't) |
| `tools/trailmap/pdf_glyphs.py` | Names and symbols from outlined glyphs: `collect` the fills in the name colours (`--max-size` for large capitals), `sheet` each unread shape, `read` `shape=char`, `labels` (word gaps `--space`, glyphs joined within `--join`, `--turned` / `--turned-hole` for shapes that are two characters turned over, `--rect-squares`, `--rounded`, `--reorder`, `--circle-curves`, `--any-circles` (circles drawn with any number of curves), `--diamond-curves` (diamonds with curved sides), `--double-dist`, `--even`, `--sym-min`, `--single`) |
| `tools/trailmap/pdf_symbols.py` | Difficulty symbols from a PDF's fills (`--rounded`, size limits: `--max-diamond`, `--max-square` for rounded squares and circles); `--check` lists trails whose rating has no matching symbol by their label |
| `tools/trailmap/raster_symbols.py` | Symbols on a raster map (square, circle, diamond, double, EX) |

**Naming and the pipeline**

| tool | what it does |
|---|---|
| `tools/trailmap/pdf_resort.py` | A PDF resort's pipeline: its names onto its pieces (the map's settings in `resort.py`, the crops' decisions in `decisions.py`), stretches along names printed in a gap of their line, markers, then the trail list, proposals, Claude's reviews and overlays. `build` writes the review-tile inputs; `add` records decisions as points |
| `tools/trailmap/seed_roster.py` | A trail list (`trails.ts`) from the names and symbols printed on the map |
| `tools/trailmap/aggregate_readings.py` | Readings (the readers', or one built from the PDF) into per-trail proposals and the review page's data |
| `tools/trailmap/traces_to_reviews.py` | Traced stretches and markers into Claude's reviews (`--replace-claude` in a rebuild: a person's reviews stay) |
| `npm run trails:apply` (`scripts/applyTrailProposals.mjs`) | Reviews + proposals into `trailPaths.json`, joining each trail's pieces into continuous lines |
| `npm run reviews:import` (`scripts/importReviews.mjs`) | The Trail Check page's export into `trailReviews.json` |
| `tools/trailmap/refresh_review_data.py` | The review page's data after fixes, with trails flagged for the reviewer to recheck |
| `tools/trailmap/review/index.html` | The Trail Check review page (published as a Claude artifact with a database) |

**AI readers** (Part 4)

| tool | what it does |
|---|---|
| `tools/trailmap/render_tiles.py` | Overlapping zoomed tiles with every piece drawn and numbered |
| `tools/trailmap/prompts/*.md` | The readers' prompts: name the pieces of a new map (`0-new-map.md`), symbols and missing trails, whole-map search, trace pass (`4-trace.md`) |
| `.claude/workflows/trailmap-readers.js`, `trailmap-trace.js` | The workflows that run them in parallel; `tools/trailmap/runs/*.json` are example arguments |
| `tools/trailmap/score_traces.py` | Trace readers scored against a person's drawn geometry |

**Sources of truth**

| tool | what it does |
|---|---|
| `tools/trailmap/reports/` | A resort's trail report: terrain feeds of Vail Resorts' sites (`fetch_page.cjs`, `extract_feed.py`, `feed_trails.py`), their Common Crawl captures (`cc_query.sh`, `cc_lookup.py`, `warc_to_html.py`), mtnfeed (`feed_trails.py` reads its feed too, and a DOR trail list like Mt. Bachelor's) and others (its README); `compare.py`: a resort's `trails.ts` against its `report.json` (runs only one lists, ratings, spellings; a run the report splits into upper and lower parts stands for the map's one run, or for the parts the map prints apart) |
| `tools/trailmap/osm_check.py` | OpenStreetMap's runs: `fetch` a box from an Overpass mirror; `check` each piece against the runs projected by a local fit on the named pieces around it |
| `tools/trailmap/vicomap.py` | A resort's interactive map on resorts-interactive.com (Alterra's resorts): `fetch` its JSON and SVG, `parse` each trail's line and label (grouped by name in the SVG; `--detail`: each line's style, every fill, the paths outside the groups), `fit` the registration on the line pieces (`fit-ink`: on an image's line pixels, where there are no pieces yet), `check` every piece against the trail covering it (`--along`: stretch by stretch), `show` a trail's lines over the map |

**Looking at pieces and overlays on crops**

| tool | what it does |
|---|---|
| `tools/trailmap/grid_crop.py` | A zoomed crop with a labelled pixel grid, optionally the pieces (`id:name`), overlays and symbols: review tiles and coordinates |
| `tools/trailmap/pieces.py` | For a `pdf_resort.py` resort: `info` (pieces and names in a box), `pair` (a crop plain and annotated side by side), `seq` (a piece's place in the PDF's drawing order among other runs' strokes) |
| `tools/trailmap/piece_sheet.py` | Each piece alone on its own crop: maps where one line carries several runs |
| `tools/trailmap/overlay_audit.py` | One cell per trail: its overlay thick, the others thin, its printed labels boxed, how it was named. The main audit |
| `tools/trailmap/region_audit.py` | Every overlay tagged with its name over zoomed regions: the whole map at a glance |
| `tools/trailmap/symbol_audit.py` | Every named symbol against its trail's overlay: off it (`--mode off`), at its end (`ends`), every diamond on one sheet (`diamonds`) |
| `tools/trailmap/pdf_overlaps.py` | Overlays lying along another trail's line (a line drawn on under another, two runs on one stroke) |
| `tools/trailmap/render_crops.py` | Zoomed crops of chosen overlays |

**Checking the whole thing**

| tool | what it does |
|---|---|
| `tools/trailmap/resorts/<id>/regen.sh` | Rebuilds one resort from its sources and decisions (`IMAGES=1`: its map image too; `FORCE=1`: on a source with another SHA-256) |
| `tools/trailmap/regen_all.sh` | Every resort's `regen.sh`, then what git sees changed |
| `tools/trailmap/hover_all.sh` | Builds the app, serves it, and runs `hover_check.cjs` on every resort and panel |
| `tools/trailmap/hover_check.cjs` | Hovers three points of every line and each marker in the real app and compares the tooltip with the trail's name (rendering, not geometry) |
| `tools/app_check.cjs` | A resort in the real app: found by search, every panel loads with overlays, phone layout, no errors |
| `tools/app_flows.cjs` | Phone flows (tap, mark, undo, summary, panels), two tabs, backups |
| `tools/offline_check.cjs` | The service worker: first visit, offline reload, a never-opened resort, panels cached, a deploy, the load-error screen |
| `tools/accounts_check.cjs`, `scripts/mockSupabase.cjs` | Accounts on two devices against a stand-in Supabase |
| `tools/serve_dist.cjs` | Serves a build as Vercel does (cache headers, ETags, gzip), throttled on one shared link if asked |
| `tools/trailmap/resort_files.py` | Where a resort's files are (for these tools) |
| `tools/check_doc_paths.py` | Every repo path the docs mention exists: run it after moving or renaming a script |

**Each resort's own:** `tools/trailmap/resorts/<id>/` (Part 3). **Everything else** written along the way, kept as
a record and not maintained: `tools/archive/` (its README indexes every script).

# Part 3. Resort by resort

In the order they were built: each one's method grew out of the ones before. Every resort but Killington and Stowe
is rebuilt from its sources by `tools/trailmap/resorts/<id>/regen.sh`, byte for byte, into `src/data/resorts/<id>/`
(`IMAGES=1` also rewrites `public/maps/<id>[-<panel>].jpg`; working files go to `work/<id>/` or `$<ID>_WORK`); the
folders built before Hunter Mountain have a README with each step's command, and the others read `resort.py`
(how the map prints things) and `decisions.py` (what the crops settled) through `tools/trailmap/pdf_resort.py`.
Starting a new resort: copy the folder of the one whose source is most alike. The hover numbers are
`tools/trailmap/hover_all.sh`'s on 2026-10-07 (points that show the right name, of all it hovers): a later run should
give the same.

| resort | source | route | rebuild | start from it for |
|---|---|---|---|---|
| [Killington](#killington) | flattened raster PDF | line detector, readers, review page | `trails:apply` from the record | a raster map with a person to review |
| [Stowe](#stowe) | PDF strokes, outlined names | readers, review page | `trails:apply` from the record | |
| [Okemo](#okemo) | PDF strokes, outlined names | readers, trace pass, review of 23 | `regen.sh` (archived readings) | a map whose names can't be extracted, with a review |
| [Sugarbush](#sugarbush) | PDF strokes, outlined labels | readers | `regen.sh` (archived readings) | the same, checked on crops |
| [Jay Peak](#jay-peak) | painting, names as text | trace pass | `regen.sh` (archived traces) | a map with no lines |
| [Whiteface](#whiteface) | PDF strokes and text | names matched to strokes | `regen.sh` (its own scripts) | |
| [Winter Park](#winter-park) | PDF strokes, text with no Unicode map | the same | `regen.sh` (its own scripts) | a font with no Unicode map |
| [Breckenridge](#breckenridge) | PDF strokes and text, CDN painting | the same | `regen.sh` (its own scripts) | |
| [Copper Mountain](#copper-mountain) | lines and names as filled outlines | skeletonised outlines, glyph sheets | `regen.sh` (its own scripts) | |
| [Keystone](#keystone) | PDF strokes, outlined glyphs, CDN image | `pdf_glyphs.py`, matching | `regen.sh` (its own scripts) | |
| [Vail](#vail) | three raster paintings | `raster_lines.py`, review tiles | `regen.sh` (points) | a raster-only map |
| [Hunter Mountain](#hunter-mountain) | PDF strokes and text | `pdf_resort.py` | `regen.sh` | a PDF of strokes and text |
| [Wildcat Mountain](#wildcat-mountain) | older export's strokes and text | `pdf_resort.py`, one line for several runs | `regen.sh` | an older export on this season's image |
| [Sunday River](#sunday-river) | PDF strokes, glyph names, insets | `pdf_resort.py` | `regen.sh` | glyph names, insets at other scales |
| [Sugarloaf](#sugarloaf) | strokes, glyph names, key circles, raster inset | `pdf_resort.py` | `regen.sh` | numbered key circles |
| [Smugglers' Notch](#smugglers-notch) | glyph names on label boxes, leader lines | `pdf_resort.py` | `regen.sh` | label boxes and leaders |
| [Whistler Blackcomb](#whistler-blackcomb) | one PDF, three panels, GIS | `pdf_resort.py` | `regen.sh` | one PDF in several panels |
| [Park City](#park-city) | strokes, glyph names, an inset | `pdf_resort.py`, drawing order, OSM | `regen.sh` | names in ovals, a redrawn inset |
| [Palisades Tahoe](#palisades-tahoe) | three PDFs | `pdf_resort.py` | `regen.sh` | several PDFs |
| [Big Sky](#big-sky) | three PDFs of strokes and text | `pdf_resort.py`, report spellings | `regen.sh` | names spelled by the report |
| [Heavenly](#heavenly) | current image + older PDF | registration, filled outlines | `regen.sh` | an image-only current map |
| [Deer Valley](#deer-valley) | a flattened image + the earlier vector PDF; an interactive map | registration, glyph names, interactive-map check | `regen.sh` | an Alterra resort (resorts-interactive.com) |
| [Mt. Bachelor](#mt-bachelor) | lines and names as filled outlines | `pdf_outline_lines.py`, glyph names | `regen.sh` | lines as filled outlines |
| [Steamboat](#steamboat) | an image; the interactive map's SVG | `vicomap.py`, lines routed onto the image's, `GROUPED` | `regen.sh` | an image-only map with an interactive map |
| [Mammoth Mountain](#mammoth-mountain) | a PDF with no trail lines, names as text; two interactive maps' SVGs | `vicomap.py` lines registered on the painting, names spelled as the groups, `GROUPED` | `regen.sh` | a map with no lines but an interactive map |
| [Snowmass](#snowmass) | PDF strokes and filled casings, names as text on pills in the run's colour | `pdf_resort.py`, the rating from the pill's colour (`COLOR_SYMBOL`) | `regen.sh` | a map rated by its names' colours |
| [Aspen Mountain](#aspen-mountain) | the same kind, three panels; no trail report | as Snowmass, names spelled as printed | `regen.sh` | a map of that kind with insets |
| [Buttermilk](#buttermilk) | the same kind, one panel; the dotted way down | as Snowmass | `regen.sh` | a small map of that kind |
| [Snowbasin](#snowbasin) | PDF strokes and text over a painting, symbols on the lines; a few lines as filled outlines | `pdf_resort.py`; the report from a Common Crawl capture of an HTML table | `regen.sh` | names printed along their lines, symbols on them |
| [Whitefish Mountain](#whitefish-mountain) | three small web JPEGs, no PDF | the map read on crops (`names.py`), lines routed on the painting (`route_trace.py`) | `regen.sh` | a map only published as small images |
| [Jackson Hole](#jackson-hole) | one PNG, no PDF; thin lines faint in the snow, names in the run's colour | the map read on crops (`names.py`), lines routed on the painting, labels snapped to their letters | `regen.sh` | a good image whose lines detection can't follow |
| [Alta](#alta) | PDF strokes, outlined black names, rounded symbols | `pdf_resort.py`, glyph sheets | `regen.sh` | strokes and glyph names, faces with no line |
| [Snowbird](#snowbird) | one JPEG (its PDF the same image), two views in one; lines among blue-painted trees | the map read on crops (`names.py`), lines routed on the painting | `regen.sh` | a map whose PDF is only its image |
| [Schweitzer](#schweitzer) | two images, runs painted with no line; two interactive maps | the groups' names and symbols on the prints, the stretch along each name, `names.py` | `regen.sh` | an image-only map of runs with no lines |
| [Northstar](#northstar) | PDF lines as filled outlines holding several runs, names as white glyphs haloed in the line's colour | `pdf_outline_lines.py` centre lines, the halo's colour as the rating, cuts at each junction | `regen.sh` | one outline for several runs |
| [Beaver Creek](#beaver-creek) | this season's map an image only (CDN); a 2023 vector export of the artwork | registration, glyph names, symbols on the lines (`SYMBOL_ON_LINE`) | `regen.sh` | a Vail Resorts map with no PDF this season |
| [Big Bear](#big-bear) | three images, no PDF: one print drawing the lines, two painting the runs with none; three interactive maps | the print's own lines named by their symbols; the interactive maps' lines and stretches along the names elsewhere; `names.py` | `regen.sh` | an image-only map whose panels differ in kind |
| [Arapahoe Basin](#arapahoe-basin) | one PDF page of two paintings under strokes and outlined black names; most runs a name and a symbol with no line | `pdf_resort.py` per panel, glyph sheets, the stretch along each name with no line (`LABEL_LINE`) | `regen.sh` | strokes and glyph names where many runs have no line |

## Killington

135 trails (113 on lines, 22 markers) · Vermont · one map · areas: its seven peaks.

- **Source:** the resort's 2025-26 map PDF, a flattened raster (one JPEG-2000 image made in Illustrator, no vector
  layers; commit `4d4a326`). Prefer that image to `public/maps/killington.jpg`, a resampled 4:2:0 copy.
- **Route:** the colour-line detector (`scripts/lib/lineDetector.mjs`, 98.6% precision and 95.8% recall on 283
  hand-labelled points), its skeleton traced into 393 pieces (`scripts/tracePolylines.mjs`), 6 readers on 37 tiles
  naming them (`prompts/1-name-lines.md`), a person's review on the Trail Check page (all 166 trails in 35
  minutes), then a second reader pass for symbols and unplaced trails and a whole-map search before removing 29
  names the map doesn't print.
- **Rebuild:** the readers' answers and the review export weren't kept from that session: `trailProposals.json`
  and `trailReviews.json` (135 reviews, a person's) are the record, and `npm run trails:apply` rebuilds the
  overlays. The detector and OCR scripts are in `scripts/` (order in `docs/killington.md`).
- **The map:** difficulty is the line colour (green, blue, black with diamonds on it); maroon lines with a black
  outline are lifts; yellow dots the boundary; magenta bands highlight corridors, not a rating; orange pills
  park features; a red tree icon a glade, often with no line. Names are black text on a white halo along their
  line.
- **Decisions:** the printed symbol rates every trail (34 ratings changed from the old list, each checked on a
  crop); SKYELARK, EAST FALL, HOME STRETCH, SKYEBURST and WILDFIRE are printed twice, each section starting at its
  own symbol: Upper/Lower trails; Treezy and Lil' Stash are glades with no line.
- **Checked:** the review page; hover 359/361 (the misses, Great Eastern showing Home Stretch and Pipe Dream showing
  South Ridge Link, are stretches two trails share).
- **History:** everything tried before this worked, and why it failed, is in `docs/killington.md`.

## Stowe

125 trails (114 + 11) · Vermont · one map · areas Mount Mansfield, Spruce Peak.

- **Source:** the resort's 2025-26 map PDF: one painting with every trail line, label and symbol as vectors
  on top, the labels outlined (no text).
- **Route:** `extract_pdf_vectors.py` (165 pieces; the orange freestyle lines added with `--append`), 6 readers on
  25 tiles with `prompts/0-new-map.md` (about 15 minutes, 620k tokens), which also read every label's symbol,
  glade icon and area, so `seed_roster.py` built the trail list from the map; 7 pieces cut where they run into a
  differently named trail (`split_pieces.py`); a person's review of every trail (`runs/stowe-readers.json`,
  `runs/stowe-trace.json` are the workflow arguments).
- **Rebuild:** built in an earlier session, before pipelines were kept: `trailProposals.json` and
  `trailReviews.json` (125 reviews, a person's) are the record; `npm run trails:apply -- --resort stowe`.
- **The map:** glades print no symbol (black by default); Lower Gulch and Lower Standard are freestyle lines;
  five short connectors print no name (`_unnamed`). The review showed what to automate next: every unanimous
  proposal and glade was accepted unchanged, and the reviewer's time went to unlabelled short trails and runs
  that share pieces (Crossover, Jake's Ride): hence auto-accept and the trace pass (Part 4).
- **Checked:** the review page; hover 351/353 (Jake's Ride / Crossover share a stretch).

## Okemo

128 trails (124 + 4) · Vermont · one map · areas Okemo Mountain, Jackson Gore · `tools/trailmap/resorts/okemo/`.

- **Source:**
  `https://www.okemo.com/-/aemasset/sitecore/okemo/maps/winter-2025-2026/20251120_OK_winter-trail_map_001.pdf`
  (plain curl works; a browser user agent without a browser's other headers gets an error page; `fetch_pdf.cjs` from
  the trail-map page also works). Page 2, clipped above the partner-logo band, at 3 px/pt.
- **Route:** `extract_pdf_vectors.py` in two passes (green, blue and black at `--max-width 0.8`, then the orange
  parks: 256 pieces; the width cap keeps out the 1.11 pt lifts and the legend's 1.0 pt hatching), names outlined
  glyphs, so 6 readers on 33 tiles (one per column; 69 minutes two at a time, 1.5M tokens), then 5 trace readers on
  22 trails, then a person's review of the 23 pre-filled ones (the other 105 auto-accepted).
- **Rebuild:** `tools/trailmap/resorts/okemo/regen.sh` (12 s) from the archived readings (`readings/`: the tile
  readers' `result_*.json`, Claude's TOMAHAWK PARK reading, the trace readers' `trace_*.json`) and Claude's own
  fixes as data (`decisions.py`, applied by `steps.py`). `trailReviews.json` is the person's 23 reviews, kept
  untouched and checked on every run. `TILES=1 FORCE=1` stops after the pieces and tiles, for a new edition.
- **The map:** a symbol with every glade (in a box with the tree icon: read the key before assuming the glade
  default); parks print only an orange pill (blue by default); TOMAHAWK is printed twice, so Tomahawk Park is its
  own trail; Tree Tap is a park; piece 239 is an unnamed spur; piece 210 is cut at (1599, 552), Challenger above,
  Turkey Shoot below. Two carpet learning areas and a small park are areas with no run: markers.
- **Checked:** `pdf_symbols.py --check`: 120 of 127 symbols match (the other 7 print none, or draw the circle
  differently); diamonds on crops, 29 single and 9 double; the review; hover 376/376.
- **New season:** new pieces have new ids, so the readers and trace pass run again (`runs/okemo-*.json`); a
  person's reviews carry over only once their pieces are mapped to the new ids by position. Next time try
  `pdf_glyphs.py` on the names first.

## Sugarbush

138 trails (111 + 27) · Vermont · one map · areas Lincoln Peak, Mt. Ellen · `tools/trailmap/resorts/sugarbush/`.

- **Source:**
  `https://links.imagerelay.com/cdn/1980/ql/7d66b14e89414d4cb778d19f33660efc/2025-26-Sugarbush_Trail_Map.pdf`
  (curl). One page at 3.5 px/pt.
- **Route:** `extract_pdf_vectors.py` in passes: 0.75 pt strokes in blue, black and green with `--filled` (Out
  Road is a green-filled path with a blue edge), then `--append` pure black (Lower Exterminator, Black Diamond Rush)
  and `--append --min-width 0.9 --max-width 1.1` (Hi & Lo Road), and Snowball as a filled outline (`--outlined`,
  found by the readers); 5 readers on 26 tiles (53 minutes, 1.2M tokens); three SPLITs cut (Jester / Allyn's
  Traverse, Northstar / Lower Northstar, Crackerjack / Lower Crackerjack).
- **Rebuild:** `tools/trailmap/resorts/sugarbush/regen.sh` (20 s) from `readings/` (the five readers'
  `result_*.json` and the Snowball reading) and `decisions.py` (the splits, the unnamed connectors 98 and 106).
  `checks/uncovered_strokes.py` lists any trail-coloured stroke without a piece (here: none).
- **The map:** glades ("wooded areas": tree icon, no line, no symbol) are black by default, 27 markers;
  Riemergasse has only a snowflake (green from its line). The diamonds sit inside the outlined labels, so
  `pdf_symbols.py` finds circles and squares only: `checks/symbol_sheet.py black` was the diamond check (30
  single, 8 double).
- **Checked:** every overlay on crops (no review page from here on, at the owner's call); hover 360/360.

## Jay Peak

88 trails (65 + 23) · Vermont · one map · `tools/trailmap/resorts/jay-peak/`.

- **Source:** `https://jaypeakresort.com/sites/default/files/2026-02/JPR_TrailMap_Winter_2025%2B2026_ToPRINT.pdf`
  (curl with a browser user agent and `Accept: application/pdf`; the trail-maps page itself 404s to curl). The
  page at 4 px/pt inside 9,66,1076,657 pt.
- **Route:** the map draws **no trail lines**: names are PDF text (DIN2014-Bold), each with its symbol just
  before it, so the trail list comes straight from the text and the nearest symbol (`labels.py`, `reading.py`), and
  every overlay was traced along the painted cut by 9 groups of trace readers (about 4 hours and 3.9M tokens in all;
  a session limit killed 8 of the first 12 runs: re-run such groups as fresh workflows with their own output).
- **Rebuild:** `tools/trailmap/resorts/jay-peak/regen.sh` (17 s) from `readings/` (the tracers' outputs, applied
  in the order they arrived: `TRACE_ORDER` in `decisions.py` keeps `trailReviews.json`'s order) and
  `decisions.py` (the two rejected traces, the five glades with no cut).
- **The map:** white text on an orange pill is a park; a name printed with mixed symbols takes the majority, the
  harder on a tie; a name printed several times is one trail running through all its labels (Ullr's Dream 7 times);
  Sis Boom Bah is printed only in the inset; "Lower Lift Linee" is a typo. 23 markers at their labels: the 11 named
  glades, the 5 parks, Sis Boom Bah, and six trails whose label sits in painted trees with no cut (Timbuktu,
  Valhalla, André's Paradise, Staircase, Deliverance, Tuckerman's Chute).
- **Checked:** every trace on a zoomed crop (`checks/audit_sheets.py`, the results in `checks/audit_log.json`); 65
  kept as lines; `checks/markers.py` (every marker on its label); hover 218/218.
- **New season:** everything is traced again; only a person's reviews carry over.

## Whiteface

98 trails (95 + 3) · New York · one map · `tools/trailmap/resorts/whiteface/`.

- **Source:** whiteface.com's PDF sits behind a Cloudflare check (curl and headless Chromium alike); skimap.org has
  the 2025-26 map (map 37629: `https://files.skimap.org/3zz4xytnhpior9rwxwsvb0erylv9.pdf`, title and date match).
  The page at 2.2 px/pt.
- **Route:** the first map matched without readers: vector strokes and every name as text in its trail's colour.
  `extract_pdf_vectors.py --max-width 1.6` (the strokes are 1.43 and 1.5 pt, the default 1 pt would drop them; lifts
  are red strokes of the same widths) gives 162 pieces; four are cut where two trails share a stroke; `labels.py`,
  `build.py` and `reading.py` match the names, `decisions.py` holds the 55 crop decisions.
- **Rebuild:** `tools/trailmap/resorts/whiteface/regen.sh` (14 s).
- **The map:** names are drawn twice on the same spot, first in another colour, then the trail colour (keep the
  latter: the colour is the rating; symbols only tell double diamonds, 7 trails); most names sit in a gap of their
  own line (76 of 102 labels matched by the pieces ending at the text's two ends), so 51 trails get a stretch
  through their name, and four are drawn by their stretch alone; fragments ("Glades", "Cut", "Dot") are joined to
  the nearest label of their colour; "Switchbacks" printed once between "Upper" and "Lower" goes on both; the map's
  "High County Road" is High Country Road. Two glades have no line, nor has Yellow Dot (its two-line name in open
  snow; `NO_LINE`, since 2026-10-07: its stretch had zigzagged through both lines): markers.
- **Decisions:** 20 confirm the automatic name, 8 change it, 27 name pieces it left unnamed; piece 130 is an
  unnamed connector. Kept by piece id (the SHA-256 check guards the file).
- **Checked:** region crops (`checks/audit.sh`), the diamond sheet; hover 288/288.

## Winter Park

172 trails (114 + 58) · Colorado · one map · `tools/trailmap/resorts/winter-park/`.

- **Source:** skimap.org map 36019 (`https://skimap.org/skimaps/view/36019`, the 2025-26 "FINAL" export of
  2025-10-30; curl). The resort's site now serves a re-export of 2025-12-02 with the same lines and names but its
  strokes in another order: its piece ids would differ, so the SHA-256 check refuses it. The clip at 3.2 px/pt (the
  embedded painting is 9000x6375, no CDN image needed).
- **Route:** strokes and text as at Whiteface, but the name font is a subset with **no ToUnicode map**:
  `get_texttrace()` still gives each glyph's index, and the subset's CFF charset names it by its index in the full
  font (`pdf_labels.py --glyph 316=- --glyph '63=‘'` for the two it can't decode). Lines: 1.25 pt strokes, then
  `--append` blue at 0.95-1.05 pt (White Rabbit, Lower Parkway, Lonesome Whistle, Jabberwocky).
- **Rebuild:** `tools/trailmap/resorts/winter-park/regen.sh` (20 s); `checks/crops.sh` re-renders every audit crop.
- **The map:** five tiers: advanced intermediate (a blue square holding a black diamond, its trails drawn black)
  is black, EX (two diamonds holding a white E and X, told from the black service icons by those letters) double
  black; lines run straight into their names, so a piece whose end sits on a name's own text line continues that
  trail (157 pieces; 6 more ending there belong to another trail); the drawing order groups each trail's labels with
  its strokes (Z to A) but is off by one at group boundaries; 58 names have no line (parks, bowls, painted chutes,
  the Cirque's nine numbered runs from its key, rated EX): markers; a trail printed with two ratings takes the
  majority, the harder on a tie.
- **Decisions:** every one of the 228 named pieces settled on crops, by piece id (`decisions.py`); 4 unnamed
  connectors.
- **Checked:** region audit in 18 boxes, symbol sheets, the collinear check; hover 400/400.

## Breckenridge

197 trails (157 + 40) · Colorado · one map · `tools/trailmap/resorts/breckenridge/`.

- **Source:**
  `https://www.breckenridge.com/-/aemasset/sitecore/breckenridge/maps/winter-2025-2026/20250926_BR_winter-trail_map_001.pdf`
  (the site refuses curl: `fetch_pdf.cjs`; skimap.org map 39900 is the same file, for curl), and the painting from
  Vail Resorts' CDN:
  `scene7.vailresorts.com/is/image/vailresorts/20250926_BR_winter-trail_map_001?wid=3037&hei=2166&fit=constrain,1&qlt=95`
  (the JPEG's bytes depend on those parameters). Both SHA-256s are checked.
- **Route:** strokes and Unicode text as at Whiteface, but the PDF's painting is only 1482x962: the map image is
  the PDF's vector layer matted over the CDN image (`matte.py`: the page rendered with its painting swapped for flat
  white and flat black, alpha = 1 - (white - black)/255). 0.99 pt strokes in the three colours (dashed ones are
  catwalks and count), four `--exclude` boxes for the legend, lift stats and ad panels: 351 pieces, one cut (piece
  250: Lower 4 O'Clock, then Gondola Ski Back), then a second pass for the 8 lead-in stubs of 2.8-4 pt the first
  drops (`--min-length 2.5 --max-length 4 --append`: pieces 352-359, so the earlier ids stay). The CDN image is the
  map flattened: the matte leaves the PDF's 20 translucent forms (a 10% wash, the Multiply bands and slow zones, a
  few 60-65% fills) to it, taking the layer's coverage from renders without them.
- **Rebuild:** `tools/trailmap/resorts/breckenridge/regen.sh` (8 s; 29 s from empty); `checks/crops.sh`
  re-renders every crop the decisions cite.
- **The map:** names are AvenirNextCondensed-Demi; the text holds many copies of each name (curved labels also a
  letter at a time, objects holding several names, two-line names both apart and joined): keep one per spot, drop
  any label whose letters all belong to other, shorter labels; 31 two-line names joined; ligatures read as fi/fl;
  three names printed twice in two colours (the last drawn wins). Lines run into their names (the legend's
  "-◆ Name-"): a piece ends at the name's symbol or text end; the drawing order doesn't group lines with names
  here. EX is two diamonds holding a white E and X (double black); chute names inside a bowl print no symbol and
  take the bowl's; the four parks are blue; three symbol fills are "Terrain Only" lift notes. 92 stretches on 89
  trails, 40 markers, 17 unnamed lines. Two names have two lines: Frosty's Freeway (its stubs into the name, and
  piece 16 beside it, drawn right after them) and Tom's Mom (through its name, and piece 67 from an access gate
  below it); Tom's Mom is in a gap of its own line although 67 runs close below the name (`IN_GAP`).
- **Decisions:** 178 pieces named on crops, by piece id, each citing its crop (`decisions.py`; the stubs on
  `checks/stubs.py`'s crops).
- **Fixed 2026-10-07** (both were found when its scripts moved into the repo): the image applied the wash and the
  bands twice (10 levels too light where only the painting shows, the bands 27 too dark; now both equal the CDN
  image); the eight stubs were missing, so those overlays stopped up to 12 px short of their lines.
- **Checked:** region audit, symbol sheets; the stubs' 7 trails on overlay-audit cells; `symbol_audit.py` (none off
  its overlay; 4 at an overlay end, each where its run starts); hover 511/511.

## Copper Mountain

128 trails (104 + 24) · Colorado · one map · `tools/trailmap/resorts/copper-mountain/`.

- **Source:** skimap.org map 36383 (`https://skimap.org/skimaps/view/36383`, the 2025-11-06 export "FY26_Main
  Trail Map_WEB"; coppercolorado.com's links were dead that day). The resort now links a December re-export that
  drops one label (THE SNOW MAZE), so every later drawing number moves: the SHA-256 check refuses it.
- **Route:** **lines and names both filled outlines**, no strokes. Names: the glyph fills grouped by shape (a
  signature of the outline's item kinds and chord lengths, unchanged by rotation and size: `glyphs.py`,
  `cluster.py`), each group read once on a contact sheet (`letters.json`, keyed by signature, not by cluster id:
  ids shift whenever a threshold changes), labels as runs of same-colour glyphs (`labels.py`); 11 of the 134
  labels are real text (merged by `names.py`). Lines (`lines.py`): each outline rasterised at 6 px/pt and thinned
  to a skeleton (Zhang-Suen), the pixel graph built without the diagonal steps a 4-neighbour path already joins
  (else every staircase forks), spurs under 2.5 pt pruned, polylines traced between forks. Tucker Mountain's lines
  are clip paths filled with a fading image (of each pair, the one with fewer items is the line); a few are plain
  strokes. Map image: `matte_pdf_layer.py` over the embedded 1817x1465 painting upscaled with Lanczos.
- **Rebuild:** `tools/trailmap/resorts/copper-mountain/regen.sh` (33 s).
- **The map:** glyphs drawn twice leave fragment copies (the longest copy wins, of equal ones the last drawn);
  recoloured names are drawn over their old colour (Sno Deal, Carefree); symbols are fills: square, diamond,
  double diamond (an 8-line outline), EX (double black), circle (4 curves); the logo, highway shields, arrows and
  icons are skipped by drawing number (`SKIP_SEQ`, this edition only); Boulderado's piece is cut at the COPPER
  MOUNTAIN label. 24 markers, no label stretches.
- **Decisions:** 26 pieces settled on crops (`decisions.py`, by piece id): the 12 with two names and the 12 with
  none.
- **Checked:** symbol sheets, crops; hover 336/336. `pdf_glyphs.py` (written after) reads the same
  labels today.

## Keystone

145 trails (120 + 25) · Colorado · one map · `tools/trailmap/resorts/keystone/`.

- **Source:**
  `https://www.keystoneresort.com/-/aemasset/sitecore/keystone/maps/winter-2025-2026/20251028_KY_winter-trail_map_001.pdf`
  (`fetch_pdf.cjs`; skimap.org map 35939 is the same file), and the CDN image
  `scene7.vailresorts.com/is/image/vailresorts/20251028_KY_winter-trail_map_001?wid=3187&hei=2569&fit=constrain,1&qlt=95`:
  the whole map flattened at 2.08 px/pt (painting, lines and names), which lines up within 0.6 px.
- **Route:** outlined glyph names as at Copper, but the lines are plain strokes; the first map read with
  `pdf_glyphs.py` (`collect` the fills in the name colours, `sheet` each unread shape, `read` it once, `labels`).
  Lines: 1.5 pt strokes in the three colours (the legend panel excluded), plus `--append` at 0.9-1.1 pt black for
  Roulette and Black Jack (over a 3 pt white casing); piece 2 is cut where Brahma becomes Snake Pit. Map image:
  `matte_pdf_layer.py --background scene7.jpg --flattened` (the CDN image already shows the PDF's three translucent
  layers, among them the 75% Multiply bands and slow zones; until 2026-10-07 they were applied twice).
- **Rebuild:** `tools/trailmap/resorts/keystone/regen.sh` (32 s).
- **The map:** a condensed font (word gaps measured along the reading direction, `--space 0.75`); its capital I is
  the l shape (a word-initial l is an I); comma and apostrophe are one shape turned over; 13 names recoloured this
  season sit over a black copy (keep the last drawn); names printed in other colours are zones (the five orange A51
  park runs, blue; the four gold kids' adventure zones, green): markers; Witchita's and Red's squares sit below their
  rotated names (`MANUAL`); a circle at (157, 1035) is a traffic light. 9 stretches (names in a gap of their own
  line; Cat South Glades is printed beside its line: none), 25 markers.
- **Truth:** the trail report (`report.json`: the terrain feed as Common Crawl captured it on 2025-11-18): every
  rating agrees with the map's. 16 runs are shown as it spells them, their ids kept (`REPORT_NAMES`, applied as
  `regen.sh`'s last step: the proposals match the reading's names to `trails.ts`): Wichita (printed Witchita), Oh
  Bob, Grays, Two Sled Road, Go Devil - Upper and - Lower, Cat South Glade, Big Horn, Black Forest, ...; kept as
  printed: Jackwhacker (the report's Jackwacker), Ripperoo's (Riperoo's), The Windows (Lower Windows). The legend's
  "Number of Trails 140" is the list's 145 less its five bowls, which the report doesn't list either; the report's
  Discovery and H&H Mine aren't on the map.
- **Decisions:** the match named 121 of 135 pieces; 14 settled and 4 confirmed on crops.
- **Checked:** region audit, symbol sheets; the report, name by name; hover 385/385.

## Vail

194 trails (173 + 21) · Colorado · three panels: Front Side, Back Bowls, Blue Sky Basin (the areas too) ·
`tools/trailmap/resorts/vail/` (its README is the template for a raster resort).

- **Source:** no vector map: three paintings on Vail Resorts' CDN,
  `20251001_VL_winter-{front-side,back-bowls,blue-sky}-trail_map_001` as PNG at `wid=4990` (the `-logos` copies add
  a header band).
- **Route:** `raster_lines.py` (a strict mask per trail colour; text dropped as glyph-sized parts crowded by other
  glyphs, unless thin like a line; symbols, icon fills and sign-box outlines dropped; dashed roads linked by growing
  their dashes until four or more in a row merge; skeleton; junctions joined straight; `--k 1.75` and `--k 2.7`
  scale the marks on Back Bowls and Blue Sky, drawn bigger), `raster_symbols.py` (a double diamond is a black blob
  with a waist, or two diamonds side by side), then every piece named on review tiles and closer crops.
- **Rebuild:** `tools/trailmap/resorts/vail/regen.sh` (13 s with the detection cached; `FRESH=1` re-runs it;
  `IMAGES=1` the JPEGs, `images.py` saving Back Bowls and Blue Sky smaller).
- **The map:** a run's symbol is printed **on** its line, the name beside it, and the line resumes past the name
  (or the run simply starts at its symbol: check each on a crop); where a run's rating changes, the new symbol is
  printed on the line with no name and counts toward its rating (majority, harder on a tie). Bowls print a name
  and no symbol: markers, black. Stretches the detector broke (a name printed in the line, dashes through
  slow-zone hatching, the stub from a symbol to its parent line) were traced from rough points snapped onto the
  painted line (`snap_trace.py`): 67 stretches. A run drawn at a panel's edge gets an overlay on both panels.
- **Decisions:** as **points** on the pieces, never piece ids (`decisions.py`, `names.py`: raster pieces renumber
  whenever the detector is re-tuned); about a third of 550 pieces matched a symbol automatically, the rest settled
  on about 30 review tiles; `add.py` records a decision.
- **Checked:** region audits per panel, `symbol_audit.py` (it found 33 gaps after the region audit had passed: a
  short stub doesn't show at 1.3x), every diamond on a sheet (a single diamond touching its own line's end passed as
  a double twice; bus-route marks passed as singles); hover 336/336 on the Front Side, 157/157 on Back Bowls, 71/71
  on Blue Sky. Cookshack's second diamond has no line of its own: its overlay is the line it is printed beside.

## Hunter Mountain

70 trails (66 + 4) · New York · one map · `tools/trailmap/resorts/hunter/`: **the template for a PDF of strokes
and text** (`resort.py`, `decisions.py`, `header.txt`, `regen.sh`, all run by `pdf_resort.py`).

- **Source:**
  `https://www.huntermtn.com/-/aemasset/sitecore/hunter/maps/winter-2025-2026/20251122_HU_winter-trail_map_001.pdf`
  (`fetch_pdf.cjs` from the trail-map page). The painting is vectors too (246,000 drawings: rendering takes 30 s).
- **Route:** `extract_pdf_vectors.py` (0.38 pt strokes in the three colours, `--min-length 0.8`: ten real stubs
  between a symbol and the next trail are under 4 pt), `pdf_labels.py`, `pdf_symbols.py --rounded` (rounded
  corners; a double diamond is one outline), `pdf_resort.py hunter`.
- **Rebuild:** `tools/trailmap/resorts/hunter/regen.sh` (48 s with images).
- **The map:** every trail line runs into its name, printed in a gap of the line with its symbol at the uphill end;
  names are FuturaPTCond-Medium 3.8 pt text, drawn twice (a halo), curved ones also a letter at a time, and two
  names that sit together also as one object (TAYLOR'S RUN WHICH WAY GLADES): keep one copy of each; four names in
  two parts (`JOIN`: UPPER EAST / SIDE DRIVE, MAD / BOX). Glades print a tree icon, a diamond and no line: markers.
- **Matching:** each name end (past its first or last character, or its symbol) takes the nearest piece end within
  4 pt, preferring the symbol's colour; a piece from one name's text to the next name's symbol belongs to the first;
  then continuations. 127 of 129 pieces named so; 2 settled on crops; 66 stretches through the names.
- **Checked:** crops, symbol audit; hover 202/202.

## Wildcat Mountain

48 trails (47 + 1) · New Hampshire · one map · `tools/trailmap/resorts/wildcat/`.

- **Source:** this season's PDF outlines the names and flattens most lines into the painting, but skimap.org's
  earlier export of the same artwork (map 33684, `https://files.skimap.org/w18ct5ihtid1a6eekf9icq9qaqtj.pdf`) has
  3.27 pt strokes and real text. The map image is this season's from the CDN
  (`20251226_WC_winter-trail_map_001`), registered to the old page within 0.2 px (a 23.77 pt bleed, scale 1.0000).
  Every old name lands on the same outlined name in this season's page, and this season prints no other.
- **Rebuild:** `tools/trailmap/resorts/wildcat/regen.sh` (8 s).
- **The map:** names are printed along their line (no gap), and **one stroke often carries several runs** (Upper,
  Middle and Lower Lynx; Top Cat and Starr Line; Cat Track, Middle Wildcat and Bobcat): `MATCH_ENDS = False`, a name
  along a piece still names it (31 pieces), the rest settled piece by piece on contact sheets (`piece_sheet.py`):
  20 decisions, 3 unnamed links, 9 cuts. Labels beside their line point at it with an arrow; Lower Cat Track's
  arrow points at Wild Kitten's line, so its overlay is that stretch (`TRACED`). Symbols are 10-15 pt and rotated
  (`pdf_symbols.py --max-size 16`); the green FIRST AID CENTER lettering is in the trail green (`--exclude`); the
  tree-skiing areas print a diamond and no name, so they aren't trails here (the map counts 48). No double diamonds.
- **Checked:** contact sheets, crops; hover 142/142.

## Sunday River

137 trails (116 + 21) · Maine · one map with three insets · `tools/trailmap/resorts/sunday-river/`.

- **Source:** the PDF on sundayriver.com's resort maps page (`https://www.sundayriver.com/resort-maps`, the
  2023-24 artwork, still current; on cdn.sanity.io): the main map and three insets (North Peak's back side, Merrill
  Hill's front side, the South Ridge base) on one vector page.
- **Route:** `prepare.py` (lines per group at its own width and cut to its frame: 1 pt on the main map, 0.49 pt in
  the North Peak inset, 1.53 and 2.04 pt in the others; the main map's lines cut out of the insets; White Heat is a
  filled-and-stroked path, `--filled`), `pdf_glyphs.py` (163 shapes read on four sheets, `letters.json`; word gaps in
  points and each inset's letters their own size, so labels are joined once per scale), `pdf_resort.py`.
- **Rebuild:** `tools/trailmap/resorts/sunday-river/regen.sh` (18 s).
- **The map:** names sit on label boxes over their lines, so a name names the line it is printed along
  (`MATCH_ENDS = False`; the nearest one in the crowded inset, `ALONG_NEAREST`); black names print a single or double
  diamond (`--double-dist 1.7`: this map's two diamonds have a gap), green and blue ones no symbol; a glade's
  diamonds sit above the middle of its name (`SYMBOL_CENTRE`). Three names are in other shades (BEAR PAW, the
  inset's ROUNDABOUT, DOUBLE BLIND's dark-grey diamonds): tally every small fill colour. A few names are real text
  (UPPER and LOWER prefixes, Merrill Hill's), joined to their glyph names. Labels drawn outside their clip are hidden:
  dropped.
- **Decisions:** 154 pieces named by the name along them, 19 settled on crops, 10 cuts (one line often carries an
  upper and a lower run: Risky Business, T72, Caramba, Vortex, Air Glow; cut between the labels where another line
  crosses); the inset's two such lines labelled without Upper/Lower stay unnamed rather than become a third trail;
  Prism's lower stub is unnamed (`trails:apply` would bridge it straight across the trees to its inset part). 18
  glades and three other names with no line are markers.
- **Checked:** crops, symbol audit; hover 369/369.

## Sugarloaf

175 trails (127 + 48) · Maine · one map · `tools/trailmap/resorts/sugarloaf/`.

- **Source:** the 2025-26 PDF linked from `https://www.sugarloaf.com/the-mountain/trail-map` (on cdn.sanity.io;
  curl): one vector page over a painting of only 1590x1146 px for 1530x1323 pt, so the map image is the vector layer
  matted over a smooth upscale (`matte_pdf_layer.py --xref 159`).
- **Route:** `prepare.py`: lines (1.2 pt green and blue strokes, 1.15 pt black, the Golden Road's orange dashes; the
  legend's other dashed routes, not in the key, left out; its blue dashed logging roads come in with the blue),
  names (outlined glyphs, 222 shapes read on sheets, `letters.json`; the east side's names are text,
  GillSansNova-Bold), symbols (double diamonds drawn as one outline up to 11.6 pt tall: `collect --max-size 12`;
  glyphs read as `*` are icons and make no names), then `pdf_resort.py`.
- **Rebuild:** `tools/trailmap/resorts/sugarloaf/regen.sh` (27 s).
- **The map:** glades and connecting trails are **red numbered circles** referring to the key under the map, read
  into `resort.py` (`KEY`): a one-digit circle is a lone glyph (`labels --single red`), 6 and 9 are one shape
  turned over (the half holding the loop decides), each circle becomes a name at its centre; a circle printed on a
  line names the unnamed line under it (`ON_CIRCLE`), one in the trees is a glade (`GLADES` where the name doesn't
  say so). Other names sit in a gap of their line, the symbol past one end (`SYMBOL_REACH` 12 pt). The Snowfields
  (the summit) is drawn again in a raster inset with its lines baked in: each of its ten lines traced from rough
  points snapped onto the black line (`snap_trace.py --rgb 20,20,25 --tol 45 --r 6`) through its label (`TRACED`).
  Markers with no symbol and no line take `DEFAULT_SYMBOL` (the back side's five chutes, circles 70-74, double
  diamond as every Snowfields run; West Sluice Chute single, as its neighbours); Winter's Way Ext.'s double diamond
  sits above its circle, out of reach (`SYMBOL_OF`).
- **Decisions:** 176 pieces named by the name at their end, along them or the circle on them; 78 settled on crops
  (links between runs, a stub between two labels, a line two runs share).
- **Checked:** crops, symbol audit; hover 429/429.

## Smugglers' Notch

82 trails (68 + 14) · Vermont · one map · areas Morse, Madonna, Sterling · `tools/trailmap/resorts/smugglers-notch/`.

- **Source:** `https://www.smuggs.com/wp-content/uploads/2024/11/trailmap_2425.pdf` (linked from the trail-map page;
  the 2024-25 artwork, still current; curl): one vector page over a painting of 2356x1596 px for 1695x1147 pt, matted
  over a smooth upscale.
- **Route:** `prepare.py` (3.44 pt strokes; the parks are 7.46 pt orange lines, class `freestyle`), `pdf_glyphs.py`
  (white glyphs on label boxes in the run's colour, 103 shapes; n and u are one shape turned over, and so are ! and
  i: `labels --turned nu --turned '!i'`; Bud's Way and the Howie's of Howie's Wanderer are white text),
  `pdf_resort.py`.
- **Rebuild:** `tools/trailmap/resorts/smugglers-notch/regen.sh` (23 s).
- **The map:** **the rating is the colour of the name's box** (`COLOR_SYMBOL`); experts' runs print chains of two
  or three black diamonds on the line (double black). A box sits on its line, or off it with a thin leader (0.99,
  1.17 or 1.46 pt, some filled-and-stroked) to the line or to a hollow circle (a glade); each leader's end becomes a
  name there, a few points short of its line (`ON_CIRCLE` 3.5); a box is tested against its outline, not its
  bounding box (rotated boxes). One line carries Upper and Lower Drifter: cut between the labels. An expert line
  from the Madonna summit to Catwalk prints a double diamond and no name, and the report has no other expert run:
  unnamed.
- **Report:** smuggs.com's Winter Report lists every trail with its rating and mountain: all 80 trails it shares with
  the map agree (its Burton Riglet Park is the map's Burton Treehouse Riglet Park; Sir Henry's Learning Hill is
  printed only as a place, left out; Bud's Way is on the map only). Areas as the report groups them (`area()`,
  `AREA_OF` for names that cross between mountains); Midway prints a green box and a blue one lower down: `RATING`
  takes the report's Easy.
- **Checked:** crops, symbol audit; hover 218/218.

## Whistler Blackcomb

232 trails (209 + 23) · British Columbia · three panels: Both mountains, Symphony, Glacier · areas Whistler,
Blackcomb · `tools/trailmap/resorts/whistler-blackcomb/` (`PANELS` in `resort.py`, each panel's settings and
decisions in `panels/<panel>/`).

- **Source:**
  `https://www.whistlerblackcomb.com/-/aemasset/sitecore/whistler-blackcomb/maps/winter-2025-2026/20251023_WB_winter-trail_map_001.pdf`
  (`fetch_pdf.cjs`): both mountains on page 2, and on page 1 two insets that draw terrain the main map leaves out
  (the Symphony Amphitheatre, the Blackcomb Glacier); a third inset repeats 7th Heaven and is left out. The images
  are the vector layers matted over upscales of the low-resolution paintings.
- **Route:** `prepare.py` (1.07 and 1.6 pt strokes in two greens, blue, black and purple, 0.8 and 0.6 pt on the
  insets; the parks' solid orange lines with `--solid`, since the same orange dashed is an access route, the boundary
  or cliff hatching; a stroke drawn twice gives one piece; a stroke past an inset's frame is cut at it; closed
  outlines such as Tree Fort split at their farthest point), names (252 glyph shapes and some text; labels hidden
  under a later one with other text, last season's names, are dropped; one glyph run holding two names is cut,
  `SPLIT`), `pdf_resort.py whistler-blackcomb` (all three panels, one trail list).
- **Rebuild:** `tools/trailmap/resorts/whistler-blackcomb/regen.sh` (47 s).
- **The map:** a glade is a black line under white dashes (`GLADE_LINES`); diamonds drawn twice made false double
  diamonds until `pdf_glyphs.py` dropped coincident copies (notched double diamonds `--even 1.6`, small diamonds
  `--sym-min 2.2`, a rounded double diamond and the insets' rectangle squares in `odd_symbols()`); names printed
  both in a gap of their line and beside it (`NO_STRETCH_BESIDE`); names printed twice with different symbols are two
  runs (`RENAME_AT`: Seppo's / Seppo's - Lower, Mainline - Upper / Lower), with the same symbol one (`RENAME`:
  Greenline, Kadenwood Trail); Expressway is a run on each mountain, two trails (`RENAME_AT` + `DISPLAY`); Rabbit
  Tracks is printed over its own line (`LABEL_LINE`); The Glades is a groomed run, not a glade (`NOT_GLADES`).
- **Truth:** the resort's ArcGIS run layer (`Ski_Runs_GDB`: names, ratings, run lines; the scripts are in
  `tools/archive/whistler-blackcomb/truth/`): not on the map's projection, but an affine fit to the named lines
  around a junction puts it within about 20 px, so where two trails' pieces meet on the map their GIS runs should
  meet too. Ten meeting points didn't, six of them naming errors (Sunset Boulevard below Sunnyside Up, Camel Humps
  beside the Harmony Express, White Light under Straight Shot's label, Big Easy below Over Easy, Sidewinder's start,
  the GIS's Peak Traverse and Pig Alley, links the map doesn't name). The trail report (terrain feed) has every name;
  Big Easy (map blue, report green) and Harmony Horseshoes (map single, report double) kept as printed; Flute Bowl,
  North Flute Bowl and Glacier Road print two ratings: the report's. Defaults: Showcase Bowl and Brownlie Basin
  black; Magic Castle, Tree Fort and Kid Trail green; Enchanted Forest and School Yard blue; the parks blue.
- **Decisions:** 228 pieces named by the name at their end or along them, 147 settled on crops, 23 not trails, 13
  cuts.
- **Checked:** every overlay on its own crop, one cell per trail (it found the parks' own lines, Dave's Day Off's
  top, the Symphony summit loop as Jeff's Ode to Joy's, the two Expressways); every diamond on the symbol sheets;
  hover 614/614 on the main map, 56/56 on Symphony, 22/22 on the Glacier.

## Park City

345 trails (252 + 93) · Utah · one map with an inset · areas the two sides, as the report groups its lift pods ·
`tools/trailmap/resorts/park-city/`.

- **Source:**
  `https://www.parkcitymountain.com/-/aemasset/sitecore/park-city/maps/20251114_PC_winter-trail_map_001.pdf`
  (`fetch_pdf.cjs`): one page with the Park City side, Canyons and the High Meadow Park inset (a kids' area, redrawn
  larger). Its paintings are about 1 px/pt, so `matte_pdf_layer.py --resample` swaps each for a Lanczos upscale and
  renders the page as it is (the inset's painting stays clipped to its frame).
- **Route:** `prepare.py` (1.14 pt strokes in green, blue, two near-blacks and the parks' orange; 1.54 and 1.57 pt in
  the inset, cut to its frame; an easier way down is its run's line drawn dashed; the short bits the map redraws
  over crossings' halos are dropped, 90 of them), `pdf_glyphs.py` (122 shapes; 6 and 9 one shape turned over:
  `--turned-hole 69` decides by the half the hole is in), `pdf_resort.py`.
- **Rebuild:** `tools/trailmap/resorts/park-city/regen.sh` (34 s).
- **The map:** the symbol before the name; names in two or three parts joined (`JOIN`); bowls and tree areas in grey
  ovals with their diamond under the oval (`SYMBOL_OF`); expert lines through the trees print a double diamond and a
  name and no line: markers. Names printed in a gap of their line or beside it (`NO_STRETCH_BESIDE`); a name on two
  or three lines between its symbol and its line gets a traced stretch from the symbol through it to the line (8,
  `TRACED`); Wapiti and Flying Salmon at the inset's top edge have no line: dropped by point (`DROP`).
- **Truth:** the report (a Common Crawl capture of the terrain page, March 2026): every name with its rating and
  lift pod; all 345 trails agree with it, and its spellings replace the map's abbreviations (`RENAME`: 10TH MTN,
  MID-MTN, MEN'S SL, LADIES' SL; HARMONY is its Lower Harmony, PINECONE its Pinecone Bowl). Which run owns a line
  between two names: the drawing order (`pieces.py seq`) and OpenStreetMap's runs (`osm_check.py`) settled Sundog
  below its symbol, Willow Draw's run-out, Panorama below its second name, Silverado, Elk Dance down to Upper
  Harmony's arrow, Blaster's line, Chrome Alley.
- **Decisions:** 446 pieces named by the name at their end or along them, 97 settled on crops, 12 not trails (four
  links and two run-outs the map doesn't name, lines entering the inset, a leader, an arrowhead), 5 cuts (one where a
  junction falls between two drawn points and `trails:apply` would bridge the wrong way: Raptor Way onto Sunrise).
- **Checked:** every overlay audited on crops, every symbol against its overlay; hover 849/849.

## Palisades Tahoe

247 trails (124 + 123) · California · three panels: Palisades, Alpine front, Alpine back · areas the two mountains ·
`tools/trailmap/resorts/palisades-tahoe/`.

- **Source:** three PDFs from palisadestahoe.com (`/-/media/palisades-tahoe/pdfs/trail-maps/...`; curl): the
  Palisades side and Alpine's front and back. The two insets the Palisades side refers to (Shirley Lake and
  Silverado; Gold Coast to High Camp) are not published, so the runs only they show are left out. An Alpine trail
  drawn on both Alpine panels opens the first that draws it.
- **Route:** `prepare.py` per panel (1.26 pt strokes on the Palisades side, 1-1.1 pt on Alpine's, whose front's
  black runs are pure black unlike the names' near-black; Alpine's back draws every stroke twice: one piece; a stroke
  hidden under a later one of another colour along its whole length gets no piece), `pdf_glyphs.py` (black glyphs in
  one condensed font on all three maps, 142 shapes; word gaps 1.8 pt on the Palisades side and 0.9 on Alpine's, read
  off a histogram of glyph gaps; d and p one shape turned over, `--turned-hole dp`; glyphs drawn out of turn,
  `--reorder`), `pdf_resort.py`.
- **Rebuild:** `tools/trailmap/resorts/palisades-tahoe/regen.sh` (20 s).
- **The map:** the Palisades side draws squares as rectangles (`--rect-squares --even 1.8`), Alpine's symbols have
  rounded corners (`--rounded`), a double diamond is one notched outline up to 14 pt; some symbols print above or
  below the name's middle (`SYMBOL_CENTRE`); the High Camp gates are numbers in boxes, named Gate 1 to Gate 8 by
  `EXTRA`. Main, Extra, Chimney and National are named in the sky above their chutes, each over a short line
  hanging from its symbol: no stretch along those names (`NO_STRETCH`), nor along Attic's or Broken Arrow's;
  Bottleneck Gully's two-line name sits in a gap of its line: `TRACED` runs through it.
- **Truth:** the trail report (the resort's mtnfeed feed, `tools/trailmap/reports/README.md`): all 247 trails'
  ratings and mountains agree but two (Gold Coast Ridge isn't in it; the back side's Shooting Star, a square, isn't
  its green run at High Camp); its spellings replace the map's (`RENAME`: D-5 to D-8, G.S., Ladies Slalom, The Face
  Cliffs); Rock Garden, Yellow Trail, Sun Bowl and Summer Road are runs on both mountains, two trails each
  (`DISPLAY`). CII Ridge and Cornice Bowl print no symbol (black lines); Gunner's Knob, High Traverse, South Face
  Access (black) and Sandy's Corner (blue) take the report's rating. Settled with the drawing order and
  OpenStreetMap: Jagged Edge past its diamond, the arrowed Lost Lake Loop, Home Run leaving Mountain Run's line at a
  fork (`CUTS`), Burkhart's, Main Backside, Werner's Schuss down the Boomerang loop.
- **Decisions:** 234 pieces named by the name at their end or along them, 54 settled on crops, 4 not trails, 1 cut,
  1 traced stretch; 123 markers (bowls, chutes, faces, cliffs, glades, pockets, the gates).
- **Checked:** every overlay audited on crops, every symbol against its overlay; hover 287/287 on the Palisades
  side, 149/149 on Alpine's front, 77/77 on its back.

## Big Sky

323 trails (290 + 33) · Montana · three panels: the main map of its three mountains, the South Face and Bowl insets ·
areas Lone Mountain, Andesite Mountain, the Spanish Peaks · `tools/trailmap/resorts/big-sky/`.

- **Source:** three PDFs on the resort's trail-maps page (a Sanity site: the files are on cdn.sanity.io named by
  their SHA-1; curl works).
- **Route:** `prepare.py` per panel (each page rendered over an upscaled painting; 1.4 pt strokes in the four
  colours; the main green and blue routes 3.5-4.9 pt wide with their centre lines drawn again, copies dropped; the
  insets' lines 2.1 pt, some drawn twice at two widths: one piece; the pink real-estate access trails read as green;
  a few lines are thin filled ribbons, read by their centre lines, from each point of one side to the nearest of the
  other; lines past an inset's frame cut at it), names as text (`pdf_labels.py`; curved names also drawn a letter at
  a time, joined), symbols as fills (one path, or a cluster of overlapping ones), `pdf_resort.py big-sky`.
- **Rebuild:** `tools/trailmap/resorts/big-sky/regen.sh` (29 s).
- **The map:** the map prints capitals, so `NAMES` (the report's names) matches a printed name by its letters alone
  and shows the report's spelling; a name printed twice for two runs is renamed by where it is printed (`RENAME_AT`:
  Calamity Jane, Take a Bough, Powder River upper and lower); a run marked only by its symbol is named there
  (`EXTRA`: PB & J Way's double square); a symbol nearer another name than its own, or at the top of its line away
  from the name, is given to its name (`SYMBOL_OF`); two runs leaving one line below a symbol they share take it by
  default (`DEFAULT_SYMBOL`). Names are printed along their own line with the symbol at one end; where one name's
  end lies at the end of a piece another name runs along, the piece is the second name's (`ALONG_FIRST`). DTM is
  Don't Tell Mama; CLASS 4, 5, 6 are the report's Whitewater chutes. Ratings: advanced intermediate (two blue
  squares) blue; expert and high exposure (a triple diamond outlined in red) double black.
- **Truth:** the trail report (`/api/reportpal`, `report.json`: name, area, rating as of 2026-09-24): all 323 trails'
  ratings and mountains agree but six it doesn't list (17 Green, Lost Frontier, Gullies Traverse, the three
  Whitewater chutes). Settled with the drawing order and OpenStreetMap: 15 strokes carrying two runs or a run and a
  link (`CUTS`: Stillwater Traverse and Meriwether, Rips and Great Falls Gully, Lazy Jack and Cinnabar, ...).
  `pdf_overlaps.py` found lines drawn on under others (Sacajawea's under Yellow Brick Road's wide line, Lone Wolf's
  inside White Wing's, Yellow Mule's under Lupine's; Liberty Bowl's and Ace's along the traverses they leave): each
  stops where it meets the other line (`TRIMS`).
- **Decisions:** 343 pieces named by the name at their end or along them, 55 settled on crops, 30 not trails (links,
  access lines, a run-out, the traverses under the Headwaters' triple diamonds, OpenStreetMap's Big Horn Cut-Off).
- **Checked:** every overlay on crops, every symbol against its overlay; hover 753/753 on the main map, 125/125 on
  the South Face, 138/139 on the Bowl (the miss: a point of the Turkey Traverse at a gully's foot shows The
  Gullies).

## Heavenly

120 trails (73 + 47) · California and Nevada · two panels: California and Nevada, Top of Gondola · areas the report's
California, Nevada, Top of Gondola · `tools/trailmap/resorts/heavenly/`.

- **Source:** skiheavenly.com shows its 2024-25 map (still current) only as a CDN image (scene7
  `20241105_HV_winter-trail_map_001`, 3652x4990) and links no winter PDF; skimap.org has the 2022-23 PDF of the same
  artwork (map 23043). Its page registers on the image's two paintings (`register_pages.py`: 5837 inliers on the main
  painting, median residual 0.10 px; 0.25 px on the inset), fixed in `resort.py` (`AFFINE`) so a rebuild doesn't
  depend on feature matching.
- **Route:** every place the editions differ was found (the warped page against the image, each region side by
  side; each line piece and label checked against the image's ink) and is recorded: what the image no longer prints
  is left out (`GONE`: Widow Maker, now Lone Wolf; two moved labels and their squares), what it prints anew is
  `EXTRA` (Lakeview Park, Lone Wolf), and a moved label's stretch is traced where the image prints it. Lines are
  **filled outlines**: `prepare.py` reads each by its centre line (split at its two farthest-apart points, each point
  of one side paired with the nearest of the other), chains a dashed line's outlines (one fill, one outline per dash)
  in drawing order, skips arrowheads (two curves and a notch), and skeletonises an outline with more area than one
  line of its length (two lines drawn as one). The names' letters are dark outlines too: a dark outline is a line
  only if it is long. Names: `pdf_glyphs.py` (M and W one shape turned over, `--turned WM`; O and zero alike, a word
  with letters takes O; circles drawn with 16 curves, `--circle-curves 16`; a double diamond is two diamonds one above
  the other, `--double-dist`).
- **Rebuild:** `tools/trailmap/resorts/heavenly/regen.sh` (56 s).
- **The map:** **most runs have no line**: the name is printed along the painted cut, the symbol before it, and
  the stretch along the name from its symbol is the run's overlay (`LABEL_LINE`); a name on two lines gets a traced
  stretch instead. Bowls, faces, woods (glades), Mott and Killebrew Canyons' 21 named chutes (no symbol: the
  canyons' double diamond, `DEFAULT_SYMBOL`), the parks and the learning areas are markers. `JOIN` picks a name's
  parts by where they are printed (UPPER and MOMBO either side of a lift, another MOMBO below).
- **Truth:** the trail report (`report.json`: two Common Crawl captures of the terrain feed, this season's and
  2024-25's, the season the map was drawn for; `tools/trailmap/reports/feed_trails.py` rebuilds both). Names take
  this season's spelling, else 2024-25's; a renamed run keeps the map's name (Express Line, now Sky Express Line); a
  run the report splits into upper and lower but the map prints once is one trail. Every rating agrees with the
  report but Hogsback's (a diamond on the map, double black on this season's report: the map's kept). The lines at
  the top of the gondola were settled with OpenStreetMap's one-way runs and an older edition's navigation map ("Nevada
  to the Top of Gondola: Comet, then the Von Schmidt traverse"), against the automatic match, which had given the
  hairpin into Von Schmidt's label to the name ending at its foot.
- **Decisions:** 45 pieces named by the name at their end or along them, 19 settled on crops, 6 not trails, 3
  traced stretches. The Top of Gondola area's elevation is the Tamarack Express top, 9,725 ft.
- **Checked:** every overlay on crops, every symbol against its overlay (Sand Dunes' symbol 13 px off its overlay's
  end, accepted); hover 265/266 (the miss: Silver Spur's overlay along the stretch of Von Schmidt's label it
  shares) and 9/9 on Top of Gondola.

## Deer Valley

207 trails (181 + 26) · Utah · one map · areas the trail report's ten mountains · `tools/trailmap/resorts/deer-valley/`.

- **Source:** the resort publishes the 2025-26 map (with the East Village expansion) only as its interactive map
  (resorts-interactive.com map 1815, behind `deervalley.com/explore-the-mountain/interactive-grooming-map`) and links
  no PDF. skimap.org keeps two exports of the artwork: the vector PDF of 2025-10-16 (map 35124: 2.1 pt strokes,
  outlined glyph names, over a 45 dpi painting) and the flattened export of 2025-11-04 (map 40099: one 5301x3997
  image in a PDF, a sharp painting, the logo and legend moved). The map image is the November image's trail area;
  the October page is registered on it (`register_pages.py`: 2982 inliers, median residual 0.09 px; `AFFINE` in
  `resort.py`) and everything is read from it.
- **Route:** `prepare.py` (the image's crop; the 2.1 pt green, blue and near-black strokes, the 1.68 and 2.15 pt ones
  too, the legend box left out), `pdf_glyphs.py` (221 shapes read on five sheets, `letters.json`: capitals up to 19 pt,
  `--max-size 19`; glyphs joined within 13 pt, wide letters leave big gaps; diamonds drawn with four curves,
  `--diamond-curves 4`; two diamonds 1.6 widths apart are expert), Northern Light's text letters, `pdf_resort.py`.
- **Rebuild:** `tools/trailmap/resorts/deer-valley/regen.sh` (20 s).
- **The map:** every name is near-black, printed in a gap of its line with its symbol a little apart (`END_REACH`
  12 pt); bowls', chutes' and glades' symbols sit under the middle of a two-line name (`SYMBOL_CENTRE`, `JOIN`, 24
  of them); l and I are one shape (inside a word, l). Names that are no trail (lifts from Sultan Express on, lodges,
  peaks, the "COMING WINTER 26/27" notice on Hail Peak) are drawn after the names: `is_name` by drawing order.
- **The two editions** (`checks/editions.py`: each label side by side, pieces and symbols against the image's ink,
  the image's line ink on no piece): the November image renames Ham Bug Humbug and corrects Persistence, Niagra and
  Pompei (Persistance, Niagara, Pompeii, `RENAME`), and adds Gilt Edge's stub (traced, `TRACED`). Magnet is drawn
  twice at one spot, first misspelt (Magent: `DROP`).
- **Truth:** the trail report (`report.json`, the mtnpowder feed, resort 49: `feed_trails.py` reads it, ratings by
  icon: BlueBlueSquare is advanced intermediate) and the **interactive map**: its SVG is this map's strokes again,
  grouped by trail name (`vicomap.py`: registered on its painting, then fitted on the pieces, median 0.27 px). `vicomap.py
  check` names the trail covering each piece; every difference was settled on a crop (the interactive map lacks a
  few lines: Carbenite's lower part, Clipper's, McHenry's middle). Names take the report's spelling (Mountain Daisy,
  Lake Shore, Nondescript) but Ruins of Pompeii and Miner's Delight; its runs split into upper, middle and lower
  are one trail each as the map prints them, but Lower Lily and Lower Magnet, printed apart, are their own. Ratings
  agree but Silver Buck's (green circles on the map, blue in the report: the map's kept); four names printed twice
  with two symbols take the report's (`RATING`).
- **Decisions:** 363 pieces named by the name at their end or along them, 82 settled on crops, 2 not trails (a link,
  the line along the Empire Express), 5 cuts (Trump/Ontario, Champion/Know You Don't, Clipper/Golden Age, Lady of the
  Lake/All Right, Carbenite/Persistance), 1 traced stretch.
- **Checked:** every overlay on crops (`overlay_audit.py`), every symbol against its overlay (Rising Star's square 50
  px off its overlay, printed under its two-line name; White Owl's and Mayflower Link's beside theirs); hover 569/569.

## Mt. Bachelor

110 trails (72 + 38) · Oregon · one map · areas the trail report's four sectors · `tools/trailmap/resorts/mt-bachelor/`.

- **Source:** the 2025-26 winter trail map PDF linked from mtbachelor.com's trail map page (`cms.mtbachelor.com`,
  plain curl): one InDesign page, the legend and Ski Patrol panel on the left, James Niehues's painting (300 dpi)
  with its vector layer on the right. The map image is the page right of the legend panel (`CLIP`) rendered at 3 px
  per pt.
- **Route (recipe C, then B):** `prepare.py`: the lines with `pdf_outline_lines.py` (every trail line is a filled
  outline 1.1 pt wide in blue, green or near-black; the names' letters, outlines in the same colours, left out by
  their glyph shapes, `--glyphs`/`--letters`; a black outline is a line from 5 pt on: Snapshot Bowl's stub is 6);
  `pdf_glyphs.py` (463 shapes read on sheets, `letters.json`: the Whitebark Pine logo's letters and the icons are
  `*`; green circles drawn with any number of curves, `--any-circles`; squares sometimes as rectangles,
  `--rect-squares`); `pdf_resort.py`.
- **Rebuild:** `tools/trailmap/resorts/mt-bachelor/regen.sh` (15 s).
- **The map:** a name is printed in a gap of its own line in the run's colour, its symbol at the name's start as it
  reads (the top or the bottom), and the line runs on from both ends: a line that runs into a name with no junction
  between is that trail's. Z is N turned a quarter (one shape: `RENAME` Convergence Zone, Atkeson's Zoom); O and zero
  are one shape (a word with letters takes O). The peaks', lodges' and elevations' labels are drawn first and last
  (`is_name` by drawing order), The Moraine among them. Ten names are drawn grouped by shape across a cluster
  (Green Flash, Morning Glory, Early Riser and Day Break at Sunrise, Shorty, Fish Hawk Wing, Marshmallow, West
  Boundary, Volcano Adventure Zone, Start Park): fragments dropped, names placed by hand (`DROP`, `EXTRA`,
  `SYMBOL_OF`). Tree runs (Clark's Jay, Low Pressure), the summit's bowls and chutes, and the Woodward parks have no
  line: 36 markers; the two Bowls & Glades are glades.
- **Lines read wide:** where two lines meet, the PDF may draw them as one outline; split at its farthest-apart
  points it pairs across the branches and reads wider than a line, so it was left out (I-5's and Carnival's lines
  at Carnival's square). `pdf_outline_lines.py` now reads such an outline by its skeleton when its mean width (twice
  its area over its perimeter) is a line's; `checks/missed.py` lists every run-coloured outline no piece, letter or
  symbol covers (none now).
- **Truth:** the trail report (`report.json`): the DOR trail list mtbachelor.com's lift and trail report page loads
  (`api.mtbachelor.com/api/v1/dor/drupal/trails`), every winter run with its sector and rating, read by
  `feed_trails.py`. Names take its spelling (Bushwacker, Northwest Crossover, Halfpipe, Backside Bowls & Glades);
  its runs split into (upper), (middle) and (lower) are one trail each as the map prints them, but Sunrise
  Getback's three parts, printed apart with their own symbols, are three. A run printed with two symbols takes the
  one printed more often, a tie the harder. Ratings agree but Serengeti Plains' (one diamond on the map, double
  black in the report: the map's kept); The Moraine and The Cone print no symbol (black, as the report rates them;
  `DEFAULT_SYMBOL`). Avalanche West and Cloudchaser Access, in the report, aren't on this map. Areas: the report's
  sectors (the parks with the side they're on; a run in two sectors with its upper part's).
- **Decisions:** 148 pieces named by the name at their end or by their symbol, 85 stretches along names, 18 settled
  on crops (the beginner loops at Sunrise, Marshmallow, West Boundary, Fish Hawk Wing against Osprey Way, DSQ against
  Corkscrew), 11 links with no name printed along them.
- **Checked:** every overlay on crops (`overlay_audit.py`); every symbol against its overlay (Northwest Crossover's
  square and Marshmallow's circle are printed beside their lines; seven at an overlay's end, each where its run
  starts); `compare.py` against the report; hover 253/254 (the miss where Melbourne's line runs on into Kangaroo's
  lower name, the stretch both share: either name is right).

## Steamboat

189 trails (144 + 45) · Colorado · one map · one area, Steamboat, as the trail report has it ·
`tools/trailmap/resorts/steamboat/`.

- **Source:** steamboat.com's trail map page links the 2026-27 map as an image only (2400x1682 px; `?w=6000` gets
  the full size as JPEG, plain curl; without it the CDN sends WebP), with the Morningside Park inset top left. No
  PDF anywhere (skimap.org has the 2025-26 image at 10156 px, the same artwork with a few runs redrawn:
  `checks/editions.py`). The interactive map (resorts-interactive.com map 1800; its id found by asking the map API
  for the ids near Deer Valley's, 1815, as the page sits behind a bot check) is this artwork's vector layer again:
  every trail's line, letters and symbol in a group named after the trail. It is the vector source.
- **Route:** `prepare.py`: the SVG parsed (`vicomap.py parse --detail`: each line's stroke and dashes, each group's
  fills, the stroked paths outside the groups, where a few runs' blue lines are), put on the image by
  `VICOMAP_AFFINE` (registered on the SVG's painting, then `vicomap.py fit-ink` on the image's blue line pixels),
  each line routed onto the print's own (the cheapest path through its colour's pixels within 24 px, drawn to the
  SVG's line; a much longer path, a detour, is not taken) after its ends under a label are cut back; the dashed black
  copy over an advanced-intermediate run's blue line left out. Symbols are the group's fills shaped like one (four
  equal sides, a few curves, a black eight-sided outline of 19 units or more is two diamonds); names its other
  fills, split where they jump, kept on two lines when the second is a line away (`two_line`: no stretch). A name
  or symbol the print shows elsewhere is moved there if onto its own line, else a symbol only rates its run
  (`far`). `pdf_resort.py` with `GROUPED`: each piece takes its group's name.
- **Rebuild:** `tools/trailmap/resorts/steamboat/regen.sh` (10 s); it checks the image's and the SVG's SHA-256 (the
  interactive map can be redrawn at any time).
- **The map:** names in the run's colour on a white halo, in a gap of the line; a black run's diamond printed again
  and again along its line; advanced intermediate is a blue line under black dashes with a square and a diamond
  (blue here). Chute 1, 2, 3 and Triangle 3 take the number in their group's id. All Out ("closed to public") and
  the snowshoe trails are left out; the parks, in orange areas in no group, are placed by hand (`EXTRA`).
- **Truth:** the trail report (`report.json`, the mtnpowder feed, resort 6: `feed_trails.py`; BlueBlackSquare is
  advanced intermediate). Every rating agrees with the map's; the report's boundary gates aren't on the map.
- **Where the print differs from the interactive map** (`checks/ink.py` lists each piece's share on the print's line
  ink, worst first): the 2026-27 artwork redrew the middle of Sunshine (Concentration's line and name, Rudi's Run,
  Vagabond's head) and the lines by the parks (Bashor, Bear Claw): the SVG's pieces there are `UNNAMED` and the
  print's lines traced (`TRACED`, read with `trace_ink.py`). A few names stand elsewhere on the print (kept where
  the SVG has them, with no stretch); the SVG's second Over Easy, in the inset, isn't printed (`DROP`).
- **Decisions:** 252 pieces named by their group, 116 stretches along names, 5 traced, 11 not trails.
- **Checked:** every overlay on crops (`overlay_audit.py`); every symbol against its overlay (Mother Nature's is
  drawn 36 px from where the print has it: rating only); `compare.py` against the report; hover 477/477.

## Mammoth Mountain

182 trails (175 + 7) · California · two panels, the whole mountain and the back side (Chairs 13 and 14) · areas the
trail report's three base lodges · `tools/trailmap/resorts/mammoth/`.

- **Source:** mammothmountain.com shows its trail map only in season (in October its pages were in summer mode);
  skimap.org keeps the resort's 2025-26 PDF (map 42347: two pages, the second the map). It prints every name as
  text (TradeGothic Bold, near-black, on a white halo, turned along its run) and every symbol as a fill, over a 100
  dpi painting, and draws **no trail lines**: the runs are the painting's. The lines are the resort's interactive
  maps' (resorts-interactive.com map 1812, the whole mountain, and 1819, the back side): their SVGs draw every run's
  line over the same paintings, grouped under the run's name (the trail report's names: Solitude (Lower), Road
  Runner Lower (Top Half)).
- **Route:** `prepare.py`, per panel: the page rendered at 2.5 px/pt with both paintings upscaled
  (`matte_pdf_layer.py --resample`); each SVG's lines put on its panel by `VICOMAP_AFFINE` (`register_pages.py --ref`
  on the SVG's painting, its offset in the SVG folded in: 106 and 1019 inliers, median 0.27 and 0.33 px; the lifts
  land on the printed lifts), kept as they are, cut where they leave the panel (the main panel less the inset), the
  green groups' circle outlines left out; the class is the group's (double black is red in the SVG, the parks
  orange). Names: `pdf_labels.py`'s text in the names' font and colour; a two-line name is one text object that
  `pdf_labels.py` splits by line, joined again (`two_line`); two names are outlined glyphs (`OUTLINED`, read on a
  crop: LOWER ROAD RUNNER, ANTIN ALLEY / CHICKADEE). Each name takes the spelling of the group of that name whose
  line is nearest (MAMBO printed twice is Mambo (Upper) once and Mambo (Lower) once; LOWER X takes X's (Lower)); LOWER
  SHAFT, in no group and not on the report, is its own run (the interactive map lists it). Symbols: fills by colour
  (green circle of four to eight curves; blue square, Slightly Difficult; a blue diamond in a black one, Difficult,
  advanced intermediate: blue; black diamond of four equal sides; a black eight-sided double diamond), turned with
  their names; bowls' and chutes' symbols sit above a level name (`SYMBOL_CENTRE`). `pdf_resort.py` with `GROUPED`
  and `MATCH_ENDS = False` (nothing printed runs into a name).
- **Rebuild:** `tools/trailmap/resorts/mammoth/regen.sh` (15 s); it checks the PDF's and both SVGs' SHA-256 (an
  interactive map can be redrawn at any time).
- **Two interactive maps:** the main one has no line for the back side's runs (Road Runner (Upper), the back side's
  Santiago, Outpost Glades) and the back side's draws them; a trail drawn on one panel gets no marker on the other.
  They disagree on Road Runner's lower half: the main map's top half comes from Kiwi Flats along Chair 14 to The
  Outpost and down the boundary, the back side's by another way to Chair 12; each panel keeps its own. The main
  map prints a green circle on the top half's LOWER ROAD RUNNER, the back side blue squares (the report: blue).
- **Truth:** the trail report (`report.json`, the mtnpowder feed, resort 60: `feed_trails.py`); its uphill routes
  (skinning routes, white names on the map) are no runs and left out, its adventure zones (a purple star: Twilight
  Zone, Woolly's Woods, Huck's Drop, Goldie's Flight) are green (`DEFAULT_SYMBOL`), its halfpipes and Jibs & More
  (Trail) aren't printed. Ratings agree but Starr Chutes' (a double diamond on both panels, a single in the report:
  the map's kept). The Hemlocks is a double-diamond run and, by the orange park pill printed beside it, the report's
  The Hemlocks (Terrain Features) too (the interactive map's orange line; `EXTRA` at the pill).
- **Where the interactive map is not the print** (`overlay_audit.py`, every cell read): its Skyline runs on from the
  ridge down the face along both SCOTTY'S labels (that descent is Scotty's: cut, `CHECKED`); Back for More's split
  falls in the middle of the second UPPER BACK FOR MORE label (moved to its diamond); Main Traverse runs on past the
  printed dotted traverse through the closed area to the gondola (`TRIMS`); Antin Alley / Chickadee's line stops at
  its label's start and Lower Shaft has none (stretches along their names, `LABEL_LINE`). Left as the interactive
  map draws them, where the painting doesn't tell: China Bowl and Christmas Bowl's parallel lines, Rusty's and
  Ralphie's either side of the Broadway Express, Carousel's line from the top of Lost in the Woods, the back side's
  Dropout Chutes right of Chair 23 and The Hemlocks' V, a few lines that start below the top of their face (Shaft,
  Grizzly (Upper), Top of the World) or end in it (Santiago Bowl, Wipeout Chutes).
- **Decisions:** 196 pieces named by their group, 2 cuts with the part settled on a crop, 1 trim, 2 stretches
  along names; 7 markers (Glades, Gravy Chute, Snake Run, the four adventure zones).
- **Checked:** every overlay on crops (`overlay_audit.py`, 51 sheets: five readers, every flag looked at again on
  `grid_crop.py` crops); every symbol against its overlay (`symbol_audit.py --mode off`: 43 symbols 15-80 px from
  their line, each beside its run as the map prints it); `compare.py` against the report; hover 499/499 (main) and
  93/93 (back side).

## Snowmass

124 trails (114 + 10) · Colorado · two panels, the whole mountain and the inset of Hanging Valley (drawn larger, with
the names the main map leaves out) · areas: the five printed summits (Cirque, High Alpine, Big Burn, Elk Camp, Sam's
Knob), each with the trail report's lift areas whose runs come down from it · `tools/trailmap/resorts/snowmass/`.

- **Source:** the 2025-26 PDF that aspensnowmass.com's Snowmass trail-map page links ("layered", plain curl): one
  Illustrator page, the trail lines vectors over two 100 dpi paintings (the mountain's and the inset's), every name
  text. Lines: blue, black and green strokes (1.12 pt on the main map, thinner in the inset); the expert runs are a
  black line in a yellow casing, drawn as filled outlines (in two yellows in the inset), a few as a thin yellow stroke
  over a wide black one (AMF, Gowdy's, an exit from the Cirque, the inset's West I & II) and a few black lines pure black instead of the
  map's near-black (Cabin, Camp 3, the foot of Garrett Gulch). Names: white text on a pill in the run's colour
  (green, blue, black), set along the run's own line; lifts are red and purple pills; the glades and areas are
  white-on-black boxes like the black runs' pills. **No symbol by any name**: the legend rates by colour, the double
  black runs by their yellow casing (with double diamonds printed along it, often far from the name) and the
  extreme terrain by an EX mark (two black diamonds, as text or as shapes).
- **Route:** `prepare.py`, per panel: the page rendered at the panel's scale (3 and 6 px/pt) with both paintings
  upscaled (`matte_pdf_layer.py --resample`); the strokes (`extract_pdf_vectors.py`, the panel's widths, the inset's
  dashed ridge line left out with `--solid`), the casings' centre lines (`pdf_outline_lines.py`, each yellow its own
  class name: two `--color` of one name keep the last) and the thin yellow strokes, one piece per path (a stroke
  lying along a casing, the inset's expert centre drawn twice, left out). Names: `pdf_labels.py`'s white text in the
  names' font or size (the lodges' and notices' white-on-black callouts are smaller and bold), each one's pill colour
  sampled round its letters on a 6 px/pt render (`pill()`); a black name is expert where its own line (the piece most
  of its letters lie on) is a casing or an EX mark is within two and a half letters; a name printed in parts
  (`JOIN`) is expert if a part is; two names drawn as one text object on two pills (UTE CHUTE FAST DRAW, AMF
  GOWDY'S, BEAR BOTTOM GUNNER'S VIEW) are split before their pills are read (`SPLIT`). `pdf_resort.py` with
  `COLOR_SYMBOL` (the pill's colour is the rating), `ALONG_FIRST` (a name is its own line's), `ALONG_SHORT` (RIO,
  AMF) and `NO_STRETCH_BESIDE`. A run the report splits into (Upper) and (Lower) is one trail as printed, but Green
  Cabin and Banzai, printed apart (`KEEP_PARTS`).
- **Rebuild:** `tools/trailmap/resorts/snowmass/regen.sh` (25 s); it checks the PDF's SHA-256.
- **Truth:** the trail report (`report.json`: Aspen Snowmass's grooming feed, `feed_trails.py`; reports README,
  "Aspen Snowmass"): 135 trails by lift area, its uphill routes left out. The map doesn't print the parks' and pipes'
  names (six), Burnt Mountain Glades (its three runs, Rio, A-Line and Split Tree, are printed instead), Cabin Cut
  Off, Elk Camp Meadows, Mousetrap or Pipeline; it prints the inset's Hanging Valley runs the report doesn't list
  (Upper Ladder, Valley Valley, Wall One and Two, Strawberry Patch, Cassidy's, Union, Willy's, Glade One to Three,
  Waters, Weird Woods: as printed, title case) and Bridges. Ratings agree but Cabin's (a black pill; the report:
  blue; the map's kept). The inset's boundary traverse below High Pass prints no name: the report's High Pass (Lower
  BD), double black (`EXTRA` with its casing's rating).
- **Decisions** (every piece settled on `grid_crop.py` crops): the main map draws a run on as one path where the
  next one starts, so 16 cuts where two runs part (Turkey Trot and Funnel, Glissade and Garrett Gulch, Wineskin and
  Monkshood, Trestle and Green Cabin, Banzai Ridge, Coney Glade and Blue Grouse, Coyote Hollow and Timberline,
  Wildcat and Campground, East Wall and the Cirque's top traverse, Assay Hill and Bridges, ...); Rock Band Chute's
  path runs down along Grinder's before it leaves it (`TRIMS`). On the whole mountain, Hanging Valley's lines take
  the inset's names (Hanging Valley Glades, Weird Woods, Baby Ruth, High Pass (Lower BD); the inset's Upper Ladder is
  Lower Ladder's on the main map, which prints only that). Connectors, cut-acrosses, the traverses along the foot
  of Hanging Valley and the top of the Cirque, and the Cirque's run-out below its headwalls print no name (20 and
  3 `UNNAMED`). Markers: the glades with no line of their own (Free Fall, Sneaky's, Powerline, Sunkiss, Frog Pond),
  Buckskin Cliffs, West Garrett, Fanny Hill, Strawberry Patch, Union.
- **Checked:** every overlay on crops (`overlay_audit.py`, 29 and 7 sheets, every cell read; the cells that showed
  a problem fixed and read again); `compare.py` against the report; hover 332/332 (main) and 75/75 (Hanging
  Valley).

## Aspen Mountain

129 trails (121 + 8) · Colorado · three panels: the whole mountain and its two insets, the summit and Hero's (drawn
larger, with the names of Hero's runs the main map leaves out) · areas: Hero's (its lift's terrain, as the map's
notice groups it) and Aspen Mountain · `tools/trailmap/resorts/aspen-mountain/`.

- **Source:** the 2025-26 PDF that aspensnowmass.com's Aspen Mountain trail-maps page links (plain curl; not named
  like the other three, `2526aspenmountainwebsite.pdf`), drawn like Snowmass's (Part 3, "Snowmass"): trail lines as
  vectors over three 100 dpi paintings, every name white text on a pill in the run's colour, no symbol by any name.
  No green runs. Lines: blue and black strokes (1 pt on the main map, 0.67-0.69 in the insets; the text halos are
  other widths); the extreme terrain is a black line under a thin yellow stroke, or in a yellow casing drawn as a
  filled outline (the Traynor chutes); expert-only runs carry a pair of diamonds on their line; EX marks (two
  diamonds with E and X, text or shapes) on the Traynor chutes.
- **Route:** `prepare.py`, per panel (each panel its own clip and scale, 3 and 6 px/pt; the main panel leaves the
  insets, the notice between them, the legend and the logo out): the page rendered with the three paintings upscaled
  (`matte_pdf_layer.py --resample`); the strokes in the panel's width, the casings' centre lines and the thin yellow
  strokes, one piece per path, each inset's lines cut at its frame (the PDF masks them, they run on under it); names
  from `pdf_labels.py` in the names' Semibold; a black name double black where its own line is a cased one or carries
  a pair of diamonds, an EX mark is by it, or (a name with no line of its own: Hero's Chutes) a pair of diamonds is by
  it. Names printed in two or three lines joined per panel (`JOIN`, a part pinned by where it is printed where the
  same word repeats: LOWER, GLADE, RUN, RIDGE). `pdf_resort.py` with `COLOR_SYMBOL`, `ALONG_FIRST`, `ALONG_SHORT`,
  `NO_STRETCH_BESIDE`; Blondie's and Blazing Star, whose lines run on hidden under their pills, get stretches along
  them (`LABEL_LINE`).
- **Rebuild:** `tools/trailmap/resorts/aspen-mountain/regen.sh` (20 s); it checks the PDF's SHA-256.
- **Truth:** none could be read: out of season the grooming feed lists no trails for Aspen Mountain
  (`mountain=AspenMountain`), and Common Crawl's January 2026 capture of its grooming-report page holds no list (the
  page loads it). Names are as printed, spelled out in `resort.py` (`NAMES`; NIAGRA as printed); GENTELMEN'S RIDGE,
  printed along the ridge, and GENT'S RIDGE, at its foot, are one line (Gent's Ridge); E=m(SKI)² GLADE with its 2
  set on its second line. In season, read the feed and check with `compare.py`.
- **Decisions** (every piece settled on `grid_crop.py` crops; `tools/archive/aspen-mountain/` has the helpers): the
  main map draws long paths that carry several runs, each cut at the junction between two printed names (24 cuts on
  the main map, 7 in the summit's inset): Dipsy Doodle, Buckhorn and Midway Road to Tourtelotte Park, down Ruthie's
  Run, round the top of Shadow Mountain, Magnifico Road and Tower Ten Road on one path; Silver Dip, Spar Gulch,
  Kleenex Corner, Upper Little Nell and Little Nell on another; Summer Road, Lower Roch Run, Summer Road again and W
  5th Ave on a third. Summer Road's two stretches are joined along LOWER ROCH RUN's line, traced again for it
  (`TRACED`; left to `trails:apply`, they would be joined down the black Aztec and Spring Pitch). 1 & 2 Leaf and
  Sunrise/Sunset are two runs, two lines each; Tourtelotte Park two lines either side of its name. Connectors and
  traverses with no name printed: 4, 1 and 1 `UNNAMED`. Markers: the glades and faces with no line (Pancake House,
  Midnight, El Avalanchero, E=m(Ski)² Glade, Nose of Bell), Hero's Chutes #1 and #2, Traynor Ridge.
- **Checked:** every overlay on crops (`overlay_audit.py`, 27, 12 and 10 sheets, every cell read; the cells that
  showed a problem fixed and read again: Corkscrew's and Corkscrew Gully's blue tails, Tourtelotte Park's western
  line, Blazing Star, Summer Road); hover 306/306 (main), 140/140 (summit), 108/108 (Hero's: before the insets' lines
  were cut at their frames, Lazy Boy's ran off the panel).

## Buttermilk

44 trails (43 + 1) · Colorado · one map · areas: its three printed bases (Main Buttermilk, Tiehack, West Buttermilk),
the trail report's lift areas · `tools/trailmap/resorts/buttermilk/`.

- **Source:** the 2025-26 PDF that aspensnowmass.com's Buttermilk trail-map page links ("layered", plain curl),
  drawn like Snowmass's (Part 3, "Snowmass"): trail lines as vectors over two 100 dpi paintings, every name white
  text on a pill in the run's colour, no symbol by any name, no expert terrain. Lines: blue (in two blues), black and
  green 1.12 pt strokes; the uphill routes are orange dashes over black ones, the "least difficult way down" green
  dots (a dashed 1.5 pt stroke): Homestead Road's line from the top to the base, and Bear's lower part.
- **Route:** `prepare.py`: the page rendered at 3 px/pt with both paintings upscaled (`matte_pdf_layer.py
  --resample`); the solid strokes (`extract_pdf_vectors.py --solid`, the legend and the logo left out) and the green
  dots, one piece per path; names from `pdf_labels.py` in the names' Semibold (the lifts', lodges' and notices' are
  Bold), each one's pill colour sampled round its letters. `pdf_resort.py` with `COLOR_SYMBOL`, `ALONG_FIRST`,
  `ALONG_SHORT`, `NO_STRETCH_BESIDE`; names printed in parts joined (`JOIN`: UNCLE CHUCK'S GLADES, MIDWAY AVENUE,
  TIMBER DOODLE GLADE and PTARMIGAN GLADE, each GLADE pinned by where it is printed); HOMESTEAD ROAD and LOWER SAVIO
  printed either side of a lift or a road (`RENAME`, `RENAME_AT`).
- **Rebuild:** `tools/trailmap/resorts/buttermilk/regen.sh` (15 s); it checks the PDF's SHA-256.
- **Truth:** the trail report (`report.json`: the grooming feed, `mountain=Buttermilk`, fetched 2026-10-10; its
  uphill routes left out). RIDGE and TRAIL, printed on Ridge Trail's green upper line and its blue lower one, are the
  report's two Ridge Trails (green and blue): Ridge Trail (Upper) and (Lower). Not printed: Northeast Passage, and the
  parks Panda Park, Teaser Park, Family Cross, the Mini Pipe and the Tiehack Snow Cross. JACOB'S LADDER is the
  report's Alex's Alley (formerly Jacob's ladder): the map's name is kept, a park as the report has it. The report's
  Timberdoodle Glad and Uncle Chucks Glades shown as Timberdoodle Glade and Uncle Chuck's Glades; Ptarmigan Glade is
  printed and not on the report. Ratings agree but Spruce (Upper)'s (a black pill; the report: green; the map's
  kept).
- **Decisions** (every piece settled on `grid_crop.py` crops): 7 cuts where one path carries two runs (Klaus' Way and
  Racer's Edge, Buckskin and Rabbit Run, Spruce and the Super Pipe, Blue Grouse and Westward Ho, Red's Rover and the
  run-out at the foot of West Buttermilk, Savio and its cut-across and its summit traverse); the three lines through
  TIMBER DOODLE GLADE and the two through UNCLE CHUCK'S GLADES are those glades'; 7 lines with no name printed
  (connectors, the summit traverse, the run-outs). Panda Hill, printed with no line (the beginner area at the base):
  a marker.
- **Checked:** every overlay on crops (`overlay_audit.py`, 11 sheets, every cell read; the two it showed wrong,
  Red's Rover's run-out and a cut-across named Ridge Trail, fixed and read again); `compare.py` against the report;
  hover 130/130.

## Snowbasin

125 trails (119 + 6) · Utah · one map · areas: the trail report's lift areas (Strawberry, Needles with Porcupine's
runs, John Paul), each with the elevation printed where its lifts top out · `tools/trailmap/resorts/snowbasin/`.

- **Source:** the 2025-26 PDF that snowbasin.com's trail-maps page links ("for Ikon, reduced", plain curl; the page
  shows a JPG of it; skimap.org's map 34864 is the same file): one InDesign page, James Niehues's painting at about
  2 px/pt under vector lines. Lines: 2.25 pt strokes in black, blue and green, each drawn again at 1.13 pt over
  itself; the Olympic downhill courses are black lines in a yellow casing, the "easier way down" yellow dashes over
  a blue or green line, the area-access gates black Π icons stroked at the trails' width. Four blue lines are filled
  outlines instead of strokes (under the Blue Grouse and Orson's pills, Coyote Bowl's lower part, Sweet Revenge's
  top). Names are text in the run's colour (AvenirNext Medium 10.1 pt; the bowls' two-line names Demi 13.5), printed
  along their line; some names are drawn twice in two colours (the last drawn is on top). Symbols are fills set on
  the line by the name, turned along it; the bowls' double diamonds sit under their names.
- **Route:** `prepare.py`: the page at 3 px/pt with the painting upscaled (`matte_pdf_layer.py --resample`); the
  2.25 pt strokes (`extract_pdf_vectors.py`), the gate icons and the pieces drawn twice dropped, and the four outlined
  lines' centre lines (the outline split at its caps, its two sides averaged); names from `pdf_labels.py` in the
  three trail colours, each copy given its top copy's colour; symbols from `pdf_symbols.py`. `pdf_resort.py` with
  `ALONG_FIRST`, `NO_STRETCH_BESIDE`; the bowls joined (`JOIN`, `JOIN_GAP` 17 pt), two names set as one text object
  split (`SPLIT`: ROCKYJ PINEVIEW, DOGLEG SUNSHINE), the bowls' and The Flank's symbols given to their names
  (`SYMBOL_OF`), and Bullwinkle's and Rocky J's (Rocky J's diamond is nearer Bullwinkle's last letter).
- **Rebuild:** `tools/trailmap/resorts/snowbasin/regen.sh` (25 s); it checks the PDF's SHA-256.
- **Truth:** the trail report (`report.json`): the mountain report page's tables as Common Crawl captured them on
  2026-01-21 (the live page lists summer trails out of season; the reports README, "Snowbasin"), read by
  `mountain_report.py`. LMM is Lower Moose Mound, Needles Run the report's Needles, Rainer's its Rainer's Run, Lower
  Pyramids its Lower Pyramid, the LITTLECAT on the park's orange pill its Littlecat Terrain Park. Printed and not on
  the report: Trapper's Bypass, Eas-A-Long, Catastrophe Rocks!, Dry Bowl, Staircase, Pig Pen, Porky Cirque, the Blue
  Grouse park. On the report and not printed: Powder Puff, Bear Hollow Woods. Ratings agree but Gordon's (a blue
  name and a square on its line; the report: black; the map's kept); Needles Cirque, printed in black with no symbol,
  double black as the report has it (`RATING`).
- **Decisions** (every piece settled on crops; `tools/archive/snowbasin/thin_crops.py` draws the pieces thin so the
  map's own colours stay readable): 17 cuts where one path carries two or three runs (Twist & Shout and Gordon's
  Gully, Trappers Trail and Lower Bear Springs, Mid and Lower Elk Ridge, Mid and Lower Main Street, Hollywood and
  Grizzly Finish, Grizzly Start and Wildflower Start, Wildcat Ridge and Centennial, Porcupine Traverse, Needles and
  Showboat, Slo Road, Bear Hollow and Snow Shoe, No Name below the ridge, Trapper's Bypass's path, which runs along
  Mid Main Street's line between its two stretches); names printed beside a line the auto-match missed (WFO, The
  Walrus, Dog Leg, Sunshine, Needles Way, LMM, 119 in black type on its blue line); 7 lines with no name printed
  (links, the ridge from the tram to No Name's top, the line under the Lower Pyramids). Penny Lane is its whole green
  line, the "Return to Base Area" route from Strawberry included. Markers: the bowls and cirques with no line
  (Sister's Bowl, Middle Bowl Cirque, Needles Cirque, Porky Cirque, Mt. Ogden Bowl, Lower Pyramid).
- **Checked:** every overlay on crops (`overlay_audit.py`, 21 sheets, every cell read; No Name's, which ran along the
  ridge from the tram, cut and read again); `compare.py` against the report; hover 363/363.

## Whitefish Mountain

113 trails (76 + 37) · Montana · three panels: the Front Side, the North Side and Hellroaring Basin (the map's three
sides, the areas too) · `tools/trailmap/resorts/whitefish/`.

- **Source:** skiwhitefish.com's trail-maps page shows three JPEGs (plain curl), James Niehues's paintings: the
  2025-26 Front Side (1600x913) and the 2024-25 North Side and Hellroaring Basin insets (1219x900, still the ones
  linked). No PDF anywhere: not on the site (its media API is closed), not on skimap.org (the same JPEGs, the
  2024-25 front side larger, 2400 px, but redrawn since), not in Common Crawl. Lines are thin (2 to 3 px at 2x),
  green, blue and black; the "easiest route down" a green or blue line in a yellow casing, the night-skiing runs
  in a purple one; names are text printed along the run's line, the symbol at its start; the open faces, bowls and
  chutes are a name and a symbol with no line.
- **Route:** `raster_lines.py --palette whitefish` (looser masks, for the JPEG) finds part of the plain lines and
  none of the cased ones, so the map is read instead (recipe G, step 4): `names.py`, per panel, every name with its
  label's middle and symbol and its run's line as waypoints, read on 2x zoomed grid crops of a 2x Lanczos upscale;
  `prepare.py` routes each line along the painted one (`route_trace.py`); `pdf_resort.py` with the names as
  `EXTRA` and the pieces named by the reading (`GROUPED`).
- **Rebuild:** `tools/trailmap/resorts/whitefish/regen.sh` (15 s); it checks the three JPEGs' SHA-256.
- **Truth:** the trail report (`report.json`: the snow report page's runs by lift, plain curl, fetched 2026-10-10,
  every run listed out of season; `snow_report.py`). Names as the report spells them: the carpets as its
  2 Easy Carpet Area and Big Easy Carpet Area, the parks 2nd Street Park and Depot Terrain Park, BENCH RUN its
  Bench Runs. Every rating agrees (Minnow Park, printed with no symbol, green by the report: `RATING`). Not printed:
  Easy Out and three park features (Central Avenue Park, Lower Central Avenue, Goat Haunt SB Course). Mully's Moguls
  is printed and not on the report. Areas: the map's sides, Chair 7's, Chair 11's and the Bigfoot T-Bar's runs the
  North Side's, Chair 8's Hellroaring Basin's.
- **Decisions:** none to record: each piece is a line of the reading. Three Stooges, three short lines from Russ's
  Street, is its middle one, through its diamond (`trails:apply` would join the three along Russ's Street). Runs on
  two panels (Russ's Street, Toni Matt, Big Ravine, Swift Creek, 1000 Turns) have a line on each. Markers: the open
  faces, bowls and chutes with no line (31 on the Front Side, Stumptown, 5 in Hellroaring Basin).
- **Checked:** every overlay on crops (`overlay_audit.py`, 14, 4 and 3 sheets, every cell read; the ones that
  showed a route on a neighbouring line, Central Avenue, Hope Slope, Ski Way, Under Easy, Middle Fork and Toni
  Matt's top, given waypoints where they strayed and read again, and seven markers moved onto their labels);
  `compare.py` against the report; hover 175/175, 61/61, 44/44.

## Jackson Hole

142 trails (108 + 34) · Wyoming · one map · areas: Rendezvous Mountain and Après Vous Mountain (the map's two
summits; the report has no areas: `resort.area()` divides them along the Teton lift and the Teewinot lift's west
side) · `tools/trailmap/resorts/jackson-hole/`.

- **Source:** jacksonhole.com's winter trail map page shows and links one image (plain curl): DatoCMS's asset
  `1764786024-2025-26trailmapresized.png`, a 3000x1900 PNG as uploaded (`?fm=json` gives its size), James Niehues's
  painting. No PDF, no interactive map; skimap.org's copies are the same image or smaller. Each run is a thin line
  (1-2 px, solid or dashed) in its colour, green, blue or black, its name printed in a gap of it **in the same
  colour**, with no symbols: the colour is the rating. Lifts red, the boundary orange dots, slow zones yellow or
  green hatching, the parks orange pills, the Stash's three parks brown icons. Its SHA-256 is checked.
- **Route:** recipe G, step 5: the map read on crops (`names.py`: per name its colour, its label's first and last
  letters, and its run's line as points from where it starts, through its label, to where it ends), on 2x grid tiles
  and 3x zooms; `prepare.py` routes each line along the painted one (`route_trace.py`, `raster_lines.py`'s
  jackson-hole masks: the lines' lighter blue and greys as well as the names' solid colours), straight across its
  own label, and snaps each label onto its letters. `pdf_resort.py` names each piece by the reading (`GROUPED`),
  rates each name by its colour (`COLOR_SYMBOL`) and the report's double blacks (`RATING`); the base area's green
  runs, printed in the slow zones' hatching, and the Alta Chutes, three labels with no line of their own, are the
  stretch along their names (`LABEL_LINE`).
- **Rebuild:** `tools/trailmap/resorts/jackson-hole/regen.sh` (5 s).
- **Truth:** the trail report (`report.json`: the feed jacksonhole.com's report pages load,
  `jacksonhole-prod.zaneray.com/api/all.json`, fetched 2026-10-10 out of season: 145 runs; `report_feed.py`). Names
  as the report spells them; runs printed in parts are the report's parts (UPPER and LOWER SUNDANCE, the two GROS
  VENTRE, KEMMERER black above and blue below, ASHLEY RIDGE blue and black, HANNA and UPPER HANNA, TEEWINOT and LOWER
  TEEWINOT, UPPER WERNER and the two WERNERs: Middle and the plain one). The resort's double blue squares (advanced
  intermediate) are blue. ST. JOHN'S is printed twice, above and below the Saratoga Bowl Traverse: one trail. Not
  printed: Cirque Gully, St. John's Extension (perhaps the lower ST. JOHN'S), The Crags, Timbered Island. Printed and
  not in the report: Laramie Bowl, the Eagle's Rest and Antelope Flats parks.
- **Decisions:** none per piece: each line is one of the reading. Lines given as read where a route strayed
  (Thunder's beside Hoops Gap's label, Crowheart's lower part beside the trees' shadows, Cowboy Couloir's short line
  through its two-line label). Markers: the bowls, faces and chutes printed with no line (Tensleep Bowl, Headwall,
  the Shots, the Hobacks, Casper and Cheyenne Bowls, Greybull, Moccasin, Fremont...), the glades (Grizzly and
  Washakie), the parks and the Stash.
- **Checked:** every overlay on crops (`overlay_audit.py`, 27 sheets of lines and 6 of markers, every cell read;
  some 40 lines given more points where a route strayed or stopped short and read again, the long traverses on
  larger cells); `compare.py` against the report; hover 358/358; the app check.

## Alta

116 trails (81 + 35) · Utah · one map · areas: the trail report's lifts (Sunnyside, Supreme, Sugarloaf, Collins,
Wildcat) · `tools/trailmap/resorts/alta/`.

- **Source:** the 2025-26 PDF alta.com's plan-your-trip page links (its Cloudinary CDN, plain curl; skimap.org's map
  36318 is an image of it): one Illustrator page, James Niehues's painting at 300 dpi under a vector layer. Lines:
  1.97 pt strokes in black, blue and green, solid; the traverses dashed (black or blue, on a white casing), the
  easier ways down dotted (2.62 pt, round dots); the controlled-access areas purple dash-dot outlines, the lifts
  maroon. Names: outlined black glyphs (no text at all) on a white halo stroke, printed along their run's line, many
  on two or three lines; the faces, bowls, chutes and glades a name and a diamond with no line. Symbols: fills with
  rounded corners, diamonds 10 pt, squares 8, circles 9.
- **Route:** `prepare.py`: the page at 2.5 px/pt (the key bar left out); the strokes 1.9 to 2.7 pt wide
  (`extract_pdf_vectors.py`); the glyphs collected and read once on three contact sheets (`letters.json`, 117
  shapes); symbols from `pdf_symbols.py --rounded --max-square 10` (a new option: Hunter's squares are under 7 pt),
  the fills under 7 pt (icons' parts) left out. `pdf_resort.py` with `ALONG_FIRST`, `NO_STRETCH_BESIDE`,
  `SYMBOL_CENTRE` (a face's diamond under its name's middle), `SYMBOL_REACH` 16 pt; 24 names in parts joined (`JOIN`,
  `JOIN_GAP` 16 pt), the areas' and the backcountry's labels dropped, and a duplicate SHUTES (CECRET CHUTES's last
  letters read again, its C as an S).
- **Rebuild:** `tools/trailmap/resorts/alta/regen.sh` (10 s); it checks the PDF's SHA-256.
- **Truth:** the trail report (`report.json`): the lift and terrain status page's `window.Alta`, every run under its
  lift (`status_report.py`, fetched 2026-10-10 out of season). Names as the report spells them: 180 Bend, 3 Bears,
  Santa Claus, East Baldy Traverse (EBT) for EBT to COLLINS, Spiney Chutes for SPINEY CHUTES AREA, Collin's Face.
  Ratings: the map's symbol; Lower Rustler (a diamond by its name) and Sugar Way (a square) are blue and green on the
  report, the map's kept; Supreme Access, printed with no symbol, black by the report (`RATING`). Not printed:
  Hourglass Chute.
- **Decisions** (every piece settled on crops): lines no name is printed on that go on from a run, given its name
  (the High Traverse's six dashed stretches along the ridge, Ballroom's dashes, Shoulder Traverse's, Johnson's
  Warm-up's foot, Race Course's run-out, Race Course Saddle's line, Race Hill's, Sugar Bowl's and Running Dog Nose's
  stubs, Rustler Four's branch, Devil's Elbow's and Rock N' Roll's dotted ways); 4 that are no run (a lift icon's
  dash, the line from the Supreme top to Catherine's Area, two dotted links); High Main Street's stretch traced
  (printed on two lines in a gap of its line). Markers: 35, the faces, bowls, chutes and glades with no line, and
  the names printed on two lines with none.
- **Checked:** every overlay on crops (`overlay_audit.py`, 13 sheets, every cell read); `compare.py` against the
  report; hover 278/278.

## Snowbird

180 trails (155 + 25) · Utah · one map, two views (the front side above, Mineral Basin below) · areas: the trail
report's sectors (Gad Valley, Peruvian Gulch, Mineral Basin) · `tools/trailmap/resorts/snowbird/`.

- **Source:** snowbird.com's winter trail map page shows a 1920x2318 JPEG (plain curl, its CMS) and links a "Download the
  Map" PDF (`/winter-trail-map/` redirects to `snowbird_trailmap_winter_2526.pdf`): one page holding the same image at
  72 dpi, no vectors. skimap.org's editions are images too (2024's 2023-24 PDF the same kind). James Niehues's
  painting: each run a thin line in its colour with its symbol on it (green circles, blue squares, black diamonds,
  doubles for experts), the name along it in the same colour; the easier ways down cased dashes (blue and orange);
  the bowls, faces and cliffs printed as a name and a symbol with no line. Its SHA-256 is checked.
- **Route:** recipe G, step 5, as Jackson Hole: `raster_lines.py`'s masks keep about half the lines (broken where they
  cross the blue-painted trees and shadows) and none of the cased ways (`tools/archive/snowbird/lines_view.py`), so the
  map is read on 2x grid tiles and 3x zooms (`names.py`: each name, its colour or 'expert' where a double diamond is
  printed by it, its label, its run's line as points). `prepare.py` is Jackson Hole's with the vail masks (`route_trace.py`
  over the JPEG); `pdf_resort.py` rates each name by its colour and symbol (`COLOR_SYMBOL`, 'expert' a double diamond);
  Chip's Access, printed along the cased way from the tram with no line read, is the stretch along its name.
- **Rebuild:** `tools/trailmap/resorts/snowbird/regen.sh` (5 s).
- **Truth:** the trail report (`report.json`: the DOR trail list snowbird.com's lift and trail report page loads,
  `api.snowbird.com/api/v1/dor/drupal/trails`, fetched 2026-10-10 out of season: 175 runs by sector; `feed_trails.py`).
  Names as the report spells them (FIELDS CUT-OFF its Fields Cutoff, NIAGARA its Niagra). Ratings as printed where
  they differ: Hot Lips Gully blue (the report black), Lazy Susan and Tiny Tiger black diamonds (the report blue).
  Printed and not in the report: Baldy's and Pipeline Bowls, Livin' the Dream, Hamilton, Flora and Sunday Cliffs,
  Sunday Saddle. In the report and not printed: Lowest Bassackwards, Old Hollywood. Who Dunnit is printed twice along
  the cased way down Gad Valley's west side, Lupine Loop twice in Mineral Basin, Mini Miners' Camp twice at Baby
  Thunder: one trail each, a line at each.
- **Decisions:** none per piece: each line is one of the reading. Lines given as read where a route strayed onto
  another line, a label or the trees (Bass Highway's bend, Barry Barry Steep, Binx's Bumper, Hoop's, Lazy Susan, Old
  Ladies, Road to Provo, Regulator Johnson, The Fin, Upper Chip's Run down its switchbacks, Junior's Powder Paradise,
  Nash Flora Lode, Tail Feathers, Westward Ho, and others). Markers: the bowls, faces, cliffs and chutes printed with no
  line.
- **Checked:** every overlay on crops (`overlay_audit.py`, 39 sheets of lines and 5 of markers, every cell read; some 45
  lines given points or taken as read and read again, two markers moved onto their labels); `compare.py` against the
  report; hover 490/490; the app check.

## Schweitzer

103 trails (96 + 7) · Idaho · two panels: Schweitzer Bowl (the front) and Outback Bowl (the back; the report's two
areas too) · `tools/trailmap/resorts/schweitzer/`.

- **Source:** schweitzer.com's maps page links the 2025-26 maps as images only (plain curl): Schweitzer Bowl at
  3300x2550, Outback Bowl at 1920x1484 only. skimap.org's map 30575 is the 2024-25 Outback Bowl at 3300x2550: the
  same artwork (the two register as a plain scaling, and the 28 places they differ are the JPEG's ringing round
  letters and lift lines: `tools/archive/schweitzer/editions.py`), used for its resolution. No PDF anywhere (skimap's
  PDFs are 2022's, images in a PDF). James Niehues's paintings: the runs are painted slopes with **no line**, the name
  printed along each in black on a white halo and its symbol by it; only the cat tracks are navy lines; the parks are
  orange pills. The resort's interactive maps (resorts-interactive.com maps 1826 and 1827, found by asking the map API
  for the ids near Deer Valley's) draw the same paintings, each run's white letters (the print's halos) and symbol in a
  group named after it (the report's names, the upper and lower parts of a run apart), and on the front the cat
  tracks' lines. The Outback map's groups have no black symbols, and 21 of its groups no letters.
- **Route:** `prepare.py`, per panel: each SVG registered on its print (`register_pages.py --ref` on the SVG's
  embedded painting: 808 inliers, 0.33 px; 653, 0.18 px); per group its letters in drawing order, split where they
  jump (a run printed twice), moved onto a smooth curve (DOWN THE HATCH's small THE zigzags), and its symbols (a fill
  of two four-sided outlines a double diamond); `names.py` adds the labels and symbols the groups lack (read on crops;
  the print's black diamonds found by `tools/archive/schweitzer/diamonds.py` and each given its run on a crop), renames
  two groups (the interactive map's Crystal is the print's SOUTHSIDE PARK, a park; Stiles is Stiles (upper)) and drops
  Crystal's square; the cat tracks are the front SVG's lines and `names.py`'s waypoints on the Outback map, routed
  along the print's navy pixels (a tight colour match: a looser one takes in the trees' shadows), each gap where its
  name is printed crossed straight. `pdf_resort.py` with `LABEL_LINE` for every name (each run's overlay is the
  stretch along its printed name, from its symbol), `NO_STRETCH` for the names printed on two lines (markers) and the
  cat tracks (their line is their overlay), the pieces named by their group (`GROUPED`).
- **Rebuild:** `tools/trailmap/resorts/schweitzer/regen.sh` (15 s); it checks the five sources' SHA-256.
- **Truth:** the trail report (`report.json`: the mtnpowder feed, resort 168, fetched out of season: every run
  listed; the cross-country trails left out). Every rating agrees; the parks (no symbol printed) are blue by default.
  JIMMIE'S RUN (J.R.) is Jimmy's Run, upper and lower; UPPER G-3, UPPER KANIKSU and LOWER LOOPHOLE the report's
  G-3 (upper), Kaniksu (upper), Loophole (lower). Printed and not on the report: Southside Park, Britt's Bowl, South
  Bowl Chutes. On the report and not printed: Dogleg, the E to H Chutes, the R Chutes, Headwall Runout, Pend Oreille
  (lower) and (middle), Kaniksu Woods, No Joke Runout, Phineas' Runout, Toomey's Runout, Upper Siberia Road, North
  Bowl Chutes.
- **Decisions:** none per piece: each label and line is named by its group or by `names.py`. Runs printed on both
  maps (Caboose, Skid Row, Trial Run, Loophole Loop, The Great Divide, Down the Hatch, Cat Track to Village) have an
  overlay on each; a run printed twice on one map has a stretch at each (Gitback's two joined by `trails:apply` across
  the open slope between them). Markers: the names printed on two lines (South Bowl Chutes, Bunny Hills, Lakeside
  Chutes, Wayne's Woods, Short Cut) and the glades (Chair 4 Glades, JR Trees; Glade-iator is a run, `NOT_GLADES`).
- **Checked:** every overlay on crops (`overlay_audit.py`, 6 and 7 sheets, every cell read; the Outback cat tracks
  routed again where they had strayed onto the trees' shadows and the boundary's yellow line); `compare.py` against
  the report; hover 136/136, 180/180.

## Northstar

99 trails (83 + 16) · California · one map · areas: the trail report's (Mt. Pluto, The Backside, Northwest Territory,
Lookout Mountain, the Village; the terrain parks Mt. Pluto's) · `tools/trailmap/resorts/northstar/`.

- **Source:** the 2025-26 PDF northstarcalifornia.com's trail-map page links (Vail Resorts: fetched from inside the
  page, `fetch_pdf.cjs`; skimap.org's map 36907 is the same file), page 1 (page 2 is the village directory): Alex
  Tait's painting in 100 tiles at 150 dpi under an Illustrator vector layer. Every trail line is a filled outline
  (the artwork's strokes outlined and united), blue, black or green, each colour in two shades; where runs meet, one
  outline holds several of them. Names are white capitals on the line itself, each letter haloed by a fill in the
  line's colour: outlined glyphs, and some as live text (Frutiger UltraBlack, Folio ExtraBold; a curved one's halo
  copy drawn one letter at a time); the lifts' names white on red bands. Symbols are fills on the line by the name.
  The terrain parks are orange pills with white names and no line; the Kids Adventure Zone's four are numbered
  smiley signs on blue squares, named only in their box; Carpet Bowl is printed only in the Mid-Mountain inset.
- **Route:** `prepare.py`: the page at 3 px/pt; the centre lines of the outlines in both shades of each colour
  (`pdf_outline_lines.py`), less the halos (a piece under 25 pt lying on white letters' boxes), the slow zone's
  hatching, closed outlines under 80 pt and three icons drawn in the trail colours; the glyphs read once on contact
  sheets (`letters.json`) and the live text; each name's colour the halo under its letters (a vote), else its live
  copy's; symbols from `pdf_symbols.py`, less the kids' signs' squares. The legend, the Mid-Mountain inset, the kids'
  box and the partners' bar are left out. `pdf_resort.py` with `ALONG_NEAREST`, `ALONG_FIRST`, `NO_STRETCH_BESIDE`;
  ten names printed in two parts joined (`JOIN`, `JOIN_GAP` 40 pt, AXE read as EX: renamed), the lifts' names dropped,
  Cowboy Pass and Bearly their labels' stretch (`LABEL_LINE`), the kids' four and Carpet Bowl as `EXTRA` markers.
- **Rebuild:** `tools/trailmap/resorts/northstar/regen.sh` (3 min: the outlines' centre lines are slow); it checks
  the PDF's SHA-256.
- **Truth:** the trail report (`report.json`): the terrain feed of the terrain-and-lift-status page as Common Crawl
  captured it on 2026-02-19 (the reports README, "Northstar"), 103 rows. Every printed name is on it and every rating
  agrees; not printed: Coyote Crossing, Drifter Connector, Lower Chute (a terrain-park run; the unnamed line with a
  square below The Chute's foot may be it).
- **Decisions** (every piece settled on crops; `tools/archive/northstar/colour_crops.py` draws each piece in its own
  colour, `sharp_turns.py` finds where a centre line turns back into another run's line, `on_points.py` the points
  either side of a cut, `overlaps.py` two named pieces along one line): 30 cuts where one outline carries several
  runs (the summits of Mt. Pluto and Lookout Mountain, the Grouse Alleys and The Flume, Axe Handle and Stump Alley,
  the Ridges, Lookout Road and Drifter, The Islands, Boca, Prosser and Stampede, Gooseneck, Schwarzstrasse and
  Washoe, Home Run, Boondocks and Lookout Bypass, the Pioneers, Skid Trail, Lumberjack and the Main Streets, Goldmine
  and Upper Jibboom, Gateway and Timber Line, the Lion's Ways, Iron Horse and Why Not; Northern Lights' outline run on
  down Christmas Tree's line); three trims where a run's outline goes on along another's to their common foot (Home
  Run's doubled stretch, Stump Alley onto Luggi's, Castle Peak onto Drifter's); lines no name is printed on that go
  on from a run given its name (Iron Horse from the summit and on to the Backside Express, Prosser's summit line,
  Christmas Tree's two run-outs, Timber Line to its lift, Overland Trail's under its two-line name); 24 pieces no
  trail: label leaders, missed letter halos and badges, and links with no name (from West Ridge's foot to Goldmine,
  under the Lookout Link, below The Chute, past the kids' signs). Markers: the parks, the glades, the kids' four,
  Carpet Bowl.
- **Checked:** every overlay on crops (`overlay_audit.py`, 17 sheets, every cell read; Crosscut's, Upper Main
  Street's, West Ridge's, The Chute's and Schwarzstrasse's extra lines, and Christmas Tree's doubled stretch, fixed
  and read again); `compare.py` against the report; hover 265/265.

## Beaver Creek

168 trails (148 + 20) · Colorado · one map · areas: the trail report's (Beaver Creek Upper and Lower, Birds of Prey,
Rose Bowl, Grouse Mountain, Larkspur, Strawberry Park, Bachelor Gulch, McCoy Park, Arrowhead, Elkhorn, the resort
skiways, the Landing) · `tools/trailmap/resorts/beaver-creek/`.

- **Source:** beavercreek.com links no PDF this season: the map is the CDN painting
  `scene7.vailresorts.com/is/image/vailresorts/20251006_BC_winter-trail_map_001` (4990x4453 px, PNG at full width),
  the map image (above the partners' band). skimap.org keeps the 2023-24 export of the same artwork as a vector
  PDF (map 25267, InDesign, 2023-10-04: the painting itself 242,000 vector drawings, trail lines strokes, names
  outlined glyphs, symbols fills). Both SHA-256s are checked.
- **Route:** recipe D: the PDF's page registered on the image (`register_pages.py`, 2664 inliers, median 0.09 px,
  `AFFINE` in `resort.py`); `checks/editions.py` finds where they differ: the lodges' and restaurants' icons, dash
  phases, and Dakota Skiway, new at Arrowhead (its name and circle `EXTRA`, its dotted line `TRACED`). Lines
  (`prepare.py`): 0.66 pt strokes in green, blue and black (dashed: roads and catwalks; 0.71 pt dotted: the
  homeowner skiways), West Fall Road's dashes in the squares' blue, the two gladed zones' brown lines (the legend's
  Gladed Zone: Three Tree Gully, Jack Rabbit Alley), and one skiway drawn as filled dots (chained into a piece:
  Creekside's). Names: `pdf_glyphs.py`, a new condensed font read on contact sheets (`letters.json`; one B and one N
  shape first misread as V and C), the symbols fills (`--rect-squares`: the squares are rectangles). Each run's
  symbol is printed on its line, often partway along it, the name beside: `SYMBOL_ON_LINE` names the piece under a
  named symbol (a `pdf_resort.py` setting new with this map). 43 names printed in two or three parts (`JOIN`).
- **Rebuild:** `tools/trailmap/resorts/beaver-creek/regen.sh` (1 min).
- **Truth:** the trail report (`report.json`): the terrain feed as Common Crawl captured it on 2026-02-07 (183 rows,
  the homeowner skiways and McCoy Park's beginner runs among them; typos fixed in `resort.py`: Holden SKiway,
  Gosawk Connector). Runs the report splits into parts and the map prints once are one trail named as printed
  (Kestrel, Peregrine, Larkspur, Cinch, Dally, Latigo, Primrose, Intertwine, Gunder's, Cabin Fever, Little Brave,
  Raven Ridge, Upper and Lower Stirrup; the report's BC Expressway and Pines/Chateau are the map's Beaver Creek
  Mountain Expressway and Borders-Pines-Chateau Skiway); where the map prints a part's own symbol, the parts are
  trails: Centennial's four (Hohum, Spruce Face, Willy's Face, Finish Face, each by its symbol: `RENAME_AT`),
  President Ford's and Stacker (a square on each line under the Strawberry Park lift with no name: - Lower).
  Not printed: Beginner Area Ch. #2, Camp Robber Rd, Golden Eagle Connector (probably the unnamed black traverse
  from West Fall Road), Ripperoo's Retreat, Bear Cave and Gold Mine (named only in the kids' zones box). Ratings
  kept from the map where the report differs: Borders and Ridge Rider (blue squares; the report green), Goshawk
  Upper, Heads Up, 4 Get About It, Royal Elk Glade (double diamonds; black), Ptarmigan and Ruffed Grouse (single
  diamonds; double black), Sheephorn - Escape (a circle; blue); Wapiti prints a diamond by its name and squares on
  its line (`RATING`: black, as the report).
- **Decisions:** 42 pieces settled on crops (`decisions.py`, by points: the continuation of a run past a catwalk,
  links to the next run, Centennial's parts), 3 cuts where one skiway carries two runs (Highlands and Charter
  Skiways, Upper and Lower Stirrup, Maverick and Second Chance, at the second's circle), 10 pieces no trail (links
  with no name, a stub by a glade's diamond, the brown mark by a kids' zone). `NO_STRETCH` for names printed beside
  their symbol, not in a gap of their line (Maverick, Solitaire, Charter Skiway, Tall Timber, Roughlock, one of
  Leav the Beav's two labels: a `(name, (x, y))` entry, new with this map). Markers: the parks, the kids' zones,
  glades and chutes printed with no line.
- **Checked:** every overlay on crops (`overlay_audit.py`, 42 sheets, every cell read; Centennial's parts, the
  stretches beside their symbols and Middle Golden Eagle's two branches fixed and read again); `compare.py` against
  the report; hover 462/464 (the two misses where Piney's and Powell's lines meet and run on together below the
  Cinch catwalk: either name is right); the app check.

## Big Bear

93 trails (91 + 2) · California · three panels, one per mountain: Snow Summit, Bear Mountain, Snow Valley (the
report's three areas too) · `tools/trailmap/resorts/big-bear/`.

- **Source:** bigbearmountainresort.com's trail-maps page links the 2025-26 maps as images only (plain curl): Snow
  Summit 2500x1859, Bear Mountain 2500x1770, Snow Valley 1965x2400 (a PNG), James Niehues's paintings. No PDF
  anywhere. The CDN (Imperva) answers one request for Snow Summit's with its own WebP and the next with the origin's
  JPEG: `regen.sh` fetches again until the WebP the data was built from comes (both are the same painting). Snow
  Summit's print **draws each run's line** (blue, green, black; lifts red); Bear Mountain's and Snow Valley's paint
  the runs as slopes with **no line**, the name and symbol printed by each. The resort's interactive maps
  (resorts-interactive.com maps 1818, 1808, 1825) draw the same paintings, each run's symbols and a line in a group
  named after it, but not the names' letters; the lines are an older drawing (Snow Summit's lie up to 25 px off its
  print's), and Snow Valley's map is an older edition (some symbols and lines differ from the print's; it adds the summit
  drawn bigger in an inset). All six SHA-256s are
  checked.
- **Route:** `prepare.py`, per panel: each SVG registered on its print (`register_pages.py --ref` on the SVG's
  painting: 1753 inliers, 0.25 px; 1951, 0.22 px; 1963, 0.19 px; `VICOMAP_AFFINE` in each panel's `resort.py`); per
  group its fills shaped like a symbol at the panel's size (a square, a diamond, two side by side a double, a
  circle), with a label at each (the name is printed by its symbol). Snow Summit's lines are the print's own: colour
  masks per class, `raster_lines.py`'s `clean()` (text, symbols, icons out, the legend and the sky excluded) and
  skeleton pieces through junctions; the black mask takes in the painting's dark trees, so a black component is kept
  only if it is long and thin (60 px or more end to end, under 7 px wide, its skeleton no more than three times its
  span: a crown's is tangled) and lies near an interactive-map black line (`lines_only()`). They are named by the
  symbol at each run's top (`MATCH_ENDS`, `SYMBOL_REACH` 6 px). Bear Mountain's and Snow Valley's lines are the
  groups' as they are (Mammoth's way); a run in no group (Bear Mountain's Learning Curve, the Park Runs, Expressway,
  The Gulch, the parks and pipes, Street Scene) has its label read on crops (`names.py`, first and last letter) and
  the stretch along it (`LABEL_LINE`). Snow Valley's names and symbols are all read on the print (`names.py`: its
  groups' symbols are the older edition's), and six runs whose line is a stub there (Bubble Gum, Lower and Upper Wine
  Rock, Quickie, Thunder Mountain, West Run) have the stretch along the name as well. Geronimo's double diamonds hold
  letters, so no group gives them: `names.py`. Two runs named Pipeline (Bear Mountain's blue, Snow Valley's black):
  `RENAME` per panel, `DISPLAY`, `AREA_OF`.
- **Rebuild:** `tools/trailmap/resorts/big-bear/regen.sh` (20 s).
- **Truth:** the trail report (`report.json`: the mtnpowder feed, mtnfeed path `big-bear-mountain`, resorts 57, 58
  and 173, fetched out of season: every run listed). Runs the report splits and the map draws as one line are one
  trail (Timber Ridge: one line, one square; Westridge Park: one line, its name printed three times). Ratings are
  the printed symbols; a run printed with two takes the report's (Miracle Mile (Upper): squares and a diamond,
  black; Side Chute and Olympic: diamonds and a double, double black); 7 Down's line is green, its symbols blue
  squares: blue. Printed and not in the report: Backdoors (Bear Mountain; in the interactive map too), Comeback Trail
  and Log Road (Snow Summit: a square each by the summit, no name or line, named by their groups: markers). In the
  report and not printed: Snow Valley's The Hideout. (`compare.py` lists Pipeline's rating as differing: it pairs
  the report's two Pipelines with one name; each panel's is right.)
- **Decisions:** Snow Summit's on crops (`panels/snow-summit/decisions.py`): 27 pieces checked (Timber Ridge, 7
  Down, Miracle Mile's Upper and Lower parts, the runs past a junction), 4 no trail (two trees, lift 6's hut icon), 2
  cuts, Off Chute's stretch traced. Bear Mountain: Easy Street (its three stretches would bridge across trees) and
  Outlaw's Alley (its symbol mid-label) traced. Snow Valley: the older map's Bubble Gum line where the print draws the
  cat track's red dashes is no trail; the Cat Track's waypoints on the dashes (`names.py`, `LINES`).
- **Checked:** every overlay on crops (`overlay_audit.py`, 9, 8 and 8 sheets, every cell read; Off Chute, Miracle
  Mile, Easy Street, Outlaw's Alley, The Gulch, the Cat Track, Bubble Gum and Snow Valley's six stubs fixed and read
  again); `compare.py` against the report; hover 95/95, 87/87, 93/93; the app check.

## Arapahoe Basin

148 trails (122 + 26) · Colorado · two panels: the Frontside & The Beavers, and Zuma Bowl · areas: the report's
terrain areas (Front Side, Pallavicini, The Beavers, Montezuma Bowl, Steep Gullies, East Wall, Molly Hogan) ·
`tools/trailmap/resorts/arapahoe-basin/`.

- **Source:** the 2025-26 winter trail map PDF arapahoebasin.com's trail-maps page links ("a basin map 2025.pdf",
  plain curl; it redirects to the site's CDN): one page, VistaMap's artwork, two paintings (5460x3617 and 3093x2616,
  about 4.2 px/pt) under one vector layer, the Frontside below and Zuma Bowl in a frame at the top right. Each is a
  panel, rendered at 3.5 px/pt over its clip (no matte: the paintings are sharp enough). Lines: strokes in black,
  blue (two shades) and green, 0.5 pt on the Frontside and 0.75 pt in Zuma, for the groomed and gladed runs, the
  traverses and the Steep Gullies; Grand Portage, a skiing traverse, 1.5 pt black dashes on a white casing; the hiking
  routes (black lines with arrowheads and hiker icons), the hike-back trails and the summer activities' outlines are
  thin black strokes too, settled as no trail. **Most runs have no line**: the open faces, chutes, gullies, glades
  and woods are a name printed down the slope from its symbol. Names: outlined near-black glyphs on a white halo (no
  text at all), read once on nine contact sheets (`letters.json`, 188 shapes). Symbols: fills with rounded corners,
  diamonds 4.8 pt and 6.1 pt (Zuma), squares 4 to 6, circles 5 to 7; the EX double diamond is one outline with the
  white E and X cut out (`pdf_symbols.py --rounded --max-square 8 --max-diamond 6.5`, fills under 3.5 pt left out).
- **Route:** `prepare.py`: the glyphs collected and decoded for the whole page (`pdf_glyphs.py labels`), each panel
  taking those inside its clip; strokes 0.45 to 0.8 pt (`extract_pdf_vectors.py`), then the 1.5 pt dashes
  (`--append`); the legend and the Steep Gullies note excluded. `pdf_resort.py` per panel with `ALONG_FIRST`,
  `ALONG_NEAREST`, `NO_STRETCH_BESIDE`, `SYMBOL_CENTRE`, `SYMBOL_REACH` 12 pt. The runs with no line printed down the
  slope from their symbol get the stretch along the name (`LABEL_LINE`, 54 on the Frontside and 18 in Zuma); the
  names printed level (Land of the Giants, Lower East Wall, Pallavicini, Bald Spot, The Cellar), on two lines, or
  calling themselves chutes, glades, woods or trees with no line are markers. CHISHOLM, printed three times, is
  Upper Chisholm Trail by the lodge and Lower Chisholm Trail below (`RENAME_AT`). The summer, base-area, deck,
  elevation and area-title labels are dropped.
- **Rebuild:** `tools/trailmap/resorts/arapahoe-basin/regen.sh` (10 s); it checks the PDF's SHA-256.
- **Truth:** the trail report (`report.json`: the snow report page's Terrain & Lift Status, server-rendered, every
  run under its terrain area, lift and zone; `status_report.py`, fetched 2026-10-10 out of season; the carpet and
  uphill-access rows left out). It rates almost nothing (a handful of icons), so the ratings are the map's symbols.
  Names as the report spells them: 1st Alley - David's Run for DAVID'S RUN, 4th Alley (West Alley), TB Glades for TB
  GLADE, Davo's Glade for DAVOS GLADE. Elephant's Trunk, printed once, is one trail (the report's Upper and Lower).
  The Steep Gullies (SG 1 to 5) print no symbol: the area's EX ("EX ONLY" in its note), double black; East Wall
  Traverse and Grand Portage, printed with none, black by their lines (`DEFAULT_SYMBOL`). Printed but not in the
  report: The Landing Strip, Cabin Glades, Pallavicini, Pali Cornice, Lower East Wall, East Wall Traverse (`AREA_OF`).
  In the report and not printed: Below the Traverse, Black Forest, Davo. Areas' elevations: each one's lift top from
  the resort's 2025 Master Development Plan (Table 1: Lenawee Express 12,465 ft, Pallavicini 12,115, Beavers 12,458,
  Zuma 12,475, Molly Hogan 10,870), the East Wall's the summit as printed (13,050 ft).
- **Decisions** (every piece settled on crops): the five Steep Gullies' lines by their SG labels beside them (SG 2's
  in two pieces), Ramrod's line on below the Aerial Adventure Park, Ned's Cache's line on from Gentling's foot, Zuma
  Cornice's line west along the ridge; Elephant's Trunk's stretch traced (printed on two lines). Not trails: the Via
  Ferrata's and the Aerial Adventure Park's outlines, four hiking routes, the two hike-back trails, and the blue link
  from the Pallavicini top to West Wall and Davis (no name printed).
- **Checked:** every overlay on crops (`overlay_audit.py`, 13 and 4 sheets, every cell read); every diamond and EX
  on `symbol_audit.py --mode diamonds`; `compare.py` against the report; hover 290/290 and 86/86; the app check;
  a rebuild from an empty work folder, byte for byte.

# Part 4. Methods in detail

## Getting a source here

Download the resort's trail-map PDF, not the web JPG, and look at what it holds (`pdf_inspect.py`). If it has text
and vector drawings, use them: exact names, positions and line geometry, no computer vision needed. If it is only
a raster, `extract_pdf_image.py map.pdf map.png` gives the lossless image: Killington's repo JPG was a resampled
4:2:0 copy (PSNR 20.6 dB against the PDF's raster), which blurs 2-4 px coloured lines and small text. Either way it
is worth asking the resort for the layered file (Killington's PDF metadata shows an Illustrator file, flattened).

In this sandbox:
- **Vail Resorts' sites** (vail.com, breckenridge.com, keystoneresort.com, ...) return an error page to curl. Open
  the trail-map page in headless Chromium through the agent proxy and fetch the PDF from inside the page (`fetch`
  in `page.evaluate`), or list the links and responses that mention pdf or map: `tools/trailmap/fetch_pdf.cjs` and
  `find_source.cjs` do this, and work out the pin themselves. By hand, Playwright's Chromium needs
  `proxy: { server: process.env.HTTPS_PROXY }` and `--ignore-certificate-errors-spki-list=<pin>`, where the pin is
  `openssl x509 -in /root/.ccr/agent-proxy-ca.crt -pubkey -noout | openssl pkey -pubin -outform der | openssl dgst -sha256 -binary | base64`.
  Load Playwright from `$(npm root -g)/playwright`.
- **Their image CDN (scene7) works with plain curl** and serves the full paintings losslessly:
  `https://scene7.vailresorts.com/is/image/vailresorts/<name>?req=imageprops` gives the size,
  `?fmt=png-alpha&wid=<width>&qlt=100` the image (byte for byte the same on a later download). Names seen:
  `20251028_KY_winter-trail_map_001` (Keystone), `20251001_VL_winter-{front-side,back-bowls,blue-sky}-trail_map_001`
  (Vail; the `-logos` copies add a header band). Find a resort's name in the image URLs of its trail-map page.
- **skimap.org** often has the PDF when the resort's own sits behind a bot check (Whiteface), and keeps past
  editions (`skimap.py`). Third-party "PDFs" can be just the rasters again (SnowStash's Vail PDF is the same three
  panels).
- **OpenStreetMap:** the main Overpass server resets connections from here; mirrors answer (`osm_check.py fetch`
  tries overpass.kumi.systems first).
- **Trail reports out of season:** a terrain-status feed lists no trails in October; Common Crawl's captures from
  the season have them (`tools/trailmap/reports/`).

## Raster line detection (Killington's detector)

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

## Naming pieces with parallel AI readers

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
  pass (the trace pass, below), ~5 trails per reader; example args
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

## Auto-accept the easy ones, trace the hard ones

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

## Naming the pieces yourself (no readers)

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
6. Rebuild, then run the crop audit (below).

Vail: 550 pieces, about a third matched automatically, the rest settled on
about 30 review tiles and many closer crops, plus 67 traced stretches.

## Auditing on crops, or the human review page

From Sugarbush on, every resort skipped the review page at the owner's call: the
readers' labelling had held up on three maps, and the PDF maps after it needed no
readers at all. In its place Claude checks every overlay itself:

1. `overlay_audit.py --resort <id> [--panel <p>] --out <dir>`: one cell per
   trail, its overlay thick over the map, the others thin, its printed labels
   boxed. Look at every cell: the overlay should run along the trail's own line
   from its name or symbol to where the line ends, and nowhere else.
   `region_audit.py` over the whole map (e.g. `--grid 5x3 --zoom 1.3`) shows
   lines with no overlay at all.
2. `symbol_audit.py --mode off` and `--mode ends` with the named symbols. It
   lists every symbol that lies off its trail's overlay or at one of its ends.
   Each is either fine (the run starts or ends at its symbol) or a missing
   stub or stretch. On Vail it found 33 gaps after the region audit had
   passed: a short stub doesn't show at 1.3x.
3. `symbol_audit.py --mode diamonds`: every diamond on one sheet with its name
   and type, for the single-vs-double check.
4. Anything unclear on `grid_crop.py`; fix it with a decision or a traced
   stretch, rebuild, and look again.
5. The hover check, per panel on a multi-panel map (below). After an app
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

## Symbols, unplaced trails, and a second search

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

## Human recheck

The reviewer opens the page; "Needs action" lists only the flagged trails,
each pre-filled with Claude's geometry. Killington: 8 trails, then 6.

## Registering, applying and verifying

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
4. Its search terms: the state or province, and `also` for other places it should be found by (a second
   state, the lake: Heavenly's `['Nevada', 'Lake Tahoe']`).
5. An ad group in `marketing/google-ads/build.mjs` (`RESORT_ADS`), then `npm run ads:build` (the build stops
   without one).

Then:

```bash
tools/trailmap/resorts/<id>/regen.sh                       # or: npm run trails:apply -- --resort <id>
npx tsc -b && npx eslint . && npm test
tools/trailmap/hover_all.sh <id>                           # builds into work/dist-check, serves it, hovers, stops it
npm run build && (node tools/serve_dist.cjs dist 4199 > work/serve.log 2>&1 &)   # its own subshell
PLAYWRIGHT_PATH=$(npm root -g)/playwright node tools/app_check.cjs http://localhost:4199/ --resort <id>
```

(Stop a server you started by its PID: `pkill -f` can kill the shell running it.)

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
`tools/trailmap/hover_all.sh` runs it for all of them; each should match its previous score (Part 3 has them).


## Several panels

A resort drawn on more than one map keeps one `trails.ts` and, per panel, `panels/<panel>/` with its own
`linePolylines`, `trailProposals`, `trailReviews` and `trailPaths`; the map is `public/maps/<resort>-<panel>.jpg`.
`trails:apply`, `hover_check.cjs` and the other `resortPaths()` scripts take `--panel <id>`; `pdf_resort.py` reads
every panel of a resort whose `resort.py` lists them (`PANELS`) and writes one trail list. The areas (`peaks`) are
the panels themselves where the panels are the resort's areas (Vail: give each trail its panel as its area), and
otherwise the resort's own areas (Whistler Blackcomb's mountains, Big Sky's three mountains, Heavenly's sides);
picking a trail in the list opens a panel that draws it. A trail's marker goes on the panel where its name is
printed, so `aggregate_readings.py` and `traces_to_reviews.py` get that panel's labels only, while
`seed_roster.py` gets all of them. A run drawn at the edge of another panel (Vail's Back Bowls roads along Blue
Sky's bottom edge) gets an overlay on both.

# Part 5. What we tried, and what it taught us

Seven attempts over six months on Killington, most on separate unmerged branches (the details in
`docs/killington.md`):

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
   Breckenridge, Copper Mountain and Keystone keep their own scripts (in their
   folders, rebuilt byte for byte), with decisions keyed by piece id; moving them
   onto `pdf_resort.py` would key them by points, which survive a re-export.
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
   Stowe (`aggregate_readings.py`, Part 4, "Auto-accept the easy ones"). Still open: also require the
   pieces' colour to match the printed symbol.
7. **Skip OCR** for new maps — done: the readers, and on PDF maps the text
   and glyphs themselves, superseded it.
8. **Reuse the review page** as a template artifact per resort, and ask the
   resort for vector sources — a layered PDF removes most of the extraction and naming (Part 1, steps 5-6).
