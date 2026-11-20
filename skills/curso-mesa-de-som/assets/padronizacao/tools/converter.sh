#!/bin/bash
# Gera de novo as versões "depois" dos cursos dados (sem argumentos: todos). Uso: bash tools/converter.sh [curso ...]
# aula: ws/<c>/depois/aula.html. V2: ws/<c>/depois/v2/08-slides-v2/ = cópia (clonefile, sem gastar disco) da V2 antes, com
# index.html e outros .html do deck empilhados e .css/.js do deck (fora de lib/ e fonts/) com os seletores trocados.
set -euo pipefail; shopt -s nullglob
cd "$(dirname "$0")/../ws"
E=../tools/empilhar.py
for c in ${*:-$(ls)}; do
  # monta em depois/v2.novo e troca no fim: um teste rodando no mesmo curso nunca vê a pasta pela metade
  A=$c/antes/v2/08-slides-v2; D=$c/depois/v2.novo/08-slides-v2
  python3 -I $E "$c/antes/aula.html" "$c/depois/aula.html.novo" > /dev/null && mv "$c/depois/aula.html.novo" "$c/depois/aula.html"
  rm -rf "$c/depois/v2.novo"; mkdir -p "$c/depois/v2.novo"; cp -cR "$A" "$c/depois/v2.novo/"; rm -f "$D/index-depois.html"
  mudou=""
  while IFS= read -r f; do
    case "$f" in
      *.html)
        src="$A/$f"
        # correções da validação de 06/11 (só V2): ws/<c>/corrigir.py entrada saida, aplicado no HTML plano antes de empilhar
        if [ -f "$c/corrigir.py" ] && grep -q 'id="quiz-' "$src"; then
          src=$(mktemp); python3 -I "$c/corrigir.py" "$A/$f" "$src" > /dev/null
        fi
        python3 -I $E "$src" "$D/$f" > /dev/null; mudou="$mudou $f" ;;
      *) t=$(python3 -I $E --trocar "$A/$f" "$D/$f"); [ "$t" = "trocas: 0" ] || mudou="$mudou $f" ;;
    esac
  done < <(cd "$A" && find . -type f \( -name '*.html' -o -name '*.css' -o -name '*.js' \) -not -path './lib/*' -not -path './fonts/*' -not -name 'index-depois.html' | sed 's|^\./||' | sort)
  # vozes regravadas na validação de 06/11
  if [ -d "$c/audio-novo" ]; then for a in "$c"/audio-novo/*.m4a; do
    [ -f "$D/audio/$(basename "$a")" ] || { echo "$c: áudio sem par na V2: $a"; exit 1; }
    cp "$a" "$D/audio/"; mudou="$mudou audio/$(basename "$a")"; done; fi
  rm -rf "$c/depois/v2.velho"; [ -d "$c/depois/v2" ] && mv "$c/depois/v2" "$c/depois/v2.velho"; mv "$c/depois/v2.novo" "$c/depois/v2"; rm -rf "$c/depois/v2.velho"
  D=$c/depois/v2/08-slides-v2
  cp "$D/index.html" "$c/depois/v2-index.html"
  echo "$c convertido; V2 alterados:$mudou"
done
