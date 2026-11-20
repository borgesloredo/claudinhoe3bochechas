export const meta = {
  name: 'lp-de-venda',
  description: 'Página de venda interativa + checkout para um livro/ebook/curso digital: estudo, copy, visual, motion, checkout e QA com avaliadores por etapa (nota mínima 8,5), versão enxuta',
  phases: [
    { title: 'Estudo', detail: 'conteúdo, identidade visual e técnicas de venda em paralelo' },
    { title: 'Copy', detail: 'textos da página e do checkout' },
    { title: 'Visual', detail: 'index.html completo com a identidade escolhida' },
    { title: 'Motion e Checkout', detail: 'animações/widgets e checkout em paralelo' },
    { title: 'QA final', detail: 'auditoria da experiência inteira (bloqueante)' },
  ],
}

// args: {
//   base: '/abs/<projeto>/curso-<mesa>/lp',            saída (index.html, checkout.html, img/, docs/)
//   produto: { nome, subtitulo, formato, preco, autor, garantia_dias, publico, entrega, extras },
//   fontes: { conteudo: '/abs/livro.pdf', interativo: '/abs/edicao.html' | '', outros: ['/abs/descricao.txt', ...] },
//   imagens: '/abs/pasta-com-prints' | '',
//   layout: 'padrao' | 'identidade' | 'template' | 'referencia',  layout_ref: '/abs/lp-anterior/index.html' ou URL ou descrição,
//   padrao: '/abs/padrao-xr18.md' | '',   padrão de qualidade (default: padrao-xr18.md desta skill), vale em todo layout
//   checkout: { modo: 'mp' | 'externo' | 'demo', url_externa: '', api_base: '', backend: '/abs/ml-server/supabase' },
//   regras_extra: '- regras do projeto e da memória',
//   venda_ref: '/abs/lp-anterior/docs/03-tecnicas-venda.md' | '',  já validado: pula a pesquisa de venda
//   autor_fatos: '/abs/perfil-expert.md' | '',   fatos do autor que a página pode usar
// }
const A = args
const B = A.base, D = B + '/docs'
const P = A.produto
const MIN = 8.5
// Economia de token: estudo sem revisão (é material interno e não convergia), revisões com no máximo 2-3 rodadas.
// Motion tem 3 rodadas: é a etapa que mais pesa no padrão XR18 e terminou em 8,2 com 2 rodadas na 01V96.
const ROUNDS = { estudo: 0, copy: 2, visual: 2, motion: 3, checkout: 2, qa: 3 }
const V = A.venda_ref || `${D}/03-tecnicas-venda.md`
// Padrão de qualidade aprovado em 05/11/2026: a LP XR18 é o 100%; botões e ícones seguem o hardware de cada produto.
const PADRAO = A.padrao || '/Users/SEU-USUARIO/.claude/skills/lp-de-venda/padrao-xr18.md'
const STD = `
PADRÃO DE QUALIDADE (obrigatório, vale para toda LP): leia ${PADRAO} INTEIRO antes de começar. A LP da XR18 é o 100% em motion, gráficos, animação e acabamento; a LP da 01V96 é o mesmo padrão aplicado a outra mesa (os caminhos estão no arquivo). Cada seção da página nova precisa ter pelo menos o motion e o acabamento da seção equivalente da XR18. Só o estilo de botões, ícones e painéis muda: eles imitam o hardware deste produto (seção "Hardware" de ${D}/02-identidade.md).`

const FACTS = `
FATOS DO PRODUTO (decididos pelo dono; nunca contradiga, nunca invente além destes e das fontes):
- Produto: ${P.nome}${P.subtitulo ? ' — ' + P.subtitulo : ''}. Formato: ${P.formato}.
- Autor/vendedor exibido: ${P.autor}. ${A.autor_fatos ? `Fatos do autor: SÓ os de ${A.autor_fatos} (sem marca [CONFIRMAR]).` : 'NÃO invente credenciais, anos de experiência, nº de alunos.'} Nunca invente depoimentos, avaliações nem números de venda. Linha que precisa de confirmação do dono leva o comentário HTML <!-- CONFIRMAR: ... -->.
- Preço: R$ ${P.preco}, pagamento único. ${A.checkout.modo === 'externo' ? 'Pagamento na plataforma de checkout externa.' : 'Mercado Pago: Pix (instantâneo) ou cartão de crédito (parcelas com juros pagos pelo comprador). Sem boleto.'}
- Entrega: ${P.entrega}
- Garantia: ${P.garantia_dias} dias, em destaque (CDC art. 49): pediu em ${P.garantia_dias} dias, recebe tudo de volta.
- Sem aulas ao vivo, sem certificado, sem comunidade, sem suporte além de e-mail, salvo se as fontes disserem o contrário.
- Público: ${P.publico}
${P.extras || ''}
- Fontes do produto: ${[A.fontes.conteudo, A.fontes.interativo, ...(A.fontes.outros || [])].filter(Boolean).join(', ')}.
${A.imagens ? `- Prints reais do produto que a página pode usar: ${A.imagens} (copie os usados para ${B}/img/).` : ''}
${A.regras_extra || ''}`

const LAYOUT = {
  padrao: `LAYOUT: padrão da casa (${PADRAO}). Estrutura, ordem das seções, widgets e motion da LP XR18, aplicados a este produto. Cores e fontes da identidade dele (${D}/02-identidade.md). Botões, ícones e painéis imitando o hardware dele. Parta do código da LP 01V96 (caminho no padrão) e troque teclas, modos, valores e textos pelos deste produto. Não copie textos nem fatos técnicos de outra LP.`,
  identidade: `LAYOUT: siga a identidade visual do PRÓPRIO produto (cores, fontes, diagramas e linguagem de movimento extraídos em ${D}/02-identidade.md). A página deve parecer irmã do produto.`,
  template: `LAYOUT: use ${A.layout_ref} como base de estrutura (ordem das seções, componentes, widgets, sticky CTA, padrão do checkout). Troque conteúdo, prints e widgets pelos deste produto e ajuste a cor de destaque à identidade dele (${D}/02-identidade.md). Não copie textos nem fatos do produto antigo.`,
  referencia: `LAYOUT: siga a referência do dono: ${A.layout_ref}. Combine com a identidade do produto (${D}/02-identidade.md) só onde a referência não decidir.`,
}[A.layout]

const HOSTING = `
HOSPEDAGEM (o link temporário é um Artifact do claude.ai; depois vai para o domínio do dono):
- ${B}/index.html é a página do Artifact: a plataforma embrulha num esqueleto doctype/head/body, então index.html NÃO tem <!doctype>, <html>, <head> nem <body>. No topo: <title>, <meta name="claude:viewport-fit-sides" content="cover"> e <style>.
- ${A.checkout.modo === 'externo' ? `Todos os CTAs apontam para ${A.checkout.url_externa} (link externo, target="_blank" rel="noopener"). Não existe checkout.html.` : `${B}/checkout.html é um documento completo (tem <!doctype html>, charset, viewport, title e estilos próprios). CTAs usam <a href="checkout.html">.`}
- Imagens em ${B}/img/ com caminho RELATIVO (img/x.webp). Converta prints grandes para .webp (cwebp ou sips) e mantenha cada um abaixo de ~150 KB.
- Scripts externos SÓ de cdnjs.cloudflare.com (preferido), cdn.jsdelivr.net/npm ou unpkg.com, versão exata (ex.: https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js e .../ScrollTrigger.min.js). Folhas de estilo SÓ de fonts.googleapis.com. Todo o resto inline. fetch/XHR para outros domínios não funciona dentro do Artifact.
- Sem alert/confirm/prompt, sem window.print, sem iframes de outros sites.
- Mobile first: 375–400 px sem rolagem horizontal; respiro lateral padding-left: max(16px, env(safe-area-inset-left, 0px)) e o mesmo à direita. prefers-reduced-motion respeitado. Foco de teclado visível. Conteúdo visível em repouso: nada fica em opacity:0 esperando observer se o JS falhar.
- Cores como tokens CSS em :root. Se o visual for de tema único, defina o fundo do body e todas as cores, mais color-scheme.
- PARA TESTAR NO NAVEGADOR (obrigatório; testar o index.html cru engana: sem viewport o celular renderiza em 980 px): crie ${B}/.preview.html = '<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"></head><body>' + conteúdo do index.html + '</body></html>', sirva ${B} com python3 -m http.server 8765 em segundo plano (reaproveite se a porta já estiver em uso) e abra http://localhost:8765/.preview.html com o chrome-devtools MCP (ToolSearch "select:mcp__chrome-devtools__navigate_page,mcp__chrome-devtools__take_screenshot,mcp__chrome-devtools__resize_page,mcp__chrome-devtools__list_console_messages,mcp__chrome-devtools__evaluate_script,mcp__chrome-devtools__click"). Fotografe em 1440 e 390. Confira innerWidth: o Chrome do dono fica com zoom de 67%; se innerWidth não bater com o viewport, emule 960x600 para ter 1440x900 em CSS (abra a prévia com new_page + isolatedContext e use emulate, não resize_page). Overflow: procure elementos com getBoundingClientRect().right > innerWidth (com body overflow-x: clip, o scrollWidth não denuncia). Recrie o .preview.html sempre que o index.html mudar.`

const RULES = `
REGRAS GERAIS:
- Página e docs em português do Brasil. Comentários de código em inglês, poucos.
- Nunca leia nem imprima arquivos .env. Não publique nada, não faça deploy, não faça git commit/push.
- Evite o visual genérico de IA: nada de hero com gradiente roxo-azul, emoji como marcador de seção, Inter/Space Grotesk, card arredondado com barra de destaque em tudo.
- Escrita: frases curtas e diretas, específico em vez de esperto. Evite travessão como aparte, "não é X, é Y", dois-pontos com revelação e frases-feitas.`

const SCHEMA = {
  type: 'object',
  properties: {
    score: { type: 'number', description: '0-10' },
    approved: { type: 'boolean' },
    issues: { type: 'array', items: { type: 'string' }, description: 'problemas concretos e acionáveis, com local; vazio se nenhum' },
  },
  required: ['score', 'approved', 'issues'],
}

const web = s => /Visual|Motion|Checkout|QA/.test(s)
const LENSES = [
  ['revisor', (s, f, g) => `Você é o REVISOR/VALIDADOR RIGOROSO da etapa "${s}" de uma página de venda.
Objetivo da etapa: ${g}
Entregável: ${f}
${FACTS}
Julgue qualidade, completude, fidelidade às fontes (aponte QUALQUER afirmação inventada) e se serve ao objetivo final: uma página que converte. Leia o entregável inteiro.${web(s) ? ' Renderize (veja HOSPEDAGEM), confira console e overflow em 1440 e 390.\n' + HOSTING : ''}${web(s) && s !== 'Checkout' ? '\n' + STD + '\nAbra também a LP da XR18 e compare seção por seção, rodando os testes da seção "Testes" do padrão. Seção com menos motion ou acabamento que a equivalente da XR18 é problema, com local e correção. Nota >= 8,5 só se a página estiver no nível da XR18.' : ''}
Nota 0-10. Aprove só com nota >= ${MIN}. Liste problemas concretos com local exato e a correção. Seja exigente: 8,5 é profissional de verdade.`],
  ['storytelling', (s, f, g) => `Você é o REVISOR DE STORYTELLING da etapa "${s}" de uma página de venda.
Antes, carregue com a ferramenta Skill a skill "anthropic-skills:storytelling" (se não existir, "storytelling") e aplique os princípios de narrativa à venda: o leitor é o herói, o problema é o vilão, o produto é o guia, a transformação é a promessa central do produto.
Objetivo da etapa: ${g}
Entregável: ${f}
Avalie se o entregável carrega um arco forte: gancho, tensão, o que está em jogo, virada, resolução e chamada para ação, com cenas concretas do mundo do leitor. Leia o entregável inteiro.
Nota 0-10. Aprove só com nota >= ${MIN}. Liste problemas concretos com local.`],
  ['redundancia', (s, f, g) => `Você é o CAÇADOR DE REDUNDÂNCIAS E REPETIÇÕES da etapa "${s}".
Objetivo da etapa: ${g}
Entregável: ${f}
Leia o entregável inteiro. Encontre: ideia ou afirmação dita duas vezes com outras palavras, palavras/frases repetidas próximas, seções com o mesmo propósito, CTAs com texto idêntico, código/CSS/animação duplicados, enchimento e vícios de escrita de IA. Repetir o botão principal ao longo da página é esperado, mas o texto em volta deve variar. Num doc de estudo, uma remissão curta é melhor que repetir texto, mas remissão em excesso também é defeito.
Nota 0-10 (10 = nenhuma redundância). Aprove só com nota >= ${MIN}. Cada problema com local exato e correção.`],
]

// Lição da 1ª execução: docs de estudo não convergem (a nota oscila entre 7,4 e 8,3 rodada após rodada).
// Por isso o estudo não passa por revisão (rounds 0); a página e o QA final é que precisam passar.
// keys: lentes desta etapa. Narrativa e repetição se julgam no texto (Copy) e no QA; código só pelo revisor.
async function gated(stage, ph, files, goal, produce, revise, rounds, keys = ['revisor']) {
  await agent(produce, { label: `produz:${stage}`, phase: ph })
  if (!rounds) return { stage, approved: null, rounds: 0 }
  const lenses = LENSES.filter(([k]) => keys.includes(k))
  let last = []
  for (let r = 1; r <= rounds; r++) {
    const rev = (await parallel(lenses.map(([k, p]) => () =>
      agent(p(stage, files, goal), { label: `${k}:${stage}:r${r}`, phase: ph, schema: SCHEMA }).then(x => x && { ...x, lens: k })))).filter(Boolean)
    last = rev
    log(`${stage} rodada ${r}: ` + rev.map(x => `${x.lens}=${x.score}`).join(' '))
    if (rev.length === lenses.length && rev.every(x => x.score >= MIN && x.approved)) {
      return { stage, approved: true, rounds: r, scores: rev.map(x => ({ lens: x.lens, score: x.score })) }
    }
    if (r === rounds) break
    const fb = rev.map(x => `## ${x.lens} (nota ${x.score})\n` + x.issues.map(i => `- ${i}`).join('\n')).join('\n\n')
    await agent(`${revise}\n\nFEEDBACK DA REVISÃO (rodada ${r}; mínimo ${MIN} em todas as lentes). Corrija TODOS os itens abaixo direto em: ${files}. Não só reconheça. Mantenha o que não foi criticado.\n\n${fb}`,
      { label: `refaz:${stage}:r${r}`, phase: ph })
  }
  return { stage, approved: false, rounds, scores: last.map(x => ({ lens: x.lens, score: x.score, issues: x.issues })) }
}

// ---------- Estudo ----------
phase('Estudo')
const conteudoGoal = `Estude o produto INTEIRO e escreva ${D}/01-conteudo.md: mapa fiel para o copywriter (resumo por capítulo/módulo com páginas, cada técnica/valor/número ensinado, as dores do leitor que cada parte resolve, frases e exemplos marcantes com página, o arco de transformação, lista de diagramas, o que o produto NÃO cobre, seção "Promessas que o produto sustenta" com referência de página). Feche com "Alertas para o dono": toda contradição entre o arquivo do produto e a oferta (ex.: capa dizendo "oficial" ou "curso", páginas com propaganda, telefone, outro canal de venda, LEIA-ME com instruções de outra plataforma, marcas citadas). Separe fatos do produto de leitura editorial.`
const identGoal = `Estude a identidade visual e de movimento do produto e escreva ${D}/02-identidade.md: paleta exata (hex, tirada do CSS ou dos prints), fontes e escala tipográfica, grade, estilo de diagramas e ícones, todo elemento interativo (diagramas animados, quizzes com correção na hora, medidores, navegação) e como anima (duração, easing, gatilho), os 6 momentos mais "vendáveis" com nome do print, um bloco :root de tokens pronto para a página e o vocabulário de movimento. Inclua uma seção "Hardware" (ver ${PADRAO}): formato e cor das teclas e dos LEDs, cor do visor, capas de fader, knobs, plaquinhas, cores do medidor, nomes reais das teclas e modos. Inclua também as pegadinhas e valores técnicos que viram widgets no padrão: a cena de abertura, o caminho do sinal, a 2ª demonstração, o widget do percurso e o roteiro de show, cada um com capítulo e página.`
const vendaGoal = `Escreva ${D}/03-tecnicas-venda.md: técnicas de conversão de páginas de venda de produto digital no Brasil aplicadas a ESTE produto: ordem das seções, fórmulas de headline, padrão de hero, oferta e ancoragem sem escassez falsa, garantia, FAQ que derruba objeções, posição e microcopy dos CTAs, padrões mobile, CTA fixo, prova social sem depoimentos (demonstração, amostra, demo interativa, especificidade), checkout com pouco atrito (Pix primeiro, sinais de confiança), elementos interativos que aumentam conversão, antipadrões. Cite fontes (URLs). Feche com o blueprint recomendado para este produto. Seja enxuto: no máximo ~600 linhas.`
const reuse = A.layout === 'template' ? ` A página-base ${A.layout_ref} e os docs ao lado dela (pasta docs/, se existir) já trazem pesquisa de venda validada: reaproveite o que servir.` : ''

const study = await parallel([
  () => gated('Estudo Conteúdo', 'Estudo', `${D}/01-conteudo.md`, conteudoGoal,
    `${RULES}\n${FACTS}\nTAREFA: ${conteudoGoal}\nLeia TUDO: PDF com a ferramenta Read e o parâmetro pages em blocos de 20, ou extraia o texto com python3 -I e pypdf. Não pule partes. Escreva o .md.`,
    `${RULES}\nVocê mantém ${D}/01-conteudo.md. Releia as partes da fonte que precisar.`, ROUNDS.estudo),
  () => gated('Estudo Identidade', 'Estudo', `${D}/02-identidade.md`, identGoal,
    `${RULES}\n${FACTS}\nTAREFA: ${identGoal}\n${A.fontes.interativo ? `Fonte principal: ${A.fontes.interativo}. Leia CSS/JS com grep/sed (não despeje base64) e abra no navegador com o chrome-devtools MCP (sirva a pasta com python3 -m http.server 8766 em segundo plano) para clicar em slides, quizzes e diagramas. Salve prints úteis em ${B}/img/ (ed-*.webp, até ~1600 px de largura) e liste-os no doc.` : `Sem edição interativa: extraia a identidade do PDF (renderize páginas-chave em PNG, ex.: sips ou pypdf + pdftoppm se houver) e dos prints em ${A.imagens || 'nenhuma pasta'}.`}${A.layout === 'template' ? `\nO layout será a página-base ${A.layout_ref}: documente também os tokens dela e o que deve mudar para combinar com este produto.` : ''}`,
    `${RULES}\nVocê mantém ${D}/02-identidade.md.`, ROUNDS.estudo),
  ...(A.venda_ref ? [] : [() => gated('Estudo Venda', 'Estudo', `${D}/03-tecnicas-venda.md`, vendaGoal,
    `${RULES}\n${FACTS}\nTAREFA: ${vendaGoal}${reuse}\nUse WebSearch/WebFetch (ToolSearch "select:WebSearch,WebFetch") para fontes atuais.`,
    `${RULES}\nVocê mantém ${D}/03-tecnicas-venda.md.`, ROUNDS.estudo)]),
])

// ---------- Copy ----------
phase('Copy')
const copyGoal = `Escreva todos os textos da página${A.checkout.modo === 'externo' ? '' : ' e do checkout'} em ${D}/04-copy.md, seção por seção na ordem final, prontos para colar: hero (headline, subheadline, CTA, microcopy), problema/história, transformação, o que tem dentro (capítulos como resultados), legendas da demonstração interativa, para quem é / não é, oferta com R$ ${P.preco}, garantia de ${P.garantia_dias} dias, seção do autor (${P.autor}, sem credenciais inventadas), FAQ de objeções (inclua com honestidade como o conteúdo foi feito, se as fontes disserem), CTA final, texto da barra fixa${A.checkout.modo === 'externo' ? '' : ', textos do checkout (resumo, rótulos Pix/cartão, linhas de confiança, tela de confirmação com download, erros)'}, <title> e meta description. Cada seção diz em uma linha qual o papel dela na conversão. Toda afirmação rastreável até 01-conteudo.md (referência de página em comentário).`
const copy = await gated('Copy', 'Copy', `${D}/04-copy.md`, copyGoal,
  `${RULES}\n${FACTS}\nTAREFA: ${copyGoal}\nLeia inteiros: ${D}/01-conteudo.md, ${D}/02-identidade.md, ${V}. Antes de escrever, carregue a skill "anthropic-skills:storytelling" (ou "storytelling") e use-a para o arco (leitor = herói, produto = guia). Use só fatos do produto; os "Alertas para o dono" do 01 viram <!-- CONFIRMAR --> quando afetarem a oferta.`,
  `${RULES}\n${FACTS}\nVocê é o copywriter e mantém ${D}/04-copy.md.`, ROUNDS.copy, ['revisor', 'storytelling', 'redundancia'])

// ---------- Visual ----------
phase('Visual')
const visualGoal = `Construa a página completa ${B}/index.html (estrutura e design final, todos os textos de 04-copy.md colocados literalmente, prints reais em img/). ${LAYOUT} Siga o blueprint de ${V}. Deixe ganchos para o agente de motion: atributos data-anim e contêineres com id para os widgets interativos que a copy cita (demonstrações do conteúdo do produto), já com o fallback estático estilizado. Barra de CTA fixa no mobile.${STD}`
const visual = await gated('Visual', 'Visual', `${B}/index.html`, visualGoal,
  `${RULES}\n${FACTS}\n${HOSTING}\nTAREFA: ${visualGoal}\nAntes, carregue a skill "frontend-design" (ou "example-skills:frontend-design") e leia inteiros ${D}/02-identidade.md, ${V} e ${D}/04-copy.md. Escreva ${B}/index.html. Renderize em 1440 e 390 para se autoavaliar antes de terminar.`,
  `${RULES}\n${FACTS}\n${HOSTING}\nVocê é o designer e mantém ${B}/index.html. Se um problema de texto aparecer, atualize também ${D}/04-copy.md.`, ROUNDS.visual)

// ---------- Motion + Checkout ----------
phase('Motion e Checkout')
const motionGoal = `Deixe ${B}/index.html animada e interativa na linguagem de movimento do produto (02-identidade.md): uma sequência orquestrada no hero, revelações no scroll partindo de um estado visível, e widgets que DEMONSTRAM o conteúdo do produto (cada valor técnico tirado de 01-conteudo.md), como mini quiz com correção na hora, diagrama clicável, controle que o leitor arrasta até a meta, contadores do que tem dentro. GSAP 3.12.5 + ScrollTrigger do cdnjs (versão fixa) e/ou CSS/canvas/SVG. 60 fps (só transform/opacity), prefers-reduced-motion, teclado e toque acessíveis, sem erros nem avisos no console, página legível mesmo se o JS falhar, sem código de animação duplicado.${STD} Implemente TODOS os itens da seção "Seções e o motion de cada uma" do padrão e rode a seção "Testes" antes de terminar.`
const checkoutMp = `Construa o checkout: (1) ${B}/checkout.html, documento completo na mesma identidade da index.html: resumo do pedido (capa, título, R$ ${P.preco}, o que inclui), nome + e-mail validados, Payment Brick do Mercado Pago (Pix primeiro, cartão com parcelas; sem boleto) carregado de https://sdk.mercadopago.com/js/v2 SÓ fora do sandbox do Artifact e com chave configurada; no topo do script: MP_PUBLIC_KEY = '', API_BASE = '${A.checkout.api_base}', SUPPORT_EMAIL = '', PRODUCT = '<slug do produto>'. Sem chave ou sem SDK (como dentro do Artifact), mostre um modo demonstração rotulado que percorre as mesmas telas (QR do Pix, cartão, aprovação com botão de download). Sinais de confiança, garantia, nota de segurança, tela de confirmação com link de download, estados de erro/nova tentativa, tela de espera do Pix com copia-e-cola e consulta de status.
(2) Backend: REAPROVEITE o que já existe em ${A.checkout.backend} (functions lp-pay, lp-status, lp-webhook, lp-dl; _shared/lp.ts e _shared/lp_logic.ts com testes em _shared/lp_logic_test.ts; tabela lp_orders). Se lp_logic.ts ainda tiver um produto só (constantes PRICE/TITLE/DL_FILES), troque por um catálogo PRODUCTS por slug (preço, título, descrição na fatura, arquivos de entrega no bucket "entregas"), mantendo o produto antigo funcionando, e crie uma migration nova que adiciona a coluna product em lp_orders (default = slug do produto antigo). Cadastre este produto no catálogo. O servidor valida o preço pelo catálogo, nunca pelo navegador. Atualize os testes e rode-os: o binário do deno pode estar em ~/.npm/_npx/*/node_modules/@deno/darwin-arm64/deno (ou npx -y deno test). NÃO faça deploy nem aplique migration.
(3) Acrescente a ${D}/05-checkout-setup.md (ou crie) o passo a passo em português simples para o dono: credenciais do Mercado Pago, secrets, arquivos de entrega deste produto no bucket, comandos de deploy, teste com usuários de teste.`
const checkoutExt = `Confira que todos os CTAs da ${B}/index.html levam a ${A.checkout.url_externa} e que a página explica o que acontece depois do clique (plataforma, Pix/cartão, entrega). Não crie checkout.html. Escreva ${D}/05-checkout-setup.md com o que o dono precisa conferir na plataforma (preço R$ ${P.preco}, garantia, arquivo de entrega, pixel).`
const checkoutGoal = A.checkout.modo === 'mp' ? checkoutMp : A.checkout.modo === 'externo' ? checkoutExt
  : `Construa ${B}/checkout.html só em modo demonstração (mesma identidade da index.html): resumo, nome/e-mail, Pix e cartão simulados, aprovação com botão de download, tudo rotulado como demonstração. Sem backend.`
const checkoutFiles = A.checkout.modo === 'mp'
  ? `${B}/checkout.html, ${A.checkout.backend}/functions/lp-*/, ${A.checkout.backend}/functions/_shared/lp*.ts, ${A.checkout.backend}/migrations/ (migration nova), ${D}/05-checkout-setup.md`
  : A.checkout.modo === 'externo' ? `${B}/index.html (só os CTAs), ${D}/05-checkout-setup.md` : `${B}/checkout.html`

const [motion, checkout] = await parallel([
  () => gated('Motion', 'Motion e Checkout', `${B}/index.html`, motionGoal,
    `${RULES}\n${FACTS}\n${HOSTING}\nTAREFA: ${motionGoal}\nAntes, carregue as skills "motion-design", "gsap-core" e "gsap-plugins" (ScrollTrigger). Leia ${D}/01-conteudo.md e ${D}/02-identidade.md. Edite ${B}/index.html usando os ganchos data-anim e os contêineres deixados pelo designer; pode ajustar markup/CSS, não mude a copy. Outro agente cuida do checkout ao mesmo tempo: não mexa em checkout.html${A.checkout.modo === 'externo' ? ' nem nos href dos CTAs' : ''}. Teste cada widget com o chrome-devtools (clique/arraste) em 1440 e 390 antes de terminar.`,
    `${RULES}\n${FACTS}\n${HOSTING}\nVocê é o engenheiro de motion e mantém as animações e widgets de ${B}/index.html. Não mexa no checkout nem na copy.`, ROUNDS.motion),
  () => gated('Checkout', 'Motion e Checkout', checkoutFiles, checkoutGoal,
    `${RULES}\n${FACTS}\n${HOSTING}\nTAREFA: ${checkoutGoal}\nPara a API atual do Mercado Pago use context7 (ToolSearch "select:mcp__plugin_context7_context7__resolve-library-id,mcp__plugin_context7_context7__query-docs") ou WebFetch. Leia os tokens CSS de ${B}/index.html para manter a identidade (outro agente anima essa página agora: leia, nunca escreva${A.checkout.modo === 'externo' ? ', exceto os href dos CTAs' : ''}) e os textos de checkout em ${D}/04-copy.md. Renderize em 1440 e 390 e percorra o fluxo.`,
    `${RULES}\n${FACTS}\n${HOSTING}\nVocê é o engenheiro de checkout e mantém: ${checkoutFiles}. Nunca faça deploy.${A.checkout.modo === 'externo' ? '' : ' Não edite index.html.'}`, ROUNDS.checkout),
])

// ---------- QA final ----------
// Lição: depois do QA a página é a fonte da verdade. Mudar a página depois exige rodar o QA de novo.
phase('QA final')
const qaGoal = `Auditoria final integrada da venda (index.html${A.checkout.modo === 'externo' ? '' : ' + checkout.html'}${A.checkout.modo === 'mp' ? ' + backend' : ''}): converte? Narrativa do hero até a confirmação, coerência de copy/preço/garantia/entrega entre página e checkout, todos os links, acabamento e fidelidade à identidade, qualidade e desempenho do motion (sem travadas, reduced-motion), 390 e 1440, acessibilidade básica (contraste, foco, alt, labels), console, overflow, regras de hospedagem, fidelidade às fontes, nenhuma afirmação inventada${A.checkout.modo === 'mp' ? ', segurança do backend (preço validado no servidor, HMAC, assinatura do webhook, nenhum segredo no front, RLS)' : ''}.${STD}`
const qaFiles = `${B}/index.html${A.checkout.modo === 'externo' ? '' : `, ${B}/checkout.html`}${A.checkout.modo === 'mp' ? `, ${A.checkout.backend}/functions/lp-*/, ${A.checkout.backend}/functions/_shared/lp*.ts` : ''}`
const qa = await gated('QA final', 'QA final', qaFiles, qaGoal,
  `${RULES}\n${FACTS}\n${HOSTING}\nTAREFA: ${qaGoal}\nVocê é o engenheiro de QA de integração. Renderize e clique em tudo com o chrome-devtools. Corrija todo problema direto nos arquivos (${qaFiles}). ${A.checkout.modo === 'mp' ? 'Rode os testes do lp_logic. ' : ''}Ao final, sincronize ${D}/04-copy.md com o texto real da página e escreva ${D}/06-qa.md com o que conferiu e corrigiu. Apague ${B}/.preview.html.`,
  `${RULES}\n${FACTS}\n${HOSTING}\nVocê é o engenheiro de QA. Corrija direto em ${qaFiles} e mantenha ${D}/04-copy.md igual ao texto da página. Apague ${B}/.preview.html ao terminar.`, ROUNDS.qa, ['revisor', 'redundancia'])

return { study, copy, visual, motion, checkout, qa }
