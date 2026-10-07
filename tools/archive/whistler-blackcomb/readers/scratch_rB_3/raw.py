import json, sys, math
W, H = 4320, 2103
raw = json.load(open('/home/user/myskiruns/work/whistler-blackcomb/main/pieces.json'))
print('source:', raw.get('_source'))
rp = raw['polylines']
cut = {p['id']: p for p in json.load(open('/home/user/myskiruns/work/whistler-blackcomb/main/pieces_cut.json'))['polylines']}
def px(p): return [(x*W/100, y*H/100) for x, y in p['points']]
for a in sys.argv[1:]:
    c = cut[int(a)]
    cp = px(c)
    best = []
    for r in rp:
        rr = px(r)
        # mean min distance of cut points to raw polyline vertices
        dsum = 0
        for (x, y) in cp:
            dsum += min(math.hypot(x-u, y-v) for u, v in rr)
        best.append((dsum/len(cp), r['id'], r['cls'], r['lengthPx'], len(rr)))
    best.sort()
    print(a, c['cls'], c['lengthPx'], '->', best[:2])
