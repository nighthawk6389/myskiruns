// node fetch_links.cjs <url> <out.html>: save the rendered page and print every link/resource that mentions map/pdf.
const { chromium } = require(process.env.PLAYWRIGHT_PATH);
(async () => {
  const [url, out] = process.argv.slice(2);
  const browser = await chromium.launch({ headless: true, proxy: { server: process.env.HTTPS_PROXY }, args: ['--disable-blink-features=AutomationControlled', '--ignore-certificate-errors-spki-list=' + process.env.SPKI] });
  const ctx = await browser.newContext({ userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36', locale: 'en-US', viewport: { width: 1366, height: 900 } });
  const page = await ctx.newPage();
  await page.addInitScript(() => Object.defineProperty(navigator, 'webdriver', { get: () => undefined }));
  const seen = new Set();
  page.on('response', (r) => { const u = r.url(); if (/pdf|trail.?map/i.test(u)) seen.add(r.status() + ' ' + u); });
  const r = await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 90000 });
  console.log('status', r && r.status());
  await page.waitForTimeout(10000);
  const html = await page.content();
  require('fs').writeFileSync(out, html);
  const links = await page.$$eval('a', (as) => as.map((a) => [a.href, (a.innerText || '').trim().slice(0, 60)]));
  for (const [h, t] of links) if (/pdf|map/i.test(h + ' ' + t)) console.log('A', h, '|', t);
  const found = [...new Set((html.match(/https?:[^"' )]+?\.pdf/gi) || []))];
  console.log('pdf urls in html', JSON.stringify(found, null, 1));
  console.log('responses', JSON.stringify([...seen], null, 1));
  await browser.close();
})().catch((e) => { console.error(e); process.exit(1); });
