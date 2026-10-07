"""seqcheck.py: Park City pieces whose PDF stroke is drawn among another trail's strokes (the strokes just before and
after it belong to one other trail) while none of its own trail's strokes are near it in the drawing order."""
import collections, contextlib, io, math, sys
import pymupdf
sys.path.insert(0, '/home/user/myskiruns/tools/trailmap')
import pdf_resort as pr
r = pr.Resort('park-city')
with contextlib.redirect_stdout(io.StringIO()):
    r.build()
P = {p['id']: p for p in r.load('pieces_cut.json')['polylines']}
page = pymupdf.open(r.work('parkcity.pdf'))[0]
D = []
for d in page.get_drawings():
    if d['type'] not in ('s', 'fs') or not d.get('color') or (d.get('width') or 0) < 0.5:
        continue
    pts = []
    for it in d['items']:
        if it[0] == 'l':
            pts += [(it[1].x, it[1].y), (it[2].x, it[2].y)]
        elif it[0] == 'c':
            a, b, cc, e = it[1:5]
            pts += [((1-t)**3*a.x+3*(1-t)**2*t*b.x+3*(1-t)*t*t*cc.x+t**3*e.x, (1-t)**3*a.y+3*(1-t)**2*t*b.y+3*(1-t)*t*t*cc.y+t**3*e.y) for t in [k/8 for k in range(9)]]
    if pts:
        D.append((d['seqno'], pts))
pt = lambda q: (12 + q[0] / 2.5, 12 + q[1] / 2.5)  # noqa: E731
seq_of = {}
for pid, p in P.items():
    if pid in r.traced:
        continue
    q = r.pts_of(p); a, z = pt(q[0]), pt(q[-1]); m = pt(q[len(q) // 2])
    hit = [s for s, pts in D if min(math.dist(m, v) for v in pts) < 0.8
           and (min(math.dist(a, v) for v in pts) < 0.8 or min(math.dist(z, v) for v in pts) < 0.8)]
    if hit:
        seq_of[pid] = hit[0]
owner = {}
for pid, s in seq_of.items():
    if pid in r.assign:
        owner.setdefault(s, set()).add(next(iter(r.assign[pid])))
    elif pid in r.unnamed:
        owner.setdefault(s, set()).add('-')
by_trail = collections.defaultdict(list)
for pid, s in seq_of.items():
    if pid in r.assign:
        by_trail[next(iter(r.assign[pid]))].append(s)
for pid, s in sorted(seq_of.items(), key=lambda kv: kv[1]):
    if pid not in r.assign:
        continue
    t = next(iter(r.assign[pid]))
    own_near = [x for x in by_trail[t] if x != s and abs(x - s) <= 3]
    nb = [owner.get(s + k) for k in (-2, -1, 1, 2) if owner.get(s + k)]
    others = set().union(*nb) - {t} if nb else set()
    if not own_near and others and len(others) == 1:
        o = next(iter(others))
        print(f'{pid:4d} seq {s}: {t} ({r.why.get(pid, "")}), drawn among {o}\'s strokes')
