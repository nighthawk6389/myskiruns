import json, sys, math
W, H = 4320, 2103
P = json.load(open('/home/user/myskiruns/work/whistler-blackcomb/main/pieces_cut.json'))['polylines']
N = json.load(open('/home/user/myskiruns/work/whistler-blackcomb/main/names.json'))
x, y, r = map(float, sys.argv[1:4])
for p in P:
    pts = [(q[0]*W/100, q[1]*H/100) for q in p['points']]
    d = min(math.dist((x, y), q) for q in pts)
    de = min(math.dist((x, y), pts[0]), math.dist((x, y), pts[-1]))
    if d <= r:
        print(p['id'], p['cls'], N.get(str(p['id'])), 'len', p['lengthPx'], 'mindist %.0f enddist %.0f' % (d, de), 'ends', [round(v) for v in pts[0]], [round(v) for v in pts[-1]])
