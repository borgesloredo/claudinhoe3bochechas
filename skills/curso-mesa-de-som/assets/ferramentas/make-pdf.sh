#!/bin/sh
# Gera o PDF da aula em duas passadas (a 2ª preenche as páginas do sumário). Caminhos relativos ao projeto.
set -e
T="$(cd "$(dirname "$0")" && pwd)"; P="$(dirname "$T")"; O="$P/06-pdf"
python3 -I "$T/build_pdf_html.py" "$P/05-curso-final.md" "$O/curso.html"
cd "$T" && node render-pdf.mjs "$O/curso.html" "$O/curso.pdf"
python3 - "$O/curso.pdf" "$O/paginas.json" <<'PY'
import sys, json, re
from pypdf import PdfReader
pages = {}
for i, p in enumerate(PdfReader(sys.argv[1]).pages, 1):
    for m in re.finditer(r'C\s*A\s*P\s*Í\s*T\s*U\s*L\s*O\s*(\d)\s*(\d)', p.extract_text() or ''):
        pages.setdefault(str(int(m.group(1) + m.group(2))), i)
json.dump(pages, open(sys.argv[2], 'w'))
print('capítulos achados:', len(pages))
PY
python3 -I "$T/build_pdf_html.py" "$P/05-curso-final.md" "$O/curso.html" "$O/paginas.json"
cd "$T" && node render-pdf.mjs "$O/curso.html" "$O/curso.pdf"
python3 "$T/marcadores_pdf.py" "$O/curso.html" "$O/paginas.json" "$O/curso.pdf"
