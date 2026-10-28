// Render each poster-*.html to a print PDF (18x24 in + bleed) and a preview PNG.
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const W = 18.25, H = 24.25; // inches, incl. 0.125in bleed per side

(async () => {
  const browser = await chromium.launch();
  const files = fs.readdirSync(__dirname).filter(f => /^poster-.*\.html$/.test(f));
  fs.mkdirSync(path.join(__dirname, 'print'), { recursive: true });
  fs.mkdirSync(path.join(__dirname, 'preview'), { recursive: true });
  for (const f of files) {
    const base = f.replace(/\.html$/, '');
    const page = await browser.newPage({
      viewport: { width: Math.round(W * 96), height: Math.round(H * 96) },
      deviceScaleFactor: 0.75,
    });
    await page.goto('file://' + path.join(__dirname, f));
    await page.evaluate(() => document.fonts.ready);
    const overflow = await page.evaluate(() => {
      const el = document.querySelector('.inner');
      return el.scrollHeight - el.clientHeight;
    });
    if (overflow > 1) console.warn(`  ! ${f}: content overflows by ${overflow}px`);
    await page.pdf({
      path: path.join(__dirname, 'print', base + '.pdf'),
      width: W + 'in', height: H + 'in', printBackground: true, pageRanges: '1',
    });
    await page.screenshot({ path: path.join(__dirname, 'preview', base + '.png') });
    console.log('rendered', base);
    await page.close();
  }
  await browser.close();
})();
