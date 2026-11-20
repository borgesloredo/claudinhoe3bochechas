#!/usr/bin/env python3
"""Monta o index.html de um vídeo de venda a partir de peças pequenas (o construtor não escreve gerador próprio).

Uso (dentro da pasta da variante, projeto HyperFrames já criado):
  python3 <G>/tools/montar.py . --musica energica                 # só música
  python3 <G>/tools/montar.py . --musica calma --voz              # narrado: tempos seguem voz/cNN.m4a (NN = nº da cena)

Peças que o construtor escreve (todas opcionais menos roteiro.json):
  roteiro.json            {cenas:[{t_ini,t_fim,texto_tela,fala?,visual,motion}]}  (o do workflow)
  cenas/sNN.html          marcação da cena NN (vai dentro de <section id="sNN" class="clip scene">). Sem arquivo: legenda padrão com o texto_tela.
  cenas/sNN.js            animação da cena: corpo de função com (t0, d, V, tl) -> ex.: V.words("#s03 .word", t0 + .1); V.push("#s03 .cam", t0, d);
  fixo.html / fixo.js     camada que atravessa o vídeo todo (fundo da mesa, selo, marca). fixo.js recebe (FIM, S, V, tl).
  estilo.css              CSS do vídeo (o kit assets/kit/tema.css entra antes, automático).
  ajustes.json            {"min": {"3": 4.0}, "off": {"1": 0.3}}: duração mínima e atraso da voz por cena (narrado).
Qualquer elemento com data-palavras vira <span class="word"> por palavra (para V.words).
Saídas: tempos.json, assets/mix.m4a (via mixar.py), index.html, ROTEIRO-FINAL.md. Depois: lint, check, render, checar.py.
Teste: python3 montar.py --teste
"""
import argparse, html, json, math, re, shutil, subprocess, sys, tempfile, os
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import mixar  # noqa: E402

FP = shutil.which("ffprobe") or os.path.expanduser("~/.local/bin/ffprobe")
GSAP = ('<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>\n'
        '<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/CustomEase.min.js"></script>')
BASE_CSS = """html,body{margin:0;background:#000}
#root{position:relative;width:1080px;height:1920px;overflow:hidden}
.scene,.fixo{position:absolute;inset:0;overflow:hidden}
.word{display:inline-block;will-change:transform}
.cap-padrao{position:absolute;left:90px;right:90px;top:300px;font-size:96px;line-height:1.05;font-weight:800;color:#fff}"""


def dur(f):
    return float(subprocess.check_output([FP, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(f)]))


def q30(t):
    return round(math.ceil(t * 30 - 1e-6) / 30, 3)


def palavras(src):
    def wrap(m):
        txt = m.group(3)
        sp = " ".join(f'<span class="word">{w}</span>' for w in txt.split())
        return m.group(1) + sp + m.group(4)
    return re.sub(r'(<(\w+)\b[^>]*\bdata-palavras\b[^>]*>)([^<]*)(</\2>)', wrap, src)


def tempos(d, rot, voz, aj):
    cenas = rot["cenas"]; n = len(cenas)
    mn = {int(k): v for k, v in aj.get("min", {}).items()}; off = {int(k): v for k, v in aj.get("off", {}).items()}
    S, VZ, falas = [0.0], {}, []
    for i, c in enumerate(cenas, 1):
        base = mn.get(i, round(c["t_fim"] - c["t_ini"], 3))
        fim = S[-1] + base
        if voz and (c.get("fala") or "").strip():
            f = d / "voz" / f"c{i:02d}.m4a"
            assert f.exists(), f"falta {f} (cena {i} tem fala)"
            VZ[i] = round(S[-1] + off.get(i, 0.10), 3)
            fim = max(fim, VZ[i] + dur(f) + 0.25)
            falas.append((f, VZ[i]))
        S.append(q30(fim))
    return S, VZ, falas


def montar(d, musica="calma", voz=False, musica_ini=0.0, abaixo=18.0):
    d = Path(d).resolve()
    rot = json.loads((d / "roteiro.json").read_text()); rot = rot.get("roteiro", rot)
    aj = json.loads((d / "ajustes.json").read_text()) if (d / "ajustes.json").exists() else {}
    S, VZ, falas = tempos(d, rot, voz, aj)
    FIM = S[-1]; n = len(rot["cenas"])
    (d / "tempos.json").write_text(json.dumps({"S": S, "voz": VZ, "fim": FIM}, indent=1))
    if musica != "nenhuma":
        assert mixar.mixar(FIM, musica, d / "assets/mix.m4a", falas, abaixo, musica_ini), "mixagem fora do alvo"
    kit = d / "assets/kit/tema.css"
    css = (kit.read_text().replace("url(fonts/", "url(assets/kit/fonts/").replace("url('fonts/", "url('assets/kit/fonts/").replace('url("fonts/', 'url("assets/kit/fonts/') if kit.exists() else "")
    css += "\n" + BASE_CSS + "\n" + ((d / "estilo.css").read_text() if (d / "estilo.css").exists() else "")
    ler = lambda p: (d / p).read_text() if (d / p).exists() else ""
    corpo, js = [], []
    if ler("fixo.html"):
        corpo.append(f'<div id="fixo" class="clip fixo" data-start="0" data-duration="{FIM}" data-track-index="2" data-track-kind="graphics">\n{palavras(ler("fixo.html"))}\n</div>')
    if ler("fixo.js"):
        js.append(f"((FIM, S, V, tl) => {{\n{ler('fixo.js')}\n}})(FIM, S, V, tl);")
    for i, c in enumerate(rot["cenas"], 1):
        sid = f"s{i:02d}"; t0, t1 = S[i - 1], S[i]
        h = ler(f"cenas/{sid}.html")
        if not h:
            txt = html.escape((c.get("texto_tela") or "").split(" | ")[0])
            h = f'<h1 class="cap-padrao" data-palavras>{txt}</h1>'
        corpo.append(f'<section id="{sid}" class="clip scene" data-start="{t0}" data-duration="{round(t1 - t0, 3)}" data-track-index="1" data-track-kind="graphics">\n<!-- cena {i}: {html.escape(c.get("texto_tela") or "")} -->\n{palavras(h)}\n</section>')
        cj = ler(f"cenas/{sid}.js") or f'V.words("#{sid} .word", t0 + 0.1); V.push("#{sid}", t0, d);'
        js.append(f"/* cena {i} */ ((t0, d, V, tl) => {{\n{cj}\n}})(S[{i - 1}], {round(t1 - t0, 3)}, V, tl);")
    audio = f'<audio id="mix" class="clip" src="assets/mix.m4a" data-start="0" data-duration="{FIM}" data-track-index="10" data-volume="1"></audio>' if musica != "nenhuma" else ""
    doc = f"""<!doctype html>
<!-- GERADO por tools/montar.py: edite cenas/, fixo.*, estilo.css ou roteiro.json e rode o montar de novo. -->
<html lang="pt-BR">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=1080, height=1920" />
<title>{html.escape(rot.get('nome') or rot.get('id') or 'video')}</title>
{GSAP}
<style>
{css}
</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{FIM}" data-width="1080" data-height="1920">
{chr(10).join(corpo)}
{audio}
</div>
<script>
{(AQUI / 'vv.js').read_text()}
const tl = gsap.timeline({{ paused: true }});
const V = VV(tl);
const S = {json.dumps(S)}, VOZ = {json.dumps({str(k): v for k, v in VZ.items()})}, FIM = {FIM};
{chr(10).join(js)}
tl.set({{}}, {{}}, FIM);
window.__timelines = window.__timelines || {{}};
window.__timelines["main"] = tl;
</script>
</body>
</html>
"""
    (d / "index.html").write_text(doc)
    L = [f"# Roteiro final · {rot.get('id', '')} ({FIM:.2f} s)", "", "| # | tempo | texto na tela | fala | visual |", "|---|---|---|---|---|"]
    for i, c in enumerate(rot["cenas"], 1):
        cel = lambda s: (s or "").replace("|", "/").replace("\n", " ")
        L.append(f"| {i} | {S[i - 1]:.2f}–{S[i]:.2f} | {cel(c.get('texto_tela'))} | {cel(c.get('fala'))} | {cel(c.get('visual'))[:140]} |")
    (d / "ROTEIRO-FINAL.md").write_text("\n".join(L) + "\n")
    print(f"OK index.html: {n} cenas, {FIM:.2f} s" + (f", {len(falas)} falas" if falas else "") + "; tempos.json e ROTEIRO-FINAL.md gravados")
    return FIM


def teste():
    with tempfile.TemporaryDirectory() as t:
        d = Path(t); (d / "voz").mkdir(); (d / "cenas").mkdir()
        rot = {"id": "t", "duracao_s": 30, "cenas": [
            {"t_ini": 0, "t_fim": 3, "texto_tela": "Primeira cena", "fala": "uma fala", "visual": "v", "motion": "m"},
            {"t_ini": 3, "t_fim": 27, "texto_tela": "Meio", "visual": "v", "motion": "m"},
            {"t_ini": 27, "t_fim": 30, "texto_tela": "Garanta o seu", "visual": "v", "motion": "m"}]}
        (d / "roteiro.json").write_text(json.dumps(rot))
        subprocess.run([mixar.FF, "-v", "error", "-f", "lavfi", "-i", "sine=f=220:d=3.5", "-y", str(d / "voz/c01.m4a")], check=True)
        (d / "cenas/s02.html").write_text('<div class="cam"><p id="x" data-palavras>duas palavras</p></div>')
        (d / "cenas/s02.js").write_text('V.words("#s02 .word", t0); V.lit("#x", t0 + 1);')
        fim = montar(d, "calma", voz=True)
        S = json.loads((d / "tempos.json").read_text())["S"]
        assert S[1] == q30(0.10 + 3.5 + 0.25) and abs(fim - (S[1] + 24 + 3)) < 0.05, S
        h = (d / "index.html").read_text()
        assert h.count('class="clip scene"') == 3 and '<span class="word">duas</span>' in h and 'id="mix"' in h and "function VV" in h
        assert (d / "assets/mix.m4a").exists() and "Garanta o seu" in (d / "ROTEIRO-FINAL.md").read_text()
    print("teste ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["--teste"]:
        teste(); sys.exit(0)
    p = argparse.ArgumentParser()
    p.add_argument("dir"); p.add_argument("--musica", default="calma"); p.add_argument("--voz", action="store_true")
    p.add_argument("--musica-ini", type=float, default=0.0); p.add_argument("--abaixo", type=float, default=18.0)
    a = p.parse_args()
    montar(a.dir, a.musica, a.voz, a.musica_ini, a.abaixo)
