#!/usr/bin/env node
// Uso: node conferir.cjs <projeto> [--amostra]. Só aprova com "CONFERIR OK".
require('./browser-environment.cjs');
const fs = require('node:fs'), path = require('node:path');
const { createRequire } = require('node:module');
const { execFileSync } = require('node:child_process');
const { projeto, validarFontes, palavras } = require('./comum.cjs');
const medir = require('./medir.cjs');

const url = f => 'file://' + encodeURI(f);

async function conferir(dir, amostra) {
  const p = projeto(dir, { amostra }), erros = [...p.erros];
  if (!p.R || erros.length) return erros;
  if (!amostra) erros.push(...validarFontes(p.R, p.telas));
  const saida = path.join(p.R, amostra ? 'amostra' : 'entregas');
  const pecas = [];
  if (amostra) {
    if (p.animado) pecas.push(['telas/index.html', 'amostra']);
    if (p.quer('pdf')) pecas.push(['paginas.pdf', 'pdf']);
  } else {
    if (p.quer('slides')) pecas.push(['slides-de-aula.html', 'aula']);
    if (p.quer('autoestudo')) pecas.push(['autoestudo/index.html', 'autoestudo'], ['autoestudo.zip', 'zip']);
    if (p.quer('pdf')) pecas.push(['ebook.pdf', 'pdf']);
  }
  for (const [f] of pecas) if (!fs.existsSync(path.join(saida, f))) erros.push(`falta ${f}: rode montar.cjs`);
  if (erros.length) return erros;

  const montadoEm = fs.statSync(path.join(saida, pecas[0][0])).mtimeMs;
  const fontes = fs.readdirSync(p.C, { recursive: true }).map(f => path.join(p.C, f)).filter(f => fs.statSync(f).isFile());
  for (const f of [...fontes, path.join(p.R, 'plano.json'), path.join(p.R, 'ebook.json')])
    if (fs.statSync(f).mtimeMs > montadoEm) erros.push(`mudou depois da montagem, monte de novo: ${path.relative(p.R, f)}`);

  if (!amostra) for (const t of p.telas) {
    if (t.tipo === 'topico' && !t.fontes?.length) erros.push(`${t.id}: tópico sem fonte no plano`);
    if (!p.quer('autoestudo')) continue;
    const [minI, minR] = t.tipo === 'topico' ? [170, 280] : [45, 70];
    const nI = palavras(t.info), nR = palavras(t.roteiro);
    if (nI < minI) erros.push(`${t.id}: explicação com ${nI} palavras, mínimo ${minI}`);
    if (nR < minR) erros.push(`${t.id}: roteiro com ${nR} palavras, mínimo ${minR}`);
    for (const m of t.info.matchAll(/data-t="([^"]+)"/g)) if (!p.glossario[m[1]]) erros.push(`${t.id}: termo fora do glossário: ${m[1]}`);
    const a = path.join(p.R, 'audio', `${t.id}.m4a`);
    if (!fs.existsSync(a)) erros.push(`${t.id}: sem áudio`);
    else if (fs.statSync(a).mtimeMs < fs.statSync(path.join(p.C, 'roteiro', `${t.id}.txt`)).mtimeMs) erros.push(`${t.id}: áudio mais velho que o roteiro`);
    else if (!fs.existsSync(path.join(saida, 'autoestudo/audio', `${t.id}.m4a`))) erros.push(`${t.id}: áudio fora da entrega, monte de novo`);
  }

  const qa = path.join(p.R, 'qa', amostra ? 'amostra' : 'final');
  fs.mkdirSync(qa, { recursive: true });
  const { chromium, webkit } = createRequire(path.join(p.R, '.ferramentas/package.json'))('playwright');
  const b = await chromium.launch({ args: ['--mute-audio'] });
  const fotos = [];
  try {
    if (p.quer('pdf')) {
      const arq = path.join(saida, amostra ? 'paginas.pdf' : 'ebook.pdf'), bytes = fs.readFileSync(arq).toString('latin1');
      const n = (bytes.match(/\/Type\s*\/Page\b/g) || []).length;
      if (n !== p.telas.length) erros.push(`PDF com ${n} páginas, esperado ${p.telas.length}`);
      if (/\/Subtype\s*\/Type3\b/.test(bytes)) erros.push('PDF com fonte Type 3 (borra em alguns leitores): use fonte estática, não variável nem system-ui');
      // confere o mesmo HTML que virou o PDF, lendo as fontes de dentro de conteudo/
      const { htmlPdf } = require('./montar.cjs'), html = path.join(qa, 'pdf.html');
      fs.writeFileSync(html, htmlPdf(p, `<base href="${url(p.C)}/">`));
      const pg = await b.newPage({ viewport: { width: 794, height: 1123 }, offline: true });
      await pg.emulateMedia({ media: 'print' });
      await pg.goto(url(html));
      await pg.evaluate(() => document.fonts.ready);
      for (const f of await pg.evaluate(() => [...document.fonts].filter(x => x.status === 'error').map(x => x.family))) erros.push(`PDF: fonte não carregou: ${f}`);
      for (const t of p.telas) {
        await pg.evaluate(id => document.getElementById(id).scrollIntoView(), t.id);
        const achados = await pg.evaluate(medir, { id: t.id, corpo: 14, rotulo: 11, livres: [{ nome: 'o rodapé', x0: 0, x1: 794, y0: 1078, y1: 1123 }] });
        achados.forEach(d => erros.push(`PDF/${t.id}: ${d}`));
        const png = await pg.locator(`[id="${t.id}"]`).screenshot();
        fs.writeFileSync(path.join(qa, `pdf-${t.id}.png`), png);
        fotos.push([`PDF ${t.id}`, png]);
      }
      await pg.close();
    }

    for (const [arq, modo] of pecas.filter(x => x[0].endsWith('.html'))) {
      const alvo = path.join(saida, arq);
      const ctx = await b.newContext({ viewport: { width: 1280, height: 720 }, offline: true });
      const pg = await ctx.newPage();
      pg.on('pageerror', e => erros.push(`${modo}: erro de JavaScript: ${e.message}`));
      pg.on('request', r => { if (/^https?:/.test(r.url())) erros.push(`${modo}: pedido externo ${r.url()}`); });
      await pg.goto(url(alvo));
      await pg.waitForFunction(() => window.Reveal?.isReady() && document.getElementById('eb-num').textContent, null, { timeout: 15000 });
      const total = await pg.evaluate(() => Reveal.getTotalSlides());
      if (total !== p.telas.length) erros.push(`${modo}: ${total} telas, esperado ${p.telas.length}`);
      // sem camada 3D: ela muda o serrilhado da letra e passa por movimento na comparação de fotos
      await pg.evaluate(() => gsap.config({ force3D: false }));
      const limpo = await pg.evaluateHandle(() => {
        const s = document.createElement('style');
        // opacity, não visibility: as setas do Reveal religam o visibility nos filhos e pulsam
        s.textContent = '.reveal .controls,.reveal .progress,#eb-num,#eb-botoes,#cel-ind-b{opacity:0!important;animation:none!important} *{transition:none!important;caret-color:transparent!important}';
        return s;
      });
      const LIVRES = [{ nome: 'os botões', x0: 1160, x1: 1280, y0: 0, y1: 68 }, { nome: 'o contador', x0: 0, x1: 90, y0: 692, y1: 720 }, { nome: 'as setas', x0: 1190, x1: 1280, y0: 630, y1: 720 }];
      const examinar = async (t, caso) => (await pg.evaluate(medir, { id: t.id, corpo: 28, rotulo: 18, livres: LIVRES })).forEach(d => erros.push(`${modo}/${t.id}${caso}: ${d}`));
      for (const t of p.telas) {
        await limpo.evaluate(s => document.head.append(s));
        const q = x => pg.evaluate(([i, y]) => EBOOK.quadro(i, y), [t.id, x]);
        await q(1); // deixa todo alvo com transform escrito antes da primeira foto
        const info = await q(0.08);
        const antes = await pg.screenshot();
        await q(0.5);
        const meio = await pg.screenshot();
        await q(1);
        const depois = await pg.screenshot();
        const anim = d => erros.push(`${modo}/${t.id}: ${d}`);
        if (info.passos < 3 || (antes.equals(depois) && meio.equals(depois))) anim('sem animação de verdade (3+ passos e mudança visível)');
        if (info.semAlvo) anim(`${info.semAlvo} passo(s) de animação sem alvo: seletor não existe`);
        if (info.passos && info.soOpacidade) anim('só fade: anime também forma, posição ou traço');
        if (info.passos && (info.duracao < 1.8 || info.duracao > 6)) anim(`animação com ${info.duracao.toFixed(1)} s, fora de 2 a 6 s`);
        await examinar(t, '');
        fs.writeFileSync(path.join(qa, `${modo}-${t.id}.png`), depois);
        fotos.push([`${modo} ${t.id}`, depois]);

        if (t.tipo === 'quiz') {
          const clicar = certa => pg.evaluate(([id, c]) => {
            const s = document.getElementById(id), ve = x => x && getComputedStyle(x).visibility === 'visible';
            const b = s.querySelector(`[data-quiz] button${c ? '[data-certa]' : ':not([data-certa])'}`);
            const sim = s.querySelector('[data-retorno="certa"]'), nao = s.querySelector('[data-retorno="errada"]');
            if (!b || !sim || !nao) return 'estrutura incompleta';
            if (!s.querySelector('[data-resposta]') && (ve(sim) || ve(nao))) return 'resposta aparece antes do clique';
            b.click();
            return ve(c ? sim : nao) && !ve(c ? nao : sim) ? null : `retorno ${c ? 'certo' : 'errado'} não funciona`;
          }, [t.id, certa]);
          for (const certa of [false, true]) {
            const r = await clicar(certa);
            if (r) { anim(`quiz: ${r}`); break; }
            await examinar(t, certa ? ' (resposta certa)' : ' (resposta errada)');
            const png = await pg.screenshot();
            fs.writeFileSync(path.join(qa, `${modo}-${t.id}-${certa ? 'certa' : 'errada'}.png`), png);
            fotos.push([`${modo} ${t.id} ${certa ? 'certa' : 'errada'}`, png]);
          }
        }
        await limpo.evaluate(s => s.remove());
        if (modo === 'autoestudo') {
          await pg.click('#eb-i');
          const cheio = await pg.evaluate(() => document.getElementById('eb-pop').open && document.querySelector('#eb-pop .eb-texto').textContent.trim() !== '');
          if (!cheio) erros.push(`${t.id}: botão (i) não abre`);
          await pg.keyboard.press('Escape');
          const toca = await pg.evaluate(() => new Promise(ok => {
            const a = document.getElementById('eb-audio');
            if (!a.getAttribute('src')) return ok(false);
            a.muted = true;
            const prazo = setTimeout(() => ok(false), 6000);
            a.ontimeupdate = () => { if (a.currentTime > 0) { clearTimeout(prazo); a.ontimeupdate = null; a.pause(); ok(true); } };
            a.play().catch(() => { clearTimeout(prazo); ok(false); });
          }));
          if (!toca) erros.push(`${t.id}: áudio não toca`);
        }
      }
      for (const f of await pg.evaluate(() => [...document.fonts].filter(x => x.status === 'error').map(x => x.family))) erros.push(`${modo}: fonte não carregou: ${f}`);
      await ctx.close();

      const w = await webkit.launch();
      try {
        const sp = await (await w.newContext({ viewport: { width: 1280, height: 720 } })).newPage();
        sp.on('pageerror', e => erros.push(`Safari/${modo}: ${e.message}`));
        await sp.goto(url(alvo));
        await sp.waitForFunction(() => window.Reveal?.isReady() && document.getElementById('eb-num').textContent, null, { timeout: 15000 });
        for (const t of p.telas) await sp.evaluate(id => EBOOK.quadro(id, 1), t.id);
      } catch (e) { erros.push(`Safari/${modo}: ${e.message.split('\n')[0]}`); } finally { await w.close(); }
    }

    if (pecas.some(x => x[1] === 'zip')) execFileSync('unzip', ['-tqq', path.join(saida, 'autoestudo.zip')]);
    // folhas de contato: o revisor olha grades, sem abrir imagem por imagem
    const pg = await b.newPage({ viewport: { width: 1584, height: 900 } });
    for (let i = 0; i < fotos.length; i += 12) {
      await pg.setContent(`<body style="margin:8px;background:#777;display:grid;grid-template-columns:repeat(3,1fr);gap:8px;font:14px system-ui">${fotos.slice(i, i + 12).map(([n, png]) =>
        `<figure style="margin:0"><img style="width:100%;display:block" src="data:image/png;base64,${png.toString('base64')}"><figcaption>${n}</figcaption></figure>`).join('')}</body>`);
      await pg.screenshot({ path: path.join(qa, `contato-${i / 12 + 1}.png`), fullPage: true });
    }
  } finally { await b.close(); }
  return [...new Set(erros)];
}

module.exports = { conferir };
if (require.main === module) {
  if (!process.argv[2]) { console.error('uso: conferir.cjs <projeto> [--amostra]'); process.exit(1); }
  conferir(process.argv[2], process.argv.includes('--amostra')).then(e => {
    console.log(e.length ? `CONFERIR FALHOU (${e.length})\n- ${e.join('\n- ')}` : 'CONFERIR OK');
    process.exit(e.length ? 1 : 0);
  }).catch(e => { console.error('CONFERIR FALHOU:', e.message); process.exit(1); });
}
