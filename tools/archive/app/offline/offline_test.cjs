const { chromium } = require(process.env.PLAYWRIGHT_PATH);
const { spawn } = require('node:child_process');
const fs = require('node:fs');
const SCR = __dirname;
const DIST = '/home/user/myskiruns/dist';
let server;
let log = [];
const start = () =>
  new Promise((r) => {
    server = spawn('node', [SCR + '/serve.cjs', DIST, '4300']);
    server.stdout.on('data', (d) => {
      for (const l of String(d).split('\n').filter(Boolean)) {
        if (l.startsWith('listening')) r();
        else log.push(l);
      }
    });
  });
const stop = () => new Promise((r) => { server.on('exit', r); server.kill(); });
const maps = () => log.filter((l) => l.includes('/maps/'));
const mb = () => (log.reduce((s, l) => s + Number(l.split(' ').at(-1) || 0), 0) / 1e6).toFixed(2);

(async () => {
  await start();
  const browser = await chromium.launch();
  const ctx = await browser.newContext({ viewport: { width: 1400, height: 900 } });
  const page = await ctx.newPage();
  const overlay = () => page.locator('svg[viewBox^="0 0 1000"]').waitFor({ timeout: 15000 });
  const mapWidth = () => page.evaluate(() => document.querySelector('img[alt*="trail map"]')?.naturalWidth ?? null);

  log = [];
  await page.goto('http://localhost:4300/?resort=killington');
  await overlay();
  await page.waitForFunction(() => !!navigator.serviceWorker.controller, null, { timeout: 15000 });
  await page.waitForTimeout(5000);
  console.log(`A first visit: ${log.length} requests, ${mb()} MB`);
  console.log('  maps:', maps());

  await stop();
  await page.reload();
  await overlay();
  console.log('B offline reload, killington map width:', await mapWidth());

  await ctx.setOffline(true);
  await page.selectOption('select[aria-label="Resort"]', 'stowe');
  await page.waitForTimeout(2000);
  console.log('C offline, stowe never opened:', await page.evaluate(() => ({
    trails: document.body.innerText.match(/\/ (\d+) trails/)?.[1],
    message: document.querySelector('[class*=placeholderTitle]')?.textContent,
  })));
  await page.screenshot({ path: SCR + '/c-offline-stowe.png' });
  await start();
  await ctx.setOffline(false);
  await overlay();
  console.log('  back online, stowe map width:', await mapWidth());

  log = [];
  await page.goto('http://localhost:4300/?resort=vail');
  await overlay();
  await page.waitForTimeout(5000);
  console.log('D vail online, maps:', maps());
  await stop();
  for (const p of ['front-side', 'back-bowls', 'blue-sky']) {
    await page.goto('http://localhost:4300/?resort=vail&panel=' + p);
    await overlay();
    console.log(`  offline vail ${p} map width:`, await mapWidth());
  }

  const sw = fs.readFileSync(DIST + '/sw.js', 'utf8');
  fs.writeFileSync(DIST + '/sw.js', sw.replace(/"version":"[0-9a-f]+"/, '"version":"e2etest00001"'));
  await start();
  log = [];
  await page.goto('http://localhost:4300/?resort=killington');
  await overlay();
  for (let i = 0; i < 60; i++) {
    const k = await page.evaluate(() => caches.keys());
    if (k.length === 1 && k[0] === 'myskiruns-e2etest00001') break;
    await page.waitForTimeout(500);
  }
  console.log('E new deploy, caches:', await page.evaluate(() => caches.keys()));
  console.log('  map requests:', maps());
  await stop();
  for (const r of ['killington', 'vail']) {
    await page.goto('http://localhost:4300/?resort=' + r);
    await overlay();
    console.log(`  offline after deploy ${r} map width:`, await mapWidth());
  }
  fs.writeFileSync(DIST + '/sw.js', sw);
  await browser.close();
})().catch(async (e) => {
  console.error(e);
  try { await stop(); } catch {}
  process.exit(1);
});
