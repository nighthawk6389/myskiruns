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

## What was done

### 1. Snow-surface detection (v1)
`src/detection/trailDetector.ts` classifies the white groomed-run surface
(bright, neutral pixels with ridge-based sky suppression). Evaluated against
58 hand-labeled points: F1 92.7%. Powers the ⛷ overlay toggle.
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
- `public/trail-lines.png` — difficulty-colored line overlay (〰 toggle).
- `src/data/trailPositions.json` — dot positions, now used only for trails
  without a traced path (`npm run lines:place` owns this file; the v1
  `detect:place` writes to `/tmp/explore/` so it can't clobber it).

### 5. Clickable trail paths
- `scripts/tracePolylines.mjs` vectorizes the detection skeletons into 393
  polylines (skeleton graph, junction resolution by straightest continuation,
  Douglas-Peucker).
- `scripts/enrichAnchors.mjs` second-pass OCR with dictionary-constrained
  matching grew name anchors to 76/130 trails.
- `scripts/assignTrailPaths.mjs` assigns polylines to trails: nearest-first
  label→line matching with baseline-angle agreement and chain stitching.
  Output: 127/130 trails get a path — **71 claimed via their own name label
  (`source: anchor`), 56 guessed by a region/color heuristic
  (`source: region`)**.
- The app renders each path as a clickable polyline (hover = name, click =
  toggle skied).

## Scripts

| command | purpose |
|---|---|
| `npm run lines:eval` | precision/recall vs line ground truth (`--why` for forensics) |
| `npm run lines:overlay` | whole-map detection overlay render |
| `npm run lines:png` | regenerate the app's line overlay |
| `npm run lines:place` | regenerate hotspot positions (`--render` audit image) |
| `npm run detect:eval` / `detect:overlay` / `detect:place` | v1 surface-detector equivalents |
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

**Status after the first full review (Sept 27 2026)** — all 166 decisions made:

| decision | trails | in the app |
|---|---|---|
| confirmed line (tapped pieces and/or hand-drawn) | 110 | clickable along the whole line |
| no drawn line (glades) | 22 | clickable marker at the label (20; 2 have no known label position) |
| not on this map | 13 | list only |
| skipped | 21 | list only (mostly upper/lower variants and liftlines) |

36 trails printed on the map were added to `trails.ts` (roster now 166).
Browser check: hovering 3 points along each of the 110 lines shows the right
name at 304/330 points; every miss is within 16px of another trail's line
(junctions, crossings, tight parallels), where either name is defensible.

Still open: the reviewer set no difficulty overrides, so roster colors that
differ from the drawn line (Breakaway, Catwalk, Needle's Eye, Low Road, Bear
View, …) are unchanged; skipped upper/lower variants need a decision on how to
split one drawn line into two trails; new trails' peak grouping comes from
`peakRegions.ts` and double-black vs black was not distinguished.

To re-export after more review: read the page's `reviews` collection, write
it to `src/data/trailReviews.json` (the page still uses `new-…` ids for the 36
added trails; strip the prefix and the `-s-` possessive, e.g.
`new-racer-s-edge` → `racers-edge`), then `npm run trails:apply`.

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
5. Known detector edge cases (3 FN / 1 FP) in `src/detection/LINES.md`;
   schematic view still uses synthetic paths.

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
