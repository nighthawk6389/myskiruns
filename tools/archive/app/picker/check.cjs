// node check.cjs <base url> <out dir>: drive the resort picker on desktop (mouse + keyboard) and a phone (touch)
const { chromium } = require(process.env.PLAYWRIGHT_PATH);
const [base, out] = process.argv.slice(2);
const results = [];
const ok = (name, cond, extra = '') => { results.push(`${cond ? 'PASS' : 'FAIL'} ${name}${extra ? ' — ' + extra : ''}`); };
const header = (p) => p.locator('header button[aria-haspopup="dialog"]').first();
const mapSrc = (p) => p.$eval('img', (i) => i.getAttribute('src')).catch(() => null);
async function waitMap(p, id) {
  await p.waitForFunction((id) => [...document.images].some((i) => (i.getAttribute('src') || '').includes(`/maps/${id}`)), id, { timeout: 30000 });
}
(async () => {
  const b = await chromium.launch();
  // ---- desktop, mouse and keyboard
  const ctx = await b.newContext({ viewport: { width: 1400, height: 900 } });
  const p = await ctx.newPage();
  const errors = [];
  p.on('pageerror', (e) => errors.push(e.message));
  await p.goto(`${base}?resort=killington`, { waitUntil: 'networkidle' });
  await waitMap(p, 'killington');
  ok('button shows the current resort', (await header(p).innerText()).includes('Killington'));
  await header(p).click();
  const input = p.getByRole('combobox', { name: 'Search resorts' });
  ok('click opens the search, focused', await input.evaluate((el) => el === document.activeElement));
  const groups = await p.$$eval('[role=listbox] [role=group]', (gs) => gs.map((g) => g.getAttribute('aria-label')));
  ok('grouped by state before typing', groups.join(',') === [...groups].sort().join(','), groups.join(', '));
  const all = await p.$$eval('[role=option]', (os) => os.map((o) => o.textContent));
  ok('every resort listed', all.length >= 16, `${all.length} options`);
  const sel = await p.$$eval('[role=option][aria-selected=true]', (os) => os.map((o) => o.textContent));
  ok('current resort marked', sel.length === 1 && sel[0].includes('Killington'), sel.join());
  await p.screenshot({ path: `${out}/desktop_open.png` });
  await input.fill('smug');
  const smug = await p.$$eval('[role=option]', (os) => os.map((o) => o.textContent));
  ok('typing filters', smug.length === 1 && smug[0].includes("Smugglers"), smug.join(' | '));
  await p.screenshot({ path: `${out}/desktop_typed.png` });
  await input.press('Enter');
  await waitMap(p, 'smugglers-notch');
  ok('Enter picks the match and loads it', (await header(p).innerText()).includes("Smugglers"));
  ok('panel closed after picking', !(await p.locator('[role=dialog][aria-label="Choose a resort"]').count()));
  ok('focus back on the button', await header(p).evaluate((el) => el === document.activeElement));
  // keyboard only: open with Enter on the focused button, state search, arrows
  await p.keyboard.press('Enter');
  await p.keyboard.type('maine');
  const maine = await p.$$eval('[role=option]', (os) => os.map((o) => o.textContent));
  ok('a state finds its resorts', maine.length === 2 && maine.every((t) => /Sugarloaf|Sunday River/.test(t)), maine.join(' | '));
  await p.keyboard.press('ArrowDown');
  const activeId = await input.getAttribute('aria-activedescendant');
  const activeText = await p.$eval(`[id="${activeId}"]`, (o) => o.textContent);
  ok('arrow moves the active option', activeText.includes('Sunday River'), activeText);
  await p.keyboard.press('Enter');
  await waitMap(p, 'sunday-river');
  ok('arrow + Enter picks', (await header(p).innerText()).includes('Sunday River'));
  // Escape closes without changing
  await header(p).click();
  await p.keyboard.type('vail');
  await p.keyboard.press('Escape');
  ok('Escape closes', !(await p.locator('[role=dialog][aria-label="Choose a resort"]').count()));
  ok('Escape keeps the resort', (await header(p).innerText()).includes('Sunday River'));
  // no match
  await header(p).click();
  await p.keyboard.type('zzzz');
  ok('no match message', (await p.getByText('No resort matches').count()) === 1);
  // Tab out closes, Shift+Tab to the button keeps it open
  await p.keyboard.press('Shift+Tab');
  ok('Shift+Tab to the button keeps it open', (await p.locator('[role=dialog][aria-label="Choose a resort"]').count()) === 1);
  await header(p).click();
  await header(p).click();
  await p.keyboard.press('Tab');
  ok('Tab out of the search closes it', !(await p.locator('[role=dialog][aria-label="Choose a resort"]').count()));
  await header(p).click();
  await p.keyboard.type('zzzz');
  // click outside closes
  await p.mouse.click(700, 600);
  ok('click outside closes', !(await p.locator('[role=dialog][aria-label="Choose a resort"]').count()));
  // mouse pick
  await header(p).click();
  await p.getByRole('option', { name: /Copper Mountain/ }).click();
  await waitMap(p, 'copper-mountain');
  ok('click on an option picks it', (await header(p).innerText()).includes('Copper'));
  ok('choice remembered', (await p.evaluate(() => localStorage.getItem('myskiruns.resort'))) === 'copper-mountain');
  ok('no page errors (desktop)', !errors.length, errors.join('; '));
  await ctx.close();
  // ---- phone, touch
  const ph = await b.newContext({ viewport: { width: 390, height: 844 }, hasTouch: true, isMobile: true, deviceScaleFactor: 2 });
  const q = await ph.newPage();
  const perr = [];
  q.on('pageerror', (e) => perr.push(e.message));
  await q.goto(`${base}?resort=stowe`, { waitUntil: 'networkidle' });
  await waitMap(q, 'stowe');
  const bb = await header(q).boundingBox();
  ok('phone: button spans the row', bb.width > 330, `${Math.round(bb.width)} px`);
  await header(q).tap();
  const panel = q.locator('[role=dialog][aria-label="Choose a resort"]');
  const pb = await panel.boundingBox();
  ok('phone: panel within the screen', pb.x >= 0 && pb.x + pb.width <= 390, `${Math.round(pb.x)}..${Math.round(pb.x + pb.width)}`);
  await q.screenshot({ path: `${out}/phone_open.png` });
  await q.getByRole('combobox', { name: 'Search resorts' }).fill('wild');
  await q.getByRole('option', { name: /Wildcat/ }).tap();
  await waitMap(q, 'wildcat');
  ok('phone: tap picks', (await header(q).innerText()).includes('Wildcat'));
  await q.screenshot({ path: `${out}/phone_picked.png` });
  ok('no page errors (phone)', !perr.length, perr.join('; '));
  await b.close();
  console.log(results.join('\n'));
})().catch((e) => { console.log(results.join('\n')); console.error('ERROR', e.message); process.exit(1); });
