#!/usr/bin/env node
// Uso: node montar.cjs <projeto> [--amostra]
// Um plano vira até três arquivos: slides de aula, PDF e autoestudo.
require('./browser-environment.cjs');
const fs = require('node:fs'), path = require('node:path');
const { createRequire } = require('node:module');
const { execFileSync } = require('node:child_process');
const { randomBytes } = require('node:crypto');
const { projeto } = require('./comum.cjs');

const A = path.join(__dirname, '../assets');
const asset = f => fs.readFileSync(path.join(A, f), 'utf8');
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
const emScript = v => JSON.stringify(v).replace(/</g, '\\u003c');
// só roda script com o número sorteado desta montagem: atributo on... e link javascript: ficam mortos
const csp = nonce => `<meta http-equiv="Content-Security-Policy" content="default-src 'self' file: data: blob:; style-src 'self' file: 'unsafe-inline'; script-src ${nonce ? `'nonce-${nonce}'` : "'none'"}; object-src 'none'; connect-src 'none'">`;

function preencher(html, p, destino) {
  const dados = { titulo: p.ebook.titulo, autor: p.ebook.autor, contato: p.ebook.contato || '' };
  const linhas = p.plano.capitulos.map((nome, i) => {
    const pos = p.plano.telas.findIndex(t => t.cap === i + 1), id = p.plano.telas[pos].id;
    return `<li><a href="${destino === 'pdf' ? '#' : '#/'}${id}"><span>${esc(nome)}</span><b>${pos + 1}</b></a></li>`;
  }).join('');
  return html.replace(/\{\{(titulo|autor|contato)\}\}/g, (_, k) => esc(dados[k]))
    .replace(/<nav data-sumario(?:="")?\s*>\s*<\/nav>/g, () => `<nav data-sumario><ol>${linhas}</ol></nav>`);
}

function deck(p, destino, modo) {
  const req = createRequire(path.join(p.R, '.ferramentas/package.json'));
  const reveal = path.resolve(path.dirname(req.resolve('reveal.js')), '..');
  const gsap = path.dirname(req.resolve('gsap'));
  fs.mkdirSync(destino, { recursive: true });
  const nonce = randomBytes(16).toString('hex');
  const script = t => `<script nonce="${nonce}">${t.replace(/<\/script/gi, '<\\/script')}</script>`;
  const G = ['gsap', 'SplitText', 'DrawSVGPlugin', 'MotionPathPlugin', 'CustomEase'];
  const libs = [path.join(reveal, 'dist/reveal.js'), ...G.map(f => path.join(gsap, `${f}.min.js`))].map(f => fs.readFileSync(f, 'utf8'));
  // a janela de notas herda a trava, então o script dela precisa do mesmo número
  if (modo === 'aula') libs.push(fs.readFileSync(path.join(reveal, 'plugin/notes/notes.js'), 'utf8').replace('<script>', () => `<script nonce='${nonce}'>`));
  if (fs.existsSync(path.join(p.C, 'fonts'))) fs.cpSync(path.join(p.C, 'fonts'), path.join(destino, 'fonts'), { recursive: true });

  const aberto = modo === 'autoestudo', audios = {};
  if (aberto) {
    fs.mkdirSync(path.join(destino, 'audio'));
    for (const t of p.telas) {
      const a = path.join(p.R, 'audio', `${t.id}.m4a`);
      // áudio mais velho que o roteiro não entra: narraria um texto que já mudou
      if (fs.existsSync(a) && fs.statSync(a).mtimeMs >= fs.statSync(path.join(p.C, 'roteiro', `${t.id}.txt`)).mtimeMs) {
        fs.copyFileSync(a, path.join(destino, 'audio', `${t.id}.m4a`));
        audios[t.id] = `audio/${t.id}.m4a`;
      }
    }
  }
  const secao = t => `<section id="${t.id}" class="tela tela-${t.tipo}" data-title="${esc(t.titulo)}">${preencher(t.html, p, 'tela')}${
    modo === 'aula' ? `<aside class="notes">${preencher(t.nota, p, 'tela')}</aside>` : ''}</section>`;
  let corpo = '', cap = 0;
  for (const t of p.telas) {
    // cada capítulo é uma pilha: seta direita muda de capítulo, seta para baixo anda dentro dele
    if (t.cap !== cap) {
      if (cap) corpo += '</section>';
      if (t.cap) corpo += '<section class="capitulo">';
      cap = t.cap;
    }
    corpo += secao(t);
  }
  if (cap) corpo += '</section>';

  const previa = modo === 'amostra' && p.quer('autoestudo') ? '<div id="eb-botoes" aria-hidden="true"><button type="button" tabindex="-1">i</button><button type="button" tabindex="-1">▶</button></div>' : '';
  const controles = !aberto ? previa : `<div id="eb-botoes"><button type="button" id="eb-i" aria-label="Explicação desta tela">i</button><button type="button" id="eb-play" aria-label="Ouvir explicação">▶</button></div>
<dialog id="eb-pop" aria-label="Explicação"><button type="button" class="eb-x" aria-label="Fechar">✕</button><div class="eb-texto"></div><div class="eb-def" aria-live="polite"></div></dialog><audio id="eb-audio" preload="none"></audio>
${p.telas.map(t => `<template id="eb-info-${t.id}">${preencher(t.info, p, 'tela')}</template>`).join('')}`;

  fs.writeFileSync(path.join(destino, 'index.html'), `<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">${csp(nonce)}
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover"><title>${esc(p.ebook.titulo)}</title>
<style>${fs.readFileSync(path.join(reveal, 'dist/reveal.css'), 'utf8')}</style>
<style>${asset('base.css')}${p.css}${aberto ? asset('celular/celular.css') : ''}</style></head>
<body><div class="reveal"><div class="slides">${corpo}</div></div><div id="eb-num"></div>${controles}
${libs.map(script).join('\n')}
${script(`window.EB_DADOS=${emScript({ modo, audios, glossario: aberto ? p.glossario : {} })};`)}
${script(asset('motor.js'))}
${p.telas.map(t => script(`(() => {${t.js}\n})();`)).join('\n')}
${aberto ? script(asset('celular/celular.js')) : ''}
${script('EBOOK.iniciar();')}</body></html>`);
}

function htmlPdf(p, base = '') {
  const paginas = p.telas.map(t => `<article id="${t.id}" class="pagina pagina-${t.tipo}">${preencher(t.pagina, p, 'pdf')}<span class="folio">${
    p.plano.telas.findIndex(x => x.id === t.id) + 1}</span></article>`).join('');
  return `<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">${base}${csp()}<title>${esc(p.ebook.titulo)}</title><style>${asset('pagina-base.css')}${p.cssPdf}</style></head><body>${paginas}</body></html>`;
}

async function pdf(p, saida, trabalho) {
  fs.mkdirSync(trabalho);
  if (fs.existsSync(path.join(p.C, 'fonts'))) fs.cpSync(path.join(p.C, 'fonts'), path.join(trabalho, 'fonts'), { recursive: true });
  const html = path.join(trabalho, 'index.html');
  fs.writeFileSync(html, htmlPdf(p));
  const { chromium } = createRequire(path.join(p.R, '.ferramentas/package.json'))('playwright');
  const b = await chromium.launch();
  try {
    const pg = await b.newPage();
    await pg.goto('file://' + encodeURI(html));
    await pg.evaluate(() => document.fonts.ready);
    await pg.pdf({ path: saida, preferCSSPageSize: true, printBackground: true, tagged: true, outline: true });
  } finally { await b.close(); }
}

async function montar(dir, amostra) {
  const p = projeto(dir, { amostra });
  if (p.erros.length) throw new Error('não montei:\n- ' + p.erros.join('\n- '));
  const obra = fs.mkdtempSync(path.join(p.R, '.montagem-')), novo = path.join(obra, 'saida');
  fs.mkdirSync(novo);
  try {
    if (amostra && p.animado) {
      deck(p, path.join(novo, 'telas'), 'amostra');
    } else if (!amostra) {
      if (p.quer('slides')) {
        deck(p, path.join(obra, 'aula'), 'aula');
        execFileSync('python3', ['-I', path.join(__dirname, 'inline_single.py'), path.join(obra, 'aula/index.html'), path.join(novo, 'slides-de-aula.html')]);
      }
      if (p.quer('autoestudo')) {
        deck(p, path.join(novo, 'autoestudo'), 'autoestudo');
        fs.writeFileSync(path.join(novo, 'autoestudo/COMO-ABRIR.txt'),
          'Descompacte a pasta inteira e abra index.html no navegador.\nSeta para a direita: próximo capítulo. Seta para baixo: dentro do capítulo. Espaço: próxima tela.\ni: explicação. ▶: áudio. R: refazer a tela.\n');
        execFileSync('zip', ['-qr', 'autoestudo.zip', 'autoestudo'], { cwd: novo });
      }
    }
    if (p.quer('pdf')) await pdf(p, path.join(novo, amostra ? 'paginas.pdf' : 'ebook.pdf'), path.join(obra, 'pdf'));

    const alvo = path.join(p.R, amostra ? 'amostra' : 'entregas');
    if (fs.existsSync(alvo)) {
      fs.mkdirSync(path.join(p.R, 'backups'), { recursive: true });
      fs.renameSync(alvo, path.join(p.R, 'backups', `${path.basename(alvo)}-${Date.now()}`)); // nunca apaga a entrega anterior
    }
    fs.renameSync(novo, alvo);
    return alvo;
  } finally { fs.rmSync(obra, { recursive: true, force: true }); } // só a pasta temporária criada acima
}

module.exports = { montar, htmlPdf };
if (require.main === module) {
  if (!process.argv[2]) { console.error('uso: montar.cjs <projeto> [--amostra]'); process.exit(1); }
  montar(process.argv[2], process.argv.includes('--amostra'))
    .then(d => console.log('montado:', d), e => { console.error(e.message); process.exit(1); });
}
