const { chromium } = require(process.env.PLAYWRIGHT_PATH);
const { spawn } = require('node:child_process');
(async () => {
  const srv = spawn('node', [process.argv[2] + '/offline/serve.cjs', process.argv[3], '4320']);
  await new Promise((r) => srv.stdout.on('data', (d) => String(d).includes('listening') && r()));
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 390, height: 844 } });
  await page.goto('http://localhost:4320/?resort=stowe');
  await page.getByRole('checkbox', { name: 'Skied Bypass this trip' }).waitFor();
  await page.screenshot({ path: process.argv[4], clip: { x: 0, y: 0, width: 390, height: 200 } });
  await page.getByRole('checkbox', { name: 'Skied Bypass this trip' }).click();
  await page.screenshot({ path: process.argv[4].replace('.png', '-trip.png'), clip: { x: 0, y: 0, width: 390, height: 200 } });
  await browser.close(); srv.kill();
})();
