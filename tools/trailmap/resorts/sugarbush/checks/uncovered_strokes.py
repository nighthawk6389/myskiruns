"""Strokes with no piece: python3 tools/trailmap/resorts/sugarbush/checks/uncovered_strokes.py [map.pdf] [linePolylines.json]

Every stroke in a trail colour (or pure black) 0.7-1.05 pt wide, sampled along its length, against the extracted
pieces: one with over 30% of its points more than 1 pt from every piece is printed as NOT COVERED. This is how
the three odd trails were found after the first extraction (Black Diamond Rush and Lwr Exterminator in pure
black, Hi & Lo Road at 1.0 pt, and Out Road, a stroke with a stray fill), hence the extra passes in regen.sh;
with all of them it prints only "done". It cannot see Snowball (a filled outline, no stroke): the readers
found that one. Defaults: $SUGARBUSH_WORK/sugarbush.pdf and src/data/resorts/sugarbush/linePolylines.json
(pieces in percent of the 3.5 px/pt image). Was inline code (2026-09-30 11:42).
"""
import json
import math
import os
import sys

import pymupdf

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *['..'] * 5))
WORK = os.environ.get('SUGARBUSH_WORK', os.path.join(ROOT, 'work', 'sugarbush'))
pdf = sys.argv[1] if len(sys.argv) > 1 else os.path.join(WORK, 'sugarbush.pdf')
pieces_file = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, 'src/data/resorts/sugarbush/linePolylines.json')
page = pymupdf.open(pdf)[0]
d = json.load(open(pieces_file))
W, H = 4333, 2981
pieces = [[(x * W / 100 / 3.5, y * H / 100 / 3.5) for x, y in p['points']] for p in d['polylines']]


def segd(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]; L = dx * dx + dy * dy
    t = max(0, min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / L)) if L else 0
    return math.dist(p, (a[0] + t * dx, a[1] + t * dy))


def dist(p):
    return min(segd(p, pts[i - 1], pts[i]) for pts in pieces for i in range(1, len(pts)))


def sample(dr):
    out = []
    for it in dr['items']:
        if it[0] == 'l':
            out += [(it[1].x, it[1].y), (it[2].x, it[2].y)]
        elif it[0] == 'c':
            p0, c1, c2, p3 = it[1:5]
            for k in range(0, 9):
                t = k / 8; m = 1 - t
                out.append((m**3 * p0.x + 3 * m * m * t * c1.x + 3 * m * t * t * c2.x + t**3 * p3.x,
                            m**3 * p0.y + 3 * m * m * t * c1.y + 3 * m * t * t * c2.y + t**3 * p3.y))
    return out


for dr in page.get_drawings():
    if dr['type'] in ('s', 'fs') and dr.get('color') and tuple(round(v, 2) for v in dr['color']) in [
            (0.08, 0.51, 0.78), (0.08, 0.65, 0.32), (0.14, 0.12, 0.13), (0.0, 0.0, 0.0)] and 0.7 <= dr['width'] <= 1.05:
        pts = sample(dr)
        far = [p for p in pts if dist(p) > 1.0]
        if len(far) > 0.3 * len(pts):
            r = dr['rect']
            print('NOT COVERED:', tuple(round(v, 2) for v in dr['color']), round(dr['width'], 2), [round(v) for v in r],
                  'px', [round(v * 3.5) for v in r], f'{len(far)}/{len(pts)} pts uncovered', [it[0] for it in dr['items']])
print('done')
