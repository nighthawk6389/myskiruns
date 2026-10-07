"""Overlays lying along another trail's line: for a resort read by pdf_resort.py, every named piece that runs
along a piece of another name (within --tol map px) for --min px or more. Two overlays on one drawn line usually
mean a line drawn on under another one (a thin line inside a wide route, a run's line on along the traverse it
leaves: decisions.py TRIMS), or two runs on one stroke that wants a cut (CUTS); a crossing at a shallow angle or a
shared junction shows up too and needs nothing. Check each on a crop.

    python3 tools/trailmap/pdf_overlaps.py big-sky/main [--tol 3] [--min 25]
"""
import argparse
import contextlib
import io
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pdf_resort as pr  # noqa: E402


def dense(pts, step=2):
    out = []
    for a, b in zip(pts, pts[1:]):
        n = max(1, int(math.dist(a, b) / step))
        out += [(a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n) for k in range(n)]
    return out + [tuple(pts[-1])]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('resort', help='<resort> or <resort>/<panel>, as pdf_resort.py takes it')
    ap.add_argument('--tol', type=float, default=3, help='map px: closer than this is along the other line')
    ap.add_argument('--min', type=float, default=25, help='map px: the shortest stretch reported')
    a = ap.parse_args()
    r = pr.Resort(a.resort)
    with contextlib.redirect_stdout(io.StringIO()):
        r.build()
    P = {p['id']: r.pts_of(p) for p in r.P}
    box = {i: (min(x for x, _ in q), min(y for _, y in q), max(x for x, _ in q), max(y for _, y in q)) for i, q in P.items()}
    found = 0
    for i in sorted(r.assign):
        di = dense(P[i])
        for j in sorted(r.assign):
            b = box[j]
            if j == i or r.assign[j] == r.assign[i] or not (box[i][0] <= b[2] + a.tol and b[0] <= box[i][2] + a.tol
                                                            and box[i][1] <= b[3] + a.tol and b[1] <= box[i][3] + a.tol):
                continue
            run = best = start = bstart = 0
            for k, q in enumerate(di):
                if pr.line_dist(q, P[j]) < a.tol:
                    start = k if run == 0 else start
                    run += 1
                    if run > best:
                        best, bstart = run, start
                else:
                    run = 0
            if best * 2 >= a.min:
                p, q = di[bstart], di[bstart + best - 1]
                print(f'{i} {sorted(r.assign[i])} along {j} {sorted(r.assign[j])} for {best * 2} px: '
                      f'({p[0]:.0f},{p[1]:.0f})..({q[0]:.0f},{q[1]:.0f})')
                found += 1
    print(f'{found} stretches of one overlay along another')


if __name__ == '__main__':
    main()
