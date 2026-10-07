"""merge_answers.py: compare the two tilings' reader answers with the tool's tags (names.json).
Prints: consensus changes (both readers agree, differ from the tag), disagreements, missing answers."""
import json, glob, sys, collections, re
S = '/tmp/claude-0/-home-user-myskiruns/6d543bfc-3ab1-5e7f-9c64-5c2d6dd5c830/scratchpad/wb'
N = json.load(open('/home/user/myskiruns/work/whistler-blackcomb/main/names.json'))
ans = {'A': {}, 'B': {}}
for f in sorted(glob.glob(f'{S}/answers/r[AB]_*.json')):
    t = re.search(r'r([AB])_', f).group(1)
    for k, v in json.load(open(f)).items():
        ans[t][str(k)] = v
def norm(x): return (x or '').strip().upper().replace("'", '’')
def tag(k): return N.get(k, '?').rstrip('~')
agree_same, agree_change, disagree, missing = [], [], [], []
for k in sorted(N, key=int):
    a, b = ans['A'].get(k), ans['B'].get(k)
    if not a or not b:
        missing.append((k, tag(k), a and a['name'], b and b['name'])); continue
    na, nb = norm(a['name']), norm(b['name'])
    t = norm(tag(k))
    if na == nb and na not in ('?',):
        (agree_same if na == t else agree_change).append((k, N.get(k), na, a['confidence'], b['confidence'], a['why'][:80], b['why'][:80]))
    else:
        disagree.append((k, N.get(k), na, a['confidence'], a['why'][:90], nb, b['confidence'], b['why'][:90]))
print(f'{len(agree_same)} agree with the tool, {len(agree_change)} agree on a change, {len(disagree)} disagree, {len(missing)} missing')
if '-v' in sys.argv:
    print('\nCONSENSUS CHANGES'); [print(' ', *x, sep=' | ') for x in agree_change]
    print('\nDISAGREEMENTS'); [print(' ', *x, sep=' | ') for x in disagree]
    print('\nMISSING'); [print(' ', *x) for x in missing]
