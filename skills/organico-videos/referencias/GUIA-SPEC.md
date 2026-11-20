# Guia do spec.json — peças de cena dos vídeos orgânicos

Cada vídeo fica em `videos/NNN/`. O `roteiro.json` traz as cenas (`texto_tela`, `fala`, `visual`, `motion`). O `spec.json` diz o que desenhar em cada cena:

```json
{"tema": "c", "cenas": [
  {"c": [{"t": "knob", "pos": "e", "label": "GAIN", "v0": 0.2, "v1": 0.6}, {"t": "fader", "pos": "d", "label": "FADER", "v0": 0.3, "v1": 0.8}], "pill": ["VOZ BAIXA", "r"]},
  {"c": [{"t": "produto"}]},
  {"c": [{"t": "cta"}]}
]}
```

Uma entrada em `cenas` por cena do roteiro, na mesma ordem. `c` = lista de peças. `pill` (opcional) = `["TEXTO", "r"|"g"|"a"]` (vermelha = erro, verde = acerto, laranja/amarela = neutra).

## Como o quadro funciona

- Quadro 1080×1920. O título da cena (`texto_tela`) é desenhado sozinho no alto (y 250–470). Não repita o título em outra peça.
- Palco das peças: y 600 a 1500. Pílula: y 1580.
- `x` cresce para a direita, `y` cresce para baixo. Valores de knob, fader e medidor vão de 0 a 1 (fader 1 = no topo).

## Regras

1. Leia o `visual` (o que a cena deve mostrar) e a `fala` (o que o narrador diz) e escolha a peça que mostra **aquela ideia**. O `visual` usa um vocabulário: CANAL, MESA, TELA, KNOB, FADER, MEDIDOR, CÍRCULOS, QUIZ, CHECKLIST, CAMINHO, PALCO, PÍLULA, SETA-RÓTULO, PRODUTO. Use a tabela "Do roteiro para a peça" abaixo.
2. Por cena: **uma peça grande**, ou **uma peça de lado no centro**, ou **duas peças de lado** (`"pos": "e"` e `"pos": "d"`). `passos`, `seta`, `laco` e `balao` podem ir por cima.
3. **No máximo 9 palavras na tela** por cena: título + pílula + rótulos grandes (nomes de `tecla`, `label` de knob/fader, opções do `quiz`, `balao`, tipo do `cabo`, rótulos de `circulos`). O validador conta e avisa. Se passar, tire a pílula ou troque a peça; não mexa no `roteiro.json`.
4. Pílula só quando o `visual` pede uma PÍLULA e ela cabe nas 9 palavras. Copie o texto do roteiro, em maiúsculas.
5. Mostre **o que muda** na cena: prefira parâmetros que animam (`v0`→`v1`, `seq`, `acende`, `sobe`/`desce`, `on1`, `curvas` com 2 ou mais estados, `estados`, `marcados`). Na mesma peça em cenas seguidas, mude o destaque (qual tecla acende, qual fader sobe, qual canal fica em destaque).
6. Última cena: `[{"t": "cta"}]`. Cena cujo `visual` começa com PRODUTO: `[{"t": "produto"}]`.
7. Nunca escreva marca ou modelo de mesa, URL, @ ou preço.
8. Mantenha o `"tema"` que já está no `spec.json` e apague a chave `"auto"`.
9. Se o roteiro pedir um desenho que o kit não tem, use a peça mais próxima da ideia e anote no seu relatório.

## Validar (obrigatório)

```bash
cd "<pasta do projeto>" && python3 kit/validar_spec.py 011 012
```

Corrija até cada vídeo dar `OK (spec.ok gravado)`. Depois do OK, não edite mais aquele vídeo (o lote começa a renderizar na hora).

## Peças grandes (uma por cena)

| Peça | Parâmetros |
|---|---|
| `canal` | Faixa de canal com 48V, MUTE, GAIN, 2 teclas, 4 knobs de EQ, fader e medidor. `gain`, `gain1` (gira até), `fader`, `fader1`, `meter:[lo,hi]`, `meter1:[lo,hi]`, `clip`, `lowcut` (1ª tecla acesa), `lowcut1` (acende na cena), `eq` (2ª tecla, padrão acesa), `blink_eq`, `mute`, `mute1` (true acende, false apaga), `p48`, `p48_1`, `botoes:["LOW CUT","EQ"]` (renomeia as 2 teclas: `["COMP","EQ"]`, `["GATE","EQ"]`, `["FX","EQ"]`...), `knobs:{"AGUDO":[v0,v1],"MÉDIO AG.":[..],"MÉDIO GR.":[..],"GRAVE":[..]}`, `hl:[...]` destaque piscando entre `gain`, `fader`, `lowcut`, `eq`, `mute`, `48v`, `eqknobs`, `meter`, `agudo`, `grave`, `checks` (3 ✓ ao redor), `at` (momento da ação, 0–1). Não combina com `passos`. O rótulo GAIN conta 1 palavra. |
| `mesa` | Mesa de 8 canais (0 VOZ, 1 VOZ 2, 2 VIOLÃO, 3 TEC, 4 BAIXO, 5 BUMBO, 6 CAIXA, 7 GTR). `teclas:"SOLO"` (fileira de teclas com esse nome, até 4 letras: SOLO, MUTE, HPF, 48V, AUX, PAN, DCA, FX, REC), `on:[i]` acesas, `on1:[i]` acendem na cena, `off1:[i]` apagam, `sobe:[i]` / `desce:[i]` faders se movem, `knobs:{"3":[0.5,0.1]}` knob do canal gira, `apagados:[i]` canais esmaecidos, `vermelho:[i]` medidor estourando, `hls:[i]` moldura de destaque, `nomes:[8 nomes de até 6 letras]`, `at`. Nada dela conta palavra. |
| `tela` | Tela de EQ. `curvas:[[termos],[termos],...]` (anima de um estado ao outro; `[]` = reta), termos `["hp",fc]`, `["bell",f0,dB,largura_em_oitavas]`, `["lshelf",fc,dB]`, `["hshelf",fc,dB]`; `faixa:[f1,f2]` com `faixa_txt:"2–4 kHz"` (conta palavras; `""` omite o texto); `cor` e `cor1` (cor final) entre `c`, `g`, `r`, `a`; `at`, `fim`. |
| `barras` | Analisador de espectro. `alturas:[10 valores de 60 a 460]`, `pico:i` (barra vermelha), `manta:true` (grave cobrindo o agudo), `sem_rotulo:true` (sem "GRAVE"/"AGUDO", que contam 2 palavras). |
| `caminho` | Blocos ligados por um trilho com uma bolinha andando. `blocos:[2 a 5 nomes de até 8 letras]`, `hl:i`, `cor`, `reverso`. Some `{"t":"laco"}` para o laço vermelho de realimentação. Não conta palavra. |
| `quiz` | Cartões de resposta. `ops:[2 ou 3 opções de até 3 palavras]`, `certa:i`, `revela:true` (acende a certa). As opções contam palavras. |
| `circulos` | Dois círculos (mascaramento, espaço). `estados:[[x1,r1,x2,r2],...]`; sobrepostos `[[440,190,650,220]]`, separados `[[350,170,730,200]]`; `a:"VOZ"`, `b:"TECLADO"` (contam 2 palavras), `cor_b`, `sobre_amarelo`, `verde`. |
| `ecos` | Repetições do delay na grade do tempo. `estados:[{"n":1-8,"dec":0.5-0.97,"fora":bool},...]`, `vermelho`. Conta 1 palavra ("TEMPO"). |
| `tecla` | Teclas grandes. `labels:[1 a 4 nomes]` (contam palavras), `acesas:[i]`, `acende:[i]`, `apaga:[i]`, `cor`. Boa para SOLO, MUTE, AUX 1, MAIN, DCA, CENA, TALKBACK, REC. |
| `pa` | Caixas de P.A. `n:1|2`, `ondas:[0|1|2 por caixa]` (0 muda, 2 forte), `cor`. |
| `lista` | Cartão de checklist. `itens:[até 4 itens de 1 a 3 palavras]`, `marcados:k`, `riscados:[i]`. Não conta palavra. |
| `bolo` | Bolo em camadas. `camadas:4`, `acesas:k`, `acende:j`. |
| `cabo` | Cabo com conectores. `tipo:"xlr"|"p10"` (conta 1 palavra), `y`, `cor`, `ruido`. Dois cabos na cena: `y` 900 e 1200. |
| `sala` | Plateia numa sala com ondas (`paredes:true` = eco nas paredes). |
| `bateria` | Bateria com microfone no tom. `vazamento`, `some:0.3` (vazamento some), `tocando`. |
| `fones` | In-ear e fone de ouvido. |
| `cauda` | Palavra + pré-delay + cauda do reverb (conta 2 palavras). |
| `produto` / `cta` | Sem parâmetros. |

## Peças de lado (`"pos": "c"` sozinha, ou `"e"` + `"d"` em par)

| Peça | Parâmetros |
|---|---|
| `knob` | `label` (conta palavra), `v0`, `v1`, `seq:[v,...]`, `cor`. PAN: 0.5 é o centro. |
| `fader` | `label` (conta), `v0`, `v1`, `seq`. |
| `meter` | Medidor. `lo`, `hi` (oscila entre), `lo1`, `hi1` (muda na cena), `clip`, `seq`, `label` (conta), `limiar:v` (linha, conta 1 palavra). |
| `gr` | Redução do compressor. `db0`, `seq:[dB,...]` (conta 1 palavra). |
| `mic` | `tipo:"dinamico"|"condensador"|"fita"`, `ondas:false`, `cardioide:true` (só no centro, sem `passos`). |
| `caixa` | Uma caixa ou sub. `label:"SUB"` ou `""`, `apagada`. |
| `retorno` | Monitor de chão. `apito:true` (ondas vermelhas), `mudo`. |
| `porta` | Porta do gate. `abre:[0 a 1, ...]`. |
| `aparelho` | `tipo:"tablet"|"notebook"|"celular"`, `wifi:0-3`. |
| `roteador` | `barras:0-4`. |
| `pessoa` | `tipo:"tecnico"|"cantor"|"musico"`, `anda:[x0,x1]`. No máximo 2 por cena. |
| `icone` | `nome:"cadeado"|"pendrive"|"ouvido"|"relogio"|"alerta"|"ok"|"x"`, `cor`, `escala` (use 0.7 em par). |

## Peças livres (vão por cima)

| Peça | Parâmetros |
|---|---|
| `passos` | Bolinhas numeradas no alto, para dica numerada ou CHECKLIST. `n:3-5`, `atual:i` (começa em 0). Não cabe com `canal`. |
| `balao` | Balão de fala. `texto` (conta), `x`, `y`. Com boneco: `{"t":"pessoa","tipo":"cantor","x":420,"y":1200}` + `{"t":"balao","texto":"Tô sem retorno!","x":560,"y":800}`. |
| `seta` | Rótulo com linha. `x`, `y`, `texto` (conta), `tx`, `ty`. Use pouco; ponha em área livre do palco. |
| `laco` | Laço vermelho, junto com `caminho`. |
| `onda` | Onda na base. `achatada:true` (distorção). Só com peça curta em cima. |
| `ruido` | Chiado. `x`, `y` (conta 1 palavra). |

Peça com `x`/`y` explícitos não entra na regra de `pos`.

## Do roteiro para a peça

| O `visual` fala em | Use |
|---|---|
| CANAL (uma faixa, GAIN, LOW CUT, EQ, MUTE, 48V) | `canal` com o `hl` e a ação certos |
| MESA, CANAIS, faders juntos, SOLO, MUTE, AUX, DCA, PAN por canal | `mesa` com `teclas`, `on1`, `sobe`, `knobs`, `hls`, `apagados` |
| uma tecla ou poucas teclas em destaque (SOLO, AUX, MAIN, CENA, TALKBACK) | `tecla` |
| TELA com curva de EQ, filtro, faixa de frequência | `tela` |
| RTA, analisador, frequência que apita | `barras` com `pico` |
| KNOB(s) | `knob` (até 2 em par) |
| FADER e MEDIDOR | `fader` + `meter` em par |
| CAMINHO, roteamento, envio | `caminho` |
| CHECKLIST com itens escritos | `lista`; dica numerada | `passos` + a peça da dica |
| QUIZ | `quiz` |
| CÍRCULOS | `circulos` |
| PALCO com microfone | `mic`; com caixa de retorno | `mic` (e) + `retorno` (d); caixas de P.A. | `pa`; plateia | `sala`; bateria | `bateria` |
| tablet, celular, notebook, wi-fi | `aparelho`, `roteador` |
| técnico, músico, cantor | `pessoa` (+ `balao` se ele fala) |
| cabo XLR / P10, ruído | `cabo` |
| cadeado, pendrive, ouvido, relógio, alerta | `icone` |
| bolo em camadas | `bolo` |
| compressor | `gr`, `meter` com `limiar`, `knob` |
| gate | `porta`, `meter` com `limiar` |
| reverb / delay | `cauda`, `ecos`, `caminho` |

## Exemplos prontos

Veja `videos/001/spec.json` (ganho × volume), `videos/006/spec.json` (checklist com `passos` + `mesa`) e `videos/008/spec.json` (gate), cada um ao lado do seu `roteiro.json`. Eles usam coordenadas à mão; nos novos, prefira `pos`.
