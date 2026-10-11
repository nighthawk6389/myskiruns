// The search across resorts in the real app, on a desktop and a phone: typing a trail's name in the resort
// picker lists that trail at every resort that has it (with its rating and resort), picking one at another resort
// opens that resort zoomed to the trail with its sheet open, and the same works from a ?trail= link. Marking a run
// sends one anonymous report to /api/marks (intercepted here), and unmarking it sends another.
//
//   npm run build && (node tools/serve_dist.cjs dist 4199 > work/serve.log 2>&1 &)   # its own subshell
//   PLAYWRIGHT_PATH=$(npm root -g)/playwright node tools/search_check.cjs http://localhost:4199/ \
//     [--query "outer limits"] [--out work/search_check]
//
// Prints PASS/FAIL lines and exits 1 on any failure.
const { chromium } = require(process.env.PLAYWRIGHT_PATH || 'playwright');
const fs = require('node:fs');
const path = require('node:path');

const root = path.resolve(__dirname, '..');
const arg = (k, d) => { const i = process.argv.indexOf(k); return i > 0 ? process.argv[i + 1] : d; };
const base = process.argv[2] || 'http://localhost:4199/';
const query = arg('--query', 'outer limits');
const out = arg('--out', path.join(root, 'work/search_check'));
fs.mkdirSync(out, { recursive: true });

const results = [];
const ok = (what, cond, extra = '') => results.push(`${cond ? 'PASS' : 'FAIL'} ${what}${extra ? ` (${extra})` : ''}`);

(async () => {
  const browser = await chromium.launch();
  const errors = [];
  for (const [label, opts] of [
    ['desktop', { viewport: { width: 1280, height: 800 } }],
    ['phone', { viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true }],
  ]) {
    const ctx = await browser.newContext(opts);
    const marks = [];
    await ctx.route('**/api/marks', async (route) => {
      marks.push(JSON.parse(route.request().postData() || '{}'));
      await route.fulfill({ status: 200, contentType: 'application/json', body: '{"ok":true}' });
    });
    const page = await ctx.newPage();
    page.on('pageerror', (e) => errors.push(`${label}: ${e.message}`));
    await page.goto(`${base}?resort=stowe`);
    await page.waitForFunction(() => [...document.images].some((i) => i.complete && i.naturalWidth > 0), null, { timeout: 60000 });

    // 1. search a trail's name from the resort picker
    await page.getByRole('button', { name: /Change resort/ }).click();
    await page.getByRole('combobox', { name: 'Search resorts and trails' }).fill(query);
    const group = page.getByRole('group', { name: 'Trails' });
    await group.waitFor({ timeout: 30000 });
    const hits = await group.getByRole('option').evaluateAll((els) => els.map((e) => e.getAttribute('aria-label')));
    const resorts = new Set(hits.map((h) => h.split(' at ').pop()));
    ok(`${label}: "${query}" lists trails at several resorts`, hits.length >= 2 && resorts.size >= 2, hits.slice(0, 4).join(' | '));
    await page.screenshot({ path: path.join(out, `${label}-results.png`) });

    // 2. pick the first one at another resort: its resort opens on it
    const pickLabel = hits.find((h) => !h.endsWith(' at Stowe'));
    const [pickName, pickResort] = [pickLabel.split(',')[0], pickLabel.split(' at ').pop()];
    await group.getByRole('option', { name: pickLabel }).click();
    const sheet = page.getByRole('dialog', { name: 'Trails here' });
    await sheet.waitFor({ timeout: 60000 });
    await page.waitForFunction(() => [...document.images].some((i) => i.complete && i.naturalWidth > 0), null, { timeout: 60000 });
    ok(`${label}: picking it opens ${pickResort}`, (await page.getByRole('button', { name: /Change resort/ }).getAttribute('aria-label')).includes(pickResort));
    ok(`${label}: with ${pickName}'s sheet open`, (await sheet.textContent()).includes(pickName));
    await page.waitForTimeout(800);
    await page.screenshot({ path: path.join(out, `${label}-picked.png`) });

    // 3. mark it from the sheet, then undo: two reports
    await sheet.getByRole('button', { name: 'Skied it' }).click();
    await page.getByRole('button', { name: 'Undo' }).click();
    await page.waitForTimeout(500);
    ok(`${label}: marking and undoing send two mark reports`, marks.length === 2 && marks[0].marked === true && marks[1].marked === false
      && marks.every((m) => m.trailId && m.resort && /^[a-zA-Z0-9-]{8,64}$/.test(m.deviceId)), JSON.stringify(marks.map((m) => [m.resort, m.trailId, m.marked])));

    // 4. a ?trail= link opens the trail
    await page.goto(`${base}?resort=${marks[0]?.resort}&trail=${marks[0]?.trailId}`);
    await sheet.waitFor({ timeout: 60000 });
    ok(`${label}: a ?trail= link opens with the trail's sheet`, (await sheet.textContent()).includes(pickName));
    const wide = await page.evaluate(() => document.documentElement.scrollWidth - innerWidth);
    ok(`${label}: no sideways scroll`, wide <= 0, `${wide}px`);
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
