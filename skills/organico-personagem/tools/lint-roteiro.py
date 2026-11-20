#!/usr/bin/env python3
"""Lint objetivo do roteiro (o roteirista roda antes de entregar; o revisor só julga o que é subjetivo).

Uso: python3 lint-roteiro.py <roteiro.json> [--dur 30-60] [--narrado]
roteiro.json = {id, nome, duracao_s, cenas: [{t_ini, t_fim, texto_tela, visual, motion, fala?}]}
- texto_tela: só o que conta pela regra "Como contar" (legenda, selo, marca, CTA, visor, rótulo inventado). Serigrafia de textura fica no campo visual.
- FALHA: > 9 palavras numa tela, termo proibido, sem CTA na última cena, duração fora da faixa, "não é X, é Y" mais de 1 vez,
  narração > 125 palavras ou cena falada a mais de 3,4 palavras/s. AVISO: cena < 1,2 s ou > 4,5 s, buraco/sobreposição entre cenas,
  risco de pronúncia (regras do kit/voz/gen_gemini.py).
Sai com código 1 se houver FALHA. Teste: python3 lint-roteiro.py --teste
"""
import argparse, importlib.util, json, re, sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
PROIBIDO = re.compile(r"oficia(l|is)|https?://|www\.|\.com\b|(?<![\w.])@\w|R\$|\bpre[cç]o\b|\bcupom\b|\bdesconto\b|\d{4}-\d{4}", re.I)
COMUNS = set("para pela pelo com sem que isso essa esse este esta você voce mais tudo cada garanta curso independente seuperfil".split())
NAO_E = re.compile(r"\bn[ãa]o (é|e)\b[^.!?]{1,60}?,\s*(é|e)\b", re.I)


def palavras(t):
    return [w for w in re.split(r"[\s/·|]+", t or "") if re.search(r"[\wÀ-ú]", w)]


def riscos_pronuncia(falas):
    try:
        spec = importlib.util.spec_from_file_location("gg", AQUI.parent / "kit/voz/gen_gemini.py")
        gg = importlib.util.module_from_spec(spec); spec.loader.exec_module(gg)
        return gg.riscos(falas)
    except Exception as e:  # o lint de pronúncia é bônus; o gerador repete a checagem antes do pedido
        return [f"(lint de pronúncia indisponível: {e})"]


def lint(r, dur=(30, 60), narrado=False, cta=r"garanta o seu"):
    R = []
    add = lambda n, m: R.append((n, m))
    cenas = r.get("cenas") or []
    if not cenas:
        add("FALHA", "sem cenas")
    D = float(r.get("duracao_s") or (cenas[-1]["t_fim"] if cenas else 0))
    add("OK" if dur[0] <= D <= dur[1] else "FALHA", f"duração {D:.1f} s (alvo {dur[0]}-{dur[1]})")
    tudo = []
    for i, c in enumerate(cenas, 1):
        n = len(palavras(c.get("texto_tela")))
        if n > 9:
            add("FALHA", f"cena {i}: {n} palavras na tela (máx. 9): {c['texto_tela']!r}")
        d = c["t_fim"] - c["t_ini"]
        if d < 1.2 or d > 4.5:
            add("AVISO", f"cena {i}: {d:.1f} s (faixa 1,5-4 s)")
        if i > 1 and abs(c["t_ini"] - cenas[i - 2]["t_fim"]) > 0.05:
            add("AVISO", f"cena {i}: começa em {c['t_ini']} mas a anterior acaba em {cenas[i - 2]['t_fim']}")
        for campo in ("texto_tela", "fala"):
            achou = sorted(set(m.group(0) for m in PROIBIDO.finditer(c.get(campo) or "")))
            if achou:
                add("FALHA", f"cena {i} ({campo}): termo proibido {achou}")
        tudo.append((c.get("texto_tela") or "") + " " + (c.get("fala") or ""))
        if narrado and c.get("fala"):
            wps = len(palavras(c["fala"])) / max(d, 0.1)
            if wps > 3.4:
                add("FALHA", f"cena {i}: fala a {wps:.1f} palavras/s em {d:.1f} s (máx. ~3); alongue a cena ou corte a fala")
    if cenas and not re.search(cta, (cenas[-1].get("texto_tela") or "").lower()):
        add("FALHA", f"última cena sem o CTA ({cta})")
    n_nao_e = len(NAO_E.findall(" ".join(tudo)))
    if n_nao_e > 1:
        add("FALHA", f"fórmula \"não é X, é Y\" {n_nao_e} vezes (máx. 1)")
    freq = {}
    for w in palavras(" ".join(tudo).lower()):
        w = re.sub(r"[^\wà-ú]", "", w)
        if len(w) >= 4 and w not in COMUNS:
            freq[w] = freq.get(w, 0) + 1
    rep = sorted((n, w) for w, n in freq.items() if n > 2)
    if rep:
        add("AVISO", "palavra repetida mais de 2 vezes (tela + fala): " + ", ".join(f"{w} ({n})" for n, w in reversed(rep)))
    if narrado:
        falas = [c["fala"] for c in cenas if c.get("fala")]
        total = sum(len(palavras(f)) for f in falas)
        add("OK" if 0 < total <= 125 else "FALHA", f"narração: {total} palavras (máx. ~120)")
        for aviso in riscos_pronuncia(falas):
            add("AVISO", f"pronúncia: {aviso}")
    if not any(n == "FALHA" for n, _ in R):
        add("OK", f"{len(cenas)} cenas sem falha objetiva")
    for n, m in R:
        print(f"{n:5s} {m}")
    return not any(n == "FALHA" for n, _ in R)


def teste():
    bom = {"id": "x", "duracao_s": 31, "cenas": [
        {"t_ini": 0, "t_fim": 3, "texto_tela": "O erro nasceu no ganho.", "visual": "", "motion": "", "fala": "O erro nasceu no ganho."},
        {"t_ini": 3, "t_fim": 31, "texto_tela": "Garanta o seu · Curso independente · seuperfil", "visual": "", "motion": ""}]}
    assert lint(bom, narrado=True)
    ruim = json.loads(json.dumps(bom))
    ruim["cenas"][0]["texto_tela"] = "Curso oficial com tudo que você precisa saber hoje mesmo"
    ruim["cenas"][1]["texto_tela"] = "Compre já"
    ruim["cenas"][0]["fala"] = "Não é sorte, é método. Não é dom, é treino. " * 3
    assert not lint(ruim, narrado=True)
    org = json.loads(json.dumps(bom))
    org["cenas"][1]["texto_tela"] = "Comenta RETORNO · Curso independente · seuperfil"
    assert not lint(org, narrado=True) and lint(org, narrado=True, cta=r"comenta|salva|marca")
    print("teste ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["--teste"]:
        teste(); sys.exit(0)
    p = argparse.ArgumentParser()
    p.add_argument("json"); p.add_argument("--dur", default="30-60"); p.add_argument("--narrado", action="store_true")
    p.add_argument("--cta", default=r"garanta o seu", help="regex do CTA exigido na última cena (orgânico: 'comenta|salva|marca|segue')")
    a = p.parse_args()
    lo, hi = (float(x) for x in a.dur.split("-"))
    r = json.loads(Path(a.json).read_text())
    r = r.get("roteiro", r)  # aceita também o roteiro-workflow.json {rodada, roteiro, revisao}
    sys.exit(0 if lint(r, (lo, hi), a.narrado, a.cta) else 1)
