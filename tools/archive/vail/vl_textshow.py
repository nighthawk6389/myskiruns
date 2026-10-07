"""vl_textshow.py panel out.png x0,y0,x1,y1 [zoom]: each label's glyph chain (dots) and its end (circle)."""
import json, sys, colorsys
from PIL import Image, ImageDraw, ImageFont
Image.MAX_IMAGE_PIXELS = None
exec(open('vl_symnames.py').read())
panel, out = sys.argv[1], sys.argv[2]
x0, y0, x1, y1 = map(int, sys.argv[3].split(','))
z = float(sys.argv[4]) if len(sys.argv) > 4 else 1
T = json.load(open(f'text_{panel}.json'))
im = Image.open(f'{panel}.png').convert('RGB').crop((x0, y0, x1, y1)).resize((int((x1 - x0) * z), int((y1 - y0) * z)))
d = ImageDraw.Draw(im)
f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 12)
for k, (i, t) in enumerate(T.items()):
    col = tuple(int(255 * c) for c in colorsys.hsv_to_rgb((k * 0.618) % 1, 1, 0.9))
    for x, y in t['pts']:
        X, Y = (x - x0) * z, (y - y0) * z
        d.ellipse((X - 3, Y - 3, X + 3, Y + 3), fill=col)
    X, Y = (t['end'][0] - x0) * z, (t['end'][1] - y0) * z
    d.ellipse((X - 9, Y - 9, X + 9, Y + 9), outline=col, width=3)
    d.text((X + 10, Y), NAMES[panel][int(i)][:14], fill=col, font=f, stroke_width=2, stroke_fill='white')
im.save(out); print(im.size)
