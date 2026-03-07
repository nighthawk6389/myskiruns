#!/usr/bin/env python3
"""
Find and extract the sign/label regions on the trail map to identify
which peak is which. Signs are dark rectangles with white text.
Also extract enlarged crops of each sign for reading.
"""

import cv2
import numpy as np

MAP_PATH = "public/killington-trail-map.jpg"

def main():
    img = cv2.imread(MAP_PATH)
    h, w = img.shape[:2]
    print(f"Image: {w}x{h}")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Signs are very dark regions (near black) that are rectangular
    # Use adaptive or simple threshold
    _, dark_mask = cv2.threshold(gray, 35, 255, cv2.THRESH_BINARY_INV)

    # Clean up
    kernel = np.ones((3, 3), np.uint8)
    dark_mask = cv2.morphologyEx(dark_mask, cv2.MORPH_OPEN, kernel, iterations=2)
    dark_mask = cv2.morphologyEx(dark_mask, cv2.MORPH_CLOSE, kernel, iterations=3)

    # Find contours
    contours, _ = cv2.findContours(dark_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    signs = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < 1500 or area > 200000:
            continue

        x, y, bw, bh = cv2.boundingRect(cnt)
        aspect = bw / max(bh, 1)

        # Signs are wider than tall, not too extreme
        if 1.0 < aspect < 10 and bw > 40 and bh > 15:
            signs.append({
                'x': x, 'y': y, 'w': bw, 'h': bh,
                'cx': x + bw // 2, 'cy': y + bh // 2,
                'cx_pct': (x + bw / 2) / w * 100,
                'cy_pct': (y + bh / 2) / h * 100,
                'area': area,
            })

    # Sort left to right
    signs.sort(key=lambda s: s['cx'])

    print(f"\nFound {len(signs)} potential signs:\n")

    # Create visualization with numbered signs
    viz = img.copy()

    for i, s in enumerate(signs):
        print(f"  Sign {i+1}: position=({s['cx_pct']:.1f}%, {s['cy_pct']:.1f}%), "
              f"size={s['w']}x{s['h']}px, area={s['area']}")

        # Draw rectangle on viz
        cv2.rectangle(viz, (s['x'], s['y']), (s['x'] + s['w'], s['y'] + s['h']),
                      (0, 255, 0), 3)
        cv2.putText(viz, f"#{i+1}", (s['x'], s['y'] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 3)

        # Save a cropped, enlarged version of each sign
        # Add some padding
        pad = 10
        crop_y1 = max(0, s['y'] - pad)
        crop_y2 = min(h, s['y'] + s['h'] + pad)
        crop_x1 = max(0, s['x'] - pad)
        crop_x2 = min(w, s['x'] + s['w'] + pad)
        crop = img[crop_y1:crop_y2, crop_x1:crop_x2]

        # Enlarge 3x
        crop_large = cv2.resize(crop, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
        cv2.imwrite(f"tools/sign_{i+1}.jpg", crop_large, [cv2.IMWRITE_JPEG_QUALITY, 95])

    # Save overview
    small = cv2.resize(viz, (w // 2, h // 2))
    cv2.imwrite("tools/signs_overview.jpg", small, [cv2.IMWRITE_JPEG_QUALITY, 85])
    print(f"\nSaved overview to tools/signs_overview.jpg")
    print(f"Saved individual sign crops to tools/sign_N.jpg")

if __name__ == "__main__":
    main()
