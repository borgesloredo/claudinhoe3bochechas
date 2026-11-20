import './browser-environment.cjs';
// Material da validação independente de UM curso (mesmo conteúdo da 2ª rodada de 05/11), lido da V2 final.
// Uso: node tools/material.mjs <curso>   (lê ws/<curso>/antes/v2/08-slides-v2/index-depois.html e ws/<curso>/c/tools/v2/script)
// Gera em ws/<curso>/material/: quiz.json (alternativas, certa 0-based, texto visível antes do toque, termos clicáveis,
// (i) e roteiro), folhas/<curso>-N.jpg (quizzes antes do toque, 3×3), fotos/<id>.jpg (antes) e fotos/<id>-depois.jpg (após tocar a certa).
// Não altera o curso.
import { chromium } from 'playwright';
import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
const c = process.argv[2], W = path.resolve('ws', c), OUT = path.join(W, process.env.OUT ?? 'material');   // OUT=material-r2 na conferência depois das correções
const V2 = path.join(W, process.env.V2 ?? 'depois/v2/08-slides-v2/index.html');   // V2 final (já com as correções, se houver)
for (const d of ['folhas', 'fotos']) fs.mkdirSync(path.join(OUT, d), { recursive: true });
const OPTS = '.opts > button, .opts > .opt, .opts > .alt, button.ans, .alt, .opt, .qkeys > .qk, button.qk';   // .qk = quiz do mackie-analogicas (sessão P, 18/11/2026)
const b = await chromium.launch({ args: ['--mute-audio'] });
const p = await b.newPage({ viewport: { width: 1280, height: 720 }, reducedMotion: 'reduce' });
const errs = []; p.on('pageerror', e => errs.push(e.message));
const abrir = async () => { await p.goto(pathToFileURL(V2).href); await p.waitForFunction(() => window.Reveal?.isReady()); await p.waitForTimeout(500); };
await abrir();
const ids = await p.evaluate(() => Reveal.getSlides().filter(s => /^quiz-\d+$/.test(s.id)).map(s => s.id));
const go = id => p.evaluate(id => { const i = Reveal.getIndices(document.getElementById(id)); Reveal.slide(i.h, i.v, 99); }, id);
const out = [], shots = [];
for (const id of ids) {
  await go(id); await p.waitForTimeout(1200);
  const pre = await p.evaluate(([id, OPTS]) => {
    const s = document.getElementById(id);
    const opts = [...new Set(s.querySelectorAll(OPTS))].filter(e => !e.closest('svg'));
    const shown = e => { for (let a = e; a && a !== s.parentElement; a = a.parentElement) { const c = getComputedStyle(a); if (c.display === 'none' || c.visibility === 'hidden' || +c.opacity < .05) return false; } const r = e.getBoundingClientRect(); return r.width > 0 && r.height > 0; };
    const skip = e => opts.some(o => o.contains(e)) || e.closest('aside.notes, .fb:not(svg *), .fbw, .fbz, script, style, template, .feedback');
    const txt = [], w = document.createTreeWalker(s, NodeFilter.SHOW_TEXT);
    for (let n; (n = w.nextNode());) { const t = n.textContent.replace(/\s+/g, ' ').trim(); if (t && !skip(n.parentElement) && shown(n.parentElement)) txt.push(t); }
    const tpl = document.getElementById('v2i-' + id);
    const info = tpl ? tpl.content.textContent.replace(/\s+/g, ' ').trim() : null;
    const gl = tpl ? [...tpl.content.querySelectorAll('.gl')].map(e => `${e.textContent.trim()} [${e.dataset.t}]`) : [];
    const aria = [...s.querySelectorAll('[aria-label]')].map(e => e.getAttribute('aria-label'));
    return { opts: opts.map(o => o.textContent.replace(/\s+/g, ' ').trim()), visivel: txt.join(' | '), info, glossario_info: gl, aria };
  }, [id, OPTS]);
  shots.push({ id, b64: (await p.screenshot({ type: 'jpeg', quality: 80 })).toString('base64') });
  await p.screenshot({ path: path.join(OUT, 'fotos', `${id}.jpg`), type: 'jpeg', quality: 85 });
  const certa = await p.evaluate(async ([id, OPTS]) => {
    const s = document.getElementById(id);
    const opts = [...new Set(s.querySelectorAll(OPTS))].filter(e => !e.closest('svg'));
    opts[0]?.click(); await new Promise(r => setTimeout(r, 900));
    const k = opts.findIndex(o => /\b(ok|right|correct|is-ok|certa|good|acerto)\b/.test(o.className) || o.dataset.ok === '1' || o.dataset.ok === 'true');
    return k;
  }, [id, OPTS]);
  let roteiro = null; try { roteiro = fs.readFileSync(path.join(W, 'c/tools/v2/script', `${id}.txt`), 'utf8').replace(/\s+/g, ' ').trim(); } catch {}
  out.push({ id, ...pre, certa, roteiro });
}
// depois: recarrega (zera os quizzes) e toca a certa de cada um
await abrir();
for (const q of out) {
  if (q.certa < 0) continue;
  await go(q.id); await p.waitForTimeout(1200);
  await p.evaluate(([id, k, OPTS]) => [...new Set(document.getElementById(id).querySelectorAll(OPTS))].filter(e => !e.closest('svg'))[k].click(), [q.id, q.certa, OPTS]);
  await p.waitForTimeout(4000);
  await p.screenshot({ path: path.join(OUT, 'fotos', `${q.id}-depois.jpg`), type: 'jpeg', quality: 85 });
}
for (let k = 0; k < shots.length; k += 9) {
  const g = shots.slice(k, k + 9);
  await p.setViewportSize({ width: 1920, height: 1110 });
  await p.setContent(`<body style="margin:0;background:#000;display:grid;grid-template-columns:repeat(3,640px);gap:0;font:bold 18px sans-serif">${g.map(s =>
    `<div style="position:relative"><img src="data:image/jpeg;base64,${s.b64}" style="width:640px;height:360px;display:block"><span style="position:absolute;left:4px;top:4px;background:#ff0;color:#000;padding:1px 5px">${s.id}</span></div>`).join('')}</body>`);
  await p.screenshot({ path: path.join(OUT, 'folhas', `${c}-${k / 9 + 1}.jpg`), type: 'jpeg', quality: 85 });
}
await b.close();
fs.writeFileSync(path.join(OUT, 'quiz.json'), JSON.stringify(out, null, 1));
console.log(c, ids.length, 'quizzes; sem gabarito:', out.filter(q => q.certa < 0).map(q => q.id).join(' ') || 'nenhum', '| sem (i):', out.filter(q => !q.info).map(q => q.id).join(' ') || 'nenhum', '| erros JS:', errs.length);
