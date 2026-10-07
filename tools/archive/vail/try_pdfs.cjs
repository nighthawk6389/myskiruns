// node try_pdfs.cjs <page-url> <url>... : from inside the page, HEAD/GET each candidate and save the PDFs that exist.
const { chromium } = require(process.env.PLAYWRIGHT_PATH);
(async () => {
  const [pageUrl, ...cands] = process.argv.slice(2);
  const browser = await chromium.launch({ headless: true, proxy: { server: process.env.HTTPS_PROXY }, args: ['--disable-blink-features=AutomationControlled', '--ignore-certificate-errors-spki-list=' + process.env.SPKI] });
  const ctx = await browser.newContext({ userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36', locale: 'en-US' });
  const page = await ctx.newPage();
  await page.addInitScript(() => Object.defineProperty(navigator, 'webdriver', { get: () => undefined }));
  await page.goto(pageUrl, { waitUntil: 'domcontentloaded', timeout: 90000 });
  await page.waitForTimeout(6000);
  for (const u of cands) {
    const res = await page.evaluate(async (u) => {
      try {
        const r = await fetch(u, { credentials: 'include' });
        const ct = r.headers.get('content-type') || '';
        if (r.status !== 200 || !/pdf/.test(ct)) return JSON.stringify({ status: r.status, ct });
        const buf = new Uint8Array(await r.arrayBuffer());
        let s = '';
        for (let i = 0; i < buf.length; i += 0x8000) s += String.fromCharCode.apply(null, buf.subarray(i, i + 0x8000));
        return JSON.stringify({ status: r.status, ct, data: btoa(s) });
      } catch (e) { return JSON.stringify({ err: String(e) }); }
    }, u);
    const o = JSON.parse(res);
    console.log(o.status, o.ct || o.err, u, o.data ? o.data.length : '');
    if (o.data) require('fs').writeFileSync(u.split('/').pop(), Buffer.from(o.data, 'base64'));
  }
  await browser.close();
})().catch((e) => { console.error(e); process.exit(1); });
