const { chromium } = require(process.env.PLAYWRIGHT_PATH);
const { spawn } = require('node:child_process');
const SCR = '/tmp/claude-0/-home-user-myskiruns/6d543bfc-3ab1-5e7f-9c64-5c2d6dd5c830/scratchpad';
(async () => {
  let server;
  await new Promise((r) => { server = spawn('node', [`${SCR}/offline/serve.cjs`, `${SCR}/dist-new`, '4406']); server.stdout.on('data', (d) => String(d).includes('listening') && r()); });
  const browser = await chromium.launch();
  for (const [w, h] of [[360, 740], [390, 844], [768, 1024]]) {
    const page = await browser.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: 2, isMobile: w < 700, hasTouch: w < 700 });
    await page.goto('http://localhost:4406/?resort=copper-mountain');
    await page.getByRole('checkbox', { name: /^Skied .* this trip$/ }).first().waitFor();
    await page.screenshot({ path: `${__dirname}/hdr-${w}-notrip.png`, clip: { x: 0, y: 0, width: w, height: 170 } });
    await page.getByRole('checkbox', { name: /^Skied .* this trip$/ }).first().click();
    await page.waitForTimeout(200);
    await page.screenshot({ path: `${__dirname}/hdr-${w}-trip.png`, clip: { x: 0, y: 0, width: w, height: 170 } });
    const hdr = await page.locator('header').first().boundingBox();
    const sel = await page.locator('#trip-select').boundingBox();
    console.log(`${w}px: header ${Math.round(hdr.height)} px tall; trip picker ${Math.round(sel.width)} px wide`);
    await page.close();
  }
  await browser.close(); server.kill();
})();
