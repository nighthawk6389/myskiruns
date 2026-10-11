"""Look at a PDF resort's line pieces while settling them on crops (docs/trail-map-playbook.md, Part 1, step 6),
for a resort read by pdf_resort.py (run its regen.sh first: the pieces and their names are in its work folder).

    python3 tools/trailmap/pieces.py info park-city 2400,1100,2800,1400
        # every piece crossing the box (map px): id, class, name (or ? undecided, - not a trail), how it was named,
        # length, end points; then the names printed in the box with their symbol
    python3 tools/trailmap/pieces.py pair big-sky/main 2400,1100,2800,1400 2 work/big-sky/pair.png
        # the crop twice, side by side: plain (the drawn lines as printed), and with every piece tagged id:name
    python3 tools/trailmap/pieces.py seq park-city 412,413 [--k 3] [--pdf work/park-city/parkcity.pdf] [--page 0]
        # the PDF stroke each piece came from (its seqno: the drawing order) and the strokes drawn just before and
        # after it with their pieces' names: an artwork usually draws one run's strokes one after another, so a piece
        # drawn among another run's strokes is worth a second look
    python3 tools/trailmap/pieces.py at brighton 55:0.15 55:0.6 18
        # the point (map px) a fraction along each piece (default halfway): a point for decisions.py that lies on it
    python3 tools/trailmap/pieces.py draw brighton 1690,1270,1900,1520 4 work/brighton/d.png 56 55 18
        # the given pieces alone over the crop, each in its own colour with its id, a ring at its first point: which
        # stroke runs where, where one ends and the next starts

Map px are the work folder's map.png px (the grid of the review tiles and decisions.py).
"""
import argparse
import contextlib
import glob
import io
import math
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pdf_resort as pr  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))


def built(rid):
    r = pr.Resort(rid)
    with contextlib.redirect_stdout(io.StringIO()):
        r.build()
    return r


def name_of(r, pid):
    return '/'.join(sorted(r.assign.get(pid, []))) or ('-' if pid in r.unnamed else '?')


def info(a):
    r = built(a.resort)
    b = tuple(map(float, a.box.split(',')))
    inb = lambda x, y: b[0] <= x <= b[2] and b[1] <= y <= b[3]  # noqa: E731
    for p in r.P:
        q = r.pts_of(p)
        if not any(inb(*v) for v in q):
            continue
        how = 'stretch' if p['id'] in r.traced else r.why.get(p['id'], '')
        print(f"{p['id']:4d} {p['cls']:9s} {name_of(r, p['id']):26s} {how:26s} L{p['lengthPx']:5d} "
              f"({q[0][0]:.0f},{q[0][1]:.0f})-({q[-1][0]:.0f},{q[-1][1]:.0f})")
    for n in r.names_:
        if any(inb(*v) for v in n['pts']):
            print(f"  name {n['name']!r} ({n.get('symbol') or 'no symbol'}) from ({n['pts'][0][0]:.0f},{n['pts'][0][1]:.0f})"
                  f" to ({n['pts'][-1][0]:.0f},{n['pts'][-1][1]:.0f})")


def pair(a):
    from PIL import Image
    r = built(a.resort)
    t = tempfile.mkdtemp()
    g = os.path.join(HERE, 'grid_crop.py')
    common = ['python3', g, '--image', r.work('map.png'), '--box', a.box, '--zoom', a.zoom, '--grid', '50']
    subprocess.run(common + ['--out', f'{t}/a.png'], check=True, capture_output=True)
    subprocess.run(common + ['--out', f'{t}/b.png', '--pieces', r.work('pieces_cut.json'), '--names', r.work('names.json')],
                   check=True, capture_output=True)
    x, y = Image.open(f'{t}/a.png'), Image.open(f'{t}/b.png')
    im = Image.new('RGB', (x.width + y.width + 10, max(x.height, y.height)), 'white')
    im.paste(x, (0, 0))
    im.paste(y, (x.width + 10, 0))
    im.save(a.out)
    print(a.out, im.size)


def seq(a):
    import pymupdf
    r = built(a.resort)
    pdf = a.pdf
    if not pdf:
        found = sorted(set(glob.glob(os.path.join(r.work_dir, '*.pdf')) + glob.glob(os.path.join(pr.work_root(r.id), '*.pdf'))))
        if len(found) != 1:
            raise SystemExit(f'which PDF? pass --pdf (found: {", ".join(found) or "none"})')
        pdf = found[0]
    page = pymupdf.open(pdf)[a.page]
    x0, y0 = r.R.CLIP[0], r.R.CLIP[1]
    to_pt = lambda q: (x0 + q[0] / r.R.SCALE, y0 + q[1] / r.R.SCALE)  # noqa: E731
    strokes = []
    for d in page.get_drawings():
        if d['type'] not in ('s', 'fs') or not d.get('color'):
            continue
        pts = []
        for it in d['items']:
            if it[0] == 'l':
                pts += [(it[1].x, it[1].y), (it[2].x, it[2].y)]
            elif it[0] == 'c':
                p0, p1, p2, p3 = it[1:5]
                pts += [((1 - t) ** 3 * p0.x + 3 * (1 - t) ** 2 * t * p1.x + 3 * (1 - t) * t * t * p2.x + t ** 3 * p3.x,
                         (1 - t) ** 3 * p0.y + 3 * (1 - t) ** 2 * t * p1.y + 3 * (1 - t) * t * t * p2.y + t ** 3 * p3.y)
                        for t in [k / 8 for k in range(9)]]
        if pts:
            strokes.append((d['seqno'], tuple(round(v, 2) for v in d['color']), round(d.get('width') or 0, 2),
                            d.get('dashes') not in (None, '[] 0'), pts))
    ends = {p['id']: (to_pt(r.pts_of(p)[0]), to_pt(r.pts_of(p)[-1])) for p in r.P}

    def stroke_of(pid):  # the strokes passing through both ends of the piece
        e0, e1 = ends[pid]
        return [s for s in strokes if min(math.dist(e0, q) for q in s[4]) < 0.6 and min(math.dist(e1, q) for q in s[4]) < 0.6]

    by_seq = {}
    for pid in ends:
        for s in stroke_of(pid):
            by_seq.setdefault(s[0], []).append(pid)
    order = sorted(s[0] for s in strokes)
    for pid in map(int, a.ids.split(',')):
        own = stroke_of(pid)
        print(f'{pid} {name_of(r, pid)}: strokes {[(s[0], s[1], s[2], "dashed" if s[3] else "solid") for s in own[:3]]}')
        for s in own[:1]:
            i = order.index(s[0])
            for q in order[max(0, i - a.k): i + a.k + 1]:
                near = by_seq.get(q, [])
                print(f'    {"->" if q == s[0] else "  "} seqno {q}: {", ".join(f"{p} {name_of(r, p)}" for p in near) or "(no piece)"}')


def at(a):
    r = built(a.resort)
    P = {p['id']: p for p in r.P}
    for arg in a.points:
        pid, _, f = arg.partition(':')
        q = r.pts_of(P[int(pid)])
        cum = [0.0]
        for u, v in zip(q, q[1:]):
            cum.append(cum[-1] + math.dist(u, v))
        t = float(f or 0.5) * cum[-1]
        k = next((i for i in range(1, len(cum)) if cum[i] >= t), len(cum) - 1)
        u, v = q[k - 1], q[k]
        w = (t - cum[k - 1]) / ((cum[k] - cum[k - 1]) or 1)
        print(arg, (round(u[0] + w * (v[0] - u[0])), round(u[1] + w * (v[1] - u[1]))), name_of(r, int(pid)))


def draw(a):
    from PIL import Image, ImageDraw
    r = built(a.resort)
    x0, y0, x1, y1 = map(int, a.box.split(','))
    z = float(a.zoom)
    im = Image.open(r.work('map.png')).convert('RGB').crop((x0, y0, x1, y1))
    im = im.resize((int((x1 - x0) * z), int((y1 - y0) * z)))
    d = ImageDraw.Draw(im)
    cols = [(255, 0, 255), (0, 200, 255), (255, 140, 0), (0, 220, 0), (255, 0, 0), (120, 0, 255)]
    P = {p['id']: p for p in r.P}
    for k, pid in enumerate(a.ids):
        c = cols[k % len(cols)]
        q = [((x - x0) * z, (y - y0) * z) for x, y in r.pts_of(P[int(pid)])]
        d.line(q, fill=c, width=5)
        d.text(q[len(q) // 2], pid, fill=c)
        d.ellipse([q[0][0] - 6, q[0][1] - 6, q[0][0] + 6, q[0][1] + 6], outline=c, width=3)
    im.save(a.out)
    print(a.out, im.size)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    sub = ap.add_subparsers(dest='cmd', required=True)
    i = sub.add_parser('info')
    i.add_argument('resort', help='<id> or <id>/<panel>')
    i.add_argument('box', help='x0,y0,x1,y1 (map px)')
    p = sub.add_parser('pair')
    p.add_argument('resort')
    p.add_argument('box')
    p.add_argument('zoom')
    p.add_argument('out')
    s = sub.add_parser('seq')
    s.add_argument('resort')
    s.add_argument('ids', help='piece ids, comma-separated')
    s.add_argument('--k', type=int, default=3, help='strokes before and after')
    s.add_argument('--pdf')
    s.add_argument('--page', type=int, default=0)
    t = sub.add_parser('at')
    t.add_argument('resort')
    t.add_argument('points', nargs='+', help='<piece id>[:<fraction along it>]')
    d = sub.add_parser('draw')
    d.add_argument('resort')
    d.add_argument('box')
    d.add_argument('zoom')
    d.add_argument('out')
    d.add_argument('ids', nargs='+')
    a = ap.parse_args()
    {'info': info, 'pair': pair, 'seq': seq, 'at': at, 'draw': draw}[a.cmd](a)


if __name__ == '__main__':
    main()
