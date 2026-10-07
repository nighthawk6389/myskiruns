"""along.py ID FRACTION | ID cross OTHER_ID: the point on piece ID (map px) at that fraction of its length, or where
it comes closest to piece OTHER_ID (a crossing)."""
import math, sys
sys.path.insert(0, '/home/user/myskiruns/tools/trailmap')
import pdf_resort as pr
r = pr.Resort('park-city')
P = {p['id']: r.pts_of(p) for p in r.load('pieces_cut.json')['polylines']}
i = int(sys.argv[1]); pts = P[i]
dense = []
for a, b in zip(pts, pts[1:]):
    n = max(1, int(math.dist(a, b)))
    dense += [(a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n) for k in range(n)]
dense += [pts[-1]]
if sys.argv[2] == 'cross':
    q = min(dense, key=lambda q: pr.line_dist(q, P[int(sys.argv[3])]))
    print(f'{round(q[0])},{round(q[1])}', round(pr.line_dist(q, P[int(sys.argv[3])]), 1))
else:
    f = float(sys.argv[2])
    L = [0]
    for a, b in zip(dense, dense[1:]):
        L.append(L[-1] + math.dist(a, b))
    k = min(range(len(dense)), key=lambda k: abs(L[k] - f * L[-1]))
    q = dense[k]
    print(f'{round(q[0])},{round(q[1])}')
