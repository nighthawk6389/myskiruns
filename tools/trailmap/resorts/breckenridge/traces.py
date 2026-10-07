"""gaps.json -> trace_gaps.json (traces_to_reviews input): stretches (strokes ordered so each jump > 400 px,
or trails:apply would join them) plus markers for names with no drawn line.

    python3 tools/trailmap/resorts/breckenridge/traces.py      # regen.sh runs it (scratch: br_traces.py, made from
                                                              # Winter Park's wp_traces.py)

Reads work/gaps.json (reading.py), work/labels.json (seed_roster.py: map name -> trail id) and the trail's pieces
from src/data/resorts/breckenridge/trailProposals.json (aggregate_readings.py). Writes work/trace_gaps.json, one
entry per trail with a stretch (its pieces + the stretch along its printed name) or with no line (a marker at its
label); traces_to_reviews.py makes each one of Claude's reviews.
"""
import itertools, json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import DATA, work  # noqa: E402
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
