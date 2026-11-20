"""Diferenças palavra a palavra roteiro × Whisper de uma voz. Uso: python3 -I tools/dif_voz.py curso id"""
import sys, difflib
sys.path.insert(0, "tools")
from comparar_voz import norm
c, i = sys.argv[1:3]
a = norm(open(f"ws/{c}/c/tools/v2/script/{i}.txt").read()); b = norm(open(f"ws/{c}/qa-vozes/whisper/{i}.txt").read())
for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b).get_opcodes():
    if op != "equal": print(" ", op, " ".join(a[i1:i2]), "->", " ".join(b[j1:j2]))
