"""info.py PANEL x0,y0,x1,y1 : pieces (id cls tag why len ends) and names (with symbol) inside the box."""
import json, sys
sys.path.insert(0, '/home/user/myskiruns/tools/trailmap')
panel = sys.argv[1]; b = tuple(map(float, sys.argv[2].split(',')))
W = f'/home/user/myskiruns/work/whistler-blackcomb/{panel}'
from PIL import Image
WW, HH = Image.open(f'{W}/map.png').size
P = json.load(open(f'{W}/pieces_cut.json'))['polylines']
N = json.load(open(f'{W}/names.json'))
A = json.load(open(f'{W}/assign.json'))
inb = lambda x, y: b[0] <= x <= b[2] and b[1] <= y <= b[3]
for p in P:
    pts = [(x * WW / 100, y * HH / 100) for x, y in p['points']]
    if not any(inb(*q) for q in pts): continue
    a, z = pts[0], pts[-1]
    print(f"{p['id']:4d} {p['cls']:6s} {N.get(str(p['id']), '?'):28.28s} {A['why'].get(str(p['id']), ''):34.34s} L{p['lengthPx']:5d} ({a[0]:.0f},{a[1]:.0f})-({z[0]:.0f},{z[1]:.0f})")
import pdf_resort as pr
r = pr.Resort(f'whistler-blackcomb/{panel}')
names = r.names(); r.symbols(names)
for n in names:
    if inb(*n['c']):
        print('   NAME', n['name'], n.get('symbol'), [round(v) for v in n['c']], 'ends', [round(v) for v in n['pts'][0]], [round(v) for v in n['pts'][-1]])
