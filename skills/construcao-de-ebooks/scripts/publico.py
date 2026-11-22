#!/usr/bin/env python3
"""Voz do público: lê comentários públicos e visualizações do YouTube, sem login e sem baixar vídeo.
Uso: python3 -I publico.py "busca 1" ["busca 2"] > publico.json
Precisa do yt-dlp. Não guarda nome de quem comentou e esconde @, e-mail, link e telefone."""
import json, os, re, shutil, subprocess, sys

ESCONDE = [(r"https?://\S+|www\.\S+", "[link]"), (r"[\w.+-]+@[\w-]+\.[\w.]+", "[e-mail]"),
           (r"@[\w.-]+", "[perfil]"), (r"(?:\+?\d[\s().-]*){8,}", "[número] ")]


def limpar(t):
    for padrao, troca in ESCONDE:
        t = re.sub(padrao, troca, t)
    return " ".join(t.split())[:400]


def resumir(d):
    cs = [x for x in d.get("comments") or [] if x.get("text") and not x.get("author_is_uploader")]
    return {"url": d.get("webpage_url"), "video": d.get("title"), "visualizacoes": d.get("view_count"),
            "publicado": d.get("upload_date"), "comentarios_lidos": len(cs),
            "comentarios": [{"texto": limpar(x["text"]), "curtidas": x.get("like_count")} for x in cs]}


def coletar(buscas, exe):
    saida = []
    for q in buscas:
        cmd = [exe, "--ignore-config", "--skip-download", "--no-warnings", "--write-comments",
               "--extractor-args", "youtube:max_comments=40,40,0,0;comment_sort=top",
               "-O", "%(.{title,view_count,upload_date,comments,webpage_url})j", "--", f"ytsearch5:{q}"]
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        except subprocess.TimeoutExpired:
            saida.append({"busca": q, "estado": "não medido: demorou demais", "videos": []})
            continue
        videos = [resumir(json.loads(l)) for l in r.stdout.splitlines() if l.startswith("{")]
        saida.append({"busca": q, "estado": "ok" if videos else f"não medido: {r.stderr.strip()[-160:]}", "videos": videos})
    return saida


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    exe = shutil.which("yt-dlp") or os.path.expanduser("~/.local/bin/yt-dlp")
    if not os.path.exists(exe):
        sys.exit("SEM YT-DLP: peça ok para instalar (brew install yt-dlp) ou registre 'não medido'")
    print(json.dumps(coletar(sys.argv[1:], exe), ensure_ascii=False, indent=1))
