// Usage: node fetch_page.cjs <url> <outdir> [waitMs]
// Opens a page in headless Chromium through the agent proxy, saves the final HTML,
// every JSON/JS-ish network response body, and a list of all requests.
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const { chromium } = require(process.env.PLAYWRIGHT_PATH || execSync('npm root -g').toString().trim() + '/playwright');

const PIN = execSync(
  "openssl x509 -in /root/.ccr/agent-proxy-ca.crt -pubkey -noout | openssl pkey -pubin -outform der | openssl dgst -sha256 -binary | base64"
).toString().trim();

(async () => {
  const url = process.argv[2];
  const outdir = process.argv[3];
  const waitMs = parseInt(process.argv[4] || '15000', 10);
  fs.mkdirSync(outdir, { recursive: true });
  const browser = await chromium.launch({
    headless: true,
    proxy: { server: process.env.HTTPS_PROXY },
    args: [`--ignore-certificate-errors-spki-list=${PIN}`],
  });
  const context = await browser.newContext({
    userAgent:
      'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    locale: 'en-US',
    viewport: { width: 1400, height: 1000 },
  });
  const page = await context.newPage();
  const log = [];
  let n = 0;
  page.on('response', async (resp) => {
    try {
      const u = resp.url();
      const ct = (resp.headers()['content-type'] || '').toLowerCase();
      const entry = { url: u, status: resp.status(), ct };
      log.push(entry);
      if (ct.includes('json') || /trail|terrain|lift|run|feed|status/i.test(u)) {
        if (ct.includes('image') || ct.includes('font') || ct.includes('css')) return;
        const body = await resp.body().catch(() => null);
        if (body && body.length > 0) {
          const fn = `resp_${String(n++).padStart(3, '0')}.${ct.includes('json') ? 'json' : 'txt'}`;
          fs.writeFileSync(path.join(outdir, fn), body);
          entry.saved = fn;
          entry.size = body.length;
        }
      }
    } catch (e) {}
  });
  let status = null;
  try {
    const r = await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 90000 });
    status = r ? r.status() : null;
  } catch (e) {
    console.error('goto error', e.message);
  }
  await page.waitForTimeout(waitMs);
  try {
    await page.waitForLoadState('networkidle', { timeout: 20000 });
  } catch (e) {}
  const html = await page.content();
  fs.writeFileSync(path.join(outdir, 'page.html'), html);
  const title = await page.title();
  const text = await page.evaluate(() => document.body ? document.body.innerText : '');
  fs.writeFileSync(path.join(outdir, 'page.txt'), text);
  fs.writeFileSync(path.join(outdir, 'network.json'), JSON.stringify(log, null, 1));
  console.log(JSON.stringify({ status, title, htmlLen: html.length, textLen: text.length, responses: log.length, saved: log.filter(e => e.saved).length }));
  await browser.close();
})();
