// Download a trail-map PDF from inside the resort's own page in headless Chromium: Vail Resorts' sites
// (huntermtn.com, vail.com, ...) return an error page to curl.
//
//   PLAYWRIGHT_PATH=$(npm root -g)/playwright node tools/trailmap/fetch_pdf.cjs <page url> <pdf url> <out.pdf>
//
// Behind this sandbox's agent proxy, set PIN to the proxy CA's public-key pin (the playbook's step 1 has the
// command); the proxy is taken from HTTPS_PROXY.
const { chromium } = require(process.env.PLAYWRIGHT_PATH || 'playwright');
const fs = require('fs');

const [pageUrl, pdfUrl, out] = process.argv.slice(2);
if (!out) {
  console.error('usage: fetch_pdf.cjs <page url> <pdf url> <out.pdf>');
  process.exit(2);
}
(async () => {
  const args = process.env.PIN ? [`--ignore-certificate-errors-spki-list=${process.env.PIN}`] : [];
  const proxy = process.env.HTTPS_PROXY ? { server: process.env.HTTPS_PROXY } : undefined;
  const browser = await chromium.launch({ proxy, args });
  try {
    const page = await browser.newPage();
    await page.goto(pageUrl, { waitUntil: 'domcontentloaded', timeout: 60000 });
    const b64 = await page.evaluate(async (u) => {
      const r = await fetch(u);
      if (!r.ok) return 'HTTP ' + r.status;
      const buf = new Uint8Array(await r.arrayBuffer());
      let s = '';
      for (let i = 0; i < buf.length; i += 0x8000) s += String.fromCharCode.apply(null, buf.subarray(i, i + 0x8000));
      return btoa(s);
    }, pdfUrl);
    if (b64.startsWith('HTTP')) throw new Error(`${pdfUrl}: ${b64}`);
    fs.writeFileSync(out, Buffer.from(b64, 'base64'));
    console.log(`wrote ${out} (${fs.statSync(out).size} bytes)`);
  } finally {
    await browser.close();
  }
})().catch((e) => {
  console.error(e.message);
  process.exit(1);
});
