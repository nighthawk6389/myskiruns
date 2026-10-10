import sys, collections, fitz
doc = fitz.open(sys.argv[1]); page = doc[0]
st = collections.Counter(); ln = collections.Counter(); fl = collections.Counter()
for d in page.get_drawings():
    c = d.get('color'); f = d.get('fill'); w = d.get('width')
    if c is not None and d['type'] in ('s', 'fs'):
        k = (tuple(round(x, 2) for x in c), round(w or 0, 2), bool(d.get('dashes') and d['dashes'] not in ('[] 0', '[] 0.0')))
        st[k] += 1
        r = d['rect']; ln[k] += r.width + r.height
    if f is not None and d['type'] in ('f', 'fs'):
        fl[tuple(round(x, 2) for x in f)] += 1
sat = lambda c: max(c) - min(c)
print('strokes not grey-brown painting (sat>0.15 or dark<0.25 or dashed):')
for k, n in st.most_common():
    c, w, dsh = k
    if (sat(c) > 0.15 or max(c) < 0.25 or dsh or c == (1.0, 1.0, 1.0)) and n >= 3:
        print(k, n, int(ln[k]))
