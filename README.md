# myskiruns — Killington Trail Tracker

A React + TypeScript app for tracking which Killington trails you've skied,
with hotspots overlaid on the actual resort trail map. The interesting part of
this repo is the **computer-vision pipeline** that reads the trail map image:
it detects the colored trail lines, OCRs the trail-name labels, audits the
trail roster, and turns trails into clickable paths. Line detection is solid;
assigning the right *name* to each line is not solved yet — see
"Honest end-to-end status" below.

## Running

```bash
npm install
npm run dev        # app at localhost:5173
npm run build      # typecheck + production build
```

**Doing this for another resort?** Follow
[`docs/trail-map-playbook.md`](docs/trail-map-playbook.md): the full workflow
(source image → line detection → AI tile reading → human review → symbols and
missing-trail search → apply and verify), the tools in `tools/trailmap/`, what
each iteration taught us, and how to scale it to many maps.

## Using the app

- **Trips.** What you ski is logged per trip ("Presidents Day weekend").
  Pick or start a trip in the header; mark a trail skied on the current
  trip from the map, or with its check box in the list. With no trip yet,
  the first mark starts one for today. Stats show this trip and all trips;
  trails skied on an earlier trip are drawn dashed and say "skied before"
  in the list.
- **Finding a trail:** search the list and tap a trail's name; the map
  zooms to it, highlights it and opens its sheet.
- **On the map:** drag to pan, pinch or scroll to zoom (the corners button
  shows the whole map; phones open zoomed to fill the screen). Tap a
  trail and a sheet lists every trail within a finger's width, nearest
  first, each with a big "Skied it" / "Remove" button, so junctions and dense
  areas are never guessed; a toast offers Undo. Lines and markers keep a
  constant on-screen size at every zoom and are thinner on small screens.
- **Trail conditions (👍 / 👎).** In a trail's sheet, rate today's conditions;
  tap the same thumb again to take it back. Votes count for 24 hours. The
  list opens with "Good conditions today" (best net votes first) and rows
  show a 👍/👎 badge. Votes are shared with everyone through
  `api/conditions.ts`, a Vercel function backed by a Redis hash (Upstash,
  added from the Vercel Marketplace; it sets `KV_REST_API_URL` /
  `KV_REST_API_TOKEN`). Until that's connected the endpoint answers 503 and
  the app keeps votes on the device (the sheet says so). Each device sends a
  random id so it has one vote per trail; nothing identifies the person.
  `vite` / `vite preview` serve the same API from memory for local testing.
- **Condition tags.** After voting, pick up to three tags for what the trail
  is like (groomed, powder, soft, moguls, hardpack, icy, slushy, thin cover,
  crowded; list in `src/conditionTags.ts`). The sheet shows the most-reported
  tags, and "Good conditions today" shows each trail's top tag. Tags are
  stored with the vote, in the same 24-hour window.
- **Trip summary.** "Summary" in the stats panel (or ⋯ → Trip summary) shows
  trails skied, trails new to you (not logged on an earlier trip), days,
  the difficulty mix and toughest trails, progress by peak, and a
  day-by-day log with times; tap a run to see it on the map. "Share summary"
  uses the phone's share sheet, or copies a text recap.
- **Works offline and installs to the home screen.** A service worker
  (`public/sw.js`, production builds only) caches the app and the trail map,
  so it opens without signal on the mountain; on a phone use "Add to Home
  Screen". On narrow screens the progress and trail list sit below the map
  and scroll together, with the search box pinned.
- **Your trips stay on this device** (browser `localStorage`, key
  `myskiruns.trips`). Use ⋯ → Export backup / Import backup to move or keep
  it; importing adds trips that aren't already on the device. Data from the
  pre-trips version is carried into a trip called "Earlier runs".

## What was done

### 1. Snow-surface detection (v1)
`src/detection/trailDetector.ts` classifies the white groomed-run surface
(bright, neutral pixels with ridge-based sky suppression). Evaluated against
58 hand-labeled points: F1 92.7%. Kept as a reference; no longer used by the app.
Docs: `src/detection/README.md`.

### 2. Trail-LINE detection (v2 — the real trail identifier)
Each named trail on the map is traced by a colored line (green/blue/black).
`scripts/lib/lineDetector.mjs` extracts those lines at full resolution:
hysteresis ink classification, sign-box slab removal, lift-outline clearing,
text/graphics separation, directional endpoint linking across marker/icon
gaps, and per-class centerline skeletons.

**Validated at 98.6% precision / 95.8% recall** (F1 97.2) against a 283-point
audited ground truth (`src/detection/groundTruthLines.json`) with per-class
recall green 29/29, blue 23/24, black 17/19. Docs and methodology:
`src/detection/LINES.md`.

### 3. Label OCR + roster reconciliation
`scripts/extractLabels.mjs` OCRs the rotated trail-name labels (103 labels
in pass 1, 125 after the verified pass 2). `scripts/reconcileTrails.mjs` matches them to the
roster: 54 trails gained name anchors; **11 trails that were missing from
`src/data/trails.ts` were added** (Blue Heaven, Helter Skelter, Full House,
Frolic, The Jug, Shorty, Bearly, Killink, Gateway, Highlander, Sassafras) and
Field Goal's difficulty was corrected to green — fixing "trails aren't
labeled / labeled incorrectly" at the data source.

### 4. Detection-driven app assets
- `public/trail-lines.png` — difficulty-colored line overlay (〰 toggle,
  shown only with `?lines` in the URL).

### 5. Clickable trail paths
- `scripts/tracePolylines.mjs` vectorizes the detection skeletons into 393
  polylines (skeleton graph, junction resolution by straightest continuation,
  Douglas-Peucker).
- `scripts/enrichAnchors.mjs` second-pass OCR with dictionary-constrained
  matching grew name anchors to 76/130 trails.
- A first fully automatic assigner (nearest-first label→line matching;
  removed, see git history) placed only ~40% of trails correctly — see the
  audit below. Paths now come from the propose-then-review workflow.
- The app renders each path as a clickable polyline (hover = name, click =
  toggle skied).

## Scripts

| command | purpose |
|---|---|
| `npm run lines:eval` | precision/recall vs line ground truth (`--why` for forensics) |
| `npm run lines:overlay` | whole-map detection overlay render |
| `npm run lines:png` | regenerate the app's line overlay |
| `npm run detect:eval` / `detect:overlay` | v1 surface-detector equivalents |
| `node scripts/extractLabels.mjs` | OCR the map labels |
| `node scripts/reconcileTrails.mjs [--apply]` | match labels to roster, propose missing trails |

## Current approach: propose, then human review (Sept 2026)

Fully automatic name→line assignment reached only ~40% (audit below), so
naming is now done in two steps:

1. **Propose.** The map is cut into 37 overlapping tiles at 1.7× zoom with
   every detected line piece numbered. Six readers (Claude sub-agents, in
   parallel) named each piece from the labels printed along it and its
   continuity through junctions, or marked it lift / not-a-trail / unknown,
   and listed labels whose line was not detected. Result:
   `src/data/trailProposals.json` — 82 trails at high confidence; 57 pieces
   flagged as not trails (building outlines, icons, text); 92% of the real
   trail-line length now carries a name (was 53%).
2. **Review.** The *Killington Trail Check* page shows each trail's proposed
   lines on the map; a person confirms, taps lines to add/remove, draws lines
   the detector missed, or marks "no line" / "not on this map". Decisions are
   exported to `src/data/trailReviews.json`.

`npm run trails:apply` merges both into `src/data/trailPaths.json`: reviews
win, unreviewed trails use high/medium proposals, and trails with neither get
**no overlay** (no more guessed dots).

**Status (Sept 28 2026, after review + map-evidence cleanup)** — every trail
in `trails.ts` (135) has an overlay: 113 clickable lines, 22 glade markers at
their printed label.

What changed after the review, all from evidence printed on the map:
- **Difficulties** follow the symbol printed at each trail (circle / square /
  diamond / double diamond), read by six sub-agents over the tiles and each
  change checked on a zoomed crop: 34 changes plus Low Road (blue line, no
  symbol). Trails whose symbol changes along the way (Great Northern, Ridge
  Run, Royal Flush, The Jug) and Skye Hawk (symbol and line disagree) keep
  their listed difficulty.
- **Splits:** the map prints SKYELARK and EAST FALL twice (upper blue, lower
  black); the upper sections are Upper Skyelark / Upper East Fall.
- **Glades found:** Treezy and Lil' Stash are printed as labels with no line.
- **Duplicates merged:** Header and Skyeburst each appeared twice.
- **Removed (29):** entries not printed anywhere on this map. Two independent
  multi-agent searches (six agents by map area, then four agents each
  scanning the whole map for 8 names) and the reviewer found no label for:
  Snow Play, Swirl, Ramshead Run, Ramshead Liftline, Start Park, Upper FIS, Mountain Run, Mountain Training Station, Snowdon Liftline, Upper Snowdon, Lower Snowdon, Sass, Upper Northbrook, Snowdon Glades, Upper Catwalk, Juggernaut, Upper Great Bear, Woodward Peace Park, Great Eastern (K.P.), Lower FIS, K-1 Gondola Run, Upper Canyon, Lower Canyon, Killington Liftline, Superstar Glade, The Mall, Falls Brook, Bear Mountain Liftline, Bear Run. They are in git history if any should come back.
- **Sections restored by the second search:** the map prints HOME STRETCH,
  SKYEBURST and WILDFIRE more than once, each section starting at its own
  difficulty marker, so Lower Home Stretch, Upper Skyeburst and Lower
  Wildfire are split out again.
- **Printed names:** Snowshed Slope, Snowshed Crossover, Northbrook Trail,
  Vertigo Headwall, Big Dipper, Skyehawk, Skye Bits, The Northway, North
  Star, Lil Stash (ids unchanged, so skied history is kept).
- Areas for the 36 trails added from the review come from their nearest
  original neighbours.

Changes made by Claude are marked `"by": "claude"` in `trailReviews.json`
and flagged "please recheck" on the review page, which now jumps to the next
trail that needs action (undecided, skipped, or flagged).
Browser check: 325/352 hover points show the right name; misses are all at
junctions/crossings.

To bring in more review work: export the page's `reviews` collection to a
folder of JSON files (one per trail), then
`npm run reviews:import -- <folder>` (maps the page's `new-…` ids, keeps the
newer decision, ignores trails no longer listed) and `npm run trails:apply`.

### Earlier audit of the fully automatic assignment

The detector scores (97% F1) measure *line pixels*, not *named trails*. The
real goal — every trail drawn on its own line, clickable, with the right
name — was audited directly on zoomed crops of a random sample:

| group | sampled | on the correct line | wrong line | can't verify |
|---|---|---|---|---|
| anchored (label-claimed) | 8 | 5 (4 of them only partially covered) | 3 | 0 |
| region heuristic | 10 | 0 | 6 | 4 |

- Anchored errors: roster difficulty wrong so the same-color preference picks
  a neighbouring line (Breakaway is drawn black, roster says blue); label
  sits between two lines and the neighbour wins (Bear Cub → Ridgeview's
  line); glades with no drawn line get forced onto one (Treezy).
- Region guesses mostly steal the *unlabeled continuation of another trail*
  (Snow Play → lower Great Northern, Lower Home Stretch → Bear Trax, Lower
  Northbrook → Caper, Start Park → Easy Street).
- Coverage: median assigned path is ~160px on a 4572px map (fragments between
  junctions), and only **53% of the detected trail-line length is clickable at
  all**.
- The earlier "26/30 hover" test was circular — it hovered on whatever path
  had been assigned, so a wrong line still passed. Don't use it as evidence.

Realistic estimate: roughly 40% of trails are on the right line, most only
partially. Treat `source: region` paths as unverified guesses.

## Prior attempts (other branches — none merged to `main`)

`main` has not moved since March 2026; every attempt below started from it.

| branch / PR | approach | outcome / lesson |
|---|---|---|
| `ski-trail-clickable-overlays` (#3) | sweepline tracing + Hungarian matching to label positions read *visually by AI agents* from crops | claimed 114/115 matched, but keyed pink/yellow as trail colors (those are highlight bands and boundary dots); tesseract got 2/114 |
| `ski-run-plotting-explanation` (#4), `improve-extraction-metrics` (#5), `heuristic-cleanup-and-naming-refactor` | Python OpenCV: HSV + heuristic scoring + skeletons, text inpainting, SAM 2 click tool, Claude-Vision naming step | 90%+ on self-defined pixel metrics; naming step needs an API key and was never run; SAM 2 tool needs a desktop display; easyocr POC 17%. PR #4 notes "the recall metric itself was wrong" |
| `fix-trail-overlays`, `debug-trail-map-overlay` | hand-set coordinates / debug overlays | point fixes only |
| `fix-build-add-e2e-tests` | Playwright E2E tests for selection + overlay alignment | reusable |
| this branch (#6) | JS line detector, rotation-aware OCR, label-anchored assignment | best line detection and OCR so far; naming still ~40% (above) |

Common failure: each attempt optimized a proxy metric (pixels, coverage,
label count) that it defined itself, and none had a human-verified,
per-trail ground truth for the actual goal.

Note: `TrailMapForWeb-compressed.pdf` (commit `4d4a326`) is a flattened
raster (one JPEG-2000 image, authored in Illustrator, no vector layers). Its
image is sharper than `public/killington-trail-map.jpg`, which was resampled
and re-encoded with 4:2:0 chroma subsampling — prefer it as pipeline input.

## What's left

1. **Per-trail ground truth for the real goal**: for each of the 130 trails,
   its line (or "no line: glade/area"), human-verified. It is both the
   shipping data and the test set. Fastest route: a review mode that shows
   each proposed overlay for ✓/✗ and snaps a click to the detected polylines.
2. **Stop shipping region guesses** (or mark them unverified) and extend
   anchored trails along their own unlabeled continuations instead.
3. **Roster authority**: the map disagrees with `trails.ts` difficulties
   (Chute, Royal Flush, East Fall, Reason drawn blue; Bear View green;
   Breakaway black); ~18 map trails are still missing; some roster entries
   (Mountain Training Station, Snow Play, Start Park) may not be lines.
4. **Glades/parks** (14 roster entries) often have a marker + tree icon but
   no line — decide how they should be clickable.
5. Known detector edge cases (3 FN / 1 FP) in `src/detection/LINES.md`.
   (The synthetic schematic view was removed in the UI review.)

## Regenerating the data (order matters)

```bash
node scripts/extractLabels.mjs        # OCR -> labelAnchors.json (keeps pass-2 labels)
node scripts/enrichAnchors.mjs        # pass-2 proposals -> /tmp/explore2/enrich; then --commit <ids>
node scripts/reconcileTrails.mjs      # labels -> trailAnchors.json
node scripts/tracePolylines.mjs       # detection -> linePolylines.json
# naming: tiles + readers produce trailProposals.json; review page -> trailReviews.json
npm run trails:apply                  # -> trailPaths.json (what the app draws)
npm run lines:png                     # -> public/trail-lines.png
```
