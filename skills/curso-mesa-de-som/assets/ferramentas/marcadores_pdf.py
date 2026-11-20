#!/usr/bin/env python3
"""Acrescenta ao PDF um marcador lateral por capítulo (como os 29 da LS9), a partir de curso.html e paginas.json.
Uso: python3 marcadores_pdf.py <curso.html> <paginas.json> <curso.pdf>   (reescreve o PDF; requer pypdf)"""
import html, json, re, sys
from pypdf import PdfReader, PdfWriter
src, pj, pdf = sys.argv[1:]
h = open(src, encoding="utf8").read(); pg = json.load(open(pj))
caps = {}
for m in re.finditer(r'<section class="chapter[^"]*" id="cap-(\d+)">(.*?)</h2>', h, flags=re.S):
    t = re.sub(r'<span class="mesas">.*?</span>', "", m.group(2), flags=re.S)
    t = re.sub(r"<[^>]+>", " ", t[t.rfind("<h2"):]); caps[m.group(1)] = " ".join(html.unescape(t).split())
assert caps and set(caps) == set(pg), {"sem página": sorted(set(caps) - set(pg)), "sem título": sorted(set(pg) - set(caps))}
w = PdfWriter(clone_from=pdf)
assert not w.outline, "PDF já tem marcadores"
n = len(w.pages)
for k in sorted(caps, key=int):
    assert 1 <= pg[k] <= n; w.add_outline_item(caps[k], pg[k] - 1)
w.write(pdf)
r = PdfReader(pdf); assert len(r.outline) == len(caps) and len(r.pages) == n
print(f"{pdf}: {len(caps)} marcadores")
