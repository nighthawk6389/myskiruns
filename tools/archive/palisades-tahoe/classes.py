"""classes.py PDF OUT ZOOM: the page rendered faintly with each coloured stroke class drawn on top (label: colour,
width, dashed), to see what each class is."""
import sys, collections
import pymupdf
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
pdf, out, z = sys.argv[1], sys.argv[2], float(sys.argv[3])
p = pymupdf.open(pdf)[0]
pix = p.get_pixmap(matrix=pymupdf.Matrix(z, z))
im = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
im = Image.blend(im, Image.new('RGB', im.size, 'white'), 0.75)
d = ImageDraw.Draw(im)
F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 11)
C = [(230, 0, 0), (0, 0, 230), (0, 150, 0), (200, 0, 200), (230, 120, 0), (0, 160, 160), (120, 60, 0), (0, 0, 0)]
keys = {}
for x in p.get_drawings():
    if x['type'] != 's' or not x.get('color'):
        continue
    col = tuple(round(v, 2) for v in x['color'])
    if col == (1.0, 1.0, 1.0) or col == (0.57, 0.0, 0.16) or col in ((1.0, 0.83, 0.12), (0.88, 0.23, 0.24)):
        continue
    k = (col, round(x.get('width') or 0, 2), x.get('dashes') not in (None, '[] 0'))
    if k not in keys:
        keys[k] = C[len(keys) % len(C)]
    pts = []
    for it in x['items']:
        if it[0] == 'l':
            pts += [(it[1].x * z, it[1].y * z), (it[2].x * z, it[2].y * z)]
        elif it[0] == 'c':
            a, b, c, e = it[1:5]
            pts += [(((1-t)**3*a.x+3*(1-t)**2*t*b.x+3*(1-t)*t*t*c.x+t**3*e.x) * z, ((1-t)**3*a.y+3*(1-t)**2*t*b.y+3*(1-t)*t*t*c.y+t**3*e.y) * z) for t in [j/8 for j in range(9)]]
    if len(pts) > 1:
        d.line(pts, fill=keys[k], width=2)
y = 5
for k, c in keys.items():
    d.rectangle((5, y, 25, y + 10), fill=c); d.text((30, y - 2), str(k), fill=c, font=F); y += 15
im.save(out); print(out, im.size, len(keys))
