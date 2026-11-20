// Uso: node shot_slides.mjs <index.html> <pasta-saida> [h/v ...]
// Lista slides cujo conteúdo passa da altura (720 px) e tira screenshots dos slides pedidos.
import { chromium } from 'playwright';
import { pathToFileURL } from 'node:url';
import { resolve } from 'node:path';
const [, , src, out, ...want] = process.argv;
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
const errs = [];
page.on('pageerror', e => errs.push(e.message));
page.on('console', m => m.type() === 'error' && errs.push(m.text()));
await page.goto(pathToFileURL(resolve(src)).href);
await page.waitForFunction(() => window.Reveal && Reveal.isReady());
const over = await page.evaluate(() => {
  const res = [];
  Reveal.getSlides().forEach(s => {
    const { h, v } = Reveal.getIndices(s);
    const st = s.parentElement.closest('section'), pv = st?.style.display, prev = s.style.display;
    if (st) st.style.display = 'block'; s.style.display = 'block';
    const hgt = Math.max(...[...s.children].filter(c => c.tagName !== 'ASIDE' && !c.classList.contains('more')).map(c => c.offsetTop + c.offsetHeight));
    s.style.display = prev; if (st) st.style.display = pv;
    if (hgt > 712) res.push(`${h}/${v} ${s.id} ${hgt}px`);
  });
  return res;
});
console.log('slides:', await page.evaluate(() => Reveal.getTotalSlides()), '| passam da altura:', over.length);
over.forEach(o => console.log('  ', o));
for (const hv of want) {
  // aceita "h/v" ou um id de slide (ex.: s5-1-2); mostra todos os fragments
  const [h, v] = await page.evaluate(hv => {
    Reveal.configure({ transition: 'none' });
    const el = hv.includes('/') ? null : document.getElementById(hv);
    const i = el ? Reveal.getIndices(el) : { h: +hv.split('/')[0], v: +hv.split('/')[1] || 0 };
    Reveal.slide(i.h, i.v, 99); return [i.h, i.v || 0];
  }, hv);
  await page.waitForTimeout(250);
  await page.screenshot({ path: `${out}/slide-${h}-${v}.png` });
}
if (errs.length) console.log('erros JS:', errs);
await browser.close();
