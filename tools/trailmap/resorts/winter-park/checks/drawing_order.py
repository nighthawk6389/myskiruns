"""The PDF's own grouping: drawings and text in display order. Each trail's line pieces sit next to its labels.
Was the scratch wp_seq.py.

    python3 tools/trailmap/resorts/winter-park/checks/drawing_order.py      # from the repo root

Reads $WINTER_PARK_WORK (default work/winter-park)/winterpark.pdf and wp_labels.json, and
src/data/resorts/winter-park/linePolylines.json; writes wp_seq.json there ({seq_of: piece -> the seqno of the
stroke it starts on, events: [(seqno, piece|label, id|text)]}) and prints the sequence, pieces as ids and labels in
[brackets]. The artwork lists trails Z to A, each one's labels next to its strokes, so a piece usually belongs to the
label just before it (off by one at some group boundaries: the crop decides).
"""
import json, math, os, pymupdf
WORK = os.environ.get('WINTER_PARK_WORK', 'work/winter-park')
p = pymupdf.open(os.path.join(WORK, 'winterpark.pdf'))[0]
X0, Y0, CW, CH = 40, 165, 1320, 985
P = json.load(open('src/data/resorts/winter-park/linePolylines.json'))['polylines']
first = {q['id']: (X0 + q['points'][0][0] * CW / 100, Y0 + q['points'][0][1] * CH / 100) for q in P}
COL = {(0.09, 0.54, 0.79), (0.09, 0.63, 0.29), (0.01, 0.02, 0.02)}
runs = []
for d in p.get_drawings():
    if d['type'] != 's' or not d.get('color') or tuple(round(v, 2) for v in d['color']) not in COL or not (0.95 <= (d.get('width') or 0) <= 1.3):
        continue
    last = None
    for it in d['items']:
        if it[0] not in ('l', 'c'):
            continue
        s = it[1]
        if last is None or math.hypot(last[0] - s.x, last[1] - s.y) > 0.5:
            runs.append((d['seqno'], (s.x, s.y)))
        e = it[-1] if it[0] == 'c' else it[2]
        last = (e.x, e.y)
seq_of = {pid: min((math.dist(f, s), sq) for sq, s in runs)[1] for pid, f in first.items()}
L = json.load(open(os.path.join(WORK, 'wp_labels.json')))
events = [(sq, 'piece', pid) for pid, sq in seq_of.items()] + \
         [(o['seq'], 'label', o['text']) for o in L if o['font'].startswith('Myriad')]
events.sort()
json.dump({'seq_of': seq_of, 'events': events}, open(os.path.join(WORK, 'wp_seq.json'), 'w'))
line = []
for sq, kind, v in events:
    line.append(f'{v}' if kind == 'piece' else f'[{v}]')
print(' '.join(line))
