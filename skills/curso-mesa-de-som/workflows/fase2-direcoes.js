export const meta = {
  name: 'curso-fase2-direcoes',
  description: 'Curso de mesa de som, fase 2: direção visual Hardware da mesa (ou as que args.direcoes pedir) com motion GSAP nos mesmos 6 slides de amostra, com 1 revisão',
  phases: [
    { title: 'Direções', detail: 'Um designer por direção' },
    { title: 'Revisão de design', detail: 'Revisor com prints intermediários, loop até aprovar' },
  ],
}

// args: { R, K, mesa, direcoes? } — direcoes: números das direções a gerar; padrão [2] (o dono prefere Hardware da mesa; as outras só se ele reprovar)
const { R, K, mesa } = args
// Modelo por função: Opus decide a qualidade (escrita final, design, motion, técnico); Sonnet confere listas, extrai, pesquisa e testa; Haiku só roda comando.
const OPUS = { model: 'opus' }, SONNET = { model: 'sonnet' }, BARATO = { model: 'sonnet', effort: 'low' }
const MAX = 1 // amostra: o polimento acontece na Fase 3, com as pendências do revisor
const D = `${R}/07-slides/redesign`
const DIRS = [
  { n: 1, name: 'Palco escuro', brief: 'Fundo escuro de palco/estúdio, acentos em cores de LED e medidores (verde/amarelo/vermelho), brilho sutil, show ao vivo.' },
  { n: 2, name: 'Hardware da mesa', brief: 'Superfície física FIEL à mesa escolhida (cor e acabamento do painel, display, disposição, serigrafia, LEDs e teclas reais, conferidos nas ilustrações do manual e em fotos); nunca elementos de outra marca/linha (ex.: scribble strips coloridas só se a mesa tiver); o diagrama parece a própria mesa.' },
  { n: 3, name: 'Editorial bold', brief: 'Claro, editorial e ousado (Swiss/poster): tipografia gigante, blocos de cor fortes por capítulo, grid rígido, alto contraste.' },
].filter(d => (args.direcoes || [2]).includes(d.n))
const SAMPLES = `Os MESMOS 6 slides de amostra, com conteúdo real de ${R}/05-curso-final.md / ${R}/06-pdf/curso.html: 1. capa; 2. abertura de um capítulo; 3. tópico com diagrama de medidores; 4. tópico com tabela (ex.: HPF por instrumento); 5. quiz (ex.: "O que o gate faz?"); 6. caminho do sinal clicável. Cada um com <aside class="notes"> curto e complementar.`
const RULES = `Leia ANTES: ${K}/references/regras-do-curso.md, ${K}/references/design.md, o manual de referência ${K}/assets/direcoes/opcao-N/DESIGN.md da sua direção (e o contato.png), ~/.claude/skills/frontend-slides/SKILL.md (+ STYLE_PRESETS.md, animation-patterns.md, viewport-base.css), ~/.claude/skills/motion-design/SKILL.md, ~/.claude/skills/gsap-core, gsap-timeline, gsap-plugins, gsap-performance.
Base: reveal.js + GSAP locais. COPIE ${R}/07-slides/lib para dentro da SUA pasta (lib/) e referencie "lib/..." — nada de "../" (o Safari bloqueia) e nada de CDN; fontes baixadas para a sua pasta.
Exigências: sem espaço vazio, diagrama protagonista, identidade própria adaptada à ${mesa}; corpo >= 28px e rótulos >= 18px em 1280x720; motion que DEMONSTRA o conceito (DrawSVG, MotionPath, medidores reagindo), estados idempotentes, reduced-motion; quiz clicável com certo/errado; caminho do sinal clicável. Não mexa fora da sua pasta.\nPRINTS (custo): confira layout por script (playwright: caixas, sobreposição, área vazia, tamanho de fonte) e olhe imagens só em grade (contact sheet de 6–24 slides, largura <= 1600 px). Abra um print individual só quando o script apontar problema. Cada imagem lida fica no contexto até o fim e encarece todos os passos seguintes.`
const VERDICT = { type: 'object', properties: { approved: { type: 'boolean' }, score: { type: 'number' }, issues: { type: 'array', items: { type: 'string' } }, highlights: { type: 'string' } }, required: ['approved', 'score', 'issues', 'highlights'] }

const results = await parallel(DIRS.map(d => async () => {
  const dir = `${D}/opcao-${d.n}`
  let fb = '', sc
  for (let r = 1; r <= MAX; r++) {
    await agent(`Você é designer de apresentações e motion designer. Crie a DIREÇÃO ${d.n} — "${d.name}" para os slides de um curso PT-BR sobre a mesa ${mesa}.\nBriefing: ${d.brief}\nEntregue em ${dir}/: index.html (${SAMPLES}); DESIGN.md (tokens, layouts por tipo de slide — capa, abertura, tópico+diagrama, tabela, quiz, interativo —, regras de motion, contrato para aplicar num gerador de ~150 slides); shots/ (prints 1280x720 do estado final de cada slide + contato.png em grade); motion.mp4 (playwright recordVideo navegando os 6 slides, convertido com ~/.local/bin/ffmpeg -c:v libx264 -pix_fmt yuv420p, porque o QuickTime não abre WebM; áudio do teste mudo).\n${RULES}\nConfira seus prints com Read e corrija antes de encerrar.${fb ? `\n\nO revisor reprovou: corrija TODOS os pontos:\n- ${fb}` : ''}`, { label: `opcao-${d.n} r${r}`, phase: 'Direções', ...OPUS })
    const v = await agent(`Você é revisor de design exigente. Revise ${dir}/ ("${d.name}"). Abra os prints; gere prints próprios em 150ms/400ms/900ms após entrar em cada slide e após cada fragment; clique no quiz; abra o index.html no WebKit do playwright (${R}/tools/node_modules/playwright) num contexto offline: 0 erros, 0 requisições externas, nenhum caminho "../".\nCritérios (reprove se falhar em qualquer um): sem espaço vazio; identidade própria coerente com "${d.brief}"; motion didático, fluido, sem exagero; legível (corpo >= 28px); quiz e interativo funcionando; DESIGN.md completo para aplicar em ~150 slides gerados por script. Liste problemas concretos.`, { label: `revisor opcao-${d.n} r${r}`, phase: 'Revisão de design', schema: VERDICT, ...OPUS })
    if (v && v.approved) return { n: d.n, name: d.name, approved: true, score: v.score, highlights: v.highlights, rounds: r }
    sc = v && v.score
    fb = v ? v.issues.join('\n- ') : 'Revisor falhou; revise contra todos os critérios.'
  }
  return { n: d.n, name: d.name, approved: false, score: sc, pendente: fb }
}))
return results
