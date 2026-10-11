"""Mount Snow: the 2023-24 PDF's page rendered on the map image's grid (resort.SCALE, resort.CLIP), for reading the
pieces where this season's image is too soft: the same artwork, sharper, so map px read on it are map px on
work/mount-snow/map.png (grey where the page ends).

    python3 -I tools/archive/mount-snow/ref2023.py [work dir]      # writes <work dir>/ref2023.png
    python3 tools/trailmap/grid_crop.py --image work/mount-snow/ref2023.png --box 1550,420,1900,640 --zoom 2.4 \\
        --grid 50 --pieces work/mount-snow/pieces_cut.json --names work/mount-snow/names.json --out spot.png
"""
import os
import sys

import pymupdf
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '../../trailmap/resorts/mount-snow'))
import resort as R  # noqa: E402

W = sys.argv[1] if len(sys.argv) > 1 else 'work/mount-snow'
p = pymupdf.open(os.path.join(W, 'mountsnow_2023-24.pdf'))[0]
pix = p.get_pixmap(matrix=pymupdf.Matrix(R.SCALE, R.SCALE))
im = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
canvas = Image.new('RGB', (R.BOX[2] - R.BOX[0], R.BOX[3] - R.BOX[1]), (128, 128, 128))
canvas.paste(im, (round(-R.CLIP[0] * R.SCALE), round(-R.CLIP[1] * R.SCALE)))
canvas.save(os.path.join(W, 'ref2023.png'))
print(canvas.size)
