"""Write a pieces file with only the given ids (for grid_crop), and print each one's ends, length and mid point."""
import json, math, sys
W, H = 4104, 1560
src, out, ids = sys.argv[1], sys.argv[2], [int(v) for v in sys.argv[3:]]
P = json.load(open(src))
keep = [p for p in P['polylines'] if p['id'] in ids]
json.dump({'polylines': keep}, open(out, 'w'))
for p in keep:
    q = [(x * W / 100, y * H / 100) for x, y in p['points']]
    L = sum(math.dist(a, b) for a, b in zip(q, q[1:]))
    m = q[len(q) // 2]
    print(p['id'], 'from', [round(v) for v in q[0]], 'to', [round(v) for v in q[-1]], 'mid', [round(v) for v in m], 'len', round(L), p.get('cls', ''), p.get('expert', ''))
