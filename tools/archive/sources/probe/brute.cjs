// node brute.cjs <page url> <url template with {D}> <from YYYYMMDD> <to YYYYMMDD>: fetch each dated URL from inside the page, print hits
const { chromium } = require(process.env.PLAYWRIGHT_PATH);
(async () => {
  const [pageUrl, tmpl, from, to] = process.argv.slice(2);
  const dates = [];
  const d = new Date(Date.UTC(+from.slice(0, 4), +from.slice(4, 6) - 1, +from.slice(6, 8)));
  const e = new Date(Date.UTC(+to.slice(0, 4), +to.slice(4, 6) - 1, +to.slice(6, 8)));
  for (; d <= e; d.setUTCDate(d.getUTCDate() + 1)) dates.push(d.toISOString().slice(0, 10).replace(/-/g, ''));
  const urls = [];
  for (const t of tmpl.split('|')) for (const x of dates) urls.push(t.replace('{D}', x));
  const args = process.env.PIN ? [`--ignore-certificate-errors-spki-list=${process.env.PIN}`] : [];
  const b = await chromium.launch({ proxy: { server: process.env.HTTPS_PROXY }, args });
  const p = await b.newPage();
  try { await p.goto(pageUrl, { waitUntil: 'domcontentloaded', timeout: 60000 }); } catch (e) { console.log('goto:', e.message.split('\n')[0]); }
  const res = await p.evaluate(async (urls) => {
    const out = [];
    for (let i = 0; i < urls.length; i += 12) {
      const part = await Promise.all(urls.slice(i, i + 12).map(async (u) => {
        try { const r = await fetch(u, { method: 'HEAD' }); return [u, r.status, r.headers.get('content-type'), r.headers.get('content-length')]; } catch (e) { return [u, 'ERR', e.message, '']; }
      }));
      out.push(...part);
    }
    return out;
  }, urls);
  const st = {};
  for (const [u, s, t, l] of res) { st[s] = (st[s] || 0) + 1; if (s !== 404) console.log(s, t, l, u); }
  console.log('statuses', JSON.stringify(st), 'tried', urls.length);
  await b.close();
})();
