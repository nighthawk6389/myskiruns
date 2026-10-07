"""crop.py x0 y0 x1 y1 ZOOM OUT [--labels]: render a PDF region of Park City's map (pt); --labels: draw each
printed label's glyph centres and text (printed.json) in magenta."""
import json, sys, pymupdf
from PIL import Image, ImageDraw, ImageFont
x0, y0, x1, y1, z = map(float, sys.argv[1:6]); out = sys.argv[6]
p = pymupdf.open('/home/user/myskiruns/work/park-city/parkcity.pdf')[0]
pix = p.get_pixmap(matrix=pymupdf.Matrix(z, z), clip=pymupdf.Rect(x0, y0, x1, y1))
im = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
if '--labels' in sys.argv:
    d = ImageDraw.Draw(im)
    F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 12)
    L = json.load(open('/home/user/myskiruns/work/park-city/printed.json'))['labels']
    for l in L:
        if not (x0 <= l['c'][0] <= x1 and y0 <= l['c'][1] <= y1):
            continue
        pts = [((q[0] - x0) * z, (q[1] - y0) * z) for q in l['pts']]
        d.line(pts, fill=(255, 0, 255), width=1)
        d.text((pts[0][0], pts[0][1] + 4), l['text'], fill=(255, 0, 255), font=F)
im.save(out); print(out, im.size)
