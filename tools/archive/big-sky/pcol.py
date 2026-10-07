"""pcol.py PANEL x0,y0,x1,y1 ZOOM OUT id[,id..]: the PDF rendered over the box (map px), the given pieces each in its
own colour with its id at its start (S) and end (E), a legend at the top."""
import json, sys
import pymupdf
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, '/home/user/myskiruns/tools/trailmap')
import pdf_resort as pr
P, b, z, out, ids = sys.argv[1], list(map(float, sys.argv[2].split(','))), float(sys.argv[3]), sys.argv[4], [int(v) for v in sys.argv[5].split(',')]
PDF = {'main': 'bigsky_main.pdf', 'south-face': 'bigsky_south-face.pdf', 'bowl': 'bigsky_bowl.pdf'}[P]
r = pr.Resort(f'big-sky/{P}'); R = r.R
x0, y0 = R.CLIP[:2]
page = pymupdf.open(f'/home/user/myskiruns/work/big-sky/{PDF}')[0]
clip = pymupdf.Rect(b[0] / R.SCALE + x0, b[1] / R.SCALE + y0, b[2] / R.SCALE + x0, b[3] / R.SCALE + y0)
pix = page.get_pixmap(matrix=pymupdf.Matrix(z, z), clip=clip)
im = Image.frombytes('RGB', (pix.width, pix.height), pix.samples).convert('RGBA')
ov = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 13)
N = json.load(open(r.work('names.json')))
Pc = {p['id']: r.pts_of(p) for p in r.load('pieces_cut.json')['polylines']}
k = z / R.SCALE
T = lambda q: ((q[0] - b[0]) * k, (q[1] - b[1]) * k)  # noqa: E731
cols = [(255, 0, 255), (255, 120, 0), (0, 200, 255), (255, 0, 0), (120, 0, 255), (0, 160, 0), (160, 80, 0), (0, 0, 0)]
for n, i in enumerate(ids):
    c = cols[n % len(cols)] + (200,)
    pts = [T(q) for q in Pc[i]]
    d.line(pts, fill=c, width=4)
    d.text((pts[0][0] + 3, pts[0][1] - 14), f'{i}S', fill=c, font=F); d.text((pts[-1][0] + 3, pts[-1][1] + 2), f'{i}E', fill=c, font=F)
    d.rectangle((4, 4 + 16 * n, 16, 16 + 16 * n), fill=c); d.text((20, 3 + 16 * n), f'{i}: {N.get(str(i))}', fill=(0, 0, 0, 255), font=F)
Image.alpha_composite(im, ov).convert('RGB').save(out); print(out, im.size)
