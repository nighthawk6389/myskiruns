// The upgrade production users will go through: the live build (b0ca176,
// service worker v9, 11 maps precached) to the merged main, on one origin, in
// one browser profile. Then no signal.
const { chromium } = require(process.env.PLAYWRIGHT_PATH);
const { spawn } = require('node:child_process');
const fs = require('node:fs');
const SCR = '/tmp/claude-0/-home-user-myskiruns/6d543bfc-3ab1-5e7f-9c64-5c2d6dd5c830/scratchpad';
const URL_ = 'http://localhost:4400';
let server;
let log = [];
const serve = (root) =>
  new Promise((r) => {
    server = spawn('node', [`${SCR}/offline/serve.cjs`, root, '4400']);
    server.stdout.on('data', (d) => {
      for (const l of String(d).split('\n').filter(Boolean)) l.startsWith('listening') ? r() : log.push(l);
    });
  });
const stop = () => new Promise((r) => { server.on('exit', r); server.kill(); });
const until = async (what, fn, ms = 60000) => {
  const end = Date.now() + ms;
  for (;;) { const v = await fn(); if (v) return v; if (Date.now() > end) throw new Error(`timed out: ${what}`); await new Promise((r) => setTimeout(r, 300)); }
};
const mb = (lines) => (lines.reduce((s, l) => s + Number(l.split(' ').at(-1) || 0), 0) / 1e6).toFixed(2);

(async () => {
  const profile = `${__dirname}/profile-upgrade`;
  fs.rmSync(profile, { recursive: true, force: true });
  const errors = [];

  // 1. today's production: open Killington, log two runs, let the old worker precache
  await serve(`${SCR}/dist-old`);
  const ctx = await chromium.launchPersistentContext(profile, { viewport: { width: 1300, height: 900 } });
  const page = ctx.pages()[0] ?? (await ctx.newPage());
  page.on('pageerror', (e) => errors.push(e.message));
  await page.goto(`${URL_}/?resort=killington`);
  await page.locator('svg[viewBox^="0 0 1000"]').waitFor({ timeout: 30000 });
  const boxes = page.getByRole('checkbox', { name: /^Skied .* this trip$/ });
  console.log('checkboxes in the list:', await boxes.count(), '| first:', await boxes.nth(0).getAttribute('aria-label'), '| fourth:', await boxes.nth(3).getAttribute('aria-label'));
  await boxes.nth(0).click();
  await boxes.nth(3).click();
  await page.waitForTimeout(500);
  console.log('stored after two clicks:', await page.evaluate(() => localStorage.getItem('myskiruns.trips')));
  await until('old worker in control', () => page.evaluate(() => !!navigator.serviceWorker.controller));
  const oldCached = await until('old precache done', () =>
    page.evaluate(async () => {
      const keys = await (await caches.open('myskiruns-v9')).keys();
      return keys.length >= 13 ? keys.map((k) => new URL(k.url).pathname) : null;
    }),
  );
  const marked = () => page.evaluate(() => document.querySelectorAll('[role=checkbox][aria-checked=true]').length);
  console.log(`1 old build: ${oldCached.filter((p) => p.startsWith('/maps/')).length} maps precached by v9; first visit ${mb(log)} MB; runs marked: ${await marked()}`);

  // 2. deploy the merged main to the same origin; the user opens the app online
  await stop();
  await serve(`${SCR}/dist-new`);
  log = [];
  await page.reload();
  await page.locator('svg[viewBox^="0 0 1000"]').waitFor({ timeout: 30000 });
  console.log(`2 after the deploy, runs still marked: ${await marked()}`);
  console.log('  stored after the deploy:', await page.evaluate(() => localStorage.getItem('myskiruns.trips')));
  const version = JSON.parse(fs.readFileSync(`${SCR}/dist-new/sw.js`, 'utf8').match(/const BUILD = (.*);/)[1]).version;
  await until('new worker replaced the old cache', () =>
    page.evaluate(async (v) => {
      const k = await caches.keys();
      return k.length === 1 && k[0] === `myskiruns-${v}`;
    }, version),
  );
  const newCached = await page.evaluate(async () => (await (await caches.open((await caches.keys())[0])).keys()).map((k) => new URL(k.url).pathname));
  const mapLines = log.filter((l) => l.includes('/maps/'));
  console.log(`  update downloaded ${mb(log)} MB; map requests: ${mapLines.length} (${mapLines.filter((l) => l.includes(' 304 ')).length} answered 304)`);
  console.log(`  new cache holds ${newCached.filter((p) => p.startsWith('/maps/')).length} maps and ${newCached.filter((p) => p.startsWith('/assets/')).length} scripts/styles`);

  // 3. no signal: server gone and browser offline
  await stop();
  await ctx.setOffline(true);
  await page.reload();
  await page.locator('svg[viewBox^="0 0 1000"]').waitFor({ timeout: 30000 });
  console.log(`3 offline reload: Killington map shown, runs marked: ${await marked()}`);
  await page.selectOption('select[aria-label="Resort"]', 'okemo');
  await page.locator('img[alt="Okemo trail map"]').waitFor({ timeout: 15000 });
  await page.locator('svg[viewBox^="0 0 1000"]').waitFor({ timeout: 15000 });
  console.log('  offline, Okemo (never opened, precached by the old worker): map shown');
  await page.getByRole('checkbox', { name: /^Skied .* this trip$/ }).nth(0).click();
  console.log(`  logged a run at Okemo offline; trips stored: ${await page.evaluate(() => JSON.parse(localStorage.getItem('myskiruns.trips')).trips.length)}`);
  console.log('page errors:', errors.length ? errors : 'none');
  await ctx.close();
})().catch(async (e) => {
  console.error(e);
  try { await stop(); } catch {}
  process.exit(1);
});
