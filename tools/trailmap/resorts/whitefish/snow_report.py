"""Whitefish Mountain Resort's trail report: the run lists of skiwhitefish.com's snow report page, as report.json.

    curl -sSL -A 'Mozilla/5.0' -o work/whitefish/report/snowreport.html https://skiwhitefish.com/snowreport/
    python3 -I tools/trailmap/resorts/whitefish/snow_report.py work/whitefish/report/snowreport.html \\
        --source "..." --out tools/trailmap/resorts/whitefish/report.json

The page (plain curl) lists every run under its lift (`wmr-lift-section`, its name in `wmr-accordion-header`), each
row its difficulty icon (an inline SVG: a circle, a square, one diamond or two), its name and its status; out of
season every run is listed, closed. Rows: [name, lift, rating], ratings as feed_trails.py writes them (Green, Blue,
Black, DoubleBlack). The terrain parks' section keeps its rows as runs of the parks' lift heading.
"""
import argparse
import html
import json
import re

RATING = {'circle': 'Green', 'square': 'Blue', 'diamond': 'Black', 'double': 'DoubleBlack'}


def icon(svg):
    if '<circle' in svg:
        return 'circle'
    if '<rect' in svg:
        return 'square'
    return {1: 'diamond', 2: 'double'}.get(svg.count('<path'))


def rows(page):
    out = []
    for sec in re.split(r'<div class="wmr-lift-section">', page)[1:]:
        lift = re.search(r'wmr-accordion-header"><span>(.*?)</span>', sec)
        lift = html.unescape(lift.group(1)).strip() if lift else None
        for r in re.findall(r'<div class="wmr-run-row">(.*?)</div></div>', sec, re.S):
            name = re.search(r'wmr-col-name"><p[^>]*>(.*?)</p>', r)
            kind = icon(r)
            if name and kind:
                out.append([html.unescape(name.group(1)).strip(), lift, RATING[kind]])
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
    for _n, lift, _r in trails:
        by[lift] = by.get(lift, 0) + 1
    print(f'{len(trails)} runs {by} -> {a.out}')


if __name__ == '__main__':
    main()
