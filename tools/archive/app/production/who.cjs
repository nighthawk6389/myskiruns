const { chromium } = require(process.env.PLAYWRIGHT_PATH);
const { spawn } = require('node:child_process');
const SCR = '/tmp/claude-0/-home-user-myskiruns/6d543bfc-3ab1-5e7f-9c64-5c2d6dd5c830/scratchpad';
(async () => {
  let server;
  await new Promise((r) => { server = spawn('node', [`${SCR}/offline/serve.cjs`, `${SCR}/dist-new`, '4403']); server.stdout.on('data', (d) => String(d).includes('listening') && r()); });
  const browser = await chromium.launch();
  const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, serviceWorkers: process.env.NOSW ? 'block' : 'allow' });
  const t0 = Date.now();
  const t = () => ((Date.now() - t0) / 1000).toFixed(2);
  ctx.on('request', (req) => {
    if (/maps|sw\.js|assets\/stowe/.test(req.url())) console.log(t(), 'request', req.serviceWorker() ? '[from SW]' : '[page]', req.resourceType(), new URL(req.url()).pathname);
  });
  ctx.on('serviceworker', () => console.log(t(), 'service worker created'));
  const page = await ctx.newPage();
  const cdp = await ctx.newCDPSession(page);
  await cdp.send('Network.enable');
  await cdp.send('Network.emulateNetworkConditions', { offline: false, latency: 150, downloadThroughput: 500000, uploadThroughput: 125000 });
  page.on('console', (m) => console.log(t(), 'console', m.text()));
  await page.exposeFunction('mark', (s) => console.log(t(), 'page:', s));
  await page.addInitScript(() => {
    navigator.serviceWorker?.addEventListener('controllerchange', () => window.mark('controllerchange'));
    window.addEventListener('load', () => window.mark('window load'));
    new MutationObserver((ms) => {
      for (const m of ms) {
        for (const n of m.addedNodes) if (n.nodeType === 1 && (n.matches?.('img[alt*="trail map"]') || n.querySelector?.('img[alt*="trail map"]'))) window.mark('map <img> added');
        for (const n of m.removedNodes) if (n.nodeType === 1 && (n.matches?.('img[alt*="trail map"]') || n.querySelector?.('img[alt*="trail map"]'))) window.mark('map <img> removed');
        if (m.type === 'attributes' && m.target.matches?.('img[alt*="trail map"]')) window.mark(`map <img> ${m.attributeName} changed`);
      }
    }).observe(document, { childList: true, subtree: true, attributes: true, attributeFilter: ['src'] });
  });
  await page.goto('http://localhost:4403/?resort=stowe');
  await page.locator('svg[viewBox^="0 0 1000"]').waitFor({ timeout: 120000 });
  console.log(t(), 'overlay shown');
  await page.waitForTimeout(6000);
  await browser.close(); server.kill();
})();
