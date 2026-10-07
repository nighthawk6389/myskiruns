"""tp.py name-or-slug[,...]: the pieces each Park City trail got (id, length, ends in map px, how named)."""
import contextlib, io, re, sys
sys.path.insert(0, '/home/user/myskiruns/tools/trailmap')
import pdf_resort as pr
r = pr.Resort('park-city')
with contextlib.redirect_stdout(io.StringIO()):
    r.build()
slug = lambda nm: re.sub(r'[^a-z0-9]+', '-', nm.lower().replace('’', '').replace("'", '')).strip('-')  # noqa: E731
P = {p['id']: p for p in r.load('pieces_cut.json')['polylines']}
for want in sys.argv[1].split(','):
    print(want)
    for pid, v in sorted(r.assign.items()):
        if slug(next(iter(v))) != want:
            continue
        q = r.pts_of(P[pid])
        tag = 'stretch' if pid in r.traced else r.why.get(pid, '')
        print(f'  {pid:4d} {P[pid]["cls"]:9s} L{P[pid]["lengthPx"]:5d} ({q[0][0]:.0f},{q[0][1]:.0f})-({q[-1][0]:.0f},{q[-1][1]:.0f}) {tag}')
