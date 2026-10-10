import json, sys, importlib.util, collections
spec = importlib.util.spec_from_file_location('pg', 'tools/trailmap/pdf_glyphs.py'); pg = importlib.util.module_from_spec(spec); spec.loader.exec_module(pg)
g = json.load(open('work/beaver-creek/glyphs.json'))['glyphs']
table = json.load(open('tools/trailmap/resorts/beaver-creek/letters.json'))
want = sys.argv[1]
by = collections.defaultdict(list)
for i, x in enumerate(g):
    best = None
    for k, t in enumerate(table):
        if t['kinds'] != x['kinds'] or len(t['sig']) != len(x['sig']): continue
        if max(abs(a - b) for a, b in zip(t['sig'], x['sig'])) >= 0.03: continue
        import math
        r = abs(math.log(t['size'] / x['size']))
        if r < math.log(1.15) and (best is None or r < best[0]): best = (r, k)
    if best and table[best[1]]['ch'] == want:
        by[best[1]].append(i)
for k, ms in by.items():
    ctx = []
    for i in ms[:6]:
        ctx.append(''.join((pg.letter(table, g[j]) or '?') for j in range(max(0, i - 4), min(len(g), i + 5))))
    print(k, table[k]['size'], len(ms), ctx)
