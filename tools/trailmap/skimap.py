"""skimap.org, the archive of past and present trail maps: where a resort's PDF is when its own site hides it behind
a bot check (Whiteface) or no longer has it, and where an older export of the same artwork with live strokes and
text can be found (Wildcat, Heavenly).

    python3 tools/trailmap/skimap.py search "heavenly"        # ski areas: id | name | region | number of maps
    python3 tools/trailmap/skimap.py maps 503 [n]             # an area's newest maps: id and caption (year, type)
    python3 tools/trailmap/skimap.py probe 503 [n] [--out work/skimap]
        # downloads the newest n downhill maps and, for a PDF, summarises each page: size, largest image, number of
        # drawings, text characters, most common stroke classes (a quick look at which route it allows)

A map's file is https://skimap.org/skimaps/view/<map id> (it redirects to files.skimap.org); keep that URL in the
resort's regen.sh. Files downloaded here are data, not code: read them with the repo's tools only.
"""
import argparse
import collections
import html
import os
import re
import subprocess


def get(url, out=None):
    cmd = ['curl', '-sS', '-L', '-m', '120', '-A', 'Mozilla/5.0 (X11; Linux x86_64) Chrome/124.0', url]
    if out:
        cmd[1:1] = ['-o', out, '-w', '%{content_type} %{size_download}']
    return subprocess.run(cmd, capture_output=True, text=True).stdout


def maps(aid, n):
    s = get(f'https://skimap.org/skiareas/view/{aid}')
    t = re.search(r'<title>([^<]*)', s)
    found = []
    for m in re.finditer(r'<figure class="figure" id="ski-map-(\d+)".*?</figure>', s, re.S):
        cap = re.search(r'<figcaption.*?</figcaption>', m.group(0), re.S)
        found.append((m.group(1), ' '.join(html.unescape(re.sub(r'<[^>]+>', ' ', cap.group(0) if cap else '')).split())))
    return (t.group(1) if t else '?'), found[:n] if n else found


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    sub = ap.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('search')
    s.add_argument('query')
    m = sub.add_parser('maps')
    m.add_argument('area')
    m.add_argument('n', nargs='?', type=int, default=8)
    p = sub.add_parser('probe')
    p.add_argument('area')
    p.add_argument('n', nargs='?', type=int, default=2)
    p.add_argument('--out', default='work/skimap')
    a = ap.parse_args()
    if a.cmd == 'search':
        s = get(f'https://skimap.org/search/results?query={a.query.replace(" ", "+")}')
        for r in re.finditer(r'href="/skiareas/view/(\d+)">\s*<div class="fw-bold">([^<]*)</div>\s*<small>\s*([^<]*)'
                             r'</small>.*?(\d+) ski maps?', s, re.S):
            print(r.group(1), '|', html.unescape(r.group(2)).strip(), '|', r.group(3).strip(), '|', r.group(4), 'maps')
    elif a.cmd == 'maps':
        title, found = maps(a.area, a.n)
        print('==', a.area, title)
        for mid, cap in found:
            print(mid, cap[:160])
    else:
        import pymupdf
        os.makedirs(a.out, exist_ok=True)
        title, found = maps(a.area, 0)
        print('==', a.area, title)
        done = 0
        for mid, cap in found:
            if 'downhill' not in cap or 'master plan' in cap:
                continue
            out = os.path.join(a.out, f'{a.area}_{mid}')
            r = get(f'https://skimap.org/skimaps/view/{mid}', out)
            info = ''
            if 'pdf' in r:
                try:
                    d = pymupdf.open(out)
                    for i, pg in enumerate(d):
                        dr = pg.get_drawings()
                        st = collections.Counter((tuple(round(v, 2) for v in x['color']), round(x.get('width') or 0, 2))
                                                 for x in dr if x['type'] == 's' and x.get('color'))
                        ims = sorted(pg.get_images(), key=lambda im: -im[2] * im[3])[:1]
                        info += (f'\n     p{i} {round(pg.rect.width)}x{round(pg.rect.height)} pt, image '
                                 f'{[(im[2], im[3]) for im in ims]}, {len(dr)} drawings, {len(pg.get_text())} text chars,'
                                 f' strokes {st.most_common(4)}')
                except Exception as e:  # not a PDF after all, or damaged
                    info = f' ({e})'
            print(' ', mid, cap[:90], '|', r, '->', out, info)
            done += 1
            if done >= a.n:
                break


if __name__ == '__main__':
    main()
