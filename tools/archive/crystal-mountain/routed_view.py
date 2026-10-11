"""Crystal Mountain: the Northway panel's routed lines (prepare.py's pieces.json), each in its own colour with its name,
over the faded inset: to check every route keeps to its painted line.

    python3 -I tools/archive/crystal-mountain/routed_view.py <work/crystal-mountain/northway> <out.png>
"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

W = sys.argv[1]
im = Image.open(os.path.join(W, 'map.png')).convert('RGB')
im = Image.blend(im, Image.new('RGB', im.size, 'white'), 0.35)
d = ImageDraw.Draw(im)
F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 26)
cols = [(255, 0, 0), (0, 160, 0), (0, 0, 255), (255, 0, 255), (0, 170, 170), (255, 120, 0), (120, 0, 200),
        (200, 0, 90), (0, 90, 200), (150, 110, 0), (0, 0, 0)]
for i, p in enumerate(json.load(open(os.path.join(W, 'pieces.json')))['polylines']):
    pts = [(x * im.width / 100, y * im.height / 100) for x, y in p['points']]
    d.line(pts, fill=cols[i % len(cols)], width=6)
    m = pts[len(pts) // 2]
    d.text((m[0] + 8, m[1]), p['name'], fill=cols[i % len(cols)], font=F, stroke_width=3, stroke_fill='white')
im.resize((im.width // 2, im.height // 2)).save(sys.argv[2])
