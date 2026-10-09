"""A resort's trail report from a Vail Resorts terrain feed: the FR.TerrainStatusFeed object of its
terrain-and-lift-status page (extract_feed.py writes each one to a JSON file), from an mtnpowder feed
(mtnpowder.com/feed/v3.json: README.md, "mtnfeed / mtnpowder") or from a DOR trail list (README.md, "Mt. Bachelor"),
as report.json rows [name, area, difficulty label], in the feed's order.

    python3 -I tools/trailmap/reports/feed_trails.py work/heavenly/feed/FR.TerrainStatusFeed_1.json
    python3 -I tools/trailmap/reports/feed_trails.py FEED.json --out tools/trailmap/resorts/<id>/report.json \\
        --key trails --source "the trail feed of <site>'s terrain page as Common Crawl captured it on <date>"

A page holds two feeds: the lift widget's, whose difficulties are numbers, and the trail widget's, with labels; either
works (numbers are turned into labels: 1 Green, 2 Blue, 3 Black, 4 DoubleBlack, 5 TerrainPark, 7 Extreme). With
--out, the rows go under --key in that JSON file (created, or that key replaced), with --source as its "_source";
without, a summary and the rows are printed. Out of season the feed lists no trails: use a capture from the season
(cc_query.sh / cc_lookup.py, then warc_to_html.py and extract_feed.py).

An mtnpowder feed's areas are its MountainAreas, and its difficulty is read from each trail's icon, not its label
(Deer Valley labels a single black diamond "Expert" and a double one "Extremely Difficult"): GreenCircle Green,
BlueSquare Blue, BlueBlueSquare DoubleBlue (advanced intermediate), BlackDiamond Black, DoubleBlackDiamond
DoubleBlack; a park icon TerrainPark.

A DOR trail list (a JSON list of trails, each with name, sector, difficulty, type and season: Mt. Bachelor's
api.mtbachelor.com/api/v1/dor/drupal/trails, which its trail report page loads) gives its winter alpine and
terrain-park trails, the sector as the area: easiest Green, more_difficult Blue, most_difficult Black, extreme
DoubleBlack, a park TerrainPark.
"""
import argparse
import collections
import json
import os

CODES = {1: 'Green', 2: 'Blue', 3: 'Black', 4: 'DoubleBlack', 5: 'TerrainPark', 7: 'Extreme'}


ICONS = {'GreenCircle': 'Green', 'BlueSquare': 'Blue', 'BlueBlueSquare': 'DoubleBlue', 'BlackDiamond': 'Black',
         'DoubleBlackDiamond': 'DoubleBlack', 'TerrainPark': 'TerrainPark'}


DOR = {'easiest': 'Green', 'more_difficult': 'Blue', 'most_difficult': 'Black', 'extreme': 'DoubleBlack'}


def rows(feed):
    out = []
    if isinstance(feed, list):  # a DOR trail list (Mt. Bachelor's api.mtbachelor.com/api/v1/dor/drupal/trails)
        for t in feed:
            if t.get('season') == 'winter' and t.get('type') in ('alpine_trail', 'terrain_park_trail'):
                rating = 'TerrainPark' if t['type'] == 'terrain_park_trail' else DOR.get(t['difficulty'], t['difficulty'])
                out.append([t['name'].strip(), t['sector']['name'].strip().title(), rating])
        return out
    if 'Resorts' in feed:  # mtnpowder
        for resort in feed['Resorts']:
            for area in resort['MountainAreas']:
                for t in area.get('Trails', []):
                    out.append([t['Name'].strip(), area['Name'].strip(), ICONS.get(t['TrailIcon'], t['TrailIcon'])])
        return out
    for area in feed['GroomingAreas']:
        for t in area['Trails']:
            d = t['Difficulty']
            out.append([t['Name'].strip(), area['Name'].strip(), CODES.get(d, str(d)) if isinstance(d, int) else d])
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('feed', help='one FR.TerrainStatusFeed object, an mtnpowder feed or a DOR trail list (JSON)')
    ap.add_argument('--out', help='report.json to write the rows into')
    ap.add_argument('--key', default='trails', help='the key the rows go under (e.g. trails_2024_25 for a past season)')
    ap.add_argument('--source', help='"_source": where and when the feed was captured')
    a = ap.parse_args()
    r = rows(json.load(open(a.feed)))
    print(f'{len(r)} trails;', dict(collections.Counter(x[1] for x in r)), dict(collections.Counter(x[2] for x in r)))
    if not a.out:
        for x in r:
            print(json.dumps(x, ensure_ascii=False))
        return
    doc = json.load(open(a.out)) if os.path.exists(a.out) else {}
    if a.source:
        doc['_source'] = a.source
    doc[a.key] = r
    json.dump(doc, open(a.out, 'w'), indent=1, ensure_ascii=False)
    open(a.out, 'a').write('\n')
    print('->', a.out)


if __name__ == '__main__':
    main()
