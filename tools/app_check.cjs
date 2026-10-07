// A resort in the real app, on a desktop and a phone screen: the picker's search finds it (by its name, the name's
// first word, its state or province, and the other places src/resorts.ts lists for it), picking it loads its map,
// every map panel opens from the switcher with its overlays drawn, there are no page errors, and the phone page has
// no sideways scroll. Screenshots of each step go to --out. Run it for a new resort after registering it, and for
// any resort after an app change.
//
//   npm run build && (node tools/serve_dist.cjs dist 4199 > work/serve.log 2>&1 &)   # its own subshell
//   PLAYWRIGHT_PATH=$(npm root -g)/playwright node tools/app_check.cjs http://localhost:4199/ --resort heavenly \
//     [--search "lake tahoe,nv"] [--out work/app_check/heavenly]
//
// Prints PASS/FAIL lines and exits 1 on any failure. /api/* calls that fail (a static server answers 503) are
// not counted as errors.
const { chromium } = require(process.env.PLAYWRIGHT_PATH || 'playwright');
const fs = require('node:fs');
const path = require('node:path');

const root = path.resolve(__dirname, '..');
const arg = (k, d) => { const i = process.argv.indexOf(k); return i > 0 ? process.argv[i + 1] : d; };
const base = process.argv[2] || 'http://localhost:4199/';
const id = arg('--resort');
if (!id) throw new Error('--resort <id> is required');
const out = arg('--out', path.join(root, 'work/app_check', id));
fs.mkdirSync(out, { recursive: true });

// the resort's entry in src/resorts.ts: oneMap('<id>', '<name>', '<region>', ...) or panels(...), with its panels and
// the other places it is found by (the trailing ['...'] list of a panels() entry)
const src = fs.readFileSync(path.join(root, 'src/resorts.ts'), 'utf8');
const q = "(?:'((?:[^'\\\\]|\\\\.)*)'|\"([^\"]*)\")";
const head = new RegExp(`(oneMap|panels)\\('${id}', ${q}, ${q}`).exec(src);
if (!head) throw new Error(`no ${id} in src/resorts.ts`);
const unq = (a, b) => (a ?? b).replace(/\\'/g, "'");
const name = unq(head[2], head[3]);
const region = unq(head[4], head[5]);
let panels = [{ id: null, name: null }];
let also = [];
if (head[1] === 'panels') {
  const rest = src.slice(head.index);
  const block = rest.slice(0, rest.search(/\n {2}(?:oneMap|panels)\(|\n\];/));
  panels = [...block.matchAll(/\{ id: '([^']+)', name: (?:'([^']*)'|"([^"]*)")/g)].map((m) => ({ id: m[1], name: m[2] ?? m[3] }));
  const tail = /\],\s*\[([^\]]*)\]\)\s*,?\s*$/.exec(block);
  if (tail) also = [...tail[1].matchAll(/'([^']+)'/g)].map((m) => m[1]);
}
const queries = (arg('--search') ? arg('--search').split(',') : [name, name.split(/\s+/)[0], region, ...also])
  .map((s) => s.trim()).filter((s, i, a) => s && a.indexOf(s) === i);
const mapSrc = (p) => `/maps/${p ? `${id}-${p}` : id}.jpg`;

const results = [];
const ok = (what, cond, extra = '') => results.push(`${cond ? 'PASS' : 'FAIL'} ${what}${extra ? ` (${extra})` : ''}`);
const waitMap = (page, s) => page.waitForFunction(
  (s) => [...document.images].some((i) => (i.getAttribute('src') || '').includes(s) && i.complete && i.naturalWidth > 0),
  s, { timeout: 60000 });
const shapes = (page) => page.$$eval('svg path, svg polyline, svg circle', (e) => e.length);

(async () => {
  const browser = await chromium.launch();
  const errors = [];
  const watch = (page) => {
    page.on('pageerror', (e) => errors.push(e.message));
    page.on('console', (m) => {
      if (m.type() === 'error' && !(m.location().url || '').includes('/api/')) errors.push(m.text());
    });
  };
  // desktop: start on another resort and find this one with the picker
  const desk = await (await browser.newContext({ viewport: { width: 1400, height: 900 } })).newPage();
  watch(desk);
  const start = id === 'killington' ? 'stowe' : 'killington';
  await desk.goto(`${base}?resort=${start}`, { waitUntil: 'networkidle' });
  await waitMap(desk, `/maps/${start}`);
  const button = desk.locator('button[aria-label^="Resort:"]');
  await button.click();
  const input = desk.getByRole('combobox', { name: 'Search resorts' });
  for (const s of queries) {
    await input.fill(s);
    const found = await desk.locator('[role=option] >> span:first-child').allTextContents();
    ok(`search "${s}" finds ${name}`, found.includes(name), found.slice(0, 6).join(' | '));
  }
  await input.fill(name);
  await desk.screenshot({ path: path.join(out, 'search.png') });
  await input.press('Enter');
  await waitMap(desk, mapSrc(panels[0].id));
  ok(`picking it shows ${name}`, (await button.getAttribute('aria-label')) === `Resort: ${name}. Change resort`);
  ok('the tab is titled', (await desk.title()).startsWith(`${name} Trail Map`), await desk.title());
  for (const [i, p] of panels.entries()) {
    if (i > 0) {
      await desk.getByRole('button', { name: p.name, exact: true }).click();
      await waitMap(desk, mapSrc(p.id));
    }
    await desk.waitForTimeout(800);
    const n = await shapes(desk);
    ok(`${p.name ? `panel ${p.name}` : 'the map'}: overlays drawn`, n > 0, `${n} shapes`);
    await desk.screenshot({ path: path.join(out, `desktop_${p.id || 'map'}.png`) });
  }
  // phone: open it directly
  const phone = await (await browser.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true,
    deviceScaleFactor: 2 })).newPage();
  watch(phone);
  await phone.goto(`${base}?resort=${id}`, { waitUntil: 'networkidle' });
  await waitMap(phone, mapSrc(panels[0].id));
  await phone.waitForTimeout(800);
  await phone.screenshot({ path: path.join(out, 'phone.png') });
  const overflow = await phone.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
  ok('phone: no sideways scroll', overflow <= 0, `${overflow}px`);
  ok('no page errors', errors.length === 0, errors.slice(0, 3).join(' / '));
  await browser.close();
  console.log(results.join('\n'));
  console.log(`screenshots: ${out}`);
  process.exit(results.some((r) => r.startsWith('FAIL')) ? 1 : 0);
})();
