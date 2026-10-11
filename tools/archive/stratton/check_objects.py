"""Stratton: each 2020-21 run stroke and symbol checked on this season's image. The 2020-21 page's vector layer
alone (painting left out) is rendered on this season's grid; an object's pixels are those of its own colour on that
render within its reach (a stroke's dashes; a symbol's fill); the share of them this season's image also shows in
that colour (within --tol) says whether it is still printed there. Prints the objects under --min, worst first.

    python3 -I tools/archive/stratton/check_objects.py <work dir> <a,b,c,d,e,f> [--min 0.8] [--tol 70]
"""
import argparse
import json
import math
import os

import numpy as np
import pymupdf
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
ap = argparse.ArgumentParser()
ap.add_argument('work')
ap.add_argument('affine')
ap.add_argument('--min', type=float, default=0.8)
ap.add_argument('--tol', type=float, default=70)
a = ap.parse_args()
A = tuple(float(v) for v in a.affine.split(','))
new = np.asarray(Image.open(os.path.join(a.work, 'map2025.png')).convert('RGB')).astype(float)
H, W = new.shape[:2]
doc = pymupdf.open(os.path.join(a.work, 'stratton_2020-21.pdf'))
pg = doc[0]
drawings = pg.get_drawings()
pg.clean_contents()
x = pg.get_contents()[0]
doc.update_stream(x, doc.xref_stream(x).replace(b'/Im0 Do', b''))
m = pymupdf.Matrix(A[0], A[1], A[3], A[4], A[2], A[5])
pix = pg.get_pixmap(matrix=m, clip=pymupdf.Rect(0, 0, W, H))
canvas = Image.new('RGB', (W, H), (255, 255, 255))
canvas.paste(Image.frombytes('RGB', (pix.width, pix.height), pix.samples), (pix.x, pix.y))
vec = np.asarray(canvas).astype(float)
COLS = {(0.05, 0.49, 0.25): 'green', (0.08, 0.46, 0.74): 'blue', (0.14, 0.12, 0.13): 'black',
        (0.01, 0.02, 0.02): 'black'}


def px(p):
    return A[0] * p[0] + A[1] * p[1] + A[2], A[3] * p[0] + A[4] * p[1] + A[5]


def share(pts, rgb, r):
    """Of the render's pixels within r px of pts in the object's colour, the share this season shows alike."""
    col = np.array(rgb) * 255
    sel = set()
    for X, Y in pts:
        for dy in range(-int(r), int(r) + 1):
            for dx in range(-int(r), int(r) + 1):
                if dx * dx + dy * dy <= r * r:
                    sel.add((int(round(Y)) + dy, int(round(X)) + dx))
    sel = [(y, x) for y, x in sel if 0 <= y < H and 0 <= x < W]
    if not sel:
        return None, 0
    ys, xs = np.array(sel).T
    own = np.abs(vec[ys, xs] - col).max(axis=1) < 40
    if own.sum() < 4:
        return None, int(own.sum())
    alike = np.abs(new[ys[own], xs[own]] - col).max(axis=1) < a.tol
    return float(alike.mean()), int(own.sum())


rows = []
for k, d in enumerate(drawings):
    if d['type'] in ('s', 'fs') and d.get('color'):
        c = tuple(round(v, 2) for v in d['color'])
        if c not in COLS or abs((d.get('width') or 0) - 1.0) > 0.05:
            continue
        pts = []
        for it in d['items']:
            ps = [it[1], it[2]] if it[0] == 'l' else ([it[1], it[2], it[3], it[4]] if it[0] == 'c' else [])
            for p, q in zip(ps, ps[1:]):
                n = max(1, int(math.dist((p.x, p.y), (q.x, q.y)) * A[0] / 1.5))
                pts += [px((p.x + (q.x - p.x) * t / n, p.y + (q.y - p.y) * t / n)) for t in range(n + 1)]
        sh, n = share(pts, d['color'], 1.5)
        if sh is not None:
            mid = pts[len(pts) // 2]
            rows.append(('stroke', k, COLS[c], round(sh, 2), n, [round(v) for v in pts[0]],
                         [round(v) for v in mid], [round(v) for v in pts[-1]]))
for s in json.load(open(os.path.join(a.work, 'symbols_old.json'))):
    rgb = {'circle': (0.05, 0.49, 0.25), 'square': (0.08, 0.46, 0.74)}.get(s['type'], (0.01, 0.02, 0.02))
    sh, n = share([tuple(s['src'])], rgb, s['sizePt'] * A[0] * 0.75)
    if sh is not None:
        rows.append(('symbol', s['type'], '', round(sh, 2), n, [round(v) for v in s['src']], None, None))
json.dump(rows, open(os.path.join(a.work, 'found_objects.json'), 'w'), indent=0)
for r in sorted(rows, key=lambda r: r[3]):
    if r[3] < a.min:
        print(r)
print(len(rows), 'objects;', sum(r[3] < a.min for r in rows), 'under', a.min)
