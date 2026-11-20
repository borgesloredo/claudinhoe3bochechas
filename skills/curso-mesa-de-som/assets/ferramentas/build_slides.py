# Gera 07-slides/index.html (reveal.js) a partir de 06-pdf/curso.html (só biblioteca padrão).
# Uso: python3 -I build_slides.py [<curso.html> [<saida.html>]]            (padrão: 06-pdf/curso.html → 07-slides/index.html)
#      python3 -I build_slides.py --only s9-1-1,s12-1-1 --out /tmp/x.html  (prévia: deck só com esses slides, assets apontando para 07-slides)
# Quais slides existem, em que ordem, e o corpo dos slides fundidos vêm de tools/enxugamento.py; a nota de cada slide vem de tools/notes/<id>.html (política em tools/notes/README.md).
# Sob medida: tools/bespoke/<id>.svg (e .js) vale para QUALQUER slide <id>: tópico (troca o diagrama genérico), cap-N (motivo ao lado do número),
# quiz-N (painel do diagrama) e os demais (camada .bsp-layer por cima do slide). Contrato por tipo em tools/bespoke/README.md.
import argparse, glob, html, json, os, re, runpy, sys, textwrap
from html.parser import HTMLParser

TOOLS = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(TOOLS); DECK = f'{ROOT}/07-slides'
ap = argparse.ArgumentParser()
ap.add_argument('src', nargs='?', default=f'{ROOT}/06-pdf/curso.html')
ap.add_argument('out', nargs='?')
ap.add_argument('--out', dest='out2', help='arquivo de saída (padrão: 07-slides/index.html)')
ap.add_argument('--only', default='', help='ids separados por vírgula (ex.: s9-1-1,cap-9,quiz-9): deck de prévia só com esses slides')
A = ap.parse_args()
SRC, OUT = A.src, A.out2 or A.out or f'{DECK}/index.html'
ONLY = {re.sub(r'-c\d+$', '', x.strip()) for x in A.only.split(',') if x.strip()}  # "-c2" é gerado no navegador: vale o slide de origem
BESPOKE = {os.path.basename(f)[:-4]: f for f in glob.glob(f'{TOOLS}/bespoke/*.svg')}
VIZ = runpy.run_path(f'{TOOLS}/slides_viz.py')  # mini-diagramas SVG próprios
CFG = runpy.run_path(f'{TOOLS}/enxugamento.py')  # enxugamento: ordem final dos slides, fusões (bullets, títulos, diagramas), quizzes e aberturas
NOTES_DIR = f'{TOOLS}/notes'  # notes/<id>.html, se existir, é a nota do slide (política em notes/README.md)
raw = open(SRC, encoding='utf-8').read()
CSS_PDF = raw[raw.find('<style>') + 7:raw.find('</style>')]
SVGS = []
def _svg(m):
    SVGS.append(m.group(0)); return f'<svgph data-i="{len(SVGS)-1}"></svgph>'
body = re.sub(r'<svg\b.*?</svg>', _svg, raw[raw.find('<body'):], flags=re.S)

# ---------------------------------------------------------------- árvore HTML mínima
VOID = {'br', 'img', 'hr', 'meta', 'link', 'input', 'wbr', 'col'}
class N:
    def __init__(s, tag, attrs): s.tag, s.attrs, s.kids = tag, dict(attrs), []
    def cls(s): return (s.attrs.get('class') or '').split()
class P(HTMLParser):
    def __init__(s):
        super().__init__(convert_charrefs=True); s.root = N('root', []); s.st = [s.root]
    def handle_starttag(s, t, a):
        n = N(t, a); s.st[-1].kids.append(n)
        if t not in VOID: s.st.append(n)
    def handle_startendtag(s, t, a): s.st[-1].kids.append(N(t, a))
    def handle_endtag(s, t):
        for i in range(len(s.st) - 1, 0, -1):
            if s.st[i].tag == t: del s.st[i:]; break
    def handle_data(s, d): s.st[-1].kids.append(d)
p = P(); p.feed(body)
esc = lambda t: html.escape(t, quote=False)

def ser(n, notes=False):
    if isinstance(n, str): return esc(n)
    if n.tag == 'svgph':
        i = int(n.attrs['data-i'])
        return '' if notes else SVGS[i]
    a = ''.join(f' {k}="{html.escape(v or "", quote=True)}"' for k, v in n.attrs.items())
    if n.tag in VOID: return f'<{n.tag}{a}>'
    return f'<{n.tag}{a}>' + ''.join(ser(k, notes) for k in n.kids) + f'</{n.tag}>'
def inner(n, notes=False): return ''.join(ser(k, notes) for k in n.kids)
def text(n):
    if isinstance(n, str): return n
    if n.tag == 'svgph': return ''
    if n.tag == 'br': return ' '
    return ''.join(text(k) for k in n.kids)
def els(n, tag=None, cls=None):
    return [k for k in n.kids if isinstance(k, N) and (tag is None or k.tag == tag) and (cls is None or cls in k.cls())]
def find(n, tag=None, cls=None):
    for k in n.kids if isinstance(n, N) else []:
        if isinstance(k, N):
            if (tag is None or k.tag == tag) and (cls is None or cls in k.cls()): return k
            r = find(k, tag, cls)
            if r: return r
def findall(n, tag):
    out = []
    for k in n.kids:
        if isinstance(k, N):
            if k.tag == tag: out.append(k)
            out += findall(k, tag)
    return out
def notes(*parts): return '<aside class="notes">' + ''.join(parts) + '</aside>'

# ---------------------------------------------------------------- mesas em chips
XAIR = ['XR18', 'X18', 'XR16', 'XR12', 'MR18', 'MR12']
X32 = ['X32', 'X32 Rack', 'X32 Compact', 'X32 Producer', 'M32', 'M32R', 'M32C']
def chips(m):
    names = [x.strip() for x in m.strip().strip('()').split(',') if x.strip()]
    s = set(names)
    if not names: return ''
    if s >= set(XAIR + X32): return '<div class="chips"><span class="chip all">Todas as 13 mesas</span></div>'
    out = []
    for fam, lst, c in (('X AIR/M AIR', XAIR, 'xa'), ('X32/M32', X32, 'xm')):  # rótulo curto: o chip é cabeçalho, não texto
        got = [n for n in lst if n in s]
        if s >= set(lst): out.append(f'<span class="chip {c}" title="Família {fam} (todas as mesas)">{fam} (todas)</span>')
        elif len(got) >= 3: out.append(f'<span class="chip {c}" title="{esc(", ".join(got))}">{fam.split("/")[0]} ·{len(got)}</span>')  # 4+ da mesma família: um chip só (lista no tooltip)
        else: out += [f'<span class="chip {c}">{esc(n)}</span>' for n in got]
    out += [f'<span class="chip">{esc(n)}</span>' for n in names if n not in XAIR + X32]
    return '<div class="chips">' + ''.join(out) + '</div>'
def head(h):  # (número, título, mesas)
    t = text(find(h, 'span', 'ht') or h).strip(); m = find(h, 'span', 'mesas')
    num, _, tit = t.partition(' ') if re.match(r'\d', t) else ('', '', t)
    return num, CFG['TITLE'].get(num, tit), CFG['MESAS'].get(num, text(m) if m else '')

# ---------------------------------------------------------------- resumo automático
CIT = re.compile(r'\s*\[[^\]]{2,}\]|\s*Fontes?:\s*(?=[.;]|$|\s*\[)')  # citações [..] e "Fontes:" que ficam vazios
PAREN = re.compile(r'\s*\([^()]*\)')
XREF = re.compile(r'^[^.]{0,40}\b(está|estão|ver|veja)\b[^.]{0,20}\d+\.\d+(\.\d+)?\)?\.?$')
SENT = re.compile(r'(?<=[.!?])\s+(?=[A-ZÁÉÍÓÚÂÊÔÃÕÇ"(])')
def clip(t, n=120, sentence=True, tol=1.5):
    r = _clip(t, n, sentence, tol)
    return '' if r.count('"') % 2 and not t.count('"') % 2 else r  # cortou no meio de uma citação (aspas abertas): sem versão curta
def _clip(t, n=120, sentence=True, tol=1.5):
    """Versão curta e FECHADA do texto: só frases inteiras (nunca um pedaço de frase nem '…').
    Pega a 1ª frase (puxa a seguinte se a 1ª for curta demais); se não couber em tol×n, tenta sem os parênteses
    que são só aparte (lista de mesas, referência). Devolve '' quando nenhuma frase inteira cabe:
    quem chama descarta o item (ele segue completo nas notas)."""
    t = re.sub(r'\s+', ' ', CIT.sub('', t)).strip().lstrip('.;:, ')
    ss = SENT.split(t) if sentence else [t]
    while len(ss) > 1 and XREF.match(PAREN.sub('', ss[0])): ss = ss[1:]  # "O hardware (…) está em 1.1.5." não ensina: vai a frase seguinte
    best, acc = '', ''
    for x in ss:
        acc = (acc + ' ' + x).strip()
        if len(acc) <= n * tol: best = acc
        elif len(d := depar(acc)) <= n * tol: best = d
        else: break
        if len(best) >= 25: break
    return best
KEEPPAR = re.compile(r'\s*\((?:ou|e|mas|não|nem|só|sem|exceto|menos|salvo|apenas|inclusive|até)\b', re.I)
def depar(t):  # tira parênteses de aparte; os que mudam o sentido ("(ou desligado…)", "(só na X32)") ficam e a frase não encurta
    if KEEPPAR.search(t): return t
    return re.sub(r'\s+([,.;:])', r'\1', PAREN.sub('', t)).strip().lstrip('.;:, ')
SUB = re.compile(r'(?i:Além|Apesar|Fora|Exceto|Segundo|Conforme|Diferente|Para|Se|Quando|Caso|Ao|Antes|Depois|Com|Sem|Como|Mesmo|Embora|Enquanto|Em|Na|No|Nas|Nos|Durante|Assim|Já)\b')
up = lambda t: t[:1].upper() + t[1:]
# Slide = resumo curto: até MAXI itens e ~SLIDE_W palavras visíveis no total (kicker + título + chips + corpo).
# O texto completo de cada seção fica nas notas do apresentador (tecla S).
SLIDE_W, MAXI, MINB = 50, 5, 26
BW, TOL = 55, 1.6  # bullet: ~55 caracteres; uma frase inteira cabe até BW×TOL (best_summary tenta frases maiores); frase maior fica só nas notas
nw = lambda t: len(t.split())
MESA = re.compile(r'(XR18|X18|XR16|XR12|MR18|MR12|X32|M32R?C?|M32R|Rack|Compact|Producer|Core|LIVE|Live|Família|família|X|M|AIR|todas|e|as|a|[,/()×])$')
is_label = lambda t: all(MESA.match(w) for w in re.findall(r'[\w-]+|[,/()×]', t))  # "Família X AIR", "XR16, XR12"…
def li_html(li, intro=False):  # 1 bullet curto; sublistas só nas notas (a 1ª entra se o item sozinho não diz nada)
    # intro=True: item que apresenta uma sublista ("Usos ensinados:"); vira só o rótulo, e os subitens viram bullets (summary)
    kids = [k for k in li.kids if not (isinstance(k, N) and k.tag in ('ul', 'ol', 'p')) and not (isinstance(k, str) and not k.strip())]
    subs = [x for k in li.kids if isinstance(k, N) and k.tag in ('ul', 'ol') for x in els(k, 'li')]
    tidy = lambda t: re.sub(r'\s+', ' ', CIT.sub('', t)).strip(' :;,')
    lead, colon, lt = '', False, ''
    if kids and isinstance(kids[0], N) and kids[0].tag == 'strong':
        lead = text(kids[0]).strip(); colon = lead.endswith(':'); lt = lead[-1:]; lead = tidy(lead); kids = kids[1:]
    own = [k for k in li.kids if not (isinstance(k, N) and k.tag in ('ul', 'ol', 'p'))]  # com os espaços entre tags ("descontinuada <b>(…)</b>")
    raw = CIT.sub('', ''.join(text(k) for k in (own[next(i for i, k in enumerate(own) if k is kids[0]):] if kids else []))).strip()
    m = re.match(r'\(([^()]*)\)\s*:', raw)
    if lead and m:  # "Link Preferences (Setup): …"; parêntese longo (lista de mesas) sai do bullet
        if len(m.group(1)) <= 20: lead += f' ({m.group(1)})'
        raw = raw[m.end():].strip(); colon = True
    colon = colon or raw.startswith(':')
    lp = re.sub(r'^\([^()]*\)\s*', '', raw)[:1]  # pontuação entre o lead e o resto ("Ligue o EQ</b>, senão…", "<b>X;</b> Y"): não pode sumir
    lp = lp if lp in ',;.' else lt if lt in ',;' else ''
    rest = tidy(raw)
    if not rest.strip('.'): rest = ''  # sobrou só o ponto final depois da citação
    if intro and lead:
        r = tidy(re.sub(r'^\([^()]*\)[.:]?', '', PAREN.sub('', raw).strip()))
        r = clip(r, max(22, BW - len(lead)), tol=TOL) if nw(r) >= 4 else ''
        return f'<b>{esc(lead)}</b>: {esc(r)}' if r else f'<b>{esc(lead)}</b>:', f'{lead} {r}'
    if subs and not intro and (len(rest.split()) < 4 or (not lead and raw.endswith(':'))):  # "X:" + 1º subitem
        rest = (rest + ': ' if rest else '') + tidy(''.join(text(k) for k in subs[0].kids if not (isinstance(k, N) and k.tag in ('ul', 'ol', 'p'))))
        colon = colon or not raw.strip(' :')
    if raw.rstrip().endswith(':') and not intro and ':' not in rest:  # "X, com 3 abas:" sem a lista que vem depois: frase incompleta, fica nas notas
        return '', ''
    if not lead:
        t = '' if raw.endswith(':') and not subs else up(clip(rest, BW, tol=TOL))  # "X:" que apresenta uma tabela: fica nas notas
        if t and intro: t += ':'  # rótulo da lista: os subitens vêm logo depois
        return esc(t), t
    lead = up(clip(lead, BW, tol=TOL))
    if not lead: return '', ''
    r = clip(rest, max(22, BW - len(lead)), tol=TOL) if rest else ''
    if r[:1] == ':': r = r[1:].strip(); colon = True  # "(...): x" sem o parêntese
    if not r and rest: r = clip(rest, BW, tol=TOL)  # o resto inteiro, se lead + resto ainda couber
    if r and len(lead) + len(r) > BW * TOL + 8: r = ''
    if not r:
        alone = clip(rest, BW, tol=TOL) if rest else ''
        whole = not rest or lead[-1:] in '.!?' or lp == '.'  # o lead fecha a frase; "X:" ou "X, e…" sozinho seria frase cortada
        if (nw(lead) >= 4 or (nw(lead) >= 2 and lead[-1:] in '.!?')) and not is_label(lead) and not colon and whole:
            return f'<b>{esc(lead)}</b>', lead  # o lead em negrito já é a ideia ("Envio de efeito em pré-fader é erro.")
        if not colon and rest:  # "PFL é o padrão… e serve…": o lead é o começo da frase; a frase inteira, se couber
            full = clip(lead + ('' if rest[:1] == '(' else lp) + ' ' + rest.lstrip('.').strip(), BW, tol=TOL)
            if full.startswith(lead) and len(full) > len(lead): return f'<b>{esc(lead)}</b>{esc(full[len(lead):])}', full
            if full: return esc(full), full
        if alone and nw(alone) >= 4 and not is_label(lead) and colon:
            alone = up(alone)  # "Pré ou pós-EQ: o pré mostra…" → só a explicação
            return esc(alone), alone
        return '', ''  # sobrou só um rótulo ("X:" ou começo de frase): o item fica nas notas
    sep = ' ' if r[:1] == '(' else lp + ' ' if lp else '' if r[:1] in ',.;)' else ': ' if colon and lead[-1:] not in '.!?' else ' '
    if sep == ': ' and r.split(' ', 1)[0] in ('O', 'A', 'Os', 'As', 'Um', 'Uma'): r = r[0].lower() + r[1:]  # "Aviso no app: o recomendado…"
    return f'<b>{esc(lead)}</b>{sep}{esc(r)}', f'{lead} {r}'
ROWS, COLS = 3, 3  # no slide: até 3 linhas e 3 colunas, células curtas; a tabela completa está nas notas (tecla S)
KEYROW = re.compile(r'(XR18|MR18|X32|M32)\b')
DASH = re.compile(r'^[\s—–\-−.]*$')
def cell(t):  # célula curta; se não houver, o rótulo antes de ':' / ';' / '(' ("Alto: mesmos menus…" → "Alto"); '—' ou vazia → ''
    if DASH.match(t) or re.match(r'\s*https?:', t): return ''  # URL não cabe no slide (fica nas notas)
    c = clip(t, 32)
    if c: return c
    c = re.split(r'(?<!\d):(?!\d)|;| – |\(', re.sub(r'\s+', ' ', CIT.sub('', t)))[0].strip(' ,.')
    return c if 0 < len(c) <= 40 and nw(c) <= 3 else ''  # rótulo de até 3 palavras; mais que isso já é começo de frase
# Colunas de referência ("#", "Mesas", "Onde foi citado", URL…) nunca dão o sentido da linha; no slide, só ficam se forem a 1ª coluna (a "Mesas" de 3.1.4 é a chave da linha).
# Colunas-chave (o que a linha ensina: "Resumo", "Como evitar", "O que faz"…) têm prioridade; tabela que não consegue mostrá-las vira bullets "rótulo: chave" (table_rows).
# A mesma lista está em check_cuts.py, que acusa tabela visível sem a coluna-chave (2.1.6 e 24.2.1 caíram nisso).
META = {'#', 'Mesas', 'Mesa', 'Onde foi citado', 'Ver', 'URL', 'URL(s)', 'Arquivo', 'Ano do texto', 'Quem'}
KEY = ('Resumo', 'Como evitar', 'O que faz', 'Função', 'Para quê', 'Para que serve', 'Explicação curta', 'Como fazer', 'O que é certo', 'Como tratar no curso', 'Procedimento', 'O que é')
iskey = lambda h: h.startswith(KEY)
def table_cols(hd):  # colunas que podem ir ao slide, na ordem original: 1ª coluna (salvo "#"), as colunas-chave e depois as demais, até COLS
    ok = [j for j in range(len(hd)) if hd[j] != '#' and (j == 0 or hd[j] not in META)]
    pick = ok[:1] + [j for j in ok[1:] if iskey(hd[j])] + [j for j in ok[1:] if not iskey(hd[j])]
    return sorted(pick[:COLS])
def table_html(tbl, budget):
    trs = findall(tbl, 'tr')
    if not trs: return '', 0
    hd = [text(c).strip() for c in els(trs[0])]; cols = table_cols(hd)
    cells = [[cell(text(ec[k])) for k in cols if k < len(ec)] for ec in (els(tr) for tr in trs)]
    keep = [j for j in range(len(cells[0])) if (j == 0 or cells[0][j]) and sum(bool(r[j:j + 1] and r[j]) for r in cells[1:]) * 2 >= len(cells) - 1]
    if len(keep) < 2: return '', 0  # tabela de uma coluna só (ex.: só nomes de mesas) não ensina: ficam os bullets
    if any(iskey(h) and j not in [cols[k] for k in keep] for j, h in enumerate(hd)): return '', 0  # a coluna-chave não coube: vira bullets (table_rows)
    cells = [[r[j] for j in keep if j < len(r)] for r in cells]  # coluna de textos longos (ex.: URLs) fica só nas notas
    body, seen = [], set()
    for r in cells[1:]:
        if len(r) == len(keep) and all(r) and tuple(r) not in seen: seen.add(tuple(r)); body.append(r)
    body.sort(key=lambda r: not KEYROW.match(r[0]))  # XR18/MR18/X32/M32 primeiro (ordem estável)
    cells = [cells[0]] + body[:ROWS]
    while cells and sum(nw(c) for r in cells for c in r) > budget: cells.pop()  # tira linhas até caber
    if len(cells) < 2: return '', 0
    rows = ['<tr>' + ''.join(f'<{"th" if i == 0 else "td"}>{esc(c)}</{"th" if i == 0 else "td"}>' for c in r) + '</tr>' for i, r in enumerate(cells)]
    return (f'<div class="tscroll"><table class="mini">{"".join(rows)}</table></div>',
            sum(nw(c) for r in cells for c in r))  # legenda de ~7 palavras não entra na conta: tirava a definição seguinte (dBu em 25.1.1)

def table_rows(tbl):  # tabela que não cabe no slide: cada linha vira "1ª célula: 2ª célula" curto
    out, trs = [], findall(tbl, 'tr')
    hd = [text(x).strip() for x in els(trs[0])] if trs else []
    cols = table_cols(hd); i0 = cols[0] if cols else 0  # "# | Erro | …": o rótulo é "Erro", não o número
    j = next((i for i in cols[1:] if iskey(hd[i])), cols[1] if len(cols) > 1 else 1)  # "Recurso | Mesas | O que faz": a 2ª célula é a que explica, não a lista de mesas
    for tr in trs[1:]:
        c = els(tr)
        if len(c) < 2: continue
        c = [c[i0], c[j]] if max(i0, j) < len(c) else c
        if not re.search(r'[^\W\d_]', text(c[0]) + text(c[1])): continue  # tabela de valores ("8: 8", "8: 4"): sem letras não diz nada; fica nas notas
        a = cell(text(c[0])); b = '' if DASH.match(text(c[1])) else clip(text(c[1]), max(22, BW - len(a)), tol=TOL) or cell(text(c[1]))
        if a and b and len(a) + len(b) <= BW * TOL + 8: out.append((f'<b>{esc(a)}</b>: {esc(b)}', f'{a} {b}'))
    return out
def summary(blocks, budget, drop=()):  # pontos principais de cada bloco, até MAXI itens e `budget` palavras
    items, used, tbl = [], 0, False
    def add(h, t):
        nonlocal used
        if not t.strip(): return True  # item sem versão curta: pula (está nas notas)
        if any(html.unescape(re.sub('<[^>]+>', '', h)).strip().startswith(d) for d in drop): return True  # repetição (Agente 12)
        h = re.sub(r'(?<!\.)\.\.(?!\.)', '.', h)
        if len(items) >= MAXI or (items and used + nw(t) > budget): return False
        items.append(h); used += nw(t); return True
    for b in blocks:
        if not isinstance(b, N) or len(items) >= MAXI: continue
        c = b.cls()
        if b.tag == 'p':
            t = text(b).strip(); st = els(b, 'strong')
            if not t or t.endswith(':') or (st and text(st[0]).strip() == t): continue  # rótulos e "X:" que apresentam algo ficam nas notas
            t = up(clip(t, BW + 10, tol=TOL))
            if len(t.strip(' .:;').split()) > 1: add(f'<p class="pt fragment">{esc(t)}</p>', t)
        elif b.tag in ('ul', 'ol'):
            for li in els(b, 'li'):
                subs = [x for k in els(li) if k.tag in ('ul', 'ol') for x in els(k, 'li')]
                own = CIT.sub('', ''.join(text(k) for k in li.kids if not (isinstance(k, N) and k.tag in ('ul', 'ol')))).strip()
                if len(subs) >= 2 and own.endswith(':'):  # item que apresenta uma lista: rótulo + subitens como bullets
                    sub = [(h, t) for h, t in map(li_html, subs) if t.strip()]
                    lab = li_html(li, True)
                    if not sub or len(items) + 2 > MAXI or used + nw(lab[1]) + nw(sub[0][1]) > budget: continue  # rótulo sem subitem não fica
                    n0 = len(items)
                    for h, t in [lab] + sub: add(f'<li class="fragment">{h}</li>', t)  # subitem que não cabe é pulado (está nas notas)
                    if len(items) == n0 + 1: items.pop(); used -= nw(lab[1])  # rótulo "X:" sem nenhum subitem depois dele não fica
                    continue
                h, t = li_html(li)
                if t.rstrip().endswith(':'): continue  # "X:" solto, sem o conteúdo logo depois: fica nas notas
                add(f'<li class="fragment">{h}</li>', t)  # não coube: pula para o próximo item, que pode ser mais curto
        elif b.tag == 'blockquote' and 'diverge' in c:  # selo de abordagens divergentes do PDF: assunto + as opções (o rótulo em negrito de cada item)
            st = find(b, 'span', 'dv-t'); subj = text(st).strip(' .') if st else ''
            opts = [text(find(li, 'strong') or li).strip(' :.') for li in findall(b, 'li')][:4]
            if subj and opts: add(divg_li(subj, opts), f'{subj} ' + ' '.join(opts))
        elif b.tag == 'blockquote' and 'term' in c:
            st = find(b, 'strong'); lead = text(st).strip() if st else ''
            rest = text(b).strip()[len(lead):] if st and text(b).strip().startswith(lead) else text(b)
            rest = clip(rest, BW, tol=TOL); add(f'<div class="term"><b>{esc(lead)}</b> {esc(rest)}</div>', rest and f'{lead} {rest}')
        elif b.tag == 'blockquote':
            t = clip(text(b), BW, tol=TOL); add(f'<div class="note">{esc(t)}</div>', t)
        elif b.tag == 'div' and 'tbl' in c and not tbl:  # só a 1ª tabela da seção
            more = any(isinstance(x, N) and x.tag in ('ul', 'ol', 'p', 'blockquote') for x in blocks[blocks.index(b) + 1:])
            h, w = table_html(find(b, 'table'), int((budget - used) * (0.6 if more else 1)))  # deixa espaço para os bullets que vêm depois
            if h and len(items) < MAXI: items.append(h); used += w; tbl = True
            elif not h:
                for h, t in table_rows(find(b, 'table'))[:3]:
                    if not add(f'<li class="fragment">{h}</li>', t): break
        elif b.tag == 'pre':
            lines = [l for l in text(b).strip('\n').split('\n') if l.strip()][:5]
            add(f'<pre class="flow">{esc(chr(10).join(lines))}</pre>', ' '.join(lines))
    return wrap(items)
def best_summary(*a):  # frases curtas primeiro; se o slide ficar com menos itens, aceita frases inteiras mais longas
    global TOL
    outs = []
    for TOL in (1.6, 2.0, 2.4): outs.append(summary(*a))
    TOL = 1.6
    return max(outs, key=lambda h: (len(re.findall(r'<li|<p class|<div class="(?:term|note)"|<tr', h)), len(h)))
def wrap(items):  # agrupa <li> consecutivos numa lista
    out, inlist = [], False
    for h in items:
        if h.startswith('<li') and not inlist: out.append('<ul class="pts">'); inlist = True
        if not h.startswith('<li') and inlist: out.append('</ul>'); inlist = False
        out.append(h)
    if inlist: out.append('</ul>')
    return ''.join(out)

# ---------------------------------------------------------------- passos: cada fragment do corpo ganha data-i (1..); o diagrama acende a peça do passo e o cabeçalho mostra pontos ●●○
FRAG = re.compile(r'<(li|p)(\s[^>]*?class="[^"]*fragment[^"]*"[^>]*)>', re.S)
def stepkeys(num, body):
    it = iter(range(1, 999))
    return FRAG.sub(lambda m: f'<{m.group(1)} data-i="{next(it)}"{m.group(2)}>', body)

# ---------------------------------------------------------------- quizzes (1 por capítulo, baseados no texto do PDF)
QUIZ = CFG['QUIZ']  # cn -> (pergunta, alternativas, índice da certa, explicação: o porquê, sem repetir a alternativa)

# ---------------------------------------------------------------- direção visual "Palco escuro" (07-slides/redesign/opcao-1/DESIGN.md)
# O SVG do slides_viz.py entra na carcaça de 3 faixas (cabeçalho com o título do diagrama, tela, teclas dos fragments).
# As teclas (.vsteps) são montadas no navegador, depois que o tópico longo é dividido em "(continuação)".
ARR = '<svg class="arr" viewBox="0 0 16 16" aria-hidden="true"><path d="M2 8h11M9 4l4 4-4 4"/></svg>'
CURSOR = '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M3 1.5v11.2l3-2.7 2 4.6 2.1-.9-2-4.5 4-.2z"/></svg>'
DARK_DEFS = ('<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>'
             '<marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#8a95a1"/></marker>'
             '<marker id="ahr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#ff4b3e"/></marker></defs></svg>')
CROP = 24  # o rótulo de eixo mais alto dos diagramas (axes(): y1 - 6) começa em y ~26
SYM = re.compile(r'([→←✓✕⚠])')  # fora do subset latin das fontes: tspan com a fonte de símbolos do sistema
EMOJI = {'▶': 'VÍDEO', '🎓': 'CURSO', '📄': 'PDF', '🎧': 'ÁUDIO', '🔒 ': ''}
def addcls(svg, c):  # class="dg" liga o mapa de classes do CSS (bx, ln, sm…) aos tokens escuros
    head = svg[:svg.find('>')]
    return svg.replace('class="', f'class="{c} ', 1) if 'class="' in head else svg.replace('<svg ', f'<svg class="{c}" ', 1)
def dg(svg, crop=True):
    """svg do slides_viz -> (título, svg pronto para a tela). Igual a ref_dg.py (DESIGN.md 2.3.2). crop=False: diagrama sob medida (não perde a faixa de cima)."""
    m = re.search(r'<text[^>]*class="vt">(.*?)</text>', svg)
    title = html.unescape(m.group(1)) if m else ''
    if m: svg = svg.replace(m.group(0), '')
    mh = re.search(r'viewBox="0 0 400 (\d+)"', svg)
    if mh and crop: svg = svg.replace(mh.group(0), f'viewBox="0 {CROP} 400 {int(mh.group(1)) - CROP}"', 1)
    svg = addcls(svg, 'dg')
    for k, v in EMOJI.items(): svg = svg.replace(k, v)
    if title == 'Duas famílias, 13 mesas':  # o único diagrama em que a caixa nomeia a família: cor de fita
        svg = svg.replace('class="bxg"', 'class="bxg fam-xa"', 1).replace('class="bxb"', 'class="bxb fam-xm"', 1)
    svg = re.sub(r'(<text[^>]*>)([^<]*)(</text>)', lambda t: t.group(1) + SYM.sub(lambda g: f'<tspan class="sym{" ar" if g.group(1) in "→←" else ""}">{g.group(1)}</tspan>', t.group(2)) + t.group(3), svg)
    return title, svg
def carcass(svg, foot=None, crop=True):  # foot='': sem teclas de passo (painel do quiz)
    t, s = dg(svg, crop)
    return (f'<div class="viz vz3"><header class="vh"><span class="vt">{esc(t)}</span><span class="vcount" aria-hidden="true"></span></header>'
            f'<div class="vscreen">{s}</div>' + ('<ol class="vsteps"></ol>' if foot is None else foot) + '</div>')
USED = set()  # ids cujo <id>.svg já entrou no lugar próprio (tópico, cap-N, quiz-N); os outros viram camada (hookbsp)
def bsp(sid):  # SVG sob medida de um slide (cru) ou ''; marca como usado
    if sid not in BESPOKE: return ''
    USED.add(sid); return open(BESPOKE[sid], encoding='utf-8').read()
def hookbsp(h):  # capa, sumário, abertura, como-usar, encerramento, explorador, caminho-do-sinal…: o SVG vira uma camada 1280×720 por cima do slide
    sid = re.match(r'<section id="([^"]+)"', h).group(1)
    if sid not in BESPOKE or sid in USED or re.match(r'<section[^>]*class="topic', h): return h
    lay = f'<div class="bsp bsp-layer" aria-hidden="true">{dg(bsp(sid), False)[1]}</div>'
    return h.replace('<aside class="notes">', lay + '<aside class="notes">', 1)

# ---------------------------------------------------------------- diagramas interativos próprios
FLOW = [  # (chave, rótulo, título, descrição, capítulo)
 ("fonte", "Fonte", "Fonte / patch", "De onde vem o sinal do canal: entrada física, retorno USB ou, na X32/M32, blocos de 8 do patch.", 5),
 ("ganho", "Ganho", "Ganho e +48 V", "O pré-amp levanta o sinal do microfone. Meta: média perto de −18 dBFS. Phantom liga microfones condensadores.", 5),
 ("lowcut", "Low Cut", "Low Cut (HPF)", "Corta os graves que não servem para aquela fonte. Usado em quase todos os canais.", 6),
 ("gate", "Gate", "Gate / Expansor", "O gate abre quando o som passa do threshold e atenua o vazamento entre as notas. Na voz: A sem gate · B expansor ou range parcial · C automix.", 7),
 ("insert", "Insert", "Insert", "Coloca um processador (por exemplo, um compressor externo) em série, no meio do caminho do canal.", 13),
 ("eq", "EQ", "EQ de 4 bandas", "Molda o timbre. Regra de ouro: corte antes de reforçar.", 6),
 ("comp", "Comp", "Compressor", "Acima do threshold a saída sobe menos que a entrada. Na X32/M32, antes ou depois do EQ: A EQ antes · B compressor antes · C misto.", 8),
 ("delay", "Delay", "Delay de canal", "Atrasa o canal. Só na família X32/M32.", 9),
 ("fader", "Fader", "Mute e fader", "Aqui se mixa: o volume do canal na mistura. Não mixe no ganho.", 9),
 ("pan", "Pan", "Pan", "Distribui o canal entre as caixas: LR nas X AIR, LR ou LCR na X32/M32.", 9),
 ("main", "Main", "Main LR", "A soma que vai para o PA (na X32/M32 também Mono/Center).", 9),
]
FLOWDV = ('gate', 'comp')   # blocos com o selo de abordagens divergentes (gate na voz; EQ antes ou depois do compressor)
SEND = ("envios", "Envios: Aux, Mix bus, FX", "Envios (Aux / Mix bus / FX)", "Cópias do canal para retornos e efeitos. O ponto de captação (pré ou pós-fader) decide se o envio segue o fader.", 10)
def flow_slide(extra=''):
    # serpentina: 6 blocos em cima (esquerda → direita), 5 embaixo (direita → esquerda) até o PA; envios saem do fader
    pos = [(105 + 186 * i, 78) for i in range(6)] + [(1035 - 186 * i, 238) for i in range(5)]
    def blk(k, lab, t, d, c, cx, cy, bx, by, w, h, cl):
        a = lambda s: html.escape(s, quote=True)
        dv = k in FLOWDV   # bloco com abordagens divergentes: marca de bifurcação no canto e o selo no painel
        dva = ' data-dv="1"' if dv else ''; dvk = f'<g class="dvk" transform="translate({bx + w - 30} {by + 6})">{ICO["fork"]}</g>' if dv else ''
        return (f'<g class="blk {cl}" data-k="{k}" tabindex="0" role="button" aria-label="{a(t)}" data-t="{a(t)}" data-d="{a(d)}" data-c="{c}" data-x="{cx}" data-y="{cy}"{dva}>'
                f'<rect class="halo" x="{bx - 5}" y="{by - 5}" width="{w + 10}" height="{h + 10}" rx="13"/><rect class="box" x="{bx}" y="{by}" width="{w}" height="{h}" rx="10"/>'
                f'<circle class="led0" cx="{bx + 16}" cy="{by + 15}" r="5"/><circle class="led1" cx="{bx + 16}" cy="{by + 15}" r="5"/>'
                f'<text x="{cx}" y="{by + h / 2 + 9:.0f}" text-anchor="middle">{esc(lab)}</text>'
                + dvk + '</g>')
    g = ['<path class="flowpath" d="M14 78 L1060 78 C1128 78 1128 238 1060 238 L136 238" fill="none" stroke="#3a4552" stroke-width="3"/>',
         '<path class="branchpath" d="M663 276 L663 318" fill="none" stroke="#8a95a1" stroke-width="3" stroke-dasharray="6 5"/>',
         '<circle cx="14" cy="78" r="8" fill="#0b0e11" stroke="#8a95a1" stroke-width="2.5"/><circle class="sdot" r="16" fill="#2fe07b" fill-opacity=".22"/><circle class="sdot" r="7" fill="#b8ffd6"/>']
    g += [f'<polyline class="chev" points="{x},70 {x + 9},78 {x},86" fill="none" stroke="#8a95a1" stroke-width="2.5"/>' for x in (193, 379, 565, 751, 937)]
    g += [f'<polyline class="chev" points="{x},230 {x - 9},238 {x},246" fill="none" stroke="#8a95a1" stroke-width="2.5"/>' for x in (947, 761, 575, 389, 203)]
    g.append('<g class="pa"><rect x="72" y="196" width="60" height="84" rx="6" fill="#12161b" stroke="#3a4552" stroke-width="2"/><circle cx="102" cy="214" r="7" fill="none" stroke="#8a95a1" stroke-width="2"/>'
             '<circle cx="102" cy="252" r="17" fill="none" stroke="#8a95a1" stroke-width="2"/><text x="102" y="306" text-anchor="middle" class="t-mono">PA</text></g>')
    for (k, lab, t, d, c), (cx, cy) in zip(FLOW, pos):
        g.append(blk(k, lab, t, d, c, cx, cy, cx - 75, cy - 38, 150, 76, 'x32' if k == 'delay' else 'err' if k in ('ganho', 'fader') else ''))
    k, lab, t, d, c = SEND
    g.append(blk(k, lab, t, d, c, 663, 238, 498, 318, 330, 54, 'send'))
    svg = f'<svg viewBox="0 32 1140 344" xmlns="http://www.w3.org/2000/svg" aria-label="O caminho do sinal no canal">{"".join(g)}</svg>'
    return ('<section id="caminho-do-sinal" class="interactive" data-anim="flow"><div class="th"><div class="kicker">Diagrama interativo<div class="legend">'
            '<span style="--c:var(--accent)">Laranja: onde mais se erra</span><span style="--c:var(--x32)">Azul: só X32/M32</span>'
            f'<span class="dvl">{ico("fork", "dvi")}Abordagens divergentes</span>'
            f'<span class="hint">{CURSOR}Clique em um bloco</span></div></div><h3 style="margin-top:6px">O caminho do sinal no canal</h3></div>'
            f'<div class="flowfig">{svg}</div><div class="sfpanel"><span class="in"><b>Clique em um bloco</b> para ver o que ele faz e em que capítulo ele é explicado.</span></div>'
            + notes('<p>Diagrama interativo do caminho do sinal (resumo de 5.1.1). Clique em cada bloco para mostrar a explicação e o link para o capítulo.</p>',
                    ''.join(f'<p><b>{esc(t)}</b> (cap. {c}): {esc(d)}</p>' for _, _, t, d, c in FLOW + [SEND]), extra) + '</section>')

# Valor curto no explorador (revisão 2: a ficha da M32R/M32C saía do painel); o valor completo está nas tabelas 1.1.5 e 1.1.6 (notas).
EXV = {'1 "channel strip" com botão giratório CHANNEL SELECT': '1 channel strip', 'não está na especificação': 'fora da ficha', 'Console compacto montável em rack': 'Compacto, em rack',
       '7/8 no manual de 2015; 15/16 no QSG de 2023': '7/8 ou 15/16', 'aparece no roteamento; confira o conector': 'só no roteamento', '4 knobs + 8 botões × 3 = 36': '36 controles',
       'só um botão SELECT e um LCD pequeno': 'SELECT + LCD', 'P10 TRS para mic dinâmico, sem phantom': 'P10, sem phantom', 'Tipo B: interface 18 × 18 + MIDI': 'interface 18 × 18',
       '17–18 em P10 TRS balanceado': '17–18 em P10', '2 / 2 só na especificação': '2 / 2', 'XLR externo (sem mic interno)': 'XLR externo',
       '4 knobs + 8 botões × 3 bancos = 36': '36 controles', '8 botões × 3 = 24': '24 botões', 'Tipo A: gravador estéreo em pendrive': 'pendrive estéreo',
       'XLR externo com +48 V + mic interno': 'XLR (+48 V) + mic', 'XLR externo + mic interno': 'XLR + mic interno', 'RCA OUT + botão CONTROL ROOM': 'RCA + Control Room',
       'cópias de qualquer entrada 1–12': 'cópias de 1–12', '17–18 em RCA desbalanceado': '17–18 em RCA', 'Console montável em rack': 'Console em rack', 'Aux 5–6 também em RCA': 'Aux 5–6 em RCA'}
EXK = {'Controle local sem faders': 'Controle sem faders', 'Saídas de monitor da técnica': 'Monitor da técnica', 'Efeitos listados no manual': 'Efeitos no manual',
       'Buses que já vêm como subgrupo': 'Buses de subgrupo', 'Saída de monitor de estúdio': 'Monitor de estúdio'}
def explorer_slide(tables):
    data = {}
    for tbl in tables:
        trs = findall(tbl, 'tr'); hdr = [text(c).strip() for c in els(trs[0])]
        for tr in trs[1:]:
            cells = [text(c).strip() for c in els(tr)]
            for j, m in enumerate(hdr[1:], 1):
                k, v = cells[0], cells[j] if j < len(cells) else ''
                k = EXK.get(k) or (depar(k) if len(k) > 24 else k); v = re.sub(r'\s*\(não confirmad[oa]\)', ' *', v); v = EXV.get(v, re.sub(r'\s+', ' ', PAREN.sub('', v)).strip() or v); v = '7/8 ou 15/16' if '15/16' in v else v  # * = não confirmado (legenda no painel)
                data.setdefault(m, []).append([k, v])
    btn = lambda lst, c: ''.join(f'<button class="exm {c}" data-m="{esc(m)}" aria-pressed="false">{esc(m)}</button>' for m in lst if m in data)
    return ('<section id="explorador" class="interactive explorer" data-anim="explorer"><div class="th"><div class="kicker">Explorador interativo<div class="legend">'
            f'<span class="hint">{CURSOR}Clique em uma mesa</span></div></div><h3 style="margin-top:6px">Compare as mesas: clique em uma</h3></div>'
            f'<div class="exsel"><div class="exrow"><span class="fl">X AIR / M AIR</span>{btn(XAIR, "xa")}</div><div class="exrow"><span class="fl">X32 / M32</span>{btn(X32, "xm")}</div></div>'
            '<div class="expanel" aria-live="polite"><div class="exhead"><b class="ex-t">Escolha uma mesa</b><span class="ex-k">Manuais oficiais</span></div><dl class="exgrid"></dl></div>'
            + '<script type="application/json" class="exdata" id="exdata">' + json.dumps(data, ensure_ascii=False).replace('</', '<\\/') + '</script>'
            + notes('<p>Explorador interativo com os dados das tabelas 1.1.5 (X AIR) e 1.1.6 (X32/M32). Clique em uma mesa para ver formato, pré-amps, saídas, USB e demais itens. O texto completo das tabelas está nas notas dos slides 1.1.5 e 1.1.6.</p>') + '</section>')


# ---------------------------------------------------------------- arco do curso: atos, abertura (proposta) e encerramento
ACTS = [(4, "ATO I · PREPARAR A MESA"), (9, "ATO II · AJUSTAR CADA CANAL"), (15, "ATO III · MIXAR PARA O PALCO E A SALA"),
        (22, "ATO IV · GUARDAR, GRAVAR E CRESCER"), (24, "APLICAÇÃO · O DIA DO EVENTO"), (99, "CONSULTA")]
act = lambda cn: next(a for last, a in ACTS if cn <= last)
ACTSEAL = {5: "Ato II: um canal de cada vez", 10: "Ato III: o palco e a sala", 16: "Ato IV: guardar, gravar e crescer", 23: "Aplicação: o dia do evento"}  # selo de troca de ato na abertura do capítulo
ICO = {  # ícones de traço (24×24) dos cartões de ato e da origem de cada bullet
 'plug': '<path d="M9 3v5M15 3v5M6 8h12v3a6 6 0 0 1-12 0zM12 17v4"/>',
 'knob': '<circle cx="12" cy="13" r="7"/><path d="M12 13l3-4M12 3v2M4 6l1.4 1.4M20 6l-1.4 1.4"/>',
 'spk': '<rect x="5" y="3" width="14" height="18" rx="2"/><circle cx="12" cy="14" r="3.5"/><circle cx="12" cy="7" r="1.3"/>',
 'save': '<path d="M5 4h11l3 3v13H5zM8 4v5h8V4M8 20v-6h8v6"/>',
 'book': '<path d="M4 5c3-1.5 6-1.5 8 .5 2-2 5-2 8-.5v14c-3-1.5-6-1.5-8 .5-2-2-5-2-8-.5zM12 5.5v14"/>',
 'fader': '<path d="M7 3v18M17 3v18"/><rect x="4" y="13" width="6" height="4" rx="1"/><rect x="14" y="6" width="6" height="4" rx="1"/>',   # na prática: dois faders na mão
 'fork': '<path d="M12 22v-8"/><path d="M12 14 5 7"/><path d="m12 14 7-7"/><path d="M5 12V7h5"/><path d="M19 12V7h-5"/>',   # bifurcação: um ponto, mais de um caminho correto
}
ico = lambda k, c='ico': f'<svg class="{c}" viewBox="0 0 24 24" aria-hidden="true">{ICO[k]}</svg>'
DVB = f'<span class="dvb">{ico("fork", "dvi")}Abordagens divergentes</span>'   # selo único de "ponto com abordagens diferentes" (README de tools/bespoke, seção 8)
def divg_li(subject, opts, src=''):  # o selo + o assunto + as opções (A, B, C…), sem escolher lado
    o = ''.join(f'<span class="dvo"><i>{chr(65 + k)}</i>{esc(x)}</span>' for k, x in enumerate(opts))
    return f'<li class="fragment divg"{src}>{DVB}<span class="dvt">{esc(subject)}</span>{o}</li>'
ACTCARDS = [('plug', 'Ato I · 01–04', 'Preparar a mesa'), ('knob', 'Ato II · 05–09', 'Ajustar cada canal'),
            ('spk', 'Ato III · 10–15', 'Mixar para o palco e a sala'), ('save', 'Ato IV · 16–22', 'Guardar, gravar e crescer')]
def acts_html(lines=None, attr=''):
    return (f'<div class="acts"{attr}>' + ''.join(f'<div>{ico(i)}<span class="ak">{k}</span><b>{b}</b>' + (f'<small>{lines[j]}</small>' if lines else '') + '</div>'
                                         for j, (i, k, b) in enumerate(ACTCARDS)) + '</div>')
ENCERRAMENTO = ('<section id="encerramento" class="pitch end" data-anim="pitch"><div class="kick">Encerramento</div><h2>O que você leva</h2>'
                + acts_html(['A mesa certa, ligada sem estalo, numa rede que não cai e com cada canal nomeado.',
                             'Ganho no alvo, low cut, EQ, gate e compressor em cada canal.',
                             'Retornos pré-fader, efeitos por envio, DCA e um PA afinado sem microfonia.',
                             'Cenas com safe e backup, gravação multipista, expansão e firmware em dia.'])
                + '<p class="big">Leve o <a href="#/cap-23">roteiro do dia do evento (cap. 23)</a> e consulte <a href="#/cap-25">25</a>, <a href="#/cap-26">26</a> e <a href="#/cap-27">27</a> quando precisar.</p>'
                + notes() + '</section>')


# Repetições que o Agente 12 tirou do slide (o texto continua nas notas): início do item visível, por seção
DROP = {}
RENAME = {}
CUSTOM = {  '10.2.3': ['X AIR, Sends: o ponto do envio.', 'X AIR, Aux Out: pré/pós master.', 'X32/M32: Routing › Out, fonte e tap.', 'Monitor: saída post fader; envios pré.'],
  '14.2.2': ['1. X AIR, em Sends (globo aceso): o bus vira Subgroup.', '2. Ligue os canais ao subgrupo.', '3. No bus, aba Main: LR ligado.', '4. Nos canais: LR desligado (senão, som em dobro).'],
  '3.2.7': ['Ao conectar, o app pergunta: qual direção?', 'Mixer → PC: traz o que está na mesa. Seguro.', 'PC → Mixer: sobrescreve e apaga o show da mesa.', 'PC zerado + PC → Mixer = mesa muda.'],
  '6.2.1': ['Benefícios: menos "lama", vazamento, ronco e plosivas.', 'Bumbo, baixo e tons graves: A corte em ~20–40 Hz · B sem filtro (abordagens divergentes, 6.2.1).', 'Caixa, tons agudos e guitarras: ~100 Hz.', 'Voz: ~80–120 Hz; barítono pede menos.', 'Método: suba o filtro até o som afinar e volte um pouco; alto demais deixa a voz fina.']}
def kw(t):  # bullet escrito à mão "Palavra-chave: ideia": a palavra-chave vai em negrito (DESIGN.md 2: palavra-chave em --ink, o resto em --ink-2)
    m = re.match(r'([^:]{2,30}):\s', t)
    return f'<b>{esc(m.group(1))}</b>: {esc(t[m.end():])}' if m and not re.match(r'\d', t) else esc(t)  # passo numerado ("3. RESET…") fica sem negrito: a lista inteira igual
HPF_BODY = ('<p class="lead-line fragment"><b>Benefícios:</b> menos "lama", vazamento, ronco e plosivas.</p><div class="tbl"><div class="thd">Fonte</div><div class="thd">Corte</div>'
            '<div class="trow fragment divg"><div>Bumbo, baixo e tons graves<small>' + DVB + '</small><span class="dvo"><i>A</i>~20–40 Hz</span><span class="dvo"><i>B</i>sem filtro</span></div><div class="hz">A · B</div></div>'
            '<div class="trow fragment"><div>Caixa, tons agudos e guitarras</div><div class="hz">~100 Hz</div></div>'
            '<div class="trow fragment"><div>Voz<small>barítono pede menos</small></div><div class="hz">~80–120 Hz</div></div></div>'
            '<p class="lead-line fragment"><b>Método:</b> suba o filtro até o som afinar e volte um pouco; alto demais deixa a voz fina.</p>')
# ---------------------------------------------------------------- montagem
def custom_li(x):  # bullet escrito à mão. "[M] " / "[C] " no início = origem (livro = manual, faders = na prática); "[D] Assunto | A | B" = selo de abordagens divergentes
    m = re.match(r'\[(M|C|D)\]\s*', x); k = m.group(1) if m else ''; x = x[m.end():] if m else x
    if k == 'D':
        subject, *opts = [s.strip() for s in x.split('|')]
        return divg_li(subject, opts, ' data-src="D"')
    src = f' data-src="{k}"' if k else ''
    if x.startswith('<'): return x  # bloco pronto (termo, nota, tabela)
    return f'<li class="fragment"{src}>' + kw(x) + '</li>'
SRCI = {'M': ico('book', 'si'), 'C': ico('fader', 'si')}
def srcmark(body, kind):  # ícone de origem no início de cada bullet: o do próprio bullet (data-src) ou o da parte do PDF de onde a seção veio
    def f(m):
        s = re.search(r'data-src="(\w)"', m.group(2)); k = s.group(1) if s else {'pm': 'M', 'pc': 'C'}.get(kind)
        return m.group(0) + SRCI.get(k, '')
    return re.sub(r'<(li|p)(\s[^>]*class="[^"]*fragment[^"]*"[^>]*)>', f, body)
def nextbtn(cn, short=False):  # fim do capítulo: botão para o próximo (o 27 vai para o encerramento); short: só o número (quiz-7, rodapé estreito)
    if cn >= 27: return f'<a class="nextcap" href="#/encerramento">Encerramento {ARR}</a>'
    return f'<a class="nextcap" href="#/cap-{cn + 1}" title="{esc(SHORT[cn + 1])}">Próximo: {cn + 1:02d}{"" if short else " " + esc(SHORT[cn + 1])} {ARR}</a>'
def vtdedup(h):  # título do diagrama que repete o h3 do slide: some (ou fica só o que acrescenta depois de ":" / ",")
    t, v = re.search(r'<h3>(.*?)</h3>', h), re.search(r'<span class="vt">(.*?)</span>', h)
    if not (t and v): return h
    a, c = (html.unescape(re.sub(r'<[^>]+>', '', x.group(1))).strip() for x in (t, v))
    if c.lower() in a.lower(): new = ''
    elif re.match(re.escape(a) + r'\s*[:,]\s*', c, re.I): new = c[len(a):].lstrip(' :,'); new = new[:1].upper() + new[1:]
    else: return h
    return h.replace(v.group(0), f'<span class="vt">{esc(new)}</span>', 1)
# bloco único de "Abordagens divergentes" nas notas: notes/*.html escrevem <div class="divn">; o estilo vai inline porque a janela do apresentador não carrega o CSS do deck
DIVN = ('<div class="divn" style="background:#2b1806;border:1px dashed #ff9a2e;border-left:4px solid #ff9a2e;border-radius:4px;padding:6px 10px;margin:0 0 8px;color:#ffd9a8">')
def hooknotes(h):  # tools/notes/<id>.html substitui a nota gerada
    h = hookbsp(vtdedup(h))
    sid = re.match(r'<section id="([^"]+)"', h).group(1); f = f'{NOTES_DIR}/{sid}.html'
    if not os.path.exists(f): return h
    n = '<aside class="notes">' + open(f, encoding='utf-8').read().strip().replace('<div class="divn">', DIVN) + '</aside>'
    if '<aside class="notes">' in h: return re.sub(r'<aside class="notes">.*?</aside>', lambda m: n, h, count=1, flags=re.S)
    a, _, b = h.rpartition('</section>'); return a + n + '</section>' + b

ROOT = find(p.root, 'body') or p.root
tops = [k for k in ROOT.kids if isinstance(k, N)]
cover = next(k for k in tops if 'cover' in k.cls()); chapters = [k for k in tops if 'chapter' in k.cls()]
ORDER = CFG['ORDER']; SHORT = CFG['SHORT']
ACTNO = lambda cn: 1 if cn <= 4 else 2 if cn <= 9 else 3 if cn <= 15 else 4 if cn <= 22 else 5 if cn <= 24 else 6  # 6 = consulta: os 5 atos já passaram
ACTBAR = '<ol class="actbar" aria-hidden="true">' + ''.join(f'<li><i><b></b></i>{a}</li>' for a in ('Ato I', 'Ato II', 'Ato III', 'Ato IV', 'Evento')) + '</ol>'
SIG = '<svg class="sigline" viewBox="0 0 1280 170" aria-hidden="true"><path class="sig" fill="none" stroke="#ff9a2e" stroke-opacity=".55" stroke-width="2.2"/>'

keep = lambda h: not ONLY or re.match(r'<section id="([^"]+)"', h).group(1) in ONLY  # --only: todo slide tem id
S = []
# capa
S.append('<section id="capa" class="cover" data-anim="cover" data-state="is-cover">'
         '<div class="cv-top"><div class="kick">Behringer e Midas · curso avançado de mesas digitais</div><h1><span class="hl">X AIR</span> · M AIR<br>X32 · M32</h1>'
         '<p class="csub">13 mesas, 2 famílias, um só método: os manuais oficiais e a prática de operação, do primeiro cabo ao show.</p></div>'
         f'<div class="cv-meta">{chips(", ".join(XAIR + X32))}<p class="cfoot">Curso independente · não oficial</p></div>'
         '<svg class="console" viewBox="0 0 1280 300" aria-hidden="true"></svg>' + notes() + '</section>')
# sumário: uma página, uma coluna por ato (título curto; o completo no tooltip)
CAPT = {int(ch.attrs['id'].split('-')[1]): CFG['CAPTITLE'].get(int(ch.attrs['id'].split('-')[1]), text(find(find(ch, 'h2'), 'span', 'ht')).strip()) for ch in chapters}
TOCCOLS = [('Ato I · Preparar', range(1, 5)), ('Ato II · Cada canal', range(5, 10)), ('Ato III · Palco e sala', range(10, 16)), ('Ato IV · Guardar', range(16, 23))]
tocl = lambda n: f'<a href="#/cap-{n}" title="{esc(CAPT[n])}"><span class="tn">{n:02d}</span><span class="tt">{esc(SHORT[n])}</span></a>'
toc_cols = ''.join(f'<div class="col"><p class="actl">{g}</p>' + ''.join(tocl(n) for n in r) + '</div>' for g, r in TOCCOLS)
toc_row = '<p class="actl" style="grid-column:span 2">Aplicação · O dia do evento</p><p class="actl" style="grid-column:span 3">Consulta</p>' + ''.join(tocl(n) for n in range(23, 28))
S.append('<section id="sumario" class="toc" data-anim="toc"><div class="kicker">Sumário<span class="tc-hint">clique para ir ao capítulo</span></div>'
         f'<h2>27 capítulos, na ordem em que a mesa é usada</h2><div class="chlist c4">{toc_cols}</div><div class="chlist tocrow">{toc_row}</div>{notes()}</section>')
# como usar: legenda dos sinais que aparecem nos slides
CTA = ('Para mais manuais interativos de outras mesas, cursos completos em vídeo, cursos completos presenciais, turmas, mentorias individuais e muito mais, '
       'acesse loredoborges.com.br ou entre em contato pelo número: (31) 97318-0752.')   # texto exato pedido pelo dono do curso
HOWTO = [(f'<span class="sw si2">{ico("book", "si")}Manual</span>', 'Menus, botões e números de referência, do manual oficial.'),
         (f'<span class="sw si2">{ico("fader", "si")}Na prática</span>', 'Como se opera: valores de partida, dicas e erros comuns.'),
         ('<span class="sw chips"><span class="chip xa">XR18</span><span class="chip xm">X32 ·6</span></span>', 'As mesas em que aquilo vale.'),
         (f'<span class="sw">{DVB}</span>', 'Mais de um jeito correto: todas as opções, sem escolher lado.'),
         ('<span class="sw wsym">⚠</span>', 'Muda com a unidade ou o firmware: confira na sua mesa.'),   # N15: mesmo sentido da legenda do PDF
         ('<span class="sw tbox">Termo</span>', 'Borda laranja: termo técnico explicado na primeira vez.')]
S.append('<section id="como-usar" class="howto" data-anim="howto"><div class="kicker">Antes de começar</div><h2>Como ler os slides</h2><div class="hlegend">'
         + ''.join(f'<div class="lg">{a}<div>{b}</div></div>' for a, b in HOWTO) + '</div>'
         '<div class="hnames"><p><b>M32</b> inclui a M32 LIVE; <b>M32R</b>, a M32R LIVE.</p>'
         '<p><b>O que vale</b> para uma mesa vale para as irmãs.</p></div>'   # N15: o aviso de firmware virou a linha do ⚠ na legenda
         
         f'{notes()}</section>')

GPAGES = (('A–F', 'abcdef'), ('G–P', 'ghijklmnop'), ('Q–Z', 'qrstuvwxyz'))
def glossary_slide(num, tit, mz, blocks):  # um slide, três abas; a definição aparece no visor
    rows = sorted([[text(c).strip() for c in els(tr)] for b in blocks if isinstance(b, N) for t in ([b] if b.tag == 'table' else findall(b, 'table')) for tr in findall(t, 'tr')[1:]], key=lambda r: r[0].lower())
    grp = lambda r: next(i for i, (_, ls) in enumerate(GPAGES) if (re.sub(r'[^a-z0-9]', '', r[0].lower()) or 'a')[0] in ls + ('0123456789' if i == 0 else ''))
    tabs = ''.join(f'<button class="gtab{" on" if i == 0 else ""}" data-g="{i}">{k} · {sum(grp(r) == i for r in rows)}</button>' for i, (k, _) in enumerate(GPAGES))
    keys = ''.join(f'<button class="gterm" data-g="{grp(r)}"{"" if grp(r) == 0 else " hidden"} data-d="{html.escape(r[1] if len(r) > 1 else "", quote=True)}">{esc(r[0])}</button>' for r in rows)
    return (f'<section id="s{num.replace(".", "-")}" class="gloss" data-anim="gloss"><div class="lc"><div class="th"><div class="kicker"><span>Glossário · {len(rows)} termos</span></div>'
            f'</div><div class="gtabs">{tabs}</div><div class="gvisor" aria-live="polite"><b class="gv-t">Escolha um termo</b><p class="gv-d">Clique numa tecla ao lado: a definição aparece aqui.</p></div></div>'
            f'<div class="gkeys" style="--cols:5">{keys}</div>{notes()}</section>')

for ch in chapters:
    cid = ch.attrs['id']; cn = int(cid.split('-')[1])
    if cn not in ORDER: continue  # cap. 00: o útil foi para "como usar"
    want = set(ORDER[cn]); B = {}
    op = find(ch, 'div', 'opener'); h2 = find(op, 'h2'); _, tit, mz = head(h2); tit = CAPT[cn]
    label = text(find(op, 'div', 'chap-label')); nn = label.replace('CAPÍTULO', '').strip()
    osv = bsp(cid)  # tools/bespoke/cap-N.svg: motivo do capítulo entre o número e a barra de atos
    B[cid] = (f'<section id="{cid}" class="opener" data-anim="opener" data-act="{ACTNO(cn)}"><div class="op-main"><div class="clabel">{esc(label)} <span class="act">· {act(cn)}</span></div><h2>{esc(tit)}</h2>{chips(mz)}'
              f'<p class="promise">{esc(CFG["PROMISE"][cn])}</p></div>'
              + f'<div class="op-side{" has-bsp" if osv else ""}" aria-hidden="true">'
              + f'<div class="bignum"><span class="n-dim">{nn}</span><span class="n-lit"><span>{nn}</span></span></div>'
              + (f'<div class="bsp op-bsp">{dg(osv, False)[1]}</div>' if osv else '') + f'{ACTBAR}</div>'
              + SIG + '<circle class="sigdot" r="7" fill="#ffd9a8"/><circle class="sighalo" r="18" fill="#ff9a2e" fill-opacity=".25"/></svg>' + notes() + '</section>')
    # seções h3/h4: cada h4 vira um slide; o que vem entre h3 e o 1º h4 entra no slide desse h4
    secs, part = [], None
    for k in ch.kids:
        if not isinstance(k, N) or k is op or (k.tag == 'blockquote' and 'fecha' in k.cls()): continue
        if k.tag == 'h3': part = k; secs.append({'h4': k, 'part': k, 'pre': [], 'blocks': [], 'h3': True})
        elif k.tag == 'h4':
            pre = []
            if secs and secs[-1].get('h3'): h = secs.pop(); pre = [h['h4']] + h['blocks']
            secs.append({'h4': k, 'part': part, 'pre': pre, 'blocks': []})
        elif secs: secs[-1]['blocks'].append(k)
        else: raise SystemExit(f'bloco sem seção em {cid}')
    def kind(s):
        pt = text(find(s['part'], 'span', 'ht')) if s['part'] else ''
        return 'pm' if 'manual' in pt else 'pc' if 'prática' in pt else ''
    if 'explorador' in want:
        B['explorador'] = explorer_slide([find(b, 'table') for s in secs if head(s['h4'])[0] in ('1.1.5', '1.1.6') for b in s['blocks'] if isinstance(b, N) and find(b, 'table')])
    if 'caminho-do-sinal' in want: B['caminho-do-sinal'] = flow_slide()
    for s in secs:
        num, st, mz = head(s['h4']); sid = f's{num.replace(".", "-")}'
        if sid not in want: continue
        pre_n = [x for x in s['pre'] if isinstance(x, N)]
        if 'glossary' in ch.cls():
            B[sid] = glossary_slide(num, st, mz, [b for s_ in secs for b in s_['blocks']]); continue  # um slide só, com os termos de todas as seções do capítulo
        hw = nw(f"{num} {st} {re.sub('<[^>]+>', ' ', chips(mz))}")  # palavras do cabeçalho do slide
        if num in CFG['BULLETS']: body_html = wrap([custom_li(x) for x in CFG['BULLETS'][num]])
        elif num in CUSTOM: body_html = wrap([x if x.startswith('<') else f'<li class="fragment">{kw(x)}</li>' for x in CUSTOM[num]])
        else: body_html = best_summary([x for x in pre_n if x.tag != 'h3'] + s['blocks'], max(MINB, SLIDE_W - hw), DROP.get(num, ()))
        for a, b in RENAME.get(num, ()): body_html = body_html.replace(a, b)
        body_html = srcmark(stepkeys(num, body_html), kind(s))
        th = f'<h3>{esc(st)}</h3>'
        if num == '24.2.1':  # rodada 6: sete erros e o conserto em duas colunas; cada linha entra vermelha e o conserto acende em verde (CSS .errfix)
            rows = ''.join(f'<div class="efrow fragment" data-i="{i}"><div class="bad"><span class="efx">✕</span>{esc(e)}</div><div class="fix"><span class="efx">✓</span>{esc(c)}'
                           + (f'<span class="efc">cap. {n[0]}</span>' if n else '') + '</div></div>'
                           for i, (e, c, *n) in enumerate(CFG['ERRFIX'], 1))  # checklist P16: o capítulo onde cada erro é ensinado
            B[sid] = (f'<section id="{sid}" class="topic errfix" data-anim="errfix"><div class="th">{th}{chips(mz)}</div>'
                      f'<div class="eftbl"><div class="efh"><span>O erro</span><span>Faça assim</span></div>{rows}</div>{notes()}</section>'); continue
        if sid == 's26-2-1':  # fechamento do curso: o próximo passo (texto exato do dono do curso), sem fontes externas
            B[sid] = (f'<section id="{sid}" class="pitch cta" data-anim="pitch"><div class="kick">Onde estudar · o próximo passo</div><h2>{esc(st)}</h2>'
                      f'<p class="big ctatext">{CTA}</p>'
                      '<div class="ctaband"><div class="ctacard"><span class="ck">Site</span><b>loredoborges.com.br</b></div>'
                      '<div class="ctacard"><span class="ck">Contato</span><b>(31) 97318-0752</b></div></div>' + notes() + '</section>'); continue
        if num == '6.2.1':  # gráfico feito à mão (DESIGN.md 2.4): cada linha da tabela muda o corte
            B[sid] = (f'<section id="{sid}" class="topic tab" data-anim="hpf"><div class="th">{th}{chips(mz)}</div>'
                      f'<div class="lc">{srcmark(HPF_BODY, kind(s))}</div><div class="viz"><svg class="hpf" viewBox="0 0 514 530" role="img" aria-label="Low Cut (HPF): uma rampa"></svg></div>{notes()}</section>'); continue
        nrows = sum(len(findall(t, 'tr')) - 1 for b in s['blocks'] if isinstance(b, N) for t in ([b] if b.tag == 'table' else findall(b, 'table')))
        tabs = [[[text(c).strip() for c in els(tr)] for tr in findall(t, 'tr')] for b in s['blocks'] if isinstance(b, N) for t in ([b] if b.tag == 'table' else findall(b, 'table'))]
        dk = CFG['DIAG'].get(sid)
        if isinstance(dk, str) and dk.startswith('bespoke:'): vz, bsp_ = open(BESPOKE[dk[8:]], encoding='utf-8').read(), True
        elif dk: k_, a_ = dk if isinstance(dk, tuple) else (dk, {}); vz, bsp_ = VIZ['D'][k_](**a_), False
        elif sid in BESPOKE: vz, bsp_ = bsp(sid), True
        else: vz, bsp_ = VIZ['viz'](cn, st, num, nrows, tabs, [text(li).strip() for b in s['blocks'] if isinstance(b, N) for li in findall(b, 'li')]), False
        assert vz, f'tópico sem diagrama: {num}'
        B[sid] = f'<section id="{sid}" class="topic diag{" dwide" if sid in CFG.get("WIDE", ()) else ""}" data-anim="diag"><div class="lc"><div class="th">{th}{chips(mz)}</div><div class="body">{body_html}</div></div>{carcass(vz, crop=not bsp_)}{notes()}</section>'
    if cn in QUIZ:
        q, opts, ans, ex = QUIZ[cn]
        opts = [o for i, o in enumerate(opts) if i != ans]; ans = cn % 3; opts.insert(ans, QUIZ[cn][1][QUIZ[cn][2]])  # resposta certa gira entre A, B e C
        th = f'<div class="th"><div class="kicker">Quiz · {esc(label.title())}</div><h3>{esc(q)}</h3></div>'
        ob = f'<div class="opts" data-ans="{ans}">' + ''.join(f'<button>{esc(o)}</button>' for o in opts) + '</div>'
        if cn == 7:  # gate feito à mão (DESIGN.md 2.5): threshold, agulha varre, vazamento atenuado
            B[f'quiz-{cn}'] = (f'<section id="quiz-{cn}" class="quiz gatequiz" data-anim="quizgate">{th}<div class="lc">{ob}<p class="fb" hidden>{esc(ex)}</p><div class="qfoot"><p class="reset">Clique em uma alternativa.</p>{nextbtn(cn, True)}</div></div>'
                               f'<div class="viz"><svg class="gate" viewBox="0 0 480 636" role="img" aria-label="Gate: quando ele abre?"></svg></div>{notes()}</section>')
        elif qsv := bsp(f'quiz-{cn}'):  # tools/bespoke/quiz-N.svg: painel do diagrama à direita (carcaça sem teclas); o .js anima PERGUNTA → RESPOSTA   # motion total: o botão mantém o nome do próximo capítulo (texto visível igual ao de antes)
            B[f'quiz-{cn}'] = (f'<section id="quiz-{cn}" class="quiz bspq" data-anim="quizw">{th}<div class="lc">{ob}<p class="fb" hidden>{esc(ex)}</p><div class="qfoot"><p class="reset">Clique em uma alternativa.</p>{nextbtn(cn)}</div></div>'
                               f'{carcass(qsv, "", False)}{notes()}</section>')
        else:  # sem diagrama: pergunta e alternativas em largura cheia
            B[f'quiz-{cn}'] = (f'<section id="quiz-{cn}" class="quiz wide" data-anim="quizw">{th}<div class="lc">{ob}<p class="fb" hidden>{esc(ex)}</p>'
                               f'<div class="qfoot"><p class="reset">Clique em uma alternativa.</p>{nextbtn(cn)}</div></div>{notes()}</section>')
    elif cn >= 25:  # caps. 25–27: o botão vai no último slide do capítulo
        last = ORDER[cn][-1]; B[last] = B[last].replace('<aside class="notes">', f'{nextbtn(cn)}<aside class="notes">', 1)
    miss = [i for i in ORDER[cn] if i not in B]
    if miss: raise SystemExit(f'cap. {cn}: ids do ORDER sem slide: {miss}')
    V = [hooknotes(B[i]) for i in ORDER[cn] if keep(B[i])]
    if cn == 27 and keep(ENCERRAMENTO): V.append(hooknotes(ENCERRAMENTO))
    if V: S.append('<section>' + ''.join(V) + '</section>')
S = [x if x.startswith('<section>') else hooknotes(x) for x in S]

tpl = open(f'{TOOLS}/slides_template.html', encoding='utf-8').read()
S = [x for x in S if x.startswith('<section>') or keep(x)]
ids = set(re.findall(r'<section id="([^"]+)"', '\n'.join(S)))
if ONLY - ids: print('--only: ids que não existem:', ', '.join(sorted(ONLY - ids)))
# tools/bespoke/_padrao.js: padrão de motion comum a todos os slides (easings, peças), carregado antes dos .js de cada slide
PAD = f'{TOOLS}/bespoke/_padrao.js'
JS = (f'<script>/* tools/bespoke/_padrao.js */\n{open(PAD, encoding="utf-8").read()}</script>\n' if os.path.exists(PAD) else '') + ''.join(f'<script>/* tools/bespoke/{i}.js */\n{open(f"{TOOLS}/bespoke/{i}.js", encoding="utf-8").read()}</script>\n'
             for i in sorted(ids) if os.path.exists(f'{TOOLS}/bespoke/{i}.js') and i not in CFG['DIAG'])  # diagrama trocado no enxugamento: o JS sob medida antigo não vale
out = tpl.replace('<!--DEFS-->', DARK_DEFS).replace('<!--SLIDES-->', '\n'.join(S)).replace('<!--BESPOKE-->', JS)
rel = os.path.relpath(DECK, os.path.dirname(os.path.abspath(OUT)))
if rel != '.':  # prévia fora de 07-slides: lib/ e fonts/ continuam vindo de 07-slides
    out = re.sub(r'((?:src|href)=")lib/', lambda m: f'{m.group(1)}{rel}/lib/', out).replace('url(fonts/', f'url({rel}/fonts/')
def nobreak(h):  # rodada 3 (26/3): "Mapa MIDI das X AIR / M" + "AIR" e "X-" + "TOUCH" quebravam a linha
    parts, skip = re.split(r'(<[^>]+>)', h), []
    for i, x in enumerate(parts):
        m = re.match(r'<(/?)(aside|svg|script|style)\b', x)
        if m: skip.append(m.group(2)) if not m.group(1) else skip.pop() if skip else None; continue
        if not skip and x and not x.startswith('<'):
            parts[i] = re.sub(r'\b([XM]) AIR\b', '\\1\u00a0AIR', x)
            parts[i] = re.sub(r'\bX-(TOUCH|Touch)\b', '<span class="nw">X-\\1</span>', parts[i])
            parts[i] = re.sub(r'(\d) (°C|p\.|dBFS|dBu|dBV|LUFS|dB|ms|kHz|Hz|GB|MB)(?!\w)', '\\1\u00a0\\2', parts[i])  # rodada 2: número e unidade na mesma linha
            parts[i] = re.sub(r'\b([XM]32-(?:Edit|Mix)|[XM]-AIR Edit|pré-amps?\b|X-USB|X-Live|DN32-(?:USB|LIVE)|P16-[MD]\b)', '<span class="nw">\\1</span>', parts[i])  # rodada 2: "X32-" + "Edit" e "pré-" + "amps" quebravam
    return ''.join(parts)
out = nobreak(out)
open(OUT, 'w', encoding='utf-8').write(out)
print('slides:', len(re.findall(r'<section id=', out)), '→', OUT)
