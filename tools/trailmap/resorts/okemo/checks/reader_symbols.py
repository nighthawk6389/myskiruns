"""Each trail's difficulty against the PDF's symbols near every label position a reader reported (not
clustered, unlike pdf_symbols.py --check): prints the trails with no symbol of their type within reach
(NONE: no symbol at all; CHECK: only other types), and the counts.

    python3 tools/trailmap/resorts/okemo/checks/reader_symbols.py   # after regen.sh, from the repo root

Reads $OKEMO_WORK/labels.json and symbols.json, trails.ts and readings/result_*.json. (Scratch
check_symbols2.py of 2026-09-30, run after seed_roster.py; it and pdf_symbols.py --check gave the same 7
trails: the 6 printed with no symbol, and Fairway, whose circle is drawn as another shape.)
"""
import collections
import glob
import json
import math
import os
import re

W_DIR = os.environ.get('OKEMO_WORK', 'work/okemo')
labels = json.load(open(f'{W_DIR}/labels.json'))
syms = json.load(open(f'{W_DIR}/symbols.json'))
ts = open('src/data/resorts/okemo/trails.ts').read()
diff = dict(re.findall(r"id: '([^']+)'.*?difficulty: '([^']+)'", ts))
SYM = {'green': 'circle', 'blue': 'square', 'black': 'diamond', 'double-black': 'double-diamond'}
# raw reader label reports (positions per report, not clustered)
raw = {}
for f in sorted(glob.glob('tools/trailmap/resorts/okemo/readings/result_*.json')):
    for lab in json.load(open(f)).get('labels', []):
        n = re.sub(r'\s+', ' ', (lab.get('mapName') or '').upper().replace('’', "'")).strip(' .')
        raw.setdefault(n, []).append((lab.get('labelSrc'), lab.get('symbol'), f[-6]))
out = []
for tid, e in sorted(labels.items()):
    want = SYM[diff[tid]]
    reach = 5.5 * len(e['mapName']) + 60
    pts = [p for p, _, _ in raw.get(e['mapName'], []) if p] or e['positions']
    near = sorted({(round(math.dist(s['src'], p)), s['type'], tuple(s['src']))
                   for s in syms for p in pts if math.dist(s['src'], p) <= reach})
    types = {t for _, t, _ in near}
    status = 'OK' if want in types else ('NONE' if not near else 'CHECK')
    out.append((status, tid, diff[tid], dict(e['symbols']), near[:4]))
for o in out:
    if o[0] != 'OK':
        print(o)
print(collections.Counter(o[0] for o in out))
