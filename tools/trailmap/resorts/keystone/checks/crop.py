"""crop.py out.png x0,y0,x1,y1 [zoom]  - render a PDF-point box of the Keystone map, plain (default zoom 5;
scratch: crop.py)."""
import os
import sys

import pymupdf

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from common import PDF  # noqa: E402

p = pymupdf.open(PDF)[0]
x0, y0, x1, y1 = map(float, sys.argv[2].split(','))
z = float(sys.argv[3]) if len(sys.argv) > 3 else 5
pix = p.get_pixmap(clip=pymupdf.Rect(x0, y0, x1, y1), matrix=pymupdf.Matrix(z, z))
pix.save(sys.argv[1]); print(pix.width, pix.height)
