const { chromium } = require(process.env.PLAYWRIGHT_PATH);
(async () => {
  const browser = await chromium.launch({ proxy: { server: process.env.HTTPS_PROXY }, args: [`--ignore-certificate-errors-spki-list=${process.env.PIN}`] });
  const page = await browser.newPage();
  const resp = await page.goto('https://myskiruns.vercel.app/?resort=killington');
  console.log('status', resp.status());
  await page.locator('svg[viewBox^="0 0 1000"]').waitFor({ timeout: 60000 });
  console.log('overlay shown; title:', await page.title());
  await browser.close();
})().catch((e) => { console.error(e.message); process.exit(1); });
