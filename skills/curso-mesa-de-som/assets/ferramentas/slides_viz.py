# Mini-diagramas SVG próprios para os slides (desenhados aqui, sem figuras dos manuais).
# Carregado por build_slides.py via runpy. viz(cap, titulo) devolve um <svg> escolhido pelo título
# (regras REGRAS, na ordem) ou, sem regra, o diagrama-tema do capítulo (TEMA).
import html, re
E = lambda s: html.escape(str(s), quote=True)

def T(x, y, s, c='', a='middle'):
    return f'<text x="{x}" y="{y}" text-anchor="{a}" class="{c}">{E(s)}</text>'
def B(x, y, w, h, s='', c='bx', tc='b'):
    ls = s.split('\n') if s else []
    y0 = y + h / 2 + 5 - (len(ls) - 1) * 9
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="7" class="{c}"/>' + ''.join(T(x + w / 2, y0 + i * 18, l, tc) for i, l in enumerate(ls))
def B2(x, y, w, h, s='', c='bx', tc='bb'):  # rodada 4: caixa com letra grande (1ª linha bb, as outras bs), para nós que precisam de 28 px na tela
    ls = s.split('\n') if s else []; lh = 24
    y0 = y + h / 2 + 7 - (len(ls) - 1) * lh / 2
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" class="{c}"/>' + ''.join(T(x + w / 2, y0 + i * lh, l, tc if i == 0 else 'bs') for i, l in enumerate(ls))
def L(x1, y1, x2, y2, c='ln'): return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="{c}"/>'
def P(d, c): return f'<path d="{d}" class="{c}"/>'
def C(x, y, r, c): return f'<circle cx="{x}" cy="{y}" r="{r}" class="{c}"/>'
def svg(title, body, h=320):
    return (f'<svg viewBox="0 0 400 {h}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{E(title)}">'
            + T(200, 20, title, 'vt') + body + '</svg>')
def axes(x0=40, y0=260, x1=385, y1=45, xl='frequência →', yl='nível'):
    g = ''.join(L(x0, y, x1, y, 'grid') for y in range(y1 + 20, y0, 50))
    return g + L(x0, y0, x1, y0, 'axis') + L(x0, y0, x0, y1, 'axis') + T(x1, y0 + 20, xl, 'sm', 'end') + T(x0 - 4, y1 - 6, yl, 'sm', 'start')
def fader(x, y, h, pos, cap='cap'):
    return f'<rect x="{x - 3}" y="{y}" width="6" height="{h}" rx="3" class="track"/><rect x="{x - 13}" y="{y + pos - 7}" width="26" height="14" rx="3" class="{cap}"/>'
def X(x, y): return T(x, y + 6, '✕', 'xr')
def OK(x, y): return f'<text x="{x}" y="{y + 6}" text-anchor="middle" class="ok">✓</text>'

TAGS = re.compile(r'<(rect|text|line|path|circle|polygon|polyline)\b')
def S(k, *xs):  # peças que acendem junto com o k-ésimo bullet da seção (data-step; 0 = desenho principal, aceso na entrada)
    x = ''.join(xs)
    return TAGS.sub(lambda m: f'<{m.group(1)} data-step="{k}"', x) if k else x
def O(k, *xs):  # destaque que só aparece enquanto o k-ésimo bullet é o atual (data-only)
    return TAGS.sub(lambda m: f'<{m.group(1)} data-step="{k}" data-only="1"', ''.join(xs))
def F(*xs):  # peça só do 1º slide da seção; na continuação ela some e o diagrama se ajusta ao resto (data-first)
    return TAGS.sub(lambda m: f'<{m.group(1)} data-first="1"', ''.join(xs))
def Q(*xs):  # quiz: peça que entrega a resposta; fica invisível (opacity 0) até a escolha (data-q)
    return TAGS.sub(lambda m: f'<{m.group(1)} data-q="1"', ''.join(xs))
def QT(x): return x.replace('<text ', '<text data-q="1" ')  # quiz: só o texto da peça some; a caixa fica (silhueta)
def qa(q): return Q if q else (lambda *xs: ''.join(xs))
def HL(x, y, w, h, k):  # moldura laranja em volta da peça de que o bullet k fala
    return O(k, f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="9" class="hl"/>')

# ---- moldes reutilizados por vários diagramas próprios (revisão 2: um diagrama por assunto, cada bullet acende a sua parte)
def pairs(title, rows, heads=None, foot='', h=300, steps=True, rhmax=58):
    """Linhas "esquerda → direita" (erro → correção, antigo → novo, nome → equivalente).
    rows: (esquerda, direita, classe_esq, classe_dir, meio); meio = '' desenha seta, senão o texto (=, ≈, ✕…)."""
    y0 = 40 if not heads else 62; n = len(rows); room = (h - 30 - y0) if not foot else (h - 52 - y0)
    rh = min(rhmax, room / n - 10); gap = (room - n * rh) / max(1, n)
    g = ''
    if heads: g += T(95, 50, heads[0], 'zl') + T(305, 50, heads[1], 'zl')
    for i, r in enumerate(rows):
        l, rr, lc, rc, mid = list(r) + [None, None, 'bxr', 'bxg', ''][len(r):]
        y = y0 + i * (rh + gap); cy = y + rh / 2
        part = B(10, y, 170, rh, l, lc) + B(220, y, 170, rh, rr, rc)
        part += L(182, cy, 216, cy, 'ln') if not mid else T(200, cy + 7, mid, 'mid')
        g += S(steps[i] if isinstance(steps, tuple) else i + 1 if steps else 0, part)  # steps: tupla = bullet de cada linha
    if foot: g += T(200, h - 14, foot, 'sm')
    return svg(title, g, h)
def checks(title, items, foot='', h=300, steps=True, hi=None):
    """Lista de verificação: caixa marcada + texto curto por linha; cada linha acende com o seu bullet."""
    n = len(items); rh = min(50, (h - 70 - (24 if foot else 0)) / n)
    g = f'<rect x="10" y="34" width="380" height="{n * rh + 18:.0f}" rx="10" class="panel"/>'
    for i, it in enumerate(items):
        y = 44 + i * rh; c = 'bxo' if hi is not None and i == hi else 'bxg'
        g += S(i + 1 if steps else 0, f'<rect x="24" y="{y + rh / 2 - 13:.0f}" width="26" height="26" rx="4" class="{c}"/>', OK(37, y + rh / 2 - 6), T(62, y + rh / 2 + 6, it, 'b', 'start'))
    if foot: g += T(200, h - 12, foot, 'sm')
    return svg(title, g, h)
def flow(title, items, foot='', h=310, steps=None):
    """Passo a passo numerado, de cima para baixo; steps[i] = bullet que acende o passo i (padrão: i + 1)."""
    n = len(items); rh = min(46, (h - 60 - (26 if foot else 0)) / n - 12)
    g = ''
    for i, it in enumerate(items):
        y = 38 + i * (rh + 12); k = (steps or list(range(1, n + 1)))[i]
        part = f'<circle cx="34" cy="{y + rh / 2:.0f}" r="16" class="bxo"/>' + T(34, y + rh / 2 + 6, str(i + 1), 'num') + B(60, y, 330, rh, it, 'bx')
        if i < n - 1: part += L(34, y + rh / 2 + 17, 34, y + rh + 12 + rh / 2 - 17, 'ln')
        g += S(k, part)
    if foot: g += T(200, h - 12, foot, 'lbl')
    return svg(title, g, h)
def grid3(title, heads, rows, foot='', h=310, steps=True, rhmax=48):
    """Tabela-desenho de 3 colunas: rótulo | coluna A | coluna B (B vazio = linha que vale para as duas)."""
    n = len(rows); rh = min(rhmax, (h - 70 - (26 if foot else 0)) / n)
    hd = lambda x, t: ''.join(T(x, 52 - (len(t.split('\n')) - 1 - i) * 18, l, 'zl') for i, l in enumerate(t.split('\n')))  # cabeçalho longo: 2 linhas centradas na coluna
    g = hd(214, heads[0]) + hd(330, heads[1]) + L(10, 60, 390, 60, 'grid')
    for i, (lab, a, b) in enumerate(rows):
        y = 64 + i * rh; cy = y + rh / 2 + 5
        part = T(14, cy, lab, 'b', 'start')
        part += (B(160, y + 5, 108, rh - 10, a, 'bx', 'sm') + B(276, y + 5, 108, rh - 10, b, 'bx', 'sm')) if b else B(160, y + 5, 224, rh - 10, a, 'bxo', 'sm')
        g += S(i + 1 if steps else 0, part + L(10, y + rh, 390, y + rh, 'grid'))
    if foot: g += T(200, h - 12, foot, 'sm')
    return svg(title, g, h)

# ---------------------------------------------------------------- diagramas
D = {}
def d(f): D[f.__name__] = f; return f

@d
def hpf():
    return svg('Low Cut (HPF): uma rampa', axes() +
        '<rect x="41" y="45" width="125" height="214" class="zr" opacity=".35"/>' +
        P('M45 255 C125 250 140 122 175 112 L385 110', 'curve') + C(163, 118, 6, 'dot') +
        T(103, 72, 'graves', 'b') + T(103, 90, 'cortados', 'b') + T(103, 114, 'ronco, vento,', 'sm lt') + T(103, 130, 'pisadas', 'sm lt') +
        T(175, 98, 'Freq do corte', 'lbl', 'start') + T(270, 135, 'o resto passa igual', 'sm') +
        T(40, 282, '20 Hz', 'sm', 'start') + T(220, 300, 'liga/desliga + frequência ajustável', 'sm'))
@d
def eq(v=0):  # v=1: 6.2.2 (bandas livres; GEQ nos buses); v=2: agenda do cap. 06 (low cut + EQ). Rodada 3: sem o mesmo desenho em 3 slides do capítulo
    if v == 1:
        g = axes(xl='') + L(40, 150, 385, 150, 'curve2') + P('M42 150 L95 150 C120 150 130 195 150 195 C170 195 180 150 205 150 L225 150 C245 150 252 105 268 105 C284 105 291 150 311 150 L385 150', 'curve')
        g += ''.join(C(x, y, 7, 'dot') for x, y in ((70, 150), (150, 195), (268, 105), (350, 150)))
        g += ''.join(L(x - 30, 236, x + 30, 236, 'ln2') for x in (70, 150, 268, 350)) + T(200, 284, 'Low, Lo Mid, Hi Mid, High: só nomes', 'b')
        g += T(200, 308, 'corte e shelf nas pontas · PEQ e VEQ em qualquer banda', 'sm')
        g += T(178, 204, 'Q baixo: largo', 'sm', 'start') + T(268, 88, 'Q alto: estreito', 'sm')   # checklist P12/P45: o Q fica só no desenho; legenda abaixo do eixo, "Q baixo" fora da grade
        return svg('EQ do canal: 4 bandas livres', g, 318)
    if v == 2:
        g = axes() + '<rect x="41" y="45" width="70" height="214" class="zr" opacity=".3"/>' + P('M45 250 C80 246 92 160 112 152 L132 150 C150 150 160 190 180 190 C200 190 210 150 228 150 L250 150 C268 150 276 112 292 112 C306 112 314 150 330 150 L385 150', 'curve')
        g += T(76, 72, 'Low Cut', 'b') + T(180, 214, 'corte', 'sm') + T(292, 96, 'reforço', 'sm') + T(200, 300, 'primeiro o filtro, depois o EQ', 'lbl')
        return svg('Low cut e EQ: um timbre', g, 310)
    return svg('EQ paramétrico: Freq, Gain e Q', axes() + L(40, 150, 385, 150, 'curve2') +
        P('M42 150 L95 150 C120 150 130 195 150 195 C170 195 180 150 205 150 L225 150 C245 150 252 105 268 105 C284 105 291 150 311 150 L385 150', 'curve') +
        ''.join(C(x, y, 7, 'dot') for x, y in ((70, 150), (150, 195), (268, 105), (350, 150))) +
        ''.join(T(x, 252, s, 'sm') for x, s in ((70, 'Low'), (150, 'Lo Mid'), (268, 'Hi Mid'), (350, 'High'))) +
        L(118, 214, 182, 214, 'ln2') + T(150, 234, 'Q = largura', 'lbl') +
        L(268, 148, 268, 112, 'ln') + T(278, 135, 'Gain', 'lbl', 'start') +
        T(150, 128, 'corte', 'sm') + T(268, 88, 'reforço', 'sm') +
        T(200, 304, '4 bandas nos canais · 6 nos buses e no Main', 'sm'))
@d
def comp(q=False):  # q = quiz do cap. 08 (rodada 3): o que acontece acima do threshold só aparece na resposta
    A = qa(q)
    return svg('Compressor: acima do threshold?' if q else 'Compressor: curva de transferência',
        L(50, 270, 250, 270, 'axis') + L(50, 270, 50, 50, 'axis') + T(250, 290, 'entrada →', 'sm', 'end') + T(54, 46, 'saída', 'sm', 'start') +
        L(50, 270, 250, 70, 'curve2') + L(140, 270, 140, 56, 'thr') + T(140, 302, 'Threshold', 'lblr') +
        (P('M50 270 L140 180', 'curve') + T(256, 74, '1:1 (sem compressão)', 'sm', 'start') if q else '') +
        A(P('M50 270 L128 192 Q140 180 154 175 L250 127', 'curve'), P('M140 180 L250 180', 'curve4'),
          L(230, 92, 230, 133, 'ln2'), T(238, 116, 'GR', 'lbl', 'start')) +
        ('' if q else T(256, 74, '1:1 (sem compressão)', 'sm', 'start')) + A(T(256, 236, 'Knee: entrada suave', 'sm', 'start')), 310)   # rodada 6: ratio e makeup ficam nos bullets
@d
def duck():
    lane = lambda y, s: L(40, y, 385, y, 'axis') + T(40, {130: 52, 270: 166}[y], s, 'b', 'start')
    return svg('Ducking: a música abaixa quando alguém fala',
        lane(130, 'Voz (sinal de comando, key)') + P('M40 128 L120 128 L124 70 L132 100 L140 66 L150 95 L160 72 L172 98 L182 80 L190 128 L280 128 L284 76 L295 98 L305 70 L318 128 L385 128', 'curve3') +
        lane(270, 'Música (canal com ducker)') + P('M40 190 L118 190 L132 235 L188 235 L205 190 L278 190 L290 235 L320 235 L336 190 L385 190', 'curve') +
        L(132, 196, 132, 230, 'ln') + T(160, 258, 'abaixa', 'lbl') + T(250, 182, 'volta', 'lbl') +
        T(200, 305, 'quiz, cerimônia, locução', 'sm'), 315)
@d
def gate(v=0):  # v=1: 7.2.2 (uso prático, rodada 3): cada bullet acende a sua peça; a agenda do cap. 07 fica com o desenho de sempre
    hit = lambda x: f'M{x} 210 L{x + 3} 70 Q{x + 20} 160 {x + 80} 205'
    if v == 1:
        g = axes(40, 210, 385, 45, 'tempo →', 'nível') + ''.join(P(hit(x), 'curve') for x in (60, 170, 280)) + P('M40 196 q8 -10 16 0 t16 0 t16 0 M100 198 q8 -8 16 0 t16 0 t16 0 t16 0 M212 197 q8 -8 16 0 t16 0 t16 0 t16 0', 'curve3')
        g += T(150, 186, 'vazamento', 'sm') + T(80, 60, 'tom', 'b')
        g += S(2, L(40, 140, 385, 140, 'thr'), T(384, 134, 'Threshold: acima do vazamento', 'lblr', 'end'))
        g += S(1, *[f'<rect x="{a}" y="232" width="{b - a}" height="20" rx="4" class="{c}"/>' for a, b, c in ((40, 60, 'zgr'), (60, 100, 'zg'), (100, 170, 'zgr'), (170, 210, 'zg'), (210, 280, 'zgr'), (280, 320, 'zg'), (320, 385, 'zgr'))],
                 T(212, 272, 'tons, caixa, bumbo: só a batida passa', 'b'))
        g += S(3, B(90, 284, 220, 28, 'forte demais: corta o fim da nota', 'bxr', 'sm'))
        return svg('Gate na bateria: só a batida passa', g, 318)
    return svg('Gate: abre no som, fecha no silêncio', axes(40, 210, 385, 45, 'tempo →', 'nível') +
        ''.join(P(hit(x), 'curve') for x in (60, 170, 280)) + L(40, 140, 385, 140, 'thr') + T(384, 134, 'Threshold', 'lblr', 'end') +
        ''.join(f'<rect x="{a}" y="232" width="{b - a}" height="20" rx="4" class="{c}"/>' for a, b, c in
                ((40, 60, 'zgr'), (60, 100, 'zg'), (100, 170, 'zgr'), (170, 210, 'zg'), (210, 280, 'zgr'), (280, 320, 'zg'), (320, 385, 'zgr'))) +
        T(80, 270, 'aberto', 'sm') + T(135, 270, 'fechado', 'sm') + T(135, 286, '(atenua vazamento)', 'sm') +
        T(300, 290, 'Range: quanto abaixa', 'b') + T(300, 308, '(expander abaixa aos poucos)', 'sm'), 315)
@d
def taps(q=False):  # q = quiz do cap. 10: as caixas de retorno e de efeito ficam sem rótulo até a resposta
    blk = ['Entrada (ganho)', 'Low Cut + Gate', 'EQ', 'Compressor', 'Fader', 'Pan → Main LR']
    g = ''
    for i, s in enumerate(blk):
        y = 38 + i * 44
        g += B(15, y, 160, 32, s, 'bxo' if s == 'Fader' else 'bx')
        if i < len(blk) - 1: g += L(95, y + 32, 95, y + 44)
    W = QT if q else (lambda x: x)
    tap = lambda y, ty, s, c: L(95, y, 210, ty, 'lnd') + B(210, ty - 20, 180, 40, s, c)
    return svg('De onde sai o envio (tap point)', g +
        tap(117, 103, 'Pre EQ', 'bx') + W(tap(208, 190, 'Pré-fader → retorno', 'bxg')) + W(tap(252, 262, 'Pós-fader → efeito', 'bxo')) +
        qa(q)(T(300, 222, 'não segue o fader', 'sm'), T(300, 296, 'segue o fader', 'sm')), 310)
@d
def buses():
    ch = ''.join(B(15, 45 + i * 60, 80, 36, f'Canal {i + 1}') for i in range(4))
    bs = [('Aux / Mix 1', 'retorno', 'bxg'), ('Aux / Mix 2', 'in-ear', 'bxg'), ('FX 1', 'reverb', 'bxo'), ('Main LR', 'PA', 'bxb')]
    g = ''
    for j, (b, o, c) in enumerate(bs):
        y = 45 + j * 60
        g += B(175, y, 110, 36, b, c) + L(285, y + 18, 300, y + 18) + T(305, y + 23, o, 'sm', 'start')
        for i in range(4): g += L(95, 63 + i * 60, 175, y + 18, 'sep')
    return svg('Envios: cada canal vai para vários buses', ch + g + T(200, 300, 'quantidade de buses varia (tabelas 1.1.5 e 1.1.6)', 'sm'), 310)
@d
def dca():  # rodada 3: as setas dos canais chegam numa barra de soma; uma seta só entra em Main e no subgrupo
    left = (B(10, 40, 180, 26, 'DCA', 'bxo') + ''.join(B(15 + i * 44, 104, 38, 30, f'Ch{i + 1}') + L(34 + i * 44, 66, 34 + i * 44, 104, 'ctl') + L(34 + i * 44, 134, 34 + i * 44, 160, 'ln0') for i in range(4)) +
            '<rect x="22" y="160" width="156" height="7" rx="3" class="sum"/>' + L(100, 167, 100, 198, 'ln') + B(50, 200, 100, 30, 'Main') +
            T(100, 258, 'só comanda volumes', 'b') + T(100, 276, 'não soma áudio', 'sm') + T(100, 292, 'sem compressor', 'sm'))
    right = (''.join(B(215 + i * 44, 40, 38, 30, f'Ch{i + 1}') + L(234 + i * 44, 70, 234 + i * 44, 86, 'ln0') for i in range(4)) +
             '<rect x="222" y="86" width="156" height="7" rx="3" class="sum"/>' + L(300, 93, 300, 103, 'ln') +
             B(225, 105, 150, 30, 'Subgrupo (bus)', 'bxg') + L(300, 135, 300, 150) + B(225, 150, 150, 30, 'EQ + compressor', 'bx') + L(300, 180, 300, 200) +
             B(250, 200, 100, 30, 'Main') + T(300, 258, 'soma o áudio', 'b') + T(300, 276, 'processa o conjunto', 'sm'))
    return svg('DCA × subgrupo', left + L(200, 34, 200, 300, 'sep') + right, 305)
@d
def mutegrp():
    return svg('Mute group: um botão, vários mutes', B(130, 40, 140, 36, 'Mute Group 1', 'bxr') +
        ''.join(L(200, 76, 50 + i * 100, 130, 'ctl') + B(15 + i * 100, 130, 70, 40, f'Coro {i + 1}') + T(50 + i * 100, 196, 'MUTE', 'lblr') for i in range(4)) +
        T(200, 240, 'X AIR / M AIR: 4 grupos', 'b') + T(200, 262, 'X32 / M32: 6 grupos', 'b') + T(200, 290, 'teatro, coro, troca de banda', 'sm'), 300)
@d
def matrix():
    src = B(15, 60, 110, 34, 'Main LR', 'bxb') + B(15, 130, 110, 34, 'Mix buses', 'bx') + B(15, 200, 110, 34, 'Mono/Center', 'bx')
    outs = [('Matriz 1/2', 'PA (topos)'), ('Matriz 3', 'subwoofer'), ('Matriz 4', 'torre de delay'), ('Matriz 5', 'live / outra sala')]
    g = ''
    for j, (m, o) in enumerate(outs):
        y = 40 + j * 62
        g += B(190, y, 100, 32, m, 'bxo') + L(290, y + 16, 305, y + 16) + T(308, y + 21, o, 'sm', 'start')
        g += ''.join(L(125, sy, 190, y + 16, 'sep') for sy in (77, 147, 217))
    return svg('Matriz: um "aux dos auxes"', src + g + T(200, 300, 'só X32 / M32 · nas X AIR, truques com buses', 'sm'), 310)
@d
def crossover():
    return svg('Crossover: graves para o sub, resto para os topos', axes() +
        P('M42 250 C120 246 150 140 185 112 L385 110', 'curve') + P('M42 110 L150 110 C190 120 220 246 300 252', 'curve3') +
        L(178, 260, 178, 100, 'sep') + T(178, 278, 'ponto de corte', 'lbl') +
        T(95, 96, 'Sub (passa-baixas)', 'b') + T(300, 96, 'Topos (passa-altas)', 'b') +
        T(200, 296, 'LR24: a mesma frequência nos dois lados', 'sm') + T(200, 313, 'pontos de partida: cerca de 80 a 100 Hz', 'sm'), 320)
@d
def auxsub():  # 15.2.3 (rodada 4): desenho alto, ocupa o painel (o slide tem um bullet só, sem faixa de passos)
    srcs = [('Bumbo', 1), ('Baixo', 1), ('Teclado', 1), ('Voz', 0)]
    g = ''
    for i, (s_, ok) in enumerate(srcs):
        y = 44 + i * 86
        g += B(10, y, 110, 50, s_, 'bx', 'bb') + L(120, y + 25, 249, 276 + i * 15, 'ln' if ok else 'lnx') + L(120, y + 25, 250, 92, 'sep')   # rodada 3: cada seta chega num ponto da borda do Aux 6
        if not ok: g += X(196, 320)
    return svg('Sub pelo auxiliar (aux-fed sub)', g + B2(252, 58, 140, 68, 'Main LR\n→ topos', 'bxb') + B2(252, 266, 140, 68, 'Aux 6\n→ sub', 'bxo') +
        T(322, 352, 'envio pós-fader:', 'sm') + T(322, 370, 'o sub segue o fader', 'sm') + T(200, 408, 'só o que tem grave útil vai para o sub', 'b'), 418)
@d
def tower():
    return svg('Torre de delay: atrasar para alinhar',
        B(15, 60, 60, 120, 'PA', 'bxd', 'b tw') + B(250, 80, 50, 90, 'torre', 'bxd', 'b tw') +
        ''.join(C(110 + i * 26, 230, 9, 'person') for i in range(4)) + ''.join(C(320 + i * 22, 230, 9, 'person') for i in range(3)) +
        L(75, 120, 248, 120, 'lnd') + T(162, 112, 'o som do PA chega depois', 'sm') +
        L(75, 270, 300, 270, 'ln2') + T(187, 292, 'distância → tempo de atraso', 'b') +
        T(200, 316, 'delay de saída: X32/M32 · X AIR: truques (15.2.5)', 'sm'), 325)
@d
def usbrec():  # rodada 4: pistas em verde/cinza (a barra vermelha sem legenda saiu)
    tr = ''.join(f'<rect x="260" y="{150 + i * 22}" width="{60 + (i * 37) % 60}" height="14" rx="3" class="{["bar", "barb"][i % 2]}"/>' for i in range(5))
    return svg('Gravação multipista pelo USB', B(15, 60, 120, 60, 'Mesa', 'bxd', 'b tw') + B(250, 60, 140, 60, 'Computador\n(DAW)', 'bxb') +
        L(135, 80, 250, 80) + L(250, 102, 135, 102) + T(192, 72, 'USB Sends', 'sm') + T(192, 120, 'USB Returns', 'sm') +
        T(330, 144, 'uma pista por canal', 'sm') + tr +
        T(75, 160, 'XR18 / X18 / MR18:', 'b') + T(75, 178, '18 × 18', 'sm') + T(75, 210, 'X32 / M32:', 'b') + T(75, 228, 'placa (Card 1–32)', 'sm') +
        T(200, 290, 'mesma taxa na mesa e no DAW (48 kHz)', 'lbl'), 300)
@d
def vsc():  # 19.2.5 (rodada 3): uma caixa por passo; bullets 2 e 3 = "Tocar"; o 4º = voltar ao analógico
    return svg('Virtual soundcheck em 4 passos',
        S(1, B(15, 45, 370, 52, '1. Gravar: palco → canais → USB → DAW', 'bxg')) + HL(10, 40, 380, 62, 1) +
        S(2, L(200, 97, 200, 115), B(15, 115, 370, 52, '2. Tocar: DAW → canais (fonte = USB/Card)', 'bxo')) + HL(10, 110, 380, 62, 2) + HL(10, 110, 380, 62, 3) +
        S(4, L(200, 167, 200, 185), B(15, 185, 370, 52, '3. Voltar a fonte para analógico (Record)', 'bxr'), T(200, 268, 'esqueceu o passo 3? a banda sobe e não sai som', 'lblr')) + HL(10, 180, 380, 62, 4) +
        T(200, 292, 'ensaio gravado vira treino para voluntários', 'sm'), 305)
@d
def pendrive():
    return svg('Gravador estéreo e música do pendrive', B(15, 70, 130, 60, 'Main ou bus', 'bxb') + L(145, 100, 230, 100) + B(230, 70, 155, 60, 'Pendrive\n(gravador)', 'bxo') +
        L(307, 130, 307, 180) + L(307, 180, 80, 180) + L(80, 180, 80, 210) + B(15, 210, 130, 40, 'Canal / Aux', 'bx') + T(210, 172, 'tocar música do intervalo', 'sm') +
        T(200, 285, 'não tire o pendrive com o LED vermelho aceso', 'lblr'), 300)
@d
def live():
    return svg('Mix separada para a live', B(15, 50, 110, 40, 'Canais') + L(125, 70, 220, 60) + L(125, 70, 220, 160) +
        B(220, 40, 165, 40, 'Main LR → PA', 'bxb') + B(220, 140, 165, 40, 'Bus/matriz da live', 'bxg') + L(302, 180, 302, 215) +
        B(220, 215, 165, 36, 'transmissão', 'bx') + L(302, 80, 302, 132, 'lnx') + X(320, 100) +
        T(110, 170, 'o que é alto no palco', 'sm') + T(110, 188, 'fica baixo no PA', 'sm') + T(110, 206, 'e some na live', 'sm') +
        T(200, 296, 'não mande o Main direto para a live', 'lblr'), 305)
@d
def aes50(hl=False, q=False):  # q = quiz do cap. 20 (pendência 3.11): desenho alto; a contagem de canais (a resposta) entra no lugar do "?"
    g = (B(15, 50, 120, 120, 'Stagebox\nS16 / DL16\n/ DL32', 'bxd', 'b tw') + B(265, 50, 120, 120, 'X32 / M32\nportas\nA e B', 'bxb') +
         L(135, 110, 265, 110, 'ln2') + T(200, 98, 'Cat-5e blindado', 'b') + T(200, 135, 'até 100 m', 'sm'))
    g += QT(B(60, 190, 280, 50, '48 × 48 canais por porta', 'bxo', 'b')) if q else T(200, 220, '48 × 48 canais por porta', 'b')
    g += (T(200, 270, 'ganho e phantom ajustados da mesa', 'sm') + T(200, 292, 'clock comum: a mesa pode seguir a AES50', 'sm') +
          T(200, 318, 'quadrado ou LED vermelho = erro de sincronismo', 'lblr'))
    if hl: g += HL(260, 45, 130, 130, 1) + HL(60, 196, 280, 32, 1) + HL(10, 45, 130, 130, 2)
    return svg('AES50: um cabo no lugar do multicabo', g, 330)
@d
def split(hl=False):  # 20.1.2: S16 → mesa de monitor → mesa de PA
    g = (B(10, 120, 90, 60, 'S16 no\npalco', 'bxd', 'b tw') + L(100, 150, 145, 150) +
        B(145, 110, 110, 80, 'Mesa de\nmonitor\n(palco)', 'bxg') + L(255, 150, 290, 150) + B(290, 110, 100, 80, 'Mesa de\nPA (FOH)', 'bxb') +
        T(272, 100, 'AES50', 'sm') + T(122, 100, 'AES50', 'sm') +
        T(200, 236, 'a mesa de palco controla os ganhos', 'b') + T(200, 260, 'cópia digital, sem splitter caro', 'sm') + T(200, 292, 'detalhes de roteamento em 20.1.2 e 20.2.5', 'sm'))
    if hl: g += HL(98, 84, 50, 82, 1) + HL(5, 115, 100, 70, 2) + HL(250, 84, 145, 112, 3) + HL(140, 105, 120, 90, 4) + HL(5, 115, 100, 70, 5)
    return svg('Split: PA e monitor com os mesmos mics', g, 300)
@d
def ultranet():
    g = ''.join(L(200, 150, 50 + i * 100, 210) + B(15 + i * 100, 210, 70, 44, 'P16-M') + C(50 + i * 100, 274, 10, 'person') for i in range(4))
    return svg('Ultranet: cada músico mixa o próprio fone', B(120, 40, 160, 40, 'Mesa', 'bxd', 'b tw') + L(200, 80, 200, 110) +
        T(212, 100, '16 canais, cabo de rede', 'sm', 'start') + B(140, 110, 120, 40, 'P16-D', 'bxo') + g +
        T(200, 312, 'não existe na XR16, XR12 e MR12', 'lblr'), 320)
@d
def retornos():
    return svg('Cada músico com sua mistura', B(130, 35, 140, 38, 'Mesa', 'bxd', 'b tw') +
        L(160, 73, 65, 125) + L(200, 73, 200, 125) + L(240, 73, 335, 125) +
        B(10, 125, 110, 50, 'Aux/Mix 1\n(mono)', 'bxg') + B(145, 125, 110, 50, 'Aux 2+3\nlinkados', 'bxg') + B(280, 125, 110, 50, 'P16\n(Ultranet)', 'bxo') +
        '<polygon points="35,210 95,210 105,250 25,250" class="wedge"/>' + T(65, 272, 'caixa de retorno', 'sm') +
        P('M180 240 Q180 205 200 205 Q220 205 220 240', 'mk') + T(200, 272, 'in-ear estéreo', 'sm') +
        B(305, 205, 60, 45, 'P16-M') + T(335, 272, 'mixer pessoal', 'sm') + T(200, 304, 'envio pré-fader: o retorno não segue o PA', 'lbl'), 312)
@d
def scenes():
    sl = ''.join(f'<rect x="{20 + i * 46}" y="50" width="38" height="46" rx="5" class="{"bxo" if i == 2 else "bx"}"/>' + T(39 + i * 46, 79, str(i + 1), 'b') for i in range(7)) + T(355, 79, '… 64', 'sm', 'start')
    return svg('Cena (snapshot) e safe', sl + L(130, 96, 200, 150) + B(130, 150, 140, 46, 'Mesa volta ao\nestado salvo', 'bxb') +
        B(20, 225, 160, 50, '🔒 Safe: ganho (HA)\nfica como está', 'bxg') + B(220, 225, 165, 50, 'filtro de recall:\nescolha o que volta', 'bx') +
        T(200, 300, 'X AIR: 64 snapshots na mesa · X32/M32: cenas e safes', 'sm'), 310)
@d
def solo():
    return svg('Solo: só o técnico ouve', B(15, 40, 80, 34, 'Canal') + L(95, 57, 140, 57) + B(140, 40, 80, 34, 'Fader', 'bxo') + L(220, 57, 270, 57) +
        B(270, 40, 115, 34, 'Main → PA', 'bxb') + L(120, 57, 120, 140, 'lnd') + L(245, 57, 245, 140, 'lnd') +
        B(70, 140, 100, 36, 'PFL', 'bxg') + T(120, 194, 'antes do fader', 'sm') + B(195, 140, 100, 36, 'AFL', 'bxg') + T(245, 194, 'depois do fader', 'sm') +
        L(120, 200, 180, 235) + L(245, 200, 210, 235) + B(130, 235, 140, 36, 'fone do técnico', 'bxo') +
        T(200, 298, 'o público continua ouvindo a mesma mix', 'lbl'), 305)
@d
def talkback():
    return svg('Talkback: falar só com o palco', B(15, 120, 100, 50, 'Mic do\ntécnico', 'bxo') + L(115, 145, 170, 90) + L(115, 145, 170, 200) +
        B(170, 70, 100, 40, 'Talk A', 'bxg') + B(170, 180, 100, 40, 'Talk B', 'bxg') + L(270, 90, 300, 90) + L(270, 200, 300, 200) +
        B(300, 70, 95, 40, 'Mix 1–16') + B(300, 180, 95, 40, 'outro') + T(200, 150, 'dois destinos independentes', 'sm', 'start') +
        T(200, 260, 'X32/M32 · M32C: entrada P10 com TRIM', 'sm'), 272)   # rodada 6: sem o rodapé que repetia os bullets
@d
def osc():  # 17.1.5 (pendência 2.11): desenho alto; gerador, tipos e destinos acendem com os seus bullets
    g = S(1, B(10, 40, 150, 64, 'Oscilador', 'bxo'), T(85, 124, 'ninguém no microfone', 'sm'), L(160, 72, 236, 72), B(238, 40, 152, 64, 'bus escolhido', 'bxb'),
          L(314, 104, 314, 130), '<polygon points="286,132 342,132 350,176 278,176" class="wedge"/>', T(314, 196, 'PA', 'sm'))
    waves = (('senoide F1/F2', 'M22 238 Q34 214 46 238 T70 238 T94 238 T118 238'), ('ruído rosa', 'M150 238 l6 -14 l6 22 l6 -18 l6 12 l6 -20 l6 26 l6 -12 l6 8 l6 -16 l6 10'),
             ('ruído branco', 'M276 238 l4 -20 l4 28 l4 -26 l4 18 l4 -24 l4 30 l4 -22 l4 16 l4 -28 l4 22 l4 -14 l4 20 l4 -18'))
    g += S(2, *[f'<rect x="{10 + i * 128}" y="208" width="120" height="66" rx="8" class="panel"/>' + P(d, 'curve') + T(70 + i * 128, 264, t, 'sm') for i, (t, d) in enumerate(waves)])
    g += S(3, B(10, 288, 380, 44, 'destinos: Mix Bus 1–16 · Main L, R, L+R\nCenter/Mono · Matrix 1–6', 'bx', 'sm'))
    return svg('Oscilador: sinal de teste', g, 342)
@d
def automix(steps=False):
    # 18.1.1: cada bullet muda o desenho (revisão 2): 3 separa os grupos X e Y, 4 mostra o medidor azul de redução, 5 o último mic aberto
    k = (lambda n: n) if steps else (lambda n: 0)
    lv = [(1, 150, 'bara'), (2, 60, 'barb'), (3, 50, 'barb'), (4, 70, 'barb')]
    g = ''.join(f'<rect x="{30 + i * 90}" y="{240 - h}" width="50" height="{h}" class="{c}"/>' + T(55 + i * 90, 260, f'Mic {n}', 'b') for i, (n, h, c) in enumerate(lv))
    g += L(20, 240, 380, 240, 'axis') + T(55, 78, 'falando', 'lbl') + T(140, 140, 'parados: reduzidos', 'sm', 'start')
    g += S(k(3), '<rect x="18" y="268" width="172" height="26" rx="5" class="bxg"/>', T(104, 286, 'grupo X: mics 1–2', 'sm'),
           '<rect x="208" y="268" width="174" height="26" rx="5" class="bxb"/>', T(295, 286, 'grupo Y: mics 3–4', 'sm'))
    g += S(k(4), *[f'<rect x="{82 + i * 90}" y="{240 - h}" width="10" height="{h}" class="blue"/>' for i, h in ((1, 80), (2, 90), (3, 70))], T(384, 70, 'medidor azul:', 'b', 'end'), T(384, 88, 'quanto cada um reduz', 'sm', 'end'))
    g += S(k(5), L(55, 52, 55, 64, 'ln'), T(55, 46, 'Last Gate: fica aberto', 'lbl', 'start'))
    return svg('Automix: quem fala ganha, os outros abaixam', g, 300)
@d
def rta(q=False):  # q = quiz do cap. 12: só o espectro com o apito; a curva de corte se desenha na resposta
    hs = [40, 55, 70, 80, 85, 82, 90, 95, 180, 92, 85, 78, 70, 60, 48, 38]
    g = ''.join(f'<rect x="{45 + i * 21}" y="{255 - h}" width="15" height="{h}" class="{"barr" if h > 150 else "bar"}"/>' for i, h in enumerate(hs))
    if not q: return svg('Espectro com um pico de microfonia', axes() + g, 280)   # rodada 6: o "pico que sobe" é o bullet
    return svg('RTA: o raio-X do som', axes() + g + T(220, 64, 'apito', 'lblr') +
        qa(q)(P('M45 110 L195 110 C210 110 212 150 220 150 C228 150 230 110 245 110 L385 110', 'curve4'),
        T(300, 140, 'corte estreito', 'b'), T(300, 158, 'só nessa frequência', 'sm')), 280)
@d
def pink():  # checklist P64: as X AIR não têm oscilador (ruído rosa por arquivo)
    g = B(4, 40, 132, 76, 'Ruído rosa\n(oscilador\nou arquivo)', 'bxo') + L(136, 78, 158, 78) + '<polygon points="160,40 220,40 232,120 148,120" class="wedge"/>' + T(190, 142, 'PA', 'b')
    g += L(234, 78, 278, 78, 'lnd') + B(280, 50, 110, 56, 'mic de\nmedição') + L(335, 106, 335, 168)
    g += B(250, 170, 140, 50, 'RTA na mesa', 'bxb') + L(250, 195, 192, 195) + B(10, 170, 180, 50, 'EQ do Main', 'bxg') + L(100, 220, 100, 248)
    g += B(10, 250, 180, 50, 'GEQ', 'bxg') + P('M190 275 L214 275 L214 132', 'lnd') + T(222, 272, 'repita e confira', 'sm', 'start')
    return svg('Medir na plateia, corrigir no Main', g, 312)  # checklist P08: o 'não exagere' fica só em 12.2.3
@d
def meters():
    m = lambda x, h, s: f'<rect x="{x}" y="50" width="28" height="200" rx="3" class="zgr"/><rect x="{x}" y="{250 - h}" width="28" height="{h}" rx="3" class="{"zr" if h > 180 else "zy" if h > 140 else "zg"}"/>' + T(x + 14, 272, s, 'sm')
    return svg('Medidores: onde está cada sinal', m(40, 120, 'Ch1') + m(90, 150, 'Ch2') + m(140, 190, 'Ch3') + m(190, 100, 'Bus') + m(240, 130, 'L') + m(280, 132, 'R') +
        L(30, 140, 320, 140, 'sep') + T(325, 144, '−18', 'sm', 'start') + T(325, 64, '0 dBFS', 'lblr', 'start') + T(200, 300, 'vermelho = clip: baixe o ganho', 'lblr'), 310)
@d
def phantom():
    it = [('Condensador', 'ok', 'precisa'), ('DI ativa', 'ok', 'precisa'), ('Dinâmico', 'bx', 'não precisa'), ('Fita (ribbon)', 'xr', 'pode estragar')]
    g = ''.join(B(20, 45 + i * 50, 170, 38, s, 'bxr' if c == 'xr' else 'bxg' if c == 'ok' else 'bx') + T(210, 70 + i * 50, n, 'lblr' if c == 'xr' else 'sm', 'start') for i, (s, c, n) in enumerate(it))
    return svg('Phantom +48 V: quando ligar', g + T(200, 268, 'liga por canal, pelo app', 'b') + T(200, 294, 'mute o canal antes de ligar ou desligar', 'lblr'), 305)
@d
def gain(q=False):  # q = quiz do cap. 05: título neutro e o medidor sem rótulos; a meta só aparece na resposta
    A = qa(q)
    return svg('Medidor de entrada do canal' if q else 'Ganho: média perto de −18 dBFS', '<rect x="60" y="45" width="60" height="230" rx="4" class="zgr"/>' +
        '<rect x="60" y="45" width="60" height="30" class="zr"/><rect x="60" y="75" width="60" height="60" class="zy"/><rect x="60" y="135" width="60" height="140" class="zg"/>' +
        A(L(50, 135, 130, 135, 'thr'), T(145, 60, '0 dBFS: estoura (clip)', 'lblr', 'start'), T(145, 92, 'picos cabem aqui', 'sm', 'start'),
        T(145, 140, '−18 dBFS: média alvo', 'b', 'start'), L(134, 47, 134, 133, 'ln2'), T(145, 114, 'headroom (folga)', 'lbl', 'start')) +
        T(140, 220, 'ajuste na passagem de som,', 'sm', 'start') + T(140, 238, 'com a fonte no volume real', 'sm', 'start') +
        T(200, 300, 'não mixe no ganho: mixe no fader', 'lbl'), 310)
@d
def path(hl=False):
    a = ['Fonte', 'Ganho', 'Low Cut', 'Gate', 'Insert']; b = ['EQ', 'Comp', 'Delay*', 'Fader', 'Pan → Main']
    g = (HL(24, 34, 162, 100, 1) + HL(24, 138, 162, 152, 2) + HL(214, 34, 162, 100, 2) + HL(214, 190, 162, 100, 3) + HL(214, 138, 162, 48, 4)) if hl else ''
    for col, items, x in ((0, a, 30), (1, b, 220)):
        for i, s in enumerate(items):
            y = 40 + i * 52
            g += B(x, y, 150, 36, s, 'bxb' if s == 'Delay*' else 'bxo' if s in ('Ganho', 'Fader') else 'bx')
            if i < 4: g += L(x + 75, y + 36, x + 75, y + 52)
    return svg('O caminho do sinal no canal', g + P('M105 284 L105 300 L200 300 L200 30 L295 30 L295 40', 'ln') + T(200, 322, '* delay de canal: só X32/M32', 'sm'), 330)
@d
def source():
    ins = [('Entrada local', 'bx'), ('USB / Card', 'bxg'), ('AES50 (X32/M32)', 'bxb')]
    g = ''.join(B(10, 45 + i * 70, 150, 40, s, c) + L(160, 65 + i * 70, 225, 135) for i, (s, c) in enumerate(ins))
    return svg('Fonte do canal: de onde vem o sinal', g + B(225, 110, 70, 50, 'fonte', 'bxo') + L(295, 135, 320, 135) + B(320, 110, 70, 50, 'Canal') +
        T(200, 270, 'a mesma entrada pode alimentar dois canais', 'sm') + T(200, 296, 'X32/M32: patch em blocos de 8', 'sm'), 305)
@d
def insert():
    return svg('Insert: o processador no meio do canal', B(10, 60, 80, 40, 'Canal') + L(90, 80, 170, 80) + B(170, 60, 70, 40, 'EQ') + L(240, 80, 310, 80) + B(310, 60, 80, 40, 'Fader') +
        L(130, 80, 130, 150) + B(80, 150, 220, 46, 'slot de FX em insert', 'bxo') + L(250, 150, 270, 80) +
        T(200, 236, 'só aquele canal ou bus passa pelo efeito', 'b') + T(200, 260, 'GEQ, limitador, exciter, válvula', 'sm') +
        T(200, 292, 'no rack: "OFF" = insert desligado', 'lbl'), 300)
@d
def pan():
    return svg('Pan e stereo link', C(100, 120, 50, 'knob') + '<line x1="100" y1="120" x2="70" y2="82" class="needle"/>' +
        T(40, 190, 'L', 'b') + T(100, 190, 'C', 'b') + T(160, 190, 'R', 'b') + T(100, 220, 'pan distribui o canal', 'sm') +
        B(230, 60, 60, 90, 'Ch1', 'bx') + B(310, 60, 60, 90, 'Ch2', 'bx') + L(290, 105, 310, 105, 'ln2') + T(300, 175, 'stereo link:', 'b') + T(300, 193, 'um par, um ajuste', 'sm') +
        T(200, 280, 'X AIR: LR · X32/M32: LR ou LCR (Mono/Center)', 'sm'), 295)
@d
def chdelay(q=False):
    w = lambda x, c: P(f'M{x} 120 q10 -50 20 0 t20 0 t20 0', c)
    return svg('Delay e polaridade do canal', w(60, 'curve') + w(110, 'curve3') + L(60, 170, 110, 170, 'ln2') + T(85, 192, 'atraso (ms)', 'b') +
        T(85, 60, 'alinhar sinais', 'sm') + P('M240 120 q15 -50 30 0 t30 0', 'curve') + P('M240 120 q15 50 30 0 t30 0', 'curve3') + T(285, 192, 'polaridade (Ø)', 'b') +
        T(285, 60, 'inverte a onda', 'sm') + qa(q)(T(200, 270, 'delay de canal: só X32/M32', 'lbl')), 285)
@d
def fx(hl=False):
    g = (B(10, 40, 70, 32, 'Ch1') + B(10, 82, 70, 32, 'Ch2') + B(10, 124, 70, 32, 'Ch3') +
        ''.join(L(80, y, 120, 98, 'sep') for y in (56, 98, 140)) + B(120, 78, 80, 40, 'Reverb', 'bxo') + L(160, 118, 160, 160) + B(110, 160, 100, 32, 'FX Return') +
        T(110, 216, 'envio: vários canais', 'b') + L(220, 34, 220, 252, 'sep') +
        B(240, 50, 70, 32, 'Ch4') + L(310, 66, 330, 66) + B(330, 50, 60, 32, 'GEQ', 'bxo') + L(360, 82, 360, 130) + B(300, 130, 90, 32, 'continua') + T(315, 216, 'insert: um só', 'b') +
        T(200, 262, 'X AIR: 4 slots estéreo, envio ou insert', 'sm') + T(200, 282, 'X32/M32: 8 slots (5–8 só insert)', 'sm'))
    if hl:  # 13.2.3: tempo por envio, processador em insert, o porquê (sem seco/molhado) e o erro (rack inteiro para um canal)
        g += HL(4, 32, 212, 196, 1) + HL(226, 42, 168, 186, 2) + HL(114, 72, 92, 52, 3)
        # rodada 4 (18/14): o erro do bullet 4 desenhado: um compressor no lugar do reverb, no ramo de envio, riscado
        g += O(4, '<rect x="114" y="74" width="92" height="48" rx="8" class="bxd"/>', B(114, 74, 92, 48, 'Compressor\nno envio', 'bxr', 'sm'), X(206, 66), T(110, 238, 'compressor vai em insert', 'lblr'))
        g += O(3, T(110, 238, 'reverb: só o molhado', 'lbl'))
    return svg('Efeito por envio × em insert', g, 292)
@d
def dual():
    return svg('Stereo × Dual no mesmo slot', B(20, 50, 160, 90, 'Stereo\nL e R juntos', 'bxo') + B(220, 50, 75, 90, 'Dual\nL', 'bxg') + B(305, 50, 75, 90, 'Dual\nR', 'bxg') +
        T(100, 170, 'canais linkados,', 'sm') + T(100, 188, 'buses estéreo', 'sm') + T(300, 170, 'dois efeitos mono', 'sm') + T(300, 188, 'com ajustes próprios', 'sm') +
        T(200, 260, 'combinações (ex.: Delay + Chamber)', 'sm') + T(200, 280, 'ocupam um slot só', 'b'), 295)
@d
def network(q=False):  # q = quiz do cap. 03: título neutro e sem a linha "o USB não controla a mesa"
    return svg('Como o app chega à mesa' if q else 'Rede: a mesa é o motor, o app é o volante', B(15, 60, 110, 50, 'Mesa', 'bxd', 'b tw') + L(125, 85, 170, 85, 'ln2') + T(147, 76, 'cabo', 'sm') +
        B(170, 60, 100, 50, 'Roteador', 'bxg') + P('M275 70 q10 15 0 30 M285 62 q16 23 0 46', 'mk') + B(300, 50, 85, 30, 'Tablet', 'bx') + B(300, 95, 85, 30, 'Notebook', 'bx') +
        T(200, 160, 'chave REMOTE (X AIR / M AIR):', 'b') + T(200, 184, 'Ethernet · Wi-Fi Client · Access Point', 'sm') +
        T(200, 225, 'recomendado em show: roteador externo', 'lbl') + T(200, 260, 'X32/M32: sem Wi-Fi interno, só cabo', 'sm') +
        qa(q)(T(200, 290, 'o USB não controla a mesa', 'lblr')), 300)
@d
def sync(q=False):  # q = quiz do cap. 24 (pendência 3.11): Mesa ↔ App grandes, as duas direções bem separadas; o que acontece entra no lugar do "?"
    qt = QT if q else (lambda x: x)
    g = B(10, 40, 140, 96, 'Mesa', 'bxd', 'b tw') + B(250, 40, 140, 96, 'App no PC', 'bxb')
    g += L(150, 66, 248, 66) + T(200, 56, 'Mixer → PC', 'b') + L(248, 112, 152, 112, 'lnx') + T(200, 134, 'PC → Mixer', 'lblr')
    g += qt(B(10, 160, 380, 50, '✓ Mixer → PC: copia a mesa para o app', 'bxg', 'b'))
    g += qt(B(10, 224, 380, 64, 'PC → Mixer por engano: apaga o show\nou deixa a mesa muda', 'bxr', 'b'))
    return svg('Sincronizar: Mixer → PC', g, 300)
@d
def apps(v=0):
    if v:   # rodada 3: o bullet acende o aparelho de que fala (4.2.1: v=1; 4.2.6: v=2)
        hl = [(10, 44, 384, 150, 1), (10, 44, 180, 124, 2), (198, 52, 196, 106, 3), (90, 244, 220, 22, 4)] if v == 1 else \
             [(10, 44, 180, 124, 1), (198, 52, 196, 106, 1), (10, 44, 180, 124, 2), (20, 222, 360, 22, 2)]
        extra = ''.join(HL(*r) for r in hl)
    else: extra = ''
    return svg('Apps: cada aparelho com um papel' if v != 2 else 'Técnico no computador, músicos no tablet', extra + B(15, 50, 170, 110, '', 'panel') + B(30, 62, 140, 80, 'Edit no\ncomputador', 'bxb') + T(100, 182, 'técnico', 'b') +
        B(205, 60, 96, 90, 'tablet', 'bx') + B(313, 75, 76, 75, 'celular', 'bx', 'sm') + T(253, 182, 'mesa sem faders', 'sm') + T(351, 182, 'retorno', 'sm') +
        T(200, 236, 'X AIR Edit · M AIR Edit · X32-Edit · M32-Edit', 'sm') + T(200, 258, 'Mixing Station (terceiros)', 'sm') +
        T(200, 290, 'computador para o técnico, tablet para os músicos', 'lbl'), 300)
@d
def usbq(q=False):  # quiz do cap. 03 (rodada 3): o estado final de 3.2.1; com q, o que cada cabo leva só aparece na resposta
    A = qa(q)
    g = T(66, 40, 'MESA', 'b') + T(332, 40, 'COMPUTADOR', 'b')
    g += '<rect x="8" y="52" width="118" height="196" rx="8" class="bxd"/>' + B(30, 70, 60, 30, 'MUTE', 'bx', 'b')
    g += '<rect x="110" y="98" width="16" height="20" rx="2" class="bxd"/>' + T(104, 113, 'REDE', 'b', 'end')
    g += '<rect x="110" y="188" width="16" height="20" rx="2" class="bxd"/>' + T(104, 203, 'USB', 'b', 'end')
    g += '<rect x="274" y="52" width="118" height="150" rx="6" class="bxb"/>' + P('M264 202 H400 V210 Q400 214 396 214 H268 Q264 214 264 210 Z', 'bx') + T(333, 104, 'app', 'b') + T(333, 128, 'procura a mesa', 'b')
    g += L(126, 198, 272, 198, 'ln2') + T(200, 188, 'USB', 'b')
    g += A(L(126, 108, 272, 108, 'ln2'), T(200, 98, 'REDE', 'lbl'), T(200, 130, 'controle', 'b'), T(200, 222, 'áudio e MIDI', 'b'), T(200, 280, 'o controle só passa pela rede', 'lbl'))
    return svg('Só o USB ligado', g, 296)
@d
def sof(q=False):  # q = quiz do cap. 04: só os faders; "Main ↔ Bus 1" (a resposta) entra na escolha
    f = ''.join(fader(60 + i * 60, 60, 150, p) for i, p in enumerate((30, 70, 50, 100, 20)))
    return svg('Sends on Faders', f + qa(q)(B(20, 240, 160, 36, 'Main: mix do PA', 'bxb'), B(220, 240, 165, 36, 'Bus 1: retorno', 'bxg'),
        L(180, 258, 220, 258, 'ln2'), T(200, 300, 'os mesmos faders, outra mixagem', 'lbl')), 310)
def icon(k, cx, cy, c):  # ícones da fita (scribble strip): microfone, violão, bumbo, baixo, teclado, efeito
    if k == 'mic': return f'<rect x="{cx - 6}" y="{cy - 14}" width="12" height="17" rx="6" class="{c}"/><path d="M{cx - 10} {cy - 2} q0 11 10 11 q10 0 10 -11 M{cx} {cy + 9} v6" class="{c}"/>'
    if k == 'gtr': return f'<circle cx="{cx - 4}" cy="{cy + 6}" r="8" class="{c}"/><circle cx="{cx + 3}" cy="{cy - 3}" r="5" class="{c}"/><path d="M{cx + 6} {cy - 6} L{cx + 15} {cy - 16}" class="{c}"/>'
    if k == 'kick': return f'<circle cx="{cx}" cy="{cy}" r="13" class="{c}"/><circle cx="{cx}" cy="{cy}" r="4" class="{c}"/>'
    if k == 'bass': return f'<circle cx="{cx - 6}" cy="{cy + 7}" r="7" class="{c}"/><path d="M{cx - 1} {cy + 2} L{cx + 15} {cy - 16}" class="{c}"/>'
    if k == 'keys': return f'<rect x="{cx - 16}" y="{cy - 9}" width="32" height="18" rx="2" class="{c}"/>' + ''.join(f'<path d="M{cx - 8 + i * 8} {cy - 9} v11" class="{c}"/>' for i in range(3))
    return f'<path d="M{cx - 12} {cy + 6} q6 -22 12 0 q6 22 12 0" class="{c}"/>'  # efeito (onda)
NAMES = [('VOZ', 'A', 'mic'), ('VIOLÃO', 'A', 'gtr'), ('BUMBO', 'B', 'kick'), ('BAIXO', 'B', 'bass'), ('TECLADO', 'C', 'keys')]
@d
def naming(v=1):  # 4.1.4 (v=1, sem passos: desenho alto) e 4.2.11 (v=2: o 2º bullet acende a cor do efeito)
    sh = 80 if v == 1 else 70; fh = 150 if v == 1 else 84
    g = ''
    for i, (s_, c, ic) in enumerate(NAMES):
        x = 5 + i * 79   # rodada 6: fita de 71 com 8 de vão (antes 77 com 2: as caixas quase se tocavam)
        g += f'<rect x="{x}" y="40" width="71" height="{sh}" rx="7" class="sc{c}"/>' + icon(ic, x + 35.5, 66 if v == 1 else 62, 'ic' + c) + T(x + 35.5, 40 + sh - 12, 'TECLAS' if s_ == 'TECLADO' else s_, 'b')
        g += fader(x + 35.5, 52 + sh, fh, 26 + i * 10)
    y = 52 + sh + fh + 22
    if v == 1:
        g += ''.join(f'<rect x="{x}" y="{y}" width="18" height="18" rx="4" class="sc{c}"/>' + T(x + 26, y + 15, t, 'sm', 'start') for x, c, t in ((10, 'A', 'voz e violão'), (142, 'B', 'bumbo e baixo'), (284, 'C', 'teclas')))
        g += T(200, y + 52, 'nome, cor e ícone em cada canal', 'b')
        return svg('Fita de cada canal: nome, cor e ícone', g, y + 64)
    g += HL(5, 35, 390, sh + 10, 2)
    g += S(2, f'<rect x="10" y="{y}" width="150" height="40" rx="7" class="scD"/>', icon('fx', 34, y + 20, 'icD'), T(100, y + 26, 'envio FX 1', 'b'), L(162, y + 20, 238, y + 20, 'ln'),
           f'<rect x="240" y="{y}" width="150" height="40" rx="7" class="scD"/>', icon('fx', 264, y + 20, 'icD'), T(330, y + 26, 'retorno FX 1', 'b'), T(200, y + 64, 'mesma cor no envio e no retorno', 'lbl'))
    return svg('Cor por família e por efeito', g, y + 76)
@d
def power(q=False):  # q = quiz do cap. 02: as caixas ficam vazias (silhueta) e a ordem só aparece na resposta
    W = QT if q else (lambda x: x); A = qa(q); m, pa = ('bx', 'bx') if q else ('bxb', 'bxo')  # quiz: cor neutra (a cor também entregava a ordem)
    return svg('Ordem de ligar e desligar', T(100, 55, 'LIGAR', 'zl') + W(B(30, 70, 140, 40, '1. Mesa', m)) + L(100, 110, 100, 135) + W(B(30, 135, 140, 40, '2. PA / amplis', pa)) +
        T(300, 55, 'DESLIGAR', 'zl') + W(B(230, 70, 140, 40, '1. PA / amplis', pa)) + L(300, 110, 300, 135) + W(B(230, 135, 140, 40, '2. Mesa', m)) +
        A(T(200, 220, 'evita estalo no PA', 'b')) + T(200, 250, 'X AIR: Mute at Power On / Safe Levels', 'sm') + T(200, 272, 'X32: Safe Main Levels', 'sm'), 285)
@d
def reset(v=1):
    if v == 2:   # 2.2.3 (rodada 3): o tempo segurando o botão decide o que volta ao padrão (antes repetia o desenho de 2.1.8)
        g = C(50, 96, 26, 'knob') + C(50, 96, 6, 'cap') + T(50, 146, 'RESET', 'b')
        g += L(96, 96, 378, 96, 'axis') + ''.join(L(x, 90, x, 102, 'tick') + T(x, 122, t, 'sm') for x, t in ((100, '0 s'), (158, '2 s'), (374, '10 s')))
        g += '<rect x="100" y="56" width="58" height="26" rx="4" class="bxg"/>' + T(129, 74, 'rede', 'sm') + '<rect x="160" y="56" width="214" height="26" rx="4" class="bxr"/>' + T(267, 74, 'a mesa inteira', 'b')
        g += S(2, T(200, 168, 'soltou antes dos 10 s? só a rede voltou', 'lblr'))
        g += S(3, B(20, 186, 170, 40, 'Show Data: salve', 'bxg', 'sm')) + S(4, B(210, 186, 170, 40, 'Factory Reset (app)', 'bxo', 'sm'))
        g += S(5, T(200, 258, 'salve cenas e shows antes', 'lbl')) + HL(82, 48, 312, 86, 1)
        return svg('RESET: 2 s ou 10 s segurando', g, 270)
    return svg('Voltar ao padrão (X AIR / M AIR)', C(70, 124, 34, 'knob') + C(70, 124, 8, 'cap') + T(70, 186, 'RESET', 'bb') +
        B2(150, 44, 240, 80, '2 s\nsó a rede', 'bxg') + B2(150, 136, 240, 80, '10 s\na mesa inteira', 'bxr') +
        T(200, 252, 'salve cenas e shows antes', 'lblr'), 264)
@d
def firmware():  # pendência 3.6: o passo 3 bifurca de verdade (X AIR × X32/M32), com seta do 2 para cada lado e os dois voltando ao 4
    g = B(20, 36, 360, 38, '1. Backup de shows e cenas', 'bxg') + L(200, 74, 200, 88) + B(20, 90, 360, 38, '2. Baixe do site oficial', 'bx')
    g += P('M150 128 L150 140 L95 140 L95 152', 'ln') + P('M250 128 L250 140 L305 140 L305 152', 'ln')
    g += B(10, 154, 186, 56, '3. X AIR:\nEdit › Update Firmware', 'bxb') + B(204, 154, 186, 56, '3. X32/M32:\npendrive FAT32 + boot', 'bxb')
    g += P('M95 210 L95 222 L190 222 L190 234', 'ln') + P('M305 210 L305 222 L210 222 L210 234', 'ln')
    g += B(20, 236, 360, 38, '4. Confira a versão e reconecte', 'bx')
    return svg('Atualizar o firmware com segurança', g + T(200, 300, 'antes do evento, nunca durante', 'lblr2'), 310)
@d
def maint():
    it = [('Calor', 'não bloqueie a ventilação'), ('Poeira', 'capa e limpeza'), ('Energia', 'tomada com aterramento'), ('Faders', 'sujos travam: limpe')]
    g = ''.join(B(15 + (i % 2) * 190, 50 + (i // 2) * 110, 180, 90, '', 'panel') + T(105 + (i % 2) * 190, 90 + (i // 2) * 110, s, 'b') + T(105 + (i % 2) * 190, 115 + (i // 2) * 110, n, 'sm') for i, (s, n) in enumerate(it))
    return svg('Cuidados com o equipamento', g + T(200, 290, 'detalhes em 22.1.3 e 22.2.3', 'sm'), 300)
@d
def midi():
    return svg('MIDI: controle externo', B(15, 80, 120, 60, 'Controlador\n/ pedaleira', 'bxo') + L(135, 110, 265, 110) + T(200, 100, 'MIDI', 'b') +
        B(265, 80, 120, 60, 'Mesa', 'bxd', 'b tw') + L(325, 140, 325, 190, 'ln2') + B(255, 190, 140, 46, 'DAW', 'bxb') +
        T(110, 185, 'trocar snapshot', 'sm') + T(110, 205, 'mover faders e mutes', 'sm') + T(200, 285, 'mapas MIDI: X AIR (21.1.1) · M32 fixo (21.1.3)', 'sm'), 295)
@d
def clock():
    return svg('Taxa de amostragem e clock', B(20, 50, 165, 60, '44,1 kHz\náudio puro', 'bx') + B(215, 50, 165, 60, '48 kHz\náudio com vídeo', 'bxg') +
        T(200, 150, 'tudo no mesmo relógio, senão estala', 'lblr') + B(20, 175, 85, 36, 'L interno', 'bx', 'sm') + B(115, 175, 85, 36, 'A AES50', 'bxb', 'sm') +
        B(210, 175, 85, 36, 'B AES50', 'bxb', 'sm') + B(305, 175, 80, 36, 'C placa', 'bxo', 'sm') + T(200, 240, 'letra no topo da tela (X32/M32)', 'sm') +
        T(200, 272, 'mute o Main antes de trocar a taxa', 'b'), 285)
@d
def families(tall=False, q=False):
    xa = ['XR18', 'X18', 'MR18', 'XR16', 'XR12', 'MR12']; xm = ['X32', 'X32 Compact', 'X32 Producer', 'X32 Rack', 'M32', 'M32R', 'M32C']
    sa, sm_, ha, hm = (44, 40, 36, 33) if tall else (32, 30, 26, 24)
    g = B(10, 35, 180, 30, 'X AIR / M AIR', 'bxg') + B(210, 35, 180, 30, 'X32 / M32', 'bxb')
    g += ''.join(B(25, 75 + i * sa, 150, ha, s, 'bx', 'sm') for i, s in enumerate(xa))
    g += ''.join(B(225, 75 + i * sm_, 150, hm, s, 'bx', 'sm') for i, s in enumerate(xm))
    yb = 75 + 6 * sm_ + hm + 26
    return svg('Duas famílias, 13 mesas', g + qa(q)(T(100, yb, 'XR18 = MR18 · XR12 = MR12', 'sm')) + T(300, yb, 'mesmo motor, corpos diferentes', 'sm'), yb + 9)
@d
def checklist():
    it = ['Antes: firmware, rede, Mixer → PC', 'Passagem: ganho −18, low cut, EQ', 'Envios: retorno pré, efeito pós', 'Depois: salvar cena e backup']
    g = ''.join(f'<rect x="30" y="{50 + i * 55}" width="26" height="26" rx="4" class="bxg"/>' + OK(43, 63 + i * 55) + T(70, 69 + i * 55, s, 'b', 'start') for i, s in enumerate(it))
    return svg('Roteiro de trabalho', '<rect x="15" y="35" width="370" height="235" rx="10" class="panel"/>' + g + T(200, 295, 'resumo do roteiro', 'sm'), 305)
@d
def errors():
    return svg('Erro comum → correção', '<polygon points="70,40 125,140 15,140" class="bxr"/>' + T(70, 128, '!', 'xr') +
        B(150, 45, 235, 40, 'o que deu errado', 'bxr') + L(267, 85, 267, 110) + B(150, 110, 235, 40, 'por que acontece', 'bx') + L(267, 150, 267, 175) +
        B(150, 175, 235, 40, 'como corrigir', 'bxg') + T(200, 260, 'confira sempre no manual da sua mesa', 'lbl') + T(200, 286, '"(não confirmado)" = sem fonte oficial', 'sm'), 300)
@d
def legend(q=False):  # q = versão do quiz do cap. 00: as fitas de mesa e o "mesas onde vale" (a resposta) só aparecem depois da escolha
    A = qa(q)
    return svg('Como ler cada slide', B(20, 45, 170, 34, 'MANUAL', 'bxb') + T(205, 67, 'o que dizem os manuais', 'sm', 'start') +
        B(20, 95, 170, 34, 'NA PRÁTICA', 'bxg') + T(205, 117, 'como se opera ao vivo', 'sm', 'start') +
        A('<rect x="20" y="148" width="80" height="26" rx="13" class="bxg"/>', T(60, 166, 'XR18', 'sm'), '<rect x="110" y="148" width="80" height="26" rx="13" class="bxb"/>', T(150, 166, 'M32', 'sm'),
        T(205, 166, 'mesas onde vale', 'sm', 'start')) + T(20, 220, 'Termo novo: explicado na 1ª vez', 'b', 'start') +
        T(20, 248, '(não confirmado) = sem fonte segura', 'sm', 'start') + T(20, 276, 'tecla S: notas do professor', 'lbl', 'start'), 290)
@d
def inputs():
    return svg('Que entrada usar', B(15, 45, 120, 36, 'Microfone', 'bx') + L(135, 63, 230, 63) + B(230, 45, 155, 36, 'XLR / combo', 'bxb') +
        B(15, 105, 120, 36, 'Guitarra passiva', 'bx', 'sm') + L(135, 123, 230, 123) + B(230, 105, 155, 36, 'Hi-Z ou DI', 'bxo') +
        B(15, 165, 120, 36, 'Celular / PC', 'bx') + L(135, 183, 230, 183) + B(230, 165, 155, 36, '17/18 ou Aux In', 'bxg') +
        T(200, 245, 'cabo P10 longo (mais de ~6 m): use DI + XLR', 'sm') + T(200, 275, 'MR18: sem Hi-Z, use DI', 'lbl'), 290)
def panel(title, front, back, foot, tall=False, hl=None):
    ph, bh = (160, 104) if tall else (110, 64); y2 = 55 + ph; hl = hl or {}
    g = f'<rect x="10" y="40" width="380" height="{ph}" rx="8" class="panel"/>' + T(20, 58, front[0], 'zl', 'start')
    g += ''.join(B(20 + i * 92, 70, 84, bh, s, c, 'sm') for i, (s, c) in enumerate(front[1]))
    g += f'<rect x="10" y="{y2}" width="380" height="{ph}" rx="8" class="panel"/>' + T(20, y2 + 18, back[0], 'zl', 'start')
    g += ''.join(B(20 + i * 92, y2 + 30, 84, bh, s, c, 'sm') for i, (s, c) in enumerate(back[1]))
    for (r, i), k in hl.items():   # rodada 3: o bullet acende a peça de que fala (r = 0 frente, 1 traseira, 2 rodapé)
        g += HL(14, y2 + ph + 6, 372, 28, k) if r == 2 else HL(15 + i * 92, (70 if r == 0 else y2 + 30) - 5, 94, bh + 10, k)
    return svg(title, g + T(200, y2 + ph + 25, foot, 'sm'), y2 + ph + 35)
@d
def panel_xr18(hl=None):
    return panel('XR18, X18, MR18: conexões', ('ENTRADAS', [('1–16\ncombo', 'bxb'), ('17/18\nlinha', 'bxg'), ('Hi-Z\n1–2', 'bxo'), ('USB B\n18×18', 'bx')]),
                 ('SAÍDAS E REDE', [('Aux\n1–6', 'bxg'), ('Main\nL/R', 'bxb'), ('Ethernet\nREMOTE', 'bx'), ('Ultranet\nMIDI', 'bxo')]), '', hl=hl)  # rodada 6: sem rodapé (X18 e Hi-Z estão nos bullets e em 2.2.1)
@d
def x18xr18():  # 1.2.3 (rodada 3): dois formatos, o mesmo motor (antes repetia o painel de conexões de 1.1.5)
    g = T(100, 40, 'X18', 'b') + T(300, 40, 'XR18', 'b')
    g += '<rect x="14" y="52" width="172" height="96" rx="8" class="bxd"/>' + ''.join(fader(34 + i * 22, 70, 60, 12 + (i * 19) % 40) for i in range(7))
    g += '<rect x="226" y="66" width="160" height="70" rx="6" class="bxd"/>' + ''.join(C(246 + i * 20, 86, 6, 'knob') for i in range(7)) + ''.join(f'<rect x="{240 + i * 20}" y="104" width="12" height="18" rx="2" class="bx"/>' for i in range(7))
    g += T(100, 168, 'faders físicos', 'sm') + T(306, 168, 'stagebox: só o app', 'sm')
    g += P('M100 178 L100 196 L176 210', 'ln') + P('M306 178 L306 196 L226 210', 'ln')
    g += B2(70, 212, 260, 62, 'mesmo motor\n18 entradas · 16 canais · FX', 'bxo')
    g += O(1, T(200, 300, 'o processamento é o mesmo', 'lbl'))
    return svg('X18 × XR18: o mesmo motor', g, 310)
@d
def panel_xr16():
    return panel('XR16, XR12, MR12: conexões', ('ENTRADAS', [('combo\n1–8 / 1–4', 'bxb'), ('linha\n9–16 / 5–12', 'bxg'), ('Hi-Z 15–16\n/ 11–12', 'bxo'), ('USB A\npendrive', 'bx')]),
                 ('SAÍDAS E REDE', [('Aux\n4 / 2', 'bxg'), ('Main\nL/R', 'bxb'), ('Ethernet\nREMOTE', 'bx'), ('MIDI\nIN/OUT', 'bxo')]), 'XR16 / XR12 e MR12 · sem Ultranet')
@d
def surface(tall=False):
    return panel('X32 e M32: superfície e traseira', ('SUPERFÍCIE', [('Channel\nStrip', 'bxo'), ('Faders de\nentrada', 'bxb'), ('Tela e\nmonitor', 'bx'), ('Group/Bus\n/Main', 'bxg')]),
                 ('TRASEIRA', [('XLR in\n/ out', 'bxb'), ('AES50\nA / B', 'bxo'), ('Ultranet\nMIDI', 'bx'), ('placa\nde expansão', 'bxg')]), '16 faders na X32 e M32, 8 nas demais', tall)
@d
def x32rack():  # 1.1.6 (rodada 3): o que a tabela compara, desenhado: console de mesa × rack 3U (faders e tela)
    def bank(x0, y0):  # 16 + 8 + Main, faders pequenos em posições variadas
        g, x = '', x0
        for grp, n in ((0, 16), (1, 8), (2, 1)):
            for i in range(n):
                g += f'<rect x="{x - 1.2:.1f}" y="{y0}" width="2.4" height="54" rx="1.2" class="track"/><rect x="{x - 3:.1f}" y="{y0 + 8 + (i * 17 + grp * 11) % 34}" width="6" height="7" rx="1" class="{"capo" if grp == 2 else "cap"}"/>'
                x += 6.6
            x += 7
        return g
    g = T(104, 40, 'X32', 'b') + T(304, 40, 'X32 Rack', 'b') + L(204, 28, 204, 330, 'sep')
    g += '<rect x="6" y="54" width="196" height="138" rx="9" class="bxd"/>' + bank(18, 128)
    g += '<rect x="122" y="64" width="70" height="46" rx="3" style="fill:#05070a;stroke:var(--accent);stroke-width:1.8"/>' + T(157, 93, '7"', 'lbl')
    g += ''.join(C(22 + i * 16, 76, 5, 'knob') for i in range(6)) + ''.join(C(22 + i * 16, 98, 5, 'knob') for i in range(6))
    g += '<rect x="216" y="86" width="180" height="78" rx="4" class="bxd"/>' + L(222, 112, 390, 112, 'sep') + L(222, 138, 390, 138, 'sep')
    g += '<rect x="230" y="96" width="44" height="30" rx="3" style="fill:#05070a;stroke:var(--accent);stroke-width:1.8"/>' + T(252, 116, '5"', 'lbl')
    g += ''.join(C(292 + i * 18, 106, 5, 'knob') for i in range(5)) + ''.join(C(292 + i * 18, 150, 4, 'knob') for i in range(5))
    g += T(104, 214, 'console de mesa', 'sm') + T(304, 214, 'rack 3U', 'sm')
    g += L(10, 236, 390, 236, 'sep')
    g += T(104, 270, '25', 'bb') + T(104, 292, 'faders motorizados', 'sm') + T(304, 270, 'nenhum', 'bb') + T(304, 292, 'fader: mixa pelo app', 'lbl')
    g += '<rect x="226" y="246" width="156" height="56" rx="9" class="hl"/>'
    g += T(104, 322, 'tela de 7"', 'sm') + T(304, 322, 'tela de 5"', 'sm')
    return svg('X32 × X32 Rack: faders e tela', g, 336)
@d
def panel_rack():
    return panel('X32 Rack: frente e traseira', ('FRENTE', [('tela\n5"', 'bx'), ('Channel\nSelect', 'bxo'), ('USB\ngravador', 'bxg'), ('Talk\nfone', 'bx')]),
                 ('TRASEIRA', [('XLR in\n1–16', 'bxb'), ('XLR out\n1–8', 'bxb'), ('AES50\nA / B', 'bxo'), ('X-USB\nUltranet', 'bxg')]), '')  # rodada 6: operar pelo app fica em 4.2.9
@d
def panel_m32c():
    return panel('M32C: núcleo de rack', ('FRENTE', [('USB A', 'bxg'), ('LCD\n128×64', 'bx'), ('LEDs\nAES50', 'bxo'), ('SELECT\nPOWER', 'bx')]),
                 ('TRASEIRA', [('placa\nDN32-USB', 'bxg'), ('AES50\nA / B', 'bxo'), ('Ultranet\nMIDI', 'bx'), ('Monitor\nTalkback', 'bxb')]), 'microfones entram no stagebox (DL16, DL32)')
@d
def quiz():
    return svg('Quiz rápido', '<rect x="140" y="40" width="120" height="110" rx="20" class="bxo"/>' + T(200, 128, '?', 'big') +
        ''.join(f'<rect x="60" y="{175 + i * 34}" width="280" height="26" rx="6" class="bx"/>' + T(80, 193 + i * 34, 'ABC'[i], 'b', 'start') for i in range(3)), 290)  # neutro: nada destacado antes do clique

# ---------------------------------------------------------------- diagramas por assunto (revisão 2: nada de molde genérico fora de contexto)
@d
def terms():  # 0.3 e glossário: canal, bus, fader, mute group (rodada 4: cada seta chega num ponto do Bus; colchete do mute group na cor do grupo)
    ch = ''.join(B(12, 48 + i * 62, 136, 40, s_) for i, s_ in enumerate(('Canal 1: voz', 'Canal 2: violão', 'Canal 3: teclado')))
    g = S(1, ch)
    g += S(2, *[L(148, 68 + i * 62, 192, 116 + i * 14, 'ln') for i in range(3)], B(194, 103, 96, 54, 'Bus\n(soma)', 'bxo'))
    g += S(3, L(290, 130, 330, 130, 'ln'), fader(352, 60, 140, 50, 'capo'), T(352, 230, 'Fader', 'b'), T(352, 248, 'volume', 'sm'))
    g += S(4, '<rect x="6" y="40" width="148" height="120" rx="9" class="frame red"/>', P('M6 100 L-6 100 L-6 271 L10 271', 'ctl red'), B(12, 252, 160, 38, 'Mute group: 1 botão', 'bxr', 'sm'))
    return svg('Os quatro termos num desenho', g, 300)
@d
def avisos():  # 0.4: três avisos
    return pairs('Três avisos para o curso todo', [('Tutorial de\numa mesa', 'serve para as\nirmãs da família', 'bx', 'bxg'),
                 ('Firmware novo', 'telas e apps\njá mudaram', 'bx', 'bxo'), ('Informação\nque circula', 'pode estar errada:\nconfira o manual', 'bx', 'bxr')], foot='exemplos de erro em 24.2.2', h=290)
@d
def siblings():  # 1.1.2: pares entre as marcas
    return pairs('Quem é irmã de quem', [('XR18', 'MR18', 'bx', 'bx', '='), ('XR12', 'MR12', 'bx', 'bx', '='), ('X32', 'M32 / LIVE', 'bx', 'bx', '='),
                 ('X32 Producer', 'M32R / LIVE', 'bx', 'bxg', '≈'), ('sem par', 'M32C', 'bxg', 'bxg', '·'), ('X18 · XR16\nX32 Rack', 'sem par', 'bx', 'bxg', '·')], heads=('BEHRINGER', 'MIDAS'),
                 foot='= gêmeas · ≈ mesma ficha, sem par oficial', h=400, steps=False, rhmax=62).replace("aria-label=\"Quem é irmã de quem\"", 'aria-label="Pares Behringer × Midas"').replace('>Quem é irmã de quem<', '>Pares Behringer × Midas<')
@d
def xairidea():  # 1.1.3: X AIR = caixa sem faders + Wi-Fi + app
    g = S(1, B2(10, 40, 170, 96, 'XR18 · MR18\nsem faders', 'bxd'), T(95, 162, 'a mesa fica no palco', 'b'))
    g += S(2, P('M188 78 q10 13 0 26 M200 70 q17 21 0 42', 'mk'), B2(226, 40, 164, 96, 'tablet, celular\nou computador', 'bx'),
           T(308, 162, 'Wi-Fi interno', 'lbl'), T(308, 182, 'roteador: opcional', 'sm'))
    g += S(4, *[B2(10 + i * 130, 210, 120, 70, a, 'bx') for i, a in enumerate(('XR18', 'XR16', 'XR12'))], T(200, 304, 'muda o número de conectores', 'sm'))  # checklist P04: os pré-amps por modelo ficam só no explorador
    return svg('Mesa no palco, controle no aparelho', g, 312)
@d
def famfeat():  # 1.1.7: o que existe em cada família
    # rodada 6: efeitos e DCA saíram (os números já estão em 1.1.3 e 1.1.4); fica o que só esta tabela compara
    # checklist P05: faders e Wi-Fi saíram (já estão em 1.1.3 e 1.1.4); a tabela fica só com o que é exclusivo de uma família
    return grid3('O que existe em cada família', ('X AIR', 'X32/M32'), [('Matrizes', 'não', '6'), ('Delay e talkback', 'não', 'sim'), ('Automix', '2 grupos', 'fw 3+: 1–8'),
                 ('Crossover e LCR', 'não', 'sim'), ('Oscilador e AES50', 'não', 'sim')], h=330, steps=False, rhmax=56)
@d
def xrmr():  # 1.2.6: Midas × Behringer
    return grid3('MR × XR: o que muda', ('XR18/\nXR12', 'MR18/\nMR12'), [('Software', '"99% idêntico"', ''), ('Pré-amps', 'desenho Midas', 'MIDAS PRO'),
                 ('Conectores', 'comuns', 'Neutrik'), ('Hi-Z', 'sim', 'MR18: não')], h=280)
@d
def x32bodies():  # 1.2.7: mesmo cérebro, corpos diferentes
    g = B(10, 40, 380, 34, 'mesmo motor: 40 entradas de mix · 25 buses', 'bxb')
    bodies = [('X32', '25 faders'), ('X32 Compact', '17 faders'), ('X32 Producer', '17 faders · rack 19"'), ('X32 Rack', 'sem faders · 3U')]
    for i, (a, b) in enumerate(bodies):
        y = 92 + i * 50
        g += S(2 if a == 'X32 Producer' else 1, B(10, y, 150, 38, a, 'bxo' if a == 'X32 Producer' else 'bx'), L(200, 74, 200, 92, 'sep') if i == 0 else '', T(176, y + 24, b, 'b' if a == 'X32 Producer' else 'sm', 'start'))
    return svg('Um cérebro, quatro corpos', g, 300)
@d
def m32fam():  # 1.2.8 (passada final: os 4 bullets cabem num slide só, então as 4 linhas ficam baixas e a letra continua ≥ 20 px)
    row = lambda y, a, b, sub, mid, cb='bx': (B2(10, y, 120, 62, a, 'bxb') + B2(186, y, 204, 62, b + '\n' + sub, cb) +
                                             (L(132, y + 31, 184, y + 31, 'ln2') if mid == '↔' else T(158, y + 39, mid, 'mid')))
    g = S(1, row(36, 'M32', 'X32', 'por dentro', '='))
    g += S(2, row(108, 'M32R', 'X32 Producer', 'pela ficha', '≈', 'bxg'))
    g += S(3, row(180, 'M32C', 'M32 em 1U', 'USB · talkback', '='))
    g += S(4, row(252, 'M32C', 'stagebox', 'DL16 · DL32 · S16', '↔', 'bxo'))
    return svg('M32 por dentro', g, 324)
@d
def xr1612():  # 1.2.4 (enxugamento): XR16 e XR12 lado a lado; o USB das duas no fim
    g = S(1, B(10, 36, 380, 64, 'XR16 · 8 pré-amps · Hi-Z 15–16\nlinhas 9–16 · 4 Aux', 'bx', 'sm'))
    g += S(2, *[C(24 + i * 15, 136, 6, 'knob') for i in range(12)], T(106, 168, 'XR12: 12 entradas', 'sm'), L(206, 136, 232, 136, 'ln'),
           *[f'<rect x="{240 + i * 9.4:.1f}" y="122" width="6" height="28" rx="2" class="bar"/>' for i in range(16)], T(315, 170, '16 canais · 6 buses', 'b'))
    g += S(3, B(10, 190, 380, 40, '"faltam conectores, não recursos"', 'bxo', 'b'))
    g += S(4, B(10, 250, 92, 38, 'USB A', 'bxo', 'b'), L(102, 269, 136, 269, 'ln'), B(138, 250, 100, 38, 'pendrive', 'bx', 'sm'), T(250, 274, 'só estéreo', 'lbl', 'start'))
    return svg('XR16 e XR12: o mesmo motor, menos portas', g, 300)
@d
def bodies7():  # 1.1.4 (enxugamento): o mesmo motor em sete corpos, uma linha por corpo
    g = ''  # rodada 6: sem a faixa "mesmo motor" (é o 1º bullet); o desenho fica com o que muda de corpo para corpo
    rows = [('X32', '25 faders · 32 pré'), ('X32 Compact', '17 faders · 16 pré'), ('X32 Producer', '17 faders · rack 19"'), ('X32 Rack', 'sem faders · 16 pré · 3U'),
            ('M32 / LIVE', '25 faders · MIDAS PRO'), ('M32R / LIVE', '17 faders · rack'), ('M32C', '1U · áudio só por AES50')]
    for i, (a, b) in enumerate(rows):
        y = 34 + i * 44; k = 3 if a == 'M32 / LIVE' else 4 if a == 'M32R / LIVE' else 1
        g += S(k, B(10, y, 136, 36, a, 'bxb' if a.startswith('M32') else 'bx', 'sm'), T(158, y + 24, b, 'sm', 'start'))
    return svg('Corpos e faders por modelo', g, 346)
@d
def motorbodies():  # 1.1.4 (checklist P04): mesmo motor, corpos diferentes; os números por modelo ficam só no explorador
    g = B2(110, 34, 180, 64, 'mesmo motor\nX32 · M32', 'bxo')
    bodies = [('console', 14), ('compacta', 8), ('rack', 0), ('1U', 0)]
    for i, (lab, nf) in enumerate(bodies):
        x = 6 + i * 98; w = 88
        g += P(f'M200 98 L{x + w / 2} {190 if lab == "1U" else 150}', 'ln')
        if lab == '1U':
            g += f'<rect x="{x}" y="196" width="{w}" height="22" rx="4" class="bxd"/>'
        elif lab == 'rack':
            g += f'<rect x="{x}" y="156" width="{w}" height="62" rx="5" class="bxd"/><rect x="{x + 12}" y="168" width="36" height="24" rx="3" class="bx"/>'
        else:
            g += f'<rect x="{x}" y="156" width="{w}" height="62" rx="5" class="bxd"/>' + ''.join(L(x + 8 + j * (w - 16) / (nf - 1), 176, x + 8 + j * (w - 16) / (nf - 1), 210, 'grid') for j in range(nf))
        g += T(x + w / 2, 246, lab, 'b')
    g += T(x + w / 2, 268, 'áudio por AES50', 'sm')
    return svg('Mesmo motor, corpos diferentes', g, 282)
@d
def x32net():  # 3.1.3 (enxugamento): rede da X32/M32 sem roteador no desenho: a tela Network e os encoders
    g = '<rect x="10" y="34" width="380" height="120" rx="9" class="panel"/>' + T(30, 58, 'SETUP › NETWORK', 'zl', 'start')
    g += B(26, 70, 110, 30, 'IP', 'bxo', 'sm') + B(146, 70, 110, 30, 'Subnet', 'bx', 'sm') + B(266, 70, 110, 30, 'Gateway', 'bx', 'sm')
    g += T(200, 134, 'ex.: 192.168.0.201 · 255.255.255.0', 'b')
    g += S(1, *[C(45 + i * 62, 192, 16, 'knob') for i in range(6)], T(45, 228, 'campo', 'sm'), T(169, 228, 'números (2–5)', 'sm'), T(355, 228, 'confirma', 'sm'))
    g += S(3, B(10, 252, 380, 40, 'M32C: SELECT › Setup › DHCP ligado', 'bxb', 'sm'))
    return svg('Tela Network: um encoder por campo', g, 300)
@d
def day3():  # 23.2.4 (rodada 6): três fases, dois itens curtos cada, letra de corpo (o slide tem um bullet só)
    g = ''
    for i, (k, a, b) in enumerate((('ANTES', 'firmware em dia · show pronto', 'rede própria · Mixer → PC'),
                                   ('NA PASSAGEM', 'mute antes do 48 V', 'ganho em −18 · retornos pré'),
                                   ('DEPOIS', 'salve a cena e o backup', 'caixas desligadas antes da mesa'))):
        y = 34 + i * 110
        g += f'<rect x="10" y="{y}" width="380" height="100" rx="9" class="panel"/>' + T(24, y + 24, k, 'zl', 'start') + T(24, y + 56, a, 'b', 'start') + T(24, y + 84, b, 'b', 'start')
    return svg('Antes, na passagem, depois', g, 360)
@d
def mantime():  # 26.1.1 (enxugamento): o ano de cada manual; tudo que veio depois de 2018 é firmware novo
    rows = [('2013', 'X32 Producer'), ('2014', 'X32 Rack'), ('2015', 'M32R'), ('2016', 'X AIR, M AIR, X32, X32 Compact'), ('2018', 'M32 e M32C'), ('2023', 'M32R LIVE (guia rápido)')]
    g = ''.join(B(10, 36 + i * 42, 70, 32, y, 'bxo' if y > '2018' else 'bx', 'b') + T(94, 58 + i * 42, s, 'b' if y > '2018' else 'sm', 'start') for i, (y, s) in enumerate(rows))
    g += B(10, 36 + len(rows) * 42 + 6, 380, 40, 'depois de 2018: firmware novo, fora dos manuais', 'bxr', 'sm')
    return svg('Os manuais e o ano de cada um', g, 36 + len(rows) * 42 + 56)
@d
def xaxm():  # 1.2.9: diferenças citadas
    return grid3('X AIR × X32/M32 na prática', ('X AIR', 'X32/M32'), [('GEQ dos buses', 'sem gastar slot', 'gasta slot'),
                 ('Crossover, delay', 'não', 'sim'), ('Porta OSC', '10024', '10023'), ('Entre famílias', 'só ligação analógica', '')], h=280)
@d
def usedbuy():  # 1.2.10 (passada final: régua da garantia e os 4 cartões num slide só)
    g = S(1, T(10, 40, 'GARANTIA (LOJAS DOS EUA)', 'zl', 'start'), '<rect x="20" y="84" width="120" height="22" rx="4" class="zgr"/>', '<rect x="140" y="84" width="240" height="22" rx="4" class="zg"/>',
          '<rect x="20" y="84" width="40" height="22" rx="4" class="zy"/>', T(20, 130, 'compra', 'sm', 'start'), T(40, 74, '90 dias: registre', 'lbl', 'start'),
          T(140, 130, '1 ano', 'sm'), T(380, 130, '3 anos', 'b', 'end'), T(380, 74, 'registrada: 1 → 3 anos', 'b', 'end'))
    g += B2(10, 146, 185, 70, 'Brasil?\ndistribuidor oficial', 'bxg', 'b2') + B2(205, 146, 185, 70, 'importada\nconserto incerto', 'bxr', 'b2')
    g += B2(10, 226, 185, 70, 'usada: faders\ne encoders', 'bx', 'b2') + B2(205, 226, 185, 70, 'X32 Compact usada\n1 h de teste', 'bxo', 'b2')
    return svg('Antes de comprar ou usar', g, 306)
@d
def remote3(m=(1, 2, 3, 4)):  # 3.1.1 e 3.2.2: os três modos da chave REMOTE; m = bullet que acende (chave, Ethernet, Wi-Fi Client, Access Point)
    g = S(m[0], B(110, 34, 180, 32, 'chave REMOTE', 'bxo'), *[C(150 + i * 50, 76, 5, 'dotc') for i in range(3)])
    cols = [('ETHERNET', 70, 'roteador\nou notebook', 'bx', 'mais confiável'), ('WI-FI CLIENT', 200, 'roteador\ndo local', 'bxg', 'rede que já existe'),
            ('ACCESS POINT', 330, 'tablets\n(até 4)', 'bx', '192.168.1.1')]
    for i, (h, x, dev, c, foot) in enumerate(cols):
        part = T(x, 104, h, 'zlc') + B(x - 50, 114, 100, 34, 'Mesa', 'bxd', 'b tw')
        part += L(x, 148, x, 196, 'ln2') if i == 0 else P(f'M{x - 12} 166 q12 -10 24 0 M{x - 18} 178 q18 -14 36 0', 'mk')
        part += B(x - 58, 198, 116, 44, dev, c, 'sm') + T(x, 266, foot, 'sm')
        g += S(m[i + 1], part)
    return svg('Os três modos da chave REMOTE', g + L(135, 96, 135, 270, 'sep') + L(265, 96, 265, 270, 'sep'), 285)
@d
def firstconn():  # 3.1.2
    return flow('Primeira conexão, passo a passo', ['Instale o app (X AIR / M AIR)', 'REMOTE em ACCESS POINT; ligue', 'RESET 2 s: rede padrão',
                'Wi-Fi com o nome da mesa', 'Abra o app: 192.168.1.1'], h=320, steps=[0] * 5)  # rodada 6: desenho fixo (os bullets são de aparelhos diferentes)
@d
def router(v=1):  # 3.1.3, 3.2.4, 3.2.5: roteador externo; v=2 (3.2.5, rodada 3): X32/M32, cada bullet acende a sua peça
    if v == 2:
        g = B(10, 60, 100, 50, 'X32 / M32', 'bxd', 'b tw') + L(110, 85, 168, 85, 'ln2') + T(139, 76, 'cabo', 'sm') + T(60, 136, 'sem Wi-Fi', 'lblr')
        g += B(170, 50, 110, 70, 'Roteador', 'bxg') + B(176, 96, 46, 18, 'LAN', 'bxo', 'tiny') + B(228, 96, 46, 18, 'WAN', 'bxr', 'tiny') + X(251, 128)
        g += P('M290 72 q10 13 0 26 M302 64 q17 21 0 42', 'mk') + B(325, 40, 65, 34, 'tablet') + B(325, 96, 65, 34, 'celular')
        g += T(200, 186, 'mesa: IP fixo alto (192.168.1.201)', 'b') + T(200, 212, 'até 10 controles ao mesmo tempo', 'sm') + T(200, 238, 'M32C: aceita DHCP', 'sm')
        g += HL(4, 52, 112, 96, 1) + HL(172, 90, 54, 30, 2) + HL(40, 168, 320, 26, 3) + HL(320, 34, 76, 102, 4) + HL(110, 222, 180, 24, 5)
        return svg('X32/M32: rede só por cabo', g, 260)
    g = B(10, 60, 100, 50, 'Mesa', 'bxd', 'b tw') + L(110, 85, 168, 85, 'ln2') + T(139, 76, 'cabo', 'sm')
    g += B(170, 50, 110, 70, 'Roteador', 'bxg') + B(176, 96, 46, 18, 'LAN', 'bxo', 'tiny') + B(228, 96, 46, 18, 'WAN', 'bxr', 'tiny') + X(251, 128)
    g += P('M290 72 q10 13 0 26 M302 64 q17 21 0 42', 'mk') + B(325, 40, 65, 34, 'tablet') + B(325, 96, 65, 34, 'celular')
    g += T(200, 182, 'mesa na porta LAN, nunca na WAN', 'b') + T(200, 208, 'IP fixo alto: 192.168.1.201', 'sm') + T(200, 228, 'os aparelhos por DHCP', 'sm')
    g += T(200, 268, 'X32/M32: sem Wi-Fi interno, só assim', 'lbl')
    return svg('Roteador externo: a rede do show', g, 285)
@d
def oscproto():  # 3.1.5
    g = B(15, 60, 110, 56, 'App', 'bxb') + B(275, 60, 110, 56, 'Mesa', 'bxd', 'b tw') + L(125, 80, 275, 80, 'ln') + L(275, 98, 125, 98, 'ln')
    g += T(200, 72, '/ch/01/mix/fader', 'mono') + T(200, 122, 'a mesa responde', 'sm')
    g += B(15, 160, 175, 50, 'X AIR: porta 10024\nliga/desliga OSC', 'bx', 'sm') + B(210, 160, 175, 50, 'X32/M32: porta 10023\ntudo em OSC', 'bx', 'sm')
    g += T(200, 260, 'OSC: a "língua" de rede dos apps', 'lbl')
    return svg('OSC: como o app fala com a mesa', g, 280)
@d
def usbctl():  # 3.2.1
    g = B(10, 110, 110, 70, 'Notebook', 'bx') + B(280, 110, 110, 70, 'Mesa', 'bxd', 'b tw')
    g += S(1, L(120, 160, 278, 160, 'lnx'), T(200, 180, 'só USB: não acha', 'lblr'))
    g += S(2, L(120, 126, 278, 126, 'ln2'), T(200, 118, 'rede: controle', 'lbl'))
    g += S(3, T(200, 210, 'USB: áudio e MIDI', 'b'))
    g += S(4, T(200, 240, 'controlar e tocar: rede + USB', 'sm'))
    g += S(5, B(10, 40, 240, 34, 'X18: rede na porta Ultranet ✕', 'bxr', 'sm'))
    return svg('Que cabo faz o quê', g, 260)
@d
def wifi():  # 3.2.3
    g = '<rect x="10" y="40" width="150" height="110" rx="8" class="panel"/>' + T(85, 58, 'RACK', 'zl') + B(25, 70, 120, 40, 'Mesa', 'bxd', 'b tw')
    g += L(132, 70, 132, 52, 'ln0') + T(85, 136, 'antena bloqueada', 'sm')
    g += ''.join(f'<rect x="{200 + (i % 5) * 38}" y="{50 + (i // 5) * 44}" width="22" height="34" rx="4" class="phone"/>' for i in range(10))
    g += T(295, 160, 'celulares e mics sem fio', 'sm') + B(200, 172, 190, 34, '2,4 GHz lotado', 'bxr')
    g += B(10, 222, 180, 40, 'passagem: funciona', 'bxg', 'sm') + B(210, 222, 180, 40, 'público: cai', 'bxr', 'sm')
    g += T(200, 292, 'se o Wi-Fi cair, o som continua', 'lbl')
    return svg('Wi-Fi interno: o problema nº 1', g, 300)
@d
def netgood():  # 3.2.6 (rodada 4): os três hábitos desenhados, um por coluna
    g = S(1, T(65, 40, 'Reserva', 'b'), '<rect x="30" y="76" width="70" height="50" rx="4" class="bx"/>', P('M20 130 L110 130 L118 142 L12 142 Z', 'wedge'),
          B(88, 190, 54, 30, '', 'bxg'), P('M65 142 L65 205 L86 205', 'ln'), T(65, 262, 'um aparelho', 'b'), T(65, 284, 'no cabo', 'sm'))
    g += S(2, T(200, 40, 'No alto', 'b'), L(200, 122, 200, 236, 'ln0'), L(176, 236, 224, 236, 'ln0'), B(174, 94, 52, 28, '', 'bxg'), P('M186 84 q14 -12 28 0 M180 74 q20 -18 40 0', 'mk'),
          L(220, 120, 238, 182, 'lnd'), C(244, 196, 7, 'person'), P('M233 226 a11 11 0 0 1 22 0 Z', 'person'), T(200, 262, 'visada para', 'b'), T(200, 284, 'a técnica', 'sm'))
    # rodada 3: o alvo da visada fica na coluna 2; na 3, uma pessoa anda pela sala e mede o sinal em pontos (antes: círculos e til abstratos)
    g += S(3, T(335, 40, 'Alcance', 'b'), *[C(335, 118, r, 'frame') for r in (22, 40)], B(323, 106, 24, 24, '', 'bxg'),
          C(296, 196, 7, 'person'), P('M285 226 a11 11 0 0 1 22 0 Z', 'person'), P('M310 220 Q 344 176 386 212', 'lnd'),
          *[C(x_, y_, 4.5, 'dot') for x_, y_ in ((331.1, 200.8), (349.9, 195.8), (369.5, 200.8))], T(335, 262, 'teste andando', 'b'), T(335, 284, 'antes do evento', 'sm'))
    return svg('Rede de show: três hábitos', g, 294)
@d
def netsec():  # 3.2.8 (rodada 4): AP com cadeado, porta Ethernet aberta, mesa travada
    lock = lambda cx, cy, op, c: f'<rect x="{cx - 16}" y="{cy}" width="32" height="26" rx="4" class="{c}"/>' + P(f'M{cx - 9} {cy} v-9 a9 9 0 0 1 18 0' + (' v-5' if op else ' v9'), 'mk')
    g = S(1, T(65, 40, 'Access Point', 'b'), B(35, 124, 60, 34, '', 'bxg'), P('M48 114 q17 -18 34 0 M40 102 q25 -26 50 0', 'mk'), lock(65, 190, False, 'bxo'),
          T(65, 252, 'vem aberto:', 'sm'), T(65, 274, 'ponha senha', 'lbl'))
    g += S(2, T(200, 40, 'Porta Ethernet', 'b'), P('M176 112 h48 v36 h-11 v10 h-26 v-10 h-11 Z', 'wedge'), lock(200, 190, True, 'bxr'),
          T(200, 252, 'sem senha:', 'sm'), T(200, 274, 'quem pluga, controla', 'lblr'))
    g += S(3, T(335, 40, 'A mesa', 'b'), B(298, 104, 74, 52, 'Mesa', 'bxd', 'b tw'), lock(335, 190, False, 'bxo'),
          T(335, 252, 'saiu de perto?', 'sm'), T(335, 274, 'trave a mesa', 'lbl'))
    return svg('Rede e mesa protegidas', g, 284)
@d
def appscreen(m=None, tabs=None):  # 4.1.1 e telas dos apps; m = (faders, faixa do canal, mute) -> bullet; tabs = (abas, número, canal certo) -> bullet (4.2.2)
    m = m or (0, 0, 0); o = 40 if tabs else 0
    g = f'<rect x="10" y="34" width="380" height="{258 + o}" rx="10" class="panel"/>'
    if tabs:
        g += B(22, 44, 96, 28, 'Mixer', 'bxo', 'b') + B(124, 44, 96, 28, 'Channel', 'bx', 'b') + T(232, 63, 'geral × um canal', 'sm', 'start') + HL(16, 38, 210, 40, tabs[0])
    strips = range(8)
    g += S(m[1], *[f'<rect x="{22 + i * 40}" y="{46 + o}" width="34" height="34" rx="3" class="{"bxo" if tabs and i == 0 else "bx"}"/>' for i in strips], T(200, 98 + o, 'faixa do canal: só estado (48 V, envios, pan)', 'tiny' if not tabs else 'sm'))
    g += S(m[0], *[fader(39 + i * 40, 110 + o, 120, 30 + (i * 23) % 80) for i in strips], T(200, 280 + o, '8 de 16 canais na tela · Aux In (USB) · FX', 'sm'))
    g += S(m[2], *[f'<rect x="{24 + i * 40}" y="{236 + o}" width="30" height="12" rx="2" class="{"mute" if i in (2, 5) else "bx"}"/>' for i in strips], T(338, 30, 'mute = vermelho', 'lblr'))
    if tabs: g += HL(17, 41 + o, 44, 44, tabs[1]) + HL(15, 39 + o, 48, 216, tabs[2])
    return svg('Mixer × Channel no Edit' if tabs else 'A tela principal do app', g, 300 + o)   # rodada 3: título próprio na versão com abas (4.2.2)
@d
def appswap():  # 4.2.7
    return pairs('Apps antigos e substitutos', [('App X AIR\n(tablet)', 'não abre em\nsistemas 2022+', 'bx', 'bxr'), ('M32-Mix\ne M32-Q', 'descontinuados', 'bx', 'bxr'),
                 ('tablet / celular', 'MX-Mix / MX-Q', 'bx', 'bxg'), ('Apps de\ncomputador', 'continuam\nos originais', 'bx', 'bxb')], h=300)
@d
def copypaste(v=1):  # 4.1.5 e 4.2.12 (v=2, rodada 3: destaque no ganho e no Recall scope)
    mods = ['gate', 'EQ', 'comp', 'envios', 'nome', 'ganho']
    g = B(10, 40, 120, 30, 'Canal 1', 'bxb') + B(270, 40, 120, 30, 'Canal 2', 'bxb') + L(130, 55, 268, 55, 'ln') + T(200, 46, 'copiar → colar', 'sm')
    for i, m_ in enumerate(mods):
        y = 82 + i * 30
        g += B(20, y, 100, 24, m_, 'bx', 'sm') + B(270, y, 92, 24, m_, 'bxr' if m_ == 'ganho' else 'bxg', 'sm')
        g += X(380, y + 6) if m_ == 'ganho' else OK(380, y + 6)   # pendência 0.3: a marca fica fora da caixa, numa coluna própria
    g += T(200, 162, 'o ganho', 'lblr') + T(200, 180, 'não vai junto', 'lblr')
    if v == 2:
        g += HL(262, 228, 132, 32, 1) + B(90, 266, 220, 30, 'Recall scope: o que carrega', 'bxo', 'sm') + S(2, T(200, 312, 'na cena, marque o que volta', 'sm'))
        return svg('Copiar sem levar o ganho', g, 320)
    g += B(130, 266, 140, 30, 'preset de canal', 'bxo', 'sm') + T(200, 312, 'salvar, carregar, apagar', 'sm')
    return svg('Copiar canal e presets', g, 320)
@d
def template():  # 4.2.13: preparar o show em casa
    return flow('O show preparado em casa', ['Cena em branco (sem herança)', 'Nomes, cores, ganho, envios', 'FX e EQ de partida', 'Salvar como cena modelo',
                'No culto: carregar o modelo'], steps=[2, 1, 1, 2, 2], h=320)
@d
def gainsteps():  # 5.2.3: ajustar na passagem de som
    return flow('Do fader fechado ao monitor', ['Fader e envios abaixados', 'Fonte no volume real', 'Ganho: média ~ −18 dBFS', 'Desmute, fader, monitores'], steps=[1, 2, 2, 3], h=290)
@d
def gainfader():  # 5.2.4: não mixe no ganho
    g = S(1, C(100, 124, 58, 'knob'), '<line x1="100" y1="124" x2="72" y2="76" class="needle"/>', T(100, 226, 'Ganho', 'b'), T(100, 246, 'ajuste e esqueça', 'sm'),
          fader(300, 48, 160, 70, 'capo'), T(300, 226, 'Fader', 'b'), T(300, 246, 'aqui se mixa', 'sm'), L(170, 124, 270, 124, 'sep'))
    g += S(2, B(10, 268, 380, 40, 'X32/M32: ganho salvo na cena → safe', 'bxo', 'b'))
    return svg('Ganho × fader', g, 320)
@d
def gainruler():  # 5.2.5: régua de ganhos de partida
    x = lambda db: 30 + (db - 10) * 11.5
    g = L(30, 250, 375, 250, 'axis') + ''.join(L(x(v), 250, x(v), 258, 'tick') + T(x(v), 276, f'{v}', 'sm') for v in range(10, 41, 5)) + T(375, 296, 'ganho (dB)', 'sm', 'end')
    bands = [(1, 'SM58 (dinâmico)', 25, 30, 'bxo'), (2, 'Lapela', 15, 20, 'bxg'), (2, 'Condensador', 25, 35, 'bxb'), (3, 'DL32 (voz)', 25, 32, 'bx')]
    for i, (k, lab, a, b, c) in enumerate(bands):
        y = 52 + i * 48
        bar = f'<rect x="{x(a):.0f}" y="{y}" width="{x(b) - x(a):.0f}" height="30" rx="5" class="CLS"/>'
        g += S(k, bar.replace('CLS', 'barb'), T(x(b) + 8, y + 21, f'{lab}: {a}–{b}', 'b', 'start') if x(b) < 230 else T(x(a) - 8, y + 21, f'{lab}: {a}–{b}', 'b', 'end')) + O(k, bar.replace('CLS', 'capo'))
    return svg('Ganhos de partida', g, 300)
@d
def gainchain():  # 5.2.6: o volume da sala no fim da cadeia
    g = S(1, B(10, 60, 100, 56, 'Canal\n−18 dBFS', 'bx'), L(110, 88, 148, 88, 'ln'), B(150, 60, 100, 56, 'Main LR\n~0 dB', 'bxb'), L(250, 88, 288, 88, 'ln'))
    g += S(2, B(290, 50, 100, 76, 'PA\nvolume\nda sala', 'bxo'), T(340, 146, 'o volume é aqui', 'lbl'))
    g += S(3, B(150, 180, 240, 40, 'sem acesso ao PA: matriz', 'bxg', 'sm'), L(270, 180, 320, 128, 'lnd'))
    g += S(4, X(60, 136), T(60, 168, 'ganho: não', 'lblr'), T(60, 186, 'mexa', 'lblr'))
    return svg('Ganho do sistema: canal → Main → PA', g + T(200, 262, 'cada estágio no seu nível', 'sm'), 275)
@d
def trim():  # 5.2.7: trim digital × pré analógico
    g = S(1, B(10, 50, 100, 44, 'Microfone', 'bx'), L(110, 72, 148, 72, 'ln'), B(150, 50, 120, 44, 'Pré analógico\n(Gain)', 'bxb'), L(270, 72, 308, 72, 'ln'), B(310, 50, 80, 44, 'Canal'),
          B(10, 150, 100, 44, 'USB / placa', 'bx'), L(110, 172, 148, 172, 'ln'), B(150, 150, 120, 44, 'Trim digital', 'bxo'), L(270, 172, 308, 172, 'ln'), B(310, 150, 80, 44, 'Canal'),
          T(200, 128, 'canal mostra "trim" = sem pré controlável', 'sm'))
    g += S(2, T(200, 236, 'virtual soundcheck: ajuste no USB trim', 'lbl'), T(200, 258, 'não no ganho analógico', 'sm'))
    return svg('Trim digital × pré analógico', g, 270)
@d
def eqvoice():  # 6.2.4: EQ de voz com eixo em Hz
    xs = {50: 52, 100: 98, 250: 160, 500: 205, 1000: 250, 2000: 296, 5000: 356, 10000: 385}
    g = L(40, 230, 390, 230, 'axis') + ''.join(L(x, 226, x, 234, 'tick') + T(x, 252, (f'{f // 1000}k' if f >= 1000 else str(f)), 'sm') for f, x in xs.items()) + T(390, 272, 'Hz', 'sm', 'end')
    g += '<rect x="122" y="60" width="128" height="166" class="zr" opacity=".14"/>' + T(186, 54, 'barro: 160–600 Hz', 'lblr')
    g += L(40, 140, 390, 140, 'curve2') + P('M60 225 C80 200 92 150 110 140 L130 140 C145 140 152 168 160 168 C168 168 176 140 195 140 L300 140 C320 140 335 122 350 122 C365 122 372 140 390 140', 'curve')
    g += T(104, 214, 'HPF', 'b') + T(350, 110, 'presença', 'sm')   # rodada 6: o 250 Hz "embolado" está em 6.2.3; HPF fora da curva
    return svg('EQ de voz: onde cortar', g, 285)
@d
def busconfig(m=(0, 0, 0, 0)):  # 10.1.3 e 10.2.4: modelos dos 16 mix buses; m = (XR16, LR fora, pré-config, exemplos)
    sq = lambda y, kinds: ''.join(f'<rect x="{18 + i * 19.5}" y="{y}" width="16" height="26" rx="3" class="{c}"/>' for i, c in enumerate(kinds))
    g = S(m[1], T(18, 108, 'X32/M32 · Bus Pre-Configuration:', 'b', 'start'))
    g += S(m[2], sq(126, ['bxg'] * 8 + ['bxo'] * 8), T(390, 145, '8 + 8', 'sm', 'end'),
           sq(170, ['bxg'] * 4 + ['bxo'] * 4 + ['bxb'] * 8), T(390, 189, '4+4+8', 'sm', 'end'),
           '<rect x="18" y="214" width="16" height="16" rx="3" class="bxg"/>', T(40, 227, 'aux pré', 'sm', 'start'), '<rect x="128" y="214" width="16" height="16" rx="3" class="bxo"/>',
           T(150, 227, 'aux pós', 'sm', 'start'), '<rect x="238" y="214" width="16" height="16" rx="3" class="bxb"/>', T(260, 227, 'subgrupo', 'sm', 'start'))
    return svg('Dois modelos para os 16 mix buses', g, 240)
@d
def buschain():  # 11.2.2: EQ e compressor por retorno
    g = S(1, B(10, 100, 80, 50, 'Canal\nvoz', 'bx'), L(90, 125, 120, 70, 'ln'), L(90, 125, 120, 190, 'ln'))
    for y, n_, c in ((50, 'Bus 1', 'bxg'), (170, 'Bus 2', 'bxg')):
        g += S(1, B(122, y, 60, 40, n_, c, 'sm'), L(182, y + 20, 196, y + 20, 'ln'), B(198, y, 52, 40, 'EQ', 'bxo', 'sm'), L(250, y + 20, 262, y + 20, 'ln'),
               B(264, y, 56, 40, 'Comp', 'bxo', 'sm'), L(320, y + 20, 332, y + 20, 'ln'), B(334, y, 56, 40, 'GEQ', 'bxo', 'sm'))
    g += HL(6, 94, 88, 62, 1) + HL(194, 46, 60, 48, 1) + HL(194, 166, 60, 48, 1)
    g += HL(330, 46, 64, 48, 2) + HL(330, 166, 64, 48, 2) + HL(260, 46, 64, 48, 3) + HL(260, 166, 64, 48, 3)
    return svg('Canal → bus → EQ, comp e GEQ', g, 230)
@d
def phones():  # 11.2.4: fone direto na saída balanceada
    g = S(1, B(10, 70, 100, 70, 'Saída Aux\nXLR\nbalanceada', 'bxb'), L(110, 90, 168, 90, 'ln'), L(110, 120, 168, 120, 'ln'),
          T(139, 82, '+', 'b'), T(139, 136, '−', 'b'), B(170, 70, 90, 70, 'adaptador\nP10', 'bx', 'sm'), L(260, 105, 296, 105, 'ln'),
          P('M300 150 Q300 70 345 70 Q390 70 390 150', 'mk'), B(292, 140, 22, 34, '', 'bx'), B(376, 140, 22, 34, '', 'bx'), T(303, 192, 'L: +', 'sm'), T(387, 192, 'R: −', 'sm'))
    g += S(2, B(10, 222, 380, 40, 'um ouvido em fase invertida', 'bxr'))
    return svg('Fone direto na saída Aux', g, 275)
@d
def leak(q=False):  # 11.2.6: retorno vazando no PA; q = quiz do cap. 11: a ligação bus → LR (a resposta) e o botão LR só aparecem na escolha
    A = qa(q)
    g = S(1, B(10, 40, 110, 46, 'Canais', 'bx'), L(120, 63, 158, 63, 'ln'), B(160, 40, 110, 46, 'Bus 1\nretorno', 'bxg'), L(270, 63, 308, 63, 'ln'),
          '<polygon points="320,46 380,46 388,82 312,82" class="wedge"/>', T(350, 104, 'caixa de retorno', 'sm'))
    g += S(2, A(L(215, 86, 215, 158, 'lnx')), B(150, 160, 130, 44, 'Main LR → PA', 'bxb'), A(X(244, 120), T(290, 128, 'bus no LR', 'lblr', 'start')))
    g += S(3, A(B(10, 150, 120, 40, 'LR', 'bxd', 'b tw'), T(70, 214, 'botão LR do bus', 'b'), T(70, 232, 'apagado', 'sm')))
    g += S(4, A(T(200, 272, 'XR16 / XR12: subgrupos já saem no LR', 'sm')))
    return svg('Retorno vazando no PA', g, 285)
@d
def micplan():  # 12.2.2: planta do palco
    g = '<rect x="10" y="34" width="380" height="200" rx="10" class="zone"/>' + T(24, 54, 'PALCO (visto de cima)', 'zl', 'start')
    g += S(1, C(200, 84, 14, 'person'), T(176, 89, 'orador', 'sm', 'end'), P('M200 108 C150 100 140 170 200 186 C260 170 250 100 200 108 Z', 'pat'), C(200, 110, 6, 'dot'), T(258, 130, 'cardioide', 'sm', 'start'))
    g += S(1, '<polygon points="175,196 225,196 233,222 167,222" class="wedge"/>', T(160, 214, 'retorno atrás do mic', 'b', 'end'),
           '<rect x="22" y="252" width="70" height="36" rx="5" class="bxb"/>', '<rect x="308" y="252" width="70" height="36" rx="5" class="bxb"/>',
           T(57, 275, 'PA', 'b'), T(343, 275, 'PA', 'b'), T(200, 276, 'PA à frente da linha dos mics', 'lbl'))
    g += S(2, T(200, 312, '~3 dedos da boca', 'sm'))
    return svg('Primeiro, na fonte: posição', g, 320)
@d
def fxlib():  # 13.1.4: biblioteca de efeitos
    fam = [('Reverbs', 'Hall · Plate · Room', 'Chamber · Vintage'), ('Delays', 'Stereo · Tap · Echo', ''), ('Modulação', 'Chorus · Flanger · Phaser', 'Rotary · Tremolo · Mood Filter'),
           ('EQ e dinâmica', 'GEQ · TruEQ · comp', 'Wave Designer · Xtec'), ('Realce e imagem', 'Exciter · Enhancer', 'Edison'), ('Guitarra e afinação', 'Amp · Tube Stage', 'Pitch · Sub Octaver')]
    g = ''
    for i, (a, b, c) in enumerate(fam):
        y = 36 + i * 54
        g += B(10, y, 150, 46, a, 'bxo' if i == 0 else 'bx', 'b') + (T(172, y + 20, b, 'sm', 'start') + T(172, y + 39, c, 'sm', 'start') if c else T(172, y + 29, b, 'sm', 'start'))
    return svg('Seis famílias de algoritmos', g, 36 + 6 * 54)
@d
def fxrack():  # 13.2.1 (pendência 2.11): rack mais alto, a tela não sobra embaixo
    g = S(1, '<rect x="10" y="38" width="380" height="214" rx="10" class="panel"/>', T(24, 60, 'RACK X AIR · 4 SLOTS', 'zl', 'start'),
          *[B(22 + i * 92, 76, 84, 126, f'FX {i + 1}\n{t}', 'bxo' if i == 0 else 'bx', 'b') for i, t in enumerate(('Hall', 'Plate', 'Delay', 'Chorus'))],
          T(200, 234, 'algoritmos da X32 · 41 tipos (SOS)', 'sm'))
    g += S(2, C(96, 186, 12, 'touch'), T(200, 284, 'toque longo no slot: trocar o tipo', 'lbl'))
    return svg('O rack de efeitos', g, 296)
@d
def revenv():  # 13.2.5: envoltória do reverb
    g = L(40, 230, 390, 230, 'axis') + T(390, 252, 'tempo →', 'sm', 'end') + L(40, 230, 40, 50, 'axis')
    g += L(56, 230, 56, 60, 'curve3') + T(56, 46, 'som direto', 'sm', 'start')
    g += S(2, '<rect x="57" y="90" width="38" height="140" class="zg" opacity=".18"/>', T(100, 84, 'pré-delay', 'lbl', 'start'))
    g += S(1, P('M95 110 C130 170 160 205 200 222 L210 228', 'curve4'), P('M95 110 C170 150 260 200 330 222 L350 228', 'curve'),
           T(384, 76, '~1,5 s: base da voz', 'b', 'end'), T(384, 96, 'curta: música rápida', 'lblr', 'end'), T(384, 116, 'longa: balada', 'lbl', 'end'))
    return svg('Reverb no tempo: pré-delay e cauda', g, 280)
@d
def rackplans():  # 13.2.6
    row = lambda y, lab, xs, k: S(k, T(14, y - 8, lab, 'b', 'start'), *[B(10 + i * 96, y, 88, 56, t, c, 'sm') for i, (t, c) in enumerate(xs)])
    g = row(60, 'Plano por fonte (4 slots)', [('reverb\nbateria', 'bxo'), ('reverb\nvoz', 'bxo'), ('reverb\nutilitário', 'bxo'), ('delay', 'bxg')], 1)
    g += row(172, 'Plano por tamanho', [('FX1 reverb\nlongo', 'bxo'), ('FX2 reverb\ncurto ~1 s', 'bxo'), ('FX3\ndelay', 'bxg'), ('livre', 'bx')], 2)
    return svg('Quatro slots: dois planos possíveis', g + T(200, 266, 'reverb e delay por envio', 'sm'), 280)
@d
def monodelay():  # 17.1.3: um bullet só (desenho alto): sala, distância e o encoder 3 da tela Monitor
    g = '<polygon points="15,50 75,50 84,150 6,150" class="wedge"/>' + T(45, 172, 'PA', 'b') + '<rect x="290" y="76" width="100" height="56" rx="6" class="bxd"/>' + T(340, 110, 'FOH', 'b tw')
    g += L(86, 92, 288, 92, 'lnd') + T(188, 82, 'o som da sala chega depois', 'sm') + L(86, 160, 288, 160, 'ln2') + T(188, 182, 'distância: pés, metros ou ms', 'b')
    g += P('M314 158 Q314 136 340 136 Q366 136 366 158', 'mk')
    g += '<rect x="10" y="212" width="380" height="112" rx="10" class="panel"/>' + T(24, 232, 'TELA MONITOR', 'zl', 'start')
    g += ''.join(C(70 + i * 86, 274, 20, 'knob') + T(70 + i * 86, 314, str(i + 1), 'sm') for i in range(4))
    g += '<rect x="208" y="248" width="68" height="76" rx="9" class="hl"/>' + T(200, 352, 'encoder 3: atraso da escuta (fone = sala)', 'lbl')
    return svg('Delay da escuta: fone = sala', g, 362)
@d
def automix2():  # 18.2.1: usos
    g = S(1, '<rect x="10" y="38" width="185" height="200" rx="10" class="panel"/>', T(102, 60, 'mesa-redonda', 'b'),
          *[f'<rect x="{26 + i * 42}" y="{200 - h}" width="28" height="{h}" class="{c}"/>' for i, (h, c) in enumerate(((110, 'bara'), (30, 'barb'), (30, 'barb'), (30, 'barb')))],
          T(102, 224, 'quem fala sobe', 'sm'))
    g += S(2, '<rect x="205" y="38" width="185" height="200" rx="10" class="panel"/>', T(297, 60, 'DJ', 'b'), '<rect x="232" y="90" width="40" height="110" class="bara"/>',
           '<rect x="318" y="160" width="40" height="40" class="barb"/>', T(252, 224, 'mic', 'sm'), T(338, 224, 'música', 'sm'), L(338, 100, 338, 150, 'ln'))
    return svg('Onde o automix ajuda', g + T(200, 268, 'palestra, reunião, podcast, debate', 'sm'), 280)
@d
def sdcard(v=1):  # 19.1.4 e 19.2.8: placa DN32-LIVE
    g = B(10, 60, 100, 60, 'M32 LIVE', 'bxd', 'b tw') + L(110, 90, 148, 90, 'ln') + B(150, 50, 110, 80, 'placa\nDN32-LIVE', 'bxb')
    g += S(1 if v == 1 else 0, L(260, 72, 298, 66, 'ln'), L(260, 108, 298, 114, 'ln'), B(300, 48, 90, 34, 'SD 1', 'bxo', 'sm'), B(300, 98, 90, 34, 'SD 2', 'bxo', 'sm'),
           T(345, 150, 'até 32 GB · FAT32', 'sm'))
    if v == 1:
        g += S(2, T(200, 190, '32, 16 ou 8 canais em WAV', 'b'), T(200, 208, 'sem compressão, sem computador', 'sm'))
        g += S(3, B(10, 236, 170, 34, 'bateria CR123A', 'bxg', 'sm'), T(190, 258, 'protege na queda de energia', 'sm', 'start'))
    else:
        g += S(1, T(200, 190, 'os cartões não vêm com a mesa', 'b'))
        g += S(2, T(200, 216, '128 GB: fora do suportado', 'lblr'))
        g += S(3, B(10, 236, 180, 34, 'M32C: DN32-USB', 'bxr', 'sm'), X(208, 248), T(226, 258, 'sem slots de SD', 'sm', 'start'))
    return svg('Gravação em cartão SD, sem computador', g, 285)
@d
def midimap():  # 21.1.1: mapa MIDI das X AIR
    g = S(1, B(10, 40, 120, 56, 'Controlador\nMIDI', 'bxo'), L(130, 68, 168, 68, 'ln'), B(170, 40, 110, 56, 'Mesa X AIR', 'bxd', 'b tw'), T(335, 64, 'sem áudio:', 'sm'), T(335, 82, 'só comandos', 'sm'))
    g += S(2, B(10, 116, 380, 34, 'canal 1 · PC 1–64 → snapshots', 'bxg', 'sm'), B(10, 156, 380, 34, 'canal 1 · CC 0–15 → faders 1–16', 'bxg', 'sm'))
    g += S(3, B(10, 196, 185, 34, 'canal 2 → mutes', 'bx', 'sm'), B(205, 196, 185, 34, 'canal 3 → pan', 'bx', 'sm'))
    g += S(4, T(200, 260, 'X-TOUCH ou qualquer controlador', 'lbl'))
    return svg('Mapa MIDI das X AIR', g, 275)
@d
def midiscene():  # 21.1.2 (rodada 3): o PC 5 troca a cena; os canais com safe (cadeado) ficam onde estavam
    g = S(1, B(10, 40, 100, 48, 'Pedaleira', 'bxo'), L(110, 64, 158, 64, 'ln'), T(134, 56, 'PC 5', 'mono'), B(160, 40, 90, 48, 'Mesa', 'bxd', 'b tw'), L(250, 64, 298, 64, 'ln'),
          B(300, 40, 90, 48, 'cena 5', 'bxg'), T(200, 110, 'canal MIDI 1 · PC 1–100', 'sm'))
    g += S(2, B(10, 122, 380, 30, 'Setup › Remote: MIDI In + Scene Recall', 'bx', 'sm'))
    strip = ''
    for i, (old, new, safe) in enumerate(((50, 18, 0), (30, 30, 1), (20, 56, 0), (44, 44, 1))):
        x = 70 + i * 86
        strip += fader(x, 176, 80, new, 'capo' if not safe else 'cap')
        if not safe: strip += f'<rect x="{x - 13}" y="{176 + old - 7}" width="26" height="14" rx="3" style="fill:none;stroke:var(--ink-3);stroke-dasharray:3 2"/>'
        else: strip += f'<rect x="{x + 16}" y="{200}" width="16" height="13" rx="2" style="fill:var(--bg-3);stroke:var(--lamp);stroke-width:1.6"/>' + P(f'M{x + 19} 200 v-4 a5 5 0 0 1 10 0 v4', 'mk')
    g += S(3, strip, T(200, 284, 'com safe (cadeado): o canal não muda', 'lbl'))
    return svg('Trocar cena por MIDI', g, 294)
@d
def m32midi():  # 21.1.3
    rows = [('Cenas', 'canal 1 · PC 1–100', 'bxg'), ('Snippets', 'canal 2 · PC 1–100', 'bxg'), ('Cues', 'canais 3 a 6 · PC', 'bxg'), ('Faders', 'canal 1 · CC 0–79', 'bx'), ('Mutes e pan', 'canal 2 · CC 0–79', 'bx')]
    g = ''.join(B(10, 40 + i * 46, 120, 36, a, c) + B(140, 40 + i * 46, 250, 36, b, 'bx', 'sm') for i, (a, b, c) in enumerate(rows))
    return svg('Mapa MIDI fixo da M32', g + T(200, 286, 'com o modo Remote desligado', 'sm'), 295)
@d
def assign():  # 21.1.4: controle → banco → função, de cima para baixo (um bullet só: desenho alto)
    g = '<rect x="70" y="38" width="260" height="92" rx="10" class="panel"/>' + ''.join(C(110 + i * 60, 66, 14, 'knob') for i in range(4))
    g += ''.join(f'<rect x="{88 + i * 29}" y="98" width="23" height="18" rx="3" class="bx"/>' for i in range(8)) + T(342, 72, '4 knobs', 'sm', 'start') + T(342, 112, '8 botões', 'sm', 'start')
    g += L(200, 130, 200, 160, 'ln') + ''.join(B(64 + i * 84, 162, 76, 40, f'SET {c}', 'bxo' if c == 'A' else 'bx', 'b') for i, c in enumerate('ABC')) + T(342, 188, 'bancos', 'sm', 'start')
    g += L(200, 202, 200, 232, 'ln') + B(40, 234, 320, 50, 'função: send, mute, insert,\nMIDI CC/PC', 'bxg', 'b')
    g += T(200, 322, 'X32, M32, M32R: 36 controles · Compact e Producer: 24', 'sm')   # rodada 6: o exemplo do reverb é o 2º bullet
    return svg('Seção Assign: botão → banco → função', g, 354)
@d
def mixorder(q=False):  # 23.2.1; q = quiz do cap. 23: a 2ª coluna entra no lugar dos "?". Checklist P10: colunas fixas (nenhum bullet fala delas)
    g = S(0, T(100, 46, 'VOZ PRIMEIRO', 'zl'), *[B(10, 58 + i * 50, 180, 38, f'{i + 1}. {t}', 'bxo' if i == 0 else 'bx', 'sm') for i, t in enumerate(('voz e harmonia', 'base (banda)', 'HPF em tudo', 'DCAs'))])
    col2 = [B(210, 58 + i * 50, 180, 38, f'{i + 1}. {t}', 'bxo' if i == 0 else 'bx', 'sm') for i, t in enumerate(('só faders', 'EQ', 'compressão'))]
    g += S(0, T(300, 46, 'SÓ FADERS', 'zl'), *([QT(x) for x in col2] if q else col2))
    return svg('Ordem da mix: abordagens diferentes', g + L(200, 40, 200, 254, 'sep'), 265)
@d
def churchflow():  # 23.2.2 (rodada 6): painel na altura padrão; cada semana com o que se faz nela
    g = ''
    for i, (a, b) in enumerate((('Semana 1: cabo e rede', 'roteador no lugar, endereço da mesa definido'), ('Semana 2: a primeira cena', 'cena base com DCAs por grupo'),
                                ('Semana 3: backup e treino', 'show no pendrive · ensaio gravado'))):
        y = 34 + i * 104
        g += f'<circle cx="34" cy="{y + 46}" r="18" class="bxo"/>' + T(34, y + 52, str(i + 1), 'num') + B(64, y, 326, 92, '', 'bx') + T(80, y + 38, a, 'b', 'start') + T(80, y + 68, b, 'sm', 'start')
        if i < 2: g += L(34, y + 64, 34, y + 132, 'ln')
    return svg('Implantação em três semanas', g, 346)
@d
def studypath():  # 23.2.3
    rows = [('X AIR', 'hardware → app → canal → retornos → FX'), ('X32/M32', 'navegação → sinal → canal → rotas'), ('X32 Compact', 'faders → canal → DCA → cenas'), ('M32', 'cenas → rotas → split')]
    g = ''.join(S(i + 1, B(10, 44 + i * 58, 110, 42, a, 'bxb'), T(132, 70 + i * 58, b, 'sm', 'start')) for i, (a, b) in enumerate(rows))
    return svg('Trilhas de estudo por mesa', g, 290)
@d
def specxa():  # 25.1.1 (rodada 3): pontos num eixo de 100 a 110 dB, rotulado: a diferença real (4 dB) não vira 50% de barra
    ms = [('XR18', 106), ('XR16', 105), ('XR12', 104), ('MR18', 108), ('MR12', 108)]
    x = lambda v: 90 + (v - 100) * 28
    g = T(200, 40, 'faixa dinâmica analógico → analógico (dB)', 'sm')
    g += ''.join(L(x(v), 52, x(v), 236, 'grid') + T(x(v), 256, str(v), 'sm') for v in range(100, 111, 2)) + L(x(100), 236, x(110), 236, 'axis')
    for i, (m_, v) in enumerate(ms):
        y = 70 + i * 36
        g += T(76, y + 5, m_, 'b', 'end') + L(x(100), y, x(v), y, 'grid') + C(x(v), y, 8, 'dotc' if m_[0] == 'X' else 'dot') + T(x(v) + 14, y + 5, f'{v}', 'b', 'start')
    return svg('Faixa dinâmica das X AIR / M AIR', g, 270)   # rodada 6: só as barras; EIN e conversores estão nos bullets
@d
def specxm():  # 25.1.2 (pendência 3.12): os números lado a lado, o melhor de cada linha em laranja e a regra "maior/menor é melhor" escrita
    rows = [(1, 'Conversor D/A', 'maior é melhor ↑', '114 dB', '120 dB', 1), (2, 'THD+N do pré', 'menor é melhor ↓', '0,006%', '0,01%', 0),
            (3, 'EIN (ruído)', 'mais negativo é melhor ↓', '−128 dBu', '−125 dBu', 0)]
    g = T(250, 44, 'X32', 'zl') + T(350, 44, 'M32', 'zl')
    for i, (k, lab, rule, a_, b_, best) in enumerate(rows):
        y = 56 + i * 66
        g += S(k, f'<rect x="10" y="{y}" width="380" height="58" rx="8" class="panel"/>', T(22, y + 26, lab, 'b', 'start'), T(22, y + 46, rule, 'sm', 'start'),
               T(250, y + 36, a_, 'bb' if best == 0 else 'bs'), T(350, y + 36, b_, 'bb' if best == 1 else 'bs'),
               f'<rect x="{204 if best == 0 else 304}" y="{y + 8}" width="92" height="42" rx="6" class="hl"/>')
    g += S(4, T(200, 272, 'consumo, peso e tela: tabela 1.1.6', 'sm'))
    return svg('X32 × M32 em números', g, 284)
@d
def specfam():  # 25.2.1
    return grid3('As duas famílias em números', ('X AIR', 'X32'), [('Conversores', '24 bits · 114 dB', ''), ('EIN do pré', '−128 dBu', ''), ('THD+N', '0,005%', '0,006%'), ('Wi-Fi', '2,4 GHz', 'não tem')],
                 foot='M AIR e M32: números próprios (25.1)', h=290, steps=False)
def errpairs(title, rows, heads=('✕ ERRADO', '✓ CERTO'), foot='', h=300, first=1):  # erro → correção do bullet ativo (revisão 2: o molde vazio virou conteúdo)
    g = pairs(title, rows, heads, foot, h)
    return g if first == 1 else re.sub(r'data-step="(\d+)"', lambda m: f'data-step="{int(m.group(1)) + first - 1}"', g)
@d
def err241():  # 24.1.1 (rodada 3): manual × o que circula, com o selo "não confirmado" (antes: o mesmo molde de 5 slides seguidos)
    g = T(95, 40, 'O QUE SE DIZ', 'zl') + T(305, 40, 'O MANUAL', 'zl')
    g += S(1, B(6, 54, 178, 64, 'anúncios:\n"X18 com faders"', 'bx', 'b'), T(200, 94, '×', 'bb'), B(216, 54, 178, 64, 'sem faders\nfísicos', 'bxb', 'b'))
    g += S(2, B(6, 136, 178, 64, 'circula:\n"MR18 com Hi-Z"', 'bx', 'b'), T(200, 176, '×', 'bb'), B(216, 136, 178, 64, 'não cita\nHi-Z', 'bxb', 'b'))
    g += '<g transform="rotate(-5 200 246)"><rect x="96" y="224" width="208" height="42" rx="5" style="fill:rgba(255,75,62,.08);stroke:#ff8a80;stroke-width:2.4"/>' + T(200, 252, 'NÃO CONFIRMADO', 'lblr') + '</g>'
    g += T(200, 296, 'na dúvida, vale o manual', 'sm')
    return svg('O que circula × o manual', g, 306)
@d
def err242():
    return errpairs('Os erros que derrubam um show', [('Wi-Fi interno\nem show cheio', 'roteador 5 GHz\n+ um no cabo'), ('"PC → Mixer"', '"Mixer → PC"'),
                    ('RESET 10 s\npara a rede', 'RESET 2 s'), ('mixar no ganho', 'ganho fixo;\nmix no fader'), ('subgrupo com\ncanais no Main', 'canais fora\ndo Main')], h=360)
@d
def err243():
    return errpairs('Afirmações erradas que circulam', [('X32 Producer:\n25 faders', '17 faders'), ('X32: 12\nmix buses', '16 mix buses'), ('XR12\nmultipista', 'só estéreo\nem pendrive'),
                    ('MR18 com Hi-Z', 'sem Hi-Z:\nuse DI')], h=310)
@d
def err244():  # 24.2.3 (rodada 3): árvore de decisão (dúvida → o manual responde? → o que fazer); cada bullet acende o seu exemplo
    g = B(110, 34, 180, 34, 'mais de uma resposta', 'bxo', 'b') + L(200, 68, 200, 82, 'ln')
    g += P('M200 84 L292 110 L200 136 L108 110 Z', 'bx') + T(200, 115, 'o manual responde?', 'sm')
    g += P('M108 110 H66 V164', 'ln') + T(84, 102, 'sim', 'lbl') + P('M200 136 V164', 'ln') + P('M292 110 H334 V164', 'ln') + T(318, 102, 'não', 'lbl') + T(214, 154, 'não', 'lbl', 'start')
    g += B(4, 166, 124, 40, 'siga o manual', 'bxb', 'b') + B(138, 166, 124, 40, 'todas as opções', 'bxg', 'b') + B(272, 166, 124, 40, 'confira na mesa', 'bx', 'b')
    g += S(1, B(272, 256, 124, 30, 'fone na XR18', 'bx', 'sm')) + S(4, B(4, 218, 124, 30, 'Hi-Z da XR12', 'bx', 'sm'))
    g += S(2, B(138, 218, 124, 30, 'live pré × pós', 'bx', 'sm')) + S(3, B(138, 256, 124, 30, 'low cut no bumbo', 'bx', 'sm'))
    g += S(5, T(334, 220, 'lista: 24.2.3', 'sm'))
    return svg('Abordagens divergentes: o que fazer', g, 296)
@d
def sources(hi=None, n=0, sub=''):  # cap. 26: o manual da mesa e o próximo passo (sem fontes externas)
    g = B(15, 40, 370, 96, '', 'panel') + T(200, 80, 'MANUAL', 'ico') + T(200, 108, 'menus, botões e números da sua mesa', 'b')
    g += L(200, 136, 200, 170, 'ln') + B(15, 172, 370, 96, '', 'bxo') + T(200, 212, 'PRÓXIMO PASSO', 'ico') + T(200, 240, 'cursos, turmas e mentorias', 'b')
    return svg('Onde estudar', g, 290)
# ---------------------------------------------------------------- rodada 3: um diagrama por assunto onde o genérico se repetia
@d
def prefs():  # 4.1.6: três lugares de ajuste, um por bullet
    g = ''.join(f'<rect x="10" y="{y}" width="380" height="{h}" rx="8" class="panel"/>' + T(22, y + 18, t, 'zl', 'start') for y, h, t in ((34, 92, 'SETUP › EDIT (IPAD)'), (136, 86, 'PREFERENCES (COMPUTADOR)'), (232, 64, 'UTILITIES')))
    g += S(1, *[B(22 + i * 52, 62, 44, 36, str(n), 'bxo' if n == 4 else 'bx', 'b') for i, n in enumerate((1, 4, 2, 3, 5))], P('M174 102 Q122 122 70 102', 'ln'),
           T(184, 118, 'arraste para reordenar', 'sm', 'start'), B(300, 62, 78, 36, 'Reset', 'bxr', 'b'))
    g += S(2, *[f'<rect x="{x}" y="{y - 13}" width="16" height="16" rx="3" class="bxg"/>' + T(x + 24, y, t, 'b', 'start')
               for (x, y), t in zip(((22, 180), (206, 180), (22, 208), (206, 208)), ('Auto Select', 'Exclusive solo', 'fader Fine', 'medidores'))])
    g += S(3, *[B(140 + i * 62, 246, 56, 36, t, 'bx', 'sm') for i, t in enumerate(('RTA', 'Buses', 'DCA', 'Meter'))])
    return svg('Preferências: onde fica cada ajuste', g, 308)
@d
def x32edit():  # 4.2.3: janela Mixer (canais, "mix to", camadas) e os extras do M32-Edit
    g = '<rect x="10" y="34" width="380" height="140" rx="8" class="panel"/>' + T(22, 52, 'X32-EDIT · JANELA MIXER', 'zl', 'start')
    g += ''.join(f'<rect x="{22 + i * 20}" y="64" width="14" height="80" rx="3" class="bx"/><rect x="{24 + i * 20}" y="{72 + (i * 29) % 56}" width="10" height="8" rx="2" class="capd"/>' for i in range(9))
    g += T(110, 162, 'todos os canais e envios', 'sm') + B(206, 64, 84, 80, 'mix to\n(envios)', 'bxg', 'sm') + B(298, 64, 84, 80, 'camada:\nDCA, vozes\ne Main', 'bxo', 'sm')
    g += HL(201, 59, 186, 90, 1)
    bars = ''.join(f'<rect x="{22 + i * 4.4:.1f}" y="{262 - h}" width="3" height="{h}" class="bar"/>' for i, h in enumerate(12 + (i * 37) % 30 + (18 if 14 < i < 22 else 0) for i in range(40)))
    g += S(2, '<rect x="10" y="186" width="380" height="110" rx="8" class="panel"/>', T(22, 204, 'M32-EDIT', 'zl', 'start'), bars, T(110, 284, 'RTA de 100 bandas', 'sm'),
           *[C(236 + j * 38, 226 + r * 30, 10, 'knob') for r in range(2) for j in range(4)], T(293, 284, 'seção Assign', 'sm'))
    return svg('X32-Edit e M32-Edit no computador', g, 306)
@d
def msta():  # 4.2.4 (rodada 6): prós em verde (o que o app faz) e contras em vermelho; desenho fixo, os bullets falam de OSC e da ordem de ensino
    G = 'fill:rgba(47,224,123,.08);stroke:var(--led-green);stroke-width:1.8'
    g = f'<rect x="10" y="34" width="200" height="222" rx="12" style="{G}"/>' + T(110, 58, 'Mixing Station', 'b')
    g += ''.join(fader(36 + i * 30, 76, 104, p) for i, p in enumerate((30, 62, 44)))
    g += ''.join(f'<rect x="{124 + i * 12}" y="{180 - h}" width="9" height="{h}" class="{"barr" if h > 90 else "bar"}"/>' for i, h in enumerate((40, 62, 96, 70, 52, 34, 26)))
    g += T(66, 200, 'layout próprio', 'sm') + T(164, 200, 'RTA', 'sm')
    g += ''.join(f'<rect x="{26 + i * 16}" y="214" width="12" height="16" rx="2" class="{"zr" if i == 9 else "zy" if i > 6 else "zg"}"/>' for i in range(10)) + T(110, 248, 'medidores', 'sm')
    card = lambda x, y, w, h, a, b, ok: (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" style="{G}"/>' if ok else B(x, y, w, h, '', 'bxr'),
                                         OK(x + 22, y + h / 2 - 8) if ok else X(x + 22, y + h / 2 - 8), T(x + w / 2 + 12, y + h / 2 - 2, a, 'b'), T(x + w / 2 + 12, y + h / 2 + 18, b, 'sm'))
    g += ''.join(card(226, 34, 164, 106, 'Senha por bus', 'só ele respeita', True)) + ''.join(card(226, 150, 164, 106, 'Wi-Fi ruim', 'até 1 min atrasado', False))
    g += ''.join(card(10, 270, 185, 60, 'Sem suporte', 'da Music Tribe', False)) + ''.join(card(205, 270, 185, 60, 'Preço', 'confira na loja', False))
    return svg('Mixing Station: prós e contras', g, 340)
@d
def ligacoes():  # 2.1.6 (rodada 6): cada cenário com a ligação que o define; desenho alto, o slide tem um bullet só
    return pairs('Cenário → o que liga onde', [('Gravação\ncom iPad', 'USB: até 18 pistas\nno iPad', 'bx', 'bxg'), ('Show com\ntablet', 'P16 no Ultranet:\num retorno por músico', 'bx', 'bxg'),
                 ('Bar / clube', 'pendrive grava\npedal MIDI troca a cena', 'bx', 'bxg'), ('XR12 / MR12\n(4 pré-amps)', 'mesa analógica\nsoma as fontes extras', 'bx', 'bxo'),
                 ('X32 · M32C\ncom stagebox', 'S16, DL16 ou DL32\npor AES50', 'bx', 'bxb')], heads=('CENÁRIO', 'COMO LIGAR'), h=400, steps=False, rhmax=60)
@d
def dualin():  # 5.2.11: a mesma entrada em dois canais
    g = B(10, 112, 92, 64, 'Entrada 1\n(XLR)', 'bxd', 'b tw') + L(102, 136, 148, 74, 'ln') + L(102, 152, 148, 196, 'ln') + T(126, 146, '=', 'mid')
    g += B(150, 50, 100, 48, 'Canal 1', 'bxb') + B(150, 172, 100, 48, 'Canal 2', 'bxb')
    g += HL(145, 45, 110, 180, 1)
    g += S(2, B(10, 262, 380, 44, 'XR12: canais 13–16 (In/Out › Input)\nM32 / M32C: Config › Source', 'bx', 'sm'))
    g += S(3, L(250, 74, 298, 74, 'ln'), B(300, 50, 90, 48, 'PA\n(Main LR)', 'bxo', 'sm'), L(250, 186, 298, 186, 'ln'), B(300, 166, 90, 40, 'monitor', 'bxg', 'sm'))
    g += S(4, L(250, 206, 298, 224, 'lnd'), B(300, 210, 90, 36, 'solo (fone)', 'bx', 'sm'), T(200, 140, 'canal 2 fora do LR:', 'sm'), T(200, 156, 'pré-escuta de EQ', 'sm'))
    g += S(5, T(200, 330, '"voz fraca" em 2 canais (+6 dB): discutível', 'lblr'))
    return svg('Uma entrada, dois canais', g, 340)
@d
def parcomp():  # 8.2.5 (rodada 6): o roteamento desenhado, sem frases (elas estão nos bullets): ✕ no caminho do rack, ✓ no comp do subgrupo, o knob Mix
    g = B(10, 112, 84, 48, 'Canal', 'bx') + L(94, 136, 306, 136, 'ln') + B(308, 112, 82, 48, 'Main\nLR', 'bxb')
    # checklist P06: sem a caixa "comp do rack (insert)", que 8.2.3 desenha em série; aqui só o caminho certo (subgrupo com a dinâmica dele), o Mix e o Main
    g += S(3, P('M52 160 L52 220 L128 220', 'ln'), B(130, 196, 170, 48, 'Subgrupo\ncom o comp dele', 'bxo', 'sm'), P('M300 220 L350 220 L350 162', 'ln'), OK(215, 270))
    g += S(4, C(40, 64, 20, 'knob'), '<line x1="40" y1="64" x2="54" y2="50" class="needle"/>', T(70, 70, 'Mix', 'b', 'start'))
    g += S(5, '<rect x="308" y="84" width="82" height="14" rx="3" class="zgr"/><rect x="370" y="84" width="20" height="14" rx="3" class="zy"/>', T(349, 74, 'GR', 'sm'))   # redução leve no Main (o valor está no bullet)
    return svg('Dois caminhos até o Main', g, 320)
@d
def stackcomp():  # 8.2.3 (rodada 6): só a cadeia em série; as curvas de ratio já estão em 8.1.1 e os valores nos bullets
    g = ''
    boxes = (('Canal', 'bx', ''), ('comp do canal', 'bxo', '−3 dB'), ('comp do rack no insert\ndo subgrupo/Main', 'bxo', '−3 dB'), ('Main LR', 'bxb', ''))
    for i, (a, c, gr) in enumerate(boxes):
        y = 30 + i * 70
        g += B(20, y, 200, 50, a, c, 'b')
        if i < 3: g += L(120, y + 50, 120, y + 68, 'ln')
        if gr:
            g += f'<rect x="250" y="{y + 8}" width="110" height="14" rx="3" class="zgr"/><rect x="314" y="{y + 8}" width="46" height="14" rx="3" class="zy"/>' + T(305, y + 42, 'GR ' + gr, 'lbl')
    g += L(240, 316, 380, 316, 'sep') + T(310, 340, 'soma: −6 dB', 'b')
    return svg('Dois compressores em série', g, 352)
@d
def inear():  # 11.2.3: retorno estéreo: dois Aux linkados, pan no envio, cabo balanceado
    g = B(10, 104, 74, 52, 'Canal\nvoz', 'bx') + L(84, 130, 112, 130, 'ln') + B(172, 60, 96, 44, 'Aux 3 · L', 'bxg') + B(172, 156, 96, 44, 'Aux 4 · R', 'bxg')
    g += L(150, 120, 170, 84, 'ln') + L(150, 140, 170, 176, 'ln') + B(286, 92, 104, 76, 'transmissor\nin-ear', 'bxb')
    g += P('M318 214 Q318 186 338 186 Q358 186 358 214', 'mk') + T(338, 236, 'músico', 'sm')
    g += S(1, T(220, 52, 'XLR: mono, balanceada', 'sm'), T(220, 222, 'XLR: mono, balanceada', 'sm'))
    g += S(2, C(132, 130, 17, 'knob'), '<line x1="132" y1="130" x2="146" y2="118" class="needle"/>', T(132, 170, 'pan', 'lbl'), T(132, 186, 'no envio', 'lbl'), L(220, 104, 220, 154, 'ln2'), T(226, 134, 'link', 'lbl', 'start'))
    g += S(3, L(268, 82, 300, 110, 'ln'), L(268, 178, 300, 150, 'ln'), T(200, 270, 'cabo balanceado: XLR-XLR ou XLR-P10 TRS', 'b'))
    return svg('Retorno estéreo: dois Aux viram um par', g, 282)
@d
def morevias():  # 11.2.5: mais vias de retorno (rodada 4: o que vem na continuação, bullets 4 e 5, fica numa faixa de baixo; o 1º slide recorta sem buraco)
    col = lambda x, k, items: S(k, *[B(x, 46 + i * 54, 170, 38, t, 'bxo' if i == 2 else 'bx', 'sm') for i, t in enumerate(items)],
                                 *[L(x + 85, 84 + i * 54, x + 85, 98 + i * 54, 'ln') for i in range(2)])
    g = T(95, 36, 'TRUQUE 1', 'zl') + T(305, 36, 'TRUQUE 2', 'zl') + L(200, 28, 200, 270, 'sep')
    # rodada 6: os dois truques ficam inteiros no desenho; os 3 bullets dizem o porquê (o envio em pré acende com o 2º, o aviso com o 3º)
    g += col(10, 0, ('Bus 5 (retorno)', 'Monitor Source = Bus 5', 'saída de fone')) + T(95, 212, 'vira mais um retorno', 'sm')
    g += B(10, 222, 180, 46, 'envios Pre Fader\nLR do bus desligado', 'bxg', 'sm')  # checklist P02: a regra fica só no desenho
    g += col(220, 0, ('envio do FX 3', 'roteado a uma saída', 'mais uma via')) + B(220, 222, 170, 46, 'só XR18 e MR18', 'bx', 'sm')
    g += B(210, 284, 180, 46, 'gasta um slot de\nefeito, sem EQ', 'bxr', 'sm')
    g += S(2, B(10, 284, 180, 46, '⚠ na XR18: teste\nantes do show', 'bxr', 'sm'))
    return svg('Dois truques, uma via a mais cada', g, 340)
@d
def noexag():  # 12.2.5: EQ demais: o ciclo vicioso e muitos cortes × um corte
    g = S(1, *[B(18, 40 + i * 48, 172, 36, t, 'bxr' if i == 2 else 'bx', 'sm') for i, t in enumerate(('1. pede "mais"', '2. mais volume', '3. mais microfonia', '4. mais cortes de EQ'))],
          *[L(104, 76 + i * 48, 104, 88 + i * 48, 'ln') for i in range(3)], P('M18 202 L8 202 L8 58 L16 58', 'ln'), T(104, 252, 'ciclo vicioso', 'lblr'))
    many = 'M212 92 ' + ' '.join(f'L{x - 8} 92 L{x} {120 + (i % 2) * 14} L{x + 8} 92' for i, x in enumerate((236, 268, 300, 332, 364))) + ' L390 92'
    g += S(2, L(212, 130, 390, 130, 'axis'), P(many, 'curve4'), T(300, 152, 'muitos cortes: timbre torto', 'sm'),
           L(212, 230, 390, 230, 'axis'), P('M212 190 L300 190 L310 222 L320 190 L390 190', 'curve'), T(300, 252, 'um corte: só o apito', 'sm'), T(300, 64, 'EQ do retorno', 'zl'))
    return svg('Não exagere no EQ', g + L(200, 40, 200, 260, 'sep'), 272)

@d
def fxmon():  # 13.2.7: o reverb é uma via paralela; com Sends on Fader, o fader do FX return manda o reverb ao monitor
    g = B(10, 40, 84, 44, 'Canal\nvoz', 'bx') + L(94, 62, 298, 62, 'ln') + B(300, 40, 90, 44, 'Main LR\n(PA)', 'bxb')
    g += S(1, P('M52 84 L52 132 L96 132', 'ln'), B(98, 112, 88, 40, 'Reverb', 'bxo'), L(186, 132, 212, 132, 'ln'), B(214, 112, 96, 40, 'FX Return', 'bx'),
           P('M310 132 L345 132 L345 86', 'ln'), T(200, 176, 'via paralela: não passa pelo canal', 'sm'))
    caps = [('Voz', 48, 'cap'), ('Violão', 58, 'cap'), ('Teclado', 40, 'cap'), ('FX Ret', 14, 'capo')]  # rodada 4: tampa acima do rótulo
    g += S(2, '<rect x="10" y="194" width="380" height="132" rx="10" class="panel"/>', T(22, 212, 'SENDS ON FADER · BUS 1 (MONITOR)', 'zl', 'start'),
           *[fader(50 + i * 64, 222, 76, p, c) + T(50 + i * 64, 318, t, 'b' if c == 'capo' else 'sm') for i, (t, p, c) in enumerate(caps)],
           '<polygon points="314,262 370,262 378,300 306,300" class="wedge"/>', L(258, 250, 306, 270, 'ln'), T(342, 318, 'monitor', 'sm'))
    return svg('Reverb no retorno do músico', g, 336)
@d
def xairdelay():  # 15.2.5: sem delay de saída na X AIR (rodada 4: molduras com folga em volta dos rótulos; a seta de alinhamento não cruza "caixas da frente")
    wedge = lambda x, y: f'<polygon points="{x},{y} {x + 44},{y} {x + 50},{y + 36} {x - 6},{y + 36}" class="wedge"/>'
    g = B(10, 96, 76, 56, 'Canais', 'bx') + P('M86 112 L104 112 L104 66 L118 66', 'ln') + B(120, 44, 118, 46, 'Bus 5–6\nSub group', 'bxg', 'sm')
    g += L(238, 66, 318, 66, 'ln') + wedge(326, 48) + T(348, 104, 'caixas da frente', 'sm')
    g += L(165, 90, 165, 160, 'ln') + B(120, 162, 90, 44, 'Main LR', 'bxb') + L(210, 184, 230, 184, 'ln') + L(314, 184, 320, 184, 'ln') + wedge(326, 166) + T(348, 222, 'caixas de trás', 'sm')
    g += S(1, T(200, 26, 'X AIR: sem delay nativo de saída', 'lblr'))
    g += S(2, B(232, 160, 82, 48, 'Stereo\nDelay', 'bxo', 'sm'), T(200, 254, 'insert no LR: Mix 100%, filtros abertos', 'lbl'))
    g += HL(112, 36, 302, 80, 3) + HL(112, 154, 302, 80, 3)
    g += S(4, L(348, 112, 348, 162, 'ln2'), T(200, 280, 'alinhe o fundo à frente: 58 ms ≈ 20 m', 'b'))
    g += S(5, T(200, 304, 'cada delay ocupa 1 dos 4 slots de efeito', 'lblr'))
    return svg('Delay de saída improvisado na X AIR', g, 314)
@d
def backup():  # 16.2.3: show exportado para fora da mesa e a "cena zero"
    g = B(10, 96, 100, 70, 'Mesa\n(show)', 'bxd', 'b tw')
    g += S(1, L(110, 116, 238, 72, 'ln'), B2(240, 36, 150, 72, 'Pendrive\n.show', 'bxo'))
    g += S(2, B2(10, 196, 100, 72, 'slot 0\ncena base', 'bxb'), L(60, 168, 60, 194, 'ln'))
    g += S(3, L(110, 150, 238, 210, 'ln2'), B2(240, 180, 150, 72, 'Computador\n.scn / .shw', 'bxg'))
    return svg('O show fora da mesa', g, 276)
@d
def userin():  # 20.2.4: blocos de 8 (Local, AES50 A/B, Card, User In) → grade 168 × 168 → canais
    src = [('Local', 'bx'), ('AES50 A', 'bx'), ('AES50 B', 'bx'), ('Card', 'bx'), ('User In', 'bxo')]
    g = ''.join(B(10, 38 + i * 50, 110, 38, t, c) + L(120, 57 + i * 50, 142, 57 + i * 50, 'ln0') for i, (t, c) in enumerate(src))
    g += '<rect x="142" y="48" width="8" height="218" rx="3" class="sum"/>' + L(150, 157, 304, 157, 'ln') + B(306, 120, 84, 74, 'canais\n(blocos\nde 8)', 'bxb')
    g += HL(5, 33, 120, 240, 1)
    grid = ''.join(L(178 + i * 13, 96, 178 + i * 13, 218, 'grid') for i in range(9)) + ''.join(L(172, 102 + j * 14, 290, 102 + j * 14, 'grid') for j in range(9))
    g += S(2, '<rect x="166" y="88" width="130" height="138" rx="8" class="bxd"/>', grid, T(231, 162, '168 × 168', 'b tw'), T(231, 250, 'antes do processamento', 'sm'))
    return svg('Roteamento de entrada: User In e a grade', g, 290)
@d
def splitdl32():  # 20.2.5: receita oficial com DL32: FOH é a mestre; DL32 A ↔ FOH, DL32 B → monitor (porta A)
    g = B(10, 120, 88, 70, 'FOH\n(PA)', 'bxb') + B(156, 120, 88, 70, 'DL32\nno palco', 'bxd', 'b tw') + B(302, 120, 88, 70, 'Mesa de\nmonitor', 'bxg')
    g += ''.join(C(170 + i * 20, 62, 8, 'person') + L(170 + i * 20, 70, 170 + i * 20, 118, 'ln0') for i in range(4)) + T(200, 44, 'microfones', 'sm')
    g += HL(150, 114, 100, 82, 1)
    g += S(2, T(54, 216, 'mestre do clock', 'lbl'), T(54, 234, 'Sync Internal', 'sm'))
    g += S(3, L(100, 160, 154, 160, 'ln2'), T(127, 150, 'A ↔ A', 'sm'), L(246, 160, 300, 160, 'ln'), T(273, 150, 'B → A', 'sm'))
    g += O(3, L(104, 168, 150, 168, 'curve'), L(250, 168, 296, 168, 'curve'))   # pendência 3.1: destaque só nos trechos de cabo, abaixo dos rótulos
    g += T(200, 276, 'FOH é a mestre: Sync Internal', 'lbl')
    return svg('Split com DL32: FOH e monitor', g, 288)
@d
def cfgtabs():  # 21.1.7: as abas Config, Remote e Network; cada bullet acende a sua
    cols = [('Config', ['Initialize', 'firmware', 'taxa e clock', 'data e hora', 'Bus Pre-Config']), ('Remote', ['controle de DAW', 'portas MIDI', 'RTP-MIDI', 'MIDI scene recall', 'X/OSC']),
            ('Network', ['IP', 'máscara', 'gateway'])]
    g = '<rect x="10" y="74" width="380" height="214" rx="8" class="panel"/>'
    for i, (t, items) in enumerate(cols):
        x = 10 + i * 128
        g += B(x, 40, 124, 32, t, 'bx', 'b') + O(i + 1, f'<rect x="{x}" y="40" width="124" height="32" rx="7" class="bxo"/>', T(x + 62, 61, t, 'b'))
        g += S(i + 1, *[T(x + 12, 104 + j * 36, it, 'b' if j == 0 else 'sm', 'start') for j, it in enumerate(items)])
    return svg('Setup › Config, Remote e Network', g + L(136, 84, 136, 278, 'sep') + L(264, 84, 264, 278, 'sep'), 298)
@d
def onde():  # 21.2.1: onde o controle externo aparece: X-Touch (4.2.10), seção Assign (4.2.8), clock da stagebox (20.2.2)
    rows = [(1, '4.2.10', 'X-Touch: faders', 'motorizados pela rede'), (2, '4.2.8', 'seção Assign: botões', 'e encoders programáveis'), (3, '20.2.2', 'clock entre a mesa', 'e a stagebox')]
    g = ''
    for i, (k, n_, a, b) in enumerate(rows):
        y = 40 + i * 84
        ic = (''.join(fader(34 + j * 26, y + 8, 56, 10 + j * 14) for j in range(3)) if k == 1 else
              ''.join(C(30 + j * 26, y + 22, 9, 'knob') for j in range(3)) + ''.join(f'<rect x="{20 + j * 26}" y="{y + 44}" width="20" height="14" rx="3" class="bx"/>' for j in range(3)) if k == 2 else
              f'<rect x="16" y="{y + 10}" width="70" height="50" rx="6" class="bxd"/>' + C(98, y + 35, 14, 'knob') + f'<line x1="98" y1="{y + 35}" x2="98" y2="{y + 25}" class="needle"/>')
        g += S(k, f'<rect x="10" y="{y}" width="380" height="72" rx="9" class="panel"/>', ic, B(126, y + 18, 70, 36, n_, 'bxo', 'b'), T(208, y + 32, a, 'b', 'start'), T(208, y + 52, b, 'sm', 'start'))
    return svg('Onde o controle externo aparece', g, 298)
@d
def quemgrava():  # 19.2.1: quem grava o quê (a tabela inteira, uma linha por bullet)
    g = ''.join(f'<text x="{x}" y="52" text-anchor="middle" class="zlc" style="font-size:14px">{t}</text>' for x, t in ((177, 'PENDRIVE'), (263, 'USB'), (349, 'CARTÃO SD')))   # pendência 2.9: células de 82 (o texto encostava na borda)
    rows = [('XR18 · X18\nMR18', ('não', 'bxr'), ('USB\n18×18', 'bxg'), ('não', 'bxr')), ('XR16 · XR12\nMR12', ('estéreo\n(WAV)', 'bxg'), ('não', 'bxr'), ('não', 'bxr')),
            ('X32\n(todas)', ('sim', 'bxg'), ('X-USB\n32×32', 'bxg'), ('X-Live\nopcional', 'bx')), ('M32 · M32R\nM32C', ('sim', 'bxg'), ('DN32-USB\n32×32', 'bxg'), ('só nas\nLIVE', 'bx')),
            ('como grava', ('WAV estéreo\nFAT32 · 2 GB', 'panel'), ('interface\nno DAW', 'panel'), ('2 slots SD\n32/16/8 can.', 'panel')),
            ('cuidado', ('LED apagado\npara tirar', 'panel'), ('cabo USB\nde qualidade', 'panel'), ('bateria\nCR123A', 'panel'))]
    for i, (lab, *cells) in enumerate(rows):
        y = 64 + i * 58
        g += B(4, y, 126, 50, lab, 'bxb' if i < 4 else 'bx', 'b') + ''.join(B(136 + j * 86, y, 82, 50, t, c, 'sm') for j, (t, c) in enumerate(cells))
    return svg('Pendrive, USB e SD por mesa', g, 64 + 6 * 58)

# ---------------------------------------------------------------- rodada 4: diagramas do assunto onde um diagrama de outro tópico se repetia
@d
def namemap():  # 0.2: o nome no título → as mesas que ele cobre
    chip = lambda x, y, t, w=74: B(x, y, w, 30, t, 'bx', 'b')
    chip = lambda x, y, t, w=74: B(x, y, w, 36, t, 'bx', 'b')   # rodada 3: desenho mais alto (o painel tinha ~80 px vazios em cima e embaixo)
    g = T(80, 40, 'NO TÍTULO', 'zl') + T(290, 40, 'MESAS COBERTAS', 'zl')
    g += B2(20, 56, 120, 62, 'XR18', 'bxb') + L(142, 87, 194, 87, 'ln') + chip(198, 69, 'XR18') + T(282, 92, 'Behringer', 'sm', 'start')
    g += B2(20, 138, 120, 62, 'MR18', 'bxb') + L(142, 169, 194, 169, 'ln') + chip(198, 151, 'MR18') + T(282, 174, 'gêmea Midas', 'sm', 'start')
    g += S(1, B2(20, 222, 120, 92, '"X AIR"', 'bxo'), L(142, 268, 194, 268, 'ln'),
           *[chip(198 + (i % 3) * 66, 224 + (i // 3) * 46, t, 60) for i, t in enumerate(('XR18', 'X18', 'XR16', 'XR12', 'MR18', 'MR12'))],
           T(296, 342, 'a família inteira', 'lbl'))
    return svg('O nome no título → as mesas', g, 354)

def _surface(v):  # 4.1.2 (v=1) e 4.2.8 (v=2): a superfície da X32/M32 com os botões de que o slide fala
    g = '<rect x="10" y="30" width="190" height="122" rx="9" class="panel"/>' + T(22, 48, 'CHANNEL STRIP', 'zl', 'start')
    for i, cx in enumerate((46, 100)):
        g += C(cx, 92, 15, 'knob') + f'<line x1="{cx}" y1="92" x2="{cx + 8}" y2="80" class="needle"/>' + C(cx, 92, 22, 'curve' if i == 0 else 'curve2')
    g += T(73, 138, 'aceso · apagado', 'sm') + B(138, 78, 54, 28, 'VIEW', 'bx', 'icod')
    g += '<rect x="210" y="30" width="180" height="122" rx="9" class="panel"/>' + '<rect x="220" y="40" width="84" height="102" rx="5" class="bxd"/>'
    g += ''.join(B(310, 40 + i * 26, 76, 22, t, 'bx', 'icod') for i, t in enumerate(('VIEW', 'UTILITY', 'SETUP', 'METERS')))
    g += T(200, 172, 'SELECT · sempre um canal selecionado', 'sm')
    for i in range(8):
        x = 46 + i * 44
        g += f'<rect x="{x - 13}" y="182" width="26" height="12" rx="3" class="{"bxo" if i == 2 else "bx"}"/>' + fader(x, 204, 84, (30, 52, 18, 44, 60, 36, 50, 24)[i])
    if v == 1:
        g += HL(132, 72, 66, 40, 1) + HL(306, 36, 84, 30, 1) + HL(26, 178, 356, 20, 2) + HL(18, 64, 112, 82, 3) + HL(306, 62, 84, 30, 4)
        g += O(3, T(262, 96, 'apagado =', 'sm'), T(262, 114, 'não existe', 'sm'))
        g += O(4, T(262, 96, 'funções', 'sm'), T(262, 114, 'da tela', 'sm'))
        return svg('X32 e M32: botões da superfície', g, 296)
    g += HL(132, 72, 66, 40, 1) + HL(26, 178, 356, 20, 2) + HL(18, 64, 112, 82, 3) + HL(306, 36, 84, 30, 4)
    g += T(200, 306, 'SETUP: o que a cena não salva · METERS: RTA', 'lbl')
    # checklist P48: a tela mostra a página que o VIEW abre (abas e a curva do EQ), em vez de um retângulo vazio
    g += S(4, '<rect x="224" y="46" width="34" height="20" rx="3" class="bxo"/>', T(241, 61, 'EQ', 'sm'), '<rect x="261" y="46" width="40" height="20" rx="3" class="bx"/>', T(281, 61, 'DYN', 'sm'),
           P('M226 118 C244 118 248 88 262 88 C276 88 280 118 300 118', 'curve'), L(226, 118, 300, 118, 'grid'))
    return svg('View, Select e o anel de LED', g, 310)
@d
def surf412(): return _surface(1)
@d
def surf428(): return _surface(2)
@d
def layers():  # 4.2.9: 8 faders e camadas; playback na camada 17–32, comandada por um DCA na camada principal
    g = T(60, 40, 'CAMADAS', 'zl')
    for i, t in enumerate(('1–8', '9–16', '17–24', '25–32', 'DCA')):
        g += B(14, 52 + i * 38, 92, 30, t, 'bxo' if i == 0 else 'bx', 'b')
    for i in range(8):
        x = 148 + i * 32
        g += B(x - 13, 50, 26, 22, str(i + 1), 'bx', 'icod') + fader(x, 80, 110, (40, 60, 30, 70, 50, 20, 64, 44)[i])
    g += S(1, P('M136 202 v8 h256 v-8', 'ctl'), T(264, 228, '8 canais por vez: troque de camada', 'lbl'), L(108, 67, 132, 67, 'ln'))
    g += S(2, B(14, 256, 160, 46, 'camada 17–32\nplayback, faixas', 'bxg', 'sm'), L(174, 279, 214, 279, 'ln'),
           B(216, 256, 174, 46, 'DCA na camada\nprincipal', 'bxo', 'sm')) + HL(10, 124, 100, 72, 2) + HL(10, 200, 100, 38, 2)
    return svg('Só 8 faders: camadas e DCA', g, 312)
@d
def appmatrix():  # 3.1.4: família × aparelho; cada bullet acende a sua linha; o 5º risca os apps de tablet e mostra os substitutos
    g = T(195, 44, 'TABLET', 'zl') + T(325, 44, 'COMPUTADOR', 'zl')
    rows = [('X AIR', 'X AIR\niPad/Android', 'X AIR Edit'), ('M AIR', 'M AIR\niPad/Android', 'M AIR Edit'), ('X32', 'X32-Mix\niPad', 'X32-Edit'), ('M32', 'M32-Mix\niPad', 'M32-Edit')]
    for i, (f_, a, b) in enumerate(rows):
        y = 56 + i * 52
        g += S(1, B(10, y, 110, 44, f_, 'bxb', 'b'), B(132, y, 126, 44, a, 'bx', 'sm'), B(266, y, 124, 44, b, 'bx', 'sm'))
    g += S(3, *[L(140, 78 + i * 52, 250, 78 + i * 52, 'curve4') for i in range(4)], B(132, 270, 258, 40, 'tablet hoje: MX-Mix · celular: MX-Q', 'bxo', 'b'))
    return svg('Apps por família e aparelho', g, 320)
@d
def xr16usb():  # 1.2.4: o USB da XR16 grava só estéreo; não é interface de áudio
    g = B(10, 40, 120, 70, 'XR16', 'bxd', 'b tw')
    g += S(1, B(78, 84, 46, 20, 'USB A', 'bxo', 'tiny'), L(126, 94, 176, 94, 'ln'), B(178, 72, 92, 44, 'pendrive\nou HD', 'bx', 'sm'), L(270, 94, 300, 94, 'ln'),
           '<rect x="304" y="78" width="86" height="12" rx="3" class="bar"/><rect x="304" y="98" width="86" height="12" rx="3" class="bar"/>', T(347, 70, 'L / R', 'b'), T(347, 132, 'só estéreo', 'lbl'),
           L(70, 110, 70, 172, 'lnx'), X(70, 140), B(10, 174, 150, 50, 'computador\n(multipista)', 'bx', 'sm'), T(170, 205, 'não é interface de áudio', 'lblr', 'start'))
    g += S(2, B(10, 246, 380, 44, 'descontinuada? confira com o distribuidor', 'bxg', 'sm'))
    return svg('XR16: USB só em estéreo', g, 300)
@d
def xr12card():  # 1.2.5: a XR12 em quatro pontos, um por bullet
    g = S(1, *[C(24 + i * 15, 62, 6, 'knob') for i in range(12)], T(106, 96, '12 entradas físicas', 'sm'), L(206, 62, 232, 62, 'ln'),
          *[f'<rect x="{240 + i * 9.4:.1f}" y="48" width="6" height="28" rx="2" class="bar"/>' for i in range(16)], T(315, 98, '16 canais · 6 buses', 'b'))
    g += S(2, B(10, 108, 92, 38, 'USB A', 'bxo', 'b'), L(102, 127, 136, 127, 'ln'), B(138, 108, 100, 38, 'pendrive', 'bx', 'sm'), T(250, 132, 'só estéreo', 'lbl', 'start'))
    g += S(3, C(40, 186, 18, 'knob'), P('M40 186 l0 -14 M40 186 l12 8 M40 186 l-12 8', 'mk'), X(40, 180), T(70, 192, 'sem cooler', 'b', 'start'))
    g += S(4, B(10, 226, 186, 54, 'saídas: sem delay\nnem inversão de Ø', 'bxr', 'sm'), T(206, 258, 'só os canais têm', 'b', 'start'))
    return svg('XR12: faltam conectores, não recursos', g, 290)
@d
def xtouch():  # 4.2.10: mesa sem faders → app; faders físicos = X-Touch pela rede (modo Xctl); o lado da X-Touch fica à direita (o 1º slide recorta sem ele)
    g = B(10, 40, 126, 50, 'X32 Rack', 'bxd', 'b tw') + B(150, 40, 126, 50, 'M32C', 'bxd', 'b tw') + B(78, 150, 130, 46, 'app / PC', 'bx', 'b')
    g += S(1, L(110, 148, 73, 92, 'ln2'), T(10, 232, 'X32 Rack: painel lento', 'sm', 'start'))
    g += S(2, L(176, 148, 213, 92, 'ln2'), T(10, 254, 'M32C: o painel só configura', 'sm', 'start'))
    g += S(3, L(278, 65, 300, 65, 'ln2'), B(302, 40, 88, 50, 'rede\nEthernet', 'bxg', 'sm'), L(346, 90, 346, 108, 'ln2'),
           '<rect x="296" y="110" width="94" height="130" rx="8" class="bxd"/>', T(343, 130, 'X-Touch', 'b tw'),
           *[fader(314 + i * 20, 142, 74, (30, 14, 46, 24)[i]) for i in range(4)], T(343, 262, 'firmware 3.0+', 'sm'))
    g += S(4, B(10, 280, 380, 50, 'X-Touch: modo Xctl + Scan\nM32-Edit: X-Touch over Ethernet', 'bxo', 'sm'))
    return svg('Sem faders: app e X-Touch pela rede', g, 340)
@d
def preamp():  # 5.1.3: ganho, 48 V com o canal mutado, Ø e o medidor sem vermelho
    g = '<rect x="10" y="30" width="120" height="270" rx="9" class="panel"/>' + T(70, 50, 'CANAL', 'zl')
    g += C(70, 92, 22, 'knob') + '<line x1="70" y1="92" x2="84" y2="76" class="needle"/>' + T(70, 136, 'GAIN', 'icod')
    g += B(26, 152, 88, 30, '+48 V', 'bx', 'icod') + B(26, 194, 88, 30, 'Ø', 'bx', 'icod') + B(26, 236, 88, 30, 'MUTE', 'bx', 'icod')
    g += '<rect x="148" y="40" width="26" height="260" rx="3" class="zgr"/><rect x="148" y="40" width="26" height="30" class="zr"/><rect x="148" y="70" width="26" height="60" class="zy"/>'
    g += '<rect x="148" y="130" width="26" height="170" class="zg"/>'
    g += S(1, L(96, 92, 140, 128, 'ln'), T(190, 62, 'Gain: levanta o sinal', 'b', 'start'), T(190, 82, 'do mic; não é o volume final', 'sm', 'start'))
    g += S(2, B(26, 152, 88, 30, '+48 V', 'bxo', 'ico'), B(26, 236, 88, 30, 'MUTE', 'bxr', 'ico'), T(190, 132, '+48 V: ligue com', 'b', 'start'), T(190, 152, 'o canal mutado', 'sm', 'start'))
    g += S(3, B(26, 194, 88, 30, 'Ø', 'bxo', 'ico'), P('M190 206 q15 -24 30 0 t30 0 t30 0', 'curve'), P('M190 206 q15 24 30 0 t30 0 t30 0', 'curve3'),
           T(290, 200, 'dois mics', 'sm', 'start'), T(290, 218, 'se cancelam', 'sm', 'start'), T(190, 252, 'Ø inverte a polaridade', 'b', 'start'))
    g += S(4, L(140, 70, 182, 70, 'thr'), OK(198, 284), T(214, 292, 'nunca no vermelho', 'lbl', 'start'))
    return svg('Pré-amplificador: ganho, 48 V e Ø', g, 306)
@d
def gain521():  # 5.2.1: a meta (−18 e picos 3 a 6 dB acima), o teto de 0 dBFS e o 1º LED laranja da X32
    m = '<rect x="40" y="40" width="54" height="250" rx="4" class="zgr"/><rect x="40" y="40" width="54" height="30" class="zr"/><rect x="40" y="70" width="54" height="70" class="zy"/><rect x="40" y="140" width="54" height="150" class="zg"/>'
    g = m + S(1, L(30, 140, 110, 140, 'thr'), T(118, 145, '−18 dBFS: a média', 'b', 'start'), P('M104 112 h10 v26 h-10', 'ctl'), T(118, 124, 'picos até −12 / −6', 'sm', 'start'))
    g += S(2, L(30, 70, 110, 70, 'axis'), T(118, 66, '0 dBFS: o teto', 'lblr', 'start'), T(118, 86, 'acima, só distorção', 'sm', 'start'))
    leds = ['zr', 'dotc', 'dotc', 'dotc', 'dotc', 'zg', 'zg', 'zg', 'zg', 'zg']; DIM = ' opacity=".35"'
    g += S(3, T(320, 36, 'X32', 'zl'), *[f'<rect x="306" y="{48 + i * 24}" width="28" height="16" rx="3" class="{c}"{DIM if i < 4 else ""}/>' for i, c in enumerate(leds)],
           P('M346 152 h-8', 'ln'), T(354, 158, '−18', 'b', 'start'), T(320, 300, '1º LED laranja', 'lbl'))
    return svg('A meta de ganho no medidor', g, 310)
@d
def gain0vs18():  # 5.2.2: mirar 0 × mirar −18 (headroom), nível igual entre canais e pré mais limpo
    met = lambda x, lvl, pk: (f'<rect x="{x}" y="50" width="44" height="220" rx="4" class="zgr"/><rect x="{x}" y="{lvl}" width="44" height="{270 - lvl}" class="zg"/>'
                              + f'<rect x="{x}" y="{pk}" width="44" height="6" class="{"zr" if pk < 60 else "zy"}"/>')
    g = T(82, 34, 'MIRA 0', 'zl') + met(60, 70, 46) + X(82, 290) + T(162, 34, 'MIRA −18', 'zl') + met(140, 150, 110) + OK(162, 290)
    g += L(54, 50, 192, 50, 'axis') + T(48, 55, '0 dBFS', 'sm', 'end')
    g += S(1, P('M190 56 h8 v92 h-8', 'ctl'), T(206, 98, 'headroom:', 'b', 'start'), T(206, 116, 'os picos cabem', 'sm', 'start'))
    g += S(2, *[f'<rect x="{300 + i * 26}" y="150" width="18" height="120" rx="3" class="zg"/>' for i in range(4)], L(292, 150, 398, 150, 'thr'),
           T(345, 288, 'nível igual entre canais', 'sm'), T(345, 306, 'presets funcionam', 'lbl'))
    g += S(3, C(240, 210, 20, 'knob'), '<line x1="240" y1="210" x2="232" y2="193" class="needle"/>', T(240, 250, 'pré moderado:', 'sm'), T(240, 268, 'som mais limpo', 'lbl'))
    return svg('Por que −18 e não 0', g, 314)
@d
def bustap():  # 10.2.3: dois "pré/pós": o do envio (no canal) e o da saída (no bus)
    g = B(10, 44, 76, 40, 'Canal', 'bx') + L(86, 64, 104, 64, 'ln') + B(106, 44, 60, 40, 'EQ', 'bx') + L(166, 64, 184, 64, 'ln') + B(186, 44, 74, 40, 'Fader', 'bxb') + L(260, 64, 292, 64, 'ln') + B(294, 44, 96, 40, 'Main LR', 'bxb')
    g += P('M176 64 L176 128 L196 128', 'lnd') + B(198, 108, 88, 40, 'envio', 'bxg') + T(150, 172, 'pré/pós do ENVIO', 'lbl')
    g += L(286, 128, 304, 128, 'ln') + B(306, 108, 84, 40, 'Bus 5', 'bxo') + L(348, 148, 348, 204, 'ln') + B(296, 206, 94, 40, 'Aux Out 5', 'bxb') + T(270, 274, 'pré/pós da SAÍDA', 'lbl')
    g += HL(170, 100, 124, 56, 1) + O(1, T(150, 196, 'X AIR: Sends', 'b')) + HL(290, 196, 106, 58, 2) + O(2, T(250, 294, 'X AIR: Aux Out', 'b'))
    g += HL(290, 196, 106, 58, 3) + O(3, T(250, 294, 'X32/M32: Routing → Out', 'b'))
    g += O(4, T(150, 196, 'envios: pré', 'b'), T(250, 294, 'saída do monitor: post fader', 'b'))
    return svg('Dois pré/pós: envio × saída do bus', g, 304)
@d
def reaper():  # 19.2.4: Preferences › Audio › Device do Reaper
    g = '<rect x="10" y="34" width="380" height="250" rx="10" class="bxd"/>' + T(24, 56, 'Preferences › Audio › Device', 'b tw', 'start') + L(10, 68, 390, 68, 'grid')
    rows = [(1, 'Audio system', 'ASIO'), (1, 'Driver', 'o da mesa'), (2, 'Entradas', '1–18 (X AIR) · 1–32 (X32)'), (2, 'Taxa', '48000 Hz'), (2, 'Buffer', '256')]
    for i, (k, a, b) in enumerate(rows):
        y = 80 + i * 40
        g += S(k, T(24, y + 22, a, 'sm', 'start'), B(140, y, 238, 32, b, 'bxo' if a in ('Taxa', 'Audio system') else 'bx', 'b'))
    return svg('Reaper: a tela que importa', g, 294)
def _x32scenes(v):  # 16.1.2 (v=1) e 16.2.2 (v=2): cena × snippet × cue list na X32/M32
    g = T(10, 44, 'CENA · até 100', 'zl', 'start')
    g += ''.join(B(10 + i * 44, 54, 38, 38, str(i + 1), 'bx', 'b') for i in range(5)) + T(232, 79, '… 100', 'sm', 'start') + T(296, 79, 'mesa toda', 'b', 'start')
    g += T(10, 126, 'SNIPPET · só uma parte', 'zl', 'start')
    if v == 1: g += ''.join(f'<rect x="{10 + i * 24}" y="138" width="18" height="52" rx="3" class="{"bxo" if i in (2, 3) else "bx"}"/>' for i in range(10)) + T(250, 160, 'EQ e efeitos', 'b', 'start') + T(250, 180, 'da voz', 'sm', 'start')
    else:  # rodada 2: a 2ª versão mostra o exemplo da bateria (9 canais + DCA + efeitos) e o cadeado do "não carrega"
        g += ''.join(f'<rect x="{10 + i * 24}" y="138" width="18" height="52" rx="3" class="{"bxo" if i < 9 else "bx"}"/>' for i in range(10)) + T(250, 160, 'bateria: 9 canais', 'b', 'start') + T(250, 180, '+ DCA + efeitos', 'sm', 'start')
    g += T(10, 222, 'CUE LIST · até 500', 'zl', 'start') + ''.join(B(10 + i * 84, 232, 78, 34, t, 'bx', 'sm') for i, t in enumerate(('cena', 'snippet', 'MIDI'))) + B(268, 232, 58, 34, 'GO', 'bxr', 'b')
    if v == 1: g += HL(4, 48, 390, 50, 1) + HL(4, 132, 390, 64, 2)
    else:
        g += HL(4, 132, 390, 64, 1)
        g += S(2, B(10, 282, 380, 46, 'não carrega? Recall Scope · Param Safe · Channel Safe', 'bxo', 'sm'),
               '<path d="M376 62 v-6 a7 7 0 0 1 14 0 v6" style="fill:none;stroke:var(--accent);stroke-width:2.2"/><rect x="372" y="62" width="22" height="18" rx="3" style="fill:var(--bg-3);stroke:var(--accent);stroke-width:2"/>',
               T(296, 99, 'parte protegida', 'lbl', 'start'))
    return svg('X32/M32: cena, snippet e cue list', g, 338 if v == 2 else 276)
@d
def x32sc1(): return _x32scenes(1)
@d
def x32sc2(): return _x32scenes(2)
@d
def fxhow():  # 13.2.4: reverb por envio (X32) e o erro do retorno fora do LR (X AIR) em cima; como inserir (X AIR e X32) embaixo (o 1º slide recorta só a metade de cima)
    g = T(10, 36, 'ENVIO (REVERB)', 'zl', 'start')
    for i, t in enumerate(('envio\ndo canal', 'master\ndo bus', 'Reverb', 'FX Return\nsubido')):
        g += B(10 + i * 88, 50, 76, 52, t, 'bxo' if t == 'Reverb' else 'bx', 'sm') + (L(86 + i * 88, 76, 96 + i * 88, 76, 'ln') if i < 3 else '')
    g += L(350, 76, 358, 76, 'ln') + B(360, 58, 32, 36, 'LR', 'bx', 'icod') + HL(4, 44, 350, 64, 1)
    g += S(3, B(360, 58, 32, 36, 'LR', 'bxr', 'icod'), X(376, 118), T(392, 150, 'LR fechado: silêncio', 'lblr', 'end'))
    g += S(4, L(10, 172, 390, 172, 'sep'), T(10, 196, 'INSERT', 'zl', 'start'), B(10, 208, 180, 46, 'slot 1 · tipo GEQ', 'bx', 'sm'), B(10, 264, 180, 46, 'canal abaixo do slot', 'bx', 'sm'),
           B(214, 208, 176, 46, 'INSERT', 'bxo', 'ico'), T(302, 274, 'X AIR: ative Insert', 'lbl'))
    return svg('Onde o efeito some', g, 320)
@d
def xrexp():  # 20.2.6 (enxugamento): o DN4816-O faz o split das 16 entradas para a casa; a XR18 fica com os in-ears
    g = B(130, 40, 140, 52, 'XR18 / MR18', 'bxd', 'b tw') + B(166, 92, 68, 22, 'Ultranet', 'bxo', 'tiny')
    # rodada 6: sem frases (estão nos bullets); in-ears = fone, clip = LED vermelho nas duas mesas
    g += S(3, L(270, 66, 300, 66, 'ln'), P('M304 84 Q304 56 326 56 Q348 56 348 84', 'mk'), f'<rect x="298" y="80" width="10" height="16" rx="3" class="knob"/><rect x="344" y="80" width="10" height="16" rx="3" class="knob"/>')
    g += S(1, P('M200 114 L200 150 L120 150 L120 168', 'ln'), B(50, 170, 140, 44, 'DN4816-O', 'bxo', 'b'))
    g += S(2, L(120, 214, 120, 252, 'ln'), B(40, 254, 160, 50, 'mesa de PA\nda casa', 'bxb'))
    g += S(4, '<rect x="252" y="46" width="12" height="40" rx="2" class="zgr"/><rect x="252" y="46" width="12" height="12" rx="2" class="zr"/>',
           '<rect x="182" y="260" width="12" height="40" rx="2" class="zgr"/><rect x="182" y="260" width="12" height="12" rx="2" class="zr"/>', P('M258 92 Q300 180 196 262', 'lnd'))
    return svg('Expansão da XR18 pela Ultranet', g, 320)

REGRAS = [  # (regex no título minúsculo, diagrama) — a primeira que casar vence; cada regex só casa no início de palavra
    (r'^(xr16|xr12)\b', 'panel_xr16'), (r'^x18 × xr18', 'panel_xr18'), (r'^a família', 'families'), (r'^phantom', 'phantom'),
    (r'cart(ão|ões) sd', 'sdcard'), (r'firmware', 'firmware'), (r'sincroniza', 'sync'), (r'virtual soundcheck', 'vsc'), (r'\blive\b', 'live'),
    (r'pendrive|tocar música', 'pendrive'), (r'sends on faders', 'sof'), (r'automix', 'automix'),
    (r'talkback', 'talkback'), (r'oscilador', 'osc'), (r'solo|pfl|afl|fonte de monitor|delay da escuta', 'solo'),
    (r'por midi', 'midi'), (r'mute group', 'mutegrp'), (r'dca|subgrupo', 'dca'), (r'crossover', 'crossover'), (r'subwoofer|aux-fed', 'auxsub'),
    (r'delay de saída', 'tower'), (r'matriz|fora da caixa', 'matrix'), (r'pontos de (captação|tomada)|tap point|pré/pós|pré-fader|pós-fader', 'taps'),
    (r'buses|aux e mix', 'buses'), (r'ultranet|p16', 'ultranet'), (r'efeito|rack de|reverb|slots', 'fx'), (r'stereo × dual', 'dual'),
    (r'três jeitos', 'sof'), (r'retorno|in-ear|fone de ouvido|vias', 'retornos'), (r'dividir o palco|duas mesas', 'split'),
    (r'blocos de 8|user in', 'source'), (r'aes50|stagebox|remotos', 'aes50'), (r'snapshot|cena|safe|backup', 'scenes'),
    (r'afinar|ruído rosa', 'pink'), (r'\brta\b|espectro|ring out|na fonte|exagere', 'rta'), (r'medidor', 'meters'),
    (r'sidechain|ducking', 'duck'), (r'compress|dynamics', 'comp'), (r'gate|expansor|ducker', 'gate'),
    (r'low cut|hpf', 'hpf'), (r'\beq\b', 'eq'), (r'insert', 'insert'), (r'delay de canal|polaridade', 'chdelay'),
    (r'\bpan\b|stereo link', 'pan'), (r'caminho do sinal|roteiro completo|ordem de ajuste|do microfone ao pa', 'path'),
    (r'fonte do canal|patch|mesma entrada', 'source'), (r'ganho|−18|pré-amplificador|phantom', 'gain'),
    (r'hi-z|entradas estéreo|aux in', 'inputs'), (r'painel da xr18', 'panel_xr18'), (r'painel da xr16', 'panel_xr16'),
    (r'x32 rack|sem faders', 'panel_rack'), (r'm32c', 'panel_m32c'), (r'superfície|8 faders', 'surface'),
    (r'ordem de ligar|desligamento', 'power'), (r'padrão de fábrica|reset', 'reset'), (r'manutenção|calor|poeira', 'maint'),
    (r'onde o controle externo', 'tema'), (r'rede|wi-fi|roteador|remote|conexão|\bosc\b|segurança', 'network'),
    (r'\bapps?\b|edit\b|mixing station|tablet|tela principal|preferências|mx-mix', 'apps'),
    (r'multipista|grava|usb|interface de áudio', 'usbrec'),
    (r'nomes?, cor|copiar|presets|organize|preparar o show', 'naming'), (r'midi|daw|assign', 'midi'),
    (r'taxa de amostragem|clock|global', 'clock'),
    (r'erro|divergên|inconsist|lacuna|ensinam errado', 'errors'), (r'checklist|roteiro|como montar|boas práticas|estudo', 'checklist'),
    (r'organizado|legenda|termos|avisos', 'legend'),
    (r'nomes e versões|irmã|irmão|família|midas mr|comprar|diferenças|o que existe|comparativo', 'families'),
    (r'fonte|curso|séries|textos|podcast|comece|índice|onde estudar', 'sources'),
]
TEMA = {0: 'legend', 1: 'families', 2: 'inputs', 3: 'network', 4: 'apps', 5: 'gain', 6: 'eq', 7: 'gate', 8: 'comp', 9: 'path', 10: 'taps',
        11: 'retornos', 12: 'rta', 13: 'fx', 14: 'dca', 15: 'matrix', 16: 'scenes', 17: 'solo', 18: 'automix', 19: 'usbrec', 20: 'aes50',
        21: 'midi', 22: 'firmware', 23: 'checklist', 24: 'errors', 25: 'specfam', 26: 'sources', 27: 'terms'}

# ---------------------------------------------------------------- passada final (pendências 2.2, 2.7 e 3.9): um diagrama por slide onde o mesmo desenho se repetia
# em 3 a 6 slides seguidos; cada bullet acende a peça de que fala (data-step)
@d
def usbmulti():  # 19.1.2: o que vai para o computador: Routing (X AIR) e Card Out em blocos de 8 (X32/M32)
    g = S(1, B(10, 40, 120, 56, 'XR18 · X18\nMR18', 'bxd', 'b tw'), L(130, 68, 168, 68), B(170, 46, 104, 44, 'Routing', 'bxo'),
          L(274, 68, 298, 68), B(300, 40, 90, 56, '18 canais\nUSB', 'bxg', 'sm'), T(200, 120, 'você escolhe o que vai em cada canal USB', 'sm'))
    g += S(2, B(10, 146, 120, 56, 'X32 / M32', 'bxd', 'b tw'), L(130, 174, 168, 174), '<rect x="170" y="140" width="120" height="68" rx="8" class="panel"/>',
           T(230, 158, 'Card Out', 'b'), *[B(176 + (j % 2) * 56, 166 + (j // 2) * 20, 52, 18, t, 'bx', 'tiny') for j, t in enumerate(('1–8', '9–16', '17–24', '25–32'))],
           L(290, 174, 298, 174), B(300, 146, 90, 56, 'placa\nUSB', 'bxg', 'sm'), T(200, 232, 'entradas locais ou do stagebox, em blocos de 8', 'sm'))
    g += B(10, 252, 380, 44, 'Computador (DAW): uma pista por canal', 'bxb', 'b')
    return svg('Multipista: o que vai para o computador', g, 306)
@d
def usb1818():  # 19.2.2: driver, mesma taxa e 18×18 no Setup
    g = B(10, 44, 150, 84, 'XR18 · X18\nMR18', 'bxd', 'b tw') + L(160, 86, 238, 86, 'ln2') + T(199, 76, 'USB', 'b') + B(240, 44, 150, 84, 'Computador\n(DAW, OBS)', 'bxb')
    g += S(1, B(240, 146, 72, 44, 'Mac\ndireto', 'bxg', 'sm'), B(318, 146, 72, 44, 'Windows\ndriver', 'bxo', 'sm'))
    g += S(2, B(40, 146, 90, 36, '48 kHz', 'bx', 'b'), P('M130 164 Q200 214 270 194', 'lnd2'), T(200, 226, 'a mesma taxa nos dois lados', 'lbl'))
    g += S(3, '<rect x="10" y="246" width="380" height="54" rx="8" class="panel"/>', T(22, 278, 'SETUP', 'zl', 'start'),
           B(120, 256, 120, 34, '18 × 18', 'bxo', 'b'), B(250, 256, 120, 34, '2 × 2', 'bx', 'b'))
    return svg('USB 18 × 18 no computador', g, 310)
@d
def x32card():  # 19.2.3: cabo na placa, 32 in/32 out, Card Out e o modelo no DAW
    g = '<rect x="10" y="36" width="180" height="96" rx="9" class="bxd"/>' + T(100, 56, 'X32 / M32 · traseira', 'sm')
    g += B(24, 70, 74, 44, 'USB de\ncontrole', 'bx', 'sm') + B(106, 70, 74, 44, 'placa\nX-USB', 'bxo', 'sm')
    g += S(1, L(143, 114, 143, 150, 'ln'), P('M143 150 L300 150 L300 132', 'ln'), X(61, 128), B(240, 40, 150, 90, 'Computador\n(DAW)', 'bxb'))
    g += S(2, B(10, 168, 180, 40, 'Setup › Card: 32 in / 32 out', 'bx', 'sm'))
    g += S(3, B(210, 168, 180, 40, 'Card Out = o patch', 'bx', 'sm'))
    g += S(4, '<rect x="10" y="222" width="380" height="80" rx="8" class="panel"/>', T(22, 240, 'DAW', 'zl', 'start'),
           *[f'<rect x="{70 + j * 40}" y="250" width="32" height="18" rx="3" class="bx"/>' + C(86 + j * 40, 259, 4, 'dotc') for j in range(7)],
           T(200, 290, 'pistas armadas · salvo como modelo "X32 default"', 'sm'))
    return svg('Multipista na X32/M32: a placa', g, 312)
@d
def pendrec():  # 19.1.3: FAT32, WAV 16 bits, reprodução, Record na X32 e o LED de acesso (rodada 2: o menu de gravação fica no lado "grava"; a reprodução desce do pendrive direto ao canal)
    g = B(10, 44, 120, 56, 'Main LR\nou bus', 'bxb') + L(130, 72, 212, 72) + T(171, 62, 'grava', 'sm')
    g += S(1, B(214, 40, 176, 64, 'Pendrive FAT32\nporta USB tipo A', 'bxo'))
    g += S(2, T(292, 126, 'WAV · 16 bits · 2 GB ≈ 3 h', 'sm'))
    g += S(3, L(372, 104, 372, 168), T(364, 156, 'toca', 'sm', 'end'), B(250, 170, 140, 44, 'canal "USB"\nou Aux 7/8', 'bxg', 'sm'))
    g += S(4, L(150, 120, 150, 76, 'ctl'), B(10, 120, 200, 48, 'X32: View › Config ›\nRecord (encoder 5)', 'bx', 'sm'))
    g += S(5, C(36, 264, 10, 'zgr'), T(56, 270, 'LED de acesso apagado: só então tire o pendrive', 'lblr', 'start'))
    return svg('Gravador estéreo em pendrive', g, 290)
@d
def pendtap():  # 19.2.6 (pendência 2.2): USB frontal, a sua mix, o tap Pre/Post EQ do Main e a Direct Out da M32C
    g = B(10, 44, 110, 50, 'Main L/R', 'bxb') + L(120, 69, 158, 69) + '<rect x="160" y="40" width="120" height="58" rx="8" class="panel"/>' + T(220, 56, 'TAP', 'zl')
    g += B(166, 64, 52, 28, 'Pre EQ', 'bx', 'tiny') + B(222, 64, 52, 28, 'Post EQ', 'bx', 'tiny') + L(280, 69, 298, 69) + B(300, 44, 90, 50, 'Pendrive', 'bxo')
    g += S(1, T(345, 112, 'XR16 · XR12 · MR12:', 'sm'), T(345, 128, 'WAV no USB frontal', 'sm'))
    g += S(2, T(110, 124, 'X32 Producer:', 'b'), T(110, 142, 'USB › Config, fonte Main L/R', 'sm'))
    g += S(3, '<rect x="219" y="61" width="58" height="34" rx="8" class="hl"/>', L(170, 86, 214, 70, 'curve4'),
           T(220, 166, 'padrão: Pre EQ (o EQ do Main não entra)', 'lblr'))
    g += S(4, B(10, 194, 96, 44, 'mic de\npalestra', 'bx', 'sm'), L(106, 216, 148, 216), B(150, 194, 120, 44, 'Direct Out\n(pré-EQ)', 'bxo', 'sm'),
           L(270, 216, 298, 216), B(300, 194, 90, 44, 'gravador', 'bxg', 'sm'), T(200, 262, 'M32C: grava só aquele microfone', 'sm'))
    return svg('O que vai para o pendrive', g, 274)
@d
def snapxa():  # 16.1.1: 64 snapshots na mesa; shows e cenas no aparelho; Load
    g = B(10, 40, 380, 40, 'Snapshot: a "foto" do estado completo da mesa', 'bx', 'b')
    g += S(1, '<rect x="10" y="94" width="230" height="120" rx="9" class="bxd"/>', T(125, 114, 'NA MESA', 'zl'),
           *[f'<rect x="{22 + i * 30}" y="128" width="24" height="34" rx="4" class="{"bxo" if i == 2 else "bx"}"/>' for i in range(6)], T(208, 150, '… 64', 'sm', 'start'),
           T(125, 196, '64 posições', 'b tw'))
    g += S(2, '<rect x="252" y="94" width="138" height="120" rx="12" class="phone"/>', T(321, 114, 'NO APARELHO', 'zlc'),
           B(262, 126, 100, 30, 'Show: culto', 'bx', 'sm'), B(262, 162, 100, 30, 'Cena: ensaio', 'bxg', 'sm'))
    g += S(3, C(376, 177, 9, 'touch'), B(250, 230, 140, 40, 'segure › Load', 'bxo', 'b'), L(376, 188, 376, 228, 'ln'))   # rodada 2: o dedo fica fora da caixa da cena, sem cobrir texto nem borda
    return svg('Snapshots, cenas e shows (X AIR)', g, 282)
@d
def snapundo():  # 16.2.1: snapshot como "desfazer" e o padrão de emergência
    g = S(1, B(10, 50, 110, 50, 'mix boa\n(snapshot 3)', 'bxg', 'sm'), L(120, 75, 150, 75), B(152, 50, 110, 50, 'mix\ndesandou', 'bxr', 'sm'),
          P('M262 75 L300 75 L300 120 L65 120 L65 102', 'ln'), T(182, 140, 'recarregue o último bom', 'lbl'))
    g += S(2, B(10, 170, 160, 60, 'snapshot 64:\nPADRÃO', 'bxo'), T(232, 192, 'alguém mexeu', 'sm', 'start'), T(232, 210, 'na mesa?', 'sm', 'start'),
           P('M226 200 L180 200', 'ln'), T(200, 262, 'um "padrão" de emergência, sempre salvo', 'b'))
    return svg('Snapshot como "desfazer"', g, 274)
@d
def aes50road():  # 20.2.1: a analogia da estrada e o cabo certo
    g = B(10, 50, 90, 110, 'Mesa', 'bxd', 'b tw') + B(300, 50, 90, 110, 'Stagebox', 'bxd', 'b tw')
    g += '<rect x="104" y="58" width="192" height="94" rx="6" class="panel"/>' + ''.join(L(110, 64 + j * 6, 290, 64 + j * 6, 'sep') for j in range(7))
    g += ''.join(L(110, 112 + j * 6, 290, 112 + j * 6, 'sep') for j in range(7)) + L(110, 106, 290, 106, 'axis')
    g += L(150, 82, 250, 82) + T(200, 48, '48 faixas de ida →', 'b') + L(250, 130, 150, 130) + T(200, 172, '← 48 de volta', 'b')   # rótulos fora das faixas
    g += S(1, B(10, 196, 380, 50, 'Cat5e blindado: malha ligada nas duas pontas', 'bxo', 'b'), B(10, 258, 380, 46, 'etherCON: trava, um puxão não desconecta', 'bx', 'b'))
    return svg('AES50: uma estrada de 48 + 48 faixas', g, 314)
@d
def fwxa():  # 22.2.1: site oficial, versão do firmware × do app, antes do evento
    g = S(1, B(10, 40, 180, 50, 'site oficial', 'bxg', 'b'), OK(26, 59), B(210, 40, 180, 50, 'sites de terceiros', 'bxr', 'b'), X(222, 59))
    g += S(2, B(10, 116, 180, 50, 'firmware 1.17', 'bxo', 'b'), T(200, 146, '≠', 'mid'), B(210, 116, 180, 50, 'app 1.5', 'bx', 'b'),
           T(200, 190, 'são números diferentes: não confunda', 'sm'))
    g += S(3, B(10, 212, 180, 50, 'antes do evento', 'bxg', 'b'), OK(26, 231), B(210, 212, 180, 50, 'durante o evento', 'bxr', 'b'), X(222, 231))
    return svg('Firmware na X AIR: três cuidados', g, 274)
@d
def fwxm():  # 22.2.2: a tabela de 22.1.1, o backup e a versão instalada × a do site
    g = S(1, B(10, 40, 380, 46, 'passo a passo: tabela 22.1.1 (pendrive + botão ao ligar)', 'bx', 'sm'))
    g += S(2, B(10, 100, 200, 96, 'Backup antes:\ncenas · roteamento\nshows · snippets\npresets', 'bxo', 'sm'), L(210, 148, 268, 148), B(270, 120, 120, 56, 'Pendrive', 'bxg'),
           T(200, 214, 'a atualização pode apagar tudo isso', 'lblr'))
    g += S(3, B(10, 230, 180, 50, 'instalada\n(Setup › Global)', 'bx', 'sm'), T(200, 262, '↔', 'mid'), B(210, 230, 180, 50, 'a do site', 'bxb', 'sm'))
    return svg('Firmware na X32/M32: antes de atualizar', g, 292)

# figuras do PDF nos slides: saíram no enxugamento (o diagrama vive só no slide de conteúdo)

# Diagrama escolhido à mão por seção (revisão 2): vence as REGRAS por título. ('chave', {args}) passa argumentos;
# 'm'/'steps'/'v' dizem que bullet acende cada parte do desenho. No cap. 26, n = linhas reais da tabela da seção (build_slides).
PICK = {
    '0.3': 'terms', '0.4': 'avisos',
    '1.1.1': ('families', {'tall': True}), '1.1.2': 'siblings', '1.1.3': 'xairidea', '1.1.4': 'surface', '1.1.5': ('panel_xr18', {'hl': {(0, 0): 1, (0, 2): 2, (2, 0): 3, (0, 3): 4}}), '1.2.3': 'x18xr18', '2.2.3': ('reset', {'v': 2}), '1.1.6': 'x32rack', '1.1.7': 'famfeat',
    # rodada 3: diagrama próprio onde o genérico do capítulo se repetia
    '2.1.6': 'ligacoes', '4.1.4': ('naming', {'v': 1}), '4.2.11': ('naming', {'v': 2}), '4.2.4': 'msta', '5.1.1': ('path', {'hl': True}), '5.2.11': 'dualin',
    '8.2.3': 'stackcomp', '8.2.5': 'parcomp', '11.2.3': 'inear', '11.2.5': 'morevias', '12.2.5': 'noexag',
    '13.2.3': ('fx', {'hl': True}), '13.2.7': 'fxmon', '15.2.5': 'xairdelay', '16.2.3': 'backup', '19.2.1': 'quemgrava', '20.1.1': ('aes50', {'hl': True}),
    '20.1.2': ('split', {'hl': True}), '20.2.4': 'userin', '20.2.5': 'splitdl32', '21.1.7': 'cfgtabs', '21.2.1': 'onde',
    '19.1.2': 'usbmulti', '19.2.2': 'usb1818', '19.2.3': 'x32card', '19.1.3': 'pendrec', '19.2.6': 'pendtap', '16.1.1': 'snapxa', '16.2.1': 'snapundo',
    '20.2.1': 'aes50road', '22.2.1': 'fwxa', '22.2.2': 'fwxm',  # passada final: um desenho por slide (pendências 2.2, 2.7, 3.9)
    '1.2.2': 'network', '1.2.6': 'xrmr', '1.2.7': 'x32bodies', '1.2.8': 'm32fam', '1.2.9': 'xaxm', '1.2.10': 'usedbuy',
    '3.1.1': ('remote3', {'m': (1, 2, 3, 4)}), '3.2.2': ('remote3', {'m': (0, 1, 2, 3)}), '3.1.2': 'firstconn', '3.1.3': 'router', '3.1.5': 'oscproto',
    '3.2.1': 'usbctl', '3.2.3': 'wifi', '3.2.4': 'router', '3.2.5': ('router', {'v': 2}), '3.2.6': 'netgood', '3.2.8': 'netsec',
    '4.1.1': ('appscreen', {'m': (1, 2, 3)}), '4.1.5': 'copypaste', '4.1.6': 'prefs', '4.2.2': ('appscreen', {'tabs': (1, 2, 3)}), '4.2.3': 'x32edit',
    '4.2.7': 'appswap', '4.2.12': ('copypaste', {'v': 2}), '4.2.1': ('apps', {'v': 1}), '4.2.6': ('apps', {'v': 2}), '4.2.13': 'template',
    '5.2.3': 'gainsteps', '5.2.4': 'gainfader', '5.2.5': 'gainruler', '5.2.6': 'gainchain', '5.2.7': 'trim', '6.2.4': 'eqvoice', '6.2.2': ('eq', {'v': 1}), '7.2.2': ('gate', {'v': 1}),
    '10.1.3': ('busconfig', {'m': (1, 2, 3, 4, 5)}), '10.2.4': 'busconfig', '11.2.2': 'buschain', '11.2.4': 'phones', '11.2.6': 'leak', '12.2.2': 'micplan',
    '13.1.4': 'fxlib', '13.2.1': 'fxrack', '13.2.2': 'insert', '13.2.5': 'revenv', '13.2.6': 'rackplans', '17.1.3': 'monodelay',
    '18.1.1': ('automix', {'steps': True}), '18.2.1': 'automix2', '19.1.4': ('sdcard', {'v': 1}), '19.2.8': ('sdcard', {'v': 2}),
    '21.1.1': 'midimap', '21.1.2': 'midiscene', '21.1.3': 'm32midi', '21.1.4': 'assign',
    '23.2.1': 'mixorder', '23.2.2': 'churchflow', '23.2.3': 'studypath',
    '24.1.1': 'err241', '24.2.1': 'err242', '24.2.2': 'err243', '24.2.3': 'err244',
    '25.1.1': 'specxa', '25.1.2': 'specxm', '25.2.1': 'specfam',
    '26.1.1': 'sources',
    # rodada 4: diagrama do assunto onde o de outro tópico se repetia
    '0.2': 'namemap', '1.2.4': 'xr16usb', '1.2.5': 'xr12card', '3.1.4': 'appmatrix', '4.1.2': 'surf412', '4.2.8': 'surf428', '4.2.9': 'layers', '4.2.10': 'xtouch',
    '5.1.3': 'preamp', '5.2.1': 'gain521', '5.2.2': 'gain0vs18', '10.2.3': 'bustap', '13.2.4': 'fxhow', '16.1.2': 'x32sc1', '16.2.2': 'x32sc2',
    '19.2.4': 'reaper', '20.2.6': 'xrexp',
}
def escolhe(cap, titulo):
    t = titulo.lower()
    for rx, k in REGRAS:  # (?<!\w): "curso" não casa em "recursos", "reset" em "presets", "dca" em "podcasts"
        if re.search(r'(?<!\w)(?:' + rx + ')', t): return TEMA.get(cap) if k == 'tema' else k
    return TEMA.get(cap)

# ---------------------------------------------------------------- rodada 5 (revisão de redundância): diagramas de slides fundidos; o desenho traz o dado, o bullet traz o resto
@d
def ligacoes_w():  # 2.1.6 (checklist P46): slide largo, sem bullet; cada cenário numa coluna, a ligação embaixo
    rows = [('Gravação\ncom iPad', 'USB: até 18\npistas no iPad', 'bxg'), ('Show com\ntablet', 'P16 no Ultranet:\num retorno\npor músico', 'bxg'),
            ('Bar / clube', 'pendrive grava;\npedal MIDI\ntroca a cena', 'bxg'), ('XR12 / MR12\n(4 pré-amps)', 'mesa analógica\nsoma as\nfontes extras', 'bxo'),
            ('X32 · M32C\ncom stagebox', 'S16, DL16 ou\nDL32 por AES50', 'bxb')]
    g = T(0, 46, 'CENÁRIO', 'zl', 'start') + T(0, 156, 'COMO LIGAR', 'zl', 'start')
    for i, (a, b, c) in enumerate(rows):
        x = 120 + i * 136
        g += B(x, 30, 126, 64, a, 'bx', 'b') + L(x + 63, 94, x + 63, 126, 'ln') + B(x, 128, 126, 86, b, c, 'b')
    return svg('Cenário → o que liga onde', g, 224).replace('viewBox="0 0 400 224"', 'viewBox="0 0 800 224"')
@d
def day3_w():  # 23.2.4 (checklist P55): slide largo; as três fases lado a lado
    g = ''
    cols = (('ANTES', ('firmware em dia', 'show pronto', 'rede própria · Mixer → PC')),
            ('NA PASSAGEM', ('mute antes do 48 V', 'ganho em −18 dBFS', 'retornos pré-fader')),
            ('DEPOIS', ('salve a cena e o backup', 'desligue as caixas', 'e só depois a mesa')))
    for i, (k, items) in enumerate(cols):
        x = i * 268
        g += f'<rect x="{x}" y="30" width="256" height="150" rx="9" class="panel"/>' + T(x + 16, 58, k, 'zl', 'start')
        g += ''.join(T(x + 16, 94 + j * 30, t, 'b', 'start') for j, t in enumerate(items))
    return svg('Antes, na passagem, depois', g, 190).replace('viewBox="0 0 400 190"', 'viewBox="0 0 800 190"')
@d
def scenes2():  # 16.1.1: onde mora cada memória, X AIR | X32/M32 (fusão de 16.1.1 e 16.1.2)
    S = lambda k, *xs: ''.join(xs)   # rodada 6: desenho fixo; o slide só tem 2 bullets (recall filtrado e o "desfazer")
    g = T(100, 40, 'X AIR / M AIR', 'zl') + T(300, 40, 'X32 / M32', 'zl') + L(200, 30, 200, 330, 'sep')
    g += S(1, '<rect x="10" y="54" width="180" height="118" rx="9" class="bxd"/>', T(100, 76, 'NA MESA', 'zlc'),
           *[f'<rect x="{24 + i * 26}" y="88" width="20" height="34" rx="4" class="{"bxo" if i == 1 else "bx"}"/>' for i in range(5)], T(160, 110, '… 64', 'sm', 'start'),
           T(100, 156, 'snapshots', 'bb'))
    g += S(2, '<rect x="10" y="186" width="180" height="144" rx="12" class="phone"/>', T(100, 208, 'NO APARELHO', 'zlc'),
           B(26, 222, 148, 40, 'show', 'bx', 'b'), B(26, 272, 148, 40, 'cena .scn', 'bxg', 'b'))
    g += S(3, B2(210, 54, 180, 84, 'CENA × 100\na mesa toda', 'bxo'))
    g += S(4, B2(210, 150, 180, 84, 'SNIPPET\nsó uma parte', 'bxg'), B2(210, 246, 180, 84, 'CUE LIST × 500\nGO dispara', 'bxb'))
    return svg('Onde mora cada memória', g, 340)
@d
def midimap2():  # 21.1.1: mapa MIDI das duas famílias (fusão de 21.1.1 e 21.1.2); os bullets ficam com o que o mapa não mostra
    g = T(100, 40, 'X AIR / M AIR', 'zl') + T(300, 40, 'X32 / M32', 'zl') + L(200, 30, 200, 342, 'sep')
    xa = [('canal 1 · PC 1–64', '→ snapshots', 'bxo'), ('canal 1 · CC 0–15', '→ faders 1–16', 'bxg'), ('CC 21–26 · CC 31', '→ Aux · Main', 'bxg'),
          ('canal 2 · canal 3', '→ mutes · pan', 'bx')]
    xm = [('canal 1 · PC 1–100', '→ cenas', 'bxo'), ('M32 · canal 2', '→ snippets', 'bxg'), ('M32 · canais 3–6', '→ cues', 'bxg'), ('cena carregada', '→ PC, CC, Note (luz)', 'bxb')]
    for col, x in ((xa, 10), (xm, 210)):
        for i, (a, b, c) in enumerate(col):
            y = 54 + i * 72
            g += B(x, y, 180, 62, '', c) + T(x + 90, y + 26, a, 'b') + T(x + 90, y + 48, b, 'sm')
    return svg('Mensagem → o que a mesa faz', g, 350)
@d
def retorno1():  # 11.1.1 (rodada 6): um retorno mono, do canal à caixa; in-ear e P16 ficam nos slides deles
    g = ''.join(B(10 + i * 92, 34, 84, 40, n, 'bx', 'b') for i, n in enumerate(('Voz', 'Violão', 'Teclas')))
    g += ''.join(L(52 + i * 92, 74, 100, 128, 'ln') for i in range(3))
    g += ''.join(P(f'M{52 + i * 92} 74 Q{180 + i * 30} 96 318 128', 'lnd') for i in range(3))
    g += B(30, 130, 140, 48, 'Bus 1\nretorno 1', 'bxg', 'b') + B(270, 130, 120, 48, 'Main LR\nPA', 'bxb', 'b') + HL(265, 125, 130, 58, 2) + HL(25, 125, 150, 58, 2)
    g += L(100, 178, 100, 206, 'ln') + B(30, 208, 140, 40, 'Aux Out 1', 'bxo', 'b') + HL(25, 203, 150, 50, 1)
    g += L(100, 248, 100, 270, 'ln') + '<polygon points="70,272 130,272 140,312 60,312" class="wedge"/>' + T(100, 334, 'caixa de retorno', 'sm')
    g += S(3, P('M206 168 Q206 140 226 140 Q246 140 246 168', 'mk'), L(170, 154, 200, 154, 'lnd'), T(226, 196, 'Solo', 'b'))
    g += S(5, P('M170 172 Q250 290 320 178', 'lnx'), X(248, 226), T(330, 252, 'LR do bus', 'lblr'))  # checklist P02: o retorno não vai ao PA (antes era o slide 11.2.6)
    return svg('Um retorno: do canal à caixa', g, 344)
def viz(cap, titulo, num=None, rows=0, tabs=(), lis=()):
    if num in PICK:
        k, a = PICK[num] if isinstance(PICK[num], tuple) else (PICK[num], {})
        if k == 'sources': a = {**a, 'n': rows}
        return D[k](**a)
    k = escolhe(cap, titulo)
    return D[k]() if k else ''

if __name__ == '__main__':  # checagem: todo diagrama gera SVG bem formado e toda regra aponta para um diagrama
    import xml.etree.ElementTree as ET
    for k, f in D.items(): ET.fromstring(f())
    assert all(k in D or k == 'tema' for _, k in REGRAS) and all(k in D for k in TEMA.values())
    assert all((v[0] if isinstance(v, tuple) else v) in D for v in PICK.values())
    for n_, v in PICK.items(): ET.fromstring(viz(0, '', n_, 3))
    assert escolhe(6, 'Low Cut / HPF') == 'hpf' and escolhe(10, 'Retorno pré-fader, efeito pós-fader') == 'taps' and escolhe(8, 'Pontos de partida citados') == 'comp' and escolhe(1, 'Nomes e versões que confundem') == 'families' and escolhe(22, 'Manutenção e segurança') == 'maint'
    assert escolhe(1, 'XR12: "faltam conectores, não recursos"') == 'panel_xr16' and escolhe(1, 'XR16: 8 pré-amplificadores e gravador estéreo') == 'panel_xr16'
    assert escolhe(4, 'Copiar, colar e presets') == 'naming' and escolhe(26, 'Podcasts, shorts, reels, TikTok e ebooks') == 'sources' and escolhe(19, 'Cartões SD da placa DN32-LIVE') == 'sdcard'
    assert escolhe(5, 'Phantom power (+48 V)') == 'phantom' and escolhe(5, 'Pré-amplificador: ganho, phantom e fase') == 'gain' and escolhe(1, 'A família M32: M32, M32R e M32C') == 'families'
    print('ok:', len(D), 'diagramas')
