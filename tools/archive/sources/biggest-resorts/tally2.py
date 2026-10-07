import pymupdf, sys, collections
def cls(c):
    if c is None: return None
    r,g,b = c[:3]
    if max(r,g,b) < 0.25: return 'black'
    if g > 0.45 and r < 0.3 and b < 0.55 and g > b: return 'green'
    if b > 0.55 and r < 0.35: return 'blue'
    if r > 0.8 and g > 0.8 and b > 0.8: return 'white'
    return None
for f, pn in [a.split(':') for a in sys.argv[1:]]:
    d = pymupdf.open(f); p = d[int(pn)]
    st = collections.Counter(); fl = collections.Counter(); lens = collections.defaultdict(float)
    for g in p.get_drawings():
        c = cls(g.get('color')); w = g.get('width') or 0
        if c in ('green','blue','black') and g.get('color') is not None and w:
            key = (c, tuple(round(v,2) for v in g['color']), round(w,2))
            st[key] += 1
            r = g['rect']; lens[key] += r.width + r.height
        fc = cls(g.get('fill'))
        if fc in ('green','blue','black'):
            fl[(fc, tuple(round(v,2) for v in g['fill']))] += 1
    print('=====', f, 'page', pn)
    for k, n in st.most_common(12): print('  stroke', k, n, 'extent', round(lens[k]))
    for k, n in fl.most_common(6): print('  fill', k, n)
    spans = collections.Counter()
    ex = {}
    for b in p.get_text('dict')['blocks']:
        for l in b.get('lines', []):
            for s in l['spans']:
                k = (s['font'], round(s['size'],1), '#%06x' % s['color'])
                spans[k] += 1; ex.setdefault(k, s['text'])
    for k, n in spans.most_common(10): print('  text', k, n, repr(ex[k][:40]))
