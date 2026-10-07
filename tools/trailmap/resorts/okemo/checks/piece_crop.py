"""Crop the lossless map around given pieces, drawing each in its own colour with its id.

    python3 tools/trailmap/resorts/okemo/checks/piece_crop.py OUT.jpg 'id,id;id' [pad]   # from the repo root

Groups separated by ';' get different colours. Reads $OKEMO_WORK/okemo_source.png (regen.sh) and
src/data/resorts/okemo/linePolylines.json. (Scratch piece_crop.py of 2026-09-30: the crops that settled
piece 239 as an unnamed spur, the two Tomahawks, the roads' boundaries, Homeward Bound / Kettle Brook,
Turkey Shoot's split of 210 and Sunset Strip, e.g. '239;117,118;254,255;136,137;115,116' 150,
'210;238;62;60,61' 60.)
"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

Image.MAX_IMAGE_PIXELS = None
img = Image.open(os.environ.get('OKEMO_WORK', 'work/okemo') + '/okemo_source.png').convert('RGB')
W, H = img.size
polys = {p['id']: [(x * W / 100, y * H / 100) for x, y in p['points']]
         for p in json.load(open('src/data/resorts/okemo/linePolylines.json'))['polylines']}
groups = [[int(v) for v in g.split(',') if v] for g in sys.argv[2].split(';')]
pad = int(sys.argv[3]) if len(sys.argv) > 3 else 120
pts = [q for g in groups for i in g for q in polys[i]]
x0, y0 = max(0, min(q[0] for q in pts) - pad), max(0, min(q[1] for q in pts) - pad)
x1, y1 = min(W, max(q[0] for q in pts) + pad), min(H, max(q[1] for q in pts) + pad)
s = min(2.0, 1300 / max(x1 - x0, y1 - y0))
crop = img.crop((int(x0), int(y0), int(x1), int(y1))).resize((int((x1 - x0) * s), int((y1 - y0) * s)),
                                                            Image.LANCZOS).convert('RGBA')
ov = Image.new('RGBA', crop.size)
d = ImageDraw.Draw(ov)
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 16)
cols = [(255, 0, 255, 200), (0, 200, 255, 200), (255, 140, 0, 220), (0, 220, 0, 220), (255, 255, 0, 220)]
for gi, g in enumerate(groups):
    for i in g:
        q = [((x - x0) * s, (y - y0) * s) for x, y in polys[i]]
        d.line(q, fill=cols[gi % 5], width=3)
        m = q[len(q) // 2]
        d.rectangle((m[0], m[1], m[0] + 34, m[1] + 18), fill=(255, 255, 255, 220))
        d.text((m[0] + 2, m[1]), str(i), fill=(0, 0, 0, 255), font=font)
Image.alpha_composite(crop, ov).convert('RGB').save(sys.argv[1], quality=88)
print(sys.argv[1], crop.size, 'scale', round(s, 2), 'origin', int(x0), int(y0))
