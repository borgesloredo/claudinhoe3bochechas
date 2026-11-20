# Gera 06-pdf/curso.html a partir de 05-curso-final.md (só biblioteca padrão).
# Uso: python3 -I build_pdf_html.py <curso-final.md> <saida.html> [paginas.json]
# paginas.json (opcional) = {"0": 3, "1": 5, ...}: página de cada capítulo para o sumário.
import html, json, math, re, sys

MESAS_RE = re.compile(r'^(.*?)\s*(\((?:XR18|X18|XR16|XR12|MR18|MR12|X32|M32)[^()]*\))\s*$')

# ---------------------------------------------------------------- inline
def inline(s):
    s = html.escape(s, quote=False).replace('X AIR', 'X\u00a0AIR').replace('M AIR', 'M\u00a0AIR')
    codes = []
    s = re.sub(r'`([^`]+)`', lambda m: codes.append(m.group(1)) or f'\x00{len(codes)-1}\x00', s)
    s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
    s = re.sub(r'(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])', r'<em>\1</em>', s)
    def url(m):
        u = m.group(0); tail = ''
        while u and u[-1] in '.,;)':
            tail = u[-1] + tail; u = u[:-1]
        return f'<a href="{u}">{u}</a>{tail}'
    s = re.sub(r'https?://[^\s<]+', url, s)
    s = re.sub(r'\((não confirmad[^()]*)\)', r'<span class="nc">(\1)</span>', s)
    s = s.replace('⚠', '<span class="warn">⚠</span>')
    s = re.sub(r'\x00(\d+)\x00', lambda m: f'<code>{codes[int(m.group(1))]}</code>', s)
    return s

def split_title(t):
    m = MESAS_RE.match(t)
    return (m.group(1), m.group(2)) if m else (t, '')

def heading(level, text, hid=None):
    t, mesas = split_title(text)
    idattr = f' id="{hid}"' if hid else ''
    cls = ''
    if level == 3:
        cls = ' class="part-manual"' if 'O que diz o manual' in t else ' class="part-cursos"' if 'Na prática' in t else ''
    m = f' <span class="mesas">{inline(mesas)}</span>' if mesas else ''
    return f'<h{level}{idattr}{cls}><span class="ht">{inline(t)}</span>{m}</h{level}>'

# ---------------------------------------------------------------- selo de abordagens divergentes (bifurcação: um ponto, mais de um caminho correto)
DVB = ('<span class="dv-badge"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 22v-8"/><path d="M12 14 5 7"/><path d="m12 14 7-7"/>'
       '<path d="M5 12V7h5"/><path d="M19 12V7h-5"/></svg>Abordagens divergentes</span>')

# ---------------------------------------------------------------- blocks
LIST_RE = re.compile(r'^(\s*)([-*]|\d+\.)\s+(.*)$')

def render_table(rows):
    cells = [[c.strip() for c in r.strip().strip('|').split('|')] for r in rows]
    head, body = cells[0], cells[2:]
    out = ['<table><thead><tr>' + ''.join(f'<th>{inline(c)}</th>' for c in head) + '</tr></thead><tbody>']
    for r in body:
        out.append('<tr>' + ''.join(f'<td>{inline(c)}</td>' for c in r) + '</tr>')
    out.append('</tbody></table>')
    cls = 'wide' if len(head) >= 6 else ''
    return f'<div class="tbl {cls}">' + ''.join(out) + '</div>'

def render_list(lines):
    """lines: itens de lista e continuações. Monta listas aninhadas por indentação."""
    out = []; stack = []  # (indent, tag)
    for ln in lines:
        m = LIST_RE.match(ln)
        if m:
            ind = len(m.group(1)); tag = 'ol' if m.group(2)[0].isdigit() else 'ul'
            while stack and stack[-1][0] > ind:
                out.append(f'</li></{stack.pop()[1]}>')
            if stack and stack[-1][0] == ind:
                out.append('</li>')
            else:
                start = ''
                if tag == 'ol' and m.group(2) != '1.':
                    start = f' start="{m.group(2)[:-1]}"'
                out.append(f'<{tag}{start}>'); stack.append((ind, tag))
            out.append('<li>' + inline(m.group(3)))
        else:
            out.append(f'<p class="cont">{inline(ln.strip())}</p>')
    while stack:
        out.append(f'</li></{stack.pop()[1]}>')
    return ''.join(out)

def render_blocks(lines):
    out = []; i = 0; n = len(lines)
    while i < n:
        ln = lines[i]
        if not ln.strip():
            i += 1; continue
        if ln.startswith('```'):
            j = i + 1
            while j < n and not lines[j].startswith('```'):
                j += 1
            out.append('<pre>' + html.escape('\n'.join(lines[i+1:j])) + '</pre>')
            i = j + 1; continue
        m = re.match(r'^(#{1,6})\s+(.*)$', ln)
        if m:
            out.append(heading(len(m.group(1)), m.group(2))); i += 1; continue
        if ln.strip() == '---':
            i += 1; continue
        if ln.startswith('|'):
            j = i
            while j < n and lines[j].startswith('|'):
                j += 1
            out.append(render_table(lines[i:j])); i = j; continue
        if ln.startswith('>'):
            j = i; inner = []
            while j < n and lines[j].startswith('>'):
                t = lines[j][1:]
                t = t[1:] if t.startswith(' ') else t
                inner += [t, ''] if not LIST_RE.match(t) else [t]
                j += 1
            body = render_blocks(inner)
            m = re.match(r'<p><strong>Abordagens divergentes:</strong>\s*(.*?)</p>', body, re.S)
            if m:  # selo único de "ponto com abordagens diferentes" (mesmo desenho do slide; README de tools/bespoke, seção 8)
                body = f'<p class="dv-h">{DVB} <span class="dv-t">{m.group(1)}</span></p>' + body[m.end():]
                out.append(f'<blockquote class="diverge">{body}</blockquote>'); i = j; continue
            cls = ('cena' if body.startswith('<p><strong>Em cena.') else 'fecha' if body.startswith('<p><strong>Fechando.') else
                   'term' if re.search(r'Termo|^<p><strong>[^<]{1,60}:', body) else 'note')
            out.append(f'<blockquote class="{cls}">{body}</blockquote>'); i = j; continue
        if LIST_RE.match(ln):
            j = i; items = []
            while j < n:
                l2 = lines[j]
                if LIST_RE.match(l2) or (l2.startswith(' ') and l2.strip()):
                    items.append(l2); j += 1; continue
                if not l2.strip():
                    k = j
                    while k < n and not lines[k].strip():
                        k += 1
                    if k < n and (LIST_RE.match(lines[k]) and lines[k].startswith(' ') or
                                  (lines[k].startswith(' ') and lines[k].strip()) or
                                  (LIST_RE.match(lines[k]) and LIST_RE.match(items[-1]) and
                                   lines[k].lstrip()[0].isdigit() == items[0].lstrip()[0].isdigit())):
                        j = k; continue
                break
            out.append(render_list(items)); i = j; continue
        j = i; para = []
        while j < n and lines[j].strip() and not re.match(r'^(#|\||>|```)', lines[j]) and not LIST_RE.match(lines[j]):
            para.append(lines[j].strip()); j += 1
        txt = inline(" ".join(para))
        if 'loredoborges.com.br' in txt:  # cap. 26: o próximo passo, com site e telefone em destaque
            txt = txt.replace('loredoborges.com.br', '<b class="ct">loredoborges.com.br</b>').replace('(31) 97318-0752', '<b class="ct">(31) 97318-0752</b>')
            out.append(f'<p class="cta">{txt}</p>'); i = j; continue
        out.append(f'<p>{txt}</p>'); i = j
    return '\n'.join(out)

# ---------------------------------------------------------------- SVG helpers
def esc(s): return html.escape(s, quote=False)

def txt(x, y, s, cls='', anchor='middle', size=None):
    st = f' style="font-size:{size}px"' if size else ''
    return f'<text x="{x}" y="{y}" text-anchor="{anchor}" class="{cls}"{st}>{esc(s)}</text>'

def box(x, y, w, h, label, cls='bx', tcls='', rx=8, size=None):
    """label: linhas separadas por \\n; linha começando com '!' sai em negrito."""
    lines = label.split('\n') if label else []
    lh = (size or 13) + 3
    y0 = y + h / 2 - (len(lines) - 1) * lh / 2 + 4.5
    t = ''.join(txt(x + w / 2, y0 + k * lh, l[1:] if l.startswith('!') else l,
                    (tcls + (' b' if l.startswith('!') else '')).strip(), size=size)
                for k, l in enumerate(lines))
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" class="{cls}"/>{t}'

def arr(x1, y1, x2, y2, cls='ln'):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="{cls}"/>'

def path(d, cls='ln'):
    return f'<path d="{d}" class="{cls}"/>'

def fig(h, body, cap, w=680):
    return (f'<figure class="fig"><svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" role="img" '
            f'aria-label="{html.escape(cap)}">{body}</svg><figcaption>{inline(cap)}</figcaption></figure>')

def polyline(pts, cls):
    return f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" class="{cls}"/>'

# ---------------------------------------------------------------- diagramas (um ou mais por capítulo)
def d0():
    b = ''
    steps = [('!1. Conhecer a mesa\ncap. 1 e 2', 10, 20), ('!2. Conectar e navegar\ncap. 3 e 4', 180, 20),
             ('!3. Ajustar o canal\ncap. 5 a 9', 350, 20), ('!4. Mixar e distribuir\ncap. 10 a 15', 520, 20),
             ('!5. Guardar e escutar\ncap. 16 a 18', 520, 125), ('!6. Gravar e expandir\ncap. 19 a 21', 350, 125),
             ('!7. Cuidar e revisar\ncap. 22 a 27', 180, 125)]
    for k, (l, x, y) in enumerate(steps):
        b += box(x, y, 150, 62, l, 'bxo' if k == 2 else 'bx')
    b += arr(160, 51, 178, 51) + arr(330, 51, 348, 51) + arr(500, 51, 518, 51)
    b += arr(595, 82, 595, 123) + arr(520, 156, 502, 156) + arr(350, 156, 332, 156)
    b += txt(10, 228, 'Cada capítulo tem duas partes:', 'b', 'start')
    b += box(10, 240, 300, 46, '!Parte 1 · O que diz o manual\nreferência oficial: menus, botões, números', 'bxb', size=12)
    b += arr(312, 263, 348, 263)
    b += box(350, 240, 320, 46, '!Parte 2 · Na prática\noperação: dicas, valores de partida, erros comuns', 'bxg', size=12)
    return fig(300, b, 'Mapa do curso: a ordem dos capítulos segue o uso real da mesa.')

def d1():
    b = box(10, 10, 320, 34, '!Família X AIR / M AIR · controle por app + Wi-Fi', 'bxd', 'tw', size=12)
    b += box(350, 10, 320, 34, '!Família X32 / M32 · faders, AES50, sem Wi-Fi', 'bxd', 'tw', size=12)
    L = [('XR18', 'MR18', 'gêmeas'), ('X18', None, 'versão de mesa da XR18'),
         ('XR16', None, 'sem gêmea Midas'), ('XR12', 'MR12', 'gêmeas')]
    for k, (a, c, note) in enumerate(L):
        y = 62 + k * 62
        b += box(20, y, 110, 32, '!' + a)
        if c:
            cls = 'bxo' if c.startswith('"') else 'bx'
            b += box(200, y, 110, 32, ('' if c.startswith('"') else '!') + c, cls)
            b += arr(132, y + 16, 198, y + 16, 'ln2' if not c.startswith('"') else 'lnd')
        b += txt(165 if c else 140, y + 46, note, 'sm', 'middle' if c else 'start')
    R = [('X32', 'M32 / M32 LIVE', 'ln2', 'gêmeas'), ('X32 Compact', None, None, '17 faders, 16 pré'),
         ('X32 Producer', 'M32R / M32R LIVE', 'lnd2', 'parecidas pela ficha técnica'),
         ('X32 Rack', None, None, 'sem faders, 16 pré'),
         ('M32C', None, None, 'Midas · núcleo 1U, sem par Behringer')]
    for k, (a, c, cl, note) in enumerate(R):
        y = 56 + k * 50
        b += box(360, y, 120, 30, ('!' if not a.startswith('"') else '') + a, 'bx' if not a.startswith('"') else 'bxo', size=12)
        if c:
            b += box(540, y, 120, 30, '!' + c, size=12) + arr(482, y + 15, 538, y + 15, cl)
            b += txt(510, y + 42, note, 'sm', size=10.5)
        else:
            b += txt(490, y + 20, note, 'sm', 'start', size=10.5)
    b += box(10, 318, 660, 30, 'Entre as famílias a ligação é só analógica: Ultranet (P16) não é AES50.', 'bxr', size=12)
    return fig(356, b, 'Quem é irmão de quem. Linha cheia = gêmeas; tracejado = parecidas pela ficha, sem equivalência oficial.')

def d2():
    b = f'<rect x="10" y="10" width="410" height="290" rx="10" class="zone"/>' + txt(24, 30, 'PALCO', 'zl', 'start')
    b += box(30, 120, 120, 56, '!Microfones e\n!instrumentos')
    b += box(195, 112, 125, 72, '!XR18 / X18 / MR18\na mesa fica no palco', 'bxd', 'tw', size=12)
    b += arr(150, 148, 193, 148)
    b += box(195, 30, 125, 46, '!Retornos\nAux 1–6', 'bxo') + arr(257, 112, 257, 78)
    b += box(340, 30, 70, 46, '!P16\nUltranet', 'bxg', size=12) + arr(310, 112, 360, 78)
    b += box(195, 225, 125, 50, '!PA (caixas)\nMain L/R em XLR', 'bxb') + arr(257, 184, 257, 223)
    b += box(470, 112, 160, 70, '!Roteador externo\nporta LAN\n(nunca na WAN)', size=12)
    b += arr(320, 148, 468, 148) + txt(365, 166, 'cabo de rede', 'sm')
    b += box(470, 228, 200, 56, '!Técnica\ntablet ou notebook', 'bxb')
    b += arr(550, 182, 550, 226, 'lnd') + txt(556, 210, 'Wi-Fi 5 GHz', 'sm', 'start')
    b += box(440, 20, 230, 70, '!Ordem de energia\nLigar: mesa → caixas\nDesligar: caixas → mesa', 'bxr', size=12)
    return fig(310, b, 'Show típico com uma X AIR de 18 canais: a mesa vai para o palco e a técnica controla pela rede (cap. 2 e 3).')

def d3():
    b = ''
    P = [(10, 'ETHERNET', 'chave à esquerda', 'cabo até PC ou roteador', 'o modo mais confiável'),
         (235, 'WI-FI CLIENT', 'chave no meio', 'a mesa entra numa', 'rede que já existe'),
         (460, 'ACCESS POINT', 'chave à direita', 'a mesa cria a rede', '192.168.1.1 · até 4 aparelhos')]
    for x, t, s, l1, l2 in P:
        b += f'<rect x="{x}" y="10" width="210" height="140" rx="10" class="panel"/>'
        b += txt(x + 105, 32, t, 'b') + txt(x + 105, 48, s, 'sm')
        b += box(x + 12, 62, 64, 34, '!Mesa', 'bxd', 'tw', size=12)
        b += box(x + 134, 62, 64, 34, 'Tablet' if t == 'ACCESS POINT' else 'Roteador', 'bx', size=11.5)
        b += arr(x + 78, 79, x + 132, 79, 'ln' if t == 'ETHERNET' else 'lnd')
        b += txt(x + 105, 120, l1, 'sm') + txt(x + 105, 136, l2, 'sm')
    b += txt(10, 180, 'Montagem para show (endereço: ver 3.2.4):', 'b', 'start')
    b += box(10, 212, 130, 62, '!Mesa\nchave em ETHERNET\nLAN: DHCP ou IP fixo', 'bxd', 'tw', size=11.5)
    b += f'<rect x="230" y="198" width="160" height="90" rx="10" class="bx"/>' + txt(310, 222, 'Roteador dual band', 'b')
    b += box(244, 240, 60, 30, 'LAN ✓', 'bxg', size=12) + box(316, 240, 60, 30, 'WAN ✗', 'bxr', size=12)
    b += arr(140, 255, 242, 255) + txt(190, 247, 'cabo', 'sm')
    b += box(490, 192, 180, 46, '!Tablets e celulares\nWi-Fi 5 GHz · senha WPA2', 'bxb', size=12)
    b += box(490, 256, 180, 46, '!Notebook no cabo\nreserva se o Wi-Fi cair', 'bxg', size=12)
    b += arr(390, 225, 488, 215, 'lnd') + arr(390, 268, 488, 278)
    return fig(310, b, 'Os três modos da chave REMOTE (X AIR / M AIR) e uma montagem de rede para show.')

def fader(x, y, h, v, label, cls='cap'):
    cy = y + (1 - v) * h
    return (f'<rect x="{x - 3}" y="{y}" width="6" height="{h}" rx="3" class="track"/>'
            f'<rect x="{x - 14}" y="{cy - 7}" width="28" height="14" rx="3" class="{cls}"/>' + txt(x, y + h + 18, label, 'sm'))

def d4():
    b = ''
    for k, (ox, title, vals, cls, cap) in enumerate([
        (10, 'Modo normal', [0.7, 0.5, 0.8, 0.4], 'cap', 'faders = volume de cada canal no Main LR'),
        (350, 'Sends on Faders · Aux 1', [0.9, 0.25, 0.15, 0.55], 'capo', 'faders = quanto cada canal manda ao Aux 1')]):
        b += f'<rect x="{ox}" y="10" width="320" height="240" rx="10" class="panel"/>' + txt(ox + 160, 34, title, 'b')
        for j, v in enumerate(vals):
            b += fader(ox + 45 + j * 58, 52, 130, v, f'Ch {j + 1}', cls)
        b += f'<line x1="{ox + 262}" y1="50" x2="{ox + 262}" y2="200" class="sep"/>'
        b += fader(ox + 290, 52, 130, 0.75, 'Main LR' if k == 0 else 'Aux 1', 'capd')
        b += txt(ox + 160, 236, cap, 'sm')
    return fig(258, b, 'Sends on Faders: os mesmos faders passam a montar a mixagem de um retorno (Aux/Mix bus).')

def d5():
    b = ''
    r1 = ['!Fonte e pré\nGain · +48 V', '!Low Cut\n(HPF)', '!Gate\nDucker', '![Insert]', '!EQ\n4 bandas']
    r2 = ['!Compressor\nantes/depois EQ*', '!Delay*', '!Mute\nFader', '!Pan\nLR ou LCR*', '!Main LR\n(+ Mono/C*)']
    for k, l in enumerate(r1):
        x = 3 + k * 139
        b += box(x, 14, 118, 52, l, 'bxo' if k == 0 else 'bx', size=12)
        if k: b += arr(x - 21, 40, x - 2, 40)
    b += path('M 559 66 L 559 84 L 62 84 L 62 100')
    for k, l in enumerate(r2):
        x = 3 + k * 139
        b += box(x, 102, 118, 52, l, 'bxb' if k == 4 else 'bx', size=12)
        if k: b += arr(x - 21, 128, x - 2, 128)
    b += arr(340, 154, 340, 186) + box(250, 188, 180, 40, '!Envios\nAux/Mix bus e FX', 'bxg', size=12)
    b += txt(3, 250, '* Só na família X32/M32: compressor antes ou depois do EQ, delay de canal e pan LCR (Mono/Center).', 'sm', 'start')
    return fig(260, b, 'O caminho do sinal dentro do canal: a ordem é praticamente a mesma nas duas famílias.')

def d5b():
    x0, x1 = 40, 640
    X = lambda db: x0 + (db + 60) / 60 * (x1 - x0)
    b = f'<rect x="{X(-60)}" y="40" width="{X(-24) - X(-60)}" height="34" class="zg"/>'
    b += f'<rect x="{X(-24)}" y="40" width="{X(-6) - X(-24)}" height="34" class="zy"/>'
    b += f'<rect x="{X(-6)}" y="40" width="{X(0) - X(-6)}" height="34" class="zr"/>'
    for db in (-60, -48, -36, -24, -18, -12, -6, 0):
        b += f'<line x1="{X(db)}" y1="74" x2="{X(db)}" y2="82" class="tick"/>' + txt(X(db), 96, f'{db}', 'sm')
    b += f'<rect x="{X(-20)}" y="34" width="{X(-16) - X(-20)}" height="46" rx="4" class="mk"/>'
    b += txt(X(-18), 26, 'média ≈ −18 dBFS', 'b')
    b += f'<rect x="{X(-15)}" y="44" width="{X(-12) - X(-15)}" height="26" rx="3" class="mk2"/>'
    b += txt(X(-11), 126, 'picos 3 a 6 dB acima', 'sm')
    b += txt(X(0), 26, '0 dBFS = teto', 'b', 'end')
    b += txt(X(-48), 126, 'baixo demais: o ruído aparece', 'sm')
    b += txt(X(-3), 126, 'clip', 'sm')
    b += txt(340, 150, 'Escala em dBFS: no digital não existe nada acima de 0; −18 dBFS faz o papel do "0 VU" analógico.', 'sm')
    return fig(160, b, 'A meta de ganho: média perto de −18 dBFS, com folga (headroom) para os picos.')

def logx(f, x0=60, x1=660):
    return x0 + (math.log10(f) - math.log10(20)) / 3 * (x1 - x0)

def d6():
    Y = lambda g: 120 - g * 6
    b = ''
    for f, l in ((100, '100 Hz'), (1000, '1 kHz'), (10000, '10 kHz')):
        b += f'<line x1="{logx(f):.1f}" y1="30" x2="{logx(f):.1f}" y2="210" class="grid"/>' + txt(logx(f), 228, l, 'sm')
    for g in (-12, -6, 0, 6, 12):
        b += f'<line x1="60" y1="{Y(g)}" x2="660" y2="{Y(g)}" class="{"axis" if g == 0 else "grid"}"/>' + txt(52, Y(g) + 4, f'{g:+d}' if g else '0 dB', 'sm', 'end')
    pts = []
    for k in range(301):
        f = 20 * 10 ** (3 * k / 300)
        g = 20 * math.log10(1 / math.sqrt(1 + (90 / f) ** 4))
        g += -5 * math.exp(-(math.log2(f / 350)) ** 2 / (2 * 0.45 ** 2))
        g += 4 * math.exp(-(math.log2(f / 3000)) ** 2 / (2 * 0.6 ** 2))
        g += 3 * f ** 2 / (f ** 2 + 9000 ** 2)
        pts.append((logx(f), Y(max(g, -15))))
    b += polyline(pts, 'curve')
    b += txt(logx(22), Y(-3), 'Low Cut (HPF)', 'lbl', 'start') + txt(logx(350), Y(-5) + 22, 'corte de médio-grave', 'lbl')
    b += txt(logx(3000), Y(4) - 12, 'realce de presença', 'lbl') + txt(logx(12000), Y(3) - 14, 'High Shelf', 'lbl')
    return fig(240, b, 'Curva ilustrativa de EQ de voz: HPF nos graves, um corte largo e realces suaves (valores só de exemplo).')

def d7():
    T = 1.1; X = lambda t: 60 + t / T * 600; Y = lambda db: 30 + (-db) / 70 * 170
    hits = [0.15, 0.41, 0.67, 0.92]
    def inp(t):
        lv = -45 + 2 * math.sin(t * 60)
        for h in hits:
            if t >= h:
                lv = max(lv, -6 - 220 * (t - h))
        return lv
    thr, rng, hold, rel = -30, 30, 0.04, 0.05
    gain = []; last_open = -9
    for k in range(601):
        t = T * k / 600
        if inp(t) > thr: last_open = t
        dt = t - last_open - hold
        gain.append(0 if dt <= 0 else -rng * min(dt / rel, 1))
    pin = [(X(T * k / 600), Y(inp(T * k / 600))) for k in range(601)]
    pout = [(X(T * k / 600), Y(max(inp(T * k / 600) + gain[k], -70))) for k in range(601)]
    b = ''
    for db in (0, -20, -40, -60):
        b += f'<line x1="60" y1="{Y(db)}" x2="660" y2="{Y(db)}" class="grid"/>' + txt(52, Y(db) + 4, f'{db} dB', 'sm', 'end')
    b += polyline(pin, 'curve2') + polyline(pout, 'curve')
    b += f'<line x1="60" y1="{Y(thr)}" x2="660" y2="{Y(thr)}" class="thr"/>' + txt(64, Y(thr) - 6, 'Threshold', 'lblr', 'start')
    # faixa aberto/fechado
    segs = []; cur = None; start = 0
    for k, g in enumerate(gain):
        s = g > -rng + 0.01
        if s != cur:
            if cur is not None: segs.append((start, k, cur))
            cur, start = s, k
    segs.append((start, 600, cur))
    for a, z, s in segs:
        b += f'<rect x="{X(T * a / 600):.1f}" y="214" width="{X(T * z / 600) - X(T * a / 600):.1f}" height="18" class="{"zg" if s else "zgr"}"/>'
    b += txt(X(0.22), 252, 'aberto', 'sm') + txt(X(0.07), 252, 'fechado', 'sm')
    hx = hits[1]
    b += txt(X(hx) + 2, Y(-2) - 4, 'Attack', 'lbl', 'start')
    b += txt(10, 290, 'Attack: rapidez para abrir · Hold: tempo aberto depois que o som cai · Release: rapidez para fechar · Range: quanto atenua', 'sm', 'start')
    b += f'<line x1="440" y1="268" x2="470" y2="268" class="curve2"/>' + txt(476, 272, 'entrada', 'sm', 'start')
    b += f'<line x1="540" y1="268" x2="570" y2="268" class="curve"/>' + txt(576, 272, 'saída do gate', 'sm', 'start')
    return fig(298, b, 'Gate: abre quando o som passa do threshold e, entre as notas, atenua o vazamento (exemplo de tambor).')

def d8():
    X = lambda db: 60 + (db + 60) / 60 * 300; Y = lambda db: 270 - (db + 60) / 60 * 240
    thr = -24; b = ''
    for db in (-60, -48, -36, -24, -12, 0):
        b += f'<line x1="{X(db)}" y1="30" x2="{X(db)}" y2="270" class="grid"/>' + txt(X(db), 286, str(db), 'sm')
        b += f'<line x1="60" y1="{Y(db)}" x2="360" y2="{Y(db)}" class="grid"/>' + txt(54, Y(db) + 4, str(db), 'sm', 'end')
    b += txt(210, 304, 'entrada (dB)', 'sm') + txt(22, 150, 'saída', 'sm', 'middle')
    for r, cls, lab in ((1, 'curve2', '1:1 (sem compressão)'), (2, 'curve3', '2:1 suave'), (4, 'curve', '4:1'), (1e9, 'curve4', '∞:1 limitador')):
        pts = [(X(-60), Y(-60)), (X(thr), Y(thr)), (X(0), Y(thr + (0 - thr) / r))]
        b += polyline(pts, cls) + txt(X(0) + 6, Y(thr + (0 - thr) / r) + 4, lab, 'sm', 'start')
    b += f'<circle cx="{X(thr)}" cy="{Y(thr)}" r="5" class="dot"/>' + txt(X(thr) - 8, Y(thr) - 10, 'Threshold', 'lbl', 'end')
    notes = ['!Threshold\na partir de onde comprime', '!Ratio\n4:1 = 4 dB acima viram 1 dB', '!Gain (makeup)\ndevolve o volume perdido',
             '!Attack / Release\nrapidez para agir e soltar']
    for k, n in enumerate(notes):
        b += box(490, 30 + k * 64, 180, 52, n, 'bx', size=11.5)
    return fig(312, b, 'Compressor: acima do threshold a saída sobe menos que a entrada; quanto maior o ratio, mais forte o controle.')

def d9():
    b = ''
    for k, l in enumerate(['!Gate', '!Ponto de\n!Insert', '!EQ', '!Compressor']):
        x = 20 + k * 165
        b += box(x, 20, 130, 46, l, 'bxo' if k == 1 else 'bx', size=12)
        if k: b += arr(x - 35, 43, x - 2, 43)
    b += path('M 205 66 L 205 100 L 250 100', 'ln') + box(252, 82, 180, 40, '!Slot de efeito\nGEQ, limitador, exciter', 'bxg', size=11.5)
    b += path('M 432 102 L 470 102 L 470 74 L 260 74 L 260 68', 'lnd')
    b += txt(342, 142, 'sai do canal e volta no mesmo ponto (em série)', 'sm')
    b += txt(10, 168, 'Pan', 'b', 'start')
    b += box(20, 180, 300, 96, '', 'panel')
    b += txt(170, 200, 'X AIR / M AIR: Main LR', 'b')
    b += box(50, 214, 70, 40, '!L', 'bxb') + box(220, 214, 70, 40, '!R', 'bxb')
    b += f'<circle cx="170" cy="234" r="16" class="knob"/><line x1="170" y1="234" x2="160" y2="221" class="needle"/>'
    b += box(350, 180, 320, 96, '', 'panel')
    b += txt(510, 200, 'X32 / M32: LR ou LCR (Mono/Center)', 'b')
    b += box(370, 214, 70, 40, '!L', 'bxb') + box(475, 214, 70, 40, '!C', 'bxo') + box(580, 214, 70, 40, '!R', 'bxb')
    b += txt(170, 270, 'Stereo Link: dois canais vizinhos viram um par', 'sm')
    return fig(286, b, 'Insert põe um processador no meio do canal; o pan distribui o canal entre as caixas.')

def d10():
    names = ['!Pré\nganho', '!Low Cut', '!Gate', '!EQ', '!Comp', '!Fader', '!Pan']
    b = ''; xs = []
    for k, l in enumerate(names):
        x = 10 + k * 92; xs.append(x)
        b += box(x, 30, 78, 44, l, 'bxo' if k == 5 else 'bx', size=12)
        if k: b += arr(x - 14, 52, x - 1, 52)
    taps = [('Input', xs[0] + 85), ('Pre EQ', xs[2] + 85), ('Post EQ', xs[3] + 85), ('Pre Fader', xs[4] + 85),
            ('Post Fader', xs[5] + 85), ('Post Pan', xs[6] + 85)]
    for k, (l, x) in enumerate(taps):
        b += f'<circle cx="{x}" cy="52" r="5" class="dot"/>'
        b += f'<line x1="{x}" y1="57" x2="{x}" y2="{96 + (k % 2) * 16}" class="sep"/>' + txt(x, 108 + (k % 2) * 16, l, 'lbl')
    b += box(70, 170, 260, 64, '!Retorno de palco\nPre Fader (ou Pre/Post EQ)\no PA muda, o músico não', 'bxb', size=12)
    b += box(370, 170, 280, 64, '!Efeito (reverb, delay)\nPost Fader\nfader fechado = sem reverb', 'bxg', size=12)
    b += path(f'M {taps[3][1]} 128 L {taps[3][1]} 150 L 200 150 L 200 168')
    b += path(f'M {taps[4][1]} 112 L {taps[4][1]} 168')
    b += txt(340, 258, 'Nomes dos pontos como no app X AIR; na X32/M32: Pre-EQ, Post-EQ, Pre-Fader, Post-Fader e Sub-Group.', 'sm')
    b += txt(340, 274, 'Confira na sua mesa a posição do low cut nesses pontos (ver 10.2.1).', 'sm')
    return fig(282, b, 'Pontos de captação (tap points): de onde sai a cópia do canal para cada bus.')

def wedge(x, y, label):
    return (f'<path d="M {x} {y + 22} L {x + 8} {y} L {x + 52} {y} L {x + 60} {y + 22} Z" class="wedge"/>' + txt(x + 30, y + 38, label, 'sm'))

def person(x, y, label):
    return f'<circle cx="{x}" cy="{y}" r="16" class="person"/>' + txt(x, y + 32, label, 'lbl')

def d11():
    b = f'<rect x="10" y="10" width="660" height="210" rx="10" class="zone"/>' + txt(24, 30, 'PALCO', 'zl', 'start')
    b += person(110, 70, 'Voz') + wedge(80, 120, 'Aux 1')
    b += person(260, 70, 'Violão') + wedge(230, 120, 'Aux 2')
    b += person(410, 70, 'Teclado') + box(375, 120, 70, 30, 'in-ear', 'bxg', size=11) + txt(410, 168, 'Aux 3+4 linkados', 'sm')
    b += person(570, 70, 'Bateria') + box(530, 120, 80, 30, 'P16-M', 'bxg', size=11) + txt(570, 168, 'Ultranet*', 'sm')
    b += box(250, 238, 180, 46, '!Mesa\nenvios pré-fader', 'bxd', 'tw', size=12)
    for x in (110, 260, 410, 570):
        b += f'<line x1="{x}" y1="236" x2="{x}" y2="{186 if x != 570 else 186}" class="lnd"/>'
    b += txt(10, 304, '* P16 pela Ultranet: XR18, X18, MR18 e toda a família X32/M32. Buses de retorno ficam fora do Main LR.', 'sm', 'start')
    return fig(312, b, 'Cada músico com sua mistura: caixa de retorno, in-ear estéreo ou mixer pessoal P16.')

def d12():
    bands = [20 * 2 ** (k / 3) for k in range(31)]
    def lvl(f, spike):
        v = -28 + 6 * math.exp(-(math.log2(f / 120)) ** 2 / 3) - 6 * (f > 8000) * math.log2(f / 8000)
        v += 2 * math.sin(f / 37)
        if spike: v += 22 * math.exp(-(math.log2(f / 2500)) ** 2 / 0.02)
        return v
    b = ''
    for p, (ox, spike, title) in enumerate([(10, True, 'Antes: pico de microfonia'), (350, False, 'Depois: corte estreito só ali')]):
        b += f'<rect x="{ox}" y="10" width="320" height="220" rx="10" class="panel"/>' + txt(ox + 160, 32, title, 'b')
        for k, f in enumerate(bands):
            v = lvl(f, spike)
            hgt = max(4, (v + 40) * 4.2)
            cls = 'barr' if (p == 0 and abs(math.log2(f / 2500)) < 0.2) else 'bar'
            b += f'<rect x="{ox + 14 + k * 9.6:.1f}" y="{200 - hgt:.1f}" width="7.4" height="{hgt:.1f}" class="{cls}"/>'
        for f, l in ((100, '100'), (1000, '1k'), (10000, '10k')):
            b += txt(ox + 14 + math.log2(f / 20) * 3 * 9.6 + 3.7, 218, l, 'sm')
    pts = []
    for k in range(200):
        f = 20 * 10 ** (3 * k / 199)
        g = -9 * math.exp(-(math.log2(f / 2500)) ** 2 / (2 * 0.08 ** 2))
        pts.append((350 + 14 + math.log2(f / 20) * 3 * 9.6 + 3.7, 70 - g * 4))
    b += polyline(pts, 'curve') + txt(364, 60, 'curva do EQ (PEQ, Q alto)', 'lbl', 'start')
    b += txt(124, 50, '~2,5 kHz (exemplo)', 'lblr', 'start')
    return fig(240, b, 'RTA como "raio-X": ache a frequência que apita e corte só ela, com banda estreita. Valores ilustrativos.')

def d13():
    b = txt(10, 22, 'Por envio (send/return)', 'b', 'start')
    for k in range(3):
        b += box(10, 34 + k * 40, 70, 30, f'Ch {k + 1}', size=12)
        b += arr(80, 49 + k * 40, 118, 92 - (1 - k) * 8)
    b += box(120, 72, 80, 40, '!FX Send', size=12) + arr(200, 92, 222, 92)
    b += box(224, 72, 90, 40, '!Reverb\nslot 1', 'bxg', size=12)
    b += box(224, 130, 90, 34, 'FX Return', size=12) + path('M 290 112 L 290 128', 'ln')
    b += path('M 314 147 L 330 147', 'ln') + txt(336, 151, '→ Main LR', 'sm', 'start')
    b += txt(10, 184, 'vários canais, quantidades diferentes', 'sm', 'start')
    b += txt(400, 22, 'Em insert', 'b', 'start')
    b += box(400, 60, 70, 34, 'Ch 5', size=12) + arr(470, 77, 498, 77)
    b += box(500, 54, 90, 46, '!GEQ ou\n!limitador', 'bxo', size=12) + arr(590, 77, 618, 77)
    b += txt(622, 81, 'segue', 'sm', 'start') + txt(400, 128, 'um canal ou bus só, em série', 'sm', 'start')
    b += txt(10, 216, 'Slots de efeito', 'b', 'start')
    b += txt(10, 240, 'X AIR / M AIR', 'sm', 'start')
    for k in range(4):
        b += box(110 + k * 70, 226, 62, 26, str(k + 1), 'bxg', size=12)
    b += txt(400, 244, 'qualquer slot: envio ou insert', 'sm', 'start')
    b += txt(10, 284, 'X32 / M32', 'sm', 'start')
    for k in range(8):
        b += box(110 + k * 70, 270, 62, 26, str(k + 1), 'bxg' if k < 4 else 'bxo', size=12)
    b += txt(250, 316, '1–4: envio ou insert (reverbs aqui)', 'sm') + txt(530, 316, '5–8: só insert', 'sm')
    return fig(326, b, 'Duas formas de usar um efeito e quantos slots cada família oferece.')

def d14():
    b = txt(170, 22, 'DCA: controle remoto de volume', 'b')
    b += box(120, 36, 100, 34, '!DCA 1', 'bxo', size=12)
    for k in range(3):
        x = 30 + k * 105
        b += box(x, 108, 90, 32, f'Ch {k + 1}', size=12)
        b += f'<line x1="170" y1="70" x2="{x + 45}" y2="106" class="ctl"/>'
        b += arr(x + 45, 140, 170, 196)
    b += box(110, 198, 120, 34, '!Main LR', 'bxb', size=12)
    b += txt(170, 256, 'tracejado = só comando, sem áudio', 'sm') + txt(170, 272, 'não aceita compressor', 'sm')
    b += f'<line x1="340" y1="20" x2="340" y2="275" class="sep"/>'
    b += txt(510, 22, 'Subgrupo: soma e processa', 'b')
    for k in range(3):
        x = 370 + k * 105
        b += box(x, 40, 90, 32, f'Ch {k + 1}', size=12) + arr(x + 45, 72, 510, 104)
    b += box(430, 106, 160, 42, '!Subgrupo (bus)\ncompressor, EQ', 'bxg', size=12)
    b += arr(510, 148, 510, 196) + box(450, 198, 120, 34, '!Main LR', 'bxb', size=12)
    b += path('M 655 74 L 655 215 L 572 215', 'lnx') + txt(664, 140, '✗', 'xr', 'start')
    b += txt(510, 256, 'tire os canais do Main:', 'sm') + txt(510, 272, 'só o subgrupo chega ao PA', 'sm')
    return fig(282, b, 'DCA comanda volumes sem somar áudio; subgrupo soma os canais e permite processar o conjunto.')

def d15():
    b = box(10, 40, 120, 40, '!Main LR', 'bxb', size=12) + box(10, 110, 120, 40, '!Mix buses', size=12)
    M = [('!Matrix 1 · Sub\npassa-baixas', 'sub', 30), ('!Matrix 2 · PA\npassa-altas', 'caixas de cima', 100), ('!Matrix 3 · Torre\ndelay de saída', 'caixa distante', 170)]
    for l, out, y in M:
        b += box(250, y, 150, 46, l, 'bxo', size=12) + arr(400, y + 23, 468, y + 23) + box(470, y + 6, 120, 34, out, size=12)
        b += arr(130, 60, 248, y + 23, 'ln') if y < 170 else arr(130, 60, 248, y + 23, 'ln')
        b += arr(130, 130, 248, y + 23, 'lnd')
    b += txt(330, 238, 'Crossover: mesma frequência nos dois lados (ex.: ~80 a 100 Hz, Linkwitz-Riley 24 dB/oit.)', 'sm')
    b += box(10, 254, 660, 50, '!Delay da torre: o som anda cerca de 343 m/s (20 °C) ≈ 2,9 ms por metro\nex.: caixa 20 m à frente do PA → atraso de cerca de 58 ms (a mesa faz a conta em Routing › Analog Out)', 'bxr', size=11.5)
    return fig(312, b, 'Matrizes (só X32/M32): misturam o Main e os buses para sub, PA e torres de delay. Nas X AIR, ver os truques de 15.2.5.')

def d16():
    b = box(10, 40, 130, 70, '!Cena salva\nfoto de toda\na mesa', 'bxd', 'tw', size=12)
    b += arr(140, 75, 190, 75) + txt(165, 66, 'carregar', 'sm')
    for k in range(8):
        x = 200 + (k % 4) * 118; y = 20 + (k // 4) * 62
        safe = k in (2, 5)
        b += box(x, y, 106, 48, f'!Ch {k + 1}\n' + ('🔒 safe: não muda' if safe else '✓ volta ao salvo'), 'bxr' if safe else 'bxg', size=11.5)
    b += box(10, 158, 320, 100, '!X AIR / M AIR\n64 snapshots dentro da mesa\nshows e cenas no tablet ou computador\nrecall filtrado + channel safes', 'bx', size=12)
    b += box(350, 158, 320, 100, '!X32 / M32\n100 cenas (inclui o ganho dos pré)\nsnippets, cues e Scene Undo\nrecall safes por canal e parâmetro', 'bx', size=12)
    return fig(268, b, 'Cena (snapshot) traz a mesa de volta a um estado salvo; o safe protege o que não pode mudar.')

def d17():
    names = ['!Pré', '!Gate/EQ\nComp', '!Fader', '!Pan', '!Main LR\n→ PA']
    b = ''
    for k, l in enumerate(names):
        x = 20 + k * 132
        b += box(x, 30, 100, 46, l, 'bxb' if k == 4 else 'bx', size=12)
        if k: b += arr(x - 32, 53, x - 2, 53)
    b += f'<circle cx="268" cy="53" r="6" class="dot"/>' + txt(268, 98, 'PFL', 'lbl')
    b += f'<circle cx="532" cy="53" r="6" class="dot"/>' + txt(532, 98, 'AFL', 'lbl')
    b += path('M 268 104 L 268 140 L 328 140', 'lnd') + path('M 532 104 L 532 140 L 414 140', 'lnd')
    b += box(330, 122, 82, 36, '!Solo', 'bxo', size=12) + arr(371, 158, 371, 186)
    b += box(271, 188, 200, 40, '!Fone / monitor do técnico', 'bxg', size=12)
    b += txt(20, 254, 'PFL = antes do fader · AFL = depois do fader e do pan. O solo não muda o PA nem os retornos; Clear Solo limpa todos.', 'sm', 'start')
    return fig(264, b, 'Solo: o técnico escuta um canal no fone sem mexer no que o público ouve.')

def d18():
    b = ''
    for p, (ox, talk, title) in enumerate([(10, 0, 'Fala o mic 1'), (350, 2, 'Fala o mic 3')]):
        b += f'<rect x="{ox}" y="10" width="320" height="200" rx="10" class="panel"/>' + txt(ox + 160, 32, title, 'b')
        for k in range(4):
            g = 0 if k == talk else -15
            hgt = 120 + g * 6
            x = ox + 40 + k * 68
            b += f'<rect x="{x}" y="{180 - hgt}" width="40" height="{hgt}" class="{"barr" if k == talk else "bar"}"/>'
            b += txt(x + 20, 198, f'Mic {k + 1}', 'sm') + txt(x + 20, 174 - hgt, '0 dB' if g == 0 else '−15', 'lbl')
    b += txt(340, 234, 'Ganho ilustrativo: o mic em uso "rouba" ganho dos parados e o total de mics abertos fica constante.', 'sm')
    b += txt(340, 252, 'Grupos X e Y · Weight dá prioridade · Last Gate mantém o último mic aberto · para fala, não para banda.', 'sm')
    return fig(262, b, 'Dois momentos do mesmo grupo: quando a fala passa do mic 1 para o mic 3, o ganho vai junto.')

def d19():
    b = txt(10, 22, 'Gravar', 'b', 'start')
    b += box(10, 32, 120, 44, '!Entradas\nmics no palco', size=12) + arr(130, 54, 158, 54)
    b += box(160, 32, 120, 44, '!Mesa', 'bxd', 'tw', size=12) + arr(280, 54, 308, 54)
    b += box(310, 32, 120, 44, '!DAW (via USB)\numa pista por canal', 'bxg', size=12)
    b += txt(10, 112, 'Virtual soundcheck', 'b', 'start')
    b += box(10, 122, 120, 44, '!DAW toca\nas pistas', 'bxg', size=12) + arr(130, 144, 158, 144)
    b += box(160, 122, 120, 44, '!Canais com\nfonte USB', 'bxo', size=12) + arr(280, 144, 308, 144)
    b += box(310, 122, 120, 44, '!Mesa processa\ncomo ao vivo', 'bxd', 'tw', size=12)
    b += txt(10, 196, 'Depois: volte os canais para a fonte de palco (Mic/Local).', 'sm', 'start')
    rows = [('!Quem grava o quê', ''), ('XR18, X18, MR18', 'USB 18×18 multipista'), ('XR16, XR12, MR12', 'pendrive estéreo'),
            ('X32 e M32 (todas)', 'placa 32×32 + pendrive'), ('M32 LIVE, M32R LIVE', '+ cartão SD (DN32-LIVE)')]
    b += f'<rect x="450" y="10" width="220" height="212" rx="10" class="panel"/>'
    for k, (a, c) in enumerate(rows):
        y = 34 + k * 40
        if k == 0:
            b += txt(560, y, a[1:], 'b')
        else:
            b += txt(462, y - 4, a, 'b', 'start', 11.5) + txt(462, y + 12, c, 'sm', 'start')
    return fig(230, b, 'Gravação multipista e virtual soundcheck: o show gravado vira material de treino.')

def d20():
    b = f'<rect x="10" y="10" width="175" height="200" rx="10" class="zone"/>' + txt(24, 30, 'PALCO', 'zl', 'start')
    b += box(20, 80, 150, 64, '!Stagebox\nS16 / DL16 / DL32\npré-amps no palco', 'bxo', size=12)
    b += box(330, 80, 150, 64, '!Mesa de PA\nX32 / M32\nporta AES50 A', 'bxd', 'tw', size=12)
    b += arr(170, 112, 328, 112) + txt(260, 100, 'um cabo', 'lbl') + txt(260, 132, 'Cat-5e blindado', 'sm') + txt(260, 146, 'etherCON · até 100 m', 'sm')
    b += box(520, 80, 150, 64, '!Mesa de monitor\nsplit pela porta B', 'bx', size=12) + arr(480, 112, 518, 112)
    b += txt(445, 176, '48 canais em cada sentido por porta · HA Gain Split separa', 'sm') + txt(445, 192, 'o ganho do pré do trim de cada mesa (ver 20.1.2)', 'sm')
    b += box(10, 222, 660, 34, 'XR18 / MR18: a porta Ultranet só leva retorno para P16; ela não é AES50 e não liga stagebox.', 'bxr', size=12)
    return fig(264, b, 'AES50 (só X32/M32): um cabo de rede substitui o multicabo e ainda permite dividir o palco entre duas mesas.')

def d21():
    b = box(10, 70, 150, 64, '!Pedaleira ou\ncontrolador MIDI', 'bx', size=12) + arr(160, 102, 208, 102) + txt(184, 94, 'MIDI', 'sm')
    b += box(210, 70, 110, 64, '!Mesa\nX AIR / M AIR', 'bxd', 'tw', size=12)
    rows = [('Program Change 1–64', 'Snapshots 1–64'), ('CC 0–15', 'faders dos canais 1–16'), ('CC 21–26', 'Aux 1–6'), ('CC 31', 'Main LR')]
    b += f'<rect x="350" y="10" width="320" height="190" rx="10" class="panel"/>' + txt(510, 32, 'Mapa MIDI fixo (canal MIDI 1)', 'b')
    for k, (a, c) in enumerate(rows):
        y = 60 + k * 36
        b += box(362, y - 14, 140, 26, a, 'bxo', size=11.5) + arr(502, y - 1, 520, y - 1) + txt(526, y + 3, c, 'sm', 'start')
    b += txt(10, 180, 'MIDI não leva áudio: só comandos.', 'sm', 'start') + txt(10, 196, 'Família M32 tem mapa próprio (21.1.3).', 'sm', 'start')
    return fig(210, b, 'MIDI nas X AIR / M AIR: trocar snapshot e mover faders por comandos de um controlador externo.')

def d22():
    steps = ['!1. Backup\nshows e cenas\nno PC/pendrive', '!2. Baixe o\nfirmware oficial', '!3. Atualize\nX AIR: pelo app\nX32/M32: pendrive', '!4. Espere\nsem desligar', '!5. Confira\ne recarregue\no show']
    b = ''
    for k, l in enumerate(steps):
        x = 6 + k * 136
        b += box(x, 20, 120, 80, l, 'bxo' if k == 0 else 'bx', size=11.5)
        if k: b += arr(x - 16, 60, x - 2, 60)
    b += box(6, 124, 324, 56, '!Nunca no dia do show\natualize antes e teste com calma', 'bxr', size=12)
    b += box(346, 124, 324, 56, '!Travou na X32/M32?\nreligue sem segurar o botão: volta ao anterior', 'bx', size=11.5)
    return fig(190, b, 'Atualizar firmware com segurança (detalhes de cada modelo na tabela 22.1.1).')

def d23():
    cols = [('Antes do evento', ['firmware e apps em dia', 'show preparado em casa', 'rede própria da mesa', 'Mixer → PC e salve a cena', 'afine o PA e faça ring out']),
            ('Na passagem de som', ['ganho primeiro: média −18 dBFS', 'phantom → ganho → low cut', 'EQ, dinâmica, envios, fader', 'retornos pré-fader, fora do LR', 'efeitos por envio pós-fader']),
            ('Depois', ['salve a cena e exporte backup', 'treine com virtual soundcheck', 'volte as fontes para o palco', 'trave a mesa (X32/M32)', 'desligue: caixas antes da mesa'])]
    b = ''
    for k, (t, items) in enumerate(cols):
        x = 6 + k * 226
        b += box(x, 10, 216, 36, '!' + t, ['bxb', 'bxo', 'bxg'][k], size=12.5)
        b += f'<rect x="{x}" y="54" width="216" height="180" rx="10" class="panel"/>'
        for j, it in enumerate(items):
            b += txt(x + 14, 82 + j * 32, '• ' + it, '', 'start', 12)
        if k: b += arr(x - 9, 28, x - 1, 28)
    return fig(244, b, 'O dia do evento em três tempos (resumo do checklist 23.2.4).')

def d24():
    rows = [('RESET 10 s para consertar a rede', 'RESET 2 s: só a rede volta ao padrão'), ('conectar com PC → Mixer', 'conectar com Mixer → PC'),
            ('controlar a mesa pelo cabo USB', 'controle é pela rede; USB é áudio'), ('cabo de rede na porta Ultranet', 'Ethernet na porta Ethernet'),
            ('efeito pré-fader numa mesa de PA', 'efeito pós-fader, retorno pré-fader'), ('mixar mexendo no ganho', 'ganho fixo; mixe nos faders'),
            ('Wi-Fi interno no show cheio', 'roteador externo 5 GHz + um aparelho no cabo')]
    b = txt(170, 20, 'Erro comum', 'b') + txt(510, 20, 'Faça assim', 'b')
    for k, (e, c) in enumerate(rows):
        y = 32 + k * 42
        b += box(10, y, 320, 34, '✗  ' + e, 'bxr', size=12) + arr(332, y + 17, 348, y + 17) + box(350, y, 320, 34, '✓  ' + c, 'bxg', size=12)
    return fig(330, b, 'Sete erros que mais aparecem na prática e a correção de cada um (detalhes no capítulo 24).')

def d25():
    data = [('XR18', 16, 'a'), ('X18', 16, 'a'), ('XR16', 8, 'a'), ('XR12', 4, 'a'), ('MR18', 16, 'a'), ('MR12', 4, 'a'),
            ('X32', 32, 'b'), ('X32 Rack', 16, 'b'), ('X32 Compact', 16, 'b'), ('X32 Producer', 16, 'b'), ('M32', 32, 'b'), ('M32R', 16, 'b'), ('M32C', 0, 'b')]
    b = ''
    for v in (0, 8, 16, 24, 32):
        x = 120 + v * 15
        b += f'<line x1="{x}" y1="14" x2="{x}" y2="{14 + 13 * 22}" class="grid"/>' + txt(x, 316, str(v), 'sm')
    for k, (n, v, f) in enumerate(data):
        y = 18 + k * 22
        b += txt(112, y + 12, n, 'sm', 'end')
        b += f'<rect x="120" y="{y}" width="{max(v * 15, 2)}" height="15" rx="2" class="{"bara" if f == "a" else "barb"}"/>'
        b += txt(126 + v * 15, y + 12, str(v) + (' (pré nos stageboxes)' if v == 0 else ''), 'lbl', 'start')
    b += f'<rect x="560" y="30" width="14" height="14" class="bara"/>' + txt(580, 42, 'X AIR / M AIR', 'sm', 'start')
    b += f'<rect x="560" y="54" width="14" height="14" class="barb"/>' + txt(580, 66, 'X32 / M32', 'sm', 'start')
    b += txt(400, 334, 'pré-amplificadores de microfone locais', 'sm')
    return fig(342, b, 'Pré-amplificadores de microfone em cada mesa (dados das tabelas 1.1.5 e 1.1.6).')

def d27():
    b = box(10, 110, 110, 44, '!Canal', 'bxo', size=12.5)
    b += box(200, 20, 140, 40, '!Main LR', 'bxb', size=12) + arr(120, 118, 198, 48)
    b += box(420, 20, 100, 40, 'PA', size=12) + arr(340, 40, 418, 40)
    b += box(200, 90, 140, 40, '!Aux / Mix bus', 'bx', size=12) + arr(120, 128, 198, 112) + txt(150, 140, 'envio', 'sm')
    b += box(420, 90, 100, 30, 'retorno', size=12) + arr(340, 105, 418, 105)
    b += box(200, 160, 140, 40, '!FX (slot)', 'bxg', size=12) + arr(120, 142, 198, 176) + txt(150, 192, 'envio FX', 'sm')
    b += path('M 340 180 L 378 180 L 378 54 L 344 54', 'lnd') + txt(384, 172, 'FX return', 'sm', 'start')
    b += box(560, 60, 110, 46, '!Matriz\n(X32/M32)', 'bx', size=12) + txt(615, 124, 'zonas, live', 'sm')
    b += path('M 270 20 L 270 10 L 615 10 L 615 58', 'lnd') + path('M 340 124 L 545 124 L 545 90 L 558 90', 'lnd')
    b += box(10, 210, 110, 40, '!DCA', 'bxo', size=12) + f'<line x1="65" y1="210" x2="65" y2="156" class="ctl"/>' + txt(130, 236, 'comanda o fader, sem áudio', 'sm', 'start')
    b += f'<rect x="4" y="2" width="672" height="264" rx="12" class="frame"/>' + txt(670, 258, 'Cena: guarda tudo isto', 'lbl', 'end')
    return fig(272, b, 'Mapa dos termos principais: por onde o som anda dentro da mesa.')

DIAGRAMS = {0: [d0], 1: [d1], 2: [d2], 3: [d3], 4: [d4], 5: [d5, d5b], 6: [d6], 7: [d7], 8: [d8], 9: [d9], 10: [d10],
            11: [d11], 12: [d12], 13: [d13], 14: [d14], 15: [d15], 16: [d16], 17: [d17], 18: [d18], 19: [d19], 20: [d20],
            21: [d21], 22: [d22], 23: [d23], 24: [d24], 25: [d25], 27: [d27]}

# ---------------------------------------------------------------- montagem
DROP = ('> Para o curso, redesenhe estes cenários',)

def build(md_path, out_path, pages):
    lines = open(md_path, encoding='utf-8').read().split('\n')
    lines = [l for l in lines if not l.startswith(DROP)]
    title_line = lines[0][2:]
    main_title, mesas_all = split_title(title_line)
    chapters = []; cur = None
    for ln in lines:
        m = re.match(r'^## (\d+)\. (.*)$', ln)
        if m:
            cur = {'n': int(m.group(1)), 'title': m.group(2), 'lines': []}; chapters.append(cur); continue
        if cur: cur['lines'].append(ln)
    body = []
    for ch in chapters:
        n = ch['n']; t, mesas = split_title(ch['title'])
        ls = ch['lines']
        k = next((i for i, l in enumerate(ls) if l.startswith('### ')), len(ls))
        intro, rest = ls[:k], ls[k:]
        subs = [split_title(re.sub(r'^#### ', '', l))[0] for l in rest if l.startswith('#### ')]
        figs = ''.join(d() for d in DIAGRAMS.get(n, []))
        nesta = ''
        if subs:
            nesta = '<div class="nesta"><div class="nesta-t">Neste capítulo</div><ul>' + ''.join(f'<li>{inline(s)}</li>' for s in subs) + '</ul></div>'
        cls = 'chapter glossary' if n == 27 else 'chapter'
        body.append(f'<section class="{cls}" id="cap-{n}"><div class="opener"><div class="chap-label">CAPÍTULO {n:02d}</div>'
                    f'<h2><span class="ht">{inline(t)}</span> <span class="mesas">{inline(mesas)}</span></h2>'
                    f'{render_blocks(intro)}{figs}{nesta}</div>{render_blocks(rest)}</section>')
    toc = ''.join(f'<li><a href="#cap-{c["n"]}"><span class="tn">{c["n"]:02d}</span><span class="tt">{inline(split_title(c["title"])[0])}</span>'
                  f'<span class="dots"></span><span class="tp">{pages.get(str(c["n"]), "")}</span></a></li>' for c in chapters)
    cover = (f'<section class="cover"><div class="cover-top">Curso prático · mesas digitais</div>'
             f'<h1>{inline(main_title)} <span class="mesas">{inline(mesas_all)}</span></h1>'
             f'<div class="cover-sub">Do primeiro cabo ao show: manual oficial e prática de operação, num só material.</div>'
             f'{cover_art()}'
             f'<div class="cover-mesas"><div class="cm-t">Mesas cobertas</div>'
             f'<div class="fam"><b>Família X\u00a0AIR / M\u00a0AIR</b><span>XR18</span><span>X18</span><span>XR16</span><span>XR12</span><span>MR18</span><span>MR12</span></div>'
             f'<div class="fam"><b>Família X32 / M32</b><span>X32</span><span>X32 Rack</span><span>X32 Compact</span><span>X32 Producer</span><span>M32</span><span>M32R</span><span>M32C</span></div>'
             f'</div>'
             f'<div class="cover-foot">Material de aula em português do Brasil · '
             f'Behringer e Midas são marcas de seus donos; este curso é independente e não oficial.</div></section>')
    howto = ('<section class="howto"><h2 class="plain">Como usar este material</h2>'
             '<div class="legend">'
             '<div class="lg"><span class="sw sw-m">Parte 1</span><div><b>O que diz o manual</b><br>Parte 1 de cada capítulo: a referência oficial.</div></div>'
             '<div class="lg"><span class="sw sw-c">Parte 2</span><div><b>Na prática</b><br>Parte 2: como se opera, com dicas, valores de partida e erros comuns.</div></div>'
             '<div class="lg"><span class="mesas">(XR18, X32 …)</span><div>Entre parênteses, em todo título: as mesas em que o assunto vale.</div></div>'
             f'<div class="lg">{DVB}<div>Ponto com mais de um jeito correto de fazer: o curso mostra todas as abordagens, com o efeito e o contexto de cada uma, sem escolher lado (lista em 24.2.3).</div></div>'
             '<div class="lg"><span class="warn">⚠</span><div>Atenção: o dado muda com a unidade, a versão ou o firmware. Confira na sua mesa.</div></div>'
             '<div class="lg"><span class="sw sw-cena">Fechando</span><div>Cada capítulo fecha com o que você já sabe fazer e o próximo passo.</div></div>'
             '<div class="lg"><span class="tbox">Termo</span><div>Caixas com borda laranja explicam um termo técnico na primeira vez que ele aparece. O glossário completo está no capítulo 27.</div></div>'
             '</div><p class="small">Os diagramas deste material foram desenhados para o curso e simplificam a realidade: '
             'servem para entender a ideia, não para substituir a tela da sua mesa.</p></section>')
    doc = f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<title>Curso Behringer e Midas</title><style>{CSS}</style></head><body>
<svg width="0" height="0" style="position:absolute"><defs>
<marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#3b4b5c"/></marker>
<marker id="ahr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#c92a2a"/></marker>
</defs></svg>
{cover}
<section class="toc"><h2 class="plain">Sumário</h2><ol>{toc}</ol></section>
{howto}
{"".join(body)}
</body></html>'''
    open(out_path, 'w', encoding='utf-8').write(doc)

def cover_art():
    b = '<rect x="0" y="0" width="680" height="190" rx="14" class="cv-bg"/>'
    for k in range(16):
        x = 40 + k * 38
        v = 0.5 + 0.35 * math.sin(k * 0.9) * math.cos(k * 0.37)
        b += f'<rect x="{x - 2}" y="30" width="4" height="120" rx="2" class="cv-track"/>'
        b += f'<rect x="{x - 12}" y="{30 + (1 - v) * 120 - 7:.1f}" width="24" height="14" rx="3" class="{"cv-capo" if k in (3, 9) else "cv-cap"}"/>'
        b += f'<text x="{x}" y="172" text-anchor="middle" class="cv-num">{k + 1}</text>'
    return f'<svg class="cover-art" viewBox="0 0 680 190" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">{b}</svg>'

CSS = r'''
@page { size: A4; }
:root { --ink:#1b2430; --muted:#5c6773; --accent:#e8590c; --blue:#1c7ed6; --green:#2b8a3e; --line:#d5dbe2; --soft:#f4f6f8; }
* { box-sizing: border-box; }
html, body { background:#fff; }
body { font-family: -apple-system, "Helvetica Neue", Helvetica, Arial, sans-serif; color: var(--ink); font-size: 10.2pt; line-height: 1.45; margin: 0; }
a { color: #1864ab; text-decoration: none; word-break: break-all; }
code { font-family: Menlo, Consolas, monospace; font-size: 0.88em; background: var(--soft); padding: 0 3px; border-radius: 3px; }
pre { font-family: Menlo, Consolas, monospace; font-size: 8.4pt; background: var(--soft); border: 1px solid var(--line); border-radius: 6px; padding: 8px 10px; white-space: pre-wrap; break-inside: avoid; }
p { margin: 0 0 6px; }
strong { font-weight: 700; }
.mesas { display: block; font-size: 0.62em; font-weight: 500; color: var(--muted); letter-spacing: 0; margin-top: 2px; line-height: 1.3; }
h2 .mesas { font-size: 0.42em; }
.cover h1 .mesas { font-size: 0.4em; margin-top: 3mm; }
h3, h4, h5 { break-after: avoid; break-inside: avoid; }
h3::after, h4::after { content: ""; display: block; height: 28mm; margin-bottom: -28mm; }
h3 { font-size: 13pt; margin: 18px 0 8px; padding: 6px 10px; border-radius: 6px; }
h3.part-manual { background: #e7f1fb; border-left: 5px solid var(--blue); }
h3.part-cursos { background: #ebfbee; border-left: 5px solid var(--green); }
h4 { font-size: 11pt; margin: 14px 0 5px; padding-bottom: 3px; border-bottom: 1px solid var(--line); }
ul, ol { margin: 2px 0 6px; padding-left: 22px; }
li { margin: 1.5px 0; }
li > ul, li > ol { margin: 2px 0; }
p.cont { margin: 3px 0 3px; }
.tbl { margin: 6px 0 10px; }
table { border-collapse: collapse; width: 100%; font-size: 8.6pt; line-height: 1.32; }
.tbl.wide table { font-size: 7.6pt; }
th code { background: rgba(255,255,255,.15); color: #fff; }
th { background: #2c3a4a; color: #fff; text-align: left; font-weight: 600; padding: 4px 5px; }
td { border-bottom: 1px solid var(--line); padding: 3.5px 5px; vertical-align: top; }
tr:nth-child(even) td { background: #f8f9fb; }
tr { break-inside: avoid; }
thead { display: table-header-group; }
blockquote { margin: 8px 0; padding: 7px 10px; border-radius: 6px; break-inside: avoid; font-size: 9.6pt; }
blockquote p:last-child { margin-bottom: 0; }
blockquote.term { background: #fff4e6; border-left: 4px solid var(--accent); }
blockquote.note { background: var(--soft); border-left: 4px solid #8a94a0; }
blockquote.cena { background: #1b2430; color: #f1f3f5; border-left: 4px solid var(--accent); font-size: 10pt; }
blockquote.cena strong:first-child { color: #ffa94d; }
blockquote.fecha { background: #fff; border: 1px solid var(--line); border-left: 4px solid var(--ink); margin-top: 14px; }
.nc { color: #9c36b5; font-weight: 600; }
/* selo de abordagens divergentes: âmbar, ícone de bifurcação, todas as opções sem escolher lado */
blockquote.diverge { background: #fff8e6; border: 1px solid #f3cf80; border-left: 5px solid #e8a10c; }
blockquote.diverge p.dv-h { margin-bottom: 4px; }
.dv-badge { display: inline-flex; align-items: center; gap: 4px; font-size: 7.6pt; font-weight: 800; letter-spacing: .08em; text-transform: uppercase; color: #8a5300; background: #ffe5a8; border-radius: 3px; padding: 1.5px 6px 1px 4px; vertical-align: 1px; white-space: nowrap; }
.dv-badge svg { width: 10px; height: 10px; fill: none; stroke: #8a5300; stroke-width: 2.6; stroke-linecap: round; stroke-linejoin: round; }
.dv-t { font-weight: 700; }
blockquote.diverge ul { margin: 2px 0 2px; }
.lg .dv-badge { justify-self: start; font-size: 7pt; letter-spacing: .04em; }
p.cta { font-size: 12pt; line-height: 1.5; background: #1b2430; color: #f1f3f5; border-left: 5px solid var(--accent); border-radius: 6px; padding: 12px 16px; margin: 10px 0; break-inside: avoid; }
p.cta .ct { color: #ffa94d; font-size: 13pt; }
.warn { color: #d9480f; font-weight: 700; }
/* capa */
.cover { height: 258mm; display: flex; flex-direction: column; break-after: page; }
.cover-top { font-size: 10pt; letter-spacing: .14em; text-transform: uppercase; color: var(--accent); font-weight: 700; margin-top: 18mm; }
.cover h1 { font-size: 27pt; line-height: 1.12; margin: 6mm 0 4mm; letter-spacing: -.01em; }
.cover-sub { font-size: 12.5pt; color: var(--muted); max-width: 150mm; margin-bottom: 10mm; }
.cover-art { width: 100%; height: auto; }
.cv-bg { fill: #1b2430; } .cv-track { fill: #3d4b5c; } .cv-cap { fill: #dfe5ec; } .cv-capo { fill: #e8590c; }
.cv-num { fill: #8a94a0; font-size: 11px; }
.cover-mesas { margin-top: 10mm; font-size: 11pt; line-height: 1.6; }
.fam { margin: 3mm 0; display: flex; flex-wrap: wrap; gap: 6px; align-items: center; }
.fam b { width: 100%; font-size: 10.5pt; }
.fam span { background: #eef3f8; border: 1px solid #c7cfd8; border-radius: 14px; padding: 2px 10px; font-size: 10pt; font-weight: 600; }
.cm-n { font-size: 9pt; color: var(--muted); margin-top: 2mm; }
.cm-t .mesas { display: inline; font-size: 1em; letter-spacing: 0; text-transform: none; font-weight: 500; }
.cm-t { font-size: 9pt; text-transform: uppercase; letter-spacing: .12em; color: var(--muted); font-weight: 700; }
.cover-foot { margin-top: auto; font-size: 8.5pt; color: var(--muted); border-top: 1px solid var(--line); padding-top: 3mm; }
/* sumário */
h2.plain { font-size: 20pt; margin: 0 0 6mm; }
.toc { break-after: page; }
.toc ol { list-style: none; padding: 0; margin: 0; }
.toc li { margin: 0; border-bottom: 1px solid #edf0f3; }
.toc a { display: flex; align-items: baseline; gap: 8px; color: var(--ink); padding: 4.2px 0; word-break: normal; }
.tn { font-weight: 700; color: var(--accent); width: 22px; font-variant-numeric: tabular-nums; }
.tt { flex: 0 1 auto; }
.dots { flex: 1; border-bottom: 1px dotted #b8c0c8; transform: translateY(-3px); }
.tp { width: 26px; text-align: right; font-variant-numeric: tabular-nums; color: var(--muted); }
/* como usar */
.howto { break-after: page; }
.legend { display: grid; grid-template-columns: 1fr; gap: 9px; margin-bottom: 8mm; }
.lg { display: grid; grid-template-columns: 46mm 1fr; gap: 10px; align-items: center; font-size: 10pt; }
.sw { display: block; padding: 3px 8px; border-radius: 4px; font-weight: 600; }
.sw-m { background: #e7f1fb; border-left: 5px solid var(--blue); }
.sw-c { background: #ebfbee; border-left: 5px solid var(--green); }
.sw-cena { background: #1b2430; color: #ffa94d; border-left: 5px solid var(--accent); }
.lg .mesas { font-size: 9pt; }
.tbox { background: #fff4e6; border-left: 4px solid var(--accent); padding: 3px 8px; border-radius: 4px; font-weight: 600; }
.small { font-size: 9pt; color: var(--muted); }
/* capítulos */
.chapter { break-before: page; }
.chap-label { font-size: 9pt; font-weight: 800; letter-spacing: .18em; color: var(--accent); }
.chapter h2 { font-size: 21pt; line-height: 1.15; margin: 2mm 0 5mm; padding-bottom: 3mm; border-bottom: 3px solid var(--ink); }
.opener > p { font-size: 11pt; }
.nesta { background: var(--soft); border-radius: 8px; padding: 8px 12px; margin: 8px 0 6px; break-inside: avoid; }
.nesta-t { font-size: 8.5pt; text-transform: uppercase; letter-spacing: .12em; font-weight: 800; color: var(--muted); margin-bottom: 3px; }
.nesta ul { columns: 2; column-gap: 18px; margin: 0; padding-left: 14px; font-size: 9pt; }
.nesta li { break-inside: avoid; }
.fig { margin: 8px 0 10px; break-inside: avoid; }
.fig svg { width: 100%; height: auto; display: block; }
figcaption { font-size: 8.8pt; color: var(--muted); margin-top: 3px; padding-left: 8px; border-left: 3px solid var(--accent); }
.glossary td:first-child { font-weight: 700; width: 30%; }
/* SVG */
svg text { font-family: -apple-system, "Helvetica Neue", Helvetica, Arial, sans-serif; font-size: 13px; fill: #1b2430; }
svg text.b { font-weight: 700; } svg text.sm { font-size: 11px; fill: #5c6773; } svg text.tw { fill: #fff; }
svg text.lbl { font-size: 11px; font-weight: 700; fill: #c2410c; } svg text.lblr { font-size: 11px; font-weight: 700; fill: #c92a2a; }
svg text.zl { font-size: 11px; font-weight: 800; letter-spacing: .15em; fill: #8a94a0; } svg text.xr { font-size: 18px; fill: #c92a2a; font-weight: 800; }
.bx { fill: #eef3f8; stroke: #3b4b5c; stroke-width: 1.4; } .bxo { fill: #fff1e6; stroke: #e8590c; stroke-width: 1.6; }
.bxg { fill: #ebfbee; stroke: #2b8a3e; stroke-width: 1.4; } .bxb { fill: #e7f1fb; stroke: #1c7ed6; stroke-width: 1.4; }
.bxr { fill: #fff0f0; stroke: #c92a2a; stroke-width: 1.4; } .bxd { fill: #1b2430; stroke: #1b2430; }
.panel { fill: #f8f9fb; stroke: #d5dbe2; stroke-width: 1.2; } .zone { fill: #fbfaf6; stroke: #b8a98a; stroke-width: 1.4; stroke-dasharray: 6 4; }
.frame { fill: none; stroke: #b8c0c8; stroke-width: 1.2; stroke-dasharray: 5 4; }
.ln { stroke: #3b4b5c; stroke-width: 1.7; fill: none; marker-end: url(#ah); }
.lnd { stroke: #3b4b5c; stroke-width: 1.5; fill: none; stroke-dasharray: 5 4; marker-end: url(#ah); }
.ln2 { stroke: #3b4b5c; stroke-width: 1.7; fill: none; marker-end: url(#ah); marker-start: url(#ah); }
.lnd2 { stroke: #3b4b5c; stroke-width: 1.5; fill: none; stroke-dasharray: 5 4; marker-end: url(#ah); marker-start: url(#ah); }
.lnx { stroke: #c92a2a; stroke-width: 1.5; fill: none; stroke-dasharray: 5 4; marker-end: url(#ahr); }
.ctl { stroke: #e8590c; stroke-width: 1.5; stroke-dasharray: 4 3; }
.sep { stroke: #b8c0c8; stroke-width: 1; stroke-dasharray: 3 3; }
.grid { stroke: #e3e8ee; stroke-width: 1; } .axis { stroke: #8a94a0; stroke-width: 1.2; } .tick { stroke: #5c6773; }
.curve { fill: none; stroke: #e8590c; stroke-width: 2.6; } .curve2 { fill: none; stroke: #8a94a0; stroke-width: 1.6; stroke-dasharray: 5 4; }
.curve3 { fill: none; stroke: #1c7ed6; stroke-width: 2; } .curve4 { fill: none; stroke: #c92a2a; stroke-width: 2; }
.thr { stroke: #c92a2a; stroke-width: 1.4; stroke-dasharray: 6 4; }
.dot { fill: #e8590c; } .track { fill: #c7cfd8; } .cap { fill: #3b4b5c; } .capo { fill: #e8590c; } .capd { fill: #1c7ed6; }
.zg { fill: #b2f2bb; } .zy { fill: #ffe066; } .zr { fill: #ffa8a8; } .zgr { fill: #dee2e6; }
.mk { fill: none; stroke: #1b2430; stroke-width: 2; } .mk2 { fill: rgba(232,89,12,.35); stroke: #e8590c; }
.bar { fill: #74a7d8; } .barr { fill: #e8590c; } .bara { fill: #2b8a3e; } .barb { fill: #1c7ed6; }
.wedge { fill: #dfe5ec; stroke: #3b4b5c; stroke-width: 1.3; } .person { fill: #fff1e6; stroke: #e8590c; stroke-width: 1.6; }
.knob { fill: #dfe5ec; stroke: #3b4b5c; stroke-width: 1.4; } .needle { stroke: #e8590c; stroke-width: 3; stroke-linecap: round; }
'''

if __name__ == '__main__':
    pages = json.load(open(sys.argv[3])) if len(sys.argv) > 3 else {}
    build(sys.argv[1], sys.argv[2], pages)
    print('ok', sys.argv[2])
