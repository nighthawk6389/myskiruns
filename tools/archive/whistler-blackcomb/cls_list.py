import sys, pymupdf
pdf = '/home/user/myskiruns/work/whistler-blackcomb/whistler.pdf'
pg = int(sys.argv[1]); want = tuple(map(float, sys.argv[2].split(','))); w = float(sys.argv[3])
p = pymupdf.open(pdf)[pg]
n = 0
for d in p.get_drawings():
    if d['type'] not in ('s', 'fs') or not d.get('color'): continue
    if tuple(round(v, 2) for v in d['color']) != want or round(d.get('width') or 0, 2) != w: continue
    r = d['rect']
    if r.y0 > 845: continue
    n += 1
    print(d['seqno'], [round(v) for v in (r.x0, r.y0, r.x1, r.y1)], ''.join(it[0] for it in d['items'])[:40], d.get('dashes'), d.get('lineCap'))
print(n)
