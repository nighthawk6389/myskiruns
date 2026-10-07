"""Zoomed map crops with every piece drawn in its colour and tagged id:NAME (build.py's automatic name), id? (no
name) or id! (two names): the crops the decisions were settled on (scratch: zoom_pieces.py; piece_regions.py was
the same at a fixed 1.25x and made pr_*.jpg).

    Z=2.0 python3 tools/trailmap/resorts/whiteface/checks/zoom_pieces.py work/whiteface/zc 2500,450,3060,860 ...

Boxes are x0,y0,x1,y1 in map px; writes <prefix>_<k>.jpg. Reads $WHITEFACE_WORK/map.png and wf_assign.json (run
regen.sh first) and src/data/resorts/whiteface/linePolylines.json.
"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../../..'))
WORK = os.path.abspath(os.environ.get('WHITEFACE_WORK', os.path.join(REPO, 'work/whiteface')))
Image.MAX_IMAGE_PIXELS = None
src = Image.open(os.path.join(WORK, 'map.png')).convert('RGB'); W, H = src.size
P = json.load(open(os.path.join(REPO, 'src/data/resorts/whiteface/linePolylines.json')))['polylines']
A = json.load(open(os.path.join(WORK, 'wf_assign.json')))['assign']
f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 15)
C = {'blue': (255, 0, 255), 'black': (255, 110, 0), 'green': (0, 230, 230)}
boxes = [tuple(map(int, b.split(','))) for b in sys.argv[2:]]
for k, box in enumerate(boxes):
    z = float(os.environ.get("Z", "1.25"))
    im = src.crop(box).resize((int((box[2]-box[0])*z), int((box[3]-box[1])*z)), Image.LANCZOS)
    ov = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    tags = []
    for p in P:
        pts = [((x*W/100-box[0])*z, (y*H/100-box[1])*z) for x, y in p['points']]
        ins = [q for q in pts if 0 <= q[0] < im.width and 0 <= q[1] < im.height]
        if not ins: continue
        d.line(pts, fill=C[p['cls']] + (200,), width=3)
        for e in (pts[0], pts[-1]): d.ellipse((e[0]-4, e[1]-4, e[0]+4, e[1]+4), fill=(255, 0, 0, 230))
        q = ins[len(ins)//2]
        nm = A.get(str(p['id']), [])
        tags.append((q, f"{p['id']}" + (f":{nm[0][:14]}" if len(nm) == 1 else ('?' if not nm else '!'))))
    for (x, y), t in tags:
        w = d.textlength(t, font=f)
        d.rectangle((x+3, y-9, x+w+7, y+9), fill=(255, 255, 0, 220)); d.text((x+5, y-9), t, fill=(0, 0, 0, 255), font=f)
    Image.alpha_composite(im.convert('RGBA'), ov).convert('RGB').save(f'{sys.argv[1]}_{k}.jpg', quality=85)
print(len(boxes))
