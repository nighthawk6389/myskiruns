import sys, pymupdf
pg = pymupdf.open(sys.argv[1])[0]
seqs = {int(s) for s in sys.argv[2:]}
for d in pg.get_drawings():
    if d['seqno'] in seqs:
        print(d['seqno'], d['type'], d.get('fill'), d['rect'], d.get('closePath'), d.get('even_odd'))
        for it in d['items']:
            print('   ', it[0], [(round(p.x, 2), round(p.y, 2)) for p in it[1:] if hasattr(p, 'x')] if it[0] in ('l', 'c') else it[1])
