# Trail reports: the resort's own list of its trails

A resort's trail report (the "terrain and lift status" list on its website) names every trail with its rating and
area. It is the best check on a map's reading: names as the resort spells them (the map prints capitals and
abbreviations), the rating of each run against the symbol printed by it, the area or lift pod each belongs to, and
the runs a map leaves out or prints twice. Resorts so far took it into account in `resort.py` (`NAMES` spelled by
it, `RENAME`, `RATING`, `AREA_OF`; Smugglers' Notch, Whistler Blackcomb, Park City, Palisades Tahoe, Big Sky,
Heavenly; Keystone's `REPORT_NAMES`), and Big Sky, Heavenly, Keystone and Deer Valley keep it as
`tools/trailmap/resorts/<id>/report.json` (`_source`, then rows of `[name, area, rating]`). It isn't the truth
about the map: where the two differ, the map's printed symbol is kept unless the map is ambiguous (two symbols),
and each difference is listed in the resort's header.

Where to find it, by the platform the resort's site uses:

## Vail Resorts' sites (Park City, Heavenly, Whistler Blackcomb, Vail, Breckenridge, Keystone, ...)

The terrain-and-lift-status page (`/the-mountain/mountain-conditions/terrain-and-lift-status.aspx`) embeds the
data as `FR.TerrainStatusFeed = {...}`, twice: the lift widget's copy (difficulties as numbers) and the trail
widget's (labels: Green, Blue, Black, DoubleBlack, Extreme, TerrainPark). The sites refuse curl, so render the page
in headless Chromium:

```bash
PLAYWRIGHT_PATH=$(npm root -g)/playwright node tools/trailmap/reports/fetch_page.cjs \
  https://www.parkcitymountain.com/the-mountain/mountain-conditions/terrain-and-lift-status.aspx work/park-city/terrain
python3 -I tools/trailmap/reports/extract_feed.py work/park-city/terrain/page.html work/park-city/feed
python3 -I tools/trailmap/reports/feed_trails.py work/park-city/feed/<the trail widget's feed>.json
```

Out of season the feed lists no trails. Use a capture from the season in Common Crawl instead:

```bash
# which crawls captured the page (the index server, with retries; it is often slow)
tools/trailmap/reports/cc_query.sh 'www.skiheavenly.com/the-mountain/mountain-conditions/terrain-and-lift-status.aspx*' \
  work/heavenly/cdx.jsonl CC-MAIN-2026-04 CC-MAIN-2025-51 CC-MAIN-2024-51
# or without the index server: a binary search of the crawl's cluster.idx, then the WARC records (--fetch)
python3 -I tools/trailmap/reports/cc_lookup.py CC-MAIN-2026-04 \
  'com,skiheavenly)/the-mountain/mountain-conditions/terrain-and-lift-status.aspx' work/heavenly/cc --fetch
python3 -I tools/trailmap/reports/warc_to_html.py work/heavenly/cc/<record>.warc work/heavenly/cc/page.html
python3 -I tools/trailmap/reports/extract_feed.py work/heavenly/cc/page.html work/heavenly/cc/feeds
python3 -I tools/trailmap/reports/feed_trails.py work/heavenly/cc/feeds/<feed>.json \
  --out tools/trailmap/resorts/heavenly/report.json --key trails --source "..."
```

Keystone's `report.json` is one such capture (2025-11-18, CC-MAIN-2025-47: CC-MAIN-2026-04 has none, and the index
server didn't answer for CC-MAIN-2025-51 or CC-MAIN-2026-08). Heavenly's `report.json` is two such captures
(2026-01-12, CC-MAIN-2026-04, as `trails`; 2024-12-13, CC-MAIN-2024-51, the season its map was drawn for, as
`trails_2024_25`); `feed_trails.py` rebuilds both lists exactly from them. Park City's names and ratings were
checked against a March 2026 capture. Whistler Blackcomb's against its terrain feed, together with the resort's own
GIS layer of runs (ArcGIS, `Ski_Runs_GDB`: names, ratings and run lines; the scripts that read it are in
`tools/archive/whistler-blackcomb/`).

## mtnfeed / mtnpowder (Palisades Tahoe, and many independent resorts)

The site's conditions widget loads its config from `https://v4.mtnfeed.com/resorts/<slug>.json` (the slug and
URL appear in the site's scripts), which gives the resort's id and a bearer token for the feed itself:

```bash
curl -sS -o work/palisades-tahoe/cfg.json https://v4.mtnfeed.com/resorts/palisades-tahoe.json
TOKEN=$(python3 -c "import json; print(json.load(open('work/palisades-tahoe/cfg.json'))['bearerToken'])")
curl -sS -o work/palisades-tahoe/feed.json "https://mtnpowder.com/feed/v3.json?bearer_token=$TOKEN&resortId%5B%5D=61"
```

Every trail with its rating and lift area (Palisades Tahoe's id is 61, in the config). `feed_trails.py` reads such a
feed into `report.json` rows (its areas are the feed's MountainAreas; the rating is read from each trail's icon, as
labels differ by resort: Deer Valley calls a single diamond "Expert"). Deer Valley's (`deer-valley.json`, resort 49)
was fetched out of season, every trail "closed for season": the season's list all the same.

## Big Sky

The site's own scripts call `https://www.bigskyresort.com/api/reportpal?resortName=bs&useReportPal=true`
(`true` exactly, or nothing comes back): every trail with its lift area and rating (beginner, intermediate,
advanced intermediate, advanced, expert, high exposure). `tools/trailmap/resorts/big-sky/report.json` keeps name,
area and rating as of 2026-09-24.

## Smugglers' Notch

`https://www.smuggs.com/conditions/winter-report/` lists every trail with its rating and mountain (rendered by the
page; read it in headless Chromium, as above, out of the page text).

## Files here

| file | what it does |
|---|---|
| `fetch_page.cjs` | Renders a page in headless Chromium through the agent proxy; saves the HTML, its text, every JSON-ish response and the list of requests |
| `extract_feed.py` | Every `X = {json}` assignment of a TerrainStatusFeed-like variable in a page, one JSON file each |
| `feed_trails.py` | One FR.TerrainStatusFeed → report rows `[name, area, rating]`, printed or written into a `report.json` |
| `cc_query.sh` | Common Crawl's CDX index: the captures of a URL pattern in the given crawls (retries) |
| `cc_lookup.py` | The same without the index server (binary search of `cluster.idx` with range requests); `--fetch` downloads the WARC records |
| `warc_to_html.py` | One WARC response record → the page's HTML as served |
| `compare.py` | A resort's `trails.ts` against its `report.json`: runs only one of them lists, ratings that differ, names spelled otherwise |
