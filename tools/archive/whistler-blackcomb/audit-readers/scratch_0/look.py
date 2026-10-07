"""Crop a map region; draw one trail's overlay thinly (so the drawn line under it stays visible).

python3 look.py PANEL x0,y0,x1,y1 ZOOM TRAIL OUT [--plain] [--others]
Writes OUT (png). With --plain, no overlay at all. With --others, other trails' overlays thin cyan with names.
Grid every 50 px (labelled), faint every 10.
"""
import json
import re
import sys

from PIL import Image, ImageDraw, ImageFont

Image.MAX_IMAGE_PIXELS = None
ROOT = '/home/user/myskiruns'
BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'

panel, box, zoom, trail, out = sys.argv[1:6]
flags = sys.argv[6:]
x0, y0, x1, y1 = map(int, box.split(','))
z = float(zoom)
img = Image.open(f'{ROOT}/work/whistler-blackcomb/{panel}/map.png').convert('RGB')
W, H = img.size
x0, y0, x1, y1 = max(0, x0), max(0, y0), min(W, x1), min(H, y1)
im = img.crop((x0, y0, x1, y1)).resize((int((x1 - x0) * z), int((y1 - y0) * z)), Image.LANCZOS).convert('RGBA')
ov = Image.new('RGBA', im.size, (0, 0, 0, 0))
d = ImageDraw.Draw(ov)
fs = ImageFont.truetype(BOLD, 11)
f = ImageFont.truetype(BOLD, 12)
for step, alpha, label in ((10, 25, False), (50, 90, True)):
    for gx in range((x0 // step + 1) * step, x1, step):
        X = (gx - x0) * z
        d.line((X, 0, X, im.height), fill=(255, 0, 255, alpha))
        if label:
            d.text((X + 2, 2), str(gx), fill=(200, 0, 200, 255), font=fs, stroke_width=2, stroke_fill='white')
    for gy in range((y0 // step + 1) * step, y1, step):
        Y = (gy - y0) * z
        d.line((0, Y, im.width, Y), fill=(255, 0, 255, alpha))
        if label:
            d.text((2, Y + 2), str(gy), fill=(200, 0, 200, 255), font=fs, stroke_width=2, stroke_fill='white')

paths = json.load(open(f'{ROOT}/src/data/resorts/whistler-blackcomb/panels/{panel}/trailPaths.json'))['trails']
tnames = {m.group(1): m.group(2).strip('"\'') for m in re.finditer(
    r"id: '([^']+)', name: (\"[^\"]+\"|'[^']+')", open(f'{ROOT}/src/data/resorts/whistler-blackcomb/trails.ts').read())}


def to_crop(q):
    return ((q[0] * W / 100 - x0) * z, (q[1] * H / 100 - y0) * z)


tags = []
if '--plain' not in flags:
    if '--others' in flags:
        for tid, p in paths.items():
            if tid == trail:
                continue
            for seg in p.get('segments', []):
                pts = [to_crop(q) for q in seg]
                d.line(pts, fill=(0, 200, 255, 200), width=1)
                ins = [q for q in pts if 0 <= q[0] < im.width and 0 <= q[1] < im.height]
                if ins:
                    tags.append((ins[len(ins) // 2], tnames.get(tid, tid)))
            if p.get('label'):
                x, y = to_crop(p['label'])
                d.ellipse((x - 6, y - 6, x + 6, y + 6), outline=(0, 200, 255, 255), width=2)
                tags.append(((x, y), tnames.get(tid, tid)))
    p = paths.get(trail, {})
    for seg in p.get('segments', []):
        pts = [to_crop(q) for q in seg]
        d.line(pts, fill=(255, 0, 0, 200), width=2)
        for e in (pts[0], pts[-1]):
            d.ellipse((e[0] - 5, e[1] - 5, e[0] + 5, e[1] + 5), outline=(255, 0, 0, 255), width=2)
        for q in pts[1:-1]:
            d.ellipse((q[0] - 1.5, q[1] - 1.5, q[0] + 1.5, q[1] + 1.5), fill=(255, 0, 0, 255))
    if p.get('label'):
        x, y = to_crop(p['label'])
        d.ellipse((x - 10, y - 10, x + 10, y + 10), outline=(255, 0, 0, 255), width=3)
for (x, y), t in tags:
    d.text((x + 4, y - 6), t, fill=(0, 90, 160, 255), font=f, stroke_width=2, stroke_fill='white')
Image.alpha_composite(im, ov).convert('RGB').save(out)
print(out, im.size)
