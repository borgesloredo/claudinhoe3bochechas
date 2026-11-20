#!/bin/bash
# Chamado pela skill quando /curso-mesa-de-som roda fora do modo enxuto:
# abre uma janela nova do Terminal com a sessão enxuta, na mesma pasta e na mesma conta do Claude.
set -e
K="$(cd "$(dirname "$0")/.." && pwd)"
q() { printf '%q' "$1"; }
CMD="cd $(q "$PWD") && "
[ -n "$CLAUDE_CONFIG_DIR" ] && CMD+="export CLAUDE_CONFIG_DIR=$(q "$CLAUDE_CONFIG_DIR") && "
CMD+="$(q "$K/scripts/abrir-sessao.sh") /curso-mesa-de-som"
# AppleScript: escapa \ e " do comando
AS=${CMD//\\/\\\\}; AS=${AS//\"/\\\"}
osascript -e "tell application \"Terminal\" to do script \"$AS\"" -e 'tell application "Terminal" to activate' >/dev/null
echo "janela nova aberta: $CMD"
