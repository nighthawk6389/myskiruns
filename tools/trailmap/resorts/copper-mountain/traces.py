"""gaps.json -> trace_gaps.json (traces_to_reviews input): stretches (strokes ordered so each jump > 400 px,
or trails:apply would join them) plus markers for names with no drawn line.

    python3 tools/trailmap/resorts/copper-mountain/traces.py      # regen.sh runs it (was cu_traces.py)

Reads gaps.json (reading.py) and labels.json (seed_roster.py's trail ids by printed name) in the working folder,
and src/data/resorts/copper-mountain/trailProposals.json (each stretch's trail keeps its proposed pieces). Writes
trace_gaps.json there, for tools/trailmap/traces_to_reviews.py: one "confirmed" entry per trail with stretches
(its pieces + the stretches' points, ordered and flipped so that consecutive stretches are over 400 px apart, or
trails:apply would join them into one line) and one empty entry per marker (a "no-line" review at the label).
"""
import itertools, json, math, os
from common import DATA, work
P = json.load(open(os.path.join(DATA, 'trailProposals.json')))['trails']
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
