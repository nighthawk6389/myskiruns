"""Every extracted line piece drawn on the map (green, blue, magenta = black, orange = park; ends circled in yellow),
whole and as six zoomed quarters: to check on crops that the extraction covers every drawn trail line.

    python3 tools/trailmap/resorts/okemo/checks/pieces_overlay.py   # after regen.sh, from the repo root

Reads public/maps/okemo.jpg and $OKEMO_WORK/pieces.json (the pieces as extracted, before the split); writes
$OKEMO_WORK/pieces_overlay_full.jpg, pieces_overlay_small.jpg and q_{nw,n,ne,sw,s,se}.jpg. (Scratch inline
scripts of 2026-09-30 06:39 UTC; on those crops every drawn trail line was covered.)
"""
import collections
import json
import os

from PIL import Image, ImageDraw

Image.MAX_IMAGE_PIXELS = None
W_DIR = os.environ.get('OKEMO_WORK', 'work/okemo')

img = Image.open('public/maps/okemo.jpg').convert('RGB')
W, H = img.size
d = json.load(open(f'{W_DIR}/pieces.json'))
ov = Image.new('RGBA', img.size, (0, 0, 0, 0))
dr = ImageDraw.Draw(ov)
col = {'green': (0, 255, 0, 255), 'blue': (0, 160, 255, 255), 'black': (255, 0, 255, 255), 'freestyle': (255, 140, 0, 255)}
for p in d['polylines']:
    pts = [(x * W / 100, y * H / 100) for x, y in p['points']]
    dr.line(pts, fill=col[p['cls']], width=5)
    for e in (pts[0], pts[-1]):
        dr.ellipse((e[0] - 6, e[1] - 6, e[0] + 6, e[1] + 6), outline=(255, 255, 0, 255), width=2)
out = Image.alpha_composite(img.convert('RGBA'), ov).convert('RGB')
out.save(f'{W_DIR}/pieces_overlay_full.jpg', quality=85)
out.resize((W * 2 // 5, H * 2 // 5), Image.LANCZOS).save(f'{W_DIR}/pieces_overlay_small.jpg', quality=85)
print(collections.Counter(p['cls'] for p in d['polylines']))
lens = sorted(p['lengthPx'] for p in d['polylines'])
print('lengths', lens[:20], lens[-5:])

boxes = {'q_nw': (400, 300, 1900, 1300), 'q_n': (1500, 300, 3000, 1300), 'q_ne': (2900, 400, 4374, 1500),
         'q_sw': (900, 1100, 2400, 2200), 'q_s': (2200, 1100, 3500, 2200), 'q_se': (3300, 1300, 4374, 2400)}
for n, b in boxes.items():
    c = out.crop(b)
    s = 1100 / (b[2] - b[0])
    c.resize((int(c.width * s), int(c.height * s)), Image.LANCZOS).save(f'{W_DIR}/{n}.jpg', quality=88)
print('wrote', ', '.join(f'{W_DIR}/{n}.jpg' for n in boxes))
