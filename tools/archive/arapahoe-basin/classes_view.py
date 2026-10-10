"""Draw chosen stroke classes (colour x width) of a PDF page in vivid colours over a faded render."""
import sys, pymupdf
from PIL import Image, ImageDraw, ImageEnhance
pdf, out, sc = sys.argv[1], sys.argv[2], float(sys.argv[3])
clip = tuple(map(float, sys.argv[4].split(',')))
d = pymupdf.open(pdf); p = d[0]
pix = p.get_pixmap(matrix=pymupdf.Matrix(sc, sc), clip=pymupdf.Rect(*clip))
im = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
im = Image.blend(im, Image.new('RGB', im.size, 'white'), 0.6)
dr = ImageDraw.Draw(im)
CL = {((0.0, 0.61, 0.86), 0.5): (0, 0, 255), ((0.0, 0.65, 0.32), 0.5): (0, 200, 0),
      ((0.14, 0.12, 0.13), 0.5): (255, 0, 0), ((0.14, 0.12, 0.13), 0.75): (255, 0, 255),
      ((0.16, 0.56, 0.76), 0.5): (0, 220, 220)}
def pts(it):
    if it[0] == 'l': return [it[1], it[2]]
    if it[0] == 'c':
        a, b, c, e = it[1:5]
        return [pymupdf.Point((1-t)**3*a.x+3*(1-t)**2*t*b.x+3*(1-t)*t*t*c.x+t**3*e.x,
                              (1-t)**3*a.y+3*(1-t)**2*t*b.y+3*(1-t)*t*t*c.y+t**3*e.y) for t in [k/12 for k in range(13)]]
    return []
for x in p.get_drawings():
    if 's' not in x['type'] or not x.get('color'): continue
    k = (tuple(round(v, 2) for v in x['color']), round(x.get('width') or 0, 2))
    if k not in CL: continue
    for it in x['items']:
        q = [((P.x-clip[0])*sc, (P.y-clip[1])*sc) for P in pts(it)]
        if len(q) > 1: dr.line(q, fill=CL[k], width=3)
im.save(out); print(im.size)
