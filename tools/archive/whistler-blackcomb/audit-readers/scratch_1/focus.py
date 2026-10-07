"""Focused crop: plain crop (left/top) and the same crop with ONLY the target trail's overlay drawn thin
(magenta, semi-transparent, ends circled) plus other overlays as faint thin cyan lines tagged with names.

python3 focus.py PANEL TRAIL x0,y0,x1,y1 ZOOM OUT [--stack] [--others]
"""
import json
import re
import sys

from PIL import Image, ImageDraw, ImageFont

Image.MAX_IMAGE_PIXELS = None
ROOT = '/home/user/myskiruns'
BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'

panel, trail, box, zoom, out = sys.argv[1:6]
flags = sys.argv[6:]
stack = '--stack' in flags
others = '--others' in flags
img = Image.open(f'{ROOT}/work/whistler-blackcomb/{panel}/map.png').convert('RGB')
W, H = img.size
paths = json.load(open(f'{ROOT}/src/data/resorts/whistler-blackcomb/panels/{panel}/trailPaths.json'))['trails']
tnames = {m.group(1): m.group(2).strip('"\'') for m in re.finditer(
    r"id: '([^']+)', name: (\"[^\"]+\"|'[^']+')", open(f'{ROOT}/src/data/resorts/whistler-blackcomb/trails.ts').read())}
x0, y0, x1, y1 = map(int, box.split(','))
x0, y0, x1, y1 = max(0, x0), max(0, y0), min(W, x1), min(H, y1)
z = float(zoom)
base = img.crop((x0, y0, x1, y1)).resize((int((x1 - x0) * z), int((y1 - y0) * z)), Image.LANCZOS).convert('RGBA')
f = ImageFont.truetype(BOLD, 12)


def to_crop(q):
    return ((q[0] * W / 100 - x0) * z, (q[1] * H / 100 - y0) * z)


def grid(d, im):
    step = 50 if (x1 - x0) > 200 else 25
    for gx in range((x0 // step + 1) * step, x1, step):
        X = (gx - x0) * z
        d.line((X, 0, X, im.height), fill=(255, 0, 255, 60))
        d.text((X + 2, 2), str(gx), fill=(200, 0, 200, 255), font=f, stroke_width=2, stroke_fill='white')
    for gy in range((y0 // step + 1) * step, y1, step):
        Y = (gy - y0) * z
        d.line((0, Y, im.width, Y), fill=(255, 0, 255, 60))
        d.text((2, Y + 2), str(gy), fill=(200, 0, 200, 255), font=f, stroke_width=2, stroke_fill='white')


plain = base.copy()
ov = Image.new('RGBA', base.size, (0, 0, 0, 0))
d = ImageDraw.Draw(ov)
grid(d, base)
plain = Image.alpha_composite(plain, ov)

ov2 = Image.new('RGBA', base.size, (0, 0, 0, 0))
d2 = ImageDraw.Draw(ov2)
grid(d2, base)
tags = []
if others:
    for tid, p in paths.items():
        if tid == trail:
            continue
        for seg in p.get('segments', []):
            pts = [to_crop(q) for q in seg]
            d2.line(pts, fill=(0, 200, 255, 150), width=1)
            ins = [q for q in pts if 0 <= q[0] < base.width and 0 <= q[1] < base.height]
            if ins:
                tags.append((ins[len(ins) // 2], tnames.get(tid, tid)))
        if p.get('label'):
            x, y = to_crop(p['label'])
            d2.ellipse((x - 6, y - 6, x + 6, y + 6), outline=(0, 200, 255, 200), width=2)
            tags.append(((x, y), tnames.get(tid, tid)))
p = paths.get(trail, {})
for seg in p.get('segments', []):
    pts = [to_crop(q) for q in seg]
    d2.line(pts, fill=(255, 0, 200, 170), width=2)
    for q in pts:
        d2.ellipse((q[0] - 1.5, q[1] - 1.5, q[0] + 1.5, q[1] + 1.5), fill=(255, 0, 200, 220))
    for e in (pts[0], pts[-1]):
        d2.ellipse((e[0] - 6, e[1] - 6, e[0] + 6, e[1] + 6), outline=(255, 0, 0, 255), width=2)
if p.get('label'):
    x, y = to_crop(p['label'])
    d2.ellipse((x - 10, y - 10, x + 10, y + 10), outline=(255, 0, 200, 255), width=3)
for (x, y), t in tags:
    w = d2.textlength(t, font=f)
    d2.rectangle((x + 3, y - 7, x + w + 7, y + 7), fill=(255, 255, 200, 170))
    d2.text((x + 5, y - 7), t, fill=(0, 90, 140, 255), font=f)
over = Image.alpha_composite(base, ov2)
if stack:
    outim = Image.new('RGB', (base.width, base.height * 2 + 6), 'white')
    outim.paste(plain.convert('RGB'), (0, 0))
    outim.paste(over.convert('RGB'), (0, base.height + 6))
else:
    outim = Image.new('RGB', (base.width * 2 + 6, base.height), 'white')
    outim.paste(plain.convert('RGB'), (0, 0))
    outim.paste(over.convert('RGB'), (base.width + 6, 0))
outim.save(out)
print(out, outim.size)
