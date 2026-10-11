"""A resort's lift tops, for its area elevations (resort.AREAS) where the resort publishes none: each lift's two ends
as OpenStreetMap draws the lift, and the ground there on the USGS's 10 m elevation model (NED, through
api.opentopodata.org; US resorts only). The map's own printed elevations come first; this is for the rest.

    python3 tools/trailmap/osm_check.py fetch <id> --bbox south,west,north,east     # work/<id>/osm.json
    python3 tools/trailmap/lift_tops.py <id>

Prints each lift's two ends (m) and its top in feet. Run once and write the results into the resort's resort.py,
with where they came from (Crested Butte, Mount Snow).
"""
import json
import os
import subprocess
import sys
import time

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..'))


def ned(points):
    q = '|'.join(f'{lat},{lon}' for lat, lon in points)
    out = subprocess.run(['curl', '-sS', '-m', '60', f'https://api.opentopodata.org/v1/ned10m?locations={q}'],
                         capture_output=True, text=True).stdout
    return [r['elevation'] for r in json.loads(out)['results']]


def main():
    rid = sys.argv[1]
    d = json.load(open(os.path.join(REPO, 'work', rid, 'osm.json')))
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
