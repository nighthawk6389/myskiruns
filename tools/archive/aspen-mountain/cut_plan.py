"""For each piece a build left with several names: where along it each name is printed (the arc length of its letters'
projections onto the piece, px) and the junctions on it (other pieces' ends within 3 px), with a cut proposed at the
junction between each two names' spans (else their midpoint): points to check on crops before writing CUTS.
cut_plan.py <resort>/<panel> (run from the repo root after `pdf_resort.py <resort>/<panel> build`)."""
import json
import math
import sys

from PIL import Image

rid = sys.argv[1]
W_DIR = f'work/{rid}'
W, H = Image.open(f'{W_DIR}/map.png').size
P = {p['id']: [(x * W / 100, y * H / 100) for x, y in p['points']]
     for p in json.load(open(f'{W_DIR}/pieces_cut.json'))['polylines']}
A = json.load(open(f'{W_DIR}/assign.json'))['assign']


def proj(q, pts):
    """(distance, arc length) of q's nearest point on the polyline."""
    best, s = (math.inf, 0), 0
    for a, b in zip(pts, pts[1:]):
        dx, dy = b[0] - a[0], b[1] - a[1]
        n = dx * dx + dy * dy
        t = max(0, min(1, ((q[0] - a[0]) * dx + (q[1] - a[1]) * dy) / n)) if n else 0
        p = (a[0] + t * dx, a[1] + t * dy)
        d = math.dist(q, p)
        if d < best[0]:
            best = (d, s + t * math.sqrt(n))
        s += math.sqrt(n)
    return best


def at(pts, s):
    for a, b in zip(pts, pts[1:]):
        L = math.dist(a, b)
        if s <= L:
            t = s / L if L else 0
            return (round(a[0] + t * (b[0] - a[0])), round(a[1] + t * (b[1] - a[1])))
        s -= L
    return tuple(round(v) for v in pts[-1])


# the build's names (pdf_resort.py's reading: joined, renamed, spelled), each label's letters in map px
sys.path.insert(0, 'tools/trailmap')
from pdf_resort import Resort  # noqa: E402
lab_pos = {}
for n in Resort(rid).names():
    lab_pos.setdefault(n['name'], []).extend(n['pts'])
for pid, nms in sorted(A.items(), key=lambda t: int(t[0])):
    if len(nms) < 2:
        continue
    pts = P[int(pid)]
    total = sum(math.dist(a, b) for a, b in zip(pts, pts[1:]))
    spans = []
    for nm in nms:
        cands = [proj(tuple(c), pts) for c in lab_pos.get(nm, [])]
        cands = [c for c in cands if c[0] < 60]
        if cands:
            spans.append((min(c[1] for c in cands), max(c[1] for c in cands), nm))
    spans.sort()
    ends = [p for q, op in P.items() if q != int(pid) for p in (op[0], op[-1])]
    junc = sorted({round(s) for d, s in (proj(e, pts) for e in ends) if d < 3 and 5 < s < total - 5})
    print(f'piece {pid} ({round(total)} px, from {tuple(round(v) for v in pts[0])} to {tuple(round(v) for v in pts[-1])})')
    for a, b, nm in spans:
        print(f'   {nm}: at {round(a)}-{round(b)} px, {at(pts, (a + b) / 2)}')
    for (a1, b1, n1), (a2, b2, n2) in zip(spans, spans[1:]):
        mid = (b1 + a2) / 2
        js = [j for j in junc if b1 <= j <= a2] or junc
        j = min(js, key=lambda j: abs(j - mid)) if js else mid
        print(f'   cut {n1} | {n2}: at {round(j)} px {at(pts, j)} ({"junction" if j in junc else "midpoint"})')
