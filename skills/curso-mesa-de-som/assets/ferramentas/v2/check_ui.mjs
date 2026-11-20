// Uso: node tools/v2/check_ui.mjs <v2/index.html> [pasta-capturas]
// Teste de uso da V2 montada com o conteúdo de teste (tools/v2/_teste: capa e s5-1-2 com popup + áudio, quiz-7 só com popup):
// popup abre/fecha (botão, Esc, clique fora), não navega o reveal enquanto aberto, termo do glossário abre e volta, áudio toca e para ao trocar de slide,
// botões desabilitados sem conteúdo, nenhuma nota no DOM, nenhuma requisição externa, nenhum erro JS.
import { chromium } from 'playwright';
import { pathToFileURL } from 'node:url';
import { resolve } from 'node:path';
const [, , src, shots] = process.argv;
const browser = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] });
const p = await browser.newPage({ viewport: { width: 1280, height: 720 } });
const errs = [], ext = [];
p.on('pageerror', e => errs.push(e.message));
p.on('request', r => { if (!/^(file|data|blob|about):/.test(r.url())) ext.push(r.url()); });
await p.goto(pathToFileURL(resolve(src)).href);
await p.waitForFunction(() => window.__deckReady);
const ok = [], bad = [];
const t = (nome, cond) => (cond ? ok : bad).push(nome);
const go = id => p.evaluate(id => { const i = Reveal.getIndices(document.getElementById(id)); Reveal.slide(i.h, i.v); }, id);
const st = () => p.evaluate(() => ({ id: Reveal.getCurrentSlide().id, open: document.querySelector('#v2pop').open,
  i: document.querySelector('.v2b.i').disabled, p: document.querySelector('.v2b.p').disabled, def: !document.querySelector('.v2-def').hidden }));

t('sem notas no DOM', await p.evaluate(() => !document.querySelector('aside.notes') && !window.RevealNotes));
await go('capa'); await p.waitForTimeout(300);
let s = await st();
t('capa: (i) e ▶ habilitados', !s.i && !s.p);
await p.click('.v2b.i');
s = await st();
t('capa: popup abre', s.open);
t('capa: título do slide no popup, com separador entre as linhas', (await p.textContent('#v2-t')) === 'X AIR · M AIR · X32 · M32');
t('capa: 3 termos clicáveis, verbete inexistente vira texto', await p.evaluate(() => document.querySelectorAll('.v2-info .gl').length === 3 && !document.querySelector('[data-t="nao-existe"]')));
if (shots) await p.screenshot({ path: `${shots}/ui-popup.png` });
for (const k of ['ArrowRight', 'Space', 'n', 'o', 'r']) await p.keyboard.press(k);
s = await st();
t('popup aberto: teclas não navegam', s.id === 'capa' && s.open);
await p.click('.v2-info .gl[data-t="x-air"]');
s = await st();
t('termo: definição abre no popup', s.def && (await p.textContent('.v2-def h3')).includes('X AIR'));
if (shots) await p.screenshot({ path: `${shots}/ui-termo.png` });
await p.click('.v2-back');
s = await st();
t('termo: voltar', !s.def && await p.evaluate(() => document.activeElement?.dataset.t === 'x-air'));
await p.keyboard.press('Escape');
s = await st();
t('Esc fecha e o slide não muda', !s.open && s.id === 'capa');
t('foco volta ao (i)', await p.evaluate(() => document.activeElement === document.querySelector('.v2b.i')));
await p.keyboard.press('Enter');
t('Enter no (i) abre', (await st()).open);
await p.mouse.click(8, 8);
s = await st();
t('clique fora fecha', !s.open && s.id === 'capa');

// áudio
await p.click('.v2b.p');
await p.waitForTimeout(900);
const a1 = await p.evaluate(() => ({ on: document.querySelector('.v2b.p').classList.contains('on'), off: getComputedStyle(document.querySelector('.v2b.p .bar')).strokeDashoffset }));
t('▶ toca e o anel de progresso anda', a1.on && parseFloat(a1.off) < 100);
if (shots) await p.screenshot({ path: `${shots}/ui-tocando.png`, clip: { x: 1180, y: 0, width: 100, height: 110 } });
await p.click('.v2b.p'); await p.waitForTimeout(100);
t('▶ de novo pausa', await p.evaluate(() => !document.querySelector('.v2b.p').classList.contains('on')));
await p.click('.v2b.p'); await p.waitForTimeout(300);
await p.focus('.v2b.p'); await p.keyboard.press('Space'); await p.waitForTimeout(100);
s = await st();
t('Espaço no ▶ não troca de slide', s.id === 'capa');
await p.click('.v2b.p'); await p.waitForTimeout(300);
await go('s5-1-2'); await p.waitForTimeout(200);
t('trocar de slide para o áudio', await p.evaluate(() => !document.querySelector('.v2b.p').classList.contains('on') && getComputedStyle(document.querySelector('.v2b.p .bar')).strokeDashoffset.startsWith('100')));

await go('quiz-7'); await p.waitForTimeout(300);
s = await st();
t('quiz-7: (i) habilitado, ▶ desabilitado', !s.i && s.p);
await p.click('.v2b.i');
t('quiz-7: texto longo rola', await p.evaluate(() => { const b = document.querySelector('.v2-bd'); return b.scrollHeight > b.clientHeight + 50; }));
if (shots) await p.screenshot({ path: `${shots}/ui-longo.png` });
await p.keyboard.press('Escape');
await go('s3-1-1'); await p.waitForTimeout(300);
s = await st();
t('slide sem conteúdo: os dois desabilitados', s.i && s.p);
if (shots) await p.screenshot({ path: `${shots}/ui-desabilitado.png` });

// celular (deitado): popup cabe na tela
await p.setViewportSize({ width: 740, height: 360 });
await go('s5-1-2'); await p.waitForTimeout(300);
await p.click('.v2b.i');
t('celular: popup cabe na tela', await p.evaluate(() => { const r = document.querySelector('#v2pop').getBoundingClientRect(); return r.left >= 0 && r.right <= innerWidth && r.top >= 0 && r.bottom <= innerHeight; }));
if (shots) await p.screenshot({ path: `${shots}/ui-celular.png` });

await p.keyboard.press('Escape');

// área de clique ≥ 40 px de tela em qualquer janela, sem cobrir conteúdo do palco fora da faixa vazia (x ≥ 1220, y ≤ 100)
for (const [w, h] of [[1280, 720], [1440, 900], [1024, 640], [844, 390], [390, 844], [1920, 1080]]) {
  await p.setViewportSize({ width: w, height: h }); await p.waitForTimeout(250);
  const m = await p.evaluate(() => {
    const st = document.querySelector('.reveal .slides').getBoundingClientRect(), k = st.width / 1280;
    return [...document.querySelectorAll('.v2b')].map(b => { const r = b.getBoundingClientRect();
      const x0 = (Math.max(r.left, st.left) - st.left) / k, y1 = (Math.min(r.bottom, st.bottom) - st.top) / k;
      const dentro = r.right > st.left + .5 && r.left < st.right - .5 && r.bottom > st.top + .5 && r.top < st.bottom - .5;
      return { w: r.width, h: r.height, tela: r.left >= 0 && r.top >= 0 && r.right <= innerWidth && r.bottom <= innerHeight, livre: Reveal.isScrollView() || !dentro || (x0 >= 1219.5 && y1 <= 100.5) }; });   // em pé o reveal vira rolagem: os botões ficam fixos na borda, como o atalho do sumário
  });
  t(`${w}×${h}: botões ≥ 40 px, na tela e fora do conteúdo`, m.every(b => b.w >= 39.9 && b.h >= 39.9 && b.tela && b.livre));
  if (!m.every(b => b.w >= 39.9 && b.h >= 39.9 && b.tela && b.livre)) console.log('   ', w, h, JSON.stringify(m));
  const [a, b] = await p.evaluate(() => [...document.querySelectorAll('.v2b')].map(b => b.getBoundingClientRect()).map(r => [r.left, r.top, r.right, r.bottom]));
  t(`${w}×${h}: (i) e ▶ não se sobrepõem`, a[2] <= b[0] || b[2] <= a[0] || a[3] <= b[1] || b[3] <= a[1]);
  if (shots) await p.screenshot({ path: `${shots}/ui-botoes-${w}x${h}.png` });
}

// depois de girar o celular (em pé → deitado) o reveal regrava o palco (innerHTML): os botões novos continuam funcionando.
// Página separada: a própria V1 dá erro JS nesse giro (animação da capa, "reading 'shut'"); isso é da V1 e não entra na conta.
{
  const q = await browser.newPage({ viewport: { width: 844, height: 390 } }), v1err = [];
  q.on('pageerror', e => v1err.push(e.message));
  await q.goto(pathToFileURL(resolve(src)).href + '#/s5-1-2'); await q.waitForFunction(() => window.__deckReady);
  await q.setViewportSize({ width: 390, height: 844 }); await q.waitForTimeout(400);
  await q.setViewportSize({ width: 844, height: 390 }); await q.waitForTimeout(400);
  await q.click('.v2b.i');
  t('depois de girar: (i) abre o popup', await q.evaluate(() => document.querySelector('#v2pop').open));
  await q.keyboard.press('Escape');
  await q.click('.v2b.p'); await q.waitForTimeout(600);
  t('depois de girar: ▶ toca', await q.evaluate(() => document.querySelector('.v2b.p').classList.contains('on')));
  if (v1err.some(m => !/shut/.test(m))) errs.push(...v1err.filter(m => !/shut/.test(m)));
  await q.close();
}

await browser.close();
t('nenhuma requisição externa', !ext.length);
t('nenhum erro JS', !errs.length);
console.log(`ok ${ok.length} | falhas ${bad.length}`);
bad.forEach(b => console.log('  FALHA', b));
errs.forEach(e => console.log('  ERRO JS', e));
process.exit(bad.length ? 1 : 0);
