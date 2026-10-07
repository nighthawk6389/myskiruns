// node check.cjs <base url> <out dir>: Big Sky in the real app: found by search (name, "sky", "montana",
// "mt"), its three panels load with overlays, a trail on another panel opens that panel; desktop and phone.
const { chromium } = require(process.env.PLAYWRIGHT_PATH);
const [base, out] = process.argv.slice(2);
const results = [];
const ok = (name, cond, extra = '') => { results.push(`${cond ? 'PASS' : 'FAIL'} ${name}${extra ? ' — ' + extra : ''}`); };
const header = (p) => p.locator('header button[aria-haspopup="dialog"]').first();
async function waitMap(p, src) {
  await p.waitForFunction((src) => [...document.images].some((i) => (i.getAttribute('src') || '').includes(src) && i.complete && i.naturalWidth > 0), src, { timeout: 60000 });
}
const shapes = (p) => p.$$eval('svg path, svg polyline, svg circle', (e) => e.length);
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 1400, height: 900 } });
  const p = await ctx.newPage();
  const errors = [];
  p.on('pageerror', (e) => errors.push(e.message));
  // (the local server answers /api/ with 503: the conditions feature has no backend here)
  p.on('console', (m) => { if (m.type() === 'error' && !m.text().includes('503')) errors.push(m.text()); });
  await p.goto(`${base}?resort=killington`, { waitUntil: 'networkidle' });
  await waitMap(p, '/maps/killington');
  await header(p).click();
  const input = p.getByRole('combobox', { name: 'Search resorts' });
  for (const q of ['big sky', 'sky', 'montana', 'mt']) {
    await input.fill(q);
    const opts = await p.$$eval('[role=option]', (os) => os.map((o) => o.textContent));
    ok(`search "${q}" finds Big Sky`, opts.some((t) => t.includes('Big Sky')), opts.join(' | '));
  }
  await input.fill('big sky');
  await p.screenshot({ path: `${out}/search.png` });
  await input.press('Enter');
  await waitMap(p, '/maps/big-sky-main');
  ok('picking loads Big Sky', (await header(p).innerText()).includes('Big Sky'));
  await p.waitForTimeout(800);
  await p.screenshot({ path: `${out}/main.png` });
  ok('main panel: overlays drawn', (await shapes(p)) > 100, `${await shapes(p)} svg shapes`);
  for (const [id, name] of [['south-face', 'South Face'], ['bowl', 'The Bowl']]) {
    await p.getByRole('button', { name, exact: true }).click();
    await waitMap(p, `/maps/big-sky-${id}`);
    await p.waitForTimeout(800);
    await p.screenshot({ path: `${out}/${id}.png` });
    ok(`${name} panel loads with overlays`, (await shapes(p)) > 20, `${await shapes(p)} svg shapes`);
  }
  ok('no page errors', errors.length === 0, errors.slice(0, 3).join(' / '));
  // phone
  const ph = await b.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true, deviceScaleFactor: 2 });
  const q = await ph.newPage();
  await q.goto(`${base}?resort=big-sky&panel=bowl`, { waitUntil: 'networkidle' });
  await waitMap(q, '/maps/big-sky-bowl');
  await q.waitForTimeout(800);
  await q.screenshot({ path: `${out}/phone.png` });
  const overflow = await q.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
  ok('phone: no sideways page scroll', overflow <= 0, `${overflow}px`);
  console.log(results.join('\n'));
  await b.close();
})();
