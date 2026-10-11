"""Telluride's trail report into report.json: every run under the lift the resort lists it by, with its level.

Out of season the resort's snow report page (tellurideskiresort.com/snow-report/) lists only some lifts' runs, so the
report is Common Crawl's in-season capture of the page its snow-report plugin renders for scraping
(/snow-report-scrape/, 2026-02-12, CC-MAIN-2026-08), which lists every lift:

    python3 -I tools/trailmap/reports/cc_lookup.py CC-MAIN-2026-08 'com,tellurideskiresort)/snow-report' \
        work/telluride/cc --fetch
    python3 -I tools/trailmap/reports/warc_to_html.py work/telluride/cc/CC-MAIN-2026-08_20260212223520.warc \
        work/telluride/cc/scrape.html
    python3 -I tools/trailmap/resorts/telluride/status_report.py work/telluride/cc/scrape.html \
        [--out tools/trailmap/resorts/telluride/report.json]

The scrape page: per lift an <h3>NAME - <img open/closed></h3> and a table, a row per run: a level icon
(dist/images/<level>.png: novice, advanced_novice, intermediate, advanced_intermediate, expert, extreme; the map's
legend: one green circle, two, one blue square, two, a diamond, two), the name, the status. A lift's hike-to terrain is its own heading. (The live page, with the same lists as
<h4> and data-level attributes, is read too, for a newer capture.) Rows: [name, lift, rating] (as the app rates them: two circles green, two squares blue; the
page's icon is printed, not kept).
"""
import argparse
import html
import json
import re

LEVELS = {'novice': 'Green', 'advanced_novice': 'Green', 'intermediate': 'Blue', 'advanced_intermediate': 'Blue',
          'expert': 'Black', 'extreme': 'DoubleBlack'}


def scrape_rows(h):
    rows, lift = [], None
    for m in re.finditer(r'<h3[^>]*>(.*?)</h3>|<tr>\s*<td[^>]*><img[^>]*images/([a-z_-]+)\.png[^>]*/?></td>\s*<td>(.*?)</td>',
                         h, re.S):
        if m.group(1) is not None:
            lift = re.sub(r'\s*-\s*$', '', html.unescape(re.sub(r'<[^>]+>', '', m.group(1))).strip()) or lift
            continue
        if m.group(2) in LEVELS:
            rows.append([html.unescape(m.group(3)).strip(), lift, LEVELS[m.group(2)], m.group(2)])
    return rows


def live_rows(h):
    h = h[h.index('>TERRAIN<'):]
    rows, lift = [], None
    for m in re.finditer(r'<h4>(.*?)(?:<span|</h4>)|<p class="tsr-report-app-trail-list-trail" data-level="([a-z-]+)"'
                         r'[^>]*>(.*?)</p>', h, re.S):
        if m.group(1) is not None:
            lift = html.unescape(m.group(1)).strip()
            continue
        spans = re.findall(r'<span>([^<]*)</span>', m.group(3))
        if spans and spans[0].strip():
            rows.append([html.unescape(spans[0]).strip(), lift, LEVELS.get(m.group(2), m.group(2)), m.group(2)])
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('page')
    ap.add_argument('--out')
    a = ap.parse_args()
    h = open(a.page, encoding='utf-8').read()
    rows = live_rows(h) if 'tsr-report-app-trail-list-trail' in h else scrape_rows(h)
    if a.out:
        json.dump({'_source': "Telluride's snow report plugin's scrape page (tellurideskiresort.com/snow-report-scrape/), "
                   'Common Crawl capture 2026-02-12 (CC-MAIN-2026-08); status_report.py', 'trails': [r[:3] for r in rows]},
                  open(a.out, 'w'), indent=0, ensure_ascii=False)
    for r in rows:
        print(r)
    print(len(rows), 'rows')


if __name__ == '__main__':
    main()
