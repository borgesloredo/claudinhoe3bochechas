#!/usr/bin/env python3
"""Carrossel de lista para Instagram: valida o roteiro, gera os prompts das imagens,
monta os slides (1080x1350) e escreve a legenda de cada rede.

Uso (PASTA = pasta de um carrossel, com roteiro.json e as imagens IMG1.png, IMG2.png...):
  python3 carrossel.py validar PASTA [PASTA...]
  python3 carrossel.py prompts PASTA [--slide-inteiro]
  python3 carrossel.py gerar PASTA
  python3 carrossel.py legenda PASTA
  python3 carrossel.py tudo PASTA          # validar + gerar + legenda
  python3 carrossel.py --teste             # autoteste rápido
A config (perfil, cores, link, palavras proibidas) fica em PASTA/../config.json ou em --config ARQUIVO.
"""
import json, re, sys
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
FONTES = SKILL / "fontes"
W, H, M = 1080, 1350, 80  # tamanho 4:5 do Instagram e margem lateral

CONFIG_PADRAO = {
    "perfil": "@seuperfil",
    "nicho": "seu nicho",
    "cores": {"fundo": "#16110E", "destaque": "#F5A623", "texto": "#FBF3E8", "texto_suave": "#D8CCBE"},
    "link": "https://seusite.com.br/",
    "link_oferta": "https://seusite.com.br/",
    "palavra_ponte": "curso",
    "proibidas": [],
    "estilo_imagem": ("STYLE: semi-realistic editorial digital painting with a subtle colored-pencil texture, warm "
                      "saturated colors, dramatic cinematic lighting, realistic anatomy; not a cartoon, not a photo. "
                      "Any product or equipment shown is generic and unbranded."),
}
FORMATOS = {f"F{i}" for i in range(1, 11)}
TONS = {"negativo", "comico", "neutro", "orgulho"}
IMG_EXT = (".png", ".jpg", ".jpeg", ".webp")


def carregar(pasta, config_arq=None):
    pasta = Path(pasta)
    d = json.loads((pasta / "roteiro.json").read_text(encoding="utf-8"))
    cfg = json.loads(json.dumps(CONFIG_PADRAO))
    arq = Path(config_arq) if config_arq else pasta.parent / "config.json"
    if arq.exists():
        user = json.loads(arq.read_text(encoding="utf-8"))
        cfg["cores"].update(user.pop("cores", {}))
        cfg.update(user)
    return d, cfg


def troca_perfil(t, cfg):
    return (t or "").replace("{perfil}", cfg["perfil"])


def palavras(s):
    return len((s or "").replace("*", "").split())


def fonte_cobre(ch):
    """Latin + pontuação geral: o que as fontes da skill têm. Emoji e setas viram quadradinho."""
    o = ord(ch)
    return o < 0x250 or 0x2000 <= o <= 0x206F or ch in "€™−"


# ---------------------------------------------------------------- validar
def checar(d, cfg):
    e = []
    if d.get("formato") not in FORMATOS: e.append("formato deve ser F1..F10")
    if d.get("tipo") not in {"info", "ponte"}: e.append("tipo deve ser info ou ponte")
    if d.get("tom") not in TONS: e.append(f"tom deve ser um de {sorted(TONS)}")
    if palavras(d.get("titulo_capa")) > 14: e.append("titulo_capa com mais de 14 palavras")
    imgs = d.get("imagens") or []
    refs = [i.get("ref") for i in imgs]
    if refs[:2] != ["IMG1", "IMG2"]: e.append("IMG1 (capa) e IMG2 (fundo) são obrigatórias, nessa ordem")
    if len(imgs) > 6: e.append("mais de 6 imagens")
    for i in imgs:
        if palavras(i.get("prompt")) < 15: e.append(f"{i.get('ref')}: prompt curto (mín. 15 palavras)")
    sl = d.get("slides") or []
    if not 6 <= len(sl) <= 10: e.append(f"{len(sl)} slides (use 6 a 10)")
    lim = 90 if d.get("formato") == "F9" else 34
    for k, s in enumerate(sl, 1):
        if s.get("n") != k: e.append(f"slide {k}: n fora de ordem")
        if s.get("imagem") not in refs: e.append(f"slide {k}: imagem {s.get('imagem')} não existe em imagens")
        if palavras(s.get("titulo")) > 9: e.append(f"slide {k}: titulo com mais de 8 palavras")
        if palavras(s.get("texto")) > lim: e.append(f"slide {k}: texto com mais de {lim} palavras")
    texto = " ".join([d.get("titulo_capa", ""), d.get("legenda", "")] +
                     [f"{s.get('rotulo', '')} {s.get('titulo', '')} {s.get('texto', '')}" for s in sl])
    ruins = sorted({c for c in texto if not fonte_cobre(c)})
    if ruins: e.append(f"caracteres que a fonte não tem (emoji, seta?): {' '.join(ruins)}")
    baixo = json.dumps(d, ensure_ascii=False).lower()
    achou = [p for p in cfg["proibidas"] if re.search(rf"\b{re.escape(p.lower())}\b", baixo)]
    if achou: e.append(f"palavra proibida (marca/modelo?): {achou}")
    ultimo = json.dumps(sl[-1:], ensure_ascii=False).lower()
    if d.get("tipo") == "ponte" and cfg["palavra_ponte"].lower() not in ultimo:
        e.append(f"ponte sem '{cfg['palavra_ponte']}' no último slide")
    if d.get("tipo") == "info" and re.search(r"\b(dm|direct)\b", ultimo):
        e.append("info prometendo envio por DM (só prometa se a automação existir)")
    if not 5 <= len(d.get("hashtags") or []) <= 8: e.append("use 5 a 8 hashtags")
    if not d.get("legenda"): e.append("sem legenda")
    return e


# ---------------------------------------------------------------- prompts
COMPOSICAO = {
    "capa": ("COMPOSITION: main character waist-up in the upper two-thirds, looking straight at the camera, sharp "
             "well-lit face, rich slightly blurred background; the lower third darker and clean with a gradient fading "
             "to near-black, left empty for a title."),
    "fundo": ("COMPOSITION: background for text slides; no character in focus, elements pushed to the edges and "
              "blurred; darker and more sober than the cover; the top 60% of the frame is a calm, uniform, low-contrast "
              "area for text."),
}
COMPOSICAO_ITEM = ("COMPOSITION: subject clearly readable in the lower half; the top 45% darker, clean and empty for "
                   "text. Same palette and universe as the cover of this carousel.")
SEM_TEXTO = "ABSOLUTELY NO text, letters, numbers, logos, brand names or watermarks anywhere in the image."


def prompts(d, cfg, slide_inteiro=False):
    base = f"Vertical 4:5 image, 1080x1350 px, very high detail. {cfg['estilo_imagem']}"
    out = [f"# Prompts do carrossel {d.get('id', '')}: {d['titulo_capa']}\n"]
    if not slide_inteiro:
        out.append("Gere cada imagem e salve nesta pasta com o nome indicado (IMG1.png, IMG2.png...).\n")
        for i in d["imagens"]:
            comp = COMPOSICAO.get(i.get("uso"), COMPOSICAO_ITEM)
            out.append(f"## {i['ref']}.png ({i.get('uso', '')})\n\n```\n{i['prompt'].strip()} {base} {SEM_TEXTO} {comp}\n```\n")
        notas = [f"- slide {s['n']}: {s['grafico']}" for s in d["slides"] if s.get("grafico")]
        if notas:
            out.append("## Gráficos pedidos no roteiro\n\nO gerador local não desenha estes gráficos. "
                       "Vire lista no texto, ou use o modo --slide-inteiro.\n\n" + "\n".join(notas) + "\n")
        return "\n".join(out)
    # Modo B: a IA desenha o slide inteiro, com texto e gráfico. Confira letra por letra depois.
    c = cfg["cores"]
    cena = {i["ref"]: i["prompt"].strip() for i in d["imagens"]}
    n = len(d["slides"])
    for s in d["slides"]:
        tit = troca_perfil(s.get("titulo"), cfg).replace("*", "")
        txt = troca_perfil(s.get("texto"), cfg)
        partes = [cena[s["imagem"]], base, "Typography: bold modern sans-serif, perfectly spelled Brazilian Portuguese with all accents.",
                  f"Colors: background tone {c['fundo']}, accent {c['destaque']}, text {c['texto']}."]
        if s["n"] == 1:
            partes.append(f'Cover layout: huge condensed uppercase title in the lower third: "{tit}". Subtitle below: "{txt}". '
                          f'Small "ARRASTE" with an arrow at the bottom right.')
        else:
            if s.get("rotulo"): partes.append(f'Small letter-spaced label at the top in the accent color: "{s["rotulo"]}".')
            partes.append(f'Big title at the top: "{tit}". Body text below it: "{txt}".')
            if s.get("grafico"): partes.append(f"Simple flat vector diagram in the accent color, mid-frame: {s['grafico']}.")
            partes.append(f'Footer: "{cfg["perfil"]}" small at the bottom left and "{s["n"]}/{n}" at the bottom right.')
        partes.append("No logos, no brand names, no watermarks. Write only the text quoted above, nothing else.")
        out.append(f"## S{s['n']:02d}.png\n\n```\n{' '.join(partes)}\n```\n")
    return "\n".join(out)


# ---------------------------------------------------------------- gerar
def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def fonte(nome, tam):
    from PIL import ImageFont
    return ImageFont.truetype(str(FONTES / nome), tam)


def achar_imagem(pasta, ref):
    for ext in IMG_EXT:
        p = pasta / f"{ref}{ext}"
        if p.exists(): return p
    return None


def fundo(pasta, ref, cfg):
    from PIL import Image, ImageOps
    p = achar_imagem(pasta, ref)
    if p:
        return ImageOps.fit(Image.open(p).convert("RGB"), (W, H), Image.LANCZOS), True
    # Sem imagem: degradê da cor de fundo com um brilho leve da cor de destaque embaixo.
    f, a = rgb(cfg["cores"]["fundo"]), rgb(cfg["cores"]["destaque"])
    col = Image.new("RGB", (1, H))
    for y in range(H):
        t = (y / H) ** 2 * 0.22
        col.putpixel((0, y), tuple(int(f[i] * (1 - t) + a[i] * t) for i in range(3)))
    return col.resize((W, H)), False


def escurecer(img, cor, alfa_topo, alfa_base, de=0.0):
    """Véu da cor de fundo: transparente acima de `de`, depois vai de alfa_topo a alfa_base."""
    from PIL import Image
    col = Image.new("RGBA", (1, H))
    for y in range(H):
        t = y / H
        a = 0 if t < de else int(alfa_topo + (alfa_base - alfa_topo) * (t - de) / (1 - de))
        col.putpixel((0, y), cor + (a,))
    return Image.alpha_composite(img.convert("RGBA"), col.resize((W, H)))


def partes_destaque(texto):
    """'Pediram *mais volume*?' -> [(palavra, destaque?)]; o trecho entre asteriscos sai na cor de destaque."""
    out, ligado = [], False
    for k, pedaco in enumerate(texto.split("*")):
        ligado = k % 2 == 1
        out += [(w, ligado) for w in pedaco.split()]
    return out


def quebrar_rico(draw, texto, f, larg):
    linhas, atual = [], []
    for w, dest in partes_destaque(texto):
        teste = " ".join(x for x, _ in atual + [(w, dest)])
        if atual and draw.textlength(teste, font=f) > larg:
            linhas.append(atual); atual = []
        atual.append((w, dest))
    if atual: linhas.append(atual)
    return linhas


def quebrar(draw, texto, f, larg):
    linhas = []
    for par in texto.split("\n"):
        linhas += [" ".join(w for w, _ in l) for l in quebrar_rico(draw, par.replace("*", ""), f, larg)] or [""]
    return linhas


def caber_rico(draw, texto, nome, maior, menor, larg, max_linhas):
    for tam in range(maior, menor - 1, -4):
        f = fonte(nome, tam)
        ls = quebrar_rico(draw, texto, f, larg)
        if len(ls) <= max_linhas: return f, ls, tam
    return f, ls, tam


def caber(draw, texto, nome, maior, menor, larg, altura, entre=1.38):
    for tam in range(maior, menor - 1, -2):
        f = fonte(nome, tam)
        ls = quebrar(draw, texto, f, larg)
        if len(ls) * tam * entre <= altura: return f, ls, tam, True
    return f, ls, tam, False


def escrever_rico(draw, x, y, linhas, f, tam, cor, cor_dest, entre=1.08):
    esp = draw.textlength(" ", font=f)
    for l in linhas:
        cx = x
        for w, dest in l:
            draw.text((cx, y), w, font=f, fill=cor_dest if dest else cor)
            cx += draw.textlength(w, font=f) + esp
        y += int(tam * entre)
    return y


def espacado(draw, x, y, texto, f, cor, esp=6, direita=False):
    larg = sum(draw.textlength(c, font=f) + esp for c in texto) - esp
    if direita: x -= larg
    for c in texto:
        draw.text((x, y), c, font=f, fill=cor)
        x += draw.textlength(c, font=f) + esp
    return larg


def seta(draw, x, y, cor, tam=34, w=4):
    draw.line([(x, y), (x + tam, y)], fill=cor, width=w)
    draw.line([(x + tam - 12, y - 12), (x + tam, y), (x + tam - 12, y + 12)], fill=cor, width=w, joint="curve")


def icone_salvar(draw, x, y, cor, h=44):
    w = h * 0.72
    draw.line([(x, y + h), (x, y), (x + w, y), (x + w, y + h), (x + w / 2, y + h * 0.7), (x, y + h)], fill=cor, width=5, joint="curve")


def icone_enviar(draw, x, y, cor, h=44):
    draw.line([(x, y + h * 0.45), (x + h, y), (x + h * 0.62, y + h), (x + h * 0.42, y + h * 0.58), (x, y + h * 0.45)], fill=cor, width=5, joint="curve")
    draw.line([(x + h * 0.42, y + h * 0.58), (x + h, y)], fill=cor, width=4)


def rodape(draw, cfg, n, total):
    c = cfg["cores"]; f = fonte("PlusJakartaSans-500.ttf", 30)
    draw.text((M, H - 92), cfg["perfil"], font=f, fill=rgb(c["texto_suave"]))
    if total:
        t = f"{n}/{total}"
        draw.text((W - M - draw.textlength(t, font=f), H - 92), t, font=f, fill=rgb(c["texto_suave"]))


def slide_capa(pasta, d, s, cfg):
    from PIL import ImageDraw
    c = cfg["cores"]
    img, _ = fundo(pasta, s["imagem"], cfg)
    img = escurecer(img, rgb(c["fundo"]), 0, 245, de=0.45)
    dr = ImageDraw.Draw(img)
    larg = W - 2 * M
    titulo = troca_perfil(s.get("titulo") or d["titulo_capa"], cfg).upper()
    ft, lt, tt = caber_rico(dr, titulo, "Anton-Regular.ttf", 150, 84, larg, 3)
    sub = troca_perfil(s.get("texto"), cfg)
    fs, ls, ts, _ = caber(dr, sub, "PlusJakartaSans-700.ttf", 46, 34, larg, 140, 1.3) if sub else (None, [], 0, True)
    base = H - 140                                  # acima do rodapé
    y_sub = base - int(len(ls) * ts * 1.3)
    y_tit = y_sub - 18 - int(len(lt) * tt * 1.04)
    dr.rectangle([M, y_tit - 44, M + 130, y_tit - 30], fill=rgb(c["destaque"]))
    escrever_rico(dr, M, y_tit, lt, ft, tt, rgb(c["texto"]), rgb(c["destaque"]), 1.04)
    for i, l in enumerate(ls):
        dr.text((M, y_sub + int(i * ts * 1.3)), l, font=fs, fill=rgb(c["texto"]))
    rodape(dr, cfg, 1, 0)
    f = fonte("PlusJakartaSans-800.ttf", 28)
    lw = espacado(dr, W - M - 50, H - 90, "ARRASTE", f, rgb(c["texto_suave"]), 5, direita=True)
    seta(dr, W - M - 36, H - 74, rgb(c["texto_suave"]))
    return img.convert("RGB"), lt and y_tit - 44 > H * 0.35


def slide_conteudo(pasta, d, s, cfg, total):
    from PIL import ImageDraw
    c = cfg["cores"]
    img, tem_img = fundo(pasta, s["imagem"], cfg)
    if tem_img: img = escurecer(img, rgb(c["fundo"]), 235, 120)
    dr = ImageDraw.Draw(img)
    larg, y = W - 2 * M, 110
    final = s["n"] == total
    if s.get("rotulo"):
        espacado(dr, M, y, troca_perfil(s["rotulo"], cfg).upper(), fonte("PlusJakartaSans-800.ttf", 32), rgb(c["destaque"]), 7)
        y += 64
    ft, lt, tt = caber_rico(dr, troca_perfil(s.get("titulo"), cfg), "PlusJakartaSans-800.ttf", 86, 52, larg, 4)
    y = escrever_rico(dr, M, y, lt, ft, tt, rgb(c["texto"]), rgb(c["destaque"]), 1.1) + 36
    limite = H - (430 if final else 150)            # o slide final reserva espaço para ícones e botão
    ok = True
    if s.get("texto"):
        fb, lb, tb, ok = caber(dr, troca_perfil(s["texto"], cfg), "PlusJakartaSans-500.ttf", 46, 26, larg, limite - y)
        for l in lb:
            dr.text((M, y), l, font=fb, fill=rgb(c["texto_suave"])); y += int(tb * 1.38)
    if final:
        y += 40; fi = fonte("PlusJakartaSans-700.ttf", 40); cor = rgb(c["destaque"])
        icone_salvar(dr, M, y, cor); dr.text((M + 60, y - 2), "Salve", font=fi, fill=cor)
        x2 = M + 60 + dr.textlength("Salve", font=fi) + 80
        icone_enviar(dr, x2, y, cor); dr.text((x2 + 64, y - 2), "Envie", font=fi, fill=cor)
        y += 110; fp = fonte("PlusJakartaSans-800.ttf", 42); t = f"Siga {cfg['perfil']}"
        lp = dr.textlength(t, font=fp)
        dr.rounded_rectangle([M, y, M + lp + 80, y + 92], radius=46, fill=cor)
        dr.text((M + 40, y + 20), t, font=fp, fill=rgb(c["fundo"]))
    rodape(dr, cfg, s["n"], total)
    return img.convert("RGB"), ok


def gerar(pasta, d, cfg):
    pasta = Path(pasta); saida = pasta / "slides"; saida.mkdir(exist_ok=True)
    total, avisos, faltam = len(d["slides"]), [], set()
    for s in d["slides"]:
        if not achar_imagem(pasta, s["imagem"]): faltam.add(s["imagem"])
        img, ok = slide_capa(pasta, d, s, cfg) if s["n"] == 1 else slide_conteudo(pasta, d, s, cfg, total)
        if not ok: avisos.append(f"S{s['n']:02d}: texto não coube no tamanho mínimo, encurte")
        img.save(saida / f"S{s['n']:02d}.png")
    if faltam: avisos.append(f"sem imagem (usei degradê): {', '.join(sorted(faltam))}")
    return saida, avisos


# ---------------------------------------------------------------- legenda
def perfil_link(t): return t.replace("link da bio", "link do perfil")


def youtube(t):
    """YouTube não marca amigo: 'marca o X' vira 'manda pro X'; o link fica na descrição do canal."""
    t = t.replace("link da bio", "link da descrição do canal")
    def troca(m):
        v = {"Marca": "Manda", "marca": "manda", "Marque": "Mande", "marque": "mande"}[m[1]]
        return f"{v} " + {"o": "pro", "a": "pra", "um": "pra um", "uma": "pra uma", "quem": "pra quem"}[m[2]]
    return re.sub(r"\b(Marca|marca|Marque|marque) (o|a|um|uma|quem)\b", troca, t)


def pinterest(d, cfg):
    """O Pin mostra só a capa: sem o CTA de comentar/marcar, o gesto é salvar. Descrição até 500 caracteres."""
    linhas = d["legenda"].split("\n")[:-1] or d["legenda"].split("\n")
    tags = " ".join(d["hashtags"][:3])
    desc = " ".join(linhas + ["Salve este Pin para consultar depois."]).replace("No carrossel:", "Neste guia:")
    if len(desc) + len(tags) + 2 > 500:
        desc = desc[:497 - len(tags) - 2].rsplit(" ", 1)[0] + "…"
    link = cfg["link_oferta"] if d["tipo"] == "ponte" else cfg["link"]
    t = d["titulo_capa"].replace("*", "")
    return f"Título: {t if len(t) <= 100 else t[:99].rstrip() + '…'}\nDescrição:\n{desc}\n\n{tags}\nLink: {link}"


def legenda(d, cfg):
    leg, tags = troca_perfil(d["legenda"], cfg), d["hashtags"]
    d = dict(d, legenda=leg)
    n = len(d["slides"])
    fb = leg.replace("link da bio", cfg["link_oferta"])  # página do Facebook não tem link na bio
    return f"""TÍTULO
{d['titulo_capa'].replace('*', '')}

IMAGENS
{n} slides: slides/S01.png (capa) até slides/S{n:02d}.png, nessa ordem.

INSTAGRAM (carrossel, corte 4:5)
{leg}

{' '.join(tags[:5])}

TIKTOK (carrossel de fotos)
{perfil_link(leg)}

{' '.join(tags[:5])}

KWAI (fotos)
{perfil_link(leg)}

{' '.join(tags[:4])}

PINTEREST (pin da capa: slides/S01.png)
{pinterest(d, cfg)}

YOUTUBE (postagem com imagens)
{youtube(leg)}

{' '.join(tags[:3])}

FACEBOOK (post com fotos)
{fb}

{' '.join(tags[:3])}
"""


# ---------------------------------------------------------------- autoteste
def teste():
    assert youtube("Comenta e marca o amigo que é o nº 3.") == "Comenta e manda pro amigo que é o nº 3."
    assert youtube("Marque quem esquece.") == "Mande pra quem esquece."
    assert partes_destaque("Pediram *mais volume*?") == [("Pediram", False), ("mais", True), ("volume", True), ("?", False)]
    assert palavras("um *dois* três") == 3
    assert not fonte_cobre("\U0001F525") and fonte_cobre("ç") and fonte_cobre("“")
    cfg = json.loads(json.dumps(CONFIG_PADRAO)); cfg["proibidas"] = ["marcax"]
    d = {"formato": "F1", "tipo": "info", "tom": "neutro", "titulo_capa": "T", "legenda": "A.\nB.\nComenta.",
         "hashtags": ["#a", "#b", "#c", "#d", "#e"], "imagens": [{"ref": "IMG1", "prompt": "x " * 15}, {"ref": "IMG2", "prompt": "x " * 15}],
         "slides": [{"n": k, "imagem": "IMG2", "titulo": "t", "texto": "x"} for k in range(1, 7)]}
    assert checar(d, cfg) == [], checar(d, cfg)
    d["slides"][-1]["texto"] = "Peça no DM com a MarcaX 🔥"
    e = " | ".join(checar(d, cfg))
    assert "DM" in e and "proibida" in e and "fonte" in e, e
    p = pinterest(d, cfg)
    assert "Comenta" not in p and p.endswith(cfg["link"])
    print("ok")


def main():
    a = sys.argv[1:]
    if not a or a[0] in {"-h", "--help"}: print(__doc__); return 0
    if a[0] == "--teste": teste(); return 0
    cfg_arq = a[a.index("--config") + 1] if "--config" in a else None
    cmd, pastas = a[0], [x for x in a[1:] if not x.startswith("--") and x != cfg_arq]
    falhou = False
    for pasta in pastas:
        d, cfg = carregar(pasta, cfg_arq)
        nome = Path(pasta).name
        if cmd in {"validar", "tudo"}:
            e = checar(d, cfg)
            print(f"{nome}: " + ("ok" if not e else "FALHA\n  - " + "\n  - ".join(e)))
            if e: falhou = True; continue
        if cmd == "prompts":
            arq = Path(pasta) / ("prompts-slide-inteiro.md" if "--slide-inteiro" in a else "prompts.md")
            arq.write_text(prompts(d, cfg, "--slide-inteiro" in a), encoding="utf-8"); print(f"{nome}: {arq}")
        if cmd in {"gerar", "tudo"}:
            saida, avisos = gerar(pasta, d, cfg)
            print(f"{nome}: {len(d['slides'])} slides em {saida}")
            for av in avisos: print(f"  AVISO {av}")
        if cmd in {"legenda", "tudo"}:
            arq = Path(pasta) / "legenda.txt"; arq.write_text(legenda(d, cfg), encoding="utf-8"); print(f"{nome}: {arq}")
    return 1 if falhou else 0


if __name__ == "__main__":
    sys.exit(main())
