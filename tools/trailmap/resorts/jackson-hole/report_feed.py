"""Jackson Hole Mountain Resort's trail report: the feed its grooming and mountain report pages load
(https://jacksonhole-prod.zaneray.com/api/all.json, plain curl; tools/trailmap/reports/fetch_page.cjs found it), as
report.json.

    curl -sS -o work/jackson-hole/report/all.json https://jacksonhole-prod.zaneray.com/api/all.json
    python3 -I tools/trailmap/resorts/jackson-hole/report_feed.py work/jackson-hole/report/all.json \\
        --source "..." --out tools/trailmap/resorts/jackson-hole/report.json

The feed's `trails` hold every winter run, listed out of season too (closed), each with its name and trailLevel; it
gives no area (the rows' area is left empty: resort.py places each name by where it is printed). Rows: [name, '',
rating], ratings as tools/trailmap/reports/feed_trails.py writes them (Green, Blue, DoubleBlue: the resort's double
blue square, advanced intermediate; Black, DoubleBlack, TerrainPark).
"""
import argparse
import json

RATING = {'GREEN_CIRCLE': 'Green', 'BLUE_SQUARE': 'Blue', 'DOUBLE_BLUE_SQUARE': 'DoubleBlue',
          'BLACK_DIAMOND': 'Black', 'DOUBLE_BLACK_DIAMOND': 'DoubleBlack', 'TERRAIN_PARKS': 'TerrainPark'}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('feed')
    ap.add_argument('--out')
    ap.add_argument('--source', default='')
    a = ap.parse_args()
    trails = json.load(open(a.feed))['trails']
    rows = [[t['name'], '', RATING[t['trailLevel']]] for t in trails.values()
            if t.get('trailType') == 'DOWNHILL_SKIING']
    if a.out:
        json.dump({'_source': a.source, 'trails': rows}, open(a.out, 'w'), indent=1, ensure_ascii=False)
        open(a.out, 'a').write('\n')
    by = {}
    for _n, _a, r in rows:
        by[r] = by.get(r, 0) + 1
    print(f'{len(rows)} runs {by}')


if __name__ == '__main__':
    main()
