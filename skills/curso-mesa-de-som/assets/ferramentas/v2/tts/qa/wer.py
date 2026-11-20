import sys, re, difflib, unicodedata
def norm(t):
    t = t.lower(); t = re.sub(r"[^\wàáâãéêíóôõúüç]+", " ", t); return t.split()
a, b = norm(open(sys.argv[1]).read()), norm(open(sys.argv[2]).read())
sm = difflib.SequenceMatcher(None, a, b, autojunk=False); err = 0
for op, i1, i2, j1, j2 in sm.get_opcodes():
    if op != "equal":
        err += max(i2-i1, j2-j1); print(op, " ".join(a[i1:i2]), "->", " ".join(b[j1:j2]))
print(f"palavras={len(a)} diffs={err} WER~{err/len(a):.3f}")
