const { chromium } = require(process.env.PLAYWRIGHT_PATH);
const [url, resort, out] = process.argv.slice(2);
(async () => {
  const b = await chromium.launch();
  for (const [name, vp] of [['desktop', { width: 1400, height: 900 }], ['phone', { width: 390, height: 844 }]]) {
    const p = await b.newPage({ viewport: vp, deviceScaleFactor: 1 });
    const errors = [];
    p.on('pageerror', (e) => errors.push(e.message));
    await p.goto(`${url}?resort=${resort}`, { waitUntil: 'networkidle' });
    await p.waitForSelector('svg path, svg polyline', { timeout: 30000 });
    await p.waitForTimeout(1500);
    const sel = await p.$eval('select', (s) => s.options[s.selectedIndex].text).catch(() => '?');
    const opts = await p.$$eval('select option', (os) => os.map((o) => o.text)).catch(() => []);
    await p.screenshot({ path: `${out}_${name}.png` });
    console.log(name, 'selected:', sel, '| options:', opts.length, '| errors:', errors.length ? errors : 'none');
  }
  await b.close();
})();
