"""Northstar: the map image, line pieces, printed names and symbols, for tools/trailmap/pdf_resort.py.

    python3 tools/trailmap/resorts/northstar/prepare.py      # regen.sh runs it

The 2025-26 trail map (northstarcalifornia.com: 20251022_NS_winter-trail_map_001.pdf, Illustrator, Alex Tait's
painting in 100 tiles at 150 dpi under the vector layer) is page 1; page 2 is the village directory.

- Image: page 1 rendered at resort.SCALE.
- Lines: every trail line is a filled outline (the artwork's strokes outlined), in blue, black or green, each in
  two shades (tools/trailmap/pdf_outline_lines.py: centre lines). Names are printed on the line itself, each white letter
  haloed by an outline in the line's colour: those halos come out as short pieces lying on the letters, and are
  dropped (a piece under 25 pt whose points all lie on white fills' boxes, the letters' and the signs'), and so are
  the slow zone's hatching (pieces under 16 pt), closed outlines under 80 pt (letters, icons) and the icons drawn in
  the trail colours (ICONS). The legend, the Mid-Mountain inset (the
  base area again at another scale), the Kids Adventure Zone box and the partners' bar are left out.
- Names: the white letters, outlined glyphs (tools/trailmap/pdf_glyphs.py; each shape's letter, read once on its
  contact sheets, is in letters.json here: the ski-area-boundary lettering, the logos and icons are read as *), and
  the names printed as live text in the same style (pdf_labels.py: white Frutiger UltraBlack and Folio ExtraBold,
  white on a red band: the lifts'). Each label takes the colour of the halo under its letters (the run's: blue,
  black, green; a live-text name is drawn twice, its halo copy in that colour first), its fallback rating
  (resort.COLOR_SYMBOL); the lifts' names, on red, take none and are no names (resort.is_name).
- Symbols: pdf_symbols.py (green circles, blue squares, black diamonds drawn as rhombi, on the lines), less the Kids
  Adventure Zone signs' blue squares (each under a smiley).

Writes, in $NORTHSTAR_WORK (default work/northstar): map.png, pieces.json, glyphs.json, printed.json (labels,
PDF points), symbols.json (map px).
"""
import json
import math
import os
import subprocess
import sys

import pymupdf

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '../../../..'))
T = os.path.join(REPO, 'tools/trailmap')
sys.path.insert(0, HERE)
from resort import CLIP, SCALE  # noqa: E402

W = os.path.abspath(os.environ.get('NORTHSTAR_WORK', os.path.join(REPO, 'work/northstar')))
PDF = os.path.join(W, 'northstar_2025-26.pdf')
LETTERS = os.path.join(HERE, 'letters.json')
BLUE, BLACK, GREEN = (0.23, 0.43, 0.56), (0.18, 0.18, 0.18), (0.5, 0.5, 0.33)
# the halos' colours: the lines' (blue), and a second near-black and olive for the black and green names
HALO = {'blue': [(0.23, 0.43, 0.56), (0.23, 0.44, 0.57)],
        'black': [(0.17, 0.18, 0.18), (0.18, 0.18, 0.18), (0.14, 0.12, 0.13)],
        'green': [(0.5, 0.51, 0.34), (0.5, 0.5, 0.33)],
        'park': [(0.97, 0.55, 0.2)]}  # the terrain parks' orange pills
# pt: the legend, the Mid-Mountain inset, the Kids Adventure Zone box, the partners' bar
EXCLUDE = [(1055, 160, 1305, 845), (835, 585, 1045, 845), (60, 40, 245, 115), (10, 760, 690, 845)]
NAME_FONTS = ('Frutiger-UltraBlack', 'Folio-ExtraBold')
# pt: icons drawn in the trail colours (the village's badge, the cross-country centre's, the Northwest Territory sign)
ICONS = [(5, 690, 100, 790), (70, 410, 115, 480), (270, 495, 300, 530)]
SMILEY = (0.85, 0.58, 0.11)  # the Kids Adventure Zone signs' faces


def run(*cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode:
        sys.exit(f'{" ".join(cmd)} failed:\n{p.stdout}{p.stderr}')
    return p.stdout


def rgb(c):
    return ','.join(str(v) for v in c)


def ex():
    return [a for e in EXCLUDE for a in ('--exclude', ','.join(map(str, e)))]


def inside(p, r):
    return r[0] <= p[0] <= r[2] and r[1] <= p[1] <= r[3]


def image():
    out = os.path.join(W, 'map.png')
    if not os.path.exists(out) or os.environ.get('IMAGES'):
        pymupdf.open(PDF)[0].get_pixmap(matrix=pymupdf.Matrix(SCALE, SCALE), clip=pymupdf.Rect(*CLIP)).save(out)


def glyphs():
    print(' ', run('python3', f'{T}/pdf_glyphs.py', 'collect', PDF, '--color', 'white=1,1,1', '--max-size', '9', *ex(),
                   '--out', os.path.join(W, 'glyphs.json')).strip().replace(W + '/', ''))


def lines():
    out = os.path.join(W, 'pieces.json')
    # each colour in both its shades (the lines and the halos use either), merged into one class below
    cols = [a for k, cs in HALO.items() if k != 'park' for i, c in enumerate(cs)
            for a in ('--color', f'{k}{i}={rgb(c)}')]
    print(' ', run('python3', f'{T}/pdf_outline_lines.py', PDF, '--clip', ','.join(map(str, CLIP)), '--scale',
                   str(SCALE), *cols, '--max-width', '2.5', '--min-length', '3', *ex(),
                   '--out', out).strip().replace(W + '/', ''))
    # the white letters' boxes: every white fill up to 40 pt (the names' letters, and the signs' larger lettering)
    boxes = [(d['rect'].x0, d['rect'].y0, d['rect'].x1, d['rect'].y1) for d in pymupdf.open(PDF)[0].get_drawings()
             if d['type'] == 'f' and d.get('fill') and tuple(round(v, 2) for v in d['fill']) == (1.0, 1.0, 1.0)
             and max(d['rect'].width, d['rect'].height) <= 40]
    d = json.load(open(out))
    for p in d['polylines']:
        p['cls'] = p['cls'].rstrip('0123456789')
    w, h = (CLIP[2] - CLIP[0]) * SCALE, (CLIP[3] - CLIP[1]) * SCALE

    def pt(q):
        return (CLIP[0] + q[0] * w / 100 / SCALE, CLIP[1] + q[1] * h / 100 / SCALE)

    def on_glyph(q):
        return any(b[0] - 1.2 <= q[0] <= b[2] + 1.2 and b[1] - 1.2 <= q[1] <= b[3] + 1.2 for b in boxes)
    keep = [p for p in d['polylines'] if p['lengthPx'] / SCALE >= 25 or not all(on_glyph(pt(q)) for q in p['points'])]
    halos = len(d['polylines']) - len(keep)

    def junk(p):
        a, b = pt(p['points'][0]), pt(p['points'][-1])
        return (p['lengthPx'] / SCALE < 16  # the slow zone's hatching, stray bits of icons
                or (math.dist(a, b) < 2 and p['lengthPx'] / SCALE < 80)  # a closed outline: a letter, an icon
                or any(inside(a, e) and inside(b, e) for e in ICONS))
    marks = [p for p in keep if junk(p)]
    keep = [p for p in keep if p not in marks]
    for i, p in enumerate(keep):  # ids in order again (pdf_resort.py indexes pieces by id)
        p['id'] = i
    d['polylines'] = keep
    json.dump(d, open(out, 'w'))
    by = {}
    for p in keep:
        by[p['cls']] = by.get(p['cls'], 0) + 1
    print(f'  {len(keep)} line pieces {by} ({halos} letter halos and {len(marks)} hatching strokes and icon bits left '
          f'out)')


def halo_colours():
    """Every fill in a halo colour no larger than a name's halo (150 pt), with its class and box, smallest first."""
    out = []
    for d in pymupdf.open(PDF)[0].get_drawings():
        f = d.get('fill')
        r = d['rect']
        if d['type'] != 'f' or not f or max(r.width, r.height) > 150:
            continue
        f = tuple(round(v, 2) for v in f)
        k = next((k for k, cs in HALO.items() if f in cs), None)
        if k:
            out.append((r.width * r.height, k, (r.x0, r.y0, r.x1, r.y1)))
    return sorted(out)


def colour(lab, halos, copies):
    """A label's colour: that of a copy of its text drawn at the same place in a trail colour (live text is drawn
    twice, its halo first; a curved name's copy one letter at a time: a vote of its letters), else the class of the
    smallest halo fill holding each letter (a vote), else None."""
    for c in copies:
        if c['text'].replace(' ', '') == lab['text'].replace(' ', '') and math.dist(c['c'], lab['c']) < 1:
            return c['cls']
    votes = {}
    for q in lab['pts'] if copies else ():  # a curved name's halo copy, drawn one letter at a time
        k = next((c['cls'] for c in copies if len(c['text']) == 1 and math.dist(c['c'], q) < 0.5), None)
        if k:
            votes[k] = votes.get(k, 0) + 1
    if votes:
        return max(votes, key=votes.get)
    for q in lab['pts']:
        k = next((k for _a, k, b in halos if inside(q, b)), None)
        if k:
            votes[k] = votes.get(k, 0) + 1
    return max(votes, key=votes.get) if votes else None


def labels():
    G = os.path.join(W, 'glyphs.json')
    f = os.path.join(W, 'glyph_labels.json')
    print(' ', run('python3', f'{T}/pdf_glyphs.py', 'labels', PDF, '--glyphs', G, '--letters', LETTERS,
                   '--out', f).strip().replace(W + '/', ''))
    halos = halo_colours()
    t = os.path.join(W, 'text.json')
    run('python3', '-I', f'{T}/pdf_labels.py', PDF, '--out', t)
    text = json.load(open(t))
    copies = [{**c, 'cls': k} for c in text for k, cs in HALO.items() if tuple(c['color']) in cs]
    labs = []
    for lab in json.load(open(f))['labels']:
        if '*' in lab['text'] or any(inside(lab['c'], e) for e in EXCLUDE):
            continue  # the boundary's lettering, logos and icons (read as *)
        labs.append({**lab, 'font': 'glyph', 'color': colour(lab, halos, [])})
    for lab in text:
        if (lab['font'] in NAME_FONTS and tuple(lab['color']) == (1.0, 1.0, 1.0)
                and not any(inside(lab['c'], e) for e in EXCLUDE)):
            labs.append({**lab, 'color': colour(lab, halos, copies)})
    os.remove(t)
    json.dump({'labels': labs, 'symbols': []}, open(os.path.join(W, 'printed.json'), 'w'), indent=0)
    tally = {}
    for lab in labs:
        tally[lab['color']] = tally.get(lab['color'], 0) + 1
    print(f'  {len(labs)} labels {tally}')


def symbols():
    out = os.path.join(W, 'symbols.json')
    run('python3', f'{T}/pdf_symbols.py', PDF, '--clip', ','.join(map(str, CLIP)), '--scale', str(SCALE),
        '--circle', rgb(GREEN), '--square', rgb(BLUE), '--diamond', rgb(BLACK), '--max-size', '13',
        '--max-diamond', '10', *ex(), '--out', out)
    # the Kids Adventure Zone's signs: a smiley on a blue square, which reads as a square symbol
    smileys = [((d['rect'].x0 + d['rect'].x1) / 2, (d['rect'].y0 + d['rect'].y1) / 2)
               for d in pymupdf.open(PDF)[0].get_drawings() if d['type'] == 'f' and d.get('fill')
               and tuple(round(v, 2) for v in d['fill']) == SMILEY and max(d['rect'].width, d['rect'].height) < 12]
    S = [s for s in json.load(open(out))
         if not any(math.dist(s['src'], ((x - CLIP[0]) * SCALE, (y - CLIP[1]) * SCALE)) < 3 * SCALE for x, y in smileys)]
    json.dump(S, open(out, 'w'))
    by = {}
    for s in S:
        by[s['type']] = by.get(s['type'], 0) + 1
    print(f'  {len(S)} symbols {by}')


if __name__ == '__main__':
    os.makedirs(W, exist_ok=True)
    image()
    glyphs()
    lines()
    labels()
    symbols()
