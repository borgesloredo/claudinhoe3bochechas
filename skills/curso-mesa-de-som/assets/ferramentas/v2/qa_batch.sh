#!/bin/bash
# QA dos áudios em lote (um processo pesado por vez): transcrição, sotaque, volume.
# Uso: tools/v2/qa_batch.sh [id ...]   (sem ids = todos)
V="$(cd "$(dirname "$0")" && pwd)"; A="$V/../../08-slides-v2/audio"; O="$V/qa-out"; mkdir -p "$O/whisper"
if [ $# -gt 0 ]; then F=(); for i in "$@"; do F+=("$A/$i.m4a"); done; else F=("$A"/*.m4a); fi
"$V/heavy.sh" ~/.local/share/uv/tools/mlx-whisper/bin/python -I "$V/qa_whisper.py" "$O/whisper" "${F[@]}" > "$O/whisper.log" 2>&1
HF_HOME="$V/tts/hf" "$V/heavy.sh" "$V/tts/.venv/bin/python" -I "$V/tts/qa/cls.py" "${F[@]}" > "$O/sotaque-$(date +%H%M%S).txt" 2>"$O/sotaque.err"
for f in "${F[@]}"; do printf "%s " "$(basename "$f")"; ~/.local/bin/ffmpeg -nostats -i "$f" -af ebur128 -f null - 2>&1 | grep -E "^\s+I:" | tail -1; done > "$O/loudness-$(date +%H%M%S).txt"
echo "qa ok: ${#F[@]} arquivos"
