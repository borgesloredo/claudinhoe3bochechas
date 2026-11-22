#!/bin/bash
# Voz do autoestudo. Nunca mostra a chave.
# Uso: voz.sh --chaves | --lint <pasta> | --teste | <roteiros> <audios>
set -euo pipefail
D="$(cd "$(dirname "$0")" && pwd -P)"
V="$D/voz/gerar.py"
[ "${1:-}" = "--lint" ] && exec python3 -I "$V" "$@"

rodar=(python3 -I "$V" "$@")
[ "${1:-}" = "--chaves" ] && rodar=(python3 -I -c 'import os; n=sum(1 for k,v in os.environ.items() if k.startswith("GEMINI") and "KEY" in k and v); print(f"{n} chave(s)"); raise SystemExit(0 if n else 1)')
case "${1:-}" in --chaves|--teste) ;; *) rodar=("$D/heavy.sh" "${rodar[@]}") ;; esac

# 1) chave da própria pessoa (arquivo lido como dado, nunca executado)
ARQ="$HOME/.config/construcao-de-ebooks/gemini.env"
if [ -f "$ARQ" ]; then
  while IFS='=' read -r k v || [ -n "$k" ]; do
    [[ "$k" =~ ^GEMINI_API_KEY[A-Z0-9_]*$ ]] && export "$k=$v"
  done < "$ARQ"
  exec "${rodar[@]}"
fi
# 2) script "cofre" numa pasta acima da instalação da skill, com a lista de nomes das chaves
P="$D"
while [ "$P" != "/" ]; do
  if [ -x "$P/cofre" ]; then
    L="$P/skill-curso-mesa-de-som/chaves-gemini.txt"
    nomes=()
    if [ -n "${GEMINI_CHAVES:-}" ]; then
      read -r -a nomes <<< "$GEMINI_CHAVES"
    elif [ -f "$L" ]; then
      while read -r n || [ -n "$n" ]; do [[ "$n" =~ ^GEMINI[A-Z0-9_]+$ ]] && nomes+=("$n"); done < "$L"
    fi
    if [ "${#nomes[@]}" -gt 0 ]; then exec "$P/cofre" "${nomes[@]}" -- "${rodar[@]}"; fi
  fi
  P="$(dirname "$P")"
done
echo "SEM CHAVE: siga references/chave-de-voz.md"
exit 1
