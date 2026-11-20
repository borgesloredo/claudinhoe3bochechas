// Confere o padrão de interface e de conteúdo da XR18 num curso. Uso: node check_padrao.mjs <pasta-do-curso> [--sem-texto]
// Sai com 1 se algo faltar. Áudio sempre mudo; não altera nada.
import { createRequire } from 'node:module';
import fs from 'node:fs'; import path from 'node:path';
const C = path.resolve(process.argv[2]), R = createRequire(C + '/tools/package.json');
R(C + '/tools/browser-environment.cjs');
const { chromium } = R('playwright');
const med = (dir, ext) => { const w = fs.readdirSync(path.join(C, dir)).filter(f => f.endsWith(ext)).map(f => fs.readFileSync(path.join(C, dir, f), 'utf8').replace(/<[^>]+>/g, ' ').trim().split(/\s+/).length).sort((a, b) => a - b); return w[w.length >> 1]; };
const prob = [], b = await chromium.launch({ args: ['--mute-audio'] });
const p = await b.newPage({ viewport: { width: 1280, height: 720 }, reducedMotion: 'reduce' });
const erros = []; p.on('pageerror', e => erros.push(String(e)));
const V2 = fs.existsSync(C + '/08-slides-v2/index.html'); // antes da V2, confere o deck de aula
await p.goto('file://' + C + (V2 ? '/08-slides-v2' : '/07-slides') + '/index.html'); await p.waitForFunction(() => window.Reveal?.isReady());
const r = await p.evaluate(async () => {
  const vis = e => { if (!e) return false; const q = e.getBoundingClientRect(), s = getComputedStyle(e); return q.width > 0 && q.height > 0 && s.visibility !== 'hidden' && s.display !== 'none'; };
  const ids = Reveal.getSlides().map(s => s.id), cnt = document.querySelector('.chrome .num') || document.querySelector('.slide-number');
  const txt = () => (cnt?.textContent || '').replace(/\s+/g, ''), out = { ids, sobre: [], contador: [] }, go = id => { const i = Reveal.getIndices(document.getElementById(id)); Reveal.slide(i.h, i.v, 999); };
  for (const [k, id] of ids.entries()) {
    go(id); await new Promise(f => setTimeout(f, 120));
    if (txt() !== `${k + 1}/${ids.length}`) out.contador.push(`${id}: "${txt()}"`);
    if (!vis(cnt)) { out.sobre.push(id + ': contador invisível'); continue; }
    const q = cnt.getBoundingClientRect(), cur = Reveal.getCurrentSlide();
    const w = document.createTreeWalker(cur, NodeFilter.SHOW_TEXT); let n;
    while ((n = w.nextNode())) { if (!n.textContent.trim() || !n.parentElement || n.parentElement.closest('aside.notes,script,style')) continue;
      const e = n.parentElement, s = getComputedStyle(e); if (s.visibility === 'hidden' || +s.opacity < .05) continue; const g = document.createRange(); g.selectNodeContents(n);
      for (const t of g.getClientRects()) if (t.width && t.left < q.right && q.left < t.right && t.top < q.bottom && q.top < t.bottom) { out.sobre.push(`${id}: "${n.textContent.trim().slice(0, 18)}"`); break; } }
  }
  go(ids[0]);
  const c = Reveal.getConfig(); out.setas = !!c.controls; out.progresso = vis(document.querySelector('.reveal .progress')) || vis(document.querySelector('.chrome .rail'));
  const su = document.getElementById('sumario'); out.sumario = su ? su.querySelectorAll('a[href^="#/"],[data-go],[data-goto],[data-cap],[data-href],button').length : 0;
  out.fluxo = !!document.querySelector('svg.flow,.flow,[data-kit=flow]'); out.cta = document.body.innerHTML.includes('loredoborges.com.br'); out.fundo = getComputedStyle(document.body).backgroundColor;
  out.titulos = Reveal.getSlides().map(s => (s.querySelector('h1,h2,.ttl')?.textContent || '').trim()); return out;
});
const lum = /\d+/g.test(r.fundo) ? r.fundo.match(/\d+/g).slice(0, 3).reduce((a, x) => a + +x, 0) / 3 : 0;
if (r.contador.length) prob.push(`contador errado em ${r.contador.length}: ${r.contador.slice(0, 3)}`);
if (r.sobre.length) prob.push(`contador sobre texto em ${r.sobre.length}: ${r.sobre.slice(0, 8)}`);
if (lum > 120) prob.push(`fundo claro fora do slide: ${r.fundo}`);
if (!r.setas) prob.push('sem setas'); if (!r.progresso) prob.push('sem indicador de progresso'); if (!r.cta) prob.push('sem CTA');
if (r.sumario < 20) prob.push(`sumário com ${r.sumario} destinos clicáveis`);
const tem = (re, tre) => r.ids.some(i => re.test(i)) || (tre && r.titulos.some(t => tre.test(t)));
for (const [nome, re, tre] of [['capa', /^capa$/], ['sumario', /^sumario$/], ['como-usar', /^como-usar$/], ['explorador', /^explorador$/], ['caminho do sinal', /^(caminho|flow-)/], ['encerramento', /^encerramento$/], ['glossario', /^glossario$/, /gloss/i]])
  if (!tem(re, tre) && !(nome === 'caminho do sinal' && r.fluxo)) prob.push('falta tela: ' + nome);
if (V2 && !process.argv.includes('--sem-texto')) { const a = med('tools/v2/script', '.txt'), i = med('tools/v2/info', '.html'); if (a < 280) prob.push(`roteiros curtos: mediana ${a} (mínimo 280)`); if (i < 170) prob.push(`explicações curtas: mediana ${i} (mínimo 170)`); }
if (erros.length) prob.push('erros JS: ' + erros.slice(0, 2));
await b.close();
console.log(path.basename(C), prob.length ? 'FALTA:\n  ' + prob.join('\n  ') : 'OK: padrão completo'); process.exit(prob.length ? 1 : 0);
