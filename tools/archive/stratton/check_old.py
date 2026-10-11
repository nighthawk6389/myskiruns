"""Stratton: each 2020-21 name label and run stroke checked against this season's image, where the 2020-21 page on
its grid (editions_diff.py's old_on_grid.png) and this season's image differ along it: a label whose box differs, a
stroke whose dashes differ, is changed or gone this season (look at it on a crop).

    python3 -I tools/archive/stratton/check_old.py <work dir> <a,b,c,d,e,f>
"""
import json
import math
import os
import sys

import numpy as np
import pymupdf
from PIL import Image, ImageFilter

Image.MAX_IMAGE_PIXELS = None
W, A = sys.argv[1], tuple(float(v) for v in sys.argv[2].split(','))
old = np.asarray(Image.open(os.path.join(W, 'diff/old_on_grid.png')).convert('RGB').filter(ImageFilter.GaussianBlur(1))).astype(int)
new = np.asarray(Image.open(os.path.join(W, 'map2025.png')).convert('RGB').filter(ImageFilter.GaussianBlur(1))).astype(int)
H, Wd = new.shape[:2]


def px(x, y):
    return A[0] * x + A[1] * y + A[2], A[3] * x + A[4] * y + A[5]


def diff_at(pts, r=3):
    ds = []
    for x, y in pts:
        X, Y = (int(round(v)) for v in px(x, y))
        if r <= X < Wd - r and r <= Y < H - r:
            a, b = old[Y - r:Y + r + 1, X - r:X + r + 1], new[Y - r:Y + r + 1, X - r:X + r + 1]
            ds.append(np.abs(a - b).max(axis=2).mean())
    return float(np.mean(ds)) if ds else -1


labels = [l for l in json.load(open(os.path.join(W, 'labels_raw.json')))
          if l['font'] == 'BrandonGrotesque-Bold' and abs(l['size'] - 6.5) < 0.2 and tuple(l['color']) != (1.0, 1.0, 1.0)]
print('labels, most changed first (mean diff along the characters):')
for l in sorted(labels, key=lambda l: -diff_at(l['pts'], 4)):
    d = diff_at(l['pts'], 4)
    if d > 12:
        X, Y = px(*l['c'])
        print(f'  {d:5.1f}  {l["text"]!r:32} at {round(X)},{round(Y)}')
p = pymupdf.open(os.path.join(W, 'stratton_2020-21.pdf'))[0]
cols = {(0.05, 0.49, 0.25): 'green', (0.08, 0.46, 0.74): 'blue', (0.14, 0.12, 0.13): 'black'}
print('run strokes, most changed first:')
rows = []
for k, dr in enumerate(p.get_drawings()):
    c = tuple(round(v, 2) for v in dr.get('color') or ())
    if dr['type'] not in ('s', 'fs') or c not in cols or abs((dr.get('width') or 0) - 1.0) > 0.05:
        continue
    pts = []
    for it in dr['items']:
        if it[0] == 'l':
            ps = [it[1], it[2]]
        elif it[0] == 'c':
            ps = [it[1], it[4]]
        else:
            continue
        for a, b in zip(ps, ps[1:]):
            n = max(1, int(math.dist((a.x, a.y), (b.x, b.y)) / 2))
            pts += [(a.x + (b.x - a.x) * t / n, a.y + (b.y - a.y) * t / n) for t in range(n + 1)]
    if not pts:
        continue
    d = diff_at(pts, 2)
    X, Y = px(*pts[len(pts) // 2])
    rows.append((d, k, cols[c], round(X), round(Y), len(pts) * 2))
for d, k, cl, X, Y, L in sorted(rows, reverse=True):
    if d > 15:
        print(f'  {d:5.1f}  drawing {k} {cl} middle {X},{Y} ~{L} pt')
