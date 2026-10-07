"""pinfo.py RESORT/PANEL id [names...]: a piece's points (every ~20 px, with index) and where the given names'
characters run (first/last point), to pick a cut point."""
import contextlib, io, math, sys
sys.path.insert(0, '/home/user/myskiruns/tools/trailmap')
import pdf_resort as pr
r = pr.Resort(sys.argv[1]); i = int(sys.argv[2]); names = sys.argv[3:]
with contextlib.redirect_stdout(io.StringIO()):
    r.build()
P = {p['id']: r.pts_of(p) for p in r.P}
pts = P[i]
acc, last, out = 0, None, []
for k, q in enumerate(pts):
    if last is not None:
        acc += math.dist(last, q)
    if last is None or k == len(pts) - 1 or not out or acc - out[-1][0] >= 20:
        out.append((acc, k, q))
    last = q
print(f'#{i}: {len(pts)} points, {acc:.0f} px:', ' '.join(f'[{k}]({q[0]:.0f},{q[1]:.0f})@{a:.0f}' for a, k, q in out))
for n in r.names_all:
    if n['name'] in names:
        a, b = n['pts'][0], n['pts'][-1]
        da = min(range(len(pts)), key=lambda k: math.dist(pts[k], a)); db = min(range(len(pts)), key=lambda k: math.dist(pts[k], b))
        print(f"  {n['name']} [{n.get('symbol')}]: ({a[0]:.0f},{a[1]:.0f})..({b[0]:.0f},{b[1]:.0f}); nearest piece points [{da}] {math.dist(pts[da], a):.0f}px, [{db}] {math.dist(pts[db], b):.0f}px; symbol at {n.get('symbol_at')}")
