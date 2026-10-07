"""strokes.py OUT x0,y0,x1,y1 (map px) ZOOM seq[,seq...]: the PDF region rendered sharp, and below it the same region
with only the given strokes redrawn on a white ground, each in its own colour with its seqno."""
import sys
import pymupdf
from PIL import Image, ImageDraw, ImageFont
out = sys.argv[1]; b = list(map(float, sys.argv[2].split(','))); z = float(sys.argv[3]); want = [int(v) for v in sys.argv[4].split(',')]
pt = lambda x, y: (x / 2.5 + 12, y / 2.5 + 12)  # noqa: E731
r0, r1 = pt(b[0], b[1]), pt(b[2], b[3])
page = pymupdf.open('/home/user/myskiruns/work/park-city/parkcity.pdf')[0]
pix = page.get_pixmap(matrix=pymupdf.Matrix(z, z), clip=pymupdf.Rect(*r0, *r1))
im = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
ov = Image.new('RGB', im.size, 'white'); d = ImageDraw.Draw(ov)
F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 14)
C = [(230, 0, 0), (0, 120, 255), (0, 160, 0), (200, 0, 200), (255, 140, 0), (0, 170, 170), (120, 60, 0), (0, 0, 0)]
tr = lambda p: ((p[0] - r0[0]) * z, (p[1] - r0[1]) * z)  # noqa: E731
for d0 in page.get_drawings():
    if d0['seqno'] not in want:
        continue
    k = want.index(d0['seqno']); pts = []
    for it in d0['items']:
        if it[0] == 'l':
            pts += [tr((it[1].x, it[1].y)), tr((it[2].x, it[2].y))]
        elif it[0] == 'c':
            a, bb, cc, e = it[1:5]
            pts += [tr(((1-t)**3*a.x+3*(1-t)**2*t*bb.x+3*(1-t)*t*t*cc.x+t**3*e.x, (1-t)**3*a.y+3*(1-t)**2*t*bb.y+3*(1-t)*t*t*cc.y+t**3*e.y)) for t in [j/10 for j in range(11)]]
    if pts:
        d.line(pts, fill=C[k % len(C)], width=3)
        d.ellipse((pts[0][0] - 4, pts[0][1] - 4, pts[0][0] + 4, pts[0][1] + 4), outline=C[k % len(C)], width=2)
        d.text((pts[len(pts) // 2][0] + 3, pts[len(pts) // 2][1] + 3), str(d0['seqno']), fill=C[k % len(C)], font=F)
sheet = Image.new('RGB', (im.width, im.height * 2 + 6), (90, 90, 90)); sheet.paste(im, (0, 0)); sheet.paste(ov, (0, im.height + 6))
sheet.save(out, quality=90); print(out, sheet.size)
