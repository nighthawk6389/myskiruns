"""probe.py x,y ...  - the PDF's drawings (paths) near each PDF point: seqno, type, fill, stroke colour, width,
opacity, box and item count, nearest first (to find a line's or symbol's colour and width; scratch: probe.py)."""
import math
import os
import sys

import pymupdf

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from common import PDF  # noqa: E402

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
