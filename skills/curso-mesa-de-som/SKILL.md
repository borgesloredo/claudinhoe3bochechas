---
name: curso-mesa-de-som
description: Use quando o usuário quiser criar um curso completo sobre uma mesa de som digital (Behringer, Midas, Allen & Heath, Yamaha, Soundcraft, PreSonus etc.) e as mesas da mesma família — manual consolidado, pesquisa de cursos, PDF de aula, slides de aula com motion e notas do apresentador, e versão de autoestudo com (i) explicativo e áudio narrado. Dispare também com "curso da mesa X", "monta o curso da XR18/X32/SQ5/TF5", "material de aula de mesa de som", "slides e PDF para ensinar mesa digital", mesmo que o usuário não fale em "skill" nem descreva as etapas.
---

# Curso de mesa de som (pipeline completo, com aprovações)

## O que esta skill faz
Reproduz, numa única chamada, o caminho que levou do zero ao curso aprovado da Behringer XR18. A ordem é esta:

1. **Mesa e família.** Pergunta a mesa, pesquisa a família e confirma a lista com o usuário (portão 1).
2. **Fase 1, conteúdo e PDF.** Manuais e pesquisa por mesa rodam em paralelo. Depois vêm a consolidação, o curso final e o **PDF de aula**, que já nasce revisado em storytelling, redundância, neutralidade, parte técnica e design.
3. **Fase 2, direção visual.** Gera a direção **Hardware da mesa** com motion em 6 slides de amostra. O usuário aprova ou não (portão 2). As outras 2 direções só são geradas se ele reprovar.
4. **Fase 3, deck de aula (V1).** O deck sai na direção escolhida, **já enxuto** (sem a versão inchada que depois precisava ser cortada), com motion sob medida em todo slide, notas do apresentador completas e arquivo único para envio. O usuário aprova (portão 3), e só então a V1 é congelada como somente leitura.
5. **Fase 4, V2 de autoestudo.** Os mesmos slides recebem o botão (i), com explicação para leigo e glossário clicável, e o botão ▶, com áudio de voz masculina brasileira.
6. **Padronização final (automática, sem portão).** Navegação por capítulos (→ muda de capítulo, ↓ anda dentro dele) na aula e na V2, validação independente dos quizzes, correções, vozes regravadas e testes, no mesmo nível dos 20 cursos anteriores. Só depois o usuário aprova a entrega final (portão 4).

O usuário só responde nos portões. Ele não precisa instalar nada, pesquisar ferramentas nem mandar repetir etapas. Todo o conhecimento acumulado está aqui:

| Arquivo | O que tem |
|---|---|
| `references/regras-do-curso.md` | Regras de conteúdo, voz, neutralidade, slides, notas e V2. Todo agente lê. |
| `references/design.md` | As 3 direções, o padrão de motion e a verificação visual |
| `references/storytelling.md` | Storytelling aplicado a curso técnico (usado junto com a skill "storytelling", se ela existir) |
| `assets/` | Manuais de design aprovados, skills de design (vendored) e ferramentas validadas (gerador de slides, checadores, PDF, arquivo único, V2, voz). **As ferramentas vêm da 1ª execução (XR18) e os workflows mandam adaptá-las.** Amarras conhecidas: `enxugamento.py` (exemplo de plano de slides), listas de modelos e sumário em `build_slides.py`, duas famílias em `check_titles.mjs`, textos fixos em `v2/check_ui.mjs` e `v2/check_glossario.py`, pronúncias Behringer/Midas em `v2/tts/gen.py` (`PRON`), cores por família nos `DESIGN.md`. |
| `assets/padronizacao/` | Passo 7: `padronizar.sh` (preparar, aplicar, entregar), ferramentas de teste e as instruções `VALIDACAO.md`, `APLICAR.md`, `VERIFICAR.md`, com um curso de exemplo em `exemplos/` |
| `workflows/` | Um workflow por fase, mais `ajustes-checklist.js` para os pedidos feitos nos portões |
| `config.json` | O CTA do dono (site e telefone) e a meta de slides |
| `scripts/abrir-sessao.sh` + `sessao-enxuta.json` + `mcp-vazio.json` | Abre a sessão enxuta (ver "Sessão enxuta") |

Caminho da skill: `K=~/.claude/skills/curso-mesa-de-som` (use o caminho absoluto nos `args`).

## Sessão enxuta (confira antes de tudo)
Rode `echo "$CURSO_SESSAO_ENXUTA"`. Se não sair `1`, a sessão foi aberta com todos os plugins, conectores do claude.ai, servidores MCP e skills do dono, e **cada agente dos workflows herda esse contexto**. Medido em 03/11/2026: ~41 mil tokens por início de agente na sessão normal, ~22 mil na enxuta. O curso não usa nada disso: só as skills locais `frontend-slides`, `gsap-*`, `motion-design` e `storytelling`, mais as ferramentas nativas.
O dono quer continuar chamando `/curso-mesa-de-som` e ir direto para o modo enxuto, sem pergunta. Então, antes de qualquer outra coisa (avisos e pergunta da mesa ficam para a sessão nova), rode:
```bash
~/.claude/skills/curso-mesa-de-som/scripts/abrir-em-nova-janela.sh
```
Ele abre uma janela nova do Terminal, na mesma pasta e na mesma conta, já no modo enxuto e com `/curso-mesa-de-som` rodando. Depois diga em uma linha: "Abri o curso numa janela nova do Terminal, já no modo enxuto. Continue por lá e feche esta (`/exit`)." e pare.
Se o script falhar, peça ao usuário para sair (`/exit`) e reabrir digitando `curso` no Terminal (atalho do `~/.zshrc` que roda `scripts/abrir-sessao.sh "/curso-mesa-de-som"`).
O script aplica `sessao-enxuta.json` (conectores e skills sem uso desligados; plugins desligados na hora de abrir) e `mcp-vazio.json`, e mantém o Mac acordado enquanto a sessão durar. Se o usuário preferir seguir na sessão atual, siga. Plugin ou skill nova que o curso passe a usar: tire de `skillOverrides` em `sessao-enxuta.json`.

## Antes de começar (uma vez, em 3 linhas)
Avise o usuário:
- **Duração e custo.** São muitas horas de execução. As 4 maiores execuções medidas usaram de 49M a 86M de tokens sem contar leitura de cache (1,2 a 1,8 bilhão contando), todas antes da sessão enxuta.
- **Confirmações de permissão atrasam tudo** quando ninguém está olhando. Recomende **Shift+Tab** até "bypass permissions" nesta sessão. A lista "ask" do usuário (`rm`, `mv`, `chmod`, cliques do Playwright) ainda prevalece sobre isso; se ela travar o andamento, ofereça suspendê-la temporariamente, com backup e comando de restauração. Você não pode editar as próprias permissões: quem roda o comando é o usuário, com `!`.
- **O Mac fica ligado.** Na sessão enxuta, o script já cuida disso. Fora dela, sugira `! caffeinate -dims &`.

## Passo 1: Mesa e família (portão 1)
1. Leia `$K/config.json`. Ele traz o CTA (`cta_texto`), a meta de slides (`meta_slides`) e a pasta base.
2. Pergunte, em texto simples: "Qual mesa de som você quer como base do curso?"
3. Pesquise a família com WebSearch:
   - **O que conta:** variantes da mesma **linha de produto** (mesmo firmware e app, outros formatos: console, compacta, rack); gerações e "plus" da mesma linha ainda vendidas ou comuns no mercado usado; e o **mesmo produto vendido com outra marca** do grupo (exemplos: Behringer X AIR e Midas MR; Behringer X32 e Midas M32).
   - **O que não conta:** stageboxes e expansores de I/O, apps, superfícies de controle e acessórios. Também ficam fora outras linhas que só dividem o processador interno (exemplo: Avantis, dLive e Qu não entram num curso da SQ) e outras marcas do mesmo dono corporativo que não são o mesmo produto.
   - Para cada modelo, traga uma linha de diferença (faders, preamps, formato).
4. Mostre a lista e pergunte se confirma, tira ou acrescenta. Se o usuário citar um nome que não existe, diga isso com evidência e proponha a correção. **O material final nunca menciona o nome inexistente.**
5. Defina estas variáveis:
   - `mesa`: o nome da mesa escolhida;
   - `familia`: o nome da família ou linha (exemplo: "Allen & Heath SQ");
   - `slug`;
   - `R=<pasta_base>/curso-<slug>` (caminho absoluto);
   - `modelos: [{slug, name}]`;
   - **`grupos: [{slug, name, modelos: [nomes]}]`**: modelos que dividem o mesmo manual e a mesma plataforma ficam num grupo só (exemplo: SQ-5, SQ-6, SQ-7 e SQ-Rack = 1 grupo; X32 e M32 = 2 grupos, porque são manuais de marcas diferentes). A Fase 1 roda manual e pesquisa **por grupo**, o que evita trabalho repetido.
6. **Chave do Gemini (a voz da V2).** Resolva agora, ainda na conversa inicial, porque a Fase 4 só roda com ela e é melhor descobrir um problema agora do que horas depois. Se o script `cofre` do dono existir (`~/SEU-PROJETO/cofre`) ou se `~/.config/curso-mesa-de-som/gemini.env` já existir, pule este item. Senão, guie o usuário em texto simples, um passo por vez:
   1. "Abra https://aistudio.google.com/apikey e entre com uma conta Google. É grátis e não pede cartão."
   2. "Clique em **Create API key** (Criar chave de API), aceite os termos se aparecerem e copie a chave. Ela começa com `AIza`."
   3. "**Não cole a chave aqui no chat.** Abra o app Terminal do Mac, cole o comando abaixo, tecle Enter e, quando ele pedir, cole a chave e tecle Enter de novo. A chave não aparece na tela, é normal." Mande o comando num bloco de código:
      ```bash
      mkdir -p ~/.config/curso-mesa-de-som && printf 'Cole a chave do Gemini e tecle Enter: ' && read -rs k && printf 'GEMINI_API_KEY=%s\n' "$k" > ~/.config/curso-mesa-de-som/gemini.env && chmod 600 ~/.config/curso-mesa-de-som/gemini.env && echo && echo salvo
      ```
   4. Quando ele disser que apareceu `salvo`, confira a chave sem gastar a cota e sem mostrá-la:
      ```bash
      ( set -a; . ~/.config/curso-mesa-de-som/gemini.env; curl -s -o /dev/null -w '%{http_code}\n' -H "x-goog-api-key: $GEMINI_API_KEY" https://generativelanguage.googleapis.com/v1beta/models )
      ```
      `200` é chave certa. `400` ou `403` é chave errada ou copiada pela metade: peça para repetir os passos 2 e 3.
   5. Avise da cota em uma linha: o plano grátis dá 10 pedidos de voz por dia por chave, e um curso de ~100 telas precisa de ~35 pedidos (uns 4 dias com 1 chave; o gerador retoma sozinho no dia seguinte). Para ir mais rápido, ele pode criar mais chaves, cada uma em outra conta Google ou outro projeto (chaves do mesmo projeto dividem a cota), e salvar cada uma com o mesmo comando, trocando `GEMINI_API_KEY=` por `GEMINI_API_KEY_2=`, `GEMINI_API_KEY_3=` e assim por diante, e `>` por `>>`.
   Nunca peça, mostre nem copie o valor da chave para o chat ou para arquivos do curso.

## Passo 2: Preparar o projeto
```bash
"$K/scripts/setup.sh" "$R"
```
O script cria as pastas, copia as ferramentas de referência para `$R/tools/`, instala playwright, reveal.js e GSAP, baixa os navegadores, monta `07-slides/lib/` e instala as skills de design que faltarem.

## Passo 3: Fase 1, conteúdo e PDF
```js
Workflow({ scriptPath: `${K}/workflows/fase1-conteudo-pdf.js`, args: { R, K, mesa, familia, modelos, grupos, cta: config.cta_texto } })
```
Ao terminar:
- Leia o resultado. Se alguma etapa ficou "não aprovada", diga qual.
- Mostre ao usuário o caminho do PDF (`$R/06-pdf/curso.pdf`) e o abra (`open`).
- Siga direto para a Fase 2. Não há portão aqui: o usuário pediu que o PDF já saia bom e que a escolha aconteça no visual.

## Passo 4: Fase 2, direção visual Hardware da mesa (portão 2)
```js
Workflow({ scriptPath: `${K}/workflows/fase2-direcoes.js`, args: { R, K, mesa } })
```
O padrão é gerar só a direção 2, **Hardware da mesa**, porque o dono a preferiu em quase todos os cursos. Gere as outras (`direcoes: [1, 3]`) só se ele reprovar ou pedir.
Ao terminar:
1. Leia o `contato.png` com Read para conferir.
2. Abra no Safari (`open -a Safari .../opcao-2/index.html`) e abra o `motion.mp4`.
3. Mostre a nota do revisor e as pendências principais. Pergunte se ele aprova. **Espere a resposta**, porque esse portão é sempre dele.
4. Se ele aprovar, salve as pendências do revisor em `opcao-2/PENDENCIAS-REVISOR.md` e passe para a Fase 3 via `args.extra`. A Fase 2 faz só 1 rodada de propósito: o polimento acontece na Fase 3.
5. Se ele reprovar, aplique os ajustes pedidos na mesma direção ou gere `direcoes: [1, 3]`, conforme o que ele disser.

## Passo 5: Fase 3, deck de aula V1 (portão 3)
```js
Workflow({ scriptPath: `${K}/workflows/fase3-deck-aula.js`, args: { R, K, mesa, direcao: { n, name }, meta_slides: config.meta_slides } })
```
Ao terminar:
- Confira por conta própria, no WebKit e offline, a contagem de telas, se abre, se a tecla S funciona e se o contador aparece em toda tela.
- Abra o deck e o arquivo único `07-slides/curso-slides.html`.
- Reporte as notas dos revisores e peça aprovação.
- **Se o usuário pedir ajustes:** transforme cada pedido em um item da lista e rode `ajustes-checklist.js` com `escopo: 'deck'` ou `'pdf'`. Repita até ele aprovar. Antes de cada rodada, faça backup em `$R/backups/<etapa>-<data>/`.
- **Quando o usuário aprovar, congele a V1:**
```bash
V="$R/entregas/v1-aulas"; mkdir -p "$V/deck" && cp "$R/07-slides/index.html" "$V/deck/" && find "$R/07-slides" -maxdepth 1 \( -name '*.css' -o -name '*.js' \) -exec cp {} "$V/deck/" \; && cp -R "$R/07-slides/lib" "$R/07-slides/fonts" "$V/deck/" \
 && cp "$R/07-slides/curso-slides.html" "$R/06-pdf/curso.pdf" "$V/" && (cd "$V" && shasum -a 256 curso-slides.html curso.pdf deck/index.html > SHA256SUMS) && chmod -R a-w "$V"
```

## Passo 6: Fase 4, V2 de autoestudo
1. Prepare a voz: `"$K/scripts/setup.sh" "$R" --tts`. A voz é a **mesma dos vídeos de venda: Gemini TTS, voz Puck, estilo "reels2"** (decisão do dono, 14/11/2026; o Kokoro `pm_alex` saiu). O setup baixa o Whisper e roda `gen.sh --teste`, que deve dizer "5 chave(s)". As chaves são as `GEMINI_API_KEY_*` do cofre. Guia de escrita e detalhes: `tools/v2/tts/README.md`.
2. Rode a etapa de conteúdo:
   ```js
   Workflow({ scriptPath: `${K}/workflows/fase4a-v2-conteudo.js`, args: { R, K, mesa } })
   ```
   O resultado traz `cap_min` e `cap_max`.
3. Gere os áudios **no fio principal**, em segundo plano e **pela trava global**:
   ```bash
   cd "$R/tools/v2" && tts/gen.sh --lint script/ && ./heavy.sh tts/gen.sh script/ ../../08-slides-v2/audio/
   ```
   Cada pedido leva 3 roteiros (~4 min de áudio, ~70 s de relógio): ~35 pedidos e ~15 min num curso de ~100 telas. **Cota: ~50 pedidos/dia** (10 por chave × 5). Se aparecer `COTA DO DIA ESGOTADA`, rode o mesmo comando no dia seguinte, porque ele retoma sozinho. O `--lint` não gasta pedido: roteiro com risco é pulado e listado. Se o lint reprovar, o roteiro volta para o registro falado do guia ("tá", "aperta", sem letra solta nem `main`/`bus` minúsculos).
   Para gerar só um subconjunto, use links simbólicos numa pasta. Os avisos que pedem escuta ficam em `tools/v2/qa-out/gemini-conferir.txt`.
4. **Só depois que a geração terminar**, faça o QA em lote, em segundo plano: `"$R/tools/v2/qa_batch.sh"`. Ele faz a transcrição, o classificador de sotaque pt-BR × pt-PT e a medição de volume, um modelo de cada vez. Nunca rode TTS e Whisper ao mesmo tempo.
5. Rode a etapa final:
   ```js
   Workflow({ scriptPath: `${K}/workflows/fase4b-v2-audio-final.js`, args: { R, K, mesa, cap_min, cap_max } })
   ```
6. Siga direto para o Passo 7, sem portão e sem perguntar: o dono quer todo curso padronizado sem precisar pedir.

## Passo 7: Padronização final (automática)
Deixa o curso no mesmo padrão dos 20 anteriores. Trabalha em `$R/padronizacao/` (fora do git) e só troca as entregas no fim, com backup.
```bash
S="$K/assets/padronizacao/padronizar.sh"
bash "$S" "$R" preparar     # ~20 min: pilhas por capítulo, testes Chromium+WebKit, tecla R no original, material da validação
```
1. **Leia a saída de `preparar`.** Exija "a investigar: 0" e o `deck/` com "falhas: 0". Diferença de imagem num slide: rode-o sozinho em `$R/padronizacao` (`node tools/antes_depois.mjs <antes> <depois> <nav> --so <id>`). Se passar sozinho ou se o original comparado com ele mesmo também variar, é ruído: ponha em `RUIDO` de `tools/conferir_final.py`, com o motivo. Falha de navegação ou erro de JS novo é defeito: corrija antes de seguir.
2. **Validador** (1 agente, Opus, em segundo plano): "Siga À RISCA `$R/padronizacao/VALIDACAO.md`, com <c> = `<slug>`. Leia TODAS as folhas de quizzes e de tiras. Somente leitura, exceto `validacao/<slug>.md`." Quando ele voltar, confira você mesmo 2 itens CORRIGIR (a definição no glossário ou a foto) antes de seguir.
3. **Aplicador** (1 agente, Opus): "Siga À RISCA `$R/padronizacao/APLICAR.md`, com <c> = `<slug>`." Ele escreve `ws/<slug>/corrigir.py`, edita os roteiros do curso (com backup) e lista as vozes em `ws/<slug>/vozes.txt`.
4. **`bash "$S" "$R" aplicar`**: vozes pela trava global, V2 refeita, fotos novas e testes. Exija:
   - vozes com nota ≥ 0,80, pt-BR em todas as janelas, −16 a −17 LUFS e duração sem suspeita. Nota baixa: `tools/dif_voz.py`; frases repetidas inventadas no fim da transcrição são alucinação do Whisper (transcreva só os últimos 8 s para provar);
   - "a investigar: 0" (diferença nos quizzes que o `corrigir.py` mudou é esperada);
   - tecla R com "suspeitos: 0". Suspeito restante: veja a foto (`DUMP=<pasta>` no `tecla_r.mjs`); só animação contínua ou borda de letra é aceitável.
5. **Verificador** (1 agente, Sonnet): "Siga À RISCA `$R/padronizacao/VERIFICAR.md`, com <c> = `<slug>`; fotos novas em `material-r2`." Se houver PROBLEMA, o aplicador corrige só esses itens, rode `OUT=material-r3 bash "$S" "$R" aplicar` e o verificador de novo com `material-r3`. Repita até não sobrar problema.
6. **`bash "$S" "$R" entregar`**: backup em `$R/backups/padronizacao-<data>/`; troca o zip, `v1-aulas/curso-slides.html`, `v1-aulas/deck/`, `SHA256SUMS` e `08-slides-v2/`; commit dos roteiros numa branch nova.
7. **Modo celular**: depois do `entregar`, rode `python3 "$K/assets/celular/aplicar.py" --backup-dir "$R/backups/celular-<data>" <zip V2 entregue>` (e o mesmo script, sem `--backup-dir`, em `08-slides-v2/index.html` se a pasta existir). Ele injeta a camada de celular (deitado: tela cheia e deslizar na ordem de leitura; em pé: aviso para girar; botão ☰ com o índice dos capítulos, que procura um canto livre a cada slide; "Tela cheia" no Android e, no iPhone, os passos de Adicionar à Tela de Início) e é idempotente. Teste: `python3 "$K/assets/celular/aplicar_test.py"`. Fonte da camada: `curso-xr18/tools/celular/` (copie de lá se mudar).
8. **Trava (obrigatória, depois do modo celular e de qualquer mudança no zip V2)**: na pasta `ml-server`, rode `../cofre DL_SECRET -- deno run -A lp/travar-autoestudo.ts <pasta do curso>`. Ela gera `autoestudo/v2-autoestudo-travado.zip`, com a tela e as narrações criptografadas. O comprador libera uma vez com o e-mail da compra e um código; depois o curso se renova sozinho quando houver internet e funciona até 7 dias sem internet; estorno perde o acesso. É o mesmo arquivo para computador e celular. O curso precisa estar no catálogo `PRODUCTS` (`supabase/functions/_shared/lp_logic.ts`). Para vender, suba com `lp/subir-cursos.ts --online`. Esse script recusa um zip travado mais velho que o V2. Desde 17/11/2026 o comprador não baixa zip nenhum: recebe só o link, e o Worker `cursos` (ml-server `cloudflare/cursos/worker.js`) serve o travado como aplicativo instalável (PWA) que funciona sem internet. Curso novo não precisa de nada extra além do `--online`; o PDF continua para baixar. Nunca entregue o `v2-autoestudo.zip` aberto: ele só alimenta a trava e a amostra grátis.
Defeitos de motion e avisos de título não são aplicados, salvo rótulo errado que se corrige trocando o texto. Liste os que ficaram no resumo da entrega. Os relatórios ficam em `$R/padronizacao/validacao/`.

## Passo 8: Conferência e portão 4
1. Confira por conta própria: `node "$R/tools/check_padrao.mjs" "$R"` deve sair OK; extraia o zip numa pasta vazia, abra no WebKit offline e clique no (i), num termo do glossário e no ▶. Use `muted` no teste. Confira também → (próximo capítulo) e ↓ (dentro do capítulo).
2. Abra a V2 para o usuário e peça para ele **ouvir um áudio**: ele já rejeitou uma voz com sotaque de Portugal. Para ajustes, use `ajustes-checklist.js` com `escopo: 'v2'` e depois rode de novo `padronizar.sh`: mova `$R/padronizacao` para `$R/backups/` e comece de `preparar`.

## Passo 9: Entrega
Resuma:
- **o que foi feito:** os arquivos e as notas dos revisores;
- **o que ficou pendente;**
- **o que depende do usuário:** restaurar permissões e lista "ask", reativar o som se os testes o mutaram, `pkill caffeinate` (só se ele foi iniciado à mão, fora da sessão enxuta).

Atualize a memória persistente (tipo `project`) com a pasta, as decisões e o status.

## Durante a execução
- **Avisos:** avise em uma linha a cada fase concluída. Quando o usuário perguntar a previsão, dê uma estimativa honesta pelo journal (`<transcript dir>/journal.jsonl`) e corrija para cima, sem esconder atrasos.
- **Paralelismo:** cada workflow roda no máximo 8 agentes ao mesmo tempo neste Mac. Para ir além, lance workflows independentes em paralelo, como a escrita do conteúdo dividida em 2 workflows. **Nunca** rode TTS, Whisper ou torch em paralelo: use `heavy.sh` e `qa_batch.sh`.
- **Modelo por função (definido em cada workflow, constantes `OPUS`, `SONNET`, `BARATO`):** Opus no que decide a qualidade e custa rodada se sair errado (curso final, PDF, direção visual, base e motion do deck, roteiros da V2, revisores técnico, design, storytelling e objetivo, corretores do PDF e do deck, ajustes do dono). Sonnet em extração, pesquisa, consolidação, notas, glossário, interface da V2, revisores de regras, redundância, leigo e funcional, todos os verificadores e corretores de texto e áudio. Sonnet com esforço baixo para montar e conferir arquivos; Haiku só para rodar comando (a integração do deck é o script `tools/integrar.sh`, rodado pelo Haiku; o Sonnet só entra se ele falhar). Motion: primeiro um agente Opus cria o padrão (`bespoke/_padrao.js`, `bespoke/PADRAO.md` e um slide-modelo de cada tipo); depois lotes de 5 slides seguem esse padrão, com no máximo 3 imagens lidas por agente; os revisores de design cobram a consistência entre lotes. Etapa nova segue a mesma regra; não deixe agente sem modelo.
- **Fase 3 acelerada (mais de 8 agentes):** rode `fase3-deck-aula.js` com `parar_em:'base'`, que devolve `slides` e `modelos` (já com o padrão de motion pronto). Em seguida, dispare 2 workflows ao mesmo tempo com `plan: slides, modelos, shard:{n:0|1, of:2}, parar_em:'motion'`. Por fim, rode um último workflow com `plan: slides, pular_motion:true` para a integração e a revisão. Os mesmos `args` base valem em todos.
- **Fonte nova no meio da fase (vídeo ou arquivo do usuário):** não mande `SendMessage` para um agente que o workflow está rodando. Ele passa a entregar o relatório ao fio principal, e o workflow trava esperando. Salve a fonte em `$R/downloads/<grupo>/` com um `LEIA.md` e deixe que as etapas seguintes a usem. Se precisar reaproveitar uma etapa entregue fora do workflow, retome com `args.pular: ['pesquisa:<slug>']` (só na Fase 1).
- **Fase 3 com motion e notas já prontos** (retomada de outra sessão): passe `plan` junto com `pular_motion:true`; sem `plan`, a base e o padrão de motion rodam de novo e podem reescrever o que estava pronto.
- **Workflow que falhou ou travou:** corrija a causa e rode `Workflow({scriptPath, resumeFromRunId, args})` com os mesmos args. As etapas prontas vêm do cache. Se a sessão caiu, o trabalho em disco continua lá: confira o journal e relance só o que falta.
- **Teste de navegador tocando som no Mac:** é um revisor testando o ▶. Silencie o som ou peça para os testes usarem `muted`.
- **Antes de sobrescrever qualquer entrega,** faça backup em `$R/backups/`. A V1 congelada só muda no Passo 7 (pilhas por capítulo, com a imagem de cada tela comprovada idêntica), pelo `padronizar.sh`, que faz o backup e volta a travá-la.

## Erros que esta skill já evita (não repita)
| Erro da 1ª execução | Como a skill evita |
|---|---|
| Fase 4b do curso XENYX (15/11/2026) regravou áudios por janelas isoladas do classificador de sotaque perto de 0 e esgotou a cota Gemini do dia; 13 áudios ficaram mais velhos que o roteiro | Critério de sotaque da voz Gemini = média >= 0,80 (janela isolada é pausa ou termo em inglês); regravação só por erro de fala confirmado. Se a cota acabar, a padronização (Passo 7) roda mesmo assim e os áudios pendentes entram em `ws/<slug>/vozes.txt` para o `aplicar`, depois que a cota voltar (~05h de Brasília) |
| Slides fatiados do PDF, com 435 telas, ~100 palavras por slide e "(continuação)" | A Fase 3 gera o deck enxuto direto, com meta de ~150 telas e no máximo 3 continuações |
| Visual genérico, metade vazia, diagrama pequeno no canto | Direção visual aprovada pelo usuário antes do deck; revisores de design com prints |
| Só parte dos slides com motion sob medida | Motion sob medida em todos os slides, em lotes paralelos |
| Notas repetindo o slide; "Pergunte à turma" e "Em cena" no slide | Regras da seção 7; revisor de notas |
| Nomes de autores e escolas, X16/X12, tom de IA respondendo | Regras 1 a 4; revisores de narrativa e neutralidade |
| Arquivo não abre no Safari ou no Brave | Pastas autocontidas, sem `../`; arquivo único com tudo embutido |
| Voz com sotaque de Portugal; depois, o Kokoro `pm_alex` (bom só para ebook) | Desde 14/11/2026, a voz dos vídeos de venda (Gemini Puck, aprovada pelo dono), com classificador de sotaque no QA |
| Gerar 1 pedido Gemini por voz (cota de 10/dia por chave) e conferência palavra por palavra num roteiro de 300 palavras (sempre cai em CONFERIR por homófono) | `gen_curso.py`: 3 roteiros por pedido, 5 chaves do cofre, retomada no dia seguinte, conferência tolerante (trecho de 3+ palavras ou semelhança < 96%); `vozes.sh` da padronização também em lote |
| Mac travou com 6 transcrições ao mesmo tempo | `heavy.sh` (trava global) e QA em lote |
| 3 geradores de voz juntos renderam menos que 1 (3 contra 4 vozes por minuto, swap quase cheio); no processador, uma voz passou de 6 min | Um gerador por vez, na placa gráfica. Paralelizar voz não acelera |
| O Whisper acusou trechos faltando ou repetidos em 32 áudios; em janelas curtas todos estavam certos (só siglas e números escritos de outro jeito) | Antes de refazer voz por trecho longo divergente, rode `tools/v2/qa_janelas.py <curso> <id>...` com o Python do mlx-whisper e confira palavras por segundo (2,8 a 3,2 no Kokoro antigo; 3,2 a 3,4 na voz Gemini). Para ajustar grafia, confie no erro repetido entre telas, não no erro isolado |
| Verificador com dois cursos ao mesmo tempo mais geração de voz deu 12 falhas seguidas de identidade na 01V96; sozinho, passou tudo | Verificador em sequência, sem TTS ou Whisper rodando. Falha de identidade em bloco de telas seguidas: repita sozinho antes de investigar |
| V2 de 4 cursos sem `preserve-slide-nodes.js`: ao girar o celular, o Reveal trocava as 148 telas (teste de rotação falhou) | `build_v2.py` injeta `preserve-slide-nodes.js` no `<head>` **e** troca `plugins: [RevealNotes]` por `plugins: [PreserveSlideNodes]` (só injetar não basta); exige Reveal 5.1.0 |
| No Si, fechar o (i) não devolvia o foco ao botão (o fechamento só focava se o foco estivesse fora do popup) | O `close` do popup sempre devolve o foco ao (i); no Safari o foco fica preso no popup fechado |
| Filas de voz esperando com `while pgrep -f <nome>` travaram por horas: o `pgrep -f` achava o texto do próprio comando de espera | Uma fila única em arquivo `.sh`, um curso por vez, sem esperar por `pgrep -f` |
| Revisões que nunca fecham | Padrão de checklist numerado, com corretor e verificador item a item |
| Só um curso tinha contador de telas; faixas brancas fora do 16:9; telas especiais faltando | `check_padrao.mjs` e seção 6 das regras: interface e telas obrigatórias em toda direção visual |
| Explicações e roteiros rasos (metade da XR18) e 297 telas reescritas depois | Faixas de 170–220 e 280–380 palavras, narração elemento por elemento, `conta_lote.py` em cada lote |
| Desenho contradizendo a fonte; quiz com a resposta já desenhada; recorte cortando controle | Regras da seção 6; o revisor técnico confere o desenho, não só o texto |
| AudioLab: na entrada do slide, as camadas de outra etapa (`data-ok`) só sumiam depois de 0,45 s e se sobrepunham à atual ("DESGIGAR" em s3-2) | No `deck.js`, na primeira entrada, camada com opacidade-alvo 0 some na hora (`gsap.set`), e só a atual anima; as tiras de 0 e 300 ms (`shot_motion.mjs`) mostram isso |
| Frase corrigida no slide e esquecida na nota, no (i) ou no PDF | Correção vale para os quatro lugares (seção 6) |
| 17 de 19 cursos com navegação fora do padrão: fila única de ~150 telas (seta → não pulava capítulo) ou `navigationMode: 'linear'` (HD96, M7CL, Midas) | Padrão XR18: cada capítulo é uma pilha `<section>` sem atributos de `cap-N` até `quiz-N`; capa/sumário/como usar e o fechamento ficam soltos; sem `navigationMode: 'linear'`. → muda de capítulo, ↓ anda dentro dele. CSS/JS do deck não pode depender de `.slides > section` (use `.slides section`) e o invólucro `.stack` tem `padding:0`. O Passo 7 empilha e testa (`assets/padronizacao/`) |
| Quizzes entregando a resposta pela definição do termo clicável do (i) (16 de 26 no AudioLab Live XL) e peças escondidas que a tecla R não escondia de novo | Regra na seção do (i); validação independente no Passo 7, que lê a definição de cada termo; teste `tecla_r.mjs` com controle negativo |
