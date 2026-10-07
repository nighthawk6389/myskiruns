# Google Ads campaign

A Google Search campaign for www.myskiruns.app, ready to import into Google
Ads Editor. It has three campaigns, 23 ad groups (one per resort, plus five
for people looking for a way to track their runs), 249 keywords and 488
negative keywords. Each ad group has a responsive search ad, and each
campaign has sitelinks, callouts and a structured snippet. Everything imports
**paused**: nothing runs or costs anything until you enable it.

| file | what |
|---|---|
| [`preview.md`](preview.md) | every ad, keyword and asset, for reading |
| `editor/1-campaigns.csv` … `editor/9-structured-snippets.csv` | the import files, in import order |
| [`build.mjs`](build.mjs) | makes all of the above (`npm run ads:build`); the ad text, keywords and settings live here |

## The plan

### Who the ads are for

| campaign | ad groups | typical search | where the ad goes |
|---|---|---|---|
| **Trail Maps - East** | Killington, Stowe, Okemo, Sugarbush, Jay Peak, Smugglers' Notch, Whiteface, Hunter Mountain, Wildcat Mountain, Sunday River, Sugarloaf | "stowe trail map" | that resort's map: `?resort=stowe` |
| **Trail Maps - West** | Vail, Breckenridge, Keystone, Copper Mountain, Winter Park, Park City Mountain, Whistler Blackcomb | "whistler piste map" | `?resort=whistler-blackcomb` |
| **Ski Run Tracker** | Ski Run Tracker, Ski Trail Checklist, Ski Trip Log, Interactive Trail Maps, Brand | "app to track ski runs" | the home page |

Most of the budget goes to **resort trail-map searches**, where the site has
its best match. Someone searching "vail trail map" wants the map. The ad takes
them to that map, with every run clickable and a count of what they've skied.
Each resort's ad uses the resort's name, its run count and its own terrain
("Back Bowls & Blue Sky Basin", "Mt. Mansfield & Spruce Peak").

The **tracker** campaign competes with GPS apps such as Slopes, so its ads
say plainly that the app works differently: "No GPS, Just Tap the Map". That
way people who want automatic tracking don't click. Searches about GPS,
watches, speed or other apps by name are blocked with negative keywords.

### Keywords and negatives

- **Phrase and exact match only.** Broad match needs conversion data to work
  well, and there isn't any yet.
- Each resort has "trail map", "ski map", "ski trails", "trail list" and
  "run map" searches, plus the names people use for it ("breck", "smuggs",
  "canyons village", "whistler piste map").
- **Ambiguous names** appear on their own only in exact searches ("keystone
  trail map") or next to "ski" ("keystone ski map"). Otherwise they appear
  only in longer forms ("keystone resort trail map"). They are:
  - Keystone, also a town in South Dakota;
  - Park City, also a summer trail network;
  - Winter Park, also a city in Florida;
  - Sugarloaf, also a mountain in Maryland.

  Negatives block the other meanings ("south dakota", "deer valley",
  "florida", "maryland").
- **Campaign negatives** block what people usually want with a resort's name
  besides the winter map: summer trails and bike parks, lodging, lift
  tickets and passes, weather, webcams, snow reports, jobs, trail-map
  posters and other merchandise, and news.

### The ads

Each ad group has one responsive search ad: 15 headlines and 4 descriptions,
which Google mixes and matches. Two headlines are pinned to position 1, so
the first thing people read is always their own search: "Vail Trail Map" or
"Interactive Vail Trail Map". One way the Vail ad can show:

> Sponsored · myskiruns.app/Vail/Trail-Map
> **Vail Trail Map | 194 Vail Runs to Check Off | Works Offline on the Mountain**
> Tap any of the 194 runs on the Vail trail map to mark it skied. See what's left. A free,
> independent web app. No app download or sign-up, and it works offline once opened.
> Vail Back Bowls Map · Blue Sky Basin Map · Breckenridge Trail Map · Park City Mountain Map

Every claim matches what the app does today:

- It's free, with no app to install and no sign-up.
- It works offline once a resort has been opened.
- Conditions are rated by skiers.
- Trip recaps can be shared.

The ads don't mention syncing between devices, because accounts aren't
switched on in production yet. Once they are, add a "Syncs Across Devices"
callout. Run counts come from each resort's `trails.ts`.

### Settings

`1-campaigns.csv` and `2-locations.csv` set these values. The rows marked
"by hand" have no CSV column, so set them in Editor before posting.

| setting | Trail Maps - East | Trail Maps - West | Ski Run Tracker |
|---|---|---|---|
| type, networks | Search; Google Search only (no Search Partners, no Display Network) | same | same |
| locations | United States, Canada | same | same |
| location option (by hand) | Presence or interest (the default) | same; brings in trip planners from abroad, e.g. the UK and Australia for Whistler | **Presence**: people in the US or Canada |
| languages | English, French (Quebec skiers) | English | English |
| budget | $5/day | $5/day | $5/day |
| bidding | Maximize clicks, max CPC $1.00 | same | Maximize clicks, max CPC $1.50 |
| final URL suffix | `utm_source=google&utm_medium=cpc&utm_campaign=trail-maps-east` | `…trail-maps-west` | `…ski-run-tracker` |
| EU political ads (by hand) | No | No | No |
| AI Max, automatically created assets, broad match (by hand) | Off | Off | Off |

AI Max and automatically created assets let Google write its own headlines
and choose its own landing pages. Leave them off so no ad promises GPS
tracking or sends someone to the wrong resort. Also go to **Recommendations →
Auto-apply** and turn all of them off. Otherwise Google may add broad-match
keywords or change the bidding without asking.

### Budget and season (2026-27)

| dates | what | budget |
|---|---|---|
| now to Nov 12 | deploy this branch's landing-page changes (below); verify the advertiser; import everything (paused) | $0 |
| Fri Nov 13 to Dec 17 | launch as resorts open; learn which resorts and searches work | $15/day ($5 per campaign) |
| Dec 18 to Mar 14 | peak: Christmas to New Year, MLK weekend (Jan 16-18), Presidents' Day week (Feb 13-21), Quebec's spring break (early March) | up to $30/day if click-through rate holds (move the extra to whichever campaign shows "Limited by budget") |
| Mar 15 to Apr 18 | spring; pause each resort's ad group when the resort closes | $15/day |
| late April | pause all three campaigns until next season | $0 |

That's at most about $3,660 for the season with the peak increase, or about
$2,355 at a flat $15/day. Maximize clicks spends less when there are fewer
searches. Google can spend up to twice the daily budget on a busy day, but
never more than 30.4 days' worth in a month. Automated rules (**Tools →
Rules**) can change the budgets on these dates for you.

## Launch checklist

1. **Merge and deploy this branch's landing-page changes.** Ad visitors used to
   see "Killington Trail Tracker" in the browser tab whatever the resort, and
   nothing on the page said who made the app. Now:
   - each resort sets its own tab title ("Vail Trail Map · My Ski Runs");
   - the home page has a title and description, and the installed app's name
     is My Ski Runs;
   - the map shows "My Ski Runs is an independent app, not affiliated with
     Vail". That supports Google's rules for informational sites that use a
     trademark (the resort's name) in ad text.

   Then check that www.myskiruns.app serves the new build.
2. **Create the Google Ads account** (ads.google.com). If it pushes you into
   its guided "Smart" or Performance Max setup, choose to create the account
   without a campaign, or switch to Expert mode. Add billing. Complete
   **advertiser verification** when Google asks. It sets a deadline, and ads
   stop if it's missed.
3. **Import** the files (next section) and post them. Everything stays
   paused.
4. **Wait for ad review** (usually about a business day). Fix anything shown
   as disapproved or limited (Policy notes, below).
5. **Enable the three campaigns** on launch day.
6. Optional: add **business name and logo** assets ("My Ski Runs" and
   `public/icon-512.png`) once the advertiser is verified.

## Importing with Google Ads Editor

Google Ads Editor is Google's free desktop app for bulk changes
(ads.google.com/home/tools/ads-editor). The files use the column names it
recognizes.

1. Open Editor, sign in, and download the account.
2. Go to **Account → Import → From file…** and pick `editor/1-campaigns.csv`.
   Editor previews the rows. If it shows a column it didn't recognize, choose
   the matching field in the preview's column list. Accept the changes.
3. Import the other files in order, 2 to 9. Locations and ad groups attach
   to the campaigns from file 1, so keep the campaign names as they are.
4. Check each campaign in the edit panel: Search type, **Google Search only**
   (untick Display Network if it's ticked), budget, Maximize clicks with its
   CPC limit, locations, languages, and the "by hand" settings above.
5. Click **Check changes**, fix anything it flags, then **Post**.

To change something later, edit `build.mjs`, run `npm run ads:build`, and
import the changed files again. Editor adds what's new, but it never deletes
anything, so remove dropped keywords, callouts and sitelinks in Editor. An
ad can't be edited in place, either: a changed ad imports as a new one
alongside the old, so remove the old ad.

## After launch

- **Daily for the first week, then weekly: Search terms report** (Insights
  and reports → Search terms). Add anything off-topic as a negative keyword.
  Expect hiking and summer searches, town maps and lift-ticket searches at
  first. Add campaign negatives to `TRAIL_MAP_NEGATIVES` or
  `TRACKER_NEGATIVES` in `build.mjs` too, so the next build keeps them.
- **Click-through rate.** For searches this specific, 5% or more is healthy.
  Under 2% means the ad doesn't match what people want: check the search
  terms first, then the headlines.
- **Budget between campaigns.** If one campaign is "Limited by budget" and
  has a good click-through rate, move budget to it from a weaker one.
- **Asset report** (Ads → Assets), after two to four weeks: replace
  headlines rated "Low" with new ones in `build.mjs`.
- **Search lost impression share (rank)** is high and the click-through
  rate is good: raise the max CPC limit by about $0.25.

### Measuring results

Maximize clicks needs no conversion tracking, so the campaign can launch
without it. You will see clicks, click-through rate and cost per click, but
not what visitors do once they're on the site. Adding a Google Ads tag
would show that, counting:

- the first run marked (the main conversion);
- installs to the home screen;
- shared trip recaps.

Once you have about 30 conversions a month, switch to Maximize conversions.
The tag needs your Google Ads conversion ID and a short privacy note on the
site. The app could load it only when an environment variable is set, the way
accounts work today. Until then, the final URL suffix tags every ad visit
with `utm_source=google`, so a privacy-friendly analytics tool such as Vercel
Web Analytics can tell ad visits from organic ones.

## Policy notes

- **Resort names are trademarks.** Bidding on them as keywords is allowed.
  Using them in ad text is allowed for informational sites (Google's
  trademark policy). That's why the landing page says the app is
  independent, and the ads never say "official".
  - A resort that has filed a trademark complaint with Google can still get
    its ads marked "Eligible (limited)" or disapproved.
  - If that happens, ask Google for a review as an informational site. If
    that's refused, replace that ad group's resort-name headlines with
    generic ones, such as "Interactive Ski Trail Map".
- **"App Store" is Apple's trademark**, so the ads say "No App to Download".
- **Keep every final URL on www.myskiruns.app.** The bare myskiruns.app
  redirects there, and a myskiruns.vercel.app URL would show a different
  domain in the ad.
- **The trail maps are the resorts' artwork.** Paid ads make the site more
  visible, so keep the independent-app line on the map.

## Changing the campaign

Everything comes from `build.mjs`:

- `CAMPAIGNS`: budgets, CPC limits, languages.
- `RESORT_ADS`: each resort's short name, terrain headline, keyword names
  and negatives.
- The shared headlines and descriptions.
- `TRACKER_GROUPS`: the tracker campaign's ad groups.
- The negative lists and the assets.

Run counts and the resort list come from the app (`src/resorts.ts`,
`src/data/resorts/<id>/trails.ts`). A resort added to the app without an
entry in `RESORT_ADS` stops the build, which names it. Add the entry, run
`npm run ads:build`, and import the files again (Importing, above). The run
totals in the callouts and the tracker ads change too.

Not included, and worth considering later:

- **A campaign on competitors' names** (Slopes, Ski Tracks). It's allowed
  in the US and Canada as keywords but not in ad text, and those ads usually
  get a low click-through rate.
- **Image assets** from app screenshots, once the account qualifies.
- **Display, YouTube and Performance Max.** Not worth it at this budget:
  they spend mostly outside search.
