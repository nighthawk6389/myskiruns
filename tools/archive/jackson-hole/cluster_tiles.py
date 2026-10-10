"""Draw the label clusters (jh_glyphs.py) on the map, numbered, in tiles."""
import json, sys
from PIL import Image, ImageDraw, ImageFont
im = Image.open(sys.argv[1]).convert('RGB')
L = json.load(open(sys.argv[2]))
d = ImageDraw.Draw(im)
f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 15)
col = {'blue': (255, 0, 200), 'black': (255, 0, 0), 'green': (255, 120, 0)}
for l in L:
    x0, y0, x1, y1 = l['box']
    d.rectangle((x0 - 2, y0 - 2, x1 + 2, y1 + 2), outline=col[l['cls']], width=2)
    d.line([tuple(p) for p in l['pts']], fill=col[l['cls']], width=1)
    d.text((x0, y0 - 17), str(l['id']), fill=col[l['cls']], font=f, stroke_width=2, stroke_fill='white')
tw, th = int(sys.argv[4]), int(sys.argv[5])
k = 0
for y in range(0, im.height, th):
    for x in range(0, im.width, tw):
        im.crop((x, y, min(im.width, x + tw), min(im.height, y + th))).save(f'{sys.argv[3]}_{k:02d}_{x}_{y}.png'); k += 1
