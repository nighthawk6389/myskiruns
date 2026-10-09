"""A resort's interactive map on resorts-interactive.com ("vicomap": Deer Valley's, and other Alterra resorts'), as a
source of truth for naming line pieces: its SVG draws the printed map's vector layer with each trail's line (and its
name's outlined letters) in a group named after the trail, `<g id="<rating>Trail-<Name>">`, over the map's painting.

    python3 tools/trailmap/vicomap.py fetch 1815 --out work/deer-valley/vicomap      # api.json, map.svg
    python3 tools/trailmap/vicomap.py parse work/deer-valley/vicomap                 # trails.json, background.png
    python3 tools/trailmap/register_pages.py --ref work/deer-valley/vicomap/background.png --ref-scale 2.77778 \\
        --image work/deer-valley/map.png                                            # the SVG's units on the map
    python3 tools/trailmap/vicomap.py fit deer-valley                                # the affine, refined on the pieces
    python3 tools/trailmap/vicomap.py check deer-valley [--only 12,40] [--all]      # pieces against its trails
    python3 tools/trailmap/vicomap.py show deer-valley Sunrise --out work/sunrise.png  # a trail's lines on the map

fetch: the map's JSON (`/api/maps/<id>`: every trail's and lift's name and status, no ratings) and its SVG
(`/map/<id>/svg`) from vicomap-cdn.resorts-interactive.com (plain curl works). The map id is in the resort's
interactive-map page (`find_source.cjs links <page> vicomap`).

parse: per named group, the trail's name (Illustrator's id escapes undone: _x28_ "(", _x29_ ")", _x27_ "'", _
space), its rating (the id's prefix: novice, intermediate, advanced, expert) and its line: the group's first path, a
stroke in the rating's colour, flattened to polylines in the SVG's units; lifts the same. The embedded painting is
written as background.png with its placement (the `<use>` transform: SVG units per background px).

fit: the registration refined on the line pieces (work/<id>/pieces.json): the interactive map's lines are the printed
map's strokes drawn again, so ICP from the painting's affine pairs every line point with a piece point (median 0.27
px at Deer Valley); keep the result in resort.py.

check: the trails' lines put on the map image by the resort's resort.py `VICOMAP_AFFINE` (x = a u + b v + c,
y = d u + e v + f, SVG units to map px, from register_pages.py --ref), and per line piece of pdf_resort.py's last
build (work/<id>/pieces_cut.json, names.json) the share of it each vicomap trail covers (within --tol px). Prints the
pieces whose name (or undecided `?`) differs from the trail covering most of them. Names match on letters alone, with
the interactive map's "(Upper)", "(Lower)" and the like left out (one printed run may be two vicomap trails). The
interactive map is the resort's own naming, but it is a second drawing of the map: settle every difference on a crop
of the printed map, and record it in decisions.py. `--along` lists, for each piece shown, the trails covering it stretch
by stretch (where one stroke carries two runs: the point to cut it at).
"""
import argparse
import base64
import collections
import html
import json
import math
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

HOST = 'https://vicomap-cdn.resorts-interactive.com'
NUM = re.compile(r'[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?')
RATINGS = {'noviceTrail': 'green', 'intermediateTrail': 'blue', 'advancedTrail': 'black',
           'expertTrail': 'double-black', 'lift': 'lift',
           # Steamboat's: advanced intermediate (a blue square with a black diamond), and its snowshoe trails
           'advancedIntermediateTrail': 'advanced-intermediate', 'IntermediateTrail': 'blue', 'nordicTrail': 'nordic'}


def fetch(a):
    os.makedirs(a.out, exist_ok=True)
    for url, name in ((f'{HOST}/api/maps/{a.id}', 'api.json'), (f'{HOST}/map/{a.id}/svg', 'map.svg')):
        subprocess.run(['curl', '-sSf', '-m', '180', '-o', os.path.join(a.out, name), url], check=True)
        print(f'{url} -> {os.path.join(a.out, name)}')


def unescape(s):
    s = re.sub(r'_x([0-9A-Fa-f]{2})_', lambda m: chr(int(m.group(1), 16)), s)
    return ' '.join(s.replace('_', ' ').split())


def bez(p0, p1, p2, p3, n=8):
    return [tuple((1 - t) ** 3 * p0[k] + 3 * (1 - t) ** 2 * t * p1[k] + 3 * (1 - t) * t * t * p2[k] + t ** 3 * p3[k]
                  for k in (0, 1)) for t in (i / n for i in range(1, n + 1))]


def path_lines(d):
    """An SVG path's subpaths as polylines (curves flattened)."""
    toks = re.findall(r'[MmLlHhVvCcSsQqTtZz]|' + NUM.pattern, d)
    out, cur, i, cmd = [], [], 0, None
    pos, start, last_ctrl = (0.0, 0.0), (0.0, 0.0), None

    def nums(k):
        nonlocal i
        v = [float(x) for x in toks[i:i + k]]
        i += k
        return v
    while i < len(toks):
        if re.fullmatch(r'[A-Za-z]', toks[i]):
            cmd = toks[i]
            i += 1
            if cmd in 'Zz':
                if cur:
                    cur.append(start)
                    out.append(cur)
                cur, pos = [], start
                continue
        rel = cmd.islower()
        C = cmd.upper()
        ox, oy = pos if rel else (0.0, 0.0)
        if C == 'M':
            x, y = nums(2)
            pos = start = (ox + x, oy + y)
            if len(cur) > 1:
                out.append(cur)
            cur = [pos]
            cmd = 'l' if rel else 'L'  # further pairs are lines
            last_ctrl = None
        elif C == 'L':
            x, y = nums(2)
            pos = (ox + x, oy + y)
            cur.append(pos)
            last_ctrl = None
        elif C == 'H':
            (x,) = nums(1)
            pos = (ox + x, pos[1])
            cur.append(pos)
            last_ctrl = None
        elif C == 'V':
            (y,) = nums(1)
            pos = (pos[0], oy + y)
            cur.append(pos)
            last_ctrl = None
        elif C in 'CS':
            if C == 'C':
                x1, y1, x2, y2, x, y = nums(6)
                c1 = (ox + x1, oy + y1)
            else:
                x2, y2, x, y = nums(4)
                c1 = (2 * pos[0] - last_ctrl[0], 2 * pos[1] - last_ctrl[1]) if last_ctrl else pos
            c2, end = (ox + x2, oy + y2), (ox + x, oy + y)
            cur += bez(pos, c1, c2, end)
            pos, last_ctrl = end, c2
        elif C in 'QT':
            if C == 'Q':
                x1, y1, x, y = nums(4)
                q = (ox + x1, oy + y1)
            else:
                x, y = nums(2)
                q = (2 * pos[0] - last_ctrl[0], 2 * pos[1] - last_ctrl[1]) if last_ctrl else pos
            end = (ox + x, oy + y)
            c1 = (pos[0] + 2 / 3 * (q[0] - pos[0]), pos[1] + 2 / 3 * (q[1] - pos[1]))
            c2 = (end[0] + 2 / 3 * (q[0] - end[0]), end[1] + 2 / 3 * (q[1] - end[1]))
            cur += bez(pos, c1, c2, end)
            pos, last_ctrl = end, q
        else:
            raise ValueError(f'path command {cmd} not handled')
    if len(cur) > 1:
        out.append(cur)
    return out


def style_of(el):
    return dict(kv.split(':', 1) for kv in el.get('style', '').split(';') if ':' in kv)


def line_style(st):
    return {'stroke': st.get('stroke', '').lower(), 'width': float(re.sub(r'px$', '', st.get('stroke-width', '1')) or 1),
            'dashed': st.get('stroke-dasharray', 'none') != 'none'}


def fill_box(st, pls, d=''):
    """A fill's colour, box, number of outlines and drawing commands (a symbol's are few: four sides, or curves),
    and a polygon's corners when it has few (a square or diamond against a turned letter I)."""
    pts = [q for pl in pls for q in pl]
    if not pts:
        return None
    xs, ys = [q[0] for q in pts], [q[1] for q in pts]
    out = {'fill': st['fill'].lower(), 'box': [round(min(xs), 2), round(min(ys), 2), round(max(xs), 2),
                                               round(max(ys), 2)], 'parts': len(pls),
           'cmds': ''.join(re.findall(r'[A-DF-Za-df-z]', d))[:60]}
    if len(pls) == 1 and len(pts) <= 12:  # a polygon of a few corners (a symbol, or a letter like I): its corners
        out['poly'] = [[round(x, 2), round(y, 2)] for x, y in pts]
    return out


def parse(a):
    import xml.etree.ElementTree as ET
    ns = '{http://www.w3.org/2000/svg}'
    root = ET.parse(os.path.join(a.dir, 'map.svg')).getroot()
    vb = [float(v) for v in root.get('viewBox').split()]
    trails, lifts = [], []
    for g in root.iter(ns + 'g'):
        gid = g.get('id', '')
        kind, _, raw = gid.partition('-')
        if kind not in RATINGS:
            continue
        name = unescape(re.sub(r'(?<=[a-z)])\d+$', '', re.sub(r'_\d+_?$', '', raw)))
        lines, glyphs, stroke = [], [], None
        styles, fills = [], []  # each line's stroke style; every fill's box and colour (letters, symbols, halos)
        for el in g.iter(ns + 'path'):
            st = style_of(el)
            pls = path_lines(el.get('d', ''))
            if st.get('fill') == 'none' and st.get('stroke', '#fff').lower() not in ('#fff', '#ffffff'):
                stroke = stroke or st['stroke']
                lines += pls
                styles += [line_style(st)] * len(pls)
            elif st.get('fill', 'none') != 'none':
                glyphs += [q for pl in pls for q in pl]
                fills.append(fill_box(st, pls, el.get('d', '')))
        label = None
        if glyphs:
            xs, ys = [q[0] for q in glyphs], [q[1] for q in glyphs]
            label = [round(min(xs), 1), round(min(ys), 1), round(max(xs), 1), round(max(ys), 1)]
        entry = {'name': name, 'rating': RATINGS[kind], 'id': gid, 'stroke': stroke, 'label': label,
                 'lines': [[[round(x, 2), round(y, 2)] for x, y in pl] for pl in lines]}
        if getattr(a, 'detail', False):
            entry.update({'styles': styles, 'fills': [f for f in fills if f]})
        (lifts if kind == 'lift' else trails).append(entry)
    # --detail: the stroked paths outside the named groups, each with its id's rating and name (a trailing _ or number
    # left out: Steamboat's Half_Hitch_ is the blue line under the group Half_Hitch's dashed one; an empty name or a
    # bare number is a line the interactive map names nowhere)
    loose = []
    for el in root.iter(ns + 'path') if getattr(a, 'detail', False) else ():
        gid = el.get('id', '')
        kind, _, raw = gid.partition('-')
        st = style_of(el)
        if kind not in RATINGS or st.get('fill') != 'none' or st.get('stroke', '#fff').lower() in ('#fff', '#ffffff'):
            continue
        name = '' if re.fullmatch(r'\d*', raw) else unescape(re.sub(r'_?\d*_?$', '', raw))
        pls = path_lines(el.get('d', ''))
        loose.append({'name': name, 'rating': RATINGS[kind], 'id': gid, 'style': line_style(st),
                      'lines': [[[round(x, 2), round(y, 2)] for x, y in pl] for pl in pls]})
    # the painting: <use xlink:href="#_ImageN" ... transform="matrix(s,0,0,s,tx,ty)"/> and <image id="_ImageN" ...>
    svg = open(os.path.join(a.dir, 'map.svg')).read()
    # (id="map", or another id with serif:id="map" as Steamboat's; an x, y offset folded into the translation)
    use = next((u for u in re.findall(r'<use [^>]*>', svg) if re.search(r'(?<![\w:])id="map"|serif:id="map"', u)), None)
    bg = None
    if use and 'transform="matrix(' in use:
        href = re.search(r'xlink:href="#([^"]+)"', use).group(1)
        img = re.search(r'<image id="' + re.escape(href) + r'"[^>]*xlink:href="data:image/(\w+);base64,([^"]+)"', svg)
        m = [float(v) for v in re.search(r'transform="matrix\(([^)]+)\)"', use).group(1).split(',')]
        ox, oy = (float((re.search(k + r'="([-\d.]+)"', use) or [0, 0])[1]) for k in (r'\bx', r'\by'))
        m[4], m[5] = m[0] * ox + m[2] * oy + m[4], m[1] * ox + m[3] * oy + m[5]
        bg = {'file': f'background.{img.group(1)}', 'matrix': m}
        open(os.path.join(a.dir, bg['file']), 'wb').write(base64.b64decode(img.group(2)))
    api = os.path.join(a.dir, 'api.json')
    listed = [html.unescape(t['name']) for t in json.load(open(api))['trails']] if os.path.exists(api) else None
    out = {'_source': f'{a.dir}/map.svg (vicomap.py parse)', 'viewBox': vb, 'background': bg, 'trails': trails,
           'lifts': lifts, 'api_trails': listed}
    if getattr(a, 'detail', False):
        out['loose'] = loose
    json.dump(out, open(os.path.join(a.dir, 'trails.json'), 'w'), indent=0)
    print(f'{len(trails)} trail groups ({sum(1 for t in trails if t["lines"])} with a line), {len(lifts)} lifts; '
          f'background {bg}; the API lists {len(listed) if listed is not None else "-"} trails')
    if listed is not None:
        named = {t['name'] for t in trails}
        print('  in the API, no group in the SVG:', sorted(set(listed) - named))
        print('  a group in the SVG, not in the API:', sorted(named - set(listed)))
        print('  a group with no line:', sorted(t['name'] for t in trails if not t['lines']))


def base(name):
    """A name without the interactive map's (Upper), (Lower), ... and without case and punctuation."""
    t = re.sub(r'\s*\((?:upper|lower|mid|middle|full|top|bottom)\)', '', name, flags=re.I)
    t = t.upper().replace('’', "'")
    t = re.sub(r'^(?:UPPER|LOWER|MIDDLE|THE)\s+', '', t)
    return re.sub(r'[^A-Z0-9]', '', t)


def dense_pts(pts, step):
    out = []
    for u, v in zip(pts, pts[1:]):
        n = max(1, int(math.dist(u, v) / step))
        out += [(u[0] + (v[0] - u[0]) * k / n, u[1] + (v[1] - u[1]) * k / n) for k in range(n)]
    return out + [tuple(pts[-1])]


def fit(a):
    """Refine the resort's VICOMAP_AFFINE on the line pieces themselves: the interactive map's trail lines are the
    printed map's strokes drawn again, so each of their points has a piece point under it (ICP: pair each with the
    nearest piece point within --tol px, solve the affine by least squares, repeat)."""
    import numpy as np
    from scipy.spatial import cKDTree
    import pdf_resort as pr
    R = pr.Resort(a.resort)
    V = json.load(open(a.trails or os.path.join(pr.work_root(R.id), 'vicomap', 'trails.json')))
    src = np.array([q for t in V['trails'] for pl in t['lines'] if len(pl) > 1 for q in dense_pts(pl, 4.0)])
    dst = np.array([q for p in R.load('pieces.json')['polylines'] for q in dense_pts(R.pts_of(p), 1.0)])
    tree = cKDTree(dst)
    M = np.array(R.R.VICOMAP_AFFINE, float).reshape(2, 3)
    for it in range(12):
        proj = src @ M[:, :2].T + M[:, 2]
        d, j = tree.query(proj)
        ok = d < a.tol
        X = np.hstack([src[ok], np.ones((ok.sum(), 1))])
        M = np.linalg.lstsq(X, dst[j[ok]], rcond=None)[0].T
        print(f'  pass {it + 1}: {ok.sum()} of {len(src)} points paired, median {np.median(d[ok]):.3f} px, '
              f'90th percentile {np.percentile(d[ok], 90):.3f} px')
    (a_, b_, c_), (d_, e_, f_) = M
    print(f'VICOMAP_AFFINE = ({a_:.7f}, {b_:.7f}, {c_:.4f}, {d_:.7f}, {e_:.7f}, {f_:.4f})')


def fit_ink(a):
    """Register the interactive map's lines on a map image with no line pieces of its own (Steamboat, whose SVG is
    the vector source): ICP of the solid lines of the --stroke colours onto the image's pixels of the --ink colour
    (within --ink-dist of it, RGB). Each line point goes to the centroid of the ink pixels within the radius of where
    the affine puts it, the affine is solved by least squares (pairs off by more than twice the median left out),
    and the radius shrinks pass by pass (--radius)."""
    import numpy as np
    from PIL import Image
    from scipy.spatial import cKDTree
    V = json.load(open(os.path.join(a.dir, 'trails.json')))
    want = {c.strip().lower() for c in a.stroke.split(',')}
    src = []
    for t in V['trails']:
        for pl, st in zip(t['lines'], t.get('styles') or [{'stroke': (t['stroke'] or '').lower()}] * len(t['lines'])):
            if st.get('stroke') in want and not st.get('dashed') and len(pl) > 1:
                src += dense_pts(pl, 3.0)
    for t in V.get('loose', []):
        if t['style']['stroke'] in want and not t['style']['dashed']:
            src += [q for pl in t['lines'] if len(pl) > 1 for q in dense_pts(pl, 3.0)]
    src = np.array(src)
    img = np.asarray(Image.open(a.image).convert('RGB')).astype(float)
    ink = np.array([float(v) for v in a.ink.split(',')])
    ys, xs = np.nonzero(np.linalg.norm(img - ink, axis=2) < a.ink_dist)
    pix = np.column_stack([xs, ys]).astype(float)
    tree = cKDTree(pix)
    M = np.array([float(v) for v in a.affine.split(',')]).reshape(2, 3)
    print(f'{len(src)} line points, {len(pix)} ink pixels')
    for r in [float(v) for v in a.radius.split(',')]:
        for _ in range(4):
            proj = src @ M[:, :2].T + M[:, 2]
            hits = tree.query_ball_point(proj, r)
            ok = np.array([len(h) >= 3 for h in hits])
            tgt = np.array([pix[h].mean(axis=0) if len(h) >= 3 else (0, 0) for h in hits])
            d = np.linalg.norm(tgt - proj, axis=1)
            keep = ok & (d <= 2 * np.median(d[ok]) + 0.25)
            X = np.hstack([src[keep], np.ones((keep.sum(), 1))])
            M = np.linalg.lstsq(X, tgt[keep], rcond=None)[0].T
        proj = src @ M[:, :2].T + M[:, 2]
        d, _j = tree.query(proj)
        print(f'  radius {r:g}: {keep.sum()} of {len(src)} points paired; nearest ink pixel median {np.median(d):.2f} px, '
              f'90th percentile {np.percentile(d, 90):.2f} px')
    (a_, b_, c_), (d_, e_, f_) = M
    print(f'VICOMAP_AFFINE = ({a_:.7f}, {b_:.7f}, {c_:.4f}, {d_:.7f}, {e_:.7f}, {f_:.4f})')


def check(a):
    import numpy as np
    from scipy.spatial import cKDTree
    import pdf_resort as pr
    R = pr.Resort(a.resort)
    A = R.R.VICOMAP_AFFINE
    V = json.load(open(a.trails or os.path.join(pr.work_root(R.id), 'vicomap', 'trails.json')))

    def tf(p):
        return (A[0] * p[0] + A[1] * p[1] + A[2], A[3] * p[0] + A[4] * p[1] + A[5])
    vn, vp = [], []
    for t in V['trails']:
        for pl in t['lines']:
            if len(pl) > 1:
                q = dense_pts([tf(p) for p in pl], 1.0)
                vp += q
                vn += [t['name']] * len(q)
    tree = cKDTree(np.array(vp))
    pieces = R.load('pieces_cut.json')['polylines']
    names = R.load('names.json')
    only = {int(v) for v in a.only.split(',')} if a.only else None
    shown = 0
    for p in pieces:
        pid = p['id']
        if only and pid not in only:
            continue
        dense = dense_pts(R.pts_of(p), 2.0)
        cover = collections.Counter()
        for hits in tree.query_ball_point(np.array(dense), a.tol):
            for nm in {vn[k] for k in hits}:
                cover[nm] += 1
        best = [(nm, n / len(dense)) for nm, n in cover.most_common(3)]
        mine = names.get(str(pid), '?')
        if mine.endswith('~'):
            continue  # a stretch along a name: the interactive map draws no line through names
        top = best[0] if best else ('', 0)
        agree = mine not in ('?', '-') and top[1] >= a.share and base(top[0]) == base(mine)
        quiet = mine == '-' and top[1] < a.share
        if only or a.all or not (agree or quiet):
            shown += 1
            print(f'{pid:4d} {mine:28s} vicomap: ' + (', '.join(f'{n} {s:.0%}' for n, s in best) or '-') +
                  f'  ({round(p["lengthPx"])} px)')
            if a.along:  # the trails covering it, stretch by stretch from its first point (where a line changes run)
                runs = []
                for q, hits in zip(dense, tree.query_ball_point(np.array(dense), a.tol)):
                    here = '/'.join(sorted({vn[k] for k in hits})) or '-'
                    if runs and runs[-1][0] == here:
                        runs[-1][2] = q
                    else:
                        runs.append([here, q, q])
                for here, q0, q1 in runs:
                    print(f'       {here}: {round(q0[0])},{round(q0[1])} to {round(q1[0])},{round(q1[1])}')
    print(f'{shown} pieces shown')


def show(a):
    """The interactive map's lines of the trails named (any part: Sunrise draws Sunrise; 'Lily' draws Lily (Upper) and
    Lily (Lower)) over the map image, each in its own colour, with the line pieces in thin grey: a crop of their
    extent (or --box), written to --out."""
    from PIL import Image, ImageDraw
    import pdf_resort as pr
    R = pr.Resort(a.resort)
    A = R.R.VICOMAP_AFFINE
    V = json.load(open(a.trails or os.path.join(pr.work_root(R.id), 'vicomap', 'trails.json')))
    img = Image.open(R.work('map.png')).convert('RGB')
    want = [t for t in V['trails'] if any(base(t['name']) == base(n) for n in a.names)]
    lines = [(t['name'], [(A[0] * p[0] + A[1] * p[1] + A[2], A[3] * p[0] + A[4] * p[1] + A[5]) for p in pl])
             for t in want for pl in t['lines'] if len(pl) > 1]
    if a.box:
        box = [int(v) for v in a.box.split(',')]
    else:
        xs = [q[0] for _n, pl in lines for q in pl]
        ys = [q[1] for _n, pl in lines for q in pl]
        box = [int(min(xs)) - 80, int(min(ys)) - 80, int(max(xs)) + 80, int(max(ys)) + 80]
    crop = img.crop(box)
    z = a.zoom
    crop = crop.resize((int(crop.width * z), int(crop.height * z)))
    d = ImageDraw.Draw(crop)
    for p in R.load('pieces_cut.json')['polylines']:
        d.line([((x - box[0]) * z, (y - box[1]) * z) for x, y in R.pts_of(p)], fill=(120, 120, 120), width=1)
    cols = [(255, 0, 255), (255, 120, 0), (0, 160, 0), (0, 0, 255), (200, 0, 0)]
    for k, nm in enumerate(sorted({n for n, _pl in lines})):
        for n, pl in lines:
            if n == nm:
                d.line([((x - box[0]) * z, (y - box[1]) * z) for x, y in pl], fill=cols[k % len(cols)], width=3)
        d.text((4, 4 + 14 * k), nm, fill=cols[k % len(cols)])
    crop.save(a.out)
    print(a.out, crop.size, 'box', box)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    sub = ap.add_subparsers(dest='cmd', required=True)
    f = sub.add_parser('fetch')
    f.add_argument('id')
    f.add_argument('--out', required=True)
    p = sub.add_parser('parse')
    p.add_argument('dir')
    p.add_argument('--detail', action='store_true',
                   help="also each line's style, each group's fills (letters, symbols, halos) and the stroked paths "
                        'outside the named groups (loose): for an interactive map read as the vector source')
    fi = sub.add_parser('fit-ink')
    fi.add_argument('dir')
    fi.add_argument('--image', required=True)
    fi.add_argument('--affine', required=True, help='a,b,c,d,e,f to start from (register_pages.py --ref)')
    fi.add_argument('--stroke', default='#2052a4', help="the lines' stroke colours to fit, comma-separated")
    fi.add_argument('--ink', required=True, help='R,G,B of those lines on the image')
    fi.add_argument('--ink-dist', type=float, default=45)
    fi.add_argument('--radius', default='8,5,3,2', help='px, pass by pass')
    f2 = sub.add_parser('fit')
    f2.add_argument('resort')
    f2.add_argument('--trails', help='default work/<id>/vicomap/trails.json')
    f2.add_argument('--tol', type=float, default=3.0, help='px: a pair farther apart is left out')
    c = sub.add_parser('check')
    c.add_argument('resort')
    c.add_argument('--trails', help='default work/<id>/vicomap/trails.json')
    c.add_argument('--tol', type=float, default=4.0, help='px from a vicomap line that counts as on it')
    c.add_argument('--share', type=float, default=0.6, help='the share of a piece a trail must cover to name it')
    c.add_argument('--only', help='piece ids (comma-separated): print these, whatever they agree on')
    c.add_argument('--all', action='store_true', help='print every piece')
    c.add_argument('--along', action='store_true', help='each piece shown: the trails covering it, stretch by stretch')
    sh = sub.add_parser('show')
    sh.add_argument('resort')
    sh.add_argument('names', nargs='+')
    sh.add_argument('--out', required=True)
    sh.add_argument('--box', help="x0,y0,x1,y1 of the map image (default: the lines' extent)")
    sh.add_argument('--zoom', type=float, default=1.0)
    sh.add_argument('--trails', help='default work/<id>/vicomap/trails.json')
    a = ap.parse_args()
    {'fetch': fetch, 'parse': parse, 'fit': fit, 'fit-ink': fit_ink, 'check': check, 'show': show}[a.cmd](a)


if __name__ == '__main__':
    main()
