"""orange_draw.py PAGE x0 y0 x1 y1 ZOOM OUT: crop of the page with each orange stroke (by width) redrawn on top:
1.98 red, 1.07 magenta, 0.85 cyan, 1.6 lime, other blue."""
import sys, pymupdf
from PIL import Image, ImageDraw
pg, x0, y0, x1, y1, z = int(sys.argv[1]), *map(float, sys.argv[2:7]); out = sys.argv[7]
doc = pymupdf.open('/home/user/myskiruns/work/whistler-blackcomb/whistler.pdf'); p = doc[pg]
pix = p.get_pixmap(matrix=pymupdf.Matrix(z, z), clip=pymupdf.Rect(x0, y0, x1, y1))
im = Image.frombytes('RGB', (pix.width, pix.height), pix.samples).convert('RGBA')
ov = Image.new('RGBA', im.size); d = ImageDraw.Draw(ov)
col = {1.98: (255, 0, 0, 200), 1.07: (255, 0, 255, 200), 0.85: (0, 220, 255, 160), 1.6: (0, 255, 0, 200)}
tr = lambda q: ((q.x - x0) * z, (q.y - y0) * z)
n = 0
for dr in p.get_drawings():
    c = dr.get('color')
    if dr['type'] not in ('s', 'fs') or not c or tuple(round(v, 3) for v in c) != (0.97, 0.579, 0.116): continue
    r = dr['rect']
    if r.x1 < x0 or r.x0 > x1 or r.y1 < y0 or r.y0 > y1: continue
    w = round(dr.get('width') or 0, 2); n += 1
    for it in dr['items']:
        if it[0] == 'l': d.line([tr(it[1]), tr(it[2])], fill=col.get(w, (0, 0, 255, 200)), width=3)
        elif it[0] == 'c':
            a, b, cc, e = it[1:5]
            pts = [((1-t)**3*a.x+3*(1-t)**2*t*b.x+3*(1-t)*t*t*cc.x+t**3*e.x, (1-t)**3*a.y+3*(1-t)**2*t*b.y+3*(1-t)*t*t*cc.y+t**3*e.y) for t in [k/12 for k in range(13)]]
            d.line([((x - x0) * z, (y - y0) * z) for x, y in pts], fill=col.get(w, (0, 0, 255, 200)), width=3)
Image.alpha_composite(im, ov).convert('RGB').save(out); print(out, n)
