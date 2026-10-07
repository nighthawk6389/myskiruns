"""orange_list.py PAGE: each orange stroke other than the boundary (1.6) and hatching (0.85): index, width, dashes,
rect (pt), length (pt)."""
import sys, math, pymupdf
doc = pymupdf.open('/home/user/myskiruns/work/whistler-blackcomb/whistler.pdf'); p = doc[int(sys.argv[1])]
k = 0
for i, dr in enumerate(p.get_drawings()):
    c = dr.get('color')
    if dr['type'] not in ('s', 'fs') or not c or tuple(round(v, 3) for v in c) != (0.97, 0.579, 0.116): continue
    w = round(dr.get('width') or 0, 2)
    if w in (0.85,): continue
    L = 0
    for it in dr['items']:
        if it[0] == 'l': L += math.dist((it[1].x, it[1].y), (it[2].x, it[2].y))
        elif it[0] == 'c': L += math.dist((it[1].x, it[1].y), (it[4].x, it[4].y))
    r = dr['rect']
    print(i, w, dr.get('dashes'), dr.get('closePath'), tuple(round(v) for v in r), round(L), len(dr['items']), dr['type'])
