"""runs.py glyphs.json [join] [exclude x0,y0,x1,y1 ...]: rough count of glyph runs (labels) - consecutive same-colour glyphs within join pt."""
import json, math, sys, collections
j = json.load(open(sys.argv[1]))
join = float(sys.argv[2]) if len(sys.argv) > 2 else 9.0
ex = [tuple(map(float, a.split(','))) for a in sys.argv[3:]]
g = sorted(j['glyphs'], key=lambda x: x['seq'])
g = [x for x in g if not any(e[0] <= x['c'][0] <= e[2] and e[1] <= x['c'][1] <= e[3] for e in ex)]
runs = []
for x in g:
    if runs and runs[-1][-1]['col'] == x['col'] and math.dist(runs[-1][-1]['c'], x['c']) < join and x['seq'] - runs[-1][-1]['seq'] < 6:
        runs[-1].append(x)
    else:
        runs.append([x])
big = [r for r in runs if len(r) >= 3]
print('glyphs', len(g), 'runs', len(runs), 'runs>=3 glyphs', len(big), collections.Counter(r[0]['col'] for r in big))
