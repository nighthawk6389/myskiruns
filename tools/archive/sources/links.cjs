// node links.cjs <url> : list links and responses mentioning pdf/map/trail
const { chromium } = require(process.env.PLAYWRIGHT_PATH);
(async () => {
  const args = process.env.PIN ? [`--ignore-certificate-errors-spki-list=${process.env.PIN}`] : [];
  const b = await chromium.launch({ proxy: { server: process.env.HTTPS_PROXY }, args });
  const p = await b.newPage();
  const seen = new Set();
  p.on('response', (r) => { const u = r.url(); if ((/\.pdf|winter-trail/i.test(u)) && !seen.has(u)) { seen.add(u); console.log('RESP', r.status(), u); } });
  try { await p.goto(process.argv[2], { waitUntil: 'networkidle', timeout: 60000 }); } catch (e) { console.log('goto:', e.message.split('\n')[0]); }
  const links = await p.$$eval('a', (as) => as.map((a) => a.href)).catch(() => []);
  for (const l of [...new Set(links)]) if (/pdf|map/i.test(l)) console.log('LINK', l);
  console.log('TITLE', await p.title());
  await b.close();
})();
