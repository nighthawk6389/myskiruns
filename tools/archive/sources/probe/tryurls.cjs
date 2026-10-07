// node tryurls.cjs <page url> <url1> <url2> ...: fetch each URL from inside the page (HEAD-like: status, type, length)
const { chromium } = require(process.env.PLAYWRIGHT_PATH);
(async () => {
  const args = process.env.PIN ? [`--ignore-certificate-errors-spki-list=${process.env.PIN}`] : [];
  const b = await chromium.launch({ proxy: { server: process.env.HTTPS_PROXY }, args });
  const p = await b.newPage();
  try { await p.goto(process.argv[2], { waitUntil: 'domcontentloaded', timeout: 60000 }); } catch (e) { console.log('goto:', e.message.split('\n')[0]); }
  for (const u of process.argv.slice(3)) {
    const r = await p.evaluate(async (u) => { try { const r = await fetch(u, { method: 'GET' }); const t = r.headers.get('content-type'); const l = r.headers.get('content-length'); let n = -1; if (r.ok && /pdf/.test(t || '')) { n = (await r.arrayBuffer()).byteLength; } return `${r.status} ${t} len=${l} got=${n} final=${r.url}`; } catch (e) { return 'ERR ' + e.message; } }, u);
    console.log(r, '<-', u);
  }
  await b.close();
})();
