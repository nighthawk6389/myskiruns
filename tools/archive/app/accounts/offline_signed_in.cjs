const { chromium } = require(process.env.PLAYWRIGHT_PATH);
const { spawn } = require('node:child_process');
const MOCK = 'http://localhost:54321';
const APP = 'http://localhost:4310/?resort=stowe';
const EMAIL = `phone-${Date.now()}@example.com`;
const SCR = '/tmp/claude-0/-home-user-myskiruns/6d543bfc-3ab1-5e7f-9c64-5c2d6dd5c830/scratchpad';
const until = async (what, fn, ms = 20000) => {
  const end = Date.now() + ms;
  for (;;) { const v = await fn(); if (v) return v; if (Date.now() > end) throw new Error(`timed out: ${what}`); await new Promise((r) => setTimeout(r, 250)); }
};
const PIDFILE = `${__dirname}/preview.pid`;
const stopPreview = () => process.kill(Number(require('node:fs').readFileSync(PIDFILE, 'utf8')));
const startPreview = () => {
  const child = spawn('node', ['node_modules/vite/bin/vite.js', 'preview', '--port', '4310', '--strictPort', '--outDir', `${SCR}/dist-acct`], {
    cwd: '/home/user/myskiruns', detached: true, stdio: 'ignore',
    env: { ...process.env, SUPABASE_URL: MOCK, VITE_SUPABASE_ANON_KEY: 'anon-key', SUPABASE_SERVICE_ROLE_KEY: 'service-key' },
  });
  child.unref();
  require('node:fs').writeFileSync(PIDFILE, String(child.pid));
  return until('preview up', () => fetch('http://localhost:4310/').then((r) => r.ok, () => false));
};
const local = (page) => page.evaluate(() => localStorage.getItem('myskiruns.trips'));
const saved = async () => (await (await fetch(`${MOCK}/__debug`)).json()).rows.flatMap((r) => r.trips.flatMap((t) => t.runs.map((x) => x.trailId))).sort();

(async () => {
  const browser = await chromium.launch();
  const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', (e) => errors.push(e.message));
  await page.goto(APP);
  await page.getByRole('checkbox', { name: 'Skied Bypass this trip' }).waitFor();
  await page.waitForFunction(() => !!navigator.serviceWorker.controller, null, { timeout: 20000 });
  await page.getByRole('button', { name: 'Trip options' }).click();
  await page.screenshot({ path: `${__dirname}/m1-menu.png` });
  await page.getByRole('menuitem', { name: /Sign in to back up/ }).click();
  await page.getByLabel('Email').fill(EMAIL);
  await page.getByRole('button', { name: 'Email me a code' }).click();
  await page.getByLabel('Code').waitFor();
  const { code } = await (await fetch(`${MOCK}/__debug/code?email=${EMAIL}`)).json();
  await page.getByLabel('Code').fill(code);
  await page.screenshot({ path: `${__dirname}/m2-code.png` });
  await page.getByRole('button', { name: 'Sign in' }).click();
  await page.getByText(/^Synced /).waitFor({ timeout: 15000 });
  await page.screenshot({ path: `${__dirname}/m3-account.png` });
  await page.getByRole('button', { name: 'Close' }).click();
  await page.getByRole('checkbox', { name: 'Skied Bypass this trip' }).click();
  await until('first run saved', async () => (await saved()).includes('bypass'));
  console.log('local after bypass:', await local(page));
  await page.waitForTimeout(3000);
  console.log('local 3s later:', await local(page));

  // no signal: the server is gone and the phone is offline; reopen the app
  stopPreview();
  await ctx.setOffline(true);
  await page.reload().catch((e) => console.log('reload error:', e.message));
  await page.waitForTimeout(3000);
  console.log('local after offline reload:', await local(page));
  await page.screenshot({ path: `${__dirname}/m-offline-reload.png` });
  await page.getByRole('checkbox', { name: 'Skied Centerline this trip' }).click();
  await page.getByRole('button', { name: 'Trip options' }).click();
  await page.getByRole('menuitem', { name: 'Account & sync' }).click();
  const status = await page.locator('[role=status]').innerText();
  console.log('offline reopen, account dialog says:', status);
  await page.screenshot({ path: `${__dirname}/m4-offline.png` });
  await page.getByRole('button', { name: 'Close' }).click();

  // signal again: the offline run reaches the account
  await startPreview();
  await ctx.setOffline(false);
  await until('offline run saved', async () => (await saved()).includes('centerline'));
  console.log('back online, account has runs:', await saved());
  console.log('page errors:', errors.length ? errors : 'none');
  await browser.close();
})().catch((e) => { console.error(e); process.exit(1); });
