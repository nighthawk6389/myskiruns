// Browser check of accounts: two devices sign in with an emailed code, sync,
// edit offline, delete a trip, delete the account. Runs against a build that
// points at scripts/mockSupabase.cjs (no real project or email needed):
//
//   node scripts/mockSupabase.cjs 54321 &
//   VITE_SUPABASE_URL=http://localhost:54321 VITE_SUPABASE_ANON_KEY=anon-key npm run build
//   (SUPABASE_URL=http://localhost:54321 VITE_SUPABASE_ANON_KEY=anon-key SUPABASE_SERVICE_ROLE_KEY=service-key \
//     npx vite preview --port 4310 --strictPort &)   # its own subshell; stop it by PID
//   PLAYWRIGHT_PATH=$(npm root -g)/playwright node tools/accounts_check.cjs [app url] [mock url] [screenshot dir]
//
// Rebuild without the VITE_SUPABASE_* variables afterwards: they are built in.
// Note: Playwright's offline mode doesn't stop a service worker's own
// requests; to check the app opening with no signal, stop the server too.
const { chromium } = require(process.env.PLAYWRIGHT_PATH || 'playwright');
const APP = `${process.argv[2] || 'http://localhost:4310/'}?resort=stowe`;
const MOCK = process.argv[3] || 'http://localhost:54321';
const SHOTS = process.argv[4] || null;
const EMAIL = `skier-${Date.now()}@example.com`;
const debug = async () => (await fetch(`${MOCK}/__debug`)).json();
const until = async (what, fn, ms = 15000) => {
  const end = Date.now() + ms;
  for (;;) {
    const v = await fn();
    if (v) return v;
    if (Date.now() > end) throw new Error(`timed out: ${what}`);
    await new Promise((r) => setTimeout(r, 250));
  }
};
// the trips a device holds (deleted ones are hidden in the app too)
const tripsOn = (page) =>
  page.evaluate(() => {
    const s = JSON.parse(localStorage.getItem('myskiruns.trips') ?? '{"trips":[]}');
    const live = (t) => !t.deletedAt || (t.updatedAt ?? t.createdAt) > t.deletedAt || t.runs.length > 0;
    return s.trips.filter(live).map((t) => `${t.name}: ${t.runs.map((r) => r.trailId).sort().join(',')}`).sort();
  });
// this run's account and its saved row (the stand-in may hold earlier runs')
const mine = async () => {
  const d = await debug();
  const user = d.users.find((u) => u.email === EMAIL);
  return { user, row: user && d.rows.find((r) => r.user_id === user.id) };
};
const savedTrips = async () => {
  const { row } = await mine();
  if (!row) return null;
  const live = (t) => !t.deletedAt || (t.updatedAt ?? t.createdAt) > t.deletedAt || t.runs.length > 0;
  return row.trips.filter(live).map((t) => `${t.name}: ${t.runs.map((r) => r.trailId).sort().join(',')}`).sort();
};
const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);

async function device(browser, name) {
  const ctx = await browser.newContext({ viewport: { width: 1300, height: 900 } });
  const page = await ctx.newPage();
  page.errors = [];
  page.on('pageerror', (e) => page.errors.push(`${name}: ${e.message}`));
  page.on('dialog', (d) => d.accept());
  await page.goto(APP);
  await page.getByRole('checkbox', { name: 'Skied Bypass this trip' }).waitFor();
  return { ctx, page };
}
const mark = (page, trail) => page.getByRole('checkbox', { name: `Skied ${trail} this trip` }).click();
const openAccount = async (page) => {
  await page.getByRole('button', { name: 'Trip options' }).click();
  await page.getByRole('menuitem', { name: /Sign in to back up|Account & sync/ }).click();
};
async function signIn(page, shots) {
  await openAccount(page);
  await page.getByLabel('Email').fill(EMAIL);
  if (shots && SHOTS) await page.screenshot({ path: `${SHOTS}/1-email.png` });
  await page.getByRole('button', { name: 'Email me a code' }).click();
  await page.getByLabel('Code').waitFor();
  const { code } = await (await fetch(`${MOCK}/__debug/code?email=${EMAIL}`)).json();
  await page.getByLabel('Code').fill('000000' === code ? '111111' : '000000');
  await page.getByRole('button', { name: 'Sign in' }).click();
  await page.getByText('That code is wrong or has expired').waitFor();
  await page.getByLabel('Code').fill(code);
  if (shots && SHOTS) await page.screenshot({ path: `${SHOTS}/2-code.png` });
  await page.getByRole('button', { name: 'Sign in' }).click();
  await page.getByText('Signed in as').waitFor();
  await page.getByText(/^Synced /).waitFor({ timeout: 15000 });
  if (shots && SHOTS) await page.screenshot({ path: `${SHOTS}/3-signed-in.png` });
}
const close = (page) => page.getByRole('button', { name: 'Close' }).click();

(async () => {
  const browser = await chromium.launch();
  const phone = await device(browser, 'phone');
  await mark(phone.page, 'Bypass');
  await mark(phone.page, 'Centerline');
  await signIn(phone.page, true);
  console.log('1 phone signed in; saved:', await savedTrips());

  const laptop = await device(browser, 'laptop');
  await mark(laptop.page, 'Chapel Lane');
  await signIn(laptop.page);
  console.log('2 laptop signed in; laptop has:', await tripsOn(laptop.page));

  await phone.page.getByRole('button', { name: 'Sync now' }).click();
  await until('phone gets the laptop trip', async () => (await tripsOn(phone.page)).length === 2);
  console.log('3 phone after sync now:', await tripsOn(phone.page));
  await close(phone.page);
  await close(laptop.page);

  // phone offline logs a run; laptop renames the phone's trip meanwhile
  await phone.ctx.setOffline(true);
  await mark(phone.page, 'Chin Clip');
  await openAccount(phone.page);
  await phone.page.getByText(/^Offline: changes sync/).waitFor({ timeout: 10000 });
  if (SHOTS) await phone.page.screenshot({ path: `${SHOTS}/4-offline.png` });
  await close(phone.page);
  const phoneTripId = await phone.page.evaluate(() => JSON.parse(localStorage.getItem('myskiruns.trips')).activeTripId);
  await laptop.page.selectOption('#trip-select', phoneTripId);
  await laptop.page.getByRole('button', { name: 'Trip options' }).click();
  await laptop.page.getByRole('menuitem', { name: 'Rename trip' }).click();
  await laptop.page.getByLabel('Trip name').fill('Presidents Day');
  await laptop.page.getByRole('button', { name: 'Save' }).click();
  await until('rename saved', async () => (await savedTrips())?.some((t) => t.startsWith('Presidents Day')));
  console.log('4 saved after laptop rename (phone offline):', await savedTrips());
  await phone.ctx.setOffline(false);
  await until('phone back online synced', async () => (await tripsOn(phone.page)).includes('Presidents Day: bypass,centerline,chin-clip'));
  await until('saved has both', async () => (await savedTrips())?.includes('Presidents Day: bypass,centerline,chin-clip'));
  console.log('5 phone back online:', await tripsOn(phone.page), '| saved:', await savedTrips());

  // laptop deletes its own trip; the phone hears on its next sync
  const laptopTripId = await laptop.page.evaluate((other) => JSON.parse(localStorage.getItem('myskiruns.trips')).trips.find((t) => t.id !== other).id, phoneTripId);
  await laptop.page.selectOption('#trip-select', laptopTripId);
  await laptop.page.getByRole('button', { name: 'Trip options' }).click();
  await laptop.page.getByRole('menuitem', { name: 'Delete trip' }).click();
  await until('deletion saved', async () => (await savedTrips())?.length === 1);
  await openAccount(phone.page);
  await phone.page.getByRole('button', { name: 'Sync now' }).click();
  await until('phone drops the deleted trip', async () => (await tripsOn(phone.page)).length === 1);
  console.log('6 after laptop deletes its trip, phone has:', await tripsOn(phone.page));

  // delete the account from the phone
  await phone.page.getByRole('button', { name: 'Delete account…' }).click();
  await phone.page.getByRole('button', { name: 'Delete account', exact: true }).click();
  await phone.page.getByRole('button', { name: 'Email me a code' }).waitFor();
  const gone = await mine();
  console.log('7 account deleted:', gone.user ? 'user still there' : 'user gone', '|', gone.row ? 'row still there' : 'row gone', '| phone keeps:', await tripsOn(phone.page));
  const errors = [...phone.page.errors, ...laptop.page.errors];
  console.log('page errors:', errors.length ? errors : 'none');
  await browser.close();
  if (errors.length || gone.user || gone.row) process.exit(1);
})().catch((e) => {
  console.error(e);
  process.exit(1);
});
