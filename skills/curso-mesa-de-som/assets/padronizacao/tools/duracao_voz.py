"""Acha voz cortada: duração do .m4a novo × tamanho do roteiro (~17 caracteres/s nessa voz). Uso: python3 -I tools/duracao_voz.py curso ..."""
import sys, os, subprocess, glob
FP = os.path.expanduser("~/.local/bin/ffprobe")
ruins = 0
for c in sys.argv[1:]:
    for a in sorted(glob.glob(f"ws/{c}/audio-novo/*.m4a")):
        i = os.path.basename(a)[:-4]
        d = float(subprocess.run([FP, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", a], capture_output=True, text=True).stdout or 0)
        e = len(open(f"ws/{c}/c/tools/v2/script/{i}.txt", encoding="utf-8").read()) / 17.1
        if d / e < 0.85 or d / e > 1.4:
            ruins += 1; print(f"{c} {i} {d:.0f}s esperado~{e:.0f}s razão {d/e:.2f}")
print("suspeitos:", ruins)
