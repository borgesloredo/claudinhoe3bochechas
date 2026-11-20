# Aplicação da validação — AudioLab Live XL, 07/11/2026

Só a V2 mudou, e só por meio de `ws/audiolab-live-xl/corrigir.py`. Não editei nada em `ws/audiolab-live-xl/antes/`, `depois/` ou `material/`. Não usei git, navegador, node, TTS nem Whisper.
Backup dos roteiros: `ws/audiolab-live-xl/bak-validacao/` guarda os 5 `quiz-N.txt` originais (4, 7, 10, 20 e 24). Conferi com `ls` (5 arquivos) e com `cmp`: antes da edição, todos eram iguais aos originais.
`08-slides-v2/` tem só um HTML (`index.html`).

## Teste
- `python3 -I ws/audiolab-live-xl/corrigir.py ws/audiolab-live-xl/antes/v2/08-slides-v2/index.html <scratchpad>/audiolab-live-xl-corrigido.html` deu "corrigir ok: 53 trocas". Nenhum assert falhou, e o número de `<section` continuou 149. A saída foi para o scratchpad da sessão, e não para `/tmp`.
- Conferência do diff: tirei dos dois arquivos o slide, o JS sob medida e o (i) de cada quiz, e também o slide s22-1. O resto ficou idêntico. Mudaram só os 18 quizzes CORRIGIR e o s22-1. Nenhum `data-ans` mudou, então o gabarito continua o mesmo.
- Como os desenhos escondem peças antes do toque: o `reset(x)` do JS sob medida esconde a peça. Ele roda na entrada do slide, na tecla R e na saída. Depois, o `answer` mostra a peça no toque, tanto no acerto quanto no erro. Os nomes de classe novos (`q1-real`, `q1-neu`, `q4-lbl`, `q10-dash`) não aparecem em nenhuma regra do CSS nem no `deck.js`.

## Itens (quiz | o que foi feito | onde)
- quiz-1 | Saíram os botões do glossário de `FX1 e FX2 [fx]` e `subgrupos [subgrupo]`. | (i)
- quiz-1 | Antes do toque, as duas mesas reais (`q1-real`) ficam escondidas. No lugar delas aparecem duas molduras tracejadas neutras com "?" (`q1-neu`, classe `slot2`). As etiquetas LIVE 16XL (azul) e LIVE 24XL (magenta) e o visor continuam. No toque, as molduras somem e as mesas reais entram em 0,3 s. Isso acontece antes das demonstrações de erro (faders e SUB1-4) e antes da resposta. A voz e o (i) continuam certos, porque falam só das duas mesas com as etiquetas e do visor. | slide, JS
- quiz-2 | Saiu o botão do glossário de `subgrupos [subgrupo]`. | (i)
- quiz-4 | O título do desenho virou "PAINEL E FADER". O recorte da moldura foi de 174,6 para 164,3, na mesma conta por número de letras dos outros títulos. O rótulo do visor virou "CANAL" antes do toque e volta a "SELECIONADO" no toque (`q4-lbl`). O reset (tecla R) devolve "CANAL". No (i), "Seleção e fader" virou "Painel e fader" e "Selecionado" virou "Canal". Na voz, "com o título painel e fêider" e "um visor chamado canal". | slide, JS, (i), roteiro
- quiz-5 | Saíram os botões do glossário de `mini display [mini-display]` e `camada [camada]`. | (i)
- quiz-7 | No (i), "ainda sem nomes" virou "ainda vazia". Na voz, "ainda com traços no lugar dos nomes" virou "ainda com traços". | (i), roteiro
- quiz-8 | Saiu o botão do glossário de `medidor [medidor]`. | (i)
- quiz-9 | Saiu o botão do glossário de `ganho [ganho]`. O ponteiro do knob GANHO fica ao meio-dia (0°) antes do toque, no SVG e no reset. No toque, ele gira até o valor alto (100°) em 0,3 s. Na resposta certa, ele desce a 15° 0,35 s depois. O medidor e o CLIP seguem com o mesmo atraso. A voz e o (i) não falam da posição do knob. | (i), slide, JS
- quiz-10 | Saiu o botão do glossário de `polaridade [polaridade]`. Antes do toque, as ondas TOP e BOT ficam escondidas, e no lugar de cada uma aparece um "—" (`q10-dash`). A SOMA vermelha fina continua, porque é o cenário. No toque, os traços somem e as ondas entram em 0,2 s, antes das demonstrações. No (i), "as ondas TOP e BOT" virou "as linhas TOP e BOT". Na voz, "Na primeira linha, a onda do top. Na segunda, a onda do bót." virou "Na primeira linha fica o top, e na segunda, o bót." | (i), slide, JS, roteiro
- quiz-11 | Saiu o botão do glossário de `threshold [threshold]`. | (i)
- quiz-14 | Saiu o botão do glossário de `Assign [assign]`. | (i)
- quiz-18 | Saiu o botão do glossário de `DCA [dca]`. Antes do toque, as três linhas verdes VOZ → MAIN (`b-aw`) ficam escondidas, e o reset agora põe a opacidade delas em 0. Na resposta certa, elas entram junto com a tecla DCA, antes dos pontos de sinal que descem por elas. No erro, elas já entravam na demonstração. A voz e o (i) não falam das linhas. | (i), JS
- quiz-19 | Saiu o botão do glossário de `PRE [pre-pos-fader]`. | (i)
- quiz-20 | Saíram os botões do glossário de `AFL [afl]` e `PFL [pfl]`. Antes do toque, o ponto de captura e a seta ao FONE (`b-tap`) ficam escondidos, e entram no toque em 0,2 s. Saiu do (i) "Um ponto de captura leva uma cópia ao quadro FONE." Na voz, a frase do ponto de captura virou "Embaixo, o quadro fone, com medidores e o desenho de um fone de ouvido." | (i), JS, roteiro
- quiz-21 | Saíram os botões do glossário de `ring out [ring-out]` e `RTA [rta]`. | (i)
- quiz-22 | Saiu o botão do glossário de `Automix [automix]`. | (i)
- quiz-23 | Saiu o botão do glossário de `cena [cena]`. | (i)
- quiz-24 | Saíram os botões do glossário de `USB [usb]` e `driver [driver-software]`. A alternativa A virou "Fazer um teste curto antes do início". Ela tem 35 caracteres, contra 31 da B e 43 da C, e não repete mais "gravação" nem "evento". O retorno (`fb`) continua igual. No (i), "fala de um teste de gravação" virou "fala de um teste". Na voz, a leitura da A virou "fazer um teste curto antes do início. Ela fala de um teste." | (i), slide, roteiro
- quiz-25 | Saiu o botão do glossário de `LAN [lan-wan]`. | (i)
- s22-1 (motion, rótulo errado de gravidade baixa) | O rótulo do LCD "ABERTOS" virou "ABERTO(S)", porque a contagem termina em 1. Foi só uma troca de texto. Pela conta de letras, ele cabe nos 124 px do visor. | slide
- Em todos os itens do glossário, o texto do (i) ficou igual, e o glossário geral não mudou.

## Roteiros mudados (`ws/audiolab-live-xl/vozes.txt`, 5)
quiz-4, quiz-7, quiz-10, quiz-20, quiz-24. Não gerei os áudios: eles precisam passar pela fila central de TTS e Whisper. O HTML não tem legenda nem transcrição da voz, então não havia texto de voz para trocar no `corrigir.py`.

## Não aplicado
- Nenhum item CORRIGIR ficou de fora.
- quiz-18, o botão opcional `bus [bus]`: não tirei. A definição ("Main, aux e subgrupo são buses") não dá a resposta nem descarta uma alternativa.
- MANTER ficou como estava: 12, 13, 17 e 26 (fronteira) e 3, 6, 15 e 16 (sem vazamento). As sugestões opcionais do 17 e do 26 também não foram aplicadas.
- Motion s3-2, s7-1 e s9-1 (camadas sobrepostas nos quadros de 0 e 300 ms): não apliquei. São defeitos de motion, e o quadro final está certo. O APLICAR.md manda não aplicar esse tipo.
- Título s25-1: é editorial e ficou como está.

## Pendente (central)
- Conferência visual, com fotos antes e depois do toque e também depois da tecla R, dos quizzes 1, 4, 9, 10, 18, 20 e 24 e do slide s22-1. No quiz-1, vale olhar as molduras neutras (classe `slot2`, tracejado escuro) contra o fundo do desenho.
- Checagem de sintaxe do JS. Não rodei node. Revisei as trocas no diff: todas são inserções numa chamada `P.gsap.set` ou numa linha nova de timeline, no mesmo formato do código em volta.
- Áudio das 5 vozes da lista.
