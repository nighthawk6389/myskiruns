"""seq.py id[,id...]: for each Park City piece, the PDF stroke(s) it came from (seqno, colour, dashes), found by its
end points: drawing order often groups one run's strokes (a line cut by a label)."""
import json, math, sys
import pymupdf
sys.path.insert(0, '/home/user/myskiruns/tools/trailmap')
import pdf_resort as pr
r = pr.Resort('park-city')
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
            a, b, cc, e = it[1:5]
            pts += [((1-t)**3*a.x+3*(1-t)**2*t*b.x+3*(1-t)*t*t*cc.x+t**3*e.x, (1-t)**3*a.y+3*(1-t)**2*t*b.y+3*(1-t)*t*t*cc.y+t**3*e.y) for t in [k/8 for k in range(9)]]
    if pts:
        D.append((d['seqno'], tuple(round(v, 2) for v in c), round(d.get('width') or 0, 2), d.get('dashes') not in (None, '[] 0'), pts))
pt = lambda q: (12 + q[0] / 2.5, 12 + q[1] / 2.5)  # noqa: E731
for i in map(int, sys.argv[1].split(',')):
    a, z = pt(P[i][0]), pt(P[i][-1])
    hits = [(s, c, w, dsh) for s, c, w, dsh, pts in D if min(math.dist(a, q) for q in pts) < 0.6 and min(math.dist(z, q) for q in pts) < 0.6]
    print(i, N.get(str(i)), [(round(a[0], 1), round(a[1], 1)), (round(z[0], 1), round(z[1], 1))], hits[:3])
