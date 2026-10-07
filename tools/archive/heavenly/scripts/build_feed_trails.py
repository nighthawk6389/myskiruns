"""Build Heavenly's trail list from the FR.TerrainStatusFeed of an archived
terrain-and-lift-status.aspx page.

Inputs (feed JSON files written by wb_truth/scripts/extract_feed.py):
  --numeric  the page's first FR.TerrainStatusFeed (lift widget; enums as numbers)
  --labels   the page's second FR.TerrainStatusFeed (trail widget; enums as strings)
  --prev     optional: the labelled feed of an earlier season, to record renames
  --prev-numeric  optional: that earlier page's numeric feed
Outputs into --out: feed_trails.json, feed_raw.json, feed_raw_labels.json
(and, with --prev-out, the earlier season's list in the same schema).

Usage: python3 -I build_feed_trails.py --numeric A.json --labels B.json
         [--prev C.json --prev-out trails_prev.json] --out <dir>
"""
import argparse
import collections
import json
from pathlib import Path

# Feed code -> (label in the labelled feed, our mapping).
CODES = {
    1: ('Green', 'green'),
    2: ('Blue', 'blue'),
    3: ('Black', 'black'),
    4: ('DoubleBlack', 'double-black'),
    5: ('TerrainPark', 'park'),
    7: ('Extreme', 'double-black'),
}
LABEL_TO_MAPPED = {label: mapped for label, mapped in CODES.values()}

STATE = {
    'California': ('CA', 'feed area name'),
    'Nevada': ('NV', 'feed area name'),
    'Top of Gondola': ('CA', 'inferred, not in feed: the gondola top / Adventure Peak / '
                             'Tamarack Lodge area, reached from Heavenly Village in South '
                             'Lake Tahoe, is on the California side'),
}


def trails_of(feed):
    for area in feed['GroomingAreas']:
        for t in area['Trails']:
            yield area, t


def build(labels, numeric=None):
    num = {t['Id']: t for _, t in trails_of(numeric)} if numeric else {}
    out = []
    for area, t in trails_of(labels):
        label = t['Difficulty']
        rec = {'id': t['Id'], 'name': t['Name']}
        if numeric:
            code = num[t['Id']]['Difficulty']
            assert CODES[code][0] == label, (t, code)
            rec['difficulty_code'] = code
        rec['difficulty_label'] = label
        rec['difficulty'] = LABEL_TO_MAPPED[label]
        rec['area'] = area['Name']
        rec['area_id'] = area['Id']
        state, src = STATE[area['Name']]
        rec['state'] = state
        rec['state_source'] = src
        out.append(rec)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--numeric', required=True)
    ap.add_argument('--labels', required=True)
    ap.add_argument('--prev')
    ap.add_argument('--prev-numeric')
    ap.add_argument('--prev-out')
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    numeric = json.loads(Path(a.numeric).read_text(encoding='utf-8'))
    labels = json.loads(Path(a.labels).read_text(encoding='utf-8'))
    out = Path(a.out)
    trails = build(labels, numeric)
    if a.prev:
        prev = json.loads(Path(a.prev).read_text(encoding='utf-8'))
        prev_num = json.loads(Path(a.prev_numeric).read_text(encoding='utf-8')) if a.prev_numeric else None
        prev_trails = build(prev, prev_num)
        by_id = {t['id']: t for t in prev_trails}
        for t in trails:
            p = by_id.get(t['id'])
            if p and p['name'] != t['name']:
                t['name_dec_2024'] = p['name']
            if p and p['difficulty_label'] != t['difficulty_label']:
                t['difficulty_label_dec_2024'] = p['difficulty_label']
        if a.prev_out:
            Path(a.prev_out).write_text(json.dumps(prev_trails, indent=1, ensure_ascii=False) + '\n',
                                        encoding='utf-8')
        cur_ids = {t['id'] for t in trails}
        print('dropped since prev:', [(p['id'], p['name']) for p in prev_trails if p['id'] not in cur_ids])
        print('added since prev:', [(t['id'], t['name']) for t in trails if t['id'] not in by_id])
    (out / 'feed_trails.json').write_text(json.dumps(trails, indent=1, ensure_ascii=False) + '\n',
                                          encoding='utf-8')
    (out / 'feed_raw.json').write_text(json.dumps(numeric, indent=1, ensure_ascii=False) + '\n',
                                       encoding='utf-8')
    (out / 'feed_raw_labels.json').write_text(json.dumps(labels, indent=1, ensure_ascii=False) + '\n',
                                              encoding='utf-8')
    print('trails', len(trails))
    print('by area', collections.Counter(t['area'] for t in trails))
    print('by code', sorted(collections.Counter((t['difficulty_code'], t['difficulty_label'])
                                                for t in trails).items()))
    print('by mapped', collections.Counter(t['difficulty'] for t in trails))
    print('by area x mapped', sorted(collections.Counter((t['area'], t['difficulty'])
                                                         for t in trails).items()))


if __name__ == '__main__':
    main()
