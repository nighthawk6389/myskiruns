"""Winter Park: each label -> the line pieces it is printed along (or in a gap of), then names spread along
unlabelled continuation pieces. Writes wp_assign.json for checking on crops. Was the scratch wp_build.py.

    python3 tools/trailmap/resorts/winter-park/automatch.py      # regen.sh runs it, from the repo root

Reads src/data/resorts/winter-park/linePolylines.json and $WINTER_PARK_WORK/wp_names.json (names.py); writes
$WINTER_PARK_WORK/wp_assign.json ({labels, assign: piece id -> [names], why}). A label names a piece it is printed
along (median glyph within 7 pt, 60% within 9 pt), the piece ending at its symbol, or the piece running on from
the far end of its text; pieces of the label's own colour win (its symbol's: advanced-intermediate and EX trails
are black lines). Then a name spreads to a piece whose end meets exactly one named piece of the same colour.
This was the first pass only: every piece's name was then settled on crops (checks/zoom.py tags each piece with
this auto-name) into decisions.py, which is what reading.py uses; the committed data do not depend on this file.
"""
import collections, json, math, os
WORK = os.environ.get('WINTER_PARK_WORK', 'work/winter-park')
X0, Y0, CW, CH = 40, 165, 1320, 985  # the --clip the pieces were extracted with
N = json.load(open(os.path.join(WORK, 'wp_names.json')))
SKIPNAMES = set(N['not_trails'])
CLS = {'circle': 'green', 'square': 'blue', 'blue-black': 'black', 'diamond': 'black', 'ex': 'black'}
labs = [o for o in N['labels'] if o['text'] not in SKIPNAMES]
P = json.load(open('src/data/resorts/winter-park/linePolylines.json'))['polylines']
for p in P:
    p['pt'] = [(X0 + x * CW / 100, Y0 + y * CH / 100) for x, y in p['points']]


def seg_dist(q, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]; n = dx * dx + dy * dy
    t = max(0, min(1, ((q[0] - a[0]) * dx + (q[1] - a[1]) * dy) / n)) if n else 0
    return math.dist(q, (a[0] + t * dx, a[1] + t * dy))


def dist(q, pts):
    return min(seg_dist(q, pts[i], pts[i + 1]) for i in range(len(pts) - 1))


def unit(a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]; n = math.hypot(dx, dy) or 1
    return dx / n, dy / n


def end_dir(pts, k):
    if k == 0:
        return unit(pts[min(2, len(pts) - 1)], pts[0])
    return unit(pts[max(-3, -len(pts))], pts[-1])


assign = collections.defaultdict(set); why = {}
SYMS = [x for x in N['syms'] if x.get('label')]
for o in labs:
    name, q = o['text'], o['pts']
    o['line'] = CLS[o['syms'][0]] if o['syms'] else o['cls']
    mine = [x['c'] for x in SYMS if x['label'] == name and min(math.dist(x['c'], q[0]), math.dist(x['c'], q[-1])) < 30]
    cand = {}
    for p in P:
        ds = [dist(c, p['pt']) for c in q]
        if sorted(ds)[len(ds) // 2] < 7 and sum(d < 9 for d in ds) / len(ds) >= 0.6:
            cand[p['id']] = 'along'  # printed beside this line
    # the line ends at the name's symbol (this map puts the symbol where the line meets the label)
    for s in mine:
        best = min(((math.dist(s, p['pt'][k]), p['id']) for p in P for k in (0, -1)), default=None)
        if best and best[0] < 9:
            cand.setdefault(best[1], 'symbol')
    # ... or at the far end of the text, running on from it
    if len(q) >= 2:
        for first, second in ((q[0], q[1]), (q[-1], q[-2])):
            if any(math.dist(s, first) < 14 for s in mine):
                continue  # that end has the symbol
            text_out = unit(second, first)
            best = None
            for p in P:
                for k in (0, -1):
                    e = p['pt'][k]; d = math.dist(e, first)
                    if d > 14:
                        continue
                    into = end_dir(p['pt'], k)
                    if -(into[0] * text_out[0] + into[1] * text_out[1]) > 0.5 and (best is None or d < best[0]):
                        best = (d, p['id'])
            if best:
                cand.setdefault(best[1], 'text end')
    same = {c: w for c, w in cand.items() if P[c]['cls'] == o['line']}
    o['pieces'] = sorted(same or cand)
    o['how'] = {str(c): w for c, w in (same or cand).items()}
    for pid in o['pieces']:
        assign[pid].add(name); why[pid] = 'label'

ends = [(p['pt'][k], p['id']) for p in P for k in (0, -1)]


def neighbours(pid):
    p = P[pid]; out = []
    for k in (0, -1):
        e = p['pt'][k]
        at = {i for f, i in ends if i != pid and math.dist(f, e) < 3}
        mid = [q['id'] for q in P if q['id'] != pid and q['id'] not in at and dist(e, q['pt']) < 2]
        if len(at) == 1 and not mid:
            out.append(next(iter(at)))
    return out


changed = True
while changed:
    changed = False
    for p in P:
        if assign.get(p['id']):
            continue
        names = set()
        for n in neighbours(p['id']):
            if P[n]['cls'] == p['cls'] and len(assign.get(n, ())) == 1 and p['id'] in neighbours(n):
                names |= assign[n]
        if len(names) == 1:
            assign[p['id']] = set(names); why[p['id']] = 'continuation'; changed = True

json.dump({'labels': labs, 'assign': {str(k): sorted(v) for k, v in assign.items()}, 'why': {str(k): v for k, v in why.items()}},
          open(os.path.join(WORK, 'wp_assign.json'), 'w'), indent=1)
print(len(labs), 'labels')
print('labels with no piece:', [o['text'] for o in labs if not o['pieces']])
print('pieces with 2+ names:', {k: sorted(v) for k, v in assign.items() if len(v) > 1})
print('pieces unassigned:', [p['id'] for p in P if not assign.get(p['id'])])
print('colour mismatch:', [(o['text'], o['line'], [P[i]['cls'] for i in o['pieces']]) for o in labs if any(P[i]['cls'] != o['line'] for i in o['pieces'])])
