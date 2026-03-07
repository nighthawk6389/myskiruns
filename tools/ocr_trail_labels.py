#!/usr/bin/env python3
"""
OCR trail labels by rotating each trail path region to horizontal.

For each sweepline-extracted trail path:
1. Compute the path's overall angle from its start to end point
2. Crop a wide band around the trail from the original image
3. Rotate the crop so the trail axis is horizontal
4. Enhance contrast and run Tesseract on the rotated crop
5. The detected text = the trail's label/name
"""

import cv2
import numpy as np
import pytesseract
from pytesseract import Output
import json
import re
import os
from collections import defaultdict

MAP_PATH = "public/killington-trail-map.jpg"


def load_extracted_paths():
    """Load the sweepline-extracted paths from the JSON output."""
    # Re-run sweepline extraction or load from saved data
    # For now, parse from the TS file
    with open("src/data/trailPaths.ts", 'r') as f:
        content = f.read()

    paths = {}
    # Match: 'trail-id': [[[x1, y1], ...]]
    pattern = r"'([a-z][a-z0-9-]+)':\s*\[\[(.+?)\]\]"
    for match in re.finditer(pattern, content):
        trail_id = match.group(1)
        points_str = match.group(2)
        point_pattern = r'\[(\d+\.?\d*),\s*(\d+\.?\d*)\]'
        points = [(float(x), float(y)) for x, y in re.findall(point_pattern, points_str)]
        if points:
            paths[trail_id] = points
    return paths


def get_path_angle(points):
    """Compute the overall angle of a path from start to end."""
    if len(points) < 2:
        return 0

    # Use start and end points
    x1, y1 = points[0]
    x2, y2 = points[-1]

    # Also try using a line fit for more robustness
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]

    # Fit a line y = mx + b
    if len(points) >= 3:
        pts = np.array(points)
        # Use PCA to find principal direction
        mean = np.mean(pts, axis=0)
        centered = pts - mean
        cov = np.cov(centered.T)
        eigenvalues, eigenvectors = np.linalg.eigh(cov)
        # Principal direction
        principal = eigenvectors[:, np.argmax(eigenvalues)]
        angle_rad = np.arctan2(principal[1], principal[0])
    else:
        angle_rad = np.arctan2(y2 - y1, x2 - x1)

    return np.degrees(angle_rad)


def crop_and_rotate_trail(img, points, w, h, band_width_pct=3.0, padding_pct=2.0):
    """
    Crop a region around the trail path and rotate it so the trail is horizontal.

    Returns the rotated crop image, or None if the crop is too small.
    """
    # Convert percentage points to pixel coordinates
    px_points = [(int(x / 100 * w), int(y / 100 * h)) for x, y in points]

    # Get bounding box of all points
    xs = [p[0] for p in px_points]
    ys = [p[1] for p in px_points]

    x_min, x_max = min(xs), max(xs)
    y_min, y_max = min(ys), max(ys)

    # Add padding
    pad_x = int(padding_pct / 100 * w)
    pad_y = int(band_width_pct / 100 * h)  # Wider band perpendicular to trail

    x_min = max(0, x_min - pad_x)
    x_max = min(w, x_max + pad_x)
    y_min = max(0, y_min - pad_y)
    y_max = min(h, y_max + pad_y)

    crop_w = x_max - x_min
    crop_h = y_max - y_min

    if crop_w < 20 or crop_h < 20:
        return None, 0

    # Crop the region
    crop = img[y_min:y_max, x_min:x_max].copy()

    # Get path angle
    angle = get_path_angle(points)

    # Rotate the crop so the trail is horizontal
    # The center of rotation is the center of the crop
    center = (crop_w // 2, crop_h // 2)

    # We want to rotate by -angle to make horizontal
    M = cv2.getRotationMatrix2D(center, angle, 1.0)

    # Calculate new bounding box size after rotation
    cos = abs(M[0, 0])
    sin = abs(M[0, 1])
    new_w = int(crop_h * sin + crop_w * cos)
    new_h = int(crop_h * cos + crop_w * sin)

    # Adjust the rotation matrix
    M[0, 2] += (new_w - crop_w) / 2
    M[1, 2] += (new_h - crop_h) / 2

    rotated = cv2.warpAffine(crop, M, (new_w, new_h),
                              borderMode=cv2.BORDER_REPLICATE)

    return rotated, angle


def enhance_for_ocr(img):
    """Enhance a crop image for better OCR results."""
    results = []

    # Method 1: Grayscale + adaptive threshold
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Method 2: Increase contrast
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    # Method 3: Invert (some labels are light text on dark background)
    inverted = cv2.bitwise_not(enhanced)

    # Method 4: Scale up (text may be very small)
    scale = 2
    scaled = cv2.resize(enhanced, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    scaled_inv = cv2.resize(inverted, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

    return [
        ('enhanced', enhanced),
        ('inverted', inverted),
        ('scaled', scaled),
        ('scaled_inv', scaled_inv),
    ]


def ocr_crop(img, methods=None):
    """Run OCR on a crop with multiple preprocessing methods."""
    if methods is None:
        methods = enhance_for_ocr(img)

    all_texts = []

    for name, processed in methods:
        # Try different PSM modes
        for psm in [7, 11]:  # 7=single line, 11=sparse text
            try:
                text = pytesseract.image_to_string(
                    processed,
                    config=f'--psm {psm} --oem 3'
                ).strip()
                if text and len(text) >= 2:
                    # Clean up the text
                    cleaned = re.sub(r'[^a-zA-Z\s\'-]', '', text).strip()
                    if len(cleaned) >= 2:
                        all_texts.append({
                            'text': cleaned,
                            'raw': text,
                            'method': name,
                            'psm': psm,
                        })
            except Exception:
                pass

    return all_texts


def match_text_to_trail_names(ocr_texts, known_names):
    """
    Try to match OCR-detected text to known trail names.
    Uses fuzzy matching since OCR may not be perfect.
    """
    from difflib import SequenceMatcher

    best_match = None
    best_score = 0

    for item in ocr_texts:
        text = item['text'].lower().strip()
        if len(text) < 2:
            continue

        for name in known_names:
            name_lower = name.lower()

            # Exact substring match
            if name_lower in text or text in name_lower:
                score = len(name_lower) / max(len(text), len(name_lower))
                score = max(score, 0.8)  # Boost substring matches
            else:
                # Fuzzy match
                score = SequenceMatcher(None, text, name_lower).ratio()

            # Also try matching individual words
            text_words = set(text.split())
            name_words = set(name_lower.split())
            if text_words and name_words:
                word_overlap = len(text_words & name_words) / max(len(text_words), len(name_words))
                score = max(score, word_overlap)

            if score > best_score:
                best_score = score
                best_match = {
                    'name': name,
                    'detected': item['text'],
                    'score': score,
                    'method': item['method'],
                    'psm': item['psm'],
                }

    return best_match


def main():
    img = cv2.imread(MAP_PATH)
    h, w = img.shape[:2]
    print(f"Image: {w}x{h}")

    # Load extracted trail paths
    paths = load_extracted_paths()
    print(f"Loaded {len(paths)} trail paths from trailPaths.ts")

    # Load known trail names
    with open("src/data/trails.ts", 'r') as f:
        content = f.read()

    known_names = []
    name_pattern = r"name:\s*'([^']+)'"
    for match in re.finditer(name_pattern, content):
        known_names.append(match.group(1))
    known_names = list(set(known_names))
    print(f"Known trail names: {len(known_names)}")

    # Also create trail_id -> name mapping
    id_to_name = {}
    id_pattern = r"id:\s*'([^']+)',\s*name:\s*'([^']+)'"
    for match in re.finditer(id_pattern, content):
        id_to_name[match.group(1)] = match.group(2)

    # Process each trail path
    results = {}
    debug_crops = []

    os.makedirs("tools/ocr_crops", exist_ok=True)

    print(f"\nProcessing {len(paths)} trail paths...")
    for trail_id, points in paths.items():
        # Crop and rotate
        rotated, angle = crop_and_rotate_trail(img, points, w, h,
                                                band_width_pct=2.5, padding_pct=3.0)
        if rotated is None:
            results[trail_id] = {'status': 'no_crop', 'texts': []}
            continue

        # Save crop for debugging
        crop_path = f"tools/ocr_crops/{trail_id}.jpg"
        cv2.imwrite(crop_path, rotated, [cv2.IMWRITE_JPEG_QUALITY, 90])

        # OCR the rotated crop
        texts = ocr_crop(rotated)

        # Match to known trail names
        match = match_text_to_trail_names(texts, known_names)

        results[trail_id] = {
            'status': 'matched' if match and match['score'] > 0.5 else 'unmatched',
            'texts': [{'text': t['text'], 'method': t['method'], 'psm': t['psm']}
                      for t in texts[:10]],
            'match': match,
            'angle': round(angle, 1),
            'expected_name': id_to_name.get(trail_id, '?'),
        }

    # Print results summary
    print("\n" + "=" * 70)
    print("  OCR RESULTS")
    print("=" * 70)

    matched_correct = 0
    matched_wrong = 0
    unmatched = 0

    for trail_id, result in sorted(results.items()):
        expected = result.get('expected_name', '?')
        match = result.get('match')
        status = result['status']

        if match and match['score'] > 0.5:
            is_correct = match['name'].lower() == expected.lower()
            if is_correct:
                matched_correct += 1
                symbol = "✓"
            else:
                matched_wrong += 1
                symbol = "✗"
            print(f"  {symbol} {trail_id}: expected='{expected}', "
                  f"OCR='{match['detected']}' → '{match['name']}' "
                  f"(score={match['score']:.2f}, {match['method']}/psm{match['psm']})")
        else:
            unmatched += 1
            texts_preview = ", ".join(f"'{t['text']}'" for t in result.get('texts', [])[:3])
            if texts_preview:
                print(f"  ? {trail_id}: expected='{expected}', raw OCR: {texts_preview}")
            else:
                print(f"  - {trail_id}: expected='{expected}', no text detected")

    print(f"\n  Summary: {matched_correct} correct, {matched_wrong} wrong, {unmatched} unmatched")
    print(f"  Total: {len(results)} trails")

    # Save full results
    with open("tools/ocr_trail_results.json", 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print("  Saved to tools/ocr_trail_results.json")


if __name__ == "__main__":
    main()
