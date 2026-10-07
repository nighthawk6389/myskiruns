const { chromium } = require(process.env.PLAYWRIGHT_PATH);
const { spawn } = require('node:child_process');
const SCR = '/tmp/claude-0/-home-user-myskiruns/6d543bfc-3ab1-5e7f-9c64-5c2d6dd5c830/scratchpad';
let server; const log = []; const t0 = Date.now();
(async () => {
  await new Promise((r) => { server = spawn('node', [`${SCR}/offline/serve.cjs`, `${SCR}/dist-new`, '4402']); server.stdout.on('data', (d) => { for (const l of String(d).split('\n').filter(Boolean)) l.startsWith('listening') ? r() : log.push(`${((Date.now() - t0) / 1000).toFixed(1)}s ${l}`); }); });
  const browser = await chromium.launch();
  for (const throttle of [null, { down: 4, rtt: 150 }]) {
    log.length = 0;
    const ctx = await browser.newContext({ viewport: { width: 390, height: 844 } });
    const page = await ctx.newPage();
    if (throttle) {
      const cdp = await ctx.newCDPSession(page);
      await cdp.send('Network.enable');
      await cdp.send('Network.emulateNetworkConditions', { offline: false, latency: throttle.rtt, downloadThroughput: (throttle.down * 1e6) / 8, uploadThroughput: 125000 });
    }
    await page.goto('http://localhost:4402/?resort=stowe');
    await page.locator('svg[viewBox^="0 0 1000"]').waitFor({ timeout: 120000 });
    await page.waitForTimeout(15000);
    console.log(`== ${throttle ? '4 Mbps' : 'unthrottled'}:`, log.filter((l) => l.includes('/maps/') || l.includes('sw.js')).join(' | '));
    await ctx.close();
  }
  await browser.close(); server.kill();
})();
