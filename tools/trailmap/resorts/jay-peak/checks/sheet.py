"""Label contact sheet: python3 tools/trailmap/resorts/jay-peak/checks/sheet.py out.png NAME [NAME...]

Every printed copy of the named trails' labels (from jay_label_spans.json), rendered from the PDF at 4.4x
around the label, captioned with the printed name, the symbol labels.py gave it and the label's position in
source px: to check a symbol (the mixed ones: Jet, U.N., Green Mountain Boys, Northway, Ullr's Dream) or
whether a name is a trail at all (601, Progression Terrain, Micky, Taxi, Poma Line, Lift Line, Interstate,
Subway were looked at so). Reads $JAY_PEAK_WORK (default work/jay-peak, filled by regen.sh): jay.pdf and
jay_label_spans.json. Was the scratch sheet.py, unchanged but for its paths.
"""
import sys, json, os, pymupdf
from PIL import Image, ImageDraw
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *['..'] * 5))
WORK = os.environ.get('JAY_PEAK_WORK', os.path.join(ROOT, 'work', 'jay-peak'))
CLIP = (9, 66, 1076, 657); S = 4.0; Z = 7.0
spans = json.load(open(os.path.join(WORK, 'jay_label_spans.json')))
page = pymupdf.open(os.path.join(WORK, 'jay.pdf'))[0]
cells = []
for name in sys.argv[2:]:
    for s in spans:
        if s['mapName'] != name.upper():
            continue
        cx, cy = s['labelSrc'][0] / S + CLIP[0], s['labelSrc'][1] / S + CLIP[1]
        r = pymupdf.Rect(cx - 45, cy - 20, cx + 45, cy + 20)
        pix = page.get_pixmap(matrix=pymupdf.Matrix(Z / 1.6, Z / 1.6), clip=r)
        im = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
        cap = Image.new('RGB', (im.width, im.height + 16), 'white')
        cap.paste(im, (0, 16))
        ImageDraw.Draw(cap).text((3, 2), f"{s['printed']} -> {s['symbol']}  @{s['labelSrc']}", fill='black')
        cells.append(cap)
W = 3
w, h = max(c.width for c in cells), max(c.height for c in cells)
out = Image.new('RGB', (W * w, ((len(cells) + W - 1) // W) * h), 'white')
for i, c in enumerate(cells):
    out.paste(c, ((i % W) * w, (i // W) * h))
out.save(sys.argv[1])
print(out.size, len(cells))
