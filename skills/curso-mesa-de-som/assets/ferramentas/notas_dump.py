# Gera o dump para leitura dos revisores: id, texto visível (coluna HTML e diagrama SVG) e nota de cada slide.
# Uso: python3 -I notas_dump.py <slides/index.html> <saida.md>
import os, re, runpy, sys
from html.parser import HTMLParser

VOID = {'br', 'img', 'hr', 'meta', 'link', 'input', 'wbr', 'col', 'circle', 'rect', 'line', 'path', 'polyline', 'polygon', 'use', 'stop', 'ellipse'}

class Deck(HTMLParser):
    def __init__(s):
        super().__init__(convert_charrefs=True); s.slides, s.stack = [], []
    def handle_starttag(s, t, a):
        if t in VOID: return
        a = dict(a); kind = None
        if t == 'section' and a.get('id'): kind = 'slide'; s.slides.append({'id': a['id'], 'html': [], 'svg': [], 'notes': []})
        elif t == 'aside' and 'notes' in (a.get('class') or ''): kind = 'notes'
        elif t in ('script', 'style'): kind = 'skip'
        elif t == 'svg': kind = 'svg'
        s.stack.append((t, kind))
    def handle_endtag(s, t):
        for i in range(len(s.stack) - 1, -1, -1):
            if s.stack[i][0] == t: del s.stack[i:]; break
    def handle_data(s, d):
        kinds = [k for _, k in s.stack]
        if 'skip' in kinds or 'slide' not in kinds or not d.strip(): return
        cur = s.slides[-1]
        if 'notes' in kinds: cur['notes'].append(d.strip())
        elif 'svg' in kinds: cur['svg'].append(d.strip())
        else: cur['html'].append(d.strip())

d = Deck(); d.feed(open(sys.argv[1], encoding='utf-8').read())
assert d.slides, 'nenhum slide encontrado'
# a faixa do diagrama só aparece em execução: vem dos passos do plano
# cada curso reescreve enxugamento.py: plano em outro formato só deixa a faixa vazia, não derruba o dump
try:
    PLAN = runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'enxugamento.py'))
    FAIXAS = {p['id']: [st['txt']['msg'] for st in p.get('inst', {}).get('steps', []) if st.get('txt', {}).get('msg')] for p in PLAN['SLIDES']}
except Exception as e:
    print('aviso: faixa por passo indisponível (' + type(e).__name__ + ')', file=sys.stderr); FAIXAS = {}
out = [f'# Dump do deck: {len(d.slides)} telas\n']
for s in d.slides:
    svg = list(dict.fromkeys(s['svg']))  # o diagrama repete rótulos (pente, escala): basta uma vez
    out += [f"## {s['id']}\n", '**Texto:** ' + ' | '.join(s['html']) + '\n', '**Diagrama:** ' + ' · '.join(svg) + '\n', '**Faixa por passo:** ' + ' · '.join(FAIXAS.get(s['id'], [])) + '\n', '**Nota:** ' + re.sub(r'\s+', ' ', ' '.join(s['notes'])) + '\n']
open(sys.argv[2], 'w', encoding='utf-8').write('\n'.join(out))
print(sys.argv[2], len(d.slides), 'slides')
