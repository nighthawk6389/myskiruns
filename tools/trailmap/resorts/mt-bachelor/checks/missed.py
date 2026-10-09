"""Lines the extraction may have missed: every outline the PDF fills in a run's colour (blue, green, black) that is
neither a letter of a name (letters.json) nor a symbol, drawn at the map's scale, less the line pieces (8 px wide):
what is left, in blobs of 40 px or more, is listed with its box (map px), to be looked at on a crop.

    python3 tools/trailmap/resorts/mt-bachelor/checks/missed.py      # after regen.sh (reads work/mt-bachelor)

Found the junction outlines pdf_outline_lines.py read wide (I-5's and Carnival's lines meeting at Carnival's
square), now read by their skeleton.
"""
import json
import os
import sys

import numpy as np
import pymupdf
from PIL import Image, ImageDraw
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
sys.path.insert(0, os.path.join(HERE, '../../..'))
from resort import CLIP, SCALE  # noqa: E402
import pdf_outline_lines as pol  # noqa: E402
from pdf_glyphs import letter  # noqa: E402
import prepare  # noqa: E402

W = prepare.W
page = pymupdf.open(prepare.PDF)[0]
table = json.load(open(prepare.LETTERS))
letters = {g['seq'] for g in json.load(open(os.path.join(W, 'glyphs.json')))['glyphs'] if letter(table, g) is not None}
colours = [prepare.BLUE, prepare.GREEN, prepare.BLACK]
w, h = round((CLIP[2] - CLIP[0]) * SCALE), round((CLIP[3] - CLIP[1]) * SCALE)
drawn = Image.new('L', (w, h), 0)
dd = ImageDraw.Draw(drawn)
for d in page.get_drawings():
    f = d.get('fill') if d['type'] == 'f' else None
    if not f or d['seqno'] in letters or not any(max(abs(x - y) for x, y in zip(f, c)) < 0.01 for c in colours):
        continue
    if d['rect'].x1 < CLIP[0] + 1:
        continue  # the legend panel
    for sp in pol.subpaths(d):
        o = pol.outline(sp)
        if len(o) > 2:
            dd.polygon([((x - CLIP[0]) * SCALE, (y - CLIP[1]) * SCALE) for x, y in o], fill=255)
lines = Image.new('L', (w, h), 0)
ld = ImageDraw.Draw(lines)
for p in json.load(open(os.path.join(W, 'pieces.json')))['polylines']:
    ld.line([(x * w / 100, y * h / 100) for x, y in p['points']], fill=255, width=8)
for s in json.load(open(os.path.join(W, 'named_syms.json'))) + json.load(open(os.path.join(W, 'loose_syms.json'))):
    x, y = s['c']
    ld.ellipse([x - 16, y - 16, x + 16, y + 16], fill=255)
left = (np.asarray(drawn) > 0) & ~(np.asarray(lines) > 0)
lab, n = ndimage.label(left)
sizes = ndimage.sum(left, lab, range(1, n + 1))
boxes = ndimage.find_objects(lab)
found = sorted(((int(sizes[i]), boxes[i]) for i in range(n) if sizes[i] >= 40), key=lambda t: -t[0])
for size, (ys, xs) in found:
    print(f'{size:6d} px  box {xs.start},{ys.start},{xs.stop},{ys.stop}')
print(len(found), 'blobs')
