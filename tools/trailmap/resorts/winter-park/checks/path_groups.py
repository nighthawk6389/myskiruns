"""Which PDF path (drawing) each piece came from: pieces cut from one path by label gaps are one trail's line.
Was the scratch wp_paths.py.

    python3 tools/trailmap/resorts/winter-park/checks/path_groups.py      # from the repo root

Reads $WINTER_PARK_WORK (default work/winter-park)/winterpark.pdf and src/data/resorts/winter-park/linePolylines.json;
writes wp_pathgroups.json there ({path_of: piece -> drawing index, multi: drawing -> its pieces}) and prints the
drawings holding two or more pieces.
"""
import json, math, collections, os, pymupdf
WORK = os.environ.get('WINTER_PARK_WORK', 'work/winter-park')
p = pymupdf.open(os.path.join(WORK, 'winterpark.pdf'))[0]
X0, Y0, CW, CH = 40, 165, 1320, 985
P = json.load(open('src/data/resorts/winter-park/linePolylines.json'))['polylines']
first = {p_['id']: (X0 + p_['points'][0][0] * CW / 100, Y0 + p_['points'][0][1] * CH / 100) for p_ in P}
COL = {(0.09, 0.54, 0.79), (0.09, 0.63, 0.29), (0.01, 0.02, 0.02)}
runs = []  # (drawing index, start point)
for di, d in enumerate(p.get_drawings()):
    if d['type'] != 's' or not d.get('color') or tuple(round(v, 2) for v in d['color']) not in COL:
        continue
    w = d.get('width') or 0
    if not (0.95 <= w <= 1.3):
        continue
    last = None
    for it in d['items']:
        if it[0] not in ('l', 'c'):
            continue
        s = it[1]
        if last is None or math.hypot(last[0] - s.x, last[1] - s.y) > 0.5:
            runs.append((di, (s.x, s.y)))
        e = it[-1] if it[0] == 'c' else it[2]
        last = (e.x, e.y)
path_of = {}
for pid, f in first.items():
    best = min(((math.dist(f, s), di) for di, s in runs))
    if best[0] < 1.0:
        path_of[pid] = best[1]
groups = collections.defaultdict(list)
for pid, di in path_of.items():
    groups[di].append(pid)
multi = {di: sorted(v) for di, v in groups.items() if len(v) > 1}
print(len(path_of), 'pieces mapped;', len(groups), 'paths;', len(multi), 'paths with 2+ pieces')
json.dump({'path_of': path_of, 'multi': multi}, open(os.path.join(WORK, 'wp_pathgroups.json'), 'w'))
for di, v in sorted(multi.items(), key=lambda kv: kv[1][0]):
    print(di, v)
