// Uso: node check_fonts.mjs <index.html> [-v]
// Mede no Chromium, slide a slide (estado final, todos os fragments visíveis), o MENOR tamanho de letra visível em px
// no palco de 1280×720 (texto HTML: font-size computado × escala do reveal; texto de SVG: font-size × escala do SVG na tela).
// Acusa: qualquer texto < 18 px; texto de corpo (bullets, células, cartões, alternativas, painéis) < 28 px;
// conteúdo que passa da borda de baixo do slide; texto de diagrama que vaza da caixa (rect) em que está;
// texto que encosta no contador "N / total" (.chrome .num) ou nas setas (.controls), com 8 px de folga, e caixa/filete/painel que entra nessa faixa (4 px);
// legenda de figura com mais de 1 linha.
// -v lista o menor tamanho de cada slide. Sai com código 1 se achar algum problema.
import { chromium } from 'playwright';
import { pathToFileURL } from 'node:url';
import { resolve } from 'node:path';
const [, , src, flag] = process.argv;
const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: 1280, height: 720 }, reducedMotion: 'reduce' });
const page = await ctx.newPage();
await page.goto(pathToFileURL(resolve(src)).href);
await page.waitForFunction(() => window.__deckReady, null, { timeout: 60000 });
const BODY = '.pts li, .body .pt, .lead-line, table.mini td, .tbl .trow > div, .cena, .ask, .fb, .opts button, .sfpanel, .gv-d, .ffoot .figcap, .strip .st, .chlist a, .hlegend .lg > div, .exgrid dd, .fbox p, .term, .note, .hk-lead, .hook p.big, .csub, .hnames p, .pitch.end .acts small, .efrow > div';
const rows = [];
for (const k of await page.evaluate(() => Reveal.getSlides().map(s => Reveal.getIndices(s)))) {
  await page.evaluate(({ h, v }) => Reveal.slide(h, v, 99), k);
  await page.waitForTimeout(120);
  rows.push(await page.evaluate(BODY => {
    const s = Reveal.getCurrentSlide(), sc = Reveal.getScale(), top = s.getBoundingClientRect().top;
    const vis = el => el.checkVisibility({ checkOpacity: true, checkVisibilityCSS: true }) && !el.closest('aside, script, style, .sr, [hidden]');
    let min = 1e9, minT = '', bottom = 0;
    const small = [], body = [], leaks = [], hits = [], caps = [];
    const box = el => { const r = el.getBoundingClientRect(); return r.width && r.height ? r : null; };
    const contador = [...document.querySelectorAll('.chrome .num, .clv')].map(box).filter(Boolean);   // caixa pode ficar sob as setas (o texto não), nunca sob o contador
    const guard = ['.chrome .num', '.reveal .controls button.enabled'].flatMap(q => [...document.querySelectorAll(q)]).map(e => [...e.querySelectorAll('*'), e].map(box).filter(Boolean)).flat();   // com setas nas bordas, o contêiner .controls cobre a tela: só contam as setas visíveis
    const near = (r, g, m = 8) => r.left < g.right + m && r.right > g.left - m && r.top < g.bottom + m && r.bottom > g.top - m;
    const w = document.createTreeWalker(s, NodeFilter.SHOW_TEXT);
    for (let n; (n = w.nextNode());) {
      const el = n.parentElement, t = n.textContent.trim();
      if (!t || !vis(el)) continue;
      const svg = el.closest('svg');
      const px = parseFloat(getComputedStyle(el).fontSize) * (svg ? el.getScreenCTM()?.a || sc : sc);
      if (px < min) { min = px; minT = t.slice(0, 40); }
      if (px < 17.95) small.push(`${px.toFixed(1)} "${t.slice(0, 30)}"`);
      const rg = document.createRange(); rg.selectNodeContents(n);
      for (const r of rg.getClientRects()) if (guard.some(g => near(r, g))) { hits.push(t.slice(0, 30)); break; }
    }
    s.querySelectorAll(BODY).forEach(el => {
      if (!vis(el) || !el.textContent.trim()) return;
      const px = parseFloat(getComputedStyle(el).fontSize) * sc;
      if (px < 27.95) body.push(`${px.toFixed(1)} "${el.textContent.trim().slice(0, 30)}"`);
    });
    s.querySelectorAll('*').forEach(el => {   // só o que tem texto próprio, e as caixas dos protagonistas
      if (el.closest('aside, svg') || !vis(el)) return;
      if (!el.matches('.vz3, .figbox, .gterm, .strip, .expanel') && ![...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim())) return;
      const r = el.getBoundingClientRect();
      if (r.height) bottom = Math.max(bottom, (r.bottom - top) / sc);
    });
    s.querySelectorAll('*').forEach(el => {   // caixas, filetes e painéis (não só texto) que entram na faixa do contador ou das setas (rodada 3)
      if (el.closest('aside, .sigline, .console, .haze') || (el.closest('svg') && el.tagName !== 'svg') || !vis(el)) return;
      const cs = getComputedStyle(el), paint = el.tagName === 'svg' || el.tagName === 'IMG' || [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim())
        || !/rgba\(0, 0, 0, 0\)|transparent/.test(cs.backgroundColor) || ['Top', 'Right', 'Bottom', 'Left'].some(d => parseFloat(cs['border' + d + 'Width']) > 0 && cs['border' + d + 'Style'] !== 'none');
      // camada sob medida (.bsp-layer) ocupa o slide inteiro por contrato: vale a caixa do que ela desenha, não a do <svg>
      const r = el.matches('.bsp-layer svg') ? [...el.children].map(c => c.getBoundingClientRect()).filter(q => q.width && q.height)
        .reduce((u, q) => u ? { left: Math.min(u.left, q.left), top: Math.min(u.top, q.top), right: Math.max(u.right, q.right), bottom: Math.max(u.bottom, q.bottom) } : q, null) : box(el);
      if (paint && r && contador.some(g => near(r, g, 4))) hits.push('caixa ' + (el.className?.baseVal ?? el.className ?? el.tagName).toString().slice(0, 24));
    });
    s.querySelectorAll('.vscreen svg, .fscreen svg').forEach(g => {
      const rects = [...g.querySelectorAll('rect')].map(x => x.getBBox());
      g.querySelectorAll('text').forEach(t => {
        const b = t.getBBox(), cx = b.x + b.width / 2, cy = b.y + b.height / 2;
        const host = rects.filter(q => cx > q.x && cx < q.x + q.width && cy > q.y && cy < q.y + q.height).sort((a, b) => a.width * a.height - b.width * b.height)[0];
        if (host && (b.x < host.x - 1 || b.x + b.width > host.x + host.width + 1)) leaks.push(t.textContent);
      });
    });
    s.querySelectorAll('.figbox .figcap').forEach(c => { if (vis(c) && c.getClientRects().length && c.getBoundingClientRect().height > parseFloat(getComputedStyle(c).lineHeight) * sc * 1.5) caps.push(c.textContent.slice(0, 30)); if (c.scrollWidth > c.clientWidth + 1) caps.push('cortada: ' + c.textContent.slice(0, 30)); });
    const i = Reveal.getIndices(s);
    return { k: `${i.h}/${i.v || 0}`, id: s.id, cls: s.className.split(' ').filter(c => !/present|past|future/.test(c)).join('.'), min: +min.toFixed(1), minT, small, body, bottom: Math.round(bottom), leaks, hits, caps };
  }, BODY));
}
// explorador: a ficha de cada mesa cabe no painel (revisão 2: X32 Compact/M32R/M32C vazavam até 902 px)
const exl = await page.evaluate(() => { const x = document.querySelector('.explorer'); if (!x) return []; const i = Reveal.getIndices(x); Reveal.slide(i.h, i.v); return [...x.querySelectorAll('.exm')].map(b => b.dataset.m); });
const exBad = [];
for (const m of exl) {
  await page.click(`.explorer .exm[data-m="${m}"]`); await page.waitForTimeout(150);
  const r = await page.evaluate(() => { const p = document.querySelector('.explorer .expanel').getBoundingClientRect(), sc = Reveal.getScale(); return [p.bottom / sc, Math.max(...[...document.querySelectorAll('.explorer .exgrid > div')].map(e => e.getBoundingClientRect().bottom / sc))]; });
  if (r[1] > r[0] - 8 || r[0] > 664) exBad.push(`${m}: ficha até ${Math.round(r[1])}, painel até ${Math.round(r[0])}`);
}
console.log(`explorador: ${exl.length} mesas | ficha fora do painel: ${exBad.length}` + (exBad.length ? ' | ' + exBad.join('; ') : ''));
await browser.close();
const bad = rows.filter(r => r.small.length || r.body.length || r.bottom > 712 || r.leaks.length || r.hits.length || r.caps.length);
if (flag === '-v') rows.forEach(r => console.log(`${r.k.padEnd(6)} ${String(r.min).padStart(5)} px  ${r.cls} ${r.id}  "${r.minT}"`));
const mins = rows.map(r => r.min).sort((a, b) => a - b);
console.log(`slides: ${rows.length} | menor letra do deck: ${mins[0]} px | mediana do menor por slide: ${mins[Math.floor(mins.length / 2)]} px`);
console.log(`texto < 18 px: ${rows.filter(r => r.small.length).length} slides | corpo < 28 px: ${rows.filter(r => r.body.length).length} | passa da altura: ${rows.filter(r => r.bottom > 712).length} | texto vazando da caixa: ${rows.filter(r => r.leaks.length).length} | encosta no contador/setas: ${rows.filter(r => r.hits.length).length} | legenda de figura em 2+ linhas: ${rows.filter(r => r.caps.length).length}`);
bad.forEach(r => console.log(`  ${r.k} ${r.id} ${r.cls}` + (r.small.length ? ` | <18: ${r.small.slice(0, 3).join('; ')}` : '') + (r.body.length ? ` | corpo: ${r.body.slice(0, 2).join('; ')}` : '')
  + (r.bottom > 712 ? ` | até ${r.bottom}px` : '') + (r.leaks.length ? ` | vaza: ${r.leaks.slice(0, 3).join(' / ')}` : '') + (r.hits.length ? ` | contador: ${r.hits.slice(0, 2).join(' / ')}` : '') + (r.caps.length ? ` | legenda: ${r.caps[0]}` : '')));
process.exit(bad.length || exBad.length ? 1 : 0);
