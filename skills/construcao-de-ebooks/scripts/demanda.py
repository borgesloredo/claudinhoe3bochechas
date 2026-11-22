#!/usr/bin/env python3
"""Sugestões de busca do Google e do YouTube no Brasil: mostram o que as pessoas digitam, não o volume.
Uso: python3 -I demanda.py "termo" ["outro termo"] > sugestoes.json
Para no primeiro bloqueio e registra "não medido". Nunca tenta contornar."""
import json, sys, time, urllib.error, urllib.parse, urllib.request

MOLDES = ["{}", "como {}", "por que {}", "{} para", "{} não", "{} ou", "erros {}", "curso {}"]

PAGINA = {"google": "https://www.google.com/search?q=", "youtube": "https://www.youtube.com/results?search_query="}


def buscar(q, canal):
    p = {"client": "firefox", "hl": "pt-BR", "gl": "br", "ie": "utf-8", "oe": "utf-8", "q": q}
    if canal == "youtube":
        p["ds"] = "yt"
    url = "https://suggestqueries.google.com/complete/search?" + urllib.parse.urlencode(p)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read().decode("utf-8", "replace"))[1]


def coletar(termos, buscar=buscar, pausa=0.4):
    saida = {"medida": "sugestões de busca, sem volume", "aviso": "podem vir puxadas para a cidade de quem pesquisa", "canais": {}}
    for canal in ("google", "youtube"):
        achados, estado = {}, "ok"
        for q in dict.fromkeys(m.format(t) for t in termos for m in MOLDES if not (m.startswith("como") and t.startswith("como"))):
            try:
                if s := buscar(q, canal):
                    achados[q] = {"prova": PAGINA[canal] + urllib.parse.quote_plus(q), "sugestoes": s}
            except (urllib.error.URLError, OSError, ValueError) as e:
                estado = f"não medido a partir de '{q}': {e}"
                break
            time.sleep(pausa)
        saida["canais"][canal] = {"estado": estado, "sugestoes": achados}
    return saida


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    print(json.dumps(coletar(sys.argv[1:]), ensure_ascii=False, indent=1))
