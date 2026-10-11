"""Each label's characters with the glyph cluster they were read from (to find a misread shape)."""
import json, math, sys
g = json.load(open(sys.argv[1]))['glyphs']
d = json.load(open(sys.argv[2]))['labels']
want = sys.argv[3:]
for l in d:
    if want and not any(w in l['text'] for w in want):
        continue
    out = []
    chars = [c for c in l['text'] if c != ' ']
    for ch, p in zip(chars, l['pts']):
        best = min(g, key=lambda x: math.dist(x['c'], p))
        out.append(f"{ch}{best['cl']}")
    print(l['text'], '|', ' '.join(out))
