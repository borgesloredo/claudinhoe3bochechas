#!/bin/bash
# Abre o Claude Code enxuto para o curso: sem plugins, conectores do claude.ai, servidores MCP e skills que o curso não usa.
# Cada agente dos workflows nasce com esse contexto; medido em 03/11/2026: ~41 mil tokens na sessão normal, ~22 mil na enxuta.
# O Mac fica acordado enquanto a sessão durar (caffeinate termina junto com o Claude).
# Uso: abrir-sessao.sh [argumentos do claude]   ex.: abrir-sessao.sh "/curso-mesa-de-som"
set -e
K="$(cd "$(dirname "$0")/.." && pwd)"
CFG="${TMPDIR:-/tmp}/curso-sessao-enxuta.json"
# Plugins lidos na hora de abrir: plugin instalado depois também fica desligado
python3 -I - "$K/sessao-enxuta.json" "$HOME/.claude/settings.json" "$CFG" <<'PY'
import json, sys
base, user, out = sys.argv[1:]
c = json.load(open(base))
try: plugins = json.load(open(user)).get("enabledPlugins", {})
except FileNotFoundError: plugins = {}
c["enabledPlugins"] = {k: False for k in plugins}
json.dump(c, open(out, "w"), indent=2, ensure_ascii=False)
PY
# "$@" antes das opções: --mcp-config aceita vários arquivos e engoliria o prompt
exec caffeinate -dims claude "$@" --settings "$CFG" --strict-mcp-config --mcp-config "$K/mcp-vazio.json"
