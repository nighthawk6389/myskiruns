# usage: lab.py x0 y0 x1 y1  (map px) -> printed labels (whole words, not single letters) inside, in map px
import json, sys
x0, y0, x1, y1 = map(float, sys.argv[1:5])
d = json.load(open('/home/user/myskiruns/work/whistler-blackcomb/main/printed.json'))
S = 2.5
rows = []
for l in d['labels']:
    x, y = l['c'][0]*S, l['c'][1]*S
    if x0 <= x <= x1 and y0 <= y <= y1 and len(l['text']) > 1:
        rows.append((round(x), round(y), l['text'], l['color'], l['size'], [round(v*S) for v in l['pts'][0]], [round(v*S) for v in l['pts'][-1]], l.get('font')))
for r in sorted(rows, key=lambda r: (r[1], r[0])):
    print(r)
print('symbols:')
for s in d['symbols'][:0]:
    pass
