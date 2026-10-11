"""Each undecided piece of a panel: id, class, length, its ends and the named pieces meeting each end."""
import json, math, sys
W = sys.argv[1]
P = {p['id']: p for p in json.load(open(W + '/pieces_cut.json'))['polylines']}
N = json.load(open(W + '/names.json'))
from PIL import Image
w, h = Image.open(W + '/map.png').size
def px(p): return [(x * w / 100, y * h / 100) for x, y in p['points']]
ends = {i: (px(p)[0], px(p)[-1]) for i, p in P.items()}
def near(q, me):
    out = []
    for j, p in P.items():
        if j == me: continue
        pts = px(p)
        d = min(math.dist(q, a) for a in pts)
        if d < 8: out.append(f"{j}:{N.get(str(j), '?')}")
    return out
ids = [int(k) for k, v in N.items() if v == '?'] if len(sys.argv) < 3 else [int(a) for a in sys.argv[2].split(',')]
for i in sorted(ids):
    p = P[i]; pts = px(p)
    a, b = pts[0], pts[-1]
    m = pts[len(pts) // 2]
    print(f"{i} {p['cls']} {round(p['lengthPx'])}px  A({a[0]:.0f},{a[1]:.0f}) {near(a, i)}  B({b[0]:.0f},{b[1]:.0f}) {near(b, i)}  mid({m[0]:.0f},{m[1]:.0f})")
