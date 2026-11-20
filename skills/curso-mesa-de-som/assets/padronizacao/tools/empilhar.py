"""Padrão de navegação da XR18 num deck reveal.js já pronto (aula e V2).

Seta para o lado muda de capítulo; seta para baixo anda dentro do capítulo. Para isso:
- cada capítulo vira uma pilha vertical (<section> sem atributos em volta), de `cap-N` até `quiz-N`
  (sem quiz-N: até o próximo cap-*, ou até um slide sem id, que são os extras soltos da V2);
- slides antes do primeiro cap-* e depois do último capítulo ficam soltos, como na XR18;
- pilhas já existentes que não abrem com cap-* (ex.: capa/sumário/como usar do Midas PRO) são desfeitas;
- `navigationMode: 'linear'` sai (o padrão do reveal é a navegação por pilhas).

Uso: python3 -I empilhar.py entrada.html saida.html
"""
import re
import sys

TOK = re.compile(r"<section\b[^>]*>|</section>")


def secoes_topo(h):
    """Devolve (ini, fim, inicio_do_bloco_slides) das <section> de topo dentro de <div class="slides">."""
    m = re.search(r'<div class="slides"[^>]*>', h)
    assert m, 'div.slides não encontrada'
    pos, d, topo, ini = m.end(), 0, [], None
    for t in TOK.finditer(h, pos):
        if t.group().startswith("</"):
            d -= 1
            assert d >= 0, f"</section> sobrando em {t.start()}"
            if d == 0:
                topo.append((ini, t.end()))
        else:
            if d == 0:
                # só conta seções que começam logo depois de outra (ou do div), com espaço/comentário no meio
                if topo:   # entre duas seções de topo só pode haver espaço/comentário; outra coisa = fim do bloco de slides
                    entre = h[topo[-1][1]:t.start()]
                    if re.sub(r"<!--.*?-->", "", entre, flags=re.S).strip():
                        break
                ini = t.start()
            d += 1
    assert d == 0, "seções desbalanceadas"
    return topo


def ident(h, a):
    m = re.match(r'<section\b([^>]*)>', h[a:])
    i = re.search(r'\bid="([^"]*)"', m.group(1))
    return i.group(1) if i else None


def filhos(h, a, b):
    """Seções filhas diretas de uma pilha (ini, fim) ou None se a seção não é pilha."""
    abre = re.match(r"<section\b[^>]*>", h[a:]).end() + a
    d, res, ini = 0, [], None
    for t in TOK.finditer(h, abre, b - len("</section>")):
        if t.group().startswith("</"):
            d -= 1
            if d == 0:
                res.append((ini, t.end()))
        else:
            if d == 0:
                ini = t.start()
            d += 1
    return res or None


def empilhar(h):
    topo = secoes_topo(h)
    itens = []   # lista de (ids, trechos) por slide-folha, em ordem
    for a, b in topo:
        fs = filhos(h, a, b)
        if fs and ident(h, fs[0][0]) and ident(h, fs[0][0]).startswith("cap-"):
            itens.append(("pilha", [ident(h, x) for x, _ in fs], [h[x:y] for x, y in fs]))
        elif fs:
            for x, y in fs:
                itens.append(("solto", [ident(h, x)], [h[x:y]]))
        else:
            itens.append(("solto", [ident(h, a)], [h[a:b]]))
    saida, k = [], 0
    while k < len(itens):
        tipo, ii, tt = itens[k]
        cap = re.fullmatch(r"cap-(\d+)", ii[0] or "")
        if tipo == "pilha" or not cap:
            saida.append(tt[0] if tipo == "solto" else "<section>" + "\n".join(tt) + "</section>")
            k += 1
            continue
        fim = f"quiz-{cap.group(1)}"
        grupo = [tt[0]]
        k += 1
        while k < len(itens):
            t2, i2, x2 = itens[k]
            if t2 == "pilha" or i2[0] is None or re.fullmatch(r"cap-\d+", i2[0]):
                break
            grupo.append(x2[0])
            k += 1
            if i2[0] == fim:
                break
        saida.append("<section>" + "\n".join(grupo) + "</section>")
    a0, b0 = topo[0][0], topo[-1][1]
    return h[:a0] + "\n".join(saida) + h[b0:]


# Seletores do próprio deck que só pegavam os slides do 1º nível (fila única). Com pilhas, o slide fica um nível abaixo.
# Troca exata e conferida (a biblioteca do reveal, minificada, não entra: ela já trata as pilhas).
SELETORES = [
    ("const secs = $$('.reveal .slides > section');", "const secs = $$('.reveal .slides section');"),   # LS9 fitTitles: mede com pilha e slide visíveis
    (".reveal .slides>section{padding:0!important;width:1280px", ".reveal .slides section{padding:0!important;width:1280px"),   # Axios32
    (".reveal .slides>section{width:1280px;height:720px;padding:0!important", ".reveal .slides section{width:1280px;height:720px;padding:0!important"),   # StudioLive AI
    (".reveal .slides>section{padding:0;width:1280px;height:720px;top:0}", ".reveal .slides section{padding:0;width:1280px;height:720px;top:0}"),   # WING
    (".reveal .slides > section { padding: 0; width: 1280px;", ".reveal .slides section { padding: 0; width: 1280px;"),   # Rivage
    (".reveal .slides>section.pnl", ".reveal .slides section.pnl"),   # Si, PM5D
    (".reveal .slides > section.pnl", ".reveal .slides section.pnl"),   # Ui24R
    (".reveal .slides>section{width:1280px;height:720px;padding:0;top:0;left:0;box-sizing:border-box}", ".reveal .slides section{width:1280px;height:720px;padding:0;top:0;left:0;box-sizing:border-box}"),   # Mackie DL (sem isto o slide dentro da pilha fica com altura 0 e some)
    ('.reveal .slides > section { width: 1280px; height: 720px; padding: 0; box-sizing: border-box; top: 0 !important; }', '.reveal .slides section { width: 1280px; height: 720px; padding: 0; box-sizing: border-box; top: 0 !important; }'),   # ZED-14 (sessão L, 18/11/2026: sem isto o slide da pilha fica com altura 0 e some)
    ("$$('.reveal .slides > section')", "$$('.reveal .slides section:not(:has(> section))')"),   # LS9, Series III (JS)
]


ESTILO = ("<style>/* navegação por capítulos (06/11/2026): o invólucro da pilha não tem margem própria; "
          "sem isto o padding lateral do deck empurra o slide */ .reveal .slides>section.stack{padding:0!important}</style>")


def trocar(h):
    """Só as trocas de seletor (para .css/.js da V2 fora do index.html)."""
    for old, new in SELETORES:
        h = h.replace(old, new)
    return h


def seletores(h):
    h = trocar(h)
    i = h.index("</head>")   # o 1º é o do documento (os outros estão em strings do reveal)
    assert i < h.index("<body"), "</head> do documento não encontrado"
    return h[:i] + ESTILO + h[i:]


def sem_linear(h):
    return re.sub(r"\s*navigationMode:\s*'linear',", "", h)


def folhas(h):
    """ids dos slides-folha em ordem (para conferir que nada sumiu nem mudou de ordem)."""
    res = []
    for a, b in secoes_topo(h):
        fs = filhos(h, a, b)
        res += [ident(h, x) for x, _ in fs] if fs else [ident(h, a)]
    return res


if __name__ == "__main__":
    if sys.argv[1] == "--trocar":   # .css/.js: python3 empilhar.py --trocar entrada saida
        t = open(sys.argv[2], encoding="utf-8").read()
        n = trocar(t)
        open(sys.argv[3], "w", encoding="utf-8").write(n)
        print(f"trocas: {sum(t.count(a) for a, _ in SELETORES)}")
        sys.exit(0)
    ent, sai = sys.argv[1], sys.argv[2]
    h = open(ent, encoding="utf-8").read()
    n = seletores(sem_linear(empilhar(h)))
    assert folhas(h) == folhas(n), "a ordem dos slides mudou"
    open(sai, "w", encoding="utf-8").write(n)
    t = secoes_topo(n)
    fora = len(re.findall(r"<section\b", h)) - sum(len(re.findall(r"<section\b", h[a:b])) for a, b in secoes_topo(h))
    print(f"{len(folhas(n))} slides, {len(t)} no topo, <section> fora do bloco: {fora}, "
          f"{sum(1 for a, b in t if filhos(n, a, b))} pilhas, linear removido: {h.count(chr(39) + 'linear' + chr(39)) - n.count(chr(39) + 'linear' + chr(39))}")
