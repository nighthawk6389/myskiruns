import json, sys, math
W, H = 4320, 2103
pcs = {p['id']: p for p in json.load(open('/home/user/myskiruns/work/whistler-blackcomb/main/pieces_cut.json'))['polylines']}
i = int(sys.argv[1])
pts = [(q[0]*W/100, q[1]*H/100) for q in pcs[i]['points']]
c = 0
out = [(0, pts[0])]
for k in range(1, len(pts)):
    c += math.dist(pts[k-1], pts[k]); out.append((c, pts[k]))
for c, p in out:
    print(f'{c:7.0f}  ({p[0]:.0f},{p[1]:.0f})')
