"""nosym.py PANEL: names with no symbol, each with the nearest unassigned symbols (distance from its nearest glyph,
in pt) and the names nearest those symbols."""
import math, sys
sys.path.insert(0, '/home/user/myskiruns/tools/trailmap')
import pdf_resort as pr
p = sys.argv[1]
r = pr.Resort(f'palisades-tahoe/{p}')
names = r.names()
syms, loose = r.symbols(names)
sc = r.R.SCALE
for n in names:
    if n.get('symbol'):
        continue
    near = sorted((min(math.dist(s['c'], q) for q in n['pts']) / sc, s) for s in loose)[:2]
    near_all = sorted((min(math.dist(s['c'], q) for q in n['pts']) / sc, s) for s in syms)[:1]
    owner = None
    if near_all:
        s = near_all[0][1]
        owner = next((m['name'] for m in names if m.get('sym') is s), None)
    print(f"{n['name']:24s}", ' | '.join(f"{s['t']} {d:.1f}pt at ({s['c'][0]:.0f},{s['c'][1]:.0f})" for d, s in near),
          f"  nearest any: {near_all[0][1]['t']} {near_all[0][0]:.1f}pt owned by {owner}" if near_all else '')
