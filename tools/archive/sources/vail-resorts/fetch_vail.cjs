// node fetch_vail.cjs <page-url> <outprefix>: open the resort's trail-map page in a real browser, list the
// map PDFs it links, and download the winter trail map PDF with the page as referer.
const { chromium } = require(process.env.PLAYWRIGHT_PATH);
(async () => {
  const [pageUrl, out] = process.argv.slice(2);
  const browser = await chromium.launch({ headless: true, proxy: { server: process.env.HTTPS_PROXY }, args: ['--disable-blink-features=AutomationControlled', '--ignore-certificate-errors-spki-list=' + process.env.SPKI] });
  const ctx = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    locale: 'en-US', viewport: { width: 1366, height: 900 },
  });
  const page = await ctx.newPage();
  await page.addInitScript(() => Object.defineProperty(navigator, 'webdriver', { get: () => undefined }));
  const r = await page.goto(pageUrl, { waitUntil: 'domcontentloaded', timeout: 90000 });
  console.log('status', r && r.status());
  await page.waitForTimeout(8000);
  console.log('title', await page.title());
  const links = [...new Set(await page.$$eval('a', (as) => as.map((a) => a.href)))].filter((h) => /\.pdf|scene7/i.test(h));
  console.log(JSON.stringify(links, null, 1));
  const winter = links.find((h) => /winter-trail_map.*\.pdf/i.test(h)) || links.find((h) => /winter.*\.pdf/i.test(h));
  if (winter) {
    // fetch through the page itself (the browser's own network stack and cookies)
    const b64 = await page.evaluate(async (u) => {
      const r = await fetch(u, { credentials: 'include' });
      const ct = r.headers.get('content-type');
      const buf = new Uint8Array(await r.arrayBuffer());
      let s = '';
      for (let i = 0; i < buf.length; i += 0x8000) s += String.fromCharCode.apply(null, buf.subarray(i, i + 0x8000));
      return JSON.stringify({ status: r.status, ct, data: btoa(s) });
    }, winter);
    const o = JSON.parse(b64);
    console.log('pdf', o.status, o.ct, winter, o.data.length);
    if (o.status === 200) require('fs').writeFileSync(out + '.pdf', Buffer.from(o.data, 'base64'));
  }
  await browser.close();
})().catch((e) => { console.error(e); process.exit(1); });
