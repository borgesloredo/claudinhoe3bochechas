#!/bin/bash
# Uso: gen.sh <roteiro.txt> <saida.m4a>   ou   gen.sh <pasta_roteiros> <pasta_saida>
D="$(cd "$(dirname "$0")" && pwd)"
export HF_HOME="$D/hf" HF_HUB_OFFLINE="${HF_HUB_OFFLINE:-1}"
exec "$D/.venv/bin/python" -I "$D/gen.py" "$@"
