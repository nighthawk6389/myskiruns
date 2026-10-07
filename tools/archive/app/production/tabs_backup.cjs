// Two tabs on one device, and backups: export, import into a fresh browser,
// import a file from before this release, re-import a deleted trip.
const { chromium } = require(process.env.PLAYWRIGHT_PATH);
const { spawn } = require('node:child_process');
const fs = require('node:fs');
const SCR = '/tmp/claude-0/-home-user-myskiruns/6d543bfc-3ab1-5e7f-9c64-5c2d6dd5c830/scratchpad';
const APP = 'http://localhost:4405/?resort=stowe';
const box = (page, name) => page.getByRole('checkbox', { name: `Skied ${name} this trip` });
const isChecked = async (page, name) => (await box(page, name).getAttribute('aria-checked')) === 'true';

(async () => {
  let server;
  await new Promise((r) => { server = spawn('node', [`${SCR}/offline/serve.cjs`, `${SCR}/dist-new`, '4405']); server.stdout.on('data', (d) => String(d).includes('listening') && r()); });
  const browser = await chromium.launch();
  const errors = [];

  // two tabs
  const ctx = await browser.newContext({ acceptDownloads: true, viewport: { width: 1300, height: 900 } });
  const [a, b] = [await ctx.newPage(), await ctx.newPage()];
  for (const p of [a, b]) {
    p.on('pageerror', (e) => errors.push(e.message));
    p.on('dialog', (d) => d.accept());
    await p.goto(APP);
    await box(p, 'Bypass').waitFor();
  }
  await box(a, 'Bypass').click();
  await b.waitForFunction(() => document.querySelector('[aria-label="Skied Bypass this trip"]')?.getAttribute('aria-checked') === 'true', null, { timeout: 5000 });
  await box(b, 'Centerline').click();
  await a.waitForFunction(() => document.querySelector('[aria-label="Skied Centerline this trip"]')?.getAttribute('aria-checked') === 'true', null, { timeout: 5000 });
  console.log('two tabs: a run marked in either tab shows in the other without reloading');

  // export
  await a.getByRole('button', { name: 'Trip options' }).click();
  const [download] = await Promise.all([a.waitForEvent('download'), a.getByRole('menuitem', { name: 'Export backup' }).click()]);
  const file = `${__dirname}/backup.json`;
  await download.saveAs(file);
  const exported = JSON.parse(fs.readFileSync(file, 'utf8'));
  console.log(`export: ${exported.trips.length} trip, runs ${exported.trips[0].runs.map((r) => r.trailId).join(', ')}`);

  // import into a fresh browser
  const ctx2 = await browser.newContext({ viewport: { width: 1300, height: 900 } });
  const c = await ctx2.newPage();
  c.on('pageerror', (e) => errors.push(e.message));
  await c.goto(APP);
  await box(c, 'Bypass').waitFor();
  await c.locator('input[type=file]').setInputFiles(file);
  await c.getByText('Imported 1 trip.').waitFor({ timeout: 5000 });
  console.log(`import into a fresh browser: Bypass ${await isChecked(c, 'Bypass')}, Centerline ${await isChecked(c, 'Centerline')}`);

  // a backup made by the version before this release (no resort, no edit times)
  const old = { app: 'myskiruns', exportedAt: '2026-02-01T10:00:00.000Z', version: 1, activeTripId: 'trip-old-1',
    trips: [{ id: 'trip-old-1', name: 'Presidents Day 2026', startDate: '2026-02-14', createdAt: '2026-02-14T09:00:00.000Z', runs: [{ trailId: 'superstar', at: '2026-02-14T10:00:00.000Z' }] }] };
  fs.writeFileSync(`${__dirname}/old-backup.json`, JSON.stringify(old));
  await c.locator('input[type=file]').setInputFiles(`${__dirname}/old-backup.json`);
  await c.getByText('Imported 1 trip.').waitFor({ timeout: 5000 });
  await c.selectOption('select[aria-label="Resort"]', 'killington');
  await c.locator('#trip-select').waitFor();
  const killingtonTrips = await c.locator('#trip-select option').allInnerTexts();
  console.log('old-format backup: trip shows at Killington:', JSON.stringify(killingtonTrips));

  // delete a trip, then import the backup that has it: it comes back (as a copy)
  await c.selectOption('select[aria-label="Resort"]', 'stowe');
  await box(c, 'Bypass').waitFor();
  await c.getByRole('button', { name: 'Trip options' }).click();
  c.on('dialog', (d) => d.accept());
  await c.getByRole('menuitem', { name: 'Delete trip' }).click();
  await c.getByText(/No trip yet/).waitFor({ timeout: 5000 });
  await c.locator('input[type=file]').setInputFiles(file);
  await c.getByText('Imported 1 trip.').waitFor({ timeout: 5000 });
  console.log(`deleted, then re-imported: Bypass ${await isChecked(c, 'Bypass')}, Centerline ${await isChecked(c, 'Centerline')}`);
  console.log('page errors:', errors.length ? errors : 'none');
  await browser.close();
  server.kill();
})().catch((e) => { console.error(e); process.exit(1); });
