"""Every name of a panel: printed text, name, centre (map px), symbol, the pieces named after it."""
import sys, os, io, contextlib, collections
sys.path.insert(0, '/home/user/myskiruns/tools/trailmap')
import pdf_resort as pr
r = pr.Resort(sys.argv[1])
with contextlib.redirect_stdout(io.StringIO()):
    r.build()
by = collections.defaultdict(list)
for pid, v in r.assign.items():
    for n in v:
        by[n].append(pid)
for n in sorted(r.names_, key=lambda n: (n['c'][0] // 400, n['c'][1])):
    print(f"{n['name'][:28]:28s} | {str(n.get('printed'))[:24]:24s} | ({n['c'][0]:.0f},{n['c'][1]:.0f}) | {n.get('symbol') or '-':14s} | {sorted(by.get(n['name'], []))}")
