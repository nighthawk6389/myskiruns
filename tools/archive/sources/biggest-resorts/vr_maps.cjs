const { chromium } = require(process.env.PLAYWRIGHT_PATH);
const SITES = {
  'mount-snow': 'https://www.mountsnow.com/the-mountain/about-the-mountain/trail-maps.aspx',
  'crested-butte': 'https://www.skicb.com/the-mountain/about-the-mountain/trail-maps.aspx',
  'mount-sunapee': 'https://www.mountsunapee.com/the-mountain/about-the-mountain/trail-maps.aspx',
  'beaver-creek': 'https://www.beavercreek.com/the-mountain/about-the-mountain/trail-map.aspx',
  'okemo-check': 'https://www.okemo.com/the-mountain/about-the-mountain/trail-map.aspx',
};
(async () => {
  const browser = await chromium.launch({ proxy: { server: process.env.HTTPS_PROXY }, args: [`--ignore-certificate-errors-spki-list=${process.env.PIN}`] });
  const only = process.argv.slice(2);
  for (const [id, url] of Object.entries(SITES)) {
    if (only.length && !only.includes(id)) continue;
    const page = await browser.newPage();
    const seen = new Set();
    page.on('response', (r) => { const u = r.url(); if (/\.pdf|scene7.*(trail|map)/i.test(u)) seen.add(u.split('?')[0]); });
    try {
      await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
      await page.waitForTimeout(6000);
      const links = await page.evaluate(() => [...document.querySelectorAll('a[href]')].map((a) => a.href).filter((h) => /\.pdf/i.test(h) || (/trail.?map/i.test(h) && !h.includes('#'))));
      const imgs = await page.evaluate(() => [...document.querySelectorAll('img, source')].map((i) => i.currentSrc || i.src || i.srcset).filter((s) => s && /scene7|map/i.test(s)));
      console.log(`== ${id} (${await page.title()})`);
      console.log('  pdf/map links:', [...new Set(links)].slice(0, 8));
      console.log('  images:', [...new Set(imgs.map((s) => s.split('?')[0]))].slice(0, 6));
      console.log('  responses:', [...seen].slice(0, 6));
    } catch (e) { console.log(`== ${id} error ${e.message.slice(0, 100)}`); }
    await page.close();
  }
  await browser.close();
})();
