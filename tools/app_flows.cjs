// The app's everyday flows in a real browser, against a production build served as Vercel serves it
// (tools/serve_dist.cjs):
// - on a phone (iPhone 13 screen, touch): tap a trail on the map, mark it from the sheet, undo, mark one from the
//   list, open the trip summary, switch to a resort in several panels and change panel;
// - on a desktop: two tabs of one browser stay in step, a backup exports, imports into a fresh browser, a backup
//   from before trips had a resort lands at Killington, and a deleted trip comes back from its backup.
//
//   npm run build && PLAYWRIGHT_PATH=$(npm root -g)/playwright node tools/app_flows.cjs [dist] [--port 4405]
//
// Prints PASS/FAIL lines and exits 1 on any failure; screenshots go to work/app_flows/.
const { chromium, devices } = require(process.env.PLAYWRIGHT_PATH || 'playwright');
const { spawn } = require('node:child_process');
const fs = require('node:fs');
const path = require('node:path');

const root = path.resolve(__dirname, '..');
const dist = path.resolve(process.argv[2] && !process.argv[2].startsWith('--') ? process.argv[2] : path.join(root, 'dist'));
const pi = process.argv.indexOf('--port');
const port = pi > 0 ? Number(process.argv[pi + 1]) : 4405;
const base = `http://localhost:${port}/`;
const out = path.join(root, 'work/app_flows');
fs.mkdirSync(out, { recursive: true });

const results = [];
const ok = (what, cond, extra = '') => results.push(`${cond ? 'PASS' : 'FAIL'} ${what}${extra ? ` (${extra})` : ''}`);
const overlay = (page) => page.locator('svg[viewBox^="0 0 1000"]').waitFor({ timeout: 30000 });
const waitMap = (page, s) => page.waitForFunction(
  (s) => [...document.images].some((i) => (i.getAttribute('src') || '').includes(s) && i.complete && i.naturalWidth > 0),
  s, { timeout: 30000 });
async function pick(page, name, touch = false) {
  const button = page.locator('button[aria-label^="Resort:"]');
  await (touch ? button.tap() : button.click());
  await page.getByRole('combobox', { name: 'Search resorts' }).fill(name);
  await page.getByRole('combobox', { name: 'Search resorts' }).press('Enter');
}

(async () => {
  let server;
  await new Promise((resolve) => {
    server = spawn('node', [path.join(__dirname, 'serve_dist.cjs'), dist, String(port)]);
    server.stdout.on('data', (d) => String(d).includes('listening') && resolve());
  });
  const browser = await chromium.launch();
  const errors = [];
  const watch = (p) => p.on('pageerror', (e) => errors.push(e.message));
  try {
    // ---- phone
    const { defaultBrowserType: _ignored, ...iphone } = devices['iPhone 13'];
    const page = await (await browser.newContext(iphone)).newPage();
    watch(page);
    await page.goto(`${base}?resort=killington`);
    await overlay(page);
    await page.waitForTimeout(800);
    await page.screenshot({ path: path.join(out, 'phone-1-open.png') });
    // a trail point on screen, clear of the map's buttons
    const paths = JSON.parse(fs.readFileSync(path.join(root, 'src/data/resorts/killington/trailPaths.json'), 'utf8')).trails;
    const box = await page.locator('svg[viewBox^="0 0 1000"]').boundingBox();
    const area = await page.locator('[class*=mapArea]').boundingBox();
    let target = null;
    for (const [id, p] of Object.entries(paths)) {
      const seg = (p.segments || []).reduce((x, y) => (y.length > x.length ? y : x), []);
      if (seg.length < 6) continue;
      const [x, y] = seg[Math.floor(seg.length / 2)];
      const sx = box.x + (x / 100) * box.width;
      const sy = box.y + (y / 100) * box.height;
      if (sx > area.x + 40 && sx < area.x + area.width - 70 && sy > area.y + 70 && sy < area.y + area.height - 40) {
        target = { id, sx, sy };
        break;
      }
    }
    ok('phone: a trail on screen to tap', !!target);
    await page.touchscreen.tap(target.sx, target.sy);
    const sheet = page.getByRole('dialog', { name: 'Trails here' });
    ok('phone: tapping a trail opens its sheet', await sheet.waitFor({ timeout: 5000 }).then(() => true, () => false));
    await page.screenshot({ path: path.join(out, 'phone-2-sheet.png') });
    await page.waitForTimeout(500);
    await sheet.getByRole('button', { name: 'Skied it' }).first().tap();
    const toast = page.getByRole('status').filter({ hasText: 'Marked' });
    ok('phone: "Skied it" marks it (toast)', await toast.waitFor({ timeout: 5000 }).then(() => true, () => false));
    const checked = () => page.evaluate(() => [...document.querySelectorAll('[role=checkbox][aria-checked=true]')]
      .map((e) => e.getAttribute('aria-label')));
    ok('phone: the list shows it skied', (await checked()).length === 1, JSON.stringify(await checked()));
    await toast.getByRole('button', { name: 'Undo' }).tap();
    await page.waitForTimeout(300);
    ok('phone: Undo takes it back', (await checked()).length === 0);
    await page.getByRole('checkbox', { name: /^Skied .* this trip$/ }).nth(2).tap();
    await page.getByRole('button', { name: 'Trip options' }).tap();
    await page.getByRole('menuitem', { name: 'Trip summary' }).tap();
    const summary = page.getByRole('dialog').filter({ hasText: 'Difficulty mix' });
    ok('phone: the trip summary opens', await summary.waitFor({ timeout: 5000 }).then(() => true, () => false));
    await page.screenshot({ path: path.join(out, 'phone-3-summary.png') });
    await page.getByRole('button', { name: 'Close summary' }).tap();
    await pick(page, 'Vail', true);
    await waitMap(page, '/maps/vail-front-side.jpg');
    await page.getByRole('group', { name: 'Trail map' }).getByRole('button', { name: 'Back Bowls' }).tap();
    const panel = await waitMap(page, '/maps/vail-back-bowls.jpg').then(() => true, () => false);
    ok('phone: Vail, then its Back Bowls panel', panel && (await overlay(page).then(() => true, () => false)));
    await page.screenshot({ path: path.join(out, 'phone-4-vail-back-bowls.png') });

    // ---- desktop: two tabs, backups
    const APP = `${base}?resort=stowe`;
    const tick = (p, name) => p.getByRole('checkbox', { name: `Skied ${name} this trip` });
    const isTicked = async (p, name) => (await tick(p, name).getAttribute('aria-checked')) === 'true';
    const ctx = await browser.newContext({ acceptDownloads: true, viewport: { width: 1300, height: 900 } });
    const [a, b] = [await ctx.newPage(), await ctx.newPage()];
    for (const p of [a, b]) {
      watch(p);
      p.on('dialog', (d) => d.accept());
      await p.goto(APP);
      await tick(p, 'Bypass').waitFor();
    }
    await tick(a, 'Bypass').click();
    const inB = await b.waitForFunction(() => document.querySelector('[aria-label="Skied Bypass this trip"]')
      ?.getAttribute('aria-checked') === 'true', null, { timeout: 5000 }).then(() => true, () => false);
    await tick(b, 'Centerline').click();
    const inA = await a.waitForFunction(() => document.querySelector('[aria-label="Skied Centerline this trip"]')
      ?.getAttribute('aria-checked') === 'true', null, { timeout: 5000 }).then(() => true, () => false);
    ok('two tabs: a run marked in either shows in the other', inA && inB);
    await a.getByRole('button', { name: 'Trip options' }).click();
    const [download] = await Promise.all([a.waitForEvent('download'), a.getByRole('menuitem', { name: 'Export backup' }).click()]);
    const file = path.join(out, 'backup.json');
    await download.saveAs(file);
    const exported = JSON.parse(fs.readFileSync(file, 'utf8'));
    ok('export: one trip with both runs', exported.trips.length === 1 && exported.trips[0].runs.length === 2,
      exported.trips.map((t) => t.runs.map((r) => r.trailId).join('+')).join());
    const c = await (await browser.newContext({ viewport: { width: 1300, height: 900 } })).newPage();
    watch(c);
    c.on('dialog', (d) => d.accept());
    await c.goto(APP);
    await tick(c, 'Bypass').waitFor();
    await c.locator('input[type=file]').setInputFiles(file);
    await c.getByText('Imported 1 trip.').waitFor({ timeout: 5000 });
    ok('import into a fresh browser: both runs', (await isTicked(c, 'Bypass')) && (await isTicked(c, 'Centerline')));
    // a backup made before trips had a resort (and edit times): its trips are Killington's
    const old = { app: 'myskiruns', exportedAt: '2026-02-01T10:00:00.000Z', version: 1, activeTripId: 'trip-old-1',
      trips: [{ id: 'trip-old-1', name: 'Presidents Day 2026', startDate: '2026-02-14', createdAt: '2026-02-14T09:00:00.000Z',
        runs: [{ trailId: 'superstar', at: '2026-02-14T10:00:00.000Z' }] }] };
    fs.writeFileSync(path.join(out, 'old-backup.json'), JSON.stringify(old));
    await c.locator('input[type=file]').setInputFiles(path.join(out, 'old-backup.json'));
    await c.getByText('Imported 1 trip.').waitFor({ timeout: 5000 });
    await pick(c, 'Killington');
    await waitMap(c, '/maps/killington.jpg');
    await c.locator('#trip-select').waitFor();
    const trips = await c.locator('#trip-select option').allInnerTexts();
    ok('an old backup: its trip is at Killington', trips.some((t) => t.includes('Presidents Day 2026')), JSON.stringify(trips));
    await pick(c, 'Stowe');
    await tick(c, 'Bypass').waitFor();
    await c.getByRole('button', { name: 'Trip options' }).click();
    await c.getByRole('menuitem', { name: 'Delete trip' }).click();
    await c.getByText(/No trip yet/).waitFor({ timeout: 5000 });
    await c.locator('input[type=file]').setInputFiles(file);
    await c.getByText('Imported 1 trip.').waitFor({ timeout: 5000 });
    ok('a deleted trip comes back from its backup', (await isTicked(c, 'Bypass')) && (await isTicked(c, 'Centerline')));
    ok('no page errors', errors.length === 0, errors.slice(0, 3).join(' / '));
  } catch (e) {
    ok(`ran to the end: ${e.message.split('\n')[0]}`, false);
  }
  await browser.close();
  server.kill();
  console.log(results.join('\n'));
  console.log(`screenshots: ${out}`);
  process.exit(results.some((r) => r.startsWith('FAIL')) ? 1 : 0);
})();
