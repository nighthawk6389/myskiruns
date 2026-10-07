"""tps.py slug[,...]: each Park City trail's pieces with the drawing order (seqno) of the PDF stroke each came from:
one run's strokes are usually drawn one after another, so a piece far off in the order is worth a look."""
import contextlib, io, math, re, sys
import pymupdf
sys.path.insert(0, '/home/user/myskiruns/tools/trailmap')
import pdf_resort as pr
r = pr.Resort('park-city')
with contextlib.redirect_stdout(io.StringIO()):
    r.build()
slug = lambda nm: re.sub(r'[^a-z0-9]+', '-', nm.lower().replace('’', '').replace("'", '')).strip('-')  # noqa: E731
P = {p['id']: p for p in r.load('pieces_cut.json')['polylines']}
page = pymupdf.open(r.work('parkcity.pdf'))[0]
D = []
for d in page.get_drawings():
    if d['type'] not in ('s', 'fs') or not d.get('color'):
        continue
    pts = []
    for it in d['items']:
        if it[0] == 'l':
            pts += [(it[1].x, it[1].y), (it[2].x, it[2].y)]
        elif it[0] == 'c':
            a, b, cc, e = it[1:5]
            pts += [((1-t)**3*a.x+3*(1-t)**2*t*b.x+3*(1-t)*t*t*cc.x+t**3*e.x, (1-t)**3*a.y+3*(1-t)**2*t*b.y+3*(1-t)*t*t*cc.y+t**3*e.y) for t in [k/8 for k in range(9)]]
    if pts:
        D.append((d['seqno'], pts))
pt = lambda q: (12 + q[0] / 2.5, 12 + q[1] / 2.5)  # noqa: E731
def seqs(pid):
    q = r.pts_of(P[pid]); a, z = pt(q[0]), pt(q[-1]); m = pt(q[len(q) // 2])
    return [s for s, pts in D if min(math.dist(m, v) for v in pts) < 0.8
            and (min(math.dist(a, v) for v in pts) < 0.8 or min(math.dist(z, v) for v in pts) < 0.8)][:3]
for want in sys.argv[1].split(','):
    rows = []
    for pid, v in sorted(r.assign.items()):
        if slug(next(iter(v))) != want:
            continue
        q = r.pts_of(P[pid])
        tag = 'stretch' if pid in r.traced else r.why.get(pid, '')
        rows.append(f'  {pid:4d} L{P[pid]["lengthPx"]:5d} ({q[0][0]:.0f},{q[0][1]:.0f})-({q[-1][0]:.0f},{q[-1][1]:.0f}) seq {seqs(pid)} {tag}')
    print(want); print('\n'.join(rows))
