"""hl.py PAGE x0,y0,x1,y1 ZOOM OUT seqno[,seqno...] : render a region with the given drawings outlined in magenta."""
import sys, io, pymupdf
from PIL import Image, ImageDraw
pdf = '/home/user/myskiruns/work/whistler-blackcomb/whistler.pdf'
pg = int(sys.argv[1]); x0, y0, x1, y1 = map(float, sys.argv[2].split(',')); z = float(sys.argv[3]); out = sys.argv[4]
seqs = {int(s) for s in sys.argv[5].split(',')} if len(sys.argv) > 5 else set()
p = pymupdf.open(pdf)[pg]
pix = p.get_pixmap(matrix=pymupdf.Matrix(z, z), clip=pymupdf.Rect(x0, y0, x1, y1))
im = Image.open(io.BytesIO(pix.tobytes('png'))).convert('RGB')
im = Image.blend(im, Image.new('RGB', im.size, (255, 255, 255)), 0.45)
dr = ImageDraw.Draw(im)
def P(q): return ((q.x - x0) * z, (q.y - y0) * z)
def bez(a, b, c, e, n=12):
    return [(((1-t)**3*a.x+3*(1-t)**2*t*b.x+3*(1-t)*t*t*c.x+t**3*e.x - x0)*z, ((1-t)**3*a.y+3*(1-t)**2*t*b.y+3*(1-t)*t*t*c.y+t**3*e.y - y0)*z) for t in [i/n for i in range(n+1)]]
for d in p.get_drawings():
    if d['seqno'] not in seqs: continue
    for it in d['items']:
        if it[0] == 'l': dr.line([P(it[1]), P(it[2])], fill=(255, 0, 200), width=3)
        elif it[0] == 'c': dr.line(bez(*it[1:5]), fill=(255, 0, 200), width=3)
        elif it[0] == 're': r = it[1]; dr.rectangle([P(r.tl), P(r.br)], outline=(255, 0, 200), width=3)
    r = d['rect']; dr.text(((r.x0 - x0) * z, (r.y0 - y0) * z - 12), str(d['seqno']), fill=(200, 0, 0))
im.save(out); print(out, im.size)
