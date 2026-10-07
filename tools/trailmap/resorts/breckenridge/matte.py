"""Breckenridge's map image: the PDF's vector layer (lines, names, symbols, icons, lifts) matted over Vail Resorts'
sharper CDN raster of the same painting (the PDF embeds only a 1482x962 copy).

    python3 tools/trailmap/resorts/breckenridge/matte.py [--jpg public/maps/breckenridge.jpg]   # regen.sh runs it

Reads work/breckenridge.pdf and work/scene7.jpg (the painting from scene7, 3037x2166 for the 1458x1039.5 pt page).
Writes work/map.png (the map clip, 0,80-1458,925 pt, at 3 px/pt: 4374x2535, the grid the pieces are on) and, with
--jpg, the app's JPEG (quality 82, progressive). The page is rendered twice with its painting (image xref 150)
swapped for flat white and flat black: alpha = 1 - (white - black) / 255, colour = black render / alpha; the
scene7 raster is cropped to the clip and resized (Lanczos) under it.

This is the inline script that made the committed image (session history, 2026-10-01T15:08:14; it wrote
br_hybrid.png, br_q82.jpg = the committed JPEG, and a quality-80 test copy), with its image logic unchanged.
tools/trailmap/matte_pdf_layer.py, written later from it, places the background with a bicubic affine transform
instead and differs by about 1.6 levels on average, so it would not rebuild the committed JPEG byte for byte.
Known flaw, kept so the committed image is rebuilt exactly: scene7's raster is the flattened map, so the PDF's
translucent layers (a 10% white wash, the yellow Multiply bands) are applied a second time (README.md).
"""
import argparse, os, sys
import numpy as np, pymupdf
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import PDF, work  # noqa: E402
Image.MAX_IMAGE_PIXELS = None
ap = argparse.ArgumentParser()
ap.add_argument('--jpg', help="also save the app's map image here")
a = ap.parse_args()
S = 3.0
CLIP = pymupdf.Rect(0, 80, 1458, 925)


def render(fill):
    doc = pymupdf.open(PDF); p = doc[0]
    px = pymupdf.Pixmap(pymupdf.csRGB, pymupdf.IRect(0, 0, 4, 4), 0); px.clear_with(fill)
    p.replace_image(150, pixmap=px)  # the painted background, swapped for a flat colour
    pix = p.get_pixmap(matrix=pymupdf.Matrix(S, S), clip=CLIP)
    return np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, 3).astype(np.float32)


W = render(255); B = render(0)
alpha = np.clip(1 - (W - B).mean(axis=2) / 255.0, 0, 1)[..., None]
col = np.where(alpha > 1e-3, B / np.maximum(alpha, 1e-3), 0)
# the same painting, sharper: Vail's CDN raster of this map (3037x2166 for the 1458x1039.5 pt page)
cdn = Image.open(work('scene7.jpg')).convert('RGB')
k = cdn.width / 1458.0
bg = cdn.crop((round(CLIP.x0 * k), round(CLIP.y0 * k), round(CLIP.x1 * k), round(CLIP.y1 * k))).resize((W.shape[1], W.shape[0]), Image.LANCZOS)
out = col * alpha + np.asarray(bg, np.float32) * (1 - alpha)
im = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))
im.save(work('map.png'))
print(work('map.png'), im.size)
if a.jpg:
    im.save(a.jpg, quality=82, optimize=True, progressive=True)
    print(a.jpg, os.path.getsize(a.jpg), 'bytes')
