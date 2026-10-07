import json, sys
W, H = 4320, 2103
P = json.load(open('/home/user/myskiruns/work/whistler-blackcomb/main/pieces_cut.json'))['polylines']
N = json.load(open('/home/user/myskiruns/work/whistler-blackcomb/main/names.json'))
byid = {p['id']: p for p in P}
for a in sys.argv[1:]:
    p = byid[int(a)]
    pts = [(round(q[0]*W/100), round(q[1]*H/100)) for q in p['points']]
    step = max(1, len(pts)//14)
    sub = pts[::step]
    if sub[-1] != pts[-1]: sub.append(pts[-1])
    print(a, p['cls'], N.get(a), 'len', p['lengthPx'], 'npts', len(pts), sub)
