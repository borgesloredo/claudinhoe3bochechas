export const meta = {
  name: 'videos-de-venda',
  description: 'Vídeos de venda HyperFrames (N variantes), versão enxuta: Opus só cria (kit, roteiro, build); Sonnet revisa e corrige; Haiku entrega; checagens objetivas por script',
  phases: [
    { title: 'Preparo', detail: 'ficha (Sonnet) + kit visual (Opus); pesquisa e música copiadas do compartilhado' },
    { title: 'Diferenciação', detail: 'mapa curto de hooks/visuais/CTA por variante (Sonnet)' },
    { title: 'Variantes', detail: 'roteiro (Opus + lint) -> revisor (Sonnet) -> build (Opus + checar.py) -> revisor visual (Sonnet, folhas de contato) -> fix (Sonnet)' },
    { title: 'Entrega', detail: 'revisão cruzada + ENTREGA.md + cópia final (Haiku)' },
  ],
}

// args: { base, produto, fontes[], design, fonts, plugin, formato, audio, duracao, cta, regras_extra, variantes[{id, abordagem}],
//         compartilhado? (pasta com tools/, musica/, voz/, HF-RESUMO.md, REGRAS-AGENTE.md, pesquisa-vendas.md), destino? (pasta final dos MP4),
//         reaproveitar? (true = retoma: pesquisa, ficha, kit e mapa já no disco; <id>/roteiro-workflow.json = último roteiro + revisão) }
// Modelos: sem `model` = herda o da sessão (Opus) -> só nas etapas criativas. Revisão/correção = Sonnet; burocracia = Haiku.
const A = args
const BASE = A.base
const P = A.plugin
const G = A.compartilhado || '/Users/SEU-USUARIO/SEU-PROJETO/geral/videos-de-venda-compartilhado'
const CLI = `node "${P}/skills/hyperframes/scripts/plugin-cli.mjs"`
const [W, H] = A.formato === '1:1' ? [1080, 1080] : A.formato === '16:9' ? [1920, 1080] : [1080, 1920]
// LS9 (09/11): 5 rodadas de roteiro não subiram a nota (revisor achava problema novo a cada rodada). Agora: 1 revisão + no máx. 1 correção conferida.
const NOTA_ALVO = 9, NOTA_MIN = 8.5, ROD_ROTEIRO = 2, FIX_MAX = 2, NOTA_FIX2 = 8.3
const DUR = (A.duracao || '30-60').replace(/\s/g, '')
const SONNET = { model: 'sonnet', effort: 'medium' }
const HAIKU = { model: 'haiku', effort: 'low' }
const narrado = (v) => A.audio !== 'musica' && /narra/i.test(v.abordagem)

// Regras: um arquivo curto, por papel (REGRAS-AGENTE.md). O prompt só traz o que muda por produto.
const RULES = (papel) => `REGRAS: leia ${G}/REGRAS-AGENTE.md, seções "Todos" e "${papel}" (<G> = ${G}). Produto: ${A.produto}. ${A.formato} ${W}x${H}, ${DUR} s, CTA "${A.cta}". Áudio: ${A.audio}. Kit visual da mesa: ${BASE}/kit/ (design: ${A.design}).
${A.regras_extra || ''}`

phase('Preparo')
const prep = A.reaproveitar ? ['reaproveitado', 'reaproveitado'] : await parallel([
  () => agent(`1) mkdir -p "${BASE}/kit/musica"; cp -n "${G}/pesquisa-vendas.md" "${BASE}/"; cp -n "${G}/musica/calma.m4a" "${G}/musica/energica.m4a" "${G}/musica/LICENCAS.md" "${BASE}/kit/musica/".
2) Monte ${BASE}/ficha-produto.md (máx. 10 mil caracteres). Fontes: ${A.fontes.join(', ')}. Arquivo grande: grep/head, nunca inteiro. Só fatos verificáveis, cada um com o arquivo de origem:
- nome, conteúdo (capítulos/módulos), números reais (slides, páginas, telas, quizzes), entregáveis e formatos;
- o que o cliente aprende, dores do público, features diferenciais (marque as "em produção");
- 8–12 "momentos visuais" do material (arquivo + seletor ou página).
${RULES('Todos')}
Retorne 10 linhas.`, { label: 'ficha-produto', phase: 'Preparo', ...SONNET }),
  () => agent(`Crie o kit visual em ${BASE}/kit/ (pasta de assets, NÃO projeto hyperframes). Leia ${G}/HF-RESUMO.md.
1) kit/fonts/ (copie de ${A.fonts}) e kit/tema.css: tokens de ${A.design}, @font-face, fundo, tipografia ${W}x${H} (display >= 110 px, texto >= 56 px, kicker >= 36 px), classe .safe. Sem animação CSS.
2) kit/componentes.html: snippets estáticos HTML/SVG do HARDWARE da mesa e do produto (mock de tela/slide, teclas, faders, knobs, LEDs, visor, selo, botão de CTA), tirados de ${A.design}. Leia o CSS da LP por grep/sed nos blocos do console, não o arquivo inteiro.
3) kit/img/: 6–10 recortes reais do produto (capa do PDF, telas do autoestudo, slides) prontos para usar, sem texto proibido visível. Grave kit/img/INDICE.md (arquivo | tamanho px | o que mostra | texto legível) e kit/img/folha.png (ffmpeg tile de todas), para o construtor escolher sem abrir cada imagem.
4) kit/LEIAME.md (máx. 4 mil caracteres): id/classe de cada peça e quando usar.
Confira com uma captura de componentes.html (respeite a regra de navegador). Retorne a lista do que criou.
${RULES('Construtor / corretor (build, fix)')}`, { label: 'kit-visual', phase: 'Preparo' }),
])
log('Preparo: ' + prep.map(x => x ? 'ok' : 'FALHOU').join(', '))
if (prep.some(x => !x)) return { erro: 'Preparo falhou (ficha/kit). Corrija e retome com resumeFromRunId.', prep }

phase('Diferenciação')
const MAPA_SCHEMA = { type: 'object', properties: { variantes: { type: 'array', items: { type: 'object', properties: {
  id: { type: 'string' }, hook: { type: 'string' }, arco: { type: 'string' }, momentos_visuais: { type: 'array', items: { type: 'string' } },
  imagem_final: { type: 'string' }, musica: { type: 'string', enum: ['calma', 'energica', 'nenhuma'] }, proibido: { type: 'array', items: { type: 'string' } } },
  required: ['id', 'hook', 'arco', 'momentos_visuais', 'imagem_final', 'musica', 'proibido'] } } }, required: ['variantes'] }
const mapa = A.reaproveitar
  ? await agent(`Leia ${BASE}/mapa-variantes.md (mapa já aprovado) e devolva-o no schema, SEM mudar o sentido; encurte cada campo ao essencial. Variantes: ${JSON.stringify(A.variantes)}.`, { label: 'mapa-reaproveitado', phase: 'Diferenciação', schema: MAPA_SCHEMA, ...HAIKU })
  : await agent(`Leia ${BASE}/ficha-produto.md (e ${BASE}/pesquisa-vendas.md só a parte das abordagens). Monte o MAPA DE DIFERENCIAÇÃO das variantes ${JSON.stringify(A.variantes)}, para cada uma ser escrita em paralelo SEM repetir as outras.
Por variante: hook (frase + imagem, <= 40 palavras), arco (<= 120 palavras), 3–5 momentos visuais EXCLUSIVOS, imagem final do CTA (diferente entre variantes), música (calma/energica; narrado = calma) e "proibido" (hooks, frases, números, imagens e moldes de CTA das outras, <= 8 itens curtos). Números e imagens do produto: cada um em no máximo 2 variantes.
Grave ${BASE}/mapa-variantes.md (máx. 6 mil caracteres). ${RULES('Roteirista / revisor de roteiro')}`, { label: 'mapa', phase: 'Diferenciação', schema: MAPA_SCHEMA, ...SONNET })
if (!mapa) return { erro: 'Mapa de diferenciação falhou. Retome com resumeFromRunId.' }

phase('Variantes')
const SCRIPT = { type: 'object', properties: { id: { type: 'string' }, nome: { type: 'string' }, duracao_s: { type: 'number' },
  cenas: { type: 'array', items: { type: 'object', properties: { t_ini: { type: 'number' }, t_fim: { type: 'number' }, texto_tela: { type: 'string' }, fala: { type: 'string' }, visual: { type: 'string' }, motion: { type: 'string' } }, required: ['t_ini', 't_fim', 'texto_tela', 'visual', 'motion'] } } },
  required: ['id', 'nome', 'duracao_s', 'cenas'] }
const REV = { type: 'object', properties: { nota: { type: 'number' }, problemas: { type: 'array', items: { type: 'string' } } }, required: ['nota', 'problemas'] }
const VIS = { type: 'object', properties: { nota: { type: 'number' }, legibilidade: { type: 'number' }, motion: { type: 'number' }, ritmo: { type: 'number' }, conformidade: { type: 'number' }, storytelling: { type: 'number' }, problemas: { type: 'array', items: { type: 'string' } } }, required: ['nota', 'problemas'] }

const linha = (v) => mapa.variantes.find(m => m.id === v.id) || {}
const lint = (v) => `python3 "${G}/tools/lint-roteiro.py" "${BASE}/${v.id}/roteiro.json" --dur ${DUR}${narrado(v) ? ' --narrado' : ''}`

async function roteiro(v) {
  const m = linha(v)
  let cur = null, rev = null
  for (let r = 1; r <= ROD_ROTEIRO; r++) {
    const base = r === 1
      ? `Parta do molde da abordagem em ${G}/MOLDES-ROTEIRO.md (seção "Em todas" + a sua). Leia ${BASE}/ficha-produto.md; ${BASE}/pesquisa-vendas.md só se o molde não bastar.
${A.reaproveitar ? `PONTO DE PARTIDA: ${BASE}/${v.id}/roteiro-workflow.json (roteiro + revisao de execução interrompida). Nota >= ${NOTA_MIN}: mantenha; senão corrija todos os problemas da revisao.\n` : ''}O roteiro apresenta a ideia, explica o produto, mostra benefícios, features e o que ele faz de mais legal. Hook nos 3 s iniciais, cenas de 1,5–4 s, visual e motion com as peças de ${BASE}/kit/LEIAME.md.`
      : `CORRIJA TODOS os pontos do revisor e mantenha o que está bom. Não releia a ficha inteira: grep só para conferir um fato.
REVISOR: ${JSON.stringify(rev)}
VERSÃO ATUAL: ${JSON.stringify(cur)}`
    cur = await agent(`Roteirista sênior de anúncios. Variante "${v.id}" (${v.abordagem})${narrado(v) ? ', NARRADA (preencha "fala" em cada cena falada)' : ', só música (sem "fala")'}.
MAPA desta variante (obrigatório, inclusive "proibido"): ${JSON.stringify(m)}
${base}
Grave o JSON em ${BASE}/${v.id}/roteiro.json (mkdir -p) e rode: ${lint(v)}. Corrija até zero FALHA. Retorne o mesmo JSON.
${RULES('Roteirista / revisor de roteiro')}`, { label: `roteiro-${v.id}-r${r}`, phase: 'Variantes', schema: SCRIPT })
    if (!cur) return { cur: null, rev: { nota: 0, problemas: ['roteirista falhou'] } }
    const prev = rev
    rev = await agent(`${prev ? `RODADA DE CONFERÊNCIA. Problemas da rodada anterior: ${JSON.stringify(prev.problemas)}. Confira só se cada um foi resolvido. Problema NOVO só entra se for fato errado ou FALHA de regra; não rebaixe a nota por gosto.\n` : ''}Revisor exigente de roteiro de anúncio. Rode ${lint(v)} (FALHA = conformidade < 9). Nota 0–10 em hook, storytelling, clareza, benefícios/features, CTA, sem redundância e conformidade; nota = média; conformidade < 9 limita a nota a 6. Liste no máximo 5 problemas, só os que mudam a percepção do comprador, cada um com cena e correção. Confira fatos com grep em ${BASE}/ficha-produto.md. Exclusividade: ${JSON.stringify({ proibido: m.proibido })}.
${RULES('Roteirista / revisor de roteiro')}
VARIANTE "${v.id}" (${BASE}/${v.id}/roteiro.json): ${JSON.stringify(cur)}`, { label: `rev-roteiro-${v.id}-r${r}`, phase: 'Variantes', schema: REV, ...SONNET })
    if (!rev) rev = { nota: 0, problemas: ['revisor falhou'] }
    log(`${v.id} roteiro r${r}: ${rev.nota}`)
    if (rev.nota >= NOTA_MIN) break
  }
  return { cur, rev }
}

const checar = (v, r) => `cd "${BASE}/${v.id}" && python3 "${G}/tools/checar.py" renders/${v.id}.mp4 --html index.html --dur ${DUR} --folhas rev-r${r}/folhas`

const reviewVideo = (v, r) => agent(`Revisor final de anúncio. Vídeo "${v.id}": ${BASE}/${v.id}/renders/${v.id}.mp4. Roteiro final: ${BASE}/${v.id}/ROTEIRO-FINAL.md.
1) Rode: ${checar(v, r)}  (FALHA = conformidade < 9).
2) Olhe TODAS as folhas de rev-r${r}/folhas com Read. Quadro grande (ffmpeg -ss T -frames:v 1 -vf scale=540:-1) só onde suspeitar, no máximo 6.
Nota 0–10 em legibilidade, motion, ritmo, conformidade, storytelling; nota = média; conformidade < 9 limita a 6. Problemas: só o que muda a percepção do comprador, com tempo e correção concreta.
Grave ${BASE}/${v.id}/rev-r${r}.md (máx. 25 linhas). ${RULES('Revisor de vídeo')}`, { label: `rev-video-${v.id}-r${r}`, phase: 'Variantes', schema: VIS, ...SONNET })

const resultados = await pipeline(A.variantes,
  (v) => roteiro(v),
  async (rot, v) => {
    if (!rot || !rot.cur) return { id: v.id, nota: 0, problemas: ['sem roteiro'] }
    const m = linha(v)
    const built = await agent(`Construa o vídeo "${v.id}" em HyperFrames, ${W}x${H}. Leia ${G}/HF-RESUMO.md (substitui as skills do plugin; CLI = ${CLI}), ${BASE}/kit/LEIAME.md e ${BASE}/kit/img/INDICE.md.
${A.reaproveitar ? `EXECUÇÃO RETOMADA: ${BASE}/${v.id}/ pode ter index.html, hyperframes.json e voz/. Não apague; reaproveite o que bate com o roteiro e refaça só o que mudou.\n` : ''}1) Projeto em ${BASE}/${v.id} (init só se não houver hyperframes.json). Copie o kit para assets/kit/ (tema.css, fonts/, só as imagens que usar). Grave o roteiro abaixo em roteiro.json.
${narrado(v) ? `2) Voz: cada "fala" do roteiro vira voz/cNN.txt; gere TODAS numa chamada com ${G}/voz/gen_gemini.sh (veja REGRAS-AGENTE). Meça cada fala e ajuste os tempos das cenas à voz.\n` : '2) Sem narração: texto animado legível sem som.\n'}3) Siga o roteiro (texto, visual, motion). Escreva só cenas/sNN.html + cenas/sNN.js, fixo.* e estilo.css e monte com: python3 ${G}/tools/montar.py . --musica ${m.musica && m.musica !== 'nenhuma' ? m.musica : 'calma'}${narrado(v) ? ' --voz' : ''}. Nada de gerador próprio nem mixagem própria. No máximo 6 Read de imagem no build inteiro. kit/componentes.html: copie só os trechos INÍCIO/FIM das peças que usar (grep/sed), nunca o arquivo inteiro.
4) lint + check até zero erro; render em renders/${v.id}.mp4; depois ${checar(v, 0)} e corrija toda FALHA e todo AVISO de faixa vazia. Olhe as folhas e corrija o que estiver quebrado.
5) O montar.py grava ROTEIRO-FINAL.md; acrescente só observações que o revisor precise.
Retorne 5 linhas: duração, resultado do checar, pendências.
${RULES('Construtor / corretor (build, fix)')}
ROTEIRO: ${JSON.stringify(rot.cur)}`, { label: `build-${v.id}`, phase: 'Variantes' })
    if (built && /PENDENTE-VOZ|cota do dia acabou/i.test(built)) return { id: v.id, nota: 0, nota_roteiro: rot.rev.nota, problemas: ['voz pendente: ' + BASE + '/' + v.id + '/PENDENTE-VOZ.md'] }
    let rev = await reviewVideo(v, 1)
    for (let r = 2; r <= FIX_MAX + 1 && rev && rev.nota < NOTA_ALVO; r++) {
      if (r > 2 && rev.nota >= NOTA_FIX2) break
      await agent(`Corrija o vídeo HyperFrames "${v.id}" em ${BASE}/${v.id} conforme o parecer. Mexa SÓ nos pontos citados, nas peças cenas/sNN.*, fixo.*, estilo.css ou ajustes.json, e rode o tools/montar.py de novo (vídeo antigo sem cenas/: edite o index.html direto). Não reescreva o resto. Leia ${G}/HF-RESUMO.md só se precisar de um detalhe.
Antes de renderizar: cp renders/${v.id}.mp4 renders/${v.id}-r${r - 1}.mp4 (backup). lint + check, render em renders/${v.id}.mp4, depois ${checar(v, 0)} com zero FALHA. Retorne 3 linhas.
${RULES('Construtor / corretor (build, fix)')}
PARECER: ${JSON.stringify(rev)}`, { label: `fix-${v.id}-r${r}`, phase: 'Variantes', ...SONNET })
      rev = await reviewVideo(v, r)
    }
    log(`${v.id} vídeo: nota ${rev && rev.nota}`)
    return { id: v.id, nota_roteiro: rot.rev.nota, ...rev }
  })

phase('Entrega')
const ids = A.variantes.map(v => v.id).join(', ')
const cruzada = await agent(`Revisor cruzado: leia ${BASE}/*/ROTEIRO-FINAL.md das variantes ${ids}. Aponte redundâncias ENTRE os vídeos (hooks, frases, números, imagens, CTAs repetidos) e diga qual usar em cada lugar (topo de funil, remarketing, página do Mercado Livre). Até 12 linhas.`, { label: 'revisor-cruzado', phase: 'Entrega', ...SONNET })
await agent(`1) mkdir -p ${BASE}/entregas-final${A.destino ? ` "${A.destino}"` : ''}; copie ${BASE}/<id>/renders/<id>.mp4 para ${BASE}/entregas-final/${A.destino ? ` e para "${A.destino}"/` : ''} (ids: ${ids}). Não sobrescreva arquivo diferente sem antes copiar para <nome>-anterior.mp4.
2) Para cada id rode python3 "${G}/tools/checar.py" ${BASE}/entregas-final/<id>.mp4 --dur ${DUR} e anote o resultado.
3) Escreva ${BASE}/ENTREGA.md em PT-BR simples para dono de produto não técnico: por vídeo, abordagem, duração, nota, uso sugerido, resumo de 2 linhas do ROTEIRO-FINAL.md e resultado do checar. Inclua música e licença (${BASE}/kit/musica/LICENCAS.md), backups (renders/*-rN.mp4), a revisão cruzada e pendências. Não invente nada.
Notas: ${JSON.stringify(resultados.map(x => x && { id: x.id, nota: x.nota, roteiro: x.nota_roteiro }))}
Revisão cruzada: ${cruzada}`, { label: 'entrega', phase: 'Entrega', ...HAIKU })
return { resultados, cruzada }
