"""ratecmp.py: trails.ts ratings and sides vs the resort's trail report (truth/feed_trails.json)."""
import json, re, collections
S = '/tmp/claude-0/-home-user-myskiruns/6d543bfc-3ab1-5e7f-9c64-5c2d6dd5c830/scratchpad/pt'
F = json.load(open(f'{S}/truth/feed_trails.json'))
norm = lambda s: re.sub(r'[^a-z0-9]', '', s.lower())  # noqa: E731
ICON = {'GreenCircle': 'green', 'BlueSquare': 'blue', 'BlackDiamond': 'black', 'DoubleBlackDiamond': 'double-black',
        'Park': 'park'}
PAL = {'Palisades Peak', 'Emigrant Peak', 'High Camp', 'Granite Peak', 'Snow King Peak', 'KT Peak'}
rep = collections.defaultdict(list)
for t in F:
    rep[norm(t['name'])].append((ICON[t['icon']], 'palisades' if t['area'] in PAL else ('alpine' if t['area'] != 'Terrain Parks' else '?'), t['area']))
ts = open('/home/user/myskiruns/src/data/resorts/palisades-tahoe/trails.ts').read()
rows = re.findall(r"\{ id: '([^']+)', name: (\"[^\"]+\"|'[^']+'), difficulty: '([^']+)', peak: '([^']+)'", ts)
agree = 0
for tid, name, diff, peak in rows:
    name = name[1:-1]
    r = rep.get(norm(name))
    if not r:
        print(f'not in report: {name} ({diff}, {peak})')
        continue
    if any(d == diff and s == peak for d, s, _a in r):
        agree += 1
        continue
    print(f'DIFFERS: {name}: ours {diff}/{peak}; report {r}')
print(f'{len(rows)} trails, {agree} agree with the report')
