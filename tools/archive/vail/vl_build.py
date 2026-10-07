"""Vail: name each line piece from the symbols (Vail draws a trail's symbol on its line, at its top, with the name
printed beside it): a piece through a named symbol, or starting at it and running downhill, takes that name; names
then spread along unlabelled continuations. Writes assign_<panel>.json {id: [names]} for checking on crops."""
import collections, json, math, sys
exec(open('vl_symnames.py').read())
exec(open('vl_checked.py').read())
exec(open('vl_pt.py').read())
CLS = {'circle': 'green', 'square': 'blue', 'diamond': 'black', 'double-diamond': 'black', 'ex': 'black'}
SIZE = {'front-side': (4990, 2594), 'back-bowls': (4990, 2028), 'blue-sky': (4990, 3327)}


def seg_dist(q, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]; n = dx * dx + dy * dy
    t = max(0, min(1, ((q[0] - a[0]) * dx + (q[1] - a[1]) * dy) / n)) if n else 0
    return math.dist(q, (a[0] + t * dx, a[1] + t * dy))


def dist(q, pts):
    return min(seg_dist(q, pts[i], pts[i + 1]) for i in range(len(pts) - 1))


def build(panel):
    W, H = SIZE[panel]
    P = json.load(open(f'lines_{panel}.json'))['polylines']
    # cuts where one drawn line carries two trails (CUTS in vl_checked.py): the piece through the point is split there
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
    json.dump({'polylines': P}, open(f'pieces_{panel}.json', 'w'))
    for p in P:
        p['pt'] = [(x * W / 100, y * H / 100) for x, y in p['points']]
    S = {s['i']: s for s in json.load(open(f'syms_{panel}.json'))}
    names = NAMES.get(panel, {})
    assign = collections.defaultdict(set); why = {}
    REACH = {'front-side': 230, 'back-bowls': 360, 'blue-sky': 620}[panel]  # longest label, px
    cands = []  # (score, symbol index, name, piece)
    for i, n in names.items():
        if not n or n == '?':
            continue
        s = S[i]; c, r = s['c'], s['r']; cls = CLS[s['t']]
        for p in P:
            if p['cls'] != cls:
                continue
            pts = p['pt']
            if dist(c, pts) < 0.9 * r and min(math.dist(c, pts[0]), math.dist(c, pts[-1])) > 2.5 * r:
                cands.append((0.0, i, n, p['id']))  # the symbol sits on this piece
                continue
            for k in (0, -1):
                e = pts[k]; d = math.dist(c, e)
                if d > REACH:
                    continue
                other = pts[-1] if k == 0 else pts[0]
                inner = pts[min(3, len(pts) - 1)] if k == 0 else pts[max(-4, -len(pts))]
                v = (inner[0] - e[0], inner[1] - e[1]); lv = math.hypot(*v) or 1
                v = (v[0] / lv, v[1] / lv)
                if d < 1.8 * r + 8:
                    cands.append((d / 4, i, n, p['id']))  # the line starts right at the symbol
                    continue
                u = ((e[0] - c[0]) / d, (e[1] - c[1]) / d)
                align = u[0] * v[0] + u[1] * v[1]  # the line goes on the way the text runs
                downhill = other[1] >= e[1] - 0.3 * abs(other[0] - e[0])  # this end is the piece's top
                if align > 0.75 and downhill:
                    cands.append((d * (2.2 - align), i, n, p['id']))
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
              open(f'assign_{panel}.json', 'w'), indent=0)
    named = {n for v in assign.values() for n in v}
    want = {n for n in names.values() if n and n != '?'}
    print(panel, len(P), 'pieces;', sum(1 for p in P if assign.get(p['id'])), 'named;',
          'several names:', sum(1 for v in assign.values() if len(v) > 1), '; names with no piece:', sorted(want - named))


for panel in sys.argv[1:] or SIZE:
    build(panel)
