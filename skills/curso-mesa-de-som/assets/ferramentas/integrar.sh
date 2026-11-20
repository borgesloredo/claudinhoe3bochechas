#!/bin/bash
# Integração do deck (Fase 3), sem agente pensando: regera o deck, roda todos os checadores, gera as folhas de contato,
# as tiras de motion, o dump de texto+notas para os revisores e o arquivo único.
# Uso: sh tools/integrar.sh <pasta-do-curso>
# Saída: "INTEGRAR OK" e código 0; ou a lista de falhas com as últimas 40 linhas de cada uma e código 1.
# Logs completos em <curso>/07-slides/redesign/integrar-logs/.
C="$(cd "${1:?uso: integrar.sh <pasta-do-curso>}" && pwd)"; T="$C/tools"; D="$C/07-slides/index.html"
S="$C/07-slides/redesign/shots-deck"; L="$C/07-slides/redesign/integrar-logs"
# Mesma proteção de tools/browser-environment.cjs: o seatbelt do Codex derruba navegadores no macOS
if [ "$(uname)" = Darwin ] && [ "$CODEX_SANDBOX" = seatbelt ]; then
  echo "BROWSER_ENVIRONMENT_BLOCKED: rode este comando no Terminal do Mac. Não repita aqui."; exit 2; fi
command -v node >/dev/null || export PATH="$(ls -d ~/.local/share/fnm/node-versions/*/installation/bin 2>/dev/null | tail -1):$PATH"
mkdir -p "$S" "$L"; cd "$T" || exit 1
FALHAS=""
run() { n=$1; shift; if "$@" >"$L/$n.log" 2>&1; then echo "ok    $n"; else echo "FALHA $n"; FALHAS="$FALHAS $n"; fi; }
# sem argumentos: a versão base e as adaptadas pelos cursos geram 07-slides/index.html por padrão
run build python3 -I build_slides.py
if [ -n "$FALHAS" ]; then echo "--- build"; tail -40 "$L/build.log"; exit 1; fi
run verify_slides node verify_slides.mjs "$D"
run check_fonts node check_fonts.mjs "$D"
run check_titles node check_titles.mjs "$D"
run check_cuts python3 -I check_cuts.py "$D"
run check_notes python3 -I check_notes.py "$D"
run check_padrao node check_padrao.mjs "$C"
# tiras antes das folhas: shot_motion sem ids apaga todo .png da pasta, inclusive folhas antigas
run shot_motion node shot_motion.mjs "$D" "$S"
run shot_sheets node shot_sheets.mjs "$D" "$S" 24
run notas_dump python3 -I notas_dump.py "$D" "$C/07-slides/redesign/notas-dump.md"
run arquivo_unico python3 -I inline_single.py "$D" "$C/07-slides/curso-slides.html"
if [ -z "$FALHAS" ]; then echo "INTEGRAR OK"; exit 0; fi
for n in $FALHAS; do echo "--- $n"; tail -40 "$L/$n.log"; done; exit 1
