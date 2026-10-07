"""Pieces on a crop: python3 tools/trailmap/resorts/sugarbush/checks/piece_crop.py out.png x0,y0,x1,y1 id,id,... [zoom]

The source (x0..y1 in source px) at zoom (default 3) with the given pieces drawn in turn in magenta, cyan,
orange, green and red, each tagged with its id: how the splits and unnamed connectors in decisions.py were
settled (session crops split_jester.png 690,1150,960,1340 25,26,20,0,31; split_northstar.png
3500,1440,3680,1600 85,87; split_crackerjack.png 3520,1930,3700,2080 94,88; unnamed.png 1700,1000,1850,1140 98
and 1370,1650,1540,1790 106). Those crops drew the pieces before the cut; the pieces read here
(PIECES=, default src/data/resorts/sugarbush/linePolylines.json) are after it, so the lower part of a split
shows as its new id (115, 116, 117). Reads $SUGARBUSH_WORK/sugarbush_source.png (regen.sh). Was inline code.
"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

Image.MAX_IMAGE_PIXELS = None
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *['..'] * 5))
WORK = os.environ.get('SUGARBUSH_WORK', os.path.join(ROOT, 'work', 'sugarbush'))
src = Image.open(os.path.join(WORK, 'sugarbush_source.png')).convert('RGB'); W, H = src.size
P = {p['id']: p for p in json.load(open(os.environ.get(
    'PIECES', os.path.join(ROOT, 'src/data/resorts/sugarbush/linePolylines.json'))))['polylines']}
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 18)
out, box, ids = sys.argv[1], tuple(map(int, sys.argv[2].split(','))), [int(i) for i in sys.argv[3].split(',')]
z = int(sys.argv[4]) if len(sys.argv) > 4 else 3
im = src.crop(box).resize(((box[2] - box[0]) * z, (box[3] - box[1]) * z), Image.LANCZOS)
d = ImageDraw.Draw(im)
cols = [(255, 0, 255), (0, 200, 255), (255, 140, 0), (0, 200, 0), (255, 0, 0)]
for k, i in enumerate(ids):
    pts = [((x * W / 100 - box[0]) * z, (y * H / 100 - box[1]) * z) for x, y in P[i]['points']]
    d.line(pts, fill=cols[k % 5], width=3)
    d.text(pts[len(pts) // 2], str(i), fill=cols[k % 5], font=font, stroke_width=2, stroke_fill='white')
im.save(out)
print(out, im.size)
