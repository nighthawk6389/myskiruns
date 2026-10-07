"""crop.py out.png x0,y0,x1,y1 [zoom]  - render a PDF-point box of the Winter Park map.

    python3 tools/trailmap/resorts/winter-park/checks/crop.py c_chutes.png 330,500,420,585 6   # from the repo root

Renders the box of $WINTER_PARK_WORK/winterpark.pdf (default work/winter-park) at zoom px/pt (default 5) straight
from the PDF (sharper than the map image), to out.png in the work folder.
"""
import os, sys, pymupdf
WORK = os.environ.get('WINTER_PARK_WORK', 'work/winter-park')
p = pymupdf.open(os.path.join(WORK, 'winterpark.pdf'))[0]
x0, y0, x1, y1 = map(float, sys.argv[2].split(','))
z = float(sys.argv[3]) if len(sys.argv) > 3 else 5
pix = p.get_pixmap(clip=pymupdf.Rect(x0, y0, x1, y1), matrix=pymupdf.Matrix(z, z))
pix.save(os.path.join(WORK, sys.argv[1])); print(pix.width, pix.height)
