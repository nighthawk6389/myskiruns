"""Crested Butte: the names printed in two or three parts. Pairs of labels in one colour within 30 pt whose joined
text is a name the trail report lists (or starts one), and every label the report doesn't list as it stands: the
list resorts/crested-butte/panels/main/resort.py's JOIN was written from (each pair checked on a crop).

    python3 tools/archive/crested-butte/cb_joins.py      # after prepare.py (work/crested-butte/main/printed.json)
"""
import json, math, re, sys
sys.path.insert(0, 'tools/trailmap/resorts/crested-butte')
import resort as R
d = json.load(open('work/crested-butte/main/printed.json'))
L = [l for l in d['labels'] if l['color'] != 'dark']
keys = {R.key(n): n for n in R.NAMES}
def k(t): return re.sub(r'[^a-z0-9]', '', t.lower())
used = set()
for i, a in enumerate(L):
    for j, b in enumerate(L):
        if i == j or a['color'] != b['color']: continue
        dd = math.dist(a['c'], b['c'])
        if dd > 30: continue
        for t in (a['text'] + ' ' + b['text'],):
            kk = k(t)
            hit = [n for kn, n in keys.items() if kn == kk or (kn.startswith(kk) and len(kk) > 5) ]
            if hit and k(a['text']) not in keys:
                print(f"{a['text']!r} + {b['text']!r} -> {hit} d={dd:.0f} at {[round(v*3) for v in a['c']]}")
print('---- singles not in report:')
for a in L:
    if k(a['text']) not in keys:
        print(repr(a['text']), [round(v*3) for v in a['c']], a['color'])
