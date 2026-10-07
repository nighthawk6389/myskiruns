"""namegrid.py PANEL OUT name[,name..] [--m 90] [--z 3]: one cell per printed name (every copy): the PDF rendered
sharp around it, line pieces thin with id:name, the name magenta."""
import contextlib, io, json, sys
import pymupdf
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, '/home/user/myskiruns/tools/trailmap')
import pdf_resort as pr
P, out, want = sys.argv[1], sys.argv[2], sys.argv[3].split(',')
m = float(sys.argv[sys.argv.index('--m') + 1]) if '--m' in sys.argv else 90
z = float(sys.argv[sys.argv.index('--z') + 1]) if '--z' in sys.argv else 3
PDF = {'main': 'bigsky_main.pdf', 'south-face': 'bigsky_south-face.pdf', 'bowl': 'bigsky_bowl.pdf'}[P]
r = pr.Resort(f'big-sky/{P}')
with contextlib.redirect_stdout(io.StringIO()):
    r.build()
R = r.R; x0, y0 = R.CLIP[0], R.CLIP[1]
page = pymupdf.open(f'/home/user/myskiruns/work/big-sky/{PDF}')[0]
N = json.load(open(r.work('names.json')))
pieces = {p['id']: r.pts_of(p) for p in r.P}
F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 11)
cells = []
for n in r.names_all:
    if n['name'] not in want:
        continue
    xs = [p[0] for p in n['pts']]; ys = [p[1] for p in n['pts']]
    bx = (min(xs) - m, min(ys) - m, max(xs) + m, max(ys) + m)
    clip = pymupdf.Rect(bx[0] / R.SCALE + x0, bx[1] / R.SCALE + y0, bx[2] / R.SCALE + x0, bx[3] / R.SCALE + y0)
    pix = page.get_pixmap(matrix=pymupdf.Matrix(z, z), clip=clip)
    im = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
    d = ImageDraw.Draw(im)
    k = z / R.SCALE
    T = lambda q: ((q[0] - bx[0]) * k, (q[1] - bx[1]) * k)  # noqa: E731
    for i, pts in pieces.items():
        if any(bx[0] <= x <= bx[2] and bx[1] <= y <= bx[3] for x, y in pts):
            d.line([T(q) for q in pts], fill=(255, 120, 0), width=1)
            mid = T(pts[len(pts) // 2])
            d.text(mid, f'{i}:{N.get(str(i))}', fill=(200, 60, 0), font=F)
    d.line([T(q) for q in n['pts']] if len(n['pts']) > 1 else [T(n['pts'][0]), T(n['pts'][0])], fill=(255, 0, 255), width=2)
    if n.get('sym'):
        c = T(n['sym']['c']); d.ellipse([c[0] - 5, c[1] - 5, c[0] + 5, c[1] + 5], outline=(255, 0, 0), width=2)
    hdr = Image.new('RGB', (im.width, 18), 'white')
    ImageDraw.Draw(hdr).text((3, 2), f"{n['name']} [{n.get('symbol')}] at ({xs[0]:.0f},{ys[0]:.0f})", fill=(180, 0, 0), font=F)
    c = Image.new('RGB', (im.width, im.height + 18), 'white'); c.paste(hdr, (0, 0)); c.paste(im, (0, 18))
    cells.append(c)
W = 2
cw = max(c.width for c in cells); ch = max(c.height for c in cells)
sheet = Image.new('RGB', (W * cw + (W - 1) * 6, ((len(cells) + W - 1) // W) * (ch + 6)), (90, 90, 90))
for i, c in enumerate(cells):
    sheet.paste(c, ((i % W) * (cw + 6), (i // W) * (ch + 6)))
sheet.save(out); print(out, sheet.size, len(cells))
