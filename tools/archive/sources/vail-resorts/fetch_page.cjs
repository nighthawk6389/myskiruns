const { chromium } = require(process.env.PLAYWRIGHT_PATH);
(async () => {
  const browser = await chromium.launch({ headless: true, proxy: { server: process.env.HTTPS_PROXY }, args: ['--disable-blink-features=AutomationControlled', '--ignore-certificate-errors-spki-list=' + process.env.SPKI] });
  const ctx = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    locale: 'en-US', viewport: { width: 1366, height: 900 },
  });
  const page = await ctx.newPage();
  await page.addInitScript(() => Object.defineProperty(navigator, 'webdriver', { get: () => undefined }));
  const seen = new Set();
  page.on('response', (r) => { const u = r.url(); if (/\.(pdf|jpe?g|png)(\?|$)/i.test(u) && /map/i.test(u)) seen.add(r.status() + ' ' + u); });
  for (const url of process.argv.slice(2)) {
    try {
      const r = await page.goto(url, { waitUntil: 'networkidle', timeout: 60000 });
      console.log('==', url, r && r.status(), await page.title());
      const links = await page.$$eval('a', (as) => as.map((a) => a.href).filter((h) => /\.pdf|trail.?map|map/i.test(h)));
      console.log('links', JSON.stringify([...new Set(links)].slice(0, 30)));
    } catch (e) { console.log('ERR', url, String(e).slice(0, 200)); }
  }
  console.log('resources', JSON.stringify([...seen].slice(0, 40), null, 0));
  await browser.close();
})().catch((e) => { console.error(e); process.exit(1); });
