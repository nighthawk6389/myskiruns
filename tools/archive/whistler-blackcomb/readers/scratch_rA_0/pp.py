import json, sys
W, H = 4320, 2103
d = json.load(open('/home/user/myskiruns/work/whistler-blackcomb/main/pieces_cut.json'))
names = json.load(open('/home/user/myskiruns/work/whistler-blackcomb/main/names.json'))
byid = {p['id']: p for p in d['polylines']}
ids = [int(a) for a in sys.argv[1:]]
for i in ids:
    p = byid[i]
    pts = [(round(x*W/100), round(y*H/100)) for x, y in p['points']]
    print(i, p['cls'], p['lengthPx'], names.get(str(i)), 'n=%d' % len(pts))
    step = max(1, len(pts)//25)
    print('   ', pts[::step] + ([pts[-1]] if (len(pts)-1) % step else []))
