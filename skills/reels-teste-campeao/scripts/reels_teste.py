#!/usr/bin/env python3
"""Reels de teste do campeão: escolhe o Reel orgânico que mais performou e gera as variações para postar como
Reel de teste do Instagram (trial reel: aparece só para quem não segue o perfil).

Só biblioteca padrão do Python (3.8+) e ffmpeg/ffprobe no PATH. A API da Meta é opcional (medir e postar):
o token fica em ~/.config/reels-teste-campeao/meta.env (META_TOKEN e IG_USER_ID) e nunca é mostrado.

Comandos:
  campeao  METRICAS.csv|json          quem é o campeão (regra: mais views da janela 48-96 h, acima da média)
  vencedor METRICAS.csv|json          qual Reel de teste venceu (>= 20% acima da mediana dos testes e >= 100 views)
  variacoes VIDEO.mp4 --titulos ...   gera as variações visuais (fase 1: r1 r2 r3; fase 2: cenario, cta, gancho)
  voz VIDEO.mp4 --voz fala.wav --de 0 --ate 3.2   troca só o trecho falado (gancho ou CTA) por uma fala nova
  medir  [--saida metricas.csv]       (API) baixa views, alcance, salvos e compartilhamentos dos Reels
  postar VIDEO.mp4 --legenda texto.txt  (API) posta como Reel de teste e anota em registro.csv
  contas                              (API) lista as páginas e o ID da conta do Instagram ligada a cada uma
  --teste                             autoteste sem internet (métricas falsas + MP4 de 5 s gerado pelo ffmpeg)
"""
import argparse
import csv
import json
import os
import re
import shutil
import statistics
import subprocess
import sys
import tempfile
import textwrap
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

CONFIG = Path.home() / ".config/reels-teste-campeao/meta.env"
GRAPH = "https://graph.facebook.com/" + os.environ.get("GRAPH_VERSION", "v23.0")
RUPLOAD = "https://rupload.facebook.com/ig-api-upload/" + os.environ.get("GRAPH_VERSION", "v23.0")
CAMPOS = ["id", "postado", "views", "alcance", "salvos", "compartilhamentos", "curtidas", "comentarios",
          "teste", "campeao", "link"]
NUMEROS = CAMPOS[2:8]
REGISTRO_CAMPOS = ["data", "campeao", "variante", "variavel", "media_id", "link"]

# Plano do campeão: fase 1 = 3 repostagens (dia 0, 2, 4); fase 2 = 1 por semana até o dia 56, em rodízio.
FASE1 = [(0, "r1"), (2, "r2"), (4, "r3")]
FASE2 = [(7 * (i + 1), ("cenario", "cta", "gancho")[i % 3]) for i in range(8)]
VARIAVEL = {"r1": "repostagem (cor, fonte, título)", "r2": "repostagem (cor, fonte, título)",
            "r3": "repostagem (cor, fonte, título, ritmo)", "cenario": "visual novo", "cta": "chamada mais forte",
            "gancho": "uma palavra trocada no gancho"}
CENARIOS = [("escuro", "negate,hue=h=180,eq=saturation=1.2"),  # bom para vídeo de fundo claro
            ("quente", "colorbalance=rs=.12:gs=.02:bs=-.12:rm=.08:bm=-.08,hue=h=25,eq=saturation=1.2"),
            ("frio", "colorbalance=rs=-.12:bs=.15:rm=-.06:bm=.1,eq=saturation=1.1:contrast=1.05")]
FONTES = [  # uma família diferente por versão da fase 1; a primeira que existir na máquina
    ["/System/Library/Fonts/Supplemental/Impact.ttf", "C:/Windows/Fonts/impact.ttf",
     "/usr/share/fonts/truetype/msttcorefonts/Impact.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf"],
    ["/System/Library/Fonts/Supplemental/Courier New Bold.ttf", "C:/Windows/Fonts/courbd.ttf",
     "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf"],
    ["/System/Library/Fonts/Supplemental/Arial Bold.ttf", "C:/Windows/Fonts/arialbd.ttf",
     "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"],
]


def erro(msg):
    sys.exit("ERRO: " + msg)


# ---------- métricas ----------
def data(txt):
    """Aceita '2026-11-15T12:30:00+0000' (API), '2026-11-15 12:30' e '2026-11-15'. Sem fuso = hora local."""
    txt = txt.strip().replace("Z", "+00:00")
    txt = re.sub(r"([+-]\d\d)(\d\d)$", r"\1:\2", txt)
    d = datetime.fromisoformat(txt)
    return d if d.tzinfo else d.astimezone()


def carregar_metricas(arq):
    arq = Path(arq)
    if arq.suffix.lower() == ".json":
        linhas = json.loads(arq.read_text(encoding="utf-8"))
    else:
        with arq.open(encoding="utf-8-sig", newline="") as f:
            linhas = list(csv.DictReader(f))
    out = []
    for n, l in enumerate(linhas, 2):
        if not str(l.get("id", "")).strip():
            continue
        try:
            r = {k: str(l.get(k) or "").strip() for k in CAMPOS}
            for k in NUMEROS:
                r[k] = int(float(r[k] or 0))
            r["postado"] = data(r["postado"])
        except ValueError as e:
            erro(f"{arq.name}, linha {n}: {e}. Confira a data (AAAA-MM-DD HH:MM) e os números.")
        out.append(r)
    return out


def salvar_metricas(linhas, arq):
    with open(arq, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, CAMPOS)
        w.writeheader()
        for l in linhas:
            w.writerow({**l, "postado": l["postado"].isoformat(timespec="minutes")})


def escolher_campeao(linhas, agora, min_h=48, max_h=96, base_n=30, excluir=()):
    """Campeão = Reel orgânico com mais views entre os postados há min_h..max_h horas (desempate: salvos +
    compartilhamentos), se passar da média de views dos base_n Reels orgânicos mais recentes com min_h horas ou mais.
    Devolve (campeao ou None, media, janela, base)."""
    org = [l for l in linhas if not l["teste"]]
    idade = lambda l: (agora - l["postado"]).total_seconds() / 3600  # noqa: E731
    maduros = sorted((l for l in org if idade(l) >= min_h), key=lambda l: l["postado"], reverse=True)
    base = maduros[:base_n]
    janela = [l for l in maduros if idade(l) <= max_h and l["id"] not in excluir]
    if not base or not janela:
        return None, 0.0, janela, base
    media = sum(l["views"] for l in base) / len(base)
    top = max(janela, key=lambda l: (l["views"], l["salvos"] + l["compartilhamentos"]))
    return (top if top["views"] > media else None), media, janela, base


def escolher_vencedor(testes, folga=1.2, minimo=100):
    """Reel de teste vencedor: views >= folga x mediana dos testes e >= minimo views. Devolve (vencedor|None, mediana)."""
    if len(testes) < 2:
        return None, 0.0
    med = statistics.median(t["views"] for t in testes)
    top = max(testes, key=lambda t: (t["views"], t["salvos"] + t["compartilhamentos"]))
    return (top if top["views"] >= folga * med and top["views"] >= minimo else None), med


def agenda(inicio):
    base = data(inicio)
    return [{"dia": d, "variante": v, "variavel": VARIAVEL[v], "quando": (base + timedelta(days=d)).strftime("%d/%m/%Y")}
            for d, v in FASE1 + FASE2]


def ids_registro(arq):
    if not Path(arq).is_file():
        return {}
    with open(arq, encoding="utf-8", newline="") as f:
        return {r["media_id"]: r for r in csv.DictReader(f) if r.get("media_id")}


def por_mil(l):
    return 1000 * (l["salvos"] + l["compartilhamentos"]) / max(l["views"], 1)


def cmd_campeao(a):
    linhas = carregar_metricas(a.metricas)
    agora = data(a.agora) if a.agora else datetime.now().astimezone()
    excluir = {r["campeao"] for r in ids_registro(a.registro).values()}
    top, media, janela, base = escolher_campeao(linhas, agora, a.min_horas, a.max_horas, a.base, excluir)
    print(f"Média de views dos últimos {len(base)} Reels orgânicos (com {a.min_horas} h ou mais): {media:.0f}")
    print(f"Janela ({a.min_horas} a {a.max_horas} h depois de postados): {len(janela)} Reel(s)")
    for l in sorted(janela, key=lambda l: -l["views"])[:5]:
        print(f"  {l['id']}: {l['views']} views, alcance {l['alcance']}, {l['salvos']} salvos, "
              f"{l['compartilhamentos']} compart. ({por_mil(l):.1f} por mil views)")
    if not top:
        print("Sem campeão desta vez: " + ("nenhum Reel na janela." if not janela else "nenhum passou da média."))
        return 1
    print(f"\nCAMPEÃO: {top['id']} ({top['views']} views, {top['views'] / max(media, 1):.1f}x a média) {top['link']}")
    print("Plano (uma variação por data):")
    for p in agenda(a.agora or datetime.now().astimezone().isoformat()):
        print(f"  dia {p['dia']:>2} ({p['quando']}): {p['variante']:<8} {p['variavel']}")
    return 0


def cmd_vencedor(a):
    linhas = [l for l in carregar_metricas(a.metricas) if l["teste"]]
    if a.campeao:
        linhas = [l for l in linhas if l["campeao"] == a.campeao]
    if not linhas:
        print("Nenhuma linha de Reel de teste (coluna 'teste' preenchida) nas métricas.")
        return 1
    grupos = {}
    for l in linhas:
        grupos.setdefault(l["campeao"] or "-", []).append(l)
    for camp, ts in grupos.items():
        v, med = escolher_vencedor(ts, a.folga, a.minimo)
        print(f"Campeão {camp}: {len(ts)} teste(s), mediana {med:.0f} views")
        for t in sorted(ts, key=lambda t: -t["views"]):
            print(f"  {t['teste']:<10} {t['views']:>7} views, {por_mil(t):.1f} salvos+compart. por mil, {t['comentarios']} coment.")
        print(f"  VENCEDOR: {v['teste']} ({v['views']} views)" if v else
              "  Sem vencedor claro: mantenha a versão original e teste outra variável.")
    return 0


# ---------- ffmpeg ----------
def rodar(cmd, cwd=None):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if p.returncode != 0:
        erro(f"{cmd[0]} falhou: {p.stderr.strip()[-600:]}")
    return p.stdout + p.stderr


def info(mp4):
    out = rodar(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=codec_type", "-of", "json", str(mp4)])
    j = json.loads(out[out.index("{"):])
    return float(j["format"]["duration"]), any(s["codec_type"] == "audio" for s in j.get("streams", []))


def lufs(arq, de=None, ate=None):
    trim = f"atrim={de}:{ate}," if de is not None else ""
    out = rodar(["ffmpeg", "-nostdin", "-nostats", "-i", str(arq), "-vn", "-af", trim + "ebur128", "-f", "null", "-"])
    v = re.findall(r"I:\s+(-?[\d.]+) LUFS", out)
    return float(v[-1]) if v and float(v[-1]) > -70 else None


def achar_fonte(i, escolhidas):
    if escolhidas:
        f = escolhidas[i % len(escolhidas)]
        return f if Path(f).is_file() else erro(f"fonte não encontrada: {f}")
    for grupo in FONTES[i:] + FONTES[:i]:
        for f in grupo:
            if Path(f).is_file():
                return f
    erro("nenhuma fonte encontrada. Use --fontes /caminho/fonte.ttf (uma .ttf em negrito).")


def quando(ini=None, fim=None):
    c = " * ".join(x for x in (f"gte(t,{ini})" if ini is not None else "", f"lt(t,{fim})" if fim is not None else "") if x)
    return f":enable='{c}'" if c else ""


class Textos:
    """Grava cada texto e fonte com nome simples numa pasta temporária: o filtro do ffmpeg não sofre com
    acento, aspas, dois-pontos ou espaço no caminho."""
    def __init__(self, pasta):
        self.pasta, self.n = Path(pasta), 0

    def linhas(self, txt, fonte, tam, y0, cor, largura, ini=None, fim=None, espaco=1.25):
        ff = self.pasta / ("f" + str(abs(hash(fonte))) + ".ttf")
        if not ff.is_file():
            shutil.copy(fonte, ff)
        partes = textwrap.wrap(txt.strip(), largura) or [txt]
        out = []
        for i, linha in enumerate(partes):
            self.n += 1
            (self.pasta / f"t{self.n}.txt").write_text(linha, encoding="utf-8")
            out.append(f"drawtext=fontfile={ff.name}:textfile=t{self.n}.txt:expansion=none:fontsize={tam}:fontcolor={cor}:"
                       f"x=(w-text_w)/2:y={y0 + int(i * tam * espaco)}" + quando(ini, fim))
        return out, len(partes)

    def faixa(self, txt, fonte, cor_txt, cor_faixa, tam, largura, ate=3.5, altura=600):
        """Título numa faixa opaca no topo, só nos primeiros segundos (fora da área que a interface do Reels cobre)."""
        n = len(textwrap.wrap(txt.strip(), largura)) or 1
        y0 = int((altura - n * tam * 1.25) / 2) + 40
        dt, _ = self.linhas(txt, fonte, tam, y0, cor_txt, largura, fim=ate)
        return [f"drawbox=x=0:y=0:w=iw:h={altura}:color={cor_faixa}:t=fill" + quando(fim=ate)] + dt


def zoom(z):
    return f"scale=trunc(iw*{z}/2)*2:-2,crop=1080:1920"


def filtro_variante(var, k, a, tx, dur):
    """Variante -> (filtro de vídeo, velocidade). Todos partem do vídeo já em 1080x1920."""
    tit = a.titulos
    if var == "r1":
        return ",".join([zoom(1.03), "eq=saturation=1.35:contrast=1.06",
                         *tx.faixa(tit[0].upper(), achar_fonte(0, a.fontes), "white", "black@0.97", 92, 18)]), 1.0
    if var == "r2":
        return ",".join([zoom(1.06), "eq=saturation=0.75:brightness=0.03",
                         *tx.faixa(tit[1 % len(tit)], achar_fonte(1, a.fontes), "black", "0xFFD400@0.98", 70, 18)]), 1.0
    if var == "r3":
        return ",".join([zoom(1.04), "eq=saturation=1.15:gamma=0.92", "vignette=PI/6",
                         *tx.faixa(tit[2 % len(tit)], achar_fonte(2, a.fontes), "white", "0xD62828@0.97", 70, 20)]), 1.03
    if var == "cenario":
        return ",".join([zoom(1.05), CENARIOS[k % 3][1]]), 1.0
    if var == "cta":
        ini = a.cta_inicio if a.cta_inicio is not None else max(dur - 4.5, 0)
        grande, pequeno = (a.cta.split("|", 1) + [""])[:2]
        f = achar_fonte(0, a.fontes)
        l1, n1 = tx.linhas(grande.strip(), f, 130, 760, "0xFFD400", 14, ini)
        l2, _ = tx.linhas(pequeno.strip(), f, 62, 760 + int(n1 * 130 * 1.25) + 20, "white", 26, ini) if pequeno.strip() else ([], 0)
        return ",".join([zoom(1.02), "eq=saturation=1.1",
                         "drawbox=x=0:y=700:w=iw:h=520:color=black@0.97:t=fill" + quando(ini), *l1, *l2]), 1.0
    if var == "gancho":
        g = a.ganchos[k % len(a.ganchos)]
        return ",".join([zoom(1.02), "eq=saturation=1.08:contrast=1.03",
                         *tx.faixa(g.upper(), achar_fonte(0, a.fontes), "white", "black@0.97", 92, 18)]), 1.0
    raise ValueError(var)


def cmd_variacoes(a):
    video = Path(a.video).resolve()
    if not video.is_file():
        erro(f"vídeo não encontrado: {video}")
    a.titulos = [t.strip() for t in (a.titulos or "").split("|") if t.strip()]
    a.ganchos = [t.strip() for t in (a.ganchos or "").split("|") if t.strip()]
    a.fontes = [t.strip() for t in (a.fontes or "").split("|") if t.strip()]
    pedidas = [v.strip() for v in a.so.split(",")] if a.so else ["r1", "r2", "r3", "cenario", "cta", "gancho"]
    if any(v in pedidas for v in ("r1", "r2", "r3")) and not a.titulos:
        erro('a fase 1 precisa de --titulos "título 1|título 2|título 3" (até ~38 caracteres cada).')
    if "gancho" in pedidas and not a.ganchos:
        if a.so:
            erro('a variação gancho precisa de --ganchos "gancho com 1 palavra trocada|outra troca".')
        pedidas.remove("gancho")
    saida = Path(a.saida or video.with_name(video.stem + "-variacoes")).resolve()
    saida.mkdir(parents=True, exist_ok=True)
    dur, tem_audio = info(video)
    feitos = []
    for var in pedidas:
        n = {"cenario": 3, "gancho": len(a.ganchos)}.get(var, 1)
        for k in range(n):
            nome = var if n == 1 else f"{var}-{k + 1}" + (f"-{CENARIOS[k][0]}" if var == "cenario" else "")
            with tempfile.TemporaryDirectory() as tmp:
                fv, vel = filtro_variante(var, k, a, Textos(tmp), dur)
                fv = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1," + fv
                if vel != 1.0:
                    fv += f",setpts=PTS/{vel}"
                cmd = ["ffmpeg", "-nostdin", "-y", "-loglevel", "error", "-i", str(video), "-vf", fv + ",format=yuv420p",
                       "-map", "0:v:0", "-map", "0:a:0?", "-r", "30", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
                       "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart"]
                if vel != 1.0 and tem_audio:
                    cmd += ["-af", f"atempo={vel}"]
                rodar(cmd + [str(saida / f"{nome}.mp4")], cwd=tmp)
            feitos.append(saida / f"{nome}.mp4")
            print(f"ok {nome}.mp4  ({VARIAVEL[var]})")
    print(f"\n{len(feitos)} variação(ões) em {saida}")
    return feitos


def cmd_voz(a):
    """Troca o áudio de [de, ate] por uma fala nova (opcional: a mesma música por baixo), no volume do trecho
    original, com emendas curtas. O vídeo não muda; a duração final é a mesma."""
    video, voz = Path(a.video), Path(a.voz)
    for p in (video, voz):
        if not p.is_file():
            erro(f"arquivo não encontrado: {p}")
    dur, tem_audio = info(video)
    if not tem_audio:
        erro("o vídeo não tem áudio para trocar.")
    de, ate = a.de, min(a.ate, dur)
    vaga, vd = ate - de, info(voz)[0]
    if vaga < 0.5:
        erro("o trecho (--de/--ate) precisa ter pelo menos 0,5 s.")
    if vd > vaga * 1.2:
        erro(f"a fala nova tem {vd:.1f} s e o trecho {vaga:.1f} s: encurte a fala (no máximo 20% mais longa).")
    tempo = max(1.0, vd / vaga)
    seg = f"[1:a]aresample=48000,aformat=channel_layouts=stereo,atempo={tempo:.3f},adelay=80|80,apad,atrim=0:{vaga:.3f}"
    entradas = ["-i", str(video), "-i", str(voz)]
    if a.musica:
        entradas += ["-i", a.musica]
        mi = a.musica_inicio if a.musica_inicio is not None else de
        seg += (f"[v];[2:a]atrim={mi:.3f}:{mi + vaga:.3f},asetpts=PTS-STARTPTS,aresample=48000,"
                f"aformat=channel_layouts=stereo,volume={a.musica_db}dB[m];[v][m]amix=inputs=2:normalize=0")
    with tempfile.TemporaryDirectory() as tmp:
        bruto = Path(tmp) / "seg.wav"
        rodar(["ffmpeg", "-nostdin", "-y", "-v", "error", *entradas, "-filter_complex", seg + "[o]", "-map", "[o]",
               "-c:a", "pcm_s24le", str(bruto)])
        orig, novo = lufs(video, de, ate), lufs(bruto)
        ganho = (orig - novo) if orig is not None and novo is not None else 0.0
        partes, rot = [], []
        if de > 0.05:
            partes.append(f"[0:a]atrim=0:{de:.3f},asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo,"
                          f"afade=t=out:st={max(de - 0.05, 0):.3f}:d=0.05[p0]")
            rot.append("[p0]")
        partes.append(f"[1:a]volume={ganho:.2f}dB,alimiter=limit=0.89:level=false,afade=t=in:d=0.05,"
                      f"afade=t=out:st={vaga - 0.05:.3f}:d=0.05[p1]")
        rot.append("[p1]")
        if dur - ate > 0.05:
            partes.append(f"[0:a]atrim=start={ate:.3f},asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo,"
                          f"afade=t=in:d=0.05[p2]")
            rot.append("[p2]")
        fc = ";".join(partes) + f";{''.join(rot)}concat=n={len(rot)}:v=0:a=1[o]"
        saida = Path(a.saida or video.with_name(video.stem + "-voz-nova.mp4"))
        rodar(["ffmpeg", "-nostdin", "-y", "-v", "error", "-i", str(video), "-i", str(bruto), "-filter_complex", fc,
               "-map", "0:v:0", "-map", "[o]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
               str(saida)])
    print(f"ok {saida} (fala de {vd:.1f} s no trecho {de:.1f}-{ate:.1f} s, ganho {ganho:+.1f} dB"
          + (f", acelerada {tempo:.2f}x" if tempo > 1 else "") + ")")
    return saida


# ---------- API da Meta (opcional) ----------
def credenciais():
    if not CONFIG.is_file():
        erro(f"falta {CONFIG}. Siga referencias/TOKEN-META.md (o token nunca vai para o chat).")
    env = {}
    for l in CONFIG.read_text().splitlines():
        if "=" in l and not l.strip().startswith("#"):
            k, v = l.split("=", 1)
            env[k.strip()] = v.strip()
    if not env.get("META_TOKEN"):
        erro(f"META_TOKEN vazio em {CONFIG}.")
    return env


def graph(metodo, caminho, params, token, base=GRAPH, corpo=None, cabecalhos=None):
    """Chamada à Graph API. O token vai no corpo (POST) ou na query (GET) e nunca aparece em mensagem de erro."""
    params = {**params, "access_token": token}
    url = f"{base}/{caminho}"
    dados = corpo
    if metodo == "GET":
        url += "?" + urllib.parse.urlencode(params)
    elif corpo is None:
        dados = urllib.parse.urlencode(params).encode()
    req = urllib.request.Request(url, data=dados, method=metodo, headers=cabecalhos or {})
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        corpo_erro = e.read().decode("utf-8", "replace")
        try:
            msg = json.loads(corpo_erro)["error"]["message"]
        except (ValueError, KeyError, TypeError):
            msg = corpo_erro[:300]
        raise RuntimeError(f"Graph API {e.code} em {caminho.split('?')[0]}: {msg.replace(token, '***')}") from None


def ig_id(env):
    """IG_USER_ID do meta.env; sem ele, usa a única conta do Instagram ligada às páginas do token."""
    if env.get("IG_USER_ID"):
        return env["IG_USER_ID"]
    r = graph("GET", "me/accounts", {"fields": "instagram_business_account"}, env["META_TOKEN"])
    ids = [p["instagram_business_account"]["id"] for p in r.get("data", []) if p.get("instagram_business_account")]
    if len(ids) != 1:
        erro(f"achei {len(ids)} contas do Instagram no token: rode o comando contas e grave IG_USER_ID em {CONFIG}.")
    return ids[0]


def params_trial(legenda, estrategia):
    """Parâmetros do contêiner de Reel de teste (trial reel). SS_PERFORMANCE = o Instagram mostra aos seguidores
    sozinho se for bem; MANUAL = você decide no app."""
    return {"media_type": "REELS", "upload_type": "resumable", "caption": legenda,
            "trial_params": json.dumps({"graduation_strategy": estrategia})}


def cmd_contas(_a):
    env = credenciais()
    r = graph("GET", "me/accounts", {"fields": "name,instagram_business_account{id,username}"}, env["META_TOKEN"])
    for p in r.get("data", []):
        ig = p.get("instagram_business_account") or {}
        print(f"Página '{p.get('name')}': Instagram @{ig.get('username', '-')} IG_USER_ID={ig.get('id', '(sem conta ligada)')}")
    return 0


def cmd_medir(a):
    env = credenciais()
    tok, ig = env["META_TOKEN"], ig_id(env)
    reg = ids_registro(a.registro)
    r = graph("GET", f"{ig}/media", {"fields": "id,media_type,media_product_type,permalink,timestamp", "limit": a.limite}, tok)
    midias = [m for m in r.get("data", []) if m.get("media_product_type") == "REELS" or m.get("media_type") == "VIDEO"]
    vistos = {m["id"] for m in midias}
    for mid in reg:  # Reels de teste podem não vir na lista do perfil: busca cada um pelo ID anotado ao postar
        if mid not in vistos:
            try:
                midias.append(graph("GET", mid, {"fields": "id,media_type,media_product_type,permalink,timestamp"}, tok))
            except RuntimeError as e:
                print(f"aviso: {e}", file=sys.stderr)
    linhas = []
    for m in midias:
        try:
            ins = graph("GET", f"{m['id']}/insights", {"metric": "views,reach,saved,shares,likes,comments"}, tok)
        except RuntimeError as e:
            print(f"aviso: {m['id']} sem métricas ({e})", file=sys.stderr)
            continue
        v = {i["name"]: (i.get("values") or [{}])[0].get("value", i.get("total_value", {}).get("value", 0)) for i in ins.get("data", [])}
        rg = reg.get(m["id"], {})
        linhas.append({"id": m["id"], "postado": data(m["timestamp"]), "views": v.get("views", 0), "alcance": v.get("reach", 0),
                       "salvos": v.get("saved", 0), "compartilhamentos": v.get("shares", 0), "curtidas": v.get("likes", 0),
                       "comentarios": v.get("comments", 0), "teste": rg.get("variante", ""), "campeao": rg.get("campeao", ""),
                       "link": m.get("permalink", "")})
    salvar_metricas(linhas, a.saida)
    print(f"ok {len(linhas)} Reel(s) em {a.saida}")
    return 0


def cmd_postar(a):
    env = credenciais()
    tok, ig = env["META_TOKEN"], ig_id(env)
    video = Path(a.video)
    leg = Path(a.legenda).read_text(encoding="utf-8").strip() if a.legenda else ""
    params = params_trial(leg, a.graduacao)
    if a.normal:  # Reel comum (aparece para os seguidores e no perfil), sem trial_params
        params.pop("trial_params"); params["share_to_feed"] = "true"
    if a.url:  # vídeo num link público: o envio direto falha em vídeos acima de ~60 s (ProcessingFailedError)
        params.pop("upload_type"); params["video_url"] = a.url
    c = graph("POST", f"{ig}/media", {**params, **({"thumb_offset": a.capa_ms} if a.capa_ms is not None else {})}, tok)
    if not a.url:
        graph("POST", c["id"], {}, tok, base=RUPLOAD, corpo=video.read_bytes(),
              cabecalhos={"Authorization": f"OAuth {tok}", "offset": "0", "file_size": str(video.stat().st_size)})
    for _ in range(60):  # até 10 min processando
        st = graph("GET", c["id"], {"fields": "status_code,status"}, tok)
        if st.get("status_code") == "FINISHED":
            break
        if st.get("status_code") == "ERROR":
            erro(f"o Instagram recusou o vídeo: {st.get('status')}")
        time.sleep(10)
    else:
        erro("o vídeo não terminou de processar em 10 min. Nada foi publicado; tente de novo mais tarde.")
    pub = graph("POST", f"{ig}/media_publish", {"creation_id": c["id"]}, tok)
    link = graph("GET", pub["id"], {"fields": "permalink"}, tok).get("permalink", "")
    novo = not Path(a.registro).is_file()
    with open(a.registro, "a", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, REGISTRO_CAMPOS)
        if novo:
            w.writeheader()
        w.writerow({"data": datetime.now().astimezone().isoformat(timespec="minutes"), "campeao": a.campeao,
                    "variante": a.variante or video.stem, "variavel": VARIAVEL.get((a.variante or video.stem).split("-")[0], ""),
                    "media_id": pub["id"], "link": link})
    print(f"ok Reel {'comum' if a.normal else 'de teste'} publicado: {link} (anotado em {a.registro})")
    return 0


# ---------- autoteste ----------
def pixel(mp4, t, x=5, y=5):
    p = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-i", str(mp4), "-vf", f"crop=2:2:{x}:{y},format=rgb24", "-frames:v", "1",
                        "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True)
    return tuple(p.stdout[:3])


def teste():
    agora = data("2026-11-17 09:00")
    h = lambda horas: agora - timedelta(hours=horas)  # noqa: E731
    lin = lambda i, horas, views, **kw: {**{k: 0 for k in NUMEROS}, "id": i, "postado": h(horas), "views": views,  # noqa: E731
                                          "teste": "", "campeao": "", "link": "", **kw}
    m = [lin("a", 50, 900, salvos=10), lin("b", 60, 900, salvos=40), lin("c", 120, 200), lin("d", 200, 100),
         lin("novo", 10, 99999), lin("t1", 70, 5000, teste="r1", campeao="b")]
    top, media, janela, base = escolher_campeao(m, agora)
    assert [l["id"] for l in base] == ["a", "b", "c", "d"] and media == 525, (base, media)  # sem o novo (<48 h) e sem teste
    assert top["id"] == "b", top  # empate em views: desempata por salvos + compartilhamentos
    assert escolher_campeao(m, agora, excluir={"a", "b"})[0] is None  # janela vazia
    assert escolher_campeao([lin("a", 50, 100), lin("c", 120, 900)], agora)[0] is None  # abaixo da média
    assert escolher_campeao([], agora) == (None, 0.0, [], [])
    ts = [lin(f"t{i}", 50, v, teste=f"r{i}") for i, v in enumerate([300, 320, 310, 500])]
    assert escolher_vencedor(ts)[0]["teste"] == "r3"
    assert escolher_vencedor(ts[:3])[0] is None  # ninguém 20% acima da mediana
    assert escolher_vencedor([lin("x", 50, 80, teste="a"), lin("y", 50, 10, teste="b")])[0] is None  # < 100 views
    ag = agenda("2026-11-17")
    assert [p["dia"] for p in ag] == [0, 2, 4, 7, 14, 21, 28, 35, 42, 49, 56]
    assert [p["variante"] for p in ag[3:]] == ["cenario", "cta", "gancho"] * 2 + ["cenario", "cta"]
    assert ag[-1]["quando"] == "12/01/2027"
    assert data("2026-11-15T12:30:00+0000").utcoffset() == timedelta(0)
    p = params_trial("legenda", "SS_PERFORMANCE")
    assert json.loads(p["trial_params"]) == {"graduation_strategy": "SS_PERFORMANCE"} and p["media_type"] == "REELS"
    print("regras: ok")

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        for ext in ("csv", "json"):  # leitura de métricas nos dois formatos
            arq = tmp / f"m.{ext}"
            if ext == "csv":
                salvar_metricas(m, arq)
            else:
                arq.write_text(json.dumps([{**l, "postado": l["postado"].isoformat()} for l in m]))
            assert escolher_campeao(carregar_metricas(arq), agora)[0]["id"] == "b", ext
        print("métricas csv/json: ok")

        base_mp4 = tmp / "base.mp4"
        rodar(["ffmpeg", "-nostdin", "-y", "-v", "error", "-f", "lavfi", "-i", "color=c=0x3366CC:s=1080x1920:d=5:r=30",
               "-f", "lavfi", "-i", "sine=frequency=440:duration=5", "-shortest", "-c:v", "libx264", "-pix_fmt", "yuv420p",
               "-c:a", "aac", str(base_mp4)])
        a = argparse.Namespace(video=str(base_mp4), titulos="O erro que estraga seu som|Ninguém te conta isso|Salva: 50% faz errado",
                               ganchos="O erro que destrói seu som|O detalhe que estraga seu som", fontes="",
                               cta="COMENTA CURSO|que eu te mando o capítulo grátis", cta_inicio=None, so="", saida=str(tmp / "var"))
        feitos = cmd_variacoes(a)
        nomes = sorted(f.stem for f in feitos)
        assert nomes == sorted(["r1", "r2", "r3", "cenario-1-escuro", "cenario-2-quente", "cenario-3-frio", "cta",
                                "gancho-1", "gancho-2"]), nomes
        for f in feitos:
            d, au = info(f)
            assert au and (4.7 if f.stem == "r3" else 4.9) <= d <= 5.1, (f.stem, d)
        orig = pixel(base_mp4, 1)
        assert max(pixel(tmp / "var/r1.mp4", 1)) < 30, "r1 sem faixa preta no topo"
        assert pixel(tmp / "var/r2.mp4", 1)[0] > 200, "r2 sem faixa amarela no topo"
        assert abs(pixel(tmp / "var/r1.mp4", 4.5)[2] - orig[2]) < 60, "faixa do r1 não sumiu depois de 3,5 s"
        assert pixel(tmp / "var/cta.mp4", 4, 5, 750)[2] < 30 and pixel(tmp / "var/cta.mp4", 0.2, 5, 750)[2] > 100, "CTA fora de hora"
        assert pixel(tmp / "var/cenario-1-escuro.mp4", 2) != pixel(tmp / "var/cenario-3-frio.mp4", 2)
        print("variações visuais: ok")

        fala = tmp / "fala.wav"
        rodar(["ffmpeg", "-nostdin", "-y", "-v", "error", "-f", "lavfi", "-i", "sine=frequency=880:duration=1.6", str(fala)])
        v = argparse.Namespace(video=str(tmp / "var/gancho-1.mp4"), voz=str(fala), de=0.0, ate=2.0, musica=None,
                               musica_inicio=None, musica_db=-18.0, saida=str(tmp / "gancho-1-voz.mp4"))
        d, au = info(cmd_voz(v))
        assert au and 4.9 <= d <= 5.1, d
        v.de, v.ate, v.musica, v.saida = 3.0, 5.0, str(base_mp4), str(tmp / "cta-voz.mp4")
        assert 4.9 <= info(cmd_voz(v))[0] <= 5.1
        print("troca de voz: ok")
    print("TESTE OK (nenhuma API chamada)")
    return 0


def main():
    if "--teste" in sys.argv:
        return teste()
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0], formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("campeao", help="escolhe o campeão a partir das métricas")
    s.add_argument("metricas")
    s.add_argument("--agora", help="data/hora de referência (padrão: agora)")
    s.add_argument("--min-horas", type=float, default=48)
    s.add_argument("--max-horas", type=float, default=96)
    s.add_argument("--base", type=int, default=30, help="quantos Reels entram na média (padrão 30)")
    s.add_argument("--registro", default="registro.csv", help="campeões já usados saem da escolha")
    s.set_defaults(f=cmd_campeao)
    s = sub.add_parser("vencedor", help="lê o resultado dos Reels de teste")
    s.add_argument("metricas")
    s.add_argument("--campeao")
    s.add_argument("--folga", type=float, default=1.2, help="quanto acima da mediana (padrão 1.2 = 20%%)")
    s.add_argument("--minimo", type=int, default=100, help="views mínimas do vencedor")
    s.set_defaults(f=cmd_vencedor)
    s = sub.add_parser("variacoes", help="gera as variações visuais de um MP4")
    s.add_argument("video")
    s.add_argument("--titulos", help='"título 1|título 2|título 3" (fase 1)')
    s.add_argument("--ganchos", help='"gancho com 1 palavra trocada|outro" (fase 2)')
    s.add_argument("--cta", default="COMENTA CURSO|que eu te mando o capítulo grátis", help='"LINHA GRANDE|linha menor"')
    s.add_argument("--cta-inicio", type=float, help="segundo em que o CTA aparece (padrão: últimos 4,5 s)")
    s.add_argument("--fontes", help='"a.ttf|b.ttf|c.ttf" (padrão: Impact, Courier New e Arial em negrito)')
    s.add_argument("--so", help="só estas: r1,r2,r3,cenario,cta,gancho")
    s.add_argument("--saida")
    s.set_defaults(f=cmd_variacoes)
    s = sub.add_parser("voz", help="troca o áudio de um trecho por uma fala nova")
    s.add_argument("video")
    s.add_argument("--voz", required=True)
    s.add_argument("--de", type=float, required=True)
    s.add_argument("--ate", type=float, required=True)
    s.add_argument("--musica", help="a trilha do vídeo, para ficar por baixo da fala nova")
    s.add_argument("--musica-inicio", type=float, help="ponto da trilha que toca nesse trecho (padrão: --de)")
    s.add_argument("--musica-db", type=float, default=-18.0)
    s.add_argument("--saida")
    s.set_defaults(f=cmd_voz)
    s = sub.add_parser("medir", help="(API) baixa as métricas dos Reels")
    s.add_argument("--saida", default="metricas.csv")
    s.add_argument("--limite", type=int, default=50)
    s.add_argument("--registro", default="registro.csv")
    s.set_defaults(f=cmd_medir)
    s = sub.add_parser("postar", help="(API) posta um MP4 como Reel de teste")
    s.add_argument("video")
    s.add_argument("--legenda", help="arquivo .txt com a legenda")
    s.add_argument("--campeao", default="", help="ID do Reel campeão de origem")
    s.add_argument("--variante", help="r1, r2, r3, cenario-1, cta, gancho-1... (padrão: nome do arquivo)")
    s.add_argument("--graduacao", choices=["SS_PERFORMANCE", "MANUAL"], default="SS_PERFORMANCE")
    s.add_argument("--url", help="link público HTTPS do mesmo vídeo (use para vídeos acima de ~60 s)")
    s.add_argument("--normal", action="store_true", help="posta como Reel comum (não de teste)")
    s.add_argument("--capa-ms", type=int, help="quadro do vídeo usado como capa, em milissegundos (ex.: 150 com a capa nos 0,3 s iniciais)")
    s.add_argument("--registro", default="registro.csv")
    s.set_defaults(f=cmd_postar)
    s = sub.add_parser("contas", help="(API) mostra o IG_USER_ID de cada página")
    s.set_defaults(f=cmd_contas)
    a = ap.parse_args()
    if a.cmd in ("variacoes", "voz") and not shutil.which("ffmpeg"):
        erro("ffmpeg não encontrado. Mac: brew install ffmpeg | Windows: winget install ffmpeg | Linux: apt install ffmpeg")
    try:
        r = a.f(a)
    except RuntimeError as e:
        erro(str(e))
    return r if isinstance(r, int) else 0


if __name__ == "__main__":
    sys.exit(main())
