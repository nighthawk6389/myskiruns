"""A resort's trail list (trails.ts) against its trail report (report.json): which runs only one of them lists,
which ratings differ, and which names are spelled otherwise (the same letters and digits, other spacing, case or
punctuation). Read every difference on a crop of the map before acting on it: the map decides what's on it, the
report decides spellings (docs/trail-map-playbook.md, Part 1, "Conventions for the judgment calls").

    python3 tools/trailmap/reports/compare.py --resort keystone
    python3 tools/trailmap/reports/compare.py --resort heavenly --key trails_2024_25
    python3 tools/trailmap/reports/compare.py --resort big-sky --report work/big-sky/feed_rows.json

--report: a report.json ({_source, <key>: [[name, area, rating], ...]}, as feed_trails.py writes it), default the
resort's tools/trailmap/resorts/<id>/report.json; --key: its list (default: trails). Ratings are compared as the
app's: Green, Blue, Black, DoubleBlack (Extreme too) map to green, blue, black, double-black; TerrainPark is left
out of the rating check (the app rates parks by the map). Names match on their letters and digits, upper-cased,
with "The" dropped (Black Forest = The Black Forest).
"""
import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from resort_files import resort_files, trail_info  # noqa: E402

RATING = {'green': 'green', 'blue': 'blue', 'black': 'black', 'doubleblack': 'double-black', 'extreme': 'double-black',
          'beginner': 'green', 'intermediate': 'blue', 'advanced': 'black', 'expert': 'double-black'}


def key(n):
    n = n.upper().replace('’', "'")
    n = re.sub(r'\bTHE\b', '', n)
    return re.sub(r'[^A-Z0-9]', '', n)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('--resort', required=True)
    ap.add_argument('--report', help='default: tools/trailmap/resorts/<id>/report.json')
    ap.add_argument('--key', default='trails')
    a = ap.parse_args()
    f = resort_files(a.resort)
    rows = json.load(open(a.report or os.path.join(f['tools'], 'report.json')))[a.key]
    trails = trail_info(f['trails'])
    rk = {}
    for n, area, rating in rows:
        rk.setdefault(key(n), (n, area, RATING.get(re.sub(r'[^a-z]', '', str(rating).lower()))))
    tk = {key(n): (tid, n, d) for tid, (n, d, _) in trails.items()}
    only_app = sorted(v for k, v in tk.items() if k not in rk)
    only_rep = sorted(v for k, v in rk.items() if k not in tk)
    print(f'{len(trails)} trails in trails.ts, {len(rows)} rows in the report ({len(rk)} names)')
    print(f'\nonly in trails.ts ({len(only_app)}):')
    for tid, n, d in only_app:
        print(f'  {n} ({d}; id {tid})')
    print(f'\nonly in the report ({len(only_rep)}):')
    for n, area, r in only_rep:
        print(f'  {n} ({area}, {r or "park or other"})')
    print('\nratings that differ:')
    for k, (tid, n, d) in sorted(tk.items()):
        if k in rk and rk[k][2] and rk[k][2] != d:
            print(f'  {n}: trails.ts {d}, report {rk[k][2]} ({rk[k][1]})')
    print('\nspelled otherwise (trails.ts -> report):')
    for k, (tid, n, d) in sorted(tk.items()):
        if k in rk and rk[k][0].replace('’', "'") != n.replace('’', "'"):
            print(f'  {n!r} -> {rk[k][0]!r}')


if __name__ == '__main__':
    main()
