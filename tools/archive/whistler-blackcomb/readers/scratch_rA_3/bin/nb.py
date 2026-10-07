# neighbours: for each given piece, list pieces with an endpoint (or any point) near its endpoints
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
R = 12
for a in sys.argv[1:]:
    i = int(a); pts = byid[i]
    for lab, e in (('start', pts[0]), ('end', pts[-1])):
        out = []
        for j, q in byid.items():
            if j == i: continue
            d_end = min(math.hypot(q[0][0]-e[0], q[0][1]-e[1]), math.hypot(q[-1][0]-e[0], q[-1][1]-e[1]))
            d_any = dist_to(q, e)
            if d_any < R:
                out.append(f"{j}({cls[j]},{N.get(str(j))},{'end' if d_end<R else 'mid'} {d_any:.0f})")
        print(i, lab, f"({e[0]:.0f},{e[1]:.0f})", '; '.join(out))
