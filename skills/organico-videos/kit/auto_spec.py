#!/usr/bin/env python3
"""spec.json automático: lê o campo "visual" de cada cena do roteiro e escolhe as peças do gerar_cenas.py.

Uso: python3 auto_spec.py <pasta_do_video> <tema>     (não sobrescreve spec.json feito à mão: use --forca)
     python3 auto_spec.py --teste
Regra: uma peça principal por cena (prioridade: quiz > círculos > tela > caminho > mesa > canal > knob > fader/medidor > palco),
passos (CHECKLIST) por cima quando cabe, pílula do texto 'PÍLULA verde|vermelha 'X''. Penúltima com PRODUTO = produto; última = CTA.
shortcut: heurística por palavra-chave; cena estranha cai num microfone genérico. Ajuste à mão o spec.json se o vídeo pedir.
"""
import json, re, sys
from pathlib import Path

CANAIS = {"VOZ": 0, "VOZES": 0, "VIOLÃO": 2, "TECLADO": 3, "TEC": 3, "BAIXO": 4, "BUMBO": 5, "CAIXA": 6, "GUITARRA": 7, "GTR": 7}
PEAKS = [["bell", 150, 6, 1], ["bell", 800, 5, .8], ["bell", 3000, 7, .6]]


def q(v):
    return [x.strip().upper() for x in re.findall(r"'([^']{2,24})'", v)]


def tem(v, *ps):
    return any(re.search(p, v, re.I) for p in ps)


def pill(v):
    m = re.search(r"PÍLULA\s*(verde|vermelha|amarela)?\s*'([^']+)'", v)
    if not m:
        return None
    return [m.group(2).upper(), {"verde": "g", "vermelha": "r", "amarela": "a"}.get(m.group(1) or "", "a")]


def tela(v):
    o = {"t": "tela"}
    if tem(v, "abafad"):
        o["curvas"] = [[["lshelf", 200, 9], ["hshelf", 4000, -6]]]
    elif tem(v, "pico"):
        o["curvas"] = [[], PEAKS]
    elif tem(v, "sino", "varre"):
        o["curvas"] = [[["bell", f, 10, .35]] for f in (250, 900, 3000, 7000)]
    elif tem(v, "vale", "corta", "cortando"):
        o["curvas"] = [[], [["bell", 3000, -7, .8]]]
    elif tem(v, "colina", "reforço", "realce"):
        o["curvas"] = [[], [["bell", 2500, 4, 1.5]]]
    elif tem(v, "rampa", "LOW CUT", "corte", "filtro", "HPF"):
        o["curvas"] = [[], [["hp", 120]]]
    else:
        o["curvas"] = [[], [["bell", 1000, 3, 1.2]]]
    m = re.search(r"(\d+(?:[.,]\d+)?)\s*(?:a|e|–|-)\s*(\d+(?:[.,]\d+)?)\s*(k?Hz)", v)
    if m:
        k = 1000 if m.group(3).startswith("k") else 1
        f1, f2 = (float(x.replace(",", ".")) * k for x in m.group(1, 2))
        if 20 <= f1 < f2 <= 20000:
            o.update(faixa=[f1, f2], faixa_txt="")
    if tem(v, "vermelh"):
        o["cor1"] = "r"
    elif tem(v, "verde"):
        o["cor1"] = "g"
    return o


def canal(v):
    o = {"t": "canal", "hl": []}
    if tem(v, r"\bCOMP\b"):
        o["botoes"] = ["COMP", "EQ"]
    if tem(v, r"\bGATE\b"):
        o["botoes"] = ["GATE", "EQ"]
    if tem(v, r"GAIN"):
        o.update(gain=.2, gain1=.6); o["hl"].append("gain")
    if tem(v, r"(LOW CUT|COMP|GATE|HPF)[^.;]*(acend|aces)"):
        o["lowcut1"] = True; o["hl"].append("lowcut")
    if tem(v, r"MUTE[^.;]*(acend|aces)"):
        o["mute"] = True; o["hl"].append("mute")
    elif tem(v, r"MUTE[^.;]*apag"):
        o.update(mute=True, mute1=False)
    if tem(v, "48 ?V"):
        o["p48_1"] = True; o["hl"].append("48v")
    for k in ("AGUDO", "GRAVE"):
        if k in v:
            o.setdefault("knobs", {})[k] = [.5, .85]; o["hl"].append(k.lower())
    if tem(v, r"FADER[^.;]*desc"):
        o.update(fader=.9, fader1=.4); o["hl"].append("fader")
    elif tem(v, r"FADER[^.;]*sub"):
        o.update(fader=.3, fader1=.85); o["hl"].append("fader")
    if tem(v, "MEDIDOR") and tem(v, "vermelh", "CLIP"):
        o.update(meter=[.85, 1], clip=True)
    elif tem(v, "MEDIDOR"):
        o.update(meter=[.05, .15], meter1=[.45, .65])
    if tem(v, r"\bEQ\b") and not o["hl"]:
        o["hl"] = ["eqknobs"]
    return o


def mesa(v):
    o = {"t": "mesa"}
    hl = sorted({i for n, i in CANAIS.items() if re.search(rf"\b{n}\b", v)})
    if hl:
        o["hls"] = hl[:3]
    if tem(v, "48 ?V"):
        o["p48"] = True
    elif tem(v, "LOW CUT", "HPF", "filtro"):
        o.update(hpf=True, hpf1=hl or [0, 1])
    if tem(v, "vermelh"):
        o["vermelho"] = hl or [0, 1, 2]
    return o


def caminho(v):
    m = re.search(r"CAMINHO[^:]*:\s*([^;.,]+)", v)
    bl = []
    if m:
        bl = [re.sub(r"[^A-ZÀ-Ú0-9 +]", "", x.upper()).strip()[:10] for x in re.split(r"→|->|>", m.group(1))]
        bl = [b for b in bl if b][:5]
    o = {"t": "caminho", "blocos": bl if len(bl) >= 2 else ["MIC", "CANAL", "MAIN"], "cor": "r" if tem(v, "vermelh") else "c"}
    if tem(v, "ao contrário"):
        o["reverso"] = True
    return o


def palco(v):
    if tem(v, "bateria", r"\btom\b", "prato"):
        return [{"t": "bateria", "vazamento": tem(v, "vaza")}]
    if tem(v, "fone", "in-ear"):
        return [{"t": "fones"}]
    if tem(v, "plateia", "sala", "parede"):
        return [{"t": "sala", "paredes": tem(v, "parede", "batendo")}]
    if tem(v, r"\bcaixa", "monitor", r"\bsub\b"):
        return [{"t": "caixa", "x": 540, "y": 1030, "label": "", "apagada": tem(v, "apagad")}]
    tipo = "condensador" if tem(v, "condensador") else ("fita" if tem(v, "fita") else "dinamico")
    return [{"t": "mic", "tipo": tipo, "ondas": not tem(v, "mudo", "apagad")}]


def knobs(v):
    ls = [x.strip() for x in re.findall(r"KNOBs?\s+([A-ZÀ-Ú][A-ZÀ-Ú0-9()]*(?:\s[A-ZÀ-Ú][A-ZÀ-Ú()]+)?)", v)][:3]
    ls = [l for l in ls if l not in ("DE", "DO", "DA")] or ["NÍVEL"]
    sobe = not tem(v, "desc", "volta", "menos")
    if len(ls) == 1:
        return [{"t": "knob", "x": 540, "y": 1060, "r": 170, "label": ls[0][:12], "v0": .25 if sobe else .75, "v1": .7 if sobe else .35}]
    xs = {2: (300, 780), 3: (200, 540, 880)}[len(ls)]
    return [{"t": "knob", "x": x, "y": 1040, "r": 120 if len(ls) == 2 else 100, "label": l[:12], "v0": .3, "v1": .65, "lsize": 34,
             "cor": "cag"[k], "at": .3 + .15 * k} for k, (x, l) in enumerate(zip(xs, ls))]


def cena(v):
    c = []
    if "QUIZ" in v and q(v):
        ops = [x for x in q(v) if len(x.split()) <= 3][:3]
        o = {"t": "quiz", "ops": ops}
        if tem(v, "acende verde", "verde"):
            certa = next((k for k, x in enumerate(ops) if x in v.upper().split("'")[-2:]), len(ops) - 1)
            o.update(ops=[ops[certa]], certa=0, revela=True)
        return [o]
    if "CÍRCULOS" in v:
        sep = tem(v, "afast", "lado a lado", "encost")
        o = {"t": "circulos", "estados": [[350, 170, 730, 200]] if sep else [[440, 190, 650, 220]]}
        if tem(v, "verde"):
            o.update(verde=True, verde_at=.15)
        if tem(v, "amarel", "sobreposi"):
            o["sobre_amarelo"] = True
        return [o]
    if tem(v, "repetições"):
        n = 8 if tem(v, "empilhad", "muitas", "sobrepost") else 3
        return [{"t": "ecos", "estados": [{"n": n, "dec": .95 if n == 8 else .6, "fora": tem(v, "fora")}], "vermelho": tem(v, "vermelh")}]
    if "CHECKLIST" in v:
        m = re.search(r"item (\d)", v)
        n = 4 if tem(v, r"\b4\b") else 3
        c.append({"t": "passos", "n": max(n, int(m.group(1)) if m else 1), "atual": int(m.group(1)) - 1 if m else 0})
    if "TELA" in v:
        return c + [tela(v)]
    if "CAMINHO" in v:
        return [caminho(v)]
    if "MESA" in v:
        return c + [mesa(v)]
    if "CANAL" in v and not c:
        return [canal(v)]
    if "KNOB" in v:
        return knobs(v)
    if "FADER" in v and "MEDIDOR" in v:
        return [{"t": "fader", "x": 330, "top": 760, "h": 520, "label": "FADER", "v0": .4, "v1": .8, "w": 110},
                {"t": "meter", "x": 700, "top": 760, "h": 520, "w": 90, "lo": .3, "hi": .7}]
    if "FADER" in v:
        d = tem(v, "desc")
        return [{"t": "fader", "x": 560, "top": 720, "h": 600, "label": "FADER", "v0": .85 if d else .35, "v1": .35 if d else .85, "w": 150}]
    if "MEDIDOR" in v:
        return c + [{"t": "meter", "x": 490, "top": 740, "h": 540, "w": 100, "lo": .8 if tem(v, "vermelh") else .3,
                     "hi": 1 if tem(v, "vermelh") else .65, "clip": tem(v, "vermelh", "CLIP")}]
    return c + palco(v)


def gerar_spec(r, tema):
    cs = []; n = len(r["cenas"])
    for k, c in enumerate(r["cenas"]):
        v = c.get("visual", "")
        if k == n - 1:
            cs.append({"c": [{"t": "cta"}]}); continue
        if "PRODUTO" in v:
            cs.append({"c": [{"t": "produto"}]}); continue
        d = {"c": cena(v)}
        p = pill(v)
        if p:
            d["pill"] = p
        cs.append(d)
    return {"tema": tema, "auto": True, "cenas": cs}


def teste():
    r = {"cenas": [{"visual": "CANAL com o KNOB GAIN girando; PÍLULA vermelha 'VOZ BAIXA'"},
                   {"visual": "TELA com a faixa de 2 a 4 kHz em amarelo"}, {"visual": "CAMINHO: MIC → GAIN → EQ, linha ciano"},
                   {"visual": "QUIZ: cartões 'CABO RUIM', 'FALTA PHANTOM'"}, {"visual": "PALCO: bateria com vazamento"},
                   {"visual": "PRODUTO no centro"}, {"visual": "CTA"}]}
    s = gerar_spec(r, "c")["cenas"]
    assert s[0]["c"][0]["t"] == "canal" and s[0]["pill"] == ["VOZ BAIXA", "r"]
    assert s[1]["c"][0]["faixa"] == [2000, 4000]
    assert s[2]["c"][0]["blocos"] == ["MIC", "GAIN", "EQ"]
    assert s[3]["c"][0]["ops"] == ["CABO RUIM", "FALTA PHANTOM"]
    assert s[4]["c"][0]["t"] == "bateria" and s[5]["c"][0]["t"] == "produto" and s[6]["c"][0]["t"] == "cta"
    print("teste ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["--teste"]:
        teste(); sys.exit()
    d = Path(sys.argv[1]); sp = d / "spec.json"
    if sp.exists() and "--forca" not in sys.argv and not json.loads(sp.read_text()).get("auto"):
        sys.exit(f"{sp} feito à mão: não sobrescrevo (use --forca)")
    sp.write_text(json.dumps(gerar_spec(json.loads((d / "roteiro.json").read_text()), sys.argv[2]), ensure_ascii=False, indent=1))
