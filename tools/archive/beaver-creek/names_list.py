import sys, io, contextlib
sys.path.insert(0, 'tools/trailmap')
sys.argv = ['pdf_resort.py', sys.argv[1]]
import pdf_resort as pr
r = pr.Resort(sys.argv[1])
with contextlib.redirect_stdout(io.StringIO()):
    r.build()
names = set(getattr(r.R, 'NAMES', ()))
assigned = {n for v in r.assign.values() for n in v}
for n in sorted(r.names_all, key=lambda n: n['name']):
    tag = 'R' if n['name'] in names else '-'
    print(tag, 'L' if n['name'] in assigned else '.', repr(n['name']), '<-', repr(n['printed']), n.get('symbol'), [round(v) for v in n['c']])
