"""labmatch.py PANEL: each printed label (text, centre in map px, glyph count) with the feed names it could be part
of (exact, or the label's words all in the name), to plan JOIN / RENAME."""
import json, re, sys
S = '/tmp/claude-0/-home-user-myskiruns/6d543bfc-3ab1-5e7f-9c64-5c2d6dd5c830/scratchpad/pt'
p = sys.argv[1]
F = json.load(open(f'{S}/truth/feed_trails.json'))
norm = lambda s: re.sub(r'[^a-z0-9 ]', '', s.lower().replace('’', "'").replace("'", ''))  # noqa: E731
names = {}
for r in F:
    names.setdefault(norm(r['name']), []).append(r)
d = json.load(open(f'/home/user/myskiruns/work/palisades-tahoe/{p}/printed.json'))
sys.path.insert(0, f'/home/user/myskiruns/tools/trailmap/resorts/palisades-tahoe/panels/{p}')
import importlib.util
spec = importlib.util.spec_from_file_location('r', f'/home/user/myskiruns/tools/trailmap/resorts/palisades-tahoe/panels/{p}/resort.py')
R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
x0, y0 = R.CLIP[0], R.CLIP[1]
for l in sorted(d['labels'], key=lambda l: (round(l['c'][1] / 15), l['c'][0])):
    t = norm(' '.join(l['text'].split()))
    c = ((l['c'][0] - x0) * R.SCALE, (l['c'][1] - y0) * R.SCALE)
    exact = t in names
    words = set(t.split())
    part = [k for k in names if words and words <= set(k.split()) and k != t]
    tag = 'EXACT ' + names[t][0]['difficulty'] + '/' + names[t][0]['area'] if exact else ('part of: ' + ', '.join(part[:4]) if part else 'NO MATCH')
    print(f"{l['text']:28s} ({c[0]:5.0f},{c[1]:5.0f}) {tag}")
