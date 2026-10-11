"""Crested Butte: every fill in the black runs' colour that holds four or more outlines (a dashed line drawn as one
fill), each in its own colour with its drawing number, over the faded map at half size: these are the boundary and
the control fences (dots 4 to 6 pt), not runs, so pdf_outline_lines.py is told never to chain that colour's dashes
(--undashed) and to link the runs' dashes, drawn one fill each (--linked).

    python3 tools/archive/crested-butte/dash_fills_view.py work/crested-butte/crested-butte_2025-26.pdf \
        work/crested-butte/main/map.png out.png
"""
import colorsys
import os
import sys

import pymupdf
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../trailmap'))
import pdf_outline_lines as O  # noqa: E402

Image.MAX_IMAGE_PIXELS = None
BLACK, SCALE = (0.01, 0.02, 0.02), 3

pdf, img, out = sys.argv[1:4]
page = pymupdf.open(pdf)[1]
im = Image.open(img).convert('RGB')
im = Image.blend(im, Image.new('RGB', im.size, 'white'), 0.6)
d = ImageDraw.Draw(im)
k = 0
for dr in page.get_drawings():
    f = dr.get('fill')
    if dr['type'] != 'f' or not f or max(abs(a - b) for a, b in zip(f, BLACK)) >= 0.01:
        continue
    sps = list(O.subpaths(dr))
    if len(sps) < 4:
        continue
    k += 1
    col = tuple(int(255 * v) for v in colorsys.hsv_to_rgb((k * 0.618) % 1, 1, 0.8))
    for sp in sps:
        c, _w = O.centre(sp)
        if c:
            d.line([(x * SCALE, y * SCALE) for x, y in c], fill=col, width=6)
    c, _w = O.centre(sps[len(sps) // 2])
    if c:
        d.text((c[0][0] * SCALE + 8, c[0][1] * SCALE), str(dr['seqno']), fill=(0, 0, 0))
im.resize((im.width // 2, im.height // 2)).save(out)
