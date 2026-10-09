"""Deer Valley: where the 2025-11-04 image (the map image) differs from the 2025-10-16 PDF it takes its lines, names
and symbols from (the playbook, Part 1, recipe D, step 2). Run after regen.sh (it reads work/deer-valley/).

    python3 tools/trailmap/resorts/deer-valley/checks/editions.py labels [--sheets N]   # names, most changed first
    python3 tools/trailmap/resorts/deer-valley/checks/editions.py lines                 # pieces off the image's ink
    python3 tools/trailmap/resorts/deer-valley/checks/editions.py symbols               # symbols off the image's ink
    python3 tools/trailmap/resorts/deer-valley/checks/editions.py extra                 # the image's lines on no piece

labels: per printed label, the share of its dark text pixels (the PDF page rendered on the image's grid, and the
image) with no dark pixel of the other within 1 px; with --sheets, contact sheets of the N most changed (the image
above, the PDF below: work/deer-valley/editions/labels_*.png). Read them: a score is no evidence (Ham Bug, now
Humbug, ranks 25th; the painting's blur scores too).
lines: per line piece, the share of its points (every 2 px) with a pixel of its colour within 2 px on the image.
symbols: per named symbol, whether the image has the symbol's colour at its centre.
extra: the image's green and blue line ink farther than 6 px from every piece and stretch (pieces_cut.json): lines
the November image draws that the October PDF doesn't (Gilt Edge's stub), as clusters of 40 px or more with a crop
each in work/deer-valley/editions/extra_*.png (black is left out: the painting's tree shadows match it).
"""
import argparse
import json
import math
import os
import sys

import numpy as np
import pymupdf
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '../../../../..'))
sys.path.insert(0, os.path.dirname(HERE))
from resort import AFFINE, BOX  # noqa: E402

Image.MAX_IMAGE_PIXELS = None
W = os.path.abspath(os.environ.get('DEER_VALLEY_WORK', os.path.join(REPO, 'work/deer-valley')))
COLOUR = {'green': (0, 173, 77), 'blue': (0, 173, 240), 'black': (36, 31, 33)}


def to_img(p):
    """PDF points -> px of the map image (BOX of the November image)."""
    return (AFFINE[0] * p[0] + AFFINE[1] * p[1] + AFFINE[2] - BOX[0], AFFINE[3] * p[0] + AFFINE[4] * p[1] + AFFINE[5] - BOX[1])


def pdf_render(size):
    """The October page rendered on the map image's grid (the affine's shear left out)."""
    s = (AFFINE[0] + AFFINE[4]) / 2
    x0, y0 = (BOX[0] - AFFINE[2]) / AFFINE[0], (BOX[1] - AFFINE[5]) / AFFINE[4]
    page = pymupdf.open(os.path.join(W, 'deervalley_2025-10.pdf'))[0]
    clip = pymupdf.Rect(x0, y0, x0 + size[0] / s, y0 + size[1] / s) & page.rect
    pix = page.get_pixmap(matrix=pymupdf.Matrix(s, s), clip=clip)
    out = Image.new('RGB', size, (128, 128, 128))
    out.paste(Image.frombytes('RGB', (pix.width, pix.height), pix.samples),
              (round((clip.x0 - x0) * s), round((clip.y0 - y0) * s)))
    return out


def labels(a, img):
    import cv2
    pdf = pdf_render(img.size)
    nov, oct_ = np.asarray(img.convert('L')), np.asarray(pdf.convert('L'))
    k = np.ones((3, 3), np.uint8)
    rows = []
    for lab in json.load(open(os.path.join(W, 'printed.json')))['labels']:
        P = [to_img(p) for p in lab['pts']]
        x0, y0 = max(0, int(min(p[0] for p in P)) - 9), max(0, int(min(p[1] for p in P)) - 9)
        x1, y1 = int(max(p[0] for p in P)) + 10, int(max(p[1] for p in P)) + 10
        A, B = nov[y0:y1, x0:x1] < 100, oct_[y0:y1, x0:x1] < 100
        if not B.any():
            continue
        dA = cv2.dilate(A.astype(np.uint8), k).astype(bool)
        dB = cv2.dilate(B.astype(np.uint8), k).astype(bool)
        rows.append(((B & ~dA).sum() + (A & ~dB).sum()) / max(1, (A | B).sum()), lab['text'], lab['seq'],
                    (x0, y0, x1, y1))
    rows.sort(key=lambda r: -r[0])
    for r in rows[:40]:
        print(f'{r[0]:.3f} {r[1]!r} (seq {r[2]}) at {r[3][:2]}')
    if a.sheets:
        out = os.path.join(W, 'editions')
        os.makedirs(out, exist_ok=True)
        cells = []
        for score, text, seq, (x0, y0, x1, y1) in rows[:a.sheets]:
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            w, h = min(max(x1 - x0 + 20, 60), 320), min(max(y1 - y0 + 20, 40), 180)
            b = (int(cx - w / 2), int(cy - h / 2), int(cx + w / 2), int(cy + h / 2))
            t = Image.new('RGB', (2 * 320 + 6, 194), 'white')
            t.paste(img.crop(b), (0, 14))
            t.paste(pdf.crop(b), (326, 14))
            ImageDraw.Draw(t).text((2, 1), f'{seq} {text} ({score:.3f}): image | PDF', fill='red')
            cells.append(t)
        for s in range(0, len(cells), 20):
            chunk = cells[s:s + 20]
            sheet = Image.new('RGB', (2 * (646 + 4), 10 * 198), 'gray')
            for i, t in enumerate(chunk):
                sheet.paste(t, ((i % 2) * 650, (i // 2) * 198))
            sheet.save(os.path.join(out, f'labels_{s // 20:02d}.png'))
        print(f'{len(cells)} labels on sheets in {out}')


def near_colour(arr, x, y, rgb, r, tol):
    x0, y0 = max(0, int(x) - r), max(0, int(y) - r)
    patch = arr[y0:int(y) + r + 1, x0:int(x) + r + 1].astype(int)
    return patch.size and (np.abs(patch - rgb).max(axis=2) <= tol).any()


def lines(a, img):
    arr = np.asarray(img)
    H, Wd = arr.shape[:2]
    bad = 0
    for p in json.load(open(os.path.join(W, 'pieces.json')))['polylines']:
        pts = [(x * Wd / 100, y * H / 100) for x, y in p['points']]
        dense = []
        for u, v in zip(pts, pts[1:]):
            n = max(1, int(math.dist(u, v) / 2))
            dense += [(u[0] + (v[0] - u[0]) * k / n, u[1] + (v[1] - u[1]) * k / n) for k in range(n)]
        dense.append(pts[-1])
        ok = sum(1 for q in dense if near_colour(arr, q[0], q[1], COLOUR[p['cls']], 2, a.tol)) / len(dense)
        if ok < 0.8:
            bad += 1
            print(f'piece {p["id"]} ({p["cls"]}, {p["lengthPx"]} px): {ok:.0%} of it on its colour, from '
                  f'{[round(v) for v in pts[0]]} to {[round(v) for v in pts[-1]]}')
    print(f'{bad} pieces under 80% on their colour')


def symbols(a, img):
    arr = np.asarray(img)
    want = {'circle': 'green', 'square': 'blue', 'diamond': 'black', 'double-diamond': 'black'}
    bad = 0
    syms = json.load(open(os.path.join(W, 'named_syms.json')))
    for s in syms:
        if not near_colour(arr, s['c'][0], s['c'][1], COLOUR[want[s['t']]], 2, a.tol):
            bad += 1
            print(f'{s["name"]}: no {s["t"]} colour at {[round(v) for v in s["c"]]}')
    print(f'{bad} of {len(syms)} named symbols off their colour')


def extra(a, img):
    import cv2
    arr = np.asarray(img).astype(int)
    H, Wd = arr.shape[:2]
    ink = np.zeros((H, Wd), np.uint8)
    for cls in ('green', 'blue'):
        ink |= (np.abs(arr - COLOUR[cls]).max(axis=2) <= a.tol).astype(np.uint8)
    near = np.zeros((H, Wd), np.uint8)
    for p in json.load(open(os.path.join(W, 'pieces_cut.json')))['polylines']:
        pts = np.array([(x * Wd / 100, y * H / 100) for x, y in p['points']], np.int32)
        cv2.polylines(near, [pts], False, 1, thickness=13)
    left = ink & (1 - near)
    left = cv2.morphologyEx(left, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
    n, lab, st, _c = cv2.connectedComponentsWithStats(left)
    out = os.path.join(W, 'editions')
    os.makedirs(out, exist_ok=True)
    rows = sorted(((int(st[i][4]), tuple(int(v) for v in st[i][:4])) for i in range(1, n) if st[i][4] >= 40), reverse=True)
    for k, (area, (x, y, w, h)) in enumerate(rows):
        print(f'{area} px of line ink at {x},{y} ({w}x{h}) on no piece')
        b = (max(0, x - 60), max(0, y - 60), x + w + 60, y + h + 60)
        crop = img.crop(b)
        crop.resize((crop.width * 2, crop.height * 2)).save(os.path.join(out, f'extra_{k:02d}.png'))
    print(f'{len(rows)} clusters')


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('what', choices=['labels', 'lines', 'symbols', 'extra'])
    ap.add_argument('--sheets', type=int, default=0, help='contact sheets of the N most changed labels')
    ap.add_argument('--tol', type=int, default=60, help='colour tolerance (max channel difference)')
    a = ap.parse_args()
    img = Image.open(os.path.join(W, 'map.png')).convert('RGB')
    {'labels': labels, 'lines': lines, 'symbols': symbols, 'extra': extra}[a.what](a, img)


if __name__ == '__main__':
    main()
