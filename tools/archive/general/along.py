"""For a piece: the arc length of each label projected on it and of each junction (another piece's end on it)."""
import json, math, sys
sys.path.insert(0, '/home/user/myskiruns/tools/trailmap')
from pdf_resort import Resort, line_dist
r = Resort(sys.argv[1])
P = {p['id']: r.pts_of(p) for p in r.load('pieces_cut.json')['polylines']}
names = r.names()
def proj(pts, q):
    best = (1e9, 0, None); run = 0
    for a, b in zip(pts, pts[1:]):
        dx, dy = b[0]-a[0], b[1]-a[1]; L = math.hypot(dx, dy) or 1e-9
        t = max(0, min(1, ((q[0]-a[0])*dx + (q[1]-a[1])*dy) / (L*L)))
        c = (a[0]+t*dx, a[1]+t*dy); d = math.dist(c, q)
        if d < best[0]: best = (d, run + t*L, c)
        run += L
    return best
for pid in map(int, sys.argv[2:]):
    pts = P[pid]; L = sum(math.dist(a, b) for a, b in zip(pts, pts[1:]))
    print(f'== piece {pid}: length {L:.0f}, from {[round(v) for v in pts[0]]} to {[round(v) for v in pts[-1]]}')
    ev = []
    for n in names:
        ds = [proj(pts, q) for q in n['pts']]
        close = [d for d in ds if d[0] < 25]
        if len(close) >= 0.6 * len(n['pts']):
            ev.append((min(d[1] for d in close), max(d[1] for d in close), 'label ' + n['name']))
    for oid, o in P.items():
        if oid == pid: continue
        for e in (o[0], o[-1]):
            d, s, c = proj(pts, e)
            if d < 6 and 3 < s < L - 3:
                ev.append((s, s, f'junction with {oid} at {[round(v) for v in c]}'))
    for a, b, what in sorted(ev):
        print(f'   {a:7.0f} {b:7.0f}  {what}')

def crossings(pid):
    pts = P[pid]
    out = []
    run = 0
    for a, b in zip(pts, pts[1:]):
        L = math.dist(a, b)
        for oid, o in P.items():
            if oid == pid: continue
            for c, d in zip(o, o[1:]):
                den = (b[0]-a[0])*(d[1]-c[1]) - (b[1]-a[1])*(d[0]-c[0])
                if abs(den) < 1e-9: continue
                t = ((c[0]-a[0])*(d[1]-c[1]) - (c[1]-a[1])*(d[0]-c[0])) / den
                u = ((c[0]-a[0])*(b[1]-a[1]) - (c[1]-a[1])*(b[0]-a[0])) / den
                if 0 <= t <= 1 and 0 <= u <= 1:
                    out.append((round(run + t*L), oid, [round(a[0]+t*(b[0]-a[0])), round(a[1]+t*(b[1]-a[1]))]))
        run += L
    return sorted(out)
if len(sys.argv) > 2:
    for pid in map(int, sys.argv[2:]):
        print(pid, 'crossings:', crossings(pid))
