import json, sys
W, H = 4320, 2103
d = json.load(open('/home/user/myskiruns/work/whistler-blackcomb/main/pieces_cut.json'))['polylines']
names = json.load(open('/home/user/myskiruns/work/whistler-blackcomb/main/names.json'))
by = {p['id']: p for p in d}
step = int(sys.argv[1])
for a in sys.argv[2:]:
    p = by[int(a)]
    pts = [(round(x * W / 100), round(y * H / 100)) for x, y in p['points']]
    print(a, p['cls'], p['lengthPx'], names.get(a), 'npts', len(pts))
    print('   ', pts[::max(1, step)] + ([pts[-1]] if (len(pts)-1) % max(1,step) else []))
