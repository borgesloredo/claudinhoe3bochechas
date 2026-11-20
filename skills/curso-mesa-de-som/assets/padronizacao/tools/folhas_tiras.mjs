import './browser-environment.cjs';
// Junta as tiras de motion (4 quadros por slide) em folhas de 6, na ordem do deck. Uso: node tools/folhas_tiras.mjs <curso>
// Lê ws/<c>/material/tiras/*.png e ws/<c>/c/tools/v2/slides.json; grava ws/<c>/material/tiras-folhas/. Não altera o curso.
import { chromium } from 'playwright';
import fs from 'node:fs'; import path from 'node:path';
const c = process.argv[2], W = path.resolve('ws', c), T = path.join(W, 'material/tiras'), OUT = path.join(W, 'material/tiras-folhas');
fs.mkdirSync(OUT, { recursive: true });
const ordem = JSON.parse(fs.readFileSync(path.join(W, 'c/tools/v2/slides.json'), 'utf8')).map(s => s.id).filter(id => fs.existsSync(path.join(T, id + '.png')));
const sobra = fs.readdirSync(T).filter(f => f.endsWith('.png')).map(f => f.slice(0, -4)).filter(id => !ordem.includes(id));
const ids = [...ordem, ...sobra];
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1970, height: 6 * 312 } });
const lista = [];
for (let k = 0; k < ids.length; k += 6) {
  const g = ids.slice(k, k + 6), n = String(k / 6 + 1).padStart(2, '0');
  await p.setContent(`<body style="margin:0;background:#000">${g.map(id => `<img src="data:image/png;base64,${fs.readFileSync(path.join(T, id + '.png')).toString('base64')}" style="display:block;width:1970px;height:312px">`).join('')}</body>`);
  const f = path.join(OUT, `${c}-${n}.jpg`); await p.screenshot({ path: f, type: 'jpeg', quality: 82, fullPage: true }); lista.push(`${path.basename(f)}: ${g.join(' ')}`);
}
fs.writeFileSync(path.join(OUT, `${c}-indice.txt`), lista.join('\n') + '\n');
await b.close(); console.log(c, ids.length, 'tiras,', lista.length, 'folhas');
