"""Whiteface: the label-gap stretches as traces for traces_to_reviews.py (scratch: an inline step of the
2026-09-30 build).

    python3 tools/trailmap/resorts/whiteface/stretches.py

Reads src/data/resorts/whiteface/trailProposals.json and trails.ts, $WHITEFACE_WORK/labels.json (seed_roster.py)
and $WHITEFACE_WORK/wf_gaps.json (reading.py). Writes $WHITEFACE_WORK/trace_gaps.json ({trails: [{id, pieces,
traced, confidence, note}]}): per trail whose name is printed in a gap of its line (or whose label is all of
its line), its proposed pieces plus the stretch along the printed name, which traces_to_reviews.py turns into a
confirmed review by Claude. A name printed twice gives two strokes, joined in one trace; they must lie more
than 400 px apart, or trails:apply would join them into one line. Also prints the trails with no proposed
pieces and no marker: the five whose overlay is their stretch alone (John's Bypass, Off Broadway, Round-a-bout,
Upper Thruway, Yellow Dot).
"""
import json
import math
import os
import re

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../..'))
WORK = os.path.abspath(os.environ.get('WHITEFACE_WORK', os.path.join(REPO, 'work/whiteface')))
D = os.path.join(REPO, 'src/data/resorts/whiteface')

P = json.load(open(os.path.join(D, 'trailProposals.json')))['trails']
ts = open(os.path.join(D, 'trails.ts')).read()
ids = re.findall(r"id: '([^']+)'", ts)[1:]
print('no proposal:', [(i, P.get(i)) for i in ids if not P.get(i) or (not P[i].get('polylines') and not P[i].get('noLine'))])
L = json.load(open(os.path.join(WORK, 'labels.json')))
G = json.load(open(os.path.join(WORK, 'wf_gaps.json')))
def slug(s):
    import unicodedata
    s = ''.join(c for c in unicodedata.normalize('NFKD', s) if not unicodedata.combining(c))
    return re.sub(r'[^a-z0-9]+', '-', s.lower().replace("'", '')).strip('-')
by = {}
for n, pts in G['stretches']:
    by.setdefault(slug(n), []).append(pts)
trails = []
for tid, strokes in by.items():
    assert tid in ids, tid
    if len(strokes) > 1:  # separate strokes must be > 400 px apart or trails:apply joins them
        for a, b in zip(strokes, strokes[1:]):
            assert math.dist(a[-1], b[0]) > 400, (tid, a[-1], b[0])
    pieces = (P.get(tid) or {}).get('polylines') or []
    trails.append({'id': tid, 'pieces': pieces, 'traced': [q for s in strokes for q in s], 'confidence': 'high',
                   'note': 'Label printed in a gap of its own line (or the line is only the label): the stretch along the printed name, plus its pieces'})
json.dump({'trails': trails}, open(os.path.join(WORK, 'trace_gaps.json'), 'w'), indent=1)
print(len(trails), 'trails get label-gap stretches')
