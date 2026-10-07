"""Breckenridge: trail-name labels from the PDF text (pdf_labels.py output), cleaned: per-letter copies,
merged multi-name objects and repeated copies dropped; names set on two lines joined; each symbol attached
to the name it sits beside (before the first character, after the last, or under a two-line name).

    python3 tools/trailmap/resorts/breckenridge/names.py      # regen.sh runs it (scratch: br_names.py)

Reads work/printed.json (tools/trailmap/pdf_labels.py on the PDF: every text object, with its characters'
centres) and work/symbols.json (symbols.py). Writes work/names.json: {labels: [{text, cls, size, pts, lines, c,
seq, syms}], syms: [symbol + the label it belongs to]}, in PDF points. The trail names are the AvenirNextCondensed-
Demi text in the four trail colours (orange = the terrain parks); the PDF holds several copies of most names
(curved labels also as one object per letter, objects holding several names, two-line names both split and
joined), so one copy per position is kept, the last drawn (it is the one that shows).
"""
import collections, json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import work  # noqa: E402
L = json.load(open(work('printed.json')))
for o in L:  # ligatures as plain letters
    o['text'] = o['text'].replace('ﬁ', 'fi').replace('ﬂ', 'fl')
S = json.load(open(work('symbols.json')))
COL = {(0.0, 0.0, 0.0): 'black', (0.01, 0.28, 0.82): 'blue', (0.02, 0.53, 0.02): 'green', (0.96, 0.51, 0.12): 'orange'}
NOT_TRAILS = {'Hike-To', 'Terrain', 'Terrain Only', 'Easiest Way to Peak 9', 'No Lift Access', 'GoldRunner Coaster',
              'Breck Free Ride Bus', 'BRECKENRIDGE STATION', 'Summit Stage Bus', 'Breckenridge Ski Resort Transit'}


PANELS = [(1326, 395, 1458, 925), (1222, 525, 1326, 573), (1094, 573, 1326, 925), (964, 685, 1086, 915),
          (8, 735, 168, 925)]  # legend, terrain parks, lift stats, Epic box, emergency box


def inmap(c):
    x, y = c
    return 160 < y < 930 and not any(b[0] <= x <= b[2] and b[1] <= y <= b[3] for b in PANELS)


atoms = []
for o in sorted(L, key=lambda o: (-len(o['text']), -o['seq'])):  # of copies at one spot, the last drawn shows
    if not (o['font'].startswith('AvenirNextCondensed-Demi') and tuple(o['color']) in COL and 4.9 <= o['size'] <= 7.0):
        continue
    if not inmap(o['c']) or len(o['text']) < 2 or o['text'] in NOT_TRAILS:
        continue
    if any(q['text'] == o['text'] and math.dist(q['c'], o['c']) < 2 for q in atoms):
        continue  # a repeated copy
    atoms.append(dict(o, cls=COL[tuple(o['color'])]))


def covered_by(x, others):
    """x's characters all coincide with characters of other (shorter) labels."""
    return all(any(math.dist(q, r) < 0.8 for o in others for r in o['pts']) for q in x['pts'])


# two-line names: printed as two stacked lines (the PDF usually also holds the joined copy)
JOIN = ['Twin Chutes', 'The Back 9', 'Needle’s Eye', 'Snow White', 'Contest Bowl', 'Lake Chutes', 'George’s Thumb',
        'Cucumber Bowl', 'North Bowl', 'Whale’s Tail', 'Peak 7 Bowl', 'Art’s Bowl', 'The Dunes', 'Ore Bucket', 'South Col',
        'Lost Cabin', 'Six Senses', 'Serenity Bowl', 'Elysian Fields', 'Beyond Bowl', 'Pat’s Wonderland', 'Imperial Bowl',
        'Horseshoe Bowl', 'Lower Boneyard', 'Goodbye Girl', 'Southern Cross', 'The Burn', 'Ripperoo’s Forest',
        'American Terrain Park', 'Eldorado Terrain Park', 'Toyota Banked Slalom']
labs = []
joined = {}
for name in JOIN:
    for split in range(1, len(name.split())):
        a, b = ' '.join(name.split()[:split]), ' '.join(name.split()[split:])
        pairs = [(math.dist(x['c'], y['c']), x, y) for x in atoms if x['text'] == a for y in atoms if y['text'] == b
                 and y['cls'] == x['cls'] and x is not y]
        if pairs:
            d, x, y = min(pairs, key=lambda t: t[0])
            assert d < 14, (name, d)
            joined[name] = (x, y)
            break
    assert name in joined, name
used = set()
for name, (x, y) in joined.items():
    used |= {id(x), id(y)}
    pts = x['pts'] + y['pts']
    labs.append({'text': name, 'cls': x['cls'], 'size': x['size'], 'pts': pts, 'lines': [x['pts'], y['pts']],
                 'c': [round(sum(q[0] for q in pts) / len(pts), 1), round(sum(q[1] for q in pts) / len(pts), 1)], 'seq': x['seq']})
singles = [o for o in atoms if id(o) not in used and o['text'] not in joined]
# every trail-font text, notes included, for spotting merged objects
allfont = [o for o in L if o['font'].startswith('AvenirNextCondensed-Demi') and tuple(o['color']) in COL and len(o['text']) >= 2]
# merged objects: drop any label whose characters are all characters of other, shorter labels
keep = []
for o in singles:
    others = [q for q in singles + labs + allfont if q is not o and len(q['text']) < len(o['text'])]
    if covered_by(o, others):
        continue
    keep.append(o)
for o in keep:
    labs.append({'text': o['text'], 'cls': o['cls'], 'size': o['size'], 'pts': o['pts'], 'lines': [o['pts']], 'c': o['c'], 'seq': o['seq']})


def gap_to(o, q):
    """How far symbol centre q sits before a line's first char or after its last, along that line (None if off it);
    a two-line name's symbol may also sit under its last line."""
    best = None
    for pts in o['lines']:
        if len(pts) < 2:
            continue
        a, b = pts[0], pts[-1]
        Ln = math.dist(a, b); u = ((b[0] - a[0]) / Ln, (b[1] - a[1]) / Ln)
        v = (q[0] - a[0], q[1] - a[1]); along = v[0] * u[0] + v[1] * u[1]; perp = abs(v[0] * u[1] - v[1] * u[0])
        g = None
        if perp < 4.5 and -12 < along < 0: g = -along
        elif perp < 4.5 and Ln < along < Ln + 12: g = along - Ln
        elif 3 < (v[0] * u[1] - v[1] * u[0]) * -1 < 11 and -3 < along < Ln + 3 and pts is o['lines'][-1]:
            g = 6  # under the name (bowls: the symbol on its own line below)
        if g is not None and (best is None or g < best):
            best = g
    return best


for o in labs:
    o['syms'] = []
for s in S:
    cands = sorted((g, k) for k, o in enumerate(labs) if (g := gap_to(o, s['c'])) is not None)
    if cands:
        labs[cands[0][1]]['syms'].append(s['t']); s['label'] = labs[cands[0][1]]['text']
    else:
        s['label'] = None
json.dump({'labels': labs, 'syms': S}, open(work('names.json'), 'w'), indent=0)
print(len(atoms), 'atoms ->', len(labs), 'labels,', len({o['text'] for o in labs}), 'names')
print('symbols with no label:', [(s['t'], [round(v) for v in s['c']]) for s in S if not s['label']])
print('labels with 2+ symbols:', [(o['text'], o['syms']) for o in labs if len(o['syms']) > 1])
print('labels with no symbol:', [(o['text'], o['cls']) for o in labs if not o['syms']])
