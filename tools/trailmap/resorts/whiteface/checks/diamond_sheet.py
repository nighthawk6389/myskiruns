"""Every black name's label rendered from the PDF with the difficulty it got in trails.ts: the single vs double
diamond check (scratch: the one-off script that wrote wf_diamonds.png).

    python3 tools/trailmap/resorts/whiteface/checks/diamond_sheet.py

Reads $WHITEFACE_WORK/whiteface.pdf and wf_assign.json and src/data/resorts/whiteface/trails.ts; writes
$WHITEFACE_WORK/wf_diamonds.png (six crops a row, each headed "<name> = <difficulty>").
"""
import json
import os
import re

import pymupdf
from PIL import Image, ImageDraw, ImageFont

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../../..'))
WORK = os.path.abspath(os.environ.get('WHITEFACE_WORK', os.path.join(REPO, 'work/whiteface')))
A = json.load(open(os.path.join(WORK, 'wf_assign.json')))
ts = open(os.path.join(REPO, 'src/data/resorts/whiteface/trails.ts')).read()
diff = {m.group(2).strip('"\''): m.group(3) for m in re.finditer(r"id: '([^']+)', name: (\"[^\"]+\"|'[^']+'), difficulty: '([^']+)'", ts)}
page = pymupdf.open(os.path.join(WORK, 'whiteface.pdf'))[0]
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 13)
cells = []
for l in sorted(A['labels'], key=lambda l: l['text']):
    if l['cls'] != 'black':
        continue
    pts = l['pts']
    x0 = min(p[0] for p in pts) - 16; x1 = max(p[0] for p in pts) + 16
    y0 = min(p[1] for p in pts) - 16; y1 = max(p[1] for p in pts) + 16
    s = min(6, 300 / max(x1 - x0, y1 - y0))
    pix = page.get_pixmap(matrix=pymupdf.Matrix(s, s), clip=pymupdf.Rect(x0, y0, x1, y1))
    im = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
    c = Image.new('RGB', (300, 320), 'white'); c.paste(im.resize((min(300, im.width), min(300, im.height))), (0, 20))
    name = l['text'].replace('’', "'")
    ImageDraw.Draw(c).text((3, 3), f"{name} = {diff.get(name, '?')}", fill='black', font=font)
    cells.append(c)
cols = 6
sheet = Image.new('RGB', (cols * 302, ((len(cells) + cols - 1) // cols) * 322), (120, 120, 120))
for k, c in enumerate(cells):
    sheet.paste(c, ((k % cols) * 302, (k // cols) * 322))
sheet.save(os.path.join(WORK, 'wf_diamonds.png')); print(len(cells), sheet.size)
