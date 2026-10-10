"""The junctions along given pieces: each other piece whose end lies within 3 px of the piece, where (arc length px and
point), and its names; with the piece's printed names' positions along it. junctions.py <resort>/<panel> id [id ...]
(repo root, after a build)."""
import json
import math
import sys

from PIL import Image

sys.path.insert(0, 'tools/trailmap')
from pdf_resort import Resort  # noqa: E402

rid, ids = sys.argv[1], [int(v) for v in sys.argv[2:]]
W_DIR = f'work/{rid}'
W, H = Image.open(f'{W_DIR}/map.png').size
P = {p['id']: [(x * W / 100, y * H / 100) for x, y in p['points']]
     for p in json.load(open(f'{W_DIR}/pieces_cut.json'))['polylines']}
N = json.load(open(f'{W_DIR}/names.json'))
names = Resort(rid).names()


def proj(q, pts):
    best, s = (math.inf, 0, None), 0
    for a, b in zip(pts, pts[1:]):
        dx, dy = b[0] - a[0], b[1] - a[1]
        n = dx * dx + dy * dy
        t = max(0, min(1, ((q[0] - a[0]) * dx + (q[1] - a[1]) * dy) / n)) if n else 0
        p = (a[0] + t * dx, a[1] + t * dy)
        d = math.dist(q, p)
        if d < best[0]:
            best = (d, s + t * math.sqrt(n), p)
        s += math.sqrt(n)
    return best


for i in ids:
    pts = P[i]
    total = sum(math.dist(a, b) for a, b in zip(pts, pts[1:]))
    ev = []
    for j, op in P.items():
        if j == i:
            continue
        for k, e in ((0, op[0]), (-1, op[-1])):
            d, s, p = proj(e, pts)
            if d < 3:
                ev.append((s, f'junction {j} ({N.get(str(j))}) {"start" if k == 0 else "end"}', p))
    for n in names:
        ds = [proj(q, pts) for q in n['pts']]
        near = [x for x in ds if x[0] < 25]
        if len(near) >= max(1, len(ds) // 2):
            s = sorted(x[1] for x in near)[len(near) // 2]
            ev.append((s, f'name {n["name"]} ({round(sorted(x[0] for x in near)[len(near) // 2])} px off)',
                       near[0][2]))
    print(f'piece {i} {N.get(str(i))}: {round(total)} px from {tuple(round(v) for v in pts[0])} to '
          f'{tuple(round(v) for v in pts[-1])}')
    for s, what, p in sorted(ev):
        print(f'   {round(s):5d} {tuple(round(v) for v in p)} {what}')
