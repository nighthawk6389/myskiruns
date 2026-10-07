"""lonely.py RESORT[/panels/PANEL]: label stretches whose label meets no line end (neither terminal within END_REACH)."""
import sys, contextlib, io, math
sys.path.insert(0, '/home/user/myskiruns/tools/trailmap')
import pdf_resort as pr
r = pr.Resort(sys.argv[1])
with contextlib.redirect_stdout(io.StringIO()):
    r.build()
R = r.R
reach = R.END_REACH * R.SCALE
real = [p for p in r.P if p['id'] not in r.traced]
ends = [p['pt'][k] for p in real for k in (0, -1)]
ll = set(getattr(R, 'LABEL_LINE', ()))
out = []
for pid, kind in r.traced.items():
    if kind != 'label':
        continue
    p = r.P[pid]
    nm = next(iter(r.assign[pid]))
    best = min((j for j, n in enumerate(r.names_) if n['name'] == nm), key=lambda j: min(math.dist(p['pt'][len(p['pt']) // 2], q) for q in r.names_[j]['pts']))
    n = r.names_[best]
    hit = [min(math.dist(t, e) for e in ends) for t, _s in r.terminals(n)]
    if min(hit) > reach:
        out.append((nm, nm in ll, [round(v) for v in n['c']], [round(h) for h in hit]))
print(sys.argv[1], len(out), out)
