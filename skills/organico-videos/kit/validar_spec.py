#!/usr/bin/env python3
"""Valida o spec.json de um ou mais vídeos e, se passar, grava spec.ok na pasta (o lote só produz vídeo com spec.ok).

Uso: python3 validar_spec.py 011 012 ...        (roda de qualquer pasta; os vídeos ficam em ../videos/NNN)
     python3 validar_spec.py --teste
Confere: nº de cenas igual ao roteiro, última cena = cta, uma peça grande por cena, peças de lado com pos e/d diferentes,
gera as cenas (gerar_cenas.py) sem erro e sem AVISO (mais de 9 palavras na tela ou pílula que não coube).
"""
import json, os, subprocess, sys
from pathlib import Path

KIT = Path(__file__).resolve().parent; V = Path(os.environ.get("ORG_RAIZ", KIT.parent)).resolve() / "videos"
GRANDE = {"canal", "mesa", "tela", "caminho", "quiz", "circulos", "ecos", "sala", "barras", "bateria", "produto", "cta", "cauda",
          "lista", "bolo", "pa", "tecla", "fones", "cabo"}
LADO = {"knob", "fader", "meter", "gr", "mic", "caixa", "porta", "aparelho", "roteador", "pessoa", "icone", "retorno"}
LIVRE = {"passos", "seta", "ruido", "onda", "laco", "balao"}
SEM_PASSOS = {"canal"}  # peças que sobem até onde ficam os passos (y 630)


def regras(rot, spec):
    e = []
    cs = spec.get("cenas", [])
    if spec.get("auto"):
        e.append('spec ainda é o automático: reescreva as cenas e tire a chave "auto"')
    if len(cs) != len(rot["cenas"]):
        return e + [f"spec tem {len(cs)} cenas, roteiro tem {len(rot['cenas'])}"]
    for n, sp in enumerate(cs, 1):
        ps = sp.get("c") or []; ts = [x.get("t") for x in ps]
        if not ps:
            e.append(f"cena {n}: sem peça"); continue
        if n == len(cs) and ts != ["cta"]:
            e.append(f"cena {n}: a última cena tem que ser só [{{\"t\":\"cta\"}}]")
        if n == len(cs) and rot.get("curso") is False and not ps[0].get("icone"):  # lote 2: informativo não mostra o curso
            e.append(f"cena {n}: vídeo informativo: o cta precisa de \"icone\" (comenta|salva|marca|segue)")
        desc = [t for t in ts if t not in GRANDE | LADO | LIVRE]
        if desc:
            e.append(f"cena {n}: peça desconhecida {desc}")
        g = [t for t in ts if t in GRANDE]
        if len(g) > 1 and set(g) != {"cabo"}:
            e.append(f"cena {n}: {g} são peças grandes; use só uma por cena")
        lados = [x for x in ps if x.get("t") in LADO and "x" not in x]
        if g and lados:
            e.append(f"cena {n}: peça grande {g} não divide a cena com {[x['t'] for x in lados]}")
        pos = [x.get("pos", "c") for x in lados]
        if len(lados) >= 2 and ("c" in pos or len(set(pos)) < len(pos)):
            e.append(f"cena {n}: duas peças de lado precisam de pos diferentes (\"e\" e \"d\"); veio {pos}")
        if len(lados) > 2:
            e.append(f"cena {n}: no máximo 2 peças de lado")
        if "passos" in ts and SEM_PASSOS & set(ts):
            e.append(f"cena {n}: passos não cabe junto com {sorted(SEM_PASSOS & set(ts))}")
        if any(x.get("t") == "mic" and x.get("cardioide") for x in ps) and "passos" in ts:
            e.append(f"cena {n}: microfone com cardioide não cabe junto com passos")
        p = sp.get("pill")
        if p and (len(p) != 2 or p[1] not in "rga"):
            e.append(f"cena {n}: pill = [\"TEXTO\", \"r\"|\"g\"|\"a\"]")
    return e


def valida(nome):
    d = V / nome; ok = d / "spec.ok"
    try:
        rot = json.loads((d / "roteiro.json").read_text()); spec = json.loads((d / "spec.json").read_text())
    except Exception as ex:
        return [f"não li roteiro/spec: {ex}"]
    e = regras(rot, spec)
    if not e:
        p = subprocess.run([sys.executable, str(KIT / "gerar_cenas.py"), "."], cwd=d, capture_output=True, text=True)
        if p.returncode:
            e.append("gerar_cenas falhou: " + (p.stderr.strip().splitlines() or ["?"])[-1][:200])
        e += [l[6:] for l in p.stdout.splitlines() if l.startswith("AVISO ")]
        if not e and any("{C[" in f.read_text() for f in (d / "cenas").glob("*.html")):
            e.append("sobrou {C[...]} no HTML (erro do kit: avise)")
    if e:
        ok.unlink(missing_ok=True)
    else:
        ok.write_text("ok\n")
    return e


def teste():
    rot = {"cenas": [{}, {}, {}]}
    bom = {"cenas": [{"c": [{"t": "knob", "pos": "e"}, {"t": "fader", "pos": "d"}]}, {"c": [{"t": "passos"}, {"t": "mesa"}]}, {"c": [{"t": "cta"}]}]}
    assert regras(rot, bom) == [], regras(rot, bom)
    ruim = {"auto": True, "cenas": [{"c": [{"t": "mesa"}, {"t": "tela"}]}, {"c": [{"t": "knob"}, {"t": "fader"}]}, {"c": [{"t": "produto"}]}]}
    r = regras(rot, ruim)
    assert len(r) == 4 and "automático" in r[0] and "peças grandes" in r[1] and "pos diferentes" in r[2] and "última" in r[3], r
    assert regras(rot, {"cenas": [{"c": [{"t": "passos"}, {"t": "canal"}]}, {"c": []}, {"c": [{"t": "cta"}]}]})[0].startswith("cena 1: passos")
    info = dict(rot, curso=False)
    assert any("icone" in x for x in regras(info, bom)) and not regras(info, {"cenas": bom["cenas"][:2] + [{"c": [{"t": "cta", "icone": "salva"}]}]})
    print("teste ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["--teste"]:
        teste(); sys.exit()
    falhou = 0
    for nome in sys.argv[1:]:
        e = valida(f"{int(nome):03d}")
        print(f"{int(nome):03d} " + ("OK (spec.ok gravado)" if not e else "FALHOU"))
        for x in e:
            print("   -", x)
        falhou += bool(e)
    sys.exit(1 if falhou else 0)
