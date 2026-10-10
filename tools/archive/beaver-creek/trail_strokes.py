import sys, collections, pymupdf
page = pymupdf.open(sys.argv[1])[0]
T = {'green': (0.0, 0.65, 0.32), 'blue': (0.0, 0.62, 0.88), 'black': (0.14, 0.12, 0.13)}
st = collections.Counter(); items = collections.Counter(); ex = {}
for i, d in enumerate(page.get_drawings()):
    c = d.get('color')
    if c is None: continue
    c = tuple(round(x, 2) for x in c)
    for k, v in T.items():
        if all(abs(a - b) < 0.03 for a, b in zip(c, v)):
            key = (k, round(d.get('width') or 0, 2), d.get('dashes'), d.get('lineCap'))
            st[key] += 1; items[key] += len(d['items']); ex.setdefault(key, (i, d['rect']))
for k, n in sorted(st.items(), key=lambda x: -x[1]): print(k, n, items[k], ex[k])
