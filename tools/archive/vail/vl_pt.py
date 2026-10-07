"""Piece ids change whenever the extraction changes, so decisions are kept as a point on the piece (its middle, in
panel px): pt(panel, id, lines_file) gives that point; resolve(panel, P, (x, y)) finds the current piece through it."""
import json, math
SIZE = {'front-side': (4990, 2594), 'back-bowls': (4990, 2028), 'blue-sky': (4990, 3327)}


def pts_of(panel, p):
    W, H = SIZE[panel]
    return [(x * W / 100, y * H / 100) for x, y in p['points']]


def midpoint(pts):
    cum = [0]
    for a, b in zip(pts, pts[1:]):
        cum.append(cum[-1] + math.dist(a, b))
    t = cum[-1] / 2
    for i in range(1, len(pts)):
        if cum[i] >= t:
            f = (t - cum[i - 1]) / ((cum[i] - cum[i - 1]) or 1)
            return (round(pts[i - 1][0] + f * (pts[i][0] - pts[i - 1][0])), round(pts[i - 1][1] + f * (pts[i][1] - pts[i - 1][1])))
    return tuple(round(v) for v in pts[0])


def pt(panel, pid, lines_file):
    P = {p['id']: p for p in json.load(open(lines_file))['polylines']}
    return midpoint(pts_of(panel, P[pid]))


def seg_dist(q, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]; n = dx * dx + dy * dy
    t = max(0, min(1, ((q[0] - a[0]) * dx + (q[1] - a[1]) * dy) / n)) if n else 0
    return math.dist(q, (a[0] + t * dx, a[1] + t * dy))


def resolve(panel, P, q, tol=6):
    best = None
    for p in P:
        pts = pts_of(panel, p)
        d = min(seg_dist(q, pts[i], pts[i + 1]) for i in range(len(pts) - 1))
        if d <= tol and (best is None or d < best[0]):
            best = (d, p['id'])
    return best[1] if best else None
