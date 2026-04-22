const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();

  page.on('console', msg => console.log('BROWSER CONSOLE:', msg.type(), msg.text()));
  page.on('pageerror', error => console.log('BROWSER ERROR:', error.message));

  console.log('Navigating to http://127.0.0.1:8000');
  await page.goto('http://127.0.0.1:8000', { waitUntil: 'networkidle' });

  // Wait 2 seconds for WS and rendering
  await page.waitForTimeout(2000);

  const deviceHtml = await page.innerHTML('#device-list');
  console.log('DEVICE LIST HTML:', deviceHtml);

  await browser.close();
})();
