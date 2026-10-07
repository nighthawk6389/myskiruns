"""binfo.py RESORT/PANEL [x0,y0,x1,y1]: pieces (crossing the box): id, class, name, why, length, ends."""
import contextlib, io, sys
sys.path.insert(0, '/home/user/myskiruns/tools/trailmap')
import pdf_resort as pr
r = pr.Resort(sys.argv[1])
b = tuple(map(float, sys.argv[2].split(','))) if len(sys.argv) > 2 else (-1e9, -1e9, 1e9, 1e9)
with contextlib.redirect_stdout(io.StringIO()):
    r.build()
inb = lambda x, y: b[0] <= x <= b[2] and b[1] <= y <= b[3]  # noqa: E731
for p in r.P:
    q = p['pt'] if 'pt' in p else r.pts_of(p)
    if not any(inb(*v) for v in q):
        continue
    nm = '/'.join(sorted(r.assign.get(p['id'], []))) or ('-' if p['id'] in r.unnamed else '?')
    tag = 'stretch' if p['id'] in r.traced else r.why.get(p['id'], '')
    print(f"{p['id']:4d} {p['cls']:9s} {nm:26s} {tag:34s} L{p['lengthPx']:5d} ({q[0][0]:.0f},{q[0][1]:.0f})-({q[-1][0]:.0f},{q[-1][1]:.0f})")
