#!/usr/bin/env python3
"""Produz os vídeos orgânicos em lote, sem intervenção: voz (Gemini, 1 pedido por vídeo, numa fila à parte) -> cenas -> montar
-> check -> render (até 3 ao mesmo tempo: Mac de 16 GB) -> checar.py. Um design por bloco de 5 (011-015 = c ... 096-100 = t).

Uso: python3 lote.py 11 100 [--espera]   (--espera: fica rodando até tudo sair; sem ela, para quando não há mais o que fazer agora)
Só produz vídeo com spec.ok (gravado por validar_spec.py) e com todas as falas em voz/. Vídeo com renders/NNN.mp4 é pulado.
Estado em ../videos/LOTE-STATUS.md.
"""
import concurrent.futures as cf, glob, json, os, shutil, subprocess, sys, threading, time
from pathlib import Path

KIT = Path(__file__).resolve().parent; RO = Path(os.environ.get("ORG_RAIZ", KIT.parent)).resolve(); V = RO / "videos"  # ORG_RAIZ: outra pasta com json/ e videos/ (ex.: domingo-noite/<data>)
G = KIT.parent  # pasta do projeto: tools/, musica/
CONF = Path.home() / ".config"
ENVS = [CONF / "organico-videos/gemini.env", CONF / "organico-personagem/gemini.env", CONF / "curso-mesa-de-som/gemini.env"]
COFRE = next((p / "cofre" for p in (G, *G.parents) if (p / "cofre").is_file()), None)  # script "cofre" acima do projeto, se houver
LISTA = Path.home() / ".claude/skills/curso-mesa-de-som/chaves-gemini.txt"  # nomes das chaves no cofre, um por linha
H = (sorted(Path.home().glob(".claude/plugins/cache/hyperframes/hyperframes/*/skills/hyperframes/scripts/plugin-cli.mjs")) or [None])[-1]
HF = os.environ.get("HF_CMD", "").split() or ["node", str(H)]  # VPS (sem o plugin do Claude): HF_CMD="npx --yes hyperframes@0.8.185"
HF_LOCAL = KIT / "hf-base"  # projeto HyperFrames vazio (hyperframes.json, package.json, meta.json)
RENDER = threading.Semaphore(int(os.environ.get("LOTE_RENDERS", 3)))  # menos render se o Mac já está ocupado
ST = {}; LK = threading.Lock(); VOZ = {}


def musica(n):
    """faixa do roteiro ("musica": nome de musica/<nome>.m4a) ou a "calma"."""
    r = V / f"{n:03d}/roteiro.json"
    m = json.loads(r.read_text()).get("musica") if r.exists() else None
    return str(G / "musica" / f"{m}.m4a") if m and m not in ("calma", "energica") else (m or "calma")


def tema(n):
    # 101-200 (lote 2) recomeça a roda dos 18 designs: 101-105 = c, 106-110 = d ...
    return "cdefghijklmnopqrst"[(n - 11) // 5 % 18] if n > 10 else "ab"[(n - 1) // 5]


def status(n, s):
    with LK:
        if ST.get(n) == s:
            return
        ST[n] = s
        linhas = ["# Lote dos vídeos orgânicos", "", "| Vídeo | Design | Música | Estado |", "|---|---|---|---|"]
        linhas += [f"| {k:03d} | {tema(k) if k > 10 else '-'} | {Path(musica(k)).stem} | {v} |" for k, v in sorted(ST.items())]
        (V / "LOTE-STATUS.md").write_text("\n".join(linhas) + "\n")
    print(f"{time.strftime('%H:%M')} {n:03d} {s}", flush=True)


def run(cmd, cwd, t=1800):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=t)
    return p.returncode, p.stdout + p.stderr


def prepara(n):
    d = V / f"{n:03d}"; (d / "voz").mkdir(parents=True, exist_ok=True)
    if not (d / "roteiro.json").exists():
        shutil.copy(glob.glob(str(RO / f"json/{n:03d}-*.json"))[0], d / "roteiro.json")
    r = json.loads((d / "roteiro.json").read_text()); k = len(r["cenas"])
    for i, c in enumerate(r["cenas"], 1):
        t = d / f"voz/c{i:02d}.txt"
        if not t.exists():
            t.write_text(c["fala"].strip() + "\n")
    if not (d / "ajustes.json").exists():  # CTA fica pelo menos 3 s na tela
        (d / "ajustes.json").write_text(json.dumps({"min": {str(k): 3.0}}))
    return d, k


def falta_voz(d, k):
    return [i for i in range(1, k + 1) if not (d / f"voz/c{i:02d}.m4a").exists()]


def voz(n, d, k):
    a = []
    for i in range(1, k + 1):
        a += [f"voz/c{i:02d}.txt", f"voz/c{i:02d}.m4a"]
    env = dict(os.environ)
    if not any(k.startswith("GEMINI") and "KEY" in k for k in env):
        f = next((f for f in ENVS if f.exists()), None)
        if f:
            env |= dict(l.split("=", 1) for l in f.read_text().split() if "=" in l)  # só no processo da voz, nunca impressa
        elif not (COFRE and LISTA.exists()):
            return f"erro voz: nenhuma chave do Gemini; salve em {ENVS[0]} (passo da chave no SKILL.md)"
    cmd = [sys.executable, "-I", str(KIT / "voz/gen_gemini.py"), *a]
    if not any(k.startswith("GEMINI") and "KEY" in k for k in env):  # dono: chaves pelo cofre
        cmd = [str(COFRE), *[l.strip() for l in LISTA.read_text().splitlines() if l.strip() and not l.startswith("#")], "--", *cmd]
    p = subprocess.run(cmd, cwd=d, capture_output=True, text=True, timeout=1500, env=env)
    rc, out = p.returncode, p.stdout + p.stderr
    (d / "voz/qa").mkdir(exist_ok=True); (d / "voz/qa/geracao.log").write_text(out)
    if falta_voz(d, k):
        return "cota" if "429" in out else f"erro voz: {out.strip().splitlines()[-1][:120] if out.strip() else rc}"
    return f"voz ok ({out.count('CONFERIR')} a conferir)"


def fila_voz(itens, espera):
    """uma voz por vez (a cota do Gemini é por dia); com --espera tenta de novo a cada hora."""
    for n, d, k in itens:
        while falta_voz(d, k):
            s = voz(n, d, k)
            if s == "cota":
                VOZ[n] = "aguardando cota do Gemini"
                if not espera:
                    return
                time.sleep(3600); continue
            VOZ[n] = ("FALHA " + s) if s.startswith("erro") else s
            break


def produz(n, d):
    try:
        for f in ("hyperframes.json", "package.json", "meta.json"):
            if not (d / f).exists():
                shutil.copy(HF_LOCAL / f, d / f)
        rc, out = run([sys.executable, str(KIT / "gerar_cenas.py"), "."], d)
        if rc:
            return status(n, f"FALHA cenas: {out.strip()[-150:]}")
        rc, out = run([sys.executable, str(G / "tools/montar.py"), ".", "--musica", musica(n), "--voz"], d)
        if rc and "mixagem fora do alvo" in out:  # pico passou do teto: música 1,5 dB mais baixa resolve
            rc, out = run([sys.executable, str(G / "tools/montar.py"), ".", "--musica", musica(n), "--voz", "--abaixo", "19.5"], d)
        if rc:
            return status(n, f"FALHA montar: {out.strip()[-150:]}")
        rc, out = run([*HF, "check", "--json"], d)
        try:
            # o HyperFrames escreve uma linha da GPU no stderr depois do JSON: lê só o primeiro objeto
            j = json.JSONDecoder().raw_decode(out[out.index("{"):])[0]; ok = j["runtime"]["errorCount"] == 0
            (d / "check.json").write_text(json.dumps({k: [f for f in j[k]["findings"] if f["severity"] != "info"] for k in ("runtime", "layout", "contrast", "craft")}, ensure_ascii=False))
        except Exception:
            ok = False
        if not ok:
            return status(n, f"FALHA check: {out.strip()[-150:]}")
        status(n, "na fila do render")
        with RENDER:
            status(n, "renderizando")
            (d / "renders").mkdir(exist_ok=True)
            rc, out = run([*HF, "render", ".", "-q", "delivery", "-w", "auto", "--quiet", "-o", f"renders/{n:03d}.mp4"], d, 3600)
        if rc:
            (d / f"renders/{n:03d}.mp4").unlink(missing_ok=True)
            return status(n, f"FALHA render: {out.strip()[-150:]}")
        rc, out = run([sys.executable, str(G / "tools/checar.py"), f"renders/{n:03d}.mp4", "--html", "index.html", "--folhas", "rev-r1/folhas"], d)
        (d / "checar.log").write_text(out)
        fal = [l for l in out.splitlines() if l.startswith("FALHA")]
        av = sum(1 for l in out.splitlines() if l.startswith("AVISO"))
        status(n, ("FALHA checar: " + fal[0][:120]) if fal else f"pronto ({av} aviso)")
    except Exception as e:
        status(n, f"FALHA: {e}")


def main(a, b, espera):
    pend = []
    for n in range(a, b + 1):
        d, k = prepara(n)
        if (d / f"renders/{n:03d}.mp4").exists():
            status(n, "pronto (já existia)")
        else:
            pend.append((n, d, k))
    tv = threading.Thread(target=fila_voz, args=([x for x in pend if falta_voz(x[1], x[2])], espera), daemon=True); tv.start()
    parado = time.time()
    with cf.ThreadPoolExecutor(int(os.environ.get("LOTE_TRABALHOS", 6))) as ex:  # VPS: 1 (o check também abre o Chrome)
        while pend:
            resto = []
            for n, d, k in pend:
                if VOZ.get(n, "").startswith("FALHA"):
                    status(n, VOZ[n]); continue
                if falta_voz(d, k):
                    status(n, VOZ.get(n, "aguardando voz")); resto.append((n, d, k))
                elif not (d / "spec.ok").exists():
                    status(n, "aguardando spec"); resto.append((n, d, k))
                else:
                    ex.submit(produz, n, d); parado = time.time()
            pend = resto
            if pend:
                if not espera and not tv.is_alive() and time.time() - parado > 1200:
                    print(f"{len(pend)} vídeo(s) ainda sem voz ou sem spec; rode de novo depois", flush=True); break
                time.sleep(30)


if __name__ == "__main__":
    main(int(sys.argv[1]), int(sys.argv[2]), "--espera" in sys.argv)
