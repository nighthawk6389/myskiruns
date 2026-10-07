"""near.py RESORT/PANEL id[,id..] [--r 220]: names printed within r map px of each piece (nearest point), with their
symbol and whether a piece already carries them."""
import contextlib, io, math, sys
sys.path.insert(0, '/home/user/myskiruns/tools/trailmap')
import pdf_resort as pr
r = pr.Resort(sys.argv[1])
ids = [int(v) for v in sys.argv[2].split(',')]
rad = float(sys.argv[sys.argv.index('--r') + 1]) if '--r' in sys.argv else 220
with contextlib.redirect_stdout(io.StringIO()):
    r.build()
named = {n for v in r.assign.values() for n in v}
P = {p['id']: (p['pt'] if 'pt' in p else r.pts_of(p)) for p in r.P}
for i in ids:
    out = []
    for n in r.names_all:
        d = min(pr.line_dist(q, P[i]) for q in n['pts'])
        if d < rad:
            out.append((round(d), n['name'], n.get('symbol') or '-', 'drawn' if n['name'] in named else 'NO LINE'))
    print(f'#{i}:', '; '.join(f'{nm} [{s}, {d}px, {dr}]' for d, nm, s, dr in sorted(out)))
