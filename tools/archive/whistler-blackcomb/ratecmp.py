import json, re, sys, collections
sys.path.insert(0, '/home/user/myskiruns/tools/trailmap')
import pdf_resort as pr
R = json.load(open('/tmp/claude-0/-home-user-myskiruns/6d543bfc-3ab1-5e7f-9c64-5c2d6dd5c830/scratchpad/wb_truth/runs.json'))
def key(n):
    n = n.upper().replace('’', "'")
    n = re.sub(r"[^A-Z0-9& ]", ' ', n.replace("'", ''))
    n = re.sub(r'\b(UPPER|LOWER|MID|MIDDLE)\b', ' ', n).replace('&', ' AND ')
    return ''.join(n.split())
feed = collections.defaultdict(set)
for r in R:
    if 'feed' in r['source']:
        feed[key(r['name'])].add(r['difficulty'])
SYM = {'circle': 'Green', 'square': 'Blue', 'diamond': 'Black', 'double-diamond': 'DoubleBlack'}
syms = collections.defaultdict(list)
for panel in ('main', 'symphony', 'glacier'):
    r = pr.Resort(f'whistler-blackcomb/{panel}')
    names = r.names(); r.symbols(names)
    for n in names:
        syms[n['name']].append((panel, n.get('symbol')))
for nm, ss in sorted(syms.items()):
    f = feed.get(key(nm))
    got = {SYM.get(s) for _, s in ss if s}
    if not f:
        continue
    if not got:
        print(f'NO SYMBOL  {nm:28s} feed={sorted(f)}')
    elif not got & f:
        print(f'DIFFERS    {nm:28s} map={sorted(got)} feed={sorted(f)}')
