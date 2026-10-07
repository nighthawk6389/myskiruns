"""Contact sheets of every difficulty symbol found in the PDF's fills, each rendered from the PDF at 6x and
captioned with its index, type and size: to check pdf_symbols.py's circles, squares, diamonds and doubles.

    python3 tools/trailmap/resorts/okemo/checks/symbol_sheet.py   # after regen.sh, from the repo root

Reads $OKEMO_WORK/okemo.pdf and $OKEMO_WORK/symbols.json (pdf_symbols.py, regen.sh step 10); writes
$OKEMO_WORK/symsheet_<n>.png, 48 symbols each, ordered by type and size. (Scratch inline script of 2026-09-30
06:50 UTC, run on the scratch symbols_from_pdf.py's output, which pdf_symbols.py reproduces exactly.)
"""
import io
import json
import os

import pymupdf
from PIL import Image, ImageDraw, ImageFont

W_DIR = os.environ.get('OKEMO_WORK', 'work/okemo')
page = pymupdf.open(f'{W_DIR}/okemo.pdf')[1]
syms = json.load(open(f'{W_DIR}/symbols.json'))
for i, s in enumerate(syms):
    s['i'] = i
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 14)
Z, HALF, CELL = 6, 14, 168
order = sorted(syms, key=lambda s: (s['type'], s['sizePt']))
per = 48
for sheet in range(0, len(order), per):
    batch = order[sheet:sheet + per]
    cols = 8
    rows = (len(batch) + cols - 1) // cols
    out = Image.new('RGB', (cols * CELL, rows * (CELL + 18)), 'white')
    d = ImageDraw.Draw(out)
    for k, s in enumerate(batch):
        cx, cy = s['src'][0] / 3, s['src'][1] / 3
        pix = page.get_pixmap(matrix=pymupdf.Matrix(Z, Z), clip=pymupdf.Rect(cx - HALF, cy - HALF, cx + HALF, cy + HALF))
        im = Image.open(io.BytesIO(pix.tobytes('png'))).convert('RGB').resize((CELL, CELL))
        x, y = (k % cols) * CELL, (k // cols) * (CELL + 18)
        out.paste(im, (x, y + 18))
        dd = ImageDraw.Draw(out)
        dd.ellipse((x + CELL / 2 - 10, y + 18 + CELL / 2 - 10, x + CELL / 2 + 10, y + 18 + CELL / 2 + 10),
                   outline=(255, 0, 255), width=1)
        d.text((x + 2, y + 1), f"#{s['i']} {s['type'][:7]} {s['sizePt']}", fill='black', font=font)
    out.save(f'{W_DIR}/symsheet_{sheet // per}.png')
    print(f'{W_DIR}/symsheet_{sheet // per}.png', len(batch))
