"""Trail-name labels from a trail-map PDF whose names are outlined glyphs
(filled vector shapes, no text at all: Copper Mountain and Keystone 2025-26).

    G=work/glyphs.json L=work/letters.json
    python3 tools/trailmap/pdf_glyphs.py collect map.pdf --out $G \\
        --color blue=0,0.48,0.76 --color green=0,0.61,0.4 --color black=0,0,0
    python3 tools/trailmap/pdf_glyphs.py sheet map.pdf --glyphs $G --letters $L --out work/sheet.png
    python3 tools/trailmap/pdf_glyphs.py read --glyphs $G --letters $L 12=a 13=e 40=S ...
    python3 tools/trailmap/pdf_glyphs.py labels map.pdf --glyphs $G --letters $L --out work/labels.json \\
        --square blue --diamond black --circle green

collect: every fill in a trail-name colour small enough to be a glyph, with a
shape signature that ignores rotation and size (the outline's item kinds and
its chord lengths over their total). A shape drawn twice at the same spot (a
halo pass under the visible one, or last season's colour under this one's)
keeps only the last drawn. Identical shapes are clustered.

sheet: each shape not yet read, drawn upright (turned so the next glyph of
its label lies to the right) in black between its neighbours in grey, twice,
numbered. Read the sheet and record each shape's character with `read`; the
letters file is keyed by shape, so it survives re-clustering and can be reused
for another map in the same font. Size tells case apart where the shapes
match (o/O, s/S): a shape only takes a letter whose glyph size is within 15%.

labels: glyphs are drawn in reading order, so a label is a run of
consecutive same-colour glyphs (each within --join pt of the last); a word
gap is a gap between outlines well over the label's median letter gap, or,
with --space, over that many points along the reading direction (condensed
fonts). Comma and apostrophe are often one shape turned over: read it as
either, and the side of the line it sits on decides; so are n and u, and !
and i, in some fonts (--turned nu: the half its gap is in decides). A run
whose glyphs all sit on another, longer (or later) run's is a fragment copy
and is dropped. Difficulty symbols are fills too: an even four-sided fill in
the --square colour is a square, in the --diamond colour a diamond; two diamonds
side by side (or one eight-sided fill) are a double diamond, and EX when
small white letter fills sit inside; four curves in the --circle colour are a
circle. Output: {"labels": [{seq, text, color, size, c, pts}], "symbols":
[{t, c, color, seq}]} in PDF points, c a label's centre and pts its glyph
centres in reading order (the same fields as pdf_labels.py, so the matching
step is the same). Join names set on two lines and attach each symbol to the
label it is printed with per map; layouts differ.

Requires: pip install pymupdf pillow
"""
import argparse
import collections
import json
import math

import pymupdf
from PIL import Image, ImageChops, ImageDraw, ImageFont

FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'


def bez(a, b, c, e, n=6):
    return [((1 - t) ** 3 * a.x + 3 * (1 - t) ** 2 * t * b.x + 3 * (1 - t) * t * t * c.x + t ** 3 * e.x,
             (1 - t) ** 3 * a.y + 3 * (1 - t) ** 2 * t * b.y + 3 * (1 - t) * t * t * c.y + t ** 3 * e.y)
            for t in [i / n for i in range(1, n + 1)]]


def subpaths(items):
    subs, cur, last = [], [], None
    for it in items:
        if it[0] == 're':
            r = it[1]
            subs.append([('l', pymupdf.Point(r.x0, r.y0), pymupdf.Point(r.x1, r.y0))])
            continue
        if it[0] == 'qu':
            continue
        s = it[1]
        if last is not None and math.dist((s.x, s.y), last) > 0.01:
            subs.append(cur)
            cur = []
        cur.append(it)
        last = (it[-1].x, it[-1].y)
    if cur:
        subs.append(cur)
    return subs


def polygons(items, n=8):
    out, cur, last = [], [], None
    for it in items:
        if it[0] == 're':
            r = it[1]
            out.append([(r.x0, r.y0), (r.x1, r.y0), (r.x1, r.y1), (r.x0, r.y1)])
            continue
        if it[0] == 'qu':
            continue
        s = it[1]
        if last is not None and math.dist((s.x, s.y), last) > 0.01:
            out.append(cur)
            cur = []
        if not cur:
            cur.append((s.x, s.y))
        cur += bez(*it[1:5], n=n) if it[0] == 'c' else [(it[2].x, it[2].y)]
        last = (it[-1].x, it[-1].y)
    if cur:
        out.append(cur)
    return [pl for pl in out if len(pl) >= 3]


def cluster(glyphs):
    clusters = []
    for i, g in enumerate(glyphs):
        for c in clusters:
            if (c['kinds'] == g['kinds'] and max(abs(a - b) for a, b in zip(c['sig'], g['sig'])) < 0.03
                    and abs(math.log(c['size'] / g['size'])) < math.log(1.15)):
                c['m'].append(i)
                break
        else:
            clusters.append({'kinds': g['kinds'], 'sig': g['sig'], 'size': g['size'], 'm': [i]})
    clusters.sort(key=lambda c: -len(c['m']))
    for k, c in enumerate(clusters):
        for i in c['m']:
            glyphs[i]['cl'] = k
    return [{'kinds': c['kinds'], 'sig': c['sig'], 'size': c['size'], 'n': len(c['m']), 'm': c['m']} for c in clusters]


def letter(table, g):
    best = None
    for t in table:
        if t['kinds'] != g['kinds'] or len(t['sig']) != len(g['sig']):
            continue
        if max(abs(a - b) for a, b in zip(t['sig'], g['sig'])) >= 0.03:
            continue
        r = abs(math.log(t['size'] / g['size']))
        if r < math.log(1.15) and (best is None or r < best[0]):
            best = (r, t['ch'])
    return best[1] if best else None


def collect(a):
    page = pymupdf.open(a.pdf)[a.page]
    classes = {}
    for spec in a.color:
        name, rgb = spec.split('=')
        classes[tuple(round(float(v), 2) for v in rgb.split(','))] = name
    excludes = [tuple(map(float, e.split(','))) for e in a.exclude]
    at = {}
    for d in page.get_drawings():
        if d['type'] not in ('f', 'fs') or not d.get('fill'):
            continue
        col = classes.get(tuple(round(v, 2) for v in d['fill']))
        r = d['rect']
        if not col or not a.min_size <= max(r.width, r.height) < a.max_size:
            continue
        if any(e[0] <= r.x0 and r.x1 <= e[2] and e[1] <= r.y0 and r.y1 <= e[3] for e in excludes):
            continue
        pts, lens, kinds = [], [], []
        for sp in subpaths(d['items']):
            kinds.append(''.join(it[0] for it in sp))
            for it in sp:
                s, e = it[1], it[-1]
                lens.append(math.dist((s.x, s.y), (e.x, e.y)))
                pts += [(s.x, s.y)] + (bez(*it[1:5]) if it[0] == 'c' else [(e.x, e.y)])
        for it in d['items']:  # rectangles (a sans-serif I): their outline, for measuring gaps
            if it[0] == 're':
                q = it[1]
                pts += [(q.x0 + (q.x1 - q.x0) * t / 4, y) for y in (q.y0, q.y1) for t in range(5)]
                pts += [(x, q.y0 + (q.y1 - q.y0) * t / 4) for x in (q.x0, q.x1) for t in range(5)]
        tot = sum(lens) or 1
        key = (round(r.x0, 1), round(r.y0, 1), round(r.x1, 1), round(r.y1, 1), '|'.join(kinds))
        at.pop(key, None)  # drawn again here: the later copy is the one that shows
        at[key] = {'seq': d['seqno'], 'col': col, 'rect': [round(v, 2) for v in r],
                   'c': [round(sum(q[0] for q in pts) / len(pts), 2), round(sum(q[1] for q in pts) / len(pts), 2)],
                   'kinds': '|'.join(kinds), 'sig': [round(v / tot, 3) for v in lens], 'size': round(tot, 2),
                   'pts': [[round(x, 2), round(y, 2)] for x, y in pts]}
    glyphs = sorted(at.values(), key=lambda g: g['seq'])
    clusters = cluster(glyphs)
    json.dump({'pdf': a.pdf, 'page': a.page, 'glyphs': glyphs, 'clusters': clusters}, open(a.out, 'w'))
    print(f'{len(glyphs)} glyph fills, {len(clusters)} shapes ->', a.out, dict(collections.Counter(g['col'] for g in glyphs)))


def direction(G, i, join):
    g, best = G[i], None
    for j in (i - 1, i + 1):
        if 0 <= j < len(G) and G[j]['col'] == g['col']:
            d = math.dist(G[j]['c'], g['c'])
            if d < join and (best is None or d < best[0]):
                best = (d, j)
    if not best:
        return 0.0
    j = best[1]
    p, q = (g['c'], G[j]['c']) if j > i else (G[j]['c'], g['c'])
    return math.atan2(q[1] - p[1], q[0] - p[0])


def sheet(a):
    doc = json.load(open(a.glyphs))
    G, C = doc['glyphs'], doc['clusters']
    page = pymupdf.open(a.pdf)[doc['page']]
    D = {d['seqno']: d for d in page.get_drawings()}
    try:
        table = json.load(open(a.letters)) if a.letters else []
    except FileNotFoundError:
        table = []
    font = ImageFont.truetype(FONT, 14)

    z = a.zoom
    cw, chh = int(32 * z), int(12 * z)  # one context strip: the glyph (black) between its neighbours (grey)

    def render(i):
        g = G[i]
        th = -direction(G, i, a.join)
        cx, cy = g['c']
        strip = Image.new('L', (cw, chh), 255)
        for j in range(max(0, i - 3), min(len(G), i + 4)):
            n = G[j]
            if n['col'] != g['col'] or math.dist(n['c'], g['c']) > 3 * a.join:
                continue
            mask = Image.new('1', strip.size, 0)
            for pl in polygons(D[n['seq']]['items']):
                rot = [((x - cx) * math.cos(th) - (y - cy) * math.sin(th), (x - cx) * math.sin(th) + (y - cy) * math.cos(th))
                       for x, y in pl]
                m = Image.new('1', strip.size, 0)
                ImageDraw.Draw(m).polygon([(cw / 2 + x * z, chh / 2 + y * z) for x, y in rot], fill=1)
                mask = ImageChops.logical_xor(mask, m)
            strip.paste(0 if j == i else 175, mask=mask)
        return strip

    todo = [k for k, c in enumerate(C) if a.all or letter(table, G[c['m'][0]]) is None]
    todo = [k for k in todo if C[k]['n'] >= a.min_count]
    todo = [int(v) for v in a.ids.split(',')] if a.ids else todo[a.skip: a.skip + a.limit]
    cols, W, H = 6, cw + 10, 2 * chh + 30
    im = Image.new('RGB', (cols * W, max(1, (len(todo) + cols - 1) // cols) * H), 'white')
    dr = ImageDraw.Draw(im)
    for n, k in enumerate(todo):
        c = C[k]
        x, y = (n % cols) * W, (n // cols) * H
        for m, i in enumerate(c['m'][:2]):
            im.paste(render(i), (x + 5, y + 5 + m * chh))
        dr.text((x + 5, y + 2 * chh + 8), f"#{k} n={c['n']} {G[c['m'][0]]['col']} {c['size']:.0f}", fill=(200, 0, 0), font=font)
        dr.rectangle((x, y, x + W - 2, y + H - 2), outline=(200, 200, 200))
    im.save(a.out)
    print(f'{len(todo)} shapes to read -> {a.out}')


def read(a):
    doc = json.load(open(a.glyphs))
    G, C = doc['glyphs'], doc['clusters']
    try:
        table = json.load(open(a.letters))
    except FileNotFoundError:
        table = []
    for spec in a.pairs:
        k, ch = spec.split('=', 1)
        g = G[C[int(k)]['m'][0]]
        table = [t for t in table if not (t['kinds'] == g['kinds'] and t['sig'] == g['sig'] and t['size'] == g['size'])]
        table.append({'kinds': g['kinds'], 'sig': g['sig'], 'size': g['size'], 'ch': ch})
    json.dump(table, open(a.letters, 'w'))
    print(len(table), 'shapes in', a.letters)


def labels(a):
    doc = json.load(open(a.glyphs))
    G = doc['glyphs']
    table = json.load(open(a.letters))
    page = pymupdf.open(a.pdf)[doc['page']]
    white = []
    for d in page.get_drawings():
        if d['type'] in ('f', 'fs') and d.get('fill') and tuple(round(v, 2) for v in d['fill']) == (1.0, 1.0, 1.0):
            r = d['rect']
            if max(r.width, r.height) < 3.5:
                white.append(((r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2))

    def inside(rect):
        return sum(1 for w in white if rect[0] < w[0] < rect[2] and rect[1] < w[1] < rect[3])

    syms = []
    for g in G:
        k, s, big = g['kinds'], g['sig'], max(g['rect'][2] - g['rect'][0], g['rect'][3] - g['rect'][1]) >= a.sym_min
        even = len(s) > 0 and max(s) < 1.4 * min(s)
        g['ch'] = None
        if big and k == 'llll' and even and g['col'] in a.square:
            g['sym'] = 'square'
        elif big and k == 'llll' and even and g['col'] in a.diamond:
            g['sym'] = 'diamond'
        elif big and k == 'llllllll' and even and g['col'] in a.diamond:
            g['sym'] = 'ex' if inside(g['rect']) >= 2 else 'double-diamond'
        elif big and k == 'cccc' and g['col'] in a.circle:
            g['sym'] = 'circle'
        else:
            g['ch'] = letter(table, g)
        if g.get('sym'):
            syms.append({'t': g['sym'], 'c': g['c'], 'color': g['col'], 'seq': g['seq'], 'rect': g['rect']})
    # two diamonds side by side: a double diamond (EX with white letters inside)
    merged, used = [], set()
    for i, s in enumerate(syms):
        if i in used:
            continue
        if s['t'] == 'diamond':
            side = max(s['rect'][2] - s['rect'][0], s['rect'][3] - s['rect'][1])
            j = next((j for j, t in enumerate(syms) if j != i and j not in used and t['t'] == 'diamond'
                      and math.dist(t['c'], s['c']) < a.double_dist * side), None)
            if j is not None:
                used.add(j)
                t = syms[j]
                rect = [min(s['rect'][0], t['rect'][0]), min(s['rect'][1], t['rect'][1]),
                        max(s['rect'][2], t['rect'][2]), max(s['rect'][3], t['rect'][3])]
                s = {**s, 't': 'ex' if inside(rect) >= 2 else 'double-diamond', 'rect': rect,
                     'c': [round((s['c'][0] + t['c'][0]) / 2, 2), round((s['c'][1] + t['c'][1]) / 2, 2)]}
        merged.append(s)
    syms = [{k: v for k, v in s.items() if k != 'rect'} for s in merged]

    def gap(p, q):
        return min(math.dist(u, v) for u in p['pts'][::2] for v in q['pts'][::2])

    def directions(run):
        """The local reading direction at each pair of neighbours, from the centres of the full-size glyphs
        around it (marks such as ’ , . - sit off the baseline and would skew it)."""
        sizes = sorted(g['size'] for g in run)
        full = [k for k, g in enumerate(run) if g['size'] >= 0.6 * sizes[len(sizes) // 2]]
        out = []
        for k in range(len(run) - 1):
            near = [j for j in full if k - 2 <= j <= k + 3] or full
            p, q = run[near[0]]['c'], run[near[-1]]['c']
            if near[0] == near[-1]:
                p, q = run[k]['c'], run[k + 1]['c']
            n = math.dist(p, q) or 1
            out.append(((q[0] - p[0]) / n, (q[1] - p[1]) / n))
        return out

    def projected_gaps(run, dirs):
        return [min(x * u[0] + y * u[1] for x, y in run[k + 1]['pts']) - max(x * u[0] + y * u[1] for x, y in run[k]['pts'])
                for k, u in enumerate(dirs)]

    def side(run, k, u):
        """+1 if glyph k sits above its neighbours' centre line (an apostrophe), -1 below (a comma)."""
        nb = [run[j]['c'] for j in (k - 1, k + 1) if 0 <= j < len(run)]
        mx, my = sum(q[0] for q in nb) / len(nb), sum(q[1] for q in nb) / len(nb)
        g = run[k]['c']
        return 1 if (g[0] - mx) * u[1] - (g[1] - my) * u[0] > 0 else -1

    def open_side(g, u):
        """Where glyph g's centre line, upright, crosses no ink: -1 mostly below its middle (n between its legs, !
        between stroke and dot), +1 mostly above (u, i), 0 nowhere. u is the reading direction; up is u turned
        back a right angle (PDF y runs down)."""
        up = (u[1], -u[0])
        polys = polygons(D[g['seq']]['items'])
        along = [x * u[0] + y * u[1] for pl in polys for x, y in pl]
        ext = [x * up[0] + y * up[1] for pl in polys for x, y in pl]
        a0, h0 = (max(along) + min(along)) / 2, (max(ext) + min(ext)) / 2
        h = (max(ext) - min(ext)) / 2

        def filled(t):
            px, py = a0 * u[0] + (h0 + t * h) * up[0], a0 * u[1] + (h0 + t * h) * up[1]
            inside = False
            for pl in polys:
                for (x0, y0), (x1, y1) in zip(pl, pl[1:] + pl[:1]):
                    if (y0 > py) != (y1 > py) and px < x0 + (py - y0) * (x1 - x0) / (y1 - y0):
                        inside = not inside
            return inside
        empty = [t / 20 for t in range(-19, 20) if not filled(t / 20)]
        return 0 if not empty else -1 if sum(empty) < 0 else 1

    D = {d['seqno']: d for d in page.get_drawings()} if a.turned else {}
    runs, cur = [], []
    for g in (g for g in G if g.get('ch')):
        if cur and (g['col'] != cur[-1]['col'] or math.dist(g['c'], cur[-1]['c']) > a.join
                    or g['seq'] - cur[-1]['seq'] > a.seq_gap):
            runs.append(cur)
            cur = []
        cur.append(g)
    if cur:
        runs.append(cur)
    out = []
    for run in runs:
        if len(run) < 2 and run[0]['col'] not in a.single:
            continue  # a lone mark, not a label
        dirs = directions(run)
        if a.space is None:
            gaps = [gap(p, q) for p, q in zip(run, run[1:])]
            med = sorted(gaps)[len(gaps) // 2]
            space = [d > max(2.3 * med, med + 0.9) for d in gaps]
        else:
            space = [d > a.space for d in projected_gaps(run, dirs)]
        chars = [g['ch'] for g in run]
        for k, ch in enumerate(chars):
            if ch in (',', '’'):  # one shape turned over: above the line it is an apostrophe
                chars[k] = '’' if side(run, k, dirs[min(k, len(dirs) - 1)]) > 0 else ','
            for pair in a.turned:  # two letters that are one shape turned over (n/u): the half with the gap decides
                if ch in pair and len(run) > 1:
                    opening = open_side(run[k], dirs[min(k, len(dirs) - 1)])
                    if opening:
                        chars[k] = pair[0] if opening < 0 else pair[1]
        text = chars[0]
        for ch, sp in zip(chars[1:], space):
            text += (' ' if sp else '') + ch
        pts = [g['c'] for g in run]
        out.append({'seq': run[0]['seq'], 'text': text, 'color': run[0]['col'], 'size': round(max(g['size'] for g in run), 1),
                    'pts': pts, 'c': [round(sum(q[0] for q in pts) / len(pts), 1), round(sum(q[1] for q in pts) / len(pts), 1)]})
    keep = []
    for o in sorted(out, key=lambda o: (-len(o['pts']), -o['seq'])):
        if any(all(any(math.dist(q, r) < 0.8 for r in k['pts']) for q in o['pts']) for k in keep):
            continue  # a fragment copy of a longer (or later) label
        keep.append(o)
    keep.sort(key=lambda o: o['seq'])
    json.dump({'labels': keep, 'symbols': syms}, open(a.out, 'w'))
    unread = collections.Counter(g['cl'] for g in G if not g.get('ch') and not g.get('sym'))
    print(f'{len(keep)} labels, {len(syms)} symbols', dict(collections.Counter(s['t'] for s in syms)), '->', a.out)
    if unread:
        print(f'{sum(unread.values())} glyphs in {len(unread)} unread shapes (sheet, then read):', unread.most_common(12))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    c = sub.add_parser('collect')
    c.add_argument('pdf')
    c.add_argument('--page', type=int, default=0)
    c.add_argument('--color', action='append', required=True, help='class=r,g,b (0-1, 2 decimals)')
    c.add_argument('--min-size', type=float, default=0.6, help='pt; smaller fills are dots and specks')
    c.add_argument('--max-size', type=float, default=10.5, help='pt; larger fills are lines, icons or areas')
    c.add_argument('--exclude', action='append', default=[], help='x0,y0,x1,y1 pt: drop fills wholly inside (legend)')
    c.add_argument('--out', required=True)
    s = sub.add_parser('sheet')
    s.add_argument('pdf')
    s.add_argument('--glyphs', required=True)
    s.add_argument('--letters')
    s.add_argument('--out', required=True)
    s.add_argument('--all', action='store_true', help='include shapes already read')
    s.add_argument('--min-count', type=int, default=1)
    s.add_argument('--limit', type=int, default=48)
    s.add_argument('--skip', type=int, default=0, help='start after this many shapes (next sheet)')
    s.add_argument('--ids', help='only these shapes, e.g. 6,11,20 (a closer look)')
    s.add_argument('--zoom', type=float, default=6.0, help='px per pt')
    s.add_argument('--join', type=float, default=9.0)
    r = sub.add_parser('read')
    r.add_argument('--glyphs', required=True)
    r.add_argument('--letters', required=True)
    r.add_argument('pairs', nargs='+', help='cluster=char (e.g. 12=a 40=S 7=’)')
    lb = sub.add_parser('labels')
    lb.add_argument('pdf')
    lb.add_argument('--glyphs', required=True)
    lb.add_argument('--letters', required=True)
    lb.add_argument('--out', required=True)
    lb.add_argument('--square', action='append', default=[], help='colour class of square symbols')
    lb.add_argument('--diamond', action='append', default=[], help='colour class of diamond symbols')
    lb.add_argument('--circle', action='append', default=[], help='colour class of circle symbols')
    lb.add_argument('--sym-min', type=float, default=2.5, help='pt; smaller even shapes are dots, not symbols')
    lb.add_argument('--double-dist', type=float, default=0.8,
                    help='two diamonds whose centres are closer than this many diamond widths are a double diamond '
                         '(1.6 where a gap separates them: Sunday River)')
    lb.add_argument('--join', type=float, default=9.0, help='pt; a farther glyph starts a new label')
    lb.add_argument('--space', type=float,
                    help='pt: a word gap is a gap over this between outlines along the reading direction (condensed '
                         'fonts; Keystone 0.75). Default: a gap well over the label\'s median outline-to-outline gap')
    lb.add_argument('--seq-gap', type=int, default=6, help='drawing-order gap that starts a new label')
    lb.add_argument('--turned', action='append', default=[],
                    help='two letters that are one shape turned over, the one with its gap low first: nu, !i (a shape '
                         'read as either is decided by which half its gap is in: Smugglers\' Notch)')
    lb.add_argument('--single', action='append', default=[],
                    help='colour class whose lone glyphs are labels too (one-digit numbered circles: Sugarloaf)')
    a = ap.parse_args()
    {'collect': collect, 'sheet': sheet, 'read': read, 'labels': labels}[a.cmd](a)


if __name__ == '__main__':
    main()
