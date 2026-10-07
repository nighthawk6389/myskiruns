"""Whiteface: match every printed name to its line pieces (scratch name: wf_build.py).

    python3 tools/trailmap/resorts/whiteface/build.py

Reads $WHITEFACE_WORK/whiteface.pdf (the symbols), $WHITEFACE_WORK/wf_labels.json (labels.py) and
src/data/resorts/whiteface/linePolylines.json (the pieces, after regen.sh's cuts). Writes
$WHITEFACE_WORK/wf_assign.json: {labels: [{text, cls, syms, pieces, c, size, pts}], assign: {piece id: [names]},
why: {piece id: 'label' | 'continuation'}}, and prints what is left to settle on crops (labels with no piece,
pieces with two names or none, symbol/colour mismatches). reading.py applies the crop decisions on top.

How the map prints things, and so the rules:
- Labels: the text objects in the trail colours on the three name layers; the colour is the difficulty.
  Fragments are merged into their names: a second line ("Glades", "Cut", "Dot", "Bridge", "Loop") joins the
  nearest label of its colour, and "Switchbacks", printed once between its two parts, goes onto "Upper" and
  "Lower".
- Symbols: fills on the name layers, beside each name: green circle (four curves), blue square, black diamond
  (four lines), double diamond (eight lines). Each goes to the nearest label end of its colour (25 pt at most).
- A name printed beside a piece (median character within 7 pt, 60% of them within 9 pt) names it. Failing
  that, a name printed in a gap of its own line (most names on this map) names the pieces that end at either
  end of the text (12 pt at most) and run away from it along the text's direction. Pieces of the name's colour
  win over the others.
- Names then spread along unlabelled continuations: an unnamed piece whose end meets exactly one other piece
  of its colour, end to end and both ways (no T-junction), takes that piece's single name, until nothing
  changes.
"""
import collections
import json
import math
import os

import pymupdf

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../..'))
WORK = os.path.abspath(os.environ.get('WHITEFACE_WORK', os.path.join(REPO, 'work/whiteface')))

S = 2.2
page = pymupdf.open(os.path.join(WORK, 'whiteface.pdf'))[0]
L = json.load(open(os.path.join(WORK, 'wf_labels.json')))
FILL = {(0.0, 0.46, 0.74): 'blue', (0.14, 0.12, 0.13): 'black', (0.0, 0.52, 0.27): 'green'}
labs = [dict(o, cls=FILL[tuple(o['color'])]) for o in L
        if tuple(o['color']) in FILL and o['layer'] in ('Blue Names', 'Black Names', 'Green Names')]

# --- merge label fragments (two-line names and names split along a curve)
TAILS = {'Glades', 'Cut', 'Dot', 'Bridge', 'Loop'}
used = set()
for i, o in enumerate(labs):
    if o['text'] not in TAILS:
        continue
    cands = sorted((math.dist(o['c'], p['c']), j) for j, p in enumerate(labs)
                   if j != i and p['cls'] == o['cls'] and p['text'] not in TAILS and p['text'] not in ('Upper', 'Lower', 'Switchbacks'))
    d, j = cands[0]
    assert d < 30, (o['text'], d)
    head = labs[j]
    head['text'] = head['text'] + ' ' + o['text']
    head['pts'] = head['pts'] + o['pts']
    used.add(i)
for o in labs:  # "Switchbacks" printed once between its Upper and Lower parts
    if o['text'] in ('Upper', 'Lower'):
        o['text'] += ' Switchbacks'
labs = [o for i, o in enumerate(labs) if i not in used and o['text'] != 'Switchbacks']
for o in labs:
    o['text'] = o['text'].replace('’', "'")

# --- difficulty symbols from the name layers
syms = []
for d in page.get_drawings():
    if not (d.get('layer') or '').endswith('Names') or d['type'] not in ('f', 'fs') or not d.get('fill'):
        continue
    f = tuple(round(v, 2) for v in d['fill']); k = [it[0] for it in d['items']]; r = d['rect']
    c = ((r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2)
    t = None
    if f == (0.0, 0.52, 0.27) and k == ['c'] * 4: t = 'circle'
    elif f == (0.0, 0.46, 0.74) and k == ['l'] * 4: t = 'square'
    elif f == (0.14, 0.12, 0.13) and k == ['l'] * 4: t = 'diamond'
    elif f == (0.14, 0.12, 0.13) and k == ['l'] * 8: t = 'double-diamond'
    if t and not any(s['t'] == t and math.dist(s['c'], c) < 1 for s in syms):
        syms.append({'t': t, 'c': c})
SYMCLS = {'circle': 'green', 'square': 'blue', 'diamond': 'black', 'double-diamond': 'black'}
for o in labs:
    o['syms'] = []
for s in syms:  # each symbol belongs to the nearest label end of its colour
    best = min(((min(math.dist(s['c'], o['pts'][0]), math.dist(s['c'], o['pts'][-1])), k) for k, o in enumerate(labs)
                if o['cls'] == SYMCLS[s['t']]), default=None)
    if best and best[0] < 25:
        labs[best[1]]['syms'].append(s['t'])
    else:
        print('symbol with no label nearby:', s['t'], [round(v * S) for v in s['c']], best and round(best[0]))

# --- pieces (percent -> PDF pt)
W, H = 1724.88, 1434.24
P = json.load(open(os.path.join(REPO, 'src/data/resorts/whiteface/linePolylines.json')))['polylines']
for p in P:
    p['pt'] = [(x * W / 100, y * H / 100) for x, y in p['points']]


def seg_dist(q, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]; n = dx * dx + dy * dy
    t = max(0, min(1, ((q[0] - a[0]) * dx + (q[1] - a[1]) * dy) / n)) if n else 0
    return math.dist(q, (a[0] + t * dx, a[1] + t * dy))


def dist(q, pts):
    return min(seg_dist(q, pts[i], pts[i + 1]) for i in range(len(pts) - 1))


assign = collections.defaultdict(set)  # piece id -> names
why = {}


def unit(a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]; n = math.hypot(dx, dy) or 1
    return dx / n, dy / n


def end_dir(pts, k):  # outward direction of a piece at end k (0 or -1)
    if k == 0:
        return unit(pts[min(2, len(pts) - 1)], pts[0])
    return unit(pts[max(-3, -len(pts))], pts[-1])


for o in labs:
    name, q = o['text'], o['pts']
    cand = set()
    for p in P:
        ds = [dist(c, p['pt']) for c in q]
        close = sum(d < 9 for d in ds) / len(ds)
        if sorted(ds)[len(ds) // 2] < 7 and close >= 0.6:
            cand.add(p['id'])  # the name is printed beside this line
    if not cand and len(q) >= 2:
        # printed in a gap of its line: a piece ends at each end of the text, pointing along it
        for first, second in ((q[0], q[1]), (q[-1], q[-2])):
            text_out = unit(second, first)  # from the text out past its end
            best = None
            for p in P:
                for k in (0, -1):
                    e = p['pt'][k]
                    d = math.dist(e, first)
                    if d > 12:
                        continue
                    into = end_dir(p['pt'], k)  # points out of the piece at this end
                    align = -(into[0] * text_out[0] + into[1] * text_out[1])  # piece runs away from the text
                    if align > 0.6 and (best is None or d < best[0]):
                        best = (d, p['id'])
            if best:
                cand.add(best[1])
    same = {c for c in cand if next(p for p in P if p['id'] == c)['cls'] == o['cls']}
    o['pieces'] = sorted(same or cand)
    for pid in o['pieces']:
        assign[pid].add(name)
        why[pid] = 'label'

# --- spread along continuation: endpoints shared by exactly two pieces of one colour
ends = []
for p in P:
    for k in (0, -1):
        ends.append((p['pt'][k], p['id']))
def neighbours(pid):
    p = next(q for q in P if q['id'] == pid)
    out = []
    for k in (0, -1):
        e = p['pt'][k]
        at = {i for f, i in ends if i != pid and math.dist(f, e) < 3}
        # a T-junction: this end touches another piece's middle
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
            q = next(x for x in P if x['id'] == n)
            if q['cls'] == p['cls'] and len(assign.get(n, ())) == 1 and p['id'] in neighbours(n):
                names |= assign[n]
        if len(names) == 1:
            assign[p['id']] = set(names); why[p['id']] = 'continuation'; changed = True

json.dump({'labels': [{k: o[k] for k in ('text', 'cls', 'syms', 'pieces', 'c', 'size', 'pts')} for o in labs],
           'assign': {str(k): sorted(v) for k, v in assign.items()}, 'why': {str(k): v for k, v in why.items()}},
          open(os.path.join(WORK, 'wf_assign.json'), 'w'), indent=1)
print(len(labs), 'labels,', len({o["text"] for o in labs}), 'names;', len(syms), 'symbols', collections.Counter(s['t'] for s in syms))
print('labels with no piece:', [o['text'] for o in labs if not o['pieces']])
print('pieces with 2+ names:', {k: sorted(v) for k, v in assign.items() if len(v) > 1})
print('pieces unassigned:', [p['id'] for p in P if not assign.get(p['id'])])
mism = [(o['text'], o['cls'], o['syms']) for o in labs if o['syms'] and any(SYMCLS[s] != o['cls'] for s in o['syms'])]
print('symbol/colour mismatches:', mism)
print('no symbol:', [o['text'] for o in labs if not o['syms']])
print('double:', [o['text'] for o in labs if 'double-diamond' in o['syms']])
