# Regras do agente (vídeos de venda das mesas) — versão curta

Junta `REGRAS-BASE.md` e `~/.claude/skills/videos-de-venda/ERROS-COMUNS.md` (as versões longas). Leia só a sua seção + "Todos". `<G>` = a pasta do projeto (tools/, musica/).

## Todos
- Fatos só de `<BASE>/ficha-produto.md`. Nada de preço, cupom, prazo, garantia, depoimento, nº de alunos inventado.
- Proibido no vídeo: "oficial"/"não oficial"/"manual oficial", URL, @, telefone, logo de fabricante. Selo "Curso independente"; marca do perfil (marca.json); CTA "Garanta o seu". Feature "em produção" leva "em breve" ou sai.
- 9:16 1080x1920, 30–60 s. Visual = layout do hardware DA MESA (kit da LP dela). Nada genérico, nada copiado de outra mesa.
- Nunca leia/imprima `.env`. Temporários na sua subpasta. Nunca apague: backup antes de sobrescrever (`renders/<id>-rN.mp4`).
- Navegador: se `echo $CODEX_SANDBOX` = seatbelt, não lance navegador.
- Estilo de trabalho: sem texto entre ferramentas; arquivo grande só com grep/head/sed -n; não releia o que já leu; resposta final só o pedido.

## Roteirista / revisor de roteiro
- Tela: ≤ 9 palavras. Contam: legenda, selo, marca, CTA, visor/LCD/tela, rótulo inventado. Não contam: serigrafia da mesa ≤ 30 px fora de foco; legenda gravada na tecla (ON, M, MUTE, 16/24/32).
- Rótulo inventado que repete legenda/visor: remova. Na tela só a frase-chave (vídeo funciona mudo).
- "não é X, é Y" no máximo 1 vez. Mesma ideia em 2 cenas: corte.
- Hook ≤ 3 s; cenas 1,5–4 s; payoff e CTA ≥ 1,2 s; quadro de 2 s serve de capa.
- `texto_tela` = só as palavras exatas da tela, elementos separados por " | " (sem comentário nem contagem). Narração vai em `fala`; notas em `visual`/`motion`.
- Narrado (consultivo, demonstracao): ≤ 120 palavras, ~3 palavras/s. Registro falado (é o que a voz diz): "Tá" (não "Está"), "Aperta/Toca/Gira" (não "Aperte"), sem letra solta ("o i" → "o botão de informação"), sem inglês minúsculo (main → "mix principal"; na tela fica MAIN).
- Parta do molde da sua abordagem em `<G>/MOLDES-ROTEIRO.md` (batidas e tempos aprovados; seção "Em todas" obrigatória).
- Em `visual`, diga o que ocupa o meio do quadro (y 700–1500) em cada cena: hardware da mesa ou produto real. Cena sem isso vira "faixa vazia", o defeito nº 1 dos revisores.
- Rode `python3 <G>/tools/lint-roteiro.py <arquivo> [--narrado]` até zero FALHA antes de entregar.

## Construtor / corretor (build, fix)
- Leia `<G>/HF-RESUMO.md` (não as skills do plugin). Kit da mesa em `<BASE>/kit/` (LEIAME primeiro; `componentes.html` e `tema.css` só os trechos que usar).
- Música: só `<G>/musica/calma.m4a` e `energica.m4a`. Mixagem: só `<G>/tools/mixar.py`.
- Voz (narrados): Gemini Puck aprovada, sem amostra. `<G>/voz/gen_gemini.sh voz/c01.txt voz/c01.m4a voz/c02.txt voz/c02.m4a ...` com TODAS as falas numa chamada. Ele recusa texto de risco e confere no Whisper (OK/CONFERIR). CONFERIR: `touch` só nos `.txt` citados e rode de novo; na 2ª falha reescreva a frase. Falso positivo já tratado: Sena/Cena, Beringer, Tá/Está, pra/para, números. "cota do dia acabou": não contorne; grave `<BASE>/<id>/PENDENTE-VOZ.md` com o comando e retorne isso.
- Tempos da cena seguem a voz (ffprobe), nunca o contrário. O `tools/montar.py --voz` já faz isso.
- Montagem: NÃO escreva gerador próprio (build.py, montar.py, index.tpl). Escreva só `cenas/sNN.html` + `cenas/sNN.js`, `fixo.*` e `estilo.css`, e rode `python3 <G>/tools/montar.py . --musica <calma|energica> [--voz]` (gera index.html, tempos, mix e ROTEIRO-FINAL.md). Ajudantes GSAP prontos em `V` (`tools/vv.js`: words, mask, entra, out, capOut, press, lit, flick, blink, fader, meter, breathe, count, push, zoom, camSet, shake, tap, rng).
- Imagens no contexto custam caro: no máximo 8 Read de imagem no build inteiro. Escolha recortes pelo `kit/img/INDICE.md` (sem abrir cada um) e confira o vídeo pelas folhas do `checar.py`, não por snapshot de cada cena.
- Defeitos que mais reprovaram (evite já na 1ª versão):
  1. Faixa do quadro vazia > 1,5 s: em toda cena, hardware ou produto ocupa y 700–1500 (escala ≥ 1,15); legenda no terço superior. O `checar.py` avisa "faixa vazia".
  2. Corte na borda: push/zoom ≤ 1,08, conteúdo em foco com ≥ 40 px de margem, transform-origin no centro do foco.
  3. Produto pequeno, borrado ou coberto: capa real ≥ 900 px de largura, tela real do autoestudo, nítidas ≥ 1,9 s; texto da imagem ≤ 30 px ou blur ≤ 4 px; nunca barra opaca nem mancha.
  4. Cena genérica: toda cena (inclusive payoff e CTA) tem 1 peça do kit da mesa ocupando ≥ 40% da largura.
  5. Legenda e imagem fora de sincronia: o elemento acende/entra até 0,1 s da palavra que o nomeia; LED e visor coerentes com a legenda (nada de S, M e SEL acesos juntos sem motivo).
  6. Quadro parado: micro-movimento a cada ≤ 1,2 s (medidor, LED, push ≥ 3%), inclusive no CTA.
  7. Texto: soma ≤ 9 palavras por tela; texto que não é serigrafia fica ≥ 36 px em foco ou opacidade ≤ 0,3 com blur ≥ 4 px.
  8. Corte: textos saem (0,12 s) antes da troca; o quadro novo entra no mesmo quadro (1/30 s) em que o antigo sai; fundo com inset:-6% sob push.
  9. CTA: nome curto da mesa ≥ 48 px, "Garanta o seu" ≥ 96 px, marca acima de y 1450.
- Antes de entregar: `python3 <G>/tools/checar.py renders/<id>.mp4 --html index.html --folhas rev-r<N>/folhas` com zero FALHA; olhe as folhas.

## Revisor de vídeo
- Rode `checar.py` (acima) e use o relatório; não meça à mão. Olhe as folhas de contato (folha k, linha r, coluna c = 12k+4r+c+0,5 s). Abra quadro grande (ffmpeg -ss T -frames:v 1) só onde suspeitar, no máximo 6.
- Nota 0–10 em legibilidade, motion, ritmo, conformidade, storytelling; nota = média; conformidade < 9 limita a nota a 6. FALHA no checar = conformidade < 9.
- Liste só o que muda a percepção do comprador, com tempo e correção concreta. Não reprove por gosto pessoal.
