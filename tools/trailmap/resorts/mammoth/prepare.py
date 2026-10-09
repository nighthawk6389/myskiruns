"""Mammoth Mountain: the map images, line pieces, printed names and symbols of its two panels, for
tools/trailmap/pdf_resort.py.

    python3 tools/trailmap/resorts/mammoth/prepare.py      # regen.sh runs it

The 2025-26 trail map (skimap.org 42347: the resort's two-page PDF; page 2 is the map) prints every name as text
and every symbol as a fill over a 100 dpi painting, and draws no trail lines: the runs are the painting's. The
lines come from the resort's interactive maps (resorts-interactive.com map 1812, the whole mountain, and 1819, the
back side), whose SVGs draw each run's line over the same paintings, grouped under the run's name
(tools/trailmap/vicomap.py parse).

Panels (resort.py PANELS; each one's settings in panels/<panel>/resort.py, its files in work/.../<panel>/):
- main: the whole mountain, the page right of the information panel and above the Unbound panel; the back-side
  inset in its lower right corner is left to its own panel (nothing of it is read here).
- back-side: the inset, the back side (Chairs 13 and 14) drawn larger.

- Images: the page rendered at resort.SCALE with both paintings (the main one and the inset's) swapped for a
  Lanczos upscale (tools/trailmap/matte_pdf_layer.py --resample).
- Lines: each SVG's trail lines on its panel by VICOMAP_AFFINE (register_pages.py --ref on the painting), each
  carrying its group's name (resort.GROUPED); the class is the group's (its id: green, blue, advanced intermediate
  blue, black, double black black, the parks' freestyle). The small closed loops in the green groups are the
  outlines of their circles, not lines. Lines are cut where they leave the panel's map (the main panel: its image,
  less the inset).
- Names: the page's text (pdf_labels.py) in the names' font and colour (TradeGothic Bold, near-black): every run's
  name on a white halo, the symbol before it, the whole label turned along the run; a name on two lines is one text
  object whose lines pdf_labels.py splits: joined again (two_line). Two names are outlined glyphs instead of text
  (resort.OUTLINED, read on a crop): their letters, one fill each in drawing order. The uphill routes' white names, the lodges'
  blue ones and the legend are left out. Each name is spelled as the interactive map's group of that name (the trail
  report's names): a name the map prints once for a run the report splits (MAMBO for Mambo (Upper) and (Lower);
  ROAD RUNNER) takes the group whose line is nearest; LOWER X and UPPER X take the nearest of X's (Lower) or
  (Upper) groups, and X the group X if there is one.
- Symbols: fills in the legend's colours, turned with their names: a green circle (four to eight curves), a blue square
  (Slightly Difficult; four sides), a blue diamond in a black one (Difficult: advanced intermediate; blue), a black
  diamond (four equal sides), a black double diamond (one path of eight sides, or two diamonds side by side).

Writes, per panel in $MAMMOTH_WORK/<panel> (default work/mammoth): map.png, pieces.json, printed.json (pdf_labels.py's
labels, PDF points), symbols.json ([{type, src, sizePt}], map px).
"""
import importlib.util
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
ROOT = os.path.abspath(os.environ.get('MAMMOTH_WORK', os.path.join(REPO, 'work/mammoth')))
PDF = os.path.join(ROOT, 'mammoth_2025-26.pdf')
PAGE = 1
PAINTINGS = (230, 581)  # the main painting's and the inset's image xrefs (both 100 dpi)
INSET = (1148, 797, 1728, 1183.5)  # pt: the back-side inset
SVG = {'main': 'vicomap', 'back-side': 'vicomap_back'}

CLS = {'green': 'green', 'blue': 'blue', 'advanced-intermediate': 'blue', 'black': 'black', 'double-black': 'black',
       'nordic': 'freestyle'}
NAME_COLOURS = [(0.14, 0.12, 0.12), (0.13, 0.12, 0.12)]
GREEN, BLUE, DARK = (0.53, 0.77, 0.25), (0.0, 0.67, 0.87), (0.14, 0.12, 0.12)
QUALIFIERS = ('UPPER', 'LOWER', 'MIDDLE')


def run(*cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode:
        sys.exit(f'{" ".join(cmd)} failed:\n{p.stdout}{p.stderr}')
    return p.stdout


def settings(panel):
    """The panel's resort.py (CLIP, SCALE, VICOMAP_AFFINE)."""
    spec = importlib.util.spec_from_file_location(f'mm_{panel}', os.path.join(HERE, 'panels', panel, 'resort.py'))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def col(c):
    return tuple(round(v, 2) for v in c or ())


def inside(p, r):
    return r[0] <= p[0] <= r[2] and r[1] <= p[1] <= r[3]


def length(pts):
    return sum(math.dist(a, b) for a, b in zip(pts, pts[1:]))


def dense(pts, step):
    out = []
    for a, b in zip(pts, pts[1:]):
        n = max(1, int(math.dist(a, b) / step))
        out += [(a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n) for k in range(n)]
    return out + [tuple(pts[-1])]


def seg_dist(q, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    n = dx * dx + dy * dy
    t = max(0, min(1, ((q[0] - a[0]) * dx + (q[1] - a[1]) * dy) / n)) if n else 0
    return math.dist(q, (a[0] + t * dx, a[1] + t * dy))


def line_dist(q, pts):
    return min(seg_dist(q, a, b) for a, b in zip(pts, pts[1:]))


def in_map(panel, R, p):
    """A point (pt) on this panel's map: inside its clip, and on the main panel not on the inset."""
    return inside(p, R.CLIP) and (panel != 'main' or not inside(p, INSET))


def image(panel, R, W):
    out = os.path.join(W, 'map.png')
    if os.path.exists(out) and not os.environ.get('IMAGES'):
        return
    run('python3', '-I', f'{T}/matte_pdf_layer.py', '--pdf', PDF, '--page', str(PAGE), '--out', out, '--scale',
        str(R.SCALE), '--clip', ','.join(map(str, R.CLIP)), *[a for x in PAINTINGS for a in ('--resample', str(x))])


def parse(panel):
    d = os.path.join(ROOT, SVG[panel])
    out = run('python3', '-I', f'{T}/vicomap.py', 'parse', d)
    print(f'  {panel}:', out.splitlines()[0])
    V = json.load(open(os.path.join(d, 'trails.json')))
    names = set(settings(panel).NAMES)
    for t in V['trails']:
        # vicomap.py drops a group id's trailing number (Illustrator numbers copies so), but here it can be the
        # name's: Drop_18 and Repeat_22 are the report's Drop 18 and Repeat 22
        m = re.search(r'_(\d+)_?$', t['id'])
        if m and f"{t['name']} {m.group(1)}" in names:
            t['name'] = f"{t['name']} {m.group(1)}"
        # the Hemlocks' terrain features (the parks' orange line) are the report's own run
        if t['rating'] == 'nordic' and t['name'] == 'The Hemlocks':
            t['name'] = 'The Hemlocks (Terrain Features)'
    return V


def lines(panel, R, W, V):
    a, b, c, d, e, f = R.VICOMAP_AFFINE
    x0, y0 = R.CLIP[:2]

    def pt(q):  # SVG units -> PDF points
        return ((a * q[0] + b * q[1] + c) / R.SCALE + x0, (d * q[0] + e * q[1] + f) / R.SCALE + y0)
    out, loops = [], 0
    for t in V['trails']:
        for pl in t['lines']:
            if len(pl) < 2:
                continue
            if math.dist(pl[0], pl[-1]) < 0.5 and length(pl) < 80:
                loops += 1
                continue  # a circle's outline
            run_ = []
            for q in dense([pt(q) for q in pl], 0.4) + [None]:
                if q is not None and in_map(panel, R, q):
                    run_.append(q)
                    continue
                if len(run_) >= 2 and length(run_) * R.SCALE >= 3:
                    px = [((x - x0) * R.SCALE, (y - y0) * R.SCALE) for x, y in run_]
                    px = rdp(px, 0.6)
                    w, h = (R.CLIP[2] - x0) * R.SCALE, (R.CLIP[3] - y0) * R.SCALE
                    out.append({'id': len(out), 'cls': CLS[t['rating']], 'lengthPx': round(length(px)),
                                'name': t['name'],
                                'points': [[round(100 * x / w, 3), round(100 * y / h, 3)] for x, y in px]})
                run_ = []
    json.dump({'_source': f'Mammoth interactive map ({SVG[panel]}: resorts-interactive.com) SVG lines, '
                          'tools/trailmap/resorts/mammoth/prepare.py; percent of the map image',
               'polylines': out}, open(os.path.join(W, 'pieces.json'), 'w'))
    print(f'  {panel}: wrote pieces.json: {len(out)} pieces ({loops} circle outlines left out)')
    return out


def rdp(pts, tol):
    if len(pts) < 3:
        return pts
    (ax, ay), (bx, by) = pts[0], pts[-1]
    n = math.hypot(bx - ax, by - ay) or 1e-9
    ds = [abs((by - ay) * (x - ax) - (bx - ax) * (y - ay)) / n for x, y in pts[1:-1]]
    i = max(range(len(ds)), key=ds.__getitem__)
    if ds[i] <= tol:
        return [pts[0], pts[-1]]
    return rdp(pts[:i + 2], tol)[:-1] + rdp(pts[i + 1:], tol)


def words(s):
    return re.sub(r"[^A-Z0-9 ]", '', s.upper().replace('’', "'").replace('(', ' ').replace(')', ' ')).split()


def base(s):
    """A name without its part (Upper, Lower, Middle; Top Half, Bottom Half), letters only: Road Runner Lower (Top
    Half) and UPPER ROAD RUNNER are ROADRUNNER."""
    return ''.join(w for w in words(s) if w not in QUALIFIERS + ('TOP', 'BOTTOM', 'HALF'))


def qualifier(s):
    return next((w for w in words(s) if w in QUALIFIERS), None)


def outlined(page, outlines):
    """Names drawn as outlined glyphs (resort.OUTLINED: the first glyph's drawing order -> the text, read on a
    crop): the glyphs are the dark fills drawn one after another from there, each a letter."""
    out = []
    draws = sorted((d for d in page.get_drawings() if d.get('fill') and col(d['fill']) in NAME_COLOURS),
                   key=lambda d: d['seqno'])
    for seq, text in outlines.items():
        i = next(i for i, d in enumerate(draws) if d['seqno'] == seq)
        n = len(text.replace(' ', ''))
        run_ = draws[i:i + n]
        assert all(b['seqno'] - a['seqno'] <= 2 for a, b in zip(run_, run_[1:])), ('OUTLINED: a gap in', text)
        pts = [[round((d['rect'].x0 + d['rect'].x1) / 2, 2), round((d['rect'].y0 + d['rect'].y1) / 2, 2)]
               for d in run_]
        out.append({'seq': seq, 'text': text, 'color': list(NAME_COLOURS[0]), 'font': 'outlined', 'size': 6.5,
                    'pts': pts, 'c': [round(sum(p[0] for p in pts) / n, 2), round(sum(p[1] for p in pts) / n, 2)]})
    return out


def text_labels(page, outlines):
    f = os.path.join(ROOT, 'text.json')
    if not os.path.exists(f):
        run('python3', '-I', f'{T}/pdf_labels.py', PDF, '--page', str(PAGE), '--out', f)
    L = [lab for lab in json.load(open(f))
         if lab['font'].endswith('TradeGothicLTStd-Bd2') and col(lab['color']) in NAME_COLOURS]
    # a name on two lines is one text object that pdf_labels.py splits in two: joined again
    out = []
    for lab in sorted(L, key=lambda lab: (lab['seq'], lab['c'][1])):
        prev = out[-1] if out else None
        if prev and prev['seq'] == lab['seq'] and abs(lab['c'][1] - prev['c'][1]) < 2.5 * lab['size'] * len(prev['lines']):
            prev['text'] += ' ' + lab['text']
            prev['pts'] += lab['pts']
            prev['lines'].append(lab['text'])
            n = len(prev['pts'])
            prev['c'] = [round(sum(p[0] for p in prev['pts']) / n, 2), round(sum(p[1] for p in prev['pts']) / n, 2)]
            prev['two_line'] = True
        else:
            out.append({**lab, 'lines': [lab['text']]})
    for lab in out:
        del lab['lines']
    return out + outlined(page, outlines)


def labels(panel, R, W, L, pieces):
    """The panel's names, each spelled as the interactive map's group of that name (see the docstring)."""
    x0, y0 = R.CLIP[:2]
    w, h = (R.CLIP[2] - x0) * R.SCALE, (R.CLIP[3] - y0) * R.SCALE
    own = {}
    for p in pieces:
        own.setdefault(p['name'], []).append([(x * w / 100, y * h / 100) for x, y in p['points']])
    groups = {}
    for nm in own:
        groups.setdefault(base(nm), []).append(nm)
    for nm in R.NAMES:  # the report's runs with no line here (parks, glades, adventure zones)
        if not any(g == nm for gs in groups.values() for g in gs):
            groups.setdefault(base(nm), []).append(nm)
    here = [lab for lab in L if in_map(panel, R, lab['c'])]

    def dist(nm, c):
        return min((line_dist(c, pl) for pl in own.get(nm, ())), default=math.inf)
    out, notes = [], []
    for lab in here:
        cands = groups.get(base(lab['text']), [])
        q = qualifier(lab['text'])
        c = ((lab['c'][0] - x0) * R.SCALE, (lab['c'][1] - y0) * R.SCALE)
        if q:  # LOWER X: X's (Lower) group, or Road Runner Lower's (Top Half) or (Bottom Half), whichever is nearest
            cands = [nm for nm in cands if qualifier(nm) == q]  # (none: a run of its own, LOWER SHAFT)
        elif any(qualifier(nm) is None for nm in cands):
            cands = [nm for nm in cands if qualifier(nm) is None]
        name = min(cands, key=lambda nm: dist(nm, c)) if cands else lab['text']
        if len(cands) > 1 or name.upper() != lab['text'].replace('’', "'").upper():
            dd = dist(name, c)
            notes.append(f"{lab['text']} -> {name}" + (f' ({dd:.0f} px)' if dd < math.inf else ''))
        out.append({**lab, 'text': name, 'as_printed': lab['text']})
    json.dump(out, open(os.path.join(W, 'printed.json'), 'w'), indent=0)
    print(f'  {panel}: {len(out)} names; spelled as the groups: ' + '; '.join(notes))


def symbols(panel, R, W, page):
    """Symbol fills (see the docstring): [{type, src (map px), sizePt}]."""
    x0, y0 = R.CLIP[:2]
    dark, eights, blue, out = [], [], [], []
    for d in page.get_drawings():
        if d['type'] not in ('f', 'fs') or not d.get('fill'):
            continue
        r, c, kinds = d['rect'], col(d['fill']), ''.join(it[0] for it in d['items'])
        ctr = ((r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2)
        if not in_map(panel, R, ctr) or any(inside(ctr, e) for e in R.EXCLUDE) or max(r.width, r.height) > 12:
            continue
        sides = [math.dist((it[1].x, it[1].y), (it[2].x, it[2].y)) for it in d['items'] if it[0] == 'l']
        if c == GREEN and set(kinds) == {'c'} and 4 <= len(kinds) <= 8 and abs(r.width - r.height) < 0.2 * r.width \
                and 3 <= r.width <= 9:
            out.append(('circle', r))
        elif c == BLUE and kinds in ('llll', 're', 'cccc') and abs(r.width - r.height) < 0.2 * r.width \
                and 3 <= r.width <= 9:  # (Antin Alley's square is drawn with four straight curves)
            blue.append(r)
        elif c == DARK and kinds == 'llll' and min(sides) > 0.85 * max(sides) and 2.5 <= max(r.width, r.height) <= 9:
            dark.append(r)
        elif c == DARK and kinds == 'llllllll' and 5 <= max(r.width, r.height) <= 12:
            eights.append(r)
    for r in blue:
        out.append(('square', r))
    # a black diamond round a blue one is the blue diamond's outline (Difficult: blue)
    dark = [r for r in dark if not any(r.contains(q) or (r & q).get_area() > 0.5 * q.get_area() for q in blue)]
    used = set()
    for i, r in enumerate(dark):  # two diamonds side by side: a double diamond
        for j in range(i + 1, len(dark)):
            q = dark[j]
            if j not in used and i not in used and math.dist(((r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2),
                                                             ((q.x0 + q.x1) / 2, (q.y0 + q.y1) / 2)) < 1.3 * r.width:
                used |= {i, j}
                out.append(('double-diamond', r | q))
    out += [('diamond', r) for i, r in enumerate(dark) if i not in used]
    out += [('double-diamond', r) for r in eights]
    syms = [{'type': t, 'src': [round(((u.x0 + u.x1) / 2 - x0) * R.SCALE, 2), round(((u.y0 + u.y1) / 2 - y0) * R.SCALE, 2)],
             'sizePt': round(min(u.width, u.height), 2)} for t, u in out]
    json.dump(syms, open(os.path.join(W, 'symbols.json'), 'w'), indent=0)
    tally = {}
    for s in syms:
        tally[s['type']] = tally.get(s['type'], 0) + 1
    print(f'  {panel}: {len(syms)} symbols {tally}')


def main():
    sys.path.insert(0, HERE)
    import resort as top
    doc = pymupdf.open(PDF)
    L = text_labels(doc[PAGE], top.OUTLINED)
    for panel, _name in top.PANELS:
        R = settings(panel)
        W = os.path.join(ROOT, panel)
        os.makedirs(W, exist_ok=True)
        image(panel, R, W)
        pieces = lines(panel, R, W, parse(panel))
        labels(panel, R, W, L, pieces)
        symbols(panel, R, W, doc[PAGE])


if __name__ == '__main__':
    main()
