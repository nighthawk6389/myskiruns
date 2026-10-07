"""hl2.py PANEL x0,y0,x1,y1 ZOOM OUT id[,id...]: the crop twice, plain and with the given pieces drawn thin in
distinct colours (numbered), to see which drawn line each one lies on."""
import json, sys
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, '/home/user/myskiruns/tools/trailmap')
import pdf_resort as pr
panel, box, z, out, ids = sys.argv[1], tuple(map(int, sys.argv[2].split(','))), float(sys.argv[3]), sys.argv[4], [int(i) for i in sys.argv[5].split(',')]
r = pr.Resort(f'whistler-blackcomb/{panel}')
P = {p['id']: r.pts_of(p) for p in r.load('pieces_cut.json')['polylines']}
Image.MAX_IMAGE_PIXELS = None
im = Image.open(r.work('map.png')).convert('RGB').crop(box)
im = im.resize((int(im.width * z), int(im.height * z)), Image.LANCZOS)
b = im.copy(); d = ImageDraw.Draw(b)
F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 14)
C = [(255, 0, 0), (0, 200, 0), (255, 0, 255), (255, 140, 0), (0, 0, 0), (0, 160, 255)]
for k, i in enumerate(ids):
    t = [((x - box[0]) * z, (y - box[1]) * z) for x, y in P[i]]
    d.line(t, fill=C[k % len(C)], width=2)
    for e in (t[0], t[-1]):
        d.ellipse((e[0] - 4, e[1] - 4, e[0] + 4, e[1] + 4), outline=C[k % len(C)], width=2)
    m = t[len(t) // 2]; d.text((m[0] + 5, m[1] - 16), str(i), fill=C[k % len(C)], font=F)
o = Image.new('RGB', (im.width, im.height * 2 + 6), 'white'); o.paste(im, (0, 0)); o.paste(b, (0, im.height + 6)); o.save(out)
print(out, o.size)
