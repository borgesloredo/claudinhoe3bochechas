#!/usr/bin/env python3
"""Checagem objetiva de um vídeo de venda (substitui as medições que cada revisor fazia à mão).

Uso: python3 checar.py <video.mp4> [--html index.html] [--dur 30-60] [--folhas DIR]
- Imprime uma linha por item: OK / AVISO / FALHA. Sai com código 1 se houver FALHA.
- --folhas DIR: grava folhas de contato (1 quadro por segundo, nos instantes 0,5 / 1,5 / 2,5 s...,
  12 quadros por folha em grade 4x3, lidos da esquerda para a direita): folha-00.png cobre 0-12 s, folha-01.png 12-24 s etc.
  O quadro da linha r, coluna c da folha k fica em t = 12k + 4r + c + 0,5 s. Olhe as folhas; abra quadro grande só onde suspeitar.
Teste: python3 checar.py --teste
"""
import argparse, html, re, shutil, os, subprocess, sys, tempfile
from pathlib import Path

FF = shutil.which("ffmpeg") or os.path.expanduser("~/.local/bin/ffmpeg")
FP = shutil.which("ffprobe") or os.path.expanduser("~/.local/bin/ffprobe")
PROIBIDO = re.compile(r"oficia(l|is)|https?://|www\.|\.com\b|\.br\b|(?<![\w.])@\w|R\$|\bpre[cç]o\b|\bcupom\b|\bdesconto\b|\(?\d{2}\)?\s?9?\d{4}-\d{4}", re.I)


def ff(*a):
    return subprocess.run([FF, "-hide_banner", "-nostats", *a], capture_output=True, text=True).stderr


def probe(f, *a):
    return subprocess.run([FP, "-v", "error", *a, "-of", "csv=p=0", str(f)], capture_output=True, text=True).stdout.strip()


def janela(f, t, d=0.02):
    m = re.search(r"max_volume: (-?[\d.]+|-inf)", ff("-ss", f"{t}", "-t", f"{d}", "-i", str(f), "-vn", "-af", "volumedetect", "-f", "null", "-"))
    return -99.0 if not m or m.group(1) == "-inf" else float(m.group(1))


def texto_visivel(src):
    s = re.sub(r"(?is)<(script|style)\b.*?</\1>|<!--.*?-->", " ", src)
    return html.unescape(re.sub(r"<[^>]+>", " ", s))


def faixas_vazias(mp4, fps=3, W=54, H=96, lim=2.0, min_s=2.0):
    """Faixas horizontais de 300 px (y 200-1670) quase lisas (desvio-padrão de cinza < lim) por >= min_s.
    Só AVISO: calibrado nos 16 vídeos aprovados de 09/11, que ainda têm de 0 a 5,7 s disso; o revisor decide."""
    raw = subprocess.run([FF, "-v", "error", "-i", str(mp4), "-vf", f"fps={fps},scale={W}:{H},format=gray", "-f", "rawvideo", "-"], capture_output=True).stdout
    n = len(raw) // (W * H); bandas = list(range(10, 69, 5)); corrida = [0] * len(bandas); achados = {}
    for k in range(n):
        f = raw[k * W * H:(k + 1) * W * H]
        for j, y0 in enumerate(bandas):
            b = f[y0 * W:(y0 + 15) * W]; m = sum(b) / len(b)
            liso = (sum((x - m) ** 2 for x in b) / len(b)) ** 0.5 < lim
            corrida[j] = corrida[j] + 1 if liso else 0
            if corrida[j] / fps >= min_s:
                ini = round((k - corrida[j] + 1) / fps, 1)
                achados[(j, ini)] = (corrida[j] / fps, 200 + j * 100, ini)
    melhores = {}
    for s, y, t in achados.values():  # uma linha por trecho de tempo, a faixa mais longa
        if t not in melhores or s > melhores[t][0]:
            melhores[t] = (s, y, t)
    return sorted(melhores.values(), reverse=True)


def checar(mp4, html_path=None, dur=(30, 60), folhas=None):
    R = []
    add = lambda nivel, msg: R.append((nivel, msg))
    d = float(probe(mp4, "-show_entries", "format=duration") or 0)
    wh = probe(mp4, "-select_streams", "v", "-show_entries", "stream=width,height")
    add("OK" if wh == "1080,1920" else "FALHA", f"resolução {wh} (alvo 1080,1920)")
    add("OK" if dur[0] <= d <= dur[1] else "FALHA", f"duração {d:.2f} s (alvo {dur[0]}-{dur[1]})")
    if not probe(mp4, "-select_streams", "a", "-show_entries", "stream=codec_name"):
        add("FALHA", "sem faixa de áudio")
    else:
        e = ff("-i", str(mp4), "-af", "ebur128=peak=true", "-f", "null", "-")
        i = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", e)[-1]); tp = float(re.findall(r"Peak:\s+(-?[\d.]+) dBFS", e)[-1])
        add("OK" if abs(i + 14) <= 0.6 else "FALHA", f"loudness {i:.1f} LUFS (alvo -14)")
        add("OK" if tp <= -1.0 else "FALHA", f"true peak {tp:.1f} dBTP (alvo <= -1)")
        fi = janela(mp4, 0.09)
        add("OK" if fi <= -24 else "FALHA", f"fade-in: 20 ms em 0,10 s = {fi:.1f} dB (alvo <= -24; use tools/mixar.py)")
        fo = janela(mp4, max(0, d - 0.12), 0.1)
        add("OK" if fo <= -24 else "FALHA", f"fade-out: últimos 0,1 s = {fo:.1f} dB (alvo <= -24)")
    fz = re.findall(r"freeze_start: ([\d.]+)", ff("-i", str(mp4), "-an", "-vf", "freezedetect=n=0.003:d=1.5", "-f", "null", "-"))
    add("OK" if not fz else "FALHA", "quadro parado > 1,5 s: " + (", ".join(f"{float(t):.1f} s" for t in fz) if fz else "nenhum"))
    bk = re.findall(r"black_start:([\d.]+) black_end:([\d.]+)", ff("-i", str(mp4), "-an", "-vf", "blackdetect=d=0.3:pix_th=0.10", "-f", "null", "-"))
    add("OK" if not bk else "AVISO", "tela preta >= 0,3 s: " + (", ".join(f"{float(a):.1f}-{float(b):.1f} s" for a, b in bk) if bk else "nenhuma"))
    vz = faixas_vazias(mp4)
    add("OK" if not vz else "AVISO", "faixa de 300 px vazia >= 2 s (defeito nº 1 dos revisores; olhe nas folhas): " +
        ("; ".join(f"y≈{y} px de {t:.1f} s por {s:.1f} s" for s, y, t in vz[:4]) if vz else "nenhuma"))
    if html_path:
        achados = sorted(set(m.group(0) for m in PROIBIDO.finditer(texto_visivel(Path(html_path).read_text(errors="ignore")))))
        add("OK" if not achados else "FALHA", "texto proibido no HTML: " + (", ".join(achados) if achados else "nenhum"))
    if folhas:
        Path(folhas).mkdir(parents=True, exist_ok=True)
        ff("-ss", "0.5", "-i", str(mp4), "-vf", "fps=1,scale=270:-1,tile=4x3", "-start_number", "0", "-y", str(Path(folhas) / "folha-%02d.png"))
        n = len(list(Path(folhas).glob("folha-*.png")))
        add("OK" if n else "FALHA", f"{n} folhas de contato em {folhas} (folha k, linha r, coluna c = 12k+4r+c+0,5 s)")
    for nivel, msg in R:
        print(f"{nivel:5s} {msg}")
    return not any(n == "FALHA" for n, _ in R)


def teste():
    with tempfile.TemporaryDirectory() as d:
        d = Path(d); v = d / "v.mp4"; h = d / "i.html"
        ff("-f", "lavfi", "-i", "testsrc2=s=1080x1920:r=30:d=31", "-f", "lavfi", "-i", "sine=f=330:d=31",
           "-af", "afade=t=in:d=0.3:curve=cub,afade=t=out:st=29.8:d=1.2,volume=-20dB", "-shortest", "-y", str(v))
        h.write_text('<style>.a{}</style><script>var u="https://cdn.x/gsap.js"</script><!-- manual oficial --><p>Garanta o seu</p>')
        assert subprocess.run([sys.executable, __file__, str(v), "--html", str(h), "--folhas", str(d / "f")]).returncode == 1  # loudness -14 falha
        assert len(list((d / "f").glob("folha-*.png"))) == 3
        h.write_text("<p>Curso oficial em www.x.com.br por R$ 97</p>")
        achou = set(m.group(0).lower() for m in PROIBIDO.finditer(texto_visivel(h.read_text())))
        assert {"oficial", "www.", "r$"} <= achou, achou
        assert not PROIBIDO.search(texto_visivel('<script>"https://x.com"</script><p>Curso independente · seuperfil</p>'))
    print("teste ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["--teste"]:
        teste(); sys.exit(0)
    p = argparse.ArgumentParser()
    p.add_argument("mp4"); p.add_argument("--html"); p.add_argument("--dur", default="30-60"); p.add_argument("--folhas")
    a = p.parse_args()
    lo, hi = (float(x) for x in a.dur.split("-"))
    sys.exit(0 if checar(a.mp4, a.html, (lo, hi), a.folhas) else 1)
