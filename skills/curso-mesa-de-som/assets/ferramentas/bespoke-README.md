# Diagramas sob medida (`tools/bespoke/`)

**Qualquer slide** aceita `tools/bespoke/<id>.svg` (desenho) e `tools/bespoke/<id>.js` (movimento). Onde o SVG entra depende do tipo (seção 0).
No tópico, o SVG fica **no lugar do diagrama genérico** (`slides_viz.py`) e o resto (carcaça de 3 faixas, teclas de passo, "PASSO f/n", entrada e fragments) continua do controlador `diag` do `slides_template.html`.
Nos outros tipos, o controlador do tipo (abertura, quiz, capa…) continua fazendo a entrada dele, e o orquestrador chama o JS sob medida por cima.

Exemplo funcionando: `s9-1-1.svg` + `s9-1-1.js` (Insert). Desde 21/10/2026 (motion total) **todos os slides têm `.js` sob medida** (144 depois da neutralidade, seção 8); os `.js` antigos tirados do deck ficam em `bespoke/_extra/` (o build não os lê). Os sob medida dos slides retirados na neutralidade (`abertura`, `s26-1-1`, `s26-2-2`, `s26-2-3`) estão em `backups/antes-neutralidade-2026-10-21/removidos-bespoke/`.
Tópico com diagrama trocado no enxugamento (`DIAG` do `enxugamento.py`): o build usa o genérico e **ignora** o `.js`. Quando o sob medida for refeito para o conteúdo novo, tire o id do `DIAG` (lista no fim do `enxugamento.py`).

## 0. Contrato por tipo

| Tipo (`data-anim`) | ids | Onde entra o `<id>.svg` | O `.js` |
|---|---|---|---|
| tópico (`diag`) | `sN-N-N` | no lugar do diagrama genérico, dentro da carcaça (seções 3 e 4) | `init/enter/step/leave`, chamado pelo `diag` (vale para a continuação `-c2`) |
| abertura de capítulo (`opener`) | `cap-N` | `.op-bsp`, entre o número e a barra de atos (o número encolhe para 240 px). Tela de **430 px** de largura: desenhe com `viewBox` de **~320 de largura** (escala 1,34; texto de 14 unidades = 19 px) e altura livre até ~160 | `enter` coreografa o motivo junto com o número que enche (0,35–1,55 s) e a linha de sinal (0,2–2,0 s). Exemplo: `cap-5` |
| quiz (`quizw`) | `quiz-N` | o slide passa a ter **duas colunas** (`.quiz.bspq`, 620 px + painel): o SVG vai para a carcaça da direita, sem teclas, com o `.vt` como título. Tela ~**440 × 530 px**: `viewBox` de **~330 × 372 a 400** (escala ~1,33) | `reset` monta o estado **PERGUNTA**, `answer(x, r)` anima o estado **RESPOSTA** (`r.ok` certo/errado). Exemplo: `quiz-5` |
| `quiz-7` (`quizgate`) | `quiz-7` | o gate feito à mão continua; aqui só o `.js` (`x.svg` = o SVG do gate) | complementa |
| capa, sumário, como-usar, encerramento, fechamento do cap. 26, explorador, caminho-do-sinal, glossário… | `capa`, `sumario`, `como-usar`, `encerramento`, `s26-2-1`, `explorador`, `caminho-do-sinal`, … | **camada** `.bsp-layer` do tamanho do slide (`viewBox="0 0 1280 720"`, `pointer-events: none`, por cima do conteúdo). Desenhe só onde o slide tem espaço livre: **nada por cima de texto** | complementa a interatividade que já existe (clique em bloco, mesa, termo): nunca a substitui. Sem `.svg`, `x.svg` aponta para o SVG próprio do slide (`.console` da capa, `.flowfig svg` do caminho do sinal, `.viz svg` do HPF) |
| tópicos de tipo próprio (`hpf`, `errfix`) | `s6-2-1`, `s24-2-1` | o build **não** põe camada em `<section class="topic …">`: sem `.svg`. `x.svg` = o SVG do slide (`.viz svg`, no HPF) ou nada | complementa o controlador do tipo. Exemplos: `s6-2-1` (espectro que afunda junto com o render do `hpf`), `s24-2-1` (cria a própria camada no `init`, só no vão entre as colunas) |

- O build só lê `tools/bespoke/` (as pastas `_extra/` ficam de fora). `--only` aceita todos esses ids (seção 2).
- O `<id>.svg` de qualquer tipo passa pelo mesmo `dg()` do tópico: classes do mapa (seção 3), glifos `→ ✓ ✕` na fonte de símbolos e o 1º `.vt` vira o título (só onde há carcaça: tópico e quiz).

## 1. Qual é o `<id>`

- O `id` da `<section>` do tópico: seção `9.1.1` → `s9-1-1`. Vale para os tópicos com diagrama (`topic diag`).
- A continuação gerada no navegador (`s9-1-1-c2`) usa o mesmo par de arquivos. No JS, `x.cont` diz se o slide é a continuação.
- Os bullets da seção (quantos são e o rótulo de cada tecla) estão no slide gerado (`data-i`, `data-k`) e em `slides_steps.py` (`STEPK`).
  O texto dos bullets escritos à mão fica em `CUSTOM`, no `build_slides.py`.

## 2. Prévia sem mexer no deck

```bash
python3 -I tools/build_slides.py --only s12-1-1 --out /tmp/prev-s12-1-1.html
python3 -I tools/build_slides.py --only s9-1-1,s9-1-2,quiz-9 --out /tmp/prev-cap9.html
```

O arquivo sai só com esses slides, com `lib/` e `fonts/` apontando para `07-slides/`. Ele **não** sobrescreve `07-slides/index.html`, por isso vários agentes podem testar ao mesmo tempo, cada um no seu arquivo.
Todo slide tem `id`. Os tópicos são `sN-N-N` e as aberturas `cap-N`. Os outros são `agenda-N`, `fig-N-k`, `quiz-N`, `fecha-N`, `explorador`, `caminho-do-sinal`, `capa`, `sumario`, `sumario-2`, `como-usar`, `s26-2-1` (fechamento do cap. 26) e `encerramento`.
Para medir a prévia, use `node tools/check_fonts.mjs /tmp/prev.html` e `node tools/verify_slides.mjs /tmp/prev.html`.

## 3. O SVG

**Tamanho e escala**
- Largura do `viewBox` = **400**, como nos diagramas do `slides_viz.py`. Na tela, a carcaça mostra o desenho entre 1,46× e 1,87×.
- A tela (`.vscreen`) tem cerca de **600 × 440 px** quando o slide tem 2 ou mais bullets, porque as teclas ficam embaixo. Com 0 ou 1 bullet, tem cerca de **600 × 540 px**.
  Desenhe com proporção perto de **1,35** (400 × ~300) no primeiro caso e de **1,1** (400 × ~360) no segundo. Desenho largo e baixo deixa faixa vazia em cima e embaixo.
- Na 1ª entrada, o `viewBox` é **recortado ao conteúdo** (`getBBox` + 8). Para garantir uma margem, desenhe um `<rect fill="none">` do tamanho do quadro.
  O build não corta a faixa de cima do SVG sob medida (o genérico perde 24 unidades).
- O 1º `<text class="vt">Título</text>` sai do SVG e vira o cabeçalho da carcaça (`.vh .vt`).

**Texto** (DESIGN.md 1.2 e 1.4)
- Use as classes do mapa: `b` (15, rótulo de caixa), texto sem classe (15), `sm` (14, nota), `lbl` / `lblr` (14, destaque laranja / aviso vermelho), `zl` (14 mono, título de painel), `tw` (texto claro em caixa escura), `bb` (21, número grande).
  No slide, isso dá **20 px ou mais**. Nunca use menos de 13,5 unidades. `check_fonts.mjs` reprova texto abaixo de 18 px.
- `text-anchor` em todo `<text>` (o padrão do SVG é `start`).
- `→ ← ✓ ✕ ⚠` podem ir direto: o build envolve esses glifos em `<tspan class="sym">`, a fonte de símbolos.

**Cor e forma**
- Use as classes de caixa e de linha da tabela 1.2: `bx`, `bxo` (foco), `bxg` (rota paralela, tracejada), `bxb` (destino), `bxr` (barrado), `bxd` (aparelho), `panel`, `ln`, `ln2`, `lnd`, `lnx`, `ctl`, `sep`, `thr`, `curve*`, `zg`/`zy`/`zr`/`zgr`, `bar*`, `hl` (moldura de destaque) e outras.
- Se precisar de outra cor, use **só os tokens**, em `style`: `style="fill:var(--accent)"`, `var(--led-red)`, `var(--xair)`, `var(--x32)`, `var(--bg-1)`, `var(--ink-2)`…
- A regra de cor vale também aqui. Verde, amarelo e vermelho **só com sentido de medidor** (ou certo/errado). Família = cor de fita (`--xair`, `--x32`). Nada de verde para "parte" ou enfeite.
- Os marcadores de seta `#ah` e `#ahr` já existem no documento. Use as classes de linha (`ln` etc.) e **não** crie `id` dentro do SVG: o mesmo desenho pode aparecer duas vezes (slide e continuação).

## 4. Sincronizar com os fragments (bullets)

Os atributos vão nos **filhos diretos** do `<svg>`. Pode ser um `<g>` com várias peças dentro.

| Atributo | Comportamento |
|---|---|
| sem atributo | desenho principal: liga na entrada (caixas assentam, linhas se desenham, medidores sobem) e fica aceso |
| `data-step="k"` | acende com o **k-ésimo bullet da seção** (1..n). Antes fica em esqueleto (opacidade 0,2); ao acender, as linhas se redesenham e os textos sobem 8 px. Voltar o fragment devolve a 0,2 |
| `data-step="k" data-only="1"` | só aparece enquanto o bullet k é o atual (destaque que passa de peça em peça) |
| `data-first="1"` | só no 1º slide da seção; some na continuação |
| `data-own` | o controlador genérico **não toca** nesta peça. Ela é só do JS sob medida (entrada, cor, escala) |

O número k conta os bullets da **seção inteira**, não só os do slide (a continuação começa no bullet seguinte). Uma peça de um bullet que foi para a continuação some do 1º slide.

## 5. O JS (opcional)

O arquivo é JavaScript puro. Ele registra o slide pelo id:

```js
bespoke('s12-1-1', {
  init(x) { },          // uma vez por slide (o original e cada "-c2"), na 1ª entrada, com o slide visível (getBBox funciona)
  enter(x, tl) { },     // em cada entrada, depois da entrada do tipo; acrescente tweens em tl (posições em segundos)
  step(x, k, f) { },    // em cada fragment e ~0,25 s depois da entrada: k = bullets da seção já mostrados (0 = nenhum), f = índice do fragment no slide (-1 = nenhum)
  leave(x) { },         // ao sair do slide (mate o que estiver rodando)
  answer(x, r) { },     // só quiz: clique/Enter/Espaço numa alternativa. r = { ok, pick, ans } (ok = acertou; pick e ans de 0 a 2)
  reset(x) { }          // só quiz: volta ao estado PERGUNTA. Roda no início de cada entrada, na tecla R e ao sair
});
```

- Fora do tópico, `step` recebe `k = f + 1` (fragments já mostrados; não há continuação).
- `x` é **um objeto por slide**: `x.s` (a `<section>`), `x.svg`, `x.uid`, `x.cont`, `x.type` (o `data-anim`: `diag`, `opener`, `quizw`, `cover`…). Guarde o estado em `x`, nunca no objeto do `bespoke`, porque o slide e a continuação dividem esse objeto.
- O build só inclui o `.js` se o slide estiver no deck (vale para `--only`). Ele entra num `<script>` depois do script principal, então você pode usar `gsap` (com DrawSVG, MotionPath, CustomEase `stage` e `fader`), `$`, `$$`, `mk`, `C` (cores), `RM` e `loops`.
- **Entrada**: a carcaça aparece em 0 s e o desenho genérico liga entre 0,08 e 0,5 s. Ponha o protagonista sob medida entre 0,1 e 0,8 s (DESIGN.md 3.3). Nada estrutural começa em opacidade 0 depois de 0,1 s.
- **Fragments**: `step` monta o estado **só a partir de `k`**. Mate os tweens antes e vá ao alvo. Voltar um fragment ou pular vários de uma vez precisa dar o mesmo quadro que chegar ali passo a passo.
  Animação de "acontecimento" (o medidor bater, o sinal andar) só quando `k === anterior + 1`.
- **Movimento reduzido**: com `RM` verdadeiro, a timeline `tl` da entrada vai ao fim sozinha. Em `step`, não anime: aplique o estado final (ou `duration: 0`).
- **Repetição infinita** só se for indispensável. Faça `loops.push(tween)`: tudo o que está em `loops` morre na troca de slide.
- Anime só `transform`, `opacity` e `drawSVG` (DESIGN.md 3.1). Nunca anime filtro, sombra, largura ou altura. Medidor sobe por `scaleY` a partir da base ou por um obturador.
- Número que descreve o desenho (Hz, dB, ms) muda **no mesmo `onUpdate`** que move o desenho (DESIGN.md 3.5).

### 5.1 Eventos (DOM)

Além dos ganchos acima, o orquestrador dispara `CustomEvent` na `<section>`. Eles não borbulham: escute no próprio slide ou no `document` com captura (`addEventListener(tipo, fn, true)`).

| Evento | Quando | `detail` |
|---|---|---|
| `slide:enter` | toda entrada, depois do `enter` do tipo e do sob medida | `{ tl }` (a timeline da entrada) |
| `slide:leave` | ao sair, depois do `leave` | `{}` |
| `fragment:shown` / `fragment:hidden` | cada fragment | `{ f, fragments }` |
| `quiz:answered` | resposta escolhida (o quiz trava) | `{ ok, pick, ans }` |
| `quiz:reset` | início da entrada, tecla R, saída | `{}` |

Use os ganchos (`answer`, `reset`…) para o desenho do próprio slide. Os eventos servem para quem precisa ouvir de fora (ex.: medir, ou um slide reagir ao quiz).

### 5.2 Quiz: PERGUNTA → RESPOSTA

- **PERGUNTA** (`reset`): o painel já está ligado (o sinal toca, a mesa mostra o estado atual) e só a parte que **entregaria a resposta** fica apagada ou em esqueleto 0,2. Nada de painel vazio (DESIGN.md 2.5).
- **RESPOSTA** (`answer`): sempre a mesma estrutura (DESIGN.md 2.5): a referência se desenha → a agulha varre / o controle gira → o efeito acontece → a faixa de saída acende. Comece em até 0,1 s: o veredito em texto chega em 0,3 s.
- **Errou** (`r.ok === false`): antes da resposta certa, mostre em ~1,2 s **o que a alternativa errada faz** (no `quiz-5`: o ganho sobe demais, o medidor bate no teto e o CLIP pisca) e volte. É a causa → efeito do erro.
- `answer` com `RM`: aplique o estado final direto. `reset` nunca anima.

### 5.3 Movimento reduzido (`RM`)

- A timeline `tl` da entrada vai ao fim sozinha: escreva a entrada inteira em `tl`, sem `gsap.to` solto nem `delayedCall`.
- `step`, `answer`, `reset`: com `RM`, aplique o estado final (`gsap.set` ou `duration: 0`). Sem tremor, pulso, piscar, varredura nem repetição.
- Confira com `reducedMotion: 'reduce'` no Playwright (o `check_fonts.mjs` já mede assim).

### 5.4 Coreografia e duração ("Palco escuro", `07-slides/redesign/opcao-1/DESIGN.md` seção 3)

- **Personalidade "balística de medidor"** (3.1): chega rápido e assenta suave. Easing `stage` (entradas, 80%), `fader` (controle físico, varredura), medidor sobe `power2.out` 0,07–0,3 s e cai `power1.in` 0,35–0,7 s. Overshoot (`back.out`) só em acerto, LED de tecla e ponto de gráfico.
- **Durações**: rápida 0,15–0,3 s · padrão 0,45–0,6 s · lenta 0,9–1,4 s (desenho). Stagger: texto 0,04–0,09, medidores 0,04–0,07, barras 0,008–0,02; cada grupo ≤ 0,5 s no total.
- **Troca sem pisca** (3.2): a carcaça/motivo começa **visível em 0 s a 0,3–0,4** e chega a 1 em 0,6 s com 24 px (`fromTo(x.svg, { autoAlpha: .4, x: 24 }, …, 0)`). Nada estrutural começa em 0 nem depois de 0,1 s.
- **Ordem da entrada** (3.3): 0 s carcaça e kicker · 0,04 título · 0,08–0,25 corpo · **0,12–0,8 o protagonista liga** (DrawSVG, medidor, MotionPath) · chips e legenda por último. Na abertura de capítulo, encaixe o motivo entre a linha de sinal (0,2–2,0 s) e o número que enche (0,35–1,55 s); a história do motivo termina até ~2 s.
- **Causa → efeito**: o movimento mostra o conceito. Algo muda de estado (o ganho gira → a onda cresce → o medidor chega ao alvo) e o número que descreve o desenho muda no mesmo `onUpdate` (3.5).
- **Fragment** (3.4): cada fragment muda o protagonista; o estado sai só de `k`; "acontecimento" só em `k === anterior + 1`.
- Só `transform`, `opacity`, DrawSVG e MotionPath. Nada de repetição infinita fora da capa (ambiente).

## 6. Conferência antes de entregar

1. `python3 -I tools/build_slides.py --only <id> --out 07-slides/redesign/prev-<id>.html` e olhar a prévia: estado inicial, cada fragment, voltar fragment e movimento reduzido. No quiz: errar, R, acertar. Exemplos dos tipos novos: `--only cap-5,quiz-5`.
2. `node tools/check_fonts.mjs /tmp/prev.html`: menor texto 18 px ou mais, nada vazando.
3. Movimento: `node tools/shot_motion.mjs <html> <pasta> [id …]` tira, por slide, uma tira com 0 ms, 300 ms, 800 ms e o estado final (relógio do GSAP parado e posto em cada instante).
4. No deck inteiro: `python3 -I tools/build_slides.py`, `node tools/verify_slides.mjs 07-slides/index.html` (0 erros de JS).

## 7. Aberturas (`cap-N`): o sistema

Cada abertura de capítulo tem um **motivo**: uma micro-história de causa → efeito que antecipa o tema do capítulo, contada em ~2 s junto com o número que enche.
O motivo não é enfeite: algo muda de estado e o aluno vê o resultado (o ganho gira → o medidor chega ao alvo; o fader desce → só o retorno pós cai).
Prontos: `cap-1` a `cap-13` (tabela 7.4). Siga o mesmo molde nos que faltam.

### 7.1 Quadro
- `viewBox="0 0 324 H"`, com `H` entre 112 e 140, e um `<rect width="324" height="H" fill="none"/>` de moldura. Na tela vira 430 px de largura (escala 1,33).
- Texto: `sm`, `lbl`, `lblr`, `zl` (14) e `b` (15). Nada abaixo de 14 unidades (= 18,6 px). No máximo 3 ou 4 rótulos curtos: o título e a promessa estão ao lado.
- Classes do mapa (seção 3) para caixas, linhas, medidores (`zg`/`zy`/`zr` + obturador `#05070a` a 0,86), fader (`track` + `cap`/`capo`), RTA (`bar`/`barr`).
- Classes próprias do JS com o prefixo `m-` (`m-pk`, `m-sh`…), para não colidir com o mapa. Sem `id`.
- O pulso de sinal é sempre o mesmo: `<circle class="m-pk" cx="0" cy="0" r="4" style="fill:#ffd9a8"/>`, a mesma cor do ponto da linha de sinal. Para andar por um trajeto, ponha um `<path class="m-p…" style="fill:none;stroke:none"/>` invisível.

### 7.2 Coreografia comum (três tempos)

| Tempo | Quando | O quê |
|---|---|---|
| Carcaça | 0 → 0,6 s | `tl.fromTo(x.svg, { autoAlpha: .4, x: 24 }, { autoAlpha: 1, x: 0, duration: .6 }, 0)` (troca sem pisca). Sempre a 1ª linha do `enter`. |
| 1 · Entrada | 0,1 → ~0,9 s | a "origem" se monta: a onda, a linha ou o cabo se desenha (DrawSVG, `power2.inOut`, 0,4–0,6 s), as barras do RTA sobem (proxy `A` de 0 a 1, `power2.out`), o pulso parte (`MotionPath`). Junto com o número que começa a encher (0,35 s). |
| 2 · Ação | ~0,6 → 1,6 s | o controle age (`ease: 'fader'`, 0,6–0,75 s: fader, botão, atraso, cursor) e o efeito muda **no mesmo `onUpdate`** (medidor, curva, visor em dB/Hz/ms). |
| 3 · Saída | ~1,3 → 2,0 s | o resultado pousa: o destino acende, o alvo/limiar se desenha, o rótulo final sobe (8 px, 0,35–0,4 s). A história acaba até ~2,0 s, junto com a linha de sinal. |

- Tudo dentro de `tl` (o `RM` leva `tl` ao fim): sem `gsap.to` solto, sem `delayedCall`, sem repetição. O **quadro final** é o conceito resolvido (é ele que o `RM` e o print mostram): termine no estado que ensina (refrão comprimido, retorno pós caído, apito cortado), não no estado neutro.
- As aberturas não têm fragments: não escreva `step`. `leave` é desnecessário (a `tl` é finalizada e morta pelo orquestrador).
- Proxy em `x.v` + `draw(x)` que põe **tudo** no lugar a partir dele; no `enter`, zere `x.v` e chame `draw` antes de montar a `tl`. Contas que leem o SVG (`getBBox`, `getTotalLength`) ficam no `init`.

### 7.3 Armadilhas (já resolvidas nos prontos)
- **Pulso**: `gsap.set(pk, { autoAlpha: 0 })` antes da `tl`; depois `tl.set(pk, { autoAlpha: 1 }, t).to(pk, { motionPath: { path, align: path, alignOrigin: [.5, .5] }, duration, ease }, t).to(pk, { autoAlpha: 0, duration: .15 }, t + duration)`. Sem isso o círculo aparece no canto (0,0).
- **Linha tracejada** (`thr`, `lnd`, Wi-Fi): o DrawSVG apaga o tracejado. Entre com `scaleX` a partir da esquerda (`transformOrigin: '0% 50%'`) ou com opacidade.
- **Arco com ponta redonda** em `drawSVG: '50% 50%'` vira um ponto: some com `autoAlpha: 0` no `from`.
- **Curva que muda de forma** (low cut, sino do EQ, corte estreito): não use `scaleY` num traço (o traço afina até sumir). Faça a curva de `<line>` curtas (2–3 unidades) e, a cada `onUpdate`, dê a cada uma `y`, `rotation` e `scaleX` (origem `svgOrigin` no começo do segmento, posto uma vez no `init`). Modelo: `cap-6`, `cap-12`.
- **Traço que acompanha um cursor** numa onda: o DrawSVG mede comprimento, não x. Monte no `init` a tabela x → comprimento (`getPointAtLength`). Modelo: `cap-7`.
- **Medidor**: obturador com `transformOrigin: '50% 0%'` (vertical) ou `'100% 50%'` (horizontal) e `scaleY`/`scaleX` = 1 − nível. Barra de RTA: `svgOrigin` na base.
- Overshoot (`back.out`) só em LED que acende (`cap-2`).

### 7.4 Catálogo

| id | Capítulo | Motivo (causa → efeito) |
|---|---|---|
| `cap-1` | Conheça as mesas | a fita de cada família cola, o pulso corre a linha e acende o MESMO chip dentro de caixas de tamanhos diferentes ("mesmo processamento") |
| `cap-2` | Painel, conectores e ligações | o plugue entra, o cabo se estende, liga 1 mesa → o sinal corre → liga 2 PA → as ondas saem limpas |
| `cap-3` | Rede e controle remoto | Wi-Fi acende; o fader do tablet sobe, os pacotes vão (ar + cabo), o fader da mesa obedece (visor −20 → 0 dB) e a resposta volta |
| `cap-4` | Apps, navegação e organização | canais embaralhados deslizam para a ordem, ganham cor e nome; a VOZ 1 é achada (moldura) e o fader sobe |
| `cap-5` | Caminho do sinal, fonte e ganho | entrada fraca → o GANHO gira → a onda cresce e o medidor chega a −18 |
| `cap-6` | Low cut e equalizador | a curva plana dobra no grave (100 Hz) e cava 500 Hz (−4 dB); as barras do RTA caem nas mesmas frequências |
| `cap-7` | Gate e expansor | o cursor do tempo varre: o LED abre só nas batidas acima do limiar e a saída se escreve sem o vazamento |
| `cap-8` | Compressor | verso/refrão: a entrada pula, o fader do COMP desce sozinho (GR −5 dB), a saída fica no alvo |
| `cap-9` | Delay, pan e stereo link | o microfone de perto é atrasado até alinhar com o de longe (0 → 8,7 ms) e a soma cresce; o pan anda no arco até L30 |
| `cap-10` | Buses, envios e pontos de captação | o sinal desce pelos pontos pré e pós; o fader desce e só o retorno pós cai |
| `cap-11` | Retornos de palco, in-ear e P16 | três linhas saem do AUX; cada destino (caixa, in-ear, P16) recebe uma mix diferente; o Aux 2 sobe e só o in-ear muda |
| `cap-12` | Medidores, RTA, microfonia e afinação | uma barra passa do limite (apito), o cursor acha a frequência (2,3 kHz), o corte estreito abre e a barra volta ao verde |
| `cap-13` | Efeitos | o seco chega ao MAIN; uma cópia desce pelo envio ao REVERB e volta pelo retorno: a cauda aparece depois do seco, decaindo |

### 7.5 Conferência
`python3 -I tools/build_slides.py --only cap-1,…,cap-13 --out 07-slides/redesign/preview-cap-a.html`, prints aos 150 ms, 0,5 s, 1 s, 1,5 s e 2,6 s e com `reducedMotion: 'reduce'` (deve mostrar o quadro final de saída), `node tools/check_fonts.mjs` e `node tools/verify_slides.mjs` na prévia (0 erros de JS).

## 8. Selo "Abordagens divergentes" (neutralidade, 21/10/2026)

O curso é completo em si: **não cita professores, autores, escolas, cursos, canais, fóruns nem lojas como fonte**.
Quando há mais de um jeito correto de fazer o mesmo ajuste, aparece **um selo único**, igual no slide e no PDF, com **todas as abordagens**, cada uma com o seu efeito e o contexto em que costuma ser usada, **sem escolher lado e sem dizer quem pensa assim**. Dado que muda com a unidade, a versão ou o firmware (não é escolha) continua com o **⚠** de "confira na sua mesa".

**Desenho.** Âmbar (`--accent`), ícone de bifurcação (um ponto, mais de um caminho correto) e o rótulo **ABORDAGENS DIVERGENTES** em mono. As opções levam letras (A, B, C…) na ordem em que aparecem, todas com o mesmo peso: nenhuma em destaque, nenhuma "certa".

| Onde | Como escrever | O que sai |
|---|---|---|
| PDF (`05-curso-final.md` → `build_pdf_html.py`) | um bloco de citação que começa com `> **Abordagens divergentes:** assunto.` e uma lista `> - **Opção:** efeito. Contexto.` | `<blockquote class="diverge">`: caixa âmbar com o selo (`.dv-badge`, SVG inline) e o assunto em negrito; legenda em "Como usar este material" |
| Slide escrito à mão (`enxugamento.py`, `BULLETS`) | `'[D] Assunto \| opção A \| opção B'` (até 4 opções curtas) | `build_slides.divg_li()`: `<li class="fragment divg" data-src="D">` com `.dvb` (selo), `.dvt` (assunto) e `.dvo` (cada opção com a sua letra) |
| Slide gerado do PDF (`summary`) | o próprio `blockquote.diverge` | o mesmo `li.divg`, com o rótulo em negrito de cada item como opção |
| Tabela do HPF (`s6-2-1`) | `DVB` dentro do `<small>` da linha | o selo pequeno e a alternativa ("ou sem filtro") |
| Legenda (`como-usar`) | `HOWTO` em `build_slides.py` | o selo e "Mais de um jeito correto: todas as opções, sem escolher lado." |

**Regras.**
- O `[D]` entra **na posição do bullet** que antes trazia a regra de um lado só: o número de bullets não muda e os `data-step` dos desenhos sob medida continuam certos.
- Letra mínima: o selo é rótulo (18 px, mono); assunto e opções são corpo (28 px, herdam o `.pts li`). Opção curta: cabe numa linha da coluna de 510 px.
- Desenho sob medida de um bullet `[D]` mostra **as abordagens com o mesmo peso** (ex.: `s4-2-11` desenha A, muda o cabo, e B, muda o roteamento; `s8-2-5` passa por A, B e C no GR; `s23-2-1` sobe as duas ordens e tira os números no fim). Nunca deixe só uma opção acesa como resposta.
- Rótulo de diagrama nunca é nome de pessoa: use "Abordagem A/B" ou o nome do método ("voz primeiro", "plano por fonte").

**Movimento (discreto, `slides_template.html`).** Quando o bullet `.divg` acende (`onFragment` → `divgIn`): a bifurcação se desenha (tronco e depois os ramos, DrawSVG 0,32 s, stagger 0,07) e as opções entram uma a uma (x −12 → 0, 0,4 s, stagger 0,09, a partir de 0,18 s). Com movimento reduzido, nada anima. Na legenda (`como-usar.js`), a bifurcação se desenha e o selo assenta (escala 0,94 → 1).

**Lista dos pontos.** O capítulo 24.2.3 do PDF lista todos os pontos com selo e a seção de cada um.

