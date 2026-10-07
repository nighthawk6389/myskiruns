// First visit on a slow connection: today's production build vs merged main.
// The server throttles one shared link (page and service worker alike) and
// counts every byte sent in the first 60 s.
const { chromium } = require(process.env.PLAYWRIGHT_PATH);
const { spawn } = require('node:child_process');
const SCR = '/tmp/claude-0/-home-user-myskiruns/6d543bfc-3ab1-5e7f-9c64-5c2d6dd5c830/scratchpad';
const NET = { slow: { down: 1.5, rtt: 300 }, mid: { down: 4, rtt: 150 } };
let server;
let log = [];
const serve = (root, net) =>
  new Promise((r) => {
    log = [];
    server = spawn('node', [`${SCR}/offline/serve.cjs`, root, '4401'], { env: { ...process.env, THROTTLE_MBPS: String(net.down), RTT_MS: String(net.rtt) } });
    server.stdout.on('data', (d) => {
      for (const l of String(d).split('\n').filter(Boolean)) l.startsWith('listening') ? r() : log.push(l);
    });
  });
const stop = () => new Promise((r) => { server.on('exit', r); server.kill(); });

async function visit(browser, root, net) {
  await serve(root, net);
  const ctx = await browser.newContext({ viewport: { width: 390, height: 844 } });
  const page = await ctx.newPage();
  const t0 = Date.now();
  await page.goto('http://localhost:4401/?resort=stowe', { waitUntil: 'commit' });
  await page.getByRole('checkbox', { name: /^Skied .* this trip$/ }).first().waitFor({ timeout: 120000 });
  const list = (Date.now() - t0) / 1000;
  await page.waitForFunction(() => ((i) => !!i && i.complete && i.naturalWidth > 0)(document.querySelector('img[alt*="trail map"]')), null, { timeout: 180000, polling: 100 });
  const map = (Date.now() - t0) / 1000;
  const left = 60000 - (Date.now() - t0);
  if (left > 0) await page.waitForTimeout(left);
  const bytes = log.reduce((s, l) => s + Number(l.split(' ').at(-1) || 0), 0) / 1e6;
  const maps = new Set(log.filter((l) => l.includes('/maps/')).map((l) => l.split(' ')[1])).size;
  await ctx.close();
  await stop();
  return { list, map, bytes, maps };
}

(async () => {
  const browser = await chromium.launch();
  for (const [name, net] of Object.entries(NET)) {
    for (const [label, root] of [['production (b0ca176)', `${SCR}/dist-old`], ['merged main', `${SCR}/dist-new`]]) {
      const r = await visit(browser, root, net);
      console.log(`${name} ${net.down} Mbps/${net.rtt} ms | ${label.padEnd(20)} | trail list ${r.list.toFixed(1)} s | map ${r.map.toFixed(1)} s | first minute ${r.bytes.toFixed(1)} MB, ${r.maps} map files`);
    }
  }
  await browser.close();
})().catch(async (e) => { console.error(e); try { await stop(); } catch {} process.exit(1); });
