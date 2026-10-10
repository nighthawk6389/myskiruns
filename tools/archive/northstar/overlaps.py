"""Stretches where two of Northstar's named pieces run along each other (within 5 px for over 40 px): an outline
drawn for each of two runs over a shared stretch, or a centre line doubled; there hovering would show either name,
so the stretch needs a cut (decisions.py) to leave it to the run whose name is printed on it.

    python3 tools/archive/northstar/overlaps.py [work/northstar]      (after a build)
"""
import json
import math
import sys

from PIL import Image

sys.path.insert(0, 'tools/trailmap')
from pdf_resort import line_dist  # noqa: E402

W_DIR = sys.argv[1] if len(sys.argv) > 1 else 'work/northstar'
W, H = Image.open(f'{W_DIR}/map.png').size
N = json.load(open(f'{W_DIR}/names.json'))
P = {p['id']: [(x * W / 100, y * H / 100) for x, y in p['points']]
     for p in json.load(open(f'{W_DIR}/pieces_cut.json'))['polylines']}


def resample(pts, step=4.0):
    out = [pts[0]]
    for a, b in zip(pts, pts[1:]):
        n = max(1, int(math.dist(a, b) / step))
        out += [(a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n) for k in range(1, n + 1)]
    return out


named = {i: pts for i, pts in P.items() if N.get(str(i), '?') not in ('?', '-')}
for i, pts in sorted(named.items()):
    for j, other in sorted(named.items()):
        if j == i or N[str(j)].rstrip('~') == N[str(i)].rstrip('~'):
            continue
        close = [q for q in resample(pts) if line_dist(q, other) < 5]
        if len(close) * 4 > 40:
            print(f'{i} {N[str(i)]} runs along {j} {N[str(j)]} for ~{len(close) * 4} px, '
                  f'from ({close[0][0]:.0f}, {close[0][1]:.0f}) to ({close[-1][0]:.0f}, {close[-1][1]:.0f})')
