const { chromium } = require(process.env.PLAYWRIGHT_PATH);
const fs = require('fs');
const JOBS = [
  ['park-city', 'https://www.parkcitymountain.com/the-mountain/about-the-mountain/trail-map.aspx', 'https://www.parkcitymountain.com/-/aemasset/sitecore/park-city/maps/20251114_PC_winter-trail_map_001.pdf'],
  ['attitash', 'https://www.attitash.com/the-mountain/about-the-mountain/trail-map.aspx', 'https://www.attitash.com/-/aemasset/sitecore/attitash/maps/winter-2025-2026/20251226_AT_winter-trail_map_001.pdf'],
  ['hunter', 'https://www.huntermtn.com/the-mountain/about-the-mountain/trail-map.aspx', 'https://www.huntermtn.com/-/aemasset/sitecore/hunter/maps/winter-2025-2026/20251122_HU_winter-trail_map_001.pdf'],
  ['crested-butte', 'https://www.skicb.com/the-mountain/about-the-mountain/trail-maps.aspx', 'https://www.skicb.com/-/aemasset/sitecore/crested-butte/maps/winter-2025-2026/20251103_CB_winter-trail_map_001.pdf'],
  ['beaver-creek', 'https://www.beavercreek.com/the-mountain/about-the-mountain/trail-map.aspx', 'https://www.beavercreek.com/-/aemasset/sitecore/beaver-creek/maps/winter-2025-2026/20251006_BC_winter-trail_map_001.pdf'],
];
(async () => {
  const browser = await chromium.launch({ proxy: { server: process.env.HTTPS_PROXY }, args: [`--ignore-certificate-errors-spki-list=${process.env.PIN}`] });
  for (const [id, pageUrl, pdf] of JOBS) {
    const page = await browser.newPage();
    try {
      await page.goto(pageUrl, { waitUntil: 'domcontentloaded', timeout: 60000 });
      const b64 = await page.evaluate(async (u) => {
        const r = await fetch(u);
        if (!r.ok) return 'HTTP ' + r.status;
        const buf = new Uint8Array(await r.arrayBuffer());
        let s = ''; for (let i = 0; i < buf.length; i += 0x8000) s += String.fromCharCode.apply(null, buf.subarray(i, i + 0x8000));
        return btoa(s);
      }, pdf);
      if (b64.startsWith('HTTP')) console.log(id, b64);
      else { fs.writeFileSync(`${id}.pdf`, Buffer.from(b64, 'base64')); console.log(id, 'saved', fs.statSync(`${id}.pdf`).size); }
    } catch (e) { console.log(id, 'error', e.message.slice(0, 120)); }
    await page.close();
  }
  await browser.close();
})();
