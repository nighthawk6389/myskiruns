"""Each pdf stroke of a colour and width range in a clip, drawn in its own colour with its piece id from pieces.json
(nearest), over a faded render: which stroke is which line."""
import json, math, sys, colorsys
import pymupdf
from PIL import Image, ImageDraw, ImageFont
pdf, out, z = sys.argv[1], sys.argv[2], float(sys.argv[3])
clip = tuple(map(float, sys.argv[4].split(',')))
pieces = sys.argv[5] if len(sys.argv) > 5 else None
d = pymupdf.open(pdf); p = d[0]
pix = p.get_pixmap(matrix=pymupdf.Matrix(z, z), clip=pymupdf.Rect(*clip))
im = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
im = Image.blend(im, Image.new('RGB', im.size, 'white'), 0.55)
dr = ImageDraw.Draw(im)
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 14)
P = json.load(open(pieces))['polylines'] if pieces else []
k = 0
for x in p.get_drawings():
    c = x.get('color'); w = x.get('width') or 0
    if x['type'] != 's' or not c or not 0.9 <= w <= 1.1 or tuple(round(v, 2) for v in c) not in ((0.14, 0.12, 0.12), (0.0, 0.68, 0.93), (0.0, 0.65, 0.32)):
        continue
    pts = []
    for it in x['items']:
        if it[0] == 'l': pts += [(it[1].x, it[1].y), (it[2].x, it[2].y)]
        elif it[0] == 'c':
            a, b, cc, e = it[1:5]
            pts += [((1-t)**3*a.x+3*(1-t)**2*t*b.x+3*(1-t)*t*t*cc.x+t**3*e.x, (1-t)**3*a.y+3*(1-t)**2*t*b.y+3*(1-t)*t*t*cc.y+t**3*e.y) for t in [j/10 for j in range(11)]]
    if not any(clip[0] <= a <= clip[2] and clip[1] <= b <= clip[3] for a, b in pts):
        continue
    hue = (k * 0.137) % 1; k += 1
    col = tuple(int(255 * v) for v in colorsys.hsv_to_rgb(hue, 1, 0.85))
    q = [((a - clip[0]) * z, (b - clip[1]) * z) for a, b in pts]
    dr.line(q, fill=col, width=3)
    m = q[len(q) // 2]
    dr.text(m, str(x.get('seqno')), fill=col, font=font, stroke_width=2, stroke_fill=(255, 255, 255))
im.save(out); print(im.size, k)
