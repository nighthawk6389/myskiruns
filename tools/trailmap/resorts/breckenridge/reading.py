"""Breckenridge: PDF labels + matched pieces + checked crops -> one reading (seed_roster / aggregate_readings input),
label-gap stretches drawn along the printed names, and markers for names with no drawn line.

    python3 tools/trailmap/resorts/breckenridge/reading.py      # regen.sh runs it (scratch: br_reading.py)

Reads decisions.py (pieces settled on crops, connectors with no printed name), work/names.json (names.py),
work/assign.json (match.py) and the line pieces (src/data/resorts/breckenridge/linePolylines.json). Writes, in
the work folder:
- tiles/result_breck.json: a reading in the readers' format (prompts/0-new-map.md): every label with its symbol
  (or its bowl's, ZONE) at its position in map px, and every named piece; all 'certain'.
- gaps.json: per trail, the stretches along a name printed in a gap of its own line (its line runs into the name
  along the text), and markers (map px) for names with no line of their own. traces.py turns them into reviews.
"""
import collections, json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import PIECES, work  # noqa: E402
from decisions import CHECKED, UNNAMED  # noqa: E402

S, X0, Y0 = 3.0, 0, 80  # image px per PDF pt; the map clip's origin
N = json.load(open(work('names.json')))
A = json.load(open(work('assign.json')))
P = {p['id']: p for p in json.load(open(PIECES))['polylines']}
for p in P.values():
    p['pt'] = [(X0 + x * 14.58, Y0 + y * 8.45) for x, y in p['points']]

PARKS = {'American Terrain Park', 'Eldorado Terrain Park', 'Freeway Terrain Park', 'Toyota Banked Slalom'}
SYM = {'circle': 'circle', 'square': 'square', 'diamond': 'diamond', 'double-diamond': 'double-diamond',
       'ex': 'double-diamond'}
# names printed with no symbol of their own: the symbol of the bowl / zone they are printed in (checked on crops)
ZONE = {
    **{n: ('double-diamond', 'South Col (EX)') for n in ('Sanctuary', 'Respite')},
    **{n: ('double-diamond', 'Six Senses (EX)') for n in ('Epiphany', 'E.S.P', 'Contact', 'Savor', 'Whiff', 'Behold', 'Echo')},
    **{n: ('double-diamond', 'Serenity Bowl (EX)') for n in ('Felicity', 'Rapture', 'Yugen', 'Sublime', 'Irie', 'Chi')},
    **{n: ('double-diamond', 'Snow White (EX)') for n in ('Wacky’s Chute', 'Zoot Chute')},
    **{n: ('double-diamond', 'Lake Chutes (EX) / Imperial Bowl') for n in ('9 Lives', 'Easy Street')},
    'Imperial Ridge': ('double-diamond', 'Imperial Bowl'),
    **{n: ('double-diamond', 'Contest Bowl') for n in ('King', 'Queen', 'Joker', 'Stampede', 'Mule', 'Rustler')},
    **{n: ('double-diamond', 'Horseshoe Bowl') for n in ('Outlaw', 'Brill’s Thrill', 'Eagle’s Nest', 'Lulu', 'Humbug')},
    **{n: ('diamond', 'North Bowl') for n in ('Forget-Me-Not', 'White Crown', 'Ptarmigan', 'Pika')},
    **{n: ('double-diamond', 'Peak 7 bowls') for n in ('Debbie’s Alley', 'Vertigo', 'Y-Chute', 'C.J.’s', 'Magic Carpet',
                                                        'Boundary Chutes', 'Whiskey River')},
    'Alpine Alley': ('diamond', 'its black line (a traverse)'),
}


def norm(n):
    return n.upper().replace('’', "'").replace('‘', "'")


def px(q):
    return [round((q[0] - X0) * S), round((q[1] - Y0) * S)]


labels = []
for o in N['labels']:
    n = o['text']
    sym = SYM[o['syms'][0]] if o['syms'] else (ZONE[n][0] if n in ZONE else None)
    assert sym or n in PARKS or o['cls'] != 'black', n
    labels.append({'mapName': norm(n), 'printed': n.replace('’', "'"), 'symbol': sym, 'glade': False,
                   'park': n in PARKS, 'area': 'breckenridge', 'labelSrc': px(o['c']), 'confidence': 'certain'})

names = {}
for pid, ns in A['assign'].items():
    if len(ns) == 1:
        names[int(pid)] = ns[0]
names.update(CHECKED)
for pid in UNNAMED:
    names.pop(pid, None)
missing = [pid for pid in P if pid not in names and pid not in UNNAMED]
assert not missing, missing
lines = [{'id': pid, 'mapName': norm(n), 'color': P[pid]['cls'], 'confidence': 'certain', 'note': 'PDF label + checked crop'}
         for pid, n in sorted(names.items())]
os.makedirs(work('tiles'), exist_ok=True)
json.dump({'labels': labels, 'lines': lines}, open(work('tiles/result_breck.json'), 'w'), indent=1)
print(len(labels), 'labels,', len({l['mapName'] for l in labels}), 'names,', len(lines), 'named pieces,', len(UNNAMED), 'unnamed')


def seg_dist(q, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]; L = dx * dx + dy * dy
    t = max(0, min(1, ((q[0] - a[0]) * dx + (q[1] - a[1]) * dy) / L)) if L else 0
    return math.dist(q, (a[0] + t * dx, a[1] + t * dy))


def unit(a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]; n = math.hypot(dx, dy) or 1
    return dx / n, dy / n


def resample(pts, n):
    d = [0]
    for a, b in zip(pts, pts[1:]):
        d.append(d[-1] + math.dist(a, b))
    out = []
    for k in range(n):
        t = d[-1] * k / (n - 1)
        i = max(j for j in range(len(d)) if d[j] <= t + 1e-9)
        if i >= len(pts) - 1:
            out.append(pts[-1]); continue
        f = (t - d[i]) / ((d[i + 1] - d[i]) or 1)
        out.append((pts[i][0] + f * (pts[i + 1][0] - pts[i][0]), pts[i][1] + f * (pts[i + 1][1] - pts[i][1])))
    return out


by_name = collections.defaultdict(list)
for pid, n in names.items():
    by_name[n].append(pid)
syms = collections.defaultdict(list)
for s in N['syms']:
    if s.get('label'):
        syms[s['label']].append(s['c'])

stretches, markers, beside = collections.defaultdict(list), {}, []
for o in N['labels']:
    n = o['text']
    own = [P[pid]['pt'] for pid in by_name.get(n, [])]
    if not own:
        markers.setdefault(norm(n), px(o['c']))
        continue
    q = [tuple(c) for c in o['pts']]
    near = sum(1 for c in q if min(min(seg_dist(c, s[i], s[i + 1]) for i in range(len(s) - 1)) for s in own) < 9)
    if near >= 0.5 * len(q):
        continue  # printed along its own line
    if len(o['lines']) == 2:  # two lines side by side: their midline
        k = max(len(o['lines'][0]), len(o['lines'][1]))
        a, b = resample([tuple(c) for c in o['lines'][0]], k), resample([tuple(c) for c in o['lines'][1]], k)
        q = [((x0 + x1) / 2, (y0 + y1) / 2) for (x0, y0), (x1, y1) in zip(a, b)]
    head = [c for c in syms.get(n, []) if math.dist(c, q[0]) < 14]
    tail = [c for c in syms.get(n, []) if math.dist(c, q[-1]) < 14 and not head]
    pts = head[:1] + q + tail[:1]
    ok = False  # a stretch only where a line of its own runs into the name along the text
    for end, inner in ((pts[0], pts[min(3, len(pts) - 1)]), (pts[-1], pts[max(-4, -len(pts))])):
        into = unit(end, inner)
        for s in own:
            for k in (0, -1):
                e = s[k]
                if math.dist(e, end) > 18:
                    continue
                out = unit(s[min(3, len(s) - 1)] if k == 0 else s[max(-4, -len(s))], e)
                if out[0] * into[0] + out[1] * into[1] > 0.85:
                    ok = True
    if not ok:
        beside.append(n)
        continue
    thin = [pts[0]]
    for c in pts[1:]:
        if math.dist(c, thin[-1]) >= 8:
            thin.append(c)
    if math.dist(pts[-1], thin[-1]) > 1:
        thin.append(pts[-1])
    stretches[norm(n)].append([px(c) for c in thin])
print('label-gap stretches:', sum(len(v) for v in stretches.values()), 'on', len(stretches), 'trails')
print('labels printed beside (not in) their own line (no stretch):', beside)
print('markers (no drawn line):', len(markers), sorted(markers))
json.dump({'stretches': stretches, 'markers': markers}, open(work('gaps.json'), 'w'), indent=1)
