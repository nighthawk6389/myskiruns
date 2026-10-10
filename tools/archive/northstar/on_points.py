"""For CUTS on one of Northstar's pieces: each cut's point moved onto the piece, and a point on the piece 30 px
before it (toward the piece's start) and 30 px after it, with how far the nearest other piece is from each, so a
CUTS entry's first point names the right part unambiguously (decisions.py: cuts on one piece in order along it,
each keyed by the point before it).

    python3 tools/archive/northstar/on_points.py <piece id> x,y [x,y ...]     (repo root, after a build)
    python3 tools/archive/northstar/on_points.py --at <id>[:fraction] [...]   a point on a piece after the cuts
                                                                             (pieces_cut.json), for CHECKED/UNNAMED
"""
import json
import math
import sys

from PIL import Image

sys.path.insert(0, 'tools/trailmap')
from pdf_resort import line_dist  # noqa: E402

W, H = Image.open('work/northstar/map.png').size
AT = sys.argv[1] == '--at'
P = {p['id']: [(x * W / 100, y * H / 100) for x, y in p['points']]
     for p in json.load(open(f'work/northstar/{"pieces_cut" if AT else "pieces"}.json'))['polylines']}
pid = None if AT else int(sys.argv[1])
pts = [] if AT else P[pid]


def proj(q):
    best, s = (math.inf, 0, None), 0
    for a, b in zip(pts, pts[1:]):
        dx, dy = b[0] - a[0], b[1] - a[1]
        n = dx * dx + dy * dy
        t = max(0, min(1, ((q[0] - a[0]) * dx + (q[1] - a[1]) * dy) / n)) if n else 0
        c = (a[0] + t * dx, a[1] + t * dy)
        if math.dist(q, c) < best[0]:
            best = (math.dist(q, c), s + t * math.sqrt(n), c)
        s += math.sqrt(n)
    return best


def at(s):
    for a, b in zip(pts, pts[1:]):
        L = math.dist(a, b)
        if s <= L:
            t = s / L if L else 0
            return (a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1]))
        s -= L
    return pts[-1]


def other(q):
    return min(line_dist(q, p) for i, p in P.items() if i != pid)


if AT:
    for arg in sys.argv[2:]:
        i, _, f = arg.partition(':')
        pid, pts = int(i), P[int(i)]
        L = sum(math.dist(a, b) for a, b in zip(pts, pts[1:]))
        q = at(L * float(f or 0.5))
        print(f'piece {pid} at {f or 0.5}: ({q[0]:.0f}, {q[1]:.0f}) [other piece {other(q):.1f} px]')
    sys.exit()
for arg in sys.argv[2:]:
    q = tuple(float(v) for v in arg.split(','))
    d, s, c = proj(q)
    b, f = at(max(0, s - 30)), at(s + 30)
    print(f'cut {arg}: on the piece at ({c[0]:.0f}, {c[1]:.0f}) ({d:.1f} px off), {s:.0f} px along; '
          f'before ({b[0]:.0f}, {b[1]:.0f}) [other piece {other(b):.1f} px], '
          f'after ({f[0]:.0f}, {f[1]:.0f}) [other piece {other(f):.1f} px]')
