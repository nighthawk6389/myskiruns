// "Share your day" in the real app: a trip seeded on a phone opens its summary, the share dialog draws the recap
// card in both sizes (story 1080x1920, square 1080x1080; saved to --out to look at), "Copy link" copies a link,
// and that link, opened in a fresh browser with no data, shows the day read-only (its name, every run in the list
// and on the map, no "Skied it", nothing written to the visitor's trips) until "Track your own runs" opens the app.
//
//   npm run build && (node tools/serve_dist.cjs dist 4199 > work/serve.log 2>&1 &)   # its own subshell
//   PLAYWRIGHT_PATH=$(npm root -g)/playwright node tools/recap_check.cjs http://localhost:4199/ --resort vail \
//     [--runs 14] [--out work/recap_check/vail]
//
// Prints PASS/FAIL lines and exits 1 on any failure. /api/* calls that fail (a static server answers 503) are
// not counted as errors.
const { chromium } = require(process.env.PLAYWRIGHT_PATH || 'playwright');
const fs = require('node:fs');
const path = require('node:path');

const root = path.resolve(__dirname, '..');
const arg = (k, d) => { const i = process.argv.indexOf(k); return i > 0 ? process.argv[i + 1] : d; };
const base = process.argv[2] || 'http://localhost:4199/';
const id = arg('--resort', 'killington');
const nRuns = Number(arg('--runs', 14));
const out = arg('--out', path.join(root, 'work/recap_check', id));
fs.mkdirSync(out, { recursive: true });

// trails with an overlay (lines, not markers, first), spread over the list
const dataDir = path.join(root, 'src/data/resorts', id);
const pathFiles = fs.existsSync(path.join(dataDir, 'panels'))
  ? fs.readdirSync(path.join(dataDir, 'panels')).map((p) => path.join(dataDir, 'panels', p, 'trailPaths.json'))
  : [path.join(dataDir, 'trailPaths.json')];
const withLine = [...new Set(pathFiles.flatMap((f) =>
  Object.entries(JSON.parse(fs.readFileSync(f, 'utf8')).trails).filter(([, p]) => p.segments.length).map(([t]) => t)))];
const step = Math.max(1, Math.floor(withLine.length / nRuns));
const picked = withLine.filter((_, i) => i % step === 0).slice(0, nRuns);
const tripName = 'Spring break ⛷️ with the crew';
const now = Date.now();
const iso = (ms) => new Date(ms).toISOString();
const trips = {
  version: 1,
  activeTripId: 'trip-check-2',
  trips: [
    // an earlier trip with three of the same runs: those aren't new
    { id: 'trip-check-1', resortId: id, name: 'Last season', startDate: '2025-03-01', createdAt: iso(now - 4e10),
      runs: picked.slice(0, 3).map((t, i) => ({ trailId: t, at: iso(now - 4e10 + i * 6e5) })) },
    { id: 'trip-check-2', resortId: id, name: tripName, startDate: iso(now - 864e5).slice(0, 10), createdAt: iso(now - 864e5),
      runs: picked.map((t, i) => ({ trailId: t, at: iso(now - 864e5 + i * 9e5) })) },
  ],
};

const results = [];
const ok = (what, cond, extra = '') => results.push(`${cond ? 'PASS' : 'FAIL'} ${what}${extra ? ` (${extra})` : ''}`);
// the day's runs drawn bold in their own colours (not the gold of this device's own skied runs, not the white casing)
const boldRuns = (page) => page.$$eval('svg polyline', (e) =>
  e.filter((l) => !['#fff', '#fbbf24'].includes(l.getAttribute('stroke'))).length);

(async () => {
  const browser = await chromium.launch();
  const errors = [];
  const watch = (page) => {
    page.on('pageerror', (e) => errors.push(e.message));
    page.on('console', (m) => {
      if (m.type() === 'error' && !(m.location().url || '').includes('/api/')) errors.push(m.text());
    });
  };

  // 1. the skier's phone
  const phone = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true });
  await phone.grantPermissions(['clipboard-read', 'clipboard-write'], { origin: new URL(base).origin });
  await phone.addInitScript((s) => {
    if (!sessionStorage.getItem('seeded')) {
      localStorage.setItem('myskiruns.trips', s);
      sessionStorage.setItem('seeded', '1');
    }
  }, JSON.stringify(trips));
  const page = await phone.newPage();
  watch(page);
  await page.goto(`${base}?resort=${id}`);
  await page.getByRole('button', { name: 'Summary', exact: true }).click();
  await page.getByRole('button', { name: 'Share your day' }).click();
  const dialog = page.getByRole('dialog', { name: 'Share your day' });
  ok('the share dialog opens', await dialog.isVisible());

  const card = async (size, w, h) => {
    await dialog.getByRole('radio', { name: new RegExp(size, 'i') }).click();
    const img = dialog.locator('img');
    await page.waitForFunction(({ w, h }) => {
      const i = document.querySelector('[role=dialog] img');
      return i && i.complete && i.naturalWidth === w && i.naturalHeight === h;
    }, { w, h }, { timeout: 60000 });
    const b64 = await img.evaluate(async (i) => {
      const buf = await (await fetch(i.src)).arrayBuffer();
      let s = '';
      new Uint8Array(buf).forEach((c) => { s += String.fromCharCode(c); });
      return btoa(s);
    });
    const file = path.join(out, `card-${size.toLowerCase()}.jpg`);
    fs.writeFileSync(file, Buffer.from(b64, 'base64'));
    ok(`the ${size} card is ${w}x${h}`, true, `${Math.round(fs.statSync(file).size / 1024)} KB, ${file}`);
  };
  await card('Story', 1080, 1920);
  await page.screenshot({ path: path.join(out, 'phone-share-story.png') });
  await card('Square', 1080, 1080);
  await page.screenshot({ path: path.join(out, 'phone-share-square.png') });

  await dialog.getByRole('button', { name: 'Copy link' }).click();
  await dialog.getByText('Link copied').waitFor();
  const link = await page.evaluate(() => navigator.clipboard.readText());
  ok('"Copy link" copies a recap link', /[?&]recap=/.test(link) && link.includes(`resort=${id}`), `${link.length} chars`);
  const tooWide = await page.evaluate(() => document.documentElement.scrollWidth - innerWidth);
  ok('phone: no sideways scroll in the dialog', tooWide <= 0, `${tooWide}px`);

  // 2. a friend opens the link: a fresh browser, no data
  for (const [label, opts] of [
    ['desktop', { viewport: { width: 1280, height: 800 } }],
    ['phone', { viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true }],
  ]) {
    const ctx = await browser.newContext(opts);
    const p = await ctx.newPage();
    watch(p);
    await p.goto(link);
    const cta = p.getByRole('button', { name: 'Track your own runs' });
    await cta.waitFor({ timeout: 60000 });
    await p.waitForFunction(() => [...document.images].some((i) => i.complete && i.naturalWidth > 0), null, { timeout: 60000 });
    ok(`${label}: the recap shows the trip's name`, (await p.locator('#recap-title').textContent()) === tripName);
    const listed = await p.getByRole('list', { name: 'Runs skied' }).getByRole('listitem').count();
    ok(`${label}: every run is listed`, listed === picked.length, `${listed}/${picked.length}`);
    const drawn = await boldRuns(p);
    ok(`${label}: the runs are drawn bold on the map`, drawn > 0, `${drawn} lines`);
    ok(`${label}: the tab names the day`, (await p.title()).includes(tripName));
    await p.screenshot({ path: path.join(out, `recap-${label}.png`) });
    await p.getByRole('list', { name: 'Runs skied' }).getByRole('button').first().click();
    const sheet = p.getByRole('dialog', { name: 'Trails here' });
    await sheet.waitFor();
    ok(`${label}: a run's sheet is read-only`, (await sheet.getByRole('button', { name: /Skied it|Remove/ }).count()) === 0
      && (await sheet.getByText('Skied that day').count()) > 0);
    await p.screenshot({ path: path.join(out, `recap-${label}-sheet.png`) });
    const wide = await p.evaluate(() => document.documentElement.scrollWidth - innerWidth);
    ok(`${label}: no sideways scroll`, wide <= 0, `${wide}px`);
    ok(`${label}: nothing written to the visitor's trips`, (await p.evaluate(() => localStorage.getItem('myskiruns.trips'))) === null);
    await sheet.getByRole('button', { name: 'Close' }).click();
    await cta.click();
    await p.getByRole('button', { name: 'Summary', exact: true }).waitFor({ timeout: 30000 }).catch(() => {});
    const url = new URL(p.url());
    ok(`${label}: "Track your own runs" opens the app at the resort`, !url.searchParams.has('recap')
      && (await p.evaluate(() => localStorage.getItem('myskiruns.resort'))) === id);
    await p.screenshot({ path: path.join(out, `after-${label}.png`) });
    await ctx.close();
  }

  // 3. a link that isn't a recap leaves the app as it was
  const ctx = await browser.newContext({ viewport: { width: 1280, height: 800 } });
  const p = await ctx.newPage();
  watch(p);
  await p.goto(`${base}?resort=${id}&recap=nonsense`);
  await p.waitForFunction(() => [...document.images].some((i) => i.complete && i.naturalWidth > 0), null, { timeout: 60000 });
  ok('a broken recap link opens the resort as usual', (await p.getByRole('button', { name: 'Track your own runs' }).count()) === 0);
  await ctx.close();

  ok('no page errors', errors.length === 0, errors.slice(0, 3).join(' | '));
  await browser.close();
  console.log(results.join('\n'));
  console.log(`screenshots and cards: ${path.relative(root, out)}`);
  process.exit(results.some((r) => r.startsWith('FAIL')) ? 1 : 0);
})().catch((e) => {
  console.error(e);
  process.exit(1);
});
