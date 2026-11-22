#!/usr/bin/env python3
"""Confere e ordena os temas candidatos. Uso: python3 -I temas.py pesquisa/temas.json
A nota é a média geométrica de 4 critérios de 1 a 10. Nota alta exige o tipo de prova correspondente."""
import json, math, sys
from urllib.parse import urlparse

CRITERIOS = ("dor", "procura", "lacuna", "aplicacao")
PROVA = {"dor": {"publico"}, "procura": {"busca", "trends", "audiencia"}, "lacuna": {"oferta"}}


def avaliar(temas):
    erros, saida = [], []
    if len(temas) < 5:
        erros.append("traga pelo menos 5 temas")
    for t in temas:
        nome = t.get("titulo") or "(sem título)"
        for k in ("titulo", "dor", "publico", "promessa"):
            if not t.get(k):
                erros.append(f"{nome}: falta {k}")
        provas = t.get("evidencias") or []
        sites = {urlparse(e.get("url", "")).netloc for e in provas} - {""}
        tipos = {e.get("tipo") for e in provas}
        if len(sites) < 2:
            erros.append(f"{nome}: precisa de evidência em 2 sites ou mais")
        if any("wikipedia.org" in s for s in sites):
            erros.append(f"{nome}: Wikipédia não vale como evidência")
        if any(not e.get("achado") for e in provas):
            erros.append(f"{nome}: evidência sem achado")
        notas = t.get("notas") or {}
        if not all(type(notas.get(c)) in (int, float) and 1 <= notas[c] <= 10 for c in CRITERIOS):
            erros.append(f"{nome}: notas de 1 a 10 em {', '.join(CRITERIOS)}")
            continue
        for c, precisa in PROVA.items():
            if notas[c] > 5 and not tipos & precisa:
                erros.append(f"{nome}: {c} acima de 5 exige evidência do tipo {' ou '.join(sorted(precisa))}")
        nota = round(math.prod(notas[c] for c in CRITERIOS) ** (1 / len(CRITERIOS)), 1)
        saida.append({**t, "nota": nota, "trends": t.get("trends") or "não medido"})
    return erros, sorted(saida, key=lambda t: -t["nota"])


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    with open(sys.argv[1], encoding="utf-8") as f:
        erros, temas = avaliar(json.load(f))
    if erros:
        sys.exit("TEMAS FALHOU\n- " + "\n- ".join(erros))
    for i, t in enumerate(temas, 1):
        print(f"{i}. {t['titulo']} | nota {t['nota']} | dor: {t['dor']} | Trends: {t['trends']}")
