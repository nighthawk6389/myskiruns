"""Pieces nearest each given point (map px): id, name, distance, nearest point on the piece."""
import json, math, sys
W, H = 4104, 1560
panel = sys.argv[1]
P = json.load(open(f'work/snowmass/{panel}/pieces_cut.json'))['polylines']
N = json.load(open(f'work/snowmass/{panel}/names.json'))
im = __import__('PIL.Image').Image.open(f'work/snowmass/{panel}/map.png').size
W, H = im
def near(q, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]; n = dx * dx + dy * dy
    t = max(0, min(1, ((q[0] - a[0]) * dx + (q[1] - a[1]) * dy) / n)) if n else 0
    p = (a[0] + t * dx, a[1] + t * dy)
    return math.dist(q, p), p
for arg in sys.argv[2:]:
    q = tuple(map(float, arg.split(',')))
    res = []
    for p in P:
        pts = [(x * W / 100, y * H / 100) for x, y in p['points']]
        d, c = min(near(q, a, b) for a, b in zip(pts, pts[1:]))
        res.append((round(d, 1), p['id'], N.get(str(p['id'])), p.get('cls'), (round(c[0]), round(c[1]))))
    res.sort()
    print(arg, res[:3])
