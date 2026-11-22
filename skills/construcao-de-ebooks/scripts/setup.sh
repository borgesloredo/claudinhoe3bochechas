#!/bin/bash
# Prepara o projeto. Uso: setup.sh <projeto> [--voz]   (--voz só quando houver autoestudo)
set -euo pipefail
R="${1:?uso: setup.sh <projeto> [--voz]}"
mkdir -p "$R"/{pesquisa,conteudo/{telas,paginas,notas,info,roteiro,fonts},audio,qa,backups}
R="$(cd "$R" && pwd)"
[ -f "$R/.gitignore" ] || printf '%s\n' .ferramentas/ '.montagem-*/' audio/ qa/ backups/ amostra/ entregas/ > "$R/.gitignore"
for c in node npm python3 zip unzip; do
  command -v "$c" >/dev/null || { echo "ERRO: falta o programa $c (Node.js: https://nodejs.org)"; exit 1; }
done
T="$R/.ferramentas"; mkdir -p "$T"
[ -f "$T/package.json" ] || echo '{"private":true}' > "$T/package.json"
if [ ! -d "$T/node_modules/playwright" ] || [ ! -d "$T/node_modules/reveal.js" ] || [ ! -d "$T/node_modules/gsap" ]; then
  (cd "$T" && npm i --ignore-scripts playwright@1.65.1 reveal.js@5.1.0 gsap@3.13.0 > npm.log 2>&1) || { echo "ERRO no npm (veja $T/npm.log)"; exit 1; }
fi
(cd "$T" && npx playwright install chromium webkit > navegadores.log 2>&1) || { echo "ERRO nos navegadores (veja $T/navegadores.log)"; exit 1; }

if [ "${2:-}" = "--voz" ]; then
  [ "$(uname -sm)" = "Darwin arm64" ] || { echo "ERRO: o áudio exige Mac com chip Apple. Slides e PDF funcionam sem ele."; exit 1; }
  command -v ffmpeg >/dev/null || [ -x "$HOME/.local/bin/ffmpeg" ] || { echo "ERRO: instale o ffmpeg (brew install ffmpeg)"; exit 1; }
  W="$HOME/.local/share/uv/tools/mlx-whisper/bin/python"
  if [ ! -x "$W" ]; then
    UV="$(command -v uv || true)"
    [ -n "$UV" ] || { echo "ERRO: instale o uv (brew install uv)"; exit 1; }
    "$UV" tool install mlx-whisper > "$T/whisper.log" 2>&1 || { echo "ERRO no Whisper (veja $T/whisper.log)"; exit 1; }
  fi
  "$W" -I -c "from huggingface_hub import snapshot_download as s; s('mlx-community/whisper-large-v3-turbo')" >> "$T/whisper.log" 2>&1 || { echo "ERRO ao baixar o modelo do Whisper"; exit 1; }
fi
echo "setup ok: $R"
