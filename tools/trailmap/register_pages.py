"""Register a PDF page (in points) on a map image (in px): the affine that puts an older export's strokes, text and
symbols on this season's image of the same artwork (Wildcat: this season's PDF has outlined names and flattened
lines, an earlier export has them live; Heavenly: the current map is an image only, the 2022-23 PDF has the
vectors). SIFT features on a render of the page and on the image, Lowe's ratio test, RANSAC.

    python3 tools/trailmap/register_pages.py --pdf work/heavenly/heavenly_2022.pdf --image work/heavenly/scene7.png \\
        --box 0,0,3652,2984 [--clip 0,0,1170,960] [--page 0]

--clip is the part of the page to match (pt; default the whole page), --box the part of the image (px; default the
whole image); the page is rendered at the box's scale. Prints the matches, the RANSAC inliers, the inliers'
median and 90th-percentile residual, and the affine as resort.py keeps it (AFFINE: x = a pt_x + b pt_y + c,
y = d pt_x + e pt_y + f). Fix it in the resort's resort.py rather than re-matching on every regeneration, then check
that every old name lands on the image's own name (crops), and look at every place the two differ.

--ref registers an image instead of a PDF page (an interactive map's painting: vicomap.py), in its own units:
--ref-scale units per px of it (an SVG's units where the painting is drawn scaled), --clip in those units.
"""
import argparse

import cv2
import numpy as np
import pymupdf
from PIL import Image

Image.MAX_IMAGE_PIXELS = None


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('--pdf')
    ap.add_argument('--ref', help='an image to register instead of a PDF page')
    ap.add_argument('--ref-scale', type=float, default=1.0, help="--ref's units per px of it")
    ap.add_argument('--page', type=int, default=0)
    ap.add_argument('--clip', help='x0,y0,x1,y1 of the page (pt)')
    ap.add_argument('--image', required=True)
    ap.add_argument('--box', help='x0,y0,x1,y1 of the image (px)')
    ap.add_argument('--features', type=int, default=8000)
    ap.add_argument('--ratio', type=float, default=0.7, help="Lowe's ratio test")
    ap.add_argument('--thresh', type=float, default=1.5, help='RANSAC reprojection threshold, px')
    a = ap.parse_args()
    assert bool(a.pdf) != bool(a.ref), 'one of --pdf and --ref'
    if a.pdf:
        pg = pymupdf.open(a.pdf)[a.page]
        clip = pymupdf.Rect(*map(float, a.clip.split(','))) if a.clip else pg.rect
    else:
        ref = Image.open(a.ref).convert('RGB')
        clip = pymupdf.Rect(*map(float, a.clip.split(','))) if a.clip else \
            pymupdf.Rect(0, 0, ref.width * a.ref_scale, ref.height * a.ref_scale)
    img = Image.open(a.image).convert('RGB')
    bx0, by0, bx1, by1 = map(int, a.box.split(',')) if a.box else (0, 0, *img.size)
    z = (bx1 - bx0) / clip.width
    if a.pdf:
        pix = pg.get_pixmap(matrix=pymupdf.Matrix(z, z), clip=clip, alpha=False)
        A = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, 3)
    else:
        r = a.ref_scale
        A = np.asarray(ref.crop((round(clip.x0 / r), round(clip.y0 / r), round(clip.x1 / r), round(clip.y1 / r)))
                       .resize((round(clip.width * z), round(clip.height * z)), Image.LANCZOS))
    B = np.asarray(img)[by0:by1, bx0:bx1]
    sift = cv2.SIFT_create(a.features)
    ka, da = sift.detectAndCompute(cv2.cvtColor(A, cv2.COLOR_RGB2GRAY), None)
    kb, db = sift.detectAndCompute(cv2.cvtColor(np.ascontiguousarray(B), cv2.COLOR_RGB2GRAY), None)
    good = [p for p, q in cv2.BFMatcher().knnMatch(da, db, k=2) if p.distance < a.ratio * q.distance]
    src = np.float32([ka[g.queryIdx].pt for g in good]) / z + np.float32([clip.x0, clip.y0])  # page pt
    dst = np.float32([kb[g.trainIdx].pt for g in good]) + np.float32([bx0, by0])  # image px
    M, inl = cv2.estimateAffine2D(src, dst, ransacReprojThreshold=a.thresh, maxIters=20000, confidence=0.999)
    inl = inl.ravel().astype(bool)
    res = np.linalg.norm(src[inl] @ M[:, :2].T + M[:, 2] - dst[inl], axis=1)
    print(f'{len(good)} matches, {inl.sum()} inliers, residual median {np.median(res):.3f} px, '
          f'90th percentile {np.percentile(res, 90):.3f} px')
    (a_, b_, c_), (d_, e_, f_) = M
    print(f'AFFINE = ({a_:.7f}, {b_:.7f}, {c_:.4f}, {d_:.7f}, {e_:.7f}, {f_:.4f})')


if __name__ == '__main__':
    main()
