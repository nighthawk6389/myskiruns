"""show.py out.png x0,y0,x1,y1 [zoom] [--ids a,b]: the PDF page in a PDF-point box, faded, with the current pieces
drawn in bright colours and numbered (was cu_show.py).

    python3 tools/trailmap/resorts/copper-mountain/checks/show.py out.png 480,380,760,640 3.6

Reads the PDF and src/data/resorts/copper-mountain/linePolylines.json.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import DATA, PDF  # noqa: E402
import json, colorsys
import pymupdf
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
p = pymupdf.open(PDF)[0]
x0, y0, x1, y1 = map(float, sys.argv[2].split(','))
z = float(sys.argv[3]) if len(sys.argv) > 3 and not sys.argv[3].startswith('--') else 3
only = None
if '--ids' in sys.argv:
    only = {int(v) for v in sys.argv[sys.argv.index('--ids') + 1].split(',')}
pix = p.get_pixmap(clip=pymupdf.Rect(x0, y0, x1, y1), matrix=pymupdf.Matrix(z, z))
im = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
im = ImageEnhance.Color(im).enhance(0.25)
im = Image.blend(im, Image.new('RGB', im.size, 'white'), 0.35)
dr = ImageDraw.Draw(im)
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 13)
doc = json.load(open(os.path.join(DATA, 'linePolylines.json')))
CX0, CY0, CX1, CY1 = 0, 150, 1303.44, 1052.54
for q in doc['polylines']:
    if only and q['id'] not in only:
        continue
    pts = [((CX0 + u / 100 * (CX1 - CX0) - x0) * z, (CY0 + v / 100 * (CY1 - CY0) - y0) * z) for u, v in q['points']]
    h = (q['id'] * 0.618) % 1
    col = tuple(int(255 * c) for c in colorsys.hsv_to_rgb(h, 1, 0.9))
    dr.line(pts, fill=col, width=3)
    m = pts[len(pts) // 2]
    dr.text((m[0] + 3, m[1] - 7), str(q['id']), fill=col, font=font, stroke_width=2, stroke_fill='white')
im.save(sys.argv[1]); print(im.size)
