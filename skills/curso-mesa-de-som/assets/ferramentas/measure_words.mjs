// Uso: node measure_words.mjs <index.html> [limite=50]
// DUMP=1 node measure_words.mjs <index.html> lista o texto visível de cada slide (para conferir se cada item se lê sozinho).
// Conta palavras visíveis por slide (sem notas do apresentador e sem SVG), com todos os fragments.
import { chromium } from 'playwright';
import { pathToFileURL } from 'node:url';
import { resolve } from 'node:path';
const [, , src, lim = '50'] = process.argv;
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
await page.goto(pathToFileURL(resolve(src)).href);
await page.waitForFunction(() => window.Reveal && Reveal.isReady());
const r = await page.evaluate(() => Reveal.getSlides().map(s => {
  const c = s.cloneNode(true);
  c.querySelectorAll('aside, svg, section, script, style, .vh, .vsteps, .vfoot').forEach(e => e.remove());  // moldura do diagrama (título e teclas repetem o corpo), como o texto do SVG
  const { h, v } = Reveal.getIndices(s);
  const t = (c.textContent || '').trim();
  const items = [...c.querySelectorAll('h2, h3, li, p, td, th, .term, .note, figcaption')].filter(e => !e.querySelector('li, p, td, th')).map(e => e.textContent.replace(/\s+/g, ' ').trim()).filter(Boolean);
  return { k: `${h}/${v}`, id: s.id, items, t: s.querySelector(':scope > h3, :scope > h2')?.textContent || s.id, w: t ? t.split(/\s+/).length : 0 };
}));
await browser.close();
if (process.env.DUMP) { r.forEach(x => console.log(`## ${x.k} ${x.id}\n` + x.items.map(i => '  - ' + i).join('\n'))); process.exit(0); } // DUMP=1: texto visível de cada slide, para ler
const w = r.map(x => x.w).sort((a, b) => a - b), q = p => w[Math.floor(p * (w.length - 1))];
const tot = w.reduce((a, b) => a + b, 0);
console.log(`slides=${r.length} palavras=${tot} média=${(tot / r.length).toFixed(1)} p50=${q(.5)} p75=${q(.75)} p90=${q(.9)} máx=${w.at(-1)} >${lim}: ${r.filter(x => x.w > +lim).length}`);
r.sort((a, b) => b.w - a.w).slice(0, +(process.env.TOP || 12)).forEach(x => console.log(`  ${x.k} ${x.w} ${x.t}`));
