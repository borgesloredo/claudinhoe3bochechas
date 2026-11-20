# Layout genérico dos vídeos orgânicos (mesa sem marca)

Um visual só para os 100 vídeos. Ele foi tirado do que funcionou nas referências: o diagrama limpo de canal da labtecheaudio (33,9 mil curtidas) e a manchete editorial com pílula de estado da doisroficial (14,4 mil). A mesa é **desenhada e sem marca**: não copia o painel de nenhum fabricante, então serve para qualquer mesa.

## Quadro (9:16, 1080 × 1920)
| Faixa | y | Conteúdo |
|---|---|---|
| Manchete | 120–420 | SOBRELINHA (caixa alta, espaçada, 28 px, ciano) + TÍTULO (bold, 72–88 px, branco), no máximo 6 palavras |
| Palco | 700–1500 | o componente da cena, ocupando ≥ 60% da largura, sempre centralizado |
| Legenda | 1520–1700 | caixa da LEGENDA (só a frase-chave, ≤ 9 palavras somando tudo da tela) |
| Zona coberta | 1670–1920 | nada importante (botões do app cobrem) |

## Cores e tipo
- Fundo: azul-noite `#0B1630` com grade fina `#14244A` (linhas a cada 40 px) e um brilho radial suave atrás do palco.
- Destaque: amarelo `#FFC83D` (o que estamos ensinando), ciano `#2FD3E6` (sinal, fader, medidor), verde `#3DDC84` (certo), vermelho `#FF4D4D` (erro, clip, microfonia), cinza `#8A98B8` (rótulos secundários).
- Fonte: Inter (títulos 800, texto 600). Texto que precisa ser lido: ≥ 36 px.
- Marca: o @ do perfil (`marca.json`) pequeno (28 px, 60% de opacidade) no topo da manchete, e o selo "Curso independente" só na cena do CTA.

## Componentes (use pelo nome no campo `visual`)
| Nome | O que é |
|---|---|
| **CANAL** | Faixa de canal vertical: knob GAIN, botão LOW CUT, 4 knobs de EQ (AGUDO, MÉDIO-AGUDO, MÉDIO-GRAVE, GRAVE), COMP, GATE, PAN, teclas SOLO e MUTE, fader e MEDIDOR ao lado. Rótulos genéricos em caixa alta |
| **MESA** | Visão de cima, simplificada: 8 CANAIS lado a lado + fader MAIN + uma TELA no topo. Serve para "onde fica" e para o "antes/depois" |
| **TELA** | Display genérico: curva de EQ, RTA em barras, lista de CENAS, roteamento em blocos ou medidores de envio |
| **KNOB** | Knob grande isolado com arco de valor colorido e rótulo (ex.: GAIN) |
| **FADER** | Fader grande isolado com escala (−∞ … 0 … +10) e capa |
| **MEDIDOR** | Coluna de LEDs: verde, amarelo e vermelho (CLIP no topo) |
| **SETA-RÓTULO** | Seta fina com rótulo em 2 linhas ("Ganho / na entrada"), como na referência |
| **PÍLULA** | Etiqueta arredondada de estado ("AGORA A VOZ SUMIU", "SÃO FUNÇÕES DIFERENTES"); vermelha = problema, verde = conserto |
| **CÍRCULOS** | Dois círculos que se sobrepõem (ex.: VOZ × TECLADO) para mascaramento e frequências que brigam |
| **PALCO** | Ícones em traço: microfone, pedestal, caixa de retorno, in-ear, caixa de P.A., instrumentos e plateia genérica (serve para culto, show ou evento; nada de símbolo religioso fixo) |
| **CAMINHO** | O sinal em blocos ligados por linha ciano: MIC → GAIN → LOW CUT → EQ → COMP → FADER → MAIN (ou → AUX) |
| **CHECKLIST** | Lista de 3 a 5 itens com caixa que vai sendo marcada (verde) |
| **QUIZ** | Pergunta com 2 ou 3 opções em cartões; a certa acende verde e faz "pop" |
| **PRODUTO** | Pilha estilizada de PDF + uma tela do autoestudo com o botão (i) aceso e um quiz, **sem nome de mesa legível**. Em volta, uma grade de 20 mini-capas em contorno, sem texto |
| **LEGENDA** | Caixa arredondada `#0F1E40` com borda `#2A3D6B`. A palavra falada acende em branco e o resto fica em cinza (karaokê) |

## Movimento
- Um conceito por vídeo: o componente principal fica no palco o vídeo todo e muda de estado (knob gira, medidor sobe, PÍLULA troca de vermelho para verde).
- Micro-movimento a cada ≤ 1,2 s (medidor vivo, LED piscando, push ≤ 1,08).
- Elementos entram com máscara de baixo para cima (0,3 s) e saem 0,12 s antes do corte.
- Erro: tremidinha (shake) + vermelho. Conserto: verde + "pop" leve.
- Ritmo: cena de 1,5 a 4 s, sincronizada com a narração.

## Proibido no layout
Logo, nome ou layout reconhecível de fabricante. Nome de modelo. Foto de mesa real. Capa de curso com nome de mesa legível. URL, @, preço.
