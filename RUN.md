# Trail Extraction Pipeline - How to Run

This document explains how to run the CV pipeline that extracts ski trail paths from the Killington trail map image, step by step.

## Prerequisites

**Python 3.10+** is required. Install dependencies:

```bash
pip install -r scripts/requirements.txt
```

This installs: `opencv-python`, `numpy`, `scikit-image`, `Pillow`, `PyMuPDF`, `anthropic`, `matplotlib`.

**Optional (for SAM 2 refinement):**

```bash
pip install sam2 torch
```

Note: SAM 2 requires ~150MB model download. On CPU, the image embedding takes ~30s; each click-to-segment takes ~1-2s.

**Trail map source:** The pipeline needs either:
- `TrailMapForWeb-compressed.pdf` in the project root (best quality, 300 DPI render), OR
- `public/killington-trail-map.jpg` (fallback, lower resolution)

---

## Pipeline Overview

```
Step 1: PDF/JPG --> PNG image
Step 2: Color segmentation --> per-color binary masks
Step 3: Heuristic scoring + polyline extraction --> ordered polylines
Step 3b: (Optional) SAM 2 interactive refinement for missed trails
Step 4: LLM trail identification --> polyline-to-trail-name mapping
Step 5: Output assembly --> JSON + TypeScript for React app
Step 6: Visualization overlays --> debug images
```

All scripts run from the project root directory. All output goes to `scripts/output/`.

---

## Step 1: Convert Trail Map to PNG

```bash
python scripts/01_convert_pdf.py
```

**What it does:** Converts the trail map PDF to a high-resolution PNG at 300 DPI. If the PDF is not found, falls back to the JPG in `public/`.

**Expected output:**
```
PDF not found. Using existing image killington-trail-map.jpg...
Saved scripts/output/trailmap_300dpi.png (3429x2028, 15.8 MB)
Saved metadata to scripts/output/image_meta.json
```

**Produces:**
| File | Description |
|------|-------------|
| `output/trailmap_300dpi.png` | High-res trail map image (input for all subsequent steps) |
| `output/image_meta.json` | Image dimensions and DPI metadata |

**Parameters:** DPI is hardcoded to 300 in the script. At 300 DPI, trail lines are 4-6 pixels wide, which is good for skeletonization. Change the `DPI` constant if needed.

**Watch out for:**
- If using the JPG fallback, the image is lower resolution (~3429x2028 vs ~6858x4056 from PDF). This means fewer pixels per trail line and slightly less accurate extraction.
- The PNG output is large (~16-70 MB). It is gitignored.

**Note on vector extraction (don't bother):** The source PDF was inspected with PyMuPDF — it contains zero vector drawings; the entire trail map is a single embedded JPEG-2000 image (4560x2704). There are no extractable colored stroked paths. Pixel-based CV (steps 2–3) is the only viable extraction approach for this map.

---

## Step 2: Color Segmentation

```bash
python scripts/02_segment_colors.py
```

**What it does:** Converts the image to HSV color space and segments trail lines by color using threshold ranges. Also detects black trails using Canny edge detection (since dark-on-dark can't be found by color alone).

**Expected output:**
```
Loading image...
  Image size: 3429x2028

Running color segmentation...
  Segmenting green...
    89,515 pixels (1.29%)
  Segmenting blue...
    142,857 pixels (2.05%)
  Segmenting magenta...
    62,249 pixels (0.90%)
  Segmenting cyan...
    95,876 pixels (1.38%)
  Segmenting yellow...
    8,908 pixels (0.13%)
  Detecting black trails (edge detection)...
    38,680 pixels (0.56%)
```

**Produces:**
| File | Description |
|------|-------------|
| `output/masks/green_mask.png` | Binary mask of green (easy) trail pixels |
| `output/masks/blue_mask.png` | Binary mask of blue (intermediate) trail pixels |
| `output/masks/magenta_mask.png` | Binary mask of magenta (expert/double-black) trail pixels |
| `output/masks/black_mask.png` | Binary mask of black (advanced) trail pixels |
| `output/masks/cyan_mask.png` | Binary mask of cyan (lift lines - excluded from trails) |
| `output/masks/yellow_mask.png` | Binary mask of yellow (boundaries) |
| `output/color_overlay.png` | Composite overlay of all masks on the original image |
| `output/segmentation_stats.json` | Pixel counts and component counts per color |
| `output/text_regions.json` | Per-character bounding boxes for white trail-name text (used by OCR experiments; see "OCR experiment" note below) |
| `output/symbols.json` | Per-difficulty symbol (■◆●) center positions |

**HSV threshold ranges** (defined in `scripts/utils/color_ranges.py`):

| Color | Hue | Saturation | Value | Notes |
|-------|-----|------------|-------|-------|
| Green | 35-85 | >140 | >80 | Aggressive saturation to avoid green terrain |
| Blue | 95-130 | >90 | >70 | Sky areas are blue but lighter |
| Magenta | 140-180, 0-10 | >80 | >80 | Wraps around hue 0/180 |
| Cyan | 80-95 | >100 | >150 | Lift lines (excluded from trail extraction) |
| Black | N/A | N/A | N/A | Uses Canny edge detection, not HSV |

**Interactive tuning mode:**

```bash
python scripts/02_segment_colors.py --tune
```

Opens an OpenCV window with HSV trackbars. Adjust sliders to see which pixels are selected in real-time. Press `q` to quit. Use this to fine-tune thresholds for your specific trail map image.

**Watch out for:**
- **Green mask will contain terrain noise.** The painted mountain terrain is also green. The heuristic scoring in Step 3 filters this out. Don't worry if the green mask looks noisy.
- **Blue mask may contain sky.** The top of the image has blue sky. Same solution - Step 3 filters it.
- **Black mask is conservative.** Edge detection produces fewer false positives but may miss some faint black trails. Use SAM 2 (Step 3b) for any missed ones.
- The `--tune` mode requires a display (won't work in headless/SSH environments).

**OCR experiment (deferred):** The `text_regions.json` output was added to support an OCR-augmented naming pipeline that would replace some of the LLM calls in Step 4 with deterministic text-to-trail matching. A POC was run via `scripts/ocr_poc.py` (uses easyocr; install with `pip install easyocr`). Result: OCR works on real text (perfect on labels like "SOLITUDE", "CAPER"), but the white-pixel detector here surfaces ~50% non-text clusters (bridges, snow patches, building edges), and the trail-name labels that *are* real are too small / low-contrast for high-confidence OCR matches. POC matched ~17% of test clusters to a trail name, well below the plan's 50% gate. The infrastructure (`text_regions.json` + the catalog refactor) stays in place for a future attempt with a better text-vs-noise classifier or a different OCR engine. Reproduce with: `python scripts/ocr_poc.py --cluster-size trail-like --dump-crops`.

---

## Step 3: Polyline Extraction with Heuristic Scoring

```bash
python scripts/03_extract_polylines.py
```

**What it does:** For each color mask:
1. Extracts connected components (blobs)
2. Scores each component with 6 geometric heuristics (confidence scoring system)
3. Skeletonizes accepted components to 1-pixel-wide lines
4. Walks the skeleton to produce ordered point sequences
5. Simplifies with Douglas-Peucker algorithm
6. Merges collinear segments at junctions
7. Orders points top-to-bottom (summit to base)

**Expected output:**
```
Image: 3429x2028

  Processing green...
    Found 37 components (after area filter)
    Accepted: 37, Uncertain: 0, Rejected: 0

  Processing blue...
    Found 57 components (after area filter)
    Accepted: 57, Uncertain: 0, Rejected: 0

  Processing magenta...
    Found 61 components (after area filter)
    Accepted: 60, Uncertain: 1, Rejected: 0

  Processing black...
    Found 10 components (after area filter)
    Accepted: 9, Uncertain: 1, Rejected: 0

Merging collinear segments...
  green: 37 -> 35 segments
  blue: 57 -> 54 segments
  magenta: 60 -> 52 segments

Total accepted: 150
Total uncertain: 2
```

**Produces:**
| File | Description |
|------|-------------|
| `output/extracted_polylines.json` | All extracted polylines with pixel coordinates, scores, classifications |
| `output/score_logs.json` | Detailed per-component heuristic scores for debugging |

**Heuristic scoring system** (each adds +1, max score = 6):

| # | Heuristic | +1 if | What it catches |
|---|-----------|-------|-----------------|
| 1 | Arc length | >100px | Removes text characters, small noise |
| 2 | Sinuosity | >1.1 (arc/straight) | Removes straight borders, keeps curvy trails |
| 3 | Smooth curvature | max angle change <70 deg | Removes text (sharp corners) |
| 4 | Downhill tendency | >15 deg from horizontal | Soft signal - trails go downhill |
| 5 | Stroke width | std dev <2.0px | Removes variable-width text |
| 6 | No holes | 0 enclosed holes | Removes letters O, D, B, P |

**Classification by total score** (thresholds in `scripts/utils/heuristics.py` as `CONFIDENT_THRESHOLD` / `PROBABLE_THRESHOLD` / `UNCERTAIN_THRESHOLD`):
- **5-6:** High confidence (accepted)
- **3-4:** Probable (accepted, flagged)
- **1-2:** Uncertain (kept for SAM 2 refinement)
- **0:** Rejected (noise/text)

To pick or re-tune these thresholds against the current `score_logs.json`, run:

```bash
python scripts/tune_thresholds.py
```

It sweeps candidate (confident, probable, uncertain) triples, reports
precision/recall/F1/drift versus the current pipeline output, and renders
side-by-side overlay diffs (`output/tune/overlay_*.jpg`) for the top picks.

**History note:** an earlier version of this scorer had 9 heuristics. Three were removed because they didn't actually discriminate trails from noise: aspect-ratio (>5:1) fired on only 3.9% of components because curved trails have square-ish bounding boxes; mountain-region and proximity were always +1 because their masks were never wired up at the call site. The current 6-heuristic version reproduces the prior accept set exactly (F1=1.000 in the threshold sweep).

**Watch out for:**
- Runtime is ~30-60 seconds depending on image resolution. Skeletonization of large components is the bottleneck.
- Some trails may be split into multiple segments (fragmented by text labels overlapping the trail line). The merge step catches collinear ones but not all.
- The `uncertain` count tells you how many components might need SAM 2 refinement.

---

## Step 3b: SAM 2 Interactive Refinement (Optional)

```bash
python scripts/03b_sam_refine.py
python scripts/03b_sam_refine.py --resume    # Resume a previous session
```

**What it does:** Opens an interactive matplotlib window showing the trail map with existing polylines overlaid. Click on trails the CV pipeline missed, and SAM 2 segments them automatically.

**Requirements:** `pip install sam2 torch` (not in base requirements.txt — ~2.5GB download for PyTorch + model).

**UI controls:**
| Action | What it does |
|--------|-------------|
| Left-click | Add positive point prompt (click on the trail) |
| Shift+click | Add additional positive point |
| Right-click | Add negative point (exclude a region) |
| Enter | Accept current mask (then type trail name) |
| Escape | Clear current selection |
| S | Save progress to disk |
| U | Undo last point |
| Q | Save and quit |

**CPU performance:**
- Image embedding: ~30 seconds (one-time on startup)
- Each click: ~1-2 seconds for mask decoder
- Full session for ~30 trails: ~15-20 minutes

**If SAM 2 is not installed:** Falls back to manual point-clicking mode where you trace trail paths by clicking points along them.

**Produces:**
| File | Description |
|------|-------------|
| `output/sam_refinements.json` | Accepted masks and trail assignments from interactive session |

**Watch out for:**
- SAM 2 works best with a single click near the center of the trail line. If it segments too much (grabs surrounding terrain), add negative points on the terrain.
- The matplotlib window needs a display. Won't work in headless environments.
- Progress is saved to `sam_refinements.json` on every save (`S`) and on quit (`Q`). Safe to interrupt and resume.

---

## Step 4: Trail Identification

### Prepare annotated patches only:
```bash
python scripts/04_identify_trails.py --prepare
```

### Run LLM identification (requires API key):
```bash
ANTHROPIC_API_KEY=sk-ant-... python scripts/04_identify_trails.py --identify
```

### Both steps at once:
```bash
ANTHROPIC_API_KEY=sk-ant-... python scripts/04_identify_trails.py
```

**What it does:**
1. **Prepare:** Crops the trail map into 7 peak-region patches (one per peak area). Draws numbered, color-coded polyline overlays on each patch. Saves annotated images for the LLM.
2. **Identify:** Sends each annotated patch to Claude Vision API with a list of known trail names for that peak area. Claude reads the text labels on the map and matches numbered overlays to trail names. Returns JSON mapping.

**Expected output (--prepare):**
```
Loaded 150 accepted polylines

Preparing annotated patches...
  snowshed: 8 polylines, 5 expected trails
  sunrise: 8 polylines, 5 expected trails
  ramshead: 42 polylines, 11 expected trails
  snowdon: 56 polylines, 17 expected trails
  skye-peak: 63 polylines, 26 expected trails
  killington-peak: 45 polylines, 24 expected trails
  bear-mountain: 14 polylines, 10 expected trails
```

**Produces:**
| File | Description |
|------|-------------|
| `output/patches/patch_snowshed.jpg` | Annotated patch for Snowshed peak area |
| `output/patches/patch_sunrise.jpg` | Annotated patch for Sunrise peak area |
| `output/patches/patch_ramshead.jpg` | Annotated patch for Ramshead peak area |
| `output/patches/patch_snowdon.jpg` | Annotated patch for Snowdon peak area |
| `output/patches/patch_skye-peak.jpg` | Annotated patch for Skye Peak area |
| `output/patches/patch_killington-peak.jpg` | Annotated patch for Killington Peak area |
| `output/patches/patch_bear-mountain.jpg` | Annotated patch for Bear Mountain area |
| `output/patch_info.json` | Metadata about each patch (polyline IDs, expected trails) |
| `output/trail_identifications.json` | LLM results mapping polyline numbers to trail IDs |

**Manual overrides:** Edit `scripts/manual_overrides.json` to manually assign polyline IDs to trail names. These override LLM results. Format:
```json
{
  "green_005": "superstar",
  "blue_012": "skyelark"
}
```

**Watch out for:**
- Polyline counts per region are higher than trail counts because (a) regions overlap, (b) some trails are fragmented into multiple segments, (c) some polylines are lift lines or terrain noise.
- The LLM uses `claude-sonnet-4-20250514`. Each patch is ~200-1000 KB. Total API cost is ~$0.50-1.00 per run.
- LLM results are not perfect. Expect ~70-85% accuracy. Use manual overrides for corrections.
- If `ANTHROPIC_API_KEY` is not set, `--identify` will exit with an error. Use `--prepare` to generate patches without an API key, then identify manually.

---

## Step 5: Output Assembly

```bash
python scripts/05_assemble_output.py
```

**What it does:** Merges polyline coordinates with trail identifications (from Step 4 and/or manual overrides) to produce the final output consumed by the React app.

- Converts pixel coordinates to percentage of image dimensions (0-100 range)
- Generates SVG `d` path strings with quadratic Bezier smoothing
- Resolves duplicates (keeps the polyline with more points)
- Generates TypeScript source file for direct import

**Expected output (without LLM identifications):**
```
Loaded 150 accepted polylines

Saved scripts/output/trail_paths.json
  Matched: 0 trails
  Unmatched: 150 polylines
Saved src/data/trailPaths.ts
```

**Expected output (after LLM identification):**
```
Loaded 150 accepted polylines
LLM identifications: 98 mappings
Manual overrides: 5 mappings

Saved scripts/output/trail_paths.json
  Matched: 103 trails
  Unmatched: 47 polylines
Saved src/data/trailPaths.ts
```

**Produces:**
| File | Description |
|------|-------------|
| `output/trail_paths.json` | Final output: trail ID -> percentage coordinates + SVG path |
| `src/data/trailPaths.ts` | TypeScript source file imported by the React app |

**`trail_paths.json` format:**
```json
{
  "imageWidth": 3429,
  "imageHeight": 2028,
  "trails": {
    "superstar": {
      "points": [[78.2, 18.5], [78.0, 22.1], ...],
      "svgPath": "M 78.2 18.5 Q 78.1 20.3 78.0 22.1 ..."
    }
  },
  "unmatched": ["green_007", "blue_012"],
  "metadata": {
    "dpi": 300,
    "matchedCount": 103,
    "unmatchedCount": 47,
    "totalPolylines": 150
  }
}
```

**Watch out for:**
- If you haven't run Step 4 (no `trail_identifications.json`), all polylines will be "unmatched". The React app will fall back to circle hotspots for unmatched trails.
- Re-run this step after updating `manual_overrides.json` to regenerate output.
- The generated `src/data/trailPaths.ts` is auto-formatted. Do not edit it manually.

---

## Step 6: Visualization

```bash
python scripts/06_visualize.py
```

**What it does:** Generates overlay images for visual inspection of the extraction results.

**Expected output:**
```
Loading image...
Loaded 150 accepted polylines

Creating per-color overlays...
  Saved scripts/output/overlay_green.jpg (35 trails)
  Saved scripts/output/overlay_blue.jpg (54 trails)
  Saved scripts/output/overlay_magenta.jpg (52 trails)
  Saved scripts/output/overlay_black.jpg (9 trails)

Creating composite overlay...
  Saved scripts/output/overlay_all.jpg (150 trails)

Creating numbered overlay...
  Saved scripts/output/overlay_numbered.jpg (numbered for LLM identification)

--- Summary ---
  green: 35 segments
  blue: 54 segments
  magenta: 52 segments
  black: 9 segments
  Total: 150
  Uncertain (needs SAM 2): 2
```

**Produces:**
| File | Description |
|------|-------------|
| `output/overlay_green.jpg` | Green trail polylines overlaid on map |
| `output/overlay_blue.jpg` | Blue trail polylines overlaid on map |
| `output/overlay_magenta.jpg` | Magenta trail polylines overlaid on map |
| `output/overlay_black.jpg` | Black trail polylines overlaid on map |
| `output/overlay_all.jpg` | All colors combined on map |
| `output/overlay_numbered.jpg` | All polylines with numbered labels (used for LLM identification) |

Smaller versions of all overlays, masks, and patches are saved in `output/readable/` for easy viewing and committing to the repo.

**Watch out for:**
- The full-size overlays are 1.5-2.5 MB each (gitignored). The `output/readable/` versions are ~500-600 KB.
- Compare the overlay images with the original trail map to spot false positives (detected lines that aren't trails) and false negatives (trails that weren't detected).

---

## Quick-Run: Full Pipeline

```bash
# Install dependencies
pip install -r scripts/requirements.txt

# Run steps 1-3 + 6 (no API key needed)
python scripts/01_convert_pdf.py
python scripts/02_segment_colors.py
python scripts/03_extract_polylines.py
python scripts/06_visualize.py

# Inspect output/readable/ images to verify extraction quality

# Prepare patches for LLM identification
python scripts/04_identify_trails.py --prepare

# Run LLM identification (requires API key)
ANTHROPIC_API_KEY=sk-ant-... python scripts/04_identify_trails.py --identify

# Assemble final output
python scripts/05_assemble_output.py

# Verify: check output/trail_paths.json matchedCount
# Verify: run the React app and check Image Map view
npm run dev
```

---

## Output Directory Structure

```
scripts/output/
  trailmap_300dpi.png           # [gitignored] High-res source image
  image_meta.json               # Image dimensions + DPI
  segmentation_stats.json       # Pixel counts per color
  extracted_polylines.json      # All polylines with coordinates + scores
  score_logs.json               # Detailed heuristic scores per component
  trail_paths.json              # Final output (trail ID -> coordinates)
  patch_info.json               # LLM patch metadata
  trail_identifications.json    # LLM results (after Step 4 --identify)
  sam_refinements.json          # SAM 2 session data (after Step 3b)
  masks/                        # [gitignored] Per-color binary masks
    green_mask.png
    blue_mask.png
    magenta_mask.png
    black_mask.png
    cyan_mask.png
    yellow_mask.png
  patches/                      # [gitignored] Annotated peak-region patches
    patch_snowshed.jpg
    patch_sunrise.jpg
    patch_ramshead.jpg
    patch_snowdon.jpg
    patch_skye-peak.jpg
    patch_killington-peak.jpg
    patch_bear-mountain.jpg
  overlay_*.jpg                 # [gitignored] Full-size visualization overlays
  color_overlay.png             # [gitignored] Composite mask overlay
  readable/                     # Smaller versions for repo/viewing
    masks_grid.jpg              # 2x2 grid of green/blue/magenta/black masks
    overlay_all.jpg             # All extracted trails on map
    overlay_green.jpg           # Green trails on map
    overlay_blue.jpg            # Blue trails on map
    overlay_magenta.jpg         # Magenta trails on map
    overlay_black.jpg           # Black trails on map
    overlay_numbered.jpg        # Numbered trails for identification
    patch_*.jpg                 # Peak-region annotated patches
```

---

## Troubleshooting

**"Image not found" errors:** Run Step 1 first. All subsequent steps depend on `output/trailmap_300dpi.png`.

**Green mask has too much terrain:** This is expected. The heuristic scoring in Step 3 filters out terrain blobs. Check `score_logs.json` to see what was rejected and why.

**Too few black trails detected:** Black trail detection via edge detection is conservative. Use SAM 2 (Step 3b) to interactively click on missed black trails, or manually add them via `manual_overrides.json`.

**`--tune` mode shows black window:** The OpenCV GUI needs a display. If running over SSH, use X forwarding (`ssh -X`) or run locally.

**SAM 2 "module not found":** Install separately: `pip install sam2 torch`. This is a large download (~2.5GB). The pipeline works without it — SAM 2 is optional for refinement only.

**LLM misidentifies trails:** Edit `scripts/manual_overrides.json` with the correct mapping, then re-run Step 5. Overrides take precedence over LLM results.

**React app doesn't show polylines:** Check that `src/data/trailPaths.ts` has entries (not empty). If empty, run Steps 4 + 5 to populate it. Trails without geometry data fall back to circle hotspot dots.
