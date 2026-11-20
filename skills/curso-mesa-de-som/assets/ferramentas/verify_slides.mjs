// Uso: node verify_slides.mjs <index.html>
// Confere: erros de JS, requisições externas, notas em todos os slides e #encerramento; falha se sobrar quadro .ask/.cena, slide agenda-/fecha-/fig-
// ou o antigo #abertura ("Quem ensina", retirado em 21/10/2026: o curso não apresenta escolas nem autores).
import { chromium } from 'playwright';
import { pathToFileURL } from 'node:url';
import { resolve } from 'node:path';
const src = process.argv[2];
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
const errs = [], ext = [];
page.on('pageerror', e => errs.push(e.message));
page.on('console', m => m.type() === 'error' && errs.push(m.text()));
page.on('request', r => { if (!/^(file|data|blob|about):/.test(r.url())) ext.push(r.url()); });
await page.goto(pathToFileURL(resolve(src)).href, { waitUntil: 'networkidle' });
await page.waitForFunction(() => window.Reveal && Reveal.isReady());
const r = await page.evaluate(() => {
  const s = Reveal.getSlides();
  const semNotas = s.filter(x => !(x.querySelector(':scope > aside.notes')?.textContent.trim())).map(x => x.id || JSON.stringify(Reveal.getIndices(x)));
  return { slides: s.length, semNotas, abertura: !!document.getElementById('abertura'), encerramento: !!document.getElementById('encerramento'),
    ask: document.querySelectorAll('.ask, .cena').length, agendaFechaFig: s.filter(x => /^(agenda|fecha|fig)-/.test(x.id)).map(x => x.id).length };
});
// percorre todos os slides para pegar erros que só aparecem ao navegar
await page.evaluate(async () => { Reveal.configure({ transition: 'none' }); for (const s of Reveal.getSlides()) { const i = Reveal.getIndices(s); Reveal.slide(i.h, i.v, 99); await new Promise(r => setTimeout(r, 5)); } });
await browser.close();
console.log(JSON.stringify({ ...r, semNotas: r.semNotas.length, semNotasLista: r.semNotas.slice(0, 10), errosJS: errs.length, errs: errs.slice(0, 5), externas: ext.length, ext: ext.slice(0, 5) }));
process.exit(errs.length || ext.length || r.semNotas.length || r.abertura || !r.encerramento || r.ask || r.agendaFechaFig ? 1 : 0);
