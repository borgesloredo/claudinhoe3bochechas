#!/bin/bash
# Cria a pasta de um projeto de vídeos com personagem e instala o que falta.
# Uso: criar-projeto.sh <pasta_do_projeto>      (rodar de novo é seguro: não sobrescreve elenco nem episódios)
set -euo pipefail
K="$(cd "$(dirname "$0")/.." && pwd)"
P="${1:?uso: criar-projeto.sh <pasta_do_projeto>}"
mkdir -p "$P/musica"
# kit e ferramentas sempre na versão da skill
rm -rf "$P/kit" "$P/tools"
cp -R "$K/kit" "$K/tools" "$P/"
cp -n "$K/exemplos/elenco.json" "$P/elenco.json" 2>/dev/null || true
cp "$K/musica/LICENCAS.md" "$P/musica/"
# ffmpeg/ffprobe em ~/.local/bin (o gerador de voz e o historia.py procuram lá)
FF=$(command -v ffmpeg || true)
if [ -z "$FF" ]; then command -v brew >/dev/null && brew install ffmpeg >/dev/null 2>&1 || { echo "ERRO: instale o ffmpeg (brew install ffmpeg)"; exit 1; }; FF=$(command -v ffmpeg); fi
mkdir -p ~/.local/bin
[ -x ~/.local/bin/ffmpeg ] || ln -sf "$FF" ~/.local/bin/ffmpeg
[ -x ~/.local/bin/ffprobe ] || ln -sf "$(dirname "$FF")/ffprobe" ~/.local/bin/ffprobe
# node (render do HyperFrames)
command -v node >/dev/null || { echo "ERRO: instale o Node.js 22 ou mais novo (brew install node)"; exit 1; }
# Whisper (confere cada fala da voz); mlx-whisper exige Mac com chip Apple
UV=$(command -v uv || echo ~/.local/bin/uv)
[ -x "$UV" ] || { curl -LsSf https://astral.sh/uv/install.sh | sh >/dev/null 2>&1; UV=~/.local/bin/uv; }
W=~/.local/share/uv/tools/mlx-whisper/bin/python
[ -x "$W" ] || "$UV" tool install mlx-whisper >/dev/null 2>&1 || { echo "ERRO ao instalar mlx-whisper (precisa de Mac com chip Apple)"; exit 1; }
"$W" -I -c "from huggingface_hub import snapshot_download as s; s('mlx-community/whisper-large-v3-turbo')" >/dev/null 2>&1 || { echo "ERRO ao baixar o modelo do Whisper"; exit 1; }
# Músicas padrão (Mixkit, uso comercial sem atribuição; ver musica/LICENCAS.md): 62 s, fade, -14 LUFS
baixa() {  # $1 nome, $2 id da faixa
  [ -f "$P/musica/$1.m4a" ] && return
  t=$(mktemp -d); curl -fsSL "https://assets.mixkit.co/music/$2/$2.mp3" -o "$t/o.mp3" || { echo "ERRO ao baixar a música $1"; exit 1; }
  "$FF" -v error -i "$t/o.mp3" -t 62 -af "afade=t=out:st=58.5:d=3.5,loudnorm=I=-14:TP=-1.5:LRA=11" -ar 44100 -ac 2 -c:a aac -b:a 192k "$P/musica/$1.m4a"
  rm -rf "$t"
}
baixa calma 738
baixa energica 51
python3 "$P/kit/historia.py" --teste >/dev/null || { echo "ERRO no autoteste do historia.py"; exit 1; }
echo "projeto ok: $P"
