"""Tecla R: compara logs/tecla-r/<c>.log (V2 final) com logs/tecla-r/<c>-antes.log (V2 original, sem correções nem pilha).
Um quiz só é suspeito se, depois do R, sobra mais na V2 final do que sobrava no original (mesmo quiz, mesmo desfecho).
Sobras iguais ou menores = comportamento que o original já tinha (animação contínua, foco etc.).
Uso: python3 -I tools/conferir_r.py curso ..."""
import re, sys
def falhas(f):
    d = {}
    for q, tipo, px in re.findall(r"FALHA (quiz-\d+) \(toque na (errada|certa) #\d+\): (\d+) px", open(f).read()):
        d[(q, tipo)] = int(px)
    return d
assert falhas.__doc__ is None
FOLGA = 3   # px; abaixo disso é borda de letra (TOL de cor já aplicada)
tot = 0
for c in sys.argv[1:]:
    novo, velho = falhas(f"logs/tecla-r/{c}.log"), falhas(f"logs/tecla-r/{c}-antes.log")
    susp = {k: (v, velho.get(k, 0)) for k, v in novo.items() if v > velho.get(k, 0) * 1.5 + FOLGA}
    tot += len(susp)
    print(f"{c:15} sobras: final {len(novo):2} | original {len(velho):2} | suspeitos {len(susp)}" +
          ("".join(f"\n   {q} {t}: final {a} px, original {b} px" for (q, t), (a, b) in sorted(susp.items()))))
print("suspeitos:", tot)
