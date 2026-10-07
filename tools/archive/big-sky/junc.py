"""junc.py RESORT/PANEL id: the pieces whose ends lie on the piece (within 7 px), in order along it, with the
point, the arc length there and their names."""
import contextlib, io, json, math, sys
sys.path.insert(0, '/home/user/myskiruns/tools/trailmap')
import pdf_resort as pr
r = pr.Resort(sys.argv[1]); t = int(sys.argv[2])
with contextlib.redirect_stdout(io.StringIO()):
    r.build()
P = {p['id']: r.pts_of(p) for p in r.P}
N = json.load(open(r.work('names.json')))
pts = P[t]
cum = [0]
for a, b in zip(pts, pts[1:]):
    cum.append(cum[-1] + math.dist(a, b))
def locate(q):
    best = None
    for k, (a, b) in enumerate(zip(pts, pts[1:])):
        dx, dy = b[0] - a[0], b[1] - a[1]; L = dx * dx + dy * dy or 1
        u = max(0, min(1, ((q[0] - a[0]) * dx + (q[1] - a[1]) * dy) / L))
        c = (a[0] + u * dx, a[1] + u * dy); d = math.dist(c, q)
        if best is None or d < best[0]:
            best = (d, cum[k] + u * math.sqrt(L), c)
    return best
out = []
for i, q in P.items():
    if i == t:
        continue
    for e in (q[0], q[-1]):
        d, s, c = locate(e)
        if d < 7:
            out.append((s, i, c, d))
for s, i, c, d in sorted(out):
    print(f'  @{s:5.0f} ({c[0]:.0f},{c[1]:.0f}) piece {i} {N.get(str(i))} (end {d:.0f}px off)')
print(f'#{t} total {cum[-1]:.0f} px, ends ({pts[0][0]:.0f},{pts[0][1]:.0f}) ({pts[-1][0]:.0f},{pts[-1][1]:.0f})')
