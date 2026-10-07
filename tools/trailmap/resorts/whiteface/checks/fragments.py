"""The labels printed in fragments, rendered from the PDF on one sheet: how build.py's merges were checked (two-line
names, "Switchbacks" printed once between Upper and Lower; scratch: the one-off script that wrote merge_check.png).

    python3 tools/trailmap/resorts/whiteface/checks/fragments.py

Reads $WHITEFACE_WORK/whiteface.pdf and wf_labels.json; writes $WHITEFACE_WORK/merge_check.png. The spots are in
PDF points.
"""
import json
import os

import pymupdf
from PIL import Image, ImageDraw

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../../..'))
WORK = os.path.abspath(os.environ.get('WHITEFACE_WORK', os.path.join(REPO, 'work/whiteface')))
p = pymupdf.open(os.path.join(WORK, 'whiteface.pdf'))[0]
spots = {'Ladies/Bridge': (735, 857), 'Switchbacks/Upper/Lower': (1050, 370), 'Crossover/Loop': (1083, 425),
         'Victoria': (935, 563), 'Glen/Webers': (1030, 440), 'On Ramp': None}
L = json.load(open(os.path.join(WORK, 'wf_labels.json')))
onr = [o for o in L if o['text'] == 'On Ramp'][0]['c']
spots['On Ramp'] = tuple(onr)
cells = []
for name, (x, y) in spots.items():
    pix = p.get_pixmap(matrix=pymupdf.Matrix(4, 4), clip=pymupdf.Rect(x - 60, y - 45, x + 60, y + 45))
    im = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
    c = Image.new('RGB', (im.width, im.height + 18), 'white'); c.paste(im, (0, 18)); ImageDraw.Draw(c).text((3, 3), name, fill='black')
    cells.append(c)
W = max(c.width for c in cells); H = max(c.height for c in cells)
sheet = Image.new('RGB', (W * 3, H * 2), 'white')
for i, c in enumerate(cells): sheet.paste(c, ((i % 3) * W, (i // 3) * H))
sheet.save(os.path.join(WORK, 'merge_check.png')); print(sheet.size)
