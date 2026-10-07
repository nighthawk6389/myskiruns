"""vl_grid.py panel out.png x0,y0,x1,y1 [zoom]: the panel with a labelled 100 px grid and every named symbol tagged
with its name (from vl_symnames.py), to list the labels that have no symbol and read their positions."""
import json, sys
from PIL import Image, ImageDraw, ImageFont
Image.MAX_IMAGE_PIXELS = None
exec(open('vl_symnames.py').read())
panel, out = sys.argv[1], sys.argv[2]
x0, y0, x1, y1 = map(int, sys.argv[3].split(','))
z = float(sys.argv[4]) if len(sys.argv) > 4 else 1.0
src = Image.open(f'{panel}.png').convert('RGB')
im = src.crop((x0, y0, x1, y1)).resize((int((x1 - x0) * z), int((y1 - y0) * z)), Image.LANCZOS)
d = ImageDraw.Draw(im, 'RGBA')
f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 12)
for gx in range((x0 // 100 + 1) * 100, x1, 100):
    X = (gx - x0) * z
    d.line((X, 0, X, im.height), fill=(255, 0, 255, 90), width=1)
    d.text((X + 2, 2), str(gx), fill=(200, 0, 200), font=f, stroke_width=2, stroke_fill='white')
for gy in range((y0 // 100 + 1) * 100, y1, 100):
    Y = (gy - y0) * z
    d.line((0, Y, im.width, Y), fill=(255, 0, 255, 90), width=1)
    d.text((2, Y + 2), str(gy), fill=(200, 0, 200), font=f, stroke_width=2, stroke_fill='white')
S = json.load(open(f'syms_{panel}.json'))
for s in S:
    n = NAMES.get(panel, {}).get(s['i'])
    x, y = (s['c'][0] - x0) * z, (s['c'][1] - y0) * z
    if not (0 <= x < im.width and 0 <= y < im.height):
        continue
    t = f"#{s['i']}" + (f" {n}" if n else ' -')
    d.text((x + 8, y + 6), t, fill=(220, 0, 0), font=f, stroke_width=2, stroke_fill='white')
im.save(out); print(out, im.size)
