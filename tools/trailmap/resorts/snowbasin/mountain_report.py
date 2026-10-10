"""Snowbasin's trail report: the trail tables of snowbasin.com's mountain report page, as report.json.

    python3 -I tools/trailmap/resorts/snowbasin/mountain_report.py work/snowbasin/cc/page.html \\
        --source "..." --out tools/trailmap/resorts/snowbasin/report.json

The page (https://www.snowbasin.com/the-mountain/mountain-report/) is served whole, its tables in the HTML: one
table per lift area (Strawberry, Needles, Porcupine, John Paul), then the access gates and the terrain parks. Each
row is a trail's difficulty icon (mc__icon-easy, -moderate, -difficult, -most-difficult, -terrain-park), its name,
and its status. Out of season it lists the summer trails, so the winter list comes from a capture in Common Crawl
(the reports README, "Snowbasin"). The gates are left out (they are gates, not runs); the parks keep their table as
their area. Rows: [name, area, rating], ratings as feed_trails.py writes them (Green, Blue, Black, DoubleBlack,
TerrainPark).
"""
import argparse
import html
import json
import re

RATING = {'easy': 'Green', 'moderate': 'Blue', 'difficult': 'Black', 'most-difficult': 'DoubleBlack',
          'terrain-park': 'TerrainPark'}
SKIP = {'Access Gates'}


def rows(page):
    h = page[page.index('<div class="mc-trails">'):]
    out, area = [], None
    for m in re.finditer(r'<h3 class="accordion__heading">(.*?)</h3>|<tr>(.*?)</tr>', h, re.S):
        if m.group(1) is not None:
            area = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', m.group(1))).replace('Toggle accordion', '').strip()
            continue
        names = re.findall(r'<td class="mc__table-cell">\s*<span class="mc__icon mc__icon-([a-z-]+)"></span>\s*'
                           r'<span>\s*([^<]*?)\s*</span>', m.group(2))
        if area is None or area in SKIP or not names:
            continue
        icon, name = names[0]
        if icon in RATING:
            out.append([html.unescape(name), area, RATING[icon]])
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('page')
    ap.add_argument('--source', required=True)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    trails = rows(open(a.page, encoding='utf-8', errors='replace').read())
    json.dump({'_source': a.source, 'trails': trails}, open(a.out, 'w'), indent=1, ensure_ascii=False)
    open(a.out, 'a').write('\n')
    by = {}
    for _n, area, _r in trails:
        by[area] = by.get(area, 0) + 1
    print(f'{len(trails)} trails {by} -> {a.out}')


if __name__ == '__main__':
    main()
