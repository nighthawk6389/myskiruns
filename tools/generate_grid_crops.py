#!/usr/bin/env python3
"""
Generate a dense grid of high-resolution overlapping crops from the trail map.
Each crop covers ~25% x 30% of the image with ~10% overlap between neighbors.
This ensures every trail label is clearly readable in at least one crop.
"""

import cv2
import os

MAP_PATH = "public/killington-trail-map.jpg"
OUTPUT_DIR = "tools/grid_crops"

def main():
    img = cv2.imread(MAP_PATH)
    h, w = img.shape[:2]
    print(f"Image: {w}x{h}")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Generate overlapping grid crops
    # Each crop covers ~25% width, ~35% height with 10% overlap
    crop_w_pct = 28
    crop_h_pct = 38
    step_x_pct = 18
    step_y_pct = 28

    crop_idx = 0
    for y_start_pct in range(0, 100 - crop_h_pct + 1, step_y_pct):
        for x_start_pct in range(0, 100 - crop_w_pct + 1, step_x_pct):
            x1 = int(x_start_pct / 100 * w)
            y1 = int(y_start_pct / 100 * h)
            x2 = min(int((x_start_pct + crop_w_pct) / 100 * w), w)
            y2 = min(int((y_start_pct + crop_h_pct) / 100 * h), h)

            crop = img[y1:y2, x1:x2]
            crop_h_px, crop_w_px = crop.shape[:2]

            filename = f"grid_{crop_idx:02d}_x{x_start_pct}-{x_start_pct+crop_w_pct}_y{y_start_pct}-{y_start_pct+crop_h_pct}.jpg"
            filepath = os.path.join(OUTPUT_DIR, filename)
            cv2.imwrite(filepath, crop, [cv2.IMWRITE_JPEG_QUALITY, 95])

            print(f"  [{crop_idx:02d}] x={x_start_pct}-{x_start_pct+crop_w_pct}%, "
                  f"y={y_start_pct}-{y_start_pct+crop_h_pct}% → {crop_w_px}x{crop_h_px}px")
            crop_idx += 1

    # Also generate a few extra crops for hard-to-read areas
    # Snowshed (far left, small)
    extras = [
        ("snowshed_zoom", 0, 12, 45, 75),
        ("kp_summit_zoom", 42, 62, 2, 25),
        ("skye_center_zoom", 30, 52, 20, 50),
        ("bear_mtn_zoom", 14, 38, 20, 55),
        ("snowdon_zoom", 60, 82, 15, 45),
        ("ramshead_zoom", 80, 100, 20, 55),
    ]
    for name, x1p, x2p, y1p, y2p in extras:
        x1 = int(x1p / 100 * w)
        y1 = int(y1p / 100 * h)
        x2 = int(x2p / 100 * w)
        y2 = int(y2p / 100 * h)
        crop = img[y1:y2, x1:x2]
        filepath = os.path.join(OUTPUT_DIR, f"extra_{name}.jpg")
        cv2.imwrite(filepath, crop, [cv2.IMWRITE_JPEG_QUALITY, 95])
        print(f"  [extra] {name}: {crop.shape[1]}x{crop.shape[0]}px")

    print(f"\nGenerated {crop_idx + len(extras)} crops in {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
