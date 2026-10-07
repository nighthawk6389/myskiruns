"""unmatched.py: Park City's names (after JOIN/RENAME/DROP) not in the archived trail report, and the report's
trails no name matches."""
import json, re, sys, io, contextlib
sys.path.insert(0, '/home/user/myskiruns/tools/trailmap')
import pdf_resort as pr
S = '/tmp/claude-0/-home-user-myskiruns/6d543bfc-3ab1-5e7f-9c64-5c2d6dd5c830/scratchpad/pc'
F = json.load(open(f'{S}/truth/feed_trails.json'))
def key(s):
    s = s.upper().replace('’', "'").replace('É', 'E').replace('À', 'A')
    return re.sub(r'[^A-Z0-9&]', '', s)
fk = {key(r['name']): r for r in F}
r = pr.Resort('park-city')
names = r.names()
r.symbols(names)
nk = {key(n['name']) for n in names}
un = [n for n in names if key(n['name']) not in fk]
print(len(names), 'names,', len({n['name'] for n in names}), 'distinct;', len(un), 'not in the report:')
for n in un:
    print(f"  {n['name']:26s} {n['color']:6s} {str(n.get('symbol')):14s} pt({n['c'][0]/2.5+12:5.0f},{n['c'][1]/2.5+12:4.0f})")
miss = [x for x in F if key(x['name']) not in nk]
print(len(miss), 'report trails with no name:')
for x in sorted(miss, key=lambda x: x['area']):
    print(f"  {x['area'][:24]:24s} {x['difficulty']:11s} {x['name']}")
