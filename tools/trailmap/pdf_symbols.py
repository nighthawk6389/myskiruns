"""Difficulty symbols straight from a vector trail-map PDF, to check the readers'
symbol reports (prompts/0-new-map.md, job 2) by an independent method.

    python3 tools/trailmap/pdf_symbols.py map.pdf --page 1 --clip 0,0,1458,913 --scale 3 \\
        --circle 0.05,0.53,0.26 --square 0.21,0.33,0.65 --diamond 0.01,0.02,0.02 \\
        --exclude 0,480,140,913 --out work/pdf_symbols.json \\
        --check work/labels.json --trails src/data/resorts/okemo/trails.ts

A symbol is a small filled shape in a symbol colour: a circle is a fill made of
exactly four curves; a square or diamond is a four-cornered fill with
near-equal sides (diamonds at most --max-diamond pt, so glade-icon frames in
the same colour don't count); two diamonds 0.6-1.6 sizes apart are a double
diamond. With --rounded (Hunter's symbols have rounded corners) a square or
diamond is any fill of lines and curves about as wide as tall, and a double
diamond is one fill about 1.5x as wide as tall. Take the colours from the printed legend's symbols (tally small fills
with pymupdf); --exclude the legend itself. Output: [{type, src, sizePt}] with
src in map-image px, the same grid as extract_pdf_vectors.py with the same
--clip and --scale.

--check compares each trail's difficulty (trails.ts) with the PDF symbols
within reach of its label positions (labels.json from seed_roster.py; reach =
5.5 px per letter + 60) and prints the trails with no matching symbol, to
look at on a crop. Okemo 2025-26: 120 of 127 matched; the other 7 were
printed with no difficulty symbol (5 terrain parks, Easy Street) or drawn
with a differently built circle (Fairway). Check every diamond on a crop
anyway: this tells single from double, not which label a symbol belongs to.

Requires: pip install pymupdf
"""
import argparse
import json
import math
import re

import pymupdf

SYM_DIFF = {'circle': 'green', 'square': 'blue', 'diamond': 'black', 'double-diamond': 'double-black'}


def rgb(s):
    return tuple(round(float(v), 2) for v in s.split(','))


def corners(d):
    pts = []
    for it in d['items']:
        if it[0] == 'l':
            pts += [(it[1].x, it[1].y), (it[2].x, it[2].y)]
        elif it[0] == 'qu':
            q = it[1]
            pts += [(q.ul.x, q.ul.y), (q.ur.x, q.ur.y), (q.lr.x, q.lr.y), (q.ll.x, q.ll.y)]
        elif it[0] == 're':
            r = it[1]
            pts += [(r.x0, r.y0), (r.x1, r.y0), (r.x1, r.y1), (r.x0, r.y1)]
    uniq = []
    for p in pts:
        if all(math.dist(p, u) > 0.05 for u in uniq):
            uniq.append(p)
    return uniq


def extract(a):
    x0, y0, x1, y1 = map(float, a.clip.split(','))
    ex = [tuple(map(float, e.split(','))) for e in a.exclude]
    colours = {rgb(a.circle): 'circle', rgb(a.square): 'square', rgb(a.diamond): 'diamond'}
    found = []
    for d in pymupdf.open(a.pdf)[a.page].get_drawings():
        typ = colours.get(rgb(','.join(map(str, d['fill'])))) if d['type'] in ('f', 'fs') and d.get('fill') else None
        r = d['rect']
        if not typ or not 1.2 <= max(r.width, r.height) <= a.max_size:
            continue
        cx, cy = (r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2
        if not (x0 <= cx <= x1 and y0 <= cy <= y1) or any(e[0] <= cx <= e[2] and e[1] <= cy <= e[3] for e in ex):
            continue
        kinds = [it[0] for it in d['items']]
        if typ == 'circle':
            if kinds != ['c'] * 4 or not 0.75 < r.width / r.height < 1.33:
                continue
            size = (r.width + r.height) / 2
        elif a.rounded and 'c' in kinds and 'l' in kinds:
            # rounded corners: judged by the bounding box. A fill in the diamond colour about 1.5x as wide as
            # tall is a double diamond drawn as one outline (Hunter)
            ratio, size = r.width / r.height, r.height
            if typ == 'diamond' and 1.3 < ratio < 1.8:
                typ = 'double-diamond'
            elif not 0.8 < ratio < 1.25 or size > (a.max_diamond if typ == 'diamond' else 7):
                continue
        else:
            if kinds not in (['l'] * 3, ['l'] * 4, ['qu'], ['re']):
                continue
            c4 = corners(d)
            if len(c4) != 4:
                continue
            cx, cy = sum(p[0] for p in c4) / 4, sum(p[1] for p in c4) / 4
            c4.sort(key=lambda p: math.atan2(p[1] - cy, p[0] - cx))
            sides = [math.dist(c4[i], c4[(i + 1) % 4]) for i in range(4)]
            size = sum(sides) / 4
            if max(sides) / min(sides) > 1.35 or size < 1.0 or (typ == 'diamond' and size > a.max_diamond):
                continue
        if not any(f['type'] == typ and math.dist(f['pt'], (cx, cy)) < 0.4 for f in found):  # drawn twice (halo)
            found.append({'type': typ, 'pt': (cx, cy), 'size': size})
    out = [f for f in found if f['type'] != 'diamond']
    dia = [f for f in found if f['type'] == 'diamond']
    used = set()
    for i, p in enumerate(dia):
        if i in used:
            continue
        pair = min(((math.dist(p['pt'], q['pt']), j) for j, q in enumerate(dia)
                    if j > i and j not in used and 0.6 * p['size'] <= math.dist(p['pt'], q['pt']) <= 1.6 * p['size']),
                   default=None)
        used.add(i)
        if pair:
            q = dia[pair[1]]
            used.add(pair[1])
            out.append({'type': 'double-diamond', 'size': p['size'],
                        'pt': ((p['pt'][0] + q['pt'][0]) / 2, (p['pt'][1] + q['pt'][1]) / 2)})
        else:
            out.append(p)
    return [{'type': f['type'], 'src': [round((f['pt'][0] - x0) * a.scale), round((f['pt'][1] - y0) * a.scale)],
             'sizePt': round(f['size'], 2)} for f in out]


def check(syms, labels_file, trails_file):
    labels = json.load(open(labels_file))
    diff = dict(re.findall(r"id: '([^']+)'.*?difficulty: '([^']+)'", open(trails_file).read()))
    ok = 0
    for tid, e in sorted(labels.items()):
        if tid not in diff:
            continue
        reach = 5.5 * len(e['mapName']) + 60
        near = sorted((round(math.dist(s['src'], p)), s['type']) for s in syms for p in e['positions']
                      if math.dist(s['src'], p) <= reach)
        if any(SYM_DIFF[t] == diff[tid] for _, t in near):
            ok += 1
        else:
            print(f"check {tid} ({diff[tid]}; readers saw {e['symbols']}): nearby PDF symbols {near[:3] or 'none'}")
    print(f'{ok}/{sum(1 for t in labels if t in diff)} trails have a PDF symbol matching their difficulty by the label')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('pdf')
    ap.add_argument('--page', type=int, default=0)
    ap.add_argument('--clip', required=True, help='x0,y0,x1,y1 in PDF points (as for extract_pdf_vectors.py)')
    ap.add_argument('--scale', type=float, required=True, help='image px per PDF point (as for extract_pdf_vectors.py)')
    ap.add_argument('--circle', required=True, help='fill colour r,g,b (0-1) of the easiest symbol')
    ap.add_argument('--square', required=True, help='fill colour of the more-difficult symbol')
    ap.add_argument('--diamond', required=True, help='fill colour of the diamond symbols')
    ap.add_argument('--max-diamond', type=float, default=2.6, help='larger dark squares are icon frames (pt)')
    ap.add_argument('--max-size', type=float, default=7, help='larger fills are not symbols (pt, bounding box)')
    ap.add_argument('--rounded', action='store_true',
                    help='symbols have rounded corners (lines and curves): squares and diamonds are judged by their '
                         'bounding box, and a diamond-coloured fill 1.3-1.8x as wide as tall is a double diamond')
    ap.add_argument('--exclude', action='append', default=[], help='x0,y0,x1,y1 in PDF points, e.g. the legend')
    ap.add_argument('--out', required=True)
    ap.add_argument('--check', help="labels.json from seed_roster.py: compare with the trails' difficulties")
    ap.add_argument('--trails', help='trails.ts (with --check)')
    a = ap.parse_args()
    syms = extract(a)
    json.dump(syms, open(a.out, 'w'), indent=0)
    from collections import Counter
    print(f'{len(syms)} symbols -> {a.out}:', dict(Counter(s["type"] for s in syms)))
    if a.check:
        check(syms, a.check, a.trails)


if __name__ == '__main__':
    main()
