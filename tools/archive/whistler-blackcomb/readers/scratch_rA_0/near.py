# usage: near.py x y [r]  (map px): strokes with a point within r map px (default 6) -> seq, colour, width, bbox (map px)
import pickle, sys, math
D = pickle.load(open('/tmp/claude-0/-home-user-myskiruns/6d543bfc-3ab1-5e7f-9c64-5c2d6dd5c830/scratchpad/wb/answers/scratch_rA_0/dr.pkl', 'rb'))
x, y = float(sys.argv[1]) / 2.5, float(sys.argv[2]) / 2.5
r = (float(sys.argv[3]) if len(sys.argv) > 3 else 6) / 2.5
def segd(p, a, b):
    ax, ay = a; bx, by = b; px, py = p
    dx, dy = bx - ax, by - ay
    L = dx * dx + dy * dy
    t = 0 if L == 0 else max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / L))
    return math.hypot(ax + t * dx - px, ay + t * dy - py)
for o in D:
    pts = o['pts']
    if not pts: continue
    x0, y0, x1, y1 = o['rect']
    if x < x0 - r or x > x1 + r or y < y0 - r or y > y1 + r: continue
    if len(pts) == 1: d = math.hypot(pts[0][0]-x, pts[0][1]-y)
    else: d = min(segd((x, y), pts[k], pts[k+1]) for k in range(len(pts)-1))
    if d <= r:
        c = tuple(round(v, 2) for v in o['color']) if o['color'] else None
        f = tuple(round(v, 2) for v in o['fill']) if o['fill'] else None
        print(o['i'], o['seq'], o['type'], 'col', c, 'fill', f, 'w', o['width'], 'dash', o['dashes'], 'bbox', [round(v*2.5) for v in o['rect']], 'n', len(pts), 'd', round(d*2.5,1))
