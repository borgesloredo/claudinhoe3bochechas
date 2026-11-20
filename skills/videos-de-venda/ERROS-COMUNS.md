# Erros comuns dos vídeos de venda (resolva no primeiro envio)

Lista do que já deu errado nos vídeos da XR18, WING e Axios 32 (07 a 09/11/2026), com a correção. **Todo agente lê isto antes de escrever roteiro, gerar voz, montar ou revisar.** Erro novo que custou retrabalho: acrescente uma linha aqui.

## 1. Voz e narração (o maior gasto de retrabalho)

### Corte entre falas ("trava e volta", 10/11/2026)
| Erro | Correção |
|---|---|
| A voz picotava sempre no mesmo ponto: o fim da palavra cortava e voltava depois da pausa (Matheus achou no 034 s18 e no 036 s33; 1 a 4 cortes ruins por vídeo nos 54 orgânicos). Causa: o take único da Gemini era cortado no meio do intervalo entre palavras do Whisper, que erra o tempo em décimos e não casa número escrito por extenso ("cem hertz" vs "100 Hz") | `gen_gemini.py` corta no trecho quieto mais longo (< -45 dB) a até 0,35 s do corte estimado (`refina`), com fade de 12/30 ms nas pontas, e marca CONFERIR se um corte ainda cair em som alto. Take salvo em `voz/qa/`: `gen_gemini.sh --recorta <pares>` refaz os cortes sem gastar pedido |

### Amostras de voz: poucas e diferentes de verdade
| Erro | Correção |
|---|---|
| 21 amostras para ouvir, 11 delas quase iguais (mesma voz, só semente/exaggeration/cfg diferentes). Matheus: "os 11 primeiros quase todos são iguais" | **No máximo 5 amostras por rodada**, cada uma de uma voz ou modelo diferente. Variação de semente/parâmetro nunca conta como opção nova |
| Gerar amostras de novo quando já existe voz aprovada | Voz aprovada (hoje: Gemini TTS `Puck`, estilo "reels2") é reutilizada direto. Só gere amostra se o Matheus pedir voz nova |
| Gerar a narração do vídeo antes de ele aprovar a voz | Amostra primeiro; narração só depois do "aprovado" |
| Oferecer modelo pago, ElevenLabs grátis em uso comercial, repositório de engenharia reversa ou clone de voz de pessoa real | Fora. Só voz grátis com uso comercial liberado |
| Modelos locais (VoxCPM2, Kokoro, Qwen3-TTS, Chatterbox) | Rejeitados ou 7/10. Não gere amostra deles de novo |

### Texto da fala: escreva já no jeito que a voz fala
A voz Gemini fala em registro de Reels (coloquial). O que vai no `.txt` tem que ser o que ela vai dizer, senão o Whisper acusa diferença e a fala é gerada de novo. O `gen_gemini.sh` recusa o texto com estes padrões **antes** de gastar o pedido:

| Escrito | Saiu | Escreva assim |
|---|---|---|
| "Está tudo no curso" | "Tá tudo" | "Tá tudo no curso" |
| "Aperte o play" (imperativo formal: Aperte, Toque, Gire, Ligue, Deslize, Salve) | "Aperta" | "Aperta o play", "Toca", "Gira" |
| "o i explica" (letra solta) | "o AI", "o IN", "o wing" | o nome da coisa: "o botão de informação explica". Na tela pode ficar "(i)" |
| "o envio ao main" (termo em inglês minúsculo: main, send, bus, mute, gain) | "man" | termo em português falado: "mix principal". Na tela fica a sigla da mesa (MAIN) |
| "o patch" (01V96, 09/11) | "o pet" ou "o PAD", também com a grafia "pétchi" no `PRON` (2 pedidos gastos) | "roteamento" na voz; PATCH fica na tela. O gerador já recusa "patch" antes do pedido |
| "da WING" | às vezes "Win" (aleatório) | não tem grafia melhor; o gerador confere e você refaz só essa fala |

- Outras regras de texto: frases curtas, máximo ~120 palavras no vídeo, ~3 palavras/s.
- Siglas que já saíram certas sem ajuste: Axios, quiz, WING, P.A., LO CUT, pré-fader, (i), PDF, SAVE, Behringer.

### Geração: 1 pedido por vídeo, conferido na hora
| Erro | Correção |
|---|---|
| Uma chamada por fala (estoura a cota grátis de 10 pedidos/dia) | `gen_gemini.sh voz/c01.txt voz/c01.m4a voz/c02.txt voz/c02.m4a ...` com **todas** as falas numa chamada |
| Erro de pronúncia só descoberto pelo revisor, dias depois | O gerador roda o Whisper e imprime `OK` ou `CONFERIR` por fala, e sai com código 2 se alguma diferir (lista em `voz/qa/conferencia.txt`). Resolva ali, antes de montar o vídeo |
| Refazer o vídeo inteiro para trocar uma fala | `touch` só nos `.txt` errados e rode o vídeo de novo: 1 pedido, só essas falas são trocadas |
| Gerar de novo a mesma frase pela 3ª vez | Na 2ª falha, reescreva a frase (sinônimo, outra ordem). Não insista |
| Acusação falsa de "Sena" (Cena), "Beringer" (Behringer), "Tá" (Está), "pra" (para), "32" (trinta e dois) | O gerador já trata como iguais (`EQUIV` em `tools/gen_gemini.py`). Não refaça por isso |
| Cota do dia acabou | O gerador troca sozinho entre as chaves `GEMINI*KEY*` do `.env`. Se todas acabarem, pare. Ela volta em ~20 h. Registre as falas pendentes no STATUS (`.txt` mais novo que `.m4a` = pendente) |

## 2. Roteiro e texto na tela
| Erro | Correção |
|---|---|
| Revisores contando palavras de jeitos diferentes (nota oscilando) | Regra "Como contar" do `REGRAS-BASE.md`: legenda, selo, CTA, mensagem de visor e rótulo inventado contam; serigrafia da mesa ≤ 30 px fora de foco e legenda de tecla (ON, M, MUTE) não contam |
| Rótulo inventado que repete a legenda ("CH 1 · VOZ" + legenda "Voz no canal 1") | Remova o rótulo |
| Na tela, a frase inteira da narração | Na tela só a frase-chave (≤ 9 palavras); o vídeo precisa funcionar com som desligado |
| "não é X, é Y" mais de uma vez; mesma ideia em duas cenas | No máximo 1 vez; corte a repetição |
| Palavra "oficial", logo de fabricante, preço, prazo, URL, @ | Proibidos (Mercado Livre e regra da marca). Selo: "Curso independente" |
| Feature "em produção" mostrada como pronta | Selo "em breve" ou fora |

## 3. Montagem e render
| Erro | Correção |
|---|---|
| Visual genérico ou copiado de outra mesa | Use o layout da própria mesa (CSS da LP `curso-<x>/lp/index.html`) |
| Tempos das cenas fixos e voz cortada | Meça cada fala com ffprobe e ajuste a cena à voz, nunca o contrário. Confira o corte no fim da última palavra |
| Dois agentes no mesmo `build.py` do scratchpad (um sobrescreve o outro) | Cada agente na sua subpasta |
| `pgrep -f "plugin-cli.mjs render"` acha o próprio shell e a fila trava | Use `pgrep -f "[p]lugin-cli.mjs render"` |
| Espera e render na mesma linha (`while pgrep -f "[p]lugin-cli.mjs render"; do sleep 10; done; node ... plugin-cli.mjs render ...`): o shell de espera tem o texto do render no próprio comando e acha a si mesmo (e aos shells de espera dos outros agentes); a fila nunca anda | Ponha a espera e o render num `.sh` e procure só o processo node: `pgrep -f "^node .*plugin-cli[.]mjs render"` |
| Dois renders ao mesmo tempo | Um por vez, com o máximo de workers |
| Sobrescrever MP4 aprovado | Copie para `renders/<id>-rN.mp4` antes |

## 4. Áudio final (medir antes de entregar)
| Erro | Correção |
|---|---|
| Fade-in "presente" no código mas inaudível (música com ataque forte) | Use `tools/mixar.py` (fade cúbico de 0,3 s). O `tools/checar.py` mede em janela de **20 ms** em 0,10 s, alvo ≤ −24 dB. O alvo antigo de −42 dB era inalcançável com fade de 0,3 s: os vídeos aprovados ficaram entre −34 e −58 |
| True peak −1,0 dBTP depois do fade (limite é ≤ −1) | Deixe margem: alvo −1,5 dBTP (`volume=-0.3dB` resolve) |
| Medir só LUFS, ou medir à mão em cada agente | `tools/checar.py` mede tudo de uma vez: LUFS, TP, fade-in/out, quadro parado, tela preta e texto proibido |
| Música por cima da voz | Música ~18 dB abaixo da voz, ducking leve; ganho calculado pela loudness da voz |

## 5. Processo
| Erro | Correção |
|---|---|
| Queda de rede (ENOTFOUND) mata todos os agentes | Retome cada um pelo SendMessage, não recomece |
| Ler o `.env` com `cat`/`sed` | Proibido. O gerador carrega só a linha `GEMINI_API_KEY` |
| Começar outra mesa sem pedido | Só as mesas pedidas |

## 6. Consumo de tokens (lote de 09/11: ~6,5 M por mesa, tudo em Opus)
| Erro | Correção |
|---|---|
| Todo agente lendo ~40 KB de skills do HyperFrames, dois caminhos nem existiam (`hyperframes-core`, `hyperframes-animation`) | Leia só `geral/videos-de-venda-compartilhado/HF-RESUMO.md` |
| Revisor abrindo ~90 quadros soltos por rodada | Folhas de contato do `checar.py` (12 quadros por imagem) + no máximo 6 quadros grandes |
| Cada vídeo escrevendo a própria mixagem (montar.py, mix.py) | `tools/mixar.py` |
| Revisor reprovando por contagem de palavras que o roteirista podia ter conferido | `tools/lint-roteiro.py` antes de entregar o roteiro |
| Opus em revisão, correção e cópia | Sonnet revisa e corrige, Haiku entrega (tabela no SKILL.md) |
| Ficha de 25 KB e mapa de 31 KB relidos por todos | Ficha ≤ 10 mil caracteres, mapa ≤ 6 mil |
| Comentários e contagens dentro de `texto_tela` ("(7) + selo (2) = 9") | `texto_tela` só com as palavras da tela; fala no campo `fala` |
| Cada build escrevendo o próprio gerador de HTML (build.py, montar.py, index.tpl) | `tools/montar.py`: o construtor escreve só `cenas/sNN.html/js` |
| Montagem abrindo ~14 imagens (snapshots e recortes) que ficam no contexto até o fim | Máximo 8; recortes pelo `kit/img/INDICE.md`; conferência pelas folhas do `checar.py` |
| Faixa do quadro vazia > 1,5 s (citada em ~34 de 44 revisões de vídeo) | Hardware ou produto em y 700–1500 em toda cena; `checar.py` avisa |
