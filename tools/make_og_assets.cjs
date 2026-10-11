// The link previews' fixed pictures, drawn in Chromium so the type is the app's:
//   public/og/default.jpg  1200 x 630: the preview of the site itself (index.html's og:image)
//   public/og/badge.png    the "My Ski Runs" badge api/og.ts puts in the corner of a map preview
// Rerun after changing the wording, the number of resorts, or the map it shows (Killington's):
//
//   PLAYWRIGHT_PATH=$(npm root -g)/playwright node tools/make_og_assets.cjs
const { chromium } = require(process.env.PLAYWRIGHT_PATH || 'playwright');
const fs = require('node:fs');
const path = require('node:path');

const root = path.resolve(__dirname, '..');
const out = path.join(root, 'public/og');
fs.mkdirSync(out, { recursive: true });
const resorts = (fs.readFileSync(path.join(root, 'src/resorts.ts'), 'utf8').match(/\n {2}(oneMap|panels)\('/g) || []).length;
const map = `data:image/jpeg;base64,${fs.readFileSync(path.join(root, 'public/maps/killington.jpg')).toString('base64')}`;
const font = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif";

const site = `<!doctype html><html><body style="margin:0;width:1200px;height:630px;overflow:hidden;font-family:${font}">
<div style="position:absolute;inset:0;background:url(${map}) 58% 40%/170% auto no-repeat"></div>
<div style="position:absolute;inset:0;background:linear-gradient(90deg,rgba(15,23,42,.96) 0%,rgba(15,23,42,.86) 42%,rgba(15,23,42,.15) 75%,rgba(15,23,42,0) 100%)"></div>
<div style="position:absolute;left:72px;top:96px;width:620px;color:#f1f5f9">
  <div style="color:#fbbf24;font-weight:800;font-size:30px;letter-spacing:.04em">⛷&nbsp; MY SKI RUNS</div>
  <div style="margin-top:28px;font-weight:800;font-size:72px;line-height:1.05">Track every run you ski</div>
  <div style="margin-top:28px;font-size:30px;line-height:1.35;color:#cbd5e1">Tap the runs on your resort's own trail map, trip by trip, and see what's left.</div>
  <div style="margin-top:36px;font-size:24px;font-weight:700;color:#fbbf24">${resorts} resorts · Free · Works offline</div>
</div></body></html>`;

const badge = `<!doctype html><html><body style="margin:0;background:transparent;font-family:${font}">
<div id="b" style="display:inline-flex;align-items:center;height:72px;padding:0 26px;border-radius:36px;background:rgba(15,23,42,.88);
  color:#fbbf24;font-weight:800;font-size:28px;letter-spacing:.03em;white-space:nowrap">⛷&nbsp; MY SKI RUNS</div></body></html>`;

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1200, height: 630 } });
  await page.setContent(site);
  await page.screenshot({ path: path.join(out, 'default.jpg'), type: 'jpeg', quality: 85 });
  await page.setContent(badge);
  await page.locator('#b').screenshot({ path: path.join(out, 'badge.png'), omitBackground: true });
  await browser.close();
  for (const f of ['default.jpg', 'badge.png']) console.log(`public/og/${f}: ${Math.round(fs.statSync(path.join(out, f)).size / 1024)} KB`);
})();
