"""vl_diff.py: per trail name, the symbols on its own pieces (named ones and the unnamed '?' ones sitting on them)
and the drawn length of each line colour, to settle trails printed with more than one rating."""
import collections, json, math
exec(open('vl_symnames.py').read())
exec(open('vl_checked.py').read())
exec(open('vl_pt.py').read())
out = {}
for panel in ('front-side', 'back-bowls', 'blue-sky'):
    P = json.load(open(f'pieces_{panel}.json'))['polylines']
    A = json.load(open(f'assign_{panel}.json'))['assign']
    S = json.load(open(f'syms_{panel}.json'))
    for p in P:
        p['pt'] = pts_of(panel, p)
    for pid, ns in A.items():
        n = ns[0]
        e = out.setdefault(n, {'len': collections.Counter(), 'syms': collections.Counter(), 'where': set()})
        e['len'][P[int(pid)]['cls']] += P[int(pid)]['lengthPx']
        e['where'].add(panel)
    for n, pts in TRACED.get(panel, []):
        e = out.setdefault(n, {'len': collections.Counter(), 'syms': collections.Counter(), 'where': set()})
        e['where'].add(panel)
    for s in S:
        nm = NAMES[panel].get(s['i'])
        if nm and nm != '?':
            out.setdefault(nm, {'len': collections.Counter(), 'syms': collections.Counter(), 'where': set()})['syms'][s['t']] += 1
            continue
        # an unnamed symbol: which named piece is it on?
        best = None
        for p in P:
            d = min(seg_dist(s['c'], p['pt'][i], p['pt'][i + 1]) for i in range(len(p['pt']) - 1))
            if d < s['r'] * 1.2 and (best is None or d < best[0]):
                best = (d, p['id'])
        if best and str(best[1]) in A:
            n = A[str(best[1])][0]
            out[n]['syms'][s['t'] + '?'] += 1
            print(f'{panel} #{s["i"]} {s["t"]} unnamed, on piece {best[1]} = {n}')
        else:
            print(f'{panel} #{s["i"]} {s["t"]} unnamed, on no named piece', best)
print()
for n, e in sorted(out.items()):
    kinds = {k.rstrip('?') for k in e['syms']}
    cols = {c for c, l in e['len'].items() if l > 0}
    rated = {'circle': 'green', 'square': 'blue', 'diamond': 'black', 'double-diamond': 'black'}
    mixed = len({rated[k] for k in kinds}) > 1 or len(cols) > 1 or ('diamond' in kinds and 'double-diamond' in kinds)
    if mixed:
        print(f'{n:28s} syms={dict(e["syms"])} len={dict(e["len"])} {sorted(e["where"])}')
json.dump({n: {'len': dict(e['len']), 'syms': dict(e['syms']), 'where': sorted(e['where'])} for n, e in out.items()},
          open('diff_stats.json', 'w'), indent=1)
