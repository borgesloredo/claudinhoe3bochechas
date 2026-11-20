// Uso: node shot_sheets.mjs <index.html> <pasta-saida> [por-folha=24]
// Folhas de contato de TODOS os slides no estado final (todos os fragments visíveis; quiz respondido, bloco, termo e mesa clicados),
// com o número h/v em cada miniatura. Apaga as folhas antigas (sheet-*.png) da pasta e escreve index.txt (quais slides em cada folha).
// Roda com prefers-reduced-motion: as entradas vão direto ao estado final, que é o mesmo do movimento completo.
import { chromium } from 'playwright';
import { pathToFileURL } from 'node:url';
import { resolve, join } from 'node:path';
import { mkdirSync, readdirSync, rmSync, writeFileSync } from 'node:fs';
const [, , src, out, per = '24'] = process.argv;
const N = +per, COLS = 4;
mkdirSync(out, { recursive: true });
for (const f of readdirSync(out)) if (/^sheet-\d+\.png$/.test(f) || f === 'index.txt') rmSync(join(out, f));
const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: 1280, height: 720 }, reducedMotion: 'reduce' });
const page = await ctx.newPage();
const errs = [];
page.on('pageerror', e => errs.push(e.message));
page.on('console', m => m.type() === 'error' && errs.push(m.text()));
await page.goto(pathToFileURL(resolve(src)).href);
await page.waitForFunction(() => window.__deckReady, null, { timeout: 60000 });
const list = await page.evaluate(() => Reveal.getSlides().map(s => { const i = Reveal.getIndices(s); return { h: i.h, v: i.v || 0, id: s.id || '', cls: s.className }; }));
const shots = [];
for (const s of list) {
  await page.evaluate(({ h, v }) => Reveal.slide(h, v, 99), s);
  await page.waitForTimeout(260);
  const act = await page.evaluate(() => {   // interativos: mostra o estado depois do clique
    const c = Reveal.getCurrentSlide();
    const t = c.querySelector('.opts button:nth-child(1), .blk[data-k="gate"], .gterm:nth-child(2)');
    if (t) { t.dispatchEvent(new MouseEvent('click', { bubbles: true })); return 1; }
    return 0;
  });
  if (act) await page.waitForTimeout(450);
  await page.mouse.move(640, 1);
  shots.push((await page.screenshot({ type: 'jpeg', quality: 72 })).toString('base64'));
}
const sheet = await ctx.newPage();
const idx = [];
for (let k = 0; k * N < list.length; k++) {
  const part = list.slice(k * N, (k + 1) * N), imgs = shots.slice(k * N, (k + 1) * N);
  const name = `sheet-${String(k + 1).padStart(2, '0')}.png`;
  idx.push(`${name}: ${part.map(s => `${s.h}/${s.v}${s.id ? ' ' + s.id : ''}`).join(', ')}`);
  await sheet.setViewportSize({ width: COLS * 480 + (COLS + 1) * 12, height: 800 });
  await sheet.setContent(`<body style="margin:0;background:#050607;display:grid;grid-template-columns:repeat(${COLS},480px);gap:12px;padding:12px;font:700 17px Menlo,monospace;color:#ffe2b8">${imgs.map((b, i) =>
    `<figure style="margin:0;position:relative"><img src="data:image/jpeg;base64,${b}" style="width:480px;height:270px;display:block;border:1px solid #28313b"><figcaption style="padding:4px 2px 0">${part[i].h}/${part[i].v}${part[i].id ? ' · ' + part[i].id : ''}</figcaption></figure>`).join('')}</body>`);
  await sheet.waitForTimeout(300);
  await sheet.screenshot({ path: join(out, name), fullPage: true });
}
writeFileSync(join(out, 'index.txt'), `${list.length} slides, ${N} por folha\n` + idx.join('\n') + '\n');
await browser.close();
console.log(`slides: ${list.length} | folhas: ${idx.length} | erros JS: ${errs.length}`);
if (errs.length) console.log(errs.slice(0, 5).join('\n'));
