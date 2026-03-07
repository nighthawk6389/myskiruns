#!/usr/bin/env python3
"""
Create zoomed crops of each peak region with percentage grid overlays.
Uses sign positions to determine peak boundaries.
"""

import cv2
import numpy as np

MAP_PATH = "public/killington-trail-map.jpg"

# Peak regions based on sign positions and map analysis
# Format: { peak_id: (x_min%, y_min%, x_max%, y_max%) }
PEAK_REGIONS = {
    'snowshed':       (0, 40, 12, 95),
    'sunrise':        (2, 25, 18, 80),
    'bear-mountain':  (12, 10, 38, 75),
    'skye-peak':      (28, 5, 58, 70),
    'killington-peak':(42, 3, 68, 70),
    'snowdon':        (62, 10, 88, 75),
    'ramshead':       (80, 15, 100, 85),
}

def main():
    img = cv2.imread(MAP_PATH)
    h, w = img.shape[:2]
    print(f"Image: {w}x{h}")

    for peak_id, (x1p, y1p, x2p, y2p) in PEAK_REGIONS.items():
        # Convert percentage to pixels
        x1 = int(x1p / 100 * w)
        y1 = int(y1p / 100 * h)
        x2 = int(x2p / 100 * w)
        y2 = int(y2p / 100 * h)

        crop = img[y1:y2, x1:x2].copy()
        ch, cw = crop.shape[:2]

        # Draw percentage grid lines (every 2% of full image)
        for pct_x in range(0, 101, 2):
            px = int((pct_x - x1p) / (x2p - x1p) * cw)
            if 0 <= px < cw:
                # Thin line every 2%, thick every 10%
                thickness = 2 if pct_x % 10 == 0 else 1
                color = (0, 0, 255) if pct_x % 10 == 0 else (0, 0, 180)
                cv2.line(crop, (px, 0), (px, ch), color, thickness)
                if pct_x % 5 == 0:
                    cv2.putText(crop, f"{pct_x}%", (px + 2, 20),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

        for pct_y in range(0, 101, 2):
            py = int((pct_y - y1p) / (y2p - y1p) * ch)
            if 0 <= py < ch:
                thickness = 2 if pct_y % 10 == 0 else 1
                color = (0, 0, 255) if pct_y % 10 == 0 else (0, 0, 180)
                cv2.line(crop, (0, py), (cw, py), color, thickness)
                if pct_y % 5 == 0:
                    cv2.putText(crop, f"{pct_y}%", (2, py - 3),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

        # Save at higher resolution for detail
        scale = max(1, 2000 // max(cw, ch) + 1)
        if scale > 1:
            crop = cv2.resize(crop, (cw * scale, ch * scale), interpolation=cv2.INTER_CUBIC)

        out_path = f"tools/peak_{peak_id}.jpg"
        cv2.imwrite(out_path, crop, [cv2.IMWRITE_JPEG_QUALITY, 92])
        print(f"Saved {out_path} ({cw}x{ch} -> {cw*scale}x{ch*scale})")

if __name__ == "__main__":
    main()
