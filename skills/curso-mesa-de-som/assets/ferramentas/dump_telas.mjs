// Imagem do estado final de cada tela, para quem escreve narração. Uso: node dump_telas.mjs <pasta-curso> <pasta-saida>
import { createRequire } from 'node:module'; import path from 'node:path'; import fs from 'node:fs';
const C = path.resolve(process.argv[2]), O = path.resolve(process.argv[3]), R = createRequire(C + '/tools/package.json'); R(C + '/tools/browser-environment.cjs'); const { chromium } = R('playwright');
fs.mkdirSync(O, { recursive: true });
const b = await chromium.launch({ args: ['--mute-audio'] }), p = await b.newPage({ viewport: { width: 960, height: 540 }, reducedMotion: 'reduce' });
// A fase 4a tira as imagens antes do build da V2: as telas são as da V1 congelada.
const V2 = C + '/08-slides-v2/index.html';
await p.goto('file://' + (fs.existsSync(V2) ? V2 : C + '/entregas/v1-aulas/deck/index.html')); await p.waitForFunction(() => window.Reveal?.isReady());
const ids = await p.evaluate(() => Reveal.getSlides().map(s => s.id));
for (const id of ids) { await p.evaluate(id => { const i = Reveal.getIndices(document.getElementById(id)); Reveal.slide(i.h, i.v, 999); }, id); await p.waitForTimeout(250); await p.screenshot({ path: `${O}/${id}.png` }); }
await b.close(); console.log(path.basename(C), ids.length, 'telas');
