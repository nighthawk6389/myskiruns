"""Stratton: the map image, line pieces, printed names and symbols, for tools/trailmap/pdf_resort.py.

    python3 tools/trailmap/resorts/stratton/prepare.py      # regen.sh runs it

- Image: the 2025-26 PDF's one image (the whole page, flattened: tools/trailmap/extract_pdf_image.py), cropped to the
  painting above the legend (resort.BOX).
- Lines: the 2020-21 export's 1 pt strokes in the runs' colours, green, blue and black (dashed: one stroke per line),
  on the image's grid (resort.CLIP and SCALE come from the registration, resort.AFFINE), its legend and uphill box
  left out. The lines this season no longer draws, and those it draws anew, are decisions (decisions.py).
- Names: the 2020-21 export's text in the names' style (resort.is_name), less what this season no longer prints
  (resort.GONE), the labels it prints elsewhere or shorter moved there (resort.MOVED: the old label's characters
  spaced along the new label's line), and the new ones (resort.NEW_LABELS).
- Symbols: the 2020-21 export's fills (tools/trailmap/pdf_symbols.py: green circles, blue squares, black diamonds,
  the diamonds by a turned label drawn as squares; the glades' circles and squares in a green and a blue of their
  own, up to 7.2 pt), less resort.GONE's, plus resort.NEW_SYMBOLS.

Writes, in $STRATTON_WORK (default work/stratton): map.png, pieces.json, printed.json (labels, 2020-21 PDF points),
symbols.json (map px).
"""
import json
import math
import os
import subprocess
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '../../../..'))
T = os.path.join(REPO, 'tools/trailmap')
sys.path.insert(0, HERE)
import resort as R  # noqa: E402

Image.MAX_IMAGE_PIXELS = None
W = os.path.abspath(os.environ.get('STRATTON_WORK', os.path.join(REPO, 'work/stratton')))
PDF = os.path.join(W, 'stratton_2025-26.pdf')
OLD = os.path.join(W, 'stratton_2020-21.pdf')
LINES = {'green': (0.05, 0.49, 0.25), 'blue': (0.08, 0.46, 0.74), 'black': (0.14, 0.12, 0.13)}
SYMBOLS = {'circle': (0.05, 0.49, 0.25), 'square': (0.08, 0.46, 0.74), 'diamond': (0.01, 0.02, 0.02)}
# the glades' symbols, a little larger in their own blue and green (their diamonds the runs' black)
GLADE_SYMBOLS = {'circle': (0.0, 0.53, 0.4), 'square': (0.0, 0.45, 0.74), 'diamond': (0.5, 0.5, 0.5)}


def run(*cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode:
        sys.exit(f'{" ".join(cmd)} failed:\n{p.stdout}{p.stderr}')
    return p.stdout


def rgb(c):
    return ','.join(str(v) for v in c)


def box(b):
    return ','.join(str(v) for v in b)


def px(p):
    a = R.AFFINE
    return a[0] * p[0] + a[1] * p[1] + a[2], a[3] * p[0] + a[4] * p[1] + a[5]


def pt(q):
    """Map px -> 2020-21 page points (the affine inverted)."""
    a, b, c, d, e, f = R.AFFINE
    det = a * e - b * d
    x, y = q[0] - c, q[1] - f
    return [round((e * x - b * y) / det, 3), round((a * y - d * x) / det, 3)]


def image():
    out = os.path.join(W, 'map.png')
    if not os.path.exists(out) or os.environ.get('IMAGES'):
        full = os.path.join(W, 'page2025.png')
        run('python3', '-I', f'{T}/extract_pdf_image.py', PDF, full)
        Image.open(full).convert('RGB').crop(R.BOX).save(out)
    return out


def lines():
    f = os.path.join(W, 'pieces.json')
    args = ['python3', '-I', f'{T}/extract_pdf_vectors.py', OLD, '--clip=' + box(R.CLIP), '--scale', str(R.SCALE),
            '--min-width', '0.9', '--max-width', '1.1', '--min-length', '1', '--out', f]
    for cls, c in LINES.items():
        args += ['--color', f'{cls}={rgb(c)}']
    for b in R.LEGEND:
        args += ['--exclude', box(b)]
    print(' ', run(*args).strip().splitlines()[-1].replace(W + '/', ''))


def along(first, last, ref):
    """Characters spaced along first-last (map px) as ref's (map px) are along its own line."""
    s = [0.0]
    for p, q in zip(ref, ref[1:]):
        s.append(s[-1] + math.dist(p, q))
    s = [v / s[-1] if s[-1] else 0 for v in s] if len(ref) > 1 else [0.5]
    return [(first[0] + (last[0] - first[0]) * t, first[1] + (last[1] - first[1]) * t) for t in s]


def names():
    f = os.path.join(W, 'labels_raw.json')
    run('python3', '-I', f'{T}/pdf_labels.py', OLD, '--out', f)
    raw = [l for l in json.load(open(f)) if R.is_name(l)]

    def near(l, text, q):
        return l['text'] == text and math.dist(px(l['c']), q) < 40
    gone = [l for l in raw if any(near(l, t, q) for t, q in R.GONE['labels'])]
    assert len(gone) == len(R.GONE['labels']), ('GONE: a label not found', R.GONE['labels'])
    out = [l for l in raw if l not in gone]
    for (text, q), new, first, last in R.MOVED:
        l = next((l for l in out if near(l, text, q)), None)
        assert l, ('MOVED: no label', text, q)
        k = len(new.replace(' ', ''))
        assert text.replace(' ', '').startswith(new.replace(' ', '')), ('MOVED: not a shortening', text, new)
        pts = along(first, last, [px(p) for p in l['pts'][:k]])
        l.update(text=new, pts=[pt(p) for p in pts], c=pt((sum(p[0] for p in pts) / k, sum(p[1] for p in pts) / k)))
    model = next(l for l in out if l['text'] == 'BEELINE')
    for new, first, last in R.NEW_LABELS:
        k = len(new.replace(' ', ''))
        pts = along(first, last, [(i, 0) for i in range(k)])
        out.append({**model, 'seq': len(raw) + len(out), 'text': new, 'pts': [pt(p) for p in pts],
                    'c': pt((sum(p[0] for p in pts) / k, sum(p[1] for p in pts) / k))})
    json.dump(out, open(os.path.join(W, 'printed.json'), 'w'), indent=0)
    return out


def symbols():
    syms = []
    for k, cols in enumerate((SYMBOLS, GLADE_SYMBOLS)):
        f = os.path.join(W, f'symbols_raw{k}.json')
        args = ['python3', '-I', f'{T}/pdf_symbols.py', OLD, '--clip=' + box(R.CLIP), '--scale', str(R.SCALE),
                '--max-diamond', '6.5', '--max-square', '8', '--max-size', '8', '--out', f]
        for t, c in cols.items():
            args += [f'--{t}', rgb(c)]
        for b in R.LEGEND:
            args += ['--exclude', box(b)]
        run(*args)
        syms += json.load(open(f))
    keep = [s for s in syms if not any(math.dist(s['src'], q) < 6 for q in R.GONE['symbols'])]
    assert len(syms) - len(keep) == len(R.GONE['symbols']), 'GONE: a symbol not found'
    keep += [{'type': t, 'src': list(q), 'sizePt': 4.4} for t, q in R.NEW_SYMBOLS]
    json.dump(keep, open(os.path.join(W, 'symbols.json'), 'w'), indent=0)
    return keep


if __name__ == '__main__':
    os.makedirs(W, exist_ok=True)
    image()
    lines()
    labels = names()
    syms = symbols()
    print(f'  {len(labels)} labels, {len(syms)} symbols')
