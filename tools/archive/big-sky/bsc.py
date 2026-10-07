"""bsc.py PANEL x0,y0,x1,y1 (map px) ZOOM OUT [--names] [--pieces] [--raw]: Big Sky's panel PDF rendered sharp over
the box; --names: each name (pdf_resort's reading, after joins) as a magenta line through its characters with its
text, symbols as red marks with the name they went to; --pieces: line pieces (pieces_cut.json) with ids and names;
--raw: every dark text object (printed.json) in cyan."""
import contextlib, io, json, os, sys
import pymupdf
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, '/home/user/myskiruns/tools/trailmap')
import pdf_resort as pr
P = sys.argv[1]; b = list(map(float, sys.argv[2].split(','))); z = float(sys.argv[3]); out = sys.argv[4]
PDF = {'main': 'bigsky_main.pdf', 'south-face': 'bigsky_south-face.pdf', 'bowl': 'bigsky_bowl.pdf'}[P]
r = pr.Resort(f'big-sky/{P}')
R = r.R
x0, y0 = R.CLIP[0], R.CLIP[1]
pt = lambda x, y: (x / R.SCALE + x0, y / R.SCALE + y0)  # noqa: E731
r0, r1 = pt(b[0], b[1]), pt(b[2], b[3])
page = pymupdf.open(f'/home/user/myskiruns/work/big-sky/{PDF}')[0]
pix = page.get_pixmap(matrix=pymupdf.Matrix(z, z), clip=pymupdf.Rect(*r0, *r1))
im = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
d = ImageDraw.Draw(im)
F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 12)
trp = lambda q: ((q[0] - r0[0]) * z, (q[1] - r0[1]) * z)  # noqa: E731  (PDF points)
trm = lambda q: trp(pt(*q))  # noqa: E731  (map px)
vis = lambda q: any(0 <= x <= im.width and 0 <= y <= im.height for x, y in q)  # noqa: E731
if '--names' in sys.argv or '--pieces' in sys.argv:
    with contextlib.redirect_stdout(io.StringIO()):
        r.build()
if '--raw' in sys.argv:
    for l in json.load(open(r.work('printed.json'))):
        if not R.is_name(l):
            continue
        q = [trp(p) for p in l['pts']]
        if vis(q):
            d.line(q, fill=(0, 200, 255), width=1)
            d.text((q[0][0], q[0][1] + 14), l['text'], fill=(0, 150, 220), font=F)
if '--names' in sys.argv:
    for n in r.names_all:
        q = [trm(p) for p in n['pts']]
        if not vis(q):
            continue
        d.line(q, fill=(255, 0, 255), width=2) if len(q) > 1 else d.ellipse((q[0][0] - 3, q[0][1] - 3, q[0][0] + 3, q[0][1] + 3), outline=(255, 0, 255))
        d.text((q[0][0], q[0][1] + 4), n['name'], fill=(220, 0, 220), font=F)
        s = n.get('sym')
        if s:
            x, y = trm(s['c'])
            d.line([(x, y), q[0] if pr.math.dist(s['c'], n['pts'][0]) < pr.math.dist(s['c'], n['pts'][-1]) else q[-1]], fill=(255, 0, 0))
    for s in r.loose:
        x, y = trm(s['c'])
        d.rectangle((x - 5, y - 5, x + 5, y + 5), outline=(255, 0, 0), width=2)
if '--pieces' in sys.argv:
    N = json.load(open(r.work('names.json')))
    for p in r.load('pieces_cut.json')['polylines']:
        q = [trm(v) for v in r.pts_of(p)]
        if not vis(q):
            continue
        d.line(q, fill=(255, 120, 0), width=2)
        m = q[len(q) // 2]
        d.text((m[0] + 3, m[1] - 12), f"{p['id']}:{N.get(str(p['id']), '')}", fill=(200, 60, 0), font=F)
im.save(out); print(out, im.size)
