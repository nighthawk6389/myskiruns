"""Copper Mountain: trail-name labels from the decoded glyphs (glyph_labels.json) plus the few names that are
real PDF text (pdf_labels.py output), joined where a name is set on two or three lines, with the difficulty
symbol beside each name attached.

    python3 tools/trailmap/resorts/copper-mountain/names.py       # regen.sh runs it (was cu_names.py)

Reads, in the working folder, glyph_labels.json and syms.json (labels.py) and text_raw.json
(tools/trailmap/pdf_labels.py on the PDF). Writes names.json there (was cu_names.json): {labels: [{text, cls,
pts, c, lines, syms}], syms: [{t, c, col, seq, label}]}, PDF points.
- FIX: glyph runs read as split or joined words, mended; NOT: printed words that are not trail names (signs,
  zones, roads, the snow-maze icon).
- Real text: only the map's trail font (Gotham-Black, 3.6-6.1 pt) in a trail colour; the last copy at a spot.
- JOIN: names set on two or three lines, joined (each next part under 16 pt away, same colour).
- A symbol belongs to the nearest label it sits in line with, before or after the text (under 5 pt off its line,
  up to 20 pt beyond its end), or beside the last line of a name set on several lines (2.5-10 pt off it).
  MANUAL: symbols set apart from their name (checked on crops: z_531.png, z_rhap.png, z_snodeal.png). The green
  circle at (531, 561) is a one-way arrow and the six diamonds at (96-106, 201-213) are the logo's: they stay
  unlabelled.
"""
import json, math
from common import work
GL = json.load(open(work('glyph_labels.json')))
TX = json.load(open(work('text_raw.json')))
S = json.load(open(work('syms.json')))
COLS = {(0.14, 0.12, 0.13): 'black', (0.04, 0.52, 0.78): 'blue', (0.0, 0.65, 0.3): 'green', (0.0, 0.0, 0.0): 'k0'}
FIX = {'P ARK': 'PARK', 'UNIONPARK': None, 'TPRK': None, '-': None, 'F AR EAST': 'FAR EAST', 'THETACO': 'THE TACO', 'CDL’S TRAIL #2O': 'CDL’S TRAIL #20', 'ORE DEAL E': 'ORE DEAL',
       'OHNO': 'OH NO', 'IGREENACRES': 'GREEN ACRES'}
NOT = {'CLOSEDTO', 'DOWNHILL', 'TRAFFIC', '91', 'RR', '(', 'BOUNDARY', 'ALPINELOT- EASTVILLAGEWALKING ROUTE',
       'FORESTSUPERVISORCLOSURE', 'WEST LAKE', 'FREE', 'SLEDDING', 'ZONE', 'THE SNOW MAZE',
       'ALPINE LOT - EAST VILLAGE WALKING ROUTE', 'WATERFALL ROAD'}
labs = []
for o in GL:
    t = FIX.get(o['text'], o['text'])
    if t is None or t in NOT:
        continue
    labs.append({'text': t, 'cls': 'black' if o['col'] == 'k0' else o['col'], 'pts': o['pts'], 'c': o['c'], 'lines': [o['pts']]})
# real text: the last copy drawn at a spot sets the colour; only map trail fonts (Gotham-Black, 3.7-6 pt)
tx = {}
for o in TX:
    if o['font'] != 'Gotham-Black' or not 3.6 <= o['size'] <= 6.1 or tuple(o['color']) not in COLS:
        continue
    k = (o['text'], round(o['c'][0]), round(o['c'][1]))
    tx[k] = o
for o in tx.values():
    if o['text'] in NOT or len(o['text']) < 2:
        continue
    labs.append({'text': o['text'], 'cls': COLS[tuple(o['color'])], 'pts': o['pts'], 'c': o['c'], 'lines': [o['pts']]})
for o in labs:
    if o['cls'] == 'k0':
        o['cls'] = 'black'
# names set on several lines
JOIN = [['UPPER', 'ENCHANTED', 'FOREST'], ['LOWER', 'ENCHANTED', 'FOREST'], ['RESOLUTION', 'BOWL'], ['SPAULDING', 'BOWL'],
        ['KOKO’S', 'PROGRESSION', 'PARK'], ['RED’S', 'BACKYARD'], ['CENTRAL', 'PARK'], ['PIPE', 'DREAM'],
        ['FAMILY CROSS', 'ADVENTUREZONE'], ['GREEN ACRES', 'PROGRESSION', 'PARK'], ['GREEN', 'ACRES'], ['UNION', 'BOWL'],
        ['JACKSTRAW', 'TREES'], ['KOKOMO', 'GLADE'], ['HIGH POINT', 'BYPASS'], ['WEST VILLAGE', 'TRAVERSE'],
        ['MINER’S', 'PROGRESSION', 'PARK']]
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
    chain = next((c for f in labs if f['text'] == parts[0] for c in [build(f, parts)] if c), None)
    assert chain, parts
    head = chain[0]
    head['text'] = ' '.join(o['text'] for o in chain).replace('ADVENTUREZONE', 'ADVENTURE ZONE')
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
        if abs(perp) < 5 and -20 < along < 0: g = -along
        elif abs(perp) < 5 and L < along < L + 20: g = along - L
        elif 2.5 < -perp < 10 and -3 < along < L + 3 and pts is o['lines'][-1] and len(o['lines']) > 1: g = 5
        elif 2.5 < perp < 10 and -3 < along < L + 3 and pts is o['lines'][-1] and len(o['lines']) > 1: g = 5
        if g is not None and (best is None or g < best):
            best = g
    return best


for o in labs:
    o['syms'] = []
for s in S:
    cands = sorted((g, k) for k, o in enumerate(labs) if (g := gap_to(o, s['c'])) is not None)
    s['label'] = None
    if cands:
        labs[cands[0][1]]['syms'].append(s['t']); s['label'] = labs[cands[0][1]]['text']
# symbols set apart from their name (checked on crops: z_531.png, z_rhap.png, z_snodeal.png); the green circle at
# (531, 561) is a one-way arrow and the six diamonds at (96-106, 201-213) are the logo's
MANUAL = {(555, 581): 'SAIL AWAY GLADE', (907, 312): 'UNION MEADOWS', (481, 595): 'RHAPSODY',
          (679, 821): 'SNO DEAL', (640, 813): 'BRIDGEWAY', (717, 827): 'HIDDEN VEIN',
          (398, 368): 'SPAULDING BOWL', (413, 368): 'SPAULDING BOWL', (786, 243): 'COPPER BOWL', (801, 243): 'COPPER BOWL'}
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
    print(f"{o['text']:34s} {o['cls']:6s} {o['syms']}")
