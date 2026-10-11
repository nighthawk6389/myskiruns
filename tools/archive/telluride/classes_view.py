"""Draw chosen stroke classes of a PDF page in vivid colours over a faded render.

    classes_view.py <pdf> <out.png> <scale> x0,y0,x1,y1 r,g,b@width=R,G,B[:dash|:solid] ...
"""
import sys
import pymupdf
from PIL import Image, ImageDraw

pdf, out, sc = sys.argv[1], sys.argv[2], float(sys.argv[3])
clip = tuple(map(float, sys.argv[4].split(',')))
CL = {}
for spec in sys.argv[5:]:
    k, v = spec.split('=')
    col, w = k.split('@')
    v, _, mode = v.partition(':')
    CL[(tuple(round(float(a), 2) for a in col.split(',')), round(float(w), 2))] = (tuple(int(a) for a in v.split(',')), mode)
d = pymupdf.open(pdf); p = d[0]
pix = p.get_pixmap(matrix=pymupdf.Matrix(sc, sc), clip=pymupdf.Rect(*clip))
im = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
im = Image.blend(im, Image.new('RGB', im.size, 'white'), 0.65)
dr = ImageDraw.Draw(im)


def pts(it):
    if it[0] == 'l':
        return [it[1], it[2]]
    if it[0] == 'c':
        a, b, c, e = it[1:5]
        return [pymupdf.Point((1-t)**3*a.x+3*(1-t)**2*t*b.x+3*(1-t)*t*t*c.x+t**3*e.x,
                              (1-t)**3*a.y+3*(1-t)**2*t*b.y+3*(1-t)*t*t*c.y+t**3*e.y) for t in [k/12 for k in range(13)]]
    return []


for x in p.get_drawings():
    if 's' not in x['type'] or not x.get('color'):
        continue
    k = (tuple(round(v, 2) for v in x['color']), round(x.get('width') or 0, 2))
    if k not in CL:
        continue
    col, mode = CL[k]
    dashed = x.get('dashes') not in (None, '[] 0')
    if (mode == 'dash' and not dashed) or (mode == 'solid' and dashed):
        continue
    for it in x['items']:
        q = [((P.x-clip[0])*sc, (P.y-clip[1])*sc) for P in pts(it)]
        if len(q) > 1:
            dr.line(q, fill=col, width=3)
im.save(out)
print(im.size)
