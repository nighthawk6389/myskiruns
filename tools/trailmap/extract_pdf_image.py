"""Get the best raster of a resort trail-map PDF and report whether it has
vector content worth using instead.

    python3 tools/trailmap/extract_pdf_image.py map.pdf out.png

Prints page size, embedded images, text words and vector drawings. If the PDF
has real text/vector layers, extract those instead of doing CV (exact names
and lines). Otherwise the largest embedded image is written losslessly - use
it as the pipeline input; resort JPGs are often resampled and chroma
subsampled (4:2:0), which blurs thin coloured lines and small text.

Requires: pip install pymupdf
"""
import sys

import pymupdf


def main(pdf_path: str, out_path: str) -> None:
    doc = pymupdf.open(pdf_path)
    print('metadata:', doc.metadata)
    best = None
    for pno, page in enumerate(doc):
        words = page.get_text('words')
        drawings = page.get_drawings()
        print(f'page {pno}: {page.rect.width:.0f}x{page.rect.height:.0f}pt, '
              f'{len(words)} text words, {len(drawings)} vector drawings')
        if words:
            print('  sample text:', ' '.join(w[4] for w in words[:40]))
        for img in page.get_images(full=True):
            xref, w, h = img[0], img[2], img[3]
            print(f'  image xref {xref}: {w}x{h}')
            if best is None or w * h > best[1] * best[2]:
                best = (xref, w, h)
    if best is None:
        sys.exit('no embedded raster images')
    pix = pymupdf.Pixmap(doc, best[0])
    if pix.n - pix.alpha > 3:
        pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
    pix.save(out_path)
    print(f'wrote {out_path} ({best[1]}x{best[2]}, lossless)')


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
