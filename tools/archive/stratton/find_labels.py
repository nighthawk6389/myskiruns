"""Stratton: where this season's image prints each 2020-21 name (or symbol). The 2020-21 page's vector layer alone
(its painting left out) is rendered on this season's grid; each label's glyph pixels (dark pixels inside its
characters' boxes) and their halo (a ring round them) make its template; the score of an offset is the halo's
mean brightness on this season's image less the glyphs' (high where black letters sit on their white halo). Each
label is searched within --reach px; prints the labels whose best offset is not 0 or whose score at 0 is low.

    python3 -I tools/archive/stratton/find_labels.py <work dir> <a,b,c,d,e,f> [--reach 160] [--all]
"""
import argparse
import json
import os

import numpy as np
import pymupdf
from PIL import Image
from scipy import ndimage

Image.MAX_IMAGE_PIXELS = None
ap = argparse.ArgumentParser()
ap.add_argument('work')
ap.add_argument('affine')
ap.add_argument('--reach', type=int, default=160)
ap.add_argument('--all', action='store_true')
a = ap.parse_args()
A = tuple(float(v) for v in a.affine.split(','))
new = np.asarray(Image.open(os.path.join(a.work, 'map2025.png')).convert('L')).astype(float)
H, W = new.shape
doc = pymupdf.open(os.path.join(a.work, 'stratton_2020-21.pdf'))
pg = doc[0]
pg.clean_contents()
x = pg.get_contents()[0]
s = doc.xref_stream(x)
doc.update_stream(x, s.replace(b'/Im0 Do', b''))  # the painting left out
m = pymupdf.Matrix(A[0], A[1], A[3], A[4], A[2], A[5])
pix = pg.get_pixmap(matrix=m, clip=pymupdf.Rect(0, 0, W, H))
canvas = Image.new('L', (W, H), 255)
canvas.paste(Image.frombytes('RGB', (pix.width, pix.height), pix.samples).convert('L'), (pix.x, pix.y))
vec = np.asarray(canvas).astype(float)
labels = [l for l in json.load(open(os.path.join(a.work, 'labels_raw.json')))
          if l['font'] == 'BrandonGrotesque-Bold' and abs(l['size'] - 6.5) < 0.2 and tuple(l['color']) != (1.0, 1.0, 1.0)]
# each character's box from the page's own text (rawdict), matched to the labels' character centres
chars = []
for b in pg.get_text('rawdict')['blocks']:
    for line in b.get('lines', []):
        for sp in line['spans']:
            for ch in sp['chars']:
                if ch['c'].strip():
                    chars.append(ch)


def px(p):
    return A[0] * p[0] + A[1] * p[1] + A[2], A[3] * p[0] + A[4] * p[1] + A[5]


def template(l):
    mask = np.zeros((H, W), bool)
    for p in l['pts']:
        c = min(chars, key=lambda ch: (ch['origin'][0] - p[0]) ** 2 + ((ch['bbox'][1] + ch['bbox'][3]) / 2 - p[1]) ** 2)
        x0, y0 = px((c['bbox'][0], c['bbox'][1]))
        x1, y1 = px((c['bbox'][2], c['bbox'][3]))
        X0, X1 = int(min(x0, x1)) - 1, int(max(x0, x1)) + 2
        Y0, Y1 = int(min(y0, y1)) - 1, int(max(y0, y1)) + 2
        mask[max(0, Y0):Y1, max(0, X0):X1] = True
    glyph = mask & (vec < 90)
    halo = ndimage.binary_dilation(glyph, iterations=3) & ~ndimage.binary_dilation(glyph, iterations=1)
    return np.argwhere(glyph), np.argwhere(halo)


def score(g, h, dy, dx):
    gy, gx = g[:, 0] + dy, g[:, 1] + dx
    hy, hx = h[:, 0] + dy, h[:, 1] + dx
    ok = (gy >= 0) & (gy < H) & (gx >= 0) & (gx < W)
    okh = (hy >= 0) & (hy < H) & (hx >= 0) & (hx < W)
    if ok.mean() < 0.9:
        return -999
    return new[hy[okh], hx[okh]].mean() - new[gy[ok], gx[ok]].mean()


rows = []
for l in labels:
    g, h = template(l)
    if len(g) < 10:
        continue
    s0 = score(g, h, 0, 0)
    best = (s0, 0, 0)
    for step, R, c in ((6, a.reach, (0, 0)), (2, 8, None), (1, 2, None)):
        cy, cx = (best[1], best[2]) if c is None else c
        for dy in range(cy - R, cy + R + 1, step):
            for dx in range(cx - R, cx + R + 1, step):
                sc = score(g, h, dy, dx)
                if sc > best[0]:
                    best = (sc, dy, dx)
    X, Y = px(l['c'])
    rows.append((l['text'], round(X), round(Y), round(s0, 1), round(best[0], 1), best[2], best[1]))
json.dump(rows, open(os.path.join(a.work, 'found_labels.json'), 'w'), indent=0)
for t, X, Y, s0, sb, dx, dy in sorted(rows, key=lambda r: r[3]):
    if a.all or s0 < 60 or abs(dx) > 1 or abs(dy) > 1:
        print(f'{t!r:28} at {X},{Y}: score at 0 {s0:6.1f}, best {sb:6.1f} at offset {dx:+d},{dy:+d}')
