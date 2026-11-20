// Uso: node shot_motion.mjs <index.html> <pasta-saida> [id ...]
// Para cada slide (ou só os ids pedidos), uma tira de 4 quadros da entrada: 0 ms, 300 ms, 800 ms e o estado final
// (todos os fragments mostrados, animações terminadas). Salva <pasta-saida>/<id>.png; sem ids, apaga as tiras antigas.
// O relógio do GSAP fica parado e é posto em cada instante (seek): os quadros saem iguais em qualquer máquina.
import { chromium } from 'playwright';
import { pathToFileURL } from 'node:url';
import { resolve, join } from 'node:path';
import { mkdirSync, readdirSync, rmSync } from 'node:fs';
const [, , src, out, ...want] = process.argv;
mkdirSync(out, { recursive: true });
if (!want.length) for (const f of readdirSync(out)) if (f.endsWith('.png')) rmSync(join(out, f));
const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: 1280, height: 720 } });
const page = await ctx.newPage(), strip = await ctx.newPage();
const errs = [];
page.on('pageerror', e => errs.push(e.message));
page.on('console', m => m.type() === 'error' && errs.push(m.text()));
await page.goto(pathToFileURL(resolve(src)).href);
await page.waitForFunction(() => window.__deckReady, null, { timeout: 60000 });
let list = await page.evaluate(() => Reveal.getSlides().map(s => { const i = Reveal.getIndices(s); return { h: i.h, v: i.v || 0, id: s.id || `${i.h}-${i.v || 0}` }; }));
if (want.length) list = list.filter(s => want.includes(s.id));
const T = [.017, .3, .8], shot = async () => (await page.screenshot({ type: 'jpeg', quality: 75 })).toString('base64');
for (const s of list) {
  // sai para um slide vizinho (a entrada do alvo sempre roda do zero) e para o relógio
  await page.evaluate(({ h, v }) => { Reveal.slide(h ? h - 1 : h + 1, 0); }, s);
  await page.waitForTimeout(60);
  const t0 = await page.evaluate(({ h, v }) => { const t = gsap.globalTimeline.time(); Reveal.slide(h, v, -1); gsap.globalTimeline.pause(); return t; }, s);
  await page.mouse.move(640, 1);
  const imgs = [];
  for (const t of T) { await page.evaluate(t => { gsap.globalTimeline.seek(t, false); }, t0 + t); await page.waitForTimeout(40); imgs.push(await shot()); }
  await page.evaluate(({ h, v, t }) => { Reveal.slide(h, v, 99); gsap.globalTimeline.seek(t + 9, false); gsap.globalTimeline.resume(); }, { ...s, t: t0 + .8 });
  await page.waitForTimeout(1100);   // animações CSS (linhas do errfix) e tweens criados depois do seek
  imgs.push(await shot());
  await strip.setViewportSize({ width: 4 * 480 + 5 * 10, height: 312 });
  await strip.setContent(`<body style="margin:0;background:#050607;display:flex;gap:10px;padding:10px;font:700 16px Menlo,monospace;color:#ffe2b8">${imgs.map((b, i) =>
    `<figure style="margin:0"><img src="data:image/jpeg;base64,${b}" style="width:480px;height:270px;display:block;border:1px solid #28313b"><figcaption style="padding:3px 2px 0">${s.id} · ${['0 ms', '300 ms', '800 ms', 'final'][i]}</figcaption></figure>`).join('')}</body>`);
  await strip.screenshot({ path: join(out, `${s.id}.png`) });
}
await browser.close();
console.log(`tiras: ${list.length} | erros JS: ${errs.length}`);
if (errs.length) console.log([...new Set(errs)].slice(0, 8).join('\n'));
