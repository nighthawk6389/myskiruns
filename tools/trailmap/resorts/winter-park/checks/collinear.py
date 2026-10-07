"""Objective check of the piece names: a piece whose end sits on a label's own text line, just before its first
char or after its last (|perp| < 2 pt), continues that label's trail. Compare with the checked table.
Was the scratch wp_collinear.py.

    python3 tools/trailmap/resorts/winter-park/checks/collinear.py      # from the repo root; regen.sh runs it

Reads ../decisions.py, src/data/resorts/winter-park/linePolylines.json and $WINTER_PARK_WORK/wp_names.json; prints
how many pieces continue a label so and every one whose decision is not that label's name (each was settled on a
crop: two labels' lines meet there, or the label sits at a junction).
"""
import json, math, os, sys
WORK = os.environ.get('WINTER_PARK_WORK', 'work/winter-park')
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from decisions import CHECKED, UNNAMED  # noqa: E402 (was exec(open('wp_checked.py').read()))
N = json.load(open(os.path.join(WORK, 'wp_names.json')))
P = {p['id']: p for p in json.load(open('src/data/resorts/winter-park/linePolylines.json'))['polylines']}
pt = lambda q: (40 + q[0] * 13.2, 165 + q[1] * 9.85)
SEG = {pid: [pt(q) for q in p['points']] for pid, p in P.items()}


def parts(q):
    for i in range(1, len(q) - 1):
        a, b = q[i], q[i + 1]
        if (b[0] - a[0]) * (q[1][0] - q[0][0]) + (b[1] - a[1]) * (q[1][1] - q[0][1]) < 0:
            return [q[:i + 1], q[i + 1:]]
    return [q]


hits = {}
for o in N['labels']:
    for q in parts(o['pts']):
        if len(q) < 2:
            continue
        a, b = q[0], q[-1]
        L = math.dist(a, b); u = ((b[0] - a[0]) / L, (b[1] - a[1]) / L)
        for pid, s in SEG.items():
            for e in (s[0], s[-1]):
                for ref, sign in ((b, 1), (a, -1)):
                    v = (e[0] - ref[0], e[1] - ref[1]); along = sign * (v[0] * u[0] + v[1] * u[1]); perp = v[0] * u[1] - v[1] * u[0]
                    if 0 < along < 22 and abs(perp) < 2:
                        hits.setdefault(pid, set()).add(o['text'])
conf = [(pid, sorted(ns), CHECKED.get(pid, 'UNNAMED' if pid in UNNAMED else None)) for pid, ns in sorted(hits.items())
        if CHECKED.get(pid) not in ns]
print(len(hits), 'pieces continue a label collinearly;', len(conf), 'differ from the table:')
for c in conf:
    print('  ', c)
