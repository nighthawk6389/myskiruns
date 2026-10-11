"""Crested Butte's area elevations (resort.AREAS): the top of each area's highest lift, as OpenStreetMap draws the lift
and the USGS's 10 m elevation model (NED, through api.opentopodata.org) gives the ground there. The map prints only
the summit (12,162 ft) and the resort publishes no lift elevations.

    python3 tools/trailmap/osm_check.py fetch crested-butte --bbox 38.86,-107.00,38.92,-106.93   # work/crested-butte/osm.json
    python3 tools/trailmap/resorts/crested-butte/lift_tops.py

Prints each lift's two ends (m) and its top in feet. Run once (2026-10-11); the results are written into resort.py.
"""
import json
import os
import subprocess
import time

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../..'))


def ned(points):
    q = '|'.join(f'{lat},{lon}' for lat, lon in points)
    out = subprocess.run(['curl', '-sS', '-m', '60', f'https://api.opentopodata.org/v1/ned10m?locations={q}'],
                         capture_output=True, text=True).stdout
    return [r['elevation'] for r in json.loads(out)['results']]


def main():
    d = json.load(open(os.path.join(REPO, 'work/crested-butte/osm.json')))
    for e in d.get('elements', d):
        t = e.get('tags', {})
        if e.get('type') != 'way' or 'aerialway' not in t or not e.get('geometry'):
            continue
        g = e['geometry']
        a, b = ned([(g[0]['lat'], g[0]['lon']), (g[-1]['lat'], g[-1]['lon'])])
        print(f"{t.get('name')}: ends {a:.0f} m, {b:.0f} m; top {max(a, b) / 0.3048:,.0f} ft")
        time.sleep(1.1)  # the public API allows one request a second


if __name__ == '__main__':
    main()
