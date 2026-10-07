"""Draw given fills (by seqno) of a PDF page, zoomed, with their path points: show_fill.py pdf out.png zoom seq..."""
import sys, pymupdf
from PIL import Image, ImageDraw
sys.path.insert(0, sys.argv[0].rsplit('/', 1)[0] + '/../tools')
from redraw import redraw
pdf, out, z = sys.argv[1], sys.argv[2], float(sys.argv[3])
seqs = {int(s) for s in sys.argv[4:]}
pg = pymupdf.open(pdf)[0]
D = [d for d in pg.get_drawings() if d['seqno'] in seqs]
r = pymupdf.Rect(D[0]['rect'])
for d in D: r |= d['rect']
r = pymupdf.Rect(r.x0 - 3, r.y0 - 3, r.x1 + 3, r.y1 + 3)
a = redraw(pg, D, z, clip=r)
im = Image.fromarray(a); dr = ImageDraw.Draw(im)
for d in D:
    for it in d['items']:
        ps = it[1:] if it[0] in ('l', 'c') else []
        for k, p in enumerate(ps):
            if it[0] == 'c' and k in (1, 2): continue
            x, y = (p.x - r.x0) * z, (p.y - r.y0) * z
            dr.ellipse((x - 2, y - 2, x + 2, y + 2), outline=(255, 0, 0))
im.save(out); print(im.size)
