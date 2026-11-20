---
name: organico-videos
description: Use quando o usuário pedir vídeos orgânicos para Reels, TikTok, Kwai ou YouTube Shorts que ensinam um conceito do nicho e trazem seguidor e lead — "vídeos para o Instagram", "conteúdo orgânico", "100 roteiros", "vídeo educativo narrado", "dica rápida", "Reel com diagrama", em lote ou um por um. Vídeos narrados (voz Gemini), com diagrama animado desenhado em código, legenda para cada rede e CTA orgânico (comenta, salva, marca, segue). Dispare mesmo que a pessoa não diga "skill" nem "HyperFrames".
---

# Vídeos orgânicos narrados (em lote)

## O que esta skill faz
Produz vídeos verticais de 30 a 60 s para Reels, TikTok, Kwai e Shorts: um conceito por vídeo, gancho em 3 s, diagrama animado no meio do quadro (peças desenhadas em código: canal, knob, fader, medidor, tela de EQ, quiz, checklist, caminho do sinal e outras), legenda grande, voz narrada Gemini Puck, música e CTA orgânico. Sai também um `.txt` por vídeo com título, legenda e hashtags certos para cada rede.

É o processo que gerou 200 vídeos orgânicos publicados. O kit foi feito para o nicho de áudio ao vivo: as peças desenham mesa de som. Outro nicho usa as peças genéricas (quiz, checklist, círculos, caminho, ícones, pessoa, aparelho) ou pede peças novas no `kit/gerar_cenas.py`.

| Arquivo | O que tem |
|---|---|
| `referencias/GUIA-ROTEIRO.md` | **Como escrever cada roteiro**: o padrão que funciona, conteúdo genérico, regras de voz e de tela, CTA, formato do JSON, lint |
| `referencias/INSIGHTS-INSTAGRAM.md` | O que funciona nos Reels (gancho duplo, gancho negativo, aberturas variadas, confiança) |
| `referencias/GUIA-SPEC.md` | Como escrever o `spec.json` (que peça desenhar em cada cena) e a lista de peças com parâmetros |
| `referencias/DESIGN-GENERICO.md` | O layout: quadro, cores, tipografia, onde fica cada coisa |
| `referencias/ERROS-COMUNS.md`, `REGRAS-AGENTE.md` | Erros de voz, roteiro e montagem que custaram retrabalho |
| `kit/` | `gerar_cenas.py` (desenha), `auto_spec.py` (rascunho do spec), `validar_spec.py`, `lote.py` (voz, cenas, render e conferência em lote), `posts.py` (textos por rede), `voz/gen_gemini.py` |
| `tools/` | `montar.py`, `mixar.py`, `checar.py`, `lint-roteiro.py`, `vv.js` |
| `exemplos/` | 2 roteiros com o spec de cada um (um com ponte para o produto, um só informativo) |
| `scripts/criar-projeto.sh` | Monta a pasta do projeto, instala ffmpeg e Whisper, baixa 2 músicas |

Caminho da skill: `K=~/.claude/skills/organico-videos`.

## Passo 1: Conversa inicial (uma rodada só)
Pergunte numa chamada de AskUserQuestion, com o padrão como 1ª opção "(Recomendado)". Pule o que o pedido já respondeu.
| Campo | Padrão |
|---|---|
| quantos vídeos | 5 pilotos primeiro; o lote grande só depois que ele aprovar o padrão |
| objetivo | metade ensina e cita o produto na ponte; metade só informativo |
| perfil | o nome do perfil (sem @: o @ na tela reprova no lint) que aparece no topo e no selo final |
| público e dores | do material do produto, ou da pesquisa do público se houver |

Depois resolva a chave do Gemini (passo 2), no mesmo começo de conversa.

## Passo 2: Chave do Gemini (a voz)
Pule se existir `~/.config/organico-videos/gemini.env` (ou o de outra skill do pacote: `organico-personagem`, `curso-mesa-de-som`), ou variáveis `GEMINI*KEY*` no ambiente. Senão, guie em texto simples, um passo por vez:
1. "Abra https://aistudio.google.com/apikey e entre com uma conta Google. É grátis e não pede cartão."
2. "Clique em **Create API key** (Criar chave de API), aceite os termos se aparecerem e copie a chave. Ela começa com `AIza`."
3. "**Não cole a chave aqui no chat.** Abra o app Terminal do Mac, cole o comando abaixo, tecle Enter e, quando ele pedir, cole a chave e tecle Enter de novo. A chave não aparece na tela, é normal." Mande o comando num bloco de código:
   ```bash
   mkdir -p ~/.config/organico-videos && printf 'Cole a chave do Gemini e tecle Enter: ' && read -rs k && printf 'GEMINI_API_KEY=%s\n' "$k" > ~/.config/organico-videos/gemini.env && chmod 600 ~/.config/organico-videos/gemini.env && echo && echo salvo
   ```
4. Quando ele disser `salvo`, confira sem gastar cota e sem mostrar a chave:
   ```bash
   ( set -a; . ~/.config/organico-videos/gemini.env; curl -s -o /dev/null -w '%{http_code}\n' -H "x-goog-api-key: $GEMINI_API_KEY" https://generativelanguage.googleapis.com/v1beta/models )
   ```
   `200` é chave certa. `400` ou `403`: repita os passos 2 e 3.
5. Cota em uma linha: o plano grátis dá ~10 pedidos de voz por dia por chave e cada vídeo gasta 1 (mais 1 por correção). Para lote grande, mais chaves (cada uma em outra conta Google ou projeto) entram no mesmo arquivo como `GEMINI_API_KEY_2=...` (mesmo comando, trocando o nome e `>` por `>>`). O lote espera a cota voltar sozinho com `--espera`.
Nunca peça, mostre nem copie o valor da chave para o chat ou para arquivos do projeto.

## Passo 3: Criar o projeto
```bash
"$K/scripts/criar-projeto.sh" "<pasta do projeto>"      # P = caminho absoluto
```
Depois edite `$P/marca.json`: `marca` (texto pequeno no topo de todo vídeo), `selo` (embaixo do CTA nos vídeos informativos) e `selo_produto` (nos que citam o produto). Exige Mac com chip Apple e Node.js. Música própria: `musica/<nome>.m4a` e `"musica": "<nome>"` no roteiro.

## Passo 4: Briefing
Escreva `$P/BRIEFING.md` curto: quem é o público (uma persona com nome, o que faz, a frase dela, a transformação que ela quer), as 20 a 30 dores dela numeradas, os fatos do produto (só o que está no material: nada de número inventado), o que é proibido citar, e 3 ou 4 Reels de referência do nicho com o que copiar do formato (nunca o texto). Para um lote, monte antes um plano: uma linha por vídeo com dor, abordagem, conceito e tipo de CTA, variando abordagem e CTA (proporções no `GUIA-ROTEIRO.md`).

## Passo 5: Roteiros
Siga **`referencias/GUIA-ROTEIRO.md` à risca**. Um arquivo por vídeo em `$P/json/NNN-slug.json` (NNN = 001, 002...). Rode o lint em cada um até zero FALHA:
```bash
cd "$P" && python3 tools/lint-roteiro.py json/NNN-slug.json --narrado --cta "comenta|salva|marca|segue"
```
Em lote grande, divida os roteiros entre agentes (até 8 em paralelo), cada um com o guia, o briefing e a sua faixa de números; um revisor confere amostras contra o guia.

## Passo 6: Spec (o desenho de cada cena)
Para cada vídeo:
```bash
cd "$P" && mkdir -p videos/NNN && cp json/NNN-*.json videos/NNN/roteiro.json && python3 kit/auto_spec.py videos/NNN c
```
O `auto_spec.py` faz só um rascunho (a letra no fim é o tema de cores: `a`, `b`, `c` até `t`; varie por bloco de 5). **Reescreva o `videos/NNN/spec.json` à mão** seguindo `referencias/GUIA-SPEC.md` (uma peça grande por cena, mostrar o que muda, até 9 palavras na tela, última cena `cta`), apague a chave `"auto"` e valide:
```bash
cd "$P" && python3 kit/validar_spec.py NNN [NNN ...]
```
Corrija até sair `OK (spec.ok gravado)`. Depois do OK não mexa mais no vídeo (o lote começa a renderizar na hora). Exemplos de spec bom em `exemplos/`.

## Passo 7: Produzir em lote
```bash
cd "$P" && python3 kit/lote.py 1 5 --espera
```
Rode em segundo plano. Para cada vídeo com `spec.ok`: voz (1 pedido por vídeo, numa fila só, por causa da cota), cenas, montagem com música, check, render (até 3 ao mesmo tempo; `LOTE_RENDERS=1` se o Mac estiver ocupado) e conferência objetiva. O andamento fica em `videos/LOTE-STATUS.md`. Saída: `videos/NNN/renders/NNN.mp4`, folhas de contato em `videos/NNN/rev-r1/folhas/` e `checar.log`.
- O render abre um navegador sem janela. Se `CODEX_SANDBOX=seatbelt` (Codex no macOS), não rode aqui: prepare o comando para o app Terminal.
- `voz ok (N a conferir)`: ouça os trechos listados em `videos/NNN/voz/qa/geracao.log`. Para refazer uma fala, edite `voz/cNN.txt`, apague `voz/cNN.m4a` e rode o lote de novo.
- Vídeo com `FALHA` em `LOTE-STATUS.md`: leia o motivo, corrija e rode de novo; o que já está pronto é pulado.

## Passo 8: Conferir e entregar
1. Olhe as folhas de contato de cada vídeo com Read: cena vazia, texto cortado, peça em cima da legenda, CTA que some antes de 3 s.
2. Textos por rede: `cd "$P" && python3 kit/posts.py` grava `videos/<id>.txt` (título, legenda e hashtags para Instagram, TikTok, Kwai e YouTube Shorts). Só o Instagram promete mandar algo no direct; nas outras redes o CTA sai sem essa promessa.
3. Responda com uma tabela (vídeo | conceito | CTA | duração), os caminhos dos MP4 e dos `.txt` e o que depende do usuário: resposta automática no direct para os "Comenta PALAVRA", capa no upload, licença da música própria.
4. **Nunca publique sem o usuário pedir.**

## Erros comuns
| Erro | Correção |
|---|---|
| Vídeo que cita marca, modelo ou um só cenário | Genérico sempre; o lead se qualifica pelo CTA "Comenta o modelo..." |
| Spec automático fraco (cena que não mostra a ideia) | O `auto_spec` é rascunho; todo spec é revisto à mão pelo `GUIA-SPEC.md` |
| Mais de 9 palavras na tela | O validador avisa; tire a pílula ou troque a peça, não o roteiro |
| Voz engole a 1ª palavra ("Comenta") | Pergunta antes do CTA ("Quer o resumo? Comenta...") |
| Voz corta no meio da palavra e volta | Já corrigido no `gen_gemini.py`; se aparecer, refaça só aquela fala |
| "Comenta PALAVRA" sem resposta automática no direct | Monte o auto-DM antes de postar, ou troque o CTA por salva/marca/segue |
| Lote grande sem aprovar o padrão | 5 pilotos primeiro; o resto só depois do "aprovado" |
| Gastar cota com texto arriscado | O gerador recusa antes do pedido; reescreva a frase apontada |
