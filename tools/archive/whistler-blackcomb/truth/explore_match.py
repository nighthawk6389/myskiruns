"""Exploratory: which feed names match GIS names after normalisation, and which don't."""
import collections
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wb_common as C  # noqa: E402

_, feed = C.load_feed(C.FEED_2026)
gis = C.load_gis_runs()
gis_by = collections.defaultdict(list)
for r in gis:
    gis_by[C.norm(r['run_name'])].append(r)

unmatched_feed = []
matched_keys = set()
for t in feed:
    k = C.norm(t['Name'])
    if k in gis_by:
        matched_keys.add(k)
    else:
        unmatched_feed.append(t)
print('feed entries', len(feed), 'matched', len(feed) - len(unmatched_feed))
print('\nFEED NOT IN GIS:')
for t in sorted(unmatched_feed, key=lambda t: t['Name']):
    print('  ', repr(t['Name']), t['Difficulty'], '|', t['Area'])
print('\nGIS NOT IN FEED (trailmap, mountain, difficulty, name):')
rows = sorted({(r['trailmap'], r['mountain'], r['difficulty'], r['run_name']) for k, rs in gis_by.items() if k not in matched_keys for r in rs}, key=lambda x: (str(x[0]), x[1], x[3]))
for row in rows:
    print('  ', row)
print(len(rows))
