"""veccrop.py map.pdf page x0 y0 x1 y1 zoom out.png [--both]: render the vector layer alone (drawings only) for a clip; --both puts the full render beside it."""
import sys, io
import pymupdf
from PIL import Image
pdf, pno = sys.argv[1], int(sys.argv[2])
x0, y0, x1, y1, z = map(float, sys.argv[3:8]); out = sys.argv[8]
d = pymupdf.open(pdf); p = d[pno]
clip = pymupdf.Rect(x0, y0, x1, y1)
q = pymupdf.open(); np_ = q.new_page(width=p.rect.width, height=p.rect.height)
np_.draw_rect(np_.rect, color=None, fill=(0.8, 0.8, 0.8))
sh = np_.new_shape()
for x in p.get_drawings():
    if not x['rect'].intersects(clip): continue
    for it in x['items']:
        if it[0] == 'l': sh.draw_line(it[1], it[2])
        elif it[0] == 'c': sh.draw_bezier(it[1], it[2], it[3], it[4])
        elif it[0] == 're': sh.draw_rect(it[1])
        elif it[0] == 'qu': sh.draw_quad(it[1])
    sh.finish(color=x.get('color'), fill=x.get('fill'), width=x.get('width') or 0.5, closePath=x.get('closePath', False), even_odd=x.get('even_odd', False), lineCap=0)
sh.commit()
a = Image.open(io.BytesIO(np_.get_pixmap(matrix=pymupdf.Matrix(z, z), clip=clip).tobytes('png'))).convert('RGB')
if '--both' in sys.argv:
    b = Image.open(io.BytesIO(p.get_pixmap(matrix=pymupdf.Matrix(z, z), clip=clip).tobytes('png'))).convert('RGB')
    s = Image.new('RGB', (a.width, a.height * 2 + 4), (255, 0, 0)); s.paste(b, (0, 0)); s.paste(a, (0, a.height + 4)); a = s
a.save(out); print(out, a.size)
