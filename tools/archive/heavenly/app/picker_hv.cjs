// picker_hv.cjs <url> <out prefix>: the resort picker finds Heavenly by name, second state and lake; picking it
// opens its two panels, each with its map image and overlays; screenshots on desktop and phone.
const { chromium } = require(process.env.PLAYWRIGHT_PATH);
const [url, out] = process.argv.slice(2);
(async () => {
  const b = await chromium.launch();
  let bad = 0;
  const expect = (what, got, want) => {
    const ok = JSON.stringify(got) === JSON.stringify(want);
    if (!ok) bad++;
    console.log(ok ? 'ok  ' : 'FAIL', what, JSON.stringify(got), ok ? '' : `(want ${JSON.stringify(want)})`);
  };
  for (const [name, vp] of [['desktop', { width: 1400, height: 900 }], ['phone', { width: 390, height: 844 }]]) {
    console.log('==', name);
    const p = await b.newPage({ viewport: vp, deviceScaleFactor: 1 });
    const errors = [];
    p.on('pageerror', (e) => errors.push(e.message));
    // /api/conditions is a Vercel function: this static server answers 503, as for every resort
    p.on('console', (m) => m.type() === 'error' && !(m.location().url || '').includes('/api/conditions') && errors.push(m.text()));
    await p.goto(url, { waitUntil: 'networkidle' });
    const button = p.locator('button[aria-label^="Resort:"]');
    const names = async (q) => {
      await p.locator('[role=combobox]').fill(q);
      return p.locator('[role=option] >> span:first-child').allTextContents();
    };
    await button.click();
    expect('placeholder', await p.locator('[role=combobox]').getAttribute('placeholder'), 'Search 21 resorts or a state…');
    expect('"heavenly"', await names('heavenly'), ['Heavenly']);
    expect('"nevada"', await names('nevada'), ['Heavenly']);
    expect('"nv"', await names('nv'), ['Heavenly']);
    expect('"tahoe"', await names('tahoe'), ['Palisades Tahoe', 'Heavenly']);
    expect('"lake tahoe"', await names('lake tahoe'), ['Heavenly', 'Palisades Tahoe']);
    expect('"california"', await names('california'), ['Heavenly', 'Palisades Tahoe']);
    await names('');
    const groups = await p.locator('[role=group]').evaluateAll((gs) => gs.map((g) => g.getAttribute('aria-label')));
    const cal = await p.locator('[role=group][aria-label=California] [role=option] >> span:first-child').allTextContents();
    expect('California group', cal, ['Heavenly', 'Palisades Tahoe']);
    expect('no Nevada group', groups.includes('Nevada'), false);
    await names('nevada');
    await p.keyboard.press('Enter');
    await p.waitForFunction(() => [...document.querySelectorAll('img')].some((i) => i.src.includes('heavenly-main.jpg') && i.complete && i.naturalWidth > 0), null, { timeout: 30000 });
    expect('button after Enter', await button.getAttribute('aria-label'), 'Resort: Heavenly. Change resort');
    expect('title', await p.title(), 'Heavenly Trail Map · My Ski Runs');
    expect('saved choice', await p.evaluate(() => localStorage.getItem('myskiruns.resort')), 'heavenly');
    const img = await p.evaluate(() => { const i = [...document.querySelectorAll('img')].find((i) => i.src.includes('heavenly')); return [i.naturalWidth, i.naturalHeight]; });
    expect('main image size', img, [3652, 2984]);
    await p.waitForTimeout(800);
    const panelsShown = await p.getByRole('button', { name: /California and Nevada|Top of Gondola/ }).allTextContents()
      .catch(() => []);
    const tabs = panelsShown.length ? panelsShown : await p.getByRole('tab').allTextContents();
    console.log('     panel switcher:', JSON.stringify(tabs));
    const paths = async () => p.evaluate(() => document.querySelectorAll('svg path, svg polyline, svg circle').length);
    console.log('     overlay elements on main:', await paths());
    await p.screenshot({ path: `${out}_${name}_main.png` });
    const tog = p.getByRole('button', { name: 'Top of Gondola' }).or(p.getByRole('tab', { name: 'Top of Gondola' })).first();
    await tog.click();
    await p.waitForFunction(() => [...document.querySelectorAll('img')].some((i) => i.src.includes('heavenly-top-of-gondola.jpg') && i.complete && i.naturalWidth > 0), null, { timeout: 30000 });
    await p.waitForTimeout(800);
    const img2 = await p.evaluate(() => { const i = [...document.querySelectorAll('img')].find((i) => i.src.includes('heavenly-top-of-gondola')); return [i.naturalWidth, i.naturalHeight]; });
    expect('inset image size', img2, [2368, 1102]);
    console.log('     overlay elements on the inset:', await paths());
    await p.screenshot({ path: `${out}_${name}_inset.png` });
    await p.reload({ waitUntil: 'networkidle' });
    await p.waitForFunction(() => [...document.querySelectorAll('img')].some((i) => i.src.includes('heavenly-main.jpg') && i.complete && i.naturalWidth > 0), null, { timeout: 30000 });
    expect('after a reload', await button.getAttribute('aria-label'), 'Resort: Heavenly. Change resort');
    expect('page errors', errors, []);
    await p.close();
  }
  await b.close();
  console.log(bad ? `${bad} FAILED` : 'all ok');
  process.exit(bad ? 1 : 0);
})();
