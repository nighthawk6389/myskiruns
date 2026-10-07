"""crop.py out.png x0,y0,x1,y1 [zoom]  - render a PDF-point box of the Breckenridge map (default zoom 5).

Scratch: crop.py (from Winter Park's). Reads work/breckenridge.pdf. The c_*.png crops decisions.py cites
(checks/crops.sh has the commands).
"""
import os, sys
import pymupdf
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import PDF  # noqa: E402
p = pymupdf.open(PDF)[0]
x0, y0, x1, y1 = map(float, sys.argv[2].split(','))
z = float(sys.argv[3]) if len(sys.argv) > 3 else 5
pix = p.get_pixmap(clip=pymupdf.Rect(x0, y0, x1, y1), matrix=pymupdf.Matrix(z, z))
pix.save(sys.argv[1]); print(pix.width, pix.height)
