"""Decisions for one piece cut into named stretches, as decisions.py entries: seg_decisions.py <resort>/<panel> <id>
<name>[@<arc>|<name>@<arc>|...]: the stretches in order along the piece, each name followed by the arc length (px)
where the next one starts; '-' for a stretch that is no run. Prints the CUTS (a point mid-way along the stretch before
each cut, the cut point), the CHECKED and the UNNAMED entries, keyed by points on the piece (repo root, after a build).
e.g. seg_decisions.py aspen-mountain/main 26 'Dipsy Doodle@391|Buckhorn@605|Midway Road@915|-'"""
import json
import math
import sys

from PIL import Image

rid, pid, spec = sys.argv[1], int(sys.argv[2]), sys.argv[3]
W_DIR = f'work/{rid}'
W, H = Image.open(f'{W_DIR}/map.png').size
pts = next([(x * W / 100, y * H / 100) for x, y in p['points']]
           for p in json.load(open(f'{W_DIR}/pieces_cut.json'))['polylines'] if p['id'] == pid)
total = sum(math.dist(a, b) for a, b in zip(pts, pts[1:]))


def at(s):
    for a, b in zip(pts, pts[1:]):
        L = math.dist(a, b)
        if s <= L:
            t = s / L if L else 0
            return (round(a[0] + t * (b[0] - a[0])), round(a[1] + t * (b[1] - a[1])))
        s -= L
    return tuple(round(v) for v in pts[-1])


parts = [p.split('@') for p in spec.split('|')]
bounds = [0] + [float(p[1]) for p in parts[:-1]] + [total]
cuts, checked, unnamed = [], [], []
for k, p in enumerate(parts):
    mid = at((bounds[k] + bounds[k + 1]) / 2)
    (unnamed if p[0] == '-' else checked).append((mid, p[0]))
    if k < len(parts) - 1:
        cuts.append((mid, at(bounds[k + 1])))
print(f'    # piece {pid}')
print('CUTS:', ', '.join(f'({a}, {b})' for a, b in cuts))
print('CHECKED:', ', '.join(f'({q}, {n!r})' for q, n in checked))
if unnamed:
    print('UNNAMED:', ', '.join(f'({q}, ...)' for q, _n in unnamed))
