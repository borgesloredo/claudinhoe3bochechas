# Direção 3 · Editorial bold

Preset de partida: **Swiss Modern** (frontend-slides), levado para um "pôster suíço": papel claro, tinta preta, **um bloco de cor forte por ato**, grid rígido, tipografia condensada enorme. Base: reveal.js (1280×720, `margin: 0`, `center: false`, `transition: 'none'`). A transição entre slides é o wipe do bloco de cor, feito pelo GSAP.

## 0. Arquivos

| Arquivo | Papel |
|---|---|
| `deck.css` | todos os tokens e layouts (os 13 tipos de slide + variantes) e o vocabulário dos diagramas |
| `deck.js` | motor de motion: entrada padrão, cenas, passos de ênfase, quiz, fluxo, glossário |
| `index.html` | os 6 slides de amostra (notas `<aside class="notes">` copiadas byte a byte do deck original) |
| `stress.html` | **teste de estresse** (24 slides): os layouts com o conteúdo real mais longo **e o mais curto** do deck (pergunta de 71 caracteres, título de abertura de 54 e de 61, cena de 141 + pergunta de 130, tópico de 1 e de 2 itens, tabela de 8 linhas, agenda de 17 itens em 7 \| 5 \| 5, figura redesenhada em 2 partes, figura baixa 680×160, fechamento longo com fim de ato e curto, glossário de 48 termos, sumário, como usar, gancho) |
| `audit.js` | auditoria de layout usada nos shots (texto < 20px, texto fora do quadro, painel > 580, **maior retângulo vazio**) — §5, passo 10 |
| `shots/` | 6 PNGs 1280×720 no estado final + `contato.png`; `shots/stress/` = os 24 slides do teste |
| `motion.webm` | ~50 s navegando pelos 6 slides (passos, quiz e cliques no fluxo, inclusive Envios) |
| `fonts/Archivo.ttf` | Archivo variável (OFL, `fonts/OFL.txt`) |

Dependências locais: `../../lib/dist/{reset,reveal}.css`, `reveal.js`, `../../lib/plugin/notes/notes.js`, `../../lib/gsap/{gsap,CustomEase,DrawSVGPlugin,MotionPathPlugin,SplitText}.min.js`. Nada de CDN.

---

## 1. Tokens

### 1.1 Cores: cor de ATO × cor SEMÂNTICA (nunca se misturam)

**Regra:** a cor do ato só identifica o ato (painel, faixa, chips, número-fantasma, régua do passo atual). Ela **nunca** carrega significado dentro de diagrama ou quiz. Dentro de diagramas e do quiz só existem preto, branco, papel, pedra e as 3 cores semânticas, e **nenhuma cor semântica é igual a uma cor de ato**.

Cor de ato (`.act-N` define `--act`, `--on-act`, `--act-deep`):

| Token | Valor | Ato (capítulos) | Tinta (`--on-act`) | Contraste medido |
|---|---|---|---|---|
| `--a1` | `#FFC400` amarelo | I · Preparar a mesa (00–04) | preta | 11,8:1 |
| `--a2` | `#2343E0` ultramarino | II · Ajustar cada canal (05–09) | branca | 7,1:1 |
| `--a3` | `#FF6B1A` laranja | III · Mixar para o palco e a sala (10–15) | preta | 6,6:1 |
| `--a4` | `#5B3FD0` violeta | IV · Guardar, gravar e crescer (16–22) | branca | 6,9:1 |
| `--a5` | `#111111` preto | Desfecho · O dia do evento (23–24) | papel | 16,7:1 |
| `--a6` | `#D8D3C8` pedra | Consulta (25–27) | preta | 12,7:1 |

`act = 1 if n<=4 else 2 if n<=9 else 3 if n<=15 else 4 if n<=22 else 5 if n<=24 else 6`

Cor semântica (só em diagramas e no quiz; sempre com um sinal que não depende de cor: ✓, ✕, rótulo "CLIP", legenda):

| Token | Valor | Significado | Tinta | Contraste |
|---|---|---|---|---|
| `--ok` | `#00A064` verde | certo, passa, recomendado | preta | 5,6:1 |
| `--bad` | `#D7263D` vermelho | errado, clip, **onde mais se erra** | branca | 5,0:1 |
| `--bad-ink` | `#B3172F` | vermelho usado como **texto** sobre papel | — | 6,0:1 |
| `--x32` | `#19B8D8` ciano | só X32/M32 | preta | 8,0:1 |
| `--warn` | `#FFC400` | só o segmento amarelo do medidor (convenção do aparelho), sempre dentro do painel preto | — | — |
| `--sig` | `#FFC400` + contorno preto 4px | ponto do sinal (MotionPath) | — | 11,8:1 contra preto |

Neutros: `--paper #F4F1EA` (fundo), `--ink #111` (texto e traço), `--ink-2 #4A4740` (secundário, 8,2:1 no papel), `--stone #D8D3C8` (grade, bloco neutro).

Consequências que resolvem as colisões da rodada anterior: o vermelho saiu dos atos (ATO III agora é laranja); o verde saiu dos atos (ATO IV agora é violeta); "só X32" virou ciano (o ATO II continua ultramarino); "onde mais se erra" usa o mesmo vermelho de "errado/clip" (mesmo significado: perigo). Legenda em fundo preto é sempre **texto branco + amostra de cor**, nunca texto vermelho (vermelho sobre `#111` dá só 3,8:1).

### 1.2 Tipografia (uma família, três larguras)

Archivo variável (`font-weight 100–900`, `font-stretch 62–125%`).

| Papel | stretch / peso | tamanho | entrelinha |
|---|---|---|---|
| Display `.d` (número de capítulo, "XR18", título de abertura, pergunta do quiz) | 62% / 900 | 52–520px (escalas abaixo) | .84 (.9 em 64px, .92 em 52px) |
| Título de tópico `.h` | 75% / 820 | 56px (44px em figura/tabela longa) | .98 |
| Corpo (`p`, `li`, alternativas, células, cards) | 100% / 420, negrito 760 | **28px** | 1.22 |
| Rótulo informativo `.lbl` (kicker, selo, "EM CENA", legendas) | 100% / 760, caixa alta, `letter-spacing .1em` | **20px** | 1.2 |
| Chips de compatibilidade, "CAP NN", abas do medidor, "SÓ LEITURA", fólio, rótulos de diagrama, nota da capa, termos do glossário, sumário | 600–820 | **20px** (legenda do fluxo 22px) | — |

**Piso:** nenhum texto informativo abaixo de 20px no palco 1280×720 (em SVG: tamanho em unidades × escala do SVG ≥ 20). Abaixo de 18px só o decorativo (`aria-hidden`: números 10–16 sob os faders da capa = 17px).

#### Escalas de tamanho por número de caracteres (o gerador escolhe a classe)

| Onde | Classe | Faixa de caracteres | Tamanho | Testado com (stress.html) |
|---|---|---|---|---|
| Pergunta do quiz `h3.d` | `q1` | ≤ 20 | 112px | "O que o automix faz?" (20) → 3 linhas |
| | `q2` | 21–36 | 88px | "O que faz o modo Sends on Faders?" (33) → 3 linhas |
| | `q3` | 37–52 | 64px | "Segundo Drew Brashler, como começar a montar a mix?" (51) → 4 linhas |
| | `q4` | ≥ 53 | 52px | "No rack do X AIR Edit aparece "OFF"…" (71) → 4 linhas |
| Título de abertura `h2.d` | — | ≤ 24 | 104px | "Low cut e equalizador" (21) |
| | `t2` | 25–44 | 84px | |
| | `t3` | 45–64 | 68px | "Insert, delay, pan, link e o roteiro completo do canal" (54), sintético de 61 → 3 linhas |
| Fechando `p.stmt` | `t0` | ≤ 80 | 88px | (frase curta: o tamanho **sobe**) |
| | — | 81–140 | 64px | 110 caracteres → 3 linhas; 140 → 4 linhas |
| | `t2` | > 140 | 48px | 231 caracteres → 4 linhas |
| Título da agenda `h3.d` | — / `t3` | ≤ 24 / > 24 | 84 / 64px | |
| Itens da agenda | `.few` | ≤ 7 itens | 36px, faixas iguais até y 664 | 7 itens (s15), 5 itens (s16, s17) |
| Definição do glossário | — | qualquer | termo 64px + definição 36px | |
| Título de figura/tabela longa | — | qualquer | 44px | 54 caracteres em 1 linha |

A pergunta fica num bloco ancorado embaixo (`.qcol`: `top 104`, `bottom 60`, `justify-content: flex-end`), então ela cresce para cima e nunca sai do quadro.

### 1.3 Grid e medidas fixas

12 colunas: margem 48, gutter 16, coluna 84. Pontos usados por todos os layouts:
- painel do ato (tópico, quiz, agenda, glossário): `x 0–528`, conteúdo `x 48–480`;
- painel largo (tópico `.wide`): `x 0–688`, conteúdo `x 48–640`;
- área do diagrama: `x 560–1232`, `y 40–660` (672×620); no `.wide`: `x 720–1232` (512×620); no `.narrow`: `x 464–1232` (768×620), painel `x 0–432`, conteúdo `x 48–400`;
- faixa do ato (figura, tabela longa): `y 0–112`, conteúdo `x 48–1232` a partir de `y 128`;
- fólio: `bottom 18`, 20px, alinhado à área do diagrama.
- **Limite de texto do painel: `getBoundingClientRect().bottom` do último `p`/`li` ≤ 580** (o número-fantasma `.chapno` começa em ~600).
- **Limite de vazio: o maior retângulo sem conteúdo < 30% do quadro** (276 480 px²; medido por `audit.js`, §2.14).

Sem cantos arredondados, sem sombras (inclusive dentro dos SVGs: `rect { rx: 0 }`). Réguas pretas de 6px separam blocos. Barra de progresso do reveal: 4px, preta.

---

## 2. Layouts (13 tipos do deck real + variantes)

Todo `<section>` recebe `L-<tipo>`, `act-N` e, quando tem cor de fundo, `<div class="bg wipe"></div>` como primeiro filho. Marcações de motion: `.k` (kicker), `.split` (título de display, linhas pelo SplitText), `.rise` (entra subindo), `.draw` (traço SVG desenhado), `.pop` (ponto/marca que salta no fim do desenho).

### 2.1 Capa — `L-cover act-5` (1 slide)
Esquerda em fluxo (`.ccol`, `x 44–764`, `y 78–692`): kicker com quadrado amarelo; `h1` em 3 spans (64 / 264 / 44px, "XR18" em preto); subtítulo 28px; chip "Todas as 13 mesas" (preto com texto papel); nota de rodapé 20px empurrada para o pé (`margin-top: auto`). Direita: bloco preto `x 800–1280` com 16 faders (posições da arte original); os canais 4 e 10 em amarelo, oscilando ±12px.

### 2.2 Abertura de capítulo — `L-opener` (28 slides)
- Slide inteiro na cor do ato.
- **Coluna esquerda em fluxo** (`.lcol`, `x 44–728`, `top 40` até o pé): kicker → título (escala 104/84/68) → chips → número do capítulo 520px. O número fica num `.numwrap` com `flex: 1` e `overflow: hidden`: título longo empurra o número para baixo (ele só é mais cortado), nunca sobrepõe.
- **Coluna direita em fluxo** (`.rcol`, `x 760–1232`, `y 120–580`, `gap 16`; começa em 120 para equilibrar com o mapa no pé): card **Em cena** (papel, visível desde a entrada) e card **Pergunte à turma** (preto, rótulo amarelo). O card aparece na entrada com a **linha-guia** `p.ph` "? — pergunte antes de avançar" (papel `#BDB6A8`, itálico); a pergunta (`p.fragment`) ocupa a mesma célula (`.qa`, grid 1×1) e, quando entra, a linha-guia some — o card nunca fica vazio nem muda de altura. Pior caso real (cena 141 + pergunta 130 caracteres) termina em y = 607 (medido; o mapa começa em 616).
- Mapa dos 28 capítulos no pé da coluna direita (`bottom 40`), cada marcador na cor do seu ato; o atual com 34px de altura.
- **O gerador remove o `<strong>Em cena.</strong>` / `<strong>Pergunte à turma.</strong>` inicial** quando usa o `.lbl` (o texto fica só uma vez).

### 2.3 Tópico + diagrama — `L-topic` (225 slides)
- Painel do ato `x 0–528`: selo da fonte (`.pb` "Manual" ou "Cursos e tutoriais") + número da seção; título `.h` 56px; chips; texto 28px (`ul.pts` com marcador quadrado de 12px; o 1º item terminado em ":" vira `li.lead`); número-fantasma do capítulo no pé.
- Diagrama protagonista `x 560–1232` (672 de largura). Diagramas "de aparelho" (medidores, tela da mesa) em painel preto; gráficos (curvas, eixos) direto no papel.
- **Escolha da variante por medida** (o gerador renderiza e mede, como o `split()` atual). Testa na ordem e fica com a primeira que passa:

| Ordem | Medida do último `p`/`li` (`getBoundingClientRect().bottom`) | Variante | Diagrama |
|---|---|---|---|
| 1 | ≤ 460 com o painel estreito (conteúdo 352px) | `L-topic narrow` (painel `x 0–432`) | **768×620** |
| 2 | ≤ 580 com o painel normal (432px) | `L-topic` | 672×620 |
| 3 | ≤ 580 com o painel largo (592px) | `L-topic wide` (painel `x 0–688`) | 512×620 |
| 4 | > 580 mesmo com 592px | dividir em partes de itens iguais; **cada parte volta ao passo 1** (a parte curta vira `narrow`); kicker ganha "1/2", "2/2"; a 2ª parte pode usar o diagrama-tema seguinte | — |

  Medido nos 225 tópicos reais na rodada anterior: 97 cabem no normal, 70 no largo, 58 precisam de 2 partes (maior = 770) → 283 slides de tópico (+58). A regra 1 (estreito) não muda a contagem: ela só redistribui largura quando o texto é curto (testado em `stress` s07 com 1 item e s09 com 2 itens).
- **O diagrama automático preenche a área inteira**: `div.stage.vz` tem `height: 620px` e é coluna flex; a legenda `div.vcap` em cima e o `svg.viz` com `flex: 1` embaixo, escalado pela altura (`preserveAspectRatio` padrão). Os 75 diagramas do `slides_viz.py` têm viewBox 400×(300–320): no estreito ficam ~700×560, no normal 672×530. Nunca deixar o diagrama na altura natural no topo da área (era o "45% da área" da rodada anterior).
- O texto do painel está **sempre na tela**. Os fragments viram **passos de ênfase**: o gerador troca `li.fragment` por `li[data-step="k"]` (k = 1, 2, …) e acrescenta, fora do painel, um `<i class="fragment step"></i>` por passo. No passo k, o item k ganha uma faixa na tinta do painel e o texto vira a cor do ato (`.cur`); o diagrama muda junto quando a cena tem estado.
- Exemplo: `#s12-1-1` (Telas de medidores) com a cena `meters`.
- **Ênfase do passo**: `deck.js` acrescenta ao item um `span.hl[aria-hidden]` com a faixa (`.hlbg`, tinta do painel) e, dentro dela, uma cópia do texto na cor do ato (`.hltx`, com o mesmo `padding-left` do item e o marcador quadrado). O texto original nunca muda de cor (ver §4.3).

### 2.4 Tópico + tabela
**Até 3 linhas → tabela transposta** sob o gráfico (exemplo `#s6-2-1`): gráfico 672×360 em `y 40–400`; tabela em `y 412–664`. Cada linha vira uma coluna (3 colunas de 208px, gap 24): régua preta de 6px, valor `.hz` 52px (62%/900), fonte 28px negrito, observação 28px `--ink-2`. A coluna ativa ganha a régua na cor do ato. Legenda da tabela 20px sem caixa alta. Se a tabela tem colunas Fonte/Valor/Quem: valor → `.hz`, fonte → `.src`, quem → `.note`.

**4 linhas ou mais → `L-table`** (slide próprio, depois do tópico): faixa do ato `y 0–112` com kicker e título 44px; tabela na largura toda (`x 48–1232`, a partir de `y 140`): cabeçalho 20px caixa alta sobre régua preta de 6px; células 28px, 1ª coluna em negrito, coluna de valor em 75%/820, linhas separadas por régua de 2px pedra. **Divisão por medida: a última linha termina em y ≤ 664**; continua em outro slide "tabela 2/2" repetindo o cabeçalho. A tabela de 8 linhas do HPF original cabe em 2 slides (5 + 3 linhas, `shots/stress/s10–s11`). **Conteúdo curto:** se a última linha termina antes de y 560, a tabela ganha `.fill` (`height: 524px`, vai até y 664): as linhas se distribuem e o texto fica no topo de cada linha.

### 2.5 Quiz — `L-quiz` (25 slides)
- Painel do ato `x 0–528`: kicker; "?" fantasma 760px em `--act-deep` **só com o gancho** (`clip-path: inset(0 0 35% 0)` corta o ponto, que antes aparecia como uma mancha entre as linhas da pergunta); pergunta `.d` ancorada embaixo, escala q1–q4 (1.2). O gancho termina em y ≈ 455; a pergunta mais longa (q4, 4 linhas) começa em ≈ 455.
- Coluna direita em fluxo (`x 576–1232`, `y 48–660`, `gap 16`): 3 botões (mín. 120px de altura, borda preta 3px, letra num quadrado preto de 76px, texto 28px; até 89 caracteres = 3 linhas) e a explicação numa barra preta logo abaixo (`p.fb` dentro de `div.fbwrap[aria-live=polite]`, com o espaço reservado).
- **O `div.viz` do quiz é descartado**: nos 25 quizzes ele é o mesmo desenho genérico `quiz()` (um "?" e três caixas A/B/C), que aqui é substituído pelo "?" de 760px e pelos botões reais.
- Comportamento: o 1º clique trava o grupo (`.opts.done`, `aria-disabled` em todos, `aria-pressed` no escolhido, texto oculto "resposta certa/errada"); a certa sempre aparece em verde com ✓, a escolhida errada em vermelho com ✕ (texto branco). Voltar ao slide reinicia o quiz.

### 2.6 Interativo — `L-flow` (2 slides)
- Diagrama `x 40–752` em "cobra": linha 1 Fonte → Gate, linha 2 Insert → Delay (direita para esquerda), linha 3 Fader → Main; Envios abaixo do Fader (tracejado). Blocos 152×96: "CAP NN" 20px no topo, nome 28px no pé; **o caminho do sinal passa pelo meio do bloco, entre os dois textos**.
- `circle.sig` é o **último elemento do SVG** (fica por cima dos blocos). Um clique no ponto vale para o bloco embaixo dele.
- Cores: vermelho = onde mais se erra (Ganho, Fader, texto branco); ciano = só X32/M32 (Delay); pedra = Envios. **O bloco ativo mantém o fundo semântico** e ganha borda de 8px na cor do ato (`.blk.on rect.box { stroke: var(--act); stroke-width: 8 }`) — única exceção à regra "cor de ato fora dos diagramas": é estado da interface, o mesmo papel da faixa do passo atual. Foco do teclado = borda tracejada. Legenda 22px.
- Painel do ato à direita (`x 784–1280`): kicker "Diagrama interativo · toque num bloco", título 60px, painel de detalhe (`aria-live`) com nome 40px + texto 28px + link "Ver capítulo N →". **Estado inicial: o 1º bloco (Fonte) já selecionado e o painel já preenchido** (no HTML e no `reset()`), para o painel nunca começar vazio.
- Blocos são `<g class="blk" role="button" tabindex="0" aria-pressed>` com `data-t / data-d / data-c / data-p` (posição 0–1 do centro do bloco no tronco `path.sigpath`). Envios fica fora do tronco: tem `path.sndp` invisível (`d="M76 420 V562 H172"`, do centro do Fader ao meio do bloco Envios, `data-from` = posição do Fader no tronco) e o ponto chega lá pelo Fader. Pontas de seta são `<g class="arw" data-p>`. O ramo tracejado visível (`path.sndln`) entra com `scaleY`, não com DrawSVG (que apagaria o tracejado).

### 2.7 Figura — `L-fig` (28 slides)
Faixa do ato `y 0–112` (kicker à esquerda, chips à direita, título 44px). Figura em `.figbox` de `x 48–1232`, `y 128` até a legenda, escalada para caber (`preserveAspectRatio` padrão, centralizada na vertical). Legenda `p.figcap` 28px sobre régua preta, no pé (`bottom 32`). Escala: `s = min(1184/w, H/h)`, com H ≈ 490 (legenda de 1 linha) ou 455 (2 linhas).

O gerador calcula, para cada figura, `h/w` e o **texto mínimo** `min(font-size) × s` e escolhe:

| Condição | O que fazer | Figuras (das 28, medido) |
|---|---|---|
| texto mínimo ≥ 20px e `h/w` ≥ .35 | `L-fig` normal | 13 |
| `h/w` < .35 (figura baixa: a largura trava a escala em 1,74 e sobra altura) | **`L-fig short`**: figura na largura máxima, centralizada na vertical, e a legenda vira a frase do slide (`.figcap` 40px, 75%/720). Testado com 680×160 (`stress` s14: maior vazio 17,8%) | 5: meta de ganho (160), firmware (190), idiomas (200), MIDI (210), gravação multipista (230) |
| texto mínimo < 20px | **redesenhar como `fig2`** (abaixo); se tiver grupos independentes (colunas, famílias), **um slide por grupo** com "1/2", "2/2" no kicker | 10: irmãos (13,4px), REMOTE (16,9), compressor (16,8), matrizes (16,8), sete erros (16,5), mistura de cada músico (17,3), envio × insert (18,0), show típico (19,0), mapa do curso (19,6), insert (19,7) |

**`fig2` — gramática da figura redesenhada** (exemplo pronto: "Quem é irmão de quem", `stress` s12–s13): `<svg class="viz fig2" viewBox="0 0 1184 460">` (1 unidade = 1px do palco, sem escala, cabe em `y 128–594` com legenda de 2 linhas); faixa de cabeçalho preta 44–48px com texto 22px branco caixa alta; caixas de 54–60px de altura com nome 28px (75%/820); conectores `ln2`/`lnd`/`lnd2` com as setas `#ah`; observações 24px em `--ink-2` numa coluna à direita (`x 744`); barra de aviso `bxr` 44px com texto 22px branco. Nenhum texto abaixo de 20px. Caixa escura (`bxo`) recebe texto branco automaticamente (§3.2).
**Legenda que cita cor** muda junto com a paleta: o laranja das caixas "apelido" do original é preto aqui, então "Laranja = …" vira "Preto = …".

### 2.8 Agenda do capítulo — `L-agenda` (27 slides)
Painel do ato `x 0–528`, coluna flex `y 40–680`: rótulo "CAPÍTULO NN · NESTE CAPÍTULO" no topo; **número do capítulo em tinta** (`.agnum .d`, 62%/900, cor `--on-act`) preenchendo o meio; **título `.d` 84/64px ancorado embaixo**. O número fica numa moldura `flex: 1` com `container-type: size` e `font-size: min(340px, 118cqh)`: título longo diminui o número, nunca sobrepõe. (Sem número-fantasma: o painel não fica mais vazio entre o título e o pé.)
Direita `x 576–1232`: cabeçalho da parte (selo "Manual" / "Cursos e tutoriais" + "O que diz o manual" / "O que ensinam os cursos"), itens como links: número 20px em coluna de 84px + título 28px, régua de 2px pedra. **Divisão por medida: último item com bottom ≤ 664**; divide primeiro na troca de parte e, se uma parte não couber, em metades iguais com "1/2", "2/2" no cabeçalho (cap. 01, 17 itens → 7 | 5 | 5).
**Conteúdo curto (≤ 7 itens): `.aglist.few`** — a lista vai até y 664 (`bottom: 56px`) em faixas iguais (`a { flex: 1 1 0 }`), texto 36px, número 24px em coluna de 92px, régua de 6px pedra. Se com 36px o último item passar de 664, usar 32px (não ocorreu nas agendas testadas).

### 2.9 Fechando — `L-fecha` (25 slides)
Papel; faixa de 16px na cor do ato no topo. Tudo numa coluna flex (`.fcol`, `x 44–1232`, `y 52` até 168 do pé com fim de ato ou 48 sem): rótulo "FECHANDO · CAPÍTULO NN" 20px → **moldura `.fnum` (`flex: 1`)** com o número do capítulo na cor do ato (62%/900, `min(300px, 118cqh)`, pedra escura no ato 6) e, à direita, o **mapa de progresso** (28 marcadores: capítulos vistos cheios na cor do seu ato, os que faltam só contornados, o atual alto; rótulo "CAPÍTULOS 00–27 · N DE 28") → **frase ancorada embaixo**, logo acima do botão (75%/720; escala por caracteres §1.2: ≤ 80 → 88px, ≤ 140 → 64px, > 140 → 48px e a seção ganha `.long`) → botão preto "PRÓXIMO CAPÍTULO · NN (na cor do ato; amarelo no ato 5) · título →" alinhado à direita. A frase curta não deixa mais meio slide vazio: o número e o mapa ocupam o alto (`stress` s19, 110 caracteres: maior vazio 25%).
Quando o capítulo fecha um ato (`div.actend`), uma faixa de 132px no pé na **cor do próximo ato** com "FIM DO ATO I · …" (20px) e "→ Ato II: …" (28px negrito). O gerador remove o `<strong>Fechando.</strong>` inicial.

### 2.10 Gancho — `L-hook` + `L-acts` (2 slides → 4)
O gancho original tem cena, pergunta, parágrafo e 4 cards de ato (≈ 650 caracteres): não cabe a 28px em um slide. O gerador divide:
- `L-hook` (fundo preto): kicker, título `.d` 156px numa linha só (largura 1188), `p.big` 48px em 700px; card "Pergunte à turma" em papel ancorado embaixo à direita (`x 776–1232`, `bottom 48`), texto como fragment.
- `L-acts` (papel): parágrafo de abertura 28px no topo; 4 colunas `y 200–680`, cada uma na cor do seu ato, com título negrito, texto 28px e o numeral romano 150px em `--act-deep` saindo pelo pé.

### 2.11 Glossário — `L-gloss` (2 slides, `data-scene="gloss"`)
Painel `act-6` `x 0–528`: kicker, título, chips e, **logo abaixo dos chips** (`margin-top: 30px`), o painel da definição (`aria-live`; régua de 6px, termo 64px 75%/820 + definição 36px). **O 1º termo já começa selecionado** (`reset()` da cena), então o painel nunca abre vazio. Direita: grade de 3 colunas × 16 linhas de botões (`x 560–1232`, `y 40–680`), 20px/760, régua preta de 6px à esquerda; termo ativo invertido. 48 termos cabem; a lista de 9 termos ocupa as 3 primeiras linhas da mesma grade.

### 2.12 Sumário — `L-toc` (1 slide)
Título `.h` 56px + "TOQUE PARA IR AO CAPÍTULO"; grade de 4 colunas × 7 linhas (`x 48–1232`, `y 100–684`, preenchida por coluna), cada capítulo com régua de 6px na cor do seu ato, número `.d` 34px e título 20px (até 3 linhas).

### 2.13 Como usar — `L-howto` (1 slide)
Título 56px; 7 linhas em grade de 2 colunas (`236px | resto`): à esquerda o sinal como selo de 20px caixa alta com borda preta, à direita a explicação 28px, régua de 2px pedra.

### 2.14 Conteúdo curto: preenchimento mínimo por layout
As regras de divisão (§2.3, 2.4, 2.8) cuidam do conteúdo longo; estas cuidam do curto. **Critério único: o maior retângulo vazio do slide < 30% do quadro** (grade de 16px; conteúdo = linhas de texto, formas SVG visíveis e caixas com fundo próprio; o painel do ato e os números-fantasma `.chapno`/`.qmark` **não** contam como conteúdo). `audit.js` mede e imprime `empty N% [x y w×h]`.

| Layout | Quando é "curto" | Regra de preenchimento | Medido (stress / amostra) |
|---|---|---|---|
| Tópico (`L-topic`) | último item ≤ 460 no painel estreito (1–2 itens curtos) | variante `narrow`: diagrama 768×620 escalado pela altura; painel 432 | s07 (1 item) 12,9%; s09 (2 itens) 10,3% |
| Diagrama automático | sempre | `stage.vz` 620px de altura, SVG com `flex: 1` (nunca na altura natural) | s08 17,5% |
| Figura (`L-fig`) | `h/w` < .35 | `short`: largura máxima, centralizada, legenda 40px | s14 17,8% |
| Tabela (`L-table`) | última linha < 560 | `.fill`: tabela até y 664 | s10 9,0%; s11 12,0% |
| Agenda (`L-agenda`) | ≤ 7 itens | `.few`: faixas iguais até y 664, 36px, régua 6px; número do capítulo em tinta no painel | s15–s17 12,7% |
| Fechando (`L-fecha`) | frase ≤ 140 caracteres | escala inversa (≤ 80 → 88px) + número do capítulo e mapa de progresso no alto + frase ancorada no botão | s19 25,3%; s18 9,7% |
| Glossário (`L-gloss`) | definição curta | definição logo abaixo dos chips, 64/36px; 1º termo selecionado | s22 18,5% |
| Abertura (`L-opener`) | antes do fragment | linha-guia no card da pergunta; cards a partir de y 120 | amostra 2: 19,4% |
| Interativo (`L-flow`) | antes do 1º clique | 1º bloco selecionado, painel preenchido | amostra 6: 10,7% |
| Quiz (`L-quiz`) | pergunta curta (q1) | pergunta ancorada embaixo, gancho do "?" em cima | amostra 5: 23,0% |
| Gancho (`L-hook`) | — | título numa linha (156px), texto 48px | s20 20,1% |

Os 6 slides de amostra e os 24 do stress passam (maior: 25,3%).

---

## 3. Diagramas

### 3.1 Estado neutro útil (n = 0)
Todo diagrama com cena já mostra algo didático na entrada; os passos só movem a ênfase. O **HTML já é o estado n = 0** e o `deck.js` aplica `state(sec, 0)` em todas as cenas antes do 1º paint (`html.pre` esconde o palco até o 1º `enter()`). Nada aparece para depois sumir.
- `meters`: tela METERS com cabeçalho, abas contornadas e todos os medidores em nível baixo (`data-idle`, só verde) "respirando". Passo 1: selo "SÓ LEITURA" preenche; 2: aba CHANNEL + Ch1–3 sobem aos níveis reais + CLIP; 3: MIX BUS + Bus/L/R; 4: AUX/FX + FX 1; 5: RTA. Grupos já acesos continuam acesos; só a aba do passo atual fica cheia.
- `hpf`: curva em 100 Hz com a zona cortada (hachura preta 45°, sem cor) e a tabela inteira visível. Passo 1 (benefícios): a zona pisca; 2 (bumbo): curva vai a 30 Hz, faixa citada 20–40 Hz (pedra com bordas pretas); 3 (caixa): 100 Hz; 4 (voz): faixa 80–120; 5 (método): sobe até 170 Hz e volta para 112 Hz. **A legenda "◀ graves cortados" fica abaixo do eixo**, presa ao início da zona, com uma barra preta que acompanha a zona (`scaleX` igual) — nunca fica em cima da faixa ou da curva.
- `flow`: caminho, blocos e legenda completos.

### 3.2 Diagrama sem cena (os 75 do `slides_viz.py` e as figuras): restilização + entrada automática
Não é preciso redesenhar as 75 funções. O gerador põe `class="viz"` (figura: `class="viz fig"`) no `<svg>` e o `deck.css` reestiliza as classes que elas já emitem; o `deck.js` monta a entrada pela classe de cada elemento:

| Classes emitidas | Estilo | Entrada (t a partir de .45 s) |
|---|---|---|
| `.axis .grid .tick` | preto 2 / pedra 1 | `drawSVG` 0→100%, .5 s, t+0 |
| `rect.bx .panel .wedge .knob .person .track .bar*` | branco/papel com traço preto 2, sem arredondar | `.rise` em ordem de leitura (y, depois x), stagger total .4, t+.1 |
| `rect.bxo .bxd` | preto, texto branco (o JS marca o texto dentro como `.on-dark`; a medição só funciona com o slide visível, então `prepViz` tenta de novo a cada entrada até medir — antes o "X16" saía preto sobre preto) | idem |
| `rect.bxg` / `.bxr` / `.bxb` | `--ok` / `--bad` (texto branco) / `--x32` | idem |
| `.zg .zy .zr .zgr .mk2` (zonas) | verde/amarelo/vermelho translúcidos, pedra | `scaleX` 0→1 da esquerda, .6 s, t+.3 |
| `line.ln .ln2 .curve .curve3 .curve4 .needle` | preto 2,2–3,6; `curve4` vermelho | `drawSVG` 1.0 s, stagger .3, t+.35; **pontas de seta (`marker`) escondidas até a linha terminar** (classe `.drawing` no SVG) |
| `.lnd .lnd2 .lnx .thr .ctl .sep .curve2 .zone .frame` (tracejados) | tracejado preto; `lnx`/`thr` vermelho | `autoAlpha`, .4 s, t+.6 (DrawSVG apagaria o tracejado) |
| `text` | Archivo; `.b` 800; `.sm` `--ink-2`; `.lblr` `--bad-ink` | `autoAlpha` + `y 8`, stagger total .4, t+.45 |
| `.dot .cap .capo .capd .mk text.ok text.xr` | ponto preto com contorno papel; ✓ verde, ✕ vermelho | `.pop` (`scale .6→1`, `back.out(2)`) **no fim do desenho** (t+1.65) |
| `text.vt` (título interno) | — | vira `div.vcap` HTML de 20px acima do diagrama |

Marcadores: a página precisa de um `<svg>` oculto com `<marker id="ah">` (preto) e `id="ahr"` (vermelho) — ver o topo do `<body>` de `stress.html`.

Escala e piso de texto: SVG de 400 de largura no diagrama de 672px → escala 1,68 (texto 15 → 25px; `.sm` 13 → 21,8px). Na variante larga (512px) a escala é 1,28 e o CSS sobe todo texto do diagrama para 16 unidades (20,5px).

### 3.3 Diagramas com cena (redesenhados à mão)
`meters`, `hpf` e `flow` estão no `index.html`. Para os outros temas que pedem cena (ganho −18, gate abrindo, compressor, pontos de captação, crossover…), o padrão é o mesmo: SVG em 672×620 (ou 672×360 + tabela), estado n = 0 completo no markup, `state(sec, n, anim)` só com `transform`/`opacity` e `data-step`/`data-row` ligando passo a elemento.

---

## 4. Motion

### 4.1 Identidade ("corporate decidido")
| Constante | Valor |
|---|---|
| Ease assinatura (80%) | `swiss` = `cubic-bezier(.2,0,0,1)` |
| Entrada | `enter` = `cubic-bezier(.05,.7,.1,1)` |
| Saída | `exit` = `cubic-bezier(.3,0,1,1)` |
| Durações | quick .2 · std .45 · slow .8 · draw 1.0 |
| Overshoot | só em feedback: `back.out(2–3)` em pop, CLIP, acerto do quiz |
| Stagger | total ≤ .45 s |

Só `transform` e `opacity` (no SVG: `x`, `scaleX/Y`, `drawSVG`, `motionPath`). Nenhum tween é criado com alvo vazio (`ft()`), então não há aviso "GSAP target not found" no console.

### 4.2 Entrada (`slidechanged` → `enter(sec)`)
1. `reset()` da cena e `state(sec, 0)` sem animar (volta ao neutro).
2. Timeline:

| t (s) | Elemento | Animação |
|---|---|---|
| 0 | `.wipe` | `scaleX 0→1`, .6, `swiss` (é a transição entre slides) |
| .18 | `.k` | `x −24→0` + `autoAlpha` |
| .2 | número do capítulo na agenda/fechando (`.agnum .num`, `.fnum .num`) | sobe de dentro da moldura: `yPercent 45→0`, .9, `enter` |
| .22 (+.1 por título) | `.split` | linhas sobem da máscara: `yPercent 150→0`, .7, stagger .07. A máscara (`.ln-mask`) tem folga de **.12em em cima e .26em embaixo**: com a entrelinha .84 do display 62%/900, menos que isso corta o descendente do "q"/"ç" durante a subida ("equalizador" virava "eaualizador") |
| .35 | `.draw` | `drawSVG 0→100%`, 1.0, stagger total .4 |
| .4 | `.rise` + texto do painel (`.side > ul`, `.side > p`) | `y 24→0` + `autoAlpha`, stagger total .4 |
| fim da última linha do título − .05 | `.chips.rise` | `y 16→0` + `autoAlpha`, .35 (antes entravam translúcidos por cima do título) |
| fim do desenho (1.35; .5 sem `.draw`) | `.pop` | `scale .6→1` + `autoAlpha`, `back.out(2)` |
| .45 | `svg.viz` | entrada automática (3.2) |
| .5 | passos já visíveis (voltando de trás) | `state(n)` com o n lido **na hora** |
| 1.1 | camada ambiente da cena | faders/medidores "vivos" |

### 4.3 Passos (`fragmentshown` / `fragmenthidden`)
`n` = fragments visíveis. A cena recebe `state(sec, n, true)` e o item `[data-step=n]` recebe a ênfase por **máscara em contramovimento**: a faixa `.hlbg` (tinta do painel, `overflow: hidden`) vai de `xPercent −101 → 0` e a cópia do texto `.hltx` (cor do ato) vai de `x +largura → 0`, os dois em .32 s `swiss`. A cópia fica parada na tela; só a borda da faixa varre o item. Em qualquer quadro, a parte já varrida mostra texto na cor do ato sobre a faixa e o resto mostra o texto original sobre o painel — **o texto nunca some** (na rodada anterior a faixa cobria o texto por 150–250 ms porque a cor só trocava no fim). O item anterior sai varrendo para a direita (.22 s, `exit`). Só `transform`. Fragments com conteúdo (a pergunta da abertura) entram com `autoAlpha` + `y 20` (ou `x 56`), .45 s; a linha-guia do card some no mesmo instante (CSS `.fragment.visible + .ph`).

### 4.4 Cenas
- **cover**: trilhos crescem do centro para fora; capas sobem até a posição (.9 s, `power3.out`); as 2 amarelas oscilam ±12px (2,4 s, `sine.inOut`).
- **opener**: número sobe 45% (.9 s); marcadores do mapa crescem (stagger .012), o atual com pop; cards entram da direita.
- **meters**, **hpf**: 3.1. Na entrada do HPF a zona cresce junto com o desenho da curva; o ponto "Freq do corte" só aparece quando a curva chega nele.
- **flow**: o caminho se desenha (1.6 s, linear); cada ponta de seta e cada bloco aparecem quando a linha chega neles; o ramo tracejado cresce com `scaleY`; em 2.0 s o ponto amarelo percorre o canal inteiro **por cima dos blocos** (MotionPath, 2,6 s) e cada bloco pulsa quando ele passa; em 4,62 s ele sai pelo Main (`scale .4` + fade, .2 s) e em 4,86 s reaparece **parado no bloco selecionado** (Fonte, ou o que foi tocado durante o percurso) com `back.out(3)`. No clique, o ponto anda até o bloco pelo caminho: no tronco (.2 s + 1,4 s × distância, `swiss`) ou, para Envios, tronco até o Fader e depois o ramo `.sndp` (`power2.in` + `power2.out`); o painel troca o texto (sai .15 s, entra .35 s) e o bloco dá um pop de 6%.
- **quiz**: preenchimento entra da esquerda (`scaleX`, .45 s), ✓/✕ se desenham (DrawSVG .3 s); errado treme (−14, 12, −8, 5, 0; .38 s); certo pulsa 3%; explicação sobe 30px.

### 4.5 Movimento reduzido
`gsap.matchMedia('(prefers-reduced-motion: reduce)')` liga `RM`: sem timeline de entrada nem ambiente; cada cena e cada passo vão direto ao estado (a faixa do passo aparece inteira); o quiz aplica `scaleX 1` no preenchimento antes de sair (certo verde, errado vermelho — testado); o ponto do fluxo **aparece parado na Fonte na entrada** e salta para o bloco clicado, inclusive Envios (testado: `["1","Fonte / patch"]` → `["1","Envios (Aux / Mix bus / FX)"]`).

---

## 5. Como aplicar no `tools/build_slides.py`

1. `<html class="pre">`; no `<head>`: `reset.css`, `reveal.css`, `deck.css` (sem `theme/white.css`). No fim do `<body>`: reveal, notes, os 5 GSAP e `deck.js`. Copiar `fonts/`, `deck.css` e `deck.js` para `07-slides/`. Incluir o `<svg>` oculto com os markers `#ah`/`#ahr`.
2. Para cada `<section>`: `act-N` + `L-<tipo>` (§2) + `data-scene` quando houver cena; `<div class="bg wipe"></div>` primeiro; kicker `.k`, títulos de display `.split`, textos fixos/chips `.rise`.
3. Chips: `<span class="chip all"><span>Todas as 13 mesas</span></span>`; chips de modelo ficam `<span class="chip">X32</span>`.
4. Classes de tamanho por caracteres (§1.2): quiz `q1–q4`, abertura `t2/t3`, fechando `t2`, agenda `t3`.
5. Remover o `<strong>` inicial redundante de cena, pergunta e fechamento.
6. Tópicos: `li.fragment` → `li[data-step]` + `<i class="fragment step"></i>` por passo; escolher `L-topic` / `L-topic wide` / divisão medindo y ≤ 580 (§2.3); tabelas ≤ 3 linhas transpostas, ≥ 4 em `L-table` dividida em y ≤ 664 (§2.4); agenda dividida em y ≤ 664 (§2.8); gancho em `L-hook` + `L-acts`.
7. `slides_viz.py`: só acrescentar `class="viz"` no `<svg>` (os nomes de classe atuais já são o vocabulário do §3.2); quiz descarta o `div.viz`.
8. Notas `<aside class="notes">`: sem mudança.
9. Reveal: `{ width: 1280, height: 720, margin: 0, center: false, controls: false, progress: true, transition: 'none' }` (já está no `deck.js`).
10. Verificar cada slide no estado final (todos os fragments) com `audit.js` e reprovar se houver: texto informativo < 20px; texto fora de 1280×720; painel do tópico > 580; **maior retângulo vazio ≥ 30% do quadro** (§2.14). Conferir também console limpo, os quadros de 60/150/400 ms de cada entrada e de 150 ms de cada passo, e o modo `reducedMotion: 'reduce'`.
11. Variantes por medida (o gerador renderiza antes de escrever): tópico `narrow`/normal/`wide`/dividir (§2.3), tabela `.fill` (§2.4), figura `short`/`fig2` (§2.7), agenda `.few` (§2.8), fechando `t0`/`t2`/`.long` (§2.9).

### Pendências conhecidas
- **Figuras:** a regra e a gramática `fig2` estão no §2.7 e o redesenho foi feito e validado só para "Quem é irmão de quem" (2 slides, `stress` s12–s13, texto 20–28px). **As outras 9 figuras com texto < 20px** (lista no §2.7) ainda precisam ser redesenhadas da mesma forma quando o gerador for aplicado. As 5 figuras baixas só precisam da classe `short`.
- A figura "meta de ganho" original tem os rótulos "picos 3 a 6 dB acima" e "clip" colados; no stress o primeiro foi movido para x 505 (o gerador deve fazer o mesmo ao copiar a figura).
- A divisão de tópicos acrescenta 58 slides; tabelas e agendas longas acrescentam alguns mais.
- Testado só no Chromium (Playwright).
