#!/usr/bin/env python3
"""Produz um vídeo com personagens 2D de ponta a ponta (episódio de série ou vídeo de venda com personagem):
voz (Gemini TTS Puck, 1 pedido com todas as falas) -> cenas (historia.py) -> montar.py -> check -> render
-> checar.py -> post.txt (legenda pronta para colar).

Uso: python3 kit/produzir.py <pasta_do_video> [<pasta> ...]     ex.: python3 kit/produzir.py novato/ep01
Refaz só o que falta: voz existente fica; para refazer a voz de uma fala, apague voz/cNN.m4a (ou edite o texto).
Saída: <pasta>/renders/<serie>-<ep>.mp4, <pasta>/post.txt, folhas de contato em <pasta>/rev/.

Chaves do Gemini, na ordem: variáveis GEMINI*KEY* do ambiente; ~/.config/organico-personagem/gemini.env;
~/.config/curso-mesa-de-som/gemini.env; um script "cofre" numa pasta acima do projeto, se existir.
"""
import json, os, re, shutil, subprocess, sys, unicodedata
from pathlib import Path

KIT = Path(__file__).resolve().parent
RAIZ = KIT.parent                                   # pasta do projeto (tem kit/, tools/, musica/, elenco.json)
TOOLS = RAIZ / "tools"
CONF = Path.home() / ".config"
ENVS = [CONF / "organico-personagem/gemini.env", CONF / "curso-mesa-de-som/gemini.env"]
COFRE = next((p / "cofre" for p in (RAIZ, *RAIZ.parents) if (p / "cofre").is_file()), None)  # script "cofre" acima do projeto, se houver
LISTA = Path.home() / ".claude/skills/curso-mesa-de-som/chaves-gemini.txt"  # nomes das chaves no cofre, um por linha
CHAVES_COFRE = [l.strip() for l in LISTA.read_text().splitlines() if l.strip() and not l.startswith("#")] if LISTA.exists() else []
HF_VERSAO = "hyperframes@0.8.185"
sys.path.insert(0, str(KIT))
import historia  # noqa: E402


def hf(*a):
    """comando do HyperFrames: plugin do Claude Code se instalado, senão npx."""
    h = sorted(Path.home().glob(".claude/plugins/cache/hyperframes/hyperframes/*/skills/hyperframes/scripts/plugin-cli.mjs"))
    return ["node", str(h[-1]), *a] if h else ["npx", "--yes", HF_VERSAO, *a]


def run(cmd, cwd, t=3600, env=None):
    p = subprocess.run([str(c) for c in cmd], cwd=cwd, capture_output=True, text=True, timeout=t, env=env or dict(os.environ))
    return p.returncode, p.stdout + p.stderr


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", unicodedata.normalize("NFD", s).encode("ascii", "ignore").decode().lower()).strip("-")


def voz(d, pares):
    gen = [sys.executable, "-I", KIT / "voz/gen_gemini.py", *pares]
    if any(k.startswith("GEMINI") and "KEY" in k for k in os.environ):
        return run(gen, d, 1800)
    for f in ENVS:
        if f.exists():  # chave só no ambiente do processo da voz, nunca impressa
            chaves = dict(l.split("=", 1) for l in f.read_text().split() if "=" in l)
            return run(gen, d, 1800, dict(os.environ) | chaves)
    if COFRE and CHAVES_COFRE:
        return run([COFRE, *CHAVES_COFRE, "--", *gen], d, 1800)
    return 1, f"nenhuma chave do Gemini: salve em {ENVS[0]} (passo da chave no SKILL.md)"


def produzir(d):
    d = Path(d).resolve(); ep = json.loads((d / "episodio.json").read_text())
    nome = f'{slug(ep["serie"])}-{slug(ep["ep"])}'
    for f in ("hyperframes.json", "package.json", "meta.json"):
        if not (d / f).exists():
            shutil.copy(KIT / "hf-base" / f, d / f)
    # 1. voz
    (d / "voz").mkdir(exist_ok=True); pares = []
    for i, c in enumerate(ep["cenas"], 1):
        t = d / f"voz/c{i:02d}.txt"; fala = c["fala"].strip() + "\n"
        if not t.exists() or t.read_text() != fala:
            t.write_text(fala)
        pares += [f"voz/c{i:02d}.txt", f"voz/c{i:02d}.m4a"]
    falta = [p for p in pares[1::2] if not (d / p).exists() or (d / p).stat().st_mtime < (d / p.replace(".m4a", ".txt")).stat().st_mtime]
    if falta:
        print(f"{nome}: gerando voz ({len(falta)} falas)", flush=True)
        rc, out = voz(d, pares)
        (d / "voz/geracao.log").write_text(out)
        if any(not (d / p).exists() for p in pares[1::2]):
            raise RuntimeError(f"{nome}: FALHA voz ({'cota do Gemini' if '429' in out else out.strip().splitlines()[-1][:160] if out.strip() else rc})")
        if "CONFERIR" in out:
            print(f"{nome}: AVISO voz com {out.count('CONFERIR')} trecho(s) a conferir (voz/geracao.log)")
    # 2. cenas + montagem
    historia.gerar(d)
    (d / "ajustes.json").write_text(json.dumps({"min": {str(len(ep["cenas"])): 3.0}}))  # cartão final fica 3 s no mínimo
    mus = ep.get("musica", "calma"); mus = mus if mus in ("calma", "energica", "nenhuma") else str(RAIZ / "musica" / f"{mus}.m4a")
    py = [sys.executable, TOOLS / "montar.py", ".", "--musica", mus, "--voz"]
    rc, out = run(py, d)
    if rc and "mixagem fora do alvo" in out:
        rc, out = run(py + ["--abaixo", "19.5"], d)
    if rc:
        raise RuntimeError(f"{nome}: FALHA montar: {out.strip()[-300:]}")
    print(f"{nome}: {out.strip().splitlines()[-1]}", flush=True)
    # 3. check + render (o render abre um navegador sem janela)
    if sys.platform == "darwin" and os.environ.get("CODEX_SANDBOX") == "seatbelt":
        raise RuntimeError(f"{nome}: BROWSER_ENVIRONMENT_BLOCKED: rode o render no app Terminal, fora do sandbox")
    rc, out = run(hf("check", "--json"), d)
    try:
        j = json.JSONDecoder().raw_decode(out[out.index("{"):])[0]
        erros = j["runtime"]["errorCount"]
    except Exception:
        erros = f"saída ilegível: {out.strip()[-200:]}"
    if erros:
        raise RuntimeError(f"{nome}: FALHA check ({erros})")
    (d / "renders").mkdir(exist_ok=True); mp4 = d / f"renders/{nome}.mp4"
    print(f"{nome}: renderizando", flush=True)
    rc, out = run(hf("render", ".", "-q", "delivery", "--workers", "6", "--quiet", "-o", f"renders/{nome}.mp4"), d, 5400)
    if rc or not mp4.exists():
        raise RuntimeError(f"{nome}: FALHA render: {out.strip()[-300:]}")
    # 4. conferência objetiva (sem --html: o cartão final mostra o @ do perfil de propósito)
    rc, out = run([sys.executable, TOOLS / "checar.py", f"renders/{nome}.mp4", "--dur", "15-150", "--folhas", "rev"], d)
    (d / "checar.log").write_text(out)
    # 5. legenda do post
    (d / "post.txt").write_text(f'{ep.get("legenda", "").strip()}\n\n{ep.get("hashtags", "").strip()}\n')
    falhas = [l for l in out.splitlines() if l.startswith("FALHA")]
    if falhas:
        raise RuntimeError(f"{nome}: {falhas[0]}")
    print(f"{nome}: pronto -> {mp4}", flush=True)
    return mp4


if __name__ == "__main__":
    erros = 0
    for a in sys.argv[1:]:
        try:
            produzir(a)
        except RuntimeError as e:
            print(e); erros += 1
    sys.exit(1 if erros else 0)
