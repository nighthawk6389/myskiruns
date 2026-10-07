"""Whiteface: the map's reading, with the crop decisions applied (scratch name: wf_reading.py).

    python3 tools/trailmap/resorts/whiteface/reading.py

Reads $WHITEFACE_WORK/wf_assign.json (build.py), $WHITEFACE_WORK/wf_labels.json and
src/data/resorts/whiteface/linePolylines.json; takes FIX, PRINT_FIX, OVERRIDE and UNNAMED from decisions.py.
Writes:
- $WHITEFACE_WORK/tiles/result_whiteface.json: one reading in the readers' format (labels with their printed
  spelling, symbol, glade flag and position; every named piece at confidence "certain"), the input of
  seed_roster.py and aggregate_readings.py, as if a reader had written it;
- $WHITEFACE_WORK/wf_gaps.json: {stretches: [[name, points]], markers: [names]}. A name not printed along its
  own pieces (fewer than half its characters within 30 px of them) is printed in a gap of its line, or is all
  of its line: it gets a stretch along its own characters (thinned to one point per ~25 px, in map px) that
  stretches.py turns into a review. A glade name with no piece is a marker at its label (aggregate_readings.py
  makes it); so is a name in decisions.py's NO_LINE (label_markers: stretches.py makes it, through
  traces_to_reviews.py --labels).

Difficulty: the name's colour (green circle, blue square, black diamond), double-black where a double diamond
is printed beside a black name.
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from decisions import FIX, NO_LINE, OVERRIDE, PRINT_FIX, UNNAMED  # noqa: E402

REPO = os.path.abspath(os.path.join(HERE, '../../../..'))
WORK = os.path.abspath(os.environ.get('WHITEFACE_WORK', os.path.join(REPO, 'work/whiteface')))

S = 2.2  # image px per PDF pt
A = json.load(open(os.path.join(WORK, 'wf_assign.json')))
P = {p['id']: p for p in json.load(open(os.path.join(REPO, 'src/data/resorts/whiteface/linePolylines.json')))['polylines']}
W, H = 3795, 3156


def norm(n):
    n = n.upper().replace('’', "'")
    return FIX.get(n, n)


sym_rank = {'circle': 0, 'square': 1, 'diamond': 2, 'double-diamond': 3}
CLS_SYM = {'green': 'circle', 'blue': 'square', 'black': 'diamond'}
labels = []
for l in A['labels']:
    n = norm(l['text'])
    # the name's colour is its difficulty; a black name with a double diamond is double-black
    sym = 'double-diamond' if 'double-diamond' in l['syms'] else CLS_SYM[l['cls']]
    labels.append({'mapName': n, 'printed': PRINT_FIX.get(l['text'], l['text']), 'symbol': sym,
                   'glade': 'GLADES' in n, 'area': 'whiteface',
                   'labelSrc': [round(l['c'][0] * S), round(l['c'][1] * S)], 'confidence': 'certain'})

names = {}
for pid, ns in A['assign'].items():
    if len(ns) == 1:
        names[int(pid)] = norm(ns[0])
for pid, n in OVERRIDE.items():
    names[pid] = n
for pid in UNNAMED:
    names.pop(pid, None)
lines = [{'id': pid, 'mapName': n, 'color': P[pid]['cls'], 'confidence': 'certain', 'note': 'PDF label + checked crop'}
         for pid, n in sorted(names.items())]
missing = [pid for pid in P if pid not in names and pid not in UNNAMED]
os.makedirs(os.path.join(WORK, 'tiles'), exist_ok=True)
json.dump({'labels': labels, 'lines': lines}, open(os.path.join(WORK, 'tiles/result_whiteface.json'), 'w'), indent=1)
print(len(labels), 'labels,', len(lines), 'named pieces; unnamed', sorted(UNNAMED), 'still unassigned', missing)

# --- labels printed in a gap of their own line: draw the stretch along the printed name
by_name = {}
for pid, n in names.items():
    by_name.setdefault(n, []).append(pid)


def seg_dist(q, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]; L = dx * dx + dy * dy
    t = max(0, min(1, ((q[0] - a[0]) * dx + (q[1] - a[1]) * dy) / L)) if L else 0
    return math.dist(q, (a[0] + t * dx, a[1] + t * dy))


full = {o['seq']: o for o in json.load(open(os.path.join(WORK, 'wf_labels.json')))}
traces = []
GLADE_MARKERS = []
LABEL_MARKERS = []  # NO_LINE: names with no line, outside a glade
for l in A['labels']:
    n = norm(l['text'])
    pts = [[x * S, y * S] for x, y in l['pts']]
    own = [[(x * W / 100, y * H / 100) for x, y in P[pid]['points']] for pid in by_name.get(n, [])]
    near = sum(1 for q in pts if any(min(seg_dist(q, s[i], s[i + 1]) for i in range(len(s) - 1)) < 30 for s in own))
    if own and near >= 0.5 * len(pts):
        continue  # printed along its own line
    if 'GLADES' in n and not own:
        GLADE_MARKERS.append(n)
        continue
    if n in NO_LINE and not own:
        LABEL_MARKERS.append(n)
        continue
    # thin the char centres to ~every 25 px
    thin = [pts[0]]
    for q in pts[1:]:
        if math.dist(q, thin[-1]) >= 25:
            thin.append(q)
    if math.dist(pts[-1], thin[-1]) > 3:
        thin.append(pts[-1])
    traces.append((n, [[round(x), round(y)] for x, y in thin]))
print('label-gap stretches:', [t[0] for t in traces])
print('glade markers:', GLADE_MARKERS, '; other markers (NO_LINE):', LABEL_MARKERS)
json.dump({'stretches': traces, 'markers': GLADE_MARKERS, 'label_markers': LABEL_MARKERS},
          open(os.path.join(WORK, 'wf_gaps.json'), 'w'), indent=1)
