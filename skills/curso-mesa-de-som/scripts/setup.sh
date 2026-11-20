#!/bin/bash
# Prepara um projeto de curso: pastas, ferramentas de referência, node (playwright/reveal/gsap), navegadores, skills de design.
# Uso: setup.sh <pasta_do_projeto> [--tts]     (--tts também cria o venv da voz, usado na Fase 4)
set -e
K="$(cd "$(dirname "$0")/.." && pwd)"; P="$1"; [ -z "$P" ] && { echo "uso: setup.sh <pasta_do_projeto> [--tts]"; exit 1; }
mkdir -p "$P"/{downloads,01-manuais,03-pesquisa,06-pdf,07-slides,backups,entregas} "$P/tools"
# Ferramentas de referência (da 1ª execução): copiadas uma vez; o projeto adapta as cópias
[ -f "$P/tools/build_slides.py" ] || { cp -R "$K/assets/ferramentas/." "$P/tools/"; mkdir -p "$P/tools/bespoke" "$P/tools/notes"; \
  mv "$P/tools/bespoke-README.md" "$P/tools/bespoke/README.md"; mv "$P/tools/notes-README.md" "$P/tools/notes/README.md"; }
# Git desde o início, só com fontes e ferramentas (áudio, pacotes e bibliotecas ficam fora)
# Ferramentas novas da skill chegam também a cursos já iniciados
for f in integrar.sh notas_dump.py; do [ -f "$P/tools/$f" ] || cp "$K/assets/ferramentas/$f" "$P/tools/"; done
[ -f "$P/.gitignore" ] || cp "$K/assets/gitignore-fontes.txt" "$P/.gitignore"
[ -d "$P/.git" ] || git -C "$P" init -q
# Node: usa o node do PATH ou o do fnm
command -v node >/dev/null || export PATH="$(ls -d ~/.local/share/fnm/node-versions/*/installation/bin 2>/dev/null | tail -1):$PATH"
cd "$P/tools"; [ -f package.json ] || npm init -y >/dev/null
[ -d node_modules/playwright ] || npm i playwright reveal.js@5.1.0 gsap@3.13.0 >/tmp/curso-setup-npm.log 2>&1 || { echo "ERRO no npm (veja /tmp/curso-setup-npm.log)"; exit 1; }
npx playwright install chromium webkit >/tmp/curso-setup-pw.log 2>&1 || { echo "ERRO ao baixar navegadores (veja /tmp/curso-setup-pw.log)"; exit 1; }
# ffmpeg (vídeos das direções e áudio da V2)
FF=$(command -v ffmpeg || ls ~/.local/bin/ffmpeg 2>/dev/null); if [ -z "$FF" ]; then command -v brew >/dev/null && brew install ffmpeg >/dev/null 2>&1 || { echo "ERRO: instale o ffmpeg (brew install ffmpeg)"; exit 1; }; FF=$(command -v ffmpeg); fi
[ -x ~/.local/bin/ffmpeg ] || { mkdir -p ~/.local/bin; ln -sf "$FF" ~/.local/bin/ffmpeg; ln -sf "$(dirname "$FF")/ffprobe" ~/.local/bin/ffprobe 2>/dev/null; }
# Biblioteca do deck (dentro da pasta do deck: o Safari bloqueia ../)
mkdir -p "$P/07-slides/lib/gsap" && cp -R node_modules/reveal.js/dist node_modules/reveal.js/plugin "$P/07-slides/lib/" && \
  cp node_modules/gsap/dist/{gsap,SplitText,DrawSVGPlugin,MotionPathPlugin,Flip,CustomEase}.min.js "$P/07-slides/lib/gsap/"
# Skills de design (frontend-slides, gsap-*, motion-design)
for s in "$K"/assets/vendor-skills/*; do n=$(basename "$s"); [ -e ~/.claude/skills/$n ] || cp -R "$s" ~/.claude/skills/; done
# Voz (Fase 4): Gemini TTS Puck (a voz dos videos de venda, chaves no cofre). O venv tts/.venv fica so para o classificador de sotaque do QA.
if [ "$2" = "--tts" ]; then
  T="$P/tools/v2/tts"; UV=$(command -v uv || echo ~/.local/bin/uv)
  [ -x "$UV" ] || { curl -LsSf https://astral.sh/uv/install.sh | sh >/dev/null 2>&1; UV=~/.local/bin/uv; }
  # transcrição do QA de áudio (qa_batch.sh usa o python deste tool)
  [ -x ~/.local/share/uv/tools/mlx-whisper/bin/python ] || "$UV" tool install mlx-whisper >/dev/null 2>&1 || { echo "ERRO ao instalar mlx-whisper"; exit 1; }
  [ -x "$T/.venv/bin/python" ] || { "$UV" venv -p 3.12 "$T/.venv" >/dev/null; "$UV" pip install -p "$T/.venv/bin/python" \
     mlx-audio==0.6.1 "misaki[en]==0.9.4" espeakng-loader==0.2.4 phonemizer-fork num2words soundfile torch transformers >/dev/null; }
  # Whisper em cache (o gerador roda offline: corta e confere as falas com ele)
  ~/.local/share/uv/tools/mlx-whisper/bin/python -I -c "from huggingface_hub import snapshot_download as s; s('mlx-community/whisper-large-v3-turbo')" >/tmp/curso-setup-whisper.log 2>&1 || { echo "ERRO ao baixar o Whisper (veja /tmp/curso-setup-whisper.log)"; exit 1; }
  # Autoteste sem gastar pedido da cota: confere o gerador e se as 5 chaves chegaram do cofre
  "$T/gen.sh" --teste >/tmp/curso-setup-tts.log 2>&1 || { echo "ERRO no teste de voz (veja /tmp/curso-setup-tts.log)"; exit 1; }
  echo "tts ok"
fi
echo "setup ok: $P"
