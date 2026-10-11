"""Stratton: where this season's flattened map differs from the 2020-21 export rendered on its grid (the same
painting, so what differs is the vector layer: names, lines, parks, the legend). Writes the difference mask's
regions, largest first, and a sheet of each region side by side (2020-21 | 2025-26).

    python3 -I tools/archive/stratton/editions_diff.py <work dir> <a,b,c,d,e,f> <out dir> [box x0,y0,x1,y1]
"""
import json
import os
import sys

import numpy as np
import pymupdf
from PIL import Image, ImageFilter
from scipy import ndimage

Image.MAX_IMAGE_PIXELS = None
W, A, out = sys.argv[1], tuple(float(v) for v in sys.argv[2].split(',')), sys.argv[3]
os.makedirs(out, exist_ok=True)
new = Image.open(os.path.join(W, 'map2025.png')).convert('RGB')
box = tuple(int(v) for v in sys.argv[4].split(',')) if len(sys.argv) > 4 else (0, 0) + new.size
p = pymupdf.open(os.path.join(W, 'stratton_2020-21.pdf'))[0]
m = pymupdf.Matrix(A[0], A[1], A[3], A[4], A[2], A[5])
pix = p.get_pixmap(matrix=m, clip=pymupdf.Rect(-20, -20, p.rect.x1 + 20, p.rect.y1 + 20) * m & pymupdf.Rect(0, 0, *new.size))
old = Image.new('RGB', new.size, (128, 128, 128))
old.paste(Image.frombytes('RGB', (pix.width, pix.height), pix.samples), (pix.x, pix.y))
old.save(os.path.join(out, 'old_on_grid.png'))
a = np.asarray(old.filter(ImageFilter.GaussianBlur(1.2))).astype(int)
b = np.asarray(new.filter(ImageFilter.GaussianBlur(1.2))).astype(int)
d = np.abs(a - b).max(axis=2)
mask = d > 70
x0, y0, x1, y1 = box
keep = np.zeros_like(mask)
keep[y0:y1, x0:x1] = True
mask &= keep
mask = ndimage.binary_dilation(mask, iterations=6)
lab, n = ndimage.label(mask)
regions = []
for i, sl in enumerate(ndimage.find_objects(lab), 1):
    ys, xs = sl
    area = int((lab[sl] == i).sum())
    if area < 150:
        continue
    regions.append({'box': [xs.start, ys.start, xs.stop, ys.stop], 'area': area})
regions.sort(key=lambda r: -r['area'])
json.dump(regions, open(os.path.join(out, 'regions.json'), 'w'), indent=0)
print(len(regions), 'regions')
for k, r in enumerate(regions[:400]):
    X0, Y0, X1, Y1 = r['box']
    X0, Y0, X1, Y1 = max(0, X0 - 20), max(0, Y0 - 20), min(new.width, X1 + 20), min(new.height, Y1 + 20)
    o, nn = old.crop((X0, Y0, X1, Y1)), new.crop((X0, Y0, X1, Y1))
    s = Image.new('RGB', (o.width * 2 + 6, o.height), 'magenta')
    s.paste(o, (0, 0)); s.paste(nn, (o.width + 6, 0))
    s.save(os.path.join(out, f'r{k:03d}_{X0}_{Y0}.png'))
