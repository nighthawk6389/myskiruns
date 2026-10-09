"""Rank the main panel's pieces by their distance to given printed names (the median of each letter's distance):
which line a name is printed on. near.py NAME [NAME ...] (as printed, e.g. 'GARRETT', 'HANG ON'); run from the repo
root after a build (work/snowmass/main/: pieces_cut.json, names.json, printed.json)."""
import json
import math
import sys


def seg(q, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    n = dx * dx + dy * dy
    t = max(0, min(1, ((q[0] - a[0]) * dx + (q[1] - a[1]) * dy) / n)) if n else 0
    return math.dist(q, (a[0] + t * dx, a[1] + t * dy))


sc = 3
W, H = 4104, 1560
P = json.load(open('work/snowmass/main/pieces_cut.json'))['polylines']
N = json.load(open('work/snowmass/main/names.json'))
pp = [([(x * W / 100, y * H / 100) for x, y in p['points']], p['id']) for p in P]
L = json.load(open('work/snowmass/main/printed.json'))['labels']
for lab in L:
    if lab['text'] not in sys.argv[1:]:
        continue
    q = [(x * sc, y * sc) for x, y in lab['pts']]
    res = []
    for pts, i in pp:
        ds = [min(seg(v, a, b) for a, b in zip(pts, pts[1:])) for v in q]
        res.append((round(sorted(ds)[len(ds) // 2], 1), i, N[str(i)]))
    res.sort()
    print(lab['text'], [round(v) for v in q[0]], [round(v) for v in q[-1]], res[:3])
