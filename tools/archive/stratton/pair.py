"""Stratton: one box of the map, the 2020-21 export on this season's grid beside this season's image, zoomed, with
a grid every 50 px labelled in map px.

    python3 -I tools/archive/stratton/pair.py <old_on_grid.png> <map2025.png> x0,y0,x1,y1 <zoom> <out.png>
"""
import sys

from PIL import Image, ImageDraw, ImageFont

Image.MAX_IMAGE_PIXELS = None
F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 12)
old, new = Image.open(sys.argv[1]).convert('RGB'), Image.open(sys.argv[2]).convert('RGB')
x0, y0, x1, y1 = (int(v) for v in sys.argv[3].split(','))
z = float(sys.argv[4])
out = []
for im in (old, new):
    c = im.crop((x0, y0, x1, y1)).resize((round((x1 - x0) * z), round((y1 - y0) * z)), Image.LANCZOS)
    d = ImageDraw.Draw(c)
    for gx in range((x0 // 50 + 1) * 50, x1, 50):
        d.line([((gx - x0) * z, 0), ((gx - x0) * z, c.height)], fill=(255, 0, 255), width=1)
        d.text(((gx - x0) * z + 2, 2), str(gx), fill=(255, 0, 255), font=F)
    for gy in range((y0 // 50 + 1) * 50, y1, 50):
        d.line([(0, (gy - y0) * z), (c.width, (gy - y0) * z)], fill=(255, 0, 255), width=1)
        d.text((2, (gy - y0) * z + 2), str(gy), fill=(255, 0, 255), font=F)
    out.append(c)
s = Image.new('RGB', (out[0].width * 2 + 8, out[0].height), 'black')
s.paste(out[0], (0, 0)); s.paste(out[1], (out[0].width + 8, 0))
s.save(sys.argv[5])
