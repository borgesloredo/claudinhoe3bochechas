export const meta = {
  name: 'curso-fase4b-v2-audio-final',
  description: 'Curso de mesa de som, fase 4b: QA dos áudios pelos relatórios (pronúncia, sotaque BR, volume), montagem da V2, aprovação final e zip',
  phases: [
    { title: 'Áudio', detail: 'Revisores por faixa leem os relatórios; corretores regeram pela trava global' },
    { title: 'Montagem e aprovação', detail: 'Build, slides idênticos, Chrome, Safari, design, objetivo' },
  ],
}

// args: { R, K, mesa, cap_min, cap_max }  (vêm do resultado da fase 4a)
const { R, K, mesa, cap_min, cap_max } = args
const MAX = 3
// Modelo por função: Opus decide a qualidade (escrita final, design, motion, técnico); Sonnet confere listas, extrai, pesquisa e testa; Haiku só roda comando.
const OPUS = { model: 'opus' }, SONNET = { model: 'sonnet' }, BARATO = { model: 'sonnet', effort: 'low' }
const W = `${R}/tools/v2`, OUT = `${R}/08-slides-v2`, ZIP = `${R}/entregas/v2-autoestudo.zip`
const CTX = `CONTEXTO: V2 autoestudo do curso sobre a mesa ${mesa}. Leia ${K}/references/regras-do-curso.md (seções 8 e 9). Slides da V2 = V1 pixel a pixel + (i) e ▶. Trabalho em ${W}/ (slides.json, info/, script/, glossario.json, build_v2.py, check_identico.mjs); áudios em ${OUT}/audio/<id>.m4a; V1 somente leitura em ${R}/entregas/v1-aulas/ (SHA256SUMS).
REGRA DE MEMÓRIA (o Mac de 16 GB travou com processos pesados em paralelo): NUNCA rode Whisper, TTS ou torch diretamente. Relatórios prontos em ${W}/qa-out/ (whisper/<id>.txt; sotaque-*.txt com p(pt_br) por janela; loudness-*.txt). Regerar um áudio: ${W}/heavy.sh ${W}/tts/gen.sh ${W}/script/<id>.txt ${OUT}/audio/<id>.m4a. Reavaliar: ${W}/qa_batch.sh <id> [<id>...]. Playwright pode rodar (áudio mudo: muted=true; Chromium --mute-audio).`
const VERDICT = { type: 'object', properties: { approved: { type: 'boolean' }, score: { type: 'number' }, issues: { type: 'array', items: { type: 'object', properties: { ids: { type: 'string' }, problema: { type: 'string' }, correcao: { type: 'string' } }, required: ['ids', 'problema', 'correcao'] } } }, required: ['approved', 'score', 'issues'] }
const VERIFY = { type: 'object', properties: { items: { type: 'array', items: { type: 'object', properties: { n: { type: 'number' }, status: { type: 'string' }, note: { type: 'string' } }, required: ['n', 'status', 'note'] } }, regressions: { type: 'array', items: { type: 'string' } } }, required: ['items', 'regressions'] }
const R6 = []
const s6 = Math.ceil((cap_max - cap_min + 1) / 6)
for (let a = cap_min; a <= cap_max; a += s6) R6.push([a, Math.min(cap_max, a + s6 - 1)])
const capOf = ids => { const m = String(ids).match(/(?:^|[\s,\[])(?:s|cap-|quiz-|fecha-|fig-)(\d+)/); return m ? +m[1] : cap_min }

async function loop(name, phaseName, reviewers, fixPrompt, porFaixa) {
  let pend = reviewers
  for (let r = 1; r <= MAX; r++) {
    const vs = (await parallel(pend.map(rv => () => agent(rv.p + (r > 1 ? '\nRODADA DE CONFERÊNCIA: confirme correções e regressões; não reprove por novidades menores.' : ''), { label: `${rv.l} r${r}`, phase: phaseName, schema: VERDICT, ...(rv.m || OPUS) }).then(v => v && { ...v, l: rv.l })))).filter(Boolean)
    const aprovou = rv => vs.some(v => v.l === rv.l && v.approved)
    log(`${name} r${r}: ${vs.filter(v => v.approved).length}/${pend.length} aprovados`)
    if (pend.every(aprovou)) return { approved: true, r }
    // por faixa, aprovado não volta; na montagem todos voltam, porque um conserto pode quebrar outra checagem
    if (porFaixa) pend = pend.filter(rv => !aprovou(rv))
    const items = vs.flatMap(v => v.approved ? [] : v.issues)
    const buckets = porFaixa ? R6.map(() => []) : [[]]
    items.forEach((it, i) => { const k = porFaixa ? Math.max(0, R6.findIndex(([a, b]) => capOf(it.ids) >= a && capOf(it.ids) <= b)) : 0; buckets[k].push(`${i + 1}. [${it.ids}] ${it.problema} → ${it.correcao}`) })
    await parallel(buckets.map((bk, k) => async () => {
      let todo = bk.join('\n')
      for (let f = 1; f <= 2 && todo; f++) {
        await agent(`${fixPrompt}\nCHECKLIST:\n${todo}`, { label: `${name} corrigir ${k + 1} r${r}.${f}`, phase: phaseName, ...SONNET })
        const v = await agent(`${CTX}\nVERIFICADOR: para cada item, resolvido ou pendente? Só regressões causadas pelas correções.\n${todo}`, { label: `${name} verificar ${k + 1} r${r}.${f}`, phase: phaseName, schema: VERIFY, ...SONNET })
        if (!v) continue
        todo = v.items.filter(i => i.status === 'pendente').map(p => `${p.n}. ${(todo.split('\n').find(l => l.startsWith(p.n + '.')) || '').replace(/^\d+\.\s*/, '')} (verificador: ${p.note})`).concat(v.regressions.map(x => `REGRESSÃO: ${x}`)).join('\n')
      }
    }).filter((_, k) => buckets[k].length))
  }
  return { approved: false }
}

phase('Áudio')
const audio = await loop('áudio', 'Áudio', R6.map(([a, b]) => ({ m: BARATO, l: `QA áudio ${a}-${b}`, p: `${CTX}\nREVISOR DE ÁUDIO dos capítulos ${a} a ${b}: compare ${W}/qa-out/whisper/<id>.txt com ${W}/script/<id>.txt (use ${W}/tts/qa/wer.py ou difflib; ignore números/siglas que o Whisper escreve com algarismos) — termos mal pronunciados, trechos faltando/cortados; no sotaque-*.txt mais recente de cada áudio, sotaque do BRASIL obrigatório, medido assim com a voz Gemini: média p(pt_br) >= 0,80 e a maioria das janelas acima de 0,5; janela isolada perto de 0 é pausa, sigla ou termo em inglês e NÃO justifica regravar (no curso XENYX, 15/11/2026, regravar por janela isolada esgotou a cota do dia e o classificador oscilou de 25/26 para 20/24 no mesmo áudio). Só peça regravação por erro de fala confirmado no Whisper e repetido, ou por média abaixo de 0,80; volume perto de -16 LUFS; nenhum áudio faltando. Para cada problema: ids, trecho e correção (grafia normal no roteiro, seguindo o guia da voz Gemini em ${W}/tts/README.md; leia também ${W}/qa-out/gemini-conferir.txt).` })),
  `${CTX}\nVocê CORRIGE áudios: ajuste o texto em ${W}/script/<id>.txt (sem mudar o sentido; grafia normal, registro falado do guia), rode ${W}/tts/gen.sh --lint ${W}/script/ e regere TODOS os ids corrigidos numa chamada só: cd ${W} && ./heavy.sh tts/gen.sh script/ ../../08-slides-v2/audio/ (refaz só os .m4a mais velhos que o roteiro, 3 por pedido; a cota Gemini é de ~50 pedidos/dia, nunca gere id por id). Depois confirme com qa_batch.sh <ids>. Acrescente ao guia em ${W}/tts/README.md o que a voz errou de novo.`, true)

phase('Montagem e aprovação')
await agent(`${CTX}\nMonte a V2 com ${W}/build_v2.py; rode ${W}/check_identico.mjs em TODOS os slides; gere contact sheets com os botões e prints do popup e de um termo do glossário em ${R}/07-slides/redesign/v2-shots/; crie ${OUT}/LEIA-ME.txt (como abrir, botões (i) e ▶, teclas, total de telas) e ${ZIP} com a pasta ${OUT} (sem arquivos de trabalho).`, { label: 'montar V2', phase: 'Montagem e aprovação', ...BARATO })
const final = await loop('final', 'Montagem e aprovação', [
  { m: BARATO, l: 'idêntico + V1 intacta', p: `${CTX}\nREVISOR: check_identico.mjs (todos os slides iguais à V1 com botões ocultos); cd ${R}/entregas/v1-aulas && shasum -a 256 -c SHA256SUMS; o zip ${ZIP} extraído numa pasta vazia abre offline.` },
  { l: 'funcional Chromium', m: SONNET, p: `${CTX}\nREVISOR FUNCIONAL no Chromium, offline, em TODOS os slides: (i) abre o popup certo, termo .gl abre a definição, Esc fecha, ▶ toca o áudio certo (currentTime avança), pausa, para ao trocar de slide (troque de slide de verdade: Reveal.next pode só avançar fragment), sem autoplay; 0 erros; 0 requisições externas; sem notas.` },
  { l: 'funcional WebKit', m: SONNET, p: `${CTX}\nMesmo critério no WebKit (Safari), offline, com áudio mudo.` },
  { l: 'design', m: SONNET, p: `${CTX}\nSkills: ~/.claude/skills/frontend-slides/SKILL.md, motion-design. REVISOR DE DESIGN: botões integrados ao layout do deck, consistentes, alvo >= 40px, sem sobrepor nada; popup legível (>= 20px), hierarquia, rolagem, glossário claro; hover/foco/tocando visíveis.` },
  { l: 'objetivo', p: `${CTX}\nVERIFICADOR DO OBJETIVO: node ${R}/tools/check_padrao.mjs ${R} deve sair OK (contador, fundo, setas, progresso, sumário, telas obrigatórias, medianas de roteiro e explicação); 3 níveis em todos os slides com progressão de profundidade; leigo entende; termos clicáveis; voz masculina pt-BR gratuita com licença comercial documentada (${W}/tts/README.md); slides inalterados; V1 intacta; regras do curso. Leia ao menos 1 (i) e 1 roteiro por capítulo; áudios pelos relatórios.` },
], `${CTX}\nVocê CORRIGE a V2 (build, UI, info, script, glossário; áudios só pelo heavy.sh + qa_batch.sh). Nunca altere a V1 nem a aparência dos slides. Ao final, rode build_v2.py, check_identico.mjs e refaça o zip.`, false)
return { audio, final, zip: ZIP }
