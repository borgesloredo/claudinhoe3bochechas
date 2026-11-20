# Voz da V2 (áudio ▶ dos slides): Gemini TTS, voz Puck

**Desde 14/11/2026 a V2 usa a MESMA voz dos vídeos de venda** (pedido do Matheus): Gemini TTS `gemini-3.8-flash-tts`, voz `Puck`, estilo "reels2". Ele aprovou essa voz em 09/11 (`geral/videos-de-venda-compartilhado/voz/amostras-v2/M-12-gemini-puck.m4a`); o tutorial completo está em `geral/videos-de-venda-compartilhado/voz/ESCOLHA.md`. O Kokoro `pm_alex` anterior ficou em `kokoro/` só como histórico; o dono considera essa voz "OK só para ebook".

## Uso
```bash
cd tools/v2
./heavy.sh tts/gen.sh script/ ../../08-slides-v2/audio/   # pasta: só os .txt sem .m4a em dia; retoma sozinho
./heavy.sh tts/gen.sh script/s3-1-2.txt ../../08-slides-v2/audio/s3-1-2.m4a   # um arquivo = 1 pedido
tts/gen.sh --lint script/    # checagem de risco, sem pedido e sem chave: rode ANTES de gerar
tts/gen.sh --teste           # autoteste + quantas chaves chegaram (deve dizer 5)
```
- **Chaves:** as 5 `GEMINI_API_KEY_*` do cofre (uma por conta Google), injetadas pelo script `cofre` da raiz do seu projeto. Nunca do `.env`.
- **Cota:** plano grátis, 10 pedidos por dia por chave, ~50 por dia com as 5 (cada chave é de uma conta Google). No 429, o motor passa para a próxima chave. Se todas acabarem, o script para com `COTA DO DIA ESGOTADA` e diz quantos roteiros faltam; rode o mesmo comando no dia seguinte (~20 h depois).
- **Lote:** `TTS_LOTE=5` roteiros por pedido (padrão desde 17/11; antes 3), com teto de `TTS_MAX_PALAVRAS=1900`. Um curso de ~150 telas usa ~30 pedidos, ou seja, cabe num dia. Teste de 14/11: 3 roteiros (771 palavras) num pedido deram 79 + 81 + 76 s de áudio, em 72 s de relógio, a −16,1 LUFS.
- **Corte e conferência:** o take volta inteiro e é cortado por roteiro pelo alinhamento de palavras do Whisper (`v2_wts.py`). Cada roteiro é conferido contra o que o Whisper ouviu. A conferência do curso é **tolerante**: marca só trecho de 3+ palavras faltando, sobrando ou trocado, ou semelhança < 96%. Homófono de uma palavra ("nesta"→"nessa", "seção"→"sessão") não conta. Os que precisam de escuta vão para `tools/v2/qa-out/gemini-conferir.txt`; o take desse lote fica em `tts/saida/<id>/qa/` (fora da entrega).
- **Alinhamento falhou** num lote: o script refaz aqueles roteiros um por pedido, sozinho.
- **Ritmo medido:** 3,2 a 3,4 palavras por segundo (o Kokoro dava ~2,8 a 3,2). 280–380 palavras dão ~1 min 25 s a 2 min.
- **Saída:** `.m4a` AAC-LC mono, 48 kHz, 160 kbps, −16 LUFS, pico abaixo de −1,5 dBTP (igual aos vídeos de venda).
- **Sotaque:** o classificador do `qa_batch.sh` continua (venv `tts/.venv`, criado pelo `setup.sh --tts`). No teste de 14/11, 2 dos 3 roteiros deram pt-BR em todas as janelas; no 3º, a janela com "os botões marcados AUX" deu 0,00 (sigla em inglês logo no começo). Ouça antes de reescrever.
- **Termos de uso:** no plano grátis, o Google pode usar o texto e o áudio para melhorar os produtos dele. Os termos não trazem licença comercial explícita (ver `ESCOLHA.md`). Foi decisão do dono.

## Guia de escrita do roteiro (voz Gemini)
**Escreva a grafia normal.** A Gemini lê bem termo em inglês, sigla e nome de marca: WING, P.A., LO CUT, pré-fader, PDF, SAVE, Behringer, fader, reverb, phantom power, USB e XLR saíram certos. **Nada de grafia fonética do Kokoro** ("fêider", "guêit", "cuíz", "Bêringuer", "dê i"); com a Gemini, ela piora a fala.

O `--lint` recusa, antes de gastar pedido, os padrões que a voz errou na produção dos vídeos (lista `RISCO` em `gen_gemini.py`):
- **Letra solta** ("o i explica" saiu "o IN"): escreva o nome da coisa ("o botão de informação", "o canal A" vira "o primeiro canal").
- **"Está"** sai "Tá": escreva `tá` (registro falado, de professor conversando).
- **Imperativo formal** ("Aperte", "Gire", "Ligue", "Toque", "Deslize", "Salve") sai coloquial: escreva `aperta`, `gira`, `liga`, `toca`, `desliza`, `salva`.
- **patch** sai "pet": fale "roteamento" ou "ligação" e deixe PATCH só na tela.
- **Termo em inglês minúsculo** (`main`, `send`, `bus`, `mute`, `gain`): use o termo em português ("saída principal", "envio", "barramento", "mudo", "ganho") ou a sigla da tela em MAIÚSCULAS (MAIN MIX, MUTE).

Continuam valendo as regras de fala:
- Texto corrido, como fala. Sem markdown, marcadores, parênteses, barras, setas, emoji ou URL.
- Frases de até 25–30 palavras. Linha em branco entre parágrafos vira pausa maior.
- Português do Brasil falado: "você", "a gente", "tá", gerúndio.
- Números e unidades por extenso ("quarenta e oito volts", "menos dez decibéis"); a conferência já casa "48" com "quarenta e oito".
- "WING" às vezes sai "Win", ao acaso: só a conferência pega. Se a mesma palavra falhar 2 vezes, reescreva a frase.

## Arquivos
- `gen.sh`: entrada (cofre + chaves). `gen_curso.py`: pasta, lotes, lint, conferência tolerante, retomada. `gen_gemini.py`: motor (cópia de `geral/videos-de-venda-compartilhado/voz/tools/gen_gemini.py`; se o de lá mudar, copie de novo). `v2_wts.py`: Whisper com tempo de palavra.
- `qa/`: classificador de sotaque e métricas do `qa_batch.sh`. `kokoro/`: o motor antigo e o guia de grafia dele (histórico).
