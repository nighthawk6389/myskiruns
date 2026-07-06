# Trail-LINE detection (v2)

The first detector (see `README.md`) finds the white *snow surface* of open
runs. That is not what identifies a **trail**: on this map every named trail is
traced by a colored **line** — green / blue / black strokes following the run,
including through forest — with markers (circles, squares, diamonds) riding on
the line and the trail name in black text alongside. Lifts are maroon lines
with black outlines, the resort boundary is yellow dots, highlight bands are
magenta: all of these must be rejected.

`scripts/lib/lineDetector.mjs` extracts those lines. Pipeline (following the
raster-map line-extraction literature — Chiang & Knoblock road-layer
extraction, Fletcher-Kasturi text/graphics separation, dashed-line endpoint
linking):

1. **Ink classification** (HSV, hysteresis core/grow per class) + per-column
   skyline exclusion. A green-cast guard keeps forest shadow out of "black".
2. **Sign-box removal**: integral-image local-fill — a 35×35 window that is
   ≥66% dark ink is a label-box interior (no line geometry can do that);
   punched with a halo and recorded as anchors.
3. **Lift-outline clearing**: black pixels hugging (≤5px) long maroon
   components are gondola/lift outlines. Compact red icons don't trigger this.
4. **Raw segment quality filters**: glyph size, thinness (area/diag),
   compactness (black only), core-ink minimum, stroke solidity.
   Small fragments survive as "weak": colored thin pieces and markers;
   black only straight fragments and solid diamonds.
5. **Directional endpoint linking**: fragments and segment ends march along
   their principal axis to reconnect gaps punched by markers, icons, park
   features and crossings. Black links additionally require collinearity with
   the strong ink at the far side (trail names run along their trails, so
   letters would otherwise stitch in) and must not run alongside lift ink.
6. **Bridged grouping** (3px) with per-class minimum extents, weak-chain and
   leader-line rules; then Zhang-Suen thinning + branch-aware spur pruning
   gives a 1px **centerline skeleton** per class.

## Validation criteria (v2)

The old point set measured snow-surface detection. For lines we use:

1. **Point precision/recall vs `groundTruthLines.json`** — 283 points
   (72 on-line positives across green/blue/black, 211 hard negatives
   including text glyphs, lift lines, boundary dots, sign boxes, roads,
   buildings, forest, sky). `npm run lines:eval`.
   *Labeling methodology matters*: candidates were sampled stratified by
   loose color classes (so hard negatives arrive naturally), every positive
   and borderline point was audited on zoomed contact sheets, and every
   suspect distance was re-measured on 4×-zoom crops with calibrated 4px/8px
   rings — that re-audit reclassified 14 points the low-zoom pass had gotten
   wrong. Prediction = detected centerline within 5px (positives sit ≤4px
   from the line center; negatives ≥6px; skeletons are width-independent).
2. **Class accuracy** — of detected positives, does the predicted color match
   the labeled difficulty class?
3. **Whole-map overlay audit** — `npm run lines:overlay` tints every detected
   line pixel; systematic errors (sky, lifts, text) are obvious at a glance
   in a way 283 points can never be. `npm run lines:png` produces the app's
   overlay (toggle 〰 in the image view).
4. **Failure forensics** — `--why` traces every miss to the pipeline stage
   that dropped it; every fix in the detector's history corresponds to a
   named mechanism, not threshold luck.

## Results

Scorecard on the 283-point ground truth (72 positives / 211 negatives):

| metric | value |
|---|---|
| precision | **98.6%** (1 FP) |
| recall | **95.8%** (3 FN) |
| F1 | 97.2% |
| class accuracy on detected positives | 97.1% |
| per-class recall | green 29/29 · blue 23/24 · black 17/19 |

The journey: the first naive color-threshold detector scored 69% precision /
78% recall. Every improvement is attributable to a named mechanism (hysteresis
cores, box slab removal, lift-outline clearing, glyph/solidity filters,
directional endpoint linking, marker punch-out, shadowed-blue recovery...) —
see the git history of `scripts/lib/lineDetector.mjs`.

Remaining known failures (all understood, all boundary cases): one FP where a
trail-end flare merges with a lift-end blob; one FN on a square marker's edge;
two FNs where the line ink is literally absent under forest texture
(chromatically identical to shadow — verified by pixel transects).

Consumers:
- `npm run lines:png` → `public/trail-lines.png`, the app's 〰 overlay.
- `npm run lines:place` → `src/data/trailPositions.json`: hotspots placed ON
  detected lines whose color matches each trail's difficulty, spread by
  farthest-point sampling, hardest-highest within each peak region.

## Data-quality findings (why trails "weren't labeled")

Line detection also exposed that the *data file*, not just the placement, was
wrong:

- **29+ named trails visible on the map are missing from `data/trails.ts`**,
  e.g. Killink, Frolic, Bearly, Nivis Walk, Ridgeview, Skyewalker, Gateway,
  Skyehawk, Homerun, High Traverse, Thimble, Low Rider, Racer's Edge,
  Spillway, Juanita, Launchpad, Jug Handle, The Jug, Escape, Powerline,
  Ridge Run, Sassafras, Full House, Helter Skelter, Blue Heaven, The Throne,
  South Ridge Link…
- At least one difficulty mismatch: Field Goal is drawn as a green line on
  the map but listed blue in `trails.ts`.

Fixing the roster/difficulties (or OCR-ing the map's labels with
tesseract.js — horizontal labels read at ~90% confidence in testing, angled
ones need counter-rotation) is the natural next step toward per-name
placement.
