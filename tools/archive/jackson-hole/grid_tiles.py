"""2x zoomed tiles of a map with a labelled coordinate grid (map px), for reading names' positions on crops."""
import sys
from PIL import Image, ImageDraw, ImageFont
im = Image.open(sys.argv[1]).convert('RGB')
out, tw, th, z, step = sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6])
X0, Y0, X1, Y1 = map(int, sys.argv[7].split(','))
f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 13)
k = 0
for y in range(Y0, Y1, th):
    for x in range(X0, X1, tw):
        c = im.crop((x, y, x + tw, y + th)).resize((tw * z, th * z), Image.LANCZOS)
        d = ImageDraw.Draw(c)
        for gx in range((x // step + 1) * step, x + tw, step):
            d.line([((gx - x) * z, 0), ((gx - x) * z, th * z)], fill=(255, 0, 255), width=1)
            d.text(((gx - x) * z + 2, 2), str(gx), fill=(255, 0, 255), font=f, stroke_width=2, stroke_fill='white')
        for gy in range((y // step + 1) * step, y + th, step):
            d.line([(0, (gy - y) * z), (tw * z, (gy - y) * z)], fill=(255, 0, 255), width=1)
            d.text((2, (gy - y) * z + 2), str(gy), fill=(255, 0, 255), font=f, stroke_width=2, stroke_fill='white')
        c.save(f'{out}_{k:02d}_{x}_{y}.png'); k += 1
