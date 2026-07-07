# myskiruns — Killington Trail Tracker

A React + TypeScript app for tracking which Killington trails you've skied,
with hotspots overlaid on the actual resort trail map. The interesting part of
this repo is the **computer-vision pipeline** that reads the trail map image:
it detects the colored trail lines, OCRs the trail-name labels, audits the
trail roster, and places every hotspot on the correct line.

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
`scripts/extractLabels.mjs` OCRs the rotated trail-name labels (103 labels,
mean confidence 90.4). `scripts/reconcileTrails.mjs` matches them to the
roster: 54 trails gained name anchors; **11 trails that were missing from
`src/data/trails.ts` were added** (Blue Heaven, Helter Skelter, Full House,
Frolic, The Jug, Shorty, Bearly, Killink, Gateway, Highlander, Sassafras) and
Field Goal's difficulty was corrected to green — fixing "trails aren't
labeled / labeled incorrectly" at the data source.

### 4. Detection-driven app assets
- `public/trail-lines.png` — difficulty-colored line overlay (〰 toggle).
- `src/data/trailPositions.json` — hotspot positions: 40 name-anchored at
  their OCR'd label, the rest spread over color-matched lines per peak.

### Scripts

| command | purpose |
|---|---|
| `npm run lines:eval` | precision/recall vs line ground truth (`--why` for forensics) |
| `npm run lines:overlay` | whole-map detection overlay render |
| `npm run lines:png` | regenerate the app's line overlay |
| `npm run lines:place` | regenerate hotspot positions (`--render` audit image) |
| `npm run detect:eval` / `detect:overlay` / `detect:place` | v1 surface-detector equivalents |
| `node scripts/extractLabels.mjs` | OCR the map labels |
| `node scripts/reconcileTrails.mjs [--apply]` | match labels to roster, propose missing trails |

## What's left

- **Full per-name placement**: 40/130 hotspots are name-anchored; the rest
  are on correct-color lines but not necessarily the named trail. A second
  OCR pass (per-block contrast tuning, inverted pass for white-on-maroon lift
  labels) could anchor most of the remainder (Juanita, Julio, etc.).
- **Snap disambiguation**: between close parallel same-color lines the anchor
  snap can pick the neighbour (~25px), e.g. Killink vs Royal Flush.
- **Line tracing to polylines**: the skeleton could be vectorized into named
  polyline paths (skeleton graph → junction resolution), enabling clickable
  trail *paths* instead of point hotspots and exact per-name assignment.
- **Roster completeness**: ~60 low-confidence OCR labels were discarded;
  some map trails may still be missing from the roster.
- **Known detector edge cases** (3 FN / 1 FP): two lines drawn under forest
  texture are chromatically undetectable; one trail-end flare merges with a
  lift-end blob. Documented in `src/detection/LINES.md`.
- **Schematic map view** still uses hand-drawn synthetic paths, untouched by
  detection.
