"""probe.py x,y ...  - the PDF's drawings near each point (PDF pt): distance, seqno, type, fill, stroke colour,
width, fill opacity, box and item count, nearest first (to find the drawing numbers lines.py leaves out).

    python3 tools/trailmap/resorts/copper-mountain/checks/probe.py 420,297 531,561
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import PDF  # noqa: E402
import pymupdf, math
p = pymupdf.open(PDF)[0]
D = p.get_drawings(extended=False)
def near(d, x, y, tol):
    r = d['rect']
    if not (r.x0 - tol <= x <= r.x1 + tol and r.y0 - tol <= y <= r.y1 + tol):
        return None
    best = 1e9
    for it in d['items']:
        pts = [it[1], it[-1]] if it[0] in ('l', 'c') else []
        if it[0] == 'c':
            pts = [it[1], it[2], it[3], it[4]]
        for q in pts:
            best = min(best, math.dist((q.x, q.y), (x, y)))
    return best
for arg in sys.argv[1:]:
    x, y = map(float, arg.split(','))
    print('==', x, y)
    rows = []
    for d in D:
        b = near(d, x, y, 3)
        if b is None or b > 6:
            continue
        r = d['rect']
        if r.width * r.height > 200000:
            continue
        rows.append((b, d['seqno'], d['type'], tuple(round(v, 2) for v in d['fill']) if d.get('fill') else None,
                     tuple(round(v, 2) for v in d['color']) if d.get('color') else None, round(d.get('width') or 0, 2),
                     d.get('fill_opacity'), [round(v) for v in r], len(d['items'])))
    for row in sorted(rows)[:14]:
        print('  ', row)
