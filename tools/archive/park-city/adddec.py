"""adddec.py FILE "comment": record FILE's id=NAME / id=-:why / x,y=NAME lines (# comments ignored) in Park City's
decisions.py, each id as the point on its piece farthest from every other piece (ids of the last build), so a
decision never sits on a junction."""
import math, sys
sys.path.insert(0, '/home/user/myskiruns/tools/trailmap')
import pdf_resort as pr
f, comment = sys.argv[1:3]
r = pr.Resort('park-city')
P = {p['id']: r.pts_of(p) for p in r.load('pieces_cut.json')['polylines']}


def best(i):
    pts = P[i]
    dense = []
    for a, b in zip(pts, pts[1:]):
        n = max(1, int(math.dist(a, b) / 2))
        dense += [(a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n) for k in range(n)]
    dense += [pts[-1]]
    inner = dense[len(dense) // 10: len(dense) - len(dense) // 10] or dense
    q = max(inner, key=lambda q: min(pr.line_dist(q, P[j]) for j in P if j != i))
    d = min(pr.line_dist(q, P[j]) for j in P if j != i)
    if d < 6:
        print(f'  warning: piece {i}: its best point is {d:.1f} px from another piece')
    return f'{round(q[0])},{round(q[1])}'


args = []
for line in open(f):
    line = line.strip()
    if not line or line.startswith('#'):
        continue
    k, v = line.split('=', 1)
    args.append(f'{k if "," in k else best(int(k))}={v}')
pr.add(r, comment, args)
