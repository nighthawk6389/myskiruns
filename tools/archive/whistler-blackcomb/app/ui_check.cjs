// UI check for Whistler Blackcomb: three panel tabs, a trail on an inset opens its panel, phone size.
const { chromium } = require(process.env.PLAYWRIGHT_PATH);
const S = process.argv[2];
(async () => {
  const browser = await chromium.launch();
  for (const vp of [{ width: 1440, height: 900, name: 'desktop' }, { width: 390, height: 844, name: 'phone', mobile: true }]) {
    const ctx = await browser.newContext({ viewport: { width: vp.width, height: vp.height }, isMobile: !!vp.mobile, hasTouch: !!vp.mobile });
    const page = await ctx.newPage();
    const errors = [];
    page.on('pageerror', (e) => errors.push(String(e)));
    page.on('console', (m) => m.type() === 'error' && errors.push(m.text()));
    await page.goto('http://localhost:4199/?resort=whistler-blackcomb');
    await page.waitForSelector('[aria-label="Trail map"] button', { timeout: 20000 });
    const tabs = await page.$$eval('[aria-label="Trail map"] button', (bs) => bs.map((b) => [b.textContent, b.getAttribute('aria-pressed')]));
    console.log(vp.name, 'tabs', JSON.stringify(tabs));
    const img = await page.$eval('img', (i) => i.getAttribute('src')).catch(() => null);
    console.log(vp.name, 'first img', img);
    await page.screenshot({ path: `${S}/wb/ui_${vp.name}_main.png` });
    if (vp.name === 'desktop') {
      // a trail drawn only on the glacier inset: Sapphire Bowl
      await page.fill('input[aria-label="Search trails"]', 'Sapphire');
      await page.click('button[title="Show on map"]:has-text("Sapphire Bowl")');
      await page.waitForTimeout(800);
      const on = await page.$$eval('[aria-label="Trail map"] button', (bs) => bs.filter((b) => b.getAttribute('aria-pressed') === 'true').map((b) => b.textContent));
      console.log('after Sapphire Bowl: panel', on, 'url', page.url());
      await page.screenshot({ path: `${S}/wb/ui_desktop_glacier.png` });
      await page.fill('input[aria-label="Search trails"]', 'Flute');
      await page.click('button[title="Show on map"]:has-text("North Flute Bowl")');
      await page.waitForTimeout(800);
      const on2 = await page.$$eval('[aria-label="Trail map"] button', (bs) => bs.filter((b) => b.getAttribute('aria-pressed') === 'true').map((b) => b.textContent));
      console.log('after North Flute Bowl: panel', on2);
      await page.fill('input[aria-label="Search trails"]', 'Peak To Creek');
      await page.click('button[title="Show on map"]:has-text("Peak To Creek")');
      await page.waitForTimeout(800);
      const on3 = await page.$$eval('[aria-label="Trail map"] button', (bs) => bs.filter((b) => b.getAttribute('aria-pressed') === 'true').map((b) => b.textContent));
      console.log('after Peak To Creek: panel', on3);
      // the resort picker search finds it by "bc" and by "whis"
      await page.click('button[aria-label^="Resort:"]');
      await page.fill('input[aria-label="Search resorts"]', 'bc');
      const found = await page.$$eval('[role="listbox"] [role="option"]', (os) => os.map((o) => o.textContent));
      console.log('picker "bc":', found);
      await page.fill('input[aria-label="Search resorts"]', 'whis');
      const found2 = await page.$$eval('[role="listbox"] [role="option"]', (os) => os.map((o) => o.textContent));
      console.log('picker "whis":', found2);
    }
    console.log(vp.name, 'errors', errors);
    await ctx.close();
  }
  await browser.close();
})();
