"""Winter Park: PDF labels + checked piece names -> one reading (seed_roster / aggregate_readings input), and
traces: label-gap stretches drawn along the printed name (the map prints most names in a gap of their line or
at its end), plus markers for names with no drawn line. Was the scratch wp_reading.py.

    python3 tools/trailmap/resorts/winter-park/reading.py      # regen.sh runs it, from the repo root

Reads decisions.py (CHECKED, UNNAMED), src/data/resorts/winter-park/linePolylines.json and, in $WINTER_PARK_WORK
(default work/winter-park), wp_names.json (names.py) and wp_labels.json (pdf_labels.py: the Cirque key's numbers).
Writes there tiles/result_winterpark.json ({labels, lines}: one label per printed name, with its display spelling,
symbol and position in image px, and every checked piece's name; the Cirque key's nine runs at their numbered
squares; parks, glades and the Cirque's unsymbolled names flagged) and wp_gaps.json ({stretches: name -> [points
along the printed name, image px], markers: name -> point}). A stretch is made where a name is not printed along
its own line but in a gap of it or at its end (a piece of its own ends within 18 pt of the text, pointing along
it); a name with no piece is a marker. traces.py turns wp_gaps.json into traces_to_reviews.py's input.
"""
import collections, json, math, os, re, sys

S, X0, Y0 = 3.2, 40, 165  # image px per PDF pt; the map clip's origin
WORK = os.environ.get('WINTER_PARK_WORK', 'work/winter-park')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from decisions import CHECKED, UNNAMED  # noqa: E402,F401 (was exec(open('wp_checked.py').read()))
N = json.load(open(os.path.join(WORK, 'wp_names.json')))
TXT = json.load(open(os.path.join(WORK, 'wp_labels.json')))
P = {p['id']: p for p in json.load(open('src/data/resorts/winter-park/linePolylines.json'))['polylines']}
W, H = 4224, 3152
for p in P.values():
    p['pt'] = [(X0 + x * 13.2, Y0 + y * 9.85) for x, y in p['points']]

SKIP = {'TO VILLAGE WAY': 'a pointer to Village Way', 'RACE PLACE RECREATIONAL RACING': 'the race venue',
        **{c: 'one of the Alphabet Chutes (printed under ALPHABET CHUTES)' for c in ('A', 'B', 'C', 'D', 'E', 'F', 'G1', 'G2')}}
PARKS = {'STARTER PARK', 'RE-RAILER', 'HALFPIPE', 'RAIL YARD', 'LOWER RAIL YARD', 'GANGWAY', 'BOUNCER', 'ASH CAT', 'AMBUSH'}
CIRQUE_NO_SYMBOL = {'G-FACE', 'GO-JOE', 'JR SOUTH', 'JR NORTH'}  # the Cirque key rates all Cirque terrain EX
EXTRA_SYM = {'MOCK TURTLE': 'circle'}  # its circle sits off the text line (crop checked)
SYM = {'circle': 'circle', 'square': 'square', 'blue-black': 'diamond', 'diamond': 'diamond', 'ex': 'double-diamond'}
SMALL = {'AND', 'OF', 'THE', 'IN', 'N'}
KEEP = {'JR', 'MRC', 'HCR'}


def norm(n):
    return n.upper().replace('’', "'").replace('‘', "'")


def display(n):
    words = []
    for i, w in enumerate(n.replace('’', "'").replace('‘', "'").split(' ')):
        parts = []
        for j, part in enumerate(w.split('-')):
            core = part.strip("'")
            if core in KEEP:
                parts.append(part)
            elif (i or j) and core in SMALL:
                parts.append(part.lower())
            else:
                parts.append(part[:1] + part[1:].lower())
        words.append('-'.join(parts))
    return ' '.join(words)


def px(q):
    return [round((q[0] - X0) * S), round((q[1] - Y0) * S)]


labels = []
for o in N['labels']:
    n = o['text']
    if n in SKIP:
        continue
    sym = SYM[o['syms'][0]] if o['syms'] else EXTRA_SYM.get(n) or ('double-diamond' if n in CIRQUE_NO_SYMBOL else None)
    labels.append({'mapName': norm(n), 'printed': display(n), 'symbol': sym, 'glade': 'GLADE' in n,
                   'park': n in PARKS, 'area': 'winter-park', 'labelSrc': px(o['c']), 'confidence': 'certain'})
# the Cirque key: numbered runs 1-9 printed as yellow squares, names in the key box, all EX
KEY = {'1': 'SOUTH HEADWALL', '2': 'CORNICE CANYON', '3': 'PLAYING FIELDS', '4': 'WEST HEADWALL', '5': 'THE COWBOYS',
       '6': 'SLIM PICKINS', '7': 'HARD CORE RESISTOR', '8': 'SHENKO’S CHUTE', '9': 'HEART OF DARKNESS'}
squares = {o['text']: o['c'] for o in TXT if o['font'] == 'Montserrat-ExtraBold' and o['size'] == 8.5 and o['text'] in KEY}
assert len(squares) == 9, squares
for k, n in KEY.items():
    labels.append({'mapName': norm(n), 'printed': display(n), 'symbol': 'double-diamond', 'glade': False, 'park': False,
                   'area': 'winter-park', 'labelSrc': px(squares[k]), 'confidence': 'certain'})

lines = [{'id': pid, 'mapName': norm(n), 'color': P[pid]['cls'], 'confidence': 'certain',
          'note': 'PDF label + checked crop'} for pid, n in sorted(CHECKED.items())]
json.dump({'labels': labels, 'lines': lines}, open(os.path.join(WORK, 'tiles/result_winterpark.json'), 'w'), indent=1)
print(len(labels), 'labels,', len({l['mapName'] for l in labels}), 'names,', len(lines), 'named pieces')


def seg_dist(q, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]; L = dx * dx + dy * dy
    t = max(0, min(1, ((q[0] - a[0]) * dx + (q[1] - a[1]) * dy) / L)) if L else 0
    return math.dist(q, (a[0] + t * dx, a[1] + t * dy))


by_name = collections.defaultdict(list)
for pid, n in CHECKED.items():
    by_name[n].append(pid)
syms = collections.defaultdict(list)
for s in N['syms']:
    if s.get('label'):
        syms[s['label']].append(s['c'])
syms['MOCK TURTLE'].append((1021.9, 900.6))

def lines_of(q):
    """A name set on two lines (or one object holding both) reads along line 1, then jumps back: split it."""
    if len(q) < 4:
        return [q]
    u = (q[-1][0] - q[0][0], q[-1][1] - q[0][1])
    for i in range(1, len(q) - 1):
        a, b = q[i], q[i + 1]
        if (b[0] - a[0]) * (q[1][0] - q[0][0]) + (b[1] - a[1]) * (q[1][1] - q[0][1]) < 0:
            return [q[:i + 1], q[i + 1:]]
    return [q]


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


def unit(a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]; n = math.hypot(dx, dy) or 1
    return dx / n, dy / n


stretches, markers, far = collections.defaultdict(list), {}, []
for o in N['labels']:
    n = o['text']
    if n in SKIP:
        continue
    own = [P[pid]['pt'] for pid in by_name.get(n, [])]
    q = [tuple(c) for c in o['pts']]
    if not own:
        markers.setdefault(norm(n), px(o['c']))
        continue
    near = sum(1 for c in q if min(min(seg_dist(c, s[i], s[i + 1]) for i in range(len(s) - 1)) for s in own) < 9)
    if near >= 0.5 * len(q):
        continue  # printed along its own line
    parts = lines_of(q)
    if len(parts) == 2:  # two lines side by side: their midline
        k = max(len(parts[0]), len(parts[1]))
        a, b = resample(parts[0], k), resample(parts[1], k)
        q = [((x0 + x1) / 2, (y0 + y1) / 2) for (x0, y0), (x1, y1) in zip(a, b)]
    head = [c for c in syms.get(n, []) if math.dist(c, q[0]) < 14]
    tail = [c for c in syms.get(n, []) if math.dist(c, q[-1]) < 14 and not head]
    pts = head[:1] + q + tail[:1]
    # a stretch only where a line of its own runs into the name along the text (in a gap, or at its end)
    ok = False
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
        far.append(n)
        continue
    thin = [pts[0]]
    for c in pts[1:]:
        if math.dist(c, thin[-1]) >= 8:
            thin.append(c)
    if math.dist(pts[-1], thin[-1]) > 1:
        thin.append(pts[-1])
    stretches[norm(n)].append([px(c) for c in thin])
print('label-gap stretches:', sum(len(v) for v in stretches.values()), 'on', len(stretches), 'trails')
print('labels not running on from their own line (no stretch):', far)
print('markers (no drawn line):', sorted(markers))
for k, n in KEY.items():
    markers[norm(n)] = px(squares[k])
json.dump({'stretches': stretches, 'markers': markers}, open(os.path.join(WORK, 'wp_gaps.json'), 'w'), indent=1)
