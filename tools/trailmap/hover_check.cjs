// Browser check that every trail overlay shows its own name.
//
//   npm run build && npx vite preview --port 4199 &
//   node tools/trailmap/hover_check.cjs http://localhost:4199/
//
// Hovers 3 points (1/4, 1/2, 3/4 along the longest segment) of every line
// trail and each glade marker, in the real app, and compares the tooltip with
// the trail's name. This checks rendering and overlap resolution against the
// human-verified geometry in trailPaths.json; it is NOT evidence that the
// geometry is right (that comes from the review). Expect misses only at
// junctions/crossings where another trail is within the hover width.
//
// Uses Playwright; set CHROMIUM to a browser binary if one isn't bundled.
const { chromium } = require(process.env.PLAYWRIGHT_PATH || 'playwright');
const fs = require('node:fs');
const path = require('node:path');

const root = path.resolve(__dirname, '../..');
const url = process.argv[2] || 'http://localhost:4199/';
const src = fs.readFileSync(path.join(root, 'src/data/trails.ts'), 'utf8');
const names = Object.fromEntries(
  [...src.matchAll(/\{ id:\s*'([^']+)',\s*name:\s*(['"])(.*?)\2, difficulty/g)].map((m) => [m[1], m[3]]),
);
const paths = JSON.parse(fs.readFileSync(path.join(root, 'src/data/trailPaths.json'), 'utf8')).trails;

const cases = [];
for (const [id, p] of Object.entries(paths)) {
  if (!names[id]) continue;
  if (p.label) {
    cases.push({ id, name: names[id], x: p.label[0], y: p.label[1] });
    continue;
  }
  const seg = p.segments.reduce((a, b) => (b.length > a.length ? b : a));
  const cum = [0];
  for (let i = 1; i < seg.length; i++) cum.push(cum[i - 1] + Math.hypot(seg[i][0] - seg[i - 1][0], seg[i][1] - seg[i - 1][1]));
  for (const f of [0.25, 0.5, 0.75]) {
    const t = f * cum.at(-1);
    let i = cum.findIndex((c) => c > t) - 1;
    if (i < 0) i = seg.length - 2;
    const u = (t - cum[i]) / Math.max(1e-9, cum[i + 1] - cum[i]);
    cases.push({ id, name: names[id], x: seg[i][0] + u * (seg[i + 1][0] - seg[i][0]), y: seg[i][1] + u * (seg[i + 1][1] - seg[i][1]) });
  }
}

(async () => {
  const browser = await chromium.launch(process.env.CHROMIUM ? { executablePath: process.env.CHROMIUM } : {});
  const page = await browser.newPage({ viewport: { width: 2600, height: 1700 } });
  await page.goto(url);
  await page.getByText('Trail Map').click().catch(() => {});
  await page.waitForTimeout(3000);
  const box = await page.locator('svg[viewBox^="0 0 1000"]').boundingBox();
  const misses = [];
  for (const c of cases) {
    await page.mouse.move(box.x + (c.x / 100) * box.width, box.y + (c.y / 100) * box.height);
    await page.waitForTimeout(40);
    const got = await page.locator('[class*=tooltipName]').first().textContent({ timeout: 300 }).catch(() => null);
    if (!got || !got.includes(c.name)) misses.push(`${c.name} -> ${got ?? 'nothing'}`);
  }
  console.log(`${cases.length - misses.length}/${cases.length} hover points show the right name`);
  if (misses.length) console.log(misses.join('\n'));
  await browser.close();
})();
