"""vl_dsheet.py out.png: every diamond / double-diamond symbol on the three panels, cropped around its centre and
scaled to one size, tagged with panel, index, detected type and the name read for it."""
import json
from PIL import Image, ImageDraw, ImageFont
Image.MAX_IMAGE_PIXELS = None
exec(open('vl_symnames.py').read())
f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 11)
cells = []
for panel, ab in (('front-side', 'F'), ('back-bowls', 'B'), ('blue-sky', 'S')):
    src = Image.open(f'{panel}.png').convert('RGB')
    for s in json.load(open(f'syms_{panel}.json')):
        if 'diamond' not in s['t']:
            continue
        x, y = s['c']; r = s['r'] * (2.2 if s['t'] == 'diamond' else 1.3)
        c = src.crop((int(x - r), int(y - r), int(x + r), int(y + r))).resize((110, 110), Image.LANCZOS)
        n = NAMES[panel].get(s['i'])
        cells.append((c, f"{ab}{s['i']} {'DD' if s['t'] == 'double-diamond' else 'D'}", (n or '-')[:16]))
cols = 12
W, H = 120, 145
sheet = Image.new('RGB', (cols * W, ((len(cells) + cols - 1) // cols) * H), 'white')
d = ImageDraw.Draw(sheet)
for k, (c, t1, t2) in enumerate(cells):
    X, Y = (k % cols) * W + 5, (k // cols) * H + 2
    sheet.paste(c, (X, Y))
    d.text((X, Y + 112), t1, fill=(200, 0, 0) if 'DD' in t1 else (0, 0, 0), font=f)
    d.text((X, Y + 125), t2, fill=(60, 60, 60), font=f)
sheet.save('d_sheet.png'); print(len(cells), sheet.size)
