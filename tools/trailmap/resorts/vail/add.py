"""Record naming decisions in decisions.py, always as points: give a piece's current id (its midpoint is stored)
or a point read off a grid crop.

    python3 tools/trailmap/resorts/vail/add.py <panel> "what showed it (which crop)" \\
        123=NAME 2100,1200=NAME 45=-:"why it is not a trail" 2130,1180=-

id=NAME and x,y=NAME go to CHECKED; =- or =-:why to UNNAMED. Ids are those of $VAIL_WORK/pieces_<panel>.json from
the last build.py run; re-run build.py (or regen.sh) afterwards. CUTS and TRACED are edited in decisions.py by hand
(snap a traced stretch first: tools/trailmap/snap_trace.py).
"""
import os
import sys

from common import load, midpoint, pts_of

HERE = os.path.dirname(os.path.abspath(__file__))
panel, comment = sys.argv[1], sys.argv[2]
P = {p['id']: p for p in load(f'pieces_{panel}.json')['polylines']}
named, unnamed = [], []
for a in sys.argv[3:]:
    k, v = a.split('=', 1)
    q = tuple(int(float(t)) for t in k.split(',')) if ',' in k else midpoint(pts_of(panel, P[int(k)]))
    if v.startswith('-'):
        unnamed.append((q, v[2:] if v.startswith('-:') else 'unnamed connector'))
    else:
        named.append((q, v))
f = os.path.join(HERE, 'decisions.py')
s = open(f).read()


def insert(s, block, entries, note):
    if not entries:
        return s
    i = s.index(f'{block} = {{')
    j = s.index(f"'{panel}': [", i) + len(f"'{panel}': [") + 1
    text = f'    # {note}\n' if note else ''
    text += ''.join(f'    (({x}, {y}), {nm!r}),\n' for (x, y), nm in entries)
    return s[:j] + text + s[j:]


s = insert(s, 'CHECKED', named, comment)
s = insert(s, 'UNNAMED', unnamed, None)
open(f, 'w').write(s)
print('recorded', len(named), 'named,', len(unnamed), 'not trails in', f)
