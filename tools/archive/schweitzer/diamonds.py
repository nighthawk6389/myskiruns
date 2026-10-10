"""Black diamonds on a Schweitzer print (the Outback map's interactive-map groups have none): solid dark convex
blobs of four corners about as wide as tall, 12 to 30 px, on a white halo (each is turned along its slope, so not
always a square at 45 degrees); two touching (side by side, or one above the other) are a double diamond. Prints them as names.py SYMBOLS rows, each with the nearest label's name (printed.json), for
checking on crops.

    python3 tools/archive/schweitzer/diamonds.py <panel> [x0,y0,x1,y1 to leave out ...]      (repo root)
"""
import json
import math
import sys

import cv2
import numpy as np
from PIL import Image

panel = sys.argv[1]
D = f'work/schweitzer/{panel}'
A = np.asarray(Image.open(f'{D}/map.png').convert('RGB')).astype(int)
dark = (A.max(axis=2) < 110).astype(np.uint8)
bright = A.min(axis=2)
for b in sys.argv[2:]:
    x0, y0, x1, y1 = map(int, b.split(','))
    dark[y0:y1, x0:x1] = 0
n, lab, stats, cent = cv2.connectedComponentsWithStats(dark, 8)
found = []
for i in range(1, n):
    x, y, w, h, area = stats[i]
    if not (12 <= w <= 30 and 12 <= h <= 30 and 0.7 <= w / h <= 1.43):
        continue
    if not 0.42 <= area / (w * h) <= 0.85:
        continue
    blob = (lab[y:y + h, x:x + w] == i).astype(np.uint8)
    cnt, _ = cv2.findContours(blob, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    hull = cv2.convexHull(cnt[0])
    if area / max(1, cv2.contourArea(hull)) < 0.88:
        continue
    # four corners: the hull's polygon simplified to within a tenth of its size has four or five vertices
    if not 4 <= len(cv2.approxPolyDP(hull, 0.1 * max(w, h), True)) <= 5:
        continue
    # printed on a white halo: the ring 2 to 4 px round it is bright
    full = np.zeros(dark.shape, np.uint8)
    y0, x0 = max(0, y - 5), max(0, x - 5)
    sub = (lab[y0:y + h + 5, x0:x + w + 5] == i).astype(np.uint8)
    ring = cv2.dilate(sub, np.ones((9, 9), np.uint8)).astype(bool) & ~cv2.dilate(sub, np.ones((5, 5), np.uint8)).astype(bool)
    if bright[y0:y + h + 5, x0:x + w + 5][ring].mean() < 170:
        continue
    found.append((float(cent[i][0]), float(cent[i][1]), max(w, h)))
used, out = set(), []
for i, (x, y, s) in enumerate(found):
    if i in used:
        continue
    # its pair: a diamond touching it, side by side or (turned along the slope) one above the other
    j = next((j for j, (u, v, t) in enumerate(found) if j != i and j not in used
              and math.dist((u, v), (x, y)) < 1.5 * max(s, t)), None)
    if j is not None:
        used |= {i, j}
        out.append(('double-diamond', ((x + found[j][0]) / 2, (y + found[j][1]) / 2)))
    else:
        used.add(i)
        out.append(('diamond', (x, y)))
labs = json.load(open(f'{D}/printed.json'))['labels']
for kind, (x, y) in sorted(out, key=lambda t: (round(t[1][1] / 100), t[1][0])):
    near = min(((min(math.dist((x, y), p) for p in (lab['pts'][0], lab['pts'][-1])), lab['text']) for lab in labs),
               default=(0, ''))
    print(f"    ('{kind}', ({round(x)}, {round(y)}), {near[1]!r}),  # {near[0]:.0f} px")
print(len(out), 'symbols', file=sys.stderr)
