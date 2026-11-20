# Confere as notas do apresentador do deck (política em tools/notes/README.md).
# Uso: python3 -I check_notes.py <slides/index.html> [-v]      |   python3 -I check_notes.py --selftest
# Acusa, por slide:
#   VAZIA     nota sem texto;
#   REPETE    nota que repete o slide: mais de 35% das trincas de palavras da nota estão no texto visível ou no diagrama,
#             ou uma frase da nota (6+ palavras) está 80% contida nele;
#   PROIBIDO  "Em cena", X16/X12, "Texto do diagrama", roteiro/metacomentário de produção.
# A regra antiga ("as notas contêm todo o texto do PDF") deixou de valer: a nota complementa o slide, não o copia.
# Sai com código 1 se achar algum problema.
import re, sys, unicodedata
from html.parser import HTMLParser

LIMIT, SENT_LIMIT = .35, .8
BANNED = re.compile(r'\bem cena\b|\bx16\b|"x12"|\bx12\b(?![0-9])|texto do diagrama|roteiro do apresentador|pesquisa d[ao] |resumo de busca|agentes? de|'
                    r'03-pesquisa|01-manuais|\(lacuna\)|lista do curso|lista original|apelido|hist[óo]ria fict[íi]cia|\bana\b', re.I)

def words(t):
    t = unicodedata.normalize('NFKC', t).lower()
    return re.findall(r'\w+', t)
def tri(ws): return {tuple(ws[i:i + 3]) for i in range(len(ws) - 2)}

class Deck(HTMLParser):
    def __init__(s):
        super().__init__(convert_charrefs=True); s.slides, s.stack = [], []
    def handle_starttag(s, t, a):
        if t in ('br', 'img', 'hr', 'meta', 'link', 'input', 'wbr', 'col', 'circle', 'rect', 'line', 'path', 'polyline', 'polygon', 'use'): return
        a = dict(a); kind = None
        if t == 'section' and a.get('id'): kind = 'slide'; s.slides.append({'id': a['id'], 'vis': [], 'notes': []})
        elif t == 'aside' and 'notes' in (a.get('class') or ''): kind = 'notes'
        elif t in ('script', 'style'): kind = 'skip'
        s.stack.append((t, kind))
    def handle_endtag(s, t):
        for i in range(len(s.stack) - 1, -1, -1):
            if s.stack[i][0] == t: del s.stack[i:]; break
    def handle_data(s, d):
        kinds = [k for _, k in s.stack]
        if 'skip' in kinds or 'slide' not in kinds: return
        cur = next(x for x in reversed(s.slides))
        (cur['notes'] if 'notes' in kinds else cur['vis']).append(d)

def check(html):
    d = Deck(); d.feed(html); out = []
    for sl in d.slides:
        vis, note = ' '.join(sl['vis']), ' '.join(sl['notes'])
        nw = words(note)
        if not nw: out.append((sl['id'], 'VAZIA', '')); continue
        vt, nt = tri(words(vis)), tri(nw)
        share = len(nt & vt) / len(nt) if nt else 0
        if share > LIMIT: out.append((sl['id'], 'REPETE', f'{share:.0%} das trincas da nota estão no slide'))
        for sent in re.split(r'(?<=[.!?])\s+', note):
            st = tri(words(sent))
            if len(words(sent)) >= 6 and st and len(st & vt) / len(st) >= SENT_LIMIT:
                out.append((sl['id'], 'REPETE', f'frase copiada do slide: "{sent.strip()[:90]}"'))
        m = BANNED.search(note)
        if m: out.append((sl['id'], 'PROIBIDO', f'"{m.group(0)}" na nota'))
    return d.slides, out

def selftest():
    deck = ('<section id="a"><h3>Ganho</h3><li>Média perto de −18 dBFS, picos 3 a 6 dB acima.</li>'
            '<aside class="notes"><p>Média perto de −18 dBFS, picos 3 a 6 dB acima.</p></aside></section>'
            '<section id="b"><h3>Ganho</h3><li>Média perto de −18 dBFS.</li><aside class="notes"><p>No digital, 0 dBFS é o teto; o VU analógico ainda tem folga.</p></aside></section>'
            '<section id="c"><h3>X</h3><aside class="notes"></aside></section>'
            '<section id="d"><h3>X</h3><aside class="notes"><p>Em cena: domingo às 10 horas.</p></aside></section>')
    _, out = check(deck); got = {(i, k) for i, k, _ in out}
    assert ('a', 'REPETE') in got and not any(i == 'b' for i, _ in got) and ('c', 'VAZIA') in got and ('d', 'PROIBIDO') in got, out
    print('selftest ok')

if __name__ == '__main__':
    if '--selftest' in sys.argv: selftest(); sys.exit(0)
    slides, out = check(open(sys.argv[1], encoding='utf-8').read())
    for i, k, m in out: print(f'{k:9} {i}: {m}')
    print(f'slides: {len(slides)} | problemas: {len(out)}')
    sys.exit(1 if out else 0)
