import pymupdf, sys, collections
for f in sys.argv[1:]:
    d = pymupdf.open(f)
    print('=====', f, 'pages', len(d), 'meta', {k: v for k, v in d.metadata.items() if v and k in ('creator','producer','title','creationDate')})
    for pn, p in enumerate(d):
        if pn > 1: break
        r = p.rect
        imgs = p.get_images(full=True)
        bigimg = sorted([(d.extract_image(x[0])['width'], d.extract_image(x[0])['height']) for x in imgs], reverse=True)[:3] if imgs else []
        words = p.get_text('words')
        dr = p.get_drawings()
        strokes = collections.Counter()
        fills = collections.Counter()
        for g in dr:
            if g.get('color') is not None and g.get('width'):
                c = tuple(round(v, 2) for v in g['color'])
                strokes[(c, round(g['width'], 2))] += 1
            if g.get('fill') is not None:
                fills[tuple(round(v, 2) for v in g['fill'])] += 1
        print(f'  page {pn}: {r.width:.0f}x{r.height:.0f} pt, images {len(imgs)} biggest {bigimg}, words {len(words)}, drawings {len(dr)}')
        print('   sample words:', ' '.join(w[4] for w in words[:40])[:300])
        print('   top strokes (rgb, width): count', strokes.most_common(14))
        print('   top fills:', fills.most_common(8))
