import json, sys
W, H = 4320, 2103
pcs = {p['id']: p for p in json.load(open('/home/user/myskiruns/work/whistler-blackcomb/main/pieces_cut.json'))['polylines']}
names = json.load(open('/home/user/myskiruns/work/whistler-blackcomb/main/names.json'))
step = 1
for a in sys.argv[1:]:
    if a.startswith('step='): step = int(a[5:]); continue
    p = pcs[int(a)]
    pts = [(round(q[0]*W/100), round(q[1]*H/100)) for q in p['points']]
    print(a, p['cls'], p['lengthPx'], names.get(a), len(pts), 'pts:', pts[::step] + ([pts[-1]] if (len(pts)-1) % step else []))
