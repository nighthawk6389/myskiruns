"""Cluster Copper glyph fills by shape (item kinds + normalised chord lengths).

    python3 tools/trailmap/resorts/copper-mountain/cluster.py     # regen.sh runs it (was cu_cluster.py)

Reads glyphs.json (glyphs.py), writes clusters.json in the working folder: the glyphs with their cluster id ('cl')
and the clusters (same kinds, signature within 0.03), largest first. checks/sheet.py draws them for reading;
the letters read are kept by shape signature in letters.json (cluster ids shift whenever a threshold changes).
"""
import collections, json
from common import work
G = json.load(open(work('glyphs.json')))
clusters = []  # [kinds, sig, members]
for i, g in enumerate(G):
    for c in clusters:
        if c['kinds'] == g['kinds'] and max(abs(a - b) for a, b in zip(c['sig'], g['sig'])) < 0.03:
            c['m'].append(i); break
    else:
        clusters.append({'kinds': g['kinds'], 'sig': g['sig'], 'm': [i]})
clusters.sort(key=lambda c: -len(c['m']))
for k, c in enumerate(clusters):
    for i in c['m']:
        G[i]['cl'] = k
json.dump({'glyphs': G, 'clusters': [{'kinds': c['kinds'], 'n': len(c['m']), 'm': c['m']} for c in clusters]},
          open(work('clusters.json'), 'w'))
print(len(clusters), 'clusters; sizes:', [len(c['m']) for c in clusters][:80])
print('singletons:', sum(1 for c in clusters if len(c['m']) == 1))
