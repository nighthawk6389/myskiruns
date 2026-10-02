"""Shared by Vail's pipeline scripts: the panels, the working directory, and the point helpers that keep every
decision keyed by a point on the map rather than by a piece or symbol id (ids change whenever the extraction is
re-tuned; a point still finds the same line or symbol)."""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '../../../..'))
sys.path.insert(0, os.path.join(REPO, 'tools/trailmap'))

# downloaded panels and intermediate files (not committed): VAIL_WORK, default work/vail in the repo
WORK = os.path.abspath(os.environ.get('VAIL_WORK', os.path.join(REPO, 'work/vail')))
PANELS = ('front-side', 'back-bowls', 'blue-sky')
SIZE = {'front-side': (4990, 2594), 'back-bowls': (4990, 2028), 'blue-sky': (4990, 3327)}
CLS = {'circle': 'green', 'square': 'blue', 'diamond': 'black', 'double-diamond': 'black', 'ex': 'black'}


def work(name):
    return os.path.join(WORK, name)


def pts_of(panel, p):
    """A piece's points in panel px (pieces store percent of the image)."""
    W, H = SIZE[panel]
    return [(x * W / 100, y * H / 100) for x, y in p['points']]


def midpoint(pts):
    """The point halfway along a polyline: where a decision about a whole piece is recorded."""
    cum = [0]
    for a, b in zip(pts, pts[1:]):
        cum.append(cum[-1] + math.dist(a, b))
    t = cum[-1] / 2
    for i in range(1, len(pts)):
        if cum[i] >= t:
            f = (t - cum[i - 1]) / ((cum[i] - cum[i - 1]) or 1)
            return (round(pts[i - 1][0] + f * (pts[i][0] - pts[i - 1][0])),
                    round(pts[i - 1][1] + f * (pts[i][1] - pts[i - 1][1])))
    return tuple(round(v) for v in pts[0])


def seg_dist(q, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]; n = dx * dx + dy * dy
    t = max(0, min(1, ((q[0] - a[0]) * dx + (q[1] - a[1]) * dy) / n)) if n else 0
    return math.dist(q, (a[0] + t * dx, a[1] + t * dy))


def resolve(panel, P, q, tol=6):
    """The piece through point q (nearest within tol px), or None."""
    best = None
    for p in P:
        pts = pts_of(panel, p)
        d = min(seg_dist(q, pts[i], pts[i + 1]) for i in range(len(pts) - 1))
        if d <= tol and (best is None or d < best[0]):
            best = (d, p['id'])
    return best[1] if best else None


def symbol_names(panel, syms):
    """Each detected symbol's index -> (name, kind) from names.SYMBOLS, matched by centre. name None = not a trail
    symbol, '?' = printed with no name. Warns about detected symbols nobody read and readings with no symbol."""
    from names import SYMBOLS
    out, used = {}, set()
    for s in syms:
        best = min(((math.dist(s['c'], q), k) for k, (q, _n, _kind) in enumerate(SYMBOLS[panel])), default=None)
        if best is None or best[0] > max(6, 0.6 * s['r']):
            print(f'  warning: {panel} symbol {s["i"]} ({s["t"]}) at {[round(v) for v in s["c"]]} has no reading '
                  '(names.py)', file=sys.stderr)
            continue
        q, n, kind = SYMBOLS[panel][best[1]]
        used.add(best[1])
        if n is not None and kind != s['t']:
            print(f'  note: {panel} {n} at {q}: read as {kind}, detected as {s["t"]}; using {kind}', file=sys.stderr)
        out[s['i']] = (n, kind)
    for k, (q, n, kind) in enumerate(SYMBOLS[panel]):
        if k not in used:
            print(f'  warning: {panel} reading {n!r} at {q} matches no detected symbol', file=sys.stderr)
    return out


def load(name):
    return json.load(open(work(name)))
