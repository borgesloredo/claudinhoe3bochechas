#!/usr/bin/env python3
"""Base orgânica: junta seguidores e contatos de todas as redes num banco SQLite único, une a mesma pessoa
entre redes (telefone, e-mail ou @) e dá uma nota de aquecimento + nicho para fazer o ranking.

Só biblioteca padrão do Python 3.9+. Os dados ficam no seu computador (LGPD: uso próprio, sem vender, com descadastro).
Texto de mensagem nunca é gravado: de conversa fica só que ela existiu, quantas mensagens do nicho e quais termos.

Uso:
  base_organica.py iniciar                              cria nicho.json (palavras do nicho) e o banco
  base_organica.py importar ARQUIVO... [--rede R] [--eu "Seu Nome"] [--como-leads]
        aceita: .zip ou .json do "Baixar seus dados" (Instagram, Facebook, TikTok), .csv (qualquer rede),
                .vcf (contatos), .txt (conversa exportada do WhatsApp)
  base_organica.py whatsapp-backup [PASTA]              lê o WhatsApp do backup local do iPhone (sem criptografia)
  base_organica.py ranking [--top 30] [--csv saida.csv] [--todos]
  base_organica.py painel [saida.html | saida.json]     aba "Orgânico" num arquivo HTML local (ou JSON p/ seu painel)
  base_organica.py pessoal CHAVE [MOTIVO | --tirar]     CHAVE = rede:handle (ex.: instagram:fulano)
  base_organica.py cliente CHAVE PRODUTO | interesse CHAVE PRODUTO | separar CHAVE   (PRODUTO "-" desfaz)
  base_organica.py descadastrar EMAIL|TELEFONE|rede:handle
  base_organica.py --teste                              autoteste com dados falsos
Opções gerais: --db ARQ (padrão ./base-organica.sqlite)  --nicho ARQ (padrão ./nicho.json)
"""
import argparse
import csv
import hashlib
import html
import io
import json
import os
import plistlib
import quopri
import re
import sqlite3
import sys
import unicodedata
import zipfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

REDES = ("instagram", "facebook", "tiktok", "youtube", "kwai", "pinterest", "whatsapp")
SO_NOME = ("facebook",)  # exportação traz só o nome: handle = nome em minúsculas com hífen
TIPOS = ("comentario", "curtida", "dm", "mencao", "compartilhou", "salvou")
URL = {"instagram": "https://www.instagram.com/{}/", "tiktok": "https://www.tiktok.com/@{}",
       "youtube": "https://www.youtube.com/@{}", "kwai": "https://www.kwai.com/@{}",
       "pinterest": "https://www.pinterest.com/{}/", "whatsapp": "https://wa.me/{}"}
# pontos por tipo de interação e quantas contam no máximo
PESO = {"comentario": (6, 10), "curtida": (1, 30), "dm": (15, 3), "mencao": (8, 5), "compartilhou": (8, 5), "salvou": (4, 5)}
NIVEIS = ((60, "fervendo"), (35, "quente"), (15, "morno"), (-10 ** 9, "frio"))
NICHO_PADRAO = {
    "nicho": "exemplo: áudio ao vivo (troque pelas palavras do seu nicho)",
    "fortes": ["mesa de som", "mesa digital", "tecnico de som", "operador de som", "mixag*", "equaliz*", "microfonia",
               "sonoplast*", "line array", "in ear", "som da igreja"],
    "fracas": ["som", "audio", "mesa", "microfone", "banda", "igreja", "culto", "show", "evento", "curso", "aula*"],
    "excluir_conversas": [],
    "pessoal_palavras": [],
    "meu_nome_no_whatsapp": [],
    "voce_segue_e_pessoal": False,
    "ddi_padrao": "55",
}
SCHEMA = """
create table if not exists perfis(rede text, handle text, nome text, bio text, email text, email_origem text,
  telefone text, telefone_origem text, segue_voce int default 0, voce_segue int default 0, nicho text, fonte text,
  primeiro_visto text, ultimo_visto text, deixou_em text, primary key(rede, handle));
create table if not exists interacoes(rede text, handle text, tipo text, ref text, quando text, qtd int default 1,
  termos text, primary key(rede, tipo, ref, handle));
create table if not exists agenda(nome_norm text, nome text, telefone text, email text, primary key(nome_norm, telefone));
create table if not exists ajustes(chave text primary key, pessoal text, cliente text, interesse text, separar int default 0);
create table if not exists descadastro(hash text primary key, quando text);
"""


def agora():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def norm(s):
    return unicodedata.normalize("NFD", str(s or "").lower()).encode("ascii", "ignore").decode()


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", norm(s)).strip("-")[:64] or None


def limpar_handle(v):
    """@fulano, fulano ou o link do perfil -> fulano; None se não parece um @."""
    h = norm(v).strip()
    h = re.sub(r"[?#].*$", "", h).rstrip("/").split("/")[-1].lstrip("@")
    return h if re.fullmatch(r"[a-z0-9._-]{1,64}", h) else None


def limpar_email(v):
    e = str(v or "").strip().lower()
    return e if re.fullmatch(r"[^@\s:;,]+@[^@\s:;,]+\.[a-z]{2,}", e) else None


def limpar_tel(v, ddi="55"):
    """Só dígitos, com DDI. Número de 10-11 dígitos sem + é do país padrão (ddi_padrao)."""
    s = str(v or "").replace("‪", "").replace("‬", "").strip()
    d = re.sub(r"\D", "", s)
    if 10 <= len(d) <= 11 and not s.startswith("+"):
        d = ddi + d
    return d if 11 <= len(d) <= 15 else None


def contato_da_bio(bio, ddi):
    b = str(bio or "")
    m = re.search(r"[\w.+-]+@[\w-]+(\.[\w-]+)+", b)
    t = re.search(r"(\+\d{1,3}[\s.-]?)?\(?\d{2}\)?[\s.-]?9?\d{4}[\s.-]?\d{4}", b)
    return (limpar_email(m.group(0)) if m else None), (limpar_tel(t.group(0), ddi) if t else None)


def hsh(v):
    return hashlib.sha256(str(v).encode()).hexdigest()


# ---------- configuração do nicho ----------

def compilar(termos):
    """'mesa de som' casa a expressão inteira; 'mixag*' casa mixagem, mixagens...; sem acento e sem maiúscula."""
    out = []
    for t in termos:
        t = norm(t).strip()
        if t:
            p = re.escape(t.rstrip("*")).replace(r"\ ", " ").replace(" ", r"\s+")
            out.append(re.compile(r"\b" + p + (r"\w*" if t.endswith("*") else r"\b")))
    return out


def carregar_nicho(caminho):
    cfg = dict(NICHO_PADRAO)
    p = Path(caminho)
    if p.is_file():
        cfg.update(json.loads(p.read_text(encoding="utf-8")))
    cfg["_fortes"], cfg["_fracas"] = compilar(cfg["fortes"]), compilar(cfg["fracas"])
    cfg["_excluir"] = compilar(cfg["excluir_conversas"])
    cfg["_pessoal"] = compilar(cfg["pessoal_palavras"])
    cfg["_eu"] = {norm(n).strip() for n in cfg["meu_nome_no_whatsapp"]}
    return cfg


def achados(texto, regs):
    t = norm(texto)
    return sorted({m.group(0) for r in regs for m in [r.search(t)] if m})


def do_nicho(texto, cfg):
    """(fortes, fracas, é do nicho?) — do nicho = 1 termo forte ou 2 fracos."""
    f, w = achados(texto, cfg["_fortes"]), achados(texto, cfg["_fracas"])
    return f, w, bool(f or len(w) >= 2)


# ---------- banco ----------

def abrir(caminho):
    novo = not Path(caminho).exists()
    con = sqlite3.connect(caminho)
    con.row_factory = sqlite3.Row
    con.executescript(SCHEMA)
    if novo:
        os.chmod(caminho, 0o600)  # dado pessoal: só o dono do computador lê
    return con


def bloqueado(con, *vals):
    return any(con.execute("select 1 from descadastro where hash=?", (hsh(v),)).fetchone() for v in vals if v)


def gravar(con, lote, cfg):
    """Grava um lote {rede, fonte, completo, perfis, interacoes}. completo = lista inteira de seguidores:
    quem seguia e não veio ganha deixou_em."""
    rede, t, ddi = lote["rede"], agora(), cfg["ddi_padrao"]
    vistos, bloq, n_p, n_i = set(), set(), 0, 0
    for p in lote["perfis"]:
        hd = p["handle"]
        email, tel = limpar_email(p.get("email")), limpar_tel(p.get("telefone"), ddi)
        eo = p.get("email_origem") or (f"perfil:{rede}" if email else None)
        to = p.get("telefone_origem") or (f"perfil:{rede}" if tel else None)
        be, bt = contato_da_bio(p.get("bio"), ddi)
        if not email and be:
            email, eo = be, f"bio:{rede}"
        if not tel and bt:
            tel, to = bt, f"bio:{rede}"
        if tel and not email:  # e-mail que a própria pessoa deu na agenda (.vcf) com o mesmo telefone
            r = con.execute("select email from agenda where telefone=? and email is not null", (tel,)).fetchone()
            if r:
                email, eo = r[0], "agenda"
        # só pelo nome (Facebook, conversa sem número): o nome também é checado no bloqueio de quem pediu para sair
        nome_b = "nome:" + " ".join(norm(p.get("nome")).split()) if p.get("nome") and (rede in SO_NOME or not tel) else None
        if bloqueado(con, f"{rede}:{hd}", email, tel, nome_b):
            bloq.add(hd)
            continue
        f, w, _ = do_nicho(" ".join(filter(None, [p.get("nome"), p.get("bio")])), cfg)
        segue = 1 if p.get("segue_voce") else 0
        if segue:
            vistos.add(hd)
        con.execute(
            """insert into perfis(rede,handle,nome,bio,email,email_origem,telefone,telefone_origem,segue_voce,voce_segue,
                 nicho,fonte,primeiro_visto,ultimo_visto) values(?,?,?,?,?,?,?,?,?,?,?,?,?,?)
               on conflict(rede,handle) do update set nome=coalesce(excluded.nome,nome), bio=coalesce(excluded.bio,bio),
                 email=coalesce(email,excluded.email), email_origem=coalesce(email_origem,excluded.email_origem),
                 telefone=coalesce(telefone,excluded.telefone), telefone_origem=coalesce(telefone_origem,excluded.telefone_origem),
                 segue_voce=max(segue_voce,excluded.segue_voce), voce_segue=max(voce_segue,excluded.voce_segue),
                 nicho=coalesce(excluded.nicho,nicho), fonte=excluded.fonte, ultimo_visto=excluded.ultimo_visto,
                 deixou_em=case when excluded.segue_voce=1 then null else deixou_em end""",
            (rede, hd, p.get("nome"), p.get("bio"), email, eo, tel, to, segue, 1 if p.get("voce_segue") else 0,
             json.dumps({"f": f, "w": w}) if (f or w) else None, lote.get("fonte", "exportacao"), t, t))
        n_p += 1
    if lote.get("completo"):
        con.execute("create temp table if not exists _vistos(h text primary key)")
        con.execute("delete from _vistos")
        con.executemany("insert or ignore into _vistos values(?)", [(x,) for x in vistos])
        con.execute("""update perfis set deixou_em=? where rede=? and segue_voce=1 and deixou_em is null
                       and handle not in (select h from _vistos)""", (t, rede))
    for i in lote["interacoes"]:
        if i["tipo"] not in TIPOS or i["handle"] in bloq or bloqueado(con, f"{rede}:{i['handle']}"):
            continue
        con.execute("insert or ignore into perfis(rede,handle,fonte,primeiro_visto,ultimo_visto) values(?,?,?,?,?)",
                    (rede, i["handle"], lote.get("fonte", "exportacao"), t, t))
        con.execute("insert or replace into interacoes values(?,?,?,?,?,?,?)",
                    (rede, i["handle"], i["tipo"], str(i["ref"]), i.get("quando"), int(i.get("qtd") or 1), i.get("termos")))
        n_i += 1
    con.commit()
    return n_p, n_i


def lote(rede, perfis, interacoes=(), completo=False, lista=None, fonte="exportacao"):
    return {"rede": rede, "fonte": fonte, "completo": completo, "lista": lista, "perfis": list(perfis),
            "interacoes": list(interacoes)}


# ---------- leitores das exportações ----------

def achar(d, chave):
    """Todas as listas guardadas sob `chave` em qualquer nível do JSON."""
    if isinstance(d, dict):
        for k, v in d.items():
            if k == chave and isinstance(v, list):
                yield v
            else:
                yield from achar(v, chave)
    elif isinstance(d, list):
        for v in d:
            yield from achar(v, chave)


def ler_json(nome, dados):
    """Exportações oficiais em JSON. Devolve lista de lotes (vazia se o arquivo não é de seguidores/amigos)."""
    base = Path(nome).name.lower()
    # Instagram: followers_N.json (lista ou {relationships_followers}) e following.json ({relationships_following})
    ig = dados if isinstance(dados, list) else next((v for k, v in dados.items() if k.startswith("relationships_")), None) \
        if isinstance(dados, dict) else None
    if isinstance(ig, list) and ig and isinstance(ig[0], dict) and "string_list_data" in ig[0]:
        def handle(it):
            d = (it.get("string_list_data") or [{}])[0]
            return limpar_handle(d.get("value") or it.get("title") or d.get("href"))
        hs = sorted({h for h in map(handle, ig) if h})
        if base.startswith("following"):
            return [lote("instagram", [{"handle": h, "voce_segue": True} for h in hs], lista="seguindo")]
        if base.startswith("followers"):
            return [lote("instagram", [{"handle": h, "segue_voce": True} for h in hs], completo=True, lista="seguidores")]
        return []
    # TikTok: user_data*.json, listas FansList (seguidores) e Following, itens {Date, UserName}
    fans = [it for l in achar(dados, "FansList") for it in l]
    seguindo = [it for l in achar(dados, "Following") for it in l if isinstance(it, dict) and "UserName" in it]
    if fans or seguindo:
        u = lambda it: limpar_handle(it.get("UserName") or it.get("Username"))
        out = []
        if fans:
            out.append(lote("tiktok", [{"handle": h, "segue_voce": True} for h in sorted({u(i) for i in fans} - {None})],
                            completo=True, lista="seguidores"))
        if seguindo:
            out.append(lote("tiktok", [{"handle": h, "voce_segue": True} for h in sorted({u(i) for i in seguindo} - {None})],
                            lista="seguindo"))
        return out
    # Facebook: amigos/seguidores do perfil, itens {name, timestamp} (só nome; Página não exporta seguidores)
    if isinstance(dados, dict):
        for k, v in dados.items():
            if isinstance(v, list) and v and isinstance(v[0], dict) and "name" in v[0] and re.search(r"friend|follow", k):
                ps = [{"handle": slug(it["name"]), "nome": it["name"], "segue_voce": True} for it in v if slug(it.get("name"))]
                return [lote("facebook", ps, lista=k)]
    return []


def campo(linha):
    """Linha de vCard -> (nome do campo, valor decodificado)."""
    k, v = linha.split(":", 1)
    partes = k.split(";")
    if any("QUOTED-PRINTABLE" in p.upper() for p in partes):
        v = quopri.decodestring(v.encode()).decode("utf-8", "replace")
    return partes[0].split(".")[-1].upper(), v.replace("\\n", " ").replace("\\,", ",").strip()


def ler_vcf(texto):
    texto = re.sub(r"=\r?\n", "", texto)  # quebra de linha do quoted-printable
    texto = re.sub(r"\r?\n[ \t]", "", texto)  # linha dobrada do vCard
    for bloco in re.findall(r"BEGIN:VCARD(.*?)END:VCARD", texto, re.S | re.I):
        c = {"nome": None, "tels": [], "emails": [], "extra": []}
        for linha in bloco.splitlines():
            if ":" not in linha:
                continue
            k, v = campo(linha)
            if k == "FN":
                c["nome"] = v
            elif k == "TEL":
                c["tels"].append(v)
            elif k == "EMAIL":
                c["emails"].append(v)
            elif k in ("ORG", "NOTE", "TITLE"):
                c["extra"].append(v.replace(";", " "))
        yield c


def importar_vcf(con, texto, cfg, como_leads):
    perfis, n = [], 0
    for c in ler_vcf(texto):
        tels = [t for t in (limpar_tel(x, cfg["ddi_padrao"]) for x in c["tels"]) if t]
        email = next((e for e in map(limpar_email, c["emails"]) if e), None)
        if bloqueado(con, email, *tels):
            continue
        n += 1
        for t in tels or [None]:
            if c["nome"] and (t or email):
                con.execute("insert or ignore into agenda values(?,?,?,?)", (norm(c["nome"]).strip(), c["nome"], t, email))
        if como_leads and tels:
            perfis.append({"handle": tels[0], "nome": c["nome"], "telefone": tels[0], "email": email,
                           "telefone_origem": "agenda", "email_origem": "agenda" if email else None,
                           "bio": " ".join(c["extra"]) or None})
    con.commit()
    print(f"  agenda: {n} contatos (servem para achar o telefone de quem aparece só pelo nome)")
    return [lote("whatsapp", perfis, fonte="manual")] if perfis else []


RE_MSG = [re.compile(r"^\[(\d{1,2}/\d{1,2}/\d{2,4}),? (\d{1,2}:\d{2}(?::\d{2})?)\] ([^:]{1,80}): (.*)$"),  # iPhone
          re.compile(r"^(\d{1,2}/\d{1,2}/\d{2,4}),? (\d{1,2}:\d{2}(?::\d{2})?) - ([^:]{1,80}): (.*)$")]  # Android


def data_iso(d, h):
    dia, mes, ano = (int(x) for x in d.split("/"))
    ano += 2000 if ano < 100 else 0
    return f"{ano:04d}-{mes:02d}-{dia:02d}T{h if h.count(':') == 2 else h + ':00'}"


def tel_ou_nome(con, autor, ddi):
    """Autor de mensagem -> (handle, telefone): número escrito, ou nome achado 1 vez só na agenda (.vcf), ou o nome."""
    if re.fullmatch(r"[+\d\s().-]{8,}", autor):
        t = limpar_tel(autor, ddi)
        if t:
            return t, t
    ts = {r[0] for r in con.execute("select telefone from agenda where nome_norm=? and telefone is not null",
                                    (norm(autor).strip(),))}
    if len(ts) == 1:
        t = ts.pop()
        return t, t
    return slug(autor), None


def importar_chat(con, nome, texto, cfg, eu):
    """Conversa exportada do WhatsApp (.txt). Só vira lead quem escreveu sobre o nicho. Texto não é gravado."""
    msgs = []
    for linha in texto.splitlines():
        linha = re.sub("[‎‏‪‬]", "", linha).replace(" ", " ").replace(" ", " ")
        for r in RE_MSG:
            m = r.match(linha)
            if m:
                msgs.append(list(m.groups()))
                break
        else:
            if msgs:
                msgs[-1][3] += " " + linha
    if not msgs:
        return None
    eus = set(cfg["_eu"]) | ({norm(eu).strip()} if eu else set())
    autores = {m[2].strip() for m in msgs}
    dica = re.search(r"(?:conversa do whatsapp com|whatsapp chat (?:with|-)) (.+?)(?:\.txt|\.zip)?$", Path(nome).name, re.I)
    if not eus & {norm(a).strip() for a in autores} and dica and len(autores) == 2 and dica.group(1).strip() in autores:
        eus = {norm(a).strip() for a in autores if a != dica.group(1).strip()}  # 1:1: eu sou o outro autor
    outros = {a for a in autores if norm(a).strip() not in eus}
    if not eus & {norm(a).strip() for a in autores}:
        print(f"  aviso: {Path(nome).name}: não sei qual autor é você; use --eu \"Seu nome no WhatsApp\" "
              "ou preencha meu_nome_no_whatsapp no nicho.json", file=sys.stderr)
    grupo = len(outros) > 1
    pessoas = {}
    for i, (d, h, autor, txt) in enumerate(msgs):
        autor = autor.strip()
        if autor not in outros:
            continue
        f, w, ok = do_nicho(txt, cfg)
        if not ok:
            continue
        hd, tel = tel_ou_nome(con, autor, cfg["ddi_padrao"])
        if not hd:
            continue
        p = pessoas.setdefault(hd, {"nome": None if re.fullmatch(r"[+\d\s().-]{8,}", autor) else autor, "tel": tel, "q": [], "termos": set()})
        p["q"].append((data_iso(d, h), hsh(f"{nome}|{d}|{h}|{autor}|{i}")[:16]))
        p["termos"].update(f or w)
    perfis, inter = [], []
    for hd, p in pessoas.items():
        perfis.append({"handle": hd, "nome": p["nome"], "telefone": p["tel"], "telefone_origem": "whatsapp"})
        termos = ",".join(sorted(p["termos"]))
        if grupo:
            inter += [{"handle": hd, "tipo": "comentario", "ref": f"wa:{r}", "quando": q, "termos": termos} for q, r in p["q"]]
        else:
            inter.append({"handle": hd, "tipo": "dm", "ref": f"wa-dm:{hd}", "qtd": len(p["q"]),
                          "quando": max(q for q, _ in p["q"]), "termos": termos})
    return [lote("whatsapp", perfis, inter)]


COLS = {"handle": ("handle", "usuario", "username", "user", "perfil", "@", "arroba", "conta", "link"),
        "nome": ("nome", "name", "nome completo", "full name"), "email": ("email", "e-mail"),
        "telefone": ("telefone", "phone", "celular", "whatsapp", "fone"), "bio": ("bio", "descricao", "sobre"),
        "rede": ("rede", "network", "plataforma"), "tipo": ("tipo", "interacao"), "ref": ("ref", "post", "id"),
        "quando": ("quando", "data", "date"), "qtd": ("qtd", "quantidade"), "segue": ("segue", "segue_voce")}


def importar_csv(texto, rede_padrao, cfg):
    """CSV de qualquer rede (seguidores, inscritos, comentários...). Coluna `tipo` preenchida = interação."""
    try:
        dial = csv.Sniffer().sniff(texto[:4096], delimiters=",;\t")
    except csv.Error:
        dial = csv.excel
    linhas = list(csv.DictReader(io.StringIO(texto), dialect=dial))
    if not linhas:
        return []
    mapa = {}
    for k in linhas[0]:
        nk = norm(k).strip()
        for alvo, nomes in COLS.items():
            if nk in nomes and alvo not in mapa:
                mapa[alvo] = k
    g = lambda r, c: (r.get(mapa[c]) or "").strip() if c in mapa else ""
    lotes = {}
    for r in linhas:
        rede = norm(g(r, "rede")) or rede_padrao
        if rede not in REDES:
            raise SystemExit(f"CSV sem rede válida (coluna 'rede' ou --rede {'|'.join(REDES)}): {rede or 'vazia'}")
        tel = limpar_tel(g(r, "telefone"), cfg["ddi_padrao"])
        hd = (tel if rede == "whatsapp" else None) or (None if rede in SO_NOME else limpar_handle(g(r, "handle"))) \
            or slug(g(r, "nome"))
        if not hd:
            continue
        l = lotes.setdefault(rede, lote(rede, [], fonte="manual"))
        tipo = norm(g(r, "tipo"))
        if tipo:
            l["interacoes"].append({"handle": hd, "tipo": tipo, "ref": g(r, "ref") or hsh(json.dumps(r, sort_keys=True))[:16],
                                    "quando": g(r, "quando") or None, "qtd": int(g(r, "qtd") or 1)})
        segue = norm(g(r, "segue")) not in ("0", "nao", "false", "n") if "segue" in mapa else rede != "whatsapp"
        if not tipo or g(r, "nome") or tel:
            l["perfis"].append({"handle": hd, "nome": g(r, "nome") or None, "email": g(r, "email") or None,
                                "telefone": tel, "bio": g(r, "bio") or None, "segue_voce": segue and not tipo})
    return list(lotes.values())


def lotes_de_arquivo(con, nome, dados, args, cfg):
    """nome + bytes -> lotes. Zip é lido em memória, sem extrair nada no disco."""
    ext = Path(nome).suffix.lower()
    if ext == ".zip":
        out = []
        with zipfile.ZipFile(io.BytesIO(dados)) as z:
            for m in z.namelist():
                base = Path(m).name.lower()
                if base.endswith((".json", ".csv", ".vcf")) or base == "_chat.txt" or (base.endswith(".txt") and "whatsapp" in base):
                    sub = Path(nome).stem + ".txt" if base == "_chat.txt" else m  # o nome do zip diz com quem é a conversa
                    out += lotes_de_arquivo(con, sub, z.read(m), args, cfg) or []
        return out
    texto = dados.decode("utf-8-sig", "replace")
    if ext == ".json":
        try:
            return ler_json(nome, json.loads(texto))
        except json.JSONDecodeError:
            return []
    if ext == ".vcf":
        return importar_vcf(con, texto, cfg, args.como_leads)
    if ext == ".csv":
        return importar_csv(texto, args.rede, cfg)
    if ext == ".txt":
        return importar_chat(con, nome, texto, cfg, args.eu) or []
    raise SystemExit(f"Formato não reconhecido: {nome}")


def juntar(lotes):
    """Seguidores de uma rede vindos em vários arquivos (followers_1, followers_2...) viram uma lista completa só."""
    out, comp = [], {}
    for l in lotes:
        if l.get("lista") == "seguidores" and l["completo"]:
            if l["rede"] in comp:
                comp[l["rede"]]["perfis"] += l["perfis"]
                continue
            comp[l["rede"]] = l
        out.append(l)
    return out


def cmd_importar(con, args, cfg):
    lotes = []
    for a in args.arquivos:
        p = Path(a).expanduser()
        if not p.is_file():
            raise SystemExit(f"Arquivo não existe: {p}")
        novos = lotes_de_arquivo(con, p.name, p.read_bytes(), args, cfg)
        if not novos and p.suffix.lower() not in (".vcf",):
            print(f"  {p.name}: nada de seguidores/contatos reconhecido")
        lotes += novos
    for l in juntar(lotes):
        n_p, n_i = gravar(con, l, cfg)
        print(f"  {l['rede']}: {n_p} perfis, {n_i} interações" + (" (lista completa)" if l["completo"] else ""))


# ---------- WhatsApp pelo backup do iPhone ----------

BACKUPS = Path.home() / "Library/Application Support/MobileSync/Backup"


def ro(p):
    return sqlite3.connect(f"file:{p}?mode=ro&immutable=1", uri=True)


def bancos_whatsapp(caminho):
    """[(app, ChatStorage, ContactsV2 ou None)] de um backup do iPhone (pasta com Manifest.db) ou de uma pasta
    que já tem ChatStorage.sqlite. Sem caminho: o backup mais recente do Mac."""
    p = Path(caminho).expanduser() if caminho else None
    if p and (p / "ChatStorage.sqlite").is_file():
        c = p / "ContactsV2.sqlite"
        return [("WhatsApp", p / "ChatStorage.sqlite", c if c.is_file() else None)]
    try:
        if not p:
            bks = sorted((d for d in BACKUPS.iterdir() if (d / "Manifest.db").is_file()),
                         key=lambda d: (d / "Manifest.db").stat().st_mtime)
            if not bks:
                raise SystemExit("Nenhum backup do iPhone neste Mac. Finder > iPhone > 'Fazer backup de todos os dados "
                                 "do iPhone neste Mac' (sem criptografar) > Fazer backup agora.")
            p = bks[-1]
        man = plistlib.loads((p / "Manifest.plist").read_bytes())
    except PermissionError:
        raise SystemExit("Sem permissão para ler o backup: Ajustes do Sistema > Privacidade e Segurança > "
                         "Acesso Total ao Disco > ligue o app que roda este comando (Terminal) e abra-o de novo.")
    if man.get("IsEncrypted"):
        raise SystemExit("Backup criptografado: desmarque 'Criptografar backup local' no Finder e faça outro backup.")
    m = ro(p / "Manifest.db")

    def arq(app, nome):
        r = m.execute("select fileID from Files where domain=? and relativePath=?",
                      (f"AppDomainGroup-group.net.whatsapp.{app}.shared", nome)).fetchone()
        return p / r[0][:2] / r[0] if r else None
    return [(app, arq(app, "ChatStorage.sqlite"), arq(app, "ContactsV2.sqlite"))
            for app in ("WhatsApp", "WhatsAppSMB") if arq(app, "ChatStorage.sqlite")]


def ler_backup_whatsapp(app, chat, contatos, cfg):
    ddi = cfg["ddi_padrao"]
    lid_tel, nomes = {}, {}
    if contatos:
        k = ro(contatos)
        try:
            rows = k.execute("select ZLID, ZWHATSAPPID, ZPHONENUMBER, coalesce(ZFULLNAME, ZBUSINESSNAME) from ZWAADDRESSBOOKCONTACT")
        except sqlite3.OperationalError:  # versão antiga do app, sem @lid
            rows = ((None, w, t, n) for w, t, n in k.execute(
                "select ZWHATSAPPID, ZPHONENUMBER, coalesce(ZFULLNAME, ZBUSINESSNAME) from ZWAADDRESSBOOKCONTACT"))
        for lid, waid, tel, nome in rows:
            t = limpar_tel("+" + waid.split("@")[0]) if waid and waid.endswith("@s.whatsapp.net") else limpar_tel(tel, ddi)
            if lid and t:
                lid_tel[lid] = t
            if t and nome:
                nomes.setdefault(t, nome)

    def telefone(jid):
        if not jid:
            return None
        if jid.endswith("@s.whatsapp.net"):
            return limpar_tel("+" + jid.split("@")[0])
        return lid_tel.get(jid) if jid.endswith("@lid") else None  # grupo, status, canal: não é pessoa

    db = ro(chat)
    # conversas de trabalho/família (excluir_conversas) ficam de fora: pelo nome ou citadas em >= 2% das mensagens
    excl = {pk for pk, n in db.execute("select Z_PK, ZPARTNERNAME from ZWACHATSESSION") if achados(n or "", cfg["_excluir"])}
    if cfg["_excluir"]:
        tot, cit = {}, {}
        for s, txt in db.execute("select ZCHATSESSION, ZTEXT from ZWAMESSAGE where ZTEXT is not null"):
            tot[s] = tot.get(s, 0) + 1
            cit[s] = cit.get(s, 0) + (1 if achados(txt, cfg["_excluir"]) else 0)
        excl |= {s for s in tot if cit[s] * 50 >= tot[s] and cit[s]}
    q = """select m.ZTEXT, m.ZMESSAGEDATE, m.ZISFROMME, s.Z_PK, s.ZCONTACTJID, s.ZPARTNERNAME, s.ZSESSIONTYPE,
                  coalesce(g.ZMEMBERJID, m.ZFROMJID), g.ZCONTACTNAME, m.Z_PK
           from ZWAMESSAGE m join ZWACHATSESSION s on s.Z_PK = m.ZCHATSESSION
           left join ZWAGROUPMEMBER g on g.Z_PK = m.ZGROUPMEMBER
           where m.ZTEXT is not null and length(m.ZTEXT) > 2"""
    pessoas = {}
    for txt, data, eu, sess, cjid, cnome, tipo, autor, gnome, pk in db.execute(q):
        if sess in excl or eu:
            continue  # só conta o que a pessoa escreveu
        grupo = tipo == 1 or (cjid or "").endswith("@g.us")
        if not grupo and tipo not in (0, None):
            continue  # status, transmissão, canal
        f, w, ok = do_nicho(txt, cfg)
        if not ok:
            continue
        tel = telefone(autor if grupo else cjid)
        if not tel:
            continue
        quando = datetime.fromtimestamp((data or 0) + 978307200, timezone.utc).isoformat(timespec="seconds")  # 2001-01-01
        p = pessoas.setdefault(tel, {"nome": None, "dm": [], "com": [], "termos": set()})
        p["nome"] = p["nome"] or nomes.get(tel) or (None if grupo else cnome) or gnome
        p["termos"].update(f or w)
        (p["com"] if grupo else p["dm"]).append((quando, f"wa{app[-3:].lower()}{pk}"))
    perfis, inter = [], []
    for tel, p in pessoas.items():
        termos = ",".join(sorted(p["termos"]))
        perfis.append({"handle": tel, "nome": p["nome"], "telefone": tel, "telefone_origem": "whatsapp"})
        if p["dm"]:
            inter.append({"handle": tel, "tipo": "dm", "ref": f"wa-dm:{tel}", "qtd": len(p["dm"]),
                          "quando": max(q for q, _ in p["dm"]), "termos": termos})
        inter += [{"handle": tel, "tipo": "comentario", "ref": r, "quando": q, "termos": termos} for q, r in p["com"]]
    return lote("whatsapp", perfis, inter)


def cmd_whatsapp_backup(con, args, cfg):
    bancos = bancos_whatsapp(args.pasta)
    if not bancos:
        raise SystemExit("Backup sem WhatsApp (o app não estava no iPhone ou o backup é parcial).")
    for app, chat, contatos in bancos:
        n_p, n_i = gravar(con, ler_backup_whatsapp(app, chat, contatos, cfg), cfg)
        print(f"  {app}: {n_p} pessoas falaram do nicho, {n_i} interações (texto das mensagens não foi gravado)")


# ---------- união e nota ----------

def jaro_winkler(a, b):
    if a == b:
        return 1.0
    la, lb = len(a), len(b)
    if not la or not lb:
        return 0.0
    dist = max(la, lb) // 2 - 1
    ma, mb = [False] * la, [False] * lb
    m = 0
    for i, c in enumerate(a):
        for j in range(max(0, i - dist), min(lb, i + dist + 1)):
            if not mb[j] and b[j] == c:
                ma[i] = mb[j] = True
                m += 1
                break
    if not m:
        return 0.0
    t, k = 0, 0
    for i in range(la):
        if ma[i]:
            while not mb[k]:
                k += 1
            t += a[i] != b[k]
            k += 1
    j = (m / la + m / lb + (m - t / 2) / m) / 3
    p = 0
    while p < min(4, la, lb) and a[p] == b[p]:
        p += 1
    return j + p * 0.1 * (1 - j)


def calcular(con, cfg):
    perfis = {f"{r['rede']}:{r['handle']}": dict(r) for r in con.execute("select * from perfis")}
    aj = {r["chave"]: dict(r) for r in con.execute("select * from ajustes")}
    inter = {}
    for r in con.execute("""select rede, handle, tipo, sum(qtd) q, max(quando) u, group_concat(termos) t
                            from interacoes group by 1,2,3"""):
        inter.setdefault(f"{r['rede']}:{r['handle']}", []).append(dict(r))
    pai = {c: c for c in perfis}
    redes = {c: {p["rede"]} for c, p in perfis.items()}
    liga = {}

    def raiz(c):
        while pai[c] != c:
            pai[c] = pai[pai[c]]
            c = pai[c]
        return c

    def unir(a, b, tipo):
        if (aj.get(a) or {}).get("separar") or (aj.get(b) or {}).get("separar"):
            return
        ra, rb = raiz(a), raiz(b)
        if ra == rb or redes[ra] & redes[rb]:
            return  # nunca junta dois perfis da mesma rede
        pai[rb] = ra
        redes[ra] |= redes[rb]
        for c in (a, b):
            if liga.get(c) != "certa":
                liga[c] = tipo
    # certa: mesmo @ (sem . _ -), mesmo e-mail, mesmo telefone (últimos 11 dígitos)
    idx = {}
    for c, p in perfis.items():
        if p["rede"] not in SO_NOME and p["rede"] != "whatsapp" and len(p["handle"]) >= 3:
            idx.setdefault("h:" + re.sub(r"[._-]", "", p["handle"]), []).append(c)
        if p["email"]:
            idx.setdefault("e:" + p["email"], []).append(c)
        if p["telefone"]:
            idx.setdefault("t:" + p["telefone"][-11:], []).append(c)
    for cs in idx.values():
        for c in cs[1:]:
            unir(cs[0], c, "certa")
    # provável: @ muito parecido (Jaro-Winkler >= 0,93, 5+ letras, mesmo começo) e nome parecido se os dois têm nome;
    # ou mesmo nome completo (2+ palavras)
    por_ini, por_nome = {}, {}
    for c, p in perfis.items():
        hn = re.sub(r"[._-]", "", p["handle"])
        if p["rede"] not in SO_NOME and p["rede"] != "whatsapp" and len(hn) >= 5:
            por_ini.setdefault(hn[:3], []).append((c, hn))
        nn = " ".join(norm(p["nome"]).split())
        if nn.count(" ") >= 1:
            por_nome.setdefault(nn, []).append(c)
    for grupo in por_ini.values():
        for i, (a, ha) in enumerate(grupo):
            for b, hb in grupo[i + 1:]:
                na, nb = norm(perfis[a]["nome"]), norm(perfis[b]["nome"])
                if jaro_winkler(ha, hb) >= 0.93 and (not na or not nb or jaro_winkler(na, nb) >= 0.85):
                    unir(a, b, "provavel")
    for cs in por_nome.values():
        for c in cs[1:]:
            unir(cs[0], c, "provavel")
    grupos = {}
    for c in perfis:
        grupos.setdefault(raiz(c), []).append(c)

    corte = (datetime.now(timezone.utc) - timedelta(days=30)).date().isoformat()
    leads, pessoal = [], []
    for membros in grupos.values():
        membros.sort()
        ps = [perfis[c] for c in membros]
        pts, mot = 0, []
        segue = sorted({p["rede"] for p in ps if p["segue_voce"] and not p["deixou_em"]})
        if segue:
            pts += 10 * len(segue) + 10 * (len(segue) - 1)
            mot.append(f"segue em {len(segue)} rede(s)")
        soma, ultima, termos = {}, None, set()
        for c in membros:
            for r in inter.get(c, []):
                soma[r["tipo"]] = soma.get(r["tipo"], 0) + r["q"]
                ultima = max(filter(None, [ultima, r["u"]]), default=None)
                termos |= set(filter(None, (r["t"] or "").split(",")))
        for tipo, q in soma.items():
            peso, teto = PESO[tipo]
            pts += peso * min(q, teto)
            mot.append(f"{q} {tipo}" + ("s" if q > 1 and not tipo.endswith("u") else ""))
        if ultima and ultima[:10] >= corte:
            pts += 10
            mot.append("interagiu nos últimos 30 dias")
        email = next((p["email"] for p in ps if p["email"]), None)
        tel = next((p["telefone"] for p in ps if p["telefone"]), None)
        if email or tel:
            pts += 5
            mot.append("tem contato")
        f = sorted({t for p in ps if p["nicho"] for t in json.loads(p["nicho"])["f"]})
        w = sorted({t for p in ps if p["nicho"] for t in json.loads(p["nicho"])["w"]})
        if f or termos:
            pts += 15
            mot.append("fala do nicho: " + ", ".join(sorted(set(f) | termos)[:3]))
        elif len(w) >= 2:
            pts += 8
            mot.append("perfil perto do nicho: " + ", ".join(w[:3]))
        deixou = sorted({p["rede"] for p in ps if p["deixou_em"]})
        if deixou:
            pts -= 10 * len(deixou)
            mot.append("deixou de seguir: " + ", ".join(deixou))
        cliente = next((aj[c]["cliente"] for c in membros if (aj.get(c) or {}).get("cliente")), None)
        interesse = next((aj[c]["interesse"] for c in membros if (aj.get(c) or {}).get("interesse")), None)
        if interesse and not cliente:
            pts += 40
            mot.append(f"interessado em {interesse}")
        nivel = "cliente" if cliente else next(n for lim, n in NIVEIS if pts >= lim)
        if cliente:
            mot.insert(0, f"cliente {cliente}")
        motivo_pessoal = None
        for c, p in zip(membros, ps):
            m = (aj.get(c) or {}).get("pessoal")
            if m == "-":
                continue  # devolvido ao ranking à mão: vence as regras
            if m:
                motivo_pessoal = m
            elif achados(f"{p['nome'] or ''} {p['handle']}", cfg["_pessoal"]):
                motivo_pessoal = "palavra pessoal"
            elif cfg["voce_segue_e_pessoal"] and p["voce_segue"]:
                motivo_pessoal = "você segue"
        lead = {"id": membros[0], "nome": next((p["nome"] for p in ps if p["nome"]), None),
                "perfis": [{"chave": c, "rede": p["rede"], "handle": p["handle"],
                            "url": URL[p["rede"]].format(p["handle"]) if p["rede"] in URL else None,
                            "segue": bool(p["segue_voce"] and not p["deixou_em"]), "uniao": liga.get(c)}
                           for c, p in zip(membros, ps)],
                "email": email, "telefone": tel, "interacoes": soma, "ultima_interacao": ultima,
                "pontos": pts, "nivel": nivel, "motivos": mot, "pessoal": motivo_pessoal}
        (pessoal if motivo_pessoal else leads).append(lead)
    leads.sort(key=lambda l: (-l["pontos"], l["id"]))
    por_nivel, por_redes = {}, {}
    for l in leads:
        por_nivel[l["nivel"]] = por_nivel.get(l["nivel"], 0) + 1
        k = str(len({p["rede"] for p in l["perfis"]}))
        por_redes[k] = por_redes.get(k, 0) + 1
    fontes = {r["rede"]: {"perfis": r["n"], "ultima": r["u"]} for r in
              con.execute("select rede, count(*) n, max(ultimo_visto) u from perfis group by rede")}
    return {"gerado_em": agora(), "fontes": fontes,
            "resumo": {"leads": len(leads), "por_nivel": por_nivel, "por_redes": por_redes,
                       "com_email": sum(1 for l in leads if l["email"]), "com_telefone": sum(1 for l in leads if l["telefone"]),
                       "pessoal": len(pessoal)},
            "leads": leads, "pessoal": pessoal}


# ---------- saídas ----------

def cmd_ranking(con, args, cfg):
    res = calcular(con, cfg)
    leads = res["leads"] if args.todos else [l for l in res["leads"] if l["nivel"] != "frio"]
    r = res["resumo"]
    print(f"{r['leads']} leads | " + " · ".join(f"{k} {v}" for k, v in sorted(r["por_nivel"].items())) +
          f" | com e-mail {r['com_email']} · com telefone {r['com_telefone']} | pessoal (escondido) {r['pessoal']}")
    print(f"{'#':>3}  {'nível':9} {'pts':>4}  {'nome':24} {'redes':34} contato  motivos")
    for i, l in enumerate(leads[:args.top], 1):
        redes = " ".join(f"{p['rede'][:2]}:{p['handle']}" for p in l["perfis"])
        contato = ("e" if l["email"] else "-") + ("t" if l["telefone"] else "-")  # o contato em si fica no CSV/painel
        print(f"{i:>3}  {l['nivel']:9} {l['pontos']:>4}  {(l['nome'] or '')[:24]:24} {redes[:34]:34} {contato:7}  "
              + "; ".join(l["motivos"]))
    if args.csv:
        with open(args.csv, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["posicao", "nivel", "pontos", "nome", "perfis", "email", "telefone", "motivos"])
            for i, l in enumerate(res["leads"], 1):
                w.writerow([i, l["nivel"], l["pontos"], l["nome"] or "", " ".join(p["url"] or p["chave"] for p in l["perfis"]),
                            l["email"] or "", l["telefone"] or "", "; ".join(l["motivos"])])
        os.chmod(args.csv, 0o600)
        print(f"CSV: {args.csv} (dado pessoal: não compartilhe)")


PAINEL = """<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Orgânico</title><style>
:root{--bg:#f7f7f5;--card:#fff;--tx:#1d1d1b;--mu:#6b6b66;--li:#e4e4df;--fe:#c2410c;--qu:#d97706;--mo:#2563eb;--fr:#64748b;--cl:#15803d}
@media (prefers-color-scheme:dark){:root{--bg:#141413;--card:#1f1f1d;--tx:#ecece8;--mu:#a1a19a;--li:#33332f}}
body{margin:0;background:var(--bg);color:var(--tx);font:14px/1.45 system-ui,-apple-system,sans-serif}
main{max-width:1180px;margin:auto;padding:16px}h1{font-size:22px;margin:4px 0 2px}.mu{color:var(--mu)}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:8px;margin:14px 0}
.card{background:var(--card);border:1px solid var(--li);border-radius:10px;padding:10px}.card b{display:block;font-size:22px}
.bar{display:flex;flex-wrap:wrap;gap:6px;align-items:center;margin:10px 0}
button,input{font:inherit;border:1px solid var(--li);background:var(--card);color:var(--tx);border-radius:8px;padding:6px 10px}
button.on{border-color:var(--tx);font-weight:600}input{flex:1;min-width:180px}
.tw{overflow-x:auto;background:var(--card);border:1px solid var(--li);border-radius:10px}
table{border-collapse:collapse;width:100%}th,td{text-align:left;padding:7px 9px;border-bottom:1px solid var(--li);vertical-align:top}
th{font-size:12px;color:var(--mu);font-weight:600}.n{font-weight:700;text-transform:uppercase;font-size:11px}
.fervendo{color:var(--fe)}.quente{color:var(--qu)}.morno{color:var(--mo)}.frio{color:var(--fr)}.cliente{color:var(--cl)}
a{color:inherit}small{color:var(--mu)}footer{margin:18px 0;color:var(--mu);font-size:12px}
</style></head><body><main>
<h1>Orgânico</h1><div class="mu" id="ger"></div>
<div class="cards" id="cards"></div>
<div class="bar" id="niveis"></div>
<div class="bar"><input id="busca" placeholder="Buscar nome, @, motivo" aria-label="Buscar"><button id="pes">Mostrar grupo Pessoal</button></div>
<div class="tw"><table><thead><tr><th>#</th><th>Nível</th><th>Pts</th><th>Pessoa</th><th>Redes</th><th>Contato</th><th>Por quê</th></tr></thead>
<tbody id="tb"></tbody></table></div>
<footer>Arquivo com dados pessoais (LGPD): só para uso próprio. Não publique, não envie, não venda. Quem pedir para sair:
<code>base_organica.py descadastrar &lt;contato&gt;</code> e gere o painel de novo.</footer>
</main><script>
const D=__DADOS__;const esc=s=>String(s??"").replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"})[c]);
let nivel="",pes=false;const R=D.resumo;
document.getElementById("ger").textContent="Gerado em "+new Date(D.gerado_em).toLocaleString("pt-BR")+" · fontes: "+Object.entries(D.fontes).map(([k,v])=>k+" "+v.perfis).join(", ");
document.getElementById("cards").innerHTML=[["Leads",R.leads],["Fervendo",R.por_nivel.fervendo||0],["Quentes",R.por_nivel.quente||0],["Mornos",R.por_nivel.morno||0],["Clientes",R.por_nivel.cliente||0],["Com e-mail",R.com_email],["Com telefone",R.com_telefone],["Pessoal",R.pessoal]].map(([a,b])=>`<div class="card"><small>${a}</small><b>${b}</b></div>`).join("");
const nv=document.getElementById("niveis");["","fervendo","quente","morno","frio","cliente"].forEach(n=>{const b=document.createElement("button");b.textContent=n||"todos";b.onclick=()=>{nivel=n;[...nv.children].forEach(x=>x.classList.toggle("on",x===b));draw()};if(!n)b.classList.add("on");nv.appendChild(b)});
document.getElementById("busca").oninput=draw;document.getElementById("pes").onclick=e=>{pes=!pes;e.target.classList.toggle("on",pes);draw()};
function draw(){const q=document.getElementById("busca").value.toLowerCase();const L=pes?D.pessoal:D.leads;
document.getElementById("tb").innerHTML=L.filter(l=>(!nivel||l.nivel===nivel)&&(!q||JSON.stringify([l.nome,l.perfis.map(p=>p.handle),l.motivos]).toLowerCase().includes(q))).slice(0,2000).map((l,i)=>`<tr><td>${i+1}</td><td class="n ${l.nivel}">${l.nivel}</td><td>${l.pontos}</td><td>${esc(l.nome)}${l.pessoal?`<br><small>pessoal: ${esc(l.pessoal)}</small>`:""}</td><td>${l.perfis.map(p=>(p.url?`<a href="${esc(p.url)}" target="_blank" rel="noopener">${esc(p.rede)}: ${esc(p.handle)}</a>`:esc(p.rede+": "+p.handle))+(p.uniao==="provavel"?" <small>(provável)</small>":"")+(p.segue?"":" <small>(não segue)</small>")).join("<br>")}</td><td>${esc(l.email)}${l.email&&l.telefone?"<br>":""}${l.telefone?`<a href="https://wa.me/${esc(l.telefone)}" target="_blank" rel="noopener">${esc(l.telefone)}</a>`:""}</td><td><small>${esc(l.motivos.join("; "))}</small></td></tr>`).join("")}
draw();
</script></body></html>"""


def cmd_painel(con, args, cfg):
    res = calcular(con, cfg)
    saida = Path(args.saida)
    if saida.suffix.lower() == ".json":
        saida.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    else:
        dados = json.dumps(res, ensure_ascii=False).replace("</", "<\\/")
        saida.write_text(PAINEL.replace("__DADOS__", dados), encoding="utf-8")
    os.chmod(saida, 0o600)
    print(f"Painel: {saida} ({res['resumo']['leads']} leads). Abra o arquivo no navegador. Não publique: tem dado pessoal.")


def ajustar(con, chave, campo_, valor):
    if not re.fullmatch(r"[a-z]+:[^\s]+", chave or "") or chave.split(":")[0] not in REDES:
        raise SystemExit(f"CHAVE é rede:handle, ex.: instagram:fulano ({'|'.join(REDES)})")
    if not con.execute("select 1 from perfis where rede||':'||handle=?", (chave,)).fetchone():
        raise SystemExit(f"{chave} não está na base")
    con.execute("insert or ignore into ajustes(chave) values(?)", (chave,))
    con.execute(f"update ajustes set {campo_}=? where chave=?", (valor, chave))
    con.commit()
    print(f"ok: {chave} {campo_} = {valor}")


def cmd_descadastrar(con, args, cfg):
    v = args.valor.strip()
    email, tel = limpar_email(v), (None if ":" in v or "@" in v else limpar_tel(v, cfg["ddi_padrao"]))
    chave = v.lower() if re.fullmatch(r"[a-z]+:[^\s@]+", v.lower()) else None
    alvo = [l for l in (lambda r: r["leads"] + r["pessoal"])(calcular(con, cfg))
            if (email and l["email"] == email) or (tel and l["telefone"] and l["telefone"][-11:] == tel[-11:])
            or (chave and chave in {p["chave"] for p in l["perfis"]})]
    if not alvo:
        print("Ninguém na base com esse contato. Guardado no bloqueio mesmo assim (não entra em importação futura).")
    valores = {x for x in (email, tel, chave) if x}
    for l in alvo:
        for p in l["perfis"]:
            r = con.execute("select email, telefone, nome from perfis where rede=? and handle=?", (p["rede"], p["handle"])).fetchone()
            valores |= {x for x in (p["chave"], r["email"], r["telefone"]) if x}
            if r["nome"]:
                valores.add("nome:" + " ".join(norm(r["nome"]).split()))
            con.execute("delete from perfis where rede=? and handle=?", (p["rede"], p["handle"]))
            con.execute("delete from interacoes where rede=? and handle=?", (p["rede"], p["handle"]))
            con.execute("delete from ajustes where chave=?", (p["chave"],))
    for x in valores:
        con.execute("insert or ignore into descadastro values(?,?)", (hsh(x), agora()))
        con.execute("delete from agenda where email=? or telefone=? or 'nome:'||nome_norm=?", (x, x, x))
    con.commit()
    if alvo:
        print(f"Removido: {sum(len(l['perfis']) for l in alvo)} perfil(is). Só um código (hash) fica guardado para não "
              "importar de novo. Gere o painel/CSV de novo e apague cópias antigas.")


# ---------- autoteste (só dados falsos, criados aqui) ----------

def teste():
    import shutil
    import tempfile
    d = Path(tempfile.mkdtemp(prefix="base-organica-teste-"))
    try:
        _teste(d)
    finally:
        shutil.rmtree(d)
    print("teste ok")


def _teste(d):
    cfg_p = d / "nicho.json"
    cfg_p.write_text(json.dumps({**{k: v for k, v in NICHO_PADRAO.items()}, "pessoal_palavras": ["exemplosobrenome"],
                                 "meu_nome_no_whatsapp": ["Dono Teste"], "excluir_conversas": ["empresa x"]}))
    cfg = carregar_nicho(cfg_p)
    db = d / "base.sqlite"
    con = abrir(db)
    assert oct(db.stat().st_mode & 0o777) == "0o600"
    A = argparse.Namespace(rede=None, eu=None, como_leads=False)
    # funções puras
    assert limpar_handle("https://www.instagram.com/Ana.Teste/") == "ana.teste" and limpar_handle("@x y") is None
    assert limpar_tel("(11) 90000-0001") == "5511900000001" and limpar_tel("+1 202 555 0100") == "12025550100"
    assert limpar_tel("123") is None and limpar_email("A@B.com ") == "a@b.com" and limpar_email("x@y") is None
    assert contato_da_bio("Aulas de mesa de som | contato: ana@exemplo.com | (11) 90000-0002", "55") == \
        ("ana@exemplo.com", "5511900000002")
    assert do_nicho("Opero a MESA DE SOM da banda", cfg)[2] and do_nicho("fiz a mixagem", cfg)[0] == ["mixagem"]
    assert not do_nicho("me manda um áudio", cfg)[2] and do_nicho("som da banda no show", cfg)[2]
    assert jaro_winkler("martha", "marhta") > 0.96 and jaro_winkler("abc", "xyz") == 0
    # Instagram: zip com followers_1 + followers_2 (lista completa juntando os dois) + following
    seg = lambda hs: [{"title": "", "media_list_data": [], "string_list_data": [
        {"href": f"https://www.instagram.com/{h}", "value": h, "timestamp": 1763000000}]} for h in hs]
    z = io.BytesIO()
    with zipfile.ZipFile(z, "w") as zf:
        zf.writestr("connections/followers_and_following/followers_1.json", json.dumps(seg(["ana.teste", "bruno_exemplo"])))
        zf.writestr("connections/followers_and_following/followers_2.json", json.dumps(seg(["carla.ficticia", "dono.exemplosobrenome"])))
        zf.writestr("connections/followers_and_following/following.json",
                    json.dumps({"relationships_following": [{"title": "carla.ficticia", "string_list_data": [
                        {"href": "https://www.instagram.com/_u/carla.ficticia", "timestamp": 1763000000}]}]}))
        zf.writestr("your_instagram_activity/likes/liked_posts.json", json.dumps({"likes_media_likes": []}))
    (d / "instagram.zip").write_bytes(z.getvalue())
    # TikTok, Facebook, CSV do YouTube com interações, vCard, conversas do WhatsApp (iPhone e Android)
    (d / "user_data_tiktok.json").write_text(json.dumps({"Activity": {
        "Follower List": {"FansList": [{"Date": "2026-11-01 10:00:00", "UserName": "ana_teste"},
                                       {"Date": "2026-11-01", "UserName": "joao.teste"}]},
        "Following List": {"Following": [{"Date": "2026-11-01", "UserName": "bruno_exemplo"}]}}}))
    (d / "your_friends.json").write_text(json.dumps({"friends_v2": [{"name": "Eva Ficticia", "timestamp": 1}]}))
    (d / "inscritos.csv").write_text("usuario;nome;bio;tipo;ref;quando\n"
                                     "@joaoteste;João Teste;Técnico de som em eventos;;;\n"
                                     "@joaoteste;João Teste;;comentario;c1;2099-01-01\n"
                                     "@joaoteste;João Teste;;comentario;c2;2099-01-02\n", encoding="utf-8")
    (d / "contatos.vcf").write_text("BEGIN:VCARD\r\nVERSION:3.0\r\nFN:Eva Ficticia\r\nTEL;type=CELL:(11) 90000-0005\r\n"
                                    "EMAIL:eva@exemplo.com\r\nEND:VCARD\r\nBEGIN:VCARD\r\nVERSION:2.1\r\n"
                                    "FN;CHARSET=UTF-8;ENCODING=QUOTED-PRINTABLE:Jos=C3=A9 Ficticio\r\nTEL:+55 11 90000-0006\r\nEND:VCARD\r\n")
    (d / "Conversa do WhatsApp com Eva Ficticia.txt").write_text(
        "[01/11/2026, 10:00:00] Dono Teste: oi Eva\n[01/11/2026, 10:01:00] Eva Ficticia: minha mesa de som deu microfonia\n"
        "continuação da mensagem\n[01/11/2026, 10:02:00] Eva Ficticia: me manda um áudio\n", encoding="utf-8")
    (d / "WhatsApp Chat - Grupo.txt").write_text(
        "01/11/2026 10:00 - José Ficticio: alguém tem curso de mixagem?\n01/11/2026 10:01 - +55 11 90000-0007: o som da banda no show tava ruim\n"
        "01/11/2026 10:02 - Dono Teste: mesa de som em promoção\n01/11/2026 10:03 - +55 11 90000-0008: bom dia\n", encoding="utf-8")
    A.arquivos = [str(d / "contatos.vcf"), str(d / "instagram.zip"), str(d / "user_data_tiktok.json"),
                  str(d / "your_friends.json"), str(d / "Conversa do WhatsApp com Eva Ficticia.txt"),
                  str(d / "WhatsApp Chat - Grupo.txt")]
    cmd_importar(con, A, cfg)
    A.arquivos, A.rede = [str(d / "inscritos.csv")], "youtube"
    cmd_importar(con, A, cfg)
    # iPhone: banco falso no formato do WhatsApp
    w = d / "wa"
    w.mkdir()
    c = sqlite3.connect(w / "ChatStorage.sqlite")
    c.executescript("""create table ZWACHATSESSION(Z_PK, ZCONTACTJID, ZPARTNERNAME, ZSESSIONTYPE);
      create table ZWAGROUPMEMBER(Z_PK, ZMEMBERJID, ZCONTACTNAME);
      create table ZWAMESSAGE(Z_PK, ZTEXT, ZMESSAGEDATE, ZISFROMME, ZCHATSESSION, ZGROUPMEMBER, ZFROMJID);
      insert into ZWACHATSESSION values (1,'5511900000009@s.whatsapp.net','Lia Teste',0),(2,'g1@g.us','Técnicos',1),
        (3,'g2@g.us','Time Empresa X',1),(4,'5511900000010@s.whatsapp.net','Rui Teste',0);
      insert into ZWAGROUPMEMBER values (1,'901@lid',null),(2,'902@lid',null);
      insert into ZWAMESSAGE values (1,'qual mesa de som comprar?',800000000,0,1,null,null),
        (2,'regula a equalização',800000001,1,1,null,null),(3,'meu mixer deu microfonia',800000002,0,2,1,null),
        (4,'microfonia no line array',800000003,0,3,2,null),(5,'me manda um áudio',800000004,0,4,null,null);""")
    c.commit()
    k = sqlite3.connect(w / "ContactsV2.sqlite")
    k.executescript("""create table ZWAADDRESSBOOKCONTACT(ZLID, ZWHATSAPPID, ZPHONENUMBER, ZFULLNAME, ZBUSINESSNAME);
      insert into ZWAADDRESSBOOKCONTACT values ('901@lid','5511900000011@s.whatsapp.net','90000-0011','Caio Teste',null),
        ('902@lid',null,'(11) 90000-0012','Dani Teste',null);""")
    k.commit()
    cmd_whatsapp_backup(con, argparse.Namespace(pasta=str(w)), cfg)

    res = calcular(con, cfg)
    por = {p["chave"]: l for l in res["leads"] + res["pessoal"] for p in l["perfis"]}
    # união certa pelo @ (ana.teste / ana_teste) e pelo telefone (vCard + conversa); provável pelo nome (Facebook)
    assert por["instagram:ana.teste"] is por["tiktok:ana_teste"]
    assert por["whatsapp:5511900000005"] is por["facebook:eva-ficticia"], por["whatsapp:5511900000005"]
    assert {p["uniao"] for p in por["facebook:eva-ficticia"]["perfis"]} == {"provavel"}
    assert por["youtube:joaoteste"] is por["tiktok:joao.teste"]
    # nota: João segue em 2 redes (30) + 2 comentários (12) + recente (10) + bio do nicho (15) = 67 -> fervendo
    j = por["youtube:joaoteste"]
    assert j["pontos"] == 67 and j["nivel"] == "fervendo", j
    assert por["instagram:bruno_exemplo"]["nivel"] == "frio"  # só segue, sem nada do nicho
    # WhatsApp: só quem escreveu do nicho; autor por número; nome achado na agenda vira telefone; eu não conto
    assert "whatsapp:5511900000007" in por and "whatsapp:5511900000008" not in por
    assert "whatsapp:5511900000006" in por  # José Ficticio -> telefone pela agenda (.vcf)
    assert not any(k.startswith("whatsapp:dono") for k in por)
    assert "whatsapp:5511900000009" in por and "whatsapp:5511900000011" in por  # backup: 1:1 e grupo via @lid
    assert "whatsapp:5511900000012" not in por and "whatsapp:5511900000010" not in por  # empresa fora; "áudio" sozinho não
    # grupo Pessoal pela palavra do nicho.json; texto de mensagem nunca vai para o banco
    assert por["instagram:dono.exemplosobrenome"]["pessoal"] == "palavra pessoal"
    con.commit()
    bruto = db.read_bytes()
    for frase in (b"deu microfonia", b"me manda um", b"qual mesa de som comprar", b"regula a"):
        assert frase not in bruto, frase
    # ajustes
    ajustar(con, "instagram:bruno_exemplo", "interesse", "Curso A")
    ajustar(con, "instagram:carla.ficticia", "cliente", "Curso A")
    ajustar(con, "instagram:dono.exemplosobrenome", "pessoal", "-")
    res = calcular(con, cfg)
    por = {p["chave"]: l for l in res["leads"] + res["pessoal"] for p in l["perfis"]}
    assert por["instagram:bruno_exemplo"]["nivel"] == "quente" and por["instagram:carla.ficticia"]["nivel"] == "cliente"
    assert not por["instagram:dono.exemplosobrenome"]["pessoal"]
    # nova lista completa sem a Ana -> deixou de seguir no Instagram
    (d / "followers_1.json").write_text(json.dumps(seg(["bruno_exemplo", "carla.ficticia", "dono.exemplosobrenome"])))
    A.arquivos, A.rede = [str(d / "followers_1.json")], None
    cmd_importar(con, A, cfg)
    ana = {p["chave"]: l for l in calcular(con, cfg)["leads"] for p in l["perfis"]}["instagram:ana.teste"]
    assert any("deixou de seguir: instagram" in m for m in ana["motivos"]), ana
    # descadastro: some o grupo inteiro e não volta na reimportação
    cmd_descadastrar(con, argparse.Namespace(valor="eva@exemplo.com"), cfg)
    A.arquivos = [str(d / "your_friends.json"), str(d / "Conversa do WhatsApp com Eva Ficticia.txt"), str(d / "contatos.vcf")]
    cmd_importar(con, A, cfg)
    chaves = {p["chave"] for l in calcular(con, cfg)["leads"] for p in l["perfis"]}
    assert not [c for c in chaves if "eva" in c or c.endswith("0005")], chaves
    # painel e CSV
    cmd_painel(con, argparse.Namespace(saida=str(d / "painel.html")), cfg)
    h = (d / "painel.html").read_text()
    assert h.count("</script>") == 1 and "joaoteste" in h and oct((d / "painel.html").stat().st_mode & 0o777) == "0o600"
    cmd_ranking(con, argparse.Namespace(top=5, csv=str(d / "r.csv"), todos=False), cfg)
    r = (d / "r.csv").read_text()
    assert "5511900000007" in r and "+55 11" not in r and "Eva" not in r


# ---------- linha de comando ----------

def main():
    if "--teste" in sys.argv:
        teste()
        return
    ap = argparse.ArgumentParser(description="Base orgânica: seguidores e contatos de todas as redes, unidos e com nota.")
    ap.add_argument("--db", default="base-organica.sqlite")
    ap.add_argument("--nicho", default="nicho.json")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("iniciar")
    p = sub.add_parser("importar")
    p.add_argument("arquivos", nargs="+")
    p.add_argument("--rede", choices=REDES)
    p.add_argument("--eu", help="seu nome como aparece nas conversas exportadas do WhatsApp")
    p.add_argument("--como-leads", action="store_true", help=".vcf: cada contato vira lead (lista já filtrada por você)")
    p = sub.add_parser("whatsapp-backup")
    p.add_argument("pasta", nargs="?")
    p = sub.add_parser("ranking")
    p.add_argument("--top", type=int, default=30)
    p.add_argument("--csv")
    p.add_argument("--todos", action="store_true", help="inclui os frios")
    p = sub.add_parser("painel")
    p.add_argument("saida", nargs="?", default="painel-organico.html")
    p = sub.add_parser("pessoal")
    p.add_argument("chave")
    p.add_argument("motivo", nargs="?", default="manual")
    p.add_argument("--tirar", action="store_true", help="devolve ao ranking")
    for nome in ("cliente", "interesse"):
        p = sub.add_parser(nome)
        p.add_argument("chave")
        p.add_argument("produto")
    p = sub.add_parser("separar")
    p.add_argument("chave")
    p = sub.add_parser("descadastrar")
    p.add_argument("valor")
    args = ap.parse_args()
    if args.cmd == "iniciar":
        n = Path(args.nicho)
        if not n.exists():
            n.write_text(json.dumps(NICHO_PADRAO, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"Criado {n}: troque as palavras pelas do seu nicho.")
        abrir(args.db)
        print(f"Banco: {args.db}")
        return
    cfg = carregar_nicho(args.nicho)
    con = abrir(args.db)
    if args.cmd == "importar":
        cmd_importar(con, args, cfg)
    elif args.cmd == "whatsapp-backup":
        cmd_whatsapp_backup(con, args, cfg)
    elif args.cmd == "ranking":
        cmd_ranking(con, args, cfg)
    elif args.cmd == "painel":
        cmd_painel(con, args, cfg)
    elif args.cmd == "pessoal":
        ajustar(con, args.chave, "pessoal", "-" if args.tirar else args.motivo)
    elif args.cmd in ("cliente", "interesse"):
        ajustar(con, args.chave, args.cmd, None if args.produto == "-" else args.produto)
    elif args.cmd == "separar":
        ajustar(con, args.chave, "separar", 1)
    elif args.cmd == "descadastrar":
        cmd_descadastrar(con, args, cfg)


if __name__ == "__main__":
    main()
