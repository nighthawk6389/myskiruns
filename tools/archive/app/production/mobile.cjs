// Phone flows in Chromium with an iPhone 13 screen and touch: tap a trail on
// the map, mark it from the sheet, undo, trip summary, switch to Vail and its
// panels.
const { chromium, devices } = require(process.env.PLAYWRIGHT_PATH);
const { spawn } = require('node:child_process');
const fs = require('node:fs');
const SCR = '/tmp/claude-0/-home-user-myskiruns/6d543bfc-3ab1-5e7f-9c64-5c2d6dd5c830/scratchpad';
const shot = (page, n) => page.screenshot({ path: `${__dirname}/mobile-${n}.png` });

(async () => {
  let server;
  await new Promise((r) => { server = spawn('node', [`${SCR}/offline/serve.cjs`, `${SCR}/dist-new`, '4404']); server.stdout.on('data', (d) => String(d).includes('listening') && r()); });
  const browser = await chromium.launch();
  const { defaultBrowserType: _ignored, ...iphone } = devices['iPhone 13'];
  const ctx = await browser.newContext(iphone);
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', (e) => errors.push(e.message));
  await page.goto('http://localhost:4404/?resort=killington');
  await page.locator('svg[viewBox^="0 0 1000"]').waitFor({ timeout: 30000 });
  await page.waitForTimeout(800);
  await shot(page, '1-open');

  // a trail point that is on screen and clear of the map's buttons
  const paths = JSON.parse(fs.readFileSync('/home/user/myskiruns/src/data/resorts/killington/trailPaths.json', 'utf8')).trails;
  const box = await page.locator('svg[viewBox^="0 0 1000"]').boundingBox();
  const area = await page.locator('[class*=mapArea]').boundingBox();
  let target = null;
  for (const [id, p] of Object.entries(paths)) {
    if (!p.segments?.length) continue;
    const seg = p.segments.reduce((a, b) => (b.length > a.length ? b : a));
    if (seg.length < 6) continue;
    const [x, y] = seg[Math.floor(seg.length / 2)];
    const sx = box.x + (x / 100) * box.width;
    const sy = box.y + (y / 100) * box.height;
    if (sx > area.x + 40 && sx < area.x + area.width - 70 && sy > area.y + 70 && sy < area.y + area.height - 40) { target = { id, sx, sy }; break; }
  }
  await page.touchscreen.tap(target.sx, target.sy);
  const sheet = page.getByRole('dialog', { name: 'Trails here' });
  await sheet.waitFor({ timeout: 5000 });
  await shot(page, '2-sheet');
  const nearest = await sheet.locator('strong, h3, [class*=trailName]').first().innerText().catch(() => '?');
  await page.waitForTimeout(500);
  await sheet.getByRole('button', { name: 'Skied it' }).first().tap();
  const toast = page.getByRole('status').filter({ hasText: 'Marked' });
  await toast.waitFor({ timeout: 5000 });
  const toastText = (await toast.innerText()).replace(/\s+/g, ' ');
  await shot(page, '3-marked');
  const checked = () => page.evaluate(() => [...document.querySelectorAll('[role=checkbox][aria-checked=true]')].map((e) => e.getAttribute('aria-label')));
  console.log(`tapped near "${target.id}"; sheet's first trail: ${nearest}; toast: "${toastText}"; checked in list: ${JSON.stringify(await checked())}`);
  await toast.getByRole('button', { name: 'Undo' }).tap();
  await page.waitForTimeout(300);
  console.log('after Undo, checked:', JSON.stringify(await checked()));

  // mark one from the list, then the trip summary
  await page.getByRole('checkbox', { name: /^Skied .* this trip$/ }).nth(2).tap();
  await page.getByRole('button', { name: 'Trip options' }).tap();
  await page.getByRole('menuitem', { name: 'Trip summary' }).tap();
  const summary = page.getByRole('dialog').filter({ hasText: 'Difficulty mix' });
  await summary.waitFor({ timeout: 5000 });
  await shot(page, '4-summary');
  console.log('trip summary open:', (await summary.locator('h2').innerText()).trim());
  await page.getByRole('button', { name: 'Close summary' }).tap();

  // Vail and its panels
  await page.selectOption('select[aria-label="Resort"]', 'vail');
  await page.locator('img[alt="Vail trail map, Front Side"]').waitFor({ timeout: 15000 });
  await page.getByRole('group', { name: 'Trail map' }).getByRole('button', { name: 'Back Bowls' }).tap();
  await page.locator('img[alt="Vail trail map, Back Bowls"]').waitFor({ timeout: 15000 });
  await page.locator('svg[viewBox^="0 0 1000"]').waitFor({ timeout: 15000 });
  await shot(page, '5-vail-back-bowls');
  console.log('Vail: switched to Back Bowls on a phone');
  console.log('page errors:', errors.length ? errors : 'none');
  await browser.close();
  server.kill();
})().catch((e) => { console.error(e); process.exit(1); });
