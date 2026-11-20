import './browser-environment.cjs';
// Tecla R (zerar o quiz) em todos os quizzes de uma V2: foto da PERGUNTA → toca uma alternativa (a errada e depois a certa)
// → tecla R → foto. As duas fotos devem ser iguais: as peças que as correções esconderam até o toque têm de sumir de novo.
// Uso: node tools/tecla_r.mjs <index.html> [chromium|webkit] [--so quiz-1,quiz-2]   Sai com código 1 se algum quiz não voltar.
import { chromium, webkit } from 'playwright';
import { pathToFileURL } from 'node:url';
import { resolve } from 'node:path';
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const { PNG } = require('playwright-core/lib/utilsBundle');
const [F, nav = 'chromium', ...rest] = process.argv.slice(2);
const so = rest.includes('--so') ? rest[rest.indexOf('--so') + 1].split(',') : null;
const TOL = +(process.env.TOL ?? 3);
const OPTS = '.opts > button, .opts > .opt, .opts > .alt, button.ans, .alt, .opt, .qkeys > .qk, button.qk';   // o mesmo seletor do material.mjs; .qk = quiz do mackie-analogicas (sessão P, 18/11/2026: sem isto a tecla R dava "sem alternativas")
const b = await (nav === 'webkit' ? webkit : chromium).launch({ args: nav === 'webkit' ? [] : ['--mute-audio'] });
const p = await b.newPage({ viewport: { width: 1280, height: 720 }, reducedMotion: 'reduce' });
const errs = []; p.on('pageerror', e => errs.push(e.message));
await p.goto(pathToFileURL(resolve(F)).href);
await p.waitForFunction(() => window.Reveal?.isReady?.() && (window.__deckReady ?? true), null, { timeout: 60000 });
await p.evaluate(() => document.fonts.ready);
await p.addStyleTag({ content: '.reveal .controls, .reveal .progress { opacity: 0 !important; }' });
const shot = async () => PNG.sync.read(await p.screenshot({ timeout: 90000 })).data;
let bb;
const diff = (a, c) => { let n = 0; bb = [1280, 720, 0, 0]; for (let k = 0; k < a.length; k += 4) if (Math.abs(a[k] - c[k]) > TOL || Math.abs(a[k + 1] - c[k + 1]) > TOL || Math.abs(a[k + 2] - c[k + 2]) > TOL) { n++; const x = (k / 4) % 1280, y = Math.floor(k / 4 / 1280); bb = [Math.min(bb[0], x), Math.min(bb[1], y), Math.max(bb[2], x), Math.max(bb[3], y)]; } return n; };
const go = id => p.evaluate(id => { const i = Reveal.getIndices(document.getElementById(id)); Reveal.slide(i.h, i.v, 99); }, id);
const ids = await p.evaluate(() => Reveal.getSlides().filter(s => /^quiz-\d+$/.test(s.id)).map(s => s.id));
const opcoes = id => p.evaluate(([id, OPTS]) => [...new Set(document.getElementById(id).querySelectorAll(OPTS))].filter(e => !e.closest('svg')).length, [id, OPTS]);
const tocar = (id, k) => p.evaluate(([id, k, OPTS]) => { [...new Set(document.getElementById(id).querySelectorAll(OPTS))].filter(e => !e.closest('svg'))[k].click(); document.activeElement?.blur?.(); }, [id, k, OPTS]);
const certa = id => p.evaluate(([id, OPTS]) => [...new Set(document.getElementById(id).querySelectorAll(OPTS))].filter(e => !e.closest('svg'))
  .findIndex(o => /\b(ok|right|correct|is-ok|certa|good|acerto)\b/.test(o.className) || o.dataset.ok === '1' || o.dataset.ok === 'true'), [id, OPTS]);
const falhas = [];
let testados = 0, vazios = 0;
for (const id of so || ids) {
  const n = await opcoes(id);
  if (!n) { falhas.push(`${id}: sem alternativas`); continue; }
  // 1ª passada descobre a certa; testa uma errada e a certa (são os dois desfechos do quiz)
  await go(id); await p.waitForTimeout(1200); await tocar(id, 0); await p.waitForTimeout(600);
  const k = await certa(id); const casos = k < 0 ? [0] : [k === 0 ? 1 : 0, k];
  for (const op of casos) {
    await go(ids[0] === id ? ids[1] : ids[0]); await p.waitForTimeout(300);   // sai e volta: entra no quiz zerado
    await go(id); await p.waitForTimeout(1500);
    const pre = await shot();
    await tocar(id, op); await p.waitForTimeout(2500);
    const toque = await shot();
    if (process.env.SEM_R) { await go(id); } else await p.keyboard.press('r');   // SEM_R=1: controle negativo (sem a tecla, o quiz não volta)
     await p.waitForTimeout(1500);
    let pos = await shot(), d = diff(pre, pos);
    for (let t = 0; d && t < 3; t++) { await p.waitForTimeout(800); pos = await shot(); d = diff(pre, pos); }
    testados++; if (!diff(pre, toque)) vazios++;
    if (d && process.env.DUMP) { const fs = await import('node:fs'); fs.mkdirSync(process.env.DUMP, { recursive: true }); for (const [n, x] of [['1-pergunta', pre], ['2-toque', toque], ['3-depois-do-R', pos]]) fs.writeFileSync(`${process.env.DUMP}/${id}-${op}-${n}.png`, PNG.sync.write({ width: 1280, height: 720, data: x })); }
    if (d) falhas.push(`${id} (toque ${op === k ? 'na certa' : 'na errada'} #${op}): ${d} px não voltaram em ${bb}${diff(pre, toque) ? '' : ' [o toque não mudou nada]'}`);
  }
}
await b.close();
console.log(`${F} [${nav}] quizzes: ${(so || ids).length} | casos: ${testados} (toque sem efeito visível: ${vazios}) | não voltaram: ${falhas.length} | erros JS: ${errs.length}`);
for (const f of falhas) console.log('  FALHA ' + f);
for (const e of [...new Set(errs)]) console.log('  JS ' + e);
process.exit(falhas.length || errs.length ? 1 : 0);
