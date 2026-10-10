# Trail reports: the resort's own list of its trails

A resort's trail report (the "terrain and lift status" list on its website) names every trail with its rating and
area. It is the best check on a map's reading: names as the resort spells them (the map prints capitals and
abbreviations), the rating of each run against the symbol printed by it, the area or lift pod each belongs to, and
the runs a map leaves out or prints twice. Resorts so far took it into account in `resort.py` (`NAMES` spelled by
it, `RENAME`, `RATING`, `AREA_OF`; Smugglers' Notch, Whistler Blackcomb, Park City, Palisades Tahoe, Big Sky,
Heavenly; Keystone's `REPORT_NAMES`), and Big Sky, Heavenly, Keystone, Deer Valley, Mt. Bachelor, Steamboat, Mammoth,
Snowmass, Buttermilk, Snowbasin, Whitefish, Northstar, Schweitzer, Alta, Beaver Creek, Big Bear, Jackson Hole, Snowbird and Arapahoe Basin keep it as `tools/trailmap/resorts/<id>/report.json` (`_source`, then rows of `[name, area, rating]`). It isn't the truth
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

Northstar's `report.json` is the trail widget's feed (the page's second `FR.TerrainStatusFeed`, `feed_04`) in
Common Crawl's capture of 2026-02-19 (CC-MAIN-2026-08, the page without `.aspx`; CC-MAIN-2025-47, -2025-51 and
-2026-04 have none): 103 rows, Lookout Bypass under both Northwest Territory and Lookout Mountain, the terrain parks
as their own area (`resorts/northstar/README.md` has the commands).

Beaver Creek's `report.json` is the trail widget's feed (`feed_04`) in Common Crawl's capture of 2026-02-07
(CC-MAIN-2026-08, `cc_lookup.py` on `com,beavercreek)/the-mountain/mountain-conditions/terrain-and-lift-status`; the
index found none in CC-MAIN-2026-04): 183 rows, the homeowner skiways (Resort Skiways) and McCoy Park among them.

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
was fetched out of season, every trail "closed for season": the season's list all the same. So was Steamboat's
(`steamboat.json`, resort 6), whose advanced-intermediate icon is BlueBlackSquare (a blue square and a black
diamond: blue in the app), and Mammoth's (`mammoth.json`, resort 60), whose uphill routes (UphillArrow), adventure
zones (PurpleStar) and halfpipes (Halfpipe) are icons of their own (`feed_trails.py` keeps them as they are).

Schweitzer's (`schweitzer.json`, resort 168) was fetched out of season too (2026-10-10): its Schweitzer Bowl and
Outback Bowl runs, and the cross-country trails (left out: no run of the alpine maps).

Big Bear Mountain Resort's (mtnfeed path `big-bear-mountain`, resorts 57, 58 and 173: Bear Mountain, Snow Summit,
Snow Valley, all three in one request) was fetched out of season (2026-10-10): 93 rows, each mountain an area, its
two pipes as rows with a Halfpipe icon of their own.

## Jackson Hole

Its grooming and mountain report pages (jacksonhole.com/grooming-report, a Nuxt site) load one feed,
`https://jacksonhole-prod.zaneray.com/api/all.json` (plain curl; `fetch_page.cjs` found it): snow, weather, lifts and
every winter run (`trails`: name, trailLevel GREEN_CIRCLE, BLUE_SQUARE, DOUBLE_BLUE_SQUARE, BLACK_DIAMOND,
DOUBLE_BLACK_DIAMOND, TERRAIN_PARKS), listed out of season too, with no area.
`tools/trailmap/resorts/jackson-hole/report_feed.py` reads it into `report.json` (145 rows on 2026-10-10; the double
blue square as DoubleBlue).

## Big Sky

The site's own scripts call `https://www.bigskyresort.com/api/reportpal?resortName=bs&useReportPal=true`
(`true` exactly, or nothing comes back): every trail with its lift area and rating (beginner, intermediate,
advanced intermediate, advanced, expert, high exposure). `tools/trailmap/resorts/big-sky/report.json` keeps name,
area and rating as of 2026-09-24.

## Aspen Snowmass

Its grooming report page loads `https://www.aspensnowmass.com/AspenSnowmass/GroomingReport/Feed?mountain=Snowmass`
(plain curl; `mountain=` also takes the other three mountains): every trail by lift area (`areas`, each with its
`trails`), with its difficulty (beginner, intermediate, advanced, expert, extreme, terrain-park), listed out of
season too. `feed_trails.py` reads it (beginner Green, intermediate Blue, advanced Black, expert DoubleBlack, extreme
Extreme, terrain-park TerrainPark); Snowmass's `report.json` was fetched on 2026-10-09, Buttermilk's
(`mountain=Buttermilk`) on 2026-10-10. Their uphill routes are an area of their own (Uphill Routes), left out of the
trail list. Out of season the feed for Aspen Mountain (`mountain=AspenMountain`, its page's id) lists no trails.

```bash
mkdir -p work/snowmass/report
curl -sS -o work/snowmass/report/feed.json \
  'https://www.aspensnowmass.com/AspenSnowmass/GroomingReport/Feed?mountain=Snowmass'
python3 -I tools/trailmap/reports/feed_trails.py work/snowmass/report/feed.json --source "..." \
  --out tools/trailmap/resorts/snowmass/report.json
```

## Mt. Bachelor

The lift and trail report page (`mtbachelor.com/the-mountain/lift-trail-report/`) loads its DOR trail list from
`https://api.mtbachelor.com/api/v1/dor/drupal/trails` (plain curl; `/lifts` the lifts): every trail of every season,
with its sector and rating (easiest, more difficult, most difficult, extreme). `feed_trails.py` reads such a list
(the winter alpine and terrain-park trails; its sectors are the areas), as in `resorts/mt-bachelor/README.md`.

Snowbird's lift and trail report page loads the same kind of list from
`https://api.snowbird.com/api/v1/dor/drupal/trails` (plain curl): 175 winter runs on 2026-10-10, out of season, by
sector (Gad Valley, Peruvian Gulch, Mineral Basin).

## Snowbasin

The mountain report page (`https://www.snowbasin.com/the-mountain/mountain-report/`, plain curl) holds the trail
tables in its HTML: one per lift area (Strawberry, Needles, Porcupine, John Paul), then the access gates and the
terrain parks, each row a difficulty icon (easy, moderate, difficult, most-difficult, terrain-park), a name and a
status. Out of season it lists the summer trails, so Snowbasin's `report.json` is Common Crawl's capture of
2026-01-21 (CC-MAIN-2026-04), read by `resorts/snowbasin/mountain_report.py` (the gates left out):

```bash
python3 -I tools/trailmap/reports/cc_lookup.py CC-MAIN-2026-04 'com,snowbasin)/the-mountain/mountain-report' \
  work/snowbasin/cc --fetch
python3 -I tools/trailmap/reports/warc_to_html.py work/snowbasin/cc/CC-MAIN-2026-04_20260121160328.warc \
  work/snowbasin/cc/page.html
python3 -I tools/trailmap/resorts/snowbasin/mountain_report.py work/snowbasin/cc/page.html --source "..." \
  --out tools/trailmap/resorts/snowbasin/report.json
```

## Whitefish Mountain

`https://skiwhitefish.com/snowreport/` (plain curl) lists every run under its lift, each with its difficulty icon
(an inline SVG: a circle, a square, one diamond or two) and status, out of season too (all closed).
`resorts/whitefish/snow_report.py` reads it into `report.json` (fetched 2026-10-10).

## Alta

`https://www.alta.com/lift-terrain-status` (plain curl) sets `window.Alta = {...}` in the page: every lift with its runs
(name, difficulty, status), out of season too (all closed). A run under two lifts is listed under each.
`resorts/alta/status_report.py` reads it into `report.json` (fetched 2026-10-10; the Nordic track left out by
`resort.py`).

## Arapahoe Basin

Its snow report page (arapahoebasin.com/snow-report/, "Terrain & Lift Status") is server-rendered: per terrain area
its lifts, under each the zones and under those the runs, with an open/closed icon each and a difficulty icon on only a
handful. `fetch_page.cjs` saves it (`page.html`); `tools/trailmap/resorts/arapahoe-basin/status_report.py` reads the
lists into `report.json` (151 rows on 2026-10-10, out of season: every run listed, closed; the area as the report's
terrain area, the rating mostly null). The carpet and the uphill-access rows are no runs (`resort.py` leaves them out).

## Smugglers' Notch

`https://www.smuggs.com/conditions/winter-report/` lists every trail with its rating and mountain (rendered by the
page; read it in headless Chromium, as above, out of the page text).

## Files here

| file | what it does |
|---|---|
| `fetch_page.cjs` | Renders a page in headless Chromium through the agent proxy; saves the HTML, its text, every JSON-ish response and the list of requests |
| `extract_feed.py` | Every `X = {json}` assignment of a TerrainStatusFeed-like variable in a page, one JSON file each |
| `feed_trails.py` | One FR.TerrainStatusFeed, mtnpowder feed or DOR trail list → report rows `[name, area, rating]`, printed or written into a `report.json` |
| `cc_query.sh` | Common Crawl's CDX index: the captures of a URL pattern in the given crawls (retries) |
| `cc_lookup.py` | The same without the index server (binary search of `cluster.idx` with range requests); `--fetch` downloads the WARC records |
| `warc_to_html.py` | One WARC response record → the page's HTML as served |
| `compare.py` | A resort's `trails.ts` against its `report.json`: runs only one of them lists, ratings that differ, names spelled otherwise |
