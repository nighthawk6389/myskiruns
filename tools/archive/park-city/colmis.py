"""colmis.py: Park City pieces whose line colour doesn't match their trail's difficulty (green/blue/black/park)."""
import contextlib, io, re, sys
sys.path.insert(0, '/home/user/myskiruns/tools/trailmap')
import pdf_resort as pr
r = pr.Resort('park-city')
with contextlib.redirect_stdout(io.StringIO()):
    r.build()
ts = open('/home/user/myskiruns/src/data/resorts/park-city/trails.ts').read()
dif = {m.group(3): m.group(4) for m in re.finditer(r"id: '([^']+)', name: (['\"])(.*?)\2, difficulty: '([^']+)'", ts)}
want = {'green': 'green', 'blue': 'blue', 'black': 'black', 'double-black': 'black', 'park': 'freestyle'}
P = {p['id']: p for p in r.P}
disp = getattr(r.R, 'DISPLAY', {})
def title(nm):
    for k, v in dif.items():
        if re.sub(r'[^A-Z0-9]', '', k.upper().replace('’', "'")) == re.sub(r'[^A-Z0-9]', '', nm.upper().replace('’', "'")):
            return k, v
    return nm, None
for pid, v in sorted(r.assign.items()):
    nm = next(iter(v)); t, d = title(nm)
    if d and want.get(d) != P[pid]['cls']:
        q = r.pts_of(P[pid]) if 'pt' not in P[pid] else P[pid]['pt']
        print(f"{pid:4d} {P[pid]['cls']:9s} under {t} ({d}) L{P[pid]['lengthPx']} ({q[0][0]:.0f},{q[0][1]:.0f})-({q[-1][0]:.0f},{q[-1][1]:.0f}) {r.why.get(pid, '')}")
