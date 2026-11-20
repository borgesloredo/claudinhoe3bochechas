export const meta = {
  name: 'curso-fase1-conteudo-pdf',
  description: 'Curso de mesa de som, fase 1: manuais e pesquisa por mesa (paralelo), consolidação, curso final e PDF de aula já revisado (storytelling, redundância, neutralidade, design)',
  phases: [
    { title: 'Manuais + Pesquisa', detail: 'Um agente por mesa para o manual e outro para a pesquisa, cada um com revisor' },
    { title: 'Consolidação', detail: 'Manual consolidado e conhecimento consolidado' },
    { title: 'Curso', detail: 'Curso final em capítulos' },
    { title: 'PDF', detail: 'PDF de aula e revisão por checklist até aprovar' },
  ],
}

// args: { R, K, mesa, familia, modelos: [{slug, name}], grupos?: [{slug, name, modelos: [nomes]}], cta }
// grupos = modelos que dividem o mesmo manual/plataforma (ex.: SQ-5/6/7/Rack). Manual e pesquisa rodam por GRUPO, não por modelo.
const { R, K, mesa, familia, modelos, cta } = args
const grupos = (args.grupos && args.grupos.length) ? args.grupos : modelos.map(m => ({ slug: m.slug, name: m.name, modelos: [m.name] }))
const MAX = 3
// Modelo por função: Opus decide a qualidade (escrita final, design, motion, técnico); Sonnet confere listas, extrai, pesquisa e testa; Haiku só roda comando.
const OPUS = { model: 'opus' }, SONNET = { model: 'sonnet' }, BARATO = { model: 'sonnet', effort: 'low' }
const LISTA = modelos.map(m => m.name).join('; ')
const CTX = `CONTEXTO: curso em PT-BR sobre a mesa ${mesa} e as mesas da mesma família (${familia}), que compartilham muito conteúdo. Mesas confirmadas pelo dono: ${LISTA}.
Pasta do projeto: ${R}. Leia ANTES ${K}/references/regras-do-curso.md (regras obrigatórias: voz, sem nomes de autores/escolas, divergências neutras, sem metacomentário, diagramas próprios, downloads em ${R}/downloads/<slug>/ executados nunca). Texto exato do CTA do capítulo "Onde estudar": "${cta}".
Ferramentas: python3 -I ${R}/tools/pdf2txt.py <pdf> <txt>; playwright em ${R}/tools/node_modules/playwright; render de PDF: node ${R}/tools/render-pdf.mjs <html> <pdf>. Use WebSearch/WebFetch (carregue com ToolSearch se precisar).${args.notas ? `\nNOTAS DO DONO (valem acima das instruções de etapa quando conflitarem):\n${args.notas}` : ''}`

const VERDICT = { type: 'object', properties: { approved: { type: 'boolean' }, score: { type: 'number' }, issues: { type: 'array', items: { type: 'string' } } }, required: ['approved', 'score', 'issues'] }
const VERIFY = { type: 'object', properties: { items: { type: 'array', items: { type: 'object', properties: { n: { type: 'number' }, status: { type: 'string' }, note: { type: 'string' } }, required: ['n', 'status', 'note'] } }, regressions: { type: 'array', items: { type: 'string' } } }, required: ['items', 'regressions'] }
const status = []

// Revisor de etapa: faz, revisa, refaz até aprovar (máx. MAX rodadas).
async function reviewed(label, phase, work, scope, outputs, mw = OPUS, mr = OPUS) {
  let fb = ''
  for (let r = 1; r <= MAX; r++) {
    await agent(`${CTX}\n\n${work}${fb ? `\n\nO revisor reprovou a rodada anterior. Os arquivos existem: corrija TODOS os pontos:\n- ${fb}` : ''}\n\nResponda só com um resumo curto e os caminhos.`, { label: `${label} r${r}`, phase, ...mw })
    const v = await agent(`${CTX}\n\nVocê é REVISOR da entrega "${label}". Arquivos: ${outputs}\nESCOPO:\n${scope}\nLeia tudo, confira cada item, confira 3 a 5 fatos/links por amostragem e as regras do curso. Aprove só se cumprido; senão, liste problemas concretos e acionáveis.`, { label: `revisor:${label} r${r}`, phase, schema: VERDICT, ...mr })
    if (v && v.approved) { status.push({ label, ok: true, r, score: v.score }); return true }
    fb = v ? v.issues.join('\n- ') : 'Revisor falhou; revise contra o escopo.'
  }
  status.push({ label, ok: false, pendente: fb }); log(`⚠ ${label} não aprovado após ${MAX} rodadas`); return false
}

// Checklist: revisores em paralelo → itens numerados → corretor → verificador item a item.
async function checklist(name, phase, reviewers, fixPrompt) {
  let pend = reviewers
  for (let r = 1; r <= MAX; r++) {
    const vs = (await parallel(pend.map(rv => () => agent(rv.p + (r > 1 ? '\nRODADA DE CONFERÊNCIA: confirme correções e regressões; não reprove por novidades menores.' : ''), { label: `${rv.l} r${r}`, phase, schema: VERDICT, ...(rv.m || OPUS) }).then(v => v && { ...v, l: rv.l })))).filter(Boolean)
    const aprovou = rv => vs.some(v => v.l === rv.l && v.approved)
    log(`${name} r${r}: ${vs.filter(v => v.approved).length}/${pend.length} aprovados`)
    if (pend.every(aprovou)) return { approved: true, r }
    pend = pend.filter(rv => !aprovou(rv))
    let todo = vs.flatMap(v => v.approved ? [] : v.issues).map((t, i) => `${i + 1}. ${t}`).join('\n')
    for (let f = 1; f <= 2 && todo; f++) {
      await agent(`${fixPrompt}\nCHECKLIST (corrija todos):\n${todo}`, { label: `${name} corrigir r${r}.${f}`, phase, ...OPUS })
      const v = await agent(`${CTX}\nVERIFICADOR: para cada item numerado, resolvido ou pendente? Só aponte regressões causadas pelas correções.\n${todo}`, { label: `${name} verificar r${r}.${f}`, phase, schema: VERIFY, ...SONNET })
      if (!v) continue
      const pend = v.items.filter(i => i.status === 'pendente')
      todo = pend.map(p => `${p.n}. ${(todo.split('\n').find(l => l.startsWith(p.n + '.')) || '').replace(/^\d+\.\s*/, '')} (verificador: ${p.note})`).concat(v.regressions.map(x => `REGRESSÃO: ${x}`)).join('\n')
    }
  }
  return { approved: false }
}

phase('Manuais + Pesquisa')
const manual = m => reviewed(`manual:${m.slug}`, 'Manuais + Pesquisa',
  `Condense o MANUAL OFICIAL COMPLETO (user/owner's manual, qualquer idioma; se só houver quick start, junte o manual do app e o da família) do grupo ${m.name} (modelos: ${m.modelos.join(', ')}; registre as diferenças entre eles). Baixe para ${R}/downloads/${m.slug}/, extraia e escreva ${R}/01-manuais/${m.slug}.md em PT-BR, por capítulos, com ficha técnica no topo (fonte, I/O, canais, buses, FX, conexão). Cubra tudo: hardware/conexões, fluxo de sinal, canais, preamps, EQ, dinâmica, buses, matriz, DCA/mute groups, FX, roteamento, USB/gravação, cenas, rede/apps, firmware, especificações.`,
  `- ${R}/01-manuais/${m.slug}.md existe, baseado no manual oficial mais completo, com fonte citada.\n- Nenhuma seção relevante ficou de fora; parafraseado.`, `${R}/01-manuais/${m.slug}.md`, SONNET, SONNET)
// args.pular: ['pesquisa:<slug>', ...] = etapa já entregue em disco fora do workflow (ex.: agente que entregou o relatório ao fio principal)
const pular = (label, run) => (args.pular || []).includes(label) ? (status.push({ label, ok: true, pulado: true }), true) : run()
const pesquisa = m => pular(`pesquisa:${m.slug}`, () => reviewed(`pesquisa:${m.slug}`, 'Manuais + Pesquisa',
  `Varra a internet (PT, EN, ES) atrás de TODO conteúdo de ensino sobre o grupo ${m.name} (modelos: ${m.modelos.join(', ')}): cursos, PDFs, videoaulas, YouTube, podcasts, reels, shorts, blogs, ebooks, tutoriais, fóruns. Leia as melhores fontes e escreva ${R}/03-pesquisa/${m.slug}.md: tabela de fontes (uso interno: título, tipo, idioma, URL verificada) + conhecimento condensado por tema (setup, ganho, EQ, dinâmica, monitores, FX, roteamento, gravação, cenas, rede, ao vivo, igreja/banda), com dicas, erros comuns e ONDE AS ABORDAGENS DIVERGEM (descreva cada abordagem). Os nomes ficam só neste arquivo de pesquisa; nunca passam para o material do aluno.`,
  `- ${R}/03-pesquisa/${m.slug}.md existe; varreu vários tipos de fonte; URLs reais.\n- Conhecimento condensado por tema, com divergências mapeadas.`, `${R}/03-pesquisa/${m.slug}.md`, SONNET, SONNET))
const manuaisP = parallel(grupos.map(m => () => manual(m)))
const pesquisaP = parallel(grupos.map(m => () => pesquisa(m)))

phase('Consolidação')
const TAG = 'Todo título indica entre parênteses as mesas em que vale (nomes explícitos, ou família se todas se aplicam e a legenda define).'
await Promise.all([
  manuaisP.then(() => reviewed('consolidado-manual', 'Consolidação', `Junte TODOS os .md de ${R}/01-manuais/ em ${R}/02-manual-consolidado.md: manual único, legenda de famílias, tabela comparativa de especificações, diferenças explícitas, sem repetir o comum. ${TAG}`, `- Nada relevante perdido; ${TAG}`, `${R}/02-manual-consolidado.md`, SONNET, SONNET)),
  pesquisaP.then(() => reviewed('consolidado-pesquisa', 'Consolidação', `Junte TODOS os .md de ${R}/03-pesquisa/ em ${R}/04-conhecimento-consolidado.md: conhecimento prático por tema, dicas deduplicadas, divergências com TODAS as abordagens (neutras; os nomes podem ficar só como nota interna de rodapé deste arquivo). ${TAG}`, `- Nada relevante perdido; sem repetição; ${TAG}`, `${R}/04-conhecimento-consolidado.md`, SONNET, SONNET)),
])

phase('Curso')
await reviewed('curso-final', 'Curso', `Junte ${R}/02-manual-consolidado.md e ${R}/04-conhecimento-consolidado.md em ${R}/05-curso-final.md, em capítulos didáticos (do ligar ao show; ~25–28 capítulos, incluindo glossário e "Onde estudar" com o CTA exato). Em cada capítulo: o que o manual diz e, em seguida, como se faz na prática. Já sem redundância (cada conceito num lugar canônico), com fio narrativo e com as divergências no formato "Abordagens divergentes" (todas, neutras, sem nomes). Nenhum nome de autor/escola/canal/fórum. ${TAG}`,
  `- Capítulos completos; regras do curso cumpridas (sem nomes, divergências neutras, sem metacomentário, CTA exato).\n- ${TAG}`, `${R}/05-curso-final.md`)

phase('PDF')
const PDF = `${R}/06-pdf/curso.pdf`, HTML = `${R}/06-pdf/curso.html`
await agent(`${CTX}\nSkills: leia ~/.claude/skills/frontend-slides/SKILL.md (anti-genérico) e leia ${K}/references/storytelling.md e, se a skill "storytelling" existir, invoque-a com a ferramenta Skill.\nTransforme ${R}/05-curso-final.md no PDF de aula: ${HTML} (HTML + CSS de impressão + SVG próprio, tudo local) → ${PDF}. Adapte ${R}/tools/build_pdf_html.py (referência da 1ª execução: tem amarras à XR18 — duas famílias, nomes de capítulos — troque pelas deste curso) e gere SEMPRE com sh ${R}/tools/make-pdf.sh (duas passadas: a 2ª preenche as páginas do sumário). Nunca use caminhos fora de ${R}. Requisitos: capa, sumário, glossário, numeração, pelo menos uma visualização própria por capítulo, caixas de dica/atenção, selo/caixa "Abordagens divergentes", fio narrativo, sem prolixidade nem redundância, visual sóbrio e forte. Confira páginas com Read (pages) e corrija.`, { label: 'pdf', phase: 'PDF', ...OPUS })
const base = `${CTX}\nArquivos: ${HTML}, ${PDF} (páginas com Read; texto com python3 ${R}/tools/pdf2txt.py).`
const pdf = await checklist('pdf', 'PDF', [
  { l: 'rev storytelling', p: `${base}\nLeia ${K}/references/storytelling.md e, se a skill "storytelling" existir, invoque-a com a ferramenta Skill. Critério: fio narrativo, ganchos, transições, fechamento; curso autônomo, sem voz de IA.` },
  { l: 'rev redundância', m: SONNET, p: `${base}\nCritério: nenhum conceito explicado 2+ vezes, nenhum parágrafo prolixo; use script de similaridade entre seções.` },
  { l: 'rev regras/neutralidade', m: SONNET, p: `${base}\nCritério: TODAS as regras de ${K}/references/regras-do-curso.md (zero nomes de autores/escolas/canais/fóruns; divergências neutras e completas; CTA exato; nenhuma mesa inexistente citada; sem metacomentário/bastidor).` },
  { l: 'rev técnico', p: `${base}\nCritério: correção técnica de áudio e das mesas (ganho, fluxo de sinal, insert, buses, pré/pós, DCA, matrizes, rede...), coerência com ${R}/02-manual-consolidado.md; nenhum tópico técnico relevante perdido.` },
  { l: 'rev design', p: `${base}\nCritério: visual profissional, pelo menos uma visualização própria por capítulo, nada cortado, quebras de página boas, legível.` },
], `${CTX}\nVocê CORRIGE o PDF (${HTML}; se a mudança for de conteúdo, também ${R}/05-curso-final.md) e regenera ${PDF} com sh ${R}/tools/make-pdf.sh.`)

return { status, pdf, pdfPath: PDF }
