# Trail detection

This module finds the **white/groomed snow trail surface** (open ski runs) on the
Killington trail-map image and provides a way to *measure* how well it does.

The same detection code runs in two places:

- **The app** — `useTrailDetection` paints a cyan overlay of detected runs on the
  image map (toggle the ⛷ button in the image view).
- **The evaluation harness** — `scripts/evaluate.ts` scores the detector against
  hand-labelled ground truth.

## How to tell if it's working

There are two complementary checks. Run them from the repo root.

```bash
npm run detect:eval      # precision / recall / F1 against ground-truth points
npm run detect:overlay   # render the mask over the whole map -> /tmp/explore/overlay.jpg
npm run detect:sweep     # grid-search detector params, report the best
```

1. **Quantitative** — `detect:eval` samples the detector at 58 hand-labelled
   points (`groundTruth.json`) and reports a confusion matrix plus
   precision / recall / F1. This catches regressions objectively.
2. **Qualitative** — `detect:overlay` tints every detected pixel red on a
   downscaled copy of the map. Because it covers the *whole* image (not just the
   labelled points) it's the fastest way to spot systematic errors — e.g. the
   sky or a road lighting up.

Use both: the points keep you honest, the overlay shows you *where* you're wrong.

### Current scores

| metric    | value |
|-----------|-------|
| precision | 86.4% |
| recall    | 100%  |
| F1        | 92.7% |

The 3 remaining false positives are all base-area **buildings**, which render as
neutral white and are genuinely indistinguishable from snow by colour alone
(see *Limitations*).

## The algorithm

Ski runs on this map are bright, near-neutral (low-saturation) snow carved
through dark-green forest. The detector (`trailDetector.ts`) classifies a pixel
as trail when all hold:

- `value ≥ valueMin` — bright (snow is light)
- `saturation ≤ saturationMax` — near-neutral (snow isn't a vivid colour)
- `greenExcess ≤ greenExcessMax` — rejects forest
- `blueExcess ≤ blueExcessMax` — rejects sky/teal and deep blue shadow

Two structural steps handle things colour alone can't:

- **Sky suppression** (`computeSkyHeights`) — the horizon haze is bright and
  neutral, i.e. colour-identical to snow. But sky forms a bright band contiguous
  from the top edge, ending at the dark forest ridge. We scan each column down to
  the first run of dark pixels and treat everything above as sky.
- **Neighborhood sampling** (`sampleTrailAt`) — runs are narrow corridors
  overlaid with coloured lift lines, so a single pixel often lands on a line or a
  forest gap. We instead ask whether ≥30% of a small window is trail-coloured.

## Ground truth (`groundTruth.json`)

58 points (19 trail / 39 off), normalized to `[0,1]` over the full image.
Built by overlaying a labelling grid, classifying each cell by eye against an
explicit policy (`_policy` field), dropping ambiguous cells, snapping the
positives onto the run surface, and visually auditing the result. Negatives
deliberately include the hard cases: forest, sky, background mountains, roads,
parking, and white base buildings.

## How to iterate

1. Change `DEFAULT_PARAMS` (or run `detect:sweep` to search).
2. `npm run detect:eval` — did precision/recall move?
3. `npm run detect:overlay` and look — did anything new light up or drop out?
4. To grow/curate the test set, edit `groundTruth.json` and re-audit with the
   overlay (it draws every ground-truth point: green = trail, blue = off).

Beware overfitting: 58 points is small, so favour simple, well-motivated
thresholds and always confirm changes on the whole-image overlay.

## Limitations / next steps

- **Buildings** at the base are neutral white and pass the colour test. Telling
  them from snow needs a non-colour cue (texture, sharp rectangular edges, or
  the fact that runs are bordered by forest). This is the main precision ceiling.
- The detector finds trail *surface*, not the thin forest-embedded trail lines
  drawn purely as coloured strokes — those would need separate line detection.
- Output is a pixel mask, not named runs. Associating detected pixels with the
  named trails in `data/trails.ts` (so the app's hotspots are placed by detection
  rather than the current synthetic grid) is the natural next step.
