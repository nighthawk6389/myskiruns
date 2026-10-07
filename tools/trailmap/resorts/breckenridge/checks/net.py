"""Every Breckenridge piece in a PDF box drawn in its own colour, both ends dotted and tagged id:name (the reading's),
over the PDF faded to 55%: how a trail's pieces connect around a junction (the E-Chair runs: net.py
355,330,485,430 6 out.png).

    python3 tools/trailmap/resorts/breckenridge/checks/net.py x0,y0,x1,y1 zoom out.png     # the box in PDF points
"""
import colorsys, json, os, sys
import pymupdf
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from common import PDF, PIECES, work  # noqa: E402

x0, y0, x1, y1 = map(float, sys.argv[1].split(','))
Z, out = float(sys.argv[2]), sys.argv[3]
pl = json.load(open(PIECES))['polylines']
name_of = {l['id']: l['mapName'] for l in json.load(open(work('tiles/result_breck.json')))['lines']}
pix = pymupdf.open(PDF)[0].get_pixmap(matrix=pymupdf.Matrix(Z, Z), clip=pymupdf.Rect(x0, y0, x1, y1))
im = Image.blend(Image.frombytes('RGB', (pix.width, pix.height), pix.samples), Image.new('RGB', (pix.width, pix.height), 'white'), 0.45)
d = ImageDraw.Draw(im)
k = 0
for p in pl:
    Q = [((14.58 * u - x0) * Z, (80 + 8.45 * v - y0) * Z) for u, v in p['points']]
    if not any(0 <= x <= im.width and 0 <= y <= im.height for x, y in Q):
        continue
    r, g, b = colorsys.hsv_to_rgb((k * 0.137) % 1, 0.9, 0.85); k += 1
    col = (int(r * 255), int(g * 255), int(b * 255))
    d.line(Q, fill=col, width=3)
    for q in (Q[0], Q[-1]):
        d.ellipse((q[0] - 4, q[1] - 4, q[0] + 4, q[1] + 4), fill=col)
    mx, my = Q[len(Q) // 2]
    d.text((mx + 5, my - 12), f"{p['id']}:{name_of.get(p['id'], '-')}", fill=col)
im.save(out)
print(out, im.size)
