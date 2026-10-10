"""A run's line on a raster map, routed between a few waypoints along its painted line: the cheapest path over a
cost grid that is low on the run's colour (raster_lines.py's masks) and on its casing, and high elsewhere, so the
path follows the drawn line between the points and crosses only short gaps (a label printed in the line, a
symbol, a lift crossing it). trace_ink.py's method (Dijkstra between points read on a crop) for a whole map read
this way: a module whose cost grid is built once per colour class, raster_lines.py's palette masks for the trail
colours, casings made cheap too, and waypoints moved onto their line first (Whitefish's web JPEGs, whose lines the
JPEG has blurred: give the run's start, its end, and a point past each junction where it could take another line).

    python3 tools/trailmap/route_trace.py --image map.png --palette whitefish --color blue 1210,975 1398,1183 \\
        [--casing] [--show check.png]

Each waypoint first moves to the nearest pixel of the run's colour within 12 px (points read a little off the line).
Prints the path as JSON ([[x, y], ...], image px, simplified to within 1.5 px). As a module: Router(image, palette)
.route(cls, waypoints, casing=False). --casing also makes the yellow and purple casings cheap (the "easiest route"
and night-skiing runs, whose thin centre line the JPEG blurs into its casing).

Requires: pip install pillow numpy opencv-python-headless scikit-image
"""
import argparse
import json
import math

import cv2
import numpy as np
from PIL import Image, ImageDraw
from skimage.graph import MCP_Geometric

from raster_lines import masks

Image.MAX_IMAGE_PIXELS = None
OFF = 40.0  # cost per px off any line: a gap of g px costs as much as 40 g px of line
CASING = 3.0


def simplify(pts, eps):
    if len(pts) < 3:
        return pts
    (ax, ay), (bx, by) = pts[0], pts[-1]
    dx, dy = bx - ax, by - ay
    n = math.hypot(dx, dy) or 1e-9
    d = [abs(dy * (x - ax) - dx * (y - ay)) / n for x, y in pts[1:-1]]
    i = int(np.argmax(d)) + 1
    if d[i - 1] <= eps:
        return [pts[0], pts[-1]]
    return simplify(pts[:i + 1], eps)[:-1] + simplify(pts[i:], eps)


class Router:
    def __init__(self, image, palette='vail'):
        A = np.asarray(Image.open(image).convert('RGB'))
        self.A = A
        self.M = masks(A, palette)
        r, g, b = (A[..., i].astype(np.int16) for i in range(3))
        self.casing = ((r > 150) & (g > 140) & (b < 130) & (np.abs(r - g) < 50) & (r - b > 70)) | (
            (r > 90) & (b > 130) & (g < 110) & (r - g > 25) & (b - g > 50))
        self.costs = {}

    def cost(self, cls, casing):
        k = (cls, casing)
        if k not in self.costs:
            line = cv2.dilate(self.M[cls].astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
            c = np.full(line.shape, OFF)
            if casing:
                c[self.casing] = CASING
            c[line] = 1.0
            self.costs[k] = c
        return self.costs[k]

    def snap(self, cls, q, r=12):
        """The nearest pixel of the run's line within r px of q (a waypoint read a little off its line), else q."""
        x, y = int(round(q[0])), int(round(q[1]))
        M = self.M[cls]
        win = M[max(0, y - r):y + r + 1, max(0, x - r):x + r + 1]
        ys, xs = np.nonzero(win)
        if not len(xs):
            return (x, y)
        i = int(np.argmin((xs + max(0, x - r) - x) ** 2 + (ys + max(0, y - r) - y) ** 2))
        return (int(xs[i] + max(0, x - r)), int(ys[i] + max(0, y - r)))

    def route(self, cls, waypoints, casing=False):
        c = self.cost(cls, casing)
        H, W = c.shape
        waypoints = [self.snap(cls, q) for q in waypoints]
        path = []
        for (x0, y0), (x1, y1) in zip(waypoints, waypoints[1:]):
            # a window round the two points (the line can bow out between them)
            m = int(max(80, 0.6 * math.dist((x0, y0), (x1, y1))))
            bx0, by0 = max(0, int(min(x0, x1)) - m), max(0, int(min(y0, y1)) - m)
            bx1, by1 = min(W, int(max(x0, x1)) + m), min(H, int(max(y0, y1)) + m)
            mcp = MCP_Geometric(c[by0:by1, bx0:bx1])
            start = (int(y0) - by0, int(x0) - bx0)
            end = (int(y1) - by0, int(x1) - bx0)
            mcp.find_costs([start], [end])
            seg = [(x + bx0, y + by0) for y, x in mcp.traceback(end)]
            path += seg if not path else seg[1:]
        return [[round(x), round(y)] for x, y in simplify(path, 1.5)]


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('--image', required=True)
    ap.add_argument('--palette', default='vail')
    ap.add_argument('--color', required=True, choices=('green', 'blue', 'black'))
    ap.add_argument('--casing', action='store_true')
    ap.add_argument('--show', help='write a crop with the path drawn on')
    ap.add_argument('points', nargs='+', help='x,y waypoints along the run, in order (its start, its end)')
    a = ap.parse_args()
    pts = [tuple(float(v) for v in p.split(',')) for p in a.points]
    R = Router(a.image, a.palette)
    out = R.route(a.color, pts, a.casing)
    print(json.dumps(out))
    if a.show:
        xs, ys = [p[0] for p in out], [p[1] for p in out]
        box = (max(0, min(xs) - 60), max(0, min(ys) - 60), max(xs) + 60, max(ys) + 60)
        im = Image.fromarray(R.A).crop(box)
        d = ImageDraw.Draw(im)
        d.line([(x - box[0], y - box[1]) for x, y in out], fill=(255, 0, 255), width=2)
        im.save(a.show)


if __name__ == '__main__':
    main()
