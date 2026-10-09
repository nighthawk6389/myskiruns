"""Trace a stretch along the map's own painted line between points read off a grid crop: the cheapest path through
the image where a pixel of the line's colour costs 1 and any other --off (Dijkstra on the pixel grid,
skimage.graph.route_through_array), from each point to the next. Where snap_trace.py needs rough points every
50 px or so, this needs only the ends (and a point past each fork, so the path takes the right branch): for a line
the extraction put elsewhere or missed (Steamboat's interactive map, a second drawing, is off the printed line in
places).

    python3 tools/trailmap/trace_ink.py --image map.png --rgb 45,98,165 1450,1205 1520,1160 [--show check.png]
    python3 tools/trailmap/trace_ink.py --image map.png --dark 1100,600 1150,700           # a black run

Prints the points as JSON ([[x, y], ...], image px, Ramer-Douglas-Peucker to --tol px), ready for a traced
stretch (decisions.TRACED). --rgb r,g,b [--dist 50] takes the pixels within that distance of the colour; --dark the
pixels darker than --dark-max in every channel. Check the result on the --show crop (magenta, 3x): under a label or
a symbol the path crosses the gap straight, and a path that leaves the line (no ink between the points) is a sign the
points are on different lines.

Requires: pip install pillow numpy scikit-image
"""
import argparse
import json
import math

import numpy as np
from PIL import Image, ImageDraw
from skimage.graph import route_through_array

Image.MAX_IMAGE_PIXELS = None


def rdp(pts, tol):
    if len(pts) < 3:
        return pts
    (x0, y0), (x1, y1) = pts[0], pts[-1]
    dx, dy = x1 - x0, y1 - y0
    n = math.hypot(dx, dy) or 1e-9
    d = [abs(dy * (x - x0) - dx * (y - y0)) / n for x, y in pts[1:-1]]
    i = max(range(len(d)), key=d.__getitem__)
    if d[i] <= tol:
        return [pts[0], pts[-1]]
    return rdp(pts[:i + 2], tol)[:-1] + rdp(pts[i + 1:], tol)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--image', required=True)
    ap.add_argument('--rgb', help='r,g,b of the line')
    ap.add_argument('--dist', type=float, default=50)
    ap.add_argument('--dark', action='store_true', help='a black line: pixels darker than --dark-max')
    ap.add_argument('--dark-max', type=int, default=70)
    ap.add_argument('--off', type=float, default=25, help='cost of a pixel off the line (on it: 1)')
    ap.add_argument('--pad', type=int, default=40, help='px around the points searched')
    ap.add_argument('--tol', type=float, default=1.0)
    ap.add_argument('--show')
    ap.add_argument('points', nargs='+', help='x,y in image px, in order along the line')
    a = ap.parse_args()
    pts = [tuple(float(v) for v in p.split(',')) for p in a.points]
    img = np.asarray(Image.open(a.image).convert('RGB')).astype(float)
    h, w = img.shape[:2]
    x0 = max(0, int(min(p[0] for p in pts)) - a.pad)
    y0 = max(0, int(min(p[1] for p in pts)) - a.pad)
    x1 = min(w, int(max(p[0] for p in pts)) + a.pad)
    y1 = min(h, int(max(p[1] for p in pts)) + a.pad)
    sub = img[y0:y1, x0:x1]
    if a.dark:
        ink = sub.max(axis=2) < a.dark_max
    else:
        ink = np.linalg.norm(sub - np.array([float(v) for v in a.rgb.split(',')]), axis=2) < a.dist
    cost = np.where(ink, 1.0, a.off)
    path = []
    on = 0
    for p, q in zip(pts, pts[1:]):
        idx, _c = route_through_array(cost, (int(p[1]) - y0, int(p[0]) - x0), (int(q[1]) - y0, int(q[0]) - x0),
                                      fully_connected=True, geometric=True)
        seg = [(c + x0, r + y0) for r, c in idx]
        on += sum(bool(ink[r, c]) for r, c in idx)
        path += seg if not path else seg[1:]
    out = [[round(x, 1), round(y, 1)] for x, y in rdp(path, a.tol)]
    print(json.dumps(out))
    print(f'# {len(path)} px, {on / max(1, len(path)):.0%} on the line', flush=True)
    if a.show:
        z = 3
        crop = Image.open(a.image).convert('RGB').crop((x0, y0, x1, y1))
        crop = crop.resize((crop.width * z, crop.height * z))
        d = ImageDraw.Draw(crop)
        d.line([((x - x0) * z, (y - y0) * z) for x, y in out], fill=(255, 0, 255), width=2)
        for x, y in pts:
            d.ellipse([(x - x0) * z - 4, (y - y0) * z - 4, (x - x0) * z + 4, (y - y0) * z + 4], outline=(255, 0, 0))
        crop.save(a.show)


if __name__ == '__main__':
    main()
