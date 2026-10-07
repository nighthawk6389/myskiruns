"""names.py PANEL: the panel's names after JOIN / RENAME / DROP (pdf_resort.py's reading), each with its symbol and
position (map px), and whether the trail report has it (by letters and digits only)."""
import json, re, sys
sys.path.insert(0, '/home/user/myskiruns/tools/trailmap')
import pdf_resort as pr
S = '/tmp/claude-0/-home-user-myskiruns/6d543bfc-3ab1-5e7f-9c64-5c2d6dd5c830/scratchpad/pt'
F = json.load(open(f'{S}/truth/feed_trails.json'))
norm = lambda s: re.sub(r'[^a-z0-9]', '', s.lower())  # noqa: E731
feed = {}
for r in F:
    feed.setdefault(norm(r['name']), []).append(r)
p = sys.argv[1]
r = pr.Resort(f'palisades-tahoe/{p}')
names = r.names()
syms, loose = r.symbols(names)
miss = 0
for n in names:
    k = norm(re.sub(r'\s*\(.*\)$', '', n['name']))
    f = feed.get(k)
    tag = '/'.join(sorted({x['difficulty'] + '@' + x['area'] for x in f})) if f else 'NOT IN REPORT'
    miss += not f
    print(f"{n['name']:28s} {str(n.get('symbol')):15s} ({n['c'][0]:5.0f},{n['c'][1]:5.0f}) {tag}")
print(len(names), 'names,', miss, 'not in the report;', len(loose), 'symbols with no name:',
      [(s['t'], round(s['c'][0]), round(s['c'][1])) for s in loose])
