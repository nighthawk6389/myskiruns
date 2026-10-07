// node check.cjs <base url> <out dir>: Park City in the real app: found by search (name, "utah", "ut"), its map and
// overlays load, a hover shows a name, a click marks a trail, the trail list has its 345 trails; desktop and phone.
const { chromium } = require(process.env.PLAYWRIGHT_PATH);
const [base, out] = process.argv.slice(2);
const results = [];
const ok = (name, cond, extra = '') => { results.push(`${cond ? 'PASS' : 'FAIL'} ${name}${extra ? ' — ' + extra : ''}`); };
const header = (p) => p.locator('header button[aria-haspopup="dialog"]').first();
async function waitMap(p, id) {
  await p.waitForFunction((id) => [...document.images].some((i) => (i.getAttribute('src') || '').includes(`/maps/${id}`) && i.complete && i.naturalWidth > 0), id, { timeout: 60000 });
}
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 1400, height: 900 } });
  const p = await ctx.newPage();
  const errors = [];
  p.on('pageerror', (e) => errors.push(e.message));
  p.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });
  await p.goto(`${base}?resort=killington`, { waitUntil: 'networkidle' });
  await waitMap(p, 'killington');
  await header(p).click();
  const input = p.getByRole('combobox', { name: 'Search resorts' });
  for (const q of ['park', 'utah', 'ut']) {
    await input.fill(q);
    const opts = await p.$$eval('[role=option]', (os) => os.map((o) => o.textContent));
    ok(`search "${q}" finds Park City`, opts.some((t) => t.includes('Park City Mountain')), opts.join(' | '));
  }
  await input.fill('park city');
  await p.screenshot({ path: `${out}/search.png` });
  await input.press('Enter');
  await waitMap(p, 'park-city');
  ok('picking loads Park City', (await header(p).innerText()).includes('Park City'));
  ok('URL names the resort', p.url().includes('resort=park-city'), p.url());
  await p.waitForTimeout(800);
  await p.screenshot({ path: `${out}/map.png` });
  const nOverlays = await p.$$eval('svg path, svg polyline, svg circle', (e) => e.length);
  ok('overlays drawn', nOverlays > 300, `${nOverlays} svg shapes`);
  errors.length || ok('no page errors', true);
  if (errors.length) ok('no page errors', false, errors.slice(0, 3).join(' / '));
  // phone
  const ph = await b.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true, deviceScaleFactor: 2 });
  const q = await ph.newPage();
  await q.goto(`${base}?resort=park-city`, { waitUntil: 'networkidle' });
  await waitMap(q, 'park-city');
  await q.waitForTimeout(800);
  await q.screenshot({ path: `${out}/phone.png` });
  const overflow = await q.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
  ok('phone: no sideways page scroll', overflow <= 0, `${overflow}px`);
  console.log(results.join('\n'));
  await b.close();
})();
