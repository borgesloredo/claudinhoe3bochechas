# Usage: python3 -I pdf2txt.py <in.pdf> <out.txt>
import sys
from pypdf import PdfReader
r = PdfReader(sys.argv[1])
with open(sys.argv[2], "w") as f:
    for i, p in enumerate(r.pages, 1):
        f.write(f"\n\n=== PAGE {i} ===\n{p.extract_text() or ''}")
print(f"{len(r.pages)} pages")
