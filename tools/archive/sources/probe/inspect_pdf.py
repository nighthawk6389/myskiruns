"""inspect_pdf.py map.pdf tag [--render 0.5] [--vec PAGE]: summarise a trail-map PDF's images, strokes, fills and text."""
import sys, collections, os
import pymupdf

pdf, tag = sys.argv[1], sys.argv[2]
render = 0.5
vecpages = []
a = sys.argv[3:]
i = 0
while i < len(a):
    if a[i] == '--render': render = float(a[i + 1]); i += 2
    elif a[i] == '--vec': vecpages.append(int(a[i + 1])); i += 2
    else: i += 1
OUT = os.path.dirname(os.path.abspath(__file__))
d = pymupdf.open(pdf)
print(f'{pdf}: {len(d)} pages, metadata {dict((k, v) for k, v in d.metadata.items() if v)}')
def col(c):
    return tuple(round(v, 2) for v in c) if c else None
for pno, p in enumerate(d):
    print(f'\n=== page {pno}: {p.rect.width:.0f} x {p.rect.height:.0f} pt, rotation {p.rotation}')
    ims = p.get_images(full=True)
    ims = sorted(ims, key=lambda im: -im[2] * im[3])
    print(f'  images: {len(ims)}')
    for im in ims[:6]:
        xref, smask, w, h, bpc, cs = im[0], im[1], im[2], im[3], im[4], im[5]
        try:
            rects = p.get_image_rects(xref)
        except Exception as e:
            rects = str(e)
        rs = [f'({r.x0:.0f},{r.y0:.0f},{r.x1:.0f},{r.y1:.0f}) {r.width:.0f}x{r.height:.0f}pt = {w / max(r.width, 1e-6) * 72:.0f} dpi' for r in rects[:3]] if not isinstance(rects, str) else rects
        print(f'   xref {xref} {w}x{h} bpc {bpc} {cs} smask {smask} filter {im[8] if len(im) > 8 else ""} placed {rs}')
    dr = p.get_drawings()
    print(f'  drawings: {len(dr)}')
    st = collections.Counter()
    stl = collections.Counter()
    fi = collections.Counter()
    for x in dr:
        t = x['type']
        nitems = len(x['items'])
        if 's' in t and x.get('color') is not None:
            k = (col(x['color']), round(x.get('width') or 0, 2))
            st[k] += 1
            # path length
            L = 0
            for it in x['items']:
                if it[0] == 'l': L += abs(it[2] - it[1])
                elif it[0] == 'c': L += abs(it[4] - it[1])
            stl[k] += L
        if 'f' in t and x.get('fill') is not None:
            fi[col(x['fill'])] += 1
    print('  strokes (colour, width): count, total length pt')
    for k, n in st.most_common(16):
        print(f'    {k}: {n}  len {stl[k]:.0f}')
    print('  fills (colour): count')
    for k, n in fi.most_common(14):
        print(f'    {k}: {n}')
    td = p.get_text('dict')
    sp = collections.Counter()
    samples = collections.defaultdict(list)
    nchars = 0
    for b in td['blocks']:
        for l in b.get('lines', []):
            for s in l['spans']:
                txt = s['text'].strip()
                if not txt: continue
                nchars += len(txt)
                k = (s['font'], round(s['size'], 1), f"#{s['color']:06x}")
                sp[k] += 1
                if len(samples[k]) < 6: samples[k].append(txt[:30])
    print(f'  text spans: {sum(sp.values())} ({nchars} chars)')
    for k, n in sp.most_common(14):
        print(f'    {k}: {n}  e.g. {samples[k]}')
    pm = p.get_pixmap(matrix=pymupdf.Matrix(render, render))
    fn = f'{OUT}/{tag}_p{pno}.png'
    pm.save(fn)
    print(f'  render -> {fn} ({pm.width}x{pm.height})')
    if pno in vecpages:
        q = pymupdf.open()
        np_ = q.new_page(width=p.rect.width, height=p.rect.height)
        sh = np_.new_shape()
        for x in dr:
            for it in x['items']:
                if it[0] == 'l': sh.draw_line(it[1], it[2])
                elif it[0] == 'c': sh.draw_bezier(it[1], it[2], it[3], it[4])
                elif it[0] == 're': sh.draw_rect(it[1])
                elif it[0] == 'qu': sh.draw_quad(it[1])
            sh.finish(color=x.get('color'), fill=x.get('fill'), width=x.get('width') or 0.5, closePath=x.get('closePath', False), even_odd=x.get('even_odd', False), stroke_opacity=1, fill_opacity=1)
        sh.commit()
        pm = np_.get_pixmap(matrix=pymupdf.Matrix(render, render))
        fn = f'{OUT}/{tag}_vec_p{pno}.png'
        pm.save(fn)
        print(f'  vector layer -> {fn}')
