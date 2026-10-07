"""Copper Mountain: decoded labels + matched pieces + checked crops -> one reading (seed_roster / aggregate_readings
input), label-gap stretches drawn along the printed names, and markers for names with no drawn line.

    python3 tools/trailmap/resorts/copper-mountain/reading.py     # regen.sh runs it (was cu_reading.py)

Reads names.json (names.py), assign.json (build.py), decisions.py here (CHECKED: the pieces settled on crops,
which override the automatic match; UNNAMED: links the map prints no name for) and linePolylines.json. Writes, in
the working folder, tiles/result_copper.json (the reading: every label with its symbol, glade/park flags and
position in map-image px, and every named piece) and gaps.json (was cu_gaps.json: {stretches: name -> polylines
along the printed name, markers: name -> label position}).
- Difficulty: the symbol printed with the name (EX counts as double diamond); names with no symbol take ZONE's
  (Buffalo Stampede: Tucker Mountain's EX; Log Chute: green), the parks none (seed_roster's default, blue), the
  rest the colour they are printed in (BY_COLOUR). Display names: title case, small words lower case (display()).
- Every piece must end up named or in UNNAMED (an assert): automatic single-name matches, then CHECKED on top.
- A name with no piece of its own gets a marker at its (first) label. A label printed along its own line (half its
  glyphs within 9 pt of it) needs nothing more. One printed in a gap of its own line or at its end (a line of its
  own runs into the text along it, within 18 pt) gets a stretch along its characters (two-line names: their
  midline), from its symbol if that sits at an end; one printed beside its line gets none.
"""
import collections, json, math
import os
from common import DATA, HERE, work

S, X0, Y0 = 3.0, 0, 150  # image px per PDF pt; the map clip's origin
exec(open(os.path.join(HERE, 'decisions.py')).read())
N = json.load(open(work('names.json')))
A = json.load(open(work('assign.json')))
P = {p['id']: p for p in json.load(open(os.path.join(DATA, 'linePolylines.json')))['polylines']}
for p in P.values():
    p['pt'] = [(X0 + x * 13.0344, Y0 + y * 9.0254) for x, y in p['points']]

PARKS = {'CENTRAL PARK', 'PEACE PARK', 'PIPE DREAM', 'SUPERPIPE', 'RED’S BACKYARD', 'KOKO’S PROGRESSION PARK',
         'MINER’S PROGRESSION PARK', 'GREEN ACRES PROGRESSION PARK', 'FAMILY CROSS ADVENTURE ZONE'}
SYM = {'circle': 'circle', 'square': 'square', 'diamond': 'diamond', 'double-diamond': 'double-diamond',
       'ex': 'double-diamond'}
# names printed with no symbol of their own (checked on crops)
ZONE = {
    'BUFFALO STAMPEDE': ('double-diamond', 'Tucker Mountain (the Three Bears lift): every other run there is EX; the lone diamond at its foot ends the LILLIE-G TRAVERSE label'),
    'LOG CHUTE': ('circle', 'a kids zone drawn in green'),
}
BY_COLOUR = {'green': 'circle', 'blue': 'square', 'black': 'diamond'}  # else the colour it is printed in
SMALL = {'AND', 'OF', 'THE', 'IN'}
KEEP = {'CDL’S': 'CDL’s', 'EZ': 'EZ'}


def display(n):
    words = []
    for i, w in enumerate(n.split(' ')):
        if w in KEEP:
            words.append(KEEP[w]); continue
        parts = []
        for part in w.split('-'):
            parts.append(part.lower() if i and part in SMALL else part[:1] + part[1:].lower())
        words.append('-'.join(parts))
    return ' '.join(words).replace('’', "'")


def norm(n):
    return n.upper().replace('’', "'").replace('‘', "'")


def px(q):
    return [round((q[0] - X0) * S), round((q[1] - Y0) * S)]


labels = []
for o in N['labels']:
    n = o['text']
    sym = (SYM[o['syms'][0]] if o['syms'] else ZONE[n][0] if n in ZONE else None if n in PARKS
           else BY_COLOUR[o['cls']])
    labels.append({'mapName': norm(n), 'printed': display(n), 'symbol': sym, 'glade': 'GLADE' in n,
                   'park': n in PARKS, 'area': 'copper-mountain', 'labelSrc': px(o['c']), 'confidence': 'certain'})

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
json.dump({'labels': labels, 'lines': lines}, open(work('tiles/result_copper.json'), 'w'), indent=1)
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
