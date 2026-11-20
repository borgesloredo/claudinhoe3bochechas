#!/bin/bash
# Voz da V2 = a MESMA dos videos de venda (Gemini TTS, voz Puck, estilo "reels2"). Detalhes em README.md e gen_curso.py.
# Uso: gen.sh <roteiro.txt> <saida.m4a> | gen.sh <pasta_roteiros> <pasta_saida> | gen.sh --lint <pasta_roteiros> | gen.sh --teste
# Chaves: as GEMINI_API_KEY_* do cofre (cofre pessoal), nunca do .env. O cofre e o script "cofre" da raiz do seu projeto.
# Rode sempre pelo heavy.sh (o Whisper do corte/conferencia e pesado): ./heavy.sh tts/gen.sh script/ ../../08-slides-v2/audio/
D="$(cd "$(dirname "$0")" && pwd)"
[ "$1" = "--lint" ] && exec python3 -I "$D/gen_curso.py" "$@"
C="${COFRE:-}"; P="$D"
while [ -z "$C" ] && [ "$P" != "/" ]; do [ -x "$P/cofre" ] && C="$P/cofre"; P="$(dirname "$P")"; done
[ -z "$C" ] && C="$HOME/SEU-PROJETO/cofre"
[ -x "$C" ] || { echo "cofre nao encontrado (defina COFRE=<caminho do script cofre>)"; exit 1; }
# Nomes das chaves (um por linha) em chaves-gemini.txt da skill; chave nova = só acrescentar o nome lá.
LISTA="$HOME/.claude/skills/curso-mesa-de-som/chaves-gemini.txt"
CHAVES="${GEMINI_CHAVES:-$( [ -f "$LISTA" ] && grep -v '^#' "$LISTA" | tr '\n' ' ' || echo GEMINI_API_KEY_1 GEMINI_API_KEY_2 GEMINI_API_KEY_3)}"
exec "$C" $CHAVES -- python3 -I "$D/gen_curso.py" "$@"
