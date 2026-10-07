# render the PDF page 2 for a box in MAP px at zoom z (output px per map px), with a 10-map-px grid
import sys, pymupdf
from PIL import Image, ImageDraw, ImageFont
S = 2.5
x0, y0, x1, y1 = [float(v) for v in sys.argv[1].split(',')]
z = float(sys.argv[2]); out = sys.argv[3]
step = int(sys.argv[4]) if len(sys.argv) > 4 else 25
doc = pymupdf.open('/home/user/myskiruns/work/whistler-blackcomb/whistler.pdf')
page = doc[1]
clip = pymupdf.Rect(x0 / S, y0 / S, x1 / S, y1 / S)
pix = page.get_pixmap(matrix=pymupdf.Matrix(S * z, S * z), clip=clip)
pix.save(out)
im = Image.open(out).convert('RGB')
d = ImageDraw.Draw(im)
f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 11)
gx = (int(x0) // step + 1) * step
while gx < x1:
    X = (gx - x0) * z; d.line((X, 0, X, im.height), fill=(255, 0, 255)); d.text((X + 2, 2), str(gx), fill=(200, 0, 200), font=f)
    gx += step
gy = (int(y0) // step + 1) * step
while gy < y1:
    Y = (gy - y0) * z; d.line((0, Y, im.width, Y), fill=(255, 0, 255)); d.text((2, Y + 2), str(gy), fill=(200, 0, 200), font=f)
    gy += step
im.save(out)
print(out, im.size)
