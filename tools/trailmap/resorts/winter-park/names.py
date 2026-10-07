"""Winter Park: trail-name labels (deduped, two-line names joined) with their printed colour and symbol.
Was the scratch wp_names.py.

    python3 tools/trailmap/resorts/winter-park/names.py      # regen.sh runs it, from the repo root

Reads, in $WINTER_PARK_WORK (default work/winter-park), wp_labels.json (tools/trailmap/pdf_labels.py: every text
piece) and wp_syms.json (symbols.py); writes wp_names.json: {labels: [{text, cls, c, pts, size, seq, syms}],
syms: [... + label, d], not_trails}. Trail names are the Myriad (MyriadVariableConcept) text; a name drawn twice
at one spot (fill + overprint) is one label, coloured as the last copy drawn; five names printed on two lines (or
either side of a lift) are joined (JOIN). Each symbol goes to the name whose text line it sits on, just before
its first character or after its last; a symbol off every line goes to the nearest two-line block with none yet.
"""
import collections, json, math, os
WORK = os.environ.get('WINTER_PARK_WORK', 'work/winter-park')
L = [o for o in json.load(open(os.path.join(WORK, 'wp_labels.json'))) if o['font'].startswith('Myriad')]
S = json.load(open(os.path.join(WORK, 'wp_syms.json')))
COL = {(0.09, 0.54, 0.79): 'blue', (0.01, 0.02, 0.02): 'black', (0.09, 0.63, 0.29): 'green', (0.08, 0.63, 0.3): 'green',
       (0.14, 0.12, 0.13): 'black'}
# one label per printed name: copies at the same place (fill + overprint) collapse; the last one drawn shows
labs = []
for o in sorted(L, key=lambda o: o['seq']):
    t = o['text'].replace('®', '').strip()
    if not t:
        continue
    same = next((q for q in labs if q['text'] == t and math.dist(q['c'], o['c']) < 1.5), None)
    if same:
        same['cls'] = COL[tuple(o['color'])]
        continue
    labs.append({'text': t, 'cls': COL[tuple(o['color'])], 'c': o['c'], 'pts': o['pts'], 'size': o['size'], 'seq': o['seq']})
# names printed on two lines (or either side of a lift) are one label
JOIN = [('UPPER', 'PARKWAY'), ('SOBER', 'ENGLISHMAN'), ('JOHNSTONE', 'JUNCTION'), ('LONESOME', 'WHISTLE'),
        ('RACE PLACE', 'RECREATIONAL RACING')]
for a, b in JOIN:
    A = [q for q in labs if q['text'] == a]; B = [q for q in labs if q['text'] == b]
    d, qa, qb = min((math.dist(x['c'], y['c']), x, y) for x in A for y in B if x is not y)
    assert d < 60, (a, b, d)
    qa['text'] = a + ' ' + b; qa['pts'] = qa['pts'] + qb['pts']
    qa['c'] = [round(sum(p[0] for p in qa['pts']) / len(qa['pts']), 1), round(sum(p[1] for p in qa['pts']) / len(qa['pts']), 1)]
    labs.remove(qb)
NOT_TRAILS = {'RACE PLACE RECREATIONAL RACING': 'race venue label', 'TO VILLAGE WAY': 'pointer to Village Way'}
for o in labs:
    o['syms'] = []
def gap_to(o, q):
    """How far symbol centre q sits before the name's first char or after its last, along the text line
    (None if it is not on that line)."""
    pts = o['pts']
    if len(pts) < 2:
        return math.dist(q, pts[0]) if math.dist(q, pts[0]) < 12 else None
    a, b = pts[0], pts[-1]
    L = math.dist(a, b); u = ((b[0] - a[0]) / L, (b[1] - a[1]) / L)
    v = (q[0] - a[0], q[1] - a[1])
    along = v[0] * u[0] + v[1] * u[1]; perp = abs(v[0] * u[1] - v[1] * u[0])
    if perp > 7:
        return None
    if -16 < along < 0:
        return -along
    if L < along < L + 16:
        return along - L
    return None


for s in S:  # each symbol sits on the line of its name, just before or after it
    cands = sorted((g, k) for k, o in enumerate(labs) if (g := gap_to(o, s['c'])) is not None)
    if cands:
        labs[cands[0][1]]['syms'].append(s['t'])
        s['label'] = labs[cands[0][1]]['text']; s['d'] = round(cands[0][0], 1)
    else:
        s['label'] = None
for s in S:  # names set on two lines: the symbol sits by the block, off either line
    if s['label'] is None:
        d, k = min((min(math.dist(s['c'], q) for q in o['pts']), k) for k, o in enumerate(labs))
        s['d'] = round(d, 1)
        if d < 14 and not labs[k]['syms']:
            labs[k]['syms'].append(s['t']); s['label'] = labs[k]['text']
json.dump({'labels': labs, 'syms': S, 'not_trails': NOT_TRAILS}, open(os.path.join(WORK, 'wp_names.json'), 'w'), indent=0)
print(len(labs), 'labels,', len({o['text'] for o in labs}), 'names')
print('symbols with no label nearby:', [(s['t'], [round(v) for v in s['c']], s['d']) for s in S if not s['label']])
print('labels with 2+ symbols:', [(o['text'], o['syms']) for o in labs if len(o['syms']) > 1])
print('labels with no symbol:', [(o['text'], o['cls']) for o in labs if not o['syms']])
