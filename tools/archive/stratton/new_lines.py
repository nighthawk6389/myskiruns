"""Stratton: the runs' dashes this season's image draws where the 2020-21 export has none (lines drawn anew or
moved): pixels in a run colour (blue, green, black) on this season's image, away (--away px) from the 2020-21 page's
own pixels of that colour (its whole render on this season's grid, painting included, editions_diff.py's
old_on_grid.png, so the painting's own blues cancel out), grouped into regions; writes their boxes and an overview.

    python3 -I tools/archive/stratton/new_lines.py <work dir> <a,b,c,d,e,f> <out dir> [--away 6]
"""
import argparse
import json
import os

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

Image.MAX_IMAGE_PIXELS = None
ap = argparse.ArgumentParser()
ap.add_argument('work')
ap.add_argument('affine')
ap.add_argument('out')
ap.add_argument('--away', type=int, default=6)
a = ap.parse_args()
os.makedirs(a.out, exist_ok=True)
A = tuple(float(v) for v in a.affine.split(','))
img = Image.open(os.path.join(a.work, 'map2025.png')).convert('RGB')
new = np.asarray(img).astype(float)
H, W = new.shape[:2]
H = min(H, 2061)
new = new[:H]
vec = np.asarray(Image.open(os.path.join(a.work, 'diff/old_on_grid.png')).convert('RGB')).astype(float)[:H]
regions = {}
over = img.crop((0, 0, W, H)).copy()
d = ImageDraw.Draw(over)
for name, rgb in (('blue', (0.08, 0.46, 0.74)), ('green', (0.05, 0.49, 0.25)), ('black', (0.14, 0.12, 0.13))):
    col = np.array(rgb) * 255
    now = np.abs(new - col).max(axis=2) < 45
    old = ndimage.binary_dilation(np.abs(vec - col).max(axis=2) < 70, iterations=a.away)
    left = ndimage.binary_opening(now & ~old, iterations=1)
    lab, n = ndimage.label(ndimage.binary_dilation(left, iterations=8))
    out = []
    for i, sl in enumerate(ndimage.find_objects(lab), 1):
        k = int((left[sl] & (lab[sl] == i)).sum())
        if k < 40:
            continue
        ys, xs = sl
        out.append({'box': [xs.start, ys.start, xs.stop, ys.stop], 'px': k})
        d.rectangle([xs.start, ys.start, xs.stop, ys.stop], outline={'blue': (255, 0, 255), 'green': (255, 140, 0), 'black': (0, 255, 255)}[name],
                    width=4)
    regions[name] = sorted(out, key=lambda r: -r['px'])
    print(name, len(out), [(r['box'], r['px']) for r in regions[name][:25]])
json.dump(regions, open(os.path.join(a.out, 'new_lines.json'), 'w'), indent=0)
over.resize((W // 2, H // 2)).save(os.path.join(a.out, 'new_lines.png'))
