#!/usr/bin/env python3
"""Injeta a camada de celular (celular.css + celular.js) num autoestudo V2.

Uso:
  aplicar.py caminho/08-slides-v2/index.html
  aplicar.py --backup-dir ~/Backups/x caminho/v2-autoestudo.zip [outro.zip ...]

Idempotente: o bloco entre os marcadores CELULAR é trocado, nunca duplicado.
No ZIP, só o index.html muda; o ZIP antigo é copiado para --backup-dir antes (obrigatório).
"""
import argparse, hashlib, os, re, shutil, sys, tempfile, zipfile
from pathlib import Path

AQUI = Path(__file__).resolve().parent
INI, FIM = "<!-- CELULAR:INICIO -->", "<!-- CELULAR:FIM -->"
# first thing in <head>: keeps the real Screen before decks that declare a global function screen() (Axios32, LS9, Ui24R) replace it
TELA = '<script id="cel-tela">window.celScreen = window.screen;</script><!-- CELULAR:TELA -->'


def bloco():
    css = (AQUI / "celular.css").read_text(encoding="utf-8")
    js = (AQUI / "celular.js").read_text(encoding="utf-8")
    return f'{INI}\n<style id="cel-css">\n{css}</style>\n<script id="cel-js">\n{js}</script>\n{FIM}\n'


def injeta(html: str) -> str:
    if INI in html:
        a, resto = html.split(INI, 1)
        _, b = resto.split(FIM, 1)
        html = a + b.lstrip("\n")
    html = html.replace(TELA, "")
    h = re.search(r"<head[^>]*>", html)
    if not h:
        raise ValueError("index.html sem <head>")
    html = html[: h.end()] + TELA + html[h.end():]
    i = html.rfind("</body>")
    if i < 0:
        raise ValueError("index.html sem </body>")
    novo = html[:i] + bloco() + html[i:]
    assert novo.count(INI) == 1 and novo.count(FIM) == 1 and novo.count(TELA) == 1 and novo.rstrip().endswith("</html>")
    # the layer needs the global Reveal; on/configure called before initialize (decks that start in deck.js) are queued by Reveal 5
    assert 'src="lib/dist/reveal.js"' in novo[: novo.index(INI)], "a camada precisa vir depois do lib/dist/reveal.js"
    return novo


def no_html(p: Path):
    p.write_text(injeta(p.read_text(encoding="utf-8")), encoding="utf-8")
    print(f"ok  {p}")


def no_zip(z: Path, backup_dir: Path):
    backup_dir.mkdir(parents=True, exist_ok=True)
    bk = backup_dir / (z.parent.parent.name + "-" + z.name)
    if not bk.exists():  # a re-run keeps the first backup (the ZIP before any layer), never overwrites it
        shutil.copy2(z, bk)
        if hashlib.sha256(bk.read_bytes()).digest() != hashlib.sha256(z.read_bytes()).digest():
            sys.exit(f"backup incompleto: {bk}")
    fd, tmp = tempfile.mkstemp(suffix=".zip", dir=z.parent)
    os.close(fd)
    achou = 0
    with zipfile.ZipFile(z) as src, zipfile.ZipFile(tmp, "w") as dst:
        for info in src.infolist():
            dados = src.read(info)
            if info.filename.endswith("08-slides-v2/index.html"):
                dados = injeta(dados.decode("utf-8")).encode("utf-8")
                info.compress_type = zipfile.ZIP_DEFLATED
                achou += 1
            dst.writestr(info, dados)
    if achou != 1:
        os.remove(tmp)
        sys.exit(f"{z}: esperava 1 index.html em 08-slides-v2, achei {achou}")
    with zipfile.ZipFile(tmp) as t:
        if t.testzip() is not None:
            os.remove(tmp)
            sys.exit(f"{z}: ZIP novo corrompido")
    os.replace(tmp, z)
    print(f"ok  {z}  (backup {bk})")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("alvos", nargs="+", type=Path)
    ap.add_argument("--backup-dir", type=Path)
    a = ap.parse_args()
    for p in a.alvos:
        if p.suffix == ".zip":
            if not a.backup_dir:
                sys.exit("ZIP exige --backup-dir")
            no_zip(p, a.backup_dir.expanduser())
        else:
            no_html(p)


if __name__ == "__main__":
    main()
