"""Trace a stretch the line detection missed (a name printed in the line, dashes through slow-zone hatching, the
stub between a symbol and its parent line): read a few rough points off a grid crop (grid_crop.py), then snap
them onto the painted line. The path is resampled every 8 px; each sample moves to the middle of the nearest
line pixels of that colour within --r px (samples where nothing is painted, e.g. under a label, stay on the
interpolated path); then it is smoothed lightly and thinned to ~12 px steps, keeping both ends.

    python3 tools/trailmap/snap_trace.py --image map.png --color green 853,763 870,780 859,810 886,841 \\
        [--r 8] [--show check.png]

Prints the points as JSON ([[x, y], ...], source px), ready for a traced stretch (Vail: decisions.TRACED).
--color green|blue|black uses raster_lines.py's colour masks (tuned to Vail's 2025-26 palette: check --show on
another map), or --rgb r,g,b [--tol 40] matches any colour. The thinning cuts tight bends a little: give more
points there, or use the points as read. --show draws the result in magenta on a 3x crop.

Requires: pip install pillow numpy (and opencv-python-headless scikit-image for --color)
"""
import argparse
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

Image.MAX_IMAGE_PIXELS = None


def resample(p, step=8.0):
    out = [p[0]]
    for a, b in zip(p, p[1:]):
        n = max(1, int(math.dist(a, b) // step))
        out += [(a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n) for k in range(1, n + 1)]
    return out


def snap(M, pts, r):
    snapped = []
    for x, y in resample(pts):
        x0, y0 = int(max(0, x - r)), int(max(0, y - r))
        win = M[y0:int(y + r) + 1, x0:int(x + r) + 1]
        ys, xs = np.nonzero(win)
        if len(xs) == 0:
            snapped.append((x, y)); continue
        i = int(np.argmin((xs + x0 - x) ** 2 + (ys + y0 - y) ** 2))
        nx, ny = xs[i] + x0, ys[i] + y0
        near = (xs + x0 - nx) ** 2 + (ys + y0 - ny) ** 2 <= 16
        snapped.append((float(np.mean(xs[near] + x0)), float(np.mean(ys[near] + y0))))
    sm = [snapped[0]] + [((a[0] + 2 * b[0] + c[0]) / 4, (a[1] + 2 * b[1] + c[1]) / 4)
                         for a, b, c in zip(snapped, snapped[1:], snapped[2:])] + [snapped[-1]]
    thin = [sm[0]]
    for q in sm[1:-1]:
        if math.dist(q, thin[-1]) >= 12:
            thin.append(q)
    thin.append(sm[-1])
    return [(round(x), round(y)) for x, y in thin]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--image', required=True)
    ap.add_argument('--color', choices=('green', 'blue', 'black'), help="raster_lines.py's mask for this colour")
    ap.add_argument('--rgb', help='r,g,b of the painted line, instead of --color')
    ap.add_argument('--tol', type=int, default=40, help='--rgb: max difference per channel')
    ap.add_argument('--r', type=int, default=10, help='search radius around each sample, px')
    ap.add_argument('--show', help='write a 3x crop with the result drawn on')
    ap.add_argument('points', nargs='+', help='x,y rough points along the line, in order')
    a = ap.parse_args()
    A = np.asarray(Image.open(a.image).convert('RGB'))
    if a.rgb:
        rgb = np.array([int(v) for v in a.rgb.split(',')], np.int16)
        M = (np.abs(A.astype(np.int16) - rgb) <= a.tol).all(axis=2)
    elif a.color:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from raster_lines import masks
        M = masks(A)[a.color]
    else:
        ap.error('give --color or --rgb')
    pts = [tuple(float(v) for v in p.split(',')) for p in a.points]
    out = snap(M, pts, a.r)
    print(json.dumps(out))
    if a.show:
        xs = [p[0] for p in out]; ys = [p[1] for p in out]
        bx0, by0 = int(max(0, min(xs) - 60)), int(max(0, min(ys) - 60))
        bx1, by1 = int(max(xs) + 60), int(max(ys) + 60)
        z = 3
        im = Image.fromarray(A[by0:by1, bx0:bx1]).resize(((bx1 - bx0) * z, (by1 - by0) * z))
        ImageDraw.Draw(im).line([((x - bx0) * z, (y - by0) * z) for x, y in out], fill=(255, 0, 255), width=3)
        im.save(a.show)


if __name__ == '__main__':
    main()
