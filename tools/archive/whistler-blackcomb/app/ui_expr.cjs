// The two Expressways and a park in Whistler Blackcomb's trail list: both listed (one per mountain), each shows its
// own overlay on the main map; Choker Park's line shows and hovering it names it; no console errors.
const { chromium } = require(process.env.PLAYWRIGHT_PATH);
const S = process.argv[2];
(async () => {
  const browser = await chromium.launch();
  const page = await (await browser.newContext({ viewport: { width: 1440, height: 900 } })).newPage();
  const errors = [];
  page.on('pageerror', (e) => errors.push(String(e)));
  page.on('console', (m) => m.type() === 'error' && errors.push(m.text()));
  await page.goto('http://localhost:4199/?resort=whistler-blackcomb');
  await page.waitForSelector('[aria-label="Trail map"] button', { timeout: 20000 });
  await page.fill('input[aria-label="Search trails"]', 'Expressway');
  await page.waitForTimeout(400);
  const rows = await page.$$eval('button[title="Show on map"]', (bs) => bs.map((b) => b.textContent.trim()));
  console.log('rows for Expressway:', JSON.stringify(rows));
  const btns = await page.$$('button[title="Show on map"]');
  for (let k = 0; k < btns.length; k++) {
    const b = (await page.$$('button[title="Show on map"]'))[k];
    await b.click();
    await page.waitForTimeout(700);
    console.log('url after row', k, page.url());
    await page.screenshot({ path: `${S}/wb/ui_expr_${k}.png` });
  }
  await page.fill('input[aria-label="Search trails"]', 'Choker');
  await page.waitForTimeout(400);
  await page.click('button[title="Show on map"]:has-text("Choker Park")');
  await page.waitForTimeout(700);
  await page.screenshot({ path: `${S}/wb/ui_choker.png` });
  console.log('url after Choker Park', page.url());
  console.log('errors', JSON.stringify(errors));
  await browser.close();
})();
