#!/usr/bin/env python3
"""
Create a visualization of detected trail lines overlaid on the map,
with grid lines and coordinate labels to help map trails accurately.
"""

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

MAP_PATH = "public/killington-trail-map.jpg"
OUTPUT_PATH = "tools/trail_overlay.jpg"

def main():
    img = cv2.imread(MAP_PATH)
    h, w = img.shape[:2]
    print(f"Image: {w}x{h}")

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Create output visualization
    viz = img.copy()

    # Detect trail colors
    cyan_mask = cv2.inRange(hsv, np.array([85, 50, 120]), np.array([115, 255, 255]))
    pink_mask = cv2.inRange(hsv, np.array([140, 50, 120]), np.array([175, 255, 255]))
    yellow_mask = cv2.inRange(hsv, np.array([20, 50, 120]), np.array([50, 255, 255]))

    # Clean up masks
    kernel = np.ones((3, 3), np.uint8)
    for mask in [cyan_mask, pink_mask, yellow_mask]:
        cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2, dst=mask)

    # Overlay detected trails in bright colors
    # Cyan trails -> bright blue overlay
    viz[cyan_mask > 0] = [255, 100, 0]  # bright blue in BGR
    # Pink trails -> bright magenta overlay
    viz[pink_mask > 0] = [255, 0, 255]  # magenta in BGR
    # Yellow trails -> bright yellow overlay
    viz[yellow_mask > 0] = [0, 255, 255]  # yellow in BGR

    # Draw grid lines with percentage labels
    for pct in range(0, 101, 5):
        x = int(pct / 100 * w)
        y = int(pct / 100 * h)

        # Vertical lines
        if x < w:
            color = (0, 0, 255) if pct % 10 == 0 else (0, 0, 128)
            thickness = 2 if pct % 10 == 0 else 1
            cv2.line(viz, (x, 0), (x, h), color, thickness)
            if pct % 10 == 0:
                cv2.putText(viz, f"{pct}%", (x + 5, 40), cv2.FONT_HERSHEY_SIMPLEX,
                           1.5, (0, 0, 255), 3)

        # Horizontal lines
        if y < h:
            color = (0, 0, 255) if pct % 10 == 0 else (0, 0, 128)
            thickness = 2 if pct % 10 == 0 else 1
            cv2.line(viz, (0, y), (w, y), color, thickness)
            if pct % 10 == 0:
                cv2.putText(viz, f"{pct}%", (5, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
                           1.5, (0, 0, 255), 3)

    # Add legend
    legend_y = h - 120
    cv2.rectangle(viz, (10, legend_y), (700, h - 10), (0, 0, 0), -1)
    cv2.putText(viz, "Blue=Cyan trails  ", (20, legend_y + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 100, 0), 2)
    cv2.putText(viz, "Magenta=Pink trails  ", (20, legend_y + 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 255), 2)
    cv2.putText(viz, "Yellow=Green trails  ", (20, legend_y + 90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

    cv2.imwrite(OUTPUT_PATH, viz, [cv2.IMWRITE_JPEG_QUALITY, 85])
    print(f"Saved visualization to {OUTPUT_PATH}")

    # Also create a smaller version for easier viewing
    small = cv2.resize(viz, (w // 2, h // 2))
    cv2.imwrite("tools/trail_overlay_small.jpg", small, [cv2.IMWRITE_JPEG_QUALITY, 85])
    print(f"Saved small version to tools/trail_overlay_small.jpg")

    # Now analyze specific regions to identify peaks
    print("\n=== Regional Analysis ===")
    print("Looking at trail density in different map quadrants:\n")

    # Divide into regions and count trail pixels
    regions = [
        ("Far Left (0-15%)", 0, 15),
        ("Left (15-30%)", 15, 30),
        ("Center-Left (30-45%)", 30, 45),
        ("Center (45-60%)", 45, 60),
        ("Center-Right (60-75%)", 60, 75),
        ("Right (75-90%)", 75, 90),
        ("Far Right (90-100%)", 90, 100),
    ]

    all_trails = cv2.bitwise_or(cyan_mask, pink_mask)
    all_trails = cv2.bitwise_or(all_trails, yellow_mask)

    for name, x_start, x_end in regions:
        x1 = int(x_start / 100 * w)
        x2 = int(x_end / 100 * w)
        region = all_trails[:, x1:x2]

        total_px = region.shape[0] * region.shape[1]
        trail_px = cv2.countNonZero(region)
        pct = trail_px / total_px * 100

        # Find vertical extent of trails
        row_has_trail = np.any(region > 0, axis=1)
        trail_rows = np.where(row_has_trail)[0]
        if len(trail_rows) > 0:
            y_top = trail_rows[0] / h * 100
            y_bottom = trail_rows[-1] / h * 100

            # Count cyan/pink/yellow separately
            cyan_px = cv2.countNonZero(cyan_mask[:, x1:x2])
            pink_px = cv2.countNonZero(pink_mask[:, x1:x2])
            yellow_px = cv2.countNonZero(yellow_mask[:, x1:x2])

            print(f"  {name}:")
            print(f"    Trail coverage: {pct:.1f}%")
            print(f"    Vertical extent: y={y_top:.1f}% to y={y_bottom:.1f}%")
            print(f"    Cyan: {cyan_px:,}px, Pink: {pink_px:,}px, Yellow: {yellow_px:,}px")
        else:
            print(f"  {name}: No trails detected")

    # Find the label/text regions (dark rectangular signs)
    print("\n=== Sign/Label Detection ===")
    print("Looking for dark rectangular signs (peak labels):\n")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Signs are very dark rectangles
    _, dark_mask = cv2.threshold(gray, 30, 255, cv2.THRESH_BINARY_INV)

    # Remove tiny noise
    kernel_big = np.ones((5, 5), np.uint8)
    dark_mask = cv2.morphologyEx(dark_mask, cv2.MORPH_OPEN, kernel_big, iterations=2)
    dark_mask = cv2.morphologyEx(dark_mask, cv2.MORPH_CLOSE, kernel_big, iterations=2)

    contours, _ = cv2.findContours(dark_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    signs = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < 2000 or area > 100000:
            continue
        x, y, bw, bh = cv2.boundingRect(cnt)
        # Signs are roughly rectangular and wider than tall
        aspect = bw / max(bh, 1)
        if 1.2 < aspect < 8 and bw > 50 and bh > 20:
            signs.append({
                'cx': (x + bw / 2) / w * 100,
                'cy': (y + bh / 2) / h * 100,
                'w': bw / w * 100,
                'h': bh / h * 100,
            })

    signs.sort(key=lambda s: s['cx'])
    for s in signs:
        print(f"  Sign at ({s['cx']:.1f}%, {s['cy']:.1f}%), "
              f"size=({s['w']:.1f}% x {s['h']:.1f}%)")

if __name__ == "__main__":
    main()
