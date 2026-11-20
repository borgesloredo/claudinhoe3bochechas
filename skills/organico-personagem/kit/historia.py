#!/usr/bin/env python3
"""Cenas das séries de história (Reels em episódios): personagens 2D chapados em SVG, cenários, legenda sincronizada
com a voz e cartões de voto/escolha/segue. Gera as peças que o montar.py compartilhado junta no index.html.

Uso: python3 historia.py <pasta_do_episodio>   (lê episodio.json + voz/cNN.m4a; grava roteiro.json, cenas/, fixo.*,
                                                 estilo.css, assets/kit/)
     python3 historia.py --teste
     python3 historia.py --folha <pasta>       (uma cena só com todo o elenco em todas as poses, para conferir o desenho)

episodio.json:
  {"serie": "O NOVATO DA MESA", "ep": "EP. 1", "votos": null | {"titulo": "VOCÊS VOTARAM", "resultado": "7 EM 10: ..."},
   "cenas": [ {"fala": "...", "fundo": "palco", "pers": [...], "props": [...], "cam": "push", "destaque": ["PALAVRA"]} ]}
  pers: {"id": "leo", "x": 540, "y": 1640, "s": 1, "exp": "susto", "pose": "celular", "flip": false,
         "entra": "esq"|"dir"|"baixo", "exp2": "feliz", "quando2": "palavra"}   (exp2 troca a cara quando a palavra é dita)
  props: {"t": tipo, "quando": "palavra", ...}  (aparece quando a narração diz a palavra; sem quando = início da cena)
  cam: "push" (padrão) | "zoom:x,y,escala" | "tremer:palavra" | "fixa"
  cor_destaque: "#FFC83D" (padrão) — cor da palavra em destaque na legenda, só neste vídeo
  Cena especial: {"tipo": "escolha", "a": "...", "b": "...", "pers": [...]} e {"tipo": "segue", "proximo": "PARTE 2",
                 "perfil": "@seuperfil", "perfil_desc": "Seu nicho", "sigla": "SP", "botao": "Seguir"}
Fundos: palco, cabine, cabine_noite, plateia, quadro, escuro, dentro_mesa, comporta, comporta_vermelha, arena
Props: rotulo, bolha, microfonia, ciclo, opcoes, fader_sobe, eq, circulos, placar, monstro, placa, zzz, duelo, votos
Poses: parado, aponta, bracos_cima, maos_cabeca, mexe_mesa, cruzado, comemora, celular, pensando
Caras: neutro, feliz, susto, bravo, preocupado, confiante, dormindo, triste
"""
import json, math, re, shutil, subprocess, sys, unicodedata
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
FP = shutil.which("ffprobe") or str(Path.home() / ".local/bin/ffprobe")
AM, BR, PR, AZ, VM, VD, NV = "#FFC83D", "#FFFFFF", "#0E1424", "#2F8CFF", "#FF4D4D", "#3DDC84", "#13213B"
FONTE = "'Barlow Condensed', 'Arial Narrow', sans-serif"
CONTORNO = 'stroke="#000" stroke-width="10" paint-order="stroke"'
VOZ_OFF = 0.10  # atraso padrão da voz no montar.py (ajustes.json "off")


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def norm(s):
    s = unicodedata.normalize("NFD", str(s)).encode("ascii", "ignore").decode().upper()
    return re.sub(r"[^A-Z0-9]", "", s)


def quebra(txt, n):
    linhas, cur = [], ""
    for w in txt.split():
        if cur and len(cur) + 1 + len(w) > n:
            linhas.append(cur); cur = w
        else:
            cur = (cur + " " + w).strip()
    return linhas + ([cur] if cur else [])


def texto(x, y, linhas, tam, cor=BR, anc="middle", peso=700, extra=""):
    if isinstance(linhas, str):
        linhas = [linhas]
    ts = "".join(f'<tspan x="{x}" dy="{0 if i == 0 else tam * 1.02:.0f}">{esc(l)}</tspan>' for i, l in enumerate(linhas))
    return (f'<text x="{x}" y="{y}" text-anchor="{anc}" font-family="{FONTE}" font-weight="{peso}" font-size="{tam}" '
            f'fill="{cor}" {extra}>{ts}</text>')


# ---------------------------------------------------------------- tempo das palavras

def tempos_palavras(fala, ini, dur):
    """início de cada palavra: duração da voz repartida pelo tamanho da palavra + pausa na pontuação.
    shortcut: estimativa sem alinhamento real; trocar por mlx-whisper com word_timestamps se a legenda escorregar."""
    ws = fala.split()
    if not ws:
        return [], []
    peso = [len(norm(w)) + 1.5 + (3 if re.search(r"[.?!…]$", w) else 1.6 if re.search(r"[,;:]$", w) else 0) for w in ws]
    tot, acc, out = sum(peso), 0.0, []
    for p in peso:
        out.append(round(ini + dur * acc / tot, 3)); acc += p
    return ws, out


TROCA = {}  # episodio.json "legenda_troca": {"Clipe": "Clip"} — a voz fala de um jeito, a legenda mostra de outro


def mostra(w):
    """na fala a letra B vai escrita "bê" (a voz lê "B" solto errado); na legenda volta a ser B."""
    for de, para in TROCA.items():
        w = re.sub(rf"^{re.escape(de)}(?=\W*$)", para, w)
    return re.sub(r"^[Bb][êÊ]", "B", w)


def acende(w, dest):
    """palavra em destaque; letra solta só acende maiúscula (o "A" da opção, não o artigo "a")."""
    n = norm(w)
    return n in dest and (len(n) > 1 or w[:1].isupper())


def blocos(ws):
    """legenda em blocos de 1-2 palavras (até 3 se forem curtas); pontuação fecha o bloco."""
    out, cur = [], []
    for i, w in enumerate(ws):
        if cur and (len(cur) >= 3 or len(" ".join(ws[j] for j in cur + [i])) > 14):
            out.append(cur); cur = []
        cur.append(i)
        if re.search(r"[.,;:?!…]$", w):
            out.append(cur); cur = []
    return out + ([cur] if cur else [])


def acha(ws, ts, palavra, padrao):
    if not palavra:
        return padrao
    alvo = norm(palavra)
    for igual in (True, False):  # palavra exata primeiro ("A:" não pode cair em "abaixar")
        for w, t in zip(ws, ts):
            if norm(w) == alvo or (not igual and norm(w).startswith(alvo)):
                return t
    raise SystemExit(f"palavra '{palavra}' não está na fala: {' '.join(ws)[:80]}")


# ---------------------------------------------------------------- personagem

POSES = {  # (braço da esquerda da tela: ombro, cotovelo), (braço da direita): graus, 0 = pendurado
    "parado": ((12, -6), (-12, 6)), "aponta": ((12, -6), (-95, -5)), "bracos_cima": ((150, 10), (-150, -10)),
    "maos_cabeca": ((135, 125), (-135, -125)), "mexe_mesa": ((-25, -70), (25, 70)), "cruzado": ((-20, -105), (20, 105)),
    "comemora": ((160, -25), (-95, -95)), "celular": ((12, -6), (-150, -40)), "pensando": ((-15, -100), (-30, 150)),
}

CARAS = {  # sobrancelha (y ponta interna, y ponta externa), boca, pupila (dx, dy, r), olho aberto
    "neutro": ((-668, -668), "M-30,-538 Q0,-530 30,-538", (0, 0, 13), 1),
    "feliz": ((-675, -668), "M-48,-552 Q0,-488 48,-552 Z", (0, -2, 13), 1),
    "susto": ((-690, -680), "O", (0, 0, 8), 1.15),
    "bravo": ((-652, -678), "M-36,-528 Q0,-556 36,-528", (0, 3, 13), 0.85),
    "preocupado": ((-684, -664), "M-36,-534 q12,-12 24,0 t24,0 t24,0", (0, 4, 12), 1),
    "confiante": ((-670, -676), "M-36,-546 Q12,-522 42,-556", (4, 0, 13), 0.9),
    "dormindo": ((-664, -664), "M-12,-536 a12,10 0 1 0 24,0 a12,10 0 1 0 -24,0", None, 0),
    "triste": ((-680, -664), "M-34,-526 Q0,-552 34,-526", (0, 5, 12), 1),
}


def rosto(exp, c):
    (bi, bo), boca, pup, ab = CARAS[exp]
    o = []
    for lado in (-1, 1):
        ex = 46 * lado
        if pup is None:
            o.append(f'<path d="M{ex - 24},-612 Q{ex},-596 {ex + 24},-612" stroke="{PR}" stroke-width="7" fill="none" stroke-linecap="round"/>')
        else:
            o.append(f'<g class="olho"><ellipse cx="{ex}" cy="-612" rx="28" ry="{32 * ab:.0f}" fill="#fff"/>'
                     f'<circle cx="{ex + pup[0]}" cy="{-612 + pup[1]}" r="{pup[2]}" fill="{PR}"/></g>')
        o.append(f'<line x1="{ex + 30 * lado}" y1="{bo}" x2="{ex - 22 * lado}" y2="{bi}" stroke="{PR}" stroke-width="9" stroke-linecap="round"/>')
    if boca == "O":
        o.append(f'<ellipse cx="0" cy="-532" rx="22" ry="28" fill="{PR}"/><ellipse cx="0" cy="-520" rx="13" ry="10" fill="#E8586B"/>')
    elif boca.endswith("Z"):
        o.append(f'<path d="{boca}" fill="{PR}"/><path d="M-26,-524 Q0,-505 26,-524 Q0,-532 -26,-524" fill="#E8586B"/>')
    else:
        o.append(f'<path d="{boca}" stroke="{PR}" stroke-width="8" fill="none" stroke-linecap="round"/>')
    if exp == "preocupado":
        o.append('<path d="M118,-690 q14,26 0,36 q-14,-10 0,-36z" fill="#7FD3FF"/>')
    return "".join(o)


def braco(ombro_x, a, cot, pele, manga, lado):
    return (f'<g transform="translate({ombro_x},-448) rotate({a})">'
            f'<line x1="0" y1="0" x2="0" y2="112" stroke="{manga}" stroke-width="34" stroke-linecap="round"/>'
            f'<g transform="translate(0,112) rotate({cot})"><line x1="0" y1="0" x2="0" y2="100" stroke="{pele}" stroke-width="28" stroke-linecap="round"/>'
            f'<circle cx="0" cy="104" r="22" fill="{pele}"/></g></g>')


def cabelo(tipo, cor, frente):
    if frente:
        return {
            "curto": f'<path d="M-126,-640 Q-120,-770 0,-772 Q120,-770 126,-640 Q90,-700 30,-690 Q-40,-712 -126,-640z" fill="{cor}"/>',
            "espetado": f'<path d="M-128,-630 L-140,-720 L-90,-700 L-80,-790 L-30,-730 L0,-810 L35,-735 L85,-790 L92,-700 L142,-722 L128,-630 Q60,-690 0,-680 Q-60,-690 -128,-630z" fill="{cor}"/>',
            "cacheado": "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{cor}"/>' for x, y, r in
                                [(-110, -650, 52), (-80, -720, 58), (-20, -760, 60), (45, -755, 60), (100, -712, 56), (122, -646, 50)]),
            "coque": f'<path d="M-126,-630 Q-124,-768 0,-770 Q124,-768 126,-630 Q70,-712 0,-706 Q-70,-712 -126,-630z" fill="{cor}"/><circle cx="0" cy="-790" r="52" fill="{cor}"/>',
            "longo": f'<path d="M-130,-620 Q-126,-772 0,-774 Q126,-772 130,-620 Q60,-700 0,-690 Q-60,-700 -130,-620z" fill="{cor}"/>',
        }.get(tipo, "")
    return {
        "cacheado": "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{cor}"/>' for x, y, r in
                            [(-150, -580, 56), (150, -580, 56), (-140, -500, 48), (140, -500, 48)]),
        "longo": f'<path d="M-140,-640 L-150,-430 Q0,-410 150,-430 L140,-640z" fill="{cor}"/>',
    }.get(tipo, "")


def personagem(cid, el, exp="neutro", pose="parado", exp2=None):
    p, cor_c = el["pele"], el["cor_cabelo"]
    lg = el.get("largura", 1.0); ex = set(el.get("extras", [])); ce = el.get("cor_extra", "#222")
    w = 100 * lg
    (aA, cA), (aB, cB) = POSES[pose]
    o = ['<g class="corpo">',
         # pernas e sapatos
         f'<line x1="-44" y1="-262" x2="-48" y2="-24" stroke="{el["calca"]}" stroke-width="46" stroke-linecap="round"/>',
         f'<line x1="44" y1="-262" x2="48" y2="-24" stroke="{el["calca"]}" stroke-width="46" stroke-linecap="round"/>',
         f'<ellipse cx="-58" cy="-8" rx="44" ry="20" fill="{PR}"/><ellipse cx="58" cy="-8" rx="44" ry="20" fill="{PR}"/>',
         braco(-w + 8, aA, cA, p, el["camisa"], -1) if pose in ("cruzado", "pensando") else "",
         # tronco
         f'<path d="M{-w},-430 Q{-w},-478 {-w + 46},-478 L{w - 46},-478 Q{w},-478 {w},-430 L{w - 12},-250 Q0,-236 {-w + 12},-250z" fill="{el["camisa"]}"/>',
         f'<path d="M{-w},-430 L{-w * 0.5},-478 L{-w * 0.3},-250 L{-w + 12},-250z M{w},-430 L{w * 0.5},-478 L{w * 0.3},-250 L{w - 12},-250z" fill="{ce}"/>' if "colete" in ex else "",
         f'<rect x="-34" y="-500" width="68" height="40" rx="12" fill="{p}"/>',
         f'<path d="M-70,-470 Q0,-430 70,-470" stroke="{ce}" stroke-width="16" fill="none"/><rect x="-92" y="-486" width="30" height="44" rx="10" fill="{ce}"/><rect x="62" y="-486" width="30" height="44" rx="10" fill="{ce}"/>' if "fone_pescoco" in ex else "",
         '<g class="cabeca">', cabelo(el["cabelo"], cor_c, False),
         f'<circle cx="-124" cy="-600" r="22" fill="{p}"/><circle cx="124" cy="-600" r="22" fill="{p}"/>',
         f'<circle cx="0" cy="-610" r="126" fill="{p}"/>',
         f'<path d="M-112,-560 Q-100,-470 0,-466 Q100,-470 112,-560 Q60,-520 0,-522 Q-60,-520 -112,-560z" fill="{cor_c}"/>' if "barba" in ex else "",
         cabelo(el["cabelo"], cor_c, True)]
    o.append(f'<g class="cara c1">{rosto(exp, el)}</g>')
    if exp2:
        o.append(f'<g class="cara c2" opacity="0">{rosto(exp2, el)}</g>')
    o += [f'<path d="M-46,-560 Q-22,-576 0,-562 Q22,-576 46,-560 Q24,-548 0,-554 Q-24,-548 -46,-560z" fill="{cor_c}"/>' if "bigode" in ex else "",
          f'<g fill="none" stroke="{PR}" stroke-width="7"><circle cx="-46" cy="-612" r="40"/><circle cx="46" cy="-612" r="40"/><line x1="-6" y1="-614" x2="6" y2="-614"/></g>' if "oculos" in ex else "",
          f'<path d="M-128,-650 Q-126,-776 0,-778 Q126,-776 128,-650 Q60,-700 0,-698 Q-60,-700 -128,-650z" fill="{ce}"/><path d="M-130,-662 Q-190,-660 -200,-640 Q-150,-640 -110,-650z" fill="{ce}"/>' if "bone" in ex else "",
          f'<path d="M-138,-600 Q-140,-800 0,-800 Q140,-800 138,-600" stroke="{ce}" stroke-width="16" fill="none"/><rect x="-166" y="-650" width="40" height="84" rx="16" fill="{ce}"/><rect x="126" y="-650" width="40" height="84" rx="16" fill="{ce}"/>' if "fone" in ex else "",
          "</g>",  # braços depois da cabeça: mão na cabeça e braço para cima ficam na frente do cabelo
          braco(-w + 8, aA, cA, p, el["camisa"], -1) if pose not in ("cruzado", "pensando") else "",
          braco(w - 8, aB, cB, p, el["camisa"], 1), "</g>"]
    return "".join(o)


def celular_na_mao(pose):
    return '<rect x="-30" y="-46" width="40" height="70" rx="8" fill="#1d2433" stroke="#9fb3d9" stroke-width="4"/>' if pose == "celular" else ""


# ---------------------------------------------------------------- fundos  (devolvem (fundo, frente))

def mesa_generica(y=1440, escuro=False):
    o = [f'<rect x="-40" y="{y}" width="1160" height="{1960 - y}" fill="{"#11151f" if escuro else "#1b2233"}"/>',
         f'<rect x="-40" y="{y - 26}" width="1160" height="40" rx="14" fill="{"#1a1f2c" if escuro else "#2a3450"}"/>']
    for i in range(12):
        x = 70 + i * 80
        o.append(f'<circle cx="{x}" cy="{y + 70}" r="18" fill="#3a4666"/><line x1="{x}" y1="{y + 70}" x2="{x}" y2="{y + 54}" stroke="#cfd8ec" stroke-width="5"/>')
        o.append(f'<circle cx="{x}" cy="{y + 130}" r="14" fill="#3a4666"/>')
        o.append(f'<rect x="{x - 5}" y="{y + 175}" width="10" height="190" rx="5" fill="#0b0f18"/>')
        o.append(f'<rect class="fcap" x="{x - 22}" y="{y + 250 - (i * 37 % 90)}" width="44" height="30" rx="6" fill="#d9dfeb"/>')
        o.append(f'<rect class="led" x="{x + 18}" y="{y + 175}" width="10" height="16" rx="3" fill="{VD if i % 3 else AM}" opacity="{0.25 if escuro else 0.9}"/>')
    return "".join(o)


def fundo(nome, sid):
    if nome in ("palco", "plateia"):
        f = ['<rect width="1080" height="1920" fill="#0d1226"/>',
             '<rect x="0" y="240" width="1080" height="34" fill="#2b3350"/>']
        for i, c in enumerate(["#3D7BFF", "#B44DFF", "#FF4D9A", "#3D7BFF", "#B44DFF"]):
            x = 110 + i * 215
            f.append(f'<path class="feixe" d="M{x},270 L{x - 160},1500 L{x + 160},1500z" fill="{c}" opacity="0.16"/>'
                     f'<rect x="{x - 26}" y="256" width="52" height="40" rx="8" fill="#5a6488"/>')
        f += ['<rect x="0" y="1460" width="1080" height="460" fill="#1d1b2b"/>',
              '<rect x="-20" y="760" width="190" height="700" rx="10" fill="#151824"/><circle cx="75" cy="1000" r="62" fill="#242a3b"/><circle cx="75" cy="1240" r="80" fill="#242a3b"/>',
              '<rect x="910" y="760" width="190" height="700" rx="10" fill="#151824"/><circle cx="1005" cy="1000" r="62" fill="#242a3b"/><circle cx="1005" cy="1240" r="80" fill="#242a3b"/>']
        frente = ""
        if nome == "palco":
            frente = ('<path d="M690,1700 L760,1590 L920,1590 L960,1700z" fill="#20263a" stroke="#3a4462" stroke-width="6"/>'
                      '<ellipse cx="830" cy="1645" rx="44" ry="30" fill="#2e3650"/>')
        else:
            frente = "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#06080f"/><rect x="{x - r * 1.3}" y="{y + r * 0.7}" width="{r * 2.6}" height="300" rx="{r}" fill="#06080f"/>'
                             for x, y, r in [(60, 1620, 70), (230, 1590, 64), (400, 1640, 74), (590, 1600, 66), (770, 1630, 72), (950, 1600, 66), (150, 1760, 80), (500, 1780, 84), (860, 1770, 80)])
        return "".join(f), frente
    if nome in ("cabine", "cabine_noite"):
        noite = nome == "cabine_noite"
        f = [f'<rect width="1080" height="1920" fill="{"#070a12" if noite else "#151b2c"}"/>',
             f'<rect x="90" y="300" width="900" height="560" rx="18" fill="{"#0a0d16" if noite else "#0d1226"}" stroke="#2c3550" stroke-width="16"/>']
        if not noite:
            for i, c in enumerate(["#3D7BFF", "#FF4D9A", "#B44DFF"]):
                x = 250 + i * 290
                f.append(f'<path class="feixe" d="M{x},320 L{x - 110},840 L{x + 110},840z" fill="{c}" opacity="0.2"/>')
            f.append('<rect x="100" y="760" width="880" height="90" fill="#221f31"/>')
        else:
            f.append('<circle cx="840" cy="420" r="46" fill="#cfd6e8" opacity="0.5"/>')
        return "".join(f), mesa_generica(1440, noite)
    if nome == "quadro":
        return '<rect width="1080" height="1920" fill="#F3EFE6"/>' + "".join(
            f'<line x1="0" y1="{y}" x2="1080" y2="{y}" stroke="#E2DCCD" stroke-width="2"/>' for y in range(80, 1920, 80)), ""
    if nome == "escuro":
        return ('<rect width="1080" height="1920" fill="#05070d"/>'
                '<path d="M540,0 L180,1700 L900,1700z" fill="#ffffff" opacity="0.06"/><ellipse cx="540" cy="1690" rx="380" ry="60" fill="#ffffff" opacity="0.07"/>'), ""
    if nome in ("dentro_mesa", "comporta", "comporta_vermelha"):
        f = ['<rect width="1080" height="1920" fill="#06121a"/>',
             '<path d="M0,0 L420,700 L420,1000 L0,1920z" fill="#0c2430"/><path d="M1080,0 L660,700 L660,1000 L1080,1920z" fill="#0c2430"/>',
             '<rect x="420" y="700" width="240" height="300" fill="#0a1a24"/>']
        for i in range(9):
            y = 140 + i * 200
            f.append(f'<path d="M0,{y} L{min(420, y * 0.6)},{700 + (y - 700) * 0.43:.0f}" stroke="#14495a" stroke-width="5"/>')
            f.append(f'<path d="M1080,{y} L{1080 - min(420, y * 0.6)},{700 + (y - 700) * 0.43:.0f}" stroke="#14495a" stroke-width="5"/>')
            f.append(f'<circle class="led" cx="{60 + i * 18}" cy="{y + 40}" r="9" fill="{VD}"/><circle class="led" cx="{1020 - i * 18}" cy="{y + 90}" r="9" fill="{VD}"/>')
        f.append('<path d="M470,1000 L610,1000 L760,1920 L320,1920z" fill="#1fd3ff" opacity="0.18"/>'
                 '<path class="rio" d="M540,1000 L540,1920" stroke="#7ff0ff" stroke-width="60" stroke-dasharray="40 50" opacity="0.6"/>')
        if nome != "dentro_mesa":
            vermelho = nome == "comporta_vermelha"
            if vermelho:
                f.append('<rect class="brilho" x="300" y="560" width="480" height="560" fill="#ff2a2a" opacity="0.35"/>'
                         '<path d="M330,620 l40,90 l-30,60 l50,80 M760,600 l-50,100 l40,70 l-40,90" stroke="#ff6b6b" stroke-width="10" fill="none"/>')
            f.append('<rect x="290" y="560" width="80" height="620" fill="#2a3a46"/><rect x="710" y="560" width="80" height="620" fill="#2a3a46"/>'
                     '<rect x="290" y="520" width="500" height="70" rx="10" fill="#33495a"/>'
                     + texto(540, 572, "GANHO", 52, AM) +
                     f'<rect class="porta" x="370" y="590" width="340" height="{330 if not vermelho else 160}" fill="#3e5566" stroke="#22303b" stroke-width="10"/>')
        return "".join(f), ""
    if nome == "arena":
        f = ['<rect width="1080" height="1920" fill="#0b0d1a"/>',
             '<path d="M0,0 L540,0 L540,1920 L0,1920z" fill="#C62828" opacity="0.12"/><path d="M540,0 L1080,0 L1080,1920 L540,1920z" fill="#1E63D6" opacity="0.12"/>']
        f += [f'<circle cx="{(i * 137) % 1080}" cy="{300 + (i * 89) % 500}" r="{10 + i % 3 * 3}" fill="#2a2f4a"/>' for i in range(60)]
        f.append('<path d="M540,0 L240,1720 L840,1720z" fill="#ffffff" opacity="0.07"/>'
                 '<ellipse cx="540" cy="1700" rx="520" ry="110" fill="#1b2038" stroke="#3a4170" stroke-width="10"/>')
        return "".join(f), ""
    raise SystemExit(f"fundo desconhecido: {nome}")


# ---------------------------------------------------------------- props: devolvem (svg, js) — js usa t (hora do prop)

def card(x, y, w, h, borda=AM, fundo=NV, extra=""):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="22" fill="{fundo}" stroke="{borda}" stroke-width="7" {extra}/>'


def prop(p, sel):
    t = p["t"]
    if t == "rotulo":
        tam = p.get("tam", 110)
        return f'<g class="{sel}">{texto(p.get("x", 540), p.get("y", 430), p["texto"], tam, p.get("cor", AM), extra=CONTORNO)}</g>', "pop"
    if t == "bolha":
        ls = quebra(p["texto"], 18); x, y = p.get("x", 540), p.get("y", 760); h = 70 + 64 * len(ls)
        return (f'<g class="{sel}">{card(x - 330, y, 660, h, "#cfd8ec", "#ffffff")}'
                f'<path d="M{x - 40},{y + h - 4} l-50,70 l90,-70z" fill="#fff"/>'
                + "".join(f'<rect x="{x - 290 + i * 26}" y="{y + 38 - (i * 7 % 22)}" width="12" height="{16 + (i * 7 % 22) * 2}" rx="5" fill="#2F8CFF"/>' for i in range(4)) +
                texto(x + 30, y + 92, ls, 58, NV, extra='font-style="italic"') + "</g>"), "pop"
    if t == "microfonia":
        x, y = p.get("x", 830), p.get("y", 1560)
        arcos = "".join(f'<path class="onda" d="M{x - 60 - k * 55},{y - 60 - k * 55} A{90 + k * 78},{90 + k * 78} 0 0 1 {x + 60 + k * 55},{y - 60 - k * 55}" stroke="{VM}" stroke-width="22" fill="none" stroke-linecap="round"/>' for k in range(4))
        return f'<g class="{sel}">{arcos}{texto(x, y - 380, "!!!", 150, VM, extra=CONTORNO)}</g>', "onda"
    if t == "ciclo":
        o = [f'<g class="{sel}">', '<circle cx="540" cy="900" r="300" fill="none" stroke="#C9C1AE" stroke-width="10" stroke-dasharray="30 26"/>',
             # microfone (esquerda) e caixa (direita)
             '<rect x="180" y="840" width="70" height="140" rx="35" fill="#13213B"/><rect x="205" y="980" width="20" height="120" fill="#13213B"/>',
             '<path d="M790,820 L940,820 L980,1000 L760,1000z" fill="#13213B"/><circle cx="870" cy="910" r="50" fill="#33456b"/>',
             texto(215, 1180, "MICROFONE", 54, NV), texto(870, 1100, "RETORNO", 54, NV),
             '<g class="seta"><path d="M300,700 Q540,520 770,700" stroke="#E8571C" stroke-width="18" fill="none"/><path d="M770,700 l-60,-6 l30,-50z" fill="#E8571C"/></g>',
             '<g class="seta"><path d="M780,1110 Q540,1290 300,1110" stroke="#E8571C" stroke-width="18" fill="none"/><path d="M300,1110 l60,6 l-30,50z" fill="#E8571C"/></g>',
             texto(540, 600, "SOBE", 64, "#E8571C"), texto(540, 1330, "VOLTA", 64, "#E8571C"), "</g>"]
        return "".join(o), "ciclo"
    if t == "opcoes":
        o = [f'<g class="{sel}">']
        for k, (letra, cor) in enumerate((("A", AM), ("B", AZ))):
            y = p.get("y", 330) + k * 300; ls = quebra(p[letra.lower()], 20)
            o.append(f'<g class="op op{letra}">{card(80, y, 920, 250, cor)}<circle cx="190" cy="{y + 125}" r="70" fill="{cor}"/>'
                     + texto(190, y + 155, letra, 96, NV) + texto(300, y + 105 + (60 if len(ls) == 1 else 30) - 30, ls, 62, BR, "start") + "</g>")
        return "".join(o) + "</g>", "opcoes"
    if t == "fader_sobe":
        x, y = p.get("x", 880), p.get("y", 520)
        return (f'<g class="{sel}">{card(x - 120, y, 240, 760, "#cfd8ec", "#1b2233")}<rect x="{x - 9}" y="{y + 80}" width="18" height="600" rx="9" fill="#0b0f18"/>'
                f'<rect class="cap" x="{x - 70}" y="{y + 560}" width="140" height="70" rx="12" fill="#e9edf5"/><rect x="{x - 70}" y="{y + 590}" width="140" height="10" fill="{VM}" class="cap"/>'
                f'{texto(x, y + 730, p.get("label", "VOZ"), 50, BR)}</g>'), "fader"
    if t == "eq":
        x, y = 90, p.get("y", 330)
        corte = p.get("modo", "estreito")
        d = ("M0,180 L330,180 Q380,180 395,300 Q410,180 460,180 L900,180" if corte == "estreito"
             else "M0,330 Q120,180 220,180 L330,180 Q450,180 490,260 Q530,180 650,180 L900,180")
        return (f'<g transform="translate({x},{y})"><g class="{sel}">{card(0, 0, 900, 420, "#7ff0ff", "#071027")}'
                + "".join(f'<line x1="{i * 100}" y1="20" x2="{i * 100}" y2="400" stroke="#14244A" stroke-width="3"/>' for i in range(1, 9)) +
                f'<path class="curva" d="{d}" stroke="#7ff0ff" stroke-width="12" fill="none"/>'
                + texto(450, 380, p.get("label", "GRAVE · MÉDIO · AGUDO"), 40, "#8A98B8") + "</g></g>"), "eq"
    if t == "circulos":
        return (f'<g class="{sel}"><circle class="ca" cx="460" cy="900" r="250" fill="#E8571C" opacity="0.75"/>'
                f'<circle class="cb" cx="620" cy="900" r="250" fill="#0B8A96" opacity="0.75"/>'
                + texto(330, 920, p.get("a", "VOZ"), 70, BR) + texto(760, 920, p.get("b", "BANDA"), 70, BR) + "</g>"), "circulos"
    if t == "placar":
        o = [f'<g class="{sel}">', card(90, 300, 900, 400, AM)]
        for k, (nome, n, cor) in enumerate(((p["a"], p["na"], AZ), (p["b"], p["nb"], VM))):
            y = 380 + k * 160
            o.append(texto(130, y + 60, nome, 64, BR, "start") + f'<rect x="470" y="{y + 10}" width="440" height="70" rx="14" fill="#0b1020"/>'
                     f'<rect class="barra" x="470" y="{y + 10}" width="{44 * n}" height="70" rx="14" fill="{cor}"/>' + texto(940, y + 66, str(n), 70, BR, "end"))
        return "".join(o) + "</g>", "placar"
    if t == "monstro":
        x, y, s = p.get("x", 540), p.get("y", 900), p.get("s", 1)
        return (f'<g transform="translate({x},{y}) scale({s})"><g class="{sel}"><g class="mz">'
                '<path d="M-200,120 L-230,-60 L-150,-40 L-170,-190 L-70,-110 L0,-230 L70,-110 L170,-190 L150,-40 L230,-60 L200,120 Q0,200 -200,120z" fill="#E53030" stroke="#7a0d0d" stroke-width="10"/>'
                '<ellipse cx="-70" cy="-20" rx="38" ry="30" fill="#FFE14D"/><ellipse cx="70" cy="-20" rx="38" ry="30" fill="#FFE14D"/>'
                '<circle cx="-62" cy="-16" r="13" fill="#000"/><circle cx="62" cy="-16" r="13" fill="#000"/>'
                '<path d="M-100,70 L-70,40 L-40,75 L-10,40 L20,75 L50,40 L80,75 L100,50" stroke="#fff" stroke-width="12" fill="none"/>'
                f'{card(-90, 130, 180, 64, "#fff", "#7a0d0d")}{texto(0, 178, "CLIP", 48, BR)}</g></g></g>'), "monstro"
    if t == "placa":
        x, y = p.get("x", 540), p.get("y", 640)
        return f'<g class="{sel}">{card(x - 170, y - 70, 340, 110, VD, "#0a2a1a")}{texto(x, y + 10, p["texto"], 64, VD)}</g>', "pop"
    if t == "zzz":
        x, y = p.get("x", 700), p.get("y", 700)
        return f'<g class="{sel}">' + "".join(texto(x + k * 50, y - k * 70, "Z", 60 + k * 18, "#cfd8ec") for k in range(3)) + "</g>", "zzz"
    if t == "duelo":
        return (f'<g class="{sel}">{card(60, 330, 430, 150, VM, "#3a0d0d")}{texto(275, 430, p["a"], 60, BR)}'
                f'{card(590, 330, 430, 150, AZ, "#0d1d3a")}{texto(805, 430, p["b"], 60, BR)}'
                f'<circle cx="540" cy="405" r="74" fill="{AM}"/>{texto(540, 432, "VS", 74, NV)}</g>'), "pop"
    if t == "votos":
        ls = quebra(p["resultado"], 18)
        return (f'<g class="{sel}">{card(110, 1180, 860, 150 + 84 * len(ls), AM)}{texto(540, 1250, p.get("titulo", "VOCÊS VOTARAM"), 50, "#cfd8ec")}'
                f'{texto(540, 1340, ls, 84, AM)}</g>'), "pop"
    raise SystemExit(f"prop desconhecido: {t}")


ANIM = {  # js de cada prop (t = hora em que aparece, fim = fim da cena)
    "pop": 'V.ft(S_, {opacity: 0, scale: .6, transformOrigin: "50% 50%"}, {opacity: 1, scale: 1, duration: .35, ease: "back.out(2)"}, t);',
    "onda": 'V.fadeIn(S_, t, .05); tl.fromTo(S_ + " .onda", {opacity: 0}, {opacity: 1, duration: .08, stagger: .08, yoyo: true, repeat: Math.max(1, Math.floor((fim - t) / .32)), ease: "steps(1)"}, t);',
    "ciclo": 'V.fadeIn(S_, t, .2); tl.fromTo(S_ + " .seta", {opacity: .25}, {opacity: 1, duration: .4, stagger: .4, yoyo: true, repeat: Math.max(1, Math.floor((fim - t) / .8)), ease: "sine.inOut"}, t + .3);',
    "opcoes": 'V.fadeIn(S_, t, .05); V.ft(S_ + " .opA", {x: -900}, {x: 0, duration: .45, ease: "stage"}, t); V.ft(S_ + " .opB", {x: 900}, {x: 0, duration: .45, ease: "stage"}, tB);',
    "fader": 'V.entra(S_, t, .35); V.ft(S_ + " .cap", {y: 0}, {y: -420, duration: Math.min(2.2, fim - t - .2), ease: "power1.inOut"}, t + .3);',
    "eq": 'V.entra(S_, t, .35); V.ft(S_ + " .curva", {opacity: 0}, {opacity: 1, duration: .6, ease: "none"}, t + .4);',
    "circulos": 'V.fadeIn(S_, t, .2); V.ft(S_ + " .ca", {x: 0}, {x: -150, duration: 1.2, ease: "stage"}, t + Math.min(2.5, (fim - t) * .55)); V.ft(S_ + " .cb", {x: 0}, {x: 150, duration: 1.2, ease: "stage"}, t + Math.min(2.5, (fim - t) * .55));',
    "placar": 'V.entra(S_, t, .35); tl.fromTo(S_ + " .barra", {scaleX: 0, transformOrigin: "0% 50%"}, {scaleX: 1, duration: 1.1, ease: "power2.out", stagger: .3}, t + .3);',
    "monstro": 'V.ft(S_, {opacity: 0, y: 200}, {opacity: 1, y: 0, duration: .5, ease: "back.out(1.6)"}, t); V.shake(S_ + " .mz", t + .5, 10, Math.min(1.5, fim - t - .5));',
    "zzz": 'V.fadeIn(S_, t, .05); tl.fromTo(S_ + " text", {opacity: 0, y: 30}, {opacity: 1, y: 0, duration: .5, stagger: .4, ease: "sine.out"}, t);',
}


# ---------------------------------------------------------------- cena

def dur_voz(f):
    return float(subprocess.check_output([FP, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(f)]))


def cena(i, c, elenco, dvoz):
    sid = f"s{i:02d}"; svg, js = [], []
    ws, ts = tempos_palavras(c.get("fala", ""), VOZ_OFF, max(0.5, dvoz - 0.2))
    fim = round(VOZ_OFF + dvoz + 0.25, 3)  # fim relativo (o montar.py estica a cena até o fim da voz + 0,25 s)
    tipo = c.get("tipo", "cena")
    fnd, frente = fundo(c.get("fundo", "escuro" if tipo in ("escolha", "segue") else "palco"), sid)
    svg.append(f'<g class="fundo">{fnd}</g>')
    # personagens
    for k, p in enumerate(c.get("pers", [])):
        el = elenco[p["id"]]; s = p.get("s", 1.0); fl = -1 if p.get("flip") else 1
        cls = f"p{k}"
        svg.append(f'<g transform="translate({p.get("x", 540)},{p.get("y", 1640)}) scale({s * fl},{s})"><g class="{cls}"><g class="bob">'
                   f'{personagem(p["id"], el, p.get("exp", "neutro"), p.get("pose", "parado"), p.get("exp2"))}'
                   f'<g transform="translate(140,-630)">{celular_na_mao(p.get("pose"))}</g></g></g></g>')
        base = f"#{sid} .{cls}"
        ent = p.get("entra")
        if ent:
            dx, dy = {"esq": (-900, 0), "dir": (900, 0), "baixo": (0, 900)}[ent]
            js.append(f'V.ft("{base}", {{x: {dx * fl}, y: {dy}}}, {{x: 0, y: 0, duration: .5, ease: "stage"}}, t0 + .05);')
        js.append(f'tl.fromTo("{base} .bob", {{y: 0}}, {{y: -10, duration: .7, yoyo: true, repeat: {max(1, int(fim / .7) - 1)}, ease: "sine.inOut"}}, t0);')
        for b in [x for x in (0.9, 2.6, 4.4, 6.1, 8.3) if x < fim - 0.3]:
            js.append(f'tl.to("{base} .olho", {{scaleY: .1, transformOrigin: "50% 50%", duration: .07, yoyo: true, repeat: 1}}, t0 + {b + k * 0.3:.2f});')
        if p.get("exp2"):
            tq = acha(ws, ts, p.get("quando2"), fim / 2)
            js.append(f'tl.set("{base} .c1", {{opacity: 0}}, t0 + {tq}); tl.set("{base} .c2", {{opacity: 1}}, t0 + {tq});')
    # props
    sobre = []
    for k, p in enumerate(c.get("props", [])):
        cls = f"pr{k}"; s_, kind = prop(p, cls)
        (sobre if p["t"] == "rotulo" else svg).append(s_)  # rótulo fica fora da câmera: o zoom não o empurra para baixo do título
        t = acha(ws, ts, p.get("quando"), 0.05)
        extra = ""
        if kind == "opcoes":
            extra = f"const tB = t0 + {acha(ws, ts, p.get('quando_b', 'bê'), t + 1.5)};"
        js.append(f'{{ const S_ = "#{sid} .{cls}", t = t0 + {t}, fim = t0 + {fim}; {extra} tl.set(S_, {{opacity: 0}}, t0); {ANIM[kind]} }}')
    # cartões de escolha e de segue
    if tipo == "escolha":
        for k, (letra, cor) in enumerate((("A", AM), ("B", AZ))):
            y = 330 + k * 300; ls = quebra(c[letra.lower()], 20)
            svg.append(f'<g class="op op{letra}">{card(80, y, 920, 250, cor)}<circle cx="190" cy="{y + 125}" r="70" fill="{cor}"/>'
                       + texto(190, y + 155, letra, 96, NV) + texto(300, y + 105 + (60 if len(ls) == 1 else 30) - 30, ls, 62, BR, "start") + "</g>")
        svg.append(f'<g class="chama">{texto(540, 1050, c.get("chamada", "COMENTA A OU B"), 104, AM, extra=CONTORNO)}'
                   f'<path d="M500,1110 L580,1110 L580,1180 L630,1180 L540,1270 L450,1180 L500,1180z" fill="{AM}"/></g>')
        js.append(f'V.ft("#{sid} .opA", {{x: -900}}, {{x: 0, duration: .45, ease: "stage"}}, t0 + .1); V.ft("#{sid} .opB", {{x: 900}}, {{x: 0, duration: .45, ease: "stage"}}, t0 + .35);'
                  f'V.ft("#{sid} .chama", {{opacity: 0, scale: .7, transformOrigin: "50% 50%"}}, {{opacity: 1, scale: 1, duration: .4, ease: "back.out(2)"}}, t0 + .7);'
                  f'tl.to("#{sid} .chama", {{scale: 1.06, transformOrigin: "50% 50%", duration: .45, yoyo: true, repeat: {max(1, int((fim - 1.2) / .45))}, ease: "sine.inOut"}}, t0 + 1.2);')
    if tipo == "segue":
        svg.append(f'<g class="perfil">{card(140, 560, 800, 190, "#cfd8ec", "#ffffff")}<circle cx="250" cy="655" r="66" fill="#E8571C"/>'
                   + texto(250, 680, c.get("sigla", c.get("perfil", "@sp").lstrip("@")[:2].upper()), 60, BR) + texto(345, 640, c.get("perfil", "@seuperfil"), 56, NV, "start") + texto(345, 700, c.get("perfil_desc", ""), 40, "#5B6478", "start", 600)
                   + f'<rect class="botao" x="720" y="618" width="190" height="74" rx="16" fill="{AZ}"/>' + texto(815, 670, c.get("botao", "Seguir"), 44, BR) + "</g>"
                   + f'<g class="prox">{texto(540, 1000, c.get("proximo", "PARTE 2 EM BREVE"), 96, AM, extra=CONTORNO)}</g>')
        js.append(f'V.entra("#{sid} .perfil", t0 + .1, .45); V.press("#{sid} .botao", t0 + 1.2, 6); V.ft("#{sid} .prox", {{opacity: 0, y: 40}}, {{opacity: 1, y: 0, duration: .45, ease: "stage"}}, t0 + .8);')
    svg.append(f'<g class="frente">{frente}</g>')
    # animações do fundo
    js.append(f'V.breathe("#{sid} .feixe", t0, t0 + {fim}, .5); V.breathe("#{sid} .led", t0, t0 + {fim}, .35);')
    js.append(f'tl.fromTo("#{sid} .rio", {{strokeDashoffset: 0}}, {{strokeDashoffset: -{int(fim * 220)}, duration: {fim}, ease: "none"}}, t0);')
    # câmera
    cam = c.get("cam", "push")
    if cam == "push":
        js.append(f'V.push("#{sid} .cam", t0, {fim}, 1, 1.05);')
    elif cam.startswith("zoom:"):
        x, y, s_ = (float(v) for v in cam[5:].split(","))
        js.append(f'V.camSet("#{sid} .cam", 1, 540, 960, t0); V.zoom("#{sid} .cam", t0 + .2, {min(2.5, fim - .3)}, {s_}, {x}, {y});')
    elif cam.startswith("tremer"):
        tq = acha(ws, ts, cam.split(":", 1)[1] if ":" in cam else None, 0.1)
        js.append(f'V.push("#{sid} .cam", t0, {fim}, 1, 1.04); V.shake("#{sid} .cam", t0 + {tq}, 14, {min(1.2, fim - tq)});')
    # legenda
    dest = {norm(w) for w in c.get("destaque", [])} | ({"BE"} if "B" in {norm(w) for w in c.get("destaque", [])} else set())
    leg = []
    bl = blocos(ws)
    for b_i, b in enumerate(bl):
        partes = " ".join(f'<span class="{"hl" if acende(ws[j], dest) else ""}">{esc(mostra(ws[j]))}</span>' for j in b)
        leg.append(f'<div class="leg l{b_i}">{partes}</div>')
        ti = ts[b[0]]; tf = ts[bl[b_i + 1][0]] if b_i + 1 < len(bl) else fim - 0.05
        js.append(f'tl.set("#{sid} .l{b_i}", {{opacity: 1}}, t0 + {ti}); V.ft("#{sid} .l{b_i}", {{scale: .82}}, {{scale: 1, duration: .14, ease: "back.out(3)"}}, t0 + {ti}); tl.set("#{sid} .l{b_i}", {{opacity: 0}}, t0 + {round(tf, 3)});')
    pos_leg = c.get("legenda_y", 1380 if tipo == "cena" else 1500)
    html = (f'<div class="cam"><svg viewBox="0 0 1080 1920" width="1080" height="1920" xmlns="http://www.w3.org/2000/svg">{"".join(svg)}</svg></div>'
            f'<svg class="sobre" viewBox="0 0 1080 1920" width="1080" height="1920" xmlns="http://www.w3.org/2000/svg">{"".join(sobre)}</svg>'
            f'<div class="legenda" style="top:{pos_leg}px">{"".join(leg)}</div>')
    return html, "\n".join(js), round(fim - VOZ_OFF - 0.25 + 0.0, 3)


CSS = """@font-face{font-family:'Barlow Condensed';font-weight:700;src:url(fonts/barlow-condensed-latin-700-normal.woff2) format('woff2')}
.legenda{position:absolute;left:40px;right:40px;height:0;text-align:center}
.leg{position:absolute;left:0;right:0;transform:translateY(-50%);opacity:0;font-family:'Barlow Condensed',sans-serif;font-weight:700;
 font-size:118px;line-height:1;color:#fff;text-transform:uppercase;-webkit-text-stroke:12px #000;paint-order:stroke fill;letter-spacing:1px}
.leg .hl{color:#FFC83D}
.cam{position:absolute;inset:0;transform-origin:540px 960px}
.sobre{position:absolute;inset:0;pointer-events:none}
#fixo{z-index:10}
#selo{position:absolute;top:96px;left:0;right:0;text-align:center}
#selo span{display:inline-block;padding:14px 30px;border:4px solid rgba(255,255,255,.55);border-radius:16px;background:rgba(10,14,28,.72);
 font-family:'Barlow Condensed',sans-serif;font-weight:700;font-size:44px;letter-spacing:3px;color:#fff;text-transform:uppercase}"""


def gerar(d):
    d = Path(d).resolve()
    ep = json.loads((d / "episodio.json").read_text())
    TROCA.clear(); TROCA.update(ep.get("legenda_troca", {}))
    elenco = json.loads((RAIZ / "elenco.json").read_text())
    (d / "cenas").mkdir(exist_ok=True)
    kit = d / "assets/kit"; (kit / "fonts").mkdir(parents=True, exist_ok=True)
    shutil.copy(AQUI / "fonts/barlow-condensed-latin-700-normal.woff2", kit / "fonts/")
    (kit / "tema.css").write_text(CSS.replace("#FFC83D", ep.get("cor_destaque", "#FFC83D")))  # cor da palavra em destaque na legenda, por vídeo
    cenas = ep["cenas"]
    if ep.get("votos"):  # do EP. 2 em diante: o voto do anterior entra por cima da 1ª cena
        cenas[0].setdefault("props", []).insert(0, {"t": "votos", **ep["votos"]})
    rot = {"id": f'{ep["serie"]} {ep["ep"]}', "nome": f'{ep["serie"]} · {ep["ep"]}', "cenas": []}
    t = 0.0
    for i, c in enumerate(cenas, 1):
        f = d / f"voz/c{i:02d}.m4a"
        dv = dur_voz(f) if f.exists() else len(c.get("fala", "").split()) / 3.2
        h, j, _ = cena(i, c, elenco, dv)
        (d / f"cenas/s{i:02d}.html").write_text(h); (d / f"cenas/s{i:02d}.js").write_text(j)
        rot["cenas"].append({"t_ini": round(t, 2), "t_fim": round(t + dv + 0.35, 2), "texto_tela": " ".join(c.get("destaque", [])) or c.get("tipo", "cena"),
                             "fala": c.get("fala", ""), "visual": f'{c.get("fundo", "")} {[p["id"] for p in c.get("pers", [])]}', "motion": c.get("cam", "push")})
        t += dv + 0.35
    (d / "roteiro.json").write_text(json.dumps(rot, ensure_ascii=False, indent=1))
    (d / "fixo.html").write_text(f'<div id="selo"><span>{esc(ep["serie"])} · {esc(ep["ep"])}</span></div>')
    (d / "fixo.js").write_text('V.fadeIn("#selo", 0.1, 0.3);')
    print(f"OK {len(cenas)} cenas em {d.name}")


def folha(d):
    """cena de conferência: todo o elenco, cada um numa pose/cara, sem voz."""
    d = Path(d); d.mkdir(parents=True, exist_ok=True)
    elenco = json.loads((RAIZ / "elenco.json").read_text())
    ids = list(elenco); poses = list(POSES); caras = list(CARAS)
    cenas = []
    for k in range(0, len(poses), 3):
        pers = [{"id": ids[(k + j) % len(ids)], "x": 200 + j * 340, "y": 1500, "s": 0.62, "pose": poses[k + j] if k + j < len(poses) else "parado",
                 "exp": caras[(k + j) % len(caras)]} for j in range(3)]
        cenas.append({"fala": " ".join(f"{p['id']} {p['pose']} {p['exp']}." for p in pers), "fundo": "quadro", "pers": pers, "cam": "fixa"})
    (d / "episodio.json").write_text(json.dumps({"serie": "FOLHA", "ep": "ELENCO", "cenas": cenas}, ensure_ascii=False, indent=1))
    gerar(d)


def teste():
    ws, ts = tempos_palavras("Vinte minutos pro evento começar. E agora?", 0.1, 3.0)
    assert len(ws) == len(ts) == 7 and ts[0] == 0.1 and all(a < b for a, b in zip(ts, ts[1:])) and ts[-1] < 3.1, ts
    b = blocos(ws)
    assert sum(len(x) for x in b) == 7, b
    assert all(len(" ".join(ws[j] for j in x)) <= 16 or len(x) == 1 for x in b), b
    assert acha(ws, ts, "evento", 0) == ts[3]
    assert acende("A:", {"A"}) and not acende("a", {"A"}) and acende("bê.", {"BE"})
    assert quebra("CORTA SÓ A FREQUÊNCIA QUE APITA", 20) == ["CORTA SÓ A", "FREQUÊNCIA QUE APITA"]
    el = json.loads((RAIZ / "elenco.json").read_text())
    for cid in el:
        for pose in POSES:
            assert personagem(cid, el[cid], "susto", pose, "feliz").count("<g") == personagem(cid, el[cid], "susto", pose, "feliz").count("</g>")
    print("teste ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["--teste"]:
        teste()
    elif sys.argv[1] == "--folha":
        folha(sys.argv[2])
    else:
        gerar(sys.argv[1])
