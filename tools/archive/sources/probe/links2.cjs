// node links2.cjs <url> [regex]: print responses + img/a/source URLs matching regex (default scene7|pdf|trail|map)
const { chromium } = require(process.env.PLAYWRIGHT_PATH);
(async () => {
  const re = new RegExp(process.argv[3] || 'scene7|\\.pdf|trail|map', 'i');
  const args = process.env.PIN ? [`--ignore-certificate-errors-spki-list=${process.env.PIN}`] : [];
  const b = await chromium.launch({ proxy: { server: process.env.HTTPS_PROXY }, args });
  const p = await b.newPage({ viewport: { width: 1600, height: 1200 } });
  const seen = new Set();
  p.on('response', (r) => { const u = r.url(); if (re.test(u) && !seen.has(u) && !/\.(js|css|woff2?)(\?|$)/i.test(u)) { seen.add(u); console.log('RESP', r.status(), u.slice(0, 300)); } });
  try { await p.goto(process.argv[2], { waitUntil: 'networkidle', timeout: 60000 }); } catch (e) { console.log('goto:', e.message.split('\n')[0]); }
  await p.evaluate(async () => { for (let y = 0; y < document.body.scrollHeight; y += 800) { window.scrollTo(0, y); await new Promise(r => setTimeout(r, 250)); } });
  await p.waitForTimeout(2000);
  const urls = await p.evaluate(() => {
    const out = [];
    for (const a of document.querySelectorAll('a')) out.push(['A', a.href, (a.textContent || '').trim().slice(0, 60)]);
    for (const i of document.querySelectorAll('img, source')) out.push(['IMG', i.currentSrc || i.src || i.srcset || '', i.alt || '']);
    for (const e of document.querySelectorAll('[data-src],[data-srcset],[style*="background"]')) out.push(['DATA', e.getAttribute('data-src') || e.getAttribute('data-srcset') || e.getAttribute('style'), '']);
    return out;
  }).catch(() => []);
  const s2 = new Set();
  for (const [k, u, t] of urls) if (u && re.test(u) && !u.includes('#') && !s2.has(u)) { s2.add(u); console.log(k, u.slice(0, 300), '|', t.replace(/\s+/g, ' ')); }
  console.log('TITLE', await p.title());
  await b.close();
})();
