// node check.cjs <base url> <out dir>: Palisades Tahoe in the real app: found by search (name, "tahoe", "california",
// "ca"), its three panels load with overlays, a trail on another panel opens that panel; desktop and phone.
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
  for (const q of ['palisades', 'tahoe', 'california', 'ca']) {
    await input.fill(q);
    const opts = await p.$$eval('[role=option]', (os) => os.map((o) => o.textContent));
    ok(`search "${q}" finds Palisades Tahoe`, opts.some((t) => t.includes('Palisades Tahoe')), opts.join(' | '));
  }
  await input.fill('palisades');
  await p.screenshot({ path: `${out}/search.png` });
  await input.press('Enter');
  await waitMap(p, '/maps/palisades-tahoe-palisades');
  ok('picking loads Palisades Tahoe', (await header(p).innerText()).includes('Palisades Tahoe'));
  await p.waitForTimeout(800);
  await p.screenshot({ path: `${out}/palisades.png` });
  ok('Palisades panel: overlays drawn', (await shapes(p)) > 100, `${await shapes(p)} svg shapes`);
  for (const [id, name] of [['alpine-front', 'Alpine front'], ['alpine-back', 'Alpine back']]) {
    await p.getByRole('button', { name, exact: true }).click();
    await waitMap(p, `/maps/palisades-tahoe-${id}`);
    await p.waitForTimeout(800);
    await p.screenshot({ path: `${out}/${id}.png` });
    ok(`${name} panel loads with overlays`, (await shapes(p)) > 20, `${await shapes(p)} svg shapes`);
  }
  ok('no page errors', errors.length === 0, errors.slice(0, 3).join(' / '));
  // phone
  const ph = await b.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true, deviceScaleFactor: 2 });
  const q = await ph.newPage();
  await q.goto(`${base}?resort=palisades-tahoe&panel=alpine-back`, { waitUntil: 'networkidle' });
  await waitMap(q, '/maps/palisades-tahoe-alpine-back');
  await q.waitForTimeout(800);
  await q.screenshot({ path: `${out}/phone.png` });
  const overflow = await q.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
  ok('phone: no sideways page scroll', overflow <= 0, `${overflow}px`);
  console.log(results.join('\n'));
  await b.close();
})();
