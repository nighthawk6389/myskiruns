"""Symbol check sheet: python3 tools/trailmap/resorts/sugarbush/checks/symbol_sheet.py out.png black|all|id,id,...

Crops of every printed label of the given trails (where the readers' labelSrc puts them) on the lossless
source, captioned with the trail's name, its difficulty in trails.ts and the symbol the reader saw: the single
vs double diamond check (Sugarbush draws its diamonds inside the outlined label glyphs, so pdf_symbols.py
cannot find them and this sheet was the second method: 30 single and 8 double, all as read). `black` takes
every black and double-black trail. Reads $SUGARBUSH_WORK (default work/sugarbush, filled by regen.sh):
sugarbush_source.png, labels.json, tiles/result_*.json; TRAILS= / LABELS= point at other copies (the session
checked a partial trail list while the readers were still running). Was the scratch symbol_sheet.py.
"""
import glob
import json
import os
import re
import sys

from PIL import Image, ImageDraw, ImageFont

Image.MAX_IMAGE_PIXELS = None
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *['..'] * 5))
WORK = os.environ.get('SUGARBUSH_WORK', os.path.join(ROOT, 'work', 'sugarbush'))
src = Image.open(os.path.join(WORK, 'sugarbush_source.png')).convert('RGB')
ts = open(os.environ.get('TRAILS', os.path.join(ROOT, 'src/data/resorts/sugarbush/trails.ts'))).read()
rows = re.findall(r"id: '([^']+)', name: (\"[^\"]+\"|'[^']+'), difficulty: '([^']+)'", ts)
diff = {r[0]: r[2] for r in rows}; name = {r[0]: r[1].strip('"\'') for r in rows}
labels = json.load(open(os.environ.get('LABELS', os.path.join(WORK, 'labels.json'))))
raw = {}
for f in sorted(glob.glob(os.path.join(WORK, 'tiles', 'result_*.json'))):
    for lab in json.load(open(f)).get('labels', []):
        n = re.sub(r'\s+', ' ', (lab.get('mapName') or '').upper().replace('’', "'")).strip(' .')
        if lab.get('labelSrc'):
            raw.setdefault(n, []).append((lab['labelSrc'], lab.get('symbol')))
which = sys.argv[2]
ids = ([t for t in sorted(labels) if diff.get(t) in ('black', 'double-black')] if which == 'black'
       else sorted(labels) if which == 'all' else which.split(','))
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 14)
cells = []
for tid in ids:
    e = labels[tid]
    seen = []
    for p, sym in raw.get(e['mapName'], []):
        if any(abs(p[0] - q[0]) < 40 and abs(p[1] - q[1]) < 40 for q in seen):
            continue
        seen.append(p)
        half = int(3.3 * len(e['mapName']) + 45)
        box = (p[0] - half, p[1] - half, p[0] + half, p[1] + half)
        im = src.crop(box).resize((330, 330), Image.LANCZOS)
        cells.append((f"{name.get(tid, tid)} = {diff.get(tid)} (read {sym})", im))
cols = 5
sheet = Image.new('RGB', (cols * 334, ((len(cells) + cols - 1) // cols) * 352), 'white')
d = ImageDraw.Draw(sheet)
for k, (cap, im) in enumerate(cells):
    x, y = (k % cols) * 334, (k // cols) * 352
    sheet.paste(im, (x, y + 20)); d.text((x + 3, y + 2), cap[:40], fill='black', font=font)
sheet.save(sys.argv[1]); print(sys.argv[1], len(cells))
