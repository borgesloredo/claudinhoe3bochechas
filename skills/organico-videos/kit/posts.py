#!/usr/bin/env python3
"""Gera videos/<id>.txt de cada vídeo: título, legenda e hashtags para Instagram, TikTok, Kwai e YouTube Shorts.
A legenda parte de legenda_post do roteiro e termina com o CTA que o vídeo fala (última cena).
Só o Instagram promete mandar algo no direct (exige auto-DM, ex.: ManyChat); nas outras redes o CTA fica sem essa promessa.
Uso: python3 posts.py [--teste]"""
import json, re, sys
from pathlib import Path

V = Path(__file__).resolve().parent.parent / "videos"
# Trocas pontuais por vídeo, se precisar: TITULO = {12: "novo título"}; TROCA = {12: [("frase antiga", "frase nova")]}
TITULO = {}
TROCA = {}


def frases(t):
    return [f for f in re.split(r"(?<=[.!?])\s+", t.strip()) if f]


def chave(cta):
    """palavra-chave do 'Comenta X' em maiúscula, como no auto-DM."""
    return re.sub(r"^Comenta (?!(?:o|a|se|qual|aqui)\b)(\w+)(?=[ .])", lambda m: "Comenta " + m.group(1).upper(), cta)


def sem_dm(cta):
    """CTA para TikTok e Kwai: sem a promessa de mandar curso ou link no direct."""
    cta = re.sub(r"\s+que eu te mando .*$", ".", cta)
    return re.sub(r"^Envia no direct pr([ao]) ", r"Manda pr\1 ", cta)


def youtube(cta):
    """No YouTube não dá para marcar alguém nem mandar direct, e 'seguir' é 'se inscrever'."""
    cta = sem_dm(cta)
    cta = re.sub(r"^Marca (aqui )?(o |a )", lambda m: "Manda pr" + m.group(2), cta)
    cta = re.sub(r"^Marca (aqui )?", "Manda pra ", cta)
    return re.sub(r"^Segue pr", "Se inscreve pr", cta)


def post(n, r):
    lp = r["legenda_post"]
    tags = re.findall(r"#\w+", lp)
    corpo = re.sub(r"\s*#\w+", "", lp).strip()
    for a, b in TROCA.get(n, []):
        corpo = corpo.replace(a, b)
    segue = "Me segue antes, senão a mensagem não chega."  # lote 2: só vale onde há auto-DM (Instagram)
    fs = [f for f in frases(corpo) if f != segue]
    if re.match(r"(Comenta|Salva|Marca|Segue|Envia)\b", fs[-1]):  # o CTA antigo sai; entra o que o vídeo fala
        fs = fs[:-1]
    cta = chave(r["cenas"][-1]["fala"].strip())
    ig = cta + (" " + segue if "te mando" in cta else "")  # auto-DM só chega para quem segue
    base = " ".join(fs)
    titulo = TITULO.get(n, r["nome"])
    tags = tags[:5]
    tt = tags[:4] + ["#aprendanotiktok"]
    yt_titulo = (titulo if len(titulo) <= 90 else titulo[:89].rstrip() + "…") + " #Shorts"
    return f"""TÍTULO
{titulo}

INSTAGRAM (Reels)
{base} {ig}

{' '.join(tags)}

TIKTOK
{base} {sem_dm(cta)}

{' '.join(tt)}

KWAI
{base} {sem_dm(cta)}

{' '.join(tags[:4])}

YOUTUBE SHORTS
Título: {yt_titulo}
Descrição:
{base} {youtube(cta)}

#Shorts {' '.join(tags[:2])}
"""


def teste():
    assert sem_dm("Comenta FILTRO que eu te mando o link do curso.") == "Comenta FILTRO."
    assert sem_dm("Envia no direct pra quem opera sozinho.") == "Manda pra quem opera sozinho."
    assert youtube("Marca aqui quem opera o som com você.") == "Manda pra quem opera o som com você."
    assert youtube("Marca o baixista da sua banda.") == "Manda pro baixista da sua banda."
    assert youtube("Marca aquele amigo que veio da analógica.") == "Manda pra aquele amigo que veio da analógica."
    assert youtube("Segue pra próxima dica.") == "Se inscreve pra próxima dica."
    assert sem_dm("Envia no direct pro vocal.") == "Manda pro vocal."
    assert chave("Comenta violão que eu te mando o link do curso.") == "Comenta VIOLÃO que eu te mando o link do curso."
    assert chave("Comenta o modelo da sua mesa.") == "Comenta o modelo da sua mesa."
    assert chave("Comenta se já mexeu.") == "Comenta se já mexeu."
    r = {"nome": "t", "legenda_post": "Dica. Comenta X que eu te mando o resumo. Me segue antes, senão a mensagem não chega. #a",
         "cenas": [{"fala": "Comenta passagem que eu te mando o resumo."}]}
    t = post(101, r)
    assert t.count("Me segue antes") == 1 and "Dica. Comenta PASSAGEM que eu te mando o resumo. Me segue antes" in t
    assert "Comenta PASSAGEM." in t.split("TIKTOK")[1]
    print("ok")


if __name__ == "__main__":
    if "--teste" in sys.argv:
        teste(); sys.exit()
    for d in sorted(V.glob("[0-9][0-9][0-9]")):
        r = json.loads((d / "roteiro.json").read_text())
        t = post(int(d.name), r)
        assert len(re.findall(r"#\w+", t.split("TIKTOK")[0])) <= 5
        (V / f"{r['id']}.txt").write_text(t)
    print("ok", len(list(V.glob("*.txt"))))
