// node fetch_status.cjs <terrain-status-url> <out.html>: save the rendered terrain status page (Vail sites).
const { chromium } = require(process.env.PLAYWRIGHT_PATH);
(async () => {
  const [url, out] = process.argv.slice(2);
  const browser = await chromium.launch({ headless: true, proxy: { server: process.env.HTTPS_PROXY }, args: ['--disable-blink-features=AutomationControlled', '--ignore-certificate-errors-spki-list=' + process.env.SPKI] });
  const ctx = await browser.newContext({ userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36', locale: 'en-US' });
  const page = await ctx.newPage();
  await page.addInitScript(() => Object.defineProperty(navigator, 'webdriver', { get: () => undefined }));
  const r = await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 90000 });
  console.log('status', r && r.status());
  await page.waitForTimeout(10000);
  console.log('title', await page.title());
  require('fs').writeFileSync(out, await page.content());
  await browser.close();
})().catch((e) => { console.error(e); process.exit(1); });
