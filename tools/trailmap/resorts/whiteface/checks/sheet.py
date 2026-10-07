"""Crops side by side on one sheet, to look at several at once (scratch: the sheet() helper that made sheet_a..e.jpg
from the zz_*.jpg crops).

    python3 tools/trailmap/resorts/whiteface/checks/sheet.py work/whiteface/sheet_a.jpg work/whiteface/zz_0.jpg work/whiteface/zz_1.jpg
"""
import sys

from PIL import Image


def sheet(names, out):
    ims = [Image.open(n) for n in names]
    W = sum(i.width for i in ims) + 10 * (len(ims) - 1); H = max(i.height for i in ims)
    s = Image.new('RGB', (W, H), (80, 80, 80)); x = 0
    for i in ims: s.paste(i, (x, 0)); x += i.width + 10
    s.save(out); print(out, s.size)


sheet(sys.argv[2:], sys.argv[1])
