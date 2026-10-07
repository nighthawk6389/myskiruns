"""crop.py out.png x0,y0,x1,y1 [zoom]  - render a PDF-point box of the Copper Mountain map (default zoom 5).

    python3 tools/trailmap/resorts/copper-mountain/checks/crop.py z_buffalo.png 540,200,640,340 6
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import PDF  # noqa: E402
import pymupdf
p = pymupdf.open(PDF)[0]
x0, y0, x1, y1 = map(float, sys.argv[2].split(','))
z = float(sys.argv[3]) if len(sys.argv) > 3 else 5
pix = p.get_pixmap(clip=pymupdf.Rect(x0, y0, x1, y1), matrix=pymupdf.Matrix(z, z))
pix.save(sys.argv[1]); print(pix.width, pix.height)
