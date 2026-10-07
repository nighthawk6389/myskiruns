import sys, collections, pymupdf
doc = pymupdf.open(sys.argv[1])
pg = doc[0]
print(len(doc), pg.rect, pg.mediabox, pg.cropbox)
D = pg.get_drawings()
print(len(D), 'drawings')
c = collections.Counter()
for d in D:
    f = d.get('fill'); s = d.get('color')
    key = (d['type'], tuple(round(v, 2) for v in f) if f else None, tuple(round(v, 2) for v in s) if s else None, round(d.get('width') or 0, 2))
    c[key] += 1
for k, n in c.most_common(40):
    print(n, k)
print('images', [(im[0], im[2], im[3]) for im in pg.get_images(full=True)][:10])
print('text chars', len(pg.get_text()))
