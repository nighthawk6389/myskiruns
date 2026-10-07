"""Crop helper: draw only selected pieces (thin, labelled with id) on a zoomed crop.
usage: python3 pc.py --box x0,y0,x1,y1 --zoom 3 --ids 1,2,3 --out out.png [--grid 50] [--width 2] [--dump]
--ids all  -> every piece touching the box
--dump     -> print the polylines (map px) of the selected pieces
"""
import argparse, colorsys, json
from PIL import Image, ImageDraw, ImageFont
Image.MAX_IMAGE_PIXELS = None
MAP = '/home/user/myskiruns/work/whistler-blackcomb/main/map.png'
PIECES = '/home/user/myskiruns/work/whistler-blackcomb/main/pieces_cut.json'
NAMES = '/home/user/myskiruns/work/whistler-blackcomb/main/names.json'
BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'


def colour(k):
    return tuple(int(255 * c) for c in colorsys.hsv_to_rgb((k * 0.618) % 1, 1, 0.85))


ap = argparse.ArgumentParser()
ap.add_argument('--box')
ap.add_argument('--zoom', type=float, default=3)
ap.add_argument('--ids', default='')
ap.add_argument('--out')
ap.add_argument('--grid', type=int, default=50)
ap.add_argument('--width', type=int, default=2)
ap.add_argument('--dump', action='store_true')
ap.add_argument('--names', action='store_true')
a = ap.parse_args()
img = Image.open(MAP).convert('RGB')
W, H = img.size
pieces = json.load(open(PIECES))['polylines']
names = json.load(open(NAMES))
px = {p['id']: [(q[0] * W / 100, q[1] * H / 100) for q in p['points']] for p in pieces}
cls = {p['id']: p['cls'] for p in pieces}
if a.box:
    x0, y0, x1, y1 = map(int, a.box.split(','))
    x0, y0, x1, y1 = max(0, x0), max(0, y0), min(W, x1), min(H, y1)
if a.ids == 'all':
    ids = [i for i, pts in px.items() if any(x0 <= x < x1 and y0 <= y < y1 for x, y in pts)]
else:
    ids = [int(s) for s in a.ids.split(',') if s.strip()]
if a.dump:
    for i in ids:
        pts = px[i]
        print(i, cls[i], names.get(str(i)), len(pts), ' '.join(f'({x:.0f},{y:.0f})' for x, y in pts))
if a.out:
    z = a.zoom
    im = img.crop((x0, y0, x1, y1)).resize((int((x1 - x0) * z), int((y1 - y0) * z)), Image.LANCZOS).convert('RGBA')
    ov = Image.new('RGBA', im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    f = ImageFont.truetype(BOLD, 14)
    fs = ImageFont.truetype(BOLD, 11)
    if a.grid:
        for gx in range((x0 // a.grid + 1) * a.grid, x1, a.grid):
            X = (gx - x0) * z
            d.line((X, 0, X, im.height), fill=(255, 0, 255, 60))
            d.text((X + 2, 2), str(gx), fill=(200, 0, 200, 255), font=fs, stroke_width=2, stroke_fill='white')
        for gy in range((y0 // a.grid + 1) * a.grid, y1, a.grid):
            Y = (gy - y0) * z
            d.line((0, Y, im.width, Y), fill=(255, 0, 255, 60))
            d.text((2, Y + 2), str(gy), fill=(200, 0, 200, 255), font=fs, stroke_width=2, stroke_fill='white')
    tags = []
    for i in ids:
        pts = [((x - x0) * z, (y - y0) * z) for x, y in px[i]]
        c = colour(i)
        d.line(pts, fill=c + (200,), width=a.width)
        for e in (pts[0], pts[-1]):
            d.ellipse((e[0] - 4, e[1] - 4, e[0] + 4, e[1] + 4), outline=c + (255,), width=2)
        ins = [q for q in pts if 0 <= q[0] < im.width and 0 <= q[1] < im.height]
        if ins:
            t = str(i) + (':' + names.get(str(i), '')[:14] if a.names else '')
            tags.append((ins[len(ins) // 2], t, c))
    for (x, y), t, c in tags:
        w = d.textlength(t, font=f)
        d.rectangle((x + 3, y - 9, x + w + 7, y + 9), fill=(255, 255, 160, 200))
        d.text((x + 5, y - 9), t, fill=c + (255,) if sum(c) < 500 else (0, 0, 0, 255), font=f)
    Image.alpha_composite(im, ov).convert('RGB').save(a.out)
    print(a.out, im.size)
