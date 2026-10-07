const { chromium } = require(process.env.PLAYWRIGHT_PATH);
const APP = 'http://localhost:4310/?resort=stowe';
(async () => {
  const browser = await chromium.launch();
  const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, isMobile: process.env.MOBILE === '1', hasTouch: process.env.MOBILE === '1' });
  const page = await ctx.newPage();
  page.on('console', (m) => console.log('console:', m.type(), m.text().slice(0, 200)));
  page.on('requestfailed', (r) => console.log('failed:', r.url(), r.failure()?.errorText));
  await page.goto(APP);
  await page.getByRole('checkbox', { name: 'Skied Bypass this trip' }).waitFor();
  await page.waitForFunction(() => !!navigator.serviceWorker.controller, null, { timeout: 20000 });
  console.log('caches:', await page.evaluate(async () => {
    const out = [];
    for (const k of await caches.keys()) out.push([k, (await (await caches.open(k)).keys()).map((r) => new URL(r.url).pathname)]);
    return JSON.stringify(out);
  }));
  if (process.env.STOP === '1') process.kill(Number(require('node:fs').readFileSync(__dirname + '/preview.pid', 'utf8')));
  await ctx.setOffline(true);
  await page.reload().catch((e) => console.log('reload error', e.message));
  await page.waitForTimeout(3000);
  console.log('body:', JSON.stringify((await page.evaluate(() => document.body.innerHTML)).slice(0, 300)));
  await browser.close();
})();
