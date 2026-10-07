// The app offline, in a real browser, against a production build served as Vercel serves it (tools/serve_dist.cjs):
// what a first visit downloads, a reload with the server gone, a resort never opened while offline, a resort in
// several panels cached once it's opened, a new deploy (the caches swap and the maps already on the phone stay),
// and the load-error screen with its Try again. Works on a copy of the build (the deploy step edits its sw.js).
//
//   npm run build && PLAYWRIGHT_PATH=$(npm root -g)/playwright node tools/offline_check.cjs [dist] [--port 4300]
//
// Prints PASS/FAIL lines (with the request log's numbers) and exits 1 on any failure. Playwright's offline mode
// doesn't stop a service worker's own requests, so "offline" here also stops the server.
const { chromium } = require(process.env.PLAYWRIGHT_PATH || 'playwright');
const { spawn } = require('node:child_process');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');

const root = path.resolve(__dirname, '..');
const src = path.resolve(process.argv[2] && !process.argv[2].startsWith('--') ? process.argv[2] : path.join(root, 'dist'));
const pi = process.argv.indexOf('--port');
const port = pi > 0 ? Number(process.argv[pi + 1]) : 4300;
const base = `http://localhost:${port}/`;
const dist = fs.mkdtempSync(path.join(os.tmpdir(), 'offline-check-'));
fs.cpSync(src, dist, { recursive: true });

let server = null;
let log = [];
const start = () => new Promise((resolve) => {
  server = spawn('node', [path.join(__dirname, 'serve_dist.cjs'), dist, String(port)]);
  server.stdout.on('data', (d) => {
    for (const l of String(d).split('\n').filter(Boolean)) {
      if (l.startsWith('listening')) resolve();
      else log.push(l);
    }
  });
});
const stop = () => new Promise((resolve) => { if (!server) return resolve(); server.on('exit', resolve); server.kill(); server = null; });
const maps = () => log.filter((l) => l.includes('/maps/'));
const mb = () => (log.reduce((s, l) => s + Number(l.split(' ').at(-1) || 0), 0) / 1e6).toFixed(2);

const results = [];
const ok = (what, cond, extra = '') => results.push(`${cond ? 'PASS' : 'FAIL'} ${what}${extra ? ` (${extra})` : ''}`);

(async () => {
  await start();
  const browser = await chromium.launch();
  const ctx = await browser.newContext({ viewport: { width: 1400, height: 900 } });
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', (e) => errors.push(e.message));
  const overlay = () => page.locator('svg[viewBox^="0 0 1000"]').waitFor({ timeout: 20000 }).then(() => true, () => false);
  const mapLoaded = () => page.evaluate(() => [...document.images].some((i) => (i.getAttribute('src') || '').includes('/maps/')
    && i.complete && i.naturalWidth > 0));
  const pick = async (name) => {
    await page.locator('button[aria-label^="Resort:"]').click();
    await page.getByRole('combobox', { name: 'Search resorts' }).fill(name);
    await page.getByRole('combobox', { name: 'Search resorts' }).press('Enter');
  };

  // A. first visit: the open resort's map only; the worker takes over
  log = [];
  await page.goto(`${base}?resort=killington`);
  ok('first visit: map and overlays', await overlay());
  const sw = await page.waitForFunction(() => !!navigator.serviceWorker.controller, null, { timeout: 20000 }).then(() => true, () => false);
  ok('first visit: the service worker controls the page', sw);
  await page.waitForTimeout(5000);
  ok('first visit: only the open resort\'s map downloaded', maps().every((l) => l.includes('/maps/killington')),
    `${log.length} requests, ${mb()} MB; ${maps().length} map requests`);

  // B. the server gone: a reload still opens the resort, map included
  await stop();
  await page.reload();
  ok('offline reload: overlays', await overlay());
  ok('offline reload: the map image', await mapLoaded());

  // C. offline, a resort never opened: its trail list (data cached in the background) and the "No connection" note
  await ctx.setOffline(true);
  await pick('Stowe');
  await page.waitForTimeout(2500);
  const note = await page.locator('[class*=placeholderTitle]').first().textContent({ timeout: 2000 }).catch(() => null);
  const header = await page.locator('button[aria-label^="Resort:"]').getAttribute('aria-label');
  ok('offline, never-opened resort: says so instead of breaking', header.includes('Stowe') && (note === 'No connection'
    || (await page.getByText("Couldn't load Stowe").count()) > 0), `${header}; ${note}`);
  await start();
  await ctx.setOffline(false);
  await page.waitForTimeout(3000);
  ok('back online: that map loads in place', await mapLoaded());

  // D. a resort in several panels: opening it caches every panel's map
  log = [];
  await page.goto(`${base}?resort=vail`);
  await overlay();
  await page.waitForTimeout(6000);
  const vailMaps = [...new Set(maps().map((l) => l.split(' ')[1]))];
  ok('several panels: every panel\'s map fetched once the resort is open', vailMaps.length >= 3, vailMaps.join(', '));
  await stop();
  for (const p of ['front-side', 'back-bowls', 'blue-sky']) {
    await page.goto(`${base}?resort=vail&panel=${p}`);
    ok(`offline: Vail ${p}`, (await overlay()) && (await mapLoaded()));
  }

  // E. a new deploy: the caches swap to the new version, the maps on the device are revalidated, not downloaded again
  const swFile = path.join(dist, 'sw.js');
  fs.writeFileSync(swFile, fs.readFileSync(swFile, 'utf8').replace(/"version":"[0-9a-f]+"/, '"version":"offlinecheck1"'));
  await start();
  log = [];
  await page.goto(`${base}?resort=killington`);
  await overlay();
  let keys = [];
  for (let i = 0; i < 60; i++) {
    keys = await page.evaluate(() => caches.keys());
    if (keys.length === 1 && keys[0] === 'myskiruns-offlinecheck1') break;
    await page.waitForTimeout(500);
  }
  ok('new deploy: the caches swap to the new version', keys.length === 1 && keys[0] === 'myskiruns-offlinecheck1', keys.join());
  const big = maps().filter((l) => / 200 /.test(l));
  ok('new deploy: no map downloaded again', big.length === 0, big.slice(0, 3).join('; '));
  await stop();
  for (const r of ['killington', 'vail']) {
    await page.goto(`${base}?resort=${r}`);
    ok(`offline after the deploy: ${r}`, (await overlay()) && (await mapLoaded()));
  }

  // F. no service worker, the server gone: a resort that can't load shows its error, and Try again loads it
  const plain = await (await browser.newContext({ serviceWorkers: 'block', viewport: { width: 1200, height: 800 } })).newPage();
  plain.on('pageerror', (e) => errors.push(e.message));
  await start();
  await plain.goto(`${base}?resort=killington`);
  await plain.locator('svg[viewBox^="0 0 1000"]').waitFor({ timeout: 20000 });
  await stop();
  await plain.locator('button[aria-label^="Resort:"]').click();
  await plain.getByRole('combobox', { name: 'Search resorts' }).fill('Okemo');
  await plain.getByRole('combobox', { name: 'Search resorts' }).press('Enter');
  const shown = await plain.getByText("Couldn't load Okemo").waitFor({ timeout: 10000 }).then(() => true, () => false);
  ok('load error: "Couldn\'t load Okemo" with Try again', shown);
  await start();
  await Promise.all([plain.waitForURL(/resort=okemo/), plain.getByRole('button', { name: 'Try again' }).click()]);
  const back = await plain.locator('svg[viewBox^="0 0 1000"]').waitFor({ timeout: 20000 }).then(() => true, () => false);
  ok('Try again: Okemo loads', back);

  ok('no page errors', errors.length === 0, errors.slice(0, 3).join(' / '));
  await stop();
  await browser.close();
  fs.rmSync(dist, { recursive: true, force: true });
  console.log(results.join('\n'));
  process.exit(results.some((r) => r.startsWith('FAIL')) ? 1 : 0);
})().catch(async (e) => {
  console.error(e);
  await stop();
  fs.rmSync(dist, { recursive: true, force: true });
  process.exit(1);
});
