// Leitura e validação do projeto, usadas por montar e conferir.
const fs = require('node:fs'), path = require('node:path');

const TIPOS = ['capa', 'sumario', 'abertura', 'topico', 'quiz', 'glossario', 'aviso', 'encerramento'];
const ARQUIVOS = ['slides', 'pdf', 'autoestudo'];
const CANAIS = ['documentacao', 'livros', 'cursos', 'ebooks', 'blogs', 'youtube', 'instagram', 'tiktok', 'kwai'];

const ler = f => (fs.existsSync(f) ? fs.readFileSync(f, 'utf8') : null);
const json = f => {
  const t = ler(f);
  if (t === null) return null;
  try { return JSON.parse(t); } catch (e) { throw new Error(`JSON inválido em ${f}: ${e.message}`); }
};
const palavras = t => t.replace(/<[^>]+>/g, ' ').trim().split(/\s+/).filter(Boolean).length;

function validarBase(e, p) {
  const erros = [];
  if (!e) return ['falta ebook.json'];
  for (const k of ['titulo', 'nicho', 'tema', 'autor']) if (!String(e[k] || '').trim()) erros.push(`ebook.json: falta ${k}`);
  if (!Number.isInteger(e.paginas) || e.paginas < 8 || e.paginas > 150) erros.push('ebook.json: paginas deve ser inteiro de 8 a 150');
  if (!Array.isArray(e.arquivos) || !e.arquivos.length || e.arquivos.some(a => !ARQUIVOS.includes(a)))
    erros.push(`ebook.json: arquivos deve ter um ou mais de ${ARQUIVOS.join(', ')}`);
  if (!p || !Array.isArray(p.capitulos) || !Array.isArray(p.telas)) return [...erros, 'plano.json: faltam capitulos ou telas'];
  if (p.telas.length !== e.paginas) erros.push(`plano.json: ${p.telas.length} telas, o pedido foi ${e.paginas}`);
  const vistos = new Set();
  let cap = 0, fim = false;
  p.telas.forEach((t, i) => {
    if (!/^[a-z0-9][a-z0-9-]{0,40}$/.test(t.id || '')) erros.push(`plano.json: id inválido na posição ${i + 1}`);
    if (vistos.has(t.id)) erros.push(`plano.json: id repetido ${t.id}`);
    vistos.add(t.id);
    if (!TIPOS.includes(t.tipo)) erros.push(`${t.id}: tipo inválido`);
    if (!Number.isInteger(t.cap) || t.cap < 0 || t.cap > p.capitulos.length) erros.push(`${t.id}: cap inválido`);
    else if (t.cap === 0) { if (cap) fim = true; }
    else {
      if (fim || t.cap < cap || t.cap > cap + 1) erros.push(`${t.id}: capítulos fora de ordem`);
      cap = t.cap;
    }
  });
  if (cap !== p.capitulos.length) erros.push('plano.json: há capítulo sem tela');
  if (p.telas[0]?.tipo !== 'capa' || p.telas[1]?.tipo !== 'sumario' || p.telas.at(-1)?.tipo !== 'encerramento')
    erros.push('plano.json: comece com capa e sumario, termine com encerramento');
  if (p.telas.some(t => ['capa', 'sumario', 'encerramento'].includes(t.tipo) && t.cap !== 0)) erros.push('plano.json: capa, sumario e encerramento usam cap 0');
  return erros;
}

// O conteúdo nasce de pesquisa na internet: trate como não confiável antes de virar HTML executável.
function perigoHtml(bruto) {
  // decodifica entidades antes de procurar: "&#106;avascript:" é javascript:
  const t = bruto.replace(/&#(x[0-9a-f]+|\d+);?/gi, (_, n) => {
    const c = /^x/i.test(n) ? parseInt(n.slice(1), 16) : Number(n);
    return c > 31 && c < 0x10ffff && c !== 60 && c !== 62 ? String.fromCodePoint(c) : ' ';
  }).replace(/&(colon|tab|newline);/gi, (_, n) => (n.toLowerCase() === 'colon' ? ':' : ''));
  if (/<\s*(script|iframe|object|embed|link|meta|base|form|foreignobject|set|animate|animatemotion|animatetransform|style)\b/i.test(t)) return 'elemento proibido';
  if (/<[^>]*[\s"'/]on[a-z]+\s*=/i.test(t)) return 'atributo de evento (on...=)';
  if (/(src|href|action|data)\s*=\s*["']?\s*(https?:|\/\/|javascript:|file:|\.\.\/|\/)/i.test(t)) return 'recurso externo ou fora da pasta';
  if (/\ssrcset\s*=|javascript\s*:/i.test(t)) return 'srcset ou javascript: proibido';
  if (/url\(\s*["']?\s*(https?:|\/\/|\.\.\/|\/)/i.test(t)) return 'url() externa ou fora da pasta';
  return null;
}
const perigoJs = t =>
  /\b(fetch|XMLHttpRequest|WebSocket|EventSource|sendBeacon|eval|importScripts|localStorage)\b|\bFunction\s*\(|document\.cookie|\bimport\s*\(|<\/script|["'`](https?:)?\/\/(?!www\.w3\.org)/.test(t)
    ? 'código com rede, eval ou acesso proibido' : null;
const perigoCss = t =>
  /@import|<\/style|url\(\s*["']?\s*(https?:|\/\/|\.\.\/|\/)/i.test(t) ? 'CSS com recurso externo' : null;

function projeto(dir, { amostra = false } = {}) {
  const R = path.resolve(dir), C = path.join(R, 'conteudo');
  const ebook = json(path.join(R, 'ebook.json')), plano = json(path.join(R, 'plano.json'));
  const erros = validarBase(ebook, plano);
  if (erros.length) return { erros };
  const telas = amostra ? plano.telas.filter(t => t.amostra) : plano.telas;
  if (amostra && (telas.length < 4 || telas.length > 6 || ['capa', 'abertura', 'topico', 'quiz'].some(x => !telas.some(t => t.tipo === x))))
    erros.push('a amostra precisa de 4 a 6 telas com "amostra": true, incluindo capa, abertura, topico e quiz');
  const quer = a => ebook.arquivos.includes(a);
  const animado = quer('slides') || quer('autoestudo');

  function usar(rel, checar) {
    const t = ler(path.join(C, rel));
    if (!t?.trim()) { erros.push(`falta conteudo/${rel}`); return ''; }
    const p = checar?.(t);
    if (p) erros.push(`conteudo/${rel}: ${p}`);
    return t;
  }
  const itens = telas.map(t => {
    const d = { ...t };
    if (quer('pdf')) {
      d.pagina = usar(`paginas/${t.id}.html`, perigoHtml);
      if (/<h[3-6][\s>]/i.test(d.pagina)) erros.push(`conteudo/paginas/${t.id}.html: use p com classe no lugar de h3 a h6 (viram marcadores do PDF)`);
    }
    if (animado) { d.html = usar(`telas/${t.id}.html`, perigoHtml); d.js = usar(`telas/${t.id}.js`, perigoJs); }
    if (amostra) return d;
    if (quer('slides')) d.nota = usar(`notas/${t.id}.html`, perigoHtml);
    if (quer('autoestudo')) { d.info = usar(`info/${t.id}.html`, perigoHtml); d.roteiro = usar(`roteiro/${t.id}.txt`); }
    return d;
  });
  const css = animado ? usar('tema.css', perigoCss) : '';
  const cssPdf = quer('pdf') ? usar('pagina.css', perigoCss) : '';
  for (const [, u] of (css + cssPdf).matchAll(/url\(\s*["']?([^"')]+)/g))
    if (!/^(data:|#)/.test(u) && !fs.existsSync(path.join(C, u))) erros.push(`CSS aponta para arquivo que não existe: ${u}`);
  let glossario = {};
  if (quer('autoestudo') && !amostra) {
    glossario = json(path.join(C, 'glossario.json')) || {};
    if (!Object.keys(glossario).length) erros.push('falta conteudo/glossario.json');
  }
  return { R, C, ebook, plano, telas: itens, css, cssPdf, glossario, animado, quer, amostra, erros };
}

function validarFontes(R, telas = []) {
  const f = json(path.join(R, 'pesquisa/fontes.json'));
  if (!f) return ['falta pesquisa/fontes.json'];
  const erros = [], fontes = f.fontes || [];
  for (const c of CANAIS) if (!f.cobertura?.[c]) erros.push(`fontes.json: canal sem registro de busca: ${c}`);
  for (const x of fontes) {
    if (!/^https?:\/\//.test(x.url || '')) erros.push(`fontes.json: URL inválida em ${x.id}`);
    if (/wikipedia\.org|wikiwand\.com/i.test(x.url || '')) erros.push(`fontes.json: Wikipédia não é aceita (${x.id})`);
    if (!['pagina', 'resumo', 'transcricao', 'so-resultado-de-busca'].includes(x.lido)) erros.push(`fontes.json: diga o que foi lido em ${x.id}`);
  }
  const lidas = fontes.filter(x => x.papel === 'tecnica' && x.lido !== 'so-resultado-de-busca');
  if (lidas.length < 3) erros.push('fontes.json: são necessárias 3 fontes técnicas realmente lidas');
  const ids = new Set(fontes.map(x => x.id));
  for (const t of telas) for (const id of t.fontes || []) if (!ids.has(id)) erros.push(`${t.id}: fonte ${id} não existe em fontes.json`);
  return erros;
}

module.exports = { projeto, validarBase, validarFontes, perigoHtml, perigoJs, perigoCss, palavras };
