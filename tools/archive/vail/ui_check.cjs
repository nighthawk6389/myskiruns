// UI check of the Vail panel switcher: desktop and phone screenshots, tab switching, and a trail picked from the
// list jumping to the panel it is drawn on (zoomed to it, its sheet open).
const { chromium } = require(process.env.PLAYWRIGHT_PATH);
const out = process.argv[2];
(async () => {
  const browser = await chromium.launch();
  const log = [];
  for (const [label, vp] of [['desktop', { width: 1400, height: 900 }], ['phone', { width: 390, height: 844 }]]) {
    const page = await browser.newPage({ viewport: vp, deviceScaleFactor: 1, isMobile: label === 'phone', hasTouch: label === 'phone' });
    page.on('pageerror', (e) => log.push(`${label} pageerror: ${e.message}`));
    page.on('console', (m) => { if (m.type() === 'error') log.push(`${label} console: ${m.text()}`); });
    await page.goto('http://localhost:4199/?resort=vail');
    await page.waitForTimeout(2500);
    await page.screenshot({ path: `${out}/ui_${label}_0.png` });
    const tabs = page.locator('[aria-label="Trail map"] button');
    log.push(`${label} tabs: ${(await tabs.allTextContents()).join(' | ')}; pressed: ${await page.locator('[aria-label="Trail map"] button[aria-pressed="true"]').textContent()}`);
    await tabs.nth(1).click();
    await page.waitForTimeout(1500);
    const img = await page.locator('img[alt^="Vail trail map"]').first();
    log.push(`${label} after Back Bowls tab: img ${await img.getAttribute('src')} alt "${await img.getAttribute('alt')}"`);
    await page.screenshot({ path: `${out}/ui_${label}_1.png` });
    await tabs.nth(2).click();
    await page.waitForTimeout(1500);
    log.push(`${label} after Blue Sky tab: img ${await page.locator('img[alt^="Vail trail map"]').first().getAttribute('src')}`);
    await page.screenshot({ path: `${out}/ui_${label}_2.png` });
    if (label === 'desktop') {
      // pick a Front Side trail from the list while Blue Sky is shown
      await page.getByLabel('Search trails').fill('Riva Ridge');
      await page.waitForTimeout(500);
      await page.locator('section[aria-label="Front Side"] button[title="Show on map"]').filter({ hasText: 'Riva Ridge' }).first().click();
      await page.waitForTimeout(2500);
      log.push(`after picking Riva Ridge: img ${await page.locator('img[alt^="Vail trail map"]').first().getAttribute('src')}; pressed tab ${await page.locator('[aria-label="Trail map"] button[aria-pressed="true"]').textContent()}`);
      const stage = await page.locator('[class*="stage"]').first().getAttribute('style');
      log.push(`stage: ${stage}`);
      await page.screenshot({ path: `${out}/ui_desktop_3.png` });
    }
    await page.close();
  }
  console.log(log.join('\n'));
  await browser.close();
})();
