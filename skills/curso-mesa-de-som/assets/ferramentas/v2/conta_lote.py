#!/usr/bin/env python3
"""Confere um lote da reescrita: tamanho, marcas do glossário e proibições. Uso: conta_lote.py <pasta-do-curso> <cap_ini> <cap_fim>."""
import json, re, sys
from pathlib import Path
c, a, z = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]); V = Path(c) / "tools/v2"
sl = [s for s in json.loads((V / "slides.json").read_text()) if s["capitulo"] is not None and a <= s["capitulo"] <= z]  # shortcut: telas especiais (capitulo null) não entram no lote; o passo de completude as cobre
slugs = {t["slug"] for f in V.glob("glossario*.json") for t in json.loads(f.read_text())}
falhas = 0
for s in sl:
    i, ip, sp = s["id"], V / f"info/{s['id']}.html", V / f"script/{s['id']}.txt"
    info, scr = ip.read_text(), sp.read_text(); wi, ws = len(re.sub(r"<[^>]+>", " ", info).split()), len(scr.split()); pr = []
    if not 170 <= wi <= 230: pr.append(f"info {wi}")
    if not 280 <= ws <= 380: pr.append(f"roteiro {ws}")
    for t in re.findall(r'data-t="([^"]+)"', info):
        if t not in slugs: pr.append("slug? " + t)
    if re.search(r"<script|\son\w+=|\.\./", info): pr.append("html proibido")
    if re.search(r"\d|<", scr): pr.append("roteiro com algarismo ou marca: " + ",".join(re.findall(r"\S*[\d<]\S*", scr)[:4]))
    if pr: falhas += 1; print(i, "; ".join(pr))
print(f"{c} cap {a}-{z}: {len(sl)} telas, {falhas} com pendência"); sys.exit(1 if falhas else 0)
