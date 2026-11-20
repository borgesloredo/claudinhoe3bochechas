import './browser-environment.cjs';
// Uso: node tools/antes_depois.mjs <antes.html> <depois.html> <chromium|webkit> [--so id1,id2]
// Prova que a troca para pilhas por capítulo não mudou nada além da navegação:
//  1) TODOS os slides: captura do antes × depois, estado final determinístico (reduced motion + fragments visíveis), diferença ZERO pixel;
//  2) teclas reais no depois: → vai ao cap-(N+1); ↓ anda dentro do capítulo; ← volta ao cap-(N−1); Reveal.next() segue a ordem de leitura;
//  3) nenhum erro de JS no depois que não exista no antes.
// Sai com código 1 se algo falhar.
import { chromium, webkit } from 'playwright';
import { pathToFileURL } from 'node:url';
import { resolve } from 'node:path';
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const { PNG } = require('playwright-core/lib/utilsBundle');
const [A, B, nav = 'chromium', ...rest] = process.argv.slice(2);
const so = rest.includes('--so') ? rest[rest.indexOf('--so') + 1].split(',') : null;
const browser = await (nav === 'webkit' ? webkit : chromium).launch({ args: nav === 'webkit' ? [] : ['--mute-audio'] });
const errs = { antes: [], depois: [] };
async function open(src, k) {
  const p = await browser.newPage({ viewport: { width: 1280, height: 720 }, reducedMotion: 'reduce' });
  p.on('pageerror', e => errs[k].push(e.message));
  await p.goto(pathToFileURL(resolve(src)).href);
  await p.waitForFunction(() => window.Reveal?.isReady?.() && (window.__deckReady ?? true), null, { timeout: 60000 });
  await p.evaluate(() => document.fonts.ready);
  // as setas do reveal (canto inferior direito) mudam de propósito: agora mostram ↑↓ dentro do capítulo; ficam fora da comparação
  await p.addStyleTag({ content: '.reveal .controls { opacity: 0 !important; }' });
  await p.waitForTimeout(400);
  return p;
}
const pa = await open(A, 'antes'), pb = await open(B, 'depois');
const go = (p, id) => p.evaluate(id => { const i = Reveal.getIndices(document.getElementById(id)); Reveal.slide(i.h, i.v, 99); }, id);
const shot = async p => PNG.sync.read(await p.screenshot()).data;
let bb;
// TOL: variação de cor tolerada por canal (0–255). Aninhar a pilha muda a composição na GPU em até 3 níveis (invisível); acima disso é diferença real.
const TOL = +(process.env.TOL ?? 3);
const diff = (a, b) => { let n = 0; bb = [1280, 720, 0, 0]; for (let k = 0; k < a.length; k += 4) if (Math.abs(a[k] - b[k]) > TOL || Math.abs(a[k + 1] - b[k + 1]) > TOL || Math.abs(a[k + 2] - b[k + 2]) > TOL) { n++; const x = (k / 4) % 1280, y = (k / 4 / 1280) | 0; bb = [Math.min(bb[0], x), Math.min(bb[1], y), Math.max(bb[2], x), Math.max(bb[3], y)]; } return n; };
const falhas = [];
const idsA = await pa.evaluate(() => Reveal.getSlides().map(s => s.id)), idsB = await pb.evaluate(() => Reveal.getSlides().map(s => s.id));
if (idsA.join() !== idsB.join()) falhas.push(`ordem dos slides mudou: antes ${idsA.length}, depois ${idsB.length}`);

// 1) identidade visual
const amostra = +process.env.AMOSTRA || 1;   // AMOSTRA=8: só 1 slide a cada 8 (triagem rápida)
for (const id of (so || idsA).filter((_, k) => k % amostra === 0)) {
  await Promise.all([go(pa, id), go(pb, id)]);
  await pa.waitForTimeout(150);
  let [a, b] = await Promise.all([shot(pa), shot(pb)]), d = diff(a, b);
  for (let t = 0; d && t < 3; t++) { await pa.waitForTimeout(600); [a, b] = await Promise.all([shot(pa), shot(pb)]); d = diff(a, b); }
  if (d) { falhas.push(`${id}: ${d} px diferentes em ${bb}`); if (process.env.DUMP) { const fs = await import('node:fs'); fs.mkdirSync(process.env.DUMP, { recursive: true }); fs.writeFileSync(`${process.env.DUMP}/${id}-antes.png`, await pa.screenshot()); fs.writeFileSync(`${process.env.DUMP}/${id}-depois.png`, await pb.screenshot()); } }
}

// 2) navegação por teclas no depois
const estrutura = await pb.evaluate(() => [...document.querySelectorAll('.reveal .slides > section')].map(s =>
  s.querySelector(':scope > section') ? [...s.querySelectorAll(':scope > section')].map(x => x.id) : [s.id]));
const pilhas = estrutura.filter(g => g.length > 1 && /^cap-\d+$/.test(g[0]));
const atual = () => pb.evaluate(() => Reveal.getCurrentSlide().id);
const tecla = async (k) => { await pb.keyboard.press(k); await pb.waitForTimeout(120); return atual(); };
// o reveal lembra o último slide visto em cada pilha (data-previous-indexv); a passada 1 visitou todos, então zera como numa leitura nova
const ir = async id => { await pb.evaluate(() => document.querySelectorAll('[data-previous-indexv]').forEach(s => s.removeAttribute('data-previous-indexv'))); await go(pb, id); await pb.evaluate(() => document.activeElement?.blur?.()); await pb.waitForTimeout(80); };
if (pilhas.length < 10) falhas.push(`só ${pilhas.length} capítulos em pilha`);
// o próximo de cada capítulo é o item seguinte no nível de cima (outro capítulo ou um slide solto, como resumo/glossário)
for (let k = 0; k + 1 < pilhas.length; k++) {
  const g = pilhas[k], prox = estrutura[estrutura.indexOf(g) + 1][0];
  await ir(g[0]);
  let r = await tecla('ArrowDown'); if (r !== g[1]) falhas.push(`↓ em ${g[0]} foi para ${r}, esperado ${g[1]}`);
  await ir(g[1]);
  r = await tecla('ArrowRight'); if (r !== prox) falhas.push(`→ em ${g[1]} foi para ${r}, esperado ${prox}`);
  await ir(g[1]); await tecla('ArrowRight');
  r = await tecla('ArrowLeft'); if (!g.includes(r)) falhas.push(`← em ${prox} foi para ${r}, esperado o capítulo ${g[0]}`);
  await ir(g[g.length - 1]);
  r = await pb.evaluate(() => { Reveal.next(); return Reveal.getCurrentSlide().id; });
  if (r !== prox) falhas.push(`próximo depois de ${g[g.length - 1]} foi para ${r}, esperado ${prox}`);
}
await browser.close();
const novos = errs.depois.filter(e => !errs.antes.includes(e));
console.log(`${B} [${nav}] slides: ${idsA.length} | capítulos em pilha: ${pilhas.length} | falhas: ${falhas.length} | erros JS novos: ${novos.length} (antes ${errs.antes.length})`);
falhas.slice(0, 40).forEach(f => console.log('  FALHA', f));
if (falhas.length > 40) console.log(`  … e mais ${falhas.length - 40}`);
novos.forEach(e => console.log('  ERRO JS', e));
process.exit(falhas.length || novos.length ? 1 : 0);
