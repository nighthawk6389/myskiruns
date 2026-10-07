"""Per-trail crops for the symbol spot-check: each black / double-black trail (and the listed extra ids)
cropped from a 6x render of the PDF around its label and the nearest symbol of its difficulty's type (circled),
captioned with the trail's name and difficulty.

    python3 tools/trailmap/resorts/okemo/checks/symbol_crops.py black '' OUT.png        # every diamond trail
    python3 tools/trailmap/resorts/okemo/checks/symbol_crops.py none 'id,id,...' OUT.png  # just these

From the repo root, after regen.sh. Reads $OKEMO_WORK/{okemo.pdf,labels.json,symbols.json}, trails.ts and the
readers' label reports (readings/result_*.json). (Scratch symbol_crops.py of 2026-09-30: on its sheets the 38
diamond trails read 29 single and 9 double, all as the readers had them; the second run looked at
easy-street,fairway,gordons-garden,halfpipe,progression-park,the-zone,tree-tap,tomahawk.)
"""
import glob
import io
import json
import math
import os
import re
import sys

import pymupdf
from PIL import Image, ImageDraw, ImageFont

W_DIR = os.environ.get('OKEMO_WORK', 'work/okemo')
labels = json.load(open(f'{W_DIR}/labels.json'))
syms = json.load(open(f'{W_DIR}/symbols.json'))
ts = open('src/data/resorts/okemo/trails.ts').read()
rows = re.findall(r"id: '([^']+)', name: (['\"])(.*?)\2, difficulty: '([^']+)'", ts)
diff = {r[0]: r[3] for r in rows}
name = {r[0]: r[2] for r in rows}
SYM = {'green': 'circle', 'blue': 'square', 'black': 'diamond', 'double-black': 'double-diamond'}
raw = {}
for f in sorted(glob.glob('tools/trailmap/resorts/okemo/readings/result_*.json')):
    for lab in json.load(open(f)).get('labels', []):
        n = re.sub(r'\s+', ' ', (lab.get('mapName') or '').upper().replace('’', "'")).strip(' .')
        if lab.get('labelSrc'):
            raw.setdefault(n, []).append(lab['labelSrc'])
page = pymupdf.open(f'{W_DIR}/okemo.pdf')[1]
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 15)
extra = sys.argv[2].split(',') if len(sys.argv) > 2 and sys.argv[2] else []
ids = [t for t in sorted(labels) if diff[t] in ('black', 'double-black')] if sys.argv[1] == 'black' else []
ids += extra
cells = []
for tid in ids:
    e = labels[tid]
    pts = raw.get(e['mapName']) or e['positions']
    want = SYM[diff[tid]]
    cand = sorted((math.dist(s['src'], p), s['src'], p) for s in syms if s['type'] == want for p in pts)
    if cand and cand[0][0] < 5.5 * len(e['mapName']) + 60:
        _, sp, lp = cand[0]
        cx, cy = (sp[0] + lp[0]) / 2, (sp[1] + lp[1]) / 2
        half = max(abs(sp[0] - lp[0]), abs(sp[1] - lp[1])) / 2 + 45
        mark = sp
    else:
        lp = pts[0]
        cx, cy = lp
        half = 5.5 * len(e['mapName']) / 2 + 60
        mark = None
    half = max(half, 55)
    x0, y0 = (cx - half) / 3, (cy - half) / 3
    z = 260 / (2 * half / 3)
    pix = page.get_pixmap(matrix=pymupdf.Matrix(z, z), clip=pymupdf.Rect(x0, y0, x0 + 2 * half / 3, y0 + 2 * half / 3))
    im = Image.open(io.BytesIO(pix.tobytes('png'))).convert('RGB').resize((260, 260))
    if mark:
        d = ImageDraw.Draw(im)
        mx, my = (mark[0] - (cx - half)) * 260 / (2 * half), (mark[1] - (cy - half)) * 260 / (2 * half)
        d.ellipse((mx - 13, my - 13, mx + 13, my + 13), outline=(255, 0, 255), width=2)
    cells.append((f"{name[tid]} = {diff[tid]}", im))
cols = 6
sheet = Image.new('RGB', (cols * 262, ((len(cells) + cols - 1) // cols) * 282), 'white')
d = ImageDraw.Draw(sheet)
for k, (cap, im) in enumerate(cells):
    x, y = (k % cols) * 262, (k // cols) * 282
    sheet.paste(im, (x, y + 20))
    d.text((x + 3, y + 2), cap[:30], fill='black', font=font)
sheet.save(sys.argv[3])
print(sys.argv[3], len(cells))
