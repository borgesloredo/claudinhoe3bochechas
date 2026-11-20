# Direção 2 · "Hardware da mesa"

A ideia: o slide é o próprio painel da mesa. O fundo é grafite escovado, com parafusos nos cantos. Os textos de apoio parecem serigrafia branca. As etiquetas são scribble strips (as telinhas coloridas que dão nome aos canais na X32), e os LEDs acendem. Os diagramas são peças da mesa (knob, fader, medidor, tela, tecla) e mostram o estado real do que se ensina. Nenhuma peça entra só para enfeitar.

- Amostra: `index.html`, com 6 slides em reveal.js + GSAP locais. Funciona offline.
- Fonte: `_src/build.py` (helpers SVG e slides), `_src/style.css` e `_src/motion.js`. `python3 _src/build.py` gera o `index.html` e roda as checagens (notas e links).
- Provas:
  - `shots/N-*.png`: estado final, 1280×720.
  - `shots/N-*-inicial.png`: estado de entrada, antes dos fragments.
  - `shots/contato.png` e `motion.webm`.
  - Para refazer: `node _src/shoot.mjs` e `node _src/shoot.mjs video`.

---

## 1. Tokens

### Cores

| Token | Valor | Uso |
|---|---|---|
| `--rack` | `#111315` | fora do slide (letterbox) |
| `--panel` | `#25282c` | fundo do painel (todo slide) |
| `--panel-hi` | `#30343a` | teclas (gradiente `#3b4047 → #2a2e33`) |
| `--panel-lo` | `#1b1e21` | bezel das telas |
| `--screen` | `#12161a` | LCD, telas, caixas de valor |
| `--screen-grid` | `#232a31` | grade dentro das telas |
| `--silk` | `#eceae4` | texto principal (13,4:1 sobre o painel) |
| `--silk-2` | `#bcc1c7` | texto secundário, lead e notas de tabela (8,2:1) |
| `--silk-3` | `#a8afb6` | rótulos de serigrafia e escalas (6,7:1 no painel; 5,6:1 na tecla; 8,2:1 na tela) |
| `--led-amber` | `#ffa630` | destaque: atual, "onde mais se erra", método |
| `--led-red` | `#ff5a4a` | clip, erro, corte |
| `--led-green` | `#45dc7c` | ok, sinal presente, gate aberto |
| `--led-blue` | `#63a8ff` | só X32/M32, RTA |
| `--led-off` | `#3a4047` | LED apagado (também a barra de linha de tabela ainda não mostrada) |

O `--silk-3` subiu de `#8f969d` (4,6:1) para `#a8afb6`. Num projetor com o preto lavado, o rótulo cinza é o primeiro a sumir. Agora todo texto cinza passa de 5,5:1 em qualquer fundo do deck.

**Scribble strips.** O fundo é aceso e o texto é sempre `--strip-ink #0d1013` (AA em todas). Cada cor tem um significado fixo:

| Strip | Valor | Significa |
|---|---|---|
| `st-cyan` | `#52d8e8` | X AIR (Behringer): XR18, X18, XR16, XR12 |
| `st-green` | `#66e290` | M AIR (Midas): MR18, MR12 · badge "Cursos e tutoriais" |
| `st-amber` | `#ffb547` | X32 (Behringer): X32, X32 Rack, X32 Compact, X32 Producer · número de capítulo |
| `st-magenta` | `#f272dc` | M32 (Midas): M32, M32R, M32C · quiz |
| `st-xa-all` | ciano \| verde (metade de cada) | "X AIR/M AIR (todas)" |
| `st-xm-all` | âmbar \| magenta | "X32/M32 (todas)" |
| `st-blue` | `#79afff` | badge "Manual" |
| `st-white` | `#e9edf0` | Main, neutro, "Diagrama interativo", chip sem família |
| `st-red` / `st-yellow` | `#ff7a6b` / `#ffe16e` | só barras de linha de tabela (cor da fonte sonora) |

### Tipografia: quatro camadas de texto

Só fontes do sistema: DIN no macOS, Bahnschrift no Windows. Os tamanhos valem no palco de 1280×720. **A camada vem do papel do texto, não do lugar onde ele está.**

| Camada | Mínimo | O que é | Exemplos na amostra |
|---|---|---|---|
| **1. Corpo** (HTML) | **28px** (`--t-body`) | tudo que o aluno precisa ler para aprender: bullets, células e **notas de tabela**, alternativas do quiz, feedback, legenda de figura, texto do painel interativo, **termo-chave da lista (`.key`)** | "há quem não use; ver 24.2.3", "A ordem é praticamente a mesma nas duas famílias.", CHANNEL/MIX BUS/AUX/FX/RTA |
| **2. Anotação didática** (dentro do SVG) | **22px** (`--t-annot`) | frase ou rótulo que carrega a lição do diagrama e não está repetido no texto; legenda de LED; instrução ao aluno | "vermelho = clip: baixe o ganho", "GRAVES CORTADOS", "O RESTO PASSA IGUAL", "ABERTO" / "FECHADO: ATENUA O VAZAMENTO", "Toque em uma alternativa", legenda de LEDs do interativo |
| **3. Serigrafia** | **18–20px** (`--t-label`) | nome de controle, de aba, de grupo ou de módulo, como está impresso na mesa; kicker; chips; letra miúda legal (`--t-fine` 18px) | THRESHOLD/RANGE (knobs), abas CHANNEL…RTA da tela, "LOW CUT · HPF", "FONTE", etiqueta da capa |
| **4. Escala** | **15–16px** (`--t-scale`) | só números de escala e de canal: dB, Hz, 01…13, 20/400 do knob | −18, 100, 1k, 10k Hz, dBFS |

Regra: se um texto da camada 4 passar a explicar alguma coisa, ele sobe para a camada 2. Nenhum texto fica abaixo de 15px.

| Papel | Pilha | Peso | Tamanho |
|---|---|---|---|
| Título de capa | `DIN Condensed`, Bahnschrift SemiCondensed, Arial Narrow | 700 | 78px, line-height .98 |
| Título de abertura | idem | 700 | 104px (número do capítulo: 132px) |
| Título de tópico | idem | 700 | 64px (52px no fallback, ver 3.3) · quiz 84px |
| Corpo | `Avenir Next`, Segoe UI, Helvetica Neue | 500 (600 na 1ª linha de célula) | 28px, line-height 1.22–1.32 |
| Tecla-termo `.key` | DIN Condensed | 700 | 28px, caixa alta, tecla de 48px |
| Serigrafia | `DIN Alternate`, Bahnschrift | 700, caixa alta, tracking .1–.18em | 18–20px |
| Valores e LCD | DIN Condensed (texto escuro na strip) / DIN Alternate âmbar sobre `--screen` | 700 | 28–34px |

**SVG: o tamanho vem do atributo.** `.reveal svg { font-size: 16px }` é só o padrão herdado. As classes (`.t-silk`, `.t-lbl`, `.t-ttl`) **não** definem `font-size`. Uma regra CSS venceria o `font-size="…"` do `<text>`, e foi isso que deixou rótulos com 16px quando deviam ter 18px. Toda chamada de helper passa o tamanho da sua camada.

### Grade

- Palco do reveal: 1280×720, `margin: 0`, `center: false`, escala uniforme.
- Margens: `--gx` 56px nas laterais, `--gy` 48px no topo. A base útil vai até y 680.
- **Linha do kicker** (y 48): strip do badge + número da seção + filete + chips das mesas. Os chips moram aqui, não embaixo do título.
- Coluna de texto (layout tópico + diagrama): x 56 → 568 (512px). Coluna do diagrama: x 612 → 1224 (612px), y 40 → 680, altura total.
- Legenda de módulo: recorte na moldura (`.mod > .mod-lg` em HTML; `frame()` em SVG, 18px).

---

## 2. Componentes e peças

| Peça | Onde | O que é |
|---|---|---|
| `section.pnl` | todo slide | painel: escovado, luz, 4 parafusos (só CSS) |
| `.strip.st-*` | kicker, chips, SEL | scribble strip |
| `.led(.on)` | rótulos | LED de 12px |
| `.mesas13` | chip "Todas as 13 mesas" | 13 LEDs verdes + serigrafia |
| `.mod(.amber)` + `.mod-lg` | Em cena, Pergunte, Método | moldura com legenda no recorte |
| `.key` | lista, agenda, glossário | tecla com LED em barra (`.cur` acende) |
| `.tbl .tr` + `.val` | tabela | barra colorida, texto 28px e valor numa caixa LCD âmbar |
| `knob / fader / meter / lcd / frame / key` | SVG | helpers em `_src/build.py`: desenham o **estado final** e marcam o que anima |

`<defs>` compartilhados (`gMeter`, `gKnob`, `gCap`, `gCapR`, `gKey`, `pScan`) entram **uma vez**, num `<svg width=0 height=0>` fora do `.reveal`. Gradiente dentro de slide escondido (`display:none`) não renderiza.

### Esqueleto "painel desligado" (regra de estado inicial)
Fragment ainda não mostrado **não some**. Ele fica presente com `opacity .25`, com o texto no lugar, como uma tecla de LED apagado:
- barra da linha de tabela em `--led-off`;
- `.mod.amber` com borda neutra;
- `.key` com o LED apagado.

O quadro nunca abre com metade vazia. O professor vê a estrutura e o aluno não lê antes da hora (veja os `shots/*-inicial.png`). CSS: `.reveal .slides section.pnl .fragment:not(.visible) { opacity:.25; visibility:inherit }`.

---

## 3. Layouts por tipo de slide

Coordenadas no palco de 1280×720. Na tabela "Gerador", "classe hoje" é o que o `build_slides.py` emite agora.

### 3.1 Capa (`.s-cover`, `data-anim="cover"`) · gerador: `section.cover`
- y 52: serigrafia "Curso prático · mesas digitais" com LED.
- y 88: título 78px, 830px de largura, 2 linhas.
- y 262: lead 28px `--silk-2`.
- y 348: `.mesas13`.
- Canto superior direito (x 904–1224): etiqueta do material (`.plate`, 18px).
- y 384–704: **banco de canais em largura total**. São 13 strips, uma por mesa, coloridas pela família, mais o MAIN LR com capa de fader vermelha. Colchetes serigrafados de 16px nomeiam as famílias. Aqui o banco não é decoração: ele é a lista "Todas as 13 mesas" desenhada.

### 3.2 Abertura de capítulo (`.s-opener`) · gerador: `section.opener`
- Esquerda, x 56–800:
  - LCD âmbar 236×148 com "CAPÍTULO" e o número (132px, conta de 00 até N).
  - Ao lado do LCD: ato e `.mesas13`.
  - y 232: título. Na largura de 730px, a DIN Condensed tem cerca de 34px por caractere a 104px.
    - até 21 caracteres: 104px, 1 linha ("Low cut e equalizador");
    - até 44: 84px, 2 linhas;
    - mais que isso: 68px, até 3 linhas ("Insert, delay, pan, link e o roteiro completo do canal").
    - No gerador, a coluna esquerda da abertura é flex: os módulos abaixo descem junto com o título, e o rail fica preso em y 682.
  - y 384: `.mod` "Em cena".
  - y 528: `.mod.amber` "Pergunte à turma". Os dois ficam em esqueleto até o fragment.
  - y 682: rail de 28 LEDs (passados verdes, atual âmbar).
- Direita, x 800–1224, em altura total: **módulo-tema do capítulo**, sempre um da tabela 6.2 (nunca um banco genérico). Ele aparece no estado que o capítulo vai ensinar. Os caps. 25–27 não têm "Pergunte": o `.mod` "Em cena" desce para y 456.

### 3.3 Tópico + diagrama (`.s-topic`, coluna) · gerador: `section.topic.hv`
Coluna de texto `.col` em **fluxo vertical**, não em coordenadas fixas: x 56, y 48, 512×632.
1. **Kicker**: strip do badge + número.
2. **Chips** numa linha própria. Na coluna de 512px eles não cabem ao lado do kicker; podem quebrar em no máximo 2 linhas.
3. **Título** 64px, `margin-top 16`.
4. **Lista** `margin-top 30`. Cada item é uma `.mrow` = tecla `.key` com o termo + texto 28px. Item terminado em ":" vira linha-cabeçalho `.ro` com LED.

**Título que não cabe** (DIN Condensed 64px ≈ 27px por caractere, ≈ 19 caracteres por linha em 512px):

| Título | Tratamento |
|---|---|
| até 38 caracteres | 64px, até 2 linhas. A lista desce sozinha, porque a coluna é flex |
| 39–46 caracteres | 52px (`.ttl.long`), até 2 linhas |
| mais que isso | o título vai para a largura total (`.ttl.wide`, 1168px, logo abaixo do kicker). Kicker + chips + título formam o cabeçalho, e as duas colunas começam em y = base do título + 24. O diagrama encolhe pelo `viewBox` (`preserveAspectRatio="xMidYMin meet"`) |

- **Altura máxima:** a coluna termina em y 680. O `split()` do gerador mede com 512px e 28px. Se passar, vira "(continuação)" e o título se repete com " (cont.)". O texto nunca encolhe.
- Direita, x 612–1224, y 40–680: o diagrama ocupa a coluna inteira, desenhado como uma peça da mesa (tabela 6.1).
- Cada fragment acende a parte do diagrama que corresponde ao item, pelo contrato `data-g` (seção 5).

### 3.4 Tópico **sem** diagrama · gerador: `section.topic` sem `.hv`
Hoje o `escolhe()` sempre devolve um tema (`TEMA[cap]`), então o caso só aparece se o mapa mudar ou no cap. 27. **Não se inventa hardware para preencher.** A regra é dar à lista a largura toda:
- O cabeçalho (kicker + chips + título) vai em largura total, título até 1168px.
- A lista vira **duas colunas de `.mrow`** (`.mlist.two`: x 56–596 e x 640–1224, gap 44), preenchidas por coluna.
- Com 3 itens ou menos, vira uma coluna única de 760px, e a direita fica com o **destaque do slide**: o primeiro `<b>` ou número citado num LCD grande (`--screen`, valor âmbar 96px, legenda de serigrafia). Só se existir um número ou termo de verdade. Se não existir, a coluna única fica centrada na grade com 760px.

### 3.5 Tópico com tabela (`.s-table`) · gerador: `section.topic.hv` cujo corpo é `table_html()`
- y 48: kicker + número + filete + chips na mesma linha (cabem nos 1168px).
- y 100: título em largura total, 64px (até 43 caracteres numa linha; se passar, 2 linhas e tudo abaixo desce 64px).
- y 182: linha-lead, por exemplo "Benefícios" (fragment, esqueleto).
- Esquerda, x 56–636: tabela FONTE | CORTE DE PARTIDA.
  - Cabeçalho 18px.
  - `.tr` com 1ª linha 28px/600, nota 28px `--silk-2` e valor numa caixa LCD de 172px.
  - Cada linha é um fragment, com esqueleto e barra em LED-off.
- Direita, x 664–1224, **y 226–582 (560×358)**: o módulo-instrumento é o protagonista e é maior que a tabela.
  - A tela da curva (528×222) fica em cima.
  - Embaixo: knob FREQ, leitura LCD e tecla LOW CUT ("liga / desliga").
- y 606: `.mod.amber` "Método" em largura total (fragment final).
- Linhas de tabela levam `data-f` (valor), `data-a`/`data-b` (faixa) e `data-r` (texto do LCD). O SVG leva `data-px0/px1/f0/f1` (eixo).
- **Rótulo ancorado à zona:** "GRAVES / CORTADOS" fica dentro da zona vermelha e só aparece se ela tiver pelo menos 112px. No bumbo (20–40 Hz) a zona encolhe e o rótulo apaga. A regra vale para todo rótulo dentro de região que muda de tamanho: some quando a região fica menor que ele.

### 3.6 Quiz (`.s-quiz`) · gerador: `section.quiz.hv`
- Esquerda, x 56–732:
  - Kicker magenta "Quiz rápido" + capítulo.
  - Pergunta 84px.
  - 3 alternativas como teclas grandes (676px) com letra num LCD.
  - y 590: antes da resposta, "Toque em uma alternativa" (22px). Depois, o **feedback do deck original** (`.fb`, 28px, com ▶ verde).
  - y 674: "Tecla R: refazer" (20px).
- Direita, x 772–1224: módulo do capítulo (`TEMA[cap]`) em estado neutro, sem entregar a resposta. Depois da resposta ele **demonstra** a certa.
- O `.fb` é buscado por classe (`$('.fb', s)`), nunca por `nextElementSibling`, porque a dica fica entre os dois.

### 3.7 Interativo: caminho do sinal (`.s-inter`, `data-anim="flow"`) · gerador: `flow_slide()`
- y 48: kicker e, à direita, a legenda de LEDs (22px): âmbar = onde mais se erra, azul = só X32/M32.
- y 100: título.
- y 182–452: 11 blocos-tecla 94×132 com número (16px), LED em barra e rótulo 28px. O trilho do sinal `#sp` passa por dentro dos blocos. Os envios ficam num ramal (`#sp2`) abaixo do Fader. A legenda da figura vai embaixo à esquerda, em 28px.
- y 470–672: painel LCD com SEL (número ou "ENV", na cor do bloco), título 40px, descrição 28px e link "Ver capítulo N →".

### 3.8 Interativo: explorador das mesas · gerador: `explorer_slide()`
- y 48: kicker "Explorador interativo". y 100: título.
- y 178–318: **banco de 13 strips clicáveis**, o mesmo desenho da capa em tamanho menor.
  - `button.strip[data-m]` em `.exbtns`, cor da família, 84px de largura.
  - Os rótulos de família ("X AIR / M AIR", "X32 / M32") viram colchetes serigrafados acima das strips.
- y 340–680: `.sfpanel` (LCD). À esquerda, o SEL com o nome da mesa na cor da família. À direita, um `dl` em 2 colunas com as linhas do `#exdata`: chave 18px de serigrafia, valor 28px.
  - Até 10 linhas cabem.
  - Mais que isso: paginação por tecla `▸` no canto do painel. Não se reduz a fonte.
- Contrato: o JSON `#exdata` não muda. `.expanel` vira `.sfpanel.expanel`.
- Motion: no clique, a strip pisca (`flick`) e o LED da tecla acende. As linhas entram com `y:12 → 0` e stagger de 0,04s (total ≤0,4s). O SEL troca com `flick`.

### 3.9 Interativo: glossário · gerador: `glossary_slide()`
- Cabeçalho como no 3.3 (kicker, número, chips na linha, título).
- y 178–318: `.gpanel` como LCD de largura total. Mostra o termo (DIN Condensed 40px âmbar) e a definição (28px). Antes do clique: "Clique em um termo para ver a definição." (22px, `--silk-2`).
- y 340–680: `.ggrid` como **teclado**, com `button.gterm` no estilo `.key`, DIN Condensed 28px e tecla de 52px. A grade tem 4 colunas de 272px, até 5 fileiras: **20 termos por slide**. Mais termos vão para "(continuação)", nunca para rolagem.
- Motion: no clique, a tecla acende o LED (`.on`). O texto do LCD entra com `flick` e depois `y:10 → 0`. Teclas já vistas mantêm um LED verde fraco (`.seen`), para o professor ver o que já cobriu.

### 3.10 Agenda "neste capítulo" · gerador: `section.agenda`
- y 48: kicker "CAP 06 · neste capítulo". y 100: título.
- Lista de links como **fileira de teclas**: `.key` com o número da seção (6.1.1, largura 132px) + título 28px, link inteiro clicável.
  - Até 8 itens: uma coluna de 1168px.
  - `.two` (mais de 8): 2 colunas de 572px.
  - Mais de 16: continuação.
- Motion: os LEDs das teclas acendem em sequência (stagger 0,04s, total ≤0,45s). O texto entra junto com o cabeçalho.

### 3.11 Figura · gerador: `section.figslide`
- Cabeçalho como no 3.3, com a figura em largura total.
- y 176–600: a figura dentro de uma **tela** (bezel `--panel-lo` + `--screen`, 1168×424). O SVG escala por `viewBox` e é o protagonista.
- y 616–686: legenda `.figcap` como `.mod` (28px). Se tiver 2 linhas, a tela encolhe para 176–560.
- Clique em `.figbox`: **Flip** para tela cheia (y 40–680) e volta (`Flip.from`, 0,6s `power2.inOut`). A legenda some com opacity no zoom.

### 3.12 Gancho e encerramento (`#abertura`, `#encerramento`, `section.hook`)
- Mesmo grid da abertura de capítulo. Esquerda: kick de serigrafia, título 104px, `.big` 32px.
- `.ask` vira `.mod.amber` (fragment, esqueleto); `.lead` 28px (fragment).
- `.acts` vira 4 **teclas de ato** em fileira (y 560–680). Cada uma tem LED (no gancho todas apagadas; no encerramento todas verdes, acendendo em sequência) + "Ato I · …" 22px + resumo 22px.
- Direita, x 800–1224: o gancho mostra a **tela de RTA com o pico do apito** (módulo do cap. 12, com a anotação "apito"). O encerramento mostra a mesma tela já com o corte estreito no EQ: a história fecha na mesma peça.

### 3.13 Fim de capítulo · gerador: `section.fecha`
- Esquerda: `.actend` como serigrafia âmbar 20px; `.fbox` como `.mod` 28px.
- `.nextcap` vira uma tecla grande "PRÓXIMO CAPÍTULO →" no canto inferior direito, com LED âmbar.
- Direita: o mesmo módulo-tema da abertura do capítulo, agora no **estado final** do que foi ensinado. Abertura e fechamento se espelham.

### 3.14 Sumário e "Como usar" · gerador: `section.toc`, `section.howto`
- **Sumário**: 28 capítulos em 2 colunas de 14 linhas (y 150–680, 37px por linha). Cada linha tem um LCD com o número (cor do ato) + título 28px. Os atos viram colchetes serigrafados na margem.
- **Como usar**: cada `.lg` vira uma `.mrow`. A amostra real (a strip ou o LED) ocupa o lugar da tecla, e a frase fica em 28px.

---

## 4. Motion

### Personalidade
**Metal rígido / corporativo.** Firme e preciso, sem quique. O único overshoot é o "pop" de acerto no quiz.

| Constante | Valor |
|---|---|
| Easing assinatura (80% dos casos) | `CustomEase "hw"` = `cubic-bezier(0.2, 0, 0, 1)` |
| Acender LED/LCD, ligar fragment | `CustomEase "flick"` = `M0,0 L0.18,1 L0.32,0.2 L0.46,1 L1,1` (pisca uma vez e firma) |
| Movimento no lugar (curva, knob) | `power2.inOut` |
| Progresso no tempo (sinal, playhead) | `none`, linear só aqui |
| Durações | rápido 0,2s · padrão 0,45s · lento 0,9s · desenhar 0,9–1,1s |
| Stagger | 0,03–0,08s, total ≤0,45s (`stagger: {amount}`) |
| Ambiente | **no máximo 4s** (`AMBIENT`), depois para no nível final |

### Transição entre slides
- **Corte seco: `transition: 'none'`.** Com `fade`, os dois slides densos ficavam sobrepostos por 150–300ms, e a coreografia de entrada começava em cima do slide que saía. A identidade da troca vem do `intro()`.
- Ao sair: a timeline anterior vai ao fim (`progress(1)`) e morre, e o ambiente para.

### Coreografia de entrada (todo slide, `intro()`)
1. **0,00s** kicker, chips e legenda: `x:-16 → 0` + opacity, stagger 0,06s. As strips acendem com `flick`.
2. **0,08s** título com SplitText **por linha** e máscara, `yPercent:105 → 0`, 0,75s. SplitText só no título.
3. **0,30s** lead e etiqueta: `y:16 → 0`.
4. **0,10–1,4s** o diagrama se monta (tabela abaixo).
5. **0,45s** todos os fragments entram juntos (`from opacity 0`): os acesos chegam a 1 e os do esqueleto chegam a .25.
6. **0,70s** aplica o estado dos fragments visíveis (`step` ou o `focus` genérico).
7. Depois: ambiente de no máximo 4s (capa e medidores).

### Regras por peça

| Peça | Animação |
|---|---|
| Moldura, curva, colchete | `drawSVG: 0 → 100%`, 0,9–1,1s, `power2.inOut` |
| Knob | `rotation: −135° → posição`, 0,9s `hw`, origem fixa (`svgOrigin`) |
| Fader | `y: +distância → 0`, 0,9s, stagger 0,03s |
| Medidor | `.m-cov scaleY: cheio → nível`, 0,7s `power2.out` |
| Barras de RTA / zona de corte | `scaleY` ou `scaleX` a partir da base ou da borda |
| LCD do capítulo | `flick` e contagem 00 → N em 0,6s |
| Sinal (MotionPath) | ponto âmbar percorre `#sp` em 1,8s linear; o LED de cada bloco acende quando o sinal passa |
| Clique num bloco | o sinal viaja até o bloco (0,25s + 0,9s × distância), o LED pisca e o painel troca |
| **Fragment comum** | "liga": `opacity .25 → 1` com `flick` + `x:-10 → 0`, 0,45s. Sem ir a zero |
| Fragment ligado a diagrama | `focus` genérico (seção 5) ou `step` próprio. HPF: a curva desliza, o knob gira, o LCD troca e a faixa marca o intervalo. "Método": sobe a 180 Hz e volta a 125 Hz, **a animação é o próprio método** |
| Quiz certo | o check se desenha (0,35s) e a tecla dá um pop `scale .82 → 1` `back.out(2.2)`. Feedback `y:12 → 0` |
| Quiz errado | o X se desenha, a tecla treme `x:[-12,10,-7,4,0]` em 0,4s, e a certa é mostrada |
| Demo pós-resposta | playhead linear de 2,4s; a saída é desenhada no mesmo tempo e o LED GATE acompanha |
| **Quiz: refazer** | **tecla R**, ou sair do slide e voltar, zera tudo (classes, inline styles, demo, feedback) e repete a entrada |
| Ambiente | medidores "vivos" (`scaleY` aleatório, 0,14–0,32s) por **4s**, depois param no nível em 0,6s. Não disputa com a fala do professor |

### Movimento reduzido (`prefers-reduced-motion: reduce`)
- Toda timeline salta para o fim (`progress(1)`). O estado dos fragments é aplicado **depois** do salto. Sem ambiente.
- Cliques (quiz, blocos, refazer) mostram o resultado final. Testado: errar → R → acertar → sair e voltar.

### Desempenho
- Só `transform` e `opacity`, mais DrawSVG (dash) e MotionPath (transform).
- Origem de SVG explícita: `O(o) = { svgOrigin: o, smoothOrigin: false }` no *from* e no *to*.
- No máximo cerca de 20 elementos em movimento ao mesmo tempo.

---

## 5. Contrato `data-g`: fragment ↔ diagrama (genérico, para os 367 slides)

O gerador não escreve `step()` à mão. O `motion.js` traz um `focus(s)` que roda em **qualquer** slide que tenha `.fragment[data-g]`:

```html
<li class="mrow fragment" data-g="ch">…</li>           <!-- no texto -->
<g data-g="ch">…<path class="brk" …/></g>             <!-- no SVG do diagrama -->
<g data-g="main" data-with="bus">…</g>                <!-- acende junto com "bus" -->
```

| Estado | Resultado |
|---|---|
| nenhum fragment com `data-g` visível | diagrama todo aceso |
| fragments visíveis | grupos citados com opacity 1, o resto com .28 (0,45s) |
| último visível ("atual") | `.cur` no item e no grupo; o colchete `.brk` do grupo se desenha (0,6s) e os outros se apagam |
| voltar um fragment | recalcula do zero, sem estado guardado |

**Como o gerador preenche:**
1. Cada diagrama de `slides_viz.py` passa a emitir seus grupos com `data-g` (chaves da tabela 6.1) e um dicionário `G = {chave: regex}`.
2. Para cada bullet, a primeira regex que casar com o `<b>` (ou com o início do texto) dá o `data-g` do `<li>`.
3. Bullet sem casamento fica sem `data-g`: acende só o texto, e o diagrama não muda.
4. Diagrama que precisa de mais que realce (curva que desliza, por exemplo) declara `data-anim` com `step` próprio. O `step` pode chamar `focus()` e somar o específico, como os medidores fazem.

---

## 6. Mapeamentos completos para o gerador

### 6.1 Tipo de diagrama (`slides_viz.D`) → peça de hardware

Peças-base:
- **TELA** = bezel + `--screen` com plot.
- **MED** = medidores LED (`meter()`).
- **BANCO** = strips (LCD + knob + mute + fader).
- **ROTA** = tela de roteamento: grade de patch com blocos-tecla e linhas de sinal (DrawSVG/MotionPath).
- **TRASEIRA** = painel de conectores (XLR/P10/RJ45 desenhados) com serigrafia.
- **LCD-APP** = tela de app/LCD com abas e teclas.

| viz | Peça | Grupos `data-g` | O que mostra / anima |
|---|---|---|---|
| `hpf` | TELA + knob + LCD + tecla (= amostra 6.2.1) | `freq`, `on`, `cut` | curva desliza, knob gira, LCD lê Hz |
| `eq` | TELA + 4 teclas de banda + knobs Q/FREQ/GAIN (= abertura 06) | `low`, `lomid`, `himid`, `high`, `q`, `gain` | a banda acesa mexe a curva |
| `comp` | TELA de transferência + knobs THR/RATIO/KNEE/GAIN + MED de GR | `thr`, `ratio`, `knee`, `makeup`, `gr` | ratio troca a inclinação; o medidor de GR desce |
| `duck` | TELA de 2 trilhas (voz/música) + MED de GR | `key`, `music` | a voz entra e a música abaixa (playhead) |
| `gate` | TELA de forma de onda + barra aberto/fechado + knobs (= quiz) | `thr`, `range`, `release` | playhead; segmentos abertos crescem |
| `taps` | ROTA: canal → pré/pós → bus, com fader no meio | `pre`, `post` | o sinal toma o ramal; o fader mexe e só o pós segue |
| `buses` | BANCO de 1 canal → N buses (strips de bus) | `aux`, `fx`, `main` | envios acendem um a um |
| `dca` | BANCO: 4 faders de canal + fader DCA com LCD | `dca`, `sub` | o DCA desce e os 4 seguem; o subgrupo soma |
| `mutegrp` | teclas MUTE GROUP 1–6 + strips | `grp` | o grupo apaga vários LEDs de mute |
| `matrix` | ROTA: buses → matriz → saídas | `src`, `mtx`, `out` | linhas de sinal se desenham |
| `crossover` | TELA com 2 curvas (LP/HP) + LCD da frequência | `sub`, `tops`, `xo` | o ponto de corte desliza |
| `auxsub` | ROTA: canais → aux sub (pós-fader) | `send`, `sub` | só canais com grave acendem o envio |
| `tower` | ROTA + régua distância → ms em LCD | `dist`, `delay` | o LCD calcula enquanto a régua cresce |
| `usbrec` | TRASEIRA USB + BANCO de pistas (strips com REC) | `sends`, `returns`, `rate` | os LEDs REC acendem por canal |
| `vsc` | 3 teclas de passo (1-2-3) + LCD-APP | `p1`, `p2`, `p3` | passo a passo; o 3 pisca vermelho se esquecido |
| `pendrive` | TRASEIRA USB + LCD do player | `play`, `led` | LED vermelho = não tirar |
| `live` | BANCO: PA × mix da live (2 faders por fonte) | `pa`, `live` | um fader alto no palco e baixo na live |
| `aes50` | TRASEIRA RJ45 + stagebox + LCD do clock | `cable`, `gain`, `clock` | o sinal percorre o cabo (MotionPath) |
| `split` | ROTA: stagebox → 2 mesas | `foh`, `mon`, `gain` | a cópia digital se desenha nos dois ramos |
| `ultranet` | TRASEIRA + mixer pessoal P16 (16 teclas) | `p16`, `ch` | os canais acendem no P16 |
| `retornos` | BANCO de mixes de retorno (caixa, in-ear, P16) | `wedge`, `iem`, `p16`, `pre` | o envio pré-fader não segue o fader do PA |
| `scenes` | LCD-APP: lista de cenas + teclas SAFE | `scene`, `safe` | a cena carrega e os safes ficam |
| `solo` | BANCO com teclas SOLO + MED da escuta | `pfl`, `afl` | o solo acende e a escuta muda; o Main não |
| `talkback` | tecla TALK + 2 destinos (A/B) + LED dim | `a`, `b`, `dim` | fala só no destino escolhido |
| `osc` | LCD-APP do oscilador + MED | `osc`, `dest` | o sinal de teste aparece no medidor |
| `automix` | MED de 6 canais + LCD de grupos X/Y | `talk`, `idle`, `grp` | quem fala sobe e os outros descem |
| `rta` | TELA RTA (barras) + EQ estreito | `peak`, `cut` | o pico do apito sobe e o corte estreito desce |
| `pink` | TELA RTA plana + EQ do Main/GEQ | `pink`, `geq` | o ruído rosa fica plano depois do ajuste |
| `meters` | TELA de medidores com abas (= amostra 12.1.1) | `ch`, `bus`, `fx`, `rta`, `main` (with bus) | foco por grupo; os medidores sobem |
| `phantom` | tecla +48 V com LED vermelho + MUTE | `48v`, `mute` | o mute acende antes do +48 V |
| `gain` | knob GAIN + MED com marcas −18 e 0 dBFS | `gain`, `target`, `clip` | o knob gira e o medidor estaciona em −18 |
| `path` | ROTA de 11 blocos (= interativo) | um por bloco | o sinal percorre o caminho |
| `source` | ROTA de patch em blocos de 8 (tela ROUTING) | `in`, `usb`, `block` | o bloco de 8 se liga ao canal |
| `insert` | ROTA: canal → slot FX → volta | `slot`, `ch` | o sinal desvia pelo insert |
| `pan` | knob PAN + 2/3 MED (L C R) + tecla LINK | `pan`, `link`, `lcr` | o knob distribui os medidores |
| `chdelay` | knob DELAY (ms) + tecla Ø + 2 formas de onda | `delay`, `pol` | as ondas se alinham e a polaridade inverte |
| `fx` | rack de 4/8 slots (LCD por slot) + ROTA | `send`, `ins`, `slot` | o slot acende pelo envio ou pelo insert |
| `dual` | 1 slot com 2 LCDs (A/B) | `stereo`, `dual` | o slot se divide em dois |
| `network` | TRASEIRA (RJ45, antena, chave REMOTE) + LCD-APP | `cable`, `wifi`, `router` | a chave REMOTE gira entre os 3 modos |
| `sync` | 2 LCD-APP (mesa e PC) + seta | `m2pc`, `pc2m` | a seta Mixer → PC é a certa; PC → Mixer pisca vermelho |
| `apps` | 3 telas (PC, tablet, celular) com papel | `tec`, `tab`, `ret` | cada tela acende com o seu papel |
| `sof` | BANCO: tecla SENDS ON FADER troca os LCDs | `sof` | os LCDs trocam de nome e os faders se movem |
| `naming` | BANCO: strips com nome, cor e ícone | `name`, `color`, `copy` | as strips ganham cor uma a uma |
| `power` | 2 sequências de teclas POWER (ligar/desligar) | `on`, `off` | a ordem acende passo a passo |
| `reset` | tecla RESET + LCD-APP | `save`, `reset` | salvar acende antes do reset |
| `firmware` | LCD-APP com barra de progresso | `before`, `during` | "antes do evento" fica verde, "durante" fica vermelho |
| `maint` | TRASEIRA com ventilação e cabos | `heat`, `dust`, `cable` | as áreas acendem por item |
| `midi` | TRASEIRA MIDI IN/OUT + controlador | `scene`, `fader` | a mensagem viaja e o fader mexe |
| `clock` | LCD com a taxa (48k) + LED de lock | `rate`, `lock` | os relógios entram em sincronia |
| `families` | BANCO de 13 strips (= capa) | `xair`, `mair`, `x32`, `m32` | o colchete da família se desenha |
| `checklist` | coluna de teclas com LED (checklist) | um por item | os LEDs acendem em sequência |
| `errors` | pares LED vermelho → LED verde (erro → correção) | um por par | vermelho → verde |
| `sources` | rack de "estantes": strips com o tipo de fonte | `manual`, `curso` | as strips acendem por tipo |
| `legend` | as próprias strips/LEDs do deck (Manual, Cursos, mesas) | `manual`, `cursos`, `mesas` | cada código acende com a sua frase |
| `inputs` | TRASEIRA: XLR, P10 Hi-Z, AUX IN | `xlr`, `hiz`, `aux` | o conector acende |
| `panel_xr18`, `panel_xr16`, `panel_rack`, `panel_m32c`, `surface` | TRASEIRA/frente da mesa, em escala, com serigrafia real | uma seção por grupo de conectores | as seções acendem por bullet |
| `quiz` (o "?" genérico) | **não usar**: o quiz usa o módulo do capítulo (6.2) em estado neutro | | |

### 6.2 Capítulo → módulo-tema (abertura, quiz e fechamento)
Segue o `TEMA` de `slides_viz.py`. Foi completado com o cap. 27, que não estava no mapa.

| Cap. | Título | Módulo (viz) | Estado na abertura |
|---|---|---|---|
| 00 | Antes de começar | `legend` | os códigos do deck acesos |
| 01 | Conheça as mesas | `families` | banco de 13 strips |
| 02 | Painel, conectores e ligações | `inputs` | traseira com XLR / P10 / AUX |
| 03 | Rede e controle remoto | `network` | chave REMOTE + roteador |
| 04 | Apps, navegação e organização | `apps` | 3 telas com papéis |
| 05 | Caminho do sinal, fonte e ganho | `gain` | knob + medidor em −18 |
| 06 | Low cut e equalizador | `eq` | EQUALIZER (amostra) |
| 07 | Gate, expansor e ducker | `gate` | GATE (amostra do quiz) |
| 08 | Compressor | `comp` | transferência + GR |
| 09 | Insert, delay, pan, link e roteiro | `path` | caminho de 11 blocos, em coluna |
| 10 | Buses, envios e pontos de captação | `taps` | ramal pré/pós |
| 11 | Retornos, in-ear e P16 | `retornos` | mixes de retorno |
| 12 | Medidores, RTA, microfonia e PA | `rta` | RTA com o pico do apito |
| 13 | Efeitos | `fx` | rack de slots |
| 14 | DCA, subgrupos e mute groups | `dca` | fader DCA + 4 canais |
| 15 | Sistema de PA | `matrix` | roteamento de matriz |
| 16 | Cenas, snapshots e safes | `scenes` | lista de cenas + SAFE |
| 17 | Escuta do técnico | `solo` | teclas SOLO + escuta |
| 18 | Automix | `automix` | medidores de quem fala |
| 19 | Gravação, USB, playback | `usbrec` | pistas com REC |
| 20 | Expansão: AES50, stageboxes, split | `aes50` | cabo + stagebox |
| 21 | MIDI e configurações globais | `midi` | MIDI IN/OUT |
| 22 | Firmware e manutenção | `firmware` | barra de progresso |
| 23 | Roteiros e checklists | `checklist` | teclas de checklist |
| 24 | Erros comuns e lacunas | `errors` | pares vermelho → verde |
| 25 | Especificações comparadas | `families` | banco de 13 strips com um LCD de especificação |
| 26 | Onde estudar | `sources` | estantes de fontes |
| 27 | Glossário | `legend` → **teclado de termos** | grade de `.key` com os primeiros termos do glossário |

Não existe fallback de "banco genérico com 8 strips". Todo capítulo tem um módulo que mostra o estado real do assunto.

### 6.3 Classes do gerador → direção 2

| Hoje (`build_slides.py`) | Vira |
|---|---|
| `section.cover` | `.pnl.s-cover` + banco de 13 strips |
| `.opener` + `data-background-color` | `.pnl.s-opener`, **sem** `data-background-color` (o painel é o fundo). `clabel` vira LCD + ato |
| `.topic.hv` + `.viz` | `.pnl.s-topic` com `.col` + diagrama 612×640 (ou `.s-table` se o corpo for tabela) |
| `.topic` sem `.viz` | `.pnl.s-topic.nodiag` (3.4) |
| `.kicker .pb.pm` / `.pb.pc` | `.strip.st-blue` / `.strip.st-green` dentro de `.kick` |
| `.quiz.hv` | `.pnl.s-quiz` com o módulo do capítulo |
| `.interactive` (flow / explorador) | `.s-inter` (3.7) / `.s-inter.s-explorer` (3.8) |
| `.gloss` | `.pnl.s-gloss` (3.9) |
| `.agenda`, `.figslide`, `.hook`, `.fecha`, `.toc`, `.howto` | 3.10 a 3.14 |

**Chips (`chips()`): regra exata.** O nome da mesa decide a cor; a classe `xa`/`xm` só diz o grupo.

| Chip | Strip |
|---|---|
| `.chip.all` ("Todas as 13 mesas") | `.mesas13` |
| `.chip.xa` "X AIR/M AIR (todas)" | `.strip.st-xa-all` |
| `.chip.xa` com nome que começa com "M" (MR18, MR12) | `.strip.st-green` |
| `.chip.xa` com outro nome (XR18, X18, XR16, XR12) | `.strip.st-cyan` |
| `.chip.xm` "X32/M32 (todas)" | `.strip.st-xm-all` |
| `.chip.xm` com nome que começa com "M" (M32, M32R, M32C) | `.strip.st-magenta` |
| `.chip.xm` com outro nome (X32, X32 Rack, X32 Compact, X32 Producer) | `.strip.st-amber` |
| `.chip` sem família | `.strip.st-white` |

```python
def strip_cls(chip_cls, name):
    if chip_cls == 'all': return 'mesas13'
    if name.endswith('(todas)'): return 'st-xa-all' if chip_cls == 'xa' else 'st-xm-all'
    if chip_cls == 'xa': return 'st-green' if name.startswith('M') else 'st-cyan'
    if chip_cls == 'xm': return 'st-magenta' if name.startswith('M') else 'st-amber'
    return 'st-white'
```

### 6.4 Notas do apresentador e links: as duas checagens que o gerador tem que ter

**Notas.** O `build_slides.py` monta a nota de cada slide a partir do bloco de origem, e isso continua. Quem **copiar** notas de um deck pronto (como esta amostra faz) tem que achar a seção **mais interna** que contém o marcador. Não pode usar `rfind('<section', 0, p)`: quando o marcador já começa com `<section`, esse `rfind` devolve a seção **anterior**. Foi o bug que pôs em 12.1.1 a nota do índice do cap. 12, e em 6.2.1 a nota de 6.1.2.

```python
def owner(p):  # início da <section> mais interna que contém a posição p
    st = []
    for m in re.finditer(r"<section\b|</section>", SRC[:p + 8]):
        st.pop() if m.group()[1] == "/" else st.append(m.start())
    return st[-1]

# checagem: a nota usada tem que PERTENCER à seção de destino, não só existir no deck
for marker, nt in zip(destinos, notas_usadas):
    assert SRC.count(nt) == 1
    assert owner(SRC.index(nt)) == owner(SRC.index(marker))
```

**Links.** "Ver capítulo N →", sumário, agenda e "Próximo capítulo" apontam para `#/id`. No gerador, depois de montar o `out`:

```python
ids = set(re.findall(r'\bid="([^"]+)"', out))
bad = [h for h in re.findall(r'href="#/([^"]+)"', out) if not h.isdigit() and h not in ids]
assert not bad, bad          # hoje: cap-0…cap-27, s6-2-1…, encerramento
```

O `build.py` da amostra já confere que `cap-5…cap-10`, os destinos do interativo, existem no deck. Na amostra, que só tem o cap-6, o link cai em `../../index.html#/cap-N`: o `motion.js` usa `#/cap-N` quando o id existe e o deck completo quando não existe.

---

## 7. Ajustes no gerador (resumo)

1. **`slides_viz.py`**:
   - `viewBox` 612×640 (coluna), 560×358 (instrumento ao lado de tabela) ou 1168×424 (figura).
   - Portar `knob/fader/meter/lcd/frame/key` de `_src/build.py`. O tamanho de texto vai sempre no atributo, conforme a camada.
   - Emitir `data-g` + `G` (seção 5).
2. **`split()`**: medir a coluna de 512px com 28px e o título pela regra do 3.3. Espere mais slides de continuação: o mínimo de 28px vale mais que a densidade.
3. **CSS**: trocar o `<style>` do template por `_src/style.css`.
4. **JS**: incluir os 5 GSAP de `lib/gsap/` (+ `Flip.min.js` para a figura) e o `_src/motion.js`. O `Reveal.initialize` está nele (`transition: 'none'`). Os handlers antigos de quiz e blocos foram absorvidos.
5. **Defs**: emitir o `<svg>` de `<defs>` uma vez, logo depois de `<body>`.
6. **Checagens** do 6.4 (notas e links) no `__main__` do gerador.

---

## 8. Limites conhecidos
- A DIN só existe no macOS. No Windows entra a Bahnschrift. Em Linux cai em Arial Narrow ou sans-serif, e o visual fica mais genérico.
- No slide de medidores, a aba IN/OUT existe na tela mas não tem fragment: o slide original mostra só Channel, Mix Bus, Aux/FX e RTA.
- Os layouts 3.4 e 3.8–3.14 estão especificados, mas **não estão desenhados nesta amostra**. Os 6 slides de amostra são os pedidos. As peças 6.1 marcadas "= amostra" existem; as outras são especificação para portar.
- Os controles do reveal (setas, canto inferior direito, opacity .45) ainda encostam no canto do painel do slide interativo.
