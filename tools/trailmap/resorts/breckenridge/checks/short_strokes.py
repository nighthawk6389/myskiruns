"""Every trail-coloured stroke run Breckenridge's first extraction pass drops as shorter than 4 pt (regen.sh's flags:
0.95-1.05 pt, the three trail colours, the panels excluded), with its drawing number, length and ends in PDF points
and map px: the 8 lead-in stubs of 2.8-4 pt that regen.sh's second pass appends (352-359), and two 0.74 pt scraps
it leaves out (--min-length 2.5).

    python3 tools/trailmap/resorts/breckenridge/checks/short_strokes.py
"""
import math, os, sys
import pymupdf
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../..'))
from common import PDF  # noqa: E402
from extract_pdf_vectors import bezier  # noqa: E402

CLASSES = {(0.0, 0.0, 0.0): 'black', (0.01, 0.28, 0.82): 'blue', (0.02, 0.53, 0.02): 'green'}
EXCLUDE = [(1326, 400, 1458, 925), (1094, 520, 1326, 925), (964, 685, 1086, 915), (8, 735, 168, 925)]
X0, Y0, X1, Y1 = 0, 80, 1458, 925


def runs(page, min_len, max_len):
    """(drawing number, class, points in pt) of each kept run, as extract_pdf_vectors.py splits and filters them."""
    out = []
    for seq, d in enumerate(page.get_drawings()):
        if d['type'] != 's' or not d.get('color') or not 0.95 <= (d.get('width') or 0) <= 1.05:
            continue
        cls = CLASSES.get(tuple(round(v, 2) for v in d['color']))
        if not cls:
            continue
        run, rs = [], []
        for it in d['items']:
            if it[0] == 'l':
                start, seg = it[1], [(it[2].x, it[2].y)]
            elif it[0] == 'c':
                start, seg = it[1], bezier(*it[1:5])
            else:
                continue
            if run and math.hypot(run[-1][0] - start.x, run[-1][1] - start.y) > 0.5:
                rs.append(run); run = []
            if not run:
                run = [(start.x, start.y)]
            run.extend(seg)
        if run:
            rs.append(run)
        for r in rs:
            length = sum(math.dist(p, q) for p, q in zip(r, r[1:]))
            xs, ys = [p[0] for p in r], [p[1] for p in r]
            if not min_len <= length < max_len:
                continue
            if math.dist(r[0], r[-1]) < 0.5 and math.hypot(max(xs) - min(xs), max(ys) - min(ys)) < 10:
                continue
            if not any(X0 <= x <= X1 and Y0 <= y <= Y1 for x, y in r):
                continue
            if any(all(e[0] <= x <= e[2] and e[1] <= y <= e[3] for x, y in r) for e in EXCLUDE):
                continue
            out.append((seq, cls, r))
    return out


if __name__ == '__main__':
    page = pymupdf.open(PDF)[0]
    found = runs(page, 0, 4)
    for seq, cls, r in sorted(found, key=lambda o: -sum(math.dist(p, q) for p, q in zip(o[2], o[2][1:]))):
        L = sum(math.dist(p, q) for p, q in zip(r, r[1:]))
        ends = [r[0], r[-1]]
        print(f'drawing {seq:5d} {cls:5s} {L:5.2f} pt  pt {[(round(x, 1), round(y, 1)) for x, y in ends]}  '
              f'px {[(round(3 * x, 1), round(3 * (y - Y0), 1)) for x, y in ends]}')
    print(len(found), 'runs under 4 pt')
