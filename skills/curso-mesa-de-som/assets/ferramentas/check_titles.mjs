// Uso: node check_titles.mjs <index.html>
// Passada nos títulos (Agente 13, correcao14:13 r2). Lista para leitura:
//  (a) slides cujo título promete "regra", "confusão", "pergunta", "erro", "truque" (ou dica, mito, armadilha), com o corpo visível;
//  (b) slides cujo selo cobre X AIR e X32/M32, mas o corpo cita só uma família;
//  (c) slides cujo título cita um modelo que o corpo não mostra.
// Não corrige nada: (a) é para ler; (b) e (c) devem sair vazios ou justificados em 07-slides/revisao-redundancia.md.
import { chromium } from 'playwright';
import { pathToFileURL } from 'node:url';
import { resolve } from 'node:path';
const browser = await chromium.launch();
const page = await browser.newPage();
await page.goto(pathToFileURL(resolve(process.argv[2])).href);
await page.waitForFunction(() => window.Reveal && Reveal.isReady());
const r = await page.evaluate(() => Reveal.getSlides().map(s => {
  const c = s.cloneNode(true);
  const chips = [...c.querySelectorAll('.chips .chip')].map(e => e.textContent.trim());
  c.querySelectorAll('aside, svg, section, script, style, .chips, .kicker, .vh, .vsteps, .vfoot').forEach(e => e.remove());  // .vh/.vsteps/.vfoot: moldura do diagrama (título e teclas repetem o corpo)
  const h = c.querySelector('h3, h2'); const t = h?.textContent.trim() || ''; h?.remove();
  const i = Reveal.getIndices(s);
  return { k: `${i.h}/${i.v || 0}`, id: s.id, chips, t, body: c.textContent.replace(/\s+/g, ' ').trim() };
}));
await browser.close();
if (process.env.JSON) { console.log(JSON.stringify(r)); process.exit(0); } // JSON=1: título, selo e corpo de cada slide
const KW = /regra|confus|pergunt|erro|truque|dica|mito|armadilh/i;
const XA = /X ?AIR|M ?AIR|XR1[268]|X18|MR1[28]/, XM = /X32|M32/;
const MOD = /X32 (?:Rack|Compact|Producer)|M32[RC]?|X32|XR1[268]|X18|MR1[28]/g;
const out = { a: [], b: [], c: [] };
for (const s of r) {
  if (!s.body) continue;
  const tag = `${s.k} ${s.id} | ${s.t}`;
  if (KW.test(s.t)) out.a.push(`${tag}\n      ${s.body.slice(0, 300)}`);
  const ca = s.chips.some(c => XA.test(c)), cm = s.chips.some(c => XM.test(c));
  const ba = XA.test(s.body), bm = XM.test(s.body);
  if (ca && cm && ba !== bm) out.b.push(`${tag} | selo: ${s.chips.join(', ')} | corpo só ${ba ? 'X AIR' : 'X32/M32'}`);
  const miss = [...new Set(s.t.match(MOD) || [])].filter(m => !s.body.includes(m));
  if (miss.length) out.c.push(`${tag} | fora do corpo: ${miss.join(', ')}`);
}
console.log(`(a) títulos com promessa: ${out.a.length}\n` + out.a.map(x => '  ' + x).join('\n'));
console.log(`(b) selo com as duas famílias, corpo com uma: ${out.b.length}\n` + out.b.map(x => '  ' + x).join('\n'));
console.log(`(c) título cita modelo fora do corpo: ${out.c.length}\n` + out.c.map(x => '  ' + x).join('\n'));
