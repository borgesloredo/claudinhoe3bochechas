#!/usr/bin/env python3
"""Gera o texto de publicação de cada rede (Instagram, TikTok, Kwai, YouTube Shorts, Facebook, Pinterest)
a partir de UM texto base. Só biblioteca padrão.

Texto base (.txt com estas chaves, uma por linha; TEXTO pode ter várias linhas) ou .json com as mesmas chaves:
    TÍTULO: O erro que estraga o seu som
    TEXTO: Corpo da legenda. Entrega valor e não repete o vídeo.
    CTA: Comenta MESA que eu te mando o guia.
    HASHTAGS: #audio #somaovivo #mesadesom #tecnicodesom #dicas #igreja
    LINK: https://seusite.com.br/

Regras por rede (vieram de erros reais):
- Instagram: no máximo 5 hashtags. "Comenta X que eu te mando Y" só se você tem resposta automática no direct
  (--auto-dm); com ela, pede para seguir antes (a mensagem para quem não segue cai em "pedidos").
  Link na legenda não é clicável: vira "Link na bio".
- TikTok e Kwai: nunca prometem mandar algo no direct (não há auto-DM): o CTA fica só "Comenta MESA.". 4 hashtags
  (+ a tag da rede, se você passar --tag-tiktok).
- YouTube Shorts: título até 100 caracteres com #Shorts; não dá para marcar alguém nem mandar direct;
  "Segue" vira "Se inscreve".
- Facebook (Reels): título vira a headline de cima; CTA sem direct; 3 hashtags.
- Pinterest: título até 100, descrição até 500; o gesto é salvar o Pin (CTA de comentar sai); link de destino.

Uso: textos_por_rede.py BASE... [--auto-dm] [--tag-tiktok "#aprendanotiktok"] [--saida PASTA]
     textos_por_rede.py --teste
Saída: <base>.redes.txt ao lado do base (ou em --saida). O publicar.py importa gerar() daqui.
"""
import argparse
import json
import re
import sys
from pathlib import Path

CHAVES = {"TITULO": "titulo", "TÍTULO": "titulo", "TEXTO": "texto", "CTA": "cta", "HASHTAGS": "hashtags", "LINK": "link"}
LIMITE = {"instagram": 2200, "tiktok": 2200, "kwai": 2000, "youtube": 5000, "facebook": 5000, "pinterest": 500}
SALVA = "Salva este Pin pra consultar depois."
SEGUE_ANTES = "Me segue antes, senão a mensagem não chega."
CTA_RE = re.compile(r"^(Comenta|Marca|Manda|Envia|Segue|Salva|Me segue|Se inscreve|Compartilha)\b")


def ler_base(caminho):
    p = Path(caminho)
    if p.suffix.lower() == ".json":
        d = json.loads(p.read_text(encoding="utf-8"))
        b = {CHAVES.get(k.upper(), k.lower()): v for k, v in d.items()}
    else:
        b, atual = {}, None
        for linha in p.read_text(encoding="utf-8").splitlines():
            m = re.match(r"^\s*(T[ÍI]TULO|TEXTO|CTA|HASHTAGS|LINK)\s*:\s*(.*)$", linha, re.I)
            if m:
                atual = CHAVES[m.group(1).upper()]
                b[atual] = m.group(2).strip()
            elif atual == "texto":
                b["texto"] += "\n" + linha
    b = {k: (v.strip() if isinstance(v, str) else v) for k, v in b.items()}
    if isinstance(b.get("hashtags"), str):
        b["hashtags"] = re.findall(r"#\w+", b["hashtags"])
    for k in ("titulo", "texto"):
        if not b.get(k):
            raise SystemExit(f"{p.name}: falta {k.upper()}")
    return {"titulo": b["titulo"], "texto": b["texto"], "cta": b.get("cta", ""), "hashtags": b.get("hashtags") or [],
            "link": b.get("link", "")}


def chave(cta):
    """Palavra do 'Comenta X' em maiúscula (é ela que a resposta automática procura)."""
    return re.sub(r"^Comenta (?!(?:o|a|os|as|se|qual|aqui|ai|aí|um|uma)\b)(\w+)", lambda m: "Comenta " + m.group(1).upper(), cta)


def sem_dm(cta):
    """Sem a promessa de mandar algo no direct (redes sem resposta automática)."""
    cta = re.sub(r"\s+(?:que|e) eu te mando\b.*$", ".", cta)
    return re.sub(r"^Envia no direct pr([ao]) ", r"Manda pr\1 ", cta)


def youtube_cta(cta):
    """No YouTube não dá para marcar alguém nem mandar direct, e 'seguir' é 'se inscrever'."""
    cta = sem_dm(cta)
    cta = re.sub(r"^Marca (aqui )?(o |a )", lambda m: "Manda pr" + m.group(2), cta)
    cta = re.sub(r"^Marca (aqui )?", "Manda pra ", cta)
    return re.sub(r"^(Me )?[Ss]egue pr", "Se inscreve pr", cta)


def corta(texto, limite):
    """Corta no fim da última frase que cabe."""
    if len(texto) <= limite:
        return texto
    fs = re.split(r"(?<=[.!?])\s+", texto)
    while fs and len(" ".join(fs)) > limite:
        fs.pop()
    return " ".join(fs) or texto[:limite - 1].rstrip() + "…"


def junta(*partes):
    return "\n\n".join(p for p in partes if p)


def gerar(b, auto_dm=False, tag_tiktok=""):
    """dict rede -> {titulo?, legenda, link?} a partir do texto base."""
    corpo, tags, link = b["texto"], b["hashtags"], b["link"]
    cta = chave(b["cta"])
    promete = bool(re.search(r"\b(?:que|e) eu te mando\b", cta))
    ig_cta = (cta + (" " + SEGUE_ANTES if promete else "")) if auto_dm else sem_dm(cta)
    t = b["titulo"]
    out = {
        "instagram": {"legenda": junta(f"{corpo} {ig_cta}".strip(), "Link na bio." if link else "", " ".join(tags[:5]))},
        "tiktok": {"legenda": junta(f"{corpo} {sem_dm(cta)}".strip(), " ".join(tags[:4] + ([tag_tiktok] if tag_tiktok else [])))},
        "kwai": {"legenda": junta(f"{corpo} {sem_dm(cta)}".strip(), " ".join(tags[:4]))},
        "youtube": {"titulo": (t if len(t) <= 91 else t[:90].rstrip() + "…") + " #Shorts",
                    "legenda": junta(f"{corpo} {youtube_cta(cta)}".strip(), link, " ".join(["#Shorts"] + tags[:2]))},
        "facebook": {"titulo": t, "legenda": junta(t, f"{corpo} {sem_dm(cta)}".strip(), link, " ".join(tags[:3]))},
    }
    fs = [f for f in re.split(r"(?<=[.!?])\s+", corpo.strip()) if f and not CTA_RE.match(f)]
    ptags = " ".join(tags[:3])
    out["pinterest"] = {"titulo": t if len(t) <= 100 else t[:99].rstrip() + "…",
                        "legenda": corta(" ".join(fs + [SALVA]), 500 - len(ptags) - 2) + ("\n\n" + ptags if ptags else ""),
                        "link": link}
    for rede, d in out.items():
        if len(d["legenda"]) > LIMITE[rede]:
            print(f"  aviso: {rede} passou de {LIMITE[rede]} caracteres ({len(d['legenda'])})", file=sys.stderr)
    return out


NOMES = {"instagram": "INSTAGRAM (Reels)", "tiktok": "TIKTOK", "kwai": "KWAI", "youtube": "YOUTUBE SHORTS",
         "facebook": "FACEBOOK (Reels)", "pinterest": "PINTEREST (Pin de vídeo)"}


def como_texto(b, redes):
    partes = [f"TÍTULO\n{b['titulo']}"]
    for rede, d in redes.items():
        linhas = [NOMES[rede]]
        if rede in ("youtube", "pinterest"):
            linhas.append(f"Título: {d['titulo']}")
            linhas.append("Descrição:")
        linhas.append(d["legenda"])
        if d.get("link") and rede == "pinterest":
            linhas.append(f"Link: {d['link']}")
        partes.append("\n".join(linhas))
    return "\n\n".join(partes) + "\n"


def teste():
    assert sem_dm("Comenta FILTRO que eu te mando o link.") == "Comenta FILTRO."
    assert sem_dm("Comenta MESA que eu te mando.") == "Comenta MESA."
    assert sem_dm("Envia no direct pra quem opera sozinho.") == "Manda pra quem opera sozinho."
    assert youtube_cta("Marca aqui quem opera o som com você.") == "Manda pra quem opera o som com você."
    assert youtube_cta("Marca o baixista da sua banda.") == "Manda pro baixista da sua banda."
    assert youtube_cta("Segue pra próxima dica.") == "Se inscreve pra próxima dica."
    assert chave("Comenta violão que eu te mando o resumo.") == "Comenta VIOLÃO que eu te mando o resumo."
    assert chave("Comenta o modelo da sua mesa.") == "Comenta o modelo da sua mesa."
    assert len(corta("Frase curta. " * 100, 50)) <= 50
    b = {"titulo": "O erro que estraga o seu som", "texto": "Ganho alto não é volume. Ajuste antes do fader.",
         "cta": "Comenta mesa que eu te mando o guia.", "hashtags": [f"#t{i}" for i in range(8)], "link": "https://exemplo.com.br/"}
    r = gerar(b, auto_dm=True, tag_tiktok="#aprendanotiktok")
    assert "Comenta MESA que eu te mando o guia. " + SEGUE_ANTES in r["instagram"]["legenda"]
    assert r["instagram"]["legenda"].count("#") == 5 and "Link na bio." in r["instagram"]["legenda"]
    assert "Comenta MESA." in r["tiktok"]["legenda"] and "te mando" not in r["tiktok"]["legenda"]
    assert r["tiktok"]["legenda"].endswith("#t3 #aprendanotiktok") and "te mando" not in r["kwai"]["legenda"]
    assert r["youtube"]["titulo"].endswith("#Shorts") and len(r["youtube"]["titulo"]) <= 100
    assert r["facebook"]["legenda"].startswith("O erro que estraga") and r["facebook"]["legenda"].count("#") == 3
    assert "Comenta" not in r["pinterest"]["legenda"] and SALVA in r["pinterest"]["legenda"] and len(r["pinterest"]["legenda"]) <= 500
    assert "te mando" not in gerar(b)["instagram"]["legenda"]  # sem auto-DM, o Instagram também não promete direct
    longo = dict(b, titulo="T" * 150, texto="Frase do corpo. " * 80)
    r = gerar(longo)
    assert len(r["youtube"]["titulo"]) <= 100 and len(r["pinterest"]["titulo"]) <= 100 and len(r["pinterest"]["legenda"]) <= 500
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "001.txt"
        p.write_text("TÍTULO: Teste\nTEXTO: Linha um.\nLinha dois.\nCTA: Segue pra próxima.\nHASHTAGS: #a #b\nLINK:\n")
        base = ler_base(p)
        assert base["texto"] == "Linha um.\nLinha dois." and base["hashtags"] == ["#a", "#b"] and base["link"] == ""
        txt = como_texto(base, gerar(base))
        assert "YOUTUBE SHORTS\nTítulo: Teste #Shorts" in txt and "Se inscreve pra próxima." in txt
    print("teste ok")


def main():
    if "--teste" in sys.argv:
        teste()
        return
    ap = argparse.ArgumentParser(description="Texto de cada rede a partir de um texto base.")
    ap.add_argument("bases", nargs="+")
    ap.add_argument("--auto-dm", action="store_true", help="o Instagram tem resposta automática no direct")
    ap.add_argument("--tag-tiktok", default="", help="tag extra só no TikTok, ex.: #aprendanotiktok")
    ap.add_argument("--saida")
    a = ap.parse_args()
    for caminho in a.bases:
        p = Path(caminho)
        b = ler_base(p)
        destino = (Path(a.saida) if a.saida else p.parent) / f"{p.stem}.redes.txt"
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(como_texto(b, gerar(b, a.auto_dm, a.tag_tiktok)), encoding="utf-8")
        print(f"ok {destino}")


if __name__ == "__main__":
    main()
