"""info.py x0,y0,x1,y1: Park City pieces (id cls name why len ends) and names (symbol, ends) inside the box (map px)."""
import json, sys
W = '/home/user/myskiruns/work/park-city'
b = tuple(map(float, sys.argv[1].split(',')))
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
WW, HH = Image.open(f'{W}/map.png').size
P = json.load(open(f'{W}/pieces_cut.json'))['polylines']
N = json.load(open(f'{W}/names.json'))
A = json.load(open(f'{W}/assign.json')) if False else {}
inb = lambda x, y: b[0] <= x <= b[2] and b[1] <= y <= b[3]  # noqa: E731
for p in P:
    pts = [(x * WW / 100, y * HH / 100) for x, y in p['points']]
    if not any(inb(*q) for q in pts):
        continue
    a, z = pts[0], pts[-1]
    print(f"{p['id']:4d} {p['cls']:9s} {N.get(str(p['id']), '?'):28s} L {p['lengthPx']:4d} ({a[0]:.0f},{a[1]:.0f})-({z[0]:.0f},{z[1]:.0f})")
