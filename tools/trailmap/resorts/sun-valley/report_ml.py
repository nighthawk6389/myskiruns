"""Sun Valley's trail list from its interactive maps (mountain.live: public.mountain.live/interactive-map/v1/map/name/
SunValley-BaldMountain and SunValley-DollarMountain, then each map's /staticPoiData?lang=en), as report.json rows
[name, area, rating]: every downhill-skiing trail, its area the mountain, its rating the map's trailLevel.

    python3 -I tools/trailmap/resorts/sun-valley/report_ml.py work/sun-valley/ml/bald_static.json \\
        work/sun-valley/ml/dollar_static.json --out tools/trailmap/resorts/sun-valley/report.json
"""
import argparse
import json

LEVEL = {'GREEN_CIRCLE': 'Green', 'BLUE_SQUARE': 'Blue', 'BLACK_DIAMOND': 'Black',
         'DOUBLE_BLACK_DIAMOND': 'DoubleBlack', 'TERRAIN_PARKS': 'TerrainPark'}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('bald')
    ap.add_argument('dollar')
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    rows = []
    for f, area in ((a.bald, 'Bald Mountain'), (a.dollar, 'Dollar Mountain')):
        for it in json.load(open(f))['items']:
            d = it['data']
            if d.get('type') == 'TRAIL' and d.get('trailType') == 'DOWNHILL_SKIING':
                rows.append([d['name'].strip(), area, LEVEL.get(d.get('trailLevel'), d.get('trailLevel'))])
    rows.sort(key=lambda r: (r[1], r[0]))
    json.dump({'_source': "Sun Valley's interactive maps (mountain.live: SunValley-BaldMountain, "
                          'SunValley-DollarMountain staticPoiData), fetched 2026-10-11; rows [name, area, rating]',
               'trails': rows}, open(a.out, 'w'), indent=1)
    print(len(rows), 'rows ->', a.out)


if __name__ == '__main__':
    main()
