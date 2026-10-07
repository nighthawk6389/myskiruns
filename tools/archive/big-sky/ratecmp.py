"""ratecmp.py: Big Sky's trails.ts ratings and mountains vs the trail report (tools/trailmap/resorts/big-sky/report.json)."""
import json, re, collections, sys
sys.path.insert(0, '/home/user/myskiruns/tools/trailmap/resorts/big-sky')
import importlib.util
spec = importlib.util.spec_from_file_location('bs', '/home/user/myskiruns/tools/trailmap/resorts/big-sky/resort.py')
B = importlib.util.module_from_spec(spec); spec.loader.exec_module(B)
norm = lambda s: re.sub(r'[^a-z0-9]', '', s.lower().replace('’', "'"))  # noqa: E731
APP = {'beginner': 'green', 'intermediate': 'blue', 'advanced intermediate': 'blue', 'advanced': 'black',
       'expert': 'double-black', 'high exposure': 'double-black', 'park': None}
rep = {norm(n): (n, APP[d], d, B.AREA_OF[n]) for n, a, d in B.REPORT}
ts = open('/home/user/myskiruns/src/data/resorts/big-sky/trails.ts').read()
rows = re.findall(r"\{ id: '([^']+)', name: (\"[^\"]+\"|'[^']+'), difficulty: '([^']+)', peak: '([^']+)'([^}]*)\}", ts)
agree, seen = 0, set()
for tid, name, diff, peak, rest in rows:
    name = name[1:-1]
    r = rep.get(norm(name))
    if not r:
        print(f'not in report: {name} ({diff}, {peak}){rest}')
        continue
    seen.add(norm(name))
    ok_d = r[1] is None or r[1] == diff
    if ok_d and r[3] == peak:
        agree += 1
        continue
    print(f'DIFFERS: {name}: ours {diff}/{peak}; report {r[2]} ({r[1]})/{r[3]}')
print(f'{len(rows)} trails, {agree} agree with the report')
print('report trails not in trails.ts:', [n for k, (n, *_r) in rep.items() if k not in seen])
