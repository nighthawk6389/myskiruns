"""Render a zoomed crop: top/left = plain, other = selected pieces drawn thin (so the map line stays visible).
usage: python3 hl.py x0,y0,x1,y1 zoom out.png id1 id2 ...   (ids optional; 'all' = every piece in box)
"""
import json
import sys
import colorsys
from PIL import Image, ImageDraw, ImageFont

Image.MAX_IMAGE_PIXELS = None
MAP = '/home/user/myskiruns/work/whistler-blackcomb/main/map.png'
PCS = '/home/user/myskiruns/work/whistler-blackcomb/main/pieces_cut.json'
NMS = '/home/user/myskiruns/work/whistler-blackcomb/main/names.json'
BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'


def colour(k):
    return tuple(int(255 * c) for c in colorsys.hsv_to_rgb((k * 0.618) % 1, 1, 0.85))


box = list(map(int, sys.argv[1].split(',')))
z = float(sys.argv[2])
out = sys.argv[3]
ids = sys.argv[4:]
img = Image.open(MAP).convert('RGB')
W, H = img.size
x0, y0, x1, y1 = box
x0, y0, x1, y1 = max(0, x0), max(0, y0), min(W, x1), min(H, y1)
crop = img.crop((x0, y0, x1, y1)).resize((int((x1 - x0) * z), int((y1 - y0) * z)), Image.LANCZOS)
pieces = json.load(open(PCS))['polylines']
names = json.load(open(NMS))
f = ImageFont.truetype(BOLD, 13)
fs = ImageFont.truetype(BOLD, 11)


def to_crop(q):
    return ((q[0] * W / 100 - x0) * z, (q[1] * H / 100 - y0) * z)


ov = crop.copy().convert('RGBA')
lay = Image.new('RGBA', ov.size, (0, 0, 0, 0))
d = ImageDraw.Draw(lay)
# grid
step = 50 if (x1 - x0) <= 500 else 100
for gx in range((x0 // step + 1) * step, x1, step):
    X = (gx - x0) * z
    d.line((X, 0, X, ov.height), fill=(255, 0, 255, 70))
    d.text((X + 2, 2), str(gx), fill=(200, 0, 200, 255), font=fs, stroke_width=2, stroke_fill='white')
for gy in range((y0 // step + 1) * step, y1, step):
    Y = (gy - y0) * z
    d.line((0, Y, ov.width, Y), fill=(255, 0, 255, 70))
    d.text((2, Y + 2), str(gy), fill=(200, 0, 200, 255), font=fs, stroke_width=2, stroke_fill='white')
tags = []
sel = [p for p in pieces if (ids == ['all'] or str(p['id']) in ids)]
for p in sel:
    pts = [to_crop(q) for q in p['points']]
    ins = [q for q in pts if 0 <= q[0] < ov.width and 0 <= q[1] < ov.height]
    if not ins:
        continue
    c = colour(p['id'])
    d.line(pts, fill=c + (200,), width=2)
    for e in (pts[0], pts[-1]):
        d.ellipse((e[0] - 5, e[1] - 5, e[0] + 5, e[1] + 5), outline=c + (255,), width=2)
    nm = names.get(str(p['id']), '?')
    tags.append((ins[len(ins) // 2], f"{p['id']}:{nm[:18]}", c))
for (x, y), t, c in tags:
    w = d.textlength(t, font=f)
    d.rectangle((x + 6, y - 8, x + w + 10, y + 8), fill=(255, 255, 160, 200))
    d.text((x + 8, y - 8), t, fill=c + (255,) if sum(c) < 500 else (0, 0, 0, 255), font=f)
ov = Image.alpha_composite(ov, lay).convert('RGB')
# plain with grid
pl = crop.copy().convert('RGBA')
lay2 = Image.new('RGBA', pl.size, (0, 0, 0, 0))
d2 = ImageDraw.Draw(lay2)
for gx in range((x0 // step + 1) * step, x1, step):
    X = (gx - x0) * z
    d2.line((X, 0, X, pl.height), fill=(255, 0, 255, 40))
    d2.text((X + 2, 2), str(gx), fill=(200, 0, 200, 255), font=fs, stroke_width=2, stroke_fill='white')
for gy in range((y0 // step + 1) * step, y1, step):
    Y = (gy - y0) * z
    d2.line((0, Y, pl.width, Y), fill=(255, 0, 255, 40))
    d2.text((2, Y + 2), str(gy), fill=(200, 0, 200, 255), font=fs, stroke_width=2, stroke_fill='white')
pl = Image.alpha_composite(pl, lay2).convert('RGB')
if ids:
    if pl.width >= pl.height:
        canvas = Image.new('RGB', (pl.width, pl.height * 2 + 6), 'white')
        canvas.paste(pl, (0, 0))
        canvas.paste(ov, (0, pl.height + 6))
    else:
        canvas = Image.new('RGB', (pl.width * 2 + 6, pl.height), 'white')
        canvas.paste(pl, (0, 0))
        canvas.paste(ov, (pl.width + 6, 0))
else:
    canvas = pl
canvas.save(out)
print(out, canvas.size)
