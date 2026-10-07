"""Breckenridge's named difficulty symbols in map px, for tools/trailmap/symbol_audit.py: names.json's symbols
(PDF points, each with the label it belongs to) -> work/breckenridge/named_syms.json [{name, t, c, r}].

    python3 tools/trailmap/resorts/breckenridge/checks/named_syms.py
    python3 tools/trailmap/symbol_audit.py --symbols work/breckenridge/named_syms.json \\
        --paths src/data/resorts/breckenridge/trailPaths.json --trails src/data/resorts/breckenridge/trails.ts \\
        --image work/breckenridge/map.png --out work/breckenridge/symaudit --mode off   # then ends, diamonds
"""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from common import work  # noqa: E402

S, X0, Y0 = 3.0, 0, 80  # map px per PDF pt; the map clip's origin
out = [{'name': s['label'], 't': s['t'], 'c': [round((s['c'][0] - X0) * S, 1), round((s['c'][1] - Y0) * S, 1)],
        'r': round(s['s'] * S / 2, 1)} for s in json.load(open(work('names.json')))['syms'] if s.get('label')]
json.dump(out, open(work('named_syms.json'), 'w'), indent=1)
print(work('named_syms.json'), len(out), 'named symbols')
