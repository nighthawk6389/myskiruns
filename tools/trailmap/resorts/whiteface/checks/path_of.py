"""Which PDF path (drawing) each extracted piece came from, to see whether a path's pieces (one stroke broken by
label gaps) belong together (scratch: the one-off script that wrote path_of.json). On this map they never needed
to: every piece is a path of its own (162 paths for 162 pieces), so the cuts were settled on crops alone.

    python3 tools/trailmap/resorts/whiteface/checks/path_of.py [pieces.json]

Reads the pieces before the cuts ($WHITEFACE_WORK/linePolylines_before_split.json, which regen.sh keeps), re-walks
the PDF's strokes the way extract_pdf_vectors.py does and asserts one run per piece. Prints every path that gave
more than one piece with the pieces' names in $WHITEFACE_WORK/wf_assign.json (build.py's, after the cuts: the
first time round they were the names before the cuts) and writes $WHITEFACE_WORK/path_of.json ({piece id:
drawing index}).
"""
import collections
import json
import math
import os
import sys

import pymupdf

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../../..'))
WORK = os.path.abspath(os.environ.get('WHITEFACE_WORK', os.path.join(REPO, 'work/whiteface')))
page = pymupdf.open(os.path.join(WORK, 'whiteface.pdf'))[0]
classes = {(0.0, 0.46, 0.74): 'blue', (0.14, 0.12, 0.13): 'black', (0.0, 0.52, 0.27): 'green'}
runs = []
for di, d in enumerate(page.get_drawings()):
    w = d.get('width') or 0
    if d['type'] != 's' or not d.get('color') or w > 1.6:
        continue
    cls = classes.get(tuple(round(v, 2) for v in d['color']))
    if not cls:
        continue
    run = []
    for it in d['items']:
        if it[0] == 'l': start, seg = it[1], [it[2]]
        elif it[0] == 'c': start, seg = it[1], [it[4]]
        else: continue
        if run and math.hypot(run[-1][0] - start.x, run[-1][1] - start.y) > 0.5:
            runs.append((di, cls, run)); run = []
        if not run: run = [(start.x, start.y)]
        run.extend((p.x, p.y) for p in seg)
    if run: runs.append((di, cls, run))
kept = []
for di, cls, run in runs:
    L = sum(math.dist(a, b) for a, b in zip(run, run[1:]))
    if L < 4: continue
    xs = [p[0] for p in run]; ys = [p[1] for p in run]
    if math.dist(run[0], run[-1]) < 0.5 and math.hypot(max(xs)-min(xs), max(ys)-min(ys)) < 10: continue
    kept.append((di, cls, run))
P = json.load(open(sys.argv[1] if len(sys.argv) > 1 else os.path.join(WORK, 'linePolylines_before_split.json')))['polylines']
assert len(kept) == len(P), (len(kept), len(P))
path_of = {p['id']: kept[i][0] for i, p in enumerate(P)}
groups = collections.defaultdict(list)
for pid, di in path_of.items(): groups[di].append(pid)
A = json.load(open(os.path.join(WORK, 'wf_assign.json')))['assign']
multi = {di: ids for di, ids in groups.items() if len(ids) > 1}
for di, ids in sorted(multi.items(), key=lambda kv: kv[1][0]):
    print(di, ids, [A.get(str(i), []) for i in ids])
json.dump({str(k): v for k, v in path_of.items()}, open(os.path.join(WORK, 'path_of.json'), 'w'))
print(len(groups), 'paths for', len(P), 'pieces')
