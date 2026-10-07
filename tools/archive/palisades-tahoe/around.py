"""around.py PANEL OUT x,y[,label] ... [--r 60] [--z 4]: a sheet of crops (map px centres, radius r map px) with
labels and symbols drawn (ptcrop.py's style), each captioned."""
import importlib.util, json, sys
import pymupdf
from PIL import Image, ImageDraw, ImageFont
P, out = sys.argv[1], sys.argv[2]
args = [a for a in sys.argv[3:] if not a.startswith('--')]
r = float(sys.argv[sys.argv.index('--r') + 1]) if '--r' in sys.argv else 60
z = float(sys.argv[sys.argv.index('--z') + 1]) if '--z' in sys.argv else 4
args = [a for a in args if a not in (str(r), str(z)) and not a.replace('.', '').isdigit()]
H = '/home/user/myskiruns/tools/trailmap/resorts/palisades-tahoe'
W = f'/home/user/myskiruns/work/palisades-tahoe/{P}'
spec = importlib.util.spec_from_file_location('r', f'{H}/panels/{P}/resort.py')
R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
pdf = {'palisades': 'palisades_main.pdf', 'alpine-front': 'alpine_front.pdf', 'alpine-back': 'alpine_back.pdf'}[P]
page = pymupdf.open(f'/home/user/myskiruns/work/palisades-tahoe/{pdf}')[0]
D = json.load(open(f'{W}/printed.json'))
F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 12)
x0, y0 = R.CLIP[0], R.CLIP[1]
cells = []
for a in args:
    xy, _, cap = a.partition(':')
    cx, cy = map(float, xy.split(','))
    p0 = (cx / R.SCALE + x0 - r / R.SCALE, cy / R.SCALE + y0 - r / R.SCALE)
    p1 = (cx / R.SCALE + x0 + r / R.SCALE, cy / R.SCALE + y0 + r / R.SCALE)
    pix = page.get_pixmap(matrix=pymupdf.Matrix(z, z), clip=pymupdf.Rect(*p0, *p1))
    im = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
    d = ImageDraw.Draw(im)
    tr = lambda q: ((q[0] - p0[0]) * z, (q[1] - p0[1]) * z)  # noqa: E731
    for s in D['symbols']:
        x, y = tr(s['c'])
        if 0 <= x <= im.width and 0 <= y <= im.height:
            d.rectangle((x - 4, y - 4, x + 4, y + 4), outline=(255, 0, 0), width=2)
    for l in D['labels']:
        q = [tr(p) for p in l['pts']]
        if any(0 <= x <= im.width and 0 <= y <= im.height for x, y in q):
            d.line(q, fill=(255, 0, 255), width=1)
    cell = Image.new('RGB', (im.width, im.height + 18), 'white'); cell.paste(im, (0, 18))
    ImageDraw.Draw(cell).text((3, 2), cap or xy, fill='black', font=F)
    cells.append(cell)
cols = 4
cw = max(c.width for c in cells); ch = max(c.height for c in cells)
sheet = Image.new('RGB', (cols * (cw + 6), ((len(cells) + cols - 1) // cols) * (ch + 6)), (90, 90, 90))
for i, c in enumerate(cells):
    sheet.paste(c, ((i % cols) * (cw + 6), (i // cols) * (ch + 6)))
sheet.save(out); print(out, sheet.size)
