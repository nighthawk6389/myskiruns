# for each given piece, list other pieces whose ENDPOINTS lie within R px of any part of it
import json, sys, math
W, H = 4320, 2103
P = json.load(open('/home/user/myskiruns/work/whistler-blackcomb/main/pieces_cut.json'))['polylines']
N = json.load(open('/home/user/myskiruns/work/whistler-blackcomb/main/names.json'))
byid = {p['id']: [(x * W / 100, y * H / 100) for x, y in p['points']] for p in P}
cls = {p['id']: p['cls'] for p in P}
def segd(p, a, b):
    ax, ay = a; bx, by = b; px, py = p
    dx, dy = bx - ax, by - ay
    L = dx * dx + dy * dy
    t = 0 if L == 0 else max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / L))
    return math.hypot(ax + t * dx - px, ay + t * dy - py)
def dist_to(pts, q):
    if len(pts) == 1: return math.hypot(pts[0][0]-q[0], pts[0][1]-q[1])
    return min(segd(q, pts[i], pts[i+1]) for i in range(len(pts)-1))
R = float(sys.argv[1])
for a in sys.argv[2:]:
    i = int(a); pts = byid[i]
    out = []
    for j, q in byid.items():
        if j == i: continue
        for lab, e in (('s', q[0]), ('e', q[-1])):
            d = dist_to(pts, e)
            if d < R:
                out.append(f"{j}{lab}({cls[j]},{N.get(str(j))},{e[0]:.0f},{e[1]:.0f} d{d:.0f})")
    print(i, ':', '; '.join(out))
