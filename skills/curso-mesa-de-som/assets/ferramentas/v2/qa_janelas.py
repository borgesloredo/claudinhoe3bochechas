# Transcreve em janelas curtas e independentes, para separar "Whisper pulou" de "a voz não disse".
# Uso: <python do mlx-whisper> qa_janelas.py <curso> <id> ...  Saída: tools/v2/qa-out/whisper-janelas/<id>.txt
import difflib, os, re, sys
import mlx_whisper
from mlx_whisper.audio import load_audio
SR, JAN, PASSO = 16000, 25, 22
def norm(t): return re.sub(r"[^\wàáâãéêíóôõúüç]+", " ", t.lower()).split()
c = sys.argv[1]; out = f"{c}/tools/v2/qa-out/whisper-janelas"; os.makedirs(out, exist_ok=True)
for i in sys.argv[2:]:
    a = load_audio(f"{c}/08-slides-v2/audio/{i}.m4a"); textos = []
    for ini in range(0, max(1, len(a) - 3 * SR), PASSO * SR):
        r = mlx_whisper.transcribe(a[ini:ini + JAN * SR], path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language="pt", condition_on_previous_text=False, temperature=0.0, initial_prompt=None)
        textos.append(r["text"].strip())
    t = "\n".join(textos); open(f"{out}/{i}.txt", "w", encoding="utf-8").write(t + "\n")
    roteiro = norm(open(f"{c}/tools/v2/script/{i}.txt", encoding="utf-8").read()); ouvido = norm(t)
    sm = difflib.SequenceMatcher(None, roteiro, ouvido, autojunk=False)
    falta = [" ".join(roteiro[x1:x2]) for op, x1, x2, _, _ in sm.get_opcodes() if op in ("delete", "replace") and x2 - x1 >= 3 and not any(ch.isdigit() for ch in " ".join(ouvido[_:_]))]
    print(i, f"{len(a)/SR:.0f}s", f"{len(roteiro)/(len(a)/SR):.2f}p/s", "FALTA:", " | ".join(falta), flush=True)
