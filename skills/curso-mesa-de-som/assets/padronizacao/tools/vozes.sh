#!/bin/bash
# Regrava as vozes listadas em ws/<c>/vozes.txt (um id por linha) com o motor do próprio curso (tools/v2/tts/gen.sh: Gemini Puck, a voz dos vídeos de venda, desde 14/11/2026)
# em ws/<c>/audio-novo/<id>.m4a e faz o QA em ws/<c>/qa-vozes/: Whisper, sotaque pt-BR, volume. Tudo pela trava global heavy.sh,
# um processo pesado por vez (nunca TTS e Whisper juntos). Rode da raiz da padronização. Uso: bash tools/vozes.sh <curso>
set -euo pipefail
cd "$(dirname "$0")/.."
c=$1; V=ws/$c/c/tools/v2; O=ws/$c/qa-vozes; H=$V/heavy.sh
mkdir -p ws/$c/audio-novo $O/whisper
# Gemini: 1 pedido por LOTE de roteiros (cota de ~50 pedidos/dia nas 5 chaves), não 1 por voz. Os roteiros entram por link
# numa pasta só; o gerador refaz só o .m4a ausente ou mais velho que o roteiro (retoma sozinho se a cota do dia acabar).
F=(); T=ws/$c/vozes-txt; rm -rf "$T"; mkdir -p "$T"
while read -r i; do
  [ -n "$i" ] || continue
  [ -f "$V/script/$i.txt" ] || { echo "$c: roteiro não existe: $i"; exit 1; }
  ln -s "$PWD/$V/script/$i.txt" "$T/$i.txt"
  F+=("ws/$c/audio-novo/$i.m4a")
done < <(tr -d ' \r' < ws/$c/vozes.txt)
[ ${#F[@]} -eq 0 ] || { HEAVY_SLOTS=1 "$H" bash "$V/tts/gen.sh" "$T" "ws/$c/audio-novo" > "$O/gen.log" 2>&1 < /dev/null || true; tail -3 "$O/gen.log"; }
grep -q "COTA DO DIA ESGOTADA" "$O/gen.log" 2>/dev/null && { echo "$c: cota Gemini do dia acabou; rode de novo amanhã"; exit 3; }
[ ${#F[@]} -gt 0 ] || { echo "$c: nenhuma voz"; exit 0; }
HEAVY_SLOTS=1 "$H" ~/.local/share/uv/tools/mlx-whisper/bin/python -I "$V/qa_whisper.py" "$O/whisper" "${F[@]}" > "$O/whisper.log" 2>&1
HF_HOME="$V/tts/hf" HEAVY_SLOTS=1 "$H" "$V/tts/.venv/bin/python" -I "$V/tts/qa/cls.py" "${F[@]}" > "$O/sotaque.txt" 2> "$O/sotaque.err"
for f in "${F[@]}"; do printf "%s " "$(basename "$f")"; ~/.local/bin/ffmpeg -nostats -i "$f" -af ebur128 -f null - 2>&1 | grep -E "^\s+I:" | tail -1; done > "$O/loudness.txt"
echo "$c: ${#F[@]} vozes geradas"
python3 -I tools/comparar_voz.py "$c"           # nota Whisper × roteiro (LER abaixo de 0,80: confira com tools/dif_voz.py)
cat "$O/sotaque.txt" "$O/loudness.txt"
python3 -I tools/duracao_voz.py "$c"            # áudio curto demais = cortado; regrave
