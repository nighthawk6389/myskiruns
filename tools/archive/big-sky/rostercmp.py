"""rostercmp.py [panel ...]: the panels' names vs the resort feed: names not in it, and feed trails no panel prints."""
import collections, contextlib, io, json, re, sys
sys.path.insert(0, '/home/user/myskiruns/tools/trailmap')
import pdf_resort as pr
S = '/tmp/claude-0/-home-user-myskiruns/6d543bfc-3ab1-5e7f-9c64-5c2d6dd5c830/scratchpad'
F = json.load(open(f'{S}/bs/truth/feed_trails.json'))
norm = lambda s: re.sub(r'[^a-z0-9]', '', s.lower().replace('’', "'"))  # noqa: E731
feed = {norm(t['name']): t for t in F}
panels = sys.argv[1:] or ['main', 'south-face', 'bowl']
seen = collections.defaultdict(set)
for p in panels:
    r = pr.Resort(f'big-sky/{p}')
    with contextlib.redirect_stdout(io.StringIO()):
        r.build()
    for n in r.names_all:
        seen[n['name']].add(p)
print('names on the map not in the feed:')
for n in sorted(seen):
    if norm(r.R.DISPLAY.get(n, n)) not in feed:
        print('  ', repr(n), sorted(seen[n]))
print('feed trails no panel prints:')
mapped = {norm(r.R.DISPLAY.get(n, n)) for n in seen}
by = collections.defaultdict(list)
for k, t in feed.items():
    if k not in mapped:
        by[t['area']].append(f"{t['name']} [{t['difficulty']}]")
for a, v in sorted(by.items()):
    print('  ', a + ':', ', '.join(v))
print(len(seen), 'names on the map;', len(feed), 'feed trails;', sum(len(v) for v in by.values()), 'not printed')
