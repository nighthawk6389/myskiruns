"""orange.py PAGE: tally stroke colours/widths of orange-ish strokes (r>0.85, 0.3<g<0.75, b<0.3) on the page."""
import sys, collections, pymupdf
doc = pymupdf.open('/home/user/myskiruns/work/whistler-blackcomb/whistler.pdf')
p = doc[int(sys.argv[1])]
c = collections.Counter(); ex = {}
for d in p.get_drawings():
    col = d.get('color'); f = d.get('fill')
    for kind, cc in (('s', col), ('f', f)):
        if not cc: continue
        r, g, b = cc[:3]
        if r > 0.85 and 0.3 < g < 0.8 and b < 0.35:
            k = (kind, tuple(round(v, 3) for v in cc), round(d.get('width') or 0, 2) if kind == 's' else None)
            c[k] += 1
            ex.setdefault(k, []).append(tuple(round(v) for v in d['rect']))
for k, n in c.most_common():
    print(n, k, ex[k][:6])
