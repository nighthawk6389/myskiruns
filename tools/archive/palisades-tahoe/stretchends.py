"""stretchends.py PANEL: each stretch along a name: is a line piece (any) near each of its two ends, and the angle
between the name and the trail's own line where it meets the stretch."""
import contextlib, io, json, math, sys
sys.path.insert(0, '/home/user/myskiruns/tools/trailmap')
import pdf_resort as pr
panel = sys.argv[1]
r = pr.Resort(f'palisades-tahoe/{panel}')
with contextlib.redirect_stdout(io.StringIO()):
    r.build()
N = json.load(open(r.work('names.json')))
P = {p['id']: r.pts_of(p) for p in r.load('pieces_cut.json')['polylines']}
lines = {i: q for i, q in P.items() if not N[str(i)].endswith('~') and N[str(i)] not in ('-',)}
S = r.R.SCALE
def near(e, own=None):
    best = None
    for i, q in lines.items():
        d = pr.line_dist(e, q)
        if best is None or d < best[0]:
            best = (d, i)
    return best
for k, v in N.items():
    if not v.endswith('~'):
        continue
    q = P[int(k)]
    out = []
    for e in (q[0], q[-1]):
        d, i = near(e)
        out.append(f'{d / S:5.1f}pt #{i} {N[str(i)][:18]:18s}')
    flag = ' <-- far end free' if min(float(o.split('pt')[0]) for o in out) < 3 and max(float(o.split('pt')[0]) for o in out) > 6 else ''
    print(f'{v[:-1]:22s} ' + ' | '.join(out) + flag)
