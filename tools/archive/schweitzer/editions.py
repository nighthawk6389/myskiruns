"""Schweitzer's Outback Bowl: the 2024-25 image (skimap.org 30575, 3300x2550, the one used) against the 2025-26 one
(schweitzer.com, 1920x1484 only). The two register as a plain scaling (register_pages.py --ref: 4084 inliers, median
0.07 px, x 0.5818 = 1920/3300); this lists every place they differ by more than 90 in some channel after the 2024-25
one is scaled down, and writes side-by-side crops of the largest (2024-25 left, 2025-26 right) to check by eye. On
2026-10-10 all 28 were the JPEG's ringing round letters and lift lines: no name, symbol or line differs.

    python3 tools/archive/schweitzer/editions.py [work/schweitzer] [out.png]      (repo root)
"""
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

W = sys.argv[1] if len(sys.argv) > 1 else 'work/schweitzer'
out = sys.argv[2] if len(sys.argv) > 2 else f'{W}/outback_editions.png'
a = Image.open(f'{W}/outback-bowl_2024-25.webp').convert('RGB')
b = Image.open(f'{W}/outback-bowl_2025-26-web.jpg').convert('RGB')
small = a.resize(b.size, Image.LANCZOS)
d = np.abs(np.asarray(small, float) - np.asarray(b, float)).max(axis=2) > 90
lab, n = ndimage.label(ndimage.binary_dilation(d, iterations=3))
sizes = ndimage.sum(d, lab, range(1, n + 1))
boxes = sorted(((int(s), o) for s, o in zip(sizes, ndimage.find_objects(lab)) if s > 40), key=lambda t: -t[0])
print(len(boxes), 'places differ (2025-26 px):')
for s, o in boxes:
    print(f'  {s:4d} px  {o[1].start},{o[0].start},{o[1].stop},{o[0].stop}')
k = a.width / b.width
big = b.resize(a.size, Image.LANCZOS)
tiles = []
for _s, o in boxes[:12]:
    box = (int((o[1].start - 30) * k), int((o[0].start - 30) * k), int((o[1].stop + 30) * k), int((o[0].stop + 30) * k))
    ca, cb = a.crop(box), big.crop(box)
    t = Image.new('RGB', (ca.width * 2 + 6, ca.height), 'red')
    t.paste(ca, (0, 0))
    t.paste(cb, (ca.width + 6, 0))
    tiles.append(t)
if tiles:
    s = Image.new('RGB', (max(t.width for t in tiles), sum(t.height for t in tiles)), 'white')
    y = 0
    for t in tiles:
        s.paste(t, (0, y))
        y += t.height
    s.save(out)
    print('->', out)
