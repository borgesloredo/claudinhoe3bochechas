#!/usr/bin/env node
// Autoteste. node testar.cjs                        -> regras e fluxo, sem rede nem navegador
//            node testar.cjs <pasta node_modules>   -> também monta e confere de ponta a ponta (navegador e ffmpeg)
const assert = require('node:assert'), fs = require('node:fs'), os = require('node:os'), path = require('node:path');
const { execFileSync, spawnSync } = require('node:child_process');
const S = path.join(__dirname, '..'), K = path.join(S, '..');
const { validarBase, perigoHtml, perigoJs, perigoCss, validarFontes } = require(path.join(S, 'comum.cjs'));

const ARQ = ['slides', 'pdf', 'autoestudo'];
const COMBOS = [1, 2, 3, 4, 5, 6, 7].map(n => ARQ.filter((_, i) => n & (1 << i)));
const ebook = (arquivos, paginas = 8) => ({ titulo: 'Pele <limpa> & "segura"', nicho: 'estética', tema: 'limpeza de pele', autor: 'Ana Teste', contato: 'ana.example', paginas, arquivos, sensivel: true });
function plano(n) {
  const t = [{ id: 'capa', cap: 0, tipo: 'capa', amostra: true }, { id: 'sumario', cap: 0, tipo: 'sumario' }, { id: 'abre', cap: 1, tipo: 'abertura', amostra: true }];
  for (let i = 0; i < n - 5; i++) t.push({ id: `topico-${i}`, cap: i < (n - 5) / 2 ? 1 : 2, tipo: 'topico', fontes: ['f1'], amostra: i === 0 });
  t.push({ id: 'quiz', cap: 2, tipo: 'quiz', amostra: true }, { id: 'fim', cap: 0, tipo: 'encerramento' });
  return { capitulos: ['Preparar', 'Limpar'], telas: t.map(x => ({ ...x, titulo: `Tela ${x.id}`, conceito: 'teste' })) };
}

function regras() {
  for (const n of [8, 15, 20, 30, 50, 150]) assert.deepStrictEqual(validarBase(ebook(ARQ, n), plano(n)), [], `${n} páginas`);
  assert(validarBase(ebook(ARQ, 30), plano(29)).length, 'tamanho errado reprova');
  assert(validarBase(ebook([]), plano(8)).length, 'sem arquivo reprova');
  assert(validarBase({ ...ebook(ARQ), autor: '' }, plano(8)).length, 'sem autor reprova');
  for (const h of ['<script>x</script>', '<p onclick="x()">', '<svg/onload=x>', '<img src="https://x.y/a.png">', '<img src="../a.png">', '<a href="javascript:x">', '<a href="&#106;avascript:x">', '<svg><set attributeName="href" to="x"/></svg>', '<img srcset="https://x.y/a 1x">'])
    assert(perigoHtml(h), `deveria barrar ${h}`);
  assert.strictEqual(perigoHtml('<button data-certa>Sim</button><svg viewBox="0 0 9 9"><use href="#a"/></svg><a href="#/capa">x</a>'), null);
  assert(perigoJs('fetch("x")') && perigoJs('eval("1")') && !perigoJs('tl.from($(".a"),{opacity:0})'));
  assert(perigoCss('a{background:url(https://x.y/z)}') && !perigoCss('a{background:url("fonts/a.woff2")}'));

  const d = fs.mkdtempSync(path.join(os.tmpdir(), 'ebook-fontes-'));
  fs.mkdirSync(path.join(d, 'pesquisa'));
  gravarFontes(d, 'https://pt.wikipedia.org/wiki/Pele');
  assert(validarFontes(d).some(e => /Wikipédia/.test(e)), 'Wikipédia reprova');
  fs.rmSync(d, { recursive: true });

  execFileSync('python3', ['-I', '-c', `
import importlib.util, urllib.error
def mod(n):
    s = importlib.util.spec_from_file_location(n, r"""${S}/""" + n + ".py"); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
T = mod("temas")
ev = [dict(tipo=k, url=f"https://{k}.example/x", achado="a") for k in ("publico", "busca", "oferta")]
t = lambda **k: {**dict(titulo="T", dor="d", publico="p", promessa="r", evidencias=ev, notas=dict(dor=8, procura=8, lacuna=8, aplicacao=8)), **k}
e, o = T.avaliar([t()] * 5); assert not e and o[0]["nota"] == 8 and o[0]["trends"] == "não medido", e
assert any("procura acima" in x for x in T.avaliar([t(evidencias=[ev[0], ev[2]])] * 5)[0])
assert T.avaliar([t()] * 4)[0]
P = mod("publico")
v = P.resumir(dict(comments=[dict(text="chama @ana 31 99999-1234 ana@x.com", author="Ana"), dict(text="meu", author_is_uploader=True)]))
assert v["comentarios_lidos"] == 1 and "ana" not in str(v).lower() and "99999" not in str(v), v
n = []
def bloqueia(q, c):
    n.append(c); raise urllib.error.URLError("429")
r = mod("demanda").coletar(["pele"], bloqueia, 0)
assert len(n) == 2 and all(c["estado"].startswith("não medido") for c in r["canais"].values())
`], { env: { ...process.env, PYTHONDONTWRITEBYTECODE: '1' } });
}

function gravarFontes(d, url) {
  fs.writeFileSync(path.join(d, 'pesquisa/fontes.json'), JSON.stringify({
    cobertura: Object.fromEntries('documentacao livros cursos ebooks blogs youtube instagram tiktok kwai'.split(' ').map(c => [c, 'teste'])),
    fontes: [1, 2, 3].map(i => ({ id: `f${i}`, url: url || `https://fonte${i}.example/doc`, papel: 'tecnica', lido: 'pagina' })),
  }));
}

async function fluxo() {
  const corpo = fs.readFileSync(path.join(K, 'workflows/construir.js'), 'utf8').replace('export const meta', 'const meta');
  const Fn = Object.getPrototypeOf(async function () {}).constructor;
  const rodar = new Fn('args', 'agent', 'parallel', 'phase', 'log', corpo);
  for (const arquivos of COMBOS) for (const etapa of ['amostra', 'construir', 'fechar', 'ajustes']) for (const aprova of [true, false]) {
    const pedidos = [];
    const agent = async (p, o = {}) => {
      pedidos.push({ p, o });
      if (o.schema?.properties.ids) return { ids: plano(15).telas.map(t => t.id) };
      if (o.schema) return { approved: aprova, issues: aprova ? [] : ['x'] };
      return 'ok';
    };
    const r = await rodar({ R: '/tmp/x', K, etapa, ebook: ebook(arquivos, 15), itens: ['mais claro'] }, agent, fs => Promise.all(fs.map(f => f())), () => {}, () => {});
    const nome = `${arquivos}/${etapa}`, tudo = pedidos.map(x => x.p).join('\n');
    assert.strictEqual(r.approved, aprova, nome);
    assert(pedidos.every(x => x.o.model), `${nome}: agente sem modelo`);
    if (etapa !== 'construir') continue;
    assert.strictEqual(tudo.includes('info/<id>.html'), arquivos.includes('autoestudo'), nome);
    assert.strictEqual(tudo.includes('notas/<id>.html'), arquivos.includes('slides'), nome);
    assert.strictEqual(tudo.includes('paginas/<id>.html'), arquivos.includes('pdf'), nome);
    assert(pedidos.some(x => x.o.label.startsWith('segurança')), `${nome}: sem revisor de segurança`);
  }
}

function pontaAPonta(modulos) {
  const R = fs.mkdtempSync(path.join(os.tmpdir(), 'ebook teste ç-')), P = plano(8);
  const grava = (f, t) => { fs.mkdirSync(path.dirname(path.join(R, f)), { recursive: true }); fs.writeFileSync(path.join(R, f), t); };
  grava('.ferramentas/package.json', '{"private":true}');
  fs.symlinkSync(path.resolve(modulos), path.join(R, '.ferramentas/node_modules'));
  grava('plano.json', JSON.stringify(P));
  fs.mkdirSync(path.join(R, 'pesquisa'));
  gravarFontes(R);
  grava('conteudo/tema.css', ':root{--fora:#10231f}.reveal .tela{background:#10231f;font:30px system-ui;color:#eef}.t-c{padding:70px}.t-c h2{font-size:34px;margin:0 0 10px}.t-c p{margin:4px 0}.reveal .t-c button{display:block;margin:8px 0}.t-c ol{margin:0}.t-c a{color:#eef}');
  grava('conteudo/pagina.css', '.pagina{font:12pt Helvetica;background:#f4efe8;color:#111}.pagina a{color:#111}');
  grava('conteudo/glossario.json', '{"poro":{"termo":"Poro","definicao":"Abertura pequena da pele."}}');
  for (const { id, tipo } of P.telas) {
    const extra = tipo === 'sumario' ? '<nav data-sumario></nav>' : tipo === 'quiz'
      ? '<div data-quiz><button type="button">Esfregar</button><button type="button" data-certa>Limpar leve</button><p data-retorno="certa">Isso.</p><p data-retorno="errada">Pense na barreira.</p></div>' : '';
    grava(`conteudo/telas/${id}.html`, `<div class="t-c"><h2>Tela ${id}</h2>${extra}<svg width="500" height="120"><circle class="poro" cx="60" cy="60" r="40" fill="#fb5"/></svg></div>`);
    grava(`conteudo/telas/${id}.js`, `EBOOK.anima('${id}',({tl,$})=>{tl.from($('h2'),{opacity:0,duration:.4}).from($('.poro'),{x:300,duration:.6}).to($('.poro'),{scale:1.1,duration:1.2})});`);
    grava(`conteudo/paginas/${id}.html`, tipo === 'capa' ? '<h1>{{titulo}}</h1><p>{{autor}}</p>' : `<h2>${id}</h2>${tipo === 'sumario' ? extra : '<p>Página de teste.</p>'}`);
    grava(`conteudo/notas/${id}.html`, '<p>Nota.</p>');
    grava(`conteudo/info/${id}.html`, `<p><button type="button" class="gl" data-t="poro">poro</button> ${'palavra '.repeat(175)}</p>`);
    grava(`conteudo/roteiro/${id}.txt`, 'palavra '.repeat(285));
    fs.mkdirSync(path.join(R, 'audio'), { recursive: true });
    execFileSync('ffmpeg', ['-v', 'error', '-y', '-f', 'lavfi', '-i', 'sine=frequency=330:duration=2', '-c:a', 'aac', path.join(R, `audio/${id}.m4a`)]);
  }
  const rodar = (s, ...a) => spawnSync(process.execPath, [path.join(S, s), R, ...a], { encoding: 'utf8' });
  const passa = (s, ...a) => { const r = rodar(s, ...a); assert.strictEqual(r.status, 0, `${s} ${a}\n${r.stdout}${r.stderr}`); };
  const falha = (s, trecho, ...a) => { const r = rodar(s, ...a); assert(r.status !== 0 && (r.stdout + r.stderr).includes(trecho), `esperava "${trecho}"\n${r.stdout}${r.stderr}`); };

  const tem = f => fs.existsSync(path.join(R, 'entregas', f));
  for (const c of COMBOS) {
    grava('ebook.json', JSON.stringify(ebook(c)));
    passa('montar.cjs', '--amostra'); passa('conferir.cjs', '--amostra');
    passa('montar.cjs'); passa('conferir.cjs');
    assert.strictEqual(tem('slides-de-aula.html'), c.includes('slides'));
    assert.strictEqual(tem('ebook.pdf'), c.includes('pdf'));
    assert.strictEqual(tem('autoestudo.zip'), c.includes('autoestudo'));
    console.log('  ok', c.join(' + '));
  }
  const troca = (f, novo, trecho) => {
    const velho = fs.readFileSync(path.join(R, f));
    grava(f, novo); passa('montar.cjs'); falha('conferir.cjs', trecho);
    grava(f, velho);
  };
  // o áudio é conferido contra a data do roteiro, por isso este caso fica por último
  troca('conteudo/telas/topico-0.js', "EBOOK.anima('topico-0',()=>{});", 'sem animação de verdade');
  troca('conteudo/telas/topico-0.html', '<div class="t-c"><h2>T</h2><p style="font-size:10px">miúdo</p><svg><circle class="poro" r="30"/></svg></div>', 'letra de 10 px');
  troca('conteudo/paginas/topico-0.html', '<p>linha</p>'.repeat(90), 'texto cortado');
  const base = fs.readFileSync(path.join(R, 'conteudo/telas/topico-0.html'), 'utf8'), P0 = 'position:absolute;margin:0;left:70px;';
  troca('conteudo/telas/topico-0.html', `${base}<p style="${P0}top:78px">texto por cima</p>`, 'texto sobre texto');
  troca('conteudo/telas/topico-0.html', `${base}<p style="${P0}top:500px;color:#12251f">sumido</p>`, 'contraste baixo');
  troca('conteudo/telas/topico-0.html', `${base}<p style="${P0}top:500px;font-size:20px">um dois três quatro cinco seis sete oito</p>`, 'letra de 20 px');
  troca('conteudo/telas/topico-0.js', "EBOOK.anima('topico-0',({tl,$})=>{for(let i=0;i<3;i++)tl.to($('.nao-existe'),{x:9,duration:.8})});", 'sem alvo');
  troca('conteudo/telas/topico-0.js', "EBOOK.anima('topico-0',({tl,$})=>{for(const q of ['h2','.poro','svg'])tl.from($(q),{opacity:0,duration:.8})});", 'só fade');
  troca('conteudo/telas/topico-0.js', "EBOOK.anima('topico-0',({tl,$})=>{for(const q of ['h2','.poro','svg'])tl.to($(q),{x:0,duration:.8})});", 'sem animação de verdade');
  troca('conteudo/roteiro/topico-0.txt', 'palavra '.repeat(290), 'áudio mais velho que o roteiro');
  console.log('  ok casos que devem reprovar');
  return R;
}

(async () => {
  regras(); console.log('regras ok');
  await fluxo(); console.log('fluxo ok (7 combinações x 4 etapas x aprova/reprova)');
  if (process.argv[2]) console.log('ponta a ponta ok:', pontaAPonta(process.argv[2]));
})().catch(e => { console.error(e.message); process.exit(1); });
