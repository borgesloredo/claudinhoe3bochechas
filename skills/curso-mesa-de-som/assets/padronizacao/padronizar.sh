#!/bin/bash
# Padronização final de um curso de mesa (Passo 7 da skill curso-mesa-de-som). Uso: padronizar.sh <R> preparar|aplicar|entregar
#   preparar: monta $R/padronizacao/, empilha aula (arquivo único e deck/) e V2 por capítulo, testa identidade + teclas
#             (Chromium e WebKit), mede a tecla R no original e gera o material da validação (fotos, tiras, títulos).
#   aplicar:  regrava as vozes de ws/<c>/vozes.txt, refaz a V2 com ws/<c>/corrigir.py, fotos novas (OUT=material-r2),
#             testes finais e tecla R. Rode de novo a cada rodada de correção (OUT=material-r3 …).
#   entregar: backup em $R/backups/, zip novo com a mesma lista do original, troca as entregas, commit dos roteiros numa branch nova.
# Navegação padrão: cada capítulo é uma pilha (cap-N … quiz-N); → muda de capítulo, ↓ anda dentro dele.
set -euo pipefail
R=$(cd "$1" && pwd); ETAPA=$2
K=$(cd "$(dirname "$0")" && pwd)
P=$R/padronizacao; c=$(basename "$R"); c=${c#curso-}; W=$P/ws/$c; V1=$R/entregas/v1-aulas
NAVS="chromium webkit"
testes() {   # identidade de imagem + teclas → ← ↓ ↑ + erros JS, aula e V2 nos dois navegadores (um processo por navegador)
  for nav in $NAVS; do (
    TOL=3 timeout 1800 node tools/antes_depois.mjs ws/$c/antes/aula.html ws/$c/depois/aula.html $nav > logs/final/$c-aula-$nav.log 2>&1 || true
    TOL=3 timeout 1800 node tools/antes_depois.mjs ws/$c/antes/v2/08-slides-v2/index.html ws/$c/depois/v2/08-slides-v2/index.html $nav > logs/final/$c-v2-$nav.log 2>&1 || true
  ) & done; wait
  TOL=3 timeout 1800 node tools/antes_depois.mjs ws/$c/antes/aula-deck/index.html ws/$c/depois/aula-deck/index.html chromium > logs/deck-chromium.log 2>&1 || true
  head -1 logs/deck-chromium.log
  python3 -I tools/conferir_final.py
}
case $ETAPA in
preparar)
  [ -e "$P" ] && { echo "já existe $P; para recomeçar, mova-a para $R/backups/ antes"; exit 1; }
  [ -f "$V1/curso-slides.html" ] && [ -f "$R/entregas/v2-autoestudo.zip" ] || { echo "faltam as entregas da V1 e da V2"; exit 1; }
  mkdir -p "$P/logs/final" "$P/logs/tecla-r" "$P/validacao" "$W/antes/v2" "$W/depois"
  cp -R "$K/tools" "$K/exemplos" "$K"/*.md "$P/"
  ln -s "$R/tools/node_modules" "$P/node_modules"   # playwright do curso
  ln -s "$R" "$W/c"                                 # roteiros, glossário e ferramentas do próprio curso
  cp "$V1/curso-slides.html" "$W/antes/aula.html"
  cp -R "$V1/deck" "$W/antes/aula-deck"; chmod -R u+w "$W/antes/aula-deck"
  unzip -q "$R/entregas/v2-autoestudo.zip" -d "$W/antes/v2"
  grep -qx 'padronizacao/' "$R/.gitignore" 2>/dev/null || echo 'padronizacao/' >> "$R/.gitignore"
  cd "$P"
  bash tools/converter.sh "$c"
  cp -R "ws/$c/antes/aula-deck" "ws/$c/depois/aula-deck"
  python3 -I tools/empilhar.py "ws/$c/antes/aula-deck/index.html" "ws/$c/depois/aula-deck/index.html"
  for f in "ws/$c/antes/aula-deck"/*.css "ws/$c/antes/aula-deck"/*.js; do [ -f "$f" ] && python3 -I tools/empilhar.py --trocar "$f" "ws/$c/depois/aula-deck/$(basename "$f")"; done
  testes
  timeout 2400 node tools/tecla_r.mjs "ws/$c/antes/v2/08-slides-v2/index.html" chromium > "logs/tecla-r/$c-antes.log" 2>&1 || true
  head -1 "logs/tecla-r/$c-antes.log"
  M=ws/$c/material; mkdir -p $M
  node tools/material.mjs "$c" > $M/material.log 2>&1; tail -1 $M/material.log
  node "ws/$c/c/tools/shot_motion.mjs" "ws/$c/depois/aula.html" $M/tiras > $M/tiras.log 2>&1; tail -1 $M/tiras.log
  node tools/folhas_tiras.mjs "$c" >> $M/tiras.log 2>&1; tail -1 $M/tiras.log
  node "ws/$c/c/tools/check_titles.mjs" "ws/$c/depois/aula.html" > $M/titulos.log 2>&1 || true; tail -2 $M/titulos.log
  echo "preparar ok: $P (próximo: validador com VALIDACAO.md, curso $c)" ;;
aplicar)
  cd "$P"
  [ -s "ws/$c/vozes.txt" ] && bash tools/vozes.sh "$c"
  bash tools/converter.sh "$c"
  for i in $(cat "ws/$c/vozes.txt" 2>/dev/null); do cmp -s "ws/$c/audio-novo/$i.m4a" "ws/$c/depois/v2/08-slides-v2/audio/$i.m4a" || { echo "voz $i fora do deck"; exit 1; }; done
  OUT=${OUT:-material-r2} node tools/material.mjs "$c" | tail -1
  testes
  for nav in $NAVS; do timeout 2400 node tools/tecla_r.mjs "ws/$c/depois/v2/08-slides-v2/index.html" $nav > "logs/tecla-r/$c-$nav.log" 2>&1 || true; head -1 "logs/tecla-r/$c-$nav.log"; done
  cp "logs/tecla-r/$c-chromium.log" "logs/tecla-r/$c.log"; python3 -I tools/conferir_r.py "$c"
  echo "aplicar ok (próximo: verificador com VERIFICAR.md e OUT=${OUT:-material-r2})" ;;
entregar)
  cd "$P"; D=$(date +%Y%m%d-%H%M); B=$R/backups/padronizacao-$D
  # backup do que vai ser trocado, conferido antes de qualquer troca
  mkdir -p "$B/entregas" "$B/08-slides-v2/audio"
  cp -p "$R/entregas/v2-autoestudo.zip" "$B/entregas/"; cp -pR "$V1" "$B/entregas/"; cp -p "$R/08-slides-v2/index.html" "$B/08-slides-v2/"
  for i in $(cat "ws/$c/vozes.txt" 2>/dev/null); do cp -p "$R/08-slides-v2/audio/$i.m4a" "$B/08-slides-v2/audio/"; done
  cmp -s "$R/entregas/v2-autoestudo.zip" "$B/entregas/v2-autoestudo.zip" && diff -rq "$V1" "$B/entregas/v1-aulas" > /dev/null || { echo "backup falhou; nada trocado"; exit 1; }
  # zip novo: mesma lista e ordem do original; só podem mudar o index.html e as vozes regravadas
  Z=ws/$c/v2-autoestudo.zip; rm -f "$Z"; unzip -Z1 "$R/entregas/v2-autoestudo.zip" > ws/$c/lista-zip.txt
  (cd "ws/$c/depois/v2" && zip -q -X -@ ../../v2-autoestudo.zip < ../../lista-zip.txt)
  unzip -tq "$Z" > /dev/null; diff <(unzip -Z1 "$Z") ws/$c/lista-zip.txt > /dev/null || { echo "lista do zip mudou"; exit 1; }
  echo "mudaram no zip: $(diff <(unzip -v "$R/entregas/v2-autoestudo.zip" | awk 'NF>=8 && $7 ~ /^[0-9a-f]{8}$/ {print $7, $8}') <(unzip -v "$Z" | awk 'NF>=8 && $7 ~ /^[0-9a-f]{8}$/ {print $7, $8}') | grep '^>' | awk '{print $3}' | tr '\n' ' ' || true)"
  # roteiros mudados (o aplicador edita direto no curso): commit numa branch nova
  if [ -n "$(git -C "$R" status --porcelain -- tools/v2/script .gitignore)" ]; then
    git -C "$R" switch -c "claude/padronizacao-$D" > /dev/null
    git -C "$R" add tools/v2/script .gitignore
    git -C "$R" commit -q -m "Padronização final: roteiros dos quizzes corrigidos na validação

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
    echo "commit $(git -C "$R" log --oneline -1)"
  fi
  # troca das entregas (a V1 congelada volta a somente leitura)
  chmod -R u+w "$V1"
  cp "$Z" "$R/entregas/v2-autoestudo.zip"
  cp "ws/$c/depois/aula.html" "$V1/curso-slides.html"
  cp "ws/$c/depois/aula-deck/index.html" "$V1/deck/index.html"
  for f in "ws/$c/depois/aula-deck"/*.css "ws/$c/depois/aula-deck"/*.js; do [ -f "$f" ] && cp "$f" "$V1/deck/"; done
  (cd "$V1" && shasum -a 256 curso-slides.html curso.pdf deck/index.html > SHA256SUMS)
  chmod -R a-w "$V1"
  cp "ws/$c/depois/v2/08-slides-v2/index.html" "$R/08-slides-v2/index.html"
  for i in $(cat "ws/$c/vozes.txt" 2>/dev/null); do cp "ws/$c/audio-novo/$i.m4a" "$R/08-slides-v2/audio/"; done
  cmp -s "$Z" "$R/entregas/v2-autoestudo.zip" && cmp -s "ws/$c/depois/aula.html" "$V1/curso-slides.html" \
    && cmp -s "ws/$c/depois/aula-deck/index.html" "$V1/deck/index.html" && cmp -s "ws/$c/depois/v2/08-slides-v2/index.html" "$R/08-slides-v2/index.html" \
    && (cd "$V1" && shasum -a 256 -c SHA256SUMS > /dev/null) || { echo "troca não confere; restaure de $B"; exit 1; }
  echo "entregar ok: entregas trocadas e conferidas; backup em $B" ;;
*) echo "uso: padronizar.sh <R> preparar|aplicar|entregar"; exit 1 ;;
esac
