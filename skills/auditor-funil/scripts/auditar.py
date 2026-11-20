#!/usr/bin/env python3
"""Auditor do funil de venda. Confere, como um comprador, o que o funil.json manda: página no ar, textos, preço,
botões de compra, pixels, prévia de compartilhamento, a tela seguinte do checkout e as funções do servidor. Antes das
páginas, chama as rotinas do servidor que corrigem sozinhas (e-mail que não saiu, acesso que não chegou) e junta o que
elas responderem. Salva o resultado (painel "Saúde") e avisa no Telegram quando há problema ou correção.
Só biblioteca padrão do Python 3.9+. Não roda JavaScript: o navegador continua sendo a prova final (veja SKILL.md).

Uso:
  python3 auditar.py funil.json                     rodada normal (agendada)
  python3 auditar.py funil.json --teste             ensaio: imprime tudo e não manda Telegram
  python3 auditar.py funil.json --testar-telegram   manda uma mensagem de teste ao Telegram
  python3 auditar.py --autoteste                    confere o próprio script num servidor local de mentira
Saída: 0 tudo certo, 1 há problema, 2 configuração errada.
Segredos: arquivos KEY=valor em ~/.config/auditor-funil/*.env (ou variáveis de ambiente, ex.: GitHub Actions).
"""
import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

TELEGRAM_API = "https://api.telegram.org"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) auditor-funil/1.0"
PASTA_SEGREDOS = Path(os.environ.get("AUDITOR_FUNIL_ENV", str(Path.home() / ".config" / "auditor-funil")))
HISTORICO_MAX = 500  # ~41 dias com uma rodada a cada 2 h


# ---------- utilidades ----------

def check(id_, nome, ok, detalhe, corrigidos=0, itens=None):
    return {"id": id_, "nome": nome, "ok": bool(ok), "detalhe": detalhe, "corrigidos": corrigidos, "itens": (itens or [])[:30]}


def norm(t):
    return re.sub(r"\s+", " ", html.unescape(str(t)).replace(" ", " ")).strip().casefold()


def pegar(url, metodo="GET", corpo=None, cab=None, limite=3_000_000, tempo=20):
    """(status ou None, texto, url final, segundos). Nunca levanta exceção."""
    h = {"User-Agent": UA, "Accept-Language": "pt-BR,pt;q=0.9", **({"Content-Type": "application/json"} if corpo is not None else {}), **(cab or {})}
    req = urllib.request.Request(url, data=corpo.encode() if corpo is not None else None, method=metodo, headers=h)
    t = time.time()
    try:
        with urllib.request.urlopen(req, timeout=tempo) as r:
            return r.status, r.read(limite).decode(r.headers.get_content_charset() or "utf-8", "replace"), r.geturl(), time.time() - t
    except urllib.error.HTTPError as e:
        return e.code, e.read(limite).decode("utf-8", "replace"), url, time.time() - t
    except Exception as e:  # noqa: BLE001 - sem rede, DNS, tempo esgotado
        return None, f"sem resposta ({type(e).__name__})", url, time.time() - t


def segredos():
    s = {}
    if PASTA_SEGREDOS.is_dir():
        for f in sorted(PASTA_SEGREDOS.glob("*.env")):
            for linha in f.read_text().splitlines():
                k, sep, v = linha.strip().partition("=")
                if sep and not k.startswith("#"):
                    s[k.replace("export ", "").strip()] = v.strip().strip("'\"")
    return s


def trocar(texto, seg):
    """Troca $NOME pelo segredo. Variável de ambiente vale mais que o arquivo. Falta = KeyError com o nome."""
    def um(m):
        v = os.environ.get(m[1], seg.get(m[1]))
        if not v:
            raise KeyError(m[1])
        return v
    return re.sub(r"\$\{?([A-Z][A-Z0-9_]*)\}?", um, str(texto))


class Leitor(HTMLParser):
    """Links/botões com o texto deles, scripts, metas, texto visível."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links, self.scripts, self.meta, self.texto = [], [], {}, []
        self._botao, self._oculto = None, 0

    def handle_starttag(self, tag, attrs):
        a = {k: v or "" for k, v in attrs}
        if tag in ("a", "button"):
            self._botao = [a.get("href") or a.get("formaction") or "", [a.get("aria-label", "")]]
        elif tag == "input" and a.get("type") in ("submit", "button"):
            self.links.append((a.get("value", ""), ""))
        elif tag == "script" and a.get("src"):
            self.scripts.append(a["src"])
        elif tag == "meta" and (a.get("property") or a.get("name")):
            self.meta[(a.get("property") or a.get("name")).lower()] = a.get("content", "")
        if tag in ("script", "style", "noscript", "template"):
            self._oculto += 1

    def handle_endtag(self, tag):
        if tag in ("a", "button") and self._botao:
            self.links.append((" ".join(" ".join(self._botao[1]).split()), self._botao[0]))
            self._botao = None
        if tag in ("script", "style", "noscript", "template") and self._oculto:
            self._oculto -= 1

    def handle_data(self, d):
        if self._oculto:
            return
        self.texto.append(d)
        if self._botao:
            self._botao[1].append(d)


def scripts_do_site(srcs, base):
    """Conteúdo dos scripts do mesmo domínio (o pixel costuma estar num rastreio.js, não no HTML)."""
    host = urllib.parse.urlparse(base).netloc
    partes = []
    for s in srcs[:10]:
        u = urllib.parse.urljoin(base, s)
        if urllib.parse.urlparse(u).netloc == host:
            st, corpo, _, _ = pegar(u, limite=1_500_000)
            if st == 200:
                partes.append(corpo)
    return "\n".join(partes)


# ---------- checagens ----------

def conferir_pagina(p, prefixo=""):
    nome = prefixo + p.get("nome", p["url"])
    id_ = "pagina:" + nome
    st, corpo, final, dt = pegar(p["url"])
    if st != 200:
        return [check(id_, nome, False, f"fora do ar ({'HTTP ' + str(st) if st else corpo})", itens=[p["url"]])]
    probs = []
    if dt > p.get("lenta_s", 10):
        probs.append(f"demorou {dt:.0f} s para abrir")
    ler = Leitor()
    ler.feed(corpo)
    txt, bruto = norm(" ".join(ler.texto)), norm(corpo)
    for t in p.get("precisa_ter", []):
        if norm(t) not in txt and norm(t) not in bruto:
            probs.append(f'sem o texto "{t}"')
    for t in p.get("nao_pode_ter", []):
        if norm(t) in bruto or norm(t) in txt:
            probs.append(f'tem "{t}", que não devia estar ali')
    if p.get("preco") and not re.search(r"r\$ ?" + re.escape(norm(p["preco"])) + r"(?![0-9])", txt + " " + bruto):
        probs.append(f"sem o preço R$ {p['preco']}")
    for b in p.get("botoes", []):
        hrefs = [h for t, h in ler.links if norm(b["texto"]) in norm(t)]
        if not hrefs:
            probs.append(f'sem o botão "{b["texto"]}"')
        elif b.get("link_contem") and not any(b["link_contem"] in h for h in hrefs):
            probs.append(f'o botão "{b["texto"]}" não leva a {b["link_contem"]} (leva a {hrefs[0] or "lugar nenhum"})')
    if p.get("pixels"):
        fontes = corpo + scripts_do_site(ler.scripts, final)
        for qual, valor in p["pixels"].items():
            if str(valor) not in fontes:
                probs.append(f"pixel {qual} ({valor}) não está na página nem nos scripts dela")
    if p.get("previa"):
        img = ler.meta.get("og:image", "")
        # rede social só lê endereço completo; https quando a página é https (http só no teste local)
        if not (img.startswith("https://") or (img.startswith("http://") and final.startswith("http://"))):
            probs.append("sem imagem de compartilhamento (og:image com endereço completo)")
        elif pegar(img, limite=1)[0] != 200:
            probs.append("a imagem de compartilhamento não abre")
        if not ler.meta.get("og:title"):
            probs.append("sem título de compartilhamento (og:title)")
    out = [check(id_, nome, not probs, " · ".join(probs) or f"no ar ({dt:.1f} s), tudo o que o comprador precisa ver está lá", itens=probs)]
    px = p.get("proxima")
    if px:
        alvo = [h for t, h in ler.links if norm(px["botao"]) in norm(t) and h and not h.startswith(("#", "javascript:"))]
        if not alvo:
            out.append(check(id_ + ":proxima", nome + " > tela seguinte", False, f'não achei o link do botão "{px["botao"]}" para seguir'))
        else:
            seguinte = {**px, "url": urllib.parse.urljoin(final, alvo[0]), "nome": px.get("nome", f'tela depois de "{px["botao"]}"')}
            out += conferir_pagina(seguinte, prefixo=nome + " > ")
    return out


def conferir_funcoes(fs, seg):
    """Pedido vazio deve ser recusado (4xx), nunca quebrar (5xx): prova que a função está publicada e sobe."""
    ruins = []
    for f in fs:
        try:
            url, cab = trocar(f["url"], seg), {k: trocar(v, seg) for k, v in f.get("cabecalhos", {}).items()}
        except KeyError as e:
            ruins.append(f'{f["nome"]}: falta o segredo {e.args[0]}')
            continue
        metodo = f.get("metodo", "POST")
        st, _, _, _ = pegar(url, metodo, f.get("corpo", "{}") if metodo != "GET" else None, cab)
        bom = st == f["status"] if f.get("status") else (st is not None and st < 500)
        if not bom:
            ruins.append(f'{f["nome"]} ({"HTTP " + str(st) if st else "sem resposta"})')
    return [check("funcoes", "Funções do servidor respondendo", not ruins,
                  f"fora do ar: {', '.join(ruins)}" if ruins else f"{len(fs)} função(ões) respondendo", itens=ruins)]


def limpar(c):
    itens = c.get("itens") if isinstance(c.get("itens"), list) else []
    return check(str(c.get("id", "servidor"))[:60], str(c.get("nome", "Servidor"))[:120], c.get("ok"), str(c.get("detalhe", ""))[:500],
                 int(c.get("corrigidos") or 0), [str(i)[:200] for i in itens])


def conferir_servidor(s, seg):
    """Rotina do servidor que corrige sozinha. Responde {"checks": [...]} ou {"corrigidos": n, "falhas": n, "detalhe": "..."}."""
    nome, id_ = s.get("nome", "Servidor"), "servidor:" + s.get("nome", "servidor")
    try:
        url, cab = trocar(s["url"], seg), {k: trocar(v, seg) for k, v in s.get("cabecalhos", {}).items()}
    except KeyError as e:
        return [check(id_, nome, False, f"falta o segredo {e.args[0]}: salve em {PASTA_SEGREDOS}/ (veja SKILL.md)")]
    st, corpo, _, _ = pegar(url, "POST", json.dumps(s.get("corpo", {})), cab, tempo=s.get("tempo_s", 90))
    if st is None or st >= 300:
        return [check(id_, nome, False, f"respondeu {'HTTP ' + str(st) if st else corpo}")]
    try:
        j = json.loads(corpo)
    except ValueError:
        j = {}
    if not isinstance(j, dict):
        j = {}
    if isinstance(j.get("checks"), list):
        return [limpar(c) for c in j["checks"][:50] if isinstance(c, dict)]
    return [check(id_, nome, not j.get("falhas"), str(j.get("detalhe") or f"rodou (HTTP {st})")[:500], int(j.get("corrigidos") or 0))]


def seguro(nome, f, *args):
    """Uma checagem que quebra vira problema e não impede as outras."""
    try:
        return f(*args)
    except Exception as e:  # noqa: BLE001
        return [check("erro:" + nome, nome, False, f"a conferência falhou: {type(e).__name__}: {str(e)[:200]}")]


def auditar(cfg, seg):
    checks = []
    # a ordem importa: primeiro as rotinas que corrigem, depois o que o comprador vê
    for s in cfg.get("servidor", []):
        checks += seguro(s.get("nome", "Servidor"), conferir_servidor, s, seg)
    for p in cfg.get("paginas", []):
        checks += seguro(p.get("nome", p.get("url", "página")), conferir_pagina, p)
    if cfg.get("funcoes"):
        checks += seguro("Funções do servidor", conferir_funcoes, cfg["funcoes"], seg)
    return checks


# ---------- resultado ----------

def resumo(nome, checks, painel=""):
    """Texto do aviso. Vazio quando tudo certo e nada foi corrigido (silêncio)."""
    ruins = [c for c in checks if not c["ok"]]
    feitos = [c for c in checks if c["ok"] and c.get("corrigidos")]
    if not ruins and not feitos:
        return ""
    linhas = [f"Auditoria do funil: {nome}"]
    linhas += [f"PROBLEMA - {c['nome']}: {c['detalhe']}" for c in ruins]
    linhas += [f"CORRIGIDO - {c['nome']}: {c['detalhe']}" for c in feitos]
    return "\n".join(linhas) + (f"\nDetalhes: {painel}" if painel else "")


def telegram(seg, texto):
    """None = enviado. Nunca mostra a URL: ela leva o token."""
    tok = os.environ.get("TELEGRAM_BOT_TOKEN", seg.get("TELEGRAM_BOT_TOKEN"))
    chat = os.environ.get("TELEGRAM_CHAT_ID", seg.get("TELEGRAM_CHAT_ID"))
    if not tok or not chat:
        return "Telegram não configurado (falta TELEGRAM_BOT_TOKEN ou TELEGRAM_CHAT_ID)"
    dados = {"chat_id": chat, "text": texto[:4000], "disable_web_page_preview": True}
    topico = os.environ.get("TELEGRAM_THREAD_ID", seg.get("TELEGRAM_THREAD_ID"))
    if topico:
        dados["message_thread_id"] = int(topico)
    st, _, _, _ = pegar(f"{TELEGRAM_API}/bot{tok}/sendMessage", "POST", json.dumps(dados))
    return None if st == 200 else f"o Telegram recusou ({'HTTP ' + str(st) if st else 'sem resposta'})"


def pagina_saude(nome, rodada, historico):
    agora = datetime.fromisoformat(rodada["rodado_em"]).timestamp()
    dia = [h for h in historico if agora - datetime.fromisoformat(h["rodado_em"]).timestamp() < 86400]
    e = html.escape

    def item(c):
        estado = "ok" if c["ok"] else "problema"
        feito = f" · <i>{c['corrigidos']} corrigido(s)</i>" if c.get("corrigidos") else ""
        lista = "<small>" + "<br>".join(e(i) for i in c["itens"]) + "</small>" if c.get("itens") and not c["ok"] else ""
        return f'<li class="{"ok" if c["ok"] else "erro"}"><b>{estado}</b> {e(c["nome"])}{feito}<small>{e(c["detalhe"])}</small>{lista}</li>'

    linhas = "".join(item(c) for c in sorted(rodada["checks"], key=lambda c: c["ok"]))
    return f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Saúde do funil</title><style>
:root{{--bg:#fff;--tx:#14181c;--mu:#5b6670;--ok:#127a3a;--er:#b42318;--ln:#e3e7eb}}
@media (prefers-color-scheme:dark){{:root{{--bg:#0f1317;--tx:#eef2f5;--mu:#a3aeb8;--ok:#4ade80;--er:#f87171;--ln:#26303a}}}}
body{{background:var(--bg);color:var(--tx);font:16px/1.5 system-ui,sans-serif;margin:0 auto;max-width:860px;padding:16px}}
.kpis{{display:flex;gap:12px;flex-wrap:wrap}}.kpis div{{border:1px solid var(--ln);border-radius:10px;padding:10px 14px;min-width:150px}}
.kpis b{{display:block;font-size:28px}}ul{{list-style:none;padding:0}}li{{border-bottom:1px solid var(--ln);padding:10px 0}}
li b{{display:inline-block;min-width:80px}}.ok b{{color:var(--ok)}}.erro b{{color:var(--er)}}small{{display:block;color:var(--mu)}}
#atraso{{color:var(--er);font-weight:600}}</style></head><body>
<h1>Saúde do funil: {e(nome)}</h1>
<p>Conferido em <span id="em" data-em="{e(rodada["rodado_em"])}">{e(rodada["rodado_em"][:16].replace("T", " "))} UTC</span> <span id="atraso"></span></p>
<div class="kpis"><div><b>{rodada["problemas"]}</b>problema(s) agora</div><div><b>{sum(h["corrigidos"] for h in dia)}</b>corrigido(s) sozinho em 24 h</div><div><b>{len(dia)}</b>conferência(s) em 24 h</div></div>
<ul>{linhas}</ul>
<script>/* auditor do auditor: sem rodada há mais de 2,5 h, avisa */
const em=Date.parse(document.getElementById('em').dataset.em);if(Date.now()-em>2.5*3600e3)document.getElementById('atraso').textContent='· atrasado: devia rodar a cada 2 h';</script>
</body></html>"""


def salvar(pasta, nome, checks):
    pasta.mkdir(parents=True, exist_ok=True)
    rodada = {"rodado_em": datetime.now(timezone.utc).isoformat(timespec="seconds"), "problemas": sum(not c["ok"] for c in checks),
              "corrigidos": sum(c.get("corrigidos") or 0 for c in checks), "checks": checks}
    hist_f = pasta / "historico.jsonl"
    linhas = hist_f.read_text().splitlines() if hist_f.exists() else []
    linhas = (linhas + [json.dumps(rodada, ensure_ascii=False)])[-HISTORICO_MAX:]
    hist_f.write_text("\n".join(linhas) + "\n")
    (pasta / "ultimo.json").write_text(json.dumps(rodada, ensure_ascii=False, indent=1))
    historico = [json.loads(x) for x in linhas]
    (pasta / "index.html").write_text(pagina_saude(nome, rodada, historico))
    return rodada


def carregar(caminho):
    cfg = json.loads(Path(caminho).read_text())
    for p in cfg.get("paginas", []):
        if "url" not in p:
            raise ValueError(f"página sem url: {p}")
    return cfg


def main(argv):
    if argv[:1] == ["--autoteste"]:
        return autoteste()
    if not argv or argv[0].startswith("-"):
        print(__doc__)
        return 2
    try:
        cfg = carregar(argv[0])
    except (OSError, ValueError) as e:
        print(f"funil.json com problema: {e}")
        return 2
    seg, nome = segredos(), cfg.get("nome", "meu funil")
    if "--testar-telegram" in argv:
        erro = telegram(seg, f"Auditor do funil ligado: {nome}. Os avisos vão chegar aqui.")
        print(erro or "mensagem de teste enviada")
        return 1 if erro else 0
    checks = auditar(cfg, seg)
    ensaio = "--teste" in argv
    pasta = Path(argv[0]).resolve().parent / cfg.get("pasta_saida", "saude")
    rodada = salvar(pasta, nome, checks)
    for c in checks:
        print(f"[{'ok' if c['ok'] else 'PROBLEMA'}] {c['nome']}: {c['detalhe']}" + (f" ({c['corrigidos']} corrigido(s))" if c.get("corrigidos") else ""))
    print(f"\n{rodada['problemas']} problema(s), {rodada['corrigidos']} corrigido(s). Painel: {pasta / 'index.html'}")
    aviso = resumo(nome, checks, cfg.get("painel_url", ""))
    if aviso and not ensaio:
        erro = telegram(seg, aviso)
        if erro:
            print(f"Aviso não enviado: {erro}")
    elif aviso:
        print("\n(ensaio: este aviso iria para o Telegram)\n" + aviso)
    return 1 if rodada["problemas"] else 0


# ---------- autoteste (servidor local de mentira, sem internet) ----------

def autoteste():
    import tempfile
    import threading
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
    global TELEGRAM_API, PASTA_SEGREDOS
    recebidos, paginas = [], {}
    srv = ThreadingHTTPServer(("127.0.0.1", 0), None)  # o manipulador entra abaixo; as páginas precisam do endereço
    b = f"http://127.0.0.1:{srv.server_address[1]}"
    paginas.update({
        "/venda.html": f'<html><head><meta property="og:image" content="{b}/capa.jpg"><meta property="og:title" content="Curso X">'
                       '<script src="/js/rastreio.js"></script></head><body><h1>Curso X</h1><p>Por R$&nbsp;97,00</p>'
                       '<a class="cta" href="/pagar.html?p=1">Comprar <b>agora</b></a><script>var t="R$ 10,00"</script></body></html>',
        "/js/rastreio.js": "fbq('init','111222333');gtag('config','G-TESTE123');",
        "/capa.jpg": "jpg",
        "/pagar.html": "<html><body><p>Autor: Fulano de Tal</p><p>Curso X</p><p>R$ 97,00</p></body></html>",
        "/quebrada.html": '<html><head><script src="https://outro.site/widget.min.js"></script></head><body><p>R$ 197,00</p>'
                          '<a href="https://golpe.site/x">Comprar</a><script>/* Comprar agora */</script></body></html>',
    })

    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def responder(self, st, corpo, tipo="text/html; charset=utf-8"):
            b = corpo.encode()
            self.send_response(st)
            self.send_header("Content-Type", tipo)
            self.send_header("Content-Length", str(len(b)))
            self.end_headers()
            self.wfile.write(b)

        def do_GET(self):
            c = paginas.get(self.path.split("?")[0])
            self.responder(200 if c else 404, c or "não achei")

        def do_POST(self):
            corpo = self.rfile.read(int(self.headers.get("Content-Length") or 0)).decode()
            if self.path.endswith("/sendMessage"):
                recebidos.append(json.loads(corpo))
                return self.responder(200, '{"ok":true}', "application/json")
            if self.path == "/servidor":
                if self.headers.get("Authorization") != "Bearer segredo-local":
                    return self.responder(401, "{}", "application/json")
                return self.responder(200, json.dumps({"checks": [
                    {"id": "acesso", "nome": "Comprador recebeu o acesso", "ok": True, "detalhe": "2 reenviado(s)", "corrigidos": 2},
                    {"id": "email", "nome": "E-mails <b>em dia</b>", "ok": False, "detalhe": "1 atrasado <script>x</script>", "itens": ["a@b.c"]}]}),
                    "application/json")
            if self.path == "/rotina":
                return self.responder(200, '{"corrigidos": 3, "falhas": 0, "detalhe": "3 e-mails enviados"}', "application/json")
            self.responder({"/api": 400, "/api500": 500}.get(self.path, 404), "{}", "application/json")

    srv.RequestHandlerClass = H
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    TELEGRAM_API = b
    with tempfile.TemporaryDirectory() as tmp:
        PASTA_SEGREDOS = Path(tmp) / "env"
        PASTA_SEGREDOS.mkdir()
        (PASTA_SEGREDOS / "telegram.env").write_text("TELEGRAM_BOT_TOKEN=tok-falso\nTELEGRAM_CHAT_ID=42\n")
        (PASTA_SEGREDOS / "servidor.env").write_text("export AUDITOR_TOKEN='segredo-local'\n")
        seg = segredos()
        assert seg == {"TELEGRAM_BOT_TOKEN": "tok-falso", "TELEGRAM_CHAT_ID": "42", "AUDITOR_TOKEN": "segredo-local"}, seg

        boa = {"nome": "Venda", "url": b + "/venda.html", "precisa_ter": ["Curso X"], "nao_pode_ter": ["widget.min.js"], "preco": "97,00",
               "botoes": [{"texto": "Comprar agora", "link_contem": "/pagar.html"}], "pixels": {"Meta": "111222333", "GA4": "G-TESTE123"},
               "previa": True,
               "proxima": {"botao": "Comprar agora", "nome": "Checkout", "precisa_ter": ["Autor: Fulano de Tal", "Curso X"], "preco": "97,00"}}
        r = conferir_pagina(boa)
        assert [c["ok"] for c in r] == [True, True], r
        assert r[1]["nome"] == "Venda > Checkout", r[1]

        ruim = {"nome": "Quebrada", "url": b + "/quebrada.html", "nao_pode_ter": ["widget.min.js"], "preco": "97,00",
                "botoes": [{"texto": "Comprar agora"}, {"texto": "Comprar", "link_contem": "/pagar.html"}],
                "pixels": {"Meta": "111222333"}, "previa": True, "proxima": {"botao": "Comprar agora"}}
        r = conferir_pagina(ruim)
        itens = r[0]["itens"]
        assert not r[0]["ok"] and not r[1]["ok"], r
        for esperado in ('tem "widget.min.js"', "sem o preço R$ 97,00", 'sem o botão "Comprar agora"', "não leva a /pagar.html",
                         "pixel Meta (111222333)", "og:image", "og:title"):
            assert any(esperado in i for i in itens), (esperado, itens)
        assert len(itens) == 7, itens  # "Comprar agora" dentro de <script> não conta como botão
        assert not conferir_pagina({"url": b + "/sumiu.html"})[0]["ok"]
        assert not conferir_pagina({"url": "http://127.0.0.1:9/x", "nome": "Sem rede"})[0]["ok"]

        f = conferir_funcoes([{"nome": "pagar", "url": b + "/api"}, {"nome": "quebrada", "url": b + "/api500"},
                              {"nome": "sem segredo", "url": b + "/api", "cabecalhos": {"X": "$NAO_EXISTE"}}], seg)[0]
        assert not f["ok"] and f["itens"] == ["quebrada (HTTP 500)", "sem segredo: falta o segredo NAO_EXISTE"], f

        cfg = {"nome": "Teste", "painel_url": "https://exemplo.com/saude/",
               "servidor": [{"nome": "Rotina", "url": b + "/rotina"},
                            {"nome": "Auditor do servidor", "url": b + "/servidor", "cabecalhos": {"Authorization": "Bearer $AUDITOR_TOKEN"}},
                            {"nome": "Sem token", "url": b + "/servidor"}],
               "paginas": [boa], "funcoes": [{"nome": "pagar", "url": b + "/api"}]}
        checks = auditar(cfg, seg)
        nomes = [c["nome"] for c in checks]
        assert nomes[:4] == ["Rotina", "Comprador recebeu o acesso", "E-mails <b>em dia</b>", "Sem token"], nomes
        assert checks[0]["corrigidos"] == 3 and checks[1]["corrigidos"] == 2 and not checks[3]["ok"], checks
        texto = resumo("Teste", checks, cfg["painel_url"])
        assert "PROBLEMA - Sem token" in texto and "CORRIGIDO - Rotina" in texto and "Detalhes: https://exemplo.com/saude/" in texto, texto
        assert resumo("x", [check("a", "A", True, "ok")]) == ""
        assert telegram(seg, texto) is None and recebidos[-1]["chat_id"] == "42" and "PROBLEMA" in recebidos[-1]["text"]
        assert "tok-falso" not in json.dumps(recebidos)

        cfg_f = Path(tmp) / "funil.json"
        cfg_f.write_text(json.dumps(cfg))
        assert main([str(cfg_f), "--teste"]) == 1 and len(recebidos) == 1  # ensaio não manda Telegram
        assert main([str(cfg_f)]) == 1 and len(recebidos) == 2
        pag = (Path(tmp) / "saude" / "index.html").read_text()
        assert "&lt;script&gt;x&lt;/script&gt;" in pag and "<script>x</script>" not in pag and "E-mails &lt;b&gt;" in pag
        assert len((Path(tmp) / "saude" / "historico.jsonl").read_text().splitlines()) == 2
        assert main([str(Path(tmp) / "nao-existe.json")]) == 2
    srv.shutdown()
    print("autoteste: ok (páginas, tela seguinte, pixels, prévia, funções, servidor, segredos, Telegram, painel)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
