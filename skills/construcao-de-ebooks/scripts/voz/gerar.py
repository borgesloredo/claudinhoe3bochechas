"""Roteiros do autoestudo (.txt) -> áudio .m4a com Gemini TTS, voz Puck.

Uso (via ../voz.sh, que fornece as chaves):
  voz.sh roteiro.txt saida.m4a         # um arquivo (1 pedido)
  voz.sh pasta_roteiros/ pasta_saida/  # todos os pendentes, em lotes de TTS_LOTE por pedido (retomável)
  voz.sh --lint pasta_roteiros/        # só a checagem de risco, sem pedido e sem chave
  voz.sh --teste                       # autoteste

1 pedido com as falas do lote, corte pelo alinhamento do Whisper, -16 LUFS, conferência por fala.
Cota do plano grátis: 10 pedidos por dia por chave.
"""
import os, re, sys, json, shutil, importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("gen_gemini", HERE / "gen_gemini.py")
g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g)

LOTE = int(os.environ.get("TTS_LOTE", "5"))          # roteiros por pedido (~280-380 palavras cada; 5 testado em 17/11: inteiros, sem falha)
MAX_PALAVRAS = int(os.environ.get("TTS_MAX_PALAVRAS", "1900"))  # teto de palavras por pedido (~8 min de audio; o limite do modelo é ~10 min)
SAIDA = None                                         # definida no main(): fica no projeto, nunca dentro da skill
os.environ.setdefault("HF_HUB_OFFLINE", "1")

# Conferencia tolerante: o gen_gemini marca QUALQUER palavra diferente (bom para falas de 5 s dos videos). Num roteiro de
# ~300 palavras sempre aparece homofono ("nesta"->"nessa", "secao"->"sessao"), e no teste de 14/11 os 3 roteiros cairam
# em CONFERIR so por isso. Aqui marca so trecho faltando/sobrando/trocado de 3+ palavras ou semelhanca < 96%.
_conferir = g.conferir
def _conferir_curso(fala, palavras, ini, fim):
    dif = _conferir(fala, palavras, ini, fim)
    if not dif:
        return dif
    import difflib
    esp = g.norm(fala); ouv = g.norm(" ".join(p["w"] for p in palavras if p["s"] >= ini - 0.05 and p["e"] <= fim + 0.05))
    sm = difflib.SequenceMatcher(None, esp, ouv, autojunk=False)
    grandes = [d for d, (op, a, b, c, e) in zip(dif, [o for o in sm.get_opcodes() if o[0] != "equal"]) if max(b - a, e - c) >= 3]
    return grandes + ([f"semelhanca {sm.ratio():.3f} < 0,96 ({len(dif)} trocas)"] if sm.ratio() < 0.96 else [])
g.conferir = _conferir_curso


def em_dia(t, s):
    return s.exists() and s.stat().st_mtime >= t.stat().st_mtime


def riscos(t):
    return g.riscos([" ".join(t.read_text().split())])


def lotes(pares):
    out, atual, n = [], [], 0
    for t, s in pares:
        w = len(t.read_text().split())
        if atual and (len(atual) >= LOTE or n + w > MAX_PALAVRAS):
            out.append(atual); atual, n = [], 0
        atual.append((t, s)); n += w
    return out + ([atual] if atual else [])


def gera(lote):
    """1 pedido. Devolve (status, conferir): status = 'ok' | 'conferir' | 'cota' | 'alinhamento' | 'erro: ...'."""
    pasta = SAIDA / lote[0][0].stem
    shutil.rmtree(pasta, ignore_errors=True); pasta.mkdir(parents=True)
    tmp = [(t, pasta / s.name) for t, s in lote]
    sys.argv = ["gen_gemini.py", "--aceito-risco"] + [str(x) for p in tmp for x in p]  # o risco ja foi checado por arquivo
    try:
        g.main(); cod = 0
    except SystemExit as e:
        cod = e.code
    except Exception as e:  # Whisper/ffmpeg falhou: registra e segue para o proximo lote
        cod = f"{type(e).__name__}: {e}"
    for (t, s), (_, p) in zip(lote, tmp):  # move o que saiu (mantem a data: fica "em dia" em relacao ao .txt)
        if p.exists():
            s.parent.mkdir(parents=True, exist_ok=True); os.replace(p, s)
    conf = (pasta / "qa" / "conferencia.txt")
    conferir = [l for l in conf.read_text().split("\n") if l] if conf.exists() else []
    if cod in (0, None):
        (pasta / "qa" / "gemini-take.wav").unlink(missing_ok=True)  # take so fica guardado quando ha fala a conferir
        return "ok", []
    if cod == 2:
        return "conferir", conferir
    msg = str(cod)
    if "cota do dia" in msg or "429 em todas" in msg:
        return "cota", []
    if "alinhamento falhou" in msg:
        return "alinhamento", []
    return f"erro: {msg[:300]}", []


def main():
    global SAIDA
    a = sys.argv[1:]
    if a == ["--teste"]:
        g.conferir = _conferir  # o autoteste do motor espera a conferencia original (palavra a palavra)
        g._teste()
        g.conferir = _conferir_curso
        longa = " ".join(["a pele certa pede limpeza leve e um cuidado bom todo dia"] * 4)  # ~50 palavras, como um trecho de roteiro
        ouv = [{"w": x, "s": 0, "e": 1} for x in longa.replace("leve", "breve", 1).split()]
        assert _conferir_curso(longa, ouv, 0, 1) == [], "tolerante: 1 palavra trocada nao deve marcar"
        assert _conferir_curso(longa, ouv[:6], 0, 1), "tolerante: trecho faltando deve marcar"
        return print("conferencia tolerante ok")
    if a[:1] == ["--lint"]:
        txts = sorted(Path(a[1]).glob("*.txt")) if Path(a[1]).is_dir() else [Path(x) for x in a[1:]]
        ruins = {t: riscos(t) for t in txts}
        ruins = {t: r for t, r in ruins.items() if r}
        for t, r in ruins.items():
            print(f"{t.name}:\n" + "\n".join(r))
        print(f"lint: {len(txts) - len(ruins)}/{len(txts)} roteiros sem risco")
        sys.exit(1 if ruins else 0)
    if len(a) != 2:
        sys.exit(__doc__)
    src, dst = Path(a[0]), Path(a[1])
    qa = (dst if src.is_dir() else dst.parent).resolve().parent / "qa" / "voz"
    qa.mkdir(parents=True, exist_ok=True)
    SAIDA = qa / "takes"
    if src.is_dir():
        dst.mkdir(parents=True, exist_ok=True)
        pares = [(t, dst / (t.stem + ".m4a")) for t in sorted(src.glob("*.txt"))]
    else:
        pares = [(src, dst)]
    pend = [(t, s) for t, s in pares if not em_dia(t, s)]
    if not pend:
        return print("nada a gerar (saidas em dia)")
    risco = [(t, s) for t, s in pend if riscos(t)]
    for t, _ in risco:
        print(f"PULADO (risco, nenhum pedido gasto): {t.name}\n" + "\n".join(riscos(t)), flush=True)
    fila = lotes([p for p in pend if p not in risco])
    feitos, conferir, falhas = 0, [], []
    print(f"{len(pend)} roteiro(s) a gerar em {len(fila)} pedido(s); {len(risco)} pulado(s) por risco", flush=True)
    while fila:
        lote = fila.pop(0)
        st, conf = gera(lote)
        ids = " ".join(t.stem for t, _ in lote)
        if st == "cota":
            resto = sum(len(l) for l in fila) + len(lote)
            print(f"COTA DO DIA ESGOTADA nas chaves. Faltam {resto} roteiro(s): rode o mesmo comando amanha (retoma sozinho).", flush=True)
            break
        if st == "alinhamento" and len(lote) > 1:  # o Whisper nao achou a emenda: gera um por pedido
            print(f"alinhamento falhou em [{ids}]: refazendo um por pedido", flush=True)
            fila = [[p] for p in lote] + fila; continue
        if st.startswith("erro") or st == "alinhamento":
            falhas.append(f"{ids}: {st}"); print(f"FALHA [{ids}]: {st}", flush=True); continue
        feitos += len(lote); conferir += conf
        print(f"[{ids}] {st}", flush=True)
    rel = qa
    (rel / "gemini-conferir.txt").write_text("".join(f"{c}\n" for c in conferir))
    print(f"gerados: {feitos}; a conferir: {len(conferir)} (lista em {rel / 'gemini-conferir.txt'}); falhas: {len(falhas)}; pulados por risco: {len(risco)}")
    for f in falhas:
        print("  " + f)
    sys.exit(0 if not (conferir or falhas or risco) and not fila else 2)


if __name__ == "__main__":
    main()
