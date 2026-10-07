"""ratecmp.py: Park City's trails.ts difficulty and area vs the archived trail report's (Common Crawl, March 2026)."""
import json, re
S = '/tmp/claude-0/-home-user-myskiruns/6d543bfc-3ab1-5e7f-9c64-5c2d6dd5c830/scratchpad/pc'
F = json.load(open(f'{S}/truth/feed_trails.json'))
def key(s):
    s = s.upper().replace('’', "'").replace('É', 'E').replace('À', 'A')
    s = re.sub(r'\s*\((FULL|LOWER)\)', '', s)
    s = re.sub(r'\s+(RUN|TERRAIN PARK)$', '', s)
    return re.sub(r'[^A-Z0-9&]', '', s)
REP = {}
for r in F:
    REP.setdefault(key(r['name']), []).append(r)
MAP = {'Green': 'green', 'Blue': 'blue', 'Black': 'black', 'DoubleBlack': 'double-black', 'TerrainPark': 'park'}
ts = open('/home/user/myskiruns/src/data/resorts/park-city/trails.ts').read()
rows = re.findall(r"\{ id: '([^']+)', name: (['\"])(.*?)\2, difficulty: '([^']+)', peak: '([^']+)'(.*?)\}", ts)
diff, missing = [], []
PC = {'Payday/Town/Crescent', "Bonanza/McConkey's/Pioneer", 'Silverlode/Thaynes/Motherlode', 'King Con', 'Jupiter'}
for tid, _q, name, d, peak, extra in rows:
    rs = REP.get(key(name))
    if not rs:
        missing.append(name)
        continue
    rd = {MAP[r['difficulty']] for r in rs}
    side = {'park-city' if r['area'] in PC else 'canyons' for r in rs}
    park = 'isTerrainPark' in extra
    if not (d in rd or (park and 'park' in rd)):
        diff.append((name, d, sorted(rd), 'park' if park else ''))
    if peak not in side:
        diff.append((name, 'AREA', peak, sorted(side)))
print(len(rows), 'trails;', len(missing), 'not in the report:', missing)
print(len(diff), 'differ:')
for x in diff:
    print('  ', x)
