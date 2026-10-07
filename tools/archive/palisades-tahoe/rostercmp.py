"""rostercmp.py: every panel's names vs the trail report: names not in it, and report trails no panel prints."""
import json, re, sys, collections, io, contextlib
sys.path.insert(0, '/home/user/myskiruns/tools/trailmap')
import pdf_resort as pr
S = '/tmp/claude-0/-home-user-myskiruns/6d543bfc-3ab1-5e7f-9c64-5c2d6dd5c830/scratchpad/pt'
F = json.load(open(f'{S}/truth/feed_trails.json'))
norm = lambda s: re.sub(r'[^a-z0-9]', '', s.lower())  # noqa: E731
ALIAS = {'facecliffs': 'thefacecliffs', 'hiddenknolls': 'hiddenknolls'}
seen = collections.defaultdict(set)
for p in ('palisades', 'alpine-front', 'alpine-back'):
    r = pr.Resort(f'palisades-tahoe/{p}')
    with contextlib.redirect_stdout(io.StringIO()):
        names = r.names()
    for n in names:
        nm = n['name']
        side = 'alpine' if '(Alpine)' in nm or p != 'palisades' else 'palisades'
        k = norm(re.sub(r'\s*\(.*\)$', '', nm))
        seen[(ALIAS.get(k, k), side)].add(p)
PAL = {'Palisades Peak', 'Emigrant Peak', 'High Camp', 'Granite Peak', 'Snow King Peak', 'KT Peak', 'Terrain Parks'}
rep = {(norm(x['name']), 'palisades' if x['area'] in PAL else 'alpine'): x for x in F}
print('names on the map not in the report (by side):')
for k, ps in sorted(seen.items()):
    if k not in rep:
        print('  ', k, sorted(ps))
print('report trails no panel prints:')
miss = collections.defaultdict(list)
for k, x in sorted(rep.items()):
    if k not in seen:
        miss[x['area']].append(x['name'])
for a, v in miss.items():
    print(f'   {a}: {", ".join(v)}')
print(len(seen), 'names on the map;', len(rep), 'report trails;', sum(len(v) for v in miss.values()), 'not printed')
