"""A zoomed crop of a map with a labelled grid (map px): zoom.py <img> <out> x0,y0,x1,y1 [zoom] [step]"""
import sys
from PIL import Image, ImageDraw, ImageFont
im = Image.open(sys.argv[1]).convert('RGB')
x0, y0, x1, y1 = map(int, sys.argv[3].split(','))
z = int(sys.argv[4]) if len(sys.argv) > 4 else 3
step = int(sys.argv[5]) if len(sys.argv) > 5 else 25
c = im.crop((x0, y0, x1, y1)).resize(((x1 - x0) * z, (y1 - y0) * z), Image.LANCZOS)
d = ImageDraw.Draw(c)
f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 12)
for gx in range((x0 // step + 1) * step, x1, step):
    d.line([((gx - x0) * z, 0), ((gx - x0) * z, c.height)], fill=(255, 0, 255), width=1)
    d.text(((gx - x0) * z + 2, 2), str(gx), fill=(255, 0, 255), font=f, stroke_width=2, stroke_fill='white')
for gy in range((y0 // step + 1) * step, y1, step):
    d.line([(0, (gy - y0) * z), (c.width, (gy - y0) * z)], fill=(255, 0, 255), width=1)
    d.text((2, (gy - y0) * z + 2), str(gy), fill=(255, 0, 255), font=f, stroke_width=2, stroke_fill='white')
c.save(sys.argv[2])
