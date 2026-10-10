# My Ski Runs

A web app for keeping track of the trails you ski, on each resort's own trail map: every trail is a clickable
overlay on the map, with its name and rating, so you tap the run you just skied and it's logged on your trip. It
works offline on the mountain, installs to a phone's home screen, and can sync your trips between devices with an
optional account. Live at **[www.myskiruns.app](https://www.myskiruns.app)**.

Thirty-eight resorts so far, 5,599 trails: Killington, Stowe, Okemo, Sugarbush, Jay Peak, Smugglers' Notch,
Whiteface, Hunter Mountain, Wildcat Mountain, Sunday River, Sugarloaf, Vail, Beaver Creek, Breckenridge, Keystone,
Arapahoe Basin, Copper Mountain, Winter Park, Steamboat, Snowmass, Aspen Mountain, Buttermilk, Park City, Deer
Valley, Snowbasin, Alta, Snowbird, Big Sky, Whitefish Mountain, Jackson Hole, Schweitzer, Palisades Tahoe, Northstar,
Heavenly, Mammoth Mountain, Big Bear, Mt. Bachelor and Whistler Blackcomb.

Most of the work in this repository is the **trail-map pipeline**: getting every trail's overlay onto its own
drawn line, with the right name, on maps that were never made to be machine-read. How it is done, resort by
resort, is in **[docs/trail-map-playbook.md](docs/trail-map-playbook.md)**: start there to add a resort or to
update one for a new season (its Part 1 has the first hour's triage and a recipe for each type of map).

**Contents:** [Quick start](#quick-start) · [Using the app](#using-the-app) · [Resorts](#resorts) ·
[How a map gets its overlays](#how-a-map-gets-its-overlays) · [Repository layout](#repository-layout) ·
[Scripts and checks](#scripts-and-checks) · [How the app works](#how-the-app-works) · [Accounts](#accounts) ·
[Trail conditions](#trail-conditions) · [Deploying](#deploying) · [Marketing](#marketing) · [History](#history) ·
[What's left](#whats-left)

## Quick start

```bash
npm install
npm run dev                    # http://localhost:5173 (serves /api/conditions from memory)
npm run build                  # typecheck + production build into dist/
npm test                       # the trip merge and sync rules, the resort search (tests/)
npx tsc -b && npx eslint .     # before every commit
```

The pipeline tools are Python 3 (`pip install pymupdf pillow numpy opencv-python-headless scikit-image scipy
fonttools`) and Node; the browser checks use Playwright (in the Claude Code sandbox:
`PLAYWRIGHT_PATH=$(npm root -g)/playwright`). `CLAUDE.md` has the rules every change follows.

## Using the app

- **Resorts.** Pick a resort with the button in the header: a search over the names, states and other places (it
  finds Heavenly by "nevada" or "lake tahoe"), grouped by state before you type. `?resort=<id>` in the URL opens
  one; the app remembers the last one on the device. Some maps come in several panels (Vail's Front Side, Back
  Bowls and Blue Sky Basin; Big Sky's main map and two insets), with a switcher on the map (`?panel=<id>`);
  picking a trail in the list opens the panel it is drawn on.
- **Trips.** What you ski is logged per trip ("Presidents Day weekend"). Start or pick a trip in the header and
  mark a trail skied from the map or with its check box in the list; with no trip yet, the first mark starts one
  for today. The stats show this trip and all trips; trails skied on an earlier trip are drawn dashed.
- **On the map:** drag to pan, pinch or scroll to zoom (the corners button shows the whole map). A tap opens a sheet
  listing every trail within a finger's width, nearest first, each with a big "Skied it" button, so junctions are
  never guessed; a toast offers Undo. Searching the list and tapping a name zooms the map to that trail.
- **Trail conditions (👍 / 👎).** In a trail's sheet, rate today's conditions and pick up to three tags (groomed,
  powder, moguls, icy, ...); votes are shared with everyone for 24 hours, and the list opens with "Good conditions
  today". No account is involved: each device sends a random id, one vote per trail.
- **Trip summary:** trails skied, new trails, days, the difficulty mix, progress by area and a day-by-day log;
  "Share summary" uses the phone's share sheet.
- **Offline and on the home screen.** A service worker caches the app with every resort's trail data, and each
  map once it has been shown, so the app opens without signal; "Add to Home Screen" installs it.
- **Your data stays on the device** (`localStorage`), with Export / Import backup in the ⋯ menu. **With an account**
  (optional: email and a one-time code, no password) your trips are backed up and kept in step on every device;
  changes made offline or on two devices merge rather than overwrite.

## Resorts

| resort | region | trails (lines + markers) | map | source and route | rebuild |
|---|---|---|---|---|---|
| Killington | Vermont | 135 (113 + 22) | 1 | flattened raster PDF; line detector, readers, a person's review | `npm run trails:apply -- --resort killington` ([history](docs/killington.md)) |
| Stowe | Vermont | 125 (114 + 11) | 1 | PDF strokes, outlined names; readers, a person's review | `npm run trails:apply -- --resort stowe` |
| Okemo | Vermont | 128 (124 + 4) | 1 | PDF strokes, outlined names; readers, trace pass, a person's review of 23 | `tools/trailmap/resorts/okemo/regen.sh` |
| Sugarbush | Vermont | 138 (111 + 27) | 1 | PDF strokes, outlined labels; readers | `tools/trailmap/resorts/sugarbush/regen.sh` |
| Jay Peak | Vermont | 88 (65 + 23) | 1 | a painting with no lines, names as text; trace pass | `tools/trailmap/resorts/jay-peak/regen.sh` |
| Smugglers' Notch | Vermont | 82 (68 + 14) | 1 | PDF strokes, outlined names on label boxes | `tools/trailmap/resorts/smugglers-notch/regen.sh` |
| Whiteface | New York | 98 (95 + 3) | 1 | PDF strokes and text (skimap.org) | `tools/trailmap/resorts/whiteface/regen.sh` |
| Hunter Mountain | New York | 70 (66 + 4) | 1 | PDF strokes and text over a vector painting | `tools/trailmap/resorts/hunter/regen.sh` |
| Wildcat Mountain | New Hampshire | 48 (47 + 1) | 1 | an older export's strokes and text on this season's image | `tools/trailmap/resorts/wildcat/regen.sh` |
| Sunday River | Maine | 137 (116 + 21) | 1 | PDF strokes, outlined names, insets | `tools/trailmap/resorts/sunday-river/regen.sh` |
| Sugarloaf | Maine | 175 (127 + 48) | 1 | PDF strokes, outlined names, numbered key circles, a raster inset | `tools/trailmap/resorts/sugarloaf/regen.sh` |
| Vail | Colorado | 194 (173 + 21) | 3 | three raster paintings (no PDF); raster line detection | `tools/trailmap/resorts/vail/regen.sh` |
| Beaver Creek | Colorado | 168 (148 + 20) | 1 | this season's map an image only; the 2023 export's strokes and outlined names registered on it, each run's symbol on its line | `tools/trailmap/resorts/beaver-creek/regen.sh` |
| Breckenridge | Colorado | 197 (157 + 40) | 1 | PDF strokes and text over a sharper CDN painting | `tools/trailmap/resorts/breckenridge/regen.sh` |
| Keystone | Colorado | 145 (120 + 25) | 1 | PDF strokes, outlined names, CDN painting | `tools/trailmap/resorts/keystone/regen.sh` |
| Arapahoe Basin | Colorado | 148 (122 + 26) | 2 | one PDF of two paintings (the Frontside, Zuma Bowl): strokes and outlined names; the runs with no line along their printed names | `tools/trailmap/resorts/arapahoe-basin/regen.sh` |
| Copper Mountain | Colorado | 128 (104 + 24) | 1 | PDF lines and names both as filled outlines | `tools/trailmap/resorts/copper-mountain/regen.sh` |
| Winter Park | Colorado | 172 (114 + 58) | 1 | PDF strokes, text with no Unicode map | `tools/trailmap/resorts/winter-park/regen.sh` |
| Steamboat | Colorado | 189 (144 + 45) | 1 | the map as an image; its interactive map's SVG as the vector layer, routed onto the print's lines | `tools/trailmap/resorts/steamboat/regen.sh` |
| Snowmass | Colorado | 124 (114 + 10) | 2 | PDF strokes and filled casings, names as text on pills in the run's colour | `tools/trailmap/resorts/snowmass/regen.sh` |
| Aspen Mountain | Colorado | 129 (121 + 8) | 3 | Snowmass's kind: PDF strokes and casings, names on pills in the run's colour; no trail report | `tools/trailmap/resorts/aspen-mountain/regen.sh` |
| Buttermilk | Colorado | 44 (43 + 1) | 1 | PDF strokes, names as text on pills in the run's colour (Snowmass's kind) | `tools/trailmap/resorts/buttermilk/regen.sh` |
| Park City Mountain | Utah | 345 (252 + 93) | 1 | PDF strokes, outlined names, a redrawn inset | `tools/trailmap/resorts/park-city/regen.sh` |
| Deer Valley | Utah | 207 (181 + 26) | 1 | an earlier export's strokes and outlined names on this season's flattened image; checked against the interactive map | `tools/trailmap/resorts/deer-valley/regen.sh` |
| Snowbasin | Utah | 125 (119 + 6) | 1 | PDF strokes (a few as filled outlines) and text over a painting | `tools/trailmap/resorts/snowbasin/regen.sh` |
| Alta | Utah | 116 (81 + 35) | 1 | PDF strokes, outlined names, rounded symbols; the faces and chutes printed with no line are markers | `tools/trailmap/resorts/alta/regen.sh` |
| Snowbird | Utah | 180 (155 + 25) | 1 | one image (its PDF the same image): the map read on crops, each line routed along the painted one | `tools/trailmap/resorts/snowbird/regen.sh` |
| Big Sky | Montana | 323 (290 + 33) | 3 | three PDFs of strokes and text | `tools/trailmap/resorts/big-sky/regen.sh` |
| Whitefish Mountain | Montana | 113 (76 + 37) | 3 | three small web JPEGs, no PDF: the map read on crops, each line routed along the painted one | `tools/trailmap/resorts/whitefish/regen.sh` |
| Jackson Hole | Wyoming | 142 (108 + 34) | 1 | one image, no PDF, thin lines blending into the snow: the map read on crops, each line routed along the painted one | `tools/trailmap/resorts/jackson-hole/regen.sh` |
| Schweitzer | Idaho | 103 (96 + 7) | 2 | two images, no PDF, runs painted with no line: each run's overlay along its printed name, the names and symbols from the interactive maps, the cat tracks routed on their navy lines | `tools/trailmap/resorts/schweitzer/regen.sh` |
| Palisades Tahoe | California | 247 (124 + 123) | 3 | three PDFs of strokes and outlined names | `tools/trailmap/resorts/palisades-tahoe/regen.sh` |
| Northstar | California | 99 (83 + 16) | 1 | PDF lines as filled outlines, one for the runs that meet (cut at each junction), white names haloed in the line's colour | `tools/trailmap/resorts/northstar/regen.sh` |
| Heavenly | California (and Nevada) | 120 (73 + 47) | 2 | the current map as an image; an older PDF of the artwork registered on it | `tools/trailmap/resorts/heavenly/regen.sh` |
| Mammoth Mountain | California | 182 (175 + 7) | 2 | a PDF with names as text and no trail lines; its interactive maps' SVGs as the lines | `tools/trailmap/resorts/mammoth/regen.sh` |
| Big Bear | California | 93 (91 + 2) | 3 | three images, no PDF (Snow Summit, Bear Mountain, Snow Valley): Snow Summit's print's own lines; the other two paint runs with no line, their interactive maps' lines and stretches along the printed names | `tools/trailmap/resorts/big-bear/regen.sh` |
| Mt. Bachelor | Oregon | 110 (72 + 38) | 1 | PDF lines and names both as filled outlines over a painting | `tools/trailmap/resorts/mt-bachelor/regen.sh` |
| Whistler Blackcomb | British Columbia | 232 (209 + 23) | 3 | one PDF read as a main map and two insets | `tools/trailmap/resorts/whistler-blackcomb/regen.sh` |

"Lines" are trails drawn on their own line (or along their printed name, where the map draws no line), "markers"
are trails with no line (bowls, glades, chutes, parks) shown as a clickable marker at their name. `IMAGES=1` before
a `regen.sh` also rewrites the resort's map image; every `regen.sh` downloads its sources into `work/<id>/`
(git-ignored) and rebuilds the resort's committed files byte for byte. Killington and Stowe were built before the
pipelines were kept: their proposals and a person's reviews are the record, and `trails:apply` rebuilds their
overlays from them. The playbook's [Part 3](docs/trail-map-playbook.md#part-3-resort-by-resort) has each resort's source, scripts and
quirks.

Each resort's files:
- `src/data/resorts/<id>/`: `trails.ts` (the trail list: id, name, rating, area, glade flag), and per map
  `linePolylines.json` (the line pieces), `trailProposals.json` (each piece's name), `trailReviews.json` (decisions
  that override proposals: a person's, or Claude's marked `"by": "claude"`) and `trailPaths.json` (what the app
  draws, generated by `npm run trails:apply`; never edited by hand). A map in several panels keeps these in
  `panels/<panel>/`.
- `public/maps/<id>.jpg` (or `<id>-<panel>.jpg`): the map image the overlays are drawn on (in percent of it).
- An entry in `src/resorts.ts`: name, state or province, other places the search finds it by, its panels.
- `tools/trailmap/resorts/<id>/`: how it was built (`regen.sh`, the map's reading, the decisions settled on crops),
  with a README listing its commands and files.
- An ad group in `marketing/google-ads/build.mjs` (the build stops without one).

## How a map gets its overlays

Every map is different, and the hard part is never the drawing: it's naming. A trail's overlay must lie on that
trail's own drawn line along its whole length and show that trail's name anywhere along it, and the map prints
names beside lines, in gaps of lines, on label boxes, on numbered keys, or not at all. Fully automatic name-to-line
assignment got about 40% right on Killington. What works:

1. **Take the most the source gives you.** A resort's PDF often has the trail lines as vector strokes and the names
   as text or outlined glyphs; then the geometry and the names are exact (`extract_pdf_vectors.py`,
   `pdf_labels.py`, `pdf_glyphs.py`). With only images, lines are detected from the paint (`raster_lines.py`).
2. **Match each name to the line it is printed along or at the end of**, automatically where the map is
   unambiguous (`pdf_resort.py`), and settle the rest by looking at zoomed crops, recording every decision as a
   point on the map with the crop that settled it. On maps where names can't be extracted, parallel AI readers
   name numbered pieces on tiles.
3. **Check against the resort's own data**: its trail report (names, ratings, areas), its GIS where published, and
   OpenStreetMap's runs for which line a run follows.
4. **Audit every overlay on crops**, one cell per trail, check every printed symbol against its trail, and hover
   every trail in the real app. Pixel scores are never evidence; a test that hovers on the assigned path is
   circular.

The playbook has the routes, the tools, the checks and every resort's specifics.

## Repository layout

```
src/                     the app (React 19 + TypeScript + Vite)
  resorts.ts             the resort registry: one entry per resort, each loaded on demand
  data/resorts/<id>/     each resort's trail list and overlays (above)
  components/            ImageMap (the map, overlays, tap sheet), TrailList, TripBar, StatsPanel, TripSummary,
                         ResortPicker, FilterBar, Account
  trips/                 trips on the device (store.ts), the merge rules (log.ts), the account sync (sync.ts)
  account/ hooks/        sign-in and session; trips, filters, conditions
  resortSearch.ts        the picker's search; offline.ts: when to start the service worker
  detection/             Killington's original line detector's ground truth (docs/killington.md)
public/                  the map images (maps/), the service worker (sw.js), icons, manifest
api/                     Vercel functions: conditions votes (conditions.ts), account deletion (account.ts)
supabase/migrations/     the accounts table
tests/                   npm test: trip merge and sync, resort search
scripts/                 Node pipeline scripts: trails:apply, reviews:import, Killington's detector and OCR
tools/
  trailmap/              the trail-map pipeline (Python and Node): extraction, matching, checks
    resorts/<id>/        each resort's rebuild: regen.sh, its map's reading, its decisions
    reports/             fetching resorts' trail reports (terrain feeds, Common Crawl)
    prompts/ runs/       the AI readers' prompts and example arguments (.claude/workflows/ runs them)
    review/              the Trail Check review page
  archive/               every one-off script written along the way, indexed (not maintained)
  *.cjs                  browser checks of the app and a Vercel-like static server
docs/                    the playbook; Killington's history
marketing/google-ads/    the Google Ads campaign (generated)
work/                    git-ignored: downloads and intermediate files of the pipelines
```

## Scripts and checks

| command | what it does |
|---|---|
| `npm run dev` / `build` / `preview` | the app: dev server, production build, a local preview of the build |
| `npm test` | the trip merge and sync rules (random three-device histories) and the resort search |
| `npm run lint` | ESLint (with `npx tsc -b`, the check before every commit) |
| `npm run trails:apply -- --resort <id> [--panel <p>]` | proposals + reviews → `trailPaths.json`, the overlays the app draws |
| `npm run reviews:import -- <export dir> --resort <id>` | the Trail Check page's export → `trailReviews.json` |
| `npm run ads:build` | the Google Ads import files from `marketing/google-ads/build.mjs` |
| `npm run lines:eval` / `lines:overlay` / `lines:png` | Killington's line detector: score, overlay, the app's line image |
| `tools/trailmap/resorts/<id>/regen.sh` | rebuild one resort from its sources and decisions (`IMAGES=1`: its map image too; `FORCE=1`: on a source whose SHA-256 has changed, a new edition) |
| `tools/trailmap/regen_all.sh` | rebuild every resort and list what git sees changed: after changing a shared tool |
| `tools/trailmap/hover_all.sh [<id>[:<panel>] ...]` | build the app, serve it, hover every trail of every resort and panel |
| `python3 tools/trailmap/overlay_audit.py --resort <id> --out <dir>` | one audit cell per trail: its overlay on the map, its labels boxed |
| `node tools/app_check.cjs <url> --resort <id>` | a resort in the real app: found by the search, every panel loads with overlays, phone layout |
| `node tools/app_flows.cjs [dist]` | phone flows (tap, mark, undo, summary, panels), two tabs, backups |
| `node tools/offline_check.cjs [dist]` | offline: first visit, reload without the server, a deploy, the load-error screen |
| `node tools/accounts_check.cjs` | accounts: two devices sign in, sync, edit offline, delete (with `scripts/mockSupabase.cjs`) |
| `python3 tools/check_doc_paths.py` | every repo path the docs mention exists (after moving or renaming a script) |
| `node tools/serve_dist.cjs dist 4199` | serve a build the way Vercel serves it (cache headers, ETags; `THROTTLE_MBPS`, `RTT_MS`) |

Every pipeline tool (extraction, glyph reading, matching, audits, OpenStreetMap, trail reports, source finding) is
listed in the playbook's [Part 2](docs/trail-map-playbook.md#part-2-tools), with what it's for.

## How the app works

- **Resorts load on demand.** `src/resorts.ts` lists every resort with loaders for its trail list and overlays;
  each resort's data is its own chunk, so a visit downloads the resorts it opens. A resort with several map panels
  has one trail list and one overlay file per panel; a trail's area decides the panel it opens on.
- **The map** (`src/components/ImageMap/`) draws the overlays as SVG over the map image, in percent of the image,
  at a constant on-screen width. A tap or hover names the nearest trail to the pointer (the same test the hover
  check uses), and the sheet lists every trail within a finger's width.
- **Trips** are a log of events merged, never overwritten (`src/trips/log.ts`): a trip's name and date come from the
  copy edited last, a run is kept if it was marked after it was last unmarked, and deletions stay as markers so they
  reach other devices. The merge is commutative, associative and idempotent; `npm test` checks it on random
  histories of three devices.
- **Offline:** `public/sw.js` precaches the app and every resort's data (the list is filled in by `vite build`,
  `vite.config.ts`), caches each map when it's shown (every panel of a resort once it's opened), and on a deploy
  swaps its cache while keeping the maps a phone already has. It installs only once the first map is on screen, so
  its background downloads don't compete with that map.
- **Accounts** (optional) sync the trip log to one Supabase row per person with a version check
  (`src/trips/sync.ts`); **conditions votes** go to `api/conditions.ts` (Redis). Locally, `vite` and `vite preview`
  serve both APIs: conditions from memory, accounts against the Supabase project in `.env.local`.

## Accounts

Accounts are optional: with no Supabase variables set, the app works as before, with no sign-in shown. Sign-in is
Supabase Auth's one-time email code (no passwords), sent through Resend; the trips live in one Supabase table.

1. **A Supabase project.** A new one keeps this app's users and email wording separate. Free projects pause after
   a week without use (the app keeps working on the device; sign-in and sync resume once the project is restored).
2. **The table.** In the SQL editor, run [`supabase/migrations/001_trip_logs.sql`](supabase/migrations/001_trip_logs.sql):
   one row per person (`trips`, a JSON list, and a `version`), readable and writable only by that person (row-level
   security), deleted with them.
3. **Email codes.** Authentication → Sign In / Providers → Email: on, new sign-ups allowed. Authentication → Emails →
   Templates: put the code, `{{ .Token }}`, in both "Magic Link" and "Confirm signup" (a first sign-in uses the
   second), e.g. *Your My Ski Runs sign-in code is {{ .Token }}.* The code is what works in the home-screen app; a
   link, if a template keeps one, signs in the browser it opens in (Authentication → URL Configuration → Site URL:
   the app's address).
4. **Resend as the mail server.** Authentication → Emails → SMTP settings: host `smtp.resend.com`, port `465`, user
   `resend`, password a Resend API key, sender an address on a domain verified in Resend (Supabase's own mailer
   allows only a couple of emails an hour).
5. **Vercel environment variables** (Project Settings → Environment Variables; from Supabase → Project Settings →
   API keys), then redeploy. `VITE_` values are built into the app; the service key stays on the server:

   | variable | value |
   |---|---|
   | `VITE_SUPABASE_URL` | the project URL |
   | `VITE_SUPABASE_ANON_KEY` | the anon (publishable) key |
   | `SUPABASE_SERVICE_ROLE_KEY` | the service_role (secret) key, used only by `api/account.ts` to delete an account |

   Vercel's Supabase integration sets `NEXT_PUBLIC_SUPABASE_URL` / `NEXT_PUBLIC_SUPABASE_ANON_KEY` /
   `SUPABASE_SERVICE_ROLE_KEY` instead, which work too. `.env.example` lists them for local runs (`.env.local`).

Without a Supabase project, `scripts/mockSupabase.cjs` stands in for one, and `tools/accounts_check.cjs` drives
two devices through sign-in, sync, offline edits and deletion (its header has the commands).

## Trail conditions

The 👍/👎 votes and tags are shared through `api/conditions.ts`, a Vercel function backed by a Redis hash per
resort: add Upstash Redis from the Vercel Marketplace and connect it to the project (it sets `KV_REST_API_URL` and
`KV_REST_API_TOKEN`; `UPSTASH_REDIS_REST_URL` / `_TOKEN` work too). Until then the endpoint answers 503 and the app
keeps votes on the device (the sheet says so). Votes count for 24 hours; each device sends a random id.

## Deploying

Vercel builds the app (`npm run build`) on every push and serves `dist/` with `api/*.ts` as functions; pushes to
`main` go to production (www.myskiruns.app). `api/` runs as Node ESM (`"type": "module"`), so its relative imports
need explicit `.js` extensions, or every request fails with a 500; `npx vercel build` reports a missing one as
TS2835. Environment variables: the accounts' and the conditions store's, above. Nothing else to do for a new
resort: the service worker's precache list and version are filled in by the build. Push `main` on its own and check
that a Production deployment came for the commit (`gh api 'repos/nighthawk6389/myskiruns/deployments?sha=<sha>'`
lists each with its environment) before pushing the same commit to other branches: Arapahoe Basin's commit, pushed
to `main` and two branches within a second, got two Preview deployments and no Production one, so the site stayed
on the commit before until the next push to `main`.

## Marketing

`marketing/google-ads/` is a Google Search campaign ready to import into Google Ads Editor (everything imports
paused): an ad group per resort plus general run-tracker searches. `npm run ads:build` generates it from
`build.mjs`, where each resort has an entry (names, keywords, negatives); its README has the plan.

## History

The app started on Killington's flattened raster map, where a line detector (97% F1 on line pixels) and OCR
still put only about 40% of trails on the right line. Reading numbered tiles with AI readers and a person's review
fixed that, and from the fourth resort on, the resorts' own PDFs gave exact lines and names. The detector, the OCR,
the audits and the attempts on other branches are in [docs/killington.md](docs/killington.md); the lessons are in
the playbook's [Part 5](docs/trail-map-playbook.md#part-5-what-we-tried-and-what-it-taught-us).

## What's left

1. **A person's confirmation** for the thirty-five resorts Claude checked on crops instead of the review page
   (Sugarbush through Arapahoe Basin), if wanted: the Trail Check page can be published for any resort ([playbook,
   Part 4](docs/trail-map-playbook.md#auditing-on-crops-or-the-human-review-page)).
2. **Shared tooling:** a legend file per map feeding the extraction and the readers' prompts; readers run from a
   script instead of an interactive session ([playbook, Part 5](docs/trail-map-playbook.md#scaling-to-many-maps)).
3. The hover check passes 15,297 of 15,306 points (2026-10-10). The nine misses are points where two trails'
   overlays meet or share a stretch, where either name is right: Killington 2, Stowe 2, Beaver Creek 2, Big Sky's
   Bowl 1, Heavenly 1, Mt. Bachelor 1 (each resort's numbers are in the playbook's Part 3).
4. Whiteface, Winter Park, Breckenridge, Copper Mountain and Keystone key their decisions by piece id, valid for
   their exact source file (the rebuild checks its SHA-256); Winter Park's and Copper Mountain's sites now serve
   re-exports with other ids. Moving them onto `pdf_resort.py` would key them by points.
5. **Areas:** Keystone, Breckenridge, Copper Mountain, Winter Park and Sunday River list every trail under one area
   for the whole map. Where a trail report groups the runs by mountain or peak (Keystone's `report.json`: Bergman,
   Dercum Mountain, North Peak, Outback), those groups would make the areas, as they do for the later resorts.
6. Vail: Cookshack's second diamond has no line of its own (its overlay is the line it is printed beside).
7. Killington's detector edge cases (3 false negatives, 1 false positive) are in `src/detection/LINES.md`.
