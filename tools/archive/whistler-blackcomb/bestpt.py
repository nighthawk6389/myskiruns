"""bestpt.py PANEL ID [ID...]: for each piece (ids of the last build), the point on it (map px) farthest from every
other piece, and that distance: a safe point to record a decision with."""
import json, math, sys
sys.path.insert(0, '/home/user/myskiruns/tools/trailmap')
import pdf_resort as pr
panel = sys.argv[1]
r = pr.Resort(f'whistler-blackcomb/{panel}')
P = {p['id']: r.pts_of(p) for p in r.load('pieces_cut.json')['polylines']}
for i in map(int, sys.argv[2:]):
    pts = P[i]
    dense = []
    for a, b in zip(pts, pts[1:]):
        n = max(1, int(math.dist(a, b) / 2))
        dense += [(a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n) for k in range(n)]
    best = max(dense[len(dense) // 10: len(dense) - len(dense) // 10] or dense,
               key=lambda q: min(pr.line_dist(q, P[j]) for j in P if j != i))
    d = min(pr.line_dist(best, P[j]) for j in P if j != i)
    print(i, f'{round(best[0])},{round(best[1])}', f'{d:.0f} px from the nearest other piece')
