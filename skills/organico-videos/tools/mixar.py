#!/usr/bin/env python3
"""Mixagem padrão dos vídeos de venda: música (+ falas, se houver) -> m4a final pronto para o <audio> do HyperFrames.

Uso:
  python3 mixar.py --fim 36.3 --musica energica --saida assets/mix.m4a                       # só música
  python3 mixar.py --fim 44.8 --musica calma --saida assets/mix.m4a \
                   --falas voz/c01.m4a@0.10 voz/c02.m4a@3.40 ...                             # narrado

- --musica: "calma", "energica" (faixas de ../musica) ou caminho de um arquivo. --musica-ini: segundo da faixa onde começa (padrão 0).
- Falas: cada uma no instante dado (s). Música --abaixo dB (padrão 18) abaixo da voz em LUFS, ducking leve pela voz.
- Final: loudnorm 2 passadas I=-14, TP alvo -1.5, limitador, fade-in 0.3 s cúbico, fade-out 1.2 s até --fim.
- Imprime LUFS e TP finais; sai com código 1 se o TP passar de -1.0 dBTP ou o LUFS sair de -14 +-0.6.
Teste: python3 mixar.py --teste
"""
import argparse, json, os, re, shutil, subprocess, sys, tempfile
from pathlib import Path

AQUI = Path(__file__).resolve().parent
MUSICAS = AQUI.parent / "musica"
FF = shutil.which("ffmpeg") or os.path.expanduser("~/.local/bin/ffmpeg")


def ff(*a):
    return subprocess.run([FF, "-hide_banner", "-nostats", *a], check=True, capture_output=True, text=True).stderr


def medir(path):
    e = ff("-i", str(path), "-af", "ebur128=peak=true", "-f", "null", "-")
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", e)[-1]), float(re.findall(r"Peak:\s+(-?[\d.]+) dBFS", e)[-1])


def mixar(fim, musica, saida, falas=(), abaixo=18.0, musica_ini=0.0):
    mus = MUSICAS / f"{musica}.m4a" if musica in ("calma", "energica") else Path(musica)
    assert mus.exists(), f"música não encontrada: {mus}"
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        # música cortada no tamanho do vídeo
        ff("-ss", f"{musica_ini}", "-t", f"{fim + 0.5}", "-i", str(mus), "-af", "aresample=48000",
           "-ac", "2", "-c:a", "pcm_s24le", "-y", str(d / "mus.wav"))
        if falas:
            ins, fl = [], []
            for k, (arq, t) in enumerate(falas):
                ins += ["-i", str(arq)]
                ms = int(round(t * 1000))
                fl.append(f"[{k}:a]aresample=48000,pan=stereo|c0=c0|c1=c0,adelay={ms}|{ms}[v{k}]")
            fl.append("".join(f"[v{k}]" for k in range(len(falas))) + f"amix=inputs={len(falas)}:normalize=0,apad,atrim=0:{fim + 0.5}[v]")
            ff(*ins, "-filter_complex", ";".join(fl), "-map", "[v]", "-c:a", "pcm_s24le", "-y", str(d / "voz.wav"))
            vi, _ = medir(d / "voz.wav")
            mi, _ = medir(d / "mus.wav")
            g = (vi - abaixo) - mi
            fc = (f"[1:a]volume={g:.2f}dB[m];[0:a]asplit=2[v][sc];"
                  f"[m][sc]sidechaincompress=threshold=0.03:ratio=3:attack=30:release=350:makeup=1[md];"
                  f"[v][md]amix=inputs=2:normalize=0[o]")
            ff("-i", str(d / "voz.wav"), "-i", str(d / "mus.wav"), "-filter_complex", fc, "-map", "[o]",
               "-c:a", "pcm_s24le", "-y", str(d / "soma.wav"))
            src = d / "soma.wav"
        else:
            src = d / "mus.wav"
        e = ff("-i", str(src), "-af", "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-")
        m = json.loads(e[e.rfind("{"):e.rfind("}") + 1])
        ln = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
              f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
        # apad antes do loudnorm/limitador (o lookahead come o fim) e atrim só depois do fade-out
        af = (f"apad=pad_dur=4,{ln},alimiter=limit=0.84:level=false,aresample=48000,afade=t=in:st=0:d=0.3:curve=cub,"
              f"afade=t=out:st={fim - 1.2:.3f}:d=1.2,atrim=0:{fim},asetpts=N/SR/TB")
        Path(saida).parent.mkdir(parents=True, exist_ok=True)
        ff("-i", str(src), "-af", af, "-ac", "2", "-c:a", "aac", "-b:a", "192k", "-t", f"{fim}", "-y", str(saida))
    fi, tp = medir(saida)
    ok = tp <= -1.0 and abs(fi + 14) <= 0.6
    print(f"{'OK' if ok else 'FALHA'} {saida}: {fi:.1f} LUFS, TP {tp:.1f} dBTP, {fim:.2f} s" + (f", {len(falas)} falas" if falas else ""))
    return ok


def teste():
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        ff("-f", "lavfi", "-i", "sine=f=220:d=2", "-af", "volume=-10dB", "-y", str(d / "f1.wav"))
        assert mixar(30.0, "calma", d / "a.m4a"), "só música"
        assert mixar(30.0, "calma", d / "b.m4a", falas=[(d / "f1.wav", t) for t in range(1, 28, 3)]), "narrado"
    print("teste ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["--teste"]:
        teste(); sys.exit(0)
    p = argparse.ArgumentParser()
    p.add_argument("--fim", type=float, required=True)
    p.add_argument("--musica", required=True)
    p.add_argument("--saida", required=True)
    p.add_argument("--falas", nargs="*", default=[], help="arquivo@segundos")
    p.add_argument("--abaixo", type=float, default=18.0)
    p.add_argument("--musica-ini", type=float, default=0.0)
    a = p.parse_args()
    falas = [(f.rsplit("@", 1)[0], float(f.rsplit("@", 1)[1])) for f in a.falas]
    sys.exit(0 if mixar(a.fim, a.musica, a.saida, falas, a.abaixo, a.musica_ini) else 1)
