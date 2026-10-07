"""skprobe.py AREA_ID [n]: the newest downhill maps of a skimap.org area: year, file type and, for a PDF, its vector content."""
import re, html, sys, subprocess, collections, os
aid = sys.argv[1]; n = int(sys.argv[2]) if len(sys.argv) > 2 else 2
D = os.path.dirname(os.path.abspath(__file__)) + '/skprobe'
os.makedirs(D, exist_ok=True)
s = subprocess.run(['curl', '-sS', '-L', '-m', '60', f'https://skimap.org/skiareas/view/{aid}'], capture_output=True, text=True).stdout
t = re.search(r'<title>([^<]*)', s); print('==', aid, t.group(1) if t else '?')
done = 0
for m in re.finditer(r'<figure class="figure" id="ski-map-(\d+)".*?</figure>', s, re.S):
    f = m.group(0)
    cap = ' '.join(html.unescape(re.sub(r'<[^>]+>', ' ', re.search(r'<figcaption.*?</figcaption>', f, re.S).group(0))).split())
    if 'downhill' not in cap or 'master plan' in cap:
        continue
    mid = m.group(1)
    out = f'{D}/{aid}_{mid}'
    r = subprocess.run(['curl', '-sS', '-L', '-m', '120', '-o', out, '-w', '%{content_type} %{size_download}', f'https://skimap.org/skimaps/view/{mid}'], capture_output=True, text=True).stdout
    info = ''
    if 'pdf' in r:
        import pymupdf
        try:
            d = pymupdf.open(out)
            for i, p in enumerate(d):
                dr = p.get_drawings()
                st = collections.Counter((tuple(round(v, 2) for v in x['color']), round(x.get('width') or 0, 2)) for x in dr if x['type'] == 's' and x.get('color'))
                ims = sorted(p.get_images(), key=lambda im: -im[2] * im[3])[:1]
                info += f'\n     p{i} {round(p.rect.width)}x{round(p.rect.height)} img {[(im[2], im[3]) for im in ims]} drawings {len(dr)} text {len(p.get_text())} strokes {st.most_common(4)}'
        except Exception as e:
            info = str(e)
    print(' ', mid, cap[:90], '|', r, info)
    done += 1
    if done >= n:
        break
