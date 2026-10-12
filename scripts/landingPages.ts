// The resorts' landing pages, built with the app (vite.config.ts) as plain HTML
// that search engines read without running the app:
//   /<id>-trail-map/   one per resort: its map, its runs by area with their
//                      ratings, each linking into the app on that run
//   /trail-maps/       every resort, by state or province
//   /sitemap.xml, /robots.txt
// People searching "<resort> trail map" land on a page about that resort, with
// a way into the interactive map. tests/landingPages.test.ts checks them.

export const SITE = 'https://www.myskiruns.app';
const ORDER = ['green', 'blue', 'black', 'double-black'] as const;
const LABEL: Record<string, string> = { green: 'Easy', blue: 'Intermediate', black: 'Advanced', 'double-black': 'Expert' };
const PLURAL: Record<string, string> = { green: 'green', blue: 'blue', black: 'black', 'double-black': 'double black' };
const ICON: Record<string, string> = { green: '●', blue: '■', black: '◆', 'double-black': '◆◆' };
const COLOUR: Record<string, string> = { green: '#22c55e', blue: '#3b82f6', black: '#e5e7eb', 'double-black': '#ef4444' };

export interface LandingResort {
  id: string;
  name: string;
  region: string;
  peaks: { id: string; name: string; elevation: number }[];
  trails: { id: string; name: string; difficulty: string; peak: string; isGlade?: boolean; isTerrainPark?: boolean }[];
  panels: { id: string; name: string }[];
}

export const pagePath = (id: string) => `/${id}-trail-map/`;
const appLink = (id: string, trail?: string) => `/?resort=${encodeURIComponent(id)}${trail ? `&trail=${encodeURIComponent(trail)}` : ''}`;

export const esc = (s: string) =>
  s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;');

const feet = (n: number) => `${n.toLocaleString('en-US')}'`;

function counts(r: LandingResort) {
  const c = Object.fromEntries(ORDER.map((d) => [d, r.trails.filter((t) => t.difficulty === d).length])) as Record<string, number>;
  return ORDER.filter((d) => c[d]).map((d) => ({ d, n: c[d] }));
}

/** "125 runs: 17 green, 63 blue, 30 black and 15 double black" */
function runsSentence(r: LandingResort): string {
  const parts = counts(r).map(({ d, n }) => `${n} ${PLURAL[d]}`);
  const list = parts.length > 1 ? `${parts.slice(0, -1).join(', ')} and ${parts.at(-1)}` : parts[0];
  return `${r.trails.length} runs${list ? `: ${list}` : ''}`;
}

const regionsOf = (all: LandingResort[]) => {
  const by = new Map<string, LandingResort[]>();
  for (const r of all) by.set(r.region, [...(by.get(r.region) ?? []), r]);
  return [...by.entries()].sort((a, b) => a[0].localeCompare(b[0])).map(([region, rs]) => ({ region, resorts: rs.sort((a, b) => a.name.localeCompare(b.name)) }));
};

const STYLE = `
:root{color-scheme:dark;--bg:#0f172a;--panel:#1e293b;--line:#334155;--text:#f1f5f9;--muted:#94a3b8;--gold:#fbbf24}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:16px/1.5 -apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif}
a{color:inherit}header,main,footer{max-width:1040px;margin:0 auto;padding:0 16px}
header{display:flex;align-items:center;justify-content:space-between;gap:12px;padding-top:14px;padding-bottom:14px}
.brand{color:var(--gold);font-weight:800;text-decoration:none;letter-spacing:.02em}
.cta{display:inline-block;padding:12px 18px;border-radius:10px;background:var(--gold);color:#1e1b0f;font-weight:700;text-decoration:none}
h1{font-size:clamp(28px,5vw,44px);line-height:1.1;margin:12px 0 6px}h2{font-size:22px;margin:32px 0 10px}h3{font-size:17px;margin:20px 0 6px}
.lede{color:var(--muted);font-size:18px;margin:0 0 18px}
.map{display:block;border-radius:14px;overflow:hidden;border:1px solid var(--line);margin:18px 0}.map img{display:block;width:100%;height:auto}
.stats{display:flex;flex-wrap:wrap;gap:8px;margin:14px 0}.stat{background:var(--panel);border-radius:10px;padding:8px 12px;font-weight:600}
.stat b{font-size:20px;margin-right:4px}
ul.runs{list-style:none;padding:0;margin:0;columns:3 220px;column-gap:24px}ul.runs li{break-inside:avoid;padding:3px 0}
ul.runs a{text-decoration:none}ul.runs a:hover{text-decoration:underline}.i{display:inline-block;width:26px;font-size:13px}
.tag{color:var(--muted);font-size:13px}.area{color:var(--muted);font-weight:400;font-size:15px}
.how{background:var(--panel);border-radius:14px;padding:4px 18px 12px;margin:28px 0}
.others{columns:3 200px;column-gap:24px}.others p{break-inside:avoid;margin:0 0 12px}.others a{display:block;text-decoration:none;color:var(--muted)}
.others a:hover{color:var(--text)}.others strong{display:block}
footer{color:var(--muted);font-size:13px;padding-top:24px;padding-bottom:32px;border-top:1px solid var(--line);margin-top:40px}
`;

function shell(o: { title: string; description: string; path: string; image: string; body: string; jsonLd: unknown[] }): string {
  const url = `${SITE}${o.path}`;
  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>${esc(o.title)}</title>
<meta name="description" content="${esc(o.description)}" />
<link rel="canonical" href="${esc(url)}" />
<meta name="theme-color" content="#0f172a" />
<link rel="icon" type="image/png" href="/icon-192.png" />
<link rel="apple-touch-icon" href="/icon-192.png" />
<meta property="og:type" content="website" />
<meta property="og:site_name" content="My Ski Runs" />
<meta property="og:title" content="${esc(o.title)}" />
<meta property="og:description" content="${esc(o.description)}" />
<meta property="og:url" content="${esc(url)}" />
<meta property="og:image" content="${esc(o.image)}" />
<meta property="og:image:width" content="1200" />
<meta property="og:image:height" content="630" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:image" content="${esc(o.image)}" />
${o.jsonLd.map((j) => `<script type="application/ld+json">${JSON.stringify(j).replace(/</g, '\\u003c')}</script>`).join('\n')}
<style>${STYLE}</style>
</head>
<body>
<header><a class="brand" href="/">⛷ MY SKI RUNS</a><a href="/trail-maps/">All trail maps</a></header>
${o.body}
<footer><p>My Ski Runs is an independent app, not affiliated with any resort. Trail maps are the resorts' own; runs and ratings as each map prints them.</p><p><a href="/">Open the app</a> · <a href="/trail-maps/">All trail maps</a></p></footer>
</body>
</html>
`;
}

function othersList(all: LandingResort[], except?: string): string {
  return `<div class="others">${regionsOf(all)
    .map(
      ({ region, resorts }) =>
        `<p><strong>${esc(region)}</strong>${resorts
          .filter((r) => r.id !== except)
          .map((r) => `<a href="${pagePath(r.id)}">${esc(r.name)} trail map</a>`)
          .join('')}</p>`,
    )
    .join('')}</div>`;
}

/** The page for one resort. */
export function resortPage(r: LandingResort, all: LandingResort[]): string {
  const peaks = r.peaks.filter((p) => r.trails.some((t) => t.peak === p.id));
  const top = Math.max(0, ...r.peaks.map((p) => p.elevation || 0));
  const areas = peaks.map((p) => p.name);
  const image = `${SITE}/api/og?resort=${encodeURIComponent(r.id)}`;
  const title = `${r.name} Trail Map: All ${r.trails.length} Runs | My Ski Runs`;
  const description =
    `${r.name}'s trail map with all ${runsSentence(r)}` +
    (areas.length > 1 ? `, across ${areas.slice(0, 4).join(', ')}${areas.length > 4 ? ' and more' : ''}` : '') +
    `. Tap the runs you ski, trip by trip, and see what's left. Free, works offline.`;
  const sections = peaks
    .map((p) => {
      const runs = r.trails
        .filter((t) => t.peak === p.id)
        .sort((a, b) => ORDER.indexOf(a.difficulty as (typeof ORDER)[number]) - ORDER.indexOf(b.difficulty as (typeof ORDER)[number]) || a.name.localeCompare(b.name));
      return `<h3>${esc(p.name)} <span class="area">· ${runs.length} run${runs.length === 1 ? '' : 's'}${p.elevation ? ` · ${feet(p.elevation)}` : ''}</span></h3>
<ul class="runs">${runs
        .map(
          (t) =>
            `<li><a href="${appLink(r.id, t.id)}"><span class="i" style="color:${COLOUR[t.difficulty] ?? '#94a3b8'}" title="${LABEL[t.difficulty] ?? ''}">${ICON[t.difficulty] ?? '·'}</span>${esc(t.name)}</a>${t.isGlade ? ' <span class="tag">glade</span>' : t.isTerrainPark ? ' <span class="tag">park</span>' : ''}</li>`,
        )
        .join('')}</ul>`;
    })
    .join('\n');
  const body = `<main>
<h1>${esc(r.name)} Trail Map</h1>
<p class="lede">${esc(r.region)} · ${esc(runsSentence(r))}${top ? ` · top elevation ${feet(top)}` : ''}${r.panels.length > 1 ? ` · ${r.panels.length} maps: ${esc(r.panels.map((p) => p.name).join(', '))}` : ''}</p>
<a class="cta" href="${appLink(r.id)}">Open the interactive ${esc(r.name)} map</a>
<a class="map" href="${appLink(r.id)}"><img src="/api/og?resort=${encodeURIComponent(r.id)}" width="1200" height="630" alt="${esc(r.name)} trail map" /></a>
<div class="stats">${counts(r)
    .map(({ d, n }) => `<span class="stat"><span style="color:${COLOUR[d]}">${ICON[d]}</span> <b>${n}</b>${LABEL[d]}</span>`)
    .join('')}</div>
<h2>Every run at ${esc(r.name)}</h2>
${sections}
<div class="how">
<h2>Track your ${esc(r.name)} runs</h2>
<p>Open the map, tap a run when you finish it, and it's marked for the day. See which runs you've never skied, your difficulty mix, and a recap of each trip to share. Rate today's conditions on any run and see what other skiers say. Free, no app to download, and it works offline on the mountain once opened.</p>
<p><a class="cta" href="${appLink(r.id)}">Start tracking at ${esc(r.name)}</a></p>
</div>
<h2>More trail maps</h2>
${othersList(all, r.id)}
</main>`;
  const jsonLd = [
    {
      '@context': 'https://schema.org',
      '@type': 'SkiResort',
      name: r.name,
      address: { '@type': 'PostalAddress', addressRegion: r.region },
      hasMap: `${SITE}${pagePath(r.id)}`,
      image,
    },
    {
      '@context': 'https://schema.org',
      '@type': 'BreadcrumbList',
      itemListElement: [
        { '@type': 'ListItem', position: 1, name: 'Trail maps', item: `${SITE}/trail-maps/` },
        { '@type': 'ListItem', position: 2, name: `${r.name} trail map`, item: `${SITE}${pagePath(r.id)}` },
      ],
    },
  ];
  return shell({ title, description, path: pagePath(r.id), image, body, jsonLd });
}

/** The page listing every resort. */
export function indexPage(all: LandingResort[]): string {
  const runs = all.reduce((n, r) => n + r.trails.length, 0);
  const title = `Ski Trail Maps for ${all.length} Resorts | My Ski Runs`;
  const description = `Interactive trail maps for ${all.length} ski resorts and ${runs.toLocaleString('en-US')} runs in the US and Canada: tap the runs you ski, trip by trip, and see what's left. Free, works offline.`;
  const body = `<main>
<h1>Ski trail maps</h1>
<p class="lede">${all.length} resorts, ${runs.toLocaleString('en-US')} runs, each on the resort's own trail map.</p>
<a class="cta" href="/">Open the app</a>
<h2>By state and province</h2>
${othersList(all)}
</main>`;
  return shell({ title, description, path: '/trail-maps/', image: `${SITE}/og/default.jpg`, body, jsonLd: [] });
}

export function sitemap(all: LandingResort[], lastmod: string): string {
  const urls = ['/', '/trail-maps/', ...all.map((r) => pagePath(r.id))];
  return `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${urls.map((u) => `  <url><loc>${SITE}${u}</loc><lastmod>${lastmod}</lastmod></url>`).join('\n')}
</urlset>
`;
}

export function robots(): string {
  return `User-agent: *
Allow: /
Allow: /api/og
Disallow: /api/

Sitemap: ${SITE}/sitemap.xml
`;
}
