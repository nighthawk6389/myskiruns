#!/usr/bin/env python3
"""Step 2: Color segmentation of trail map into per-color binary masks.

Pipeline:
1. Create mountain mask from yellow boundary (excludes sky, parking lots)
2. Detect and mask white trail name text
3. Detect difficulty symbols (■ ◆ ●) as trail anchor points
4. Segment trail colors within mountain mask, with text removed
5. Directional gap-fill to bridge text gaps along trail lines
6. Detect black trails via adaptive thresholding
7. Subtract lift lines from trail masks

Usage:
    python 02_segment_colors.py          # Run segmentation
    python 02_segment_colors.py --tune   # Interactive HSV threshold tuning
"""

import argparse
import json
import sys
from pathlib import Path

import cv2
import numpy as np

from utils.color_ranges import TRAIL_COLOR_RANGES, TRAIL_COLOR_RANGES_HIGH, TRAIL_COLOR_RANGES_LOW, LIFT_COLOR_RANGES, OTHER_COLOR_RANGES, COLOR_RANGES, VIS_COLORS_BGR

SCRIPT_DIR = Path(__file__).parent
OUTPUT_DIR = SCRIPT_DIR / "output"
MASKS_DIR = OUTPUT_DIR / "masks"
IMAGE_PATH = OUTPUT_DIR / "trailmap_300dpi.png"


def load_image():
    """Load the trail map image."""
    if not IMAGE_PATH.exists():
        print(f"ERROR: Image not found at {IMAGE_PATH}. Run 01_convert_pdf.py first.")
        sys.exit(1)
    img = cv2.imread(str(IMAGE_PATH))
    if img is None:
        print(f"ERROR: Could not read {IMAGE_PATH}")
        sys.exit(1)
    return img


def segment_color(hsv_img: np.ndarray, ranges: list) -> np.ndarray:
    """Create binary mask for a color using one or more HSV ranges."""
    mask = np.zeros(hsv_img.shape[:2], dtype=np.uint8)
    for lower, upper in ranges:
        mask |= cv2.inRange(hsv_img, lower, upper)
    return mask


def create_mountain_mask(hsv_img: np.ndarray) -> np.ndarray:
    """Create mountain region mask from the yellow boundary line.

    The yellow dashed boundary outlines the ski area. Everything outside
    (sky, surrounding mountains, parking lots) is excluded.
    """
    h, w = hsv_img.shape[:2]

    # Detect yellow boundary pixels
    yellow = cv2.inRange(hsv_img, np.array([15, 80, 80]), np.array([35, 255, 255]))

    # Thicken to close gaps in the dashed line
    yellow_thick = cv2.dilate(yellow, np.ones((20, 20), np.uint8), iterations=3)
    yellow_thick = cv2.morphologyEx(yellow_thick, cv2.MORPH_CLOSE,
                                     np.ones((30, 30), np.uint8), iterations=3)

    # Flood fill from corners — these are OUTSIDE the boundary
    filled = yellow_thick.copy()
    fill_mask = np.zeros((h + 2, w + 2), np.uint8)
    for seed in [(5, 5), (w - 5, 5), (5, h - 5), (w - 5, h - 5)]:
        cv2.floodFill(filled, fill_mask, seed, 255)

    # Mountain = everything NOT reached by corner flood fill
    outside = filled - yellow_thick
    mountain = cv2.bitwise_not(outside)

    # Clean up edges
    mountain = cv2.morphologyEx(mountain, cv2.MORPH_CLOSE,
                                 np.ones((15, 15), np.uint8), iterations=2)
    mountain = cv2.morphologyEx(mountain, cv2.MORPH_OPEN,
                                 np.ones((5, 5), np.uint8), iterations=1)

    # Subtract sky from mountain mask — the yellow boundary includes the
    # ridgeline which has sky bleed. Use targeted sky detection, not erosion,
    # to avoid clipping trails at the ridgeline (like Solitude).
    sky = cv2.inRange(hsv_img, np.array([85, 20, 150]), np.array([135, 255, 255]))
    sky_region = np.zeros_like(sky)
    sky_region[:int(h * 0.20), :] = sky[:int(h * 0.20), :]
    # Only dilate sky inward by a small amount
    sky_region = cv2.dilate(sky_region, np.ones((5, 5), np.uint8), iterations=1)
    mountain = cv2.bitwise_and(mountain, cv2.bitwise_not(sky_region))

    return mountain


def create_text_mask(hsv_img: np.ndarray, mountain_mask: np.ndarray) -> np.ndarray:
    """Detect white trail name text that overlaps trail lines.

    Trail names are written in white/light text along the trail lines.
    This text breaks the color detection of the underlying trail line.
    We detect the text, mask it out, and then gap-fill through it.
    """
    # White/light text: low saturation, high value
    white = cv2.inRange(hsv_img, np.array([0, 0, 185]), np.array([180, 65, 255]))
    white = cv2.bitwise_and(white, mountain_mask)

    # Filter: keep only small connected components (text characters)
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(white)
    text_mask = np.zeros_like(white)
    for i in range(1, num_labels):
        area = stats[i, cv2.CC_STAT_AREA]
        ww = stats[i, cv2.CC_STAT_WIDTH]
        hh = stats[i, cv2.CC_STAT_HEIGHT]
        # Text characters: small area, limited size
        if 5 < area < 1000 and max(ww, hh) < 60:
            text_mask[labels == i] = 255

    # Note: we do NOT detect dark text here because dark text looks identical
    # to black trail lines. Black trail detection handles this via heuristics.

    # Dilate text mask to cover the text plus small margin
    text_dilated = cv2.dilate(text_mask, np.ones((3, 3), np.uint8), iterations=1)
    return text_dilated


def detect_difficulty_symbols(hsv_img: np.ndarray, mountain_mask: np.ndarray) -> dict:
    """Detect difficulty symbols (■ blue squares, ◆ black diamonds, ● green circles).

    These symbols appear along trail lines and confirm a trail exists at that
    location. Used to boost confidence during gap-filling (not to seed new blobs).

    Returns dict of color -> list of (x, y) center positions.
    """
    symbols = {"green": [], "blue": [], "black": []}
    img_bgr = cv2.cvtColor(hsv_img, cv2.COLOR_HSV2BGR)

    # Blue squares: small, compact, blue hue, high saturation, solid fill
    blue = cv2.inRange(hsv_img, np.array([85, 80, 50]), np.array([135, 255, 255]))
    blue = cv2.bitwise_and(blue, mountain_mask)
    num_l, lbl, st, cent = cv2.connectedComponentsWithStats(blue)
    for i in range(1, num_l):
        area = st[i, cv2.CC_STAT_AREA]
        ww = st[i, cv2.CC_STAT_WIDTH]
        hh = st[i, cv2.CC_STAT_HEIGHT]
        aspect = max(ww, hh) / max(min(ww, hh), 1)
        fill = area / max(ww * hh, 1)
        if 20 < area < 200 and aspect < 1.8 and max(ww, hh) < 20 and fill > 0.4:
            symbols["blue"].append((int(cent[i][0]), int(cent[i][1])))

    # Green circles: small, compact, green hue
    green = cv2.inRange(hsv_img, np.array([35, 80, 50]), np.array([85, 255, 255]))
    green = cv2.bitwise_and(green, mountain_mask)
    num_l, lbl, st, cent = cv2.connectedComponentsWithStats(green)
    for i in range(1, num_l):
        area = st[i, cv2.CC_STAT_AREA]
        ww = st[i, cv2.CC_STAT_WIDTH]
        hh = st[i, cv2.CC_STAT_HEIGHT]
        aspect = max(ww, hh) / max(min(ww, hh), 1)
        fill = area / max(ww * hh, 1)
        if 20 < area < 200 and aspect < 1.8 and max(ww, hh) < 20 and fill > 0.4:
            symbols["green"].append((int(cent[i][0]), int(cent[i][1])))

    # Black diamonds: small, compact, dark, solid
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    dark = ((gray < 80) & (mountain_mask > 0)).astype(np.uint8) * 255
    num_l, lbl, st, cent = cv2.connectedComponentsWithStats(dark)
    for i in range(1, num_l):
        area = st[i, cv2.CC_STAT_AREA]
        ww = st[i, cv2.CC_STAT_WIDTH]
        hh = st[i, cv2.CC_STAT_HEIGHT]
        aspect = max(ww, hh) / max(min(ww, hh), 1)
        fill = area / max(ww * hh, 1)
        if 20 < area < 150 and aspect < 1.5 and max(ww, hh) < 18 and fill > 0.5:
            symbols["black"].append((int(cent[i][0]), int(cent[i][1])))

    # Filter out symbols in the base/parking area at the bottom of the image.
    # These are often legend markers, signage, or base-area features — not
    # difficulty markers on actual ski trails.
    h, w = hsv_img.shape[:2]
    max_y = int(h * 0.78)  # bottom 22% is base area
    for color in symbols:
        before = len(symbols[color])
        symbols[color] = [(x, y) for x, y in symbols[color] if y <= max_y]
        removed = before - len(symbols[color])
        if removed > 0:
            print(f"    Filtered {removed} {color} symbols in base area (y>{max_y})")

    return symbols


def create_symbol_anchor_mask(symbols: dict, shape: tuple, radius: int = 8) -> dict:
    """Create anchor regions at difficulty symbol locations.

    Radius of 8px — large enough to create skeleton fragments that survive
    extraction filters, while small enough to not create terrain-like blobs.
    """
    anchor_masks = {}
    for color, positions in symbols.items():
        mask = np.zeros(shape, dtype=np.uint8)
        for x, y in positions:
            cv2.circle(mask, (x, y), radius, 255, -1)
        anchor_masks[color] = mask
    return anchor_masks


def directional_gap_fill(mask: np.ndarray, bridge_length: int = 15) -> np.ndarray:
    """Fill gaps in trail lines using directional morphological closing.

    Instead of isotropic dilation (which creates blobs), uses thin elongated
    kernels at multiple angles to bridge gaps along the trail direction.
    This bridges text gaps without flooding surrounding terrain.
    """
    result = mask.copy()
    for angle in range(0, 180, 15):  # 12 directions
        length = bridge_length
        kern = np.zeros((length, length), dtype=np.uint8)
        center = length // 2
        dx = np.cos(np.radians(angle))
        dy = np.sin(np.radians(angle))
        for t in range(-center, center + 1):
            x = int(center + t * dx)
            y = int(center + t * dy)
            if 0 <= x < length and 0 <= y < length:
                kern[y, x] = 1
        closed = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kern, iterations=1)
        result = cv2.bitwise_or(result, closed)
    return result


def cleanup_mask(mask: np.ndarray, min_area: int = 100) -> np.ndarray:
    """Remove small connected components."""
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(mask)
    for i in range(1, num_labels):
        if stats[i, cv2.CC_STAT_AREA] < min_area:
            mask[labels == i] = 0
    return mask


def detect_black_trails(img: np.ndarray, hsv_img: np.ndarray,
                        existing_masks: dict, mountain_mask: np.ndarray,
                        text_mask: np.ndarray) -> np.ndarray:
    """Detect black trails using adaptive thresholding within mountain mask.

    Black trail lines look like dark text — so we do NOT remove text from
    this detection (it would remove trails too). Instead we rely on
    geometric heuristics in Step 3 to distinguish trails from text.
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Adaptive threshold: finds locally-dark features
    # blockSize=15 and C=7 give more stable thresholds than 11/5, reducing noise
    adaptive = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV, blockSize=15, C=7
    )

    # Constrain to mountain mask
    adaptive = cv2.bitwise_and(adaptive, mountain_mask)

    # Darkness constraint — must be genuinely dark (V < 120), not just
    # locally darker than surroundings. Black trail lines are typically V < 80.
    v_channel = hsv_img[:, :, 2]
    dark_enough = (v_channel < 120).astype(np.uint8) * 255
    adaptive = cv2.bitwise_and(adaptive, dark_enough)

    # Subtract colored trail masks and lifts — minimal dilation to preserve
    # black trails that run alongside colored trails
    for name, mask in existing_masks.items():
        if name != "black":
            dilated = cv2.dilate(mask, np.ones((3, 3), np.uint8), iterations=1)
            adaptive = cv2.bitwise_and(adaptive, cv2.bitwise_not(dilated))

    # Morphological cleanup — light MORPH_OPEN to clean noise while preserving
    # thin trail lines. Use smaller kernel (2x2) with 1 iteration instead of
    # 3x3 which was too aggressive for thin lines.
    kernel_small = np.ones((2, 2), np.uint8)
    kernel = np.ones((3, 3), np.uint8)
    adaptive = cv2.morphologyEx(adaptive, cv2.MORPH_OPEN, kernel_small, iterations=1)
    adaptive = cv2.morphologyEx(adaptive, cv2.MORPH_CLOSE, kernel, iterations=2)

    # Directional gap fill (bridges text gaps along trail direction)
    adaptive = directional_gap_fill(adaptive)

    # Remove tiny fragments
    adaptive = cleanup_mask(adaptive, min_area=50)

    # Remove compact blobs (buildings, large terrain patches)
    # But exempt components near black difficulty symbols — those are real trails.
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(adaptive)
    for i in range(1, num_labels):
        ww = stats[i, cv2.CC_STAT_WIDTH]
        hh = stats[i, cv2.CC_STAT_HEIGHT]
        area = stats[i, cv2.CC_STAT_AREA]
        aspect = max(ww, hh) / max(min(ww, hh), 1)
        if aspect < 2.5 and area > 300:
            adaptive[labels == i] = 0

    return adaptive


def run_segmentation(img: np.ndarray) -> dict:
    """Run full color segmentation pipeline."""
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, w = img.shape[:2]
    masks = {}

    # Step 1: Mountain mask from yellow boundary
    print("  Creating mountain mask from yellow boundary...")
    mountain_mask = create_mountain_mask(hsv)
    mountain_pct = np.count_nonzero(mountain_mask) / mountain_mask.size * 100
    print(f"    Mountain region: {np.count_nonzero(mountain_mask):,} pixels ({mountain_pct:.1f}%)")
    masks["_mountain"] = mountain_mask
    cv2.imwrite(str(MASKS_DIR / "mountain_mask.png"), mountain_mask)

    # Step 2: Detect and mask trail name text
    print("  Detecting trail name text...")
    text_mask = create_text_mask(hsv, mountain_mask)
    print(f"    Text mask: {np.count_nonzero(text_mask):,} pixels")
    cv2.imwrite(str(MASKS_DIR / "text_mask.png"), text_mask)

    # Step 2b: Inpaint text regions in the original image
    # This fills text areas with surrounding trail line colors, so that
    # color detection captures continuous trails THROUGH trail name text.
    print("  Inpainting text regions...")
    inpaint_mask = cv2.dilate(text_mask, np.ones((3, 3), np.uint8), iterations=1)
    inpainted_img = cv2.inpaint(img, inpaint_mask, inpaintRadius=5, flags=cv2.INPAINT_TELEA)
    hsv_inpainted = cv2.cvtColor(inpainted_img, cv2.COLOR_BGR2HSV)
    print(f"    Inpainted {np.count_nonzero(inpaint_mask):,} pixels")

    # Step 3: Detect difficulty symbols
    print("  Detecting difficulty symbols (■ ◆ ●)...")
    symbols = detect_difficulty_symbols(hsv, mountain_mask)
    for color, positions in symbols.items():
        print(f"    {color}: {len(positions)} symbols found")
    anchor_masks = create_symbol_anchor_mask(symbols, (h, w))

    # Save symbol positions
    symbol_data = {color: [(int(x), int(y)) for x, y in pos]
                   for color, pos in symbols.items()}
    (OUTPUT_DIR / "symbols.json").write_text(json.dumps(symbol_data, indent=2))

    # Step 4: Multi-scale trail color segmentation
    # HIGH saturation (S>=120/130): confident trail lines, minimal terrain
    # LOW saturation (S>=50/80): includes terrain noise
    # Keep LOW pixels only if they're in a component that touches HIGH pixels.
    # This captures faint trail sections while rejecting terrain patches.
    raw_color_masks = {}
    print("\n  --- Trail colors (multi-scale) ---")
    for color_name in TRAIL_COLOR_RANGES:
        ranges_low = TRAIL_COLOR_RANGES_LOW.get(color_name, TRAIL_COLOR_RANGES[color_name])
        ranges_high = TRAIL_COLOR_RANGES_HIGH.get(color_name, TRAIL_COLOR_RANGES[color_name])
        print(f"  Segmenting {color_name}...")

        # Detect LOW confidence from both original + inpainted
        mask_lo_orig = segment_color(hsv, ranges_low)
        mask_lo_orig = cv2.bitwise_and(mask_lo_orig, mountain_mask)
        mask_lo_inp = segment_color(hsv_inpainted, ranges_low)
        mask_lo_inp = cv2.bitwise_and(mask_lo_inp, mountain_mask)
        mask_lo = cv2.bitwise_or(mask_lo_orig, mask_lo_inp)

        # Detect HIGH confidence
        mask_hi_orig = segment_color(hsv, ranges_high)
        mask_hi_orig = cv2.bitwise_and(mask_hi_orig, mountain_mask)
        mask_hi_inp = segment_color(hsv_inpainted, ranges_high)
        mask_hi_inp = cv2.bitwise_and(mask_hi_inp, mountain_mask)
        mask_hi = cv2.bitwise_or(mask_hi_orig, mask_hi_inp)

        # Boost HIGH mask with symbol anchors — difficulty symbols are
        # definitive evidence of a trail, so treat them as HIGH confidence.
        # This ensures LOW-confidence trail components near symbols survive
        # the multi-scale filter even if the trail is faint.
        if color_name in anchor_masks:
            symbol_boost = cv2.dilate(anchor_masks[color_name],
                                       np.ones((5, 5), np.uint8), iterations=2)
            mask_hi = cv2.bitwise_or(mask_hi, cv2.bitwise_and(symbol_boost, mountain_mask))

        hi_px = np.count_nonzero(mask_hi)
        lo_px = np.count_nonzero(mask_lo)
        print(f"    High confidence: {hi_px:,} px, Low: {lo_px:,} px")

        # Multi-scale filter: keep LOW components only if >=10% of their pixels
        # are HIGH-confidence. This ensures the component is actually on a drawn
        # trail line (where colors are vivid) rather than on diffuse terrain.
        # Small components (<100px) are kept if they contain ANY high pixel.
        num_lo_labels, lo_labels, lo_stats, _ = cv2.connectedComponentsWithStats(mask_lo)
        mask = np.zeros_like(mask_lo)
        kept_components = 0
        for i in range(1, num_lo_labels):
            area = lo_stats[i, cv2.CC_STAT_AREA]
            comp_pixels = (lo_labels == i)
            hi_count = np.count_nonzero(mask_hi[comp_pixels])
            # Small components (<200px): keep if any high pixel present
            # Large components: require >=25% high-confidence pixels
            # This removes terrain blobs (diffuse, low S) while keeping
            # trail lines (vivid, high S making up >25% of the line width)
            if area < 200:
                keep = hi_count > 0
            else:
                keep = hi_count >= area * 0.25
            if keep:
                mask[comp_pixels] = 255
                kept_components += 1
        print(f"    Multi-scale filter: {kept_components}/{num_lo_labels-1} components kept")

        inpaint_extra = np.count_nonzero(mask_lo) - np.count_nonzero(mask_lo_orig)
        if inpaint_extra > 0:
            print(f"    Inpainting recovered {inpaint_extra:,} additional pixels")

        # Cleanup small components
        mask = cleanup_mask(mask, min_area=50)

        # Width-ratio filter: remove fat terrain blobs
        # Trail lines have area/skeleton_length < 12 (thin)
        # Terrain blobs have ratio > 15 (fat)
        from skimage.morphology import skeletonize as _skel
        num_l2, lbl2, st2, _ = cv2.connectedComponentsWithStats(mask)
        for i2 in range(1, num_l2):
            a2 = st2[i2, cv2.CC_STAT_AREA]
            if a2 < 200:
                continue
            cx2 = st2[i2, cv2.CC_STAT_LEFT]
            cy2 = st2[i2, cv2.CC_STAT_TOP]
            cw2 = st2[i2, cv2.CC_STAT_WIDTH]
            ch2 = st2[i2, cv2.CC_STAT_HEIGHT]
            comp = (lbl2[cy2:cy2+ch2, cx2:cx2+cw2] == i2).astype(np.uint8)
            skel = _skel(comp > 0)
            sl = float(np.count_nonzero(skel))
            if sl > 0 and a2 / sl > 15:
                mask[lbl2 == i2] = 0

        # Save raw mask (before gap-fill) for black trail subtraction
        # Add anchors to raw mask so they're available for subtraction reference
        if color_name in anchor_masks:
            mask = cv2.bitwise_or(mask, cv2.bitwise_and(anchor_masks[color_name], mountain_mask))
        raw_color_masks[color_name] = mask.copy()

        # Directional gap fill to bridge text gaps
        mask = directional_gap_fill(mask, bridge_length=15)
        # Re-apply mountain mask — gap-fill can extend pixels outside boundary
        mask = cv2.bitwise_and(mask, mountain_mask)
        # Re-apply width-ratio filter after gap-fill (blobs may have grown)
        num_l3, lbl3, st3, _ = cv2.connectedComponentsWithStats(mask)
        for i3 in range(1, num_l3):
            a3 = st3[i3, cv2.CC_STAT_AREA]
            if a3 < 200:
                continue
            cx3 = st3[i3, cv2.CC_STAT_LEFT]
            cy3 = st3[i3, cv2.CC_STAT_TOP]
            cw3 = st3[i3, cv2.CC_STAT_WIDTH]
            ch3 = st3[i3, cv2.CC_STAT_HEIGHT]
            comp3 = (lbl3[cy3:cy3+ch3, cx3:cx3+cw3] == i3).astype(np.uint8)
            skel3 = _skel(comp3 > 0)
            sl3 = float(np.count_nonzero(skel3))
            if sl3 > 0 and a3 / sl3 > 15:
                mask[lbl3 == i3] = 0
        mask = cleanup_mask(mask, min_area=30)

        # Re-add symbol anchors AFTER all filtering — anchors should never
        # be removed by width-ratio or cleanup filters since they represent
        # definitive trail locations.
        if color_name in anchor_masks:
            mask = cv2.bitwise_or(mask, cv2.bitwise_and(anchor_masks[color_name], mountain_mask))

        masks[color_name] = mask
        num_labels = cv2.connectedComponentsWithStats(mask)[0] - 1
        pixel_count = np.count_nonzero(mask)
        print(f"    {pixel_count:,} pixels ({pixel_count / mask.size * 100:.2f}%), {num_labels} components")

    # Step 5: Black trails via adaptive thresholding
    # Use RAW color masks (not gap-filled) for subtraction to avoid eating black trails
    # Pass the inpainted image so text gaps are filled before thresholding
    print("  Detecting black trails (adaptive threshold)...")
    masks["black"] = detect_black_trails(inpainted_img, hsv, raw_color_masks, mountain_mask, text_mask)
    # Add black symbol anchors
    if "black" in anchor_masks:
        masks["black"] = cv2.bitwise_or(masks["black"], anchor_masks["black"])
    pixel_count = np.count_nonzero(masks["black"])
    num_labels = cv2.connectedComponentsWithStats(masks["black"])[0] - 1
    print(f"    {pixel_count:,} pixels ({pixel_count / masks['black'].size * 100:.2f}%), {num_labels} components")

    # Step 6: Segment lift colors (tracked separately)
    print("\n  --- Lift lines ---")
    for color_name, ranges in LIFT_COLOR_RANGES.items():
        print(f"  Segmenting {color_name}...")
        mask = segment_color(hsv, ranges)
        mask = cv2.bitwise_and(mask, mountain_mask)
        mask = cleanup_mask(mask, min_area=500)
        masks[color_name] = mask
        pixel_count = np.count_nonzero(mask)
        print(f"    {pixel_count:,} pixels ({pixel_count / mask.size * 100:.2f}%)")

    # Other (boundaries)
    for color_name, ranges in OTHER_COLOR_RANGES.items():
        mask = segment_color(hsv, ranges)
        mask = cleanup_mask(mask)
        masks[color_name] = mask

    # Step 7: Subtract lift masks from trail masks
    print("\n  Subtracting lift lines from trail masks...")
    combined_lifts = np.zeros((h, w), dtype=np.uint8)
    for lift_name in LIFT_COLOR_RANGES:
        if lift_name in masks:
            dilated_lift = cv2.dilate(masks[lift_name], np.ones((5, 5), np.uint8), iterations=1)
            combined_lifts = cv2.bitwise_or(combined_lifts, dilated_lift)

    for trail_name in list(TRAIL_COLOR_RANGES.keys()) + ["black"]:
        if trail_name in masks:
            before = np.count_nonzero(masks[trail_name])
            masks[trail_name] = cv2.bitwise_and(masks[trail_name], cv2.bitwise_not(combined_lifts))
            after = np.count_nonzero(masks[trail_name])
            removed = before - after
            if removed > 0:
                print(f"    {trail_name}: removed {removed:,} lift-overlap pixels")

    return masks


def save_masks(masks: dict):
    """Save each mask as a PNG file."""
    MASKS_DIR.mkdir(parents=True, exist_ok=True)
    for name, mask in masks.items():
        if name.startswith("_"):
            continue  # skip internal masks
        path = MASKS_DIR / f"{name}_mask.png"
        cv2.imwrite(str(path), mask)
        print(f"  Saved {path}")


def save_composite_overlay(img: np.ndarray, masks: dict):
    """Save a composite image showing all masks overlaid on the original."""
    overlay = img.copy()
    for name, mask in masks.items():
        if name.startswith("_"):
            continue
        color = VIS_COLORS_BGR.get(name, (255, 255, 255))
        colored = np.zeros_like(img)
        colored[:] = color
        mask_3ch = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR) // 255
        overlay = cv2.addWeighted(overlay, 1.0, colored * mask_3ch, 0.4, 0)

    path = OUTPUT_DIR / "color_overlay.png"
    cv2.imwrite(str(path), overlay)
    print(f"  Saved composite overlay to {path}")


def interactive_tune(img: np.ndarray):
    """Interactive HSV threshold tuning with OpenCV trackbars."""
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    scale = 1200 / max(img.shape[1], img.shape[0])
    display_size = (int(img.shape[1] * scale), int(img.shape[0] * scale))

    cv2.namedWindow("HSV Tuner", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("HSV Tuner", display_size[0], display_size[1])

    cv2.createTrackbar("H Low", "HSV Tuner", 0, 180, lambda x: None)
    cv2.createTrackbar("H High", "HSV Tuner", 180, 180, lambda x: None)
    cv2.createTrackbar("S Low", "HSV Tuner", 0, 255, lambda x: None)
    cv2.createTrackbar("S High", "HSV Tuner", 255, 255, lambda x: None)
    cv2.createTrackbar("V Low", "HSV Tuner", 0, 255, lambda x: None)
    cv2.createTrackbar("V High", "HSV Tuner", 255, 255, lambda x: None)

    print("\nInteractive HSV tuning mode. Press 'q' to quit.")
    while True:
        h_lo = cv2.getTrackbarPos("H Low", "HSV Tuner")
        h_hi = cv2.getTrackbarPos("H High", "HSV Tuner")
        s_lo = cv2.getTrackbarPos("S Low", "HSV Tuner")
        s_hi = cv2.getTrackbarPos("S High", "HSV Tuner")
        v_lo = cv2.getTrackbarPos("V Low", "HSV Tuner")
        v_hi = cv2.getTrackbarPos("V High", "HSV Tuner")

        mask = cv2.inRange(hsv, np.array([h_lo, s_lo, v_lo]), np.array([h_hi, s_hi, v_hi]))
        result = img.copy()
        result[mask > 0] = [0, 255, 0]
        cv2.imshow("HSV Tuner", cv2.resize(result, display_size))
        if cv2.waitKey(30) & 0xFF == ord("q"):
            break
    cv2.destroyAllWindows()


def main():
    parser = argparse.ArgumentParser(description="Color segmentation of trail map")
    parser.add_argument("--tune", action="store_true", help="Interactive HSV tuning mode")
    args = parser.parse_args()

    print("Loading image...")
    img = load_image()
    print(f"  Image size: {img.shape[1]}x{img.shape[0]}")

    MASKS_DIR.mkdir(parents=True, exist_ok=True)

    if args.tune:
        interactive_tune(img)
        return

    print("\nRunning color segmentation...")
    masks = run_segmentation(img)

    print("\nSaving masks...")
    save_masks(masks)
    save_composite_overlay(img, masks)

    # Save stats
    stats = {}
    for name, mask in masks.items():
        if name.startswith("_"):
            continue
        num_labels = cv2.connectedComponentsWithStats(mask)[0] - 1
        stats[name] = {
            "pixel_count": int(np.count_nonzero(mask)),
            "component_count": num_labels,
            "percentage": round(np.count_nonzero(mask) / mask.size * 100, 3),
        }

    stats_path = OUTPUT_DIR / "segmentation_stats.json"
    stats_path.write_text(json.dumps(stats, indent=2))
    print(f"\nStats saved to {stats_path}")
    print("\nDone! Inspect masks in scripts/output/masks/")


if __name__ == "__main__":
    main()
