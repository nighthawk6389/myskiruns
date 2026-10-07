// Find a resort's trail-map files from its own web page, in headless Chromium (Vail Resorts' sites, among others,
// return an error page to curl but serve a real browser): step 1 of docs/trail-map-playbook.md.
//
//   node tools/trailmap/find_source.cjs links <page url> [regex]
//       every response, link, image and data-src URL of the rendered page (scrolled to the bottom, so lazy images
//       load) that matches regex (default scene7|.pdf|trail|map): the map PDF, the CDN painting's name
//   node tools/trailmap/find_source.cjs try <page url> <url> [<url>...]
//       fetch each URL from inside the page (status, type, length): does a guessed PDF URL exist?
//   node tools/trailmap/find_source.cjs dates <page url> '<template with {D}>[|<template>...]' <from YYYYMMDD> <to YYYYMMDD>
//       try a dated file name for every day in the range (Vail Resorts' maps are named like
//       /-/aemasset/sitecore/<resort>/maps/winter-2025-2026/{D}_XX_winter-trail_map_001.pdf); prints the hits
//
// Then download with tools/trailmap/fetch_pdf.cjs (or plain curl where it works). PLAYWRIGHT_PATH defaults to
// $(npm root -g)/playwright; behind the agent proxy (HTTPS_PROXY) the proxy CA's pin is worked out from
// /root/.ccr/agent-proxy-ca.crt (or taken from PIN).
const { execSync } = require('child_process');
const fs = require('fs');
const { chromium } = require(process.env.PLAYWRIGHT_PATH || `${execSync('npm root -g').toString().trim()}/playwright`);

const CA = '/root/.ccr/agent-proxy-ca.crt';
const PIN = process.env.PIN || (fs.existsSync(CA) ? execSync(`openssl x509 -in ${CA} -pubkey -noout | openssl pkey -pubin `
  + '-outform der | openssl dgst -sha256 -binary | base64').toString().trim() : '');
const [cmd, pageUrl, ...rest] = process.argv.slice(2);
if (!['links', 'try', 'dates'].includes(cmd) || !pageUrl) {
  console.error('usage: find_source.cjs links|try|dates <page url> ...  (see the header)');
  process.exit(2);
}

(async () => {
  const browser = await chromium.launch({
    proxy: process.env.HTTPS_PROXY ? { server: process.env.HTTPS_PROXY } : undefined,
    args: PIN ? [`--ignore-certificate-errors-spki-list=${PIN}`] : [],
  });
  const page = await browser.newPage({ viewport: { width: 1600, height: 1200 } });
  try {
    if (cmd === 'links') {
      const re = new RegExp(rest[0] || 'scene7|\\.pdf|trail|map', 'i');
      const seen = new Set();
      page.on('response', (r) => {
        const u = r.url();
        if (re.test(u) && !seen.has(u) && !/\.(js|css|woff2?)(\?|$)/i.test(u)) {
          seen.add(u);
          console.log('RESP', r.status(), u.slice(0, 300));
        }
      });
      await page.goto(pageUrl, { waitUntil: 'networkidle', timeout: 60000 }).catch((e) => console.log('goto:', e.message.split('\n')[0]));
      await page.evaluate(async () => {
        for (let y = 0; y < document.body.scrollHeight; y += 800) {
          window.scrollTo(0, y);
          await new Promise((r) => setTimeout(r, 250));
        }
      }).catch(() => {});
      await page.waitForTimeout(2000);
      const urls = await page.evaluate(() => {
        const out = [];
        for (const a of document.querySelectorAll('a')) out.push(['A', a.href, (a.textContent || '').trim().slice(0, 60)]);
        for (const i of document.querySelectorAll('img, source')) out.push(['IMG', i.currentSrc || i.src || i.srcset || '', i.alt || '']);
        for (const e of document.querySelectorAll('[data-src],[data-srcset],[style*="background"]')) {
          out.push(['DATA', e.getAttribute('data-src') || e.getAttribute('data-srcset') || e.getAttribute('style'), '']);
        }
        return out;
      }).catch(() => []);
      const shown = new Set();
      for (const [k, u, t] of urls) {
        if (u && re.test(u) && !u.includes('#') && !shown.has(u)) {
          shown.add(u);
          console.log(k, u.slice(0, 300), '|', t.replace(/\s+/g, ' '));
        }
      }
      console.log('TITLE', await page.title());
    } else {
      await page.goto(pageUrl, { waitUntil: 'domcontentloaded', timeout: 60000 }).catch((e) => console.log('goto:', e.message.split('\n')[0]));
      let urls = rest;
      if (cmd === 'dates') {
        const [tmpl, from, to] = rest;
        const day = (s) => new Date(Date.UTC(+s.slice(0, 4), +s.slice(4, 6) - 1, +s.slice(6, 8)));
        const dates = [];
        for (let d = day(from); d <= day(to); d.setUTCDate(d.getUTCDate() + 1)) dates.push(d.toISOString().slice(0, 10).replace(/-/g, ''));
        urls = tmpl.split('|').flatMap((t) => dates.map((x) => t.replace('{D}', x)));
      }
      const res = await page.evaluate(async ([urls, method]) => {
        const out = [];
        for (let i = 0; i < urls.length; i += 12) {
          out.push(...await Promise.all(urls.slice(i, i + 12).map(async (u) => {
            try {
              const r = await fetch(u, { method });
              return [u, r.status, r.headers.get('content-type'), r.headers.get('content-length'), r.url];
            } catch (e) {
              return [u, 'ERR', e.message, '', ''];
            }
          })));
        }
        return out;
      }, [urls, cmd === 'dates' ? 'HEAD' : 'GET']);
      const tally = {};
      for (const [u, s, t, l, final] of res) {
        tally[s] = (tally[s] || 0) + 1;
        if (cmd === 'try' || s !== 404) console.log(s, t, `len=${l}`, u, final && final !== u ? `-> ${final}` : '');
      }
      console.log('statuses', JSON.stringify(tally), 'tried', urls.length);
    }
  } finally {
    await browser.close();
  }
})().catch((e) => {
  console.error(e.message);
  process.exit(1);
});
