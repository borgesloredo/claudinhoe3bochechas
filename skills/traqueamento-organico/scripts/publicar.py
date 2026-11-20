#!/usr/bin/env python3
"""Publicador diário (OPCIONAL). Instagram Reels e Facebook Reels pela API oficial da Meta, com os tokens do próprio
comprador; TikTok, YouTube, Kwai e Pinterest viram lembrete "postar à mão" com o texto pronto. Só biblioteca padrão.

Por que só Meta automático: é a única das 6 com publicação oficial simples para conta comum. TikTok exige app auditado
(sem auditoria o post sai privado), YouTube exige OAuth com cota diária, Kwai não tem API e Pinterest exige app aprovado.
Automação de navegador nessas redes é não oficial (risco de bloqueio): ver references/publicar.md.

Regras que vieram de erros reais:
- "incerto" (a rede pode ter recebido e a resposta não voltou) NUNCA repete sozinho: post duplicado queima o perfil.
- falha clara (a rede recusou) repete até 2 vezes.
- 1 post por rede por rodada: atraso não vira rajada de posts.
- horário no fuso da agenda (servidor em outro país tem outro relógio).

Credenciais (nunca no chat): ~/.config/traqueamento-organico/meta.env com META_TOKEN, FB_PAGE_ID, IG_USER_ID.

Uso:
  publicar.py planejar PASTA --inicio AAAA-MM-DD --horarios 12:00,19:00 --url-base https://seu-arquivo/videos/
                       [--redes instagram,facebook,tiktok,youtube,kwai,pinterest] [--fuso America/Sao_Paulo] [--auto-dm]
      PASTA tem pares NNN.mp4 + NNN.txt (texto base do textos_por_rede.py). O vídeo precisa estar num link público
      (--url-base + nome do arquivo): a Meta baixa o vídeo de lá.
  publicar.py rodar [--seco]          rode a cada 10 min (cron/launchd); imprime só quando algo acontece
  publicar.py status | repetir ID REDE | --teste
  Opção geral: --agenda agenda.json (padrão ./agenda.json)
"""
import argparse
import fcntl
import json
import os
import socket
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parent))
import textos_por_rede as T  # noqa: E402

VERSAO = os.environ.get("META_GRAPH_VERSAO", "v27.0")  # confira a versão atual em developers.facebook.com/docs/graph-api/changelog
GRAPH = f"https://graph.facebook.com/{VERSAO}"
AUTO = ("instagram", "facebook")
REDES = ("instagram", "facebook", "tiktok", "youtube", "kwai", "pinterest")
CRED = Path.home() / ".config/traqueamento-organico/meta.env"
TENTATIVAS = 2


class Falha(Exception):
    """A rede recusou: nada foi publicado, pode tentar de novo."""


class Incerto(Exception):
    """Pedido final enviado sem resposta: pode ter publicado. Não repetir sozinho."""


def credenciais():
    c = {}
    if CRED.is_file():
        for linha in CRED.read_text().splitlines():
            if "=" in linha and not linha.lstrip().startswith("#"):
                k, v = linha.split("=", 1)
                c[k.strip()] = v.strip().strip('"')
    c.update({k: os.environ[k] for k in ("META_TOKEN", "FB_PAGE_ID", "IG_USER_ID") if os.environ.get(k)})
    return c


def http(metodo, url, dados=None, token=None, cab=None, final=False):
    """Chamada à Graph API. Token vai no cabeçalho (nunca na URL, para não vazar em log)."""
    h = dict(cab or {})
    if token:
        h["Authorization"] = f"OAuth {token}"
    corpo = urllib.parse.urlencode(dados).encode() if dados is not None else (b"" if metodo == "POST" else None)
    req = urllib.request.Request(url, data=corpo, headers=h, method=metodo)
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        try:
            msg = json.loads(e.read()).get("error", {}).get("message", "")
        except Exception:
            msg = ""
        raise Falha(f"HTTP {e.code} {msg}".strip())
    except (urllib.error.URLError, socket.timeout, ConnectionError, TimeoutError) as e:
        if final:
            raise Incerto(f"sem resposta da rede ({type(e).__name__})")
        raise Falha(f"rede fora ({type(e).__name__})")


def pub_instagram(c, video_url, legenda, chamar=http, dormir=time.sleep):
    ig, tok = c["IG_USER_ID"], c["META_TOKEN"]
    cont = chamar("POST", f"{GRAPH}/{ig}/media", {"media_type": "REELS", "video_url": video_url, "caption": legenda,
                                                   "share_to_feed": "true"}, tok)["id"]
    for _ in range(60):  # a Meta baixa e processa o vídeo: até ~10 min
        st = chamar("GET", f"{GRAPH}/{cont}?fields=status_code", None, tok).get("status_code")
        if st == "FINISHED":
            break
        if st in ("ERROR", "EXPIRED"):
            raise Falha(f"Instagram não aceitou o vídeo ({st})")
        dormir(10)
    else:
        raise Falha("vídeo não ficou pronto em 10 min")
    return chamar("POST", f"{GRAPH}/{ig}/media_publish", {"creation_id": cont}, tok, final=True)["id"]


def pub_facebook(c, video_url, legenda, titulo, chamar=http):
    pg, tok = c["FB_PAGE_ID"], c["META_TOKEN"]
    s = chamar("POST", f"{GRAPH}/{pg}/video_reels", {"upload_phase": "start"}, tok)
    chamar("POST", s["upload_url"], None, None, {"Authorization": f"OAuth {tok}", "file_url": video_url})
    r = chamar("POST", f"{GRAPH}/{pg}/video_reels", {"upload_phase": "finish", "video_id": s["video_id"],
                                                      "video_state": "PUBLISHED", "description": legenda, "title": titulo},
               tok, final=True)
    if not r.get("success"):
        raise Falha("Facebook não confirmou a publicação")
    return s["video_id"]


def carregar(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def salvar(p, ag):
    tmp = Path(str(p) + ".tmp")
    tmp.write_text(json.dumps(ag, ensure_ascii=False, indent=1), encoding="utf-8")
    tmp.replace(p)


def cmd_planejar(a):
    pasta = Path(a.pasta).resolve()
    videos = sorted(v for v in pasta.glob("*.mp4") if (v.with_suffix(".txt")).is_file())
    if not videos:
        raise SystemExit(f"Nenhum par NNN.mp4 + NNN.txt em {pasta}")
    redes = [r for r in a.redes.split(",") if r]
    if set(redes) - set(REDES):
        raise SystemExit(f"Redes válidas: {','.join(REDES)}")
    horarios = sorted(a.horarios.split(","))
    dia, itens = datetime.fromisoformat(a.inicio), []
    while len(itens) < len(videos):
        for h in horarios:
            if len(itens) < len(videos):
                v = videos[len(itens)]
                b = T.ler_base(v.with_suffix(".txt"))
                (v.parent / f"{v.stem}.redes.txt").write_text(T.como_texto(b, T.gerar(b, a.auto_dm)), encoding="utf-8")
                itens.append({"id": v.stem, "video": str(v), "base": str(v.with_suffix(".txt")),
                              "video_url": a.url_base.rstrip("/") + "/" + urllib.parse.quote(v.name),
                              "quando": f"{dia.date().isoformat()}T{h}",
                              "redes": {r: {"status": "pendente" if r in AUTO else "manual"} for r in redes}})
        dia += timedelta(days=1)
    salvar(a.agenda, {"fuso": a.fuso, "auto_dm": a.auto_dm, "itens": itens})
    print(f"Agenda: {a.agenda} ({len(itens)} vídeos, de {itens[0]['quando']} a {itens[-1]['quando']}, {a.fuso}). "
          "Nada foi publicado. Confira e só então ligue o 'rodar'.")


def rodar(caminho, seco=False, agora=None, chamar=http, dormir=time.sleep, cred=None):
    """Uma rodada. Devolve as linhas impressas (para o teste)."""
    ag = carregar(caminho)
    tz = ZoneInfo(ag.get("fuso", "America/Sao_Paulo"))
    agora = agora or datetime.now(tz)
    c = cred if cred is not None else credenciais()
    falta = [k for k in ("META_TOKEN", "FB_PAGE_ID", "IG_USER_ID") if not c.get(k)]
    saida, feitas = [], set()

    def diz(t):
        saida.append(t)
        print(t)
    for it in sorted(ag["itens"], key=lambda i: i["quando"]):
        if datetime.fromisoformat(it["quando"]).replace(tzinfo=tz) > agora:
            continue
        b = T.ler_base(it["base"])
        txt = T.gerar(b, ag.get("auto_dm", False))
        for rede, st in it["redes"].items():
            if st["status"] == "manual":
                diz(f"postar à mão: {it['id']} no {rede} (vídeo {it['video']}, texto em {Path(it['base']).stem}.redes.txt)")
                if not seco:
                    st["status"] = "avisado"
                continue
            pode = st["status"] == "pendente" or (st["status"] == "falhou" and st.get("tentativas", 0) < TENTATIVAS)
            if rede not in AUTO or not pode or rede in feitas:
                continue
            feitas.add(rede)  # 1 por rede por rodada
            if seco:
                diz(f"[seco] publicaria {it['id']} no {rede}")
                continue
            if falta:
                diz(f"{rede}: faltam credenciais em {CRED} ({', '.join(falta)}); nada publicado")
                continue
            try:
                if rede == "instagram":
                    ref = pub_instagram(c, it["video_url"], txt["instagram"]["legenda"], chamar, dormir)
                else:
                    ref = pub_facebook(c, it["video_url"], txt["facebook"]["legenda"], txt["facebook"]["titulo"], chamar)
                st.update(status="ok", ref=ref, em=agora.isoformat(timespec="seconds"))
                diz(f"ok: {it['id']} no {rede} ({ref})")
            except Incerto as e:
                st.update(status="incerto", erro=str(e), em=agora.isoformat(timespec="seconds"))
                diz(f"INCERTO: {it['id']} no {rede}: {e}. Confira no app se saiu. Se não saiu: publicar.py repetir {it['id']} {rede}")
            except (Falha, KeyError) as e:
                st.update(status="falhou", erro=str(e), tentativas=st.get("tentativas", 0) + 1)
                diz(f"falhou: {it['id']} no {rede} (tentativa {st['tentativas']} de {TENTATIVAS}): {e}")
            salvar(caminho, ag)  # grava a cada post: se cair no meio, não repete o que já saiu
    if not seco:
        salvar(caminho, ag)
    return saida


def cmd_status(a):
    ag = carregar(a.agenda)
    cont = {}
    for it in ag["itens"]:
        for rede, st in it["redes"].items():
            cont.setdefault(rede, {}).setdefault(st["status"], 0)
            cont[rede][st["status"]] += 1
    for rede, c in cont.items():
        print(f"{rede:10} " + " · ".join(f"{k} {v}" for k, v in sorted(c.items())))
    for it in ag["itens"]:
        for rede, st in it["redes"].items():
            if st["status"] in ("incerto", "falhou"):
                print(f"  {it['id']} {rede}: {st['status']} — {st.get('erro', '')}")


def cmd_repetir(a):
    ag = carregar(a.agenda)
    it = next((i for i in ag["itens"] if i["id"] == a.id), None)
    if not it or a.rede not in it["redes"]:
        raise SystemExit("ID ou rede não está na agenda")
    it["redes"][a.rede] = {"status": "pendente"}
    salvar(a.agenda, ag)
    print(f"{a.id} no {a.rede} volta para a fila na próxima rodada")


def teste():
    import contextlib
    import io
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        for n in ("001", "002", "003"):
            (d / f"{n}.mp4").write_bytes(b"falso")
            (d / f"{n}.txt").write_text(f"TÍTULO: Vídeo {n}\nTEXTO: Dica de teste.\nCTA: Comenta MESA que eu te mando o guia.\n"
                                        "HASHTAGS: #a #b #c\nLINK: https://exemplo.com.br/\n")
        ag = d / "agenda.json"
        A = argparse.Namespace(pasta=str(d), inicio="2099-01-01", horarios="19:00,12:00", url_base="https://arquivos.exemplo.com/v/",
                               redes="instagram,facebook,tiktok", fuso="America/Sao_Paulo", auto_dm=False, agenda=str(ag))
        with contextlib.redirect_stdout(io.StringIO()):
            cmd_planejar(A)
        itens = carregar(ag)["itens"]
        assert [i["quando"] for i in itens] == ["2099-01-01T12:00", "2099-01-01T19:00", "2099-01-02T12:00"]
        assert itens[0]["video_url"] == "https://arquivos.exemplo.com/v/001.mp4" and (d / "001.redes.txt").is_file()
        cred = {"META_TOKEN": "TOKEN-FALSO-123", "FB_PAGE_ID": "pagina", "IG_USER_ID": "ig"}
        chamadas, plano = [], {}

        def falso(metodo, url, dados=None, token=None, cab=None, final=False):
            chamadas.append((metodo, url, dados, final))
            assert "TOKEN-FALSO" not in url
            r = plano.get("r", {})
            for k, v in r.items():
                if k in url and (k != "video_reels" or (dados or {}).get("upload_phase") == ("finish" if v.get("_fim") else "start")):
                    if isinstance(v.get("_erro"), type):
                        raise v["_erro"]("teste")
                    return v
            if url.endswith("/media"):
                return {"id": "cont1"}
            if "status_code" in url:
                return {"status_code": "FINISHED"}
            if url.endswith("/media_publish"):
                return {"id": "igpost1"}
            if "video_reels" in url and dados["upload_phase"] == "start":
                return {"video_id": "fbv1", "upload_url": "https://rupload.exemplo/fbv1"}
            if "video_reels" in url:
                return {"success": True}
            return {"success": True}
        tz = ZoneInfo("America/Sao_Paulo")
        cedo = datetime(2098, 12, 31, 23, 0, tzinfo=tz)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            assert rodar(ag, agora=cedo, chamar=falso, cred=cred) == []  # nada venceu: silêncio
            # 01/01 20h: 001 e 002 venceram -> só 1 por rede por rodada; Facebook fica INCERTO no passo final
            plano["r"] = {"video_reels": {"_fim": True, "_erro": Incerto}}
            linhas = rodar(ag, agora=datetime(2099, 1, 1, 20, 0, tzinfo=tz), chamar=falso, dormir=lambda s: None, cred=cred)
        assert "ok: 001 no instagram (igpost1)" in linhas and any(l.startswith("INCERTO: 001 no facebook") for l in linhas)
        assert sum(l.startswith("postar à mão") for l in linhas) == 2  # tiktok de 001 e de 002, uma vez cada
        st = {i["id"]: i["redes"] for i in carregar(ag)["itens"]}
        assert st["002"]["instagram"]["status"] == "pendente" and st["001"]["facebook"]["status"] == "incerto"
        # próxima rodada: 002 no Instagram falha (container com erro) e no Facebook sai; o 001 incerto NÃO repete
        plano["r"] = {"status_code": {"status_code": "ERROR"}}
        with contextlib.redirect_stdout(out):
            linhas = rodar(ag, agora=datetime(2099, 1, 1, 20, 10, tzinfo=tz), chamar=falso, dormir=lambda s: None, cred=cred)
        assert "ok: 002 no facebook (fbv1)" in linhas and any("falhou: 002 no instagram (tentativa 1" in l for l in linhas)
        assert not any("001" in l for l in linhas) and not any("postar à mão" in l for l in linhas)
        with contextlib.redirect_stdout(out):
            rodar(ag, agora=datetime(2099, 1, 1, 20, 20, tzinfo=tz), chamar=falso, dormir=lambda s: None, cred=cred)
            linhas = rodar(ag, agora=datetime(2099, 1, 1, 20, 30, tzinfo=tz), chamar=falso, dormir=lambda s: None, cred=cred)
        assert carregar(ag)["itens"][1]["redes"]["instagram"]["tentativas"] == 2 and linhas == []  # parou em 2
        # seco não muda nada; sem credencial não publica; o token nunca aparece na saída
        antes = ag.read_text()
        with contextlib.redirect_stdout(out):
            linhas = rodar(ag, seco=True, agora=datetime(2099, 1, 3, 0, 0, tzinfo=tz), chamar=falso, cred=cred)
        assert ag.read_text() == antes and "[seco] publicaria 003 no instagram" in linhas
        with contextlib.redirect_stdout(out):
            linhas = rodar(ag, agora=datetime(2099, 1, 3, 0, 0, tzinfo=tz), chamar=falso, cred={})
        assert any("faltam credenciais" in l for l in linhas)
        assert "TOKEN-FALSO" not in out.getvalue()
        assert any(c[1].endswith("/media_publish") and c[3] for c in chamadas)  # publicar é o passo "final"
        with contextlib.redirect_stdout(out):
            cmd_repetir(argparse.Namespace(agenda=str(ag), id="001", rede="facebook"))
        assert carregar(ag)["itens"][0]["redes"]["facebook"] == {"status": "pendente"}
    print("teste ok")


def main():
    if "--teste" in sys.argv:
        teste()
        return
    ap = argparse.ArgumentParser(description="Publicador diário: Meta pela API oficial, outras redes como lembrete.")
    ap.add_argument("--agenda", default="agenda.json")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("planejar")
    p.add_argument("pasta")
    p.add_argument("--inicio", required=True)
    p.add_argument("--horarios", default="12:00,19:00")
    p.add_argument("--url-base", required=True)
    p.add_argument("--redes", default=",".join(REDES))
    p.add_argument("--fuso", default="America/Sao_Paulo")
    p.add_argument("--auto-dm", action="store_true")
    p = sub.add_parser("rodar")
    p.add_argument("--seco", action="store_true")
    sub.add_parser("status")
    p = sub.add_parser("repetir")
    p.add_argument("id")
    p.add_argument("rede")
    a = ap.parse_args()
    if a.cmd == "planejar":
        cmd_planejar(a)
    elif a.cmd == "rodar":
        with open(str(a.agenda) + ".lock", "w") as trava:
            try:
                fcntl.flock(trava, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                return  # rodada anterior ainda publicando
            rodar(a.agenda, a.seco)
    elif a.cmd == "status":
        cmd_status(a)
    else:
        cmd_repetir(a)


if __name__ == "__main__":
    main()
