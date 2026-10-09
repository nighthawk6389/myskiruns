"""Steamboat: the map image, line pieces, printed names and symbols, for tools/trailmap/pdf_resort.py.

    python3 tools/trailmap/resorts/steamboat/prepare.py      # regen.sh runs it

The resort publishes its 2026-27 trail map as an image only (2400x1682 px), and its interactive map
(resorts-interactive.com map 1800), whose SVG is this map's vector layer drawn again: every trail's line, its name's
letters and its symbol in a group named after the trail (tools/trailmap/vicomap.py parse --detail).

- Image: the resort's JPEG, as it is (resort.CLIP is the whole image, 1 px per unit).
- Lines: the SVG's stroked trail lines on the image by resort.VICOMAP_AFFINE (vicomap.py fit-ink), each carrying
  its group's name (resort.GROUPED: pdf_resort.py names the piece by it), its ends cut back where they run under a
  name or symbol (at most TRIM_MAX px), then routed onto the print's own line (route(): the cheapest path through
  the print's pixels of its colour near it; the interactive map's line where that would be a detour). An
  advanced-intermediate run's line is blue under black dashes: the dashes are left out (a copy along the blue
  line). The snowshoe trails (purple) are no runs.
- Symbols: per group, the fills shaped like one (one outline of four equal straight sides, or of four to eight
  curves, about as wide as tall, 8 to 25 units): green a circle, blue a square, blue and black together the
  advanced-intermediate square and diamond (a square here: blue), one black a diamond, two black side by side (or
  one outline of eight sides, 19 units or more) a double diamond; four sides of unequal length are a turned letter
  I. Steamboat prints a black run's diamond again and again along its line. A symbol the print doesn't show where
  the SVG has it rates its run but is no end of its name (far).
- Names: per group, its other fills in a run's colour (its letters) in drawing order, split where they jump (but a
  second line, whose centre lies within about a line of the first's, stays): one label per printed name; a name on
  two lines (its letters jump back against the text's way) is marked two_line (no stretch along it). A group whose
  letters aren't in it (some glades and tree areas: only their white halos are) gets its label at those halos. A
  name the print doesn't show there (a fair part of each letter's box in its colour) is moved where it does, within
  REACH px, if that puts it on its own run's line (the 2026-27 artwork moved some); else it is kept, with no stretch
  along it, or left out if its run has no line here.

Writes, in $STEAMBOAT_WORK (default work/steamboat): map.png, pieces.json, printed.json ({labels, symbols}, map px).
"""
import json
import math
import os
import re
import subprocess
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '../../../..'))
T = os.path.join(REPO, 'tools/trailmap')
sys.path.insert(0, HERE)
sys.path.insert(0, T)
from resort import CLIP, NAMES, VICOMAP_AFFINE  # noqa: E402
from vicomap import dense_pts  # noqa: E402

W = os.path.abspath(os.environ.get('STEAMBOAT_WORK', os.path.join(REPO, 'work/steamboat')))
IMAGE = os.path.join(W, 'steamboat_2026-27.jpg')
SVG_DIR = os.path.join(W, 'vicomap')

CLS = {'#2052a4': 'blue', '#0256b5': 'blue', '#295eab': 'blue', '#00984c': 'green', '#10984c': 'green',
       '#468b22': 'green', '#0c0606': 'black', '#000': 'black', '#000000': 'black', '#060000': 'black',
       '#030404': 'black', '#030405': 'black', '#020202': 'black'}


REACH = 30  # px: how far the print may have moved a name or symbol from where the interactive map keeps it
CORRIDOR, END_R, OFF, PULL, TOL = 24, 8, 30.0, 0.15, 0.8  # route(): px, px, cost, cost per px, px
TRIM_MAX = 16  # px: the longest line end trim_text() cuts back


def tf(p):
    a, b, c, d, e, f = VICOMAP_AFFINE
    return (a * p[0] + b * p[1] + c, d * p[0] + e * p[1] + f)


def image():
    out = os.path.join(W, 'map.png')
    if not os.path.exists(out) or os.environ.get('IMAGES'):
        Image.open(IMAGE).convert('RGB').save(out)


def parse():
    p = subprocess.run(['python3', '-I', os.path.join(T, 'vicomap.py'), 'parse', SVG_DIR, '--detail'],
                       capture_output=True, text=True)
    if p.returncode:
        sys.exit(p.stdout + p.stderr)
    print(' ', p.stdout.splitlines()[0])
    V = json.load(open(os.path.join(SVG_DIR, 'trails.json')))
    # vicomap.py drops a group id's trailing number (Illustrator numbers copies so), but here it can be the name's:
    # Chute_1, _2, _3 and Triangle_3 are the report's Chute 1, 2, 3 and Triangle 3
    for t in V['trails'] + V['loose']:
        m = re.search(r'_(\d+)_?$', t['id'])
        if m and f"{t['name']} {m.group(1)}" in NAMES:
            t['name'] = f"{t['name']} {m.group(1)}"
    return V


def length(pts):
    return sum(math.dist(u, v) for u, v in zip(pts, pts[1:]))


INK = {'blue': (45, 98, 165), 'green': (55, 150, 90)}  # the print's line colours (black: any dark pixel)


def ink_masks(V):
    """The print's line pixels per class, less every name's letters and symbols (the interactive map's fills, on
    the image): the snap goes to the line, not the text printed in its gap."""
    import numpy as np
    img = np.asarray(Image.open(os.path.join(W, 'map.png')).convert('RGB')).astype(float)
    m = {k: np.linalg.norm(img - np.array(c), axis=2) < 50 for k, c in INK.items()}
    m['black'] = img.max(axis=2) < 70
    m['blue'] = m['blue'] | m['black']  # an advanced-intermediate run: blue under black dashes
    text = np.zeros(m['black'].shape, bool)
    h, w = text.shape
    for t in V['trails'] + V['lifts']:
        for f in t.get('fills') or ():
            if f['fill'] in ('#fff', '#ffffff'):
                continue  # halos are larger than the letters: the line runs right up to them
            (x0, y0), (x1, y1) = tf(f['box'][:2]), tf(f['box'][2:])
            text[max(0, int(y0) - 1):min(h, int(y1) + 2), max(0, int(x0) - 1):min(w, int(x1) + 2)] = True
    return {k: v & ~text for k, v in m.items()}, text


def route(pts, mask):
    """The interactive map's line moved onto the print's own: the cheapest path between its ends (each moved to the
    nearest line pixel within END_R px) through the print's line pixels of its class (cost 1; any other pixel
    OFF), within CORRIDOR px of the interactive map's line and drawn to it a little (a junction's other branch
    costs more), simplified to TOL px. Where the print has no line near (a run redrawn since), the path keeps to
    the interactive map's line, through off-line pixels, and a path much longer than the interactive map's line
    (a detour round another line) is not taken: checks/ink.py lists such pieces."""
    import numpy as np
    from scipy import ndimage
    from skimage.graph import route_through_array
    h, w = mask.shape
    x0, y0 = max(0, int(min(p[0] for p in pts)) - CORRIDOR - 2), max(0, int(min(p[1] for p in pts)) - CORRIDOR - 2)
    x1, y1 = min(w, int(max(p[0] for p in pts)) + CORRIDOR + 3), min(h, int(max(p[1] for p in pts)) + CORRIDOR + 3)
    sub = mask[y0:y1, x0:x1]
    line = np.ones(sub.shape, bool)
    for x, y in dense_pts(pts, 0.5):
        xi, yi = round(x) - x0, round(y) - y0
        if 0 <= yi < sub.shape[0] and 0 <= xi < sub.shape[1]:
            line[yi, xi] = False
    dist = ndimage.distance_transform_edt(line)
    cost = np.where(sub, 1.0, OFF) + PULL * dist
    cost[dist > CORRIDOR] = 1e6

    def end(q):
        qx, qy = round(q[0]) - x0, round(q[1]) - y0
        ys, xs = np.nonzero(sub[max(0, qy - END_R):qy + END_R + 1, max(0, qx - END_R):qx + END_R + 1])
        if not len(xs):
            return min(max(qy, 0), sub.shape[0] - 1), min(max(qx, 0), sub.shape[1] - 1)
        ys, xs = ys + max(0, qy - END_R), xs + max(0, qx - END_R)
        k = np.argmin((xs - qx) ** 2 + (ys - qy) ** 2)
        return ys[k], xs[k]
    idx, _c = route_through_array(cost, end(pts[0]), end(pts[-1]), fully_connected=True, geometric=True)
    path = [(c + x0, r + y0) for r, c in idx]
    if length(path) > 1.4 * length(pts) + 6:
        return pts  # a detour (the print's line goes another way, or not at all): keep the interactive map's
    return rdp(path, TOL) if len(path) > 2 else path


def rdp(pts, tol):
    if len(pts) < 3:
        return pts
    (ax, ay), (bx, by) = pts[0], pts[-1]
    n = math.hypot(bx - ax, by - ay) or 1e-9
    d = [abs((by - ay) * (x - ax) - (bx - ax) * (y - ay)) / n for x, y in pts[1:-1]]
    i = max(range(len(d)), key=d.__getitem__)
    if d[i] <= tol:
        return [pts[0], pts[-1]]
    return rdp(pts[:i + 2], tol)[:-1] + rdp(pts[i + 1:], tol)


def trim_text(pts, text):
    """A line's ends that run into a name's letters or symbol (the interactive map draws some on under its label)
    are cut back to where they leave them: the stretch along the name covers the gap."""
    h, w = text.shape

    def inside(q):
        x, y = round(q[0]), round(q[1])
        return 0 <= x < w and 0 <= y < h and text[y, x]
    i, j = 0, len(pts)
    while i < j and inside(pts[i]):
        i += 1
    while j > i and inside(pts[j - 1]):
        j -= 1
    # (pts are 1 px apart) a long stretch under letters is a name printed over its own line (Cabin Fever): kept
    i = i if i <= TRIM_MAX else 0
    j = j if len(pts) - j <= TRIM_MAX else len(pts)
    return pts[i:j] if j - i >= 2 else pts


def lines(V):
    from scipy.spatial import cKDTree
    w, h = CLIP[2] - CLIP[0], CLIP[3] - CLIP[1]
    masks, text = ink_masks(V)
    raw = []  # (name, class, dashed, points in map px)
    for t in V['trails']:
        for pl, st in zip(t['lines'], t['styles']):
            raw.append((t['name'], CLS.get(st['stroke']), st['dashed'], [tf(q) for q in pl]))
    for t in V['loose']:
        for pl in t['lines']:
            raw.append((t['name'], CLS.get(t['style']['stroke']), t['style']['dashed'], [tf(q) for q in pl]))
    raw = [r for r in raw if r[1] and len(r[3]) > 1 and length(r[3]) >= 3]  # the snowshoe trails have no class
    solid = [q for r in raw if not r[2] for q in dense_pts(r[3], 1.0)]
    tree = cKDTree(solid)
    out, copies = [], 0
    for name, cls, dashed, pts in raw:
        if dashed:
            d, _ = tree.query(dense_pts(pts, 1.0))
            if (d < 2.0).mean() > 0.8:
                copies += 1
                continue  # the black dashes over an advanced-intermediate run's blue line
        pts = trim_text(dense_pts(pts, 1.0), text)
        pts = route(pts, masks[cls])
        if len(pts) < 2 or length(pts) < 3:
            continue
        out.append({'id': len(out), 'cls': cls, 'lengthPx': round(length(pts)), 'name': name,
                    'points': [[round(100 * x / w, 3), round(100 * y / h, 3)] for x, y in pts]})
    json.dump({'_source': 'Steamboat interactive map (resorts-interactive.com map 1800) SVG lines, '
                          'tools/trailmap/resorts/steamboat/prepare.py; percent of the map image',
               'polylines': out}, open(os.path.join(W, 'pieces.json'), 'w'))
    print(f'  wrote pieces.json: {len(out)} pieces ({copies} dashed copies left out)')


def inside(a, b, pad=0.5):
    return a[0] >= b[0] - pad and a[1] >= b[1] - pad and a[2] <= b[2] + pad and a[3] <= b[3] + pad


def centre(b):
    return ((b[0] + b[2]) / 2, (b[1] + b[3]) / 2)


def symbol_shape(f):
    """'side' (a square or diamond: four straight sides), 'round' (a circle: curves only) or None (a letter)."""
    w, h = f['box'][2] - f['box'][0], f['box'][3] - f['box'][1]
    if f['parts'] != 1 or min(w, h) < 0.5 * max(w, h) or max(w, h) < 8 or max(w, h) > 25:
        return None
    body = f['cmds'].strip('MZmz')
    if body == 'llll' or body == 'lll':
        # four sides of about one length (a turned letter I is a long thin quadrilateral with a squarish box)
        q = f.get('poly') or []
        sides = [math.dist(a, b) for a, b in zip(q, q[1:] + q[:1]) if math.dist(a, b) > 0.3]
        if len(sides) >= 4 and min(sides) < 0.6 * max(sides):
            return None
        return 'side'
    if body == 'llllllll' and max(w, h) >= 19 and CLS.get(f['fill']) == 'black':
        return 'double'  # two diamonds point to point, one outline of eight sides (19 to 22 units; a Z is 17)
    if set(body) == {'c'} and 4 <= len(body) <= 8 and min(w, h) >= 0.75 * max(w, h):
        return 'round'
    return None


def two_lines(pts):
    """A name printed on two or more lines: its letters, in reading order, jump back against the way the text
    runs (the median step from a letter to the next) by more than two letter steps."""
    import numpy as np
    if len(pts) < 4:
        return False
    a = np.array(pts)
    d = np.diff(a, axis=0)
    axis = np.median(d, axis=0)  # the way the text runs: the typical step from a letter to the next
    axis = axis / (np.linalg.norm(axis) or 1)
    steps = d @ axis
    return bool((steps < -2 * np.median(np.abs(steps))).any())


def letter_ink(img):
    import numpy as np
    m = {k: np.linalg.norm(img - np.array(c), axis=2) < 70 for k, c in INK.items()}
    m['black'] = img.max(axis=2) < 90
    return m


def inked(boxes, m, dx=0, dy=0):
    """(the share of these fills, map px boxes, that the print shows: a fair part of the box in its colour; the
    mean ink share of the boxes), each box moved by dx, dy."""
    h, w = m.shape
    hits, tot = 0, 0.0
    for (x0, y0), (x1, y1) in boxes:
        sub = m[max(0, int(y0 + dy)):min(h, int(y1 + dy) + 1), max(0, int(x0 + dx)):min(w, int(x1 + dx) + 1)]
        f = sub.mean() if sub.size else 0.0
        hits += f >= 0.12
        tot += f
    return hits / max(1, len(boxes)), tot / max(1, len(boxes))


def place(boxes, m):
    """Where the print shows these fills: (dx, dy) of 0, 0 if it shows them there, else the offset within REACH
    px that puts most ink in them, if it shows them there (the 2026-27 artwork moved some names and symbols from
    where the interactive map keeps them); None if the print shows them nowhere near."""
    if inked(boxes, m)[0] >= 0.5:
        return 0, 0
    _, dx, dy = max((inked(boxes, m, dx, dy)[1], dx, dy)
                    for dx in range(-REACH, REACH + 1, 2) for dy in range(-REACH, REACH + 1, 2))
    _, dx, dy = max((inked(boxes, m, x, y)[1], x, y) for x in range(dx - 2, dx + 3) for y in range(dy - 2, dy + 3))
    return (dx, dy) if inked(boxes, m, dx, dy)[0] >= 0.7 else None


def labels(V):
    import numpy as np
    img = np.asarray(Image.open(os.path.join(W, 'map.png')).convert('RGB')).astype(float)
    ink = letter_ink(img)
    labels, symbols, gone, moved, unplaced, elsewhere = [], [], [], [], [], []
    w, h = CLIP[2] - CLIP[0], CLIP[3] - CLIP[1]
    own = {}  # each run's line points (map px), from pieces.json
    for p in json.load(open(os.path.join(W, 'pieces.json')))['polylines']:
        own.setdefault(p['name'], []).extend(dense_pts([(x * w / 100, y * h / 100) for x, y in p['points']], 2.0))
    for g, t in enumerate(V['trails']):
        col = [f for f in t['fills'] if CLS.get(f['fill'])]
        shapes = [f for f in col if symbol_shape(f)]
        groups = []  # a symbol's fills: the advanced-intermediate square and its diamond, a double diamond's two
        for f in shapes:
            for grp in groups:
                size = max(max(q['box'][2] - q['box'][0], q['box'][3] - q['box'][1]) for q in grp + [f])
                if any(math.dist(centre(q['box']), centre(f['box'])) < 1.3 * size for q in grp):
                    grp.append(f)
                    break
            else:
                groups.append([f])
        for grp in groups:
            cls = [CLS[f['fill']] for f in grp]
            kind = ('circle' if 'green' in cls else 'square' if 'blue' in cls
                    else 'double-diamond' if len(grp) >= 2 or symbol_shape(grp[0]) == 'double' else 'diamond')
            xs = [f['box'][0] for f in grp] + [f['box'][2] for f in grp]
            ys = [f['box'][1] for f in grp] + [f['box'][3] for f in grp]
            c = tf(((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2))
            # a symbol the print doesn't show there rates its run all the same, but is no end of its name (far)
            far = inked([(tf(f['box'][:2]), tf(f['box'][2:])) for f in grp], ink[cls[0]])[0] < 0.5
            if far:
                elsewhere.append(f"{kind} of {t['name']}")
            symbols.append({'t': kind, 'c': [round(c[0], 2), round(c[1], 2)], 'group': t['name'],
                            **({'far': True} if far else {})})
        letters = [f for f in col if not symbol_shape(f)]
        runs, run = [], []
        for f in letters:  # drawing order is reading order; a jump starts another printing of the name
            hgt = max(f['box'][3] - f['box'][1], f['box'][2] - f['box'][0])
            if run and math.dist(centre(run[-1]['box']), centre(f['box'])) > 2.5 * hgt:
                runs.append(run)
                run = []
            run.append(f)
        if run:
            runs.append(run)
        # a name on two lines: its second line starts a jump away, but its centre lies within about a line of the
        # first's (another printing of the name is far along the run)
        merged = []
        for r in runs:
            if merged:
                hgt = max(max(f['box'][3] - f['box'][1], f['box'][2] - f['box'][0]) for f in merged[-1] + r)
                c0 = centre([min(f['box'][0] for f in merged[-1]), min(f['box'][1] for f in merged[-1]),
                             max(f['box'][2] for f in merged[-1]), max(f['box'][3] for f in merged[-1])])
                c1 = centre([min(f['box'][0] for f in r), min(f['box'][1] for f in r), max(f['box'][2] for f in r),
                             max(f['box'][3] for f in r)])
                if math.dist(c0, c1) < 2.2 * hgt:
                    merged[-1] = merged[-1] + r
                    continue
            merged.append(r)
        runs = merged
        for r in runs:
            pts = [tf(centre(f['box'])) for f in r]
            at = place([(tf(f['box'][:2]), tf(f['box'][2:])) for f in r], ink[CLS[r[0]['fill']]])
            if at and at != (0, 0) and own.get(t['name']):
                # a move is taken only onto the run's own line (a name is printed in a gap of it)
                # its line runs into it: from both its first and last letter, the line is near
                def ends(dx, dy):
                    return max(min(math.dist((x + dx, y + dy), q) for q in own[t['name']])
                               for x, y in (pts[0], pts[-1]))
                if ends(*at) > 18 or ends(*at) > ends(0, 0) + 3:
                    at = None
            if at is None:
                if inked([(tf(f['box'][:2]), tf(f['box'][2:])) for f in r], ink[CLS[r[0]['fill']]])[0] < 0.2 \
                        and not own.get(t['name']):
                    gone.append(f"{t['name']} at {round(sum(p[0] for p in pts) / len(pts))},"
                                f"{round(sum(p[1] for p in pts) / len(pts))}")
                    continue
                unplaced.append(t['name'])  # kept where the interactive map has it, with no stretch along it
            elif at != (0, 0):
                moved.append(f"{t['name']} {at}")
                pts = [(x + at[0], y + at[1]) for x, y in pts]
            labels.append({'seq': 100 * g + len(labels) % 100, 'text': t['name'],
                           **({'two_line': True} if at is None or two_lines(pts) else {}),
                           'color': CLS[r[0]['fill']],
                           'size': round(max(max(f['box'][3] - f['box'][1], f['box'][2] - f['box'][0]) for f in r)
                                         * VICOMAP_AFFINE[4], 1),
                           'pts': [[round(x, 2), round(y, 2)] for x, y in pts],
                           'c': [round(sum(p[0] for p in pts) / len(pts), 2), round(sum(p[1] for p in pts) / len(pts), 2)]})
        if not runs:  # letters drawn elsewhere: the label at the group's white halos
            words = [f['box'] for f in t['fills'] if f['fill'] in ('#fff', '#ffffff')
                     and not any(inside(q['box'], f['box']) for q in shapes)]
            if words:
                pts = [tf(centre(b)) for b in words]
                labels.append({'seq': 100 * g + 99, 'text': t['name'], 'color': 'black', 'size': 0, 'halo': True,
                               'pts': [[round(x, 2), round(y, 2)] for x, y in pts],
                               'c': [round(sum(p[0] for p in pts) / len(pts), 2),
                                     round(sum(p[1] for p in pts) / len(pts), 2)]})
    json.dump({'labels': labels, 'symbols': symbols}, open(os.path.join(W, 'printed.json'), 'w'), indent=0)
    print(f'  wrote printed.json: {len(labels)} labels, {len(symbols)} symbols\n  names moved onto the print: '
          + '; '.join(moved) + '\n  names not found on the print near where the interactive map has them (kept '
          'there, no stretch): ' + ', '.join(unplaced) + '\n  names not on this print: ' + '; '.join(gone)
          + '\n  symbols not printed where the interactive map has them (rating only): ' + ', '.join(elsewhere))


if __name__ == '__main__':
    os.makedirs(W, exist_ok=True)
    image()
    V = parse()
    lines(V)
    labels(V)
