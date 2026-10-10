"""Arapahoe Basin's trail report, from its snow report page (arapahoebasin.com/snow-report/, "Terrain & Lift
Status"), into report.json: every run under its terrain area, its lift and its zone.

    PLAYWRIGHT_PATH=$(npm root -g)/playwright node tools/trailmap/reports/fetch_page.cjs \
        https://www.arapahoebasin.com/snow-report/ work/arapahoe-basin/status 12000
    python3 -I tools/trailmap/resorts/arapahoe-basin/status_report.py work/arapahoe-basin/status/page.html \
        [--out tools/trailmap/resorts/arapahoe-basin/report.json]

The page is server-rendered: per terrain area (FRONT SIDE TERRAIN, PALLAVICINI, THE BEAVERS, MONTEZUMA BOWL, STEEP
GULLIES, EAST WALL, ...) a list of lifts, under each its zones (Lower Mountain Greens, Upper Lenawee, ...) and under
those the runs; a zone with no runs under it is a run itself. A few rows carry a difficulty icon (/img/sr/<icon>.svg:
green, blue, black, doubleblack); most carry none, so the rating column is mostly empty (the map's symbols rate the
runs). Rows: [name, area, rating or null] (the zone and lift are printed, not kept).
"""
import argparse
import html.parser
import json
import re

ICONS = {'green': 'Green', 'blue': 'Blue', 'black': 'Black', 'doubleblack': 'DoubleBlack'}


class Status(html.parser.HTMLParser):
    """The nested lists under each terrain area: (depth, text, icons) per list item."""

    def __init__(self):
        super().__init__()
        self.items, self.stack, self.area, self.in_area = [], [], None, False
        self.cur, self.box = None, 0  # (the depth of open divs inside a trail-box, 0 outside one)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = a.get('class') or ''
        if tag == 'div' and (self.box or 'trail-box' in cls.split()):
            self.box += 1
        if not self.box:
            return
        if tag == 'li':
            self.stack.append(cls)
            self.cur = {'cls': cls, 'depth': len(self.stack), 'text': '', 'icons': [], 'area': self.area}
            self.items.append(self.cur)
        elif tag == 'img' and self.cur is not None:
            m = re.match(r'/img/sr/([a-z]+)\.svg', a.get('src') or '')
            if m:
                self.cur['icons'].append(m.group(1))

    def handle_endtag(self, tag):
        if tag == 'div' and self.box:
            self.box -= 1
        if tag == 'li' and self.stack:
            self.stack.pop()
            self.cur = None

    def handle_data(self, data):
        t = ' '.join(data.split())
        if not t:
            return
        if self.pending_area(t):
            return
        if self.box and self.cur is not None and not self.cur['text']:
            self.cur['text'] = t

    def pending_area(self, t):
        if t == 'TERRAIN:' or t == 'Terrain:':
            self.in_area = True
            return True
        if self.in_area:
            self.area, self.in_area = t, False
            return True
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('page')
    ap.add_argument('--out')
    a = ap.parse_args()
    p = Status()
    p.feed(open(a.page, encoding='utf-8').read())
    rows, lift, zone = [], None, None
    items = [i for i in p.items if i['area'] and i['text']]
    for k, it in enumerate(items):
        if 'lift-opt' in it['cls']:
            lift = re.sub(r'\s*\(Lift\)$', '', it['text']).strip()
            continue
        nxt = items[k + 1] if k + 1 < len(items) else None
        if 'second-level' in it['cls']:
            zone = it['text']
            if nxt and nxt['depth'] > it['depth'] and 'lift-opt' not in nxt['cls']:
                continue  # a zone: its runs follow
        rating = next((ICONS[i] for i in it['icons'] if i in ICONS), None)
        area = ' '.join(w.capitalize() for w in it['area'].split())
        rows.append([it['text'], area, rating, zone if 'second-level' not in it['cls'] else None, lift])
    if a.out:
        json.dump({'_source': 'arapahoebasin.com/snow-report/ (Terrain & Lift Status, server-rendered), fetched '
                   '2026-10-10 out of season; status_report.py', 'trails': [r[:3] for r in rows]},
                  open(a.out, 'w'), indent=0, ensure_ascii=False)
    for r in rows:
        print(r)
    print(len(rows), 'rows')


if __name__ == '__main__':
    main()
