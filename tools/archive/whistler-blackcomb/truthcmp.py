import json, re, sys
sys.path.insert(0, '/home/user/myskiruns/tools/trailmap')
import pdf_resort as pr
R = json.load(open('/tmp/claude-0/-home-user-myskiruns/6d543bfc-3ab1-5e7f-9c64-5c2d6dd5c830/scratchpad/wb_truth/runs.json'))
feed = [r for r in R if 'feed' in r['source']]
gis = [r for r in R if 'feed' not in r['source']]
def key(n):
    n = n.upper().replace('’', "'").replace('`', "'")
    n = re.sub(r"[^A-Z0-9& ]", ' ', n.replace("'", ''))
    n = re.sub(r'\b(UPPER|LOWER|MID|MIDDLE)\b', ' ', n)
    n = n.replace('&', ' AND ')
    return ' '.join(n.split())
ours = {}
for panel in ('main', 'symphony', 'glacier'):
    r = pr.Resort(f'whistler-blackcomb/{panel}')
    names = r.names(); r.symbols(names)
    for n in names:
        ours.setdefault(n['name'], []).append((panel, n.get('symbol')))
fk = {}
for r in feed:
    fk.setdefault(key(r['name']), []).append(r)
gk = {}
for r in gis:
    for g in [r['name']] + (r.get('gis_names') or []):
        gk.setdefault(key(g), []).append(r)
print(len(ours), 'map names;', len(feed), 'feed runs')
miss = []
for nm, where in sorted(ours.items()):
    k = key(nm)
    if k in fk:
        continue
    alt = [x for x in fk if k.replace(' ', '') == x.replace(' ', '')]
    if alt: continue
    g = gk.get(k)
    miss.append((nm, [p for p, _ in where], 'GIS:' + ','.join(f"{x['name']}({x['difficulty']},map={x.get('gis_on_trail_map')})" for x in g) if g else 'not in feed or GIS'))
print('\nMAP NAMES NOT IN THE FEED:')
for m in miss: print(' ', m)
okeys = {key(n) for n in ours}
okeys |= {k.replace(' ', '') for k in okeys}
print('\nFEED RUNS NOT ON THE MAP (by base name):')
seen = set()
for r in feed:
    k = key(r['name'])
    if k in okeys or k.replace(' ', '') in okeys or k in seen: continue
    seen.add(k)
    print(f"  {r['name']} | {r['mountain']} | {r['area']} | {r['difficulty']} | gis_on_map={r.get('gis_on_trail_map')}")
