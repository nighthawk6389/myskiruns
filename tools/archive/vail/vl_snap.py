"""vl_snap.py panel cls x,y x,y ... [--r 14] [--show out.png]: snap a rough polyline (read off a zoomed crop) onto
the painted line of that colour: resample every 8 px, move each sample to the middle of the nearest run of line
pixels within r px (samples in a dash gap stay on the interpolated path), print the snapped points as a Python
list, and optionally draw them on a 3x crop to check."""
import math, sys
import numpy as np
from PIL import Image, ImageDraw
Image.MAX_IMAGE_PIXELS = None
exec(open('vl_lines.py').read().split('\ndef pca_dir')[0])  # masks()

args = sys.argv[1:]
r = int(args[args.index('--r') + 1]) if '--r' in args else 14
show = args[args.index('--show') + 1] if '--show' in args else None
panel, cls = args[0], args[1]
pts = [tuple(float(v) for v in a.split(',')) for a in args[2:] if ',' in a and not a.endswith('.png')]
A = np.asarray(Image.open(f'{panel}.png').convert('RGB'))
M = masks(A)[cls]


def resample(p, step=8.0):
    out = [p[0]]
    for a, b in zip(p, p[1:]):
        n = max(1, int(math.dist(a, b) // step))
        out += [(a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n) for k in range(1, n + 1)]
    return out


snapped = []
for x, y in resample(pts):
    x0, y0 = int(max(0, x - r)), int(max(0, y - r))
    win = M[y0:int(y + r) + 1, x0:int(x + r) + 1]
    ys, xs = np.nonzero(win)
    if len(xs) == 0:
        snapped.append((x, y)); continue
    d = (xs + x0 - x) ** 2 + (ys + y0 - y) ** 2
    i = int(np.argmin(d))
    nx, ny = xs[i] + x0, ys[i] + y0
    near = (xs + x0 - nx) ** 2 + (ys + y0 - ny) ** 2 <= 16
    snapped.append((float(np.mean(xs[near] + x0)), float(np.mean(ys[near] + y0))))
# light smoothing, keep the ends
sm = [snapped[0]] + [((a[0] + 2 * b[0] + c[0]) / 4, (a[1] + 2 * b[1] + c[1]) / 4)
                     for a, b, c in zip(snapped, snapped[1:], snapped[2:])] + [snapped[-1]]
thin = [sm[0]]
for q in sm[1:-1]:
    if math.dist(q, thin[-1]) >= 12:
        thin.append(q)
thin.append(sm[-1])
print([(round(x), round(y)) for x, y in thin])
if show:
    xs = [p[0] for p in thin]; ys = [p[1] for p in thin]
    bx0, by0 = int(min(xs) - 60), int(min(ys) - 60)
    bx1, by1 = int(max(xs) + 60), int(max(ys) + 60)
    z = 3
    im = Image.fromarray(A[max(0, by0):by1, max(0, bx0):bx1]).resize(((bx1 - max(0, bx0)) * z, (by1 - max(0, by0)) * z))
    d = ImageDraw.Draw(im)
    d.line([((x - max(0, bx0)) * z, (y - max(0, by0)) * z) for x, y in thin], fill=(255, 0, 255), width=3)
    im.save(show)
