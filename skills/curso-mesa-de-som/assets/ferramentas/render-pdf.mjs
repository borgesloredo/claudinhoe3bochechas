// Usage: node render-pdf.mjs <in.html> <out.pdf>
import { chromium } from 'playwright';
import { pathToFileURL } from 'node:url';
import { resolve } from 'node:path';
const [, , src, out] = process.argv;
const browser = await chromium.launch();
const page = await browser.newPage();
await page.goto(pathToFileURL(resolve(src)).href, { waitUntil: 'networkidle' });
await page.pdf({
  path: out, format: 'A4', printBackground: true,
  margin: { top: '18mm', bottom: '18mm', left: '16mm', right: '16mm' },
  // rodapé com número de página (o cabeçalho fica vazio)
  displayHeaderFooter: true,
  headerTemplate: '<span></span>',
  footerTemplate: '<div style="width:100%;font-size:8px;color:#8a94a0;text-align:center;font-family:Helvetica,Arial,sans-serif"><span class="pageNumber"></span></div>',
});
await browser.close();
console.log('ok', out);
