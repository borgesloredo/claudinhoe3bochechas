// Uso: node tools/v2/check_identico.mjs [v2/index.html] [--so id1,id2]
// Garante "slides idênticos": para TODOS os slides, compara a captura da V1 e da V2 (botões da V2 ocultos pela classe de teste .v2-test),
// em estado final determinístico (prefers-reduced-motion + todos os fragments visíveis). Exige diferença ZERO pixel.
// Também mede a sobreposição: nenhum pixel de conteúdo da V1 (slide visível vs slide oculto) pode cair dentro da área dos botões da V2.
// Sai com código 1 se algum slide falhar.
import { chromium } from 'playwright';
import { pathToFileURL, fileURLToPath } from 'node:url';
import { resolve, dirname } from 'node:path';
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const { PNG } = require('playwright-core/lib/utilsBundle');
const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '../..');
const args = process.argv.slice(2), so = args.includes('--so') ? args[args.indexOf('--so') + 1].split(',') : null;
const V1 = args.includes('--base') ? resolve(args[args.indexOf('--base') + 1]) : resolve(ROOT, 'entregas/v1-aulas/deck/index.html');
const V2 = resolve(args.find((a, i) => a.endsWith('.html') && args[i - 1] !== '--base') || resolve(ROOT, '08-slides-v2/index.html'));

const browser = await chromium.launch();
const errs = [];
async function open(src, cls) {
  const p = await browser.newPage({ viewport: { width: 1280, height: 720 }, reducedMotion: 'reduce' });
  p.on('pageerror', e => errs.push(`${cls}: ${e.message}`));
  await p.goto(pathToFileURL(src).href);
  await p.waitForFunction(() => window.__deckReady);
  // setas do reveal: a dica "pode descer" pula em loop (controlsTutorial) e as setas fazem fade. É cromo do reveal, não slide: congela igual nas duas
  await p.addStyleTag({ content: '.v2sem .reveal .slides > section, .v2sem .reveal .controls { visibility: hidden !important; } .reveal .controls, .reveal .controls * { animation: none !important; transition: none !important; }' });
  await p.evaluate(c => document.documentElement.classList.add(c), cls);
  return p;
}
const p1 = await open(V1, 'v1'), p2 = await open(V2, 'v2-test');
const go = (p, id) => p.evaluate(id => { const i = Reveal.getIndices(document.getElementById(id)); Reveal.slide(i.h, i.v, 99); }, id);
const shot = async p => PNG.sync.read(await p.screenshot()).data;
const ids = so || await p1.evaluate(() => Reveal.getSlides().map(s => s.id));
// área dos botões em px do palco (a 1280×720 o palco tem escala 1), com 2 px de folga
const boxes = await p2.evaluate(() => [...document.querySelectorAll('.v2b')].map(b => { const r = b.getBoundingClientRect(); return [r.left - 2, r.top - 2, r.right + 2, r.bottom + 2].map(Math.round); }));

let bb;   // retângulo que contém os pixels diferentes (para achar a causa)
const diff = (a, b) => { let n = 0; bb = [1280, 720, 0, 0]; for (let k = 0; k < a.length; k += 4) if (a[k] !== b[k] || a[k + 1] !== b[k + 1] || a[k + 2] !== b[k + 2]) { n++; const x = (k / 4) % 1280, y = (k / 4 / 1280) | 0; bb = [Math.min(bb[0], x), Math.min(bb[1], y), Math.max(bb[2], x), Math.max(bb[3], y)]; } return n; };
const inBoxes = (a, b) => { let n = 0; for (const [x0, y0, x1, y1] of boxes) for (let y = y0; y < y1; y++) for (let x = x0; x < x1; x++) { const k = (y * 1280 + x) * 4; if (Math.abs(a[k] - b[k]) + Math.abs(a[k + 1] - b[k + 1]) + Math.abs(a[k + 2] - b[k + 2]) > 6) n++; } return n; };
const falhas = [];
for (const id of ids) {
  await Promise.all([go(p1, id), go(p2, id)]);
  await p1.waitForTimeout(150);
  let [a, b] = await Promise.all([shot(p1), shot(p2)]), d = diff(a, b);
  for (let t = 0; d && t < 2; t++) { await p1.waitForTimeout(500); [a, b] = await Promise.all([shot(p1), shot(p2)]); d = diff(a, b); }   // algo ainda assentando: tenta de novo
  await p1.evaluate(() => document.documentElement.classList.add('v2sem'));
  const vazio = await shot(p1);
  await p1.evaluate(() => document.documentElement.classList.remove('v2sem'));
  const sob = inBoxes(a, vazio);
  if (d || sob) falhas.push(`${id}: ${d} px diferentes (${(d / 9216).toFixed(3)}%${d ? ' em ' + bb : ''}), ${sob} px de conteúdo sob os botões`);
}
await browser.close();
console.log(`slides comparados: ${ids.length} | botões em ${JSON.stringify(boxes)} | falhas: ${falhas.length} | erros JS: ${errs.length}`);
falhas.forEach(f => console.log('  FALHA', f));
errs.forEach(e => console.log('  ERRO JS', e));
process.exit(falhas.length || errs.length ? 1 : 0);
