"""symcmp.py PANEL: each name's symbol vs the trail report's rating; lists disagreements and names with none."""
import json, re, sys
sys.path.insert(0, '/home/user/myskiruns/tools/trailmap')
import pdf_resort as pr
S = '/tmp/claude-0/-home-user-myskiruns/6d543bfc-3ab1-5e7f-9c64-5c2d6dd5c830/scratchpad/pt'
F = json.load(open(f'{S}/truth/feed_trails.json'))
norm = lambda s: re.sub(r'[^a-z0-9]', '', s.lower())  # noqa: E731
RATE = {'Easy': 'circle', 'Intermediate': 'square', 'Very Difficult': 'diamond', 'Expert': 'double-diamond'}
feed = {}
for r in F:
    feed.setdefault(norm(r['name']), []).append(r)
p = sys.argv[1]
r = pr.Resort(f'palisades-tahoe/{p}')
names = r.names()
syms, loose = r.symbols(names)
ok = bad = none = 0
for n in names:
    f = feed.get(norm(re.sub(r'\s*\(.*\)$', '', n['name'])))
    want = {RATE.get(x['difficulty'], x['difficulty']) for x in f} if f else set()
    got = n.get('symbol')
    if got is None:
        none += 1
        print(f"  NONE  {n['name']:26s} report {sorted(want)} at ({n['c'][0]:.0f},{n['c'][1]:.0f})")
    elif want and got not in want:
        bad += 1
        print(f"  DIFF  {n['name']:26s} map {got:15s} report {sorted(want)} at ({n['c'][0]:.0f},{n['c'][1]:.0f})")
    else:
        ok += 1
print(p, ok, 'agree,', bad, 'differ,', none, 'with no symbol;', len(loose), 'loose:',
      [(s['t'], round(s['c'][0]), round(s['c'][1])) for s in loose])
