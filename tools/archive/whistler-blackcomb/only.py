"""only.py PANEL x0,y0,x1,y1 zoom out.png id,id,...: the map crop with only these pieces drawn (thick, distinct
colours), each tagged with its id at both ends."""
import json, sys
from PIL import Image, ImageDraw, ImageFont
Image.MAX_IMAGE_PIXELS = None
panel, box, z, out, ids = sys.argv[1], tuple(map(int, sys.argv[2].split(','))), float(sys.argv[3]), sys.argv[4], [int(v) for v in sys.argv[5].split(',')]
W = f'/home/user/myskiruns/work/whistler-blackcomb/{panel}'
im = Image.open(f'{W}/map.png').convert('RGB')
WW, HH = im.size
im = im.crop(box).resize((int((box[2] - box[0]) * z), int((box[3] - box[1]) * z)), Image.LANCZOS)
dr = ImageDraw.Draw(im, 'RGBA')
F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 15)
P = {p['id']: p for p in json.load(open(f'{W}/pieces_cut.json'))['polylines']}
COL = [(255, 0, 200), (0, 200, 255), (255, 140, 0), (120, 0, 255), (0, 170, 0), (255, 0, 0), (0, 90, 255), (160, 100, 0)]
for k, i in enumerate(ids):
    c = COL[k % len(COL)]
    pts = [((x * WW / 100 - box[0]) * z, (y * HH / 100 - box[1]) * z) for x, y in P[i]['points']]
    dr.line(pts, fill=c + (170,), width=4)
    for q in (pts[0], pts[-1]):
        dr.ellipse((q[0] - 4, q[1] - 4, q[0] + 4, q[1] + 4), fill=c)
    m = pts[len(pts) // 2]
    dr.text((m[0] + 4, m[1] - 8), str(i), fill=c, font=F, stroke_width=3, stroke_fill='white')
im.save(out); print(out, im.size)
