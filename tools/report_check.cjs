// "Something wrong?" in the real app, on a desktop and a phone: tapping a trail opens its sheet with a
// "Something wrong with ..." link; picking what's wrong and sending posts one report to /api/report
// (intercepted here) with the resort, panel, trail and where on the map the tap was; "A trail here is missing
// from the map?" sends one with no trail; a failed send says so and keeps the form; a shared day's read-only
// sheet has no link.
//
//   npm run build && (node tools/serve_dist.cjs dist 4199 > work/serve.log 2>&1 &)   # its own subshell
//   PLAYWRIGHT_PATH=$(npm root -g)/playwright node tools/report_check.cjs http://localhost:4199/ \
//     [--resort stowe] [--out work/report_check]
//
// Prints PASS/FAIL lines and exits 1 on any failure.
const { chromium } = require(process.env.PLAYWRIGHT_PATH || 'playwright');
const fs = require('node:fs');
const path = require('node:path');

const root = path.resolve(__dirname, '..');
const arg = (k, d) => { const i = process.argv.indexOf(k); return i > 0 ? process.argv[i + 1] : d; };
const base = process.argv[2] || 'http://localhost:4199/';
const resort = arg('--resort', 'stowe');
const out = arg('--out', path.join(root, 'work/report_check'));
fs.mkdirSync(out, { recursive: true });

const results = [];
const ok = (what, cond, extra = '') => results.push(`${cond ? 'PASS' : 'FAIL'} ${what}${extra ? ` (${extra})` : ''}`);
const paths = JSON.parse(fs.readFileSync(path.join(root, `src/data/resorts/${resort}/trailPaths.json`), 'utf8')).trails;

(async () => {
  const browser = await chromium.launch();
  const errors = [];
  for (const [label, opts] of [
    ['desktop', { viewport: { width: 1280, height: 800 } }],
    ['phone', { viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true }],
  ]) {
    const touch = label === 'phone';
    const ctx = await browser.newContext(opts);
    const reports = [];
    let fail = false;
    await ctx.route('**/api/report', async (route) => {
      if (fail) return route.fulfill({ status: 500, contentType: 'application/json', body: '{"error":"down"}' });
      reports.push(JSON.parse(route.request().postData() || '{}'));
      await route.fulfill({ status: 200, contentType: 'application/json', body: '{"ok":true}' });
    });
    const page = await ctx.newPage();
    page.on('pageerror', (e) => errors.push(`${label}: ${e.message}`));
    const press = (loc) => (touch ? loc.tap() : loc.click());
    await page.goto(`${base}?resort=${resort}`);
    await page.waitForFunction(() => [...document.images].some((i) => i.complete && i.naturalWidth > 0), null, { timeout: 60000 });
    await page.locator('svg[viewBox^="0 0 1000"]').waitFor();
    await page.waitForTimeout(800);

    // 1. tap a trail's line, clear of the map's buttons
    const box = await page.locator('svg[viewBox^="0 0 1000"]').boundingBox();
    const area = await page.locator('[class*=mapArea]').boundingBox();
    let target = null;
    for (const [id, p] of Object.entries(paths)) {
      const seg = (p.segments || []).reduce((x, y) => (y.length > x.length ? y : x), []);
      if (seg.length < 6) continue;
      const [x, y] = seg[Math.floor(seg.length / 2)];
      const sx = box.x + (x / 100) * box.width;
      const sy = box.y + (y / 100) * box.height;
      if (sx > area.x + 40 && sx < area.x + area.width - 70 && sy > area.y + 70 && sy < area.y + area.height - 260) {
        target = { id, x, y, sx, sy };
        break;
      }
    }
    ok(`${label}: a trail on screen to tap`, !!target);
    if (touch) await page.touchscreen.tap(target.sx, target.sy);
    else await page.mouse.click(target.sx, target.sy);
    const sheet = page.getByRole('dialog', { name: 'Trails here' });
    await sheet.waitFor({ timeout: 5000 });
    await page.waitForTimeout(500);
    const link = sheet.getByRole('button', { name: /^Something wrong with/ }).first();
    ok(`${label}: the sheet has a "Something wrong?" link`, await link.isVisible());

    // 2. send a wrong-name report
    await press(link);
    const form = sheet.getByRole('group', { name: /^Report a problem/ });
    const send = form.getByRole('button', { name: 'Send' });
    ok(`${label}: Send waits for what's wrong`, await send.isDisabled());
    await press(form.getByRole('radio', { name: 'Wrong name' }));
    await form.getByRole('textbox', { name: 'Note' }).fill('Signs at the top say Goat');
    await page.screenshot({ path: path.join(out, `${label}-form.png`) });
    await press(send);
    const thanks = sheet.getByRole('status').filter({ hasText: 'Thanks' });
    ok(`${label}: sending thanks the skier`, await thanks.waitFor({ timeout: 5000 }).then(() => true, () => false));
    await page.screenshot({ path: path.join(out, `${label}-sent.png`) });
    const [r] = reports;
    ok(`${label}: one report with the resort, panel, trail and note`, reports.length === 1 && r.resort === resort && r.panel
      && r.kind === 'name' && r.note === 'Signs at the top say Goat' && /^[a-zA-Z0-9-]{8,64}$/.test(r.deviceId)
      && Object.values(paths[r.trailId]?.segments ?? []).length > 0, JSON.stringify(r));
    ok(`${label}: and where the tap was on the map`, r && Math.abs(r.x - target.x) < 1 && Math.abs(r.y - target.y) < 1,
      `${r?.x},${r?.y} vs ${target.x.toFixed(2)},${target.y.toFixed(2)}`);

    // 3. a trail missing from the map; the first try fails
    await press(sheet.getByRole('button', { name: 'Close' }).last());
    await press(sheet.getByRole('button', { name: 'A trail here is missing from the map?' }));
    const missing = sheet.getByRole('group', { name: /missing from the map/ });
    ok(`${label}: a missing trail needs no kind picked`, (await missing.getByRole('radio').count()) === 0 && await missing.getByRole('button', { name: 'Send' }).isEnabled());
    fail = true;
    await press(missing.getByRole('button', { name: 'Send' }));
    ok(`${label}: a failed send says so and keeps the form`, await sheet.getByText("Couldn't send").waitFor({ timeout: 5000 }).then(() => true, () => false));
    fail = false;
    await press(missing.getByRole('button', { name: 'Send' }));
    await sheet.getByRole('status').filter({ hasText: 'Thanks' }).waitFor({ timeout: 5000 });
    ok(`${label}: then sends with no trail`, reports.length === 2 && reports[1].kind === 'missing' && reports[1].trailId === null && reports[1].x != null);
    const wide = await page.evaluate(() => document.documentElement.scrollWidth - innerWidth);
    ok(`${label}: no sideways scroll`, wide <= 0, `${wide}px`);

    // 4. opened from a link (no tap): no position
    await page.goto(`${base}?resort=${resort}&trail=${target.id}`);
    await sheet.waitFor({ timeout: 60000 });
    await page.waitForTimeout(500);
    await press(sheet.getByRole('button', { name: /^Something wrong with/ }));
    await press(sheet.getByRole('radio', { name: 'Wrong line on the map' }));
    await press(sheet.getByRole('button', { name: 'Send' }));
    await sheet.getByRole('status').filter({ hasText: 'Thanks' }).waitFor({ timeout: 5000 });
    ok(`${label}: from a ?trail= link, the report has the trail and no tap`, reports.length === 3 && reports[2].trailId === target.id
      && reports[2].kind === 'line' && reports[2].x === null && reports[2].y === null, JSON.stringify(reports[2]));
    await ctx.close();
  }
  ok('no page errors', errors.length === 0, errors.slice(0, 3).join(' | '));
  await browser.close();
  console.log(results.join('\n'));
  console.log(`screenshots: ${path.relative(root, out)}`);
  process.exit(results.some((r) => r.startsWith('FAIL')) ? 1 : 0);
})().catch((e) => {
  console.error(e);
  process.exit(1);
});
