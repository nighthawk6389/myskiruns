"""The two pieces nearest each given point (map px) of a one-panel resort, with the nearest point on each: to key a
decision to a point on its piece. snap.py <work dir> x,y [x,y ...] (run from the repo root after a build; reads
<work dir>/pieces_cut.json, names.json, map.png). Written for Buttermilk's decisions (tools/archive/snowmass/at.py,
for one resort's panels)."""
import json
import math
import sys

from PIL import Image

W_DIR = sys.argv[1]
W, H = Image.open(f'{W_DIR}/map.png').size
P = json.load(open(f'{W_DIR}/pieces_cut.json'))['polylines']
N = json.load(open(f'{W_DIR}/names.json'))


def near(q, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    n = dx * dx + dy * dy
    t = max(0, min(1, ((q[0] - a[0]) * dx + (q[1] - a[1]) * dy) / n)) if n else 0
    p = (a[0] + t * dx, a[1] + t * dy)
    return math.dist(q, p), p


for arg in sys.argv[2:]:
    q = tuple(map(float, arg.split(',')))
    res = []
    for p in P:
        pts = [(x * W / 100, y * H / 100) for x, y in p['points']]
        d, c = min(near(q, a, b) for a, b in zip(pts, pts[1:]))
        res.append((round(d, 1), p['id'], N.get(str(p['id'])), (round(c[0]), round(c[1]))))
    res.sort()
    print(arg, res[:2])
