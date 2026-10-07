"""look.py OUT id[,id...] [--margin 60] [--zoom 3]: one crop around the given pieces (map px), plain on top and with
the pieces drawn below: the given ones thick red with ids, the others thin in their colour with id:name."""
import json, sys
from PIL import Image, ImageDraw, ImageFont
Image.MAX_IMAGE_PIXELS = None
W = '/home/user/myskiruns/work/park-city'
out = sys.argv[1]; ids = [int(v) for v in sys.argv[2].split(',')]
margin = float(sys.argv[sys.argv.index('--margin') + 1]) if '--margin' in sys.argv else 60
zoom = float(sys.argv[sys.argv.index('--zoom') + 1]) if '--zoom' in sys.argv else None
base = Image.open(f'{W}/map.png').convert('RGB'); WW, HH = base.size
P = json.load(open(f'{W}/pieces_cut.json'))['polylines']; N = json.load(open(f'{W}/names.json'))
pts = {p['id']: [(x * WW / 100, y * HH / 100) for x, y in p['points']] for p in P}
xs = [q[0] for i in ids for q in pts[i]]; ys = [q[1] for i in ids for q in pts[i]]
box = (int(max(0, min(xs) - margin)), int(max(0, min(ys) - margin)), int(min(WW, max(xs) + margin)), int(min(HH, max(ys) + margin)))
z = zoom or min(4.0, 900 / max(box[2] - box[0], box[3] - box[1]))
plain = base.crop(box).resize((int((box[2] - box[0]) * z), int((box[3] - box[1]) * z)), Image.LANCZOS)
im = plain.copy(); d = ImageDraw.Draw(im)
F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 13)
F2 = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 11)
col = {'green': (0, 150, 60), 'blue': (0, 110, 230), 'black': (40, 40, 40), 'freestyle': (240, 140, 0)}
tr = lambda q: ((q[0] - box[0]) * z, (q[1] - box[1]) * z)  # noqa: E731
vis = [p for p in P if any(0 <= x <= im.width and 0 <= y <= im.height for x, y in (tr(v) for v in pts[p['id']]))]
for p in vis:
    q = [tr(v) for v in pts[p['id']]]
    if p['id'] in ids:
        d.line(q, fill=(255, 0, 0), width=4)
        for e in (q[0], q[-1]):
            d.ellipse((e[0] - 5, e[1] - 5, e[0] + 5, e[1] + 5), outline=(255, 0, 0), width=2)
    else:
        d.line(q, fill=col.get(p['cls'], (128, 0, 128)), width=2)
for p in vis:
    q = [tr(v) for v in pts[p['id']]]; m = q[len(q) // 2]
    nm = N.get(str(p['id']), '?')
    if p['id'] in ids:
        d.text((m[0] + 6, m[1] - 9), f"{p['id']}", fill=(255, 255, 255), font=F, stroke_width=3, stroke_fill=(200, 0, 0))
    elif not nm.endswith('~'):
        d.text((m[0] + 3, m[1] - 6), f"{p['id']}:{nm}", fill=(0, 0, 0), font=F2, stroke_width=2, stroke_fill=(255, 255, 210))
o = Image.new('RGB', (im.width, im.height * 2 + 8), 'gray'); o.paste(plain, (0, 0)); o.paste(im, (0, im.height + 8)); o.save(out)
print(out, o.size, 'box', box, 'zoom', round(z, 2))
