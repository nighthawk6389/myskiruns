"""wp_gaps.json -> trace_gaps.json (traces_to_reviews input): stretches (strokes ordered so each jump > 400 px,
or trails:apply would join them) plus markers for names with no drawn line. Was the scratch wp_traces.py.

    python3 tools/trailmap/resorts/winter-park/traces.py [work folder]      # regen.sh runs it, from the repo root

Reads src/data/resorts/winter-park/trailProposals.json (aggregate_readings.py: each trail's pieces) and, in the work
folder (the argument, else $WINTER_PARK_WORK, default work/winter-park), wp_gaps.json (reading.py) and labels.json
(seed_roster.py: name -> trail id). Writes trace_gaps.json there: per trail with a stretch, its pieces plus the
stretch's points (a trail's several stretches in the order and direction that keep every jump between them over
400 px, so trails:apply keeps them apart); per name with no line, an empty trace (a marker at its label).
"""
import itertools, json, math, os, sys
W = sys.argv[1] if len(sys.argv) > 1 else os.environ.get('WINTER_PARK_WORK', 'work/winter-park')
P = json.load(open('src/data/resorts/winter-park/trailProposals.json'))['trails']
G = json.load(open(f'{W}/wp_gaps.json'))
L = json.load(open(f'{W}/labels.json'))
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
                   'note': 'Named on the map with no line drawn (a painted cut, glade, bowl, park or Cirque run): marker at the label'})
json.dump({'trails': trails}, open(f'{W}/trace_gaps.json', 'w'), indent=1)
print(len(trails), 'trace entries;', sum(1 for t in trails if t['traced']), 'with stretches;', sum(1 for t in trails if not t['traced']), 'markers')
