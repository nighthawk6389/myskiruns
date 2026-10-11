"""Stratton: the map in tiles, each the 2020-21 export on this season's grid beside this season's image and the
mask of the pixels that differ (white): to read every change in the vector layer tile by tile.

    python3 -I tools/archive/stratton/diff_tiles.py <old_on_grid.png> <map2025.png> <out dir> [tile px] [x0,y0,x1,y1]
"""
import os
import sys

import numpy as np
from PIL import Image, ImageFilter

Image.MAX_IMAGE_PIXELS = None
old, new = Image.open(sys.argv[1]).convert('RGB'), Image.open(sys.argv[2]).convert('RGB')
out = sys.argv[3]
T = int(sys.argv[4]) if len(sys.argv) > 4 else 500
X0, Y0, X1, Y1 = (int(v) for v in sys.argv[5].split(',')) if len(sys.argv) > 5 else (0, 0) + new.size
os.makedirs(out, exist_ok=True)
a = np.asarray(old.filter(ImageFilter.GaussianBlur(1.2))).astype(int)
b = np.asarray(new.filter(ImageFilter.GaussianBlur(1.2))).astype(int)
mask = np.abs(a - b).max(axis=2) > 70
for y in range(Y0, Y1, T):
    for x in range(X0, X1, T):
        bx = (x, y, min(x + T, X1), min(y + T, Y1))
        m = mask[bx[1]:bx[3], bx[0]:bx[2]]
        if m.sum() < 80:
            continue
        o, n = old.crop(bx), new.crop(bx)
        s = Image.new('RGB', (o.width * 3 + 16, o.height), (255, 0, 255))
        s.paste(o, (0, 0)); s.paste(n, (o.width + 8, 0))
        s.paste(Image.fromarray((m * 255).astype('uint8')).convert('RGB'), (2 * o.width + 16, 0))
        s.save(os.path.join(out, f't_{x}_{y}.png'))
