"""Check a matted map image (matte_pdf_layer.py, or a resort's own matte.py) against the PDF's own render: where only
the painting shows, where a translucent form (a wash, a Multiply band, a slow zone) lies over it, and where opaque
vector content is drawn. A matte over a flattened background (Vail Resorts' CDN copies) that applied the
translucent layers a second time shows up as a bias in the first two (Breckenridge's was 10 levels too light and its
bands 27 too dark); the third should be 0.

    python3 tools/trailmap/matte_check.py --pdf work/keystone/keystone.pdf --xref 23 --scale 2.8 \\
        --clip 0,90,1530,1080 --image work/keystone/map.png [--compare old_map.png] [--background scene7.jpg]

--xref: the painting's image xref (default: the largest image); --scale and --clip as the matte was made. Prints,
per area (the painting under no translucent form or a light one such as a 10% wash; under one of 20% or more,
such as a band; opaque content), the mean of (image - PDF render) in R, G, B: the PDF render paints with the embedded low-resolution
painting, so per-pixel differences are large but the means should agree within a few levels (the background's own
colour rendition aside, which --background prints the same way). --compare prints another image's numbers too.
"""
import argparse

import numpy as np
import pymupdf
from PIL import Image

from matte_pdf_layer import mode_colour, render, translucent_forms

Image.MAX_IMAGE_PIXELS = None


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('--pdf', required=True)
    ap.add_argument('--page', type=int, default=0)
    ap.add_argument('--xref', type=int)
    ap.add_argument('--scale', type=float, required=True)
    ap.add_argument('--clip', required=True, help='x0,y0,x1,y1 in pt')
    ap.add_argument('--image', required=True, help='the matted map (PNG at --scale over --clip)')
    ap.add_argument('--compare', action='append', default=[], help='another image to measure the same way')
    ap.add_argument('--background', help='the background raster of the whole page, stretched to it as the matte does')
    a = ap.parse_args()
    doc = pymupdf.open(a.pdf)
    page = doc[a.page]
    clip = pymupdf.Rect(*[float(v) for v in a.clip.split(',')])
    xref = a.xref or max(page.get_images(full=True), key=lambda im: im[2] * im[3])[0]
    pix = page.get_pixmap(matrix=pymupdf.Matrix(a.scale, a.scale), clip=clip)
    ref = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, 3).astype(np.float32)
    W, B = render(a.pdf, a.page, xref, 255, a.scale, clip), render(a.pdf, a.page, xref, 0, a.scale, clip)
    forms = translucent_forms(doc, page)
    Wo, Bo = (render(a.pdf, a.page, xref, v, a.scale, clip, forms) for v in (255, 0))
    span = np.maximum(mode_colour(Wo) - mode_colour(Bo), 1)  # the bare stand-ins, as matte_pdf_layer.py --flattened
    alpha = np.clip(1 - ((W - B) / span).mean(axis=2), 0, 1)
    cover = np.clip(1 - ((Wo - Bo) / span).mean(axis=2), 0, 1)
    areas = {'painting (forms under 20%)': (cover < 1e-3) & (alpha < 0.2),
             'painting under a form 20%+': (cover < 1e-3) & (alpha >= 0.2),
             'opaque vector content': cover > 0.999}
    print(f'translucent forms: {forms}')
    print('pixels: ' + ', '.join(f'{k} {m.mean():.1%}' for k, m in areas.items()))
    images = [('image', a.image)] + [(f'compare {i + 1}', p) for i, p in enumerate(a.compare)]
    for name, path in images:
        img = np.asarray(Image.open(path).convert('RGB'), np.float32)
        assert img.shape == ref.shape, f'{path}: {img.shape[1]}x{img.shape[0]}, the render is {ref.shape[1]}x{ref.shape[0]}'
        print(f'{name} ({path}), mean minus the PDF render (R, G, B):')
        for k, m in areas.items():
            print(f'  {k:26s}', np.round((img - ref)[m].mean(axis=0), 1) if m.any() else '-')
    if a.background:
        cdn = Image.open(a.background).convert('RGB')
        sx, sy = cdn.width / page.rect.width, cdn.height / page.rect.height
        bg = np.asarray(cdn.transform((W.shape[1], W.shape[0]), Image.AFFINE, (1 / (a.scale / sx), 0, clip.x0 * sx, 0,
                                                                               1 / (a.scale / sy), clip.y0 * sy),
                                      resample=Image.BICUBIC), np.float32)
        print(f'background ({a.background}), mean minus the PDF render (R, G, B):')
        for k, m in areas.items():
            print(f'  {k:26s}', np.round((bg - ref)[m].mean(axis=0), 1) if m.any() else '-')


if __name__ == '__main__':
    main()
