"""seq.py  - pieces and labels interleaved in PDF drawing order, to see whether the file groups each trail's line
with its name (Winter Park's did; Breckenridge's does not, so match.py does not use the order).

Scratch: br_seq.py. Reads work/breckenridge.pdf, the pieces (src/data/resorts/breckenridge/linePolylines.json) and
work/names.json; writes work/seq.json and prints the sequence (piece ids, [label names]).
"""
import json, math, os, sys
import pymupdf
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import PDF, PIECES, work  # noqa: E402
p = pymupdf.open(PDF)[0]
X0, Y0, CW, CH = 0, 80, 1458, 845
P = json.load(open(PIECES))['polylines']
first = {q['id']: (X0 + q['points'][0][0] * CW / 100, Y0 + q['points'][0][1] * CH / 100) for q in P}
COL = {(0.0, 0.0, 0.0), (0.01, 0.28, 0.82), (0.02, 0.53, 0.02)}
runs = []
for d in p.get_drawings():
    if d['type'] != 's' or not d.get('color') or tuple(round(v, 2) for v in d['color']) not in COL or not (0.95 <= (d.get('width') or 0) <= 1.05):
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
N = json.load(open(work('names.json')))['labels']
events = [(sq, 'piece', pid) for pid, sq in seq_of.items()] + [(o['seq'], 'label', o['text']) for o in N]
events.sort()
json.dump({'seq_of': seq_of, 'events': events}, open(work('seq.json'), 'w'))
print(' '.join(f'{v}' if k == 'piece' else f'[{v}]' for _, k, v in events))
