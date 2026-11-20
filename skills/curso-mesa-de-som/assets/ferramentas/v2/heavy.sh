#!/bin/bash
# Roda um comando pesado (TTS, whisper, classificador) com trava global de HEAVY_VAGAS vagas (padrão 1; mais que 1 trava o Mac com as sessões abertas; 5 travou o Mac em 17/11) no Mac (16 GB).
# Vaga 0 = /tmp/curso-v2-heavy.lock (o nome antigo, de quando era um por vez); as outras = .1, .2...
# Uso: tools/v2/heavy.sh <comando...>
N=${HEAVY_VAGAS:-1}
while :; do
  for ((i=0; i<N; i++)); do
    L=/tmp/curso-v2-heavy.lock; ((i)) && L="$L.$i"
    if mkdir "$L" 2>/dev/null; then
      echo $$ > "$L/pid"; trap 'rm -rf "$L"' EXIT
      "$@"; exit $?
    fi
    pid=$(cat "$L/pid" 2>/dev/null); [ -n "$pid" ] && ! kill -0 "$pid" 2>/dev/null && rm -rf "$L"
  done
  sleep 3
done
