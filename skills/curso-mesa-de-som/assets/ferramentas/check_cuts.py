# Detector de frases cortadas nos slides: compara o texto visível de cada item com as notas do apresentador.
# Uso: python3 -I check_cuts.py <slides/index.html> [-v]
# Um item visível (4+ palavras) está "cortado" quando aparece nas notas e a frase continua depois dele
# (não termina em . ! ? nem no fim do parágrafo/célula). Também acusa itens que terminam em ':' e células '—'.
# Também acusa tabela visível sem a coluna-chave (ex.: "Cenário | Mesas" sem "Resumo"; "# | Erro | O que acontece" sem "Como evitar")
# ou com coluna de referência ("#", "Mesas"…) fora da 1ª posição. Com -t, lista cada slide cuja tabela das notas tem mais de 3 colunas
# ou uma coluna-chave, e o que o slide mostra no lugar (para a leitura à mão).
# Sai com código 1 se achar algum.
import re, sys
from html.parser import HTMLParser

CIT = re.compile(r'\s*\[[^\]]{2,}\]')
PAREN = re.compile(r'\s*\([^()]*\)')
BLOCK = {'p', 'li', 'td', 'th', 'div', 'blockquote', 'pre', 'h2', 'h3', 'h4', 'figcaption', 'ul', 'ol', 'tr'}
ITEM = {'li', 'td', 'th'}  # itens visíveis; p/div só com estas classes:
ITEMCLS = {'pt', 'term', 'note', 'figcap'}

class Slides(HTMLParser):
    def __init__(s):
        super().__init__(convert_charrefs=True)
        s.slides, s.st, s.ss = [], [], []  # st: pilha (tag, kind); ss: pilha de slides abertos
    def handle_starttag(s, t, a):
        a = dict(a); cls = (a.get('class') or '').split()
        if t in ('br', 'img', 'hr', 'meta', 'link', 'input', 'wbr', 'col'): return
        kind = None
        if t == 'section': kind = 'section'; s.ss.append({'items': [], 'notes': [], 'h': '', 'id': a.get('id', '')}); s.slides.append(s.ss[-1])
        elif t == 'aside' and 'notes' in cls: kind = 'notes'
        elif t in ('svg', 'script', 'style', 'button'): kind = 'skip'
        elif t in ('h2', 'h3') and not any(k in ('notes', 'item') for _, k in s.st): kind = 'title'
        elif not any(k in ('notes', 'item', 'skip') for _, k in s.st) and (t in ITEM or (t in ('p', 'div') and ITEMCLS & set(cls))):
            if any(x[0] == 'section' for x in s.st): kind = 'item'
        s.st.append((t, kind))
        sl = s.ss[-1] if s.ss else None
        if kind == 'item': sl['items'].append([])
        if sl is not None and t in BLOCK and any(k == 'notes' for _, k in s.st[:-1]): sl['notes'].append('\n')
    def handle_endtag(s, t):
        for i in range(len(s.st) - 1, -1, -1):
            if s.st[i][0] == t:
                s.ss = s.ss[:len(s.ss) - sum(k == 'section' for _, k in s.st[i:])]
                del s.st[i:]; break
    def handle_data(s, d):
        kinds = [k for _, k in s.st]
        if 'skip' in kinds or not s.ss: return
        sl = s.ss[-1]
        if 'notes' in kinds: sl['notes'].append(d)
        elif 'item' in kinds: sl['items'][-1].append(d)
        elif 'title' in kinds: sl['h'] += d

def sp(t): return re.sub(r'\s+', ' ', t).strip()
def variants(b):
    b = sp(b); c = sp(CIT.sub('', b)); return {b, c, sp(PAREN.sub('', c)), sp(PAREN.sub('', b))}
def ends_ok(rest):
    rest = rest.lstrip()
    rest = re.sub(r'\s*\[[^\]]*\]', '', rest).strip()  # citação [..] não conta
    return not rest or re.match(r'^[.!?…]+(\s|$)', rest) or re.fullmatch(r'[;.]', rest)  # fim de frase, ou fim do item de uma lista ("…;")

def cut(piece, blocks):
    """'cut' se o pedaço aparece nas notas e a frase continua; 'ok' se termina em fim de frase; None se não aparece (reescrito)."""
    piece = sp(piece).rstrip('.').strip()
    if len(piece.split()) < 4: return 'ok'
    found = None
    for b in blocks:
        for v in variants(b):
            for lo in (False, True):
                hay, nd = (v.lower(), piece.lower()) if lo else (v, piece)
                i = hay.find(nd)
                while i >= 0:
                    if ends_ok(hay[i + len(nd):]): return 'ok'
                    found = 'cut'; i = hay.find(nd, i + 1)
    return found

# mesmas listas de build_slides.py (META, KEY)
META = {'#', 'Mesas', 'Mesa', 'Onde foi citado', 'Ver', 'URL', 'URL(s)', 'Arquivo', 'Ano do texto', 'Quem'}
KEY = ('Resumo', 'Como evitar', 'O que faz', 'Função', 'Para quê', 'Para que serve', 'Explicação curta', 'Como fazer', 'O que é certo', 'Como tratar no curso', 'Procedimento', 'O que é')
def tables(path, listing):
    bad, seen = [], 0
    h = open(path, encoding='utf-8').read()
    heads = lambda t: [sp(re.sub('<[^>]+>', '', x)) for x in re.findall(r'<th[^>]*>(.*?)</th>', re.search(r'<tr>.*?</tr>', t, re.S).group(0), re.S)]
    for m in re.finditer(r'<section id="(s[\d-]+)"(.*?)</section>', h, re.S):  # slides de tópico (não têm section dentro)
        body, _, nts = m.group(2).partition('<aside class="notes">')
        body = re.sub(r'<svg.*?</svg>', '', body, flags=re.S)
        nt = [heads(t) for t in re.findall(r'<table.*?</table>', nts, re.S)]
        vt = [heads(t) for t in re.findall(r'<table.*?</table>', body, re.S)]
        for v in vt:
            src = next((n for n in nt if set(v) <= set(n)), None)
            if any(x in META and (x == '#' or i) for i, x in enumerate(v)): bad.append((m.group(1), ' | '.join(v), 'coluna de referência no slide'))
            if src and any(x.startswith(KEY) and x not in v for x in src): bad.append((m.group(1), ' | '.join(v), 'sem a coluna-chave: ' + ' | '.join(src)))
        if listing:
            for n in nt:
                if len(n) > 3 or any(x.startswith(KEY) for x in n):
                    seen += 1
                    shown = next((' | '.join(v) for v in vt if set(v) <= set(n)), None)
                    print(f'  [tabela] {m.group(1)}: {" | ".join(n)}  →  slide: {"tabela " + shown if shown else "bullets"}')
    if listing: print(f'tabelas com mais de 3 colunas ou coluna-chave: {seen}')
    return bad

def main(path, verbose):
    p = Slides(); p.feed(open(path, encoding='utf-8').read())
    bad, total, rew = [], 0, 0
    for k, sl in enumerate(p.slides):
        blocks = [x for x in ''.join(sl['notes']).split('\n') if x.strip()]
        its = [sp(''.join(it)) for it in sl['items']]
        for j, t in enumerate(its):
            if not t: continue
            if t in ('—', '-', '–'): bad.append((sl, t, 'célula vazia')); continue
            if t.endswith(':'):  # só vale se o conteúdo vem logo depois (rótulo de uma lista de subitens)
                if j + 1 >= len(its) or not its[j + 1] or its[j + 1].endswith(':'): bad.append((sl, t, 'termina em ":"'))
                continue
            if len(t.split()) < 4: continue
            total += 1
            parts = [t] + ([t.split(': ', 1)[1]] if ': ' in t else [])  # "Rótulo: resto" também confere só o resto
            r = [cut(x, blocks) for x in parts]
            if 'ok' in r: continue
            if 'cut' in r: bad.append((sl, t, 'frase cortada'))
            else: rew += 1
    tb = tables(path, '-t' in sys.argv)
    bad += [({'id': i, 'h': ''}, t, why) for i, t, why in tb]
    print(f'itens visíveis (4+ palavras): {total} · reescritos (não aparecem nas notas): {rew} · tabelas sem a coluna-chave: {len(tb)} · problemas: {len(bad)}')
    for sl, t, why in bad[: None if verbose else 40]:
        print(f'  [{why}] {sl["id"] or sp(sl["h"])[:50]} → {t}')
    return 1 if bad else 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1], '-v' in sys.argv))
