export const meta = {
  name: 'curso-fase3-deck-aula',
  description: 'Curso de mesa de som, fase 3: deck de aula completo (V1) na direção escolhida, já enxuto, com motion sob medida em todo slide e notas do apresentador; revisão por checklist até aprovar',
  phases: [
    { title: 'Base', detail: 'Gerador adaptado, plano enxuto de slides, design aplicado' },
    { title: 'Padrão de motion', detail: 'Biblioteca comum, receita por tipo de slide e um slide-modelo de cada tipo' },
    { title: 'Motion e notas', detail: 'Lotes paralelos: animação sob medida e notas por faixa' },
    { title: 'Revisão', detail: 'Design, motion, técnico, redundância, narrativa, notas, funcional' },
  ],
}

// args: { R, K, mesa, direcao: {n, name}, meta_slides }
// Paralelismo além de 8 agentes (opcional): 1) parar_em:'base' → devolve o plano; 2) N workflows com plan + shard:{n,of} + parar_em:'motion' em paralelo; 3) um com plan + pular_motion:true para a revisão. extra (opcional): instrução adicional para todos os agentes.
const { R, K, mesa, direcao, meta_slides } = args
const MAX = 3
// Modelo por função: Opus decide a qualidade (escrita final, design, motion, técnico); Sonnet confere listas, extrai, pesquisa e testa; Haiku só roda comando.
const OPUS = { model: 'opus' }, SONNET = { model: 'sonnet' }, BARATO = { model: 'sonnet', effort: 'low' }
const T = `${R}/tools`, DECK = `${R}/07-slides/index.html`, SHOTS = `${R}/07-slides/redesign/shots-deck`
const DIR = `${R}/07-slides/redesign/opcao-${direcao.n}`
const CTX = `CONTEXTO: deck de AULA (V1) do curso PT-BR sobre a mesa ${mesa} e família. Fonte do conteúdo: ${R}/06-pdf/curso.html (aprovado) e ${R}/05-curso-final.md.
Leia ANTES: ${K}/references/regras-do-curso.md (seções 1–4, 6, 7 e 9 são obrigatórias aqui) e ${K}/references/design.md. Quem só roda ferramentas (integrador, verificador, funcional) pula esta leitura.
Direção visual escolhida pelo dono: ${direcao.n} "${direcao.name}" — referência aprovada em ${DIR}/ (index.html, DESIGN.md, shots/). Skills: ~/.claude/skills/frontend-slides/SKILL.md, motion-design, gsap-core, gsap-timeline, gsap-plugins, gsap-performance.
SISTEMA: o deck é GERADO por ${T}/build_slides.py (+ slides_template.html, slides_viz.py, enxugamento.py, bespoke/<id>.svg|.js, notes/<id>.html) — são as ferramentas de referência da 1ª execução (curso XR18); adapte-as a este curso. AMARRAS À 1ª EXECUÇÃO (XR18) a trocar pelas deste curso: tools/enxugamento.py é um EXEMPLO — reescreva-o com o plano enxuto deste curso (ordem dos slides por capítulo, fusões, quizzes, aberturas); build_slides.py tem listas fixas de modelos por família e o sumário fixo de capítulos; check_titles.mjs assume duas famílias; as cores por família do DESIGN.md (ex.: --xair/--x32) viram as famílias deste curso (1 ou N); slides_steps.py está FORA DE USO. Nunca edite ${DECK} à mão. Prévia isolada: build_slides.py --only id1,id2 --out <arq>. Checadores em ${T}/ (verify_slides.mjs, check_fonts.mjs, check_titles.mjs, check_cuts.py, check_notes.py). Playwright em ${T}/node_modules/playwright (áudio sempre mudo nos testes). Tudo dentro de ${R}/07-slides/ (lib/, fonts/), sem "../".\nPRINTS (custo): confira layout por script (playwright: caixas, sobreposição, área vazia, tamanho de fonte) e olhe imagens só em grade (contact sheet de 6–24 slides, largura <= 1600 px). Abra um print individual só quando o script apontar problema. Cada imagem lida fica no contexto até o fim e encarece todos os passos seguintes.${args.extra ? `\n${args.extra}` : ''}`

const VERDICT = { type: 'object', properties: { approved: { type: 'boolean' }, score: { type: 'number' }, issues: { type: 'array', items: { type: 'string' } } }, required: ['approved', 'score', 'issues'] }
const VERIFY = { type: 'object', properties: { items: { type: 'array', items: { type: 'object', properties: { n: { type: 'number' }, status: { type: 'string' }, note: { type: 'string' } }, required: ['n', 'status', 'note'] } }, regressions: { type: 'array', items: { type: 'string' } } }, required: ['items', 'regressions'] }
const INTEGRA = { type: 'object', properties: { ok: { type: 'boolean' }, saida: { type: 'string' } }, required: ['ok', 'saida'] }
const MODELOS = { type: 'object', properties: { modelos: { type: 'array', items: { type: 'string' } } }, required: ['modelos'] }
const PLAN = { type: 'object', properties: { slides: { type: 'array', items: { type: 'object', properties: { id: { type: 'string' }, cap: { type: 'number' }, tipo: { type: 'string' }, conceito: { type: 'string' } }, required: ['id', 'cap', 'tipo', 'conceito'] } } }, required: ['slides'] }

phase('Base')
const plan = args.plan ? null : await agent(`${CTX}
Monte a BASE do deck:
1. Adapte o gerador ao conteúdo deste curso e aplique o DESIGN.md da direção escolhida (copie as fontes para ${R}/07-slides/fonts/). Hooks: ${T}/bespoke/<id>.svg|.js substitui o diagrama/motion do slide (contrato em ${T}/bespoke/README.md, para TODOS os tipos: capa, sumário, aberturas, tópicos, quizzes, interativos); ${T}/notes/<id>.html substitui a nota.
2. Plano ENXUTO já na primeira versão (não gere um deck inchado para cortar depois): só o índice geral (sem agenda por capítulo); abertura de capítulo como introdução; um slide por ideia, sem repetir o anterior nem outro capítulo; texto do slide sem repetir o rótulo do diagrama; sem "Em cena"; pergunta à turma fora do slide; quizzes (1 por capítulo de conteúdo), caminho do sinal clicável, explorador de mesas, glossário; selo "Abordagens divergentes" compacto nas divergências. Meta: perto de ${meta_slides} telas e no máximo 3 continuações.
3. Gere o deck, rode os checadores e conserte o que quebrar.
Retorne a lista de slides (id, capítulo, tipo, conceito a demonstrar no motion).`, { label: 'base do deck', phase: 'Base', schema: PLAN, ...OPUS })
const planFinal = args.plan ? { slides: args.plan } : plan
const slides = (planFinal && planFinal.slides) || []
log(`${slides.length} slides no plano`)

// Padrão antes dos lotes: os lotes rodam em paralelo e, sem uma referência comum, o estilo do motion varia entre eles
phase('Padrão de motion')
const tipos = [...new Set(slides.map(s => s.tipo))]
const pad = args.plan ? { modelos: args.modelos || [] } : await agent(`${CTX}
Defina o PADRÃO DE MOTION que todos os lotes vão seguir. Os lotes rodam em paralelo, 5 slides cada, e sem padrão o estilo varia entre eles.
1. ${T}/bespoke/_padrao.js: biblioteca comum que o gerador carrega antes dos .js dos slides (se o gerador adaptado não carregar, inclua). Easings nomeados da direção, durações e stagger, e as peças reutilizáveis desta mesa: entrada do painel, acender tecla/LED, medidor reagindo, filete de sinal (DrawSVG/MotionPath), fader/knob movendo, consequência de quiz, reset idempotente. Cabeçalho de até 60 linhas documentando a API: é só ele que os lotes leem.
2. ${T}/bespoke/PADRAO.md (até 150 linhas): para cada tipo de slide do plano (${tipos.join(', ')}), a receita: estrutura do SVG, classes e cores (tokens do DESIGN.md), peças do _padrao.js a usar, ritmo por passo, entrada e saída, consequência no quiz. Inclua o que NÃO fazer.
3. SLIDES-MODELO: o sob medida completo (svg + js, usando o _padrao.js) do primeiro slide de cada tipo do plano. São a referência visual dos lotes e já valem como slides finais, no nível das amostras aprovadas em ${DIR}/.
Plano: ${slides.map(s => `${s.id} (${s.tipo})`).join(', ')}
Teste os modelos com --only (0 erros no verify_slides da prévia), gere uma folha de contato dos modelos e confira seguindo a regra PRINTS. Retorne os ids dos slides-modelo.`, { label: 'padrão de motion', phase: 'Padrão de motion', schema: MODELOS, ...OPUS })
const modelos = (pad && pad.modelos) || []
if (args.parar_em === 'base') return { slides, modelos }
const modeloDo = t => modelos.find(id => (slides.find(s => s.id === id) || {}).tipo === t)

phase('Motion e notas')
// lote de 5: o contexto cresce a cada passo; dois agentes curtos gastam menos que um longo (medido: lote de 10 = 48 passos, 225K de contexto final)
const LOTE = args.lote || 5
const sh = args.shard || { n: 0, of: 1 }
const lotes = []
const resto = slides.filter(s => !modelos.includes(s.id))  // slides-modelo já ficaram prontos no padrão
for (let i = 0; i < resto.length; i += LOTE) lotes.push(resto.slice(i, i + LOTE))
const caps = [...new Set(slides.map(s => s.cap))].sort((a, b) => a - b)
const faixas = []
for (let i = 0; i < caps.length; i += Math.ceil(caps.length / 4)) faixas.push(caps.slice(i, i + Math.ceil(caps.length / 4)))
if (!args.pular_motion) await parallel([
  ...lotes.map((b, i) => [b, i]).filter(([, i]) => i % sh.of === sh.n).map(([b, i]) => () => agent(`${CTX}
Crie a animação SOB MEDIDA (${T}/bespoke/<id>.svg + .js) destes slides SEGUINDO O PADRÃO do curso: leia ${T}/bespoke/PADRAO.md, o cabeçalho de ${T}/bespoke/_padrao.js e os slides-modelo do mesmo tipo dos seus (${[...new Set(b.map(s => modeloDo(s.tipo)).filter(Boolean))].join(', ') || 'veja PADRAO.md'}). Use as peças, easings, durações e cores do padrão; nada de estilo próprio do lote. Não edite _padrao.js nem PADRAO.md: se faltar uma peça, implemente no seu .js e registre em ${T}/bespoke/PADRAO-PEDIDOS.md.
${b.map(s => `- ${s.id} (${s.tipo}, cap ${s.cap}): ${s.conceito}`).join('\n')}
A animação DEMONSTRA o conceito, sincronizada com os fragments, ~2–2,5 s por passo, estados idempotentes (avançar = voltar = pular), sem "ponto piscando na origem", reduced-motion, só transform/opacity (+DrawSVG/MotionPath), rótulos >= 18px, nada sobreposto, diagrama preenchendo o painel, tecnicamente correto (medidor de canal é pré-fader etc.). Aberturas: motivo visual do tema; quizzes: o caminho errado mostra a consequência e termina no estado de resposta.
Só crie/edite ${T}/bespoke/<id>.* dos SEUS slides. Antes de começar, liste ${T}/bespoke/: se a execução anterior foi interrompida, não refaça id que já passa em --only. Teste com --only seus ids em ${R}/07-slides/redesign/preview-lote-${i + 1}.html; print só do estado final, seguindo a regra PRINTS; no máximo 3 imagens lidas no total (uma folha de contato dos seus slides + até 2 para conferir correção); 0 erros.`, { label: `motion lote ${i + 1}/${lotes.length}`, phase: 'Motion e notas', ...OPUS })),
  ...(sh.n === sh.of - 1 ? faixas : []).map(f => () => agent(`${CTX}
Escreva as NOTAS DO APRESENTADOR (${T}/notes/<id>.html) de TODOS os slides dos capítulos ${f.join(', ')} (inclua capa/sumário/como-usar se tiver o capítulo 0; encerramento se tiver o último). Política em ${K}/references/regras-do-curso.md seção 7: complementa o slide, nunca repete slide nem diagrama, 60–160 palavras, pergunta à turma no bloco âmbar inline, divergências neutras, sem antecipar respostas. Fontes: ${R}/06-pdf/curso.html, ${R}/04-conhecimento-consolidado.md, ${R}/02-manual-consolidado.md. Só edite as notas da sua faixa.`, { label: `notas caps ${f[0]}-${f[f.length - 1]}`, phase: 'Motion e notas', ...SONNET })),
])
if (args.parar_em === 'motion') return { slides: slides.length, shard: sh }

phase('Revisão')
const crit = `Material: ${DECK}; contact sheets e tiras de motion em ${SHOTS}/ (index.txt); dump de texto+notas em ${R}/07-slides/redesign/notas-dump.md. Use playwright para conferir estados. Não leia dumps inteiros: filtre pelos ids da sua parte. Aprove só se o critério estiver cumprido; liste problemas concretos com id e correção.`
const REVS = [
  { l: 'design A', p: `Critério: design e motion na PRIMEIRA metade das sheets: identidade da direção, sem vazio, legível, motion sob medida em todo slide demonstrando o conceito, sem sobreposição; CONSISTÊNCIA: todo slide segue ${T}/bespoke/PADRAO.md e os slides-modelo do seu tipo (mesmas peças, easings, ritmo e cores), sem diferença perceptível entre lotes. Peça pedida por vários lotes em ${T}/bespoke/PADRAO-PEDIDOS.md vira item: incorporar ao _padrao.js e aplicar nos slides.` },
  { l: 'design B', p: `Critério: design e motion na SEGUNDA metade das sheets (mesmos critérios, inclusive a consistência com o padrão e com a primeira metade).` },
  { l: 'técnico', p: `Critério: conceitos de áudio e das mesas corretos em slides, diagramas, animações, quizzes e notas. Confira no desenho o estado aceso, nomes, números, abas e etiquetas de modelos contra a fonte; quiz não entrega a resposta antes do clique; contagem de tópicos da abertura bate com as telas.` },
  { l: 'redundância interna', m: SONNET, p: `Critério: nenhum slide repete o anterior ou outro do mesmo capítulo; nenhum texto duplicado; texto não repete o diagrama.` },
  { l: 'redundância entre capítulos', m: SONNET, p: `Critério: cada conceito tem lugar canônico; use script de similaridade entre todos os slides e notas.` },
  { l: 'narrativa', p: `Leia ${K}/references/storytelling.md e, se a skill "storytelling" existir, invoque-a com a ferramenta Skill. Critério: arco de curso de alto nível, aberturas e fechamentos, transições; zero voz de IA/bastidor; zero nomes de autores/escolas; divergências neutras; CTA exato.` },
  { l: 'notas', m: SONNET, p: `Critério: seção 7 das regras em TODAS as notas (complementares, sem repetir slide/diagrama, bloco âmbar nas perguntas, sem nota vazia).` },
  { l: 'funcional', m: SONNET, p: `Critério: contador, setas, progresso, fundo escuro e telas obrigatórias da seção 6 das regras; Reveal.next() pelo deck inteiro offline em Chromium e WebKit (0 erros, 0 requisições externas); contagem de telas (perto de ${meta_slides}) e continuações (<= 3); quizzes, caminho do sinal, explorador, glossário; reduced-motion; tecla S abre notas; sem "../"; arquivo único gerado por python3 -I ${T}/inline_single.py abre isolado numa pasta vazia.` },
]
const reId = id => new RegExp(`(^|[^\\w-])${id.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}($|[^\\w-])`)
const faixaDo = t => { const gs = new Set(slides.filter(sl => reId(sl.id).test(t)).map(sl => faixas.findIndex(fx => fx.includes(sl.cap)))); return gs.size === 1 ? [...gs][0] : -1 }
let resultado = { approved: false }
let pend = REVS
const notas = {}, ok = {}
for (let r = 1; r <= MAX; r++) {
  // integração mecânica por script (antes: agente Sonnet lendo imagens, 11,6M de tokens por rodada); só conserta com agente se falhar
  const iv = await agent(`Se ${T}/integrar.sh ou ${T}/notas_dump.py não existir, copie de ${K}/assets/ferramentas/. Rode: sh ${T}/integrar.sh ${R} — leva até 20 min: rode em segundo plano (run_in_background) e espere a notificação de término, sem repetir o comando. Não leia imagens nem outros arquivos. ok=true só se a saída terminar em "INTEGRAR OK"; senão ok=false e copie em saida as linhas FALHA e os trechos de erro.`, { label: `integrar r${r}`, phase: 'Revisão', model: 'haiku', schema: INTEGRA })
  if (!iv || !iv.ok) await agent(`${CTX}\nA integração falhou (sh ${T}/integrar.sh ${R}; logs completos em ${R}/07-slides/redesign/integrar-logs/):\n${iv ? iv.saida : 'o agente que roda o script não respondeu'}\nCorrija a causa no gerador, em bespoke/, em notes/ ou na ferramenta (nunca no HTML gerado) e rode o integrar.sh de novo até sair INTEGRAR OK. Falha que exige decisão de conteúdo ou design: não decida sozinho, descreva na resposta (os revisores vão ver).`, { label: `consertar integração r${r}`, phase: 'Revisão', ...SONNET })
  const vs = (await parallel(pend.map(rv => () => agent(`${CTX}\n${crit}\n${rv.p}${r > 1 ? '\nRODADA DE CONFERÊNCIA: confirme correções e regressões; não reprove por novidades menores.' : ''}`, { label: `${rv.l} r${r}`, phase: 'Revisão', schema: VERDICT, ...(rv.m || OPUS) }).then(v => v && { ...v, l: rv.l })))).filter(Boolean)
  vs.forEach(v => { notas[v.l] = v.score; ok[v.l] = v.approved })
  pend = pend.filter(rv => !vs.some(v => v.l === rv.l && v.approved))
  log(`r${r}: ${REVS.length - pend.length}/${REVS.length} aprovados`)
  if (!pend.length) { resultado = { approved: true, r, scores: notas }; break }
  if (!pend.some(rv => rv.l === 'funcional')) pend = [...pend, REVS.find(rv => rv.l === 'funcional')]
  let todo = vs.flatMap(v => v.approved ? [] : v.issues).map((t, i) => `${i + 1}. ${t}`).join('\n')
  for (let f = 1; f <= 2 && todo; f++) {
    // item que cita slides de uma faixa só vai para o corretor da faixa (contexto pequeno, em paralelo); o resto, para o corretor global
    const itens = todo.split(/\n(?=\d+\. |REGRESSÃO: )/)
    const porFaixa = faixas.map(() => []), global = []
    itens.forEach(t => { const g = faixaDo(t); (g < 0 ? global : porFaixa[g]).push(t) })
    if (global.length) await agent(`${CTX}\nCorrija TODOS os itens (no gerador, bespoke ou notes):\n${global.join('\n')}`, { label: `corrigir global r${r}.${f}`, phase: 'Revisão', ...OPUS })
    await parallel(porFaixa.map((it, g) => [it, faixas[g]]).filter(([it]) => it.length).map(([it, fx]) => () => agent(`${CTX}\nCorrija os itens abaixo só nos slides dos capítulos ${fx.join(', ')} (${T}/bespoke/<id>.* e ${T}/notes/<id>.html). Não mexa no gerador nem em slides de outros capítulos; se um item exigir isso, diga na resposta. Teste com --only.\n${it.join('\n')}`, { label: `corrigir caps ${fx[0]}-${fx[fx.length - 1]} r${r}.${f}`, phase: 'Revisão', ...OPUS })))
    const v = await agent(`${CTX}\nVERIFICADOR: regere ${DECK} e, para cada item, diga se está resolvido ou pendente. Só regressões causadas pelas correções.\n${todo}`, { label: `verificar r${r}.${f}`, phase: 'Revisão', schema: VERIFY, ...SONNET })
    if (!v) continue
    todo = v.items.filter(i => i.status === 'pendente').map(p => `${p.n}. ${(todo.split('\n').find(l => l.startsWith(p.n + '.')) || '').replace(/^\d+\.\s*/, '')} (verificador: ${p.note})`).concat(v.regressions.map(x => `REGRESSÃO: ${x}`)).join('\n')
  }
}
return { slides: slides.length, resultado: { ...resultado, scores: notas, pendentes: REVS.filter(rv => !ok[rv.l]).map(rv => rv.l) }, deck: DECK, arquivo_unico: `${R}/07-slides/curso-slides.html` }
