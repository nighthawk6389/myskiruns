"""vl_symsheet.py panel start count out.png: contact sheet of symbol crops (symbol circled in red, index on top)."""
import json, sys
from PIL import Image, ImageDraw, ImageFont
Image.MAX_IMAGE_PIXELS = None
K = {'front-side': 1.1, 'back-bowls': 1.5, 'blue-sky': 3.0}
panel, start, count, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
k = K[panel]
S = json.load(open(f'syms_{panel}.json'))[start:start + count]
src = Image.open(f'{panel}.png').convert('RGB')
cw, ch = 340, 230          # cell size in output px
half_w, half_h = 160 * k, 108 * k   # source half-window
f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 15)
cols = 5
rows = (len(S) + cols - 1) // cols
sheet = Image.new('RGB', (cols * cw, rows * ch), 'white')
d = ImageDraw.Draw(sheet)
for n, s in enumerate(S):
    x, y = s['c']
    box = (int(x - half_w), int(y - half_h), int(x + half_w), int(y + half_h))
    im = src.crop(box).resize((cw - 4, ch - 4), Image.LANCZOS)
    dd = ImageDraw.Draw(im)
    sx = (x - box[0]) / (box[2] - box[0]) * (cw - 4); sy = (y - box[1]) / (box[3] - box[1]) * (ch - 4)
    rr = s['r'] / (box[2] - box[0]) * (cw - 4) + 5
    dd.ellipse((sx - rr, sy - rr, sx + rr, sy + rr), outline=(255, 0, 0), width=2)
    X, Y = (n % cols) * cw, (n // cols) * ch
    sheet.paste(im, (X + 2, Y + 2))
    d.rectangle((X, Y, X + cw - 1, Y + ch - 1), outline=(120, 120, 120))
    t = f"{s['i']} {s['t'][:3] if s['t'] != 'double-diamond' else 'DBL'}"
    d.text((X + 6, Y + 4), t, fill=(255, 0, 0), font=f, stroke_width=2, stroke_fill='white')
sheet.save(out)
print(out, sheet.size)
