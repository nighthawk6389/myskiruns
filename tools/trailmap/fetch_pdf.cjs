// Download a trail-map PDF (or a map image the page links) from inside the resort's own page in headless Chromium:
// Vail Resorts' sites (huntermtn.com, vail.com, ...) return an error page to curl, Crystal Mountain's a bot check.
//
//   PLAYWRIGHT_PATH=$(npm root -g)/playwright node tools/trailmap/fetch_pdf.cjs <page url> <pdf url> <out.pdf>
//
// Behind this sandbox's agent proxy (HTTPS_PROXY), Chromium needs the proxy CA's public-key pin: taken from PIN, or
// worked out from /root/.ccr/agent-proxy-ca.crt when that file exists (the playbook's Part 4 has the command).
const { chromium } = require(process.env.PLAYWRIGHT_PATH || 'playwright');
const { execSync } = require('child_process');
const fs = require('fs');

const CA = '/root/.ccr/agent-proxy-ca.crt';
const PIN = process.env.PIN || (fs.existsSync(CA) ? execSync(`openssl x509 -in ${CA} -pubkey -noout | openssl pkey -pubin `
  + '-outform der | openssl dgst -sha256 -binary | base64').toString().trim() : '');

const [pageUrl, pdfUrl, out] = process.argv.slice(2);
if (!out) {
  console.error('usage: fetch_pdf.cjs <page url> <pdf url> <out.pdf>');
  process.exit(2);
}
// the file's own signature, by its extension (a PDF, or an image the same pages link); any other kind of file is
// taken as it comes
// (an image may come as another format than its name says: a media server's WebP)
const IMAGES = ['\xff\xd8\xff', '\x89PNG', 'RIFF', 'GIF8'];
const KINDS = [[/\.pdf(\?|$)/i, ['%PDF-']], [/\.(jpe?g|png|webp|gif)(\?|$)/i, IMAGES]];
const kind = KINDS.find(([re]) => re.test(pdfUrl));
const isKind = (buf) => !kind || kind[1].some((m) => buf.subarray(0, m.length).toString('latin1') === m);
(async () => {
  const args = PIN ? [`--ignore-certificate-errors-spki-list=${PIN}`] : [];
  const proxy = process.env.HTTPS_PROXY ? { server: process.env.HTTPS_PROXY } : undefined;
  const browser = await chromium.launch({ proxy, args });
  try {
    const page = await browser.newPage();
    await page.goto(pageUrl, { waitUntil: 'domcontentloaded', timeout: 60000 });
    // a site behind a bot check (Crystal Mountain's Incapsula) answers the first requests with a small challenge
    // page instead of the file: load the page again, then ask again, until the bytes are the file's kind
    let data = null;
    for (let attempt = 0; attempt < 6 && !data; attempt++) {
      if (attempt) {  // the page again, so its bot check's script runs and sets its cookie
        await page.waitForTimeout(5000);
        await page.goto(pageUrl, { waitUntil: 'load', timeout: 60000 }).catch(() => {});
      }
      const b64 = await page.evaluate(async (u) => {
        const r = await fetch(u);
        if (!r.ok) return 'HTTP ' + r.status;
        const buf = new Uint8Array(await r.arrayBuffer());
        let s = '';
        for (let i = 0; i < buf.length; i += 0x8000) s += String.fromCharCode.apply(null, buf.subarray(i, i + 0x8000));
        return btoa(s);
      }, pdfUrl);
      if (b64.startsWith('HTTP')) throw new Error(`${pdfUrl}: ${b64}`);
      const buf = Buffer.from(b64, 'base64');
      if (isKind(buf)) data = buf;
      else console.log(`not the file yet (${buf.length} bytes): waiting for the page's bot check`);
    }
    if (!data) throw new Error(`${pdfUrl}: not the file after six tries`);
    fs.writeFileSync(out, data);
    console.log(`wrote ${out} (${fs.statSync(out).size} bytes)`);
  } finally {
    await browser.close();
  }
})().catch((e) => {
  console.error(e.message);
  process.exit(1);
});
