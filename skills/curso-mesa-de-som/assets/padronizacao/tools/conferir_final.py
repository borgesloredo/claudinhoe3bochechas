"""Lê logs/final/*.log e separa as falhas: (1) navegação/ordem/JS = erro de verdade; (2) diferença de imagem em slide que o
corrigir.py mudou de propósito = esperado; (3) ruído já conhecido do original; (4) o resto = investigar.
Uso: python3 -I tools/conferir_final.py"""
import re, glob, os, subprocess, tempfile, sys
# Ruído conhecido de cada curso: ("<curso>", "aula"|"v2", "<id do slide>"). Só entra aqui o que foi provado ruído:
# o slide passou sozinho (--so) ou o original comparado com ele mesmo também varia. Registre o motivo no relatório.
RUIDO = set()
def secoes(h):
    return {m.group(1): m.group(0) for m in re.finditer(r'<section\b[^>]*\bid="([^"]+)"[\s\S]*?(?=<section\b[^>]*\bid="|$)', h)}
mudados = {}
def mudou(c):
    if c not in mudados:
        a = f"ws/{c}/antes/v2/08-slides-v2/index.html"; s = set()
        if os.path.exists(f"ws/{c}/corrigir.py"):
            t = tempfile.mktemp(suffix=".html"); subprocess.run(["python3", "-I", f"ws/{c}/corrigir.py", a, t], check=True, capture_output=True)
            A, B = secoes(open(a).read()), secoes(open(t).read()); s = {i for i in A if A[i] != B.get(i)}
            # estilo novo no <head> (ex.: LS9 esconde peças por CSS) muda os quizzes que ele cita
            ha, hb = open(a).read().split("<body")[0], open(t).read().split("<body")[0]
            if ha != hb: s |= set(re.findall(r"#(quiz-\d+)", hb)) - set(re.findall(r"#(quiz-\d+)", ha))
            # mudança por JS/CSS fora da seção (ex.: axios32 oculta a lupa até o toque): vale o rótulo "# quiz-N:" do corrigir.py
            s |= set(re.findall(r"^#.*?\b(quiz-\d+):", open(f"ws/{c}/corrigir.py").read(), re.M))
        mudados[c] = s
    return mudados[c]
ruim = 0
for f in sorted(glob.glob("logs/final/*-*-*.log")):
    m = re.match(r"logs/final/(.+)-(aula|v2)-(chromium|webkit)\.log$", f); c, k, nav = m.groups()
    t = open(f).read(); cab = re.search(r"erros JS novos: (\d+)", t)
    if not cab: print(f"{c} {k} {nav}: SEM RESULTADO"); ruim += 1; continue
    esp, rui, inv = [], [], []
    if int(cab.group(1)): inv.append(f"{cab.group(1)} erros JS novos")
    for l in re.findall(r"FALHA (.+)", t):
        mm = re.match(r"(\S+): \d+ px diferentes", l)
        if not mm: inv.append(l); continue
        i = mm.group(1)
        if (c, k, i) in RUIDO: rui.append(i)
        elif k == "v2" and i in mudou(c): esp.append(i)
        else: inv.append(l)
    ruim += bool(inv)
    print(f"{c:31} {k:4} {nav:8} esperado={len(esp):2} ruído={','.join(rui) or '-'} {'INVESTIGAR: ' + ' | '.join(inv) if inv else 'ok'}")
print("a investigar:", ruim)
