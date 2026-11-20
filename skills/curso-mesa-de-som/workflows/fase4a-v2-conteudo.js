export const meta = {
  name: 'curso-fase4a-v2-conteudo',
  description: 'Curso de mesa de som, fase 4a: V2 autoestudo — glossário, interface (i)/▶ sobre a V1 congelada, textos (i) e roteiros de áudio para leigos, revisão por faixas até aprovar',
  phases: [
    { title: 'Fundação', detail: 'Glossário e interface/pós-processador (paralelo)' },
    { title: 'Conteúdo', detail: '(i) e roteiro de áudio por faixa de capítulos' },
    { title: 'Revisão', detail: 'Revisores leigos por faixa + storytelling/redundância; corretores por faixa' },
  ],
}

// args: { R, K, mesa }
const { R, K, mesa } = args
const MAX = 3
// Modelo por função: Opus decide a qualidade (escrita final, design, motion, técnico); Sonnet confere listas, extrai, pesquisa e testa; Haiku só roda comando.
const OPUS = { model: 'opus' }, SONNET = { model: 'sonnet' }, BARATO = { model: 'sonnet', effort: 'low' }
const W = `${R}/tools/v2`, BASE = `${R}/entregas/v1-aulas/deck/index.html`, OUT = `${R}/08-slides-v2`
const CTX = `CONTEXTO: V2 AUTOESTUDO do curso PT-BR sobre a mesa ${mesa}. Leia ANTES ${K}/references/regras-do-curso.md (seções 1–4, 8 e 9 obrigatórias; o verificador pula esta leitura).
A V1 (${R}/entregas/v1-aulas/, SOMENTE LEITURA) é o material das aulas. A V2 tem os MESMOS slides, pixel a pixel, mais os botões (i) e ▶ no layout atual, sem notas do apresentador. 3 níveis: slide → (i) para leigo com termos clicáveis do glossário → ▶ áudio mais longo e didático.
Ferramentas de referência (1ª execução, adapte): ${W}/build_v2.py, check_identico.mjs, check_ui.mjs, check_glossario.py, GLOSSARIO-GUIA.md, README.md; voz em ${W}/tts/ (no README, leia só a seção "Guia de escrita do roteiro"). Rascunhos em subpasta própria da pasta temporária. Trabalho em ${W}/ (slides.json, glossario.json, info/<id>.html, script/<id>.txt). Saída ${OUT}/. Playwright em ${R}/tools/node_modules/playwright (áudio mudo nos testes). NUNCA rode TTS/Whisper/torch nesta fase.`
const WRITE = `NÍVEL 2 = ${W}/info/<id>.html: leigo entende só lendo (o porquê, o que acontece, o que observar na mesa), 170–220 palavras, termos/siglas marcados <span class="gl" data-t="slug">…</span> na 1ª ocorrência (slugs de ${W}/glossario.json; novo termo → ${W}/glossario-extra-<faixa>.json); não repete o slide literalmente; divergências neutras completas. Só afirme o que ${R}/05-curso-final.md, a nota da V1 e o manual sustentam; slide e fonte em conflito: não resolva sozinho, relate id e frase.
NÍVEL 3 = ${W}/script/<id>.txt: roteiro FALADO, voz masculina, 280–380 palavras, professor paciente com leigo, analogias curtas (sem cenas encenadas), cita cada elemento visível na ordem em que aparece (imagem em ${R}/07-slides/redesign/telas/<id>.png; abra quando houver diagrama, painel ou tabela) e diz o que é, para que serve e o que acontece se errar; segue o GUIA DE ESCRITA de ${W}/tts/README.md (voz Gemini Puck, a dos vídeos de venda: GRAFIA NORMAL, nunca grafia fonética; registro falado "tá", "aperta", "gira", "liga"; sem letra solta; sem main/send/bus/mute/gain minúsculos; "patch" só na tela; números por extenso); texto puro. Ao fechar o lote, rode ${W}/tts/gen.sh --lint ${W}/script/ (não gasta cota) e reescreva todo roteiro que ele listar.
Quiz: (i)/áudio não entregam a resposta nem eliminam alternativa antes da tentativa; trate todas as alternativas da mesma forma. Coerência técnica entre os 3 níveis e fluxo entre slides vizinhos.`
const VERDICT = { type: 'object', properties: { approved: { type: 'boolean' }, score: { type: 'number' }, issues: { type: 'array', items: { type: 'object', properties: { ids: { type: 'string' }, problema: { type: 'string' }, correcao: { type: 'string' } }, required: ['ids', 'problema', 'correcao'] } } }, required: ['approved', 'score', 'issues'] }
const VERIFY = { type: 'object', properties: { items: { type: 'array', items: { type: 'object', properties: { n: { type: 'number' }, status: { type: 'string' }, note: { type: 'string' } }, required: ['n', 'status', 'note'] } }, regressions: { type: 'array', items: { type: 'string' } } }, required: ['items', 'regressions'] }
const CAPS = { type: 'object', properties: { cap_min: { type: 'number' }, cap_max: { type: 'number' } }, required: ['cap_min', 'cap_max'] }

phase('Fundação')
const [ui] = await parallel([
  () => agent(`${CTX}\nINTERFACE: gere ${W}/slides.json (todos os slides da V1 em ordem: id, capítulo, h/v, tipo, título, texto visível, nota da V1) e adapte ${W}/build_v2.py: lê ${BASE} sem alterar, copia lib/ e fonts/ para ${OUT}/, remove notas e plugin de notas, injeta (i) e ▶ numa posição consistente que não sobrepõe nada em nenhum slide (meça bounding boxes), popup no estilo do deck (legível >= 20px, Esc/clique fora fecha, teclado não navega com popup aberto), termos .gl abrem a definição dentro do popup, player (play/pausa, progresso discreto, para ao trocar de slide, sem autoplay) com ${OUT}/audio/<id>.m4a. Adapte ${W}/check_identico.mjs (V1 × V2 com botões ocultos, reduced-motion, todos os fragments, diferença zero). Adapte também ${W}/check_ui.mjs e ${W}/check_glossario.py (têm textos e siglas fixos da XR18). Teste com conteúdo de 3 slides. Retorne o menor e o maior número de capítulo usados nos ids (ex.: cap-0..cap-27).`, { label: 'interface + slides.json', phase: 'Fundação', schema: CAPS, ...SONNET }),
  () => agent(`${CTX}\nGLOSSÁRIO: extraia da V1 (texto visível e notas) e de ${R}/06-pdf/curso.html todos os termos técnicos, siglas e jargões; escreva ${W}/glossario.json [{slug, termo, variantes, definicao (1–3 frases simples; jargão usado também existe no glossário), exemplo_curto}] e adapte ${W}/GLOSSARIO-GUIA.md. Tecnicamente correto, sem nomes de autores. Acrescente à seção "Guia de escrita do roteiro" de ${W}/tts/README.md os termos em inglês e siglas DESTA mesa e como escrevê-los no roteiro (a voz Gemini Puck lê grafia normal; não existe dicionário de pronúncia): só edite texto, não rode o TTS.`, { label: 'glossário', phase: 'Fundação', ...SONNET }),
])
const C0 = (ui && ui.cap_min != null) ? ui.cap_min : 0, C1 = (ui && ui.cap_max != null) ? ui.cap_max : 27
const faixas = n => { const st = Math.ceil((C1 - C0 + 1) / n), out = []; for (let a = C0; a <= C1; a += st) out.push([a, Math.min(C1, a + st - 1)]); return out }
const RANGES = faixas(7)

phase('Conteúdo')
await agent(`Rode: node ${R}/tools/dump_telas.mjs ${R} ${R}/07-slides/redesign/telas. Responda só com o total de telas ou o erro.`, { label: 'imagens das telas', phase: 'Conteúdo', model: 'haiku' })
await parallel(RANGES.map(([a, b]) => () => agent(`${CTX}\n${WRITE}\nEscreva os níveis 2 e 3 de TODOS os slides dos capítulos ${a} a ${b} (use ${W}/slides.json; primeiro capítulo inclui capa/sumário/como-usar; o último inclui o encerramento; interativos e quizzes também). Antes de começar, liste info/ e script/: se a execução anterior foi interrompida, não refaça id pronto. Só crie arquivos dos seus slides e ${W}/glossario-extra-${a}-${b}.json. Termine com python3 -I ${W}/conta_lote.py ${R} ${a} ${b} sem pendência.`, { label: `conteúdo caps ${a}-${b}`, phase: 'Conteúdo', ...OPUS })))
await agent(`${CTX}\nUna ${W}/glossario-extra-*.json ao ${W}/glossario.json (dedupe, slugs padronizados e atualizados nos info/), revise definições para leigo, garanta que todo data-t existe e que todo id de slides.json tem info e script (escreva os que faltarem com as regras:\n${WRITE}).`, { label: 'unir glossário + completude', phase: 'Conteúdo', ...SONNET })

phase('Revisão')
const R6 = faixas(6)
const capOf = ids => { const m = String(ids).match(/(?:^|[\s,\[])(?:s|cap-|quiz-|fecha-|fig-)(\d+)/); return m ? +m[1] : C0 }
const reviewers = [
  ...R6.map(([a, b]) => ({ l: `leigo ${a}-${b}`, m: SONNET, p: `${CTX}\n${WRITE}\nVocê é um LEIGO total em áudio revisando os capítulos ${a} a ${b}: slide (slides.json), (i) e roteiro, em ordem. Aprove só se o (i) se entende sozinho (com o glossário) e o roteiro explica ainda melhor. Aponte jargão sem marcação, saltos lógicos, frases confusas, (i) que repete o slide, roteiro que só lê o (i), erro técnico, violação das regras. Liste ids exatos.` })),
  { l: 'storytelling/redundância A', p: `${CTX}\n${WRITE}\nLeia ${K}/references/storytelling.md e, se a skill "storytelling" existir, invoque-a com a ferramenta Skill. Revise os níveis 2 e 3 da 1ª metade do curso: fio narrativo, transições, ritmo; redundâncias (vizinhos, entre capítulos, nível 2 copiando slide, nível 3 copiando nível 2, frases-padrão repetidas) com script de similaridade. Liste ids exatos.` },
  { l: 'storytelling/redundância B', p: `${CTX}\n${WRITE}\nLeia ${K}/references/storytelling.md e, se a skill "storytelling" existir, invoque-a com a ferramenta Skill. Mesmo critério na 2ª metade do curso e no fechamento, comparando também com a 1ª metade.` },
]
let ok = false
let pend = reviewers
for (let r = 1; r <= MAX && !ok; r++) {
  const vs = (await parallel(pend.map(rv => () => agent(rv.p + (r > 1 ? '\nRODADA DE CONFERÊNCIA: confirme correções e regressões; não reprove por novidades menores.' : ''), { label: `${rv.l} r${r}`, phase: 'Revisão', schema: VERDICT, ...(rv.m || OPUS) }).then(v => v && { ...v, l: rv.l })))).filter(Boolean)
  const aprovou = rv => vs.some(v => v.l === rv.l && v.approved)
  log(`r${r}: ${vs.filter(v => v.approved).length}/${pend.length} aprovados`)
  if (pend.every(aprovou)) { ok = true; break }
  // revisor de faixa aprovado não volta; os globais continuam, porque um corretor pode ter mexido em outra faixa
  pend = pend.filter(rv => !aprovou(rv) || rv.l.startsWith('storytelling'))
  const buckets = R6.map(() => [])
  vs.flatMap(v => v.approved ? [] : v.issues).forEach((it, i) => { const c = capOf(it.ids); const k = Math.max(0, R6.findIndex(([a, b]) => c >= a && c <= b)); buckets[k].push(`${i + 1}. [${it.ids}] ${it.problema} → ${it.correcao}`) })
  await parallel(buckets.map((bk, k) => async () => {
    let todo = bk.join('\n')
    for (let f = 1; f <= 2 && todo; f++) {
      await agent(`${CTX}\n${WRITE}\nCorrija os itens da faixa ${R6[k][0]}-${R6[k][1]} (info, script; glossário só com mudança pontual):\n${todo}`, { label: `corrigir f${k + 1} r${r}.${f}`, phase: 'Revisão', ...SONNET })
      const v = await agent(`${CTX}\nVERIFICADOR: para cada item, resolvido ou pendente? Só regressões causadas pelas correções.\n${todo}`, { label: `verificar f${k + 1} r${r}.${f}`, phase: 'Revisão', schema: VERIFY, ...SONNET })
      if (!v) continue
      todo = v.items.filter(i => i.status === 'pendente').map(p => `${p.n}. ${(todo.split('\n').find(l => l.startsWith(p.n + '.')) || '').replace(/^\d+\.\s*/, '')} (verificador: ${p.note})`).concat(v.regressions.map(x => `REGRESSÃO: ${x}`)).join('\n')
    }
  }).filter((_, k) => buckets[k].length))
}
return { cap_min: C0, cap_max: C1, conteudo_aprovado: ok }
