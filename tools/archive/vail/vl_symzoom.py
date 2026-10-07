"""vl_symzoom.py panel out.png ids... : larger crops (440x300 source px at 1.5x) around the given symbols."""
import json, sys
from PIL import Image, ImageDraw, ImageFont
Image.MAX_IMAGE_PIXELS = None
panel, out = sys.argv[1], sys.argv[2]
ids = [int(v) for v in sys.argv[3:]]
S = {s['i']: s for s in json.load(open(f'syms_{panel}.json'))}
src = Image.open(f'{panel}.png').convert('RGB')
f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 16)
hw, hh, z = 220, 150, 1.5
cw, ch = int(2 * hw * z), int(2 * hh * z)
cols = 2
sheet = Image.new('RGB', (cols * cw, ((len(ids) + cols - 1) // cols) * ch), 'white')
d = ImageDraw.Draw(sheet)
for n, i in enumerate(ids):
    x, y = S[i]['c']
    im = src.crop((int(x - hw), int(y - hh), int(x + hw), int(y + hh))).resize((cw, ch), Image.LANCZOS)
    dd = ImageDraw.Draw(im)
    r = S[i]['r'] * z + 6
    dd.ellipse((cw / 2 - r, ch / 2 - r, cw / 2 + r, ch / 2 + r), outline=(255, 0, 0), width=3)
    X, Y = (n % cols) * cw, (n // cols) * ch
    sheet.paste(im, (X, Y))
    d.rectangle((X, Y, X + cw - 1, Y + ch - 1), outline=(80, 80, 80), width=2)
    d.text((X + 6, Y + 4), f"{i} {S[i]['t']}", fill=(255, 0, 0), font=f, stroke_width=2, stroke_fill='white')
sheet.save(out); print(out, sheet.size)
