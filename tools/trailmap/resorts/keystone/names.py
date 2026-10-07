"""Keystone: the trail-name labels, from the glyph labels tools/trailmap/pdf_glyphs.py decoded (scratch: k_names.py).

    python3 tools/trailmap/resorts/keystone/names.py      # regen.sh runs it

Reads $KEYSTONE_WORK/glyph_labels.json (`pdf_glyphs.py labels`: every run of same-colour glyphs as text, and every
symbol fill). Writes $KEYSTONE_WORK/names.json ({labels, syms}): the labels that are trail names (roads, places,
distances and notes dropped), cleaned (glyph-spacing slips fixed, a word-initial l read as I), joined where a name is
set on two lines, each with the difficulty symbol printed before (or after) it attached, and every symbol with the
name it belongs to. Why: the PDF has no text, so these labels are the trail list, and each name's symbol is its
difficulty.
"""
import json
import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import work  # noqa: E402

D = json.load(open(work('glyph_labels.json')))
# glyph-spacing slips (checked on crops); the trail is Schoolmarm, its lower part labelled "Family Ski Trail" too
FIX = {'SpringDipper': 'Spring Dipper', 'TheTrap': 'The Trap', 'U neva': 'Uneva',
       'Schoolmarm Family Ski Trail': 'Schoolmarm'}
NOT = {'Montezuma Road', 'To Montezuma Road', 'River Run Road', 'East Keystone Road', 'Highway 6', 'To East Keystone Road',
       'Gateway', 'Plaza', 'West Keystone Road', 'Keystone', 'Lodge & Spa', 'Stop Light', 'Conference Center',
       'To I-70, Dillon', '& Nordic Center', '.6 Miles', '.75 Miles', '1 Mile', '1 .25 Mile', 'Closes at 2:00 p.m.',
       'Learning', 'Area', 'Adaptive Center', 'North & South Bowl Access', 'via Outback Express', 'closes at 1 :00 p.m.',
       'Access Closes at 1 :30pm', 'I ND E P E N D E N C E MOU NTAIN', '1 2,6 1 4', 'WAPITI PEAK', '1 2,3 5 4', 'Kindred',
       'Resort', 'I I'}


def clean(t):
    t = re.sub(r"\bl(?=[a-zA-Z-])", 'I', t)  # this font's capital I is the l shape: a word-initial l is an I
    return FIX.get(t, t)


labs = []
for o in D['labels']:
    t = clean(o['text'])
    if t is None or t in NOT:
        continue
    labs.append({'text': t, 'cls': o['color'], 'pts': o['pts'], 'c': o['c'], 'lines': [o['pts']], 'seq': o['seq']})
# names set on two lines
JOIN = [['Orfint', 'Boy'], ['Packsaddle', 'Bowl'], ['Ripperoo’s', 'Glade'], ['Jacques St. James']]


def build(first, parts):
    chain = [first]
    for w in parts[1:]:
        cands = [o for o in labs if o['text'] == w and o not in chain and math.dist(o['c'], chain[-1]['c']) < 16
                 and o['cls'] == first['cls']]
        if not cands:
            return None
        chain.append(min(cands, key=lambda o: math.dist(o['c'], chain[-1]['c'])))
    return chain


for parts in JOIN:
    if len(parts) == 1:
        continue
    chain = next((c for f in labs if f['text'] == parts[0] for c in [build(f, parts)] if c), None)
    assert chain, parts
    head = chain[0]
    head['text'] = ' '.join(o['text'] for o in chain)
    head['lines'] = [o['pts'] for o in chain]
    head['pts'] = [q for o in chain for q in o['pts']]
    head['c'] = [round(sum(q[0] for q in head['pts']) / len(head['pts']), 1), round(sum(q[1] for q in head['pts']) / len(head['pts']), 1)]
    for o in chain[1:]:
        labs.remove(o)


def gap_to(o, q):
    best = None
    for pts in o['lines']:
        if len(pts) < 2:
            continue
        a, b = pts[0], pts[-1]
        L = math.dist(a, b); u = ((b[0] - a[0]) / L, (b[1] - a[1]) / L)
        v = (q[0] - a[0], q[1] - a[1]); along = v[0] * u[0] + v[1] * u[1]; perp = v[0] * u[1] - v[1] * u[0]
        g = None
        if abs(perp) < 4 and -12 < along < 0:
            g = -along
        elif abs(perp) < 4 and L < along < L + 12:
            g = along - L + 3  # after the name: only if nothing is before it
        if g is not None and (best is None or g < best):
            best = g
    return best


for o in labs:
    o['syms'] = []
S = D['symbols']
for s in S:
    cands = sorted((g, k) for k, o in enumerate(labs) if (g := gap_to(o, s['c'])) is not None)
    s['label'] = None
    if cands:
        labs[cands[0][1]]['syms'].append(s['t']); s['label'] = labs[cands[0][1]]['text']
# symbols set off their name's text line (checked on crops): Witchita's and Red's squares sit below the start of
# their rotated names; the green circle at (157, 1035) is a traffic light
MANUAL = {(926, 272): 'Witchita', (1010, 230): 'Red'}
for s in S:
    if s['label']:
        continue
    k = next((k for k in MANUAL if math.dist(k, s['c']) < 2), None)
    if k:
        o = min((o for o in labs if o['text'] == MANUAL[k]), key=lambda o: math.dist(o['c'], s['c']))
        o['syms'].append(s['t']); s['label'] = o['text']
json.dump({'labels': labs, 'syms': S}, open(work('names.json'), 'w'), indent=0)
print(len(labs), 'labels,', len({o['text'] for o in labs}), 'names')
print('symbols with no label:', [(s['t'], [round(v) for v in s['c']]) for s in S if not s['label']])
for o in sorted(labs, key=lambda o: o['text']):
    print(f"{o['text']:30s} {o['cls']:6s} {[round(v) for v in o['c']]} {o['syms']}")
