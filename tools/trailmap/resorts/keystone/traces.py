"""Keystone: gaps.json -> trace_gaps.json (traces_to_reviews input): stretches (strokes ordered so each jump > 400 px,
or trails:apply would join them) plus markers for names with no drawn line (scratch: k_traces.py).

    python3 tools/trailmap/resorts/keystone/traces.py      # regen.sh runs it, after aggregate_readings.py

Reads $KEYSTONE_WORK/gaps.json (reading.py), $KEYSTONE_WORK/labels.json (seed_roster.py: name -> trail id) and
src/data/resorts/keystone/trailProposals.json (each trail's pieces). Writes $KEYSTONE_WORK/trace_gaps.json in the
trace readers' format, so traces_to_reviews.py makes each one Claude's review: a stretched trail keeps its pieces
plus the stretch drawn along its name; a name with no line becomes a no-line review with a marker at its label.
"""
import itertools
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import data, work  # noqa: E402

P = json.load(open(data('trailProposals.json')))['trails']
G = json.load(open(work('gaps.json')))
L = json.load(open(work('labels.json')))
slug = {v['mapName']: k for k, v in L.items()}
trails = []
for n, sts in G['stretches'].items():
    tid = slug[n]
    best = None
    for perm in itertools.permutations(range(len(sts))):
        for flips in itertools.product((False, True), repeat=len(sts)):
            seq = [sts[i][::-1] if f else sts[i] for i, f in zip(perm, flips)]
            jumps = [math.dist(a[-1], b[0]) for a, b in zip(seq, seq[1:])] or [9999]
            if best is None or min(jumps) > best[0]:
                best = (min(jumps), seq)
    assert best[0] > 400, (n, best[0])
    trails.append({'id': tid, 'pieces': (P.get(tid) or {}).get('polylines') or [], 'traced': [q for s in best[1] for q in s],
                   'confidence': 'high', 'note': 'Label printed in a gap of its own line or at its end: the stretch along the printed name, plus its pieces'})
for n in G['markers']:
    tid = slug[n]
    assert not (P.get(tid) or {}).get('polylines'), tid
    trails.append({'id': tid, 'pieces': [], 'traced': [], 'confidence': 'high',
                   'note': 'Named on the map with no line drawn (a bowl, open area, park or kids zone): marker at the label'})
json.dump({'trails': trails}, open(work('trace_gaps.json'), 'w'), indent=1)
print(len(trails), 'trace entries;', sum(1 for t in trails if t['traced']), 'with stretches;', sum(1 for t in trails if not t['traced']), 'markers')
