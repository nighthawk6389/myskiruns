// Run with `npm test`. The resorts' landing pages (scripts/landingPages.ts).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { indexPage, pagePath, resortPage, robots, sitemap, type LandingResort } from '../scripts/landingPages.ts';

const stowe: LandingResort = {
  id: 'stowe',
  name: 'Stowe',
  region: 'Vermont',
  peaks: [
    { id: 'mansfield', name: 'Mount Mansfield', elevation: 4395 },
    { id: 'spruce', name: 'Spruce Peak', elevation: 3390 },
    { id: 'empty', name: 'No Runs Here', elevation: 1000 },
  ],
  trails: [
    { id: 'nose-dive', name: 'Nose Dive', difficulty: 'black', peak: 'mansfield' },
    { id: 'gondolier', name: 'Gondolier', difficulty: 'blue', peak: 'mansfield' },
    { id: 'toll-road', name: 'Toll Road', difficulty: 'green', peak: 'mansfield' },
    { id: 'birch-glades', name: 'Birch <Glades> & "Co"', difficulty: 'black', peak: 'spruce', isGlade: true },
  ],
  panels: [{ id: 'map', name: 'Trail map' }],
};
const smuggs: LandingResort = { ...stowe, id: 'smugglers-notch', name: "Smugglers' Notch", trails: stowe.trails.slice(0, 1) };

test("a resort's page: title, description, canonical, its runs by area linking into the app", () => {
  const html = resortPage(stowe, [stowe, smuggs]);
  assert.match(html, /<title>Stowe Trail Map: All 4 Runs \| My Ski Runs<\/title>/);
  assert.match(html, /<meta name="description" content="Stowe&#39;s trail map with all 4 runs: 1 green, 1 blue and 2 black, across Mount Mansfield, Spruce Peak\./);
  assert.match(html, /<link rel="canonical" href="https:\/\/www.myskiruns.app\/stowe-trail-map\/" \/>/);
  assert.match(html, /<a href="\/\?resort=stowe&trail=nose-dive">/);
  assert.ok(html.includes('Birch &lt;Glades&gt; &amp; &quot;Co&quot;'), 'names are escaped');
  assert.ok(!html.includes('<Glades>'));
  assert.ok(!html.includes('No Runs Here'), 'an area with no runs is left out');
  assert.ok(html.indexOf('Toll Road') < html.indexOf('Nose Dive'), 'easiest first within an area');
  assert.ok(html.includes(`href="${pagePath('smugglers-notch')}"`), 'links to the other resorts');
  assert.ok(!html.includes(`href="${pagePath('stowe')}">Stowe trail map`), 'but not to itself');
  const ld = [...html.matchAll(/<script type="application\/ld\+json">(.*?)<\/script>/g)].map((m) => JSON.parse(m[1]));
  assert.equal(ld[0]['@type'], 'SkiResort');
  assert.equal(ld[1]['@type'], 'BreadcrumbList');
});

test('the index, the sitemap and robots.txt list every resort page', () => {
  const html = indexPage([stowe, smuggs]);
  assert.match(html, /<title>Ski Trail Maps for 2 Resorts \| My Ski Runs<\/title>/);
  assert.ok(html.includes('Smugglers&#39; Notch trail map'));
  const xml = sitemap([stowe, smuggs], '2026-10-12');
  assert.equal((xml.match(/<loc>/g) ?? []).length, 4);
  assert.ok(xml.includes('<loc>https://www.myskiruns.app/smugglers-notch-trail-map/</loc>'));
  assert.match(robots(), /Sitemap: https:\/\/www.myskiruns.app\/sitemap.xml/);
  assert.match(robots(), /Allow: \/api\/og\nDisallow: \/api\//);
});
