"""A sharp map image for a PDF whose vector layer (trail lines, names, symbols, icons) sits on a low-resolution
painting: render the vector layer at --scale px/pt and matte it over a better background, either a sharper copy
of the whole painting (Vail Resorts' image CDN, scene7, serves its maps at full size: see the playbook) or the
embedded painting upscaled with Lanczos instead of the renderer's blocky upscale.

    python3 tools/trailmap/matte_pdf_layer.py --pdf map.pdf --out map.png --scale 2.8 --clip 0,90,1530,1080 \\
        [--background sharper.jpg] [--xref 23] [--page 0]
    python3 tools/trailmap/matte_pdf_layer.py --pdf map.pdf --out map.png --scale 2.5 --resample 461 --resample 463

The vector layer comes from rendering the page twice with the painting swapped for flat white and then flat
black: alpha = 1 - (white - black) / 255, colour = black render / alpha. --xref is the painting's image xref
(default: the largest image on the page). --background is a raster of the whole page, stretched to the page's
size; without it the embedded painting is upscaled into place, and the result is compared with MuPDF's own
render where there are no vectors (Copper: 13.5 levels, from the smoother upscale; far more means the painting is
misplaced). --clip (in pt) is the map area.

--flattened: the background is the whole map flattened (Vail Resorts' CDN copies are), so it already shows the
page's translucent layers (form XObjects drawn under an opacity below 1 or a blend mode other than Normal: washes,
Multiply bands, slow zones). Matting the full layer over it would apply them a second time; instead the layer's
coverage comes from renders with those forms emptied: opaque vector content is drawn (with any translucent form
over it, such as a legend swatch on the legend's white box) and the background shows as it is everywhere else.
Used by the regen.sh or prepare.py of Copper Mountain (embedded painting) and Keystone (the scene7 copy of the
whole map, --flattened), Sugarloaf, Smugglers' Notch, Whistler Blackcomb, Big Sky and Park City (--resample);
Breckenridge's image comes from its own version of the same method (resorts/breckenridge/matte.py, which uses
translucent_forms() from here). Save the result as public/maps/<id>.jpg.

Requires: pip install pymupdf pillow numpy
"""
import argparse
import io
import re

import numpy as np
import pymupdf
from PIL import Image

Image.MAX_IMAGE_PIXELS = None


def translucent_forms(doc, page):
    """The xrefs of the form XObjects the page draws under an ExtGState whose opacity is below 1 or whose blend mode
    is not Normal (the q/Q nesting followed through the page's content streams)."""
    def refs(key):
        return dict(re.findall(r'/(\S+?) (\d+) 0 R', doc.xref_get_key(page.xref, key)[1]))
    gs, xo = refs('Resources/ExtGState'), refs('Resources/XObject')

    def translucent(name):
        o = doc.xref_object(int(gs[name]))
        bm = re.search(r'/BM /(\w+)', o)
        return (any(float(v) < 1 for v in re.findall(r'/(?:CA|ca) ([\d.]+)', o))
                or (bm is not None and bm.group(1) not in ('Normal', 'Compatible')))
    data = b''.join(doc.xref_stream(int(x)) + b'\n'
                    for x in re.findall(r'(\d+) 0 R', doc.xref_get_key(page.xref, 'Contents')[1]))
    tok = re.compile(rb'/[^\s/\[\]()<>{}%]+|\((?:\\.|[^\\)])*\)|<[0-9A-Fa-f\s]*>|\[|\]|[^\s/\[\]()<>{}%]+')
    stack, last, out = [False], b'', set()
    for t in tok.findall(data):
        if t == b'q':
            stack.append(stack[-1])
        elif t == b'Q':
            stack.pop()
        elif t == b'gs':
            stack[-1] = translucent(last.decode()[1:])
        elif t == b'Do' and stack[-1] and last.decode()[1:] in xo:
            out.add(int(xo[last.decode()[1:]]))
        last = t
    return sorted(out)


def render(pdf, page, xref, v, scale, clip, empty=()):
    """The page with its painting replaced by a flat grey level v (and the form XObjects in `empty` emptied)."""
    d = pymupdf.open(pdf)
    for x in empty:
        d.update_stream(x, b'')  # an empty form draws nothing
    p = d[page]
    px = pymupdf.Pixmap(pymupdf.csRGB, pymupdf.IRect(0, 0, 8, 8), False)
    px.set_rect(px.irect, (v, v, v))
    p.replace_image(xref, pixmap=px)
    pix = p.get_pixmap(matrix=pymupdf.Matrix(scale, scale), clip=clip)
    return np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, 3).astype(np.float32)


def mode_colour(img):
    """The most common colour of a render (the painting's flat stand-in, where nothing is drawn over it)."""
    v, n = np.unique(img.reshape(-1, 3), axis=0, return_counts=True)
    assert n.max() > 0.2 * len(img.reshape(-1, 3)), 'no flat stand-in colour dominates the render'
    return v[n.argmax()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pdf', required=True)
    ap.add_argument('--out', required=True, help='png')
    ap.add_argument('--scale', type=float, default=3.0, help='output px per PDF pt')
    ap.add_argument('--clip', help='x0,y0,x1,y1 in pt (default: the whole page)')
    ap.add_argument('--page', type=int, default=0)
    ap.add_argument('--xref', type=int, help="the painting's image xref (default: the largest image)")
    ap.add_argument('--background', help='a sharper raster of the whole page')
    ap.add_argument('--flattened', action='store_true',
                    help='the --background is the whole map flattened, translucent layers included: take the '
                         "layer's coverage without them (Keystone)")
    ap.add_argument('--resample', type=int, action='append', default=[],
                    help='instead of matting: replace this image (xref; repeat for several) with a copy upscaled '
                         'with Lanczos to the output scale, then render the page as it is, so any clip or '
                         'placement is kept (Park City: its painting and the High Meadow Park inset\'s, clipped '
                         'to the inset frame)')
    a = ap.parse_args()
    S = a.scale
    doc = pymupdf.open(a.pdf)
    page = doc[a.page]
    clip = pymupdf.Rect(*[float(v) for v in a.clip.split(',')]) if a.clip else page.rect
    if a.resample:
        for x in a.resample:
            pm = pymupdf.Pixmap(doc, x)
            if pm.colorspace.n != 3 or pm.alpha:
                pm = pymupdf.Pixmap(pymupdf.csRGB, pm)
            paint = Image.open(io.BytesIO(pm.tobytes('png'))).convert('RGB')
            r = page.get_image_rects(x)[0]
            f = S * r.width / paint.width  # output px per painting px
            if f > 1:
                big = paint.resize((round(paint.width * f), round(paint.height * f)), Image.LANCZOS)
                page.replace_image(x, pixmap=pymupdf.Pixmap(pymupdf.csRGB, big.width, big.height, big.tobytes(), False))
        pix = page.get_pixmap(matrix=pymupdf.Matrix(S, S), clip=clip)
        pix.save(a.out)
        print(a.out, (pix.width, pix.height), 'images resampled', a.resample)
        return
    xref = a.xref or max(page.get_images(full=True), key=lambda im: im[2] * im[3])[0]
    W = render(a.pdf, a.page, xref, 255, S, clip)
    B = render(a.pdf, a.page, xref, 0, S, clip)
    alpha = np.clip(1 - (W - B).mean(axis=2) / 255.0, 0, 1)
    col = np.where(alpha[..., None] > 1e-3, B / np.maximum(alpha[..., None], 1e-3), 0)
    if a.background:
        cdn = Image.open(a.background).convert('RGB')
        sx, sy = cdn.width / page.rect.width, cdn.height / page.rect.height
        bg = cdn.transform((W.shape[1], W.shape[0]), Image.AFFINE,
                           (1 / (S / sx), 0, clip.x0 * sx, 0, 1 / (S / sy), clip.y0 * sy), resample=Image.BICUBIC)
        bg = np.asarray(bg, np.float32)
    else:
        # the painting decoded by MuPDF (its ICC profile applied), upscaled with Lanczos to where it is placed
        pm = pymupdf.Pixmap(doc, xref)
        if pm.colorspace.n != 3:
            pm = pymupdf.Pixmap(pymupdf.csRGB, pm)
        paint = Image.open(io.BytesIO(pm.tobytes('png'))).convert('RGB')
        r = page.get_image_rects(xref)[0]
        big = paint.resize((round(r.width * S), round(r.height * S)), Image.LANCZOS)
        canvas = Image.new('RGB', (W.shape[1], W.shape[0]))
        canvas.paste(big, (round((r.x0 - clip.x0) * S), round((r.y0 - clip.y0) * S)))
        bg = np.asarray(canvas, np.float32)
    if a.flattened:
        assert a.background, '--flattened needs --background'
        forms = translucent_forms(doc, page)
        Wo = render(a.pdf, a.page, xref, 255, S, clip, forms)
        Bo = render(a.pdf, a.page, xref, 0, S, clip, forms)
        # the stand-ins as rendered: a CMYK painting's black comes out as (8,6,6), not 0 (Keystone), which the plain
        # formula takes for a faint layer over the whole painting. Their most common colours without the
        # translucent forms are the bare stand-ins (with them, a wash over the whole page would count: Breckenridge)
        kw, kb = mode_colour(Wo), mode_colour(Bo)
        span = np.maximum(kw - kb, 1)
        alpha = np.clip(1 - ((W - B) / span).mean(axis=2), 0, 1)
        col = np.where(alpha[..., None] > 1e-3,
                       (B - kb * (1 - alpha[..., None])) / np.maximum(alpha[..., None], 1e-3), 0)
        cover = np.clip(1 - ((Wo - Bo) / span).mean(axis=2), 0, 1)
        out = col * cover[..., None] + bg * (1 - cover[..., None])
        print('translucent forms left to the flattened background:', forms, '; stand-ins rendered as', kw, kb)
    else:
        out = col * alpha[..., None] + bg * (1 - alpha[..., None])
    Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save(a.out)
    print(a.out, (W.shape[1], W.shape[0]), 'xref', xref, 'vector coverage', round(float((alpha > 0.5).mean()), 3))
    if not a.background:
        plain = page.get_pixmap(matrix=pymupdf.Matrix(S, S), clip=clip)
        P0 = np.frombuffer(plain.samples, np.uint8).reshape(plain.height, plain.width, 3).astype(np.float32)
        m = alpha < 0.01
        print('mean abs diff vs the plain render where there are no vectors:', round(float(np.abs(out[m] - P0[m]).mean()), 2))


if __name__ == '__main__':
    main()
