# Direção visual 1: Palco escuro

O slide é um palco à noite e a mesa de som é o cenário. Cor forte só aparece onde há sinal (LED, medidor) ou numa etiqueta de verdade (fita de nome da família, marca). Tudo que se move tem um motivo didático: o sinal anda, o medidor sobe, o diagrama se desenha e o fragment acende a parte do desenho de que ele fala.

**Referência viva:** `index.html`, com 14 slides:
- **1 a 7: amostras.** Capa, abertura do cap. 06, medidores, HPF com tabela, quiz do gate, caminho do sinal e **o slide 9.1.1 (Insert) com o SVG real do `slides_viz.py` dentro da carcaça de 3 faixas**. Esse SVG é a saída de `python3 ref_dg.py s9-1-1`, sem retoque.
- **8 a 14: anexo.** Os outros tipos do deck com conteúdo real: agenda e figura do cap. 06, fechamento do cap. 06, gancho de abertura, glossário 27.2.1, sumário 1/2 e "Como usar". Cada um tem CSS e controlador prontos para copiar.

**Ferramentas desta pasta:**
| Arquivo | O que faz |
|---|---|
| `ref_dg.py` | Referência executável da transformação do SVG (2.3.2) e da carcaça. `python3 ref_dg.py` checa os 61 diagramas; `python3 ref_dg.py <id>` imprime a carcaça de um slide do deck real. |
| `check_dg.mjs` | Roda os 61 diagramas na carcaça do slide 7 e mede faixas, escala, menor texto em px e texto que vaza da caixa. Gera `shots/diagramas-61.png`. Resultado atual: 1,46× a 1,87×; menor texto **20,4 px**; nenhum vazamento. |
| `shoot.mjs` | `shots/NN-*.png` (estado final), `shots/inicio/` (antes dos fragments), `shots/t150/` (150 ms depois da troca), `contato.png`, `contato-anexo.png` e `motion.webm`. |

Todos os `<aside class="notes">` são os originais do deck, byte a byte.

Inventário do deck real (`07-slides/index.html`, 367 `<section>`), coberto por inteiro:

| Tipo | Qtd | Seção | Amostra |
|---|---|---|---|
| `topic hv` com diagrama | 204 | 2.3 | slide 7 (gerado) e slide 3 (feito à mão) |
| `topic hv` com tabela | 21 | 2.4 | slide 4 |
| `opener` | 28 | 2.2 | slide 2 |
| `figslide` | 28 | 2.7 | slide 9 |
| `agenda` | 27 | 2.8 | slide 8 |
| `quiz hv` | 25 | 2.5 | slide 5 |
| `fecha` | 25 | 2.9 | slide 10 |
| pilhas verticais (agrupam o capítulo) | 28 | não recebem controlador | |
| `hook` | 2 | 2.10 | slide 11 |
| `interactive` | 2 | 2.6 | slide 6 |
| `gloss` | 2 | 2.11 | slide 12 |
| `cover`, `toc`, `howto` | 1 cada | 2.1, 2.12, 2.13 | slides 1, 13, 14 |

---

## 1. Tokens

### 1.1 Cores
| Token | Valor | Uso | Contraste |
|---|---|---|---|
| `--bg-0` | `#060708` | fundo atrás de tudo | |
| `--bg-1` | `#0b0e11` | tela dos diagramas (LCD) | |
| `--bg-2` | `#12161b` | carcaça, cartões, teclas | |
| `--bg-3` | `#1a2027` | elemento elevado (letra do quiz, caixa "destino") | |
| `--line` / `--line-2` | `#28313b` / `#3a4552` | divisórias e bordas; LED apagado `#1c232b` | |
| `--ink` | `#eef2f5` | títulos, palavra-chave | 17:1 |
| `--ink-2` | `#b4bdc7` | corpo | 10:1 |
| `--ink-3` | `#8a95a1` | rótulos, eixos, rodapé, marcador de bullet, setas de diagrama | 6,4:1 no `--bg-1` |
| `--accent` | `#ff9a2e` | **marca** e **"onde mais se erra"**; valores (Hz, dB); link; passo atual | 9:1 |
| `--led-green` | `#2fe07b` | **só sentido de medidor:** sinal presente, nível ok, gate aberto, resposta certa | |
| `--led-yellow` | `#ffd23f` | **só medidor:** zona de atenção | |
| `--led-red` | `#ff4b3e` | **só medidor ou erro:** clip, resposta errada, o que é cortado ou barrado | 5,9:1 |
| texto vermelho | `#ff8a80` | texto em vermelho (aviso `lblr`, veredito errado do quiz) | 8:1 |
| `--x32` | `#46c2ff` | fita de nome X32/M32 e "só X32/M32" | |
| `--xair` | `#e8d6b4` | fita de nome X AIR/M AIR (cor de fita crepe) | |
| `--lamp` | `#ffe2b8` | luz de serviço: cromo (régua, atos concluídos, teclas já vistas, fitas acesas) | |

**Regra de cor (vale para os 367 slides):**
1. Verde, amarelo e vermelho formam a paleta de LED e só aparecem com o sentido de medidor da tabela. Nunca marcam família, parte, bullet, régua ou enfeite.
2. Família = cor de **fita de nome** (`--xair`, `--x32`), fora da paleta de LED. "Todas as 13 mesas" usa o laranja da marca.
3. Parte do capítulo = **forma**, não cor. Parte 1 (manual) é selo cheio (`.pb.pm`); Parte 2 (cursos e tutoriais) é selo vazado e tracejado (`.pb.pc`).
4. O cromo usa só `--lamp`.
5. O número gigante da abertura é um medidor em nível nominal: verde até 70% da altura e amarelo no topo, nunca vermelho.
6. Brilho (`box-shadow`) só em LED aceso, sempre fixo. Nunca se anima o brilho, só a opacidade do LED.
7. O fundo nunca é chapado: luz quente no alto à direita, respingo frio embaixo à esquerda e duas manchas de névoa (`.haze`) que derivam devagar.
8. **Nos diagramas, a cor da caixa diz o papel do bloco** (foco, destino, rota paralela, aparelho, barrado), nunca a família. A tabela 1.2 é a lei.

### 1.2 Mapa das classes do `slides_viz.py` para os tokens

O gerador põe `class="dg"` no `<svg>` (ver 2.3.2). Todas as regras abaixo ficam sob `.dg` e estão prontas no `<style>` do `index.html` (bloco "MAPA DE CLASSES"). A coluna "usos" conta as ocorrências nos 225 SVGs de `topic hv`.

| Classe original | Usos | Era (deck claro) | Vira (token) | Papel |
|---|---|---|---|---|
| `bx` | 582 | cinza-azulado | fill `--bg-2`, borda `--line-2` 1,6 | bloco comum |
| `bxo` | 140 | laranja | fill laranja 12%, borda `--accent` 2 | foco, onde mais se erra |
| `bxg` | 163 | **verde** | fill `--bg-2`, borda `--ink-2` **tracejada 6 4** | rota paralela: envio, retorno, monitor, alternativa. **Não é verde.** O sentido de "ok" fica no ✓ (`ok`), que continua verde. |
| `bxb` | 142 | azul | fill `--bg-3`, borda `--ink` 2 | destino: Main, PA, DAW, computador |
| `bxr` | 16 | vermelho | fill vermelho 10%, borda `--led-red` | barrado, perigo, erro |
| `bxd` | 46 | preto | fill `#05070a`, borda `--ink-3` | aparelho: mesa, stagebox, PA |
| `bxg`/`bxb` em "Duas famílias, 13 mesas" | 2 | | `+ fam-xa` / `fam-xm`: borda `--xair` / `--x32` | é o único diagrama em que a caixa nomeia a família |
| `panel` | 83 | cinza claro | fill branco 2,5%, borda `--line` | painel, moldura de grupo |
| `zone`, `frame` | só figuras | | borda `--line-2` tracejada | área, moldura |
| `ln`, `ln2` | 339, 47 | linha escura + seta | traço `--ink-3` 2; seta `#ah` em `#8a95a1` | ligação; `ln2` tem seta nos dois lados |
| `lnd`, `lnd2` | 26 | tracejada | `--ink-3` tracejada 5 4, seta `#ah` | ligação opcional |
| `lnx` | 5 | vermelha tracejada | `--led-red` tracejada, seta `#ahr` em `#ff4b3e` | caminho barrado |
| `ctl` | 24 | laranja tracejada | `--accent` tracejada 4 3 | comando (DCA, mute group) |
| `sep` | 130 | cinza tracejada | `#4a5664` tracejada 3 3 | leque de ligações, separador |
| `grid` / `axis` / `tick` | 57 / 44 | | `#1f262e` / `--line-2` 2 / `--ink-3` | grade, eixo |
| `curve` | 28 | laranja | `--accent` 3,2 | curva principal |
| `curve2` | 9 | cinza tracejada | `--ink-3` tracejada | referência (1:1, plano) |
| `curve3` | 6 | azul | `--ink` 2,4 | segunda curva (outro sinal) |
| `curve4` | 10 | vermelha | `--led-red` 2,4 | corte estreito, limite |
| `thr` | 16 | vermelha tracejada | `--accent` tracejada 6 5 | threshold, alvo (igual ao `.ref` das amostras) |
| `zg` / `zy` / `zr` | 21 / 9 / 11 | | LED verde / amarelo / vermelho | zonas de medidor (sentido de medidor: permitido) |
| `zgr` | 26 | cinza | `#1c232b` | LED apagado, gate fechado |
| `bar`, `bara` | 91, 10 | azul, verde | `--led-green` 85% | barra de RTA ou pista com sinal |
| `barr` | 13 | laranja | `--led-red` | apito, clip |
| `barb` | 14 | azul | `--ink-3` 60% | canal reduzido (automix), pista neutra |
| `track` / `cap` / `capo` / `capd` | 35 / 37 | | trilho `#05070a` / tampa `#c9d1d9` / `--accent` / `--ink-2` | fader |
| `dot` | 18 | | `--accent` | ponto de ajuste |
| `person` | 26 | laranja | fill crepe 8%, borda `--ink-2` | pessoa na plateia |
| `wedge`, `knob` | 11, 5 | | fill `--bg-3`, borda `--ink-3` | caixa de som, botão |
| `needle` | 3 | | `--accent` 3 | ponteiro |
| `mk` / `mk2` | 18 | | `--ink-2` / laranja 30% | marca (fone, Wi-Fi) |
| texto padrão | | 15 px `#1b2430` | **15** `--f-body`, `--ink-2` | |
| `b` | 1043 | negrito | **15**, peso 600, `--ink` | rótulo de caixa |
| `sm` | 1074 | 11 px `#5c6773` (3:1 no escuro) | **`.dg text.sm { font-size: 14px; fill: var(--ink-3) }`** (6,4:1) | nota |
| `lbl` / `lblr` | 100 / 67 | 11 px | **14**, peso 600, `--accent` / `#ff8a80` | rótulo de destaque / aviso |
| `zl` | 28 | 11 px | **14** mono 700, `--ink-3`, espaçado | título de painel (ENTRADAS) |
| `tw` | 56 | branco | `--ink` | texto em caixa escura |
| `ok` (✓) / `xr` (✕, !) | 21 / 9 | | 22 `--led-green` / 20 `--led-red` | certo / barrado |
| `ico` (emoji) | 36 | emoji | o gerador troca por palavra (VÍDEO, CURSO, PDF, ÁUDIO), mono 14 `--accent` | |
| `vt` | 225 | título no SVG | **sai do SVG** (2.3.2); `.dg text.vt { display:none }` só por segurança | |

**Tamanho na projeção:** a tela escala o diagrama entre **1,46× e 1,87×** (medido nos 61). O menor texto (`sm`, `lbl`, `zl` a 14) sai com **20,4 px** no slide de 1280×720; `b` e o texto padrão (15), com 21,9 px ou mais.

**Glifos dentro do SVG:** `→ ← ✓ ✕ ⚠` não estão no subset das fontes. O gerador os envolve em `<tspan class="sym">`, que usa a fonte de símbolos do sistema. Emojis viram palavra (tabela acima).

### 1.3 Fontes (arquivos em `fonts/`, funcionam offline)
| Papel | Família | Peso | Uso |
|---|---|---|---|
| Display | Barlow Condensed | 800 / 600 | títulos, número do capítulo, rótulos de bloco e de tecla |
| Corpo | Barlow | 400 / 600 | texto do slide e dos diagramas |
| Mono | JetBrains Mono | 500 / 700 | kicker, chips, valores, eixos, numeração |

Fallback do sistema: Avenir Next Condensed / DIN Condensed, depois Avenir Next, depois SF Mono / Menlo. Fora do SVG, os glifos ausentes do subset são trocados assim: `→ ←` viram o ícone `.arr` (constante `ARR`), `✓ ✗ ✕` viram `CHECK`/`CROSS`, `⚠` vira o triângulo SVG do slide 14, `≈` vira `~` e emojis viram ícone ou texto.

### 1.4 Tamanhos (palco de 1280×720; o reveal escala tudo junto)
| Elemento | Tamanho |
|---|---|
| Título da capa | 76 px / 0,98 |
| Título de abertura de capítulo | 112 px / 0,92; `hook` 84 px |
| Número do capítulo | 380 px |
| Título de tópico, agenda, sumário, glossário, como usar | 56–64 px; quiz 80 px |
| Corpo, bullets, células, cartões, painel, alternativas, linhas de agenda e sumário, legenda de figura | **28 px** (mínimo), entrelinha 1,3 |
| Subtítulo da capa, texto do `hook` 30 px; texto do `fecha` | 30 / 36 px |
| Rótulo de diagrama (no slide), tecla da `.vsteps`, nota de célula, nota de ato | 20–22 px |
| Kicker, chip, eixo, legenda, rodapé legal, dica | 18 px (mínimo absoluto) |

### 1.5 Espaço
- Margens do slide: 44 em cima, 40 embaixo, 76 à esquerda (a régua ocupa os primeiros 30 px) e 64 à direita. Área útil: **1140 × 636**.
- Entre colunas: 36–40 px. Raio: 3 px em chip e fita, 6–8 px em cartão e tecla, 14 px em carcaça.

### 1.6 Cromo (fixo, **dentro** do palco)
- `.chrome` fica dentro de `.reveal .slides` (1280×720, `position:absolute`) e escala junto com o slide.
- **Régua** (`.rail`): 30 segmentos na borda esquerda, uma cor só (`--lamp`): mostra quanto do curso já passou.
- **Número** (`.chrome .num`): mono 18, `n / total`. O `slideNumber` do reveal fica desligado.
- **Na capa** (`data-state="is-cover"`) o cromo e as setas do reveal somem (`.is-cover .reveal .controls { opacity:0 }`), porque o banco de faders sangra o canto inferior direito. Teclado e clique continuam a avançar.
- Nos outros slides, as setas ficam com escala 0,7 e opacidade 0,7. A barra de progresso do reveal fica desligada.

---

## 2. Layouts por tipo de slide

**Regras gerais de composição**
- O conteúdo ocupa o quadro. Nenhum slide deixa um quadrante vazio, **nem no estado inicial** (antes dos fragments). Para conferir, `shots/inicio/` mostra cada slide antes dos fragments.
- Todo slide de conteúdo tem um **protagonista** com pelo menos 45% da largura, dentro de uma carcaça (raio 14) com uma tela escura, como o visor de uma mesa.
- **Esqueleto "ghost":** fragments de texto ficam em **0,2** de opacidade até acender, e a turma vê a estrutura do slide. A lista é uma só (constante `GHOST` e a regra CSS correspondente): `.pts li, .lead-line, .cena, .ask, .hk-lead, .acts`, mais as linhas de tabela (`.trow`). Os destaques do diagrama ligados a fragments também ficam em 0,2. Só a resposta do quiz fica escondida, e mesmo assim a área dela mostra o "aparelho desligado".
- Bullet: o marcador é um traço de escala de fader (16×3, `--ink-3`). Palavra-chave em `--ink`, o resto em `--ink-2`.
- Em cada tipo abaixo: **grade**, **protagonista** e **entrada** (tempos em segundos a partir do `slidechanged`).

### 2.1 Capa (`.cover`)
- **Grade:** texto no alto (820 px) e metadados à direita (300). O banco de 16 faders sangra a base (1280×300).
- **Protagonista:** o banco de faders com medidores tocando. Fitas: 1–4 laranja, 5–8 `--xair`, 9–12 `--x32`, 13–16 branco.
- **Entrada:** a mesa já está em 0,4 em 0 s e sobe 40 px até 0,8 s · kicker 0 · título 0,04 · faders descem até a posição 0,45 (`fader`, 1,1 s, stagger 0,04) · subtítulo 0,45 · metadados 0,6 · medidores tocando a partir de 1,2 (a única repetição infinita do deck, morta ao sair).

### 2.2 Abertura de capítulo (`.opener`)
- **Grade:** `1fr | 430px`. À esquerda: rótulo, título 112, chips e os cartões "Em cena" e "Pergunte à turma". À direita: o número gigante e a barra de atos (`data-act` 1–5). A linha de sinal (`.sigline`) atravessa a base.
- **Cartões:** são fragments **com esqueleto**. Entram junto com o corpo, a 0,25 s, já em **ghost 0,2**, e acendem de 0,2 para 1 (mais 18 px) no fragment. No estado inicial o quadrante de baixo à esquerda mostra os dois cartões apagados, não um buraco.
- **Entrada:** contorno do número em 0,4 desde 0 s · rótulo 0 · título 0,04 · linha de sinal se desenha (DrawSVG 1,8 s) com um ponto que a percorre (MotionPath) 0,2 · cartões em ghost 0,25 · número enche de baixo para cima 0,35 · chips 0,4 · atos 0,7 (os concluídos acendem em `--lamp`, o atual em laranja).

### 2.3 Tópico com diagrama (`.topic.diag`, 204 slides)

#### 2.3.1 Grade
`470px | 634px`, altura 636. À esquerda: kicker (selo da parte e número), título 64, chips e bullets. **Os bullets se distribuem na altura que sobra** (`.pts { flex:1; justify-content: space-evenly }`), sem buraco embaixo quando há só 2 ou 3. À direita: a **carcaça de 3 faixas**, de cima a baixo.

```html
<div class="viz vz3">                                   <!-- 634×636, carcaça (bg-2, raio 14) -->
  <header class="vh">                                    <!-- 54 px -->
    <span class="vt">Insert: o processador no meio do canal</span>   <!-- o texto do .vt que saiu do SVG -->
    <span class="vcount"></span>                          <!-- "PASSO f/n", atualizado em cada fragment -->
  </header>
  <div class="vscreen"><svg class="dg" …/></div>          <!-- flex:1, tela LCD; o SVG escala por "contain" -->
  <ol class="vsteps" data-n="3">                          <!-- 84 a 120 px: uma tecla por fragment -->
    <li><i></i><b>1</b><span>X AIR / M AIR</span></li> …
  </ol>
</div>
```
O CSS está no bloco "CARCAÇA DE 3 FAIXAS" do `<style>`, e o slide 7 é o exemplo vivo.

#### 2.3.2 O que o gerador faz com o SVG (`ref_dg.py`, função `dg`)
1. **Tira o `.vt` do SVG.** O texto vai para `.vh .vt` e não aparece duas vezes.
2. **Recorta o viewBox estático** para `0 24 400 H-24`. O conteúdo mais alto de todos os diagramas começa em y≈26 (rótulo do eixo de `axes()`). Isso já vale sem JavaScript, no PDF por exemplo.
3. Põe `class="dg"` no `<svg>`, o que liga o mapa da tabela 1.2.
4. Troca emoji por palavra, envolve `→ ← ✓ ✕ ⚠` em `<tspan class="sym">` e, no diagrama "Duas famílias", marca as duas caixas de família (`fam-xa`, `fam-xm`).
5. Monta as teclas: uma por `<li class="fragment">`. A palavra-chave é o `<b>` do bullet; sem `<b>`, até 3 palavras que caibam em 18 caracteres, sem preposição no fim (função `keyword`).
6. Sem fragments (1 slide), sai `<ol class="vsteps legend">`, que fica escondido, e a tela ocupa a altura toda.

Na 1ª entrada, o controlador `diag` faz o **recorte fino** em tempo de execução: `viewBox = svg.getBBox()` mais 8 de margem. Depois mede a sobra de altura da tela e passa para as teclas (de 84 a 120 px). O resultado: o desenho encosta na largura da tela e o que sobra em cima e embaixo fica abaixo de ~30 px de fundo de LCD.

#### 2.3.3 Grupos que os fragments acendem: faixas de y (os SVGs não têm `<g>`)
Os 225 SVGs são `rect`/`text`/`line` soltos. O controlador `diag` agrupa assim, uma vez, na 1ª entrada (o `getBBox` precisa do slide visível):
1. **Formam faixas** as caixas, os textos e as formas, isto é, tudo menos os conectores (`line`, `polyline` e `path` sem preenchimento que não seja `.curve*`). Ordena pelo topo do `getBBox` e junta com a faixa anterior quem começa até **GAP = 6** unidades abaixo do fim dela. Caixa e rótulo ficam juntos porque se sobrepõem.
2. **A faixa 0 nunca é só um rótulo:** enquanto ela tiver menos de 25% da altura do conteúdo, junta-se com a próxima.
3. **Cada conector entra na faixa para onde aponta**, isto é, a do ponto final (`y2`, ou o último ponto do path), ou a mais próxima dele. A seta aparece junto com aquilo que ela indica.
4. **Exceção manual:** se algum filho tiver `data-step="k"`, as faixas passam a ser os valores de `data-step`, e quem não tem o atributo vai para a faixa 0. Isso fica para o caso raro de um diagrama pedir agrupamento semântico. Como o mesmo diagrama do `slides_viz.py` aparece em vários slides com bullets diferentes, a regra automática é o padrão.

**Faixa → fragment** (função `bandStep(j, r, n)`; r = número de faixas além da 0, n = número de fragments):
| Caso | O que acontece |
|---|---|
| faixa 0, ou n = 0 | acesa desde a entrada: o desenho principal nunca começa apagado |
| r = n | faixa j acende no fragment j−1 (1 para 1) |
| r < n (mais bullets que faixas) | faixas 1..r acendem nos fragments 0..r−1. Os fragments seguintes acendem só a sua tecla da `.vsteps` e o "PASSO f/n" do cabeçalho: o protagonista muda mesmo assim |
| r > n (mais faixas que bullets) | faixas se juntam em sequência: faixa j vai para o fragment `floor((j−1)·n/r)`. No último fragment o diagrama está inteiro |

Distribuição medida nos 61 diagramas (`check_dg.mjs`): 1 faixa em 3; 2 em 7; 3 em 22; 4 em 22; 5 em 6; 6 em 1. Os bullets dos 204 slides variam de 1 a 5.

#### 2.3.4 Estados e movimento
- **Inicial:** faixa 0 acesa; as outras faixas em ghost (0,2 × a opacidade própria do elemento: a zona de corte do HPF com `opacity=.35` vira 0,07); teclas apagadas (`#1c232b`); "PASSO 0/n".
- **Fragment k:** as faixas com `k_faixa ≤ k` vão a 1 (0,35 s); as linhas delas se redesenham (DrawSVG 0,5 s) e os textos sobem 8 px. A tecla k acende em `--accent` (o LED pula de 0,3 para 1 com `back.out(3)`), as teclas anteriores ficam em `--lamp` e o cabeçalho mostra "PASSO k+1/n". Voltar um fragment devolve a faixa a ghost em 0,2 s.
- **Entrada:** carcaça em 0,4 desde 0 s e chega em 0,6 s (24 px) · kicker 0 · título 0,04 · corpo em ghost 0,08 · **o desenho liga a partir de 0,12**: formas assentam (escala 0,94 → 1), medidores (`zg/zy/zr/bar*`) sobem por `scaleY` a partir da base, linhas se desenham, textos chegam por último (stagger total ≤ 0,5 s em cada grupo) · faixas fora de cena vão a ghost 0,15 · teclas 0,25 · chips 0,35.
- Diagramas com proporção ≥ 1,6 (raros no `topic`) vão para a grade da figura (2.7).

#### 2.3.5 Diagramas feitos à mão (slides 3 e 4)
Os medidores e o HPF das amostras mostram até onde um diagrama pode ir quando vale a pena desenhar à mão. O gerador não os produz: eles servem de referência para quem um dia redesenhar os diagramas mais usados ("Duas famílias" em 16 slides, "Rede" em 11, "Apps" em 10). Mesmo assim, seguem a regra de 3.3. No slide 3, o fragment 1 ("X32/M32 (METERS), só leitura") **acende a aba METERS, a moldura da tela e o selo "X32/M32 · SÓ LEITURA"** e dá um toque em todos os medidores.

### 2.4 Tópico com tabela (`.topic.tab`, 21)
- **Grade:** título em largura total, chips na linha do kicker. Corpo em `590px | 1fr`: frase de abertura, tabela de 2 colunas (`.tbl`) e frase de fechamento; à direita, o gráfico do assunto.
- **Tabela:** no máximo 4 linhas no slide (o resto fica nas notas). Coluna de valor em mono laranja; observação de 20 px embaixo da célula. **Cada linha é um fragment** que acende a linha e muda o gráfico.
- **Para os 21:** se o assunto tiver diagrama no `slides_viz.py`, use-o na carcaça de 2.3, com uma tecla por linha da tabela. O gráfico feito à mão do HPF é o modelo para quando houver tempo de desenhar.
- **Entrada:** carcaça em 0,4 desde 0 s · kicker 0 · título 0,04 · corpo em ghost 0,2 · chips 0,35 · gráfico se desenha 0,5 · o valor sobe até o alvo (3.4).

### 2.5 Quiz (`.quiz`, 25)
- **Grade:** `620px | 1fr`. À esquerda: kicker, pergunta 80, 3 alternativas de 92 px, dica (18 px) e, depois da resposta, a explicação (28 px). À direita: o diagrama do tema, nas duas linhas da grade.
- **Protagonista:** o diagrama que **explica** a resposta. No estado inicial ele já está ligado e a parte que entregaria a resposta aparece desligada.
- **Entrada:** carcaça em 0,4 desde 0 s · kicker 0 · pergunta 0,04 · alternativas vêm da esquerda a partir de 0,3 de opacidade, em 0,1 (stagger 0,08) · barras do sinal crescem 0,35 · dica 0,5.
- **Interação:** clique, Enter ou Espaço. A escolha revela a certa e **trava o quiz**. **R zera**, e sair do slide também zera.
- **Veredito em palavras:** a explicação começa com o veredito, além do ✓/✕ e da cor. Acertou: "**Certo, é a B.**" (verde). Errou: "**Não é a A. A certa é a B.**" (`#ff8a80`), mais o texto da alternativa certa num `<span class="sr">`, que só o leitor de tela lê. Depois vem a explicação original. A `.fb` tem `aria-live="polite"`; o texto original fica em `data-t` e volta no R.
- **Para os 25:** troque o diagrama genérico pelo do capítulo e escreva um `explain()` por tema, sempre com a mesma estrutura: referência se desenha → agulha varre → o efeito acontece → a faixa de saída acende.

### 2.6 Interativo (`.interactive`, 2)
- **Grade:** kicker com legenda à direita; título em 1 linha; diagrama 1140×380 em serpentina; painel de explicação de 28 px na base.
- **Legenda:** só os dois quadrados de cor (laranja = onde mais se erra; azul = só X32/M32). A dica "Clique em um bloco" usa um **ícone de cursor** (`.legend .hint svg`), não um quadrado, para não parecer a legenda dos blocos cinza.
- **Entrada:** blocos já em 0,3 a partir de 0,1, acendendo em ordem de sinal (stagger total 1,1 s) · caminho se desenha 0,1 · painel em 0,4 a partir de 0,2 · setas 0,6 · ramal 1,2 · o sinal percorre o fluxo inteiro (2,6 s) a partir de 1,8.
- **Interação:** o sinal anda até o bloco clicado (0,35 s + 1,2 s × distância), halo laranja e pulso 1,05; o painel troca o texto (sai em 0,15 s, entra em 0,35 s) e mostra o link do capítulo.

### 2.7 Figura (`.figslide`, 28) · slide 9
- **Fonte:** `viewBox="0 0 680 H"`, H de 160 a 356, com as mesmas classes de 1.2 (o gerador põe `class="dg"`).
- **Grade:** kicker "Figura · Capítulo nn" com os chips à direita; título 56; **carcaça de 1140 de largura** que vai até o fim da área (`.figbox`, flex:1), com a tela (`.fscreen`) e um rodapé de 64 px: `.figcap` em 28 px à esquerda e "Clique para ampliar" em 18 px à direita.
- A figura escala por "contain" (cerca de 1,6×). **Figura baixa (H < 220):** a tela fica com a altura da figura e a sobra vira uma faixa com os 2–4 rótulos `.b` repetidos como chips de 28 px.
- **Entrada:** carcaça em 0,4 desde 0 s · kicker 0 · título 0,04 · a figura liga com a mesma função `ignite` do `diag` a partir de 0,3 · legenda 1,0.
- **Ampliar:** clique, Enter ou Espaço na carcaça. Usa **Flip**: `Flip.getState` → classe `.zoom` (1280×720) → `Flip.from` (0,5 s, `stage`). Esc, novo clique ou sair do slide volta.

### 2.8 Agenda do capítulo (`.agenda`, 27) · slide 8
- **Dados:** 2 a 19 itens por capítulo; 19 das 27 agendas têm até 8.
- **Até 8 itens: banco de canais** (`.strips`, `--n` = número de itens). Cada item é um **canal da mesa** que vai de cima a baixo: fita com o número (mono 20), selo da parte (cheio = manual, tracejado = cursos), título de 28 px (até 5 linhas) e, embaixo, um **fader** com escala e LED que ocupa a altura que sobra. A posição da tampa varia (`--p`, de 26% a 64%), como numa mixagem real. No kicker, à direita, vai a contagem ("2 do manual · 4 dos cursos").
- **Mais de 8 itens** (ou título com mais de 5 linhas na coluna): **lista de canais** `.chlist`, a mesma do sumário (2.12), em 2 colunas com um rótulo de parte (`.actl`) em cada bloco.
- **Entrada:** canais sobem a partir de 0,3 de opacidade, em 0 s (stagger 0,06) · título 0,04 · faders sobem até a posição (`fader`, 1 s, stagger 0,05) 0,3 · fitas e LEDs acendem em `--lamp`, em sequência, a partir de 0,9. Cada canal é um link; com foco ou hover, borda e tampa ficam laranja.

### 2.9 Fechamento do capítulo (`.fecha`, 25) · slide 10
- **Grade:** espelho da abertura (`1fr | 430px`, a mesma regra CSS). À esquerda: rótulo "FECHANDO · CAPÍTULO nn", o texto do `fbox` em 36 px `--ink` ("Fechando." em laranja) e o botão "Próximo capítulo" (72 px de altura, laranja cheio, ícone `.arr`). À direita: o número do **próximo** capítulo só em contorno, embaixo dele "a seguir" e o título do próximo capítulo (30 px), e a barra de atos. A linha de sinal volta na base, **decaindo** da esquerda para a direita.
- Com `.actend` (4 capítulos): a frase de fim de ato aparece num cartão `--lamp` tracejado acima do número, e o segmento do ato acende em `--lamp`.
- **Entrada:** contorno em 0,4 desde 0 s · rótulo 0 · texto 0,04 · sinal se desenha (1,4 s) 0,2 · "a seguir" 0,4 · atos 0,5 · botão sobe 0,6.

### 2.10 Abertura e encerramento do curso (`.hook`, 2) · slide 11
- **Grade:** `1fr | 470px` e duas linhas. Linha de cima, à esquerda: kick, título 84, parágrafo 30 e o cartão "Pergunte à turma"; à direita: a carcaça de um **RTA** e, embaixo dela, a frase de promessa (`.hk-lead`). Linha de baixo: os 4 atos em 4 colunas (rótulo mono 16 "Ato I · caps. 00 a 04", nome 28 e nota de 20). Os três fragments (pergunta, promessa, atos) entram já em ghost 0,2.
- **Protagonista:** o RTA. Na **abertura**, o pico de 2,5 kHz sobe até o vermelho e o LED de CLIP acende: a microfonia. No **encerramento**, o mesmo RTA mostra o corte estreito se desenhando e o pico caindo para o verde.
- **Entrada:** RTA em 0,4 desde 0 s · kick 0 · título 0,04 · corpo em ghost 0,25 · parágrafo 0,3 · barras sobem 0,3 (stagger 0,012) · o pico sobe (`power2.in`, 0,6 s) 1,0 · CLIP e "apito" 1,6. Sem repetição.

### 2.11 Glossário (`.gloss`, 2) · slide 12
- **Grade:** `470px | 1fr`. À esquerda: kicker, título, chips e o **visor** (vai até o fim da coluna) com "GLOSSÁRIO · n TERMOS", o termo em 44 px laranja e a definição em 28 px. Antes do clique, o visor mostra "Escolha um termo". À direita: **matriz de teclas** (`.gkeys`, `--cols`) com LED no canto e o termo em 26 px display 600.
- 9 termos: 3×3. 48 termos: 3 slides de 16 (4×4), em ordem alfabética, com o intervalo no kicker.
- **Entrada:** visor em 0,4 desde 0 s · teclas acendem em varredura (`stagger { each: .03, grid: 'auto' }`) 0,1.
- **Interação:** clique, Enter ou Espaço. O LED da tecla fica laranja e o visor troca o texto (sai em 0,15 s, entra em 0,35 s). R zera.

### 2.12 Sumário (`.toc`, 1) · slide 13
- **Dois slides** (caps. 00–13 e 14–27). Kicker "Sumário · 1 de 2" com a dica à direita; título 64; `.chlist` em 2 colunas. Cada coluna abre com um rótulo de ato em mono 18; quando o ato continua na outra coluna, o rótulo diz "continuação", e as linhas das duas colunas ficam alinhadas. Cada linha tem a fita com o número (mono 26, 64 px) e o título em 28 px (até 2 linhas).
- **Entrada:** linhas sobem a partir de 0,3 de opacidade, em 0,1 (stagger 0,03) · rótulos 0,1 · fitas acendem em `--lamp` a partir de 0,6. Cada linha é um link.

### 2.13 Como usar este material (`.howto`, 1) · slide 14
- **Grade:** título 64; tabela de 7 linhas (`290px | 1fr`): à esquerda, **o componente real do deck** (selo cheio, selo tracejado, fitas de família, "(não confirmado)", o triângulo de divergência, um mini cartão "Em cena", a caixa de termo); à direita, a explicação em 28 px.
- **Entrada:** amostras "carimbam" (0,96 → 1, a partir de 0,3 de opacidade) 0,2 e textos sobem logo depois; stagger 0,06.

---

## 3. Movimento

### 3.1 Personalidade: "balística de medidor"
Chega rápido e assenta suave, como a agulha de um VU. Firme, sem quique. Overshoot leve só no acerto do quiz, no LED da tecla e no ponto do gráfico.

| Constante | Valor |
|---|---|
| Easing de entrada (`stage`) | `CustomEase 0.16,1,0.3,1` (80% das animações) |
| Easing físico (`fader`) | `CustomEase 0.65,0,0.35,1` (fader, varredura) |
| Medidor sobe / desce | `power2.out` 0,07–0,3 s / `power1.in` 0,35–0,7 s |
| Durações | rápida 0,15–0,3 s · padrão 0,45–0,6 s · lenta 0,9–1,4 s (desenho) |
| Stagger | texto 0,04–0,09 · faders e medidores 0,04–0,07 · barras 0,008–0,02; total de cada grupo ≤ 0,5 s (exceção: a onda de faders da capa) |

Só `transform` e `opacity` (60 fps). DrawSVG só no desenho de linhas finas. Nunca anime `filter`, sombra, largura ou altura. Medidor acende com **obturador** (retângulo da cor da tela que anima `scaleY`) ou com `scaleY` da própria barra a partir da base.

### 3.2 Troca de slide sem "pisca"
`transition: 'none'` no reveal: o slide que sai some na hora e o GSAP faz a entrada do novo. Para que nenhum quadro da troca fique quase preto:
1. **A carcaça do protagonista** (ou o contorno do número, a mesa da capa, as alternativas do quiz, os canais da agenda) **começa visível em 0 s, a 0,3–0,4 de opacidade**, e chega a 1 em 0,6 s com 24 px de deslocamento. Nada estrutural começa em opacidade 0 nem depois de 0,1 s.
2. O título entra por linhas atrás de máscara a partir de **0,04 s**; o corpo (já em ghost), a partir de 0,08–0,25 s.
3. O conteúdo do protagonista começa a ligar até **0,12–0,3 s**.

Conferência: `shots/t150/` captura cada slide 150 ms depois de chegar pelo anterior. Em todos aparecem a carcaça, o kicker, o título surgindo e os elementos em ghost.

### 3.3 Coreografia de entrada (padrão)
1. 0 s: carcaça a 0,4 e kicker (opacidade, 12 px).
2. 0,04 s: título (SplitText `lines` + `mask`, `yPercent 110→0`, 0,9 s). SplitText só em títulos.
3. 0,08–0,25 s: corpo (bullets, cartões, linhas de tabela; em ghost se forem fragment), stagger 0,04.
4. 0,12–0,5 s: o protagonista liga (DrawSVG, medidores, MotionPath).
5. Chips e legenda por último.

O controlador `base` faz os passos 1 a 3. Ambiente (repetição infinita, morta ao sair do slide): névoa de 16–21 s em `sine.inOut` e os medidores da capa. Nada mais repete.

### 3.4 Fragments (`fragmentshown` / `fragmenthidden`)
- Fragment com esqueleto (lista `GHOST` e `.trow`): **0,2 → 1** mais 18 px (a linha de tabela entra da esquerda, 16 px). Outro fragment: 0 → 1. A transição CSS do reveal fica desligada.
- Voltar um fragment devolve o elemento ao CSS (ghost 0,2 ou escondido).
- **Cada fragment muda o protagonista** via `step(slide, f)`, cujo estado sai **só** de `f`: primeiro mata o que estiver rodando, depois vai ao alvo. No `diag`, isso é garantido pela tecla da `.vsteps` e pelo "PASSO", mesmo quando não sobra faixa (2.3.3).
- O `step` chamado no fim da entrada lê o `f` **na hora** (`Reveal.getIndices().f`) e só roda se o slide ainda for o atual.

### 3.5 Número e desenho sempre juntos
Todo visor numérico que descreve um desenho (Hz, dB, ms) é atualizado **no mesmo `onUpdate`** que move o desenho. Nunca anime o número sozinho (exemplo: o visor "Freq do corte" do HPF).

### 3.6 Quiz
- Errou: a alternativa treme (±12 px, 3 oscilações, 0,38 s), a letra fica vermelha e o ✕ se desenha. A certa pula 1,035 com `back.out(3)`, letra verde, ✓ se desenha. A que não foi escolhida escurece para 0,45.
- O veredito em palavras abre a explicação (2.5). O diagrama explica a resposta. R zera; sair do slide zera.

### 3.7 Movimento reduzido
`gsap.matchMedia('(prefers-reduced-motion: reduce)')` liga a variável `RM`: as timelines de entrada pulam para o fim (`progress(1)`); fragments, painéis e o visor do glossário só fazem fade de 0,2 s; não há repetição, tremor, pulso, varredura, redesenho de faixa nem Flip (o estado final aparece direto).

---

## 4. Arquitetura do script (para o deck de 367 slides)

### 4.1 Uma instância de controlador por slide
- `CTRL` guarda os protótipos: `cover`, `opener`, `meters`, `hpf`, `quiz`, `flow`, `diag`, `agenda`, `toc`, `fig`, `fecha`, `hook`, `gloss` e `howto`. Slide sem tipo usa `base`.
- Na inicialização, cada `<section>` folha ganha **a sua** instância: `const c = Object.create(CTRL[tipo] || base); c.uid = i; inst.set(section, c); c.init?.(section)`. Todo estado (`this.B`, `this.lit`, `this.bars`, `this.pos`...) mora na instância. As faixas do `diag` são calculadas por instância, na 1ª entrada.
- Eventos acham a instância pelo slide: `inst.get(el.closest('section'))`.
- Ciclo: `init(s)` uma vez · `enter(s, tl)` em cada entrada · `step(s, f)` em cada fragment · `leave(s)` ao sair (o quiz zera, a figura sai do zoom) · `clear(s)` na tecla R · `pick(el, s)` em clique, Enter ou Espaço (seletor `ACT`: `.opts button, .blk, .gterm, .figbox`).

### 4.2 IDs únicos
Nenhum `id` fixo dentro de diagrama repetido. `<defs>` gerados no script levam o sufixo da instância (`cg-${uid}`, `plot-${uid}`). Caminhos usados pelo script são achados por classe (`.flowpath`, `.branchpath`). Os marcadores de seta `#ah` e `#ahr` existem **uma vez** no documento (o `<!--DEFS-->` do gerador), recoloridos: `#ah` em `#8a95a1` e `#ahr` em `#ff4b3e`.

### 4.3 Foco e teclado
`inert` em todo slide que não é o atual. Listener de `keydown` em captura no `document`: com foco num elemento `ACT`, Enter e Espaço acionam e param a propagação; Esc fecha a figura ampliada; R zera o slide atual (quiz, glossário). A explicação do quiz e o visor do glossário têm `aria-live="polite"`.

### 4.4 Como aplicar em `tools/build_slides.py`
1. **Cabeçalho:** `reveal.js`, `notes.js`, gsap, SplitText, DrawSVGPlugin, MotionPathPlugin, CustomEase e Flip de `lib/gsap/`. `Reveal.initialize({ width: 1280, height: 720, margin: 0, center: false, slideNumber: false, progress: false, transition: 'none', backgroundTransition: 'none' })`. **Copie o `<style>` e o `<script>` do `index.html` inteiros**: eles cobrem todos os tipos da tabela da introdução, e cada tipo tem um slide de exemplo. O bloco `/*SVGCSS*/` do deck claro sai; o "MAPA DE CLASSES" o substitui. Fontes vão para `07-slides/fonts/`.
2. **Cromo:** primeiro filho de `.slides`: `<div class="chrome" aria-hidden="true"><div class="rail"></div><div class="num"></div></div>`. Tire os `data-background-color`.
3. **Cada `<section>`** recebe `data-anim="<tipo>"`; a capa recebe também `data-state="is-cover"`.
4. **`topic hv` com diagrama:** classe `topic diag`; o `<div class="viz">` vira a saída de `carcass(svg, body_html)` de `ref_dg.py` (copie as funções `dg`, `keyword` e `carcass`). Bullets continuam `<li class="fragment">`.
5. **`topic hv` com tabela:** `topic tab`, `.tbl` com `.trow.fragment` (no máximo 4 linhas) e o diagrama do assunto na carcaça (2.4).
6. **`quiz`:** diagrama do capítulo + `explain()` por tema; `<p class="fb" hidden>` e `<p class="reset">` depois das `.opts`.
7. **`opener` / `fecha`:** `data-act` (1–4 = Ato I a IV, 5 = Desfecho); gere `.bignum`, `.actbar` e, no `fecha`, o número e o título do próximo capítulo (`.nx`).
8. **`figslide`:** `.figbox` (`tabindex="0" role="button"`) com `.fscreen` (SVG com `class="dg"`) e `.ffoot`.
9. **`agenda`:** até 8 itens, `.strips` com `--n` e um `.strip` por item (posição `--p` do fader: ciclo 58, 34, 50, 26, 44, 64%); mais de 8, `.chlist`.
10. **`hook`, `gloss`, `toc`, `howto`:** a marcação dos slides 11 a 14 (glossário em páginas de 16, sumário em 2 slides).
11. **Glifos:** fora do SVG, os substitutos de 1.3; dentro, o passo 4 de 2.3.2.
12. **`<aside class="notes">`:** não mexa.
13. **Conferência:** `python3 ref_dg.py` (os 61 diagramas transformam); `node check_dg.mjs` (menor texto ≥ 20 px, nada vazando); `node shoot.mjs` olhando `shots/`, `shots/inicio/` e `shots/t150/`; nenhum id repetido; sem erro de JS; voltar fragment no meio da varredura do HPF; Espaço no quiz; Tab fora de cena; 2 cópias de quiz e de interativo.

---

## 5. O que não fazer
- Fundo branco ou cinza chapado, cartões brancos, gradiente roxo.
- Diagrama pequeno num canto, metade de baixo vazia, quadrante vazio antes dos fragments.
- `.vt` repetido dentro do SVG, ou viewBox com a faixa vazia do título.
- Texto do corpo abaixo de 28 px, rótulo de diagrama abaixo de 20 px no slide, qualquer texto abaixo de 18 px.
- Verde, amarelo ou vermelho fora do sentido de medidor (`bxg` verde, família, parte, bullet, progresso).
- Elemento estrutural que começa em opacidade 0 ou depois de 0,1 s na troca de slide.
- Número que conta sozinho enquanto o desenho está parado.
- Estado de controlador em objeto compartilhado, ou `id` fixo dentro de SVG repetido.
- Transição `fade`/`slide` do reveal por cima da entrada do GSAP.
- Animar sem motivo ou repetir infinitamente fora da capa.
