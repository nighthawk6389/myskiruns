const { chromium } = require(process.env.PLAYWRIGHT_PATH);
const { spawn } = require('node:child_process');
let server;
const start = () => new Promise((r) => { server = spawn('node', [__dirname + '/serve.cjs', '/home/user/myskiruns/dist', '4300']); server.stdout.on('data', (d) => String(d).includes('listening') && r()); });
const stop = () => new Promise((r) => { server.on('exit', r); server.kill(); });
(async () => {
  await start();
  const browser = await chromium.launch();
  const ctx = await browser.newContext({ serviceWorkers: 'block', viewport: { width: 1200, height: 800 } });
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', (e) => errors.push(e.message));
  await page.goto('http://localhost:4300/?resort=killington');
  await page.locator('svg[viewBox^="0 0 1000"]').waitFor({ timeout: 15000 });
  await stop();
  await page.selectOption('select[aria-label="Resort"]', 'okemo');
  await page.getByText("Couldn't load Okemo").waitFor({ timeout: 10000 });
  console.log('error screen:', (await page.locator('[class*=splash]').innerText()).replace(/\n+/g, ' | '));
  await page.screenshot({ path: __dirname + '/load-error.png' });
  // another never-opened resort, still offline: its own error, not Okemo's
  await page.selectOption('select[aria-label="Resort"]', 'stowe');
  await page.getByText("Couldn't load Stowe").waitFor({ timeout: 10000 });
  console.log('then stowe offline:', (await page.locator('[class*=splash]').innerText()).replace(/\n+/g, ' | '));
  await start();
  // back online, picking a resort loads it without a reload
  await page.selectOption('select[aria-label="Resort"]', 'whiteface');
  await page.locator('img[alt="Whiteface trail map"]').waitFor({ timeout: 15000 });
  console.log('online again, whiteface loads in place');
  await page.selectOption('select[aria-label="Resort"]', 'okemo');
  await Promise.all([page.waitForURL(/resort=okemo/), page.getByRole("button", { name: "Try again" }).click()]);
  await page.locator('svg[viewBox^="0 0 1000"]').waitFor({ timeout: 15000 });
  console.log('after retry, picker shows:', await page.locator('select[aria-label="Resort"]').inputValue(), '| trails:', await page.evaluate(() => document.body.innerText.match(/\/ (\d+) trails/)?.[1]));
  // switching while online keeps the current resort on screen until the next has loaded
  await page.selectOption('select[aria-label="Resort"]', 'jay-peak');
  await page.locator('img[alt="Jay Peak trail map"]').waitFor({ timeout: 15000 });
  console.log('switched to jay peak; page errors:', errors.length ? errors : 'none');
  await stop();
  await browser.close();
})().catch(async (e) => { console.error(e); try { await stop(); } catch {} process.exit(1); });
