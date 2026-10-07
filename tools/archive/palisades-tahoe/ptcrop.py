"""ptcrop.py PANEL x0,y0,x1,y1 (map px) ZOOM OUT [--labels] [--pieces]: the panel's PDF rendered sharp over the box;
--labels: each printed label's glyph centres and text (printed.json) in magenta, symbols as red marks;
--pieces: the line pieces (pieces.json, or pieces_cut.json if built) with their ids."""
import importlib.util, json, sys
import pymupdf
from PIL import Image, ImageDraw, ImageFont
P = sys.argv[1]; b = list(map(float, sys.argv[2].split(','))); z = float(sys.argv[3]); out = sys.argv[4]
H = '/home/user/myskiruns/tools/trailmap/resorts/palisades-tahoe'
W = f'/home/user/myskiruns/work/palisades-tahoe/{P}'
spec = importlib.util.spec_from_file_location('r', f'{H}/panels/{P}/resort.py')
R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
pdf = {'palisades': 'palisades_main.pdf', 'alpine-front': 'alpine_front.pdf', 'alpine-back': 'alpine_back.pdf'}[P]
x0, y0 = R.CLIP[0], R.CLIP[1]
pt = lambda x, y: (x / R.SCALE + x0, y / R.SCALE + y0)  # noqa: E731
r0, r1 = pt(b[0], b[1]), pt(b[2], b[3])
page = pymupdf.open(f'/home/user/myskiruns/work/palisades-tahoe/{pdf}')[0]
pix = page.get_pixmap(matrix=pymupdf.Matrix(z, z), clip=pymupdf.Rect(*r0, *r1))
im = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
d = ImageDraw.Draw(im)
F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 12)
tr = lambda q: ((q[0] - r0[0]) * z, (q[1] - r0[1]) * z)  # noqa: E731
if '--labels' in sys.argv:
    D = json.load(open(f'{W}/printed.json'))
    for l in D['labels']:
        q = [tr(p) for p in l['pts']]
        if not any(0 <= x <= im.width and 0 <= y <= im.height for x, y in q):
            continue
        d.line(q, fill=(255, 0, 255), width=1)
        d.text((q[0][0], q[0][1] + 4), l['text'], fill=(255, 0, 255), font=F)
    for s in D['symbols']:
        x, y = tr(s['c'])
        d.rectangle((x - 3, y - 3, x + 3, y + 3), outline=(255, 0, 0))
if '--pieces' in sys.argv:
    import os
    f = f'{W}/pieces_cut.json' if os.path.exists(f'{W}/pieces_cut.json') else f'{W}/pieces.json'
    for p in json.load(open(f))['polylines']:
        q = [tr(pt(x * (R.CLIP[2] - R.CLIP[0]) * R.SCALE / 100, y * (R.CLIP[3] - R.CLIP[1]) * R.SCALE / 100)) for x, y in p['points']]
        if not any(0 <= x <= im.width and 0 <= y <= im.height for x, y in q):
            continue
        d.line(q, fill=(255, 120, 0), width=2)
        m = q[len(q) // 2]
        d.text((m[0] + 3, m[1] - 12), str(p['id']), fill=(200, 60, 0), font=F)
im.save(out); print(out, im.size)
