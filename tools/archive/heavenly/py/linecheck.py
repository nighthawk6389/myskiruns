"""For each line piece of a panel (pieces.json): the share of points along it with the line's ink within 2 px in the
2024 image (blue, green, dark)."""
import json, math, sys
import numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
panel = sys.argv[1]
W = '/home/user/myskiruns/work/heavenly'
im = np.asarray(Image.open(f'{W}/{panel}/map.png').convert('RGB')).astype(int)
H, Wd = im.shape[:2]
r, g, b = im[..., 0], im[..., 1], im[..., 2]
INK = {'blue': (b > 120) & (r < 90) & (g < 150), 'green': (g > 110) & (r < 90) & (b < 150), 'black': im.max(axis=2) < 110}
P = json.load(open(f'{W}/{panel}/pieces.json'))['polylines']
for p in P:
    pts = [(x * Wd / 100, y * H / 100) for x, y in p['points']]
    samples = []
    for a, c in zip(pts, pts[1:]):
        n = max(1, int(math.dist(a, c) / 3))
        samples += [(a[0] + (c[0] - a[0]) * k / n, a[1] + (c[1] - a[1]) * k / n) for k in range(n)]
    m = INK[p['cls']]
    hit = 0
    for x, y in samples:
        x0, y0 = int(round(x)), int(round(y))
        win = m[max(0, y0 - 2):y0 + 3, max(0, x0 - 2):x0 + 3]
        hit += bool(win.any())
    s = hit / len(samples) if samples else 0
    print(f'{s:.2f} {p["id"]} {p["cls"]} {p["lengthPx"]} ({pts[0][0]:.0f},{pts[0][1]:.0f})-({pts[-1][0]:.0f},{pts[-1][1]:.0f})')
