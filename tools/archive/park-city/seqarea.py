"""seqarea.py x0,y0,x1,y1 (map px): every Park City piece in the box with the seqno of its PDF stroke and its name,
sorted by seqno (one run's strokes are usually drawn one after another)."""
import json, math, sys
import pymupdf
sys.path.insert(0, '/home/user/myskiruns/tools/trailmap')
import pdf_resort as pr
r = pr.Resort('park-city')
b = tuple(map(float, sys.argv[1].split(',')))
P = {p['id']: r.pts_of(p) for p in r.load('pieces_cut.json')['polylines']}
N = json.load(open(r.work('names.json')))
page = pymupdf.open(r.work('parkcity.pdf'))[0]
D = []
for d in page.get_drawings():
    c = d.get('color')
    if d['type'] not in ('s', 'fs') or not c:
        continue
    pts = []
    for it in d['items']:
        if it[0] == 'l':
            pts += [(it[1].x, it[1].y), (it[2].x, it[2].y)]
        elif it[0] == 'c':
            a, bb, cc, e = it[1:5]
            pts += [((1-t)**3*a.x+3*(1-t)**2*t*bb.x+3*(1-t)*t*t*cc.x+t**3*e.x, (1-t)**3*a.y+3*(1-t)**2*t*bb.y+3*(1-t)*t*t*cc.y+t**3*e.y) for t in [k/8 for k in range(9)]]
    if pts:
        D.append((d['seqno'], pts, d.get('dashes') not in (None, '[] 0')))
pt = lambda q: (12 + q[0] / 2.5, 12 + q[1] / 2.5)  # noqa: E731
rows = []
for i, pts in P.items():
    if not any(b[0] <= x <= b[2] and b[1] <= y <= b[3] for x, y in pts):
        continue
    a, z = pt(pts[0]), pt(pts[-1])
    hit = [(s, dsh) for s, ps, dsh in D if min(math.dist(a, q) for q in ps) < 0.6 and min(math.dist(z, q) for q in ps) < 0.6]
    s, dsh = hit[0] if hit else (None, None)
    rows.append((s or 0, i, N.get(str(i), '?'), dsh, (round(pts[0][0]), round(pts[0][1])), (round(pts[-1][0]), round(pts[-1][1]))))
for row in sorted(rows):
    print(*row)
