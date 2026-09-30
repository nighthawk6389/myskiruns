# Trail map playbook: from a resort map image to clickable, named trails

This is the process that turned the Killington 2025-26 trail map into 135
clickable trails with the right names and difficulties, written so it can be
repeated (and sped up) for other resorts. It records what worked, what didn't,
and what each step cost.

**Goal (definition of done):** every trail in the resort's trail list has an
overlay that lies on that trail's own drawn line along its full length, or a
marker at its label if it has no drawn line (many glades); tapping anywhere on
it shows that trail's name; its difficulty matches the symbol printed on the
map; and the list contains exactly the trails printed on this season's map.

## The short version

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

## Tools in this repo

| file | what it does |
|---|---|
| `tools/trailmap/extract_pdf_image.py` | Lossless raster from the resort PDF; reports any vector text/lines |
| `tools/trailmap/extract_pdf_vectors.py` | Map image + numbered pieces straight from a PDF's vector trail strokes |
| `tools/trailmap/pdf_symbols.py` | Difficulty symbols from a vector PDF; `--check` compares them with the trail list |
| `scripts/lib/lineDetector.mjs`, `scripts/evaluateLines.mjs` | Colored-line detector and its ground-truth scorer |
| `scripts/tracePolylines.mjs` | Detection mask → numbered line pieces (`src/data/resorts/killington/linePolylines.json`) |
| `tools/trailmap/render_tiles.py` | Zoomed tiles with every piece drawn and numbered, for the readers |
| `tools/trailmap/prompts/*.md` | Reader prompts: name pieces, symbols + missing, whole-map search |
| `tools/trailmap/aggregate_readings.py` | Readers' votes → per-trail proposals + review-page data |
| `tools/trailmap/review/index.html` | The review page (Claude artifact with a database) |
| `tools/trailmap/refresh_review_data.py` | Rebuild page data after fixes; flag trails for recheck |
| `scripts/importReviews.mjs` (`npm run reviews:import`) | Review-page export → `src/data/resorts/killington/trailReviews.json` |
| `scripts/applyTrailProposals.mjs` (`npm run trails:apply`) | Reviews + proposals → `src/data/resorts/killington/trailPaths.json` (what the app draws) |
| `tools/trailmap/render_crops.py` | Zoomed crops of overlays for audits and split checks |
| `tools/trailmap/region_audit.py` | Every overlay tagged with its name over map regions, to audit a whole map |
| `tools/trailmap/hover_check.cjs` | Browser check that each overlay shows its own name |

Python tools need `pip install pymupdf pillow`; the hover check needs
Playwright.

## Step by step

### 1. Source image

Download the resort's trail map PDF (not the web JPG) and run
`extract_pdf_image.py map.pdf map.png`.

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

### 4. Human review

Sugarbush and Jay Peak skipped this step at the owner's call (the readers'
labelling had held up on three maps). In its place Claude checked every
overlay itself: vector maps on full-resolution region crops with each
overlay drawn in its own colour and tagged with its name
(`region_audit.py`), traced trails one by one on zoomed crops,
and every diamond on a crop; then the hover check. Keep the review page for
maps where the readers disagree or the lines are raster-detected.

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
just short of another piece is extended to touch it; remaining gaps up to
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

```bash
npm run reviews:import -- <export dir> && npm run trails:apply
npx tsc -b && npx eslint . && npm run build
npx vite preview --port 4199 &
node tools/trailmap/hover_check.cjs http://localhost:4199/ --resort <id>
```

The hover check hovers 3 points along every line and each glade marker in the
real app. The map names the NEAREST trail to the pointer (the same test a tap
uses), not whichever trail is drawn on top: that took Killington from
344/361 to 359/361 and Stowe from 343/353 to 351/353. The remaining misses
are stretches two trails genuinely share (Great Eastern / Home Stretch,
Jake's Ride / Crossover), where either name is right. It checks rendering against the reviewed geometry — it is not
evidence the geometry is right (only the review is).

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
  pattern also appears later in the same command line.

## Scaling to many maps

In rough order of payoff:

1. **One data folder per resort** — done: `src/data/resorts/<id>/`
   (`trails.ts`, `linePolylines.json`, `trailProposals.json`,
   `trailReviews.json`, `trailPaths.json`), map at `public/maps/<id>.jpg`,
   registered in `src/resorts.ts`. `tracePolylines`, `trails:apply`,
   `reviews:import` and `hover_check.cjs` take `--resort <id>`; the image
   size comes from the map file. Still to do: a `legend.json` per map.
2. **A per-map legend file** (trail colors, lift color, boundary, highlight
   bands, symbols, text styles) feeding both the detector's color gates and
   the reader prompts.
3. **Run the readers from a script** (`ANTHROPIC_API_KEY` + the prompt
   templates, images attached) instead of an interactive Claude session, so a
   new map is one command. Keep the vote aggregation as is.
4. **Start the trail list from the map, not from memory.** Seed it from the
   readers' printed names and symbols (steps 3 and 5 already produce both),
   then have the human confirm; most of Killington's list corrections came
   from a list written before looking at the map.
5. **Auto-accept only unanimous, high-confidence proposals** whose piece
   colors match the printed symbol, and send the rest to review; measure on
   Killington's reviewed data first (it's ground truth now) to pick the
   threshold.
6. **Skip OCR** for new maps; the readers superseded it.
7. **Reuse the review page** as a template artifact per resort, and ask the
   resort for vector sources — a layered PDF removes steps 2–3 entirely.
