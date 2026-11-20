"""Roteiro × transcrição do Whisper das vozes regravadas (06/11/2026). Uso: python3 -I tools/comparar_voz.py curso ...
Nota = semelhança das palavras (0–1, difflib) depois de tirar acento e pontuação. A grafia fonética do roteiro ("pê ême")
e números por extenso baixam a nota sem ser erro; abaixo de LIMITE a voz é listada para leitura humana."""
import sys, re, difflib, unicodedata, os
LIMITE = 0.80
def norm(t):
    t = unicodedata.normalize("NFD", t.lower())
    t = "".join(ch for ch in t if unicodedata.category(ch) != "Mn")
    return re.findall(r"[a-z0-9]+", t)
assert norm("Pê, Ême!") == ["pe", "eme"]
if __name__ == "__main__":
    for c in sys.argv[1:]:
        V = f"ws/{c}/c/tools/v2/script"; W = f"ws/{c}/qa-vozes/whisper"
        for i in open(f"ws/{c}/vozes.txt").read().split():
            w = f"{W}/{i}.txt"
            if not os.path.exists(w): print(f"{c} {i} SEM TRANSCRIÇÃO"); continue
            a, b = norm(open(f"{V}/{i}.txt").read()), norm(open(w).read())
            r = difflib.SequenceMatcher(None, a, b).ratio()
            print(f"{c:15} {i:8} {r:.2f} {'LER' if r < LIMITE else 'ok'}")
