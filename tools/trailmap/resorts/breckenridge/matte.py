"""Breckenridge's map image: the PDF's vector layer (lines, names, symbols, icons, lifts) matted over Vail Resorts'
sharper CDN raster of the same map (the PDF embeds only a 1482x962 copy of its painting).

    python3 tools/trailmap/resorts/breckenridge/matte.py [--jpg public/maps/breckenridge.jpg]   # regen.sh runs it

Reads work/breckenridge.pdf and work/scene7.jpg (3037x2166 for the 1458x1039.5 pt page). Writes work/map.png (the
map clip, 0,80-1458,925 pt, at 3 px/pt: 4374x2535, the grid the pieces are on) and, with --jpg, the app's JPEG
(quality 82, progressive).

The page is rendered with its painting (image xref 150) swapped for flat white and for flat black: the difference
gives the vector layer's alpha, the black render / alpha its colour. The scene7 raster is the whole map flattened,
translucent layers included: a 10% white wash over the painting, the yellow easiest-route bands and slow zones
(Multiply), and a few 60-65% fills, each a form XObject drawn under a graphics state with opacity < 1 or a
non-Normal blend (found by tools/trailmap/matte_pdf_layer.py's translucent_forms()). So the layer's coverage is
taken from renders with those forms emptied: where the opaque vector content covers a pixel it is drawn (in its full
render, with any translucent form over it, as the legend's swatches over the legend's white box), and elsewhere the
scene7 raster shows as it is, its translucent layers applied once. (Until 2026-10-07 the full layer's alpha was
used, which applied the wash and the bands a second time: the image was 6-10 levels lighter where only the painting
shows.) The scene7 raster is cropped to the clip and resized (Lanczos) under it.
"""
import argparse, os, sys
import numpy as np, pymupdf
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..'))
from common import PDF, work  # noqa: E402
from matte_pdf_layer import translucent_forms  # noqa: E402
Image.MAX_IMAGE_PIXELS = None
S = 3.0
CLIP = pymupdf.Rect(0, 80, 1458, 925)
PAINTING = 150  # the embedded painting's xref


def render(fill, opaque_only=False):
    doc = pymupdf.open(PDF); p = doc[0]
    if opaque_only:
        for x in translucent_forms(doc, p):
            doc.update_stream(x, b'')  # an empty form draws nothing
    px = pymupdf.Pixmap(pymupdf.csRGB, pymupdf.IRect(0, 0, 4, 4), 0); px.clear_with(fill)
    p.replace_image(PAINTING, pixmap=px)  # the painted background, swapped for a flat colour
    pix = p.get_pixmap(matrix=pymupdf.Matrix(S, S), clip=CLIP)
    return np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, 3).astype(np.float32)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--jpg', help="also save the app's map image here")
    a = ap.parse_args()
    W, B = render(255), render(0)
    alpha = np.clip(1 - (W - B).mean(axis=2) / 255.0, 0, 1)[..., None]
    col = np.where(alpha > 1e-3, B / np.maximum(alpha, 1e-3), 0)
    Wo, Bo = render(255, True), render(0, True)
    cover = np.clip(1 - (Wo - Bo).mean(axis=2) / 255.0, 0, 1)[..., None]  # the opaque vector content
    cdn = Image.open(work('scene7.jpg')).convert('RGB')
    k = cdn.width / 1458.0
    bg = cdn.crop((round(CLIP.x0 * k), round(CLIP.y0 * k), round(CLIP.x1 * k), round(CLIP.y1 * k))).resize(
        (W.shape[1], W.shape[0]), Image.LANCZOS)
    out = col * cover + np.asarray(bg, np.float32) * (1 - cover)
    im = Image.fromarray(np.clip(np.round(out), 0, 255).astype(np.uint8))
    im.save(work('map.png'))
    print(work('map.png'), im.size)
    if a.jpg:
        im.save(a.jpg, quality=82, optimize=True, progressive=True)
        print(a.jpg, os.path.getsize(a.jpg), 'bytes')


if __name__ == '__main__':
    main()
