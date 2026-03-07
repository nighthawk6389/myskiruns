# Trail Path Extraction & Name Matching Guide

How to extract trail polyline coordinates from a ski trail map image and correctly assign trail names to those paths. Written based on the Killington trail map project (4572x2704px JPG).

---

## The Problem

We need two things from a ski trail map image:

1. **Trail geometries** — polyline coordinates tracing each colored trail line
2. **Trail identities** — which trail name goes with which polyline

These are separate problems. The geometry extraction is computer vision; the identity matching is label reading.

---

## What Worked

### 1. Sweepline Extraction (geometry)

**Tool:** `sweepline_extract.py`, also embedded in `match_by_label_position.py`

This is the core CV technique that extracts trail paths from the map image. It works because ski trail maps draw trails as colored lines running roughly top-to-bottom.

**How it works:**

1. Convert the image to HSV color space
2. Create binary masks for each trail color using `cv2.inRange()`:
   - **Cyan** (blue/intermediate trails): HSV `[88,60,130]` to `[115,255,255]`
   - **Pink** (black/double-black trails): HSV `[145,50,130]` to `[172,255,255]`
   - **Yellow** (green/beginner trails): HSV `[20,80,150]` to `[48,255,255]`
3. Light morphological cleanup (`MORPH_OPEN` with 2x2 kernel) to remove noise without over-connecting separate trails
4. Scan each mask in horizontal bands (6px tall). For each band:
   - Project vertically to find horizontal runs of colored pixels
   - Filter runs by minimum width (4px) to ignore noise
   - Track runs across bands: if a run in band N is within 40px horizontally of a run in band N-1, they're the same trail
   - Allow gaps of up to 5 bands (30px) for trails that briefly disappear behind text/features
5. Trails that persist across enough bands (4+ points) become extracted paths
6. Each path is a list of `(x%, y%)` percentage coordinates

**Key parameters:**
- `band_height_px=6` — height of each horizontal scan band
- `min_cluster_width=4` — minimum pixel width to count as a trail segment
- `max_gap_bands=5` — how many empty bands before a trail is considered ended
- `max_shift=40` — max horizontal pixel jump between consecutive bands

**Why it works well:** Ski trails are long vertical-ish colored lines. Scanning horizontally naturally follows them from top to bottom without getting confused at intersections or branches (unlike skeleton-based approaches).

**Output:** ~150-300 unnamed paths per color, including noise. The real trails are the ones with significant vertical extent (height > 3% of image).

### 2. Label Position Matching with Hungarian Algorithm (identity)

**Tool:** `match_by_label_position.py`

This solves the name assignment problem: given N extracted paths and M trail names, which path is which trail?

**How it works:**

1. For each of the 115 trails, record the approximate `(x%, y%)` position where its name label appears on the map. These positions were determined by visual reading of high-resolution map crops (see "How Label Positions Were Determined" below).

2. Group trails and paths by color (cyan/pink/yellow). Trails only match paths of their expected color.

3. Within each color group, build a cost matrix where `cost[i][j]` = distance from trail i's label position to path j. The distance function is:
   ```
   distance = 0.6 * min_point_distance + 0.4 * center_distance
   ```
   - `min_point_distance`: closest distance from the label to any point on the path
   - `center_distance`: distance from the label to the path's centroid

4. Solve with the **Hungarian algorithm** (`scipy.optimize.linear_sum_assignment`) for globally optimal assignment.

5. Simplify matched paths to ~12 points using **Douglas-Peucker** (`cv2.approxPolyDP`) with binary search for the right epsilon.

**Why Hungarian over greedy:** Greedy matching (assign each trail to its closest unmatched path) produces cascading errors. If trail A steals trail B's correct path because it happens to be slightly closer, trail B gets a wrong path, which pushes trail C off, etc. The Hungarian algorithm minimizes total assignment cost globally.

**Output:** `src/data/trailPaths.ts` with 114/115 trails matched.

### 3. How Label Positions Were Determined

The label positions in `TRAIL_LABEL_POSITIONS` were determined by having AI agents visually read high-resolution crops of the map. The process:

1. **Generate crops:** `generate_grid_crops.py` produces ~20 overlapping high-res crops covering the entire map. `generate_peak_crops.py` produces per-peak crops. Each crop covers 25-35% of the image at full resolution.

2. **Visual reading:** Multiple AI agents examine the crops in parallel, each reading a different section. For each visible trail name label, the agent records:
   - The trail name (as printed on the map)
   - The approximate (x%, y%) position of the label
   - The color of the trail line (cyan/pink/yellow)

3. **Cross-reference:** Match the visually-read trail names against the known trail list in `src/data/trails.ts` to map `trail_id -> (label_x, label_y, color)`.

Label positions only need ~3-5% accuracy for the Hungarian matching to work correctly, since trails are spaced further apart than that in most areas.

### 4. Coordinate System

Everything uses percentage coordinates (0-100) matching the SVG `viewBox="0 0 100 100"`:
- `x=0` is the left edge of the image, `x=100` is the right edge
- `y=0` is the top edge, `y=100` is the bottom edge
- The map image is 4572x2704px, so 1% x ≈ 46px, 1% y ≈ 27px

### 5. Peak Regions

The map is divided into 7 peak regions (left to right):

```python
PEAK_REGIONS = {
    'snowshed':        (0, 10, 40, 82),     # far left, small beginner area
    'sunrise':         (3, 16, 35, 62),      # left side
    'bear-mountain':   (14, 38, 15, 68),     # left-center
    'skye-peak':       (28, 57, 5, 68),      # center, largest area
    'killington-peak': (42, 66, 3, 62),      # center-right, summit
    'snowdon':         (62, 88, 10, 65),     # right side
    'ramshead':        (82, 100, 18, 70),    # far right
}
```

Format: `(x_min%, x_max%, y_min%, y_max%)`. These overlap intentionally—a trail near the border between two peaks should be assignable to either.

### 6. Visualization Tools

- `numbered_paths_viz.py` — draws each extracted path with a unique number, grouped by peak. Useful for manually checking which extracted path = which trail.
- `generate_peak_crops.py` — clean and annotated per-peak crops
- `overlay_current_paths.py` — overlays the current `trailPaths.ts` data on the map for verification

---

## What Didn't Work

### 1. Skeletonization + Connected Components

**Tool:** `extract_and_assign.py`

**Approach:** Threshold each color mask → morphological dilation to connect fragments → find connected components → skeletonize each component → walk the skeleton to extract ordered point sequences.

**Why it failed:** The skeleton walker got stuck at branch points where trails intersect or merge. Trail intersections create junction pixels in the skeleton where 3+ branches meet. The walker would either loop or take a wrong turn, producing tiny 3-point paths instead of full trail lines. Aggressive dilation to connect fragments also merged nearby parallel trails into single blobs.

**Lesson:** Skeletonization works for isolated line segments but not for networks of intersecting lines. The sweepline approach sidesteps this entirely by tracking horizontal position across bands rather than walking a skeleton graph.

### 2. OCR (Tesseract) for Trail Name Reading

**Tools:** `ocr_explore.py`, `ocr_trail_labels.py`

Two approaches were tried:

**Full-image OCR (`ocr_explore.py`):** Ran Tesseract on the entire map with various preprocessing (grayscale, adaptive threshold, CLAHE). Only detected large peak name labels ("SKYE PEAK", "BEAR MOUNTAIN"). Trail names are too small and at various angles on a complex illustrated background.

**Rotated-crop OCR (`ocr_trail_labels.py`):** For each extracted trail path:
1. Compute the path's principal axis angle via PCA
2. Crop a band around the path from the original image
3. Rotate the crop to make the trail horizontal
4. Apply multiple preprocessing methods (CLAHE, inversion, 2x scaling)
5. Run Tesseract with PSM modes 7 (single line) and 11 (sparse text)
6. Fuzzy-match detected text against known trail names

**Results:** 2/114 correct matches. Tesseract cannot handle small (often <12px), rotated, artistically-rendered text on complex illustrated map backgrounds. The preprocessing helps with contrast but can't overcome the fundamental limitation of the text being too small and the background too noisy.

**Lesson:** OCR is not viable for reading trail labels on illustrated ski maps. The text is too small, at arbitrary angles, uses decorative fonts, and sits on complex multi-colored backgrounds. Visual AI reading of high-res crops is far more effective.

### 3. Greedy Name Matching (by height/position within peak)

**Tool:** `sweepline_extract.py` → `match_trails_in_peak()`

**Approach:** Within each peak region, group trails and paths by color. Sort paths by height (tallest first). Greedily assign the tallest unmatched path to the next trail.

**Why it failed:** Trail height is a terrible proxy for identity. Many trails have similar heights. The greedy assignment meant that whichever trail happened to be processed first grabbed the tallest path, regardless of whether it was geographically close. This produced geometrically-correct overlays (the polylines followed real trail lines) but with completely wrong name assignments.

**Lesson:** Position-based matching with global optimization (Hungarian algorithm) is essential. You need to know approximately where each trail's label is, then match labels to nearby paths. Greedy heuristics based on trail properties (height, width, position ranking) don't work when there are many similarly-shaped trails in the same area.

---

## Running the Pipeline

### Full Re-extraction

If the map image changes or you need to re-extract everything:

```bash
# 1. Generate high-res crops for visual label reading
python3 tools/generate_grid_crops.py
python3 tools/generate_peak_crops.py

# 2. Visually read the crops to determine/update TRAIL_LABEL_POSITIONS
#    in tools/match_by_label_position.py
#    (This is the manual/AI-assisted step)

# 3. Run the matching pipeline
python3 tools/match_by_label_position.py
#    Outputs: src/data/trailPaths.ts, tools/label_matched_paths.jpg

# 4. Verify the results
python3 tools/overlay_current_paths.py
python3 tools/numbered_paths_viz.py
```

### Adding a New Trail

1. Determine where the trail's name label appears on the map (x%, y%)
2. Determine the trail line color (cyan/pink/yellow)
3. Add an entry to `TRAIL_LABEL_POSITIONS` in `match_by_label_position.py`
4. Add the trail definition to `src/data/trails.ts`
5. Re-run `python3 tools/match_by_label_position.py`

### Fixing a Mismatched Trail

If a trail has the wrong path assigned:

1. Run `python3 tools/numbered_paths_viz.py` to see numbered paths
2. Look at the peak's `_numbered.jpg` output to identify which path number should be which trail
3. Adjust the trail's `(label_x, label_y)` in `TRAIL_LABEL_POSITIONS` to be closer to the correct path
4. Re-run `python3 tools/match_by_label_position.py`

The label position only needs to be closer to the correct path than to any other path of the same color. Usually moving it by 2-3% is enough.

### Tuning Sweepline Parameters

If trails aren't being extracted properly:

- **Missing thin trails:** Decrease `min_cluster_width` (try 3 or 2)
- **Trails cut short:** Increase `max_gap_bands` (try 7-8)
- **Trails merged together:** Decrease `max_shift` (try 30)
- **Too much noise:** Increase `min_cluster_width` (try 5-6) or require more minimum points
- **Wrong colors detected:** Adjust HSV ranges in `extract_masks()`

### Dependencies

```
opencv-python (cv2)
numpy
scipy (for Hungarian algorithm: scipy.optimize.linear_sum_assignment)
```

Optional (for failed OCR approach, not needed):
```
pytesseract
```

---

## File Inventory

| File | Purpose | Status |
|------|---------|--------|
| `tools/match_by_label_position.py` | **Main pipeline**: sweepline + Hungarian matching | Active, produces final output |
| `tools/sweepline_extract.py` | Standalone sweepline extraction with greedy matching | Superseded by match_by_label_position.py |
| `tools/extract_and_assign.py` | Skeleton-based extraction (failed approach) | Archived |
| `tools/ocr_explore.py` | Full-image OCR attempt | Failed, archived |
| `tools/ocr_trail_labels.py` | Per-trail rotated-crop OCR | Failed, archived |
| `tools/generate_grid_crops.py` | Generate overlapping map crops | Active utility |
| `tools/generate_peak_crops.py` | Generate per-peak clean+annotated crops | Active utility |
| `tools/numbered_paths_viz.py` | Numbered path visualization per peak | Active utility |
| `tools/overlay_current_paths.py` | Overlay trailPaths.ts on map | Active utility |
| `src/data/trailPaths.ts` | **Final output**: trail polyline coordinates | Production file |
| `src/data/trails.ts` | Trail definitions (id, name, difficulty, peak) | Production file (read-only by pipeline) |
