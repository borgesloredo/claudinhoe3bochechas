"""Confere glossario.json (e glossario-extra-*.json): formato, slugs únicos,
siglas das definições cobertas, variantes que existem nas fontes. Uso: python3 -I check_glossario.py"""
import glob, html, json, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
SOURCES = [ROOT / "entregas/v1-aulas/deck/index.html", ROOT / "06-pdf/curso.html"]
PROIBIDO = re.compile(r"\b(X16|X12)\b|Em cena", re.I)


def texto_fontes():
    out = []
    for p in SOURCES:
        s = p.read_text(encoding="utf8")
        s = re.sub(r"<(script|style)\b.*?</\1>", " ", s, flags=re.S)
        out.append(html.unescape(re.sub(r"<[^>]+>", " ", s)))
    return re.sub(r"\s+", " ", " ".join(out))


def main():
    arquivos = [HERE / "glossario.json"] + sorted(map(Path, glob.glob(str(HERE / "glossario-extra-*.json"))))
    termos = [t for a in arquivos for t in json.loads(a.read_text(encoding="utf8"))]
    erros, avisos = [], []
    slugs = [t.get("slug") for t in termos]
    for s in {s for s in slugs if slugs.count(s) > 1}:
        erros.append(f"slug repetido: {s}")
    todas_var = {v for t in termos for v in t.get("variantes", [])}
    palavras_var = {w for v in todas_var for w in re.split(r"[\s/-]+", v)}
    fonte = texto_fontes().lower()
    for t in termos:
        s = t.get("slug", "?")
        if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", s or ""):
            erros.append(f"{s}: slug fora do padrão kebab-case")
        for campo in ("termo", "variantes", "definicao"):
            if not t.get(campo):
                erros.append(f"{s}: falta {campo}")
        extra = set(t) - {"slug", "termo", "variantes", "definicao", "exemplo_curto"}
        if extra:
            erros.append(f"{s}: campos desconhecidos {extra}")
        d = t.get("definicao", "")
        if len(re.findall(r"[.!?](\s|$)", d)) > 3:
            erros.append(f"{s}: definição com mais de 3 frases")
        for txt in (d, t.get("exemplo_curto", ""), t.get("termo", "")):
            if PROIBIDO.search(txt):
                erros.append(f"{s}: texto proibido: {PROIBIDO.search(txt).group(0)}")
        # sigla (2+ maiúsculas) usada na definição precisa existir como variante de algum termo
        for sig in set(re.findall(r"\b[A-Z][A-Z0-9/+-]*[A-Z0-9]\b", d)):
            if sig not in todas_var and sig not in palavras_var and sig not in {"L", "R", "C", "XR18", "XR16", "XR12", "MR18", "MR12", "X18", "M32R", "M32C", "LIVE", "CD", "DVD", "TV", "S", "X", "P", "B"}:
                avisos.append(f"{s}: sigla '{sig}' na definição sem verbete")
        if not any(v.lower() in fonte for v in t.get("variantes", [])):
            avisos.append(f"{s}: nenhuma variante aparece no deck V1 nem no PDF")
    dono = {}
    for t in termos:
        for v in t.get("variantes", []):
            dono.setdefault(v, []).append(t["slug"])
    amb = {v: d for v, d in dono.items() if len(d) > 1}
    for e in erros:
        print("ERRO  ", e)
    for a in avisos:
        print("AVISO ", a)
    print(f"\n{len(termos)} termos em {len(arquivos)} arquivo(s); {len(erros)} erro(s), {len(avisos)} aviso(s)")
    print("Variantes ambíguas (escolha o slug pelo sentido):")
    for v, d in sorted(amb.items()):
        print(f"  {v!r}: {', '.join(d)}")
    sys.exit(1 if erros else 0)


if __name__ == "__main__":
    main()
