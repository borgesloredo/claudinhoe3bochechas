# V2 dos slides (autoestudo)

A V2 tem os mesmos slides da V1, sem nenhuma mudança neles. A V2 só acrescenta dois botões em todos os slides:

- **(i)**: abre um popup com a explicação do slide, escrita para quem é leigo. Os termos técnicos do texto são clicáveis e mostram a definição dentro do próprio popup, com um botão para voltar.
- **▶**: toca o áudio da explicação, com voz masculina, mais longo e mais didático que o texto do (i).

O conteúdo fica em três níveis: o slide (raso), o (i) (mais explicado) e o ▶ (o mais explicado).

A V1 (`entregas/v1-aulas/`) é só leitura. O build lê a V1, mas nunca grava nela.

## Gerar

```sh
python3 -I tools/v2/build_v2.py                     # gera 08-slides-v2/ e tools/v2/slides.json
node tools/v2/check_identico.mjs                     # todos os slides: V1 = V2, pixel a pixel, e nada embaixo dos botões
```

A saída fica em `08-slides-v2/`: `index.html`, `lib/`, `fonts/` e `audio/`. Funciona offline, abrindo direto o `index.html`, e não tem caminhos `../`, que o Safari bloqueia.

Opções do build:

| Opção | Padrão | Para quê |
|---|---|---|
| `--info DIR` | `tools/v2/info` | pasta com os `<id>.html` do popup |
| `--out DIR` | `08-slides-v2` | pasta de saída |
| `--audio-ext EXT` | o que existir | força a extensão do áudio. Sem ela, o build usa o primeiro arquivo que achar, nesta ordem: m4a, mp3, ogg, opus, wav |

O build avisa quando um `info/*.html` não corresponde a nenhum slide e quando um termo marcado não tem verbete. Esse termo vira texto comum.

## Entradas

| Arquivo | O que é |
|---|---|
| `slides.json` | Gerado pelo build a partir da V1, com os 144 slides em ordem. Cada um tem `id` (o mesmo da `<section>`), `capitulo`, `h`, `v`, `tipo`, `titulo`, `texto` (o texto visível) e `nota_v1` (a nota do apresentador da V1). É a fonte para escrever o `info/` e o `script/`. |
| `info/<id>.html` | Conteúdo do popup (i). É um trecho de HTML simples: `<p>`, `<ul>`, `<ol>`, `<li>`, `<b>`, `<em>` e `<h3>` para subtítulo. Não pode ter `<script>`, atributos `on*=` nem `../`. O título do popup vem do próprio slide (o primeiro título; num slide sem título, como o glossário, vem o kicker). |
| `glossario.json` + `glossario-extra-*.json` | Os verbetes. O formato e as regras estão em `GLOSSARIO-GUIA.md`. O build junta todos os arquivos e embute no HTML só os verbetes usados. |
| `<saída>/audio/<id>.<ext>` | O áudio do ▶, gerado pelo TTS (veja `tts/`). |

Para marcar um termo no `info/`, use `<span class="gl" data-t="slug">texto</span>`. O build converte a marca num botão, que funciona no teclado e no leitor de tela.

Um slide sem `info/` ou sem áudio aparece com o botão correspondente apagado e desabilitado. Um slide "(continuação)" criado na hora pela V1 (id `<id>-cN`) usa o conteúdo do slide de origem quando não tem o seu próprio. Hoje a V1 não cria nenhum.

## O que o build muda no HTML da V1

1. Tira as 144 `<aside class="notes">`, o `notes.js` e o `RevealNotes`. A tecla S deixa de abrir as notas, e a pasta `lib/plugin/notes` não é copiada.
2. Acrescenta o `<style id="v2-css">` no `<head>`. Todas as regras são novas e usam o prefixo `v2`; nenhuma regra da V1 muda.
3. Acrescenta `<div class="v2ctl">` logo depois do cromo, dentro do palco de 1280×720, para que os botões escalem junto com o slide. Os botões ficam fora do `.chrome` porque o cromo some na capa e os botões precisam aparecer em todos os slides.
4. No fim do `<body>`, acrescenta o `<dialog id="v2pop">`, um `<template id="v2i-<id>">` por popup, os dados em JSON (os áudios e os verbetes usados) e o script da V2.

## Posição dos botões

Os botões ficam no **canto superior direito**, empilhados: o (i) em cima e o ▶ embaixo. É o espelho do atalho do sumário, que fica no canto superior esquerdo:

- a área de clique de cada um tem 40×40 px no palco, em x 1234–1274 (6 px da borda direita);
- o (i) fica em y 14–54 e o ▶ em y 58–98;
- os dois desenham o mesmo círculo (26 px), com o ícone dentro.

**Em telas menores** o palco encolhe, mas a área de clique nunca fica abaixo de 40 px de tela. A cada `resize` (do reveal e da janela), o script calcula o tamanho em unidades do palco: `max(40, 40 × escala) / escala`. Depois escolhe a primeira posição que não cobre conteúdo:

1. a coluna no canto, presa à direita, crescendo para a margem preta e, se houver, subindo para a margem de cima, desde que a parte dentro do palco fique na faixa vazia (x ≥ 1220, y ≤ 100). É o caso de 1280×720, 1440×900 e 1024×640;
2. a coluna inteira na margem preta da direita (celular deitado, por exemplo 844×390, com margem de cerca de 75 px);
3. os dois lado a lado na margem preta de cima.

No celular em pé (largura abaixo de 435 px), o reveal troca para a rolagem e o palco não escala. Nesse caso, os botões ficam fixos na borda direita da tela, com 40 px, espelhando o atalho do sumário. Ao girar o celular, o reveal regrava o HTML do palco. Por isso o script sempre busca os botões de novo e trata os cliques por delegação, sem guardar referência aos nós.

**Por que ali:** medi os pixels de conteúdo dos 144 slides, comparando a captura do slide com e sem as `<section>`, no estado final. A faixa de x ≥ 1220 e y ≤ 100 está vazia em todos eles, inclusive na capa. A faixa de baixo não serve. O encerramento tem uma linha em y 676–700, as aberturas de capítulo têm o ponto do sinal e alguns slides têm o botão "Próximo" e as setas do reveal. O lado direito abaixo de y 110 também não serve, por causa dos números gigantes das aberturas. Por isso a mesma posição vale para todos os tipos de slide. O `check_identico.mjs` confere de novo, a cada build, que nenhum pixel de conteúdo cai embaixo dos botões.

**Visual (Palco escuro):**

- Os dois botões formam um par: o mesmo círculo de traço, com o "i" ou o triângulo dentro. Em repouso ficam em `--ink-2`. No hover e no foco ficam laranja (`--accent`), e o círculo ganha um fundo laranja bem leve.
- O foco do teclado é um contorno laranja de 2 px, afastado 3 px do botão, para não encostar no anel de progresso.
- Desabilitado, o botão fica com opacidade 0,3.
- Tocando, o círculo do ▶ vira o trilho do progresso: apaga para `--line-2` e a parte já tocada acende na luz de serviço `--lamp`, a mesma do cromo. O anel não tem brilho.
- Na primeira visita, o (i) dá um único pulso suave, para quem estuda sozinho achar a explicação. O pulso não aparece com `prefers-reduced-motion` e não se repete (fica lembrado no `localStorage`, dentro de `try/catch`).

## Comportamento

- **Popup:** usa um `<dialog>` modal. O texto tem 21 px (exemplo do verbete 20 px, subtítulos 24 px, kicker e "Voltar" 16 px), cerca de 70 caracteres por linha. O X tem 44×44 px e o "Voltar à explicação" tem 40 px de altura. O título vem do HTML da V1, montado pelo build: cada `<br>` ou bloco do título vira " · ". Não depende do `innerText`, que muda com o layout e com a divisão de linhas da animação. Fecha com Esc, com o X ou com um clique fora. Enquanto está aberto, nenhuma tecla chega ao reveal nem ao deck: as setas rolam o texto e não trocam de slide. Ao fechar, o foco volta ao (i). O texto longo rola dentro do popup. No celular, o popup ocupa a largura da tela menos 16 px de cada lado.
- **Termo:** o sublinhado é pontilhado laranja (`text-decoration`, 2 px, afastado 4 px), igual em todos os termos, também em tela de densidade 1. Clicar num termo troca o conteúdo do popup pela definição, com o botão "Voltar à explicação". Voltar devolve a mesma posição de rolagem e o foco ao termo.
- **Áudio:** o ▶ alterna entre tocar e pausar. O áudio nunca toca sozinho e para (e volta ao início) ao trocar de slide. Mudar de fragment no mesmo slide não para o áudio. Se o arquivo faltar, o ▶ fica desabilitado.
- **Teclado:** Enter e Espaço num botão da V2 não avançam o slide.

## Conferências

| Script | O que garante |
|---|---|
| `check_identico.mjs [html] [--so id1,id2]` | Compara a V1 e a V2 em todos os slides, com os botões ocultos pela classe de teste `.v2-test`, `prefers-reduced-motion` e todos os fragments visíveis. Exige **0 pixel diferente**, sem tolerância. Também exige 0 pixel de conteúdo embaixo dos botões. As setas do reveal ficam congeladas nas duas versões, porque a dica "pode descer" pula em loop e não faz parte do slide. Leva cerca de 3 minutos. |
| `check_ui.mjs <html> [pasta]` | Teste de uso com o conteúdo de teste. Confere o popup, o Esc, o clique fora, o teclado bloqueado, o termo e o voltar, o áudio, a parada ao trocar de slide, os botões desabilitados, o tamanho no celular, a ausência de notas, de rede externa e de erro JS. Com `[pasta]`, salva as capturas. |
| `check_glossario.py` | O glossário (veja `GLOSSARIO-GUIA.md`). |

### Conteúdo de teste (`_teste/`)

São 3 slides. A `capa` e o `s5-1-2` têm popup e áudio. O `quiz-7` tem só popup, com texto longo. A capa também tem um termo sem verbete, de propósito. Para rodar:

```sh
T=$(mktemp -d); mkdir -p $T/audio; cp tools/v2/_teste/audio/* $T/audio/
python3 -I tools/v2/build_v2.py --info tools/v2/_teste/info --out $T
node tools/v2/check_identico.mjs $T/index.html && node tools/v2/check_ui.mjs $T/index.html
```

Os áudios de teste foram gerados com o `say` do macOS e servem só para testar o player. Não vão para a saída real.
