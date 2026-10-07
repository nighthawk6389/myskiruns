"""pieces_view.py PANEL OUT [zoom] [x0,y0,x1,y1]: the panel's pieces (pieces.json) drawn over its map, ids at mid."""
import json, sys
from PIL import Image, ImageDraw, ImageFont
Image.MAX_IMAGE_PIXELS = None
P, out = sys.argv[1], sys.argv[2]
z = float(sys.argv[3]) if len(sys.argv) > 3 else 0.4
W = f'/home/user/myskiruns/work/big-sky/{P}'
im = Image.open(f'{W}/map.png').convert('RGB')
w, h = im.size
box = tuple(map(int, sys.argv[4].split(','))) if len(sys.argv) > 4 else (0, 0, w, h)
im = im.crop(box)
im = im.resize((int(im.width * z), int(im.height * z)), Image.LANCZOS)
d = ImageDraw.Draw(im, 'RGBA')
F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 11)
C = {'green': (0, 200, 0, 200), 'blue': (0, 90, 255, 200), 'black': (255, 0, 200, 200), 'freestyle': (255, 140, 0, 220)}
for p in json.load(open(f'{W}/pieces.json'))['polylines']:
    pts = [((x * w / 100 - box[0]) * z, (y * h / 100 - box[1]) * z) for x, y in p['points']]
    d.line(pts, fill=C[p['cls']], width=3)
    m = pts[len(pts) // 2]
    d.text((m[0] + 2, m[1] - 6), str(p['id']), fill=(0, 0, 0), font=F, stroke_width=2, stroke_fill=(255, 255, 255))
for s in json.load(open(f'{W}/symbols.json')):
    x, y = (s['src'][0] - box[0]) * z, (s['src'][1] - box[1]) * z
    col = {'circle': (0, 160, 0), 'square': (0, 80, 255), 'diamond': (0, 0, 0), 'double-diamond': (255, 0, 0)}[s['type']]
    d.ellipse((x - 6, y - 6, x + 6, y + 6), outline=col, width=2)
im.save(out)
print(out, im.size)
