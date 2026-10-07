"""joins.py PANEL [--gap 14]: pairs and triples of nearby labels (pt) whose words, joined in either order, make a
trail report name: candidate JOINs (reading order by position: the upper/left part first)."""
import itertools, json, math, re, sys
S = '/tmp/claude-0/-home-user-myskiruns/6d543bfc-3ab1-5e7f-9c64-5c2d6dd5c830/scratchpad/pt'
p = sys.argv[1]
GAP = float(sys.argv[sys.argv.index('--gap') + 1]) if '--gap' in sys.argv else 14
F = json.load(open(f'{S}/truth/feed_trails.json'))
norm = lambda s: re.sub(r'[^a-z0-9]', '', s.lower().replace('’', "'"))  # noqa: E731
feed = {norm(r['name']): r['name'] for r in F}
L = json.load(open(f'/home/user/myskiruns/work/palisades-tahoe/{p}/printed.json'))['labels']
gap = lambda a, b: min(math.dist(x, y) for x in a['pts'] for y in b['pts'])  # noqa: E731
out = set()
for a, b in itertools.permutations(L, 2):
    if gap(a, b) > GAP:
        continue
    t = norm(a['text'] + b['text'])
    if t in feed and norm(a['text']) not in feed:
        out.add((feed[t], a['text'], b['text'], round(a['c'][0]), round(a['c'][1])))
    for c in L:
        if c is a or c is b or gap(b, c) > GAP:
            continue
        t3 = norm(a['text'] + b['text'] + c['text'])
        if t3 in feed:
            out.add((feed[t3], a['text'], b['text'] + ' + ' + c['text'], round(a['c'][0]), round(a['c'][1])))
for o in sorted(out):
    print(o)
