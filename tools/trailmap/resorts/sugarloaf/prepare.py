"""Sugarloaf: the map image, line pieces, printed names and symbols from the 2025-26 trail-map PDF, for
tools/trailmap/pdf_resort.py.

    python3 tools/trailmap/resorts/sugarloaf/prepare.py      # regen.sh runs it

- Image: the page's painting is only 1590x1146 for 1530x1323 pt, so the map image is the vector layer matted over
  a smooth upscale of it (tools/trailmap/matte_pdf_layer.py), clipped to the map above the key.
- Lines: 1.2 pt green and blue strokes and 1.15 pt black ones, and the Golden Road's orange dashes (the legend's
  other dashed routes are left out: egresses, the King Pine X-Cut, a hiking trail and a cat road, none in the key;
  its blue dashed logging roads come in with the blue). The Snowfields inset (top right) is a small raster with its
  lines baked in: its trails are traced on crops (decisions.py TRACED).
- Names: outlined glyphs (tools/trailmap/pdf_glyphs.py; each shape's letter, read once on its contact sheets, is in
  letters.json here), plus the east side's names, set as text (GillSansNova-Bold, 5.1-5.3 pt by its matrix). Glades
  and connecting trails are printed as red numbered circles that refer to the key below the map (KEY in resort.py,
  read off the key): each circle becomes a name at its centre. Digits 6 and 9 are one outline turned over: the
  numbers are upright, so the end with the loop decides.
- Symbols: green circles, blue squares, black diamonds; two diamonds touching corner to corner (as the Snowfields
  prints them) are a double diamond.

Writes, in $SUGARLOAF_WORK (default work/sugarloaf): map.png, pieces.json, printed.json, symbols.json.
"""
import json
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '../../../..'))
T = os.path.join(REPO, 'tools/trailmap')
sys.path.insert(0, HERE)
from resort import CLIP, KEY, SCALE  # noqa: E402

W = os.path.abspath(os.environ.get('SUGARLOAF_WORK', os.path.join(REPO, 'work/sugarloaf')))
PDF = os.path.join(W, 'sugarloaf.pdf')
LETTERS = os.path.join(HERE, 'letters.json')
SNOWFIELDS = (1265, 0, 1530, 350)  # the inset (front side and back side), PDF points
KEY_AREA = (0, 955, 1530, 1323)  # the key, legend and lift list below the map
GLYPH_COLORS = ['black=0,0,0', 'red=0.94,0.23,0.17', 'blue=0,0.4,0.64', 'green=0,0.53,0.32']


def run(*cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode:
        sys.exit(f'{" ".join(cmd)} failed:\n{p.stdout}{p.stderr}')
    return p.stdout


def inside(p, r):
    return r[0] <= p[0] <= r[2] and r[1] <= p[1] <= r[3]


def image():
    if not os.path.exists(os.path.join(W, 'map.png')) or os.environ.get('IMAGES'):
        run('python3', f'{T}/matte_pdf_layer.py', '--pdf', PDF, '--out', os.path.join(W, 'map.png'), '--scale',
            str(SCALE), '--clip', ','.join(map(str, CLIP)), '--xref', '159')


def lines():
    run('python3', f'{T}/extract_pdf_vectors.py', PDF, '--clip', ','.join(map(str, CLIP)), '--scale', str(SCALE),
        '--color', 'green=0,0.53,0.32', '--color', 'blue=0,0.4,0.64', '--color', 'black=0,0,0',
        '--color', 'orange=0.92,0.61,0.16', '--min-width', '1.1',
        '--max-width', '1.25', '--min-length', '1', '--exclude', ','.join(map(str, SNOWFIELDS)),
        '--out', os.path.join(W, 'pieces.json'))


_drawings = None


def digit(g):
    """6 or 9 for a glyph of the merged 6/9 outline: its hole (the loop) is in the bottom half of a 6 and the top
    half of a 9 (the numbers are printed upright)."""
    global _drawings
    if _drawings is None:
        import pymupdf
        _drawings = {d['seqno']: d for d in pymupdf.open(PDF)[0].get_drawings()}
    d = _drawings[g['seq']]
    subs, cur = [], []
    for it in d['items']:
        if cur and math.dist((it[1].x, it[1].y), (cur[-1][-1].x, cur[-1][-1].y)) > 0.01:
            subs.append(cur)
            cur = []
        cur.append(it)
    subs.append(cur)
    boxes = []
    for sub in subs:
        ys = [p.y for it in sub for p in it[1:] if hasattr(p, 'y')]
        boxes.append((max(ys) - min(ys), (max(ys) + min(ys)) / 2))
    hole = min(boxes)[1]  # the smaller contour
    r = d['rect']
    return '6' if hole > (r.y0 + r.y1) / 2 else '9'


def labels():
    G = os.path.join(W, 'glyphs.json')
    # --max-size 12: the double diamonds drawn as one outline are up to 11.6 pt tall (the zones' 13.5 pt ones stay out)
    args = ['python3', f'{T}/pdf_glyphs.py', 'collect', PDF, '--out', G, '--exclude', '1290,960,1530,1323',
            '--max-size', '12']
    for c in GLYPH_COLORS:
        args += ['--color', c]
    run(*args)
    f = os.path.join(W, 'glyph_labels.json')
    run('python3', f'{T}/pdf_glyphs.py', 'labels', PDF, '--glyphs', G, '--letters', LETTERS, '--out', f,
        '--square', 'blue', '--diamond', 'black', '--circle', 'green', '--space', '1.2', '--double-dist', '1.3',
        '--single', 'red')
    d = json.load(open(f))
    glyphs = json.load(open(G))['glyphs']
    at = {(round(g['c'][0], 2), round(g['c'][1], 2)): g for g in glyphs}
    out, keyed = [], []
    for lab in d['labels']:
        c = lab['c']
        if not inside(c, CLIP) or inside(c, KEY_AREA):
            continue
        if lab['color'] == 'red':  # a numbered circle: the key's name, at the circle
            gs = sorted((at[(round(p[0], 2), round(p[1], 2))] for p in lab['pts']), key=lambda g: g['c'][0])
            text = ''.join(digit(g) if lab_ch in '69' else lab_ch
                           for g, lab_ch in zip(gs, [ch for ch in sorted_chars(lab, gs)]))
            if not text.isdigit() or int(text) not in KEY:
                print('  red label not in the key:', text, [round(v) for v in c])
                continue
            keyed.append(int(text))
            out.append({'text': KEY[int(text)], 'font': 'key', 'number': int(text), 'size': lab['size'],
                        'seq': lab['seq'], 'color': 'key', 'pts': [c], 'c': c})
            continue
        if lab['color'] != 'black':
            continue
        out.append({'text': lab['text'], 'font': 'glyph', 'size': lab['size'], 'seq': lab['seq'], 'color': 'black',
                    'pts': lab['pts'], 'c': lab['c']})
    f2 = os.path.join(W, 'text_labels.json')
    run('python3', f'{T}/pdf_labels.py', PDF, '--out', f2)
    for lab in json.load(open(f2)):
        if lab['font'] == 'GillSansNova-Bold' and 5.0 <= lab['size'] <= 5.4 and tuple(lab['color']) == (0, 0, 0) \
                and inside(lab['c'], CLIP) and not inside(lab['c'], KEY_AREA):
            out.append({'text': ' '.join(lab['text'].split()), 'font': lab['font'], 'size': lab['size'],
                        'seq': lab['seq'], 'color': 'black', 'pts': lab['pts'], 'c': lab['c']})
    os.remove(f2)
    json.dump(out, open(os.path.join(W, 'printed.json'), 'w'), indent=0)
    dup = sorted({n for n in keyed if keyed.count(n) > 1})
    missing = sorted(set(KEY) - set(keyed))
    print(len(out), 'labels;', len(keyed), 'numbered circles', f'(twice: {dup})' if dup else '',
          f'; key numbers on no circle: {missing}' if missing else '')
    x0, y0 = CLIP[:2]
    syms = [s for s in d['symbols'] if inside(s['c'], CLIP) and not inside(s['c'], KEY_AREA)]
    json.dump([{'type': s['t'], 'src': [round((s['c'][0] - x0) * SCALE), round((s['c'][1] - y0) * SCALE)],
                'sizePt': 3.5} for s in syms], open(os.path.join(W, 'symbols.json'), 'w'), indent=0)
    print(len(syms), 'symbols')


def sorted_chars(lab, gs):
    """The label's characters in the order of gs (left to right): pdf_glyphs.py joins them in drawing order."""
    order = sorted(range(len(lab['pts'])), key=lambda k: lab['pts'][k][0])
    chars = [ch for ch in lab['text'] if ch != ' ']
    return [chars[k] for k in order]


if __name__ == '__main__':
    image()
    lines()
    labels()
