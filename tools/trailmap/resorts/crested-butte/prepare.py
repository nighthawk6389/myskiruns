"""Crested Butte: each panel's map image, line pieces, printed names and symbols, for tools/trailmap/pdf_resort.py.

    python3 tools/trailmap/resorts/crested-butte/prepare.py      # regen.sh runs it

The 2025-26 trail map PDF (skicb.com's trail-maps page; skimap.org's map 36782 is the same file) has two pages: the
trail map is the second (page 1). Its painting (James Niehues's) is embedded at only 72 dpi, under an InDesign vector
layer: every run's line a filled outline (the artwork's strokes outlined) in blue, green or black, a few left as 2 to
2.5 pt strokes; names outlined glyphs in their run's colour (blue, green, a near-black) on white halos; symbols fills
(squares drawn as rectangles; the extreme terrain's double diamonds with E and X in white); lifts red, their names a
second black; the boundary dotted in the black lines' colour. The legend fills the right of the page, the partners'
band its foot, and the Teocalli Bowls inset (its runs numbered, with a key) its lower left.

- Images: the 2022-23 PDF (skimap.org's map 23099) embeds the same painting at 269 dpi (identical but for the JPEG's
  noise: compared blurred, no difference over 11 levels) and the inset's at 300: both are swapped in for this
  season's copies before the page is rendered at resort.SCALE (tools/trailmap/matte_pdf_layer.py --replace), so the
  vector layer is this season's and the painting sharp. The Teocalli Bowls panel is the inset and its key, rendered
  at 5 px per pt.
- Lines: the centre lines of the run-coloured outlines (tools/trailmap/pdf_outline_lines.py: up to 3.2 pt wide; the
  names' letters left out by their glyph shapes, and Keystone Ridge's green copy under its black letters too; a black
  outline is a line only if 7 pt long; the boundary's and the control fences' dashes, 4 to 6 pt, many to a fill, are
  never chained into a line; the black runs drawn dashed, one fill per dash in no order, are linked dash to dash
  across gaps up to 8.5 pt), plus the 1.9 to 2.6 pt strokes in the same colours (tools/trailmap/extract_pdf_vectors.py
  --append).
- Names and symbols: the glyphs in the name colours (tools/trailmap/pdf_glyphs.py; each shape's letter, read once on
  its contact sheets, is in letters.json here; symbols up to 14 pt: the diamonds are 11 tall), words split at gaps
  over 1.6 pt. An I and an l are one shape: inside a word with small letters it is an l, at its start an I.
- Teocalli Bowls: its numbers on the painting are glyphs too (teocalli_letters.json), the key live text; each
  number's name from the key, at the number, with its double diamond (numbers.json, read by the panel's resort.py).

Writes, per panel in $CRESTED_BUTTE_WORK/<panel> (default work/crested-butte/<panel>): map.png, pieces.json,
printed.json ({labels, symbols}, PDF points); numbers.json for the inset; glyphs.json in $CRESTED_BUTTE_WORK.
"""
import json
import math
import os
import re
import subprocess
import sys

import pymupdf

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '../../../..'))
T = os.path.join(REPO, 'tools/trailmap')
ROOT = os.path.abspath(os.environ.get('CRESTED_BUTTE_WORK', os.path.join(REPO, 'work/crested-butte')))
PDF = os.path.join(ROOT, 'crested-butte_2025-26.pdf')
OLD = os.path.join(ROOT, 'crested-butte_2022-23.pdf')
PAGE = 1
PAINTING, INSET = 6963, 6968  # this season's painting and inset image (xrefs)
OLD_PAINTING, OLD_INSET = 3687, 3696  # the same images in the 2022-23 PDF
LETTERS = os.path.join(HERE, 'letters.json')
TEO_LETTERS = os.path.join(HERE, 'teocalli_letters.json')
COLOURS = {'blue': (0.12, 0.67, 0.88), 'green': (0.03, 0.66, 0.38), 'black': (0.01, 0.02, 0.02)}
NAME_COLOURS = {'black': (0.13, 0.12, 0.12), 'blue': COLOURS['blue'], 'green': COLOURS['green'],
                'dark': COLOURS['black']}  # 'dark': the lifts' names, the title, the conveyors
LEGEND = (1436, 0, 1728, 1080)
PARTNERS = (0, 946, 1436, 1080)
INSET_BOX = (4, 670, 199, 912)  # the Teocalli Bowls inset and its key
INSET_MAP = (4, 676, 199, 860)  # its painting (its numbers)
TEO_CLIP, TEO_SCALE = (3, 670, 199, 905), 5


def run(*cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode:
        sys.exit(f'{" ".join(cmd)} failed:\n{p.stdout}{p.stderr}')
    return p.stdout


def rgb(c):
    return ','.join(str(v) for v in c)


def box(b):
    return ','.join(str(v) for v in b)


def word(w):
    """I and l are one shape: within a word with small letters an l, at its start an I."""
    if len(w) > 1 and re.search('[a-z]', w):
        w = w[0] + w[1:].replace('I', 'l')
        if w[0] == 'l':
            w = 'I' + w[1:]
    return w


def paintings():
    """The 2022-23 PDF's copies of the painting and the inset image, decoded by MuPDF as this season's are."""
    out = []
    old = pymupdf.open(OLD)
    for x, name in ((OLD_PAINTING, 'painting_2022.png'), (OLD_INSET, 'teocalli_2022.png')):
        f = os.path.join(ROOT, name)
        if not os.path.exists(f) or os.environ.get('IMAGES'):
            pymupdf.Pixmap(pymupdf.csRGB, pymupdf.Pixmap(old, x)).save(f)
        out.append(f)
    return out


def image(out, clip, scale, sharp):
    if not os.path.exists(out) or os.environ.get('IMAGES'):
        run('python3', '-I', f'{T}/matte_pdf_layer.py', '--pdf', PDF, '--page', str(PAGE), '--out', out, '--scale',
            str(scale), '--clip', box(clip), '--replace', f'{PAINTING}={sharp[0]}', '--replace', f'{INSET}={sharp[1]}')


def main_panel(R, sharp):
    W = os.path.join(ROOT, 'main')
    os.makedirs(W, exist_ok=True)
    clip = box(R.CLIP)
    image(os.path.join(W, 'map.png'), R.CLIP, R.SCALE, sharp)
    G = os.path.join(ROOT, 'glyphs.json')
    gcols = [a for k, v in NAME_COLOURS.items() for a in ('--color', f'{k}={rgb(v)}')]
    print(' ', run('python3', '-I', f'{T}/pdf_glyphs.py', 'collect', PDF, '--page', str(PAGE), *gcols, '--exclude',
                   box(LEGEND), '--exclude', box(PARTNERS), '--exclude', box(INSET_BOX), '--max-size', '14',
                   '--out', G).strip().replace(ROOT + '/', ''))
    cols = [a for k, v in COLOURS.items() for a in ('--color', f'{k}={rgb(v)}')]
    pieces = os.path.join(W, 'pieces.json')
    out = run('python3', '-I', f'{T}/pdf_outline_lines.py', PDF, '--page', str(PAGE), '--clip', clip, '--scale',
              str(R.SCALE), *cols, '--dark', 'black', '--dark-min', '7', '--undashed', 'black', '--linked', 'black',
              '--link-gap', '8.5', '--max-width', '3.2',
              '--exclude', box(INSET_BOX), '--glyphs', G, '--letters', LETTERS, '--out', pieces)
    print('  main:', out.strip().splitlines()[-1].replace(ROOT + '/', ''))
    out = run('python3', '-I', f'{T}/extract_pdf_vectors.py', PDF, '--page', str(PAGE), '--clip', clip, '--scale',
              str(R.SCALE), *cols, '--min-width', '1.9', '--max-width', '2.6', '--append', '--out', pieces)
    print('  main:', out.strip().splitlines()[-1].replace(ROOT + '/', ''))
    f = os.path.join(W, 'printed.json')
    print(' ', run('python3', '-I', f'{T}/pdf_glyphs.py', 'labels', PDF, '--glyphs', G, '--letters', LETTERS, '--out', f,
                   '--square', 'blue', '--diamond', 'black', '--diamond', 'dark', '--circle', 'green',
                   '--rect-squares', '--space', '1.6').strip().splitlines()[0].replace(ROOT + '/', ''))
    d = json.load(open(f))
    for lab in d['labels']:
        lab['text'] = ' '.join(word(w) for w in lab['text'].split(' '))
    json.dump(d, open(f, 'w'), indent=0)


def teocalli_panel(sharp):
    """The inset: its image, and each number on it with its name from the key (live text: '1', '  Top of High
    Lift', ...), at the number's middle in the panel's map px."""
    W = os.path.join(ROOT, 'teocalli-bowls')
    os.makedirs(W, exist_ok=True)
    image(os.path.join(W, 'map.png'), TEO_CLIP, TEO_SCALE, sharp)
    G = os.path.join(W, 'glyphs.json')
    x0, y0, x1, y1 = INSET_MAP
    ex = [box((0, 0, 1728, y0)), box((x1, 0, 1728, 1080)), box((0, y1, 1728, 1080)), box((0, 0, x0, 1080))]
    run('python3', '-I', f'{T}/pdf_glyphs.py', 'collect', PDF, '--page', str(PAGE), '--color',
        f'black={rgb(NAME_COLOURS["black"])}', *[a for e in ex for a in ('--exclude', e)], '--max-size', '14',
        '--out', G)
    sys.path.insert(0, T)
    from pdf_glyphs import letter
    table = json.load(open(TEO_LETTERS))
    digits = sorted((g for g in json.load(open(G))['glyphs'] if (letter(table, g) or '').isdigit()),
                    key=lambda g: g['c'][0])
    for g in digits:
        g['ch'] = letter(table, g)
    numbers = []  # digits a number's width apart and level: one number (left to right)
    for g in digits:
        n = next((n for n in numbers if abs(n[-1]['c'][1] - g['c'][1]) < 2.5 and 0 < g['c'][0] - n[-1]['c'][0] < 4.5),
                 None)
        (n.append(g) if n else numbers.append([g]))
    page = pymupdf.open(PDF)[PAGE]
    key, last = {}, None
    for b in page.get_text('dict', clip=pymupdf.Rect(*INSET_BOX))['blocks']:
        for line in b.get('lines', []):
            for s in line['spans']:
                t = s['text'].strip()
                if t.isdigit() and 'SemiBold' in s['font']:
                    last = t
                elif last and t:
                    key[last], last = t, None
    out = []
    for n in numbers:
        num = ''.join(g['ch'] for g in n)
        cx = sum(g['c'][0] for g in n) / len(n)
        cy = sum(g['c'][1] for g in n) / len(n)
        out.append({'number': num, 'name': key[num], 'x': round((cx - TEO_CLIP[0]) * TEO_SCALE),
                    'y': round((cy - TEO_CLIP[1]) * TEO_SCALE)})
    out.sort(key=lambda o: (int(o['number']), o['x']))
    json.dump(out, open(os.path.join(W, 'numbers.json'), 'w'), indent=1)
    json.dump({'_source': 'Crested Butte teocalli-bowls: no lines (prepare.py)', 'polylines': []},
              open(os.path.join(W, 'pieces.json'), 'w'))
    json.dump({'labels': [], 'symbols': []}, open(os.path.join(W, 'printed.json'), 'w'))
    print(f'  teocalli-bowls: {len(out)} numbers, {len(key)} names in the key')


def main():
    import importlib.util
    spec = importlib.util.spec_from_file_location('cb_main', os.path.join(HERE, 'panels', 'main', 'resort.py'))
    R = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(R)
    os.makedirs(ROOT, exist_ok=True)
    sharp = paintings()
    main_panel(R, sharp)
    teocalli_panel(sharp)


if __name__ == '__main__':
    main()
