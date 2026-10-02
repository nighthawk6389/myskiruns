"""Vail: name each line piece of a panel. Vail draws a trail's symbol on its line with the name printed beside
it, so a piece through a named symbol, or starting at it, or whose top end lies along the way the name runs
(within REACH px), takes that name (greedy, nearest first: one piece per symbol). Then decisions.py applies:
CUTS split pieces first, CHECKED points override, UNNAMED points mark pieces that are not trails. Names then
spread along unlabelled continuations (an end that meets exactly one other piece).

    python3 tools/trailmap/resorts/vail/build.py [panel ...]

Reads $VAIL_WORK/lines_<panel>.json and syms_<panel>.json; writes pieces_<panel>.json (after the cuts; the ids
decisions are resolved against), assign_<panel>.json ({assign: {id: [names]}, why, unnamed}) and
names_<panel>.json ({id: name, or '-' for not a trail}: grid_crop.py --names, for review tiles).
"""
import collections
import json
import math
import sys

from common import CLS, PANELS, SIZE, load, pts_of, resolve, seg_dist, symbol_names, work
from decisions import CHECKED, CUTS, UNNAMED

REACH = {'front-side': 230, 'back-bowls': 360, 'blue-sky': 620}  # the longest printed name, px


def dist(q, pts):
    return min(seg_dist(q, pts[i], pts[i + 1]) for i in range(len(pts) - 1))


def build(panel):
    W, H = SIZE[panel]
    P = load(f'lines_{panel}.json')['polylines']
    # one drawn line carrying two trails: the piece through the point is split there
    for on, q in CUTS.get(panel, []):
        pid = resolve(panel, P, on, tol=8)
        if pid is None:
            print('  cut piece not found at', on); continue
        p = P[pid]
        pts = pts_of(panel, p)
        best = (math.inf, 1, None)
        for i in range(1, len(pts)):
            (ax, ay), (bx, by) = pts[i - 1], pts[i]
            dx, dy = bx - ax, by - ay
            t = max(0, min(1, ((q[0] - ax) * dx + (q[1] - ay) * dy) / ((dx * dx + dy * dy) or 1e-9)))
            c = (ax + t * dx, ay + t * dy)
            if math.dist(c, q) < best[0]:
                best = (math.dist(c, q), i, c)
        _, i, c = best
        first, second = pts[:i] + [c], [c] + pts[i:]
        pct = lambda s: [[round(100 * x / W, 3), round(100 * y / H, 3)] for x, y in s]  # noqa: E731
        ln = lambda s: round(sum(math.dist(s[k - 1], s[k]) for k in range(1, len(s))))  # noqa: E731
        p['points'], p['lengthPx'] = pct(first), ln(first)
        P.append({'id': len(P), 'cls': p['cls'], 'lengthPx': ln(second), 'points': pct(second)})
    json.dump({'polylines': P}, open(work(f'pieces_{panel}.json'), 'w'))
    for p in P:
        p['pt'] = [(x * W / 100, y * H / 100) for x, y in p['points']]
    syms = load(f'syms_{panel}.json')
    read = symbol_names(panel, syms)
    assign = collections.defaultdict(set); why = {}
    cands = []  # (score, symbol index, name, piece)
    for s in syms:
        n, kind = read.get(s['i'], (None, None))
        if not n or n == '?':
            continue
        c, r, cls = s['c'], s['r'], CLS[kind]
        for p in P:
            if p['cls'] != cls:
                continue
            pts = p['pt']
            if dist(c, pts) < 0.9 * r and min(math.dist(c, pts[0]), math.dist(c, pts[-1])) > 2.5 * r:
                cands.append((0.0, s['i'], n, p['id']))  # the symbol sits on this piece
                continue
            for k in (0, -1):
                e = pts[k]; d = math.dist(c, e)
                if d > REACH[panel]:
                    continue
                other = pts[-1] if k == 0 else pts[0]
                inner = pts[min(3, len(pts) - 1)] if k == 0 else pts[max(-4, -len(pts))]
                v = (inner[0] - e[0], inner[1] - e[1]); lv = math.hypot(*v) or 1
                v = (v[0] / lv, v[1] / lv)
                if d < 1.8 * r + 8:
                    cands.append((d / 4, s['i'], n, p['id']))  # the line starts right at the symbol
                    continue
                u = ((e[0] - c[0]) / d, (e[1] - c[1]) / d)
                align = u[0] * v[0] + u[1] * v[1]  # the line goes on the way the text runs
                downhill = other[1] >= e[1] - 0.3 * abs(other[0] - e[0])  # this end is the piece's top
                if align > 0.75 and downhill:
                    cands.append((d * (2.2 - align), s['i'], n, p['id']))
    done_sym, done_piece = set(), set()
    for sc, i, n, pid in sorted(cands):
        if i in done_sym or pid in done_piece:
            continue
        done_sym.add(i); done_piece.add(pid)
        assign[pid].add(n); why[pid] = f'symbol {i}'
    fixed = set()
    for q, n in CHECKED.get(panel, []):
        pid = resolve(panel, P, q)
        if pid is None:
            print('  checked point on no piece:', q, n); continue
        assign[pid] = {n}; why[pid] = 'checked'; fixed.add(pid)
    unnamed = {}
    for q, note in UNNAMED.get(panel, []):
        pid = resolve(panel, P, q)
        if pid is None:
            print('  unnamed point on no piece:', q, note); continue
        assign.pop(pid, None); why[pid] = 'unnamed'; fixed.add(pid); unnamed[pid] = note
    ends = [(p['pt'][k], p['id']) for p in P for k in (0, -1)]

    def neighbours(pid):
        p = P[pid]; out = []
        for k in (0, -1):
            e = p['pt'][k]
            at = {i for f, i in ends if i != pid and math.dist(f, e) < 4}
            if len(at) == 1:
                out.append(next(iter(at)))
        return out
    changed = True
    while changed:
        changed = False
        for p in P:
            if assign.get(p['id']) or p['id'] in fixed:
                continue
            ns = set()
            for nb in neighbours(p['id']):
                if P[nb]['cls'] == p['cls'] and len(assign.get(nb, ())) == 1:
                    ns |= assign[nb]
            if len(ns) == 1:
                assign[p['id']] = set(ns); why[p['id']] = 'continuation'; changed = True
    json.dump({'assign': {str(k): sorted(v) for k, v in assign.items() if v}, 'why': {str(k): v for k, v in why.items()},
               'unnamed': {str(k): v for k, v in unnamed.items()}},
              open(work(f'assign_{panel}.json'), 'w'), indent=0)
    names = {str(k): '/'.join(sorted(v)) for k, v in assign.items() if v}
    names.update({str(k): '-' for k in unnamed})
    json.dump(names, open(work(f'names_{panel}.json'), 'w'))
    named = {n for v in assign.values() for n in v}
    want = {n for n, _k in read.values() if n and n != '?'}
    left = [p['id'] for p in P if not assign.get(p['id']) and p['id'] not in unnamed]
    print(panel, len(P), 'pieces;', sum(1 for p in P if assign.get(p['id'])), 'named,', len(unnamed), 'not trails,',
          len(left), 'undecided', left[:20], '; several names:', sum(1 for v in assign.values() if len(v) > 1),
          '; names on no detected piece (traced stretches or markers):', sorted(want - named))


for panel in sys.argv[1:] or PANELS:
    build(panel)
