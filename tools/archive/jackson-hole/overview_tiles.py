"""All of a resort's overlays (trailPaths.json) drawn on its map with names, in tiles."""
import json, sys
from PIL import Image, ImageDraw, ImageFont
rid, out, tw, th = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
X0, Y0, X1, Y1 = map(int, sys.argv[5].split(','))
im = Image.open(f'public/maps/{rid}.jpg').convert('RGB')
W, H = im.size
fade = Image.blend(im, Image.new('RGB', im.size, (255, 255, 255)), 0.4)
d = ImageDraw.Draw(fade)
f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 12)
P = json.load(open(f'src/data/resorts/{rid}/trailPaths.json'))['trails']
import itertools
cols = itertools.cycle([(230, 0, 120), (0, 120, 230), (0, 150, 60), (200, 100, 0), (120, 0, 200), (0, 0, 0)])
for tid, v in P.items():
    c = next(cols)
    for seg in v.get('segments', []):
        pts = [(x * W / 100, y * H / 100) for x, y in seg]
        if len(pts) == 1:
            x, y = pts[0]; d.ellipse((x - 6, y - 6, x + 6, y + 6), outline=c, width=3)
        else:
            d.line(pts, fill=c, width=3)
        m = pts[len(pts) // 2]
        d.text((m[0] + 5, m[1] - 6), tid, fill=c, font=f, stroke_width=2, stroke_fill='white')
k = 0
for y in range(Y0, Y1, th):
    for x in range(X0, X1, tw):
        fade.crop((x, y, x + tw, y + th)).save(f'{out}_{k}_{x}_{y}.png'); k += 1
