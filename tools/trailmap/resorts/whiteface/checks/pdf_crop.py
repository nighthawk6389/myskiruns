"""One spot of the PDF rendered sharp, straight from its vectors (scratch: the one-off renders that made
victoria.png and switchbacks.png).

    python3 tools/trailmap/resorts/whiteface/checks/pdf_crop.py work/whiteface/victoria.png 1860,1150,2120,1480 5

The box is x0,y0,x1,y1 in map px (2.2 per PDF point), the last argument the zoom in px per point (default 5).
Reads $WHITEFACE_WORK/whiteface.pdf.
"""
import os
import sys

import pymupdf

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../../..'))
WORK = os.path.abspath(os.environ.get('WHITEFACE_WORK', os.path.join(REPO, 'work/whiteface')))
p = pymupdf.open(os.path.join(WORK, 'whiteface.pdf'))[0]
x0, y0, x1, y1 = [float(v) / 2.2 for v in sys.argv[2].split(',')]  # map px at 2.2 -> pt
z = float(sys.argv[3]) if len(sys.argv) > 3 else 5
pix = p.get_pixmap(matrix=pymupdf.Matrix(z, z), clip=pymupdf.Rect(x0, y0, x1, y1)); pix.save(sys.argv[1])
print(pix.width, pix.height)
