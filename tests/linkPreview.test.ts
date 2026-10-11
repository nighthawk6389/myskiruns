// Run with `npm test`. Link previews (api/_lib/preview.ts): a shared day's or a
// resort's title and tags, escaped, and the picture's crop kept on the map.
// api/ imports with .js extensions (as Vercel runs it), so the module is
// bundled with esbuild first.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { build } from 'esbuild';
import { encodeRecap } from '../src/recap/link.ts';

const out = join(mkdtempSync(join(tmpdir(), 'preview-')), 'preview.mjs');
await build({ entryPoints: [new URL('../api/_lib/preview.ts', import.meta.url).pathname], bundle: true, platform: 'node', format: 'esm', outfile: out, logLevel: 'warning' });
const p = await import(out);

const resort = {
  id: 'stowe',
  name: 'Stowe',
  region: 'Vermont',
  trails: { 'nose-dive': 'black', 'gondolier': 'blue', 'toll-road': 'green' },
  panels: [
    { id: 'map', name: 'Trail map', map: '/maps/stowe.jpg', paths: { 'nose-dive': { segments: [[[40, 20], [45, 40]]] }, 'gondolier': { segments: [[[50, 30], [55, 50]]] } } },
  ],
};
const page = `<html><head>
    <meta name="description" content="the app" />
    <title>My Ski Runs</title>
    <!-- link preview -->
    <meta property="og:title" content="default" />
    <!-- /link preview -->
  </head><body></body></html>`;

test("a shared day's page names the day, escaped, and drops the default tags", () => {
  const payload = encodeRecap({ name: 'Powder day <b>"&"</b>', start: '2026-02-14', days: 1, newCount: 1, trailIds: ['nose-dive', 'gondolier'] });
  const recap = p.recapOf(resort, payload);
  assert.deepEqual([...recap.trailIds].sort(), ['gondolier', 'nose-dive']);
  const m = p.metaFor('https://www.myskiruns.app', resort, recap, payload);
  assert.equal(m.title, 'Powder day <b>"&"</b> at Stowe');
  assert.match(m.description, /^2 runs · 1 new · Sat, Feb 14, 2026\./);
  assert.equal(new URL(m.image).pathname, '/api/og');
  assert.equal(new URL(m.url).searchParams.get('recap'), payload);
  const html = p.withMeta(page, m);
  assert.ok(!html.includes('<b>'), 'the name is escaped');
  assert.ok(html.includes('<title>Powder day &lt;b&gt;&quot;&amp;&quot;&lt;/b&gt; at Stowe</title>'));
  assert.ok(!html.includes('content="default"'), 'the default preview tags are replaced');
  assert.equal((html.match(/property="og:title"/g) ?? []).length, 1);
  assert.match(html, /<meta name="twitter:card" content="summary_large_image" \/>/);
});

test("a resort's page names its trail map; a bad recap falls back to it", () => {
  const m = p.metaFor('https://www.myskiruns.app', resort, p.recapOf(resort, 'nonsense'), 'nonsense');
  assert.equal(m.title, 'Stowe Trail Map · My Ski Runs');
  assert.equal(new URL(m.url).searchParams.has('recap'), false);
});

test('only resort ids and sane payloads are looked at', () => {
  for (const bad of [null, '', '../secrets', 'Stowe', 'a/b', 'x'.repeat(61)]) assert.equal(p.validResortId(bad), false, String(bad));
  assert.equal(p.recapOf(resort, `1~${'A'.repeat(7000)}`), null);
});

test("the picture's crop stays on the map, at the picture's shape", () => {
  const cases: [number[][], number, number][] = [
    [[], 4000, 2400],
    [[[100, 100], [3900, 2300]], 4000, 2400],
    [[[1900, 1200], [1950, 1260]], 4000, 2400],
    [[[10, 10], [30, 40]], 4000, 2400],
    [[[500, 500], [600, 3000]], 1500, 3200],
  ];
  for (const [pts, iw, ih] of cases) {
    const c = p.cropFor(pts, iw, ih);
    assert.ok(c.x >= 0 && c.y >= 0 && c.x + c.w <= iw && c.y + c.h <= ih, JSON.stringify({ pts, c }));
    assert.ok(Math.abs(c.w / c.h - 1200 / 630) < 0.01, JSON.stringify(c));
  }
});
