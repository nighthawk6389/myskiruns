"""drawgroups.py OUT x0,y0,x1,y1 ZOOM spec...: the page region with the strokes of each spec 'r,g,b@w[@dashed]=COLOR'
redrawn in COLOR (hex)."""
import sys, pymupdf
from PIL import Image, ImageDraw
out, box, z = sys.argv[1], tuple(map(float, sys.argv[2].split(','))), float(sys.argv[3])
specs = []
for s in sys.argv[4:]:
    k, col = s.split('=')
    parts = k.split('@')
    specs.append((tuple(round(float(v), 2) for v in parts[0].split(',')), round(float(parts[1]), 2),
                  None if len(parts) < 3 else parts[2] == 'd', '#' + col))
doc = pymupdf.open('/home/user/myskiruns/work/park-city/parkcity.pdf'); p = doc[0]
pix = p.get_pixmap(matrix=pymupdf.Matrix(z, z), clip=pymupdf.Rect(*box))
im = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
im = Image.blend(im, Image.new('RGB', im.size, 'white'), 0.55)
d = ImageDraw.Draw(im)
tr = lambda x, y: ((x - box[0]) * z, (y - box[1]) * z)
n = [0] * len(specs)
for dr in p.get_drawings():
    c = dr.get('color')
    if dr['type'] not in ('s', 'fs') or not c:
        continue
    key = (tuple(round(v, 2) for v in c), round(dr.get('width') or 0, 2))
    dashed = dr.get('dashes') not in (None, '[] 0')
    for k, (sc, sw, sd, col) in enumerate(specs):
        if key != (sc, sw) or (sd is not None and sd != dashed):
            continue
        n[k] += 1
        for it in dr['items']:
            if it[0] == 'l':
                d.line([tr(it[1].x, it[1].y), tr(it[2].x, it[2].y)], fill=col, width=2)
            elif it[0] == 'c':
                a, b, cc, e = it[1:5]
                pts = [((1-t)**3*a.x+3*(1-t)**2*t*b.x+3*(1-t)*t*t*cc.x+t**3*e.x, (1-t)**3*a.y+3*(1-t)**2*t*b.y+3*(1-t)*t*t*cc.y+t**3*e.y) for t in [i/10 for i in range(11)]]
                d.line([tr(*q) for q in pts], fill=col, width=2)
im.save(out); print(out, n)
