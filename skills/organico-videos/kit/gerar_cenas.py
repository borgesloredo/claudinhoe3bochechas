#!/usr/bin/env python3
"""Peças de cena dos vídeos orgânicos genéricos (layout DESIGN-GENERICO.md: mesa desenhada, sem marca).

Uso: python3 gerar_cenas.py <pasta_do_video>      (lê roteiro.json + spec.json; grava cenas/, fixo.*, estilo.css, assets/kit/)
     python3 gerar_cenas.py --teste
Depois: python3 <G>/tools/montar.py <pasta> --musica calma --voz ; lint ; check ; render ; checar.py

spec.json = {"cenas": [ {"c": [componente, ...], "pill": ["TEXTO", "r"|"g"], "at": 0.35}, ... ]}  (uma por cena do roteiro)
Componentes ("t" = tipo; coordenadas absolutas no quadro 1080x1920):
  canal {gain,gain1,fader,fader1,meter,lowcut,eq,mute,mute1,p48,p48_1,hl:[...],knobs:{AGUDO:[v0,v1],...},checks:bool,blink_eq:bool}
  knob {x,y,r,label,v0,v1,cor}   fader {x,top,h,label,v0,v1}   meter {x,top,h,w,lo,hi,clip}
  caminho {blocos:[...],hl:i,cor}  tela {curvas:[[termo,...],...], faixa:[f1,f2], cor}  barras {alturas:[...], manta:bool}
  circulos {estados:[[x1,r1,x2,r2],...], a:"VOZ", b:"TECLADO", cor_b}  quiz {ops:[...], certa:i, revela:bool}
  mic {tipo:"condensador"|"dinamico"|"fita", ondas:bool, x,y}  fones {}  mesa {hl:i, p48:bool, nomes:[...]}
  seta {x,y,texto,tx,ty}  ruido {x,y}  onda {achatada:bool}  produto {escala, y}  cta {}
Termos de curva (tela): ["hp",fc] ["bell",f0,dB,larg_oitavas] ["lshelf",fc,dB] ["hshelf",fc,dB]
"""
import json, math, re, shutil, sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
MARCA = json.loads((AQUI.parent / "marca.json").read_text()) if (AQUI.parent / "marca.json").exists() else {}  # {"selo": "@perfil", "selo_produto": "..."}
FONTES = AQUI / "fonts"
C = dict(bg="#0B1630", grid="#14244A", am="#FFC83D", ci="#2FD3E6", vd="#3DDC84", vm="#FF4D4D", cz="#8A98B8",
         pn="#0F1E40", bd="#2A3D6B", corpo="#13254D", br="#FFFFFF")
C.update(tema="a", pg="#fff", sh="", il="#2b3a5c", il2="#1d2945", ild="#c9d2e6", ilm="#8090b5", tela="#071027", telag="#14244A", telal="#8A98B8", led="#0a1430")
COR = {"r": C["vm"], "g": C["vd"], "a": C["am"], "c": C["ci"]}
# layout B (vídeos 006+): quadro claro, tinta escura, laranja, painéis brancos com sombra sólida
TEMA_B = dict(tema="b", bg="#F3EFE6", grid="#DCD5C6", am="#E8571C", ci="#0B8A96", vd="#1E9E5A", vm="#D93036", cz="#5B6478",
              pn="#FFFFFF", bd="#13213B", corpo="#FFFFFF", br="#13213B", pg="#13213B", sh=' filter="url(#sh)"')


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class Cena:
    def __init__(self, n, d=None):
        self.n, self.svg, self.html, self.js, self.k, self.lidas = n, [], [], [], 0, []

    def id(self):
        self.k += 1
        return f"s{self.n:02d}-{self.k}"

    def txt(self, x, y, s, size=26, cor=None, peso=600, anchor="middle", conta=None):
        """Texto em SVG. Texto >= 32 px conta como palavra de tela (regra dos 9)."""
        if conta is None:
            conta = size >= 32
        if conta:
            self.lidas.append(s)
        return f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{peso}" fill="{cor or C["cz"]}" text-anchor="{anchor}" font-family="Barlow">{esc(s)}</text>'

    # ---------- peças de hardware ----------
    def knob(self, x, y, r, label, v0, v1=None, cor=None, at=0.3, lsize=30):
        i = self.id(); cor = cor or C["am"]; L = r * 1.5 * math.pi
        p = lambda a: (x + r * math.cos(math.radians(a)), y + r * math.sin(math.radians(a)))
        (ax, ay), (bx, by) = p(135), p(45)
        arc = f"M{ax:.1f},{ay:.1f} A{r},{r} 0 1 1 {bx:.1f},{by:.1f}"
        rr = r * 0.74
        self.svg.append(
            f'<g id="{i}"><path d="{arc}" fill="none" stroke="{C["bd"]}" stroke-width="{max(6, r * .1):.0f}" stroke-linecap="round"/>'
            f'<path class="val" d="{arc}" fill="none" stroke="{cor}" stroke-width="{max(6, r * .1):.0f}" stroke-linecap="round" stroke-dasharray="{L:.1f}" stroke-dashoffset="{L * (1 - v0):.1f}"/>'
            f'<circle cx="{x}" cy="{y}" r="{rr:.1f}" fill="{C["corpo"]}" stroke="{C["bd"]}" stroke-width="3"/>'
            f'<g class="ind"><line x1="{x}" y1="{y}" x2="{x}" y2="{y - rr * .82:.1f}" stroke="{C["br"]}" stroke-width="{max(4, r * .07):.0f}" stroke-linecap="round"/></g>'
            + self.txt(x, y + r + lsize + 8, label, lsize, C["cz"]) + "</g>")
        a0 = -135 + 270 * v0
        self.js.append(f'tl.set("#{i} .ind", {{rotation:{a0:.1f}, svgOrigin:"{x} {y}"}}, t0);')
        if v1 is not None:
            a1 = -135 + 270 * v1
            self.js.append(f'tl.to("#{i} .val", {{strokeDashoffset:{L * (1 - v1):.1f}, duration:.8, ease:"fader"}}, t0 + d*{at});')
            self.js.append(f'tl.to("#{i} .ind", {{rotation:{a1:.1f}, svgOrigin:"{x} {y}", duration:.8, ease:"fader"}}, t0 + d*{at});')
        return i

    def fader(self, x, top, h, label, v0, v1=None, at=0.3, w=None, escala=True, lsize=26):
        i = self.id(); w = w or max(60, h * .2)
        marcas = [("+10", 0), ("0", .25), ("-10", .5), ("-20", .68), ("-40", .85), ("-∞", 1)]
        tk = "".join(f'<line x1="{x - w * .9:.0f}" y1="{top + h * f:.0f}" x2="{x - w * .55:.0f}" y2="{top + h * f:.0f}" stroke="{C["bd"]}" stroke-width="3"/>'
                     + (self.txt(x - w * 1.05, top + h * f + 10, m, 28, C["cz"], anchor="end") if escala else "") for m, f in marcas)
        self.svg.append(
            f'<g id="{i}">{tk}<rect x="{x - 7}" y="{top}" width="14" height="{h}" rx="7" fill="{C["led"]}" stroke="{C["bd"]}" stroke-width="2"/>'
            f'<g class="cap"><rect x="{x - w / 2:.0f}" y="{top - w * .22:.0f}" width="{w:.0f}" height="{w * .44:.0f}" rx="8" fill="#D8DEEA" stroke="{C["pg"]}" stroke-width="2"/>'
            f'<line x1="{x - w * .4:.0f}" y1="{top}" x2="{x + w * .4:.0f}" y2="{top}" stroke="{C["bg"]}" stroke-width="4"/></g>'
            + self.txt(x, top + h + lsize + 26, label, lsize, C["cz"]) + "</g>")
        self.js.append(f'tl.set("#{i} .cap", {{y:{h * (1 - v0):.0f}}}, t0);')
        if v1 is not None:
            self.js.append(f'V.fader("#{i} .cap", t0 + d*{at}, {h * (1 - v1):.0f}, .9);')
        return i

    def meter(self, x, top, h, w=34, lo=.3, hi=.6, clip=False, at=0.3, lo1=None, hi1=None):
        i = self.id(); g = f"g{i}"
        segs = "".join(f'<rect x="{x}" y="{top + k * h / 20 + 2:.1f}" width="{w}" height="{h / 20 - 4:.1f}" rx="2" fill="{C["led"]}"/>' for k in range(20))
        self.svg.append(
            f'<defs><linearGradient id="{g}" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="{C["vd"]}"/><stop offset=".62" stop-color="{C["vd"]}"/>'
            f'<stop offset=".78" stop-color="#F5B301"/><stop offset=".93" stop-color="{C["vm"]}"/></linearGradient></defs>'
            f'<g id="{i}">{segs}<rect class="lit" x="{x}" y="{top}" width="{w}" height="{h}" rx="3" fill="url(#{g})" opacity=".95"/>'
            f'<rect class="clip-led" x="{x}" y="{top - 30}" width="{w}" height="18" rx="4" fill="{C["vm"]}" opacity=".15"/></g>')
        self.js.append(f'V.meter("#{i} .lit", t0, t0 + d*{at}, {lo}, {hi});')
        a, b = (lo1 if lo1 is not None else lo), (hi1 if hi1 is not None else hi)
        self.js.append(f'V.meter("#{i} .lit", t0 + d*{at}, t0 + d, {a}, {b});')
        if clip:
            self.js.append(f'V.blink("#{i} .clip-led", t0 + d*{at}, .15, .12, 4); tl.to("#{i} .clip-led", {{opacity:1, duration:.05}}, t0 + d*{at});')
        return i

    def botao(self, x, y, w, h, label, on=False, cor=None, on_at=None, off_at=None, lsize=28):
        i = self.id(); cor = cor or C["am"]
        self.svg.append(f'<g id="{i}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{C["corpo"]}" stroke="{C["bd"]}" stroke-width="2"/>'
                        f'<rect class="on" x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{cor}" opacity="{1 if on else 0}"/>'
                        + self.txt(x + w / 2, y + h / 2 + lsize * .36, label, lsize, self.tx_on(cor) if on else C["br"], 700) + "</g>")
        escuro = self.tx_on(cor) != C["br"]  # o texto precisa trocar de cor ao acender
        if on_at is not None:
            self.js.append(f'V.flick("#{i} .on", t0 + d*{on_at});')
            if escuro:
                self.js.append(f'tl.to("#{i} text", {{fill:"{self.tx_on(cor)}", duration:.1}}, t0 + d*{on_at});')
        if off_at is not None:
            self.js.append(f'tl.to("#{i} .on", {{opacity:0, duration:.08, ease:"hw"}}, t0 + d*{off_at});')
            if escuro:
                self.js.append(f'tl.to("#{i} text", {{fill:"{C["br"]}", duration:.08}}, t0 + d*{off_at});')
        return i

    @staticmethod
    def tx_on(cor):
        if C["tema"] == "b":
            return "#fff"
        if C.get("gerado"):  # temas escuros gerados: cores vivas pedem texto escuro (menos o azul-petróleo fixo do EQ)
            return C["br"] if cor == "#0F7D8B" else C["bg"]
        return C["bg"] if cor == C["am"] else C["br"]

    @staticmethod
    def sobre():
        """cor de texto/traço em cima de um preenchimento de destaque."""
        return C["bg"] if C["tema"] == "a" else "#fff"

    def seq(self, sel, o, prop):
        """o["seq"] = [v, ...]: vai de valor em valor entre o["at"] e 0.9 da cena."""
        vs = o.get("seq") or []
        for k, v in enumerate(vs):
            t = o.get("at", .2) + (.88 - o.get("at", .2)) * k / max(1, len(vs))
            self.js.append(f'tl.to("{sel}", {{{prop(v)}, duration:.45, ease:"fader"}}, t0 + d*{t:.3f});')

    def brilho(self, x, y, w, h, rx=16, at=0.25, cor=None):
        i = self.id()
        self.svg.append(f'<rect id="{i}" x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="none" stroke="{cor or C["am"]}" stroke-width="5" opacity="0"/>')
        self.js.append(f'tl.to("#{i}", {{opacity:1, duration:.2}}, t0 + d*{at}); V.breathe("#{i}", t0 + d*{at} + .2, t0 + d, .35);')

    def check(self, x, y, at):
        i = self.id()
        self.svg.append(f'<g id="{i}" opacity="0"><circle cx="{x}" cy="{y}" r="30" fill="{C["vd"]}"/><path d="M{x - 13},{y} l9,10 l17,-20" fill="none" stroke="#06210f" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/></g>')
        self.js.append(f'tl.fromTo("#{i}", {{opacity:0, scale:.4, svgOrigin:"{x} {y}"}}, {{opacity:1, scale:1, svgOrigin:"{x} {y}", duration:.3, ease:"back.out(2)", immediateRender:false}}, t0 + d*{at});')

    # ---------- componentes ----------
    def c_canal(self, o):
        at = o.get("at", .3); ini = len(self.svg)
        self.svg.append(f'<rect x="330" y="610" width="420" height="900" rx="28" fill="{C["pn"]}" stroke="{C["bd"]}" stroke-width="3"{C["sh"]}/>')
        self.botao(365, 640, 130, 56, "48V", o.get("p48", False), C["am"], on_at=at if o.get("p48_1") else None)
        self.botao(585, 640, 130, 56, "MUTE", o.get("mute", False), C["vm"], off_at=(at + .25) if o.get("mute1") is False else None,
                   on_at=at if o.get("mute1") is True else None)
        self.knob(540, 800, 72, "GAIN", o.get("gain", .5), o.get("gain1"), at=at, lsize=32)
        b1, b2 = o.get("botoes", ["LOW CUT", "EQ"])
        self.botao(365, 935, 165, 56, b1, o.get("lowcut", False), C["am"], on_at=at if o.get("lowcut1") else None)
        eqb = self.botao(570, 935, 145, 56, b2, o.get("eq", True), "#0F7D8B")
        if o.get("blink_eq"):
            self.js.append(f'V.blink("#{eqb} .on", t0 + d*{at}, 0, .35, 3);')
        kn = o.get("knobs", {})
        for nome, (kx, ky) in {"AGUDO": (450, 1050), "MÉDIO AG.": (630, 1050), "MÉDIO GR.": (450, 1165), "GRAVE": (630, 1165)}.items():
            v = kn.get(nome, [.5, None])
            self.knob(kx, ky, 38, nome, v[0], v[1], C["ci"], at=at, lsize=28)
        self.fader(470, 1300, 160, "", o.get("fader", .75), o.get("fader1"), at=at, w=64, escala=False)
        self.meter(600, 1300, 160, 30, o.get("meter", [.3, .5])[0], o.get("meter", [.3, .5])[1], o.get("clip", False), at,
                   *(o.get("meter1") or [None, None]))
        zonas = {"gain": (450, 712, 180, 215), "fader": (420, 1270, 110, 210), "lowcut": (355, 925, 185, 76), "eq": (560, 925, 165, 76),
                 "mute": (575, 630, 150, 76), "48v": (355, 630, 150, 76), "eqknobs": (395, 1000, 290, 245), "meter": (585, 1270, 60, 210),
                 "agudo": (405, 1005, 90, 115), "grave": (585, 1120, 90, 115)}
        for h in o.get("hl", []):
            self.brilho(*zonas[h], at=o.get("hl_at", .2))
        if o.get("checks"):
            for k, (x, y) in enumerate([(290, 668), (790, 668), (790, 1380)]):
                self.check(x, y, .15 + .2 * k)
        # amplia o canal (quadro inteiro mais legível); svgOrigin dos knobs é local ao grupo
        self.svg[ini:] = ['<g transform="translate(540 1030) scale(1.06) translate(-540 -1060)">' + "".join(self.svg[ini:]) + "</g>"]

    def c_knob(self, o):
        k = self.knob(o.get("x", 540), o.get("y", 1050), o.get("r", 170), o["label"], o.get("v0", .5), o.get("v1"), COR.get(o.get("cor", "a")),
                  at=o.get("at", .3), lsize=o.get("lsize", 40))
        self.seq(f"#{k} .ind", o, lambda v: f'rotation:{-135 + 270 * v:.1f}, svgOrigin:"{o.get("x", 540)} {o.get("y", 1050)}"')
        L = o.get("r", 170) * 1.5 * math.pi
        self.seq(f"#{k} .val", o, lambda v: f"strokeDashoffset:{L * (1 - v):.1f}")
        for a in o.get("arco_txt", []):
            self.svg.append(self.txt(a[0], a[1], a[2], 30, C["am"], 700))

    def c_fader(self, o):
        h = o.get("h", 620)
        self.seq_fader = h
        k = self.fader(o.get("x", 540), o.get("top", 700), o.get("h", 620), o.get("label", ""), o.get("v0", .5), o.get("v1"), at=o.get("at", .3),
                   w=o.get("w", 150), lsize=o.get("lsize", 40))
        self.seq(f"#{k} .cap", o, lambda v: f"y:{h * (1 - v):.0f}")

    def c_meter(self, o):
        x, top, h, w = o.get("x", 490), o.get("top", 720), o.get("h", 660), o.get("w", 100)
        if o.get("label"):
            self.svg.append(self.txt(x + w / 2, top + h + 56, o["label"], 36, C["cz"], 700))
        if o.get("limiar") is not None:
            y = top + h * (1 - o["limiar"])
            self.svg.append(f'<line x1="{x - 50}" y1="{y:.0f}" x2="{x + w + 50}" y2="{y:.0f}" stroke="{C["am"]}" stroke-width="7" stroke-dasharray="18 10"/>'
                            + self.txt(x + w + 64, y + 12, o.get("limiar_txt", "LIMIAR"), 36, C["am"], 800, "start"))
        k = self.meter(o.get("x", 490), o.get("top", 720), o.get("h", 660), o.get("w", 100), o.get("lo", .3), o.get("hi", .6), o.get("clip", False),
                   o.get("at", .3), o.get("lo1"), o.get("hi1"))
        self.seq(f"#{k} .lit", o, lambda v: f"scaleY:{v}, transformOrigin:\"50% 100%\"")

    def c_caminho(self, o):
        bl = o["blocos"]; n = len(bl); w = min(190, (980 - 30 * (n - 1)) // n); x0 = (1080 - (n * w + (n - 1) * 30)) / 2; y = 1000
        ids = []
        cor = COR.get(o.get("cor", "c"))
        self.svg.append(f'<line x1="{x0 + w / 2}" y1="{y + 175}" x2="{x0 + (n - 1) * (w + 30) + w / 2}" y2="{y + 175}" stroke="{cor}" stroke-width="6"/>'
                        + "".join(f'<line x1="{x0 + k * (w + 30) + w / 2}" y1="{y + 120}" x2="{x0 + k * (w + 30) + w / 2}" y2="{y + 175}" stroke="{cor}" stroke-width="4"/>' for k in range(n)))
        for k, b in enumerate(bl):
            x = x0 + k * (w + 30); i = self.id(); ids.append(i)
            hl = k == o.get("hl", -1)
            self.svg.append(f'<g id="{i}"><rect x="{x:.0f}" y="{y}" width="{w}" height="120" rx="18"{C["sh"]} fill="{C["corpo"]}" stroke="{C["am"] if hl else C["bd"]}" stroke-width="{5 if hl else 3}"/>'
                            + self.txt(x + w / 2, y + 72, b, 30 if len(b) > 5 else 34, C["am"] if hl else C["br"], 700, conta=False) + "</g>")
        dot = self.id(); xs = [x0 + k * (w + 30) + w / 2 for k in range(n)]
        if o.get("reverso"):
            xs = xs[::-1]
        self.svg.append(f'<circle id="{dot}" cx="{xs[0]:.0f}" cy="{y + 175}" r="18" fill="{cor}"/>')
        self.js.append(f'V.entra("#{" , #".join(ids)}", t0 + .05, .4, 40);')
        self.js.append(f'tl.fromTo("#{dot}", {{x:0}}, {{x:{xs[-1] - xs[0]:.0f}, duration:Math.max(.8, d*.6), ease:"none", immediateRender:false}}, t0 + .3);')
        if o.get("hl", -1) >= 0:
            self.js.append(f'V.breathe("#{ids[o["hl"]]}", t0 + .5, t0 + d, .55);')

    def c_tela(self, o):
        X0, X1, Y0, Y1 = 150, 930, 760, 1240; yc = (Y0 + Y1) / 2; esc_db = (Y1 - Y0) / 2 / 15
        fx = lambda f: X0 + (math.log10(f) - math.log10(20)) / 3 * (X1 - X0)
        def db(f, termos):
            s = 0
            for t in termos:
                if t[0] == "hp":
                    r = f / t[1]; s += 20 * math.log10(r * r / math.sqrt((1 - r * r) ** 2 + (r / .707) ** 2))
                elif t[0] == "bell":
                    s += t[2] * math.exp(-(math.log2(f / t[1])) ** 2 / (2 * (t[3] / 2.355) ** 2))
                elif t[0] == "lshelf":
                    s += t[2] / (1 + (f / t[1]) ** 2)
                elif t[0] == "hshelf":
                    s += t[2] / (1 + (t[1] / f) ** 2)
            return max(-15, min(15, s))
        def path(termos):
            pts = [(fx(20 * 10 ** (3 * k / 139)), yc - db(20 * 10 ** (3 * k / 139), termos) * esc_db) for k in range(140)]
            return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        cv = o["curvas"]; i = self.id(); cor = COR.get(o.get("cor", "c"))
        grade = "".join(f'<line x1="{fx(f):.0f}" y1="{Y0}" x2="{fx(f):.0f}" y2="{Y1}" stroke="{C["telag"]}" stroke-width="2"/>' for f in (50, 100, 200, 500, 1000, 2000, 5000, 10000))
        grade += f'<line x1="{X0}" y1="{yc}" x2="{X1}" y2="{yc}" stroke="{C["bd"]}" stroke-width="2"/>'
        rot = "".join(self.txt(fx(f), Y1 + 46, s, 30, C["telal"]) for f, s in ((100, "100"), (1000, "1k"), (10000, "10k")))
        faixa = ""
        if o.get("faixa"):
            f1, f2 = o["faixa"]; fi = self.id()
            faixa = (f'<g id="{fi}"><rect x="{fx(f1):.0f}" y="{Y0}" width="{fx(f2) - fx(f1):.0f}" height="{Y1 - Y0}" fill="{C["am"]}" opacity=".22"/>'
                     + self.txt((fx(f1) + fx(f2)) / 2, Y0 - 18, f"{o['faixa_txt']}", 34, C["am"], 700) + "</g>")
            self.js.append(f'V.fadeIn("#{fi}", t0 + d*.25, .3);')
        self.svg.append(f'<rect x="{X0 - 50}" y="{Y0 - 80}" width="{X1 - X0 + 100}" height="{Y1 - Y0 + 160}" rx="26" fill="{C["tela"]}" stroke="{C["bd"]}" stroke-width="3"{C["sh"]}/>'
                        f'{grade}{faixa}{rot}<path id="{i}" d="{path(cv[0])}" fill="none" stroke="{cor}" stroke-width="8" stroke-linejoin="round"/>')
        if len(cv) > 1:
            passo = (o.get("fim", .85) - o.get("at", .25)) / (len(cv) - 1)
            for k, termos in enumerate(cv[1:]):
                self.js.append(f'tl.to("#{i}", {{attr:{{d:"{path(termos)}"}}, duration:{o.get("dur", .7)}, ease:"fader"}}, t0 + d*{o.get("at", .25) + passo * k:.3f});')
        if o.get("cor1"):
            self.js.append(f'tl.to("#{i}", {{stroke:"{COR[o["cor1"]]}", duration:.3}}, t0 + d*{o.get("fim", .85):.2f});')

    def c_barras(self, o):
        hs = o["alturas"]; n = len(hs); w = 52; x0 = 540 - (n * w + (n - 1) * 14) / 2; base = 1300; ids = []
        for k, h in enumerate(hs):
            i = self.id(); ids.append(i); cor = C["vm"] if k == o.get("pico", -1) else (C["ci"] if k < n // 2 else C["am"])
            self.svg.append(f'<rect id="{i}" x="{x0 + k * (w + 14):.0f}" y="{base - h}" width="{w}" height="{h}" rx="6" fill="{cor}"/>')
        self.js.append(f'tl.fromTo("#{", #".join(ids)}", {{scaleY:0, transformOrigin:"50% 100%"}}, {{scaleY:1, duration:.5, ease:"stage", stagger:.04, immediateRender:false}}, t0 + .05);')
        if not o.get("sem_rotulo"):
            self.svg.append(self.txt(x0 + 40, base + 50, "GRAVE", 34, C["ci"], 700) + self.txt(x0 + n * (w + 14) - 60, base + 50, "AGUDO", 34, C["am"], 700))
        if o.get("pico", -1) >= 0:
            self.js.append(f'V.breathe("#{ids[o["pico"]]}", t0 + .7, t0 + d, .35);')
        if o.get("manta"):
            m = self.id()
            self.svg.append(f'<path id="{m}" d="M{x0 - 20},{base - 470} C{x0 + 300},{base - 470} {x0 + 520},{base - 260} {x0 + n * (w + 14) + 20},{base - 230} L{x0 + n * (w + 14) + 20},{base} L{x0 - 20},{base} Z" fill="{C["cz"]}" opacity="0"/>')
            self.js.append(f'tl.to("#{m}", {{opacity:.55, duration:.5}}, t0 + d*.35);')

    def c_circulos(self, o):
        es = o["estados"]; a, b = self.id(), self.id(); cb = COR.get(o.get("cor_b", "a"))
        x1, r1, x2, r2 = es[0]; y = 1060
        la, lb = self.id(), self.id()
        self.svg.append(f'<g id="{a}"><circle cx="0" cy="0" r="1" fill="{C["ci"]}" opacity=".9"/></g>')
        self.svg.append(f'<g id="{b}"><circle cx="0" cy="0" r="1" fill="{cb}" opacity=".93"/></g>')
        rot = (f'<g id="{la}">{self.txt(0, 0, o.get("a", "VOZ"), 44, C["ci"], 800)}</g>'
               f'<g id="{lb}">{self.txt(0, 0, o.get("b", "TECLADO"), 44, cb, 800)}</g>')
        lab = lambda x1, r1, x2, r2: f'tl.set("#{la}", {{x:{x1}, y:{y - r1 - 30}}}, t0); tl.set("#{lb}", {{x:{x2}, y:{y + r2 + 64}}}, t0);'
        self.js.append(lab(x1, r1, x2, r2))
        self.js.append(f'V.entra("#{la}, #{lb}", t0 + .2, .4, 0);')
        self.js.append(f'tl.set("#{a}", {{x:{x1}, y:{y}}}, t0); tl.set("#{a} circle", {{attr:{{r:{r1}}}}}, t0);')
        self.js.append(f'tl.set("#{b}", {{x:{x2}, y:{y}}}, t0); tl.set("#{b} circle", {{attr:{{r:{r2}}}}}, t0);')
        self.js.append(f'V.entra("#{a} circle, #{b} circle", t0 + .05, .4, 30);')
        if len(es) > 1:
            passo = .6 / (len(es) - 1)
            for k, (x1, r1, x2, r2) in enumerate(es[1:]):
                t = f"t0 + d*{o.get('at', .3) + passo * k:.2f}"
                self.js.append(f'tl.to("#{a}", {{x:{x1}, duration:.7, ease:"fader"}}, {t}); tl.to("#{a} circle", {{attr:{{r:{r1}}}, duration:.7, ease:"fader"}}, {t});')
                self.js.append(f'tl.to("#{b}", {{x:{x2}, duration:.7, ease:"fader"}}, {t}); tl.to("#{b} circle", {{attr:{{r:{r2}}}, duration:.7, ease:"fader"}}, {t});')
                self.js.append(f'tl.to("#{la}", {{x:{x1}, y:{y - r1 - 30}, duration:.7, ease:"fader"}}, {t}); tl.to("#{lb}", {{x:{x2}, y:{y + r2 + 64}, duration:.7, ease:"fader"}}, {t});')
        if o.get("sobre_amarelo"):
            j = self.id(); xm = (x1 + x2) / 2
            self.svg.append(f'<ellipse id="{j}" cx="{(es[0][0] + es[0][2]) / 2}" cy="{y}" rx="{max(30, (es[0][0] + es[0][1]) - (es[0][2] - es[0][3])) / 2:.0f}" ry="{min(es[0][1], es[0][3]) * .85:.0f}" fill="{C["br"]}" opacity="0"/>')
            self.js.append(f'tl.to("#{j}", {{opacity:.85, duration:.3}}, t0 + d*.3); V.breathe("#{j}", t0 + d*.3 + .3, t0 + d, .5);')
        self.svg.append(rot)
        if o.get("verde"):
            self.js.append(f'tl.to("#{a} circle, #{b} circle", {{fill:"{C["vd"]}", duration:.4}}, t0 + d*{o.get("verde_at", .5)});')

    def c_quiz(self, o):
        ops = o["ops"]; ids = []
        for k, op in enumerate(ops):
            i = self.id(); ids.append(i); y = 760 + k * 190
            self.svg.append(f'<g id="{i}"><rect class="bg" x="170" y="{y}" width="740" height="150" rx="26" fill="{C["corpo"]}" stroke="{C["bd"]}" stroke-width="3"{C["sh"]}/>'
                            f'<rect class="ok" x="170" y="{y}" width="740" height="150" rx="26" fill="{C["vd"]}" opacity="0"/>'
                            + self.txt(540, y + 95, op, 56, C["br"], 800) + "</g>")
        self.js.append(f'V.entra("#{", #".join(ids)}", t0 + .05, .4, 50);')
        self.js.append(f'tl.fromTo("#{", #".join(ids)}", {{x:0}}, {{x:6, duration:.6, ease:"sine.inOut", yoyo:true, repeat:Math.max(1, Math.floor(d/.6)-1), stagger:.2, immediateRender:false}}, t0 + .5);')
        if o.get("revela"):
            c = ids[o["certa"]]
            self.js.append(f'tl.to("#{c} .ok", {{opacity:1, duration:.15}}, t0 + d*.3); tl.fromTo("#{c}", {{scale:1, svgOrigin:"540 {760 + o["certa"] * 190 + 75}"}}, {{scale:1.06, duration:.18, yoyo:true, repeat:1, svgOrigin:"540 {760 + o["certa"] * 190 + 75}", immediateRender:false}}, t0 + d*.3);')
            outros = [x for x in ids if x != c]
            if outros:
                self.js.append(f'tl.to("#{", #".join(outros)}", {{opacity:.3, duration:.3}}, t0 + d*.3);')

    def c_mic(self, o):
        x, y = o.get("x", 540), o.get("y", 1150 if o.get("cardioide") else 1050); i = self.id(); tipo = o.get("tipo", "condensador")
        if tipo == "dinamico":
            cab = f'<circle cx="{x}" cy="{y - 150}" r="95" fill="{C["il"]}" stroke="{C["ild"]}" stroke-width="5"/>' + "".join(
                f'<line x1="{x - 85}" y1="{y - 150 + k * 22}" x2="{x + 85}" y2="{y - 150 + k * 22}" stroke="{C["ilm"]}" stroke-width="2"/>' for k in range(-3, 4))
            corpo = f'<path d="M{x - 55},{y - 70} L{x + 55},{y - 70} L{x + 32},{y + 230} L{x - 32},{y + 230} Z" fill="{C["il2"]}" stroke="{C["ild"]}" stroke-width="4"/>'
        elif tipo == "fita":
            cab = f'<rect x="{x - 90}" y="{y - 280}" width="180" height="260" rx="40" fill="{C["il"]}" stroke="{C["ild"]}" stroke-width="5"/>' + "".join(
                f'<line x1="{x + k * 18}" y1="{y - 255}" x2="{x + k * 18}" y2="{y - 45}" stroke="{C["ilm"]}" stroke-width="3"/>' for k in range(-4, 5))
            corpo = f'<rect x="{x - 40}" y="{y - 20}" width="80" height="230" rx="16" fill="{C["il2"]}" stroke="{C["ild"]}" stroke-width="4"/>'
        else:
            cab = f'<rect x="{x - 80}" y="{y - 300}" width="160" height="300" rx="80" fill="{C["il"]}" stroke="{C["ild"]}" stroke-width="5"/>' + "".join(
                f'<line x1="{x - 70}" y1="{y - 230 + k * 26}" x2="{x + 70}" y2="{y - 230 + k * 26}" stroke="{C["ilm"]}" stroke-width="2"/>' for k in range(7))
            corpo = f'<rect x="{x - 62}" y="{y}" width="124" height="230" rx="20" fill="{C["il2"]}" stroke="{C["ild"]}" stroke-width="4"/>'
        ondas = ""
        if o.get("ondas", True):
            ondas = "".join(f'<path class="onda" d="M{x + 130 + 40 * k},{y - 230} q{40 + 10 * k},{80} 0,{160}" fill="none" stroke="{C["ci"]}" stroke-width="6" stroke-linecap="round" opacity="0"/>'
                            f'<path class="onda" d="M{x - 130 - 40 * k},{y - 230} q-{40 + 10 * k},{80} 0,{160}" fill="none" stroke="{C["ci"]}" stroke-width="6" stroke-linecap="round" opacity="0"/>' for k in range(3))
        cabo = f'<path d="M{x},{y + 230} C{x},{y + 330} {x + 160},{y + 300} {x + 220},{y + 380}" fill="none" stroke="{C["ilm"]}" stroke-width="10"/>'
        card = ""
        if o.get("cardioide"):  # captação em coração na frente (acima) da cápsula; atrás fica a zona morta
            card = (f'<path class="card" d="M{x},{y - 240} C{x - 210},{y - 300} {x - 200},{y - 570} {x},{y - 535} C{x + 200},{y - 570} {x + 210},{y - 300} {x},{y - 240} Z" '
                    f'fill="{C["ci"]}" fill-opacity=".22" stroke="{C["ci"]}" stroke-width="6"/>')
            self.js.append(f'V.breathe("#{i} .card", t0 + .5, t0 + d, .55);')
        self.svg.append(f'<g id="{i}">{card}{cabo}{corpo}{cab}{ondas}</g>')
        self.js.append(f'V.entra("#{i}", t0 + .05, .45, 50);')
        if o.get("ondas", True):
            self.js.append(f'tl.fromTo("#{i} .onda", {{opacity:0}}, {{opacity:.9, duration:.4, yoyo:true, repeat:Math.max(1, Math.floor(d/.4)-1), stagger:.12, ease:"sine.inOut", immediateRender:false}}, t0 + .3);')

    def c_fones(self, o):
        i = self.id()
        self.svg.append(f'<g id="{i}"><path d="M250,1120 C250,880 530,880 530,1120" fill="none" stroke="{C["ild"]}" stroke-width="18"/>'
                        f'<rect x="215" y="1090" width="80" height="140" rx="30" fill="{C["il"]}" stroke="{C["ild"]}" stroke-width="5"/>'
                        f'<rect x="485" y="1090" width="80" height="140" rx="30" fill="{C["il"]}" stroke="{C["ild"]}" stroke-width="5"/>'
                        f'<circle cx="720" cy="1080" r="48" fill="{C["il"]}" stroke="{C["ild"]}" stroke-width="5"/><circle cx="860" cy="1080" r="48" fill="{C["il"]}" stroke="{C["ild"]}" stroke-width="5"/>'
                        f'<path d="M720,1128 C720,1260 860,1260 860,1128 M790,1225 L790,1330" fill="none" stroke="{C["ilm"]}" stroke-width="7"/></g>')
        self.js.append(f'V.entra("#{i}", t0 + .05, .45, 50); V.shake("#{i}", t0 + d*.45, 8, .35);')

    def c_mesa(self, o):
        """8 canais. teclas="SOLO"|"MUTE"|"HPF"|"48V"|"AUX"... (fileira de teclas; on=[i] acesas, on1=[i] acendem em at, off1=[i] apagam);
        sobe/desce=[i] faders se movem; knobs={"i":[v0,v1]}; apagados=[i]; vermelho=[i] medidor estourando; hls=[i] destaque; nomes=[8]."""
        nomes = o.get("nomes", ["VOZ", "VOZ 2", "VIOLÃO", "TEC", "BAIXO", "BUMBO", "CAIXA", "GTR"])[:8]; at = o.get("at", .3)
        tecla = o.get("teclas") or ("HPF" if o.get("hpf") else ("48V" if o.get("p48") else None))
        on = set(o.get("on", []) + o.get("hpf_on", [])); on1 = set(o.get("on1", []) + o.get("hpf1", []) + ([0, 1] if o.get("p48") else []))
        cor_t = C["vm"] if tecla == "MUTE" else C["am"]
        self.svg.append(f'<rect x="70" y="700" width="940" height="640" rx="28" fill="{C["pn"]}" stroke="{C["bd"]}" stroke-width="3"{C["sh"]}/>')
        for k, nm in enumerate(nomes):
            x = 115 + k * 100; g0 = len(self.svg)
            if tecla:
                self.botao(x - 5, 730, 80, 44, str(tecla)[:4], k in on, cor_t, on_at=at if k in on1 else None, off_at=at if k in o.get("off1", []) else None)
            kv = (o.get("knobs") or {}).get(str(k)) or [.55, None]
            self.knob(x + 35, 840, 30, "", kv[0], kv[1] if len(kv) > 1 else None, at=at)
            cap = self.id(); y0 = 1010 + (k % 3) * 25
            self.svg.append(f'<rect x="{x + 28}" y="910" width="14" height="300" rx="7" fill="{C["led"]}" stroke="{C["bd"]}" stroke-width="2"/>'
                            f'<rect id="{cap}" x="{x + 8}" y="{y0}" width="54" height="26" rx="6" fill="#D8DEEA" stroke="{C["pg"]}" stroke-width="2"/>')
            if k in o.get("sobe", []):
                self.js.append(f'tl.to("#{cap}", {{y:{925 - y0}, duration:.7, ease:"fader"}}, t0 + d*{at} + {.07 * k:.2f});')
            if k in o.get("desce", []):
                self.js.append(f'tl.to("#{cap}", {{y:{1165 - y0}, duration:.7, ease:"fader"}}, t0 + d*{at} + {.07 * k:.2f});')
            m = self.id(); ver = k in o.get("vermelho", [])
            self.svg.append(f'<rect id="{m}" x="{x + 58}" y="910" width="12" height="300" rx="3" fill="{C["vm"] if ver else C["vd"]}"/>')
            self.svg.append(self.txt(x + 35, 1262, nm, 28, C["am"] if k == o.get("hl", -1) else C["cz"], 700))
            lo, hi = (.75, .98) if ver else (.2 + .05 * (k % 3), .55 + .08 * (k % 4))
            self.js.append(f'V.meter("#{m}", t0, t0 + d, {lo}, {hi}, {.3 + .04 * k});')
            if k in o.get("apagados", []):
                self.svg[g0:] = ['<g opacity=".25">' + "".join(self.svg[g0:]) + "</g>"]
        for h in ([o["hl"]] if o.get("hl", -1) >= 0 else []) + o.get("hls", []):
            self.brilho(95 + h * 100, 795, 100, 500, at=.2)
        if o.get("p48"):
            self.botao(830, 1360, 150, 60, "48V GERAL", False, C["am"], on_at=.6, lsize=28)

    def c_seta(self, o):
        i = self.id(); x, y, tx, ty = o["x"], o["y"], o["tx"], o["ty"]
        self.svg.append(f'<g id="{i}"><line x1="{x}" y1="{y + 14}" x2="{tx}" y2="{ty}" stroke="{C["am"]}" stroke-width="4"/>'
                        f'<circle cx="{tx}" cy="{ty}" r="8" fill="{C["am"]}"/>' + self.txt(x, y, o["texto"], o.get("size", 44), C["am"], 800, o.get("anchor", "middle")) + "</g>")
        self.js.append(f'V.entra("#{i}", t0 + d*{o.get("at", .2)}, .4, 20);')

    def c_ruido(self, o):
        i = self.id(); x, y = o.get("x", 700), o.get("y", 760)
        linhas = "".join(f'<line x1="{x}" y1="{y + k * 14}" x2="{x + 60 + (k * 37) % 70}" y2="{y + k * 14}" stroke="{C["cz"]}" stroke-width="4" opacity=".7"/>' for k in range(40))
        self.svg.append(f'<g id="{i}">{linhas}</g>' + self.txt(x + 70, y - 30, "CHIADO", 40, C["cz"], 800))
        self.js.append(f'tl.fromTo("#{i}", {{scaleX:.15, transformOrigin:"0% 50%"}}, {{scaleX:1.6, duration:d*.7, ease:"none", immediateRender:false}}, t0 + d*.2); V.breathe("#{i}", t0 + .2, t0 + d, .5);')

    def c_onda(self, o):
        i = self.id(); y = 1350
        pts = " L".join(f"{120 + k * 6:.0f},{y - 120 * math.sin(k / 9):.1f}" for k in range(141))
        cl = " L".join(f"{120 + k * 6:.0f},{y - max(-70, min(70, 120 * math.sin(k / 9))):.1f}" for k in range(141))
        self.svg.append(f'<path id="{i}" d="M{pts}" fill="none" stroke="{C["ci"]}" stroke-width="7"/>')
        if o.get("achatada"):
            self.js.append(f'tl.to("#{i}", {{attr:{{d:"M{cl}"}}, stroke:"{C["vm"]}", duration:.4, ease:"hw"}}, t0 + d*.35); V.shake("#{i}", t0 + d*.35, 6, .3);')

    def c_produto(self, o, s=1.0, y0=None):
        i = self.id(); s = o.get("escala", s); cy = o.get("y", y0 or 1040)
        capas = "".join(f'<rect class="mini" x="{70 + (k % 10) * 96}" y="{(600 if k < 10 else 1440)}" width="70" height="92" rx="8" fill="none" stroke="{C["cz"]}" stroke-width="3" opacity="0"/>' for k in range(20)) if o.get("capas", True) else ""
        pdf = "".join(f'<rect x="{150 + k * 22}" y="{cy - 110 + k * 22}" width="250" height="330" rx="10" fill="{["#C9D2E6", "#DDE3EF", "#F2F5FA"][k]}" stroke="{C["pg"]}" stroke-width="2"/>' for k in range(3))
        pdf += "".join(f'<rect x="{214}" y="{cy - 40 + k * 34}" width="{170 - (k % 3) * 30}" height="12" rx="6" fill="{C["ilm"]}"/>' for k in range(7))
        tela = (f'<rect x="380" y="{cy - 230}" width="560" height="400" rx="30" fill="{C["led"]}" stroke="{C["ild"]}" stroke-width="6"/>'
                f'<rect x="420" y="{cy - 190}" width="380" height="22" rx="11" fill="{C["il"]}"/>'
                + "".join(f'<rect class="op{k}" x="420" y="{cy - 140 + k * 84}" width="480" height="64" rx="16" fill="{C["corpo"]}" stroke="{C["bd"]}" stroke-width="3"/>' for k in range(3))
                + f'<g class="info"><circle cx="880" cy="{cy - 180}" r="30" fill="{C["am"]}"/><text data-layout-ignore x="880" y="{cy - 168}" font-size="36" font-weight="800" fill="{C["bg"]}" text-anchor="middle" font-family="Barlow">i</text></g>')
        self.svg.append(f'<g id="{i}"><g class="cap">{capas}</g><g class="pr">{pdf}{tela}</g></g>')
        self.js.append(f'tl.set("#{i} .pr", {{scale:{s}, svgOrigin:"540 {cy}"}}, t0); V.entra("#{i} .pr", t0 + .05, .45, 60);')
        if capas:
            self.js.append(f'tl.to("#{i} .mini", {{opacity:.35, duration:.25, stagger:.03}}, t0 + .3);')
        self.js.append(f'tl.to("#{i} .op1", {{fill:"{C["vd"]}", duration:.2}}, t0 + d*.45); V.breathe("#{i} .info", t0 + .4, t0 + d, .4);')

    def c_cta(self, o):
        """CTA. icone=comenta|salva|marca|segue troca a imagem do curso por um ícone da ação (vídeos informativos 051+)."""
        if o.get("icone"):
            self.c_icone({"nome": o["icone"], "y": 1000})
        else:
            self.c_produto({"escala": .72, "y": 1000, "capas": False})
        i = self.id()
        selo = MARCA.get("selo", "seuperfil") if o.get("icone") else MARCA.get("selo_produto", "Curso independente · seuperfil")  # informativos não citam o produto
        self.html.append(f'<div id="{i}" class="selo">{selo}</div>')
        self.js.append(f'V.entra("#{i}", t0 + .35, .4, 20);')
        self.lidas.append(selo)

    def pill(self, texto, cor, at):
        i = self.id()
        self.html.append(f'<div id="{i}" class="pill pill-{cor}"><span>{esc(texto)}</span></div>')
        self.js.append(f'tl.fromTo("#{i} span", {{scale:.5, opacity:0}}, {{scale:1, opacity:1, duration:.3, ease:"back.out(2.2)", immediateRender:false}}, t0 + d*{at});')
        if cor == "r":
            self.js.append(f'V.shake("#{i} span", t0 + d*{at} + .3, 7, .3);')
        self.lidas.append(texto)

    # ---------- peças do lote B ----------
    def c_passos(self, o):
        n, at_ = o.get("n", 4), o["atual"]; x0 = 540 - (n - 1) * 75
        for k in range(n):
            i = self.id(); x = x0 + k * 150; y = o.get("y", 630)
            cor = C["vd"] if k < at_ else (C["am"] if k == at_ else C["corpo"])
            tc = self.sobre() if k <= at_ else C["br"]
            self.svg.append(f'<g id="{i}"><circle cx="{x}" cy="{y}" r="38" fill="{cor}" stroke="{C["bd"]}" stroke-width="4"/>'
                            + self.txt(x, y + 12, "✓" if k < at_ else str(k + 1), 36, tc, 800, conta=False) + "</g>")
            if k == at_:
                self.js.append(f'tl.fromTo("#{i}", {{scale:.4, svgOrigin:"{x} {y}"}}, {{scale:1, svgOrigin:"{x} {y}", duration:.35, ease:"back.out(2.4)", immediateRender:false}}, t0 + .15);')

    def c_caixa(self, o):
        i = self.id(); x, y = o.get("x", 820), o.get("y", 1050)
        self.svg.append(f'<g id="{i}" opacity="{.35 if o.get("apagada") else 1}"><rect x="{x - 130}" y="{y - 170}" width="260" height="340" rx="16" fill="{C["il2"]}" stroke="{C["bd"]}" stroke-width="5"{C["sh"]}/>'
                        f'<circle cx="{x}" cy="{y + 10}" r="105" fill="{C["il"]}" stroke="{C["ild"]}" stroke-width="5"/><circle class="cone" cx="{x}" cy="{y + 10}" r="40" fill="{C["ilm"]}"/></g>'
                        + self.txt(x, y + 230, o.get("label", "SUB"), 40, C["cz"], 800))
        self.js.append(f'V.entra("#{i}", t0 + .05, .45, 40);')
        if not o.get("apagada"):
            self.js.append(f'tl.fromTo("#{i} .cone", {{scale:1, svgOrigin:"{x} {y + 10}"}}, {{scale:1.25, svgOrigin:"{x} {y + 10}", duration:.2, yoyo:true, repeat:Math.max(1, Math.floor(d/.2)-1), ease:"sine.inOut", immediateRender:false}}, t0 + .3);')

    def c_bateria(self, o):
        i = self.id()
        g = (f'<line x1="790" y1="770" x2="790" y2="1330" stroke="{C["ilm"]}" stroke-width="8"/>'
             f'<ellipse class="prato" cx="790" cy="770" rx="170" ry="22" fill="#d9b44a" stroke="{C["bd"]}" stroke-width="4"/>'
             f'<ellipse class="caixa" cx="300" cy="1060" rx="130" ry="45" fill="{C["ild"]}" stroke="{C["bd"]}" stroke-width="5"/>'
             f'<rect x="170" y="1060" width="260" height="90" fill="{C["ilm"]}" stroke="{C["bd"]}" stroke-width="5"/>'
             f'<g class="tom"><ellipse cx="560" cy="900" rx="120" ry="40" fill="{C["ild"]}" stroke="{C["bd"]}" stroke-width="5"/>'
             f'<rect x="440" y="900" width="240" height="120" fill="{C["ilm"]}" stroke="{C["bd"]}" stroke-width="5"/></g>'
             f'<circle cx="540" cy="1200" r="150" fill="{C["il"]}" stroke="{C["bd"]}" stroke-width="6"/><circle cx="540" cy="1200" r="60" fill="{C["ild"]}"/>'
             f'<g class="mic"><rect x="420" y="770" width="34" height="90" rx="14" fill="{C["il2"]}" stroke="{C["ild"]}" stroke-width="4" transform="rotate(-30 437 815)"/></g>')
        if o.get("vazamento"):
            g += "".join(f'<path class="vaz" d="M{700 - k * 10},{800 + k * 18} Q{600},{760 + k * 30} {470},{810 + k * 6}" fill="none" stroke="{C["vm"]}" stroke-width="6" stroke-dasharray="14 10"/>' for k in range(3))
        self.svg.append(f'<g id="{i}">{g}</g>')
        self.js.append(f'V.entra("#{i}", t0 + .05, .45, 40);')
        if o.get("vazamento"):
            self.js.append(f'tl.fromTo("#{i} .vaz", {{strokeDashoffset:0}}, {{strokeDashoffset:-120, duration:d, ease:"none", immediateRender:false}}, t0);')
            self.js.append(f'tl.fromTo("#{i} .prato", {{rotation:0, svgOrigin:"790 770"}}, {{rotation:4, svgOrigin:"790 770", duration:.15, yoyo:true, repeat:Math.max(1, Math.floor(d/.15)-1), immediateRender:false}}, t0 + .2);')
            if o.get("some"):
                self.js.append(f'tl.to("#{i} .vaz", {{opacity:0, duration:.4}}, t0 + d*{o["some"]});')
        if o.get("tocando", True):
            self.js.append(f'tl.fromTo("#{i} .tom", {{y:0}}, {{y:8, duration:.12, yoyo:true, repeat:Math.max(1, Math.floor(d/.24)*2-1), ease:"hw", immediateRender:false}}, t0 + .3);')

    def c_porta(self, o):
        i = self.id(); x0, y0, w, h = o.get("x", 400), o.get("y", 740), 300, 520
        self.svg.append(f'<g id="{i}"><rect x="{x0 - 16}" y="{y0 - 16}" width="{w + 32}" height="{h + 16}" fill="none" stroke="{C["bd"]}" stroke-width="10"/>'
                        f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="{C["led"]}" opacity=".85"/>'
                        f'<g class="folha"><rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="{C["am"]}" stroke="{C["bd"]}" stroke-width="5"/>'
                        f'<circle cx="{x0 + w - 40}" cy="{y0 + h / 2}" r="14" fill="{C["bd"]}"/></g></g>')
        vs = o.get("abre", [0]); at_ = o.get("at", .25)
        self.js.append(f'tl.set("#{i} .folha", {{scaleX:{1 - .85 * vs[0]:.2f}, transformOrigin:"0% 50%"}}, t0); V.entra("#{i}", t0 + .05, .4, 30);')
        for k, v in enumerate(vs[1:]):
            t = at_ + (.85 - at_) * k / max(1, len(vs) - 1)
            self.js.append(f'tl.to("#{i} .folha", {{scaleX:{1 - .85 * v:.2f}, duration:.35, ease:"stage"}}, t0 + d*{t:.3f});')

    def c_gr(self, o):
        i = self.id(); x, top, h, w = o.get("x", 500), o.get("top", 740), o.get("h", 540), 90
        marcas = "".join(f'<line x1="{x - 30}" y1="{top + h * db / 12:.0f}" x2="{x}" y2="{top + h * db / 12:.0f}" stroke="{C["bd"]}" stroke-width="3"/>'
                         + self.txt(x - 40, top + h * db / 12 + 10, f"-{db}" if db else "0", 30, C["cz"], 700, "end") for db in (0, 3, 6, 9, 12))
        self.svg.append(f'<g id="{i}">{marcas}<rect x="{x}" y="{top}" width="{w}" height="{h}" rx="6" fill="{C["led"]}" stroke="{C["bd"]}" stroke-width="3"/>'
                        f'<rect class="bar" x="{x}" y="{top}" width="{w}" height="{h}" rx="6" fill="{C["vm"]}"/></g>'
                        + self.txt(x + w / 2, top + h + 60, "REDUÇÃO", 36, C["cz"], 800))
        self.js.append(f'tl.set("#{i} .bar", {{scaleY:{o.get("db0", 0) / 12:.3f}, transformOrigin:"50% 0%"}}, t0);')
        for k, db in enumerate(o.get("seq", [])):
            self.js.append(f'tl.to("#{i} .bar", {{scaleY:{db / 12:.3f}, duration:.3, ease:"stage"}}, t0 + d*{.25 + .6 * k / max(1, len(o["seq"])):.3f});')

    def c_ecos(self, o):
        """repetições do delay numa grade de tempo; estados [{n, fora, dec}] trocam ao longo da cena."""
        X0, Y0, Y1, P = 140, 760, 1300, 100
        grade = "".join(f'<line x1="{X0 + 40 + k * P}" y1="{Y0}" x2="{X0 + 40 + k * P}" y2="{Y1}" stroke="{C["cz"]}" stroke-width="3" stroke-dasharray="8 10" opacity=".7"/>' for k in range(8))
        ids = []; es = o["estados"]
        def geo(e, k):
            hh = 440 * (e.get("dec", .7) ** k) if k < e["n"] else 0
            dx = ((k * 37) % 50 - 25) if e.get("fora") else 0
            return X0 + 40 + k * P - 22 + dx, Y1 - hh, hh
        bars = ""
        for k in range(8):
            i = self.id(); ids.append(i); x, y, hh = geo(es[0], k)
            cor = C["am"] if k == 0 else (C["vm"] if o.get("vermelho") else C["ci"])
            bars += f'<rect id="{i}" x="{x:.0f}" y="{y:.0f}" width="44" height="{hh:.0f}" rx="8" fill="{cor}"/>'
        self.svg.append(f'<rect x="{X0 - 40}" y="{Y0 - 50}" width="{1080 - 2 * X0 + 80}" height="{Y1 - Y0 + 100}" rx="26" fill="{C["corpo"]}" stroke="{C["bd"]}" stroke-width="4"{C["sh"]}/>{grade}{bars}'
                        + self.txt(540, Y1 + 100, "TEMPO", 36, C["cz"], 800))
        self.js.append(f'tl.fromTo("#{", #".join(ids)}", {{scaleY:0, transformOrigin:"50% 100%"}}, {{scaleY:1, duration:.3, stagger:.08, ease:"stage", immediateRender:false}}, t0 + .05);')
        for j, e in enumerate(es[1:]):
            t = o.get("at", .35) + (.85 - o.get("at", .35)) * j / max(1, len(es) - 1)
            for k, i in enumerate(ids):
                x, y, hh = geo(e, k)
                self.js.append(f'tl.to("#{i}", {{attr:{{x:{x:.0f}, y:{y:.0f}, height:{hh:.0f}}}, duration:.5, ease:"fader"}}, t0 + d*{t:.3f});')

    def c_sala(self, o):
        i = self.id()
        povo = "".join(f'<circle cx="{220 + c * 90 + (r % 2) * 45}" cy="{1180 + r * 60}" r="24" fill="{C["cz"]}" opacity=".8"/>' for r in range(3) for c in range(7))
        ondas = "".join(f'<circle class="eco" cx="540" cy="860" r="{60 + k * 90}" fill="none" stroke="{C["ci"]}" stroke-width="6" opacity="0"/>' for k in range(5))
        self.svg.append(f'<g id="{i}"><rect x="130" y="720" width="820" height="680" fill="none" stroke="{C["bd"]}" stroke-width="10"/>'
                        f'<rect x="380" y="760" width="320" height="70" rx="10" fill="{C["il2"]}"/>{ondas}{povo}</g>')
        self.js.append(f'V.entra("#{i}", t0 + .05, .4, 30);')
        self.js.append(f'tl.fromTo("#{i} .eco", {{opacity:.9, scale:.6, svgOrigin:"540 860"}}, {{opacity:0, scale:1.4, svgOrigin:"540 860", duration:1.1, stagger:.2, repeat:Math.max(0, Math.floor(d/1.9)-1), ease:"none", immediateRender:false}}, t0 + .2);')
        if o.get("paredes"):
            self.js.append(f'tl.to("#{i} > rect:first-child", {{stroke:"{C["vm"]}", duration:.2, yoyo:true, repeat:3}}, t0 + d*.35);')

    def c_cauda(self, o):
        """palavra (bloco) + respiro (pré-delay) + cauda do reverb decaindo."""
        i = self.id(); y = 1080
        cauda = " L".join(f"{560 + k * 6},{y - 150 * math.exp(-k / 25) * (1 if k % 2 else -1):.0f}" for k in range(60))
        self.svg.append(f'<g id="{i}"><rect class="pal" x="150" y="{y - 160}" width="230" height="320" rx="20" fill="{C["am"]}"/>'
                        + self.txt(265, y + 14, "PALAVRA", 40, "#fff", 800)
                        + f'<path class="cau" d="M560,{y} L{cauda}" fill="none" stroke="{C["ci"]}" stroke-width="7"/>'
                        f'<g class="pre"><line x1="390" y1="{y + 210}" x2="550" y2="{y + 210}" stroke="{C["bd"]}" stroke-width="5"/>'
                        + self.txt(470, y + 270, "PRÉ-DELAY", 36, C["br"], 800) + "</g>"
                        + "</g>")
        self.js.append(f'V.entra("#{i} .pal", t0 + .05, .35, 30); tl.fromTo("#{i} .cau", {{opacity:0, x:-40}}, {{opacity:1, x:0, duration:.5, ease:"stage", immediateRender:false}}, t0 + d*.35);')
        self.js.append(f'V.fadeIn("#{i} .pre", t0 + d*.25, .3);')

    def c_laco(self, o):
        """laço de realimentação vermelho em volta do caminho."""
        i = self.id()
        self.svg.append(f'<path id="{i}" d="M240,1000 C240,780 840,780 840,1000 C840,1240 240,1240 240,1000" fill="none" stroke="{C["vm"]}" stroke-width="10" stroke-dasharray="40 20"/>')
        self.js.append(f'tl.fromTo("#{i}", {{strokeDashoffset:0}}, {{strokeDashoffset:-360, duration:d, ease:"none", immediateRender:false}}, t0);')
        self.js.append(f'V.breathe("#{i}", t0 + .3, t0 + d, .45);')

    # ---------- peças do lote 011-100 ----------
    def c_tecla(self, o):
        """teclas grandes da mesa. labels=[1 a 4 nomes]; acesas=[i]; acende=[i] (em at); apaga=[i]; cor a|r|g|c."""
        ls = [str(l) for l in o["labels"][:4]]; n = len(ls); cor = COR.get(o.get("cor", "a")); at = o.get("at", .35)
        w, h, fs = {1: (440, 210, 72), 2: (380, 190, 60), 3: (280, 170, 46), 4: (380, 170, 56)}[n]
        if n == 4:
            pos = [(150, 800), (550, 800), (150, 1010), (550, 1010)]
        else:
            x0 = 540 - (n * w + (n - 1) * 40) / 2
            pos = [(x0 + k * (w + 40), 1040 - h / 2) for k in range(n)]
        for k, (l, (x, y)) in enumerate(zip(ls, pos)):
            i = self.id(); on = k in o.get("acesas", [])
            self.svg.append(f'<g id="{i}"><rect x="{x:.0f}" y="{y:.0f}" width="{w}" height="{h}" rx="26" fill="{C["corpo"]}" stroke="{C["bd"]}" stroke-width="5"{C["sh"]}/>'
                            f'<rect class="on" x="{x:.0f}" y="{y:.0f}" width="{w}" height="{h}" rx="26" fill="{cor}" opacity="{1 if on else 0}"/>'
                            + self.txt(x + w / 2, y + h / 2 + fs * .35, l, fs, self.tx_on(cor) if on else C["br"], 800) + "</g>")
            self.js.append(f'V.entra("#{i}", t0 + {.05 + .08 * k:.2f}, .4, 40);')
            if k in o.get("acende", []):
                self.js.append(f'V.flick("#{i} .on", t0 + d*{at}); tl.to("#{i} text", {{fill:"{self.tx_on(cor)}", duration:.1}}, t0 + d*{at}); V.breathe("#{i} .on", t0 + d*{at} + .5, t0 + d, .75);')
            if k in o.get("apaga", []):
                self.js.append(f'tl.to("#{i} .on", {{opacity:0, duration:.1, ease:"hw"}}, t0 + d*{at}); tl.to("#{i} text", {{fill:"{C["br"]}", duration:.1}}, t0 + d*{at});')

    def _ondas(self, i, n=3):
        self.js.append(f'tl.fromTo("#{i} .onda", {{opacity:0}}, {{opacity:.9, duration:.4, yoyo:true, repeat:Math.max(1, Math.floor(d/.4)-1), stagger:.12, ease:"sine.inOut", immediateRender:false}}, t0 + .3);')

    def c_pa(self, o):
        """caixas de P.A. n=1|2; ondas=[0|1|2 por caixa] (0 muda, 2 forte); cor c|r|g das ondas."""
        n = o.get("n", 2); xs = [540] if n == 1 else [230, 850]; y = o.get("y", 1040); fs = (o.get("ondas") or [1] * n) + [1, 1]; cor = COR.get(o.get("cor", "c"))
        for k, x in enumerate(xs):
            i = self.id(); lados = (1, -1) if n == 1 else ((1,) if k == 0 else (-1,))
            ondas = "".join(f'<path class="onda" d="M{x + sg * (150 + j * 55)},{y - 110 - j * 30} q{sg * (36 + j * 10)},{110 + j * 30} 0,{220 + j * 60}" fill="none" stroke="{cor}" '
                            f'stroke-width="{12 if fs[k] > 1 else 7}" stroke-linecap="round" opacity="0"/>' for sg in lados for j in range(3)) if fs[k] else ""
            self.svg.append(f'<g id="{i}"><rect x="{x - 110}" y="{y - 230}" width="220" height="460" rx="18" fill="{C["il2"]}" stroke="{C["ild"]}" stroke-width="5"/>'
                            f'<circle cx="{x}" cy="{y - 120}" r="46" fill="{C["il"]}" stroke="{C["ild"]}" stroke-width="5"/>'
                            f'<circle cx="{x}" cy="{y + 70}" r="86" fill="{C["il"]}" stroke="{C["ild"]}" stroke-width="5"/><circle class="cone" cx="{x}" cy="{y + 70}" r="32" fill="{C["ilm"]}"/>{ondas}</g>')
            self.js.append(f'V.entra("#{i}", t0 + {.05 + .1 * k:.2f}, .45, 40);')
            if fs[k]:
                self._ondas(i)
                self.js.append(f'tl.fromTo("#{i} .cone", {{scale:1, svgOrigin:"{x} {y + 70}"}}, {{scale:1.3, svgOrigin:"{x} {y + 70}", duration:.2, yoyo:true, repeat:Math.max(1, Math.floor(d/.2)-1), ease:"sine.inOut", immediateRender:false}}, t0 + .3);')

    def c_retorno(self, o):
        """caixa de retorno (monitor de chão) apontada pra cima. x,y (ou pos); apito=True: ondas vermelhas; mudo=True: sem ondas."""
        x, y = o.get("x", 540), o.get("y", 1180); i = self.id(); cor = C["vm"] if o.get("apito") else C["ci"]
        ondas = "" if o.get("mudo") else "".join(f'<path class="onda" d="M{x - 70 - j * 34},{y - 150 - j * 50} q{70 + j * 34},{-46 - j * 8} {140 + j * 68},0" fill="none" stroke="{cor}" stroke-width="8" stroke-linecap="round" opacity="0"/>' for j in range(3))
        self.svg.append(f'<g id="{i}"><path d="M{x - 190},{y + 100} L{x + 190},{y + 100} L{x + 130},{y - 80} L{x - 110},{y - 110} Z" fill="{C["il2"]}" stroke="{C["ild"]}" stroke-width="5" stroke-linejoin="round"/>'
                        f'<circle cx="{x}" cy="{y}" r="62" fill="{C["il"]}" stroke="{C["ild"]}" stroke-width="5"/><circle cx="{x}" cy="{y}" r="24" fill="{C["ilm"]}"/>{ondas}</g>')
        self.js.append(f'V.entra("#{i}", t0 + .1, .45, 40);')
        if not o.get("mudo"):
            self._ondas(i)

    def c_aparelho(self, o):
        """tablet | notebook | celular mostrando a mesa (faders). wifi=0..3: sinal em cima (0 = sem sinal, vermelho)."""
        tipo = o.get("tipo", "tablet"); x, y = o.get("x", 540), o.get("y", 1080); i = self.id()
        w, h = {"tablet": (540, 400), "notebook": (560, 370), "celular": (270, 480)}[tipo]
        m = 3 if tipo == "celular" else 6; iw = w - 70; x0 = x - iw / 2
        fad = "".join(f'<line x1="{x0 + (j + .5) * iw / m:.0f}" y1="{y - h / 2 + 70:.0f}" x2="{x0 + (j + .5) * iw / m:.0f}" y2="{y + h / 2 - 70:.0f}" stroke="{C["telag"]}" stroke-width="8" stroke-linecap="round"/>'
                      f'<rect class="cap" x="{x0 + (j + .5) * iw / m - 22:.0f}" y="{y - 14 + (j % 3 - 1) * 40:.0f}" width="44" height="28" rx="6" fill="{C["am"] if j == 0 else C["ilm"]}"/>' for j in range(m))
        base = f'<path d="M{x - w / 2 - 60:.0f},{y + h / 2 + 6:.0f} h{w + 120} l-36,40 h-{w + 48} z" fill="{C["il"]}" stroke="{C["ild"]}" stroke-width="5" stroke-linejoin="round"/>' if tipo == "notebook" else ""
        wifi = ""
        if o.get("wifi") is not None:
            b = o["wifi"]; yw = y - h / 2 - 70; cw = C["vd"] if b else C["vm"]
            wifi = "".join(f'<path d="M{x - 34 - j * 34:.0f},{yw - j * 26:.0f} a{48 + j * 44},{48 + j * 44} 0 0 1 {68 + j * 68},0" fill="none" stroke="{cw if j < max(b, 1) else C["cz"]}" '
                           f'stroke-width="12" stroke-linecap="round" opacity="{1 if j < b else .3}"/>' for j in range(3)) + f'<circle cx="{x}" cy="{yw + 22:.0f}" r="12" fill="{cw}"/>'
        self.svg.append(f'<g id="{i}"><rect x="{x - w / 2:.0f}" y="{y - h / 2:.0f}" width="{w}" height="{h}" rx="30" fill="{C["il2"]}" stroke="{C["ild"]}" stroke-width="6"/>'
                        f'<rect x="{x - w / 2 + 24:.0f}" y="{y - h / 2 + 24:.0f}" width="{w - 48}" height="{h - 48}" rx="12" fill="{C["tela"]}"/>{fad}{base}<g class="wifi">{wifi}</g></g>')
        self.js.append(f'V.entra("#{i}", t0 + .05, .45, 40);')
        self.js.append(f'tl.fromTo("#{i} .cap", {{y:0}}, {{y:-44, duration:.7, ease:"sine.inOut", yoyo:true, repeat:Math.max(1, Math.floor(d/.7)-1), stagger:.12, immediateRender:false}}, t0 + .4);')
        if o.get("wifi") == 0:
            self.js.append(f'V.blink("#{i} .wifi", t0 + d*.3, .2, .18, 3);')

    def c_roteador(self, o):
        """roteador wi-fi com barras de sinal: barras=0..4; x,y (ou pos)."""
        x, y = o.get("x", 540), o.get("y", 1180); b = o.get("barras", 4); i = self.id(); cb = C["vd"] if b >= 3 else (C["am"] if b == 2 else C["vm"])
        bars = "".join(f'<rect class="bar" x="{x - 110 + j * 60}" y="{y - 160 - j * 46}" width="40" height="{50 + j * 46}" rx="8" fill="{cb if j < b else C["cz"]}" opacity="{1 if j < b else .3}"/>' for j in range(4))
        self.svg.append(f'<g id="{i}"><line x1="{x - 150}" y1="{y}" x2="{x - 200}" y2="{y - 150}" stroke="{C["ilm"]}" stroke-width="12" stroke-linecap="round"/>'
                        f'<line x1="{x + 150}" y1="{y}" x2="{x + 200}" y2="{y - 150}" stroke="{C["ilm"]}" stroke-width="12" stroke-linecap="round"/>'
                        f'<rect x="{x - 200}" y="{y}" width="400" height="110" rx="22" fill="{C["il2"]}" stroke="{C["ild"]}" stroke-width="5"/>'
                        f'<circle cx="{x - 130}" cy="{y + 55}" r="11" fill="{cb}"/><circle cx="{x - 90}" cy="{y + 55}" r="11" fill="{C["ilm"]}"/>{bars}</g>')
        self.js.append(f'V.entra("#{i}", t0 + .05, .45, 40); V.breathe("#{i} .bar", t0 + .6, t0 + d, .6);')

    def c_lista(self, o):
        """cartão de lista: itens=[até 5 textos curtos] (letra pequena, não conta nas 9 palavras); marcados=k (os k primeiros ganham ✓, um a um); riscados=[i]."""
        its = [str(t)[:24] for t in o["itens"][:5]]; n = len(its); k_ok = o.get("marcados", 0); h = n * 116 + 80; y0 = 1050 - h / 2
        self.svg.append(f'<rect x="150" y="{y0:.0f}" width="780" height="{h}" rx="28" fill="{C["pn"]}" stroke="{C["bd"]}" stroke-width="3"{C["sh"]}/>')
        for k, t in enumerate(its):
            yc = y0 + 98 + k * 116; i = self.id(); risc = k in o.get("riscados", [])
            self.svg.append(f'<g id="{i}"><rect x="200" y="{yc - 32:.0f}" width="64" height="64" rx="14" fill="{C["corpo"]}" stroke="{C["bd"]}" stroke-width="4"/>'
                            f'<g class="ok" opacity="0"><rect x="200" y="{yc - 32:.0f}" width="64" height="64" rx="14" fill="{C["vd"]}"/>'
                            f'<path d="M216,{yc:.0f} l14,14 l24,-28" fill="none" stroke="{self.sobre()}" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/></g>'
                            + self.txt(300, yc + 14, t, 40, C["cz"] if risc else C["br"], 700, "start", conta=False)
                            + (f'<line x1="296" y1="{yc:.0f}" x2="{300 + 22 * len(t)}" y2="{yc:.0f}" stroke="{C["vm"]}" stroke-width="5"/>' if risc else "") + "</g>")
            self.js.append(f'V.entra("#{i}", t0 + {.05 + .08 * k:.2f}, .35, 30);')
            if k < k_ok:
                self.js.append(f'tl.to("#{i} .ok", {{opacity:1, duration:.15}}, t0 + d*{.2 + .6 * k / max(1, n):.3f});')

    def c_pessoa(self, o):
        """boneco: tipo tecnico (com fone) | cantor (com microfone) | musico; x,y (ou pos); anda=[x0,x1] atravessa a cena."""
        x, y = o.get("x", 540), o.get("y", 1100); tipo = o.get("tipo", "tecnico"); i = self.id()
        if tipo == "tecnico":
            extra = (f'<path d="M{x - 78},{y - 150} a78,78 0 0 1 156,0" fill="none" stroke="{C["am"]}" stroke-width="14"/>'
                     f'<rect x="{x - 96}" y="{y - 176}" width="30" height="64" rx="12" fill="{C["am"]}"/><rect x="{x + 66}" y="{y - 176}" width="30" height="64" rx="12" fill="{C["am"]}"/>')
        elif tipo == "cantor":
            extra = f'<rect x="{x + 62}" y="{y - 96}" width="30" height="130" rx="12" fill="{C["ilm"]}" transform="rotate(25 {x + 77} {y - 30})"/><circle cx="{x + 52}" cy="{y - 104}" r="28" fill="{C["am"]}"/>'
        else:
            extra = f'<path d="M{x + 120},{y - 250} v110 a26,22 0 1 1 -18,-20 v-110 l70,20 v36 z" fill="{C["am"]}"/>'
        self.svg.append(f'<g id="{i}"><path d="M{x - 130},{y + 170} q0,-210 130,-210 q130,0 130,210 z" fill="{C["il"]}" stroke="{C["ild"]}" stroke-width="5"/>'
                        f'<circle cx="{x}" cy="{y - 150}" r="66" fill="{C["ild"]}" stroke="{C["il"]}" stroke-width="5"/>{extra}</g>')
        if o.get("anda"):
            a, b = o["anda"]
            self.js.append(f'tl.set("#{i}", {{x:{a - x}}}, t0); tl.to("#{i}", {{x:{b - x}, duration:d*.7, ease:"sine.inOut"}}, t0 + d*.15);')
        else:
            self.js.append(f'V.entra("#{i}", t0 + .05, .45, 40);')

    def c_cabo(self, o):
        """cabo com conectores e o nome: tipo xlr|p10; y; cor c|g|r; ruido=True desenha chiado em volta."""
        y = o.get("y", 1040); tipo = str(o.get("tipo", "xlr")).upper(); cor = COR.get(o.get("cor", "c")); i = self.id()
        if tipo == "P10":
            pino = (f'<line x1="150" y1="{y}" x2="84" y2="{y}" stroke="{C["ild"]}" stroke-width="14" stroke-linecap="round"/>'
                    f'<line x1="930" y1="{y}" x2="996" y2="{y}" stroke="{C["ild"]}" stroke-width="14" stroke-linecap="round"/>')
        else:
            pino = "".join(f'<circle cx="{cx}" cy="{y + dy}" r="7" fill="{C["ild"]}"/>' for cx in (180, 900) for dy in (-14, 0, 14))
        ruido = ""
        if o.get("ruido"):
            pts = " ".join(f"{275 + k * 18},{y + (60 if k % 2 else -60) * (.45 + ((k * 37) % 10) / 18):.0f}" for k in range(31))
            ruido = f'<polyline class="rd" points="{pts}" fill="none" stroke="{C["cz"]}" stroke-width="4" opacity=".85"/>'
        self.svg.append(f'<g id="{i}">{ruido}<path d="M260,{y} C420,{y - 80} 660,{y + 80} 820,{y}" fill="none" stroke="{cor}" stroke-width="16" stroke-linecap="round"/>'
                        f'<rect x="150" y="{y - 38}" width="112" height="76" rx="16" fill="{C["il2"]}" stroke="{C["ild"]}" stroke-width="5"/>'
                        f'<rect x="818" y="{y - 38}" width="112" height="76" rx="16" fill="{C["il2"]}" stroke="{C["ild"]}" stroke-width="5"/>{pino}'
                        + self.txt(540, y + 128, tipo, 44, C["cz"], 800) + "</g>")
        self.js.append(f'V.entra("#{i}", t0 + .05, .45, 40);')
        if o.get("ruido"):
            self.js.append(f'tl.fromTo("#{i} .rd", {{scaleY:.5, svgOrigin:"540 {y}"}}, {{scaleY:1.25, svgOrigin:"540 {y}", duration:.12, yoyo:true, repeat:Math.max(1, Math.floor(d/.12)-1), ease:"none", immediateRender:false}}, t0 + .3);')

    def c_icone(self, o):
        """ícone grande: nome cadeado|pendrive|ouvido|relogio|alerta|ok|x; x,y (ou pos); cor a|r|g|c; escala."""
        x, y = o.get("x", 540), o.get("y", 1050); cor = COR.get(o.get("cor", "a")); i = self.id(); f = self.sobre(); nome = o["nome"]
        F = {
            "comenta": f'<path d="M-170,-150 h340 a40,40 0 0 1 40,40 v170 a40,40 0 0 1 -40,40 h-200 l-90,80 v-80 h-50 a40,40 0 0 1 -40,-40 v-170 a40,40 0 0 1 40,-40 z" fill="{cor}"/>'
                       f'<circle cx="-80" cy="-25" r="22" fill="{f}"/><circle cx="0" cy="-25" r="22" fill="{f}"/><circle cx="80" cy="-25" r="22" fill="{f}"/>',
            "salva": f'<path d="M-110,-170 h220 a20,20 0 0 1 20,20 v320 l-130,-90 l-130,90 v-320 a20,20 0 0 1 20,-20 z" fill="{cor}"/>',
            "marca": f'<circle cx="-70" cy="-80" r="62" fill="{cor}"/><path d="M-180,130 a110,110 0 0 1 220,0 z" fill="{cor}"/>'
                     f'<circle cx="90" cy="-60" r="52" fill="{C["ilm"]}"/><path d="M0,130 a90,90 0 0 1 180,0 z" fill="{C["ilm"]}"/>',
            "envia": f'<path d="M-170,10 L170,-150 L60,170 L10,40 z" fill="{cor}"/><path d="M10,40 L170,-150 L-20,20 z" fill="{C["ilm"]}"/>',
            "segue": f'<circle cx="0" cy="0" r="160" fill="{cor}"/><rect x="-18" y="-90" width="36" height="180" rx="12" fill="{f}"/><rect x="-90" y="-18" width="180" height="36" rx="12" fill="{f}"/>',
            "cadeado": f'<path d="M-72,-30 v-80 a72,72 0 0 1 144,0 v80" fill="none" stroke="{C["ilm"]}" stroke-width="30"/><rect x="-130" y="-40" width="260" height="210" rx="30" fill="{cor}"/>'
                       f'<circle cx="0" cy="45" r="26" fill="{f}"/><rect x="-10" y="50" width="20" height="60" rx="8" fill="{f}"/>',
            "pendrive": f'<rect x="-52" y="-190" width="104" height="100" rx="8" fill="{C["ild"]}" stroke="{C["il"]}" stroke-width="5"/><rect x="-30" y="-160" width="20" height="24" fill="{C["il"]}"/>'
                        f'<rect x="10" y="-160" width="20" height="24" fill="{C["il"]}"/><rect x="-82" y="-96" width="164" height="270" rx="26" fill="{cor}"/>',
            "ouvido": f'<path d="M-30,150 C-150,60 -150,-170 10,-170 C150,-170 160,-10 70,30 C20,55 50,140 -30,150" fill="none" stroke="{cor}" stroke-width="26" stroke-linecap="round"/>'
                      f'<path d="M-40,-20 C-50,-90 50,-100 50,-30" fill="none" stroke="{cor}" stroke-width="20" stroke-linecap="round"/>',
            "relogio": f'<circle cx="0" cy="0" r="150" fill="{C["corpo"]}" stroke="{cor}" stroke-width="24"/><line class="pont" x1="0" y1="0" x2="0" y2="-100" stroke="{C["br"]}" stroke-width="14" stroke-linecap="round"/>'
                       f'<line x1="0" y1="0" x2="70" y2="30" stroke="{C["br"]}" stroke-width="14" stroke-linecap="round"/>',
            "alerta": f'<path d="M0,-170 L185,150 L-185,150 Z" fill="{cor}" stroke="{cor}" stroke-width="20" stroke-linejoin="round"/><rect x="-16" y="-70" width="32" height="120" rx="14" fill="{f}"/><circle cx="0" cy="95" r="20" fill="{f}"/>',
            "ok": f'<circle cx="0" cy="0" r="160" fill="{C["vd"]}"/><path d="M-75,5 l50,55 l100,-115" fill="none" stroke="{f}" stroke-width="34" stroke-linecap="round" stroke-linejoin="round"/>',
            "x": f'<circle cx="0" cy="0" r="160" fill="{C["vm"]}"/><path d="M-65,-65 L65,65 M65,-65 L-65,65" fill="none" stroke="#fff" stroke-width="34" stroke-linecap="round"/>',
        }
        self.svg.append(f'<g transform="translate({x} {y}) scale({o.get("escala", 1)})"><g id="{i}">{F[nome]}</g></g>')
        self.js.append(f'tl.fromTo("#{i}", {{scale:.4, opacity:0, svgOrigin:"0 0"}}, {{scale:1, opacity:1, svgOrigin:"0 0", duration:.4, ease:"back.out(2)", immediateRender:false}}, t0 + .1);')
        if nome == "relogio":
            self.js.append(f'tl.fromTo("#{i} .pont", {{rotation:0, svgOrigin:"0 0"}}, {{rotation:360, svgOrigin:"0 0", duration:d, ease:"none", immediateRender:false}}, t0);')
        elif nome in ("alerta", "x"):
            self.js.append(f'V.shake("#{i}", t0 + d*.5, 8, .3);')

    def c_balao(self, o):
        """balão de fala com texto curto (conta nas 9 palavras). texto; x,y; cor da borda."""
        x, y = o.get("x", 540), o.get("y", 860); t = str(o["texto"]); i = self.id(); w = max(280, 30 * len(t) + 110)
        self.svg.append(f'<g id="{i}"><path d="M{x - 40},{y + 60} l-24,74 l92,-74 z" fill="{C["corpo"]}" stroke="{C["bd"]}" stroke-width="4" stroke-linejoin="round"/>'
                        f'<rect x="{x - w / 2:.0f}" y="{y - 78}" width="{w}" height="150" rx="46" fill="{C["corpo"]}" stroke="{C["bd"]}" stroke-width="4"/>'
                        + self.txt(x, y + 16, t, 52, C["br"], 800) + "</g>")
        self.js.append(f'tl.fromTo("#{i}", {{scale:.5, opacity:0, svgOrigin:"{x} {y + 130}"}}, {{scale:1, opacity:1, svgOrigin:"{x} {y + 130}", duration:.35, ease:"back.out(2)", immediateRender:false}}, t0 + d*{o.get("at", .2)});')

    def c_bolo(self, o):
        """bolo em camadas (mixagem por camadas): camadas=4; acesas=k (já prontas, de baixo pra cima); acende=j (camada 1..n que entra nesta cena)."""
        n = o.get("camadas", 4); ac = o.get("acesas", 0); nova = o.get("acende"); cores = [C["ci"], C["am"], C["vd"], C["vm"]]
        self.svg.append(f'<rect x="170" y="1335" width="740" height="18" rx="9" fill="{C["ilm"]}"/>')
        for k in range(n):
            i = self.id(); w = 660 - k * 100; y = 1335 - (k + 1) * 128
            self.svg.append(f'<g id="{i}"><rect x="{540 - w / 2:.0f}" y="{y}" width="{w}" height="118" rx="22" fill="{C["corpo"]}" stroke="{C["bd"]}" stroke-width="5" stroke-dasharray="14 10"/>'
                            f'<rect class="on" x="{540 - w / 2:.0f}" y="{y}" width="{w}" height="118" rx="22" fill="{cores[k % 4]}" stroke="{C["bd"]}" stroke-width="5" opacity="{1 if k < ac else 0}"/></g>')
            self.js.append(f'V.entra("#{i}", t0 + {.05 + .07 * k:.2f}, .35, 30);')
            if nova == k + 1:
                self.js.append(f'tl.fromTo("#{i} .on", {{opacity:0, y:-70}}, {{opacity:1, y:0, duration:.5, ease:"bounce.out", immediateRender:false}}, t0 + d*{o.get("at", .3)});')


def cabeca(texto):
    """texto_tela -> título; ' · ' vira quebra de linha; palavra em CAIXA ALTA (>=2 letras) fica amarela."""
    partes = [p.strip() for p in texto.split("·")]
    def cor(p):
        return re.sub(r"\b([A-ZÀ-Ú0-9][A-ZÀ-Ú0-9]+(?: [A-ZÀ-Ú][A-ZÀ-Ú]+)*)\b", r'<em>\1</em>', esc(p))
    partes = [p for p in partes if p]
    if len(partes) > 1 and partes[0].isdigit():  # "1 · Liga o GATE" -> selo com o número na mesma linha
        partes = [f'<b class="num">{partes[0]}</b>' + cor(partes[1])] + [cor(p) for p in partes[2:]]
    else:
        partes = [cor(p) for p in partes]
    return "".join(f'<span class="ln">{p}</span>' for p in partes)  # .ln já é bloco


def palavras(s):
    return [w for w in re.split(r"[\s/·|]+", s or "") if re.search(r"[\wÀ-ú]", w)]


CSS = """@font-face{font-family:Barlow;src:url(assets/kit/fonts/barlow-latin-600-normal.woff2) format("woff2");font-weight:500 900}
@font-face{font-family:BarlowC;src:url(assets/kit/fonts/barlow-condensed-latin-700-normal.woff2) format("woff2");font-weight:700}
#root{background:%(bg)s;font-family:Barlow,sans-serif}
.fundo{position:absolute;inset:-6%%;background:radial-gradient(ellipse 60%% 38%% at 50%% 56%%,#1b3470 0%%,rgba(11,22,48,0) 70%%),
 repeating-linear-gradient(0deg,transparent 0 39px,%(grid)s 39px 41px),repeating-linear-gradient(90deg,transparent 0 39px,%(grid)s 39px 41px),%(bg)s}
.marca{position:absolute;top:96px;left:0;right:0;text-align:center;font:600 28px Barlow;letter-spacing:.32em;color:%(cz)s;opacity:.7}
.cam{position:absolute;inset:0}
.hd{position:absolute;left:70px;right:70px;top:300px;margin:0;text-align:center;font:700 96px/1.0 BarlowC;color:#fff;text-transform:none}
.hd em{font-style:normal;color:%(am)s}
.hd .ln{display:block}
.hd.cta{font-size:112px;top:330px}
.hd.l3{font-size:80px;top:200px}
.hd .num{display:inline-block;background:%(am)s;color:%(bg)s;padding:0 20px;margin-right:20px;border-radius:12px}
svg.palco{position:absolute;left:0;top:0;width:1080px;height:1920px;overflow:visible}
.pill{position:absolute;left:0;right:0;top:1570px;text-align:center}
.pill span{display:inline-block;padding:18px 40px;border-radius:60px;font:700 50px BarlowC;letter-spacing:.04em;color:#fff}
.pill-r span{background:%(vm)s}.pill-g span{background:%(vd)s;color:#06210f}.pill-a span{background:%(am)s;color:%(bg)s}
.selo{position:absolute;left:0;right:0;top:1360px;text-align:center;font:700 40px Barlow;color:%(br)s;opacity:.92}
"""

CSS_B = """@font-face{font-family:Barlow;src:url(assets/kit/fonts/barlow-latin-600-normal.woff2) format("woff2");font-weight:500 900}
@font-face{font-family:BarlowC;src:url(assets/kit/fonts/barlow-condensed-latin-700-normal.woff2) format("woff2");font-weight:700}
#root{background:%(bg)s;font-family:Barlow,sans-serif}
.fundo{position:absolute;inset:-6%%;background:radial-gradient(%(grid)s 2.4px,transparent 3px) 0 0/40px 40px,%(bg)s}
.prog{position:absolute;left:0;top:0;width:1080px;height:14px;background:%(am)s}
.marca{position:absolute;top:120px;left:80px;font:600 28px Barlow;letter-spacing:.32em;color:%(br)s;opacity:.55}
.cam{position:absolute;inset:0}
.kick{position:absolute;left:80px;top:196px;font:700 34px BarlowC;letter-spacing:.18em;color:%(am)s}
.hd{position:absolute;left:80px;right:80px;top:250px;margin:0;text-align:left;font:700 100px/1.02 BarlowC;color:%(br)s}
.hd em{font-style:normal;background:linear-gradient(transparent 58%%,#FFB48F 58%%);padding:0 6px}
.hd .ln{display:block}
.hd.cta{font-size:118px;top:300px}
.hd.l3{font-size:84px;top:240px}
.hd .num{display:inline-block;background:%(am)s;color:#fff;padding:0 22px;margin-right:22px;border-radius:12px;border:5px solid %(br)s;box-shadow:6px 6px 0 %(br)s;font-weight:700}
svg.palco{position:absolute;left:0;top:0;width:1080px;height:1920px;overflow:visible}
.pill{position:absolute;left:0;right:0;top:1580px;text-align:center;transform:rotate(-2deg)}
.pill span{display:inline-block;padding:16px 38px;border:5px solid %(br)s;border-radius:14px;box-shadow:8px 8px 0 %(br)s;font:700 54px BarlowC;letter-spacing:.04em;color:#fff}
.pill-r span{background:%(vm)s}.pill-g span{background:%(vd)s}.pill-a span{background:%(am)s}
.selo{position:absolute;left:0;right:0;top:1360px;text-align:center;font:700 40px Barlow;color:%(br)s}
"""
CSS_A = CSS

# 18 designs para os blocos 011-100 (um por bloco de 5). escuro=True usa texto escuro sobre o amarelo/acento.
# fundo: grade | pontos | diagonal | liso | linhas ; alin: left | center ; fonte: BarlowC | Barlow | Dot
_T = [
 # tema  escuro bg         grid       am         ci         vd         vm         cz         painel     tinta      fundo      alin     fonte     sombra
 ("c", 1, "#0E1A14", "#1A3326", "#B8F34A", "#4FD1C5", "#4ADE80", "#FF5C5C", "#8FB3A3", "#12261C", "#E9F5EE", "pontos", "center", "BarlowC", 0),
 ("d", 0, "#EAF2FB", "#C9DCF2", "#1D6CF2", "#0E7490", "#15803D", "#DC2626", "#4B5B70", "#FFFFFF", "#0B2545", "linhas", "left", "Barlow", 1),
 ("e", 1, "#140B24", "#2A1748", "#FF4FD8", "#59F0FF", "#5CF29A", "#FF5577", "#A795C9", "#1E1236", "#F6EEFF", "grade", "center", "BarlowC", 0),
 ("f", 0, "#E9DCC3", "#D4C29F", "#C2410C", "#0F766E", "#3F7D20", "#B91C1C", "#6B5A43", "#F7EFDF", "#2A1E12", "diagonal", "left", "BarlowC", 1),
 ("g", 1, "#0A0A0A", "#1F1F1F", "#FFD60A", "#F5F5F5", "#3DDC84", "#FF4D4D", "#9A9A9A", "#161616", "#FFFFFF", "liso", "left", "BarlowC", 0),
 ("h", 0, "#E6F7EF", "#C2E8D6", "#D9481F", "#0E7C86", "#1E9E5A", "#D93036", "#4D6B5E", "#FFFFFF", "#0F3D2E", "pontos", "center", "Barlow", 1),
 ("i", 1, "#1A0B0B", "#331616", "#FF5A36", "#FFC2A8", "#5DE08E", "#FF3B3B", "#B89A93", "#261212", "#FFF1EC", "linhas", "left", "BarlowC", 0),
 ("j", 0, "#FCE8EF", "#F3C7D7", "#E11D74", "#0E7490", "#15803D", "#C81E1E", "#7A4A60", "#FFFFFF", "#3A0D2E", "diagonal", "center", "BarlowC", 1),
 ("k", 1, "#0B2A4A", "#1C4670", "#FF9F1C", "#7FD1FF", "#4ADE80", "#FF5C5C", "#93AECB", "#0F3459", "#F2F8FF", "grade", "left", "Barlow", 0),
 ("l", 0, "#FFFFFF", "#EDEDED", "#111111", "#2563EB", "#16A34A", "#DC2626", "#5F6368", "#FFFFFF", "#111111", "liso", "left", "BarlowC", 1),
 ("m", 1, "#062A30", "#0E4048", "#FFB703", "#8ECAE6", "#52D88A", "#FF6B6B", "#86AEB4", "#0A3840", "#F0FBFC", "pontos", "center", "BarlowC", 0),
 ("n", 0, "#EEEAFB", "#D7CFF5", "#6D28D9", "#0E7490", "#15803D", "#DC2626", "#5E5480", "#FFFFFF", "#24135F", "linhas", "left", "BarlowC", 1),
 ("o", 1, "#101317", "#1C2229", "#00E5A8", "#7DD3FC", "#00E5A8", "#FF5C7A", "#8C99A6", "#161B21", "#E8FFF7", "grade", "left", "Dot", 0),
 ("p", 0, "#F5F0E1", "#E3D9BD", "#2F855A", "#0E7490", "#2F855A", "#C53030", "#5E6B4E", "#FFFDF6", "#1F3B2D", "pontos", "center", "Barlow", 1),
 ("q", 1, "#17120B", "#2E2416", "#E9B949", "#9CC8D9", "#6BD48A", "#FF6B5B", "#B3A58A", "#211A10", "#FFF8EA", "diagonal", "left", "BarlowC", 0),
 ("r", 0, "#E8F4FA", "#C8E3F0", "#E63946", "#1D6FA3", "#2A9D5C", "#C1121F", "#4F6578", "#FFFFFF", "#102A43", "grade", "left", "BarlowC", 1),
 ("s", 1, "#1B0A2E", "#2F1550", "#F72585", "#4CC9F0", "#4ADE80", "#FF4D6D", "#A38BC2", "#24103D", "#FCEFFF", "linhas", "center", "BarlowC", 0),
 ("t", 0, "#F1F3F5", "#DDE2E7", "#0284C7", "#0F766E", "#16A34A", "#DC2626", "#57606A", "#FFFFFF", "#1B1F24", "diagonal", "center", "Barlow", 1),
]
TEMAS = {t[0]: dict(zip(("tema", "escuro", "bg", "grid", "am", "ci", "vd", "vm", "cz", "pn", "br", "fundo", "alin", "fonte", "sombra"), t)) for t in _T}
FUNDO = {"grade": "repeating-linear-gradient(0deg,transparent 0 39px,%(grid)s 39px 41px),repeating-linear-gradient(90deg,transparent 0 39px,%(grid)s 39px 41px),%(bg)s",
         "pontos": "radial-gradient(%(grid)s 2.4px,transparent 3px) 0 0/40px 40px,%(bg)s",
         "diagonal": "repeating-linear-gradient(45deg,transparent 0 28px,%(grid)s 28px 31px),%(bg)s",
         "linhas": "repeating-linear-gradient(0deg,transparent 0 58px,%(grid)s 58px 61px),%(bg)s",
         "liso": "radial-gradient(ellipse 70%% 45%% at 50%% 55%%,%(grid)s 0%%,%(bg)s 75%%)"}


def mix(a, b, t):
    A = [int(a[i:i + 2], 16) for i in (1, 3, 5)]; B = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02X}" for x, y in zip(A, B))


def deriva(claro):
    """cores das ilustrações, da tela e dos medidores a partir da paleta do tema."""
    bg, br = C["bg"], C["br"]
    if claro:
        C.update(il=mix(br, bg, .2), il2=mix(br, bg, .06), ild=mix(br, bg, .82), ilm=mix(br, bg, .5), tela=C["pn"], telag=C["grid"], telal=C["cz"], led=mix(br, "#000000", .3))
    else:
        C.update(il=mix(bg, br, .24), il2=mix(bg, br, .11), ild=mix(bg, br, .8), ilm=mix(bg, br, .5), tela=mix(bg, "#000000", .4), telag=C["grid"], telal=C["cz"], led=mix(bg, "#000000", .45))


POS = {"knob": {"c": dict(x=540, y=1060, r=170), "e": dict(x=300, y=1040, r=130, lsize=36), "d": dict(x=780, y=1040, r=130, lsize=36)},
       "fader": {"c": dict(x=560, top=720, h=600, w=150), "e": dict(x=330, top=760, h=520, w=110), "d": dict(x=790, top=760, h=520, w=110)},
       "meter": {"c": dict(x=490, top=740, h=540, w=100), "e": dict(x=260, top=760, h=520, w=90), "d": dict(x=720, top=760, h=520, w=90)},
       "gr": {"c": dict(x=490), "e": dict(x=250), "d": dict(x=700)}, "porta": {"c": dict(x=390), "e": dict(x=150), "d": dict(x=630)},
       "mic": {"c": dict(x=540), "e": dict(x=300), "d": dict(x=770)}}


def com_pos(comp):
    """"pos": "c" | "e" | "d" (centro, esquerda, direita) preenche as coordenadas padrão da peça."""
    pp = comp.get("pos")
    if not pp:
        return comp
    return {**(POS.get(comp["t"], {}).get(pp) or {"x": {"c": 540, "e": 290, "d": 790}[pp]}), **comp}


def tam_titulo(tit, fonte, base, max_linhas):
    """maior tamanho de fonte (px) em que o título cabe em max_linhas (largura útil ~900 px)."""
    k = {"BarlowC": .43, "Barlow": .57, "Dot": .56}[fonte]
    partes = [x.strip() for x in tit.split("·") if x.strip()]
    for size in range(base, 59, -4):
        if sum(math.ceil(len(x) * k * size / 900) for x in partes) <= max_linhas:
            return size
    return 60


def aplica_tema(t):
    """Troca a paleta global C pelo tema t (a | b | c..t). Devolve o CSS do vídeo."""
    if t == "a":
        return CSS_A % C
    if t == "b":
        C.update(TEMA_B); COR.update({"r": C["vm"], "g": C["vd"], "a": C["am"], "c": C["ci"]}); deriva(True)
        return CSS_B % C
    T = TEMAS[t]; claro = not T["escuro"]
    C.update({k: T[k] for k in ("bg", "grid", "am", "ci", "vd", "vm", "cz", "pn", "br")})
    C.update(tema="b" if claro else "a", gerado=True, corpo=T["pn"], bd=T["br"] if claro else mix(T["bg"], T["br"], .3), pg=T["br"] if claro else "#fff",
             sh=' filter="url(#sh)"' if T["sombra"] else "")
    deriva(claro)
    COR.update({"r": C["vm"], "g": C["vd"], "a": C["am"], "c": C["ci"]})
    fam = {"BarlowC": "700 100px/1.02 BarlowC", "Barlow": "700 88px/1.06 Barlow", "Dot": "400 84px/1.12 Dot"}[T["fonte"]]
    em = ("background:linear-gradient(transparent 58%%,%(am)s55 58%%);padding:0 6px" if claro else "color:%(am)s") % C
    pill_txt = "#fff" if claro else C["bg"]
    css = f"""@font-face{{font-family:Barlow;src:url(assets/kit/fonts/barlow-latin-600-normal.woff2) format("woff2");font-weight:500 900}}
@font-face{{font-family:BarlowC;src:url(assets/kit/fonts/barlow-condensed-latin-700-normal.woff2) format("woff2");font-weight:700}}
@font-face{{font-family:Dot;src:url(assets/kit/fonts/dotgothic16-latin-400-normal.woff2) format("woff2");font-weight:400}}
#root{{background:{C["bg"]};font-family:Barlow,sans-serif}}
.fundo{{position:absolute;inset:-6%;background:{FUNDO[T["fundo"]] % C}}}
.prog{{position:absolute;left:0;top:0;width:1080px;height:12px;background:{C["am"]}}}
.marca{{position:absolute;top:118px;left:80px;right:80px;text-align:{T["alin"]};font:600 28px Barlow;letter-spacing:.32em;color:{C["br"]};opacity:.55}}
.cam{{position:absolute;inset:0}}
.kick{{position:absolute;left:80px;right:80px;text-align:{T["alin"]};top:196px;font:700 34px BarlowC;letter-spacing:.18em;color:{C["br"] if claro else C["am"]}}}
.hd{{position:absolute;left:80px;right:80px;top:250px;margin:0;text-align:{T["alin"]};font:{fam};color:{C["br"]}}}
.hd em{{font-style:normal;{em}}}
.hd .ln{{display:block}}
.hd.cta{{font-size:112px;top:300px}}
.hd.l3{{font-size:80px;top:240px}}
.hd .num{{display:inline-block;background:{C["am"]};color:{pill_txt};padding:0 20px;margin-right:20px;border-radius:12px}}
svg.palco{{position:absolute;left:0;top:0;width:1080px;height:1920px;overflow:visible}}
.pill{{position:absolute;left:0;right:0;top:1580px;text-align:center}}
.pill span{{display:inline-block;padding:16px 40px;border-radius:{14 if T["sombra"] else 60}px;{f"border:5px solid {C['br']};box-shadow:8px 8px 0 {C['br']};" if T["sombra"] else ""}font:700 52px BarlowC;letter-spacing:.04em;color:{pill_txt}}}
.pill-r span{{background:{C["vm"]}}}.pill-g span{{background:{C["vd"]}}}.pill-a span{{background:{C["am"]}}}
.selo{{position:absolute;left:0;right:0;top:1360px;text-align:center;font:700 40px Barlow;color:{C["br"]}}}
"""
    return css


def gerar(d):
    d = Path(d); rot = json.loads((d / "roteiro.json").read_text()); spec = json.loads((d / "spec.json").read_text())
    assert len(spec["cenas"]) == len(rot["cenas"]), f"spec tem {len(spec['cenas'])} cenas, roteiro tem {len(rot['cenas'])}"
    (d / "cenas").mkdir(exist_ok=True); (d / "assets/kit/fonts").mkdir(parents=True, exist_ok=True)
    for f in FONTES.glob("*.woff2"):
        shutil.copy(f, d / "assets/kit/fonts" / f.name)
    (d / "assets/kit/tema.css").write_text("/* layout genérico: ver estilo.css */\n")
    tema = spec.get("tema", "a"); b = tema != "a"  # b = tem contador de cena, barra de progresso e sombra opcional
    (d / "estilo.css").write_text(aplica_tema(tema))
    (d / "fixo.html").write_text(f'<div class="fundo"></div><div class="marca">{esc(MARCA.get("marca", "seuperfil").upper())}</div>' + ('<div class="prog"></div>' if b else ""))
    (d / "fixo.js").write_text('tl.fromTo("#fixo .fundo", {x:0, y:0}, {x:-40, y:-80, duration:FIM, ease:"none", immediateRender:false}, 0);'
                               + ('\ntl.fromTo("#fixo .prog", {scaleX:0, transformOrigin:"0% 50%"}, {scaleX:1, duration:FIM, ease:"none", immediateRender:false}, 0);' if b else ""))
    avisos = []
    ult = len(rot["cenas"])
    for n, (c, sp) in enumerate(zip(rot["cenas"], spec["cenas"]), 1):
        s = Cena(n); cta = n == ult
        for comp in sp.get("c", []):
            comp = com_pos(comp)
            getattr(s, "c_" + comp["t"])(comp)
        tit = c["texto_tela"].split("·")[0].strip() if cta else c["texto_tela"]
        if sp.get("pill"):
            antes = len(palavras(tit)) + sum(len(palavras(x)) for x in s.lidas)
            if antes + len(palavras(sp["pill"][0])) <= 9:
                s.pill(sp["pill"][0], sp["pill"][1], sp.get("pill_at", .45))
            else:
                avisos.append(f"cena {n}: pílula {sp['pill'][0]!r} omitida (a tela passaria de 9 palavras: {antes} + pílula); tire a pílula do spec ou encurte")
        l3 = " l3" if not cta and tit.count("·") >= 2 else ""  # 3 linhas: sobe e diminui para não encostar no palco
        est = ""
        if tema in TEMAS:  # título sempre cabe em 2 linhas (3 quando o texto tem 3 partes)
            fo = TEMAS[tema]["fonte"]; base = {"BarlowC": 112, "Barlow": 96, "Dot": 88}[fo] if cta else {"BarlowC": 100, "Barlow": 88, "Dot": 84}[fo]
            est = f' style="font-size:{tam_titulo(tit, fo, base, max(2, tit.count("·") + 1))}px"'
        h = f'<h1 class="hd{" cta" if cta else ""}{l3}"{est}>{cabeca(tit)}</h1>'
        corpo_svg = "".join(s.svg).replace("url(#sh)", f"url(#sh{n})")  # filtro com id único por cena
        kick = f'<div class="kick">{n:02d} / {ult:02d}</div>' if b and not cta else ""
        defs = f'<defs><filter id="sh{n}" x="-10%" y="-10%" width="130%" height="130%"><feDropShadow dx="10" dy="10" stdDeviation="0" flood-color="{C["bd"]}" flood-opacity="1"/></filter></defs>' if b else ""
        (d / f"cenas/s{n:02d}.html").write_text(f'<div class="cam">{kick}{h}<svg class="palco" viewBox="0 0 1080 1920">{defs}{corpo_svg}</svg>{"".join(s.html)}</div>')
        js = [f'tl.fromTo("#s{n:02d} .hd .ln", {{yPercent:40, opacity:0}}, {{yPercent:0, opacity:1, duration:.4, ease:"stage", stagger:.08, immediateRender:false}}, t0 + .02);',
              f'V.push("#s{n:02d} .cam", t0, d, 1, 1.035);'] + s.js
        (d / f"cenas/s{n:02d}.js").write_text("\n".join(js) + "\n")
        total = len(palavras(tit)) + sum(len(palavras(x)) for x in s.lidas)
        if total > 9:
            avisos.append(f"cena {n}: {total} palavras na tela ({tit!r} + {s.lidas})")
    return avisos


def teste():
    import tempfile
    with tempfile.TemporaryDirectory() as t:
        p = Path(t)
        (p / "roteiro.json").write_text(json.dumps({"cenas": [{"texto_tela": "GANHO não é volume"}, {"texto_tela": "Salva · Curso independente · seuperfil"}]}))
        (p / "spec.json").write_text(json.dumps({"cenas": [{"c": [{"t": "canal", "gain": .1, "gain1": .6, "hl": ["gain"]}, {"t": "tela", "curvas": [[], [["hp", 120]]]}], "pill": ["VOZ BAIXA", "r"]},
                                                         {"c": [{"t": "cta"}]}]}))
        av = gerar(p)
        h = (p / "cenas/s01.html").read_text()
        assert "<em>GANHO</em>" in h and "pill-r" in h and 'class="palco"' in h
        assert "svgOrigin" in (p / "cenas/s01.js").read_text()
        assert "Curso independente" in (p / "cenas/s02.html").read_text()
        assert av == [], av
    print("teste ok")


if __name__ == "__main__":
    teste() if sys.argv[1:] == ["--teste"] else [print("AVISO", a) for a in gerar(sys.argv[1])]
