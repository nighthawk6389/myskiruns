"""Jay Peak's trail labels straight from the PDF text + the difficulty symbol printed beside each.

    python3 tools/trailmap/resorts/jay-peak/labels.py work/jay-peak/jay.pdf work/jay-peak/jay_label_spans.json

Reads the 2025-26 map PDF; writes one record per trail-name text span (mapName, printed spelling, symbol, park,
labelSrc and symSrc in source px of the 4x map image) for reading.py. The map draws no trail lines, but every
name is real text (DIN2014-Bold, 5.2-6.1 pt, black with a white halo, or white on a park's orange pill) with
its symbol drawn just before it (or after it): a green circle (four curves), a blue square, a black diamond
(this map has no double diamonds). Left out: the legend, the stats panel, the Side View inset and the logos
(EXCLUDE, PDF pt), red lift names, and any other font, size or colour. The symbol is the nearest one on the
text's line within 12 pt before its first or after its last character. Prints what it skipped, the symbols no
label took, and each name with its symbols. Was the scratch jay_labels.py (2026-09-30), unchanged but for its
two paths.
"""
import pymupdf, json, collections, sys
page = pymupdf.open(sys.argv[1])[0]
CLIP = (9, 66, 1076, 657); S = 4.0
EXCLUDE = {'legend': (10, 68, 400, 160), 'stats': (853, 238, 1062, 646), 'inset': (794, 85, 993, 227), 'logos': (10, 605, 130, 655)}
def inside(b, r): return r[0] <= (b[0]+b[2])/2 <= r[2] and r[1] <= (b[1]+b[3])/2 <= r[3]
spans = []
for blk in page.get_text('dict')['blocks']:
    for ln in blk.get('lines', []):
        for sp in ln['spans']:
            t = sp['text'].strip()
            if t:
                spans.append({'text': t, 'size': round(sp['size'], 1), 'font': sp['font'], 'color': tuple(round(v, 2) for v in pymupdf.sRGB_to_pdf(sp['color'])), 'bbox': tuple(round(v, 1) for v in sp['bbox']), 'dir': ln['dir']})
red = {(s['text'], s['bbox']) for s in spans if s['color'] == (0.94, 0.24, 0.26)}
seen, labels, skipped = set(), [], collections.Counter()
for s in spans:
    key = (s['text'], s['bbox'])
    if key in seen: continue
    seen.add(key)
    zone = next((n for n, r in EXCLUDE.items() if inside(s['bbox'], r)), None)
    if zone: skipped[zone] += 1; continue
    if key in red: skipped['lift'] += 1; continue
    if not (s['font'].startswith('DIN2014-Bold') and 5.2 <= s['size'] <= 6.1 and s['color'] in [(0.14, 0.12, 0.13), (1.0, 1.0, 1.0)]):
        skipped['other:' + s['text'][:18]] += 1; continue
    labels.append(s)
# symbols
syms = []
for d in page.get_drawings():
    if d['type'] not in ('f', 'fs') or not d.get('fill'): continue
    c = tuple(round(v, 2) for v in d['fill']); r = d['rect']; kinds = [it[0] for it in d['items']]
    t = None
    if c == (0.0, 0.62, 0.34) and kinds == ['c'] * 4 and 5 < r.width < 8: t = 'circle'
    elif c == (0.0, 0.32, 0.63) and 4 < r.width < 7 and kinds in (['re'], ['l'] * 4): t = 'square'
    elif c == (0.14, 0.12, 0.13) and kinds == ['l'] * 4 and 6 < r.width < 9: t = 'diamond'
    if t and not any(inside((r.x0, r.y0, r.x1, r.y1), z) for z in EXCLUDE.values()):
        syms.append({'type': t, 'c': ((r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2), 'used': False})
out = []
for s in labels:
    x0, y0, x1, y1 = s['bbox']; cy = (y0 + y1) / 2
    cands = [(abs(sy['c'][0] - x0), sy) for sy in syms if abs(sy['c'][1] - cy) < 4 and -12 < sy['c'][0] - x0 < 1]
    cands += [(abs(sy['c'][0] - x1) + 2, sy) for sy in syms if abs(sy['c'][1] - cy) < 4 and -1 < sy['c'][0] - x1 < 12]
    best = min(cands, key=lambda c: c[0])[1] if cands else None
    if best: best['used'] = True
    name = s['text'].replace('’', "'").strip()
    out.append({'mapName': name.upper(), 'printed': name, 'symbol': best['type'] if best else 'none-visible',
                'park': s['color'] == (1.0, 1.0, 1.0), 'labelSrc': [round((x0 + x1) / 2 * S - CLIP[0] * S), round(cy * S - CLIP[1] * S)],
                'symSrc': [round(best['c'][0] * S - CLIP[0] * S), round(best['c'][1] * S - CLIP[1] * S)] if best else None})
json.dump(out, open(sys.argv[2], 'w'), indent=1)
print(len(out), 'label spans;', 'skipped', dict(skipped))
print('unused symbols:', [(s['type'], [round(v) for v in s['c']]) for s in syms if not s['used']])
names = collections.Counter(o['printed'] for o in out)
print(len(names), 'distinct names')
for n, k in sorted(names.items()):
    syms_ = collections.Counter(o['symbol'] for o in out if o['printed'] == n)
    print(f'  {n!r:28} x{k} {dict(syms_)}' + ('  PARK' if any(o['park'] for o in out if o['printed'] == n) else ''))
