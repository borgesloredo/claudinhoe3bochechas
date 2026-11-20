"""Correções da validação de 06/11/2026 (AudioLab Live XL, validacao/audiolab-live-xl.md), só na V2 de autoestudo.
Uso: python3 -I ws/audiolab-live-xl/corrigir.py entrada.html saida.html
Cada troca é buscada só dentro do pedaço do quiz (slide, JS sob medida ou (i)) e precisa achar o texto exatamente 1 vez.
Peça escondida antes do toque: o reset(x) do JS sob medida (roda na entrada, na tecla R e ao sair) a esconde, e o answer a mostra."""
import re
import sys

src, dst = sys.argv[1], sys.argv[2]
h = open(src, encoding='utf-8').read()
n_sec = h.count('<section')
n = 0


def area(q, k):
    """Trecho do quiz: 'sec' = slide (até o próximo <section id=), 'js' = script sob medida, 'inf' = template do (i)."""
    pat = {'sec': r'<section id="%s"[ >].*?(?=<section id=)',
           'js': r'<script>\n/\* %s · .*?</script>',
           'inf': r'<template id="v2i-%s">.*?</template>'}[k] % q
    m = list(re.finditer(pat, h, re.S))
    assert len(m) == 1, (q, k, len(m))
    return m[0].start(), m[0].end()


def tr(q, k, old, new):
    global h, n
    a, b = area(q, k)
    s = h[a:b]
    assert s.count(old) == 1, (q, k, old[:90], s.count(old))
    h = h[:a] + s.replace(old, new) + h[b:]
    n += 1


def gl(q, slug, txt):
    """Tira o botão do glossário do termo só no (i) daquele quiz; o texto fica."""
    tr(q, 'inf', f'<button type="button" class="gl" data-t="{slug}" aria-haspopup="dialog">{txt}</button>', txt)


# quiz-1: termo `fx` ("dois, FX1 e FX2, cada um com 12 programas") era a B; `subgrupo` ("a LIVE 24XL não tem") descartava a C
gl('quiz-1', 'fx', 'FX1 e FX2')
gl('quiz-1', 'subgrupo', 'subgrupos')
# quiz-1: os desenhos reais (1 fader na 16XL x 12 na 24XL) descartavam a A; antes do toque ficam molduras neutras com "?"
tr('quiz-1', 'sec', '<g transform="translate(12 48) scale(0.72)">', '<g class="q1-real" transform="translate(12 48) scale(0.72)">')
tr('quiz-1', 'sec', '<g transform="translate(12 330) scale(0.46)">', '<g class="q1-real" transform="translate(12 330) scale(0.46)">')
tr('quiz-1', 'sec', '<rect x="89.9" y="304.9" width="100.2" height="24.3" rx="3" class="tag16"/>',
   '<g class="q1-neu"><rect x="12" y="48" width="461" height="252" rx="8" class="slot2"/>'
   '<text x="242" y="188" font-size="40" class="t-lbl" text-anchor="middle">?</text>'
   '<rect x="12" y="330" width="276" height="258" rx="8" class="slot2"/>'
   '<text x="150" y="473" font-size="40" class="t-lbl" text-anchor="middle">?</text></g>\n'
   '<rect x="89.9" y="304.9" width="100.2" height="24.3" rx="3" class="tag16"/>')
tr('quiz-1', 'js', "no: P.q(x, '.b-no'), noT: P.qa(x, '.b-no text') });",
   "no: P.q(x, '.b-no'), noT: P.qa(x, '.b-no text'), real: P.qa(x, '.q1-real'), neu: P.q(x, '.q1-neu') });")
tr('quiz-1', 'js', "    P.gsap.set(x.names, { opacity: 0, y: 8 });",
   "    P.gsap.set(x.real, { opacity: 0 }); P.gsap.set(x.neu, { opacity: 1 });   // antes do toque: só as molduras\n"
   "    P.gsap.set(x.names, { opacity: 0, y: 8 });")
tr('quiz-1', 'js', "    P.verdict(t, r, {",
   "    t.to(x.neu, { opacity: 0, duration: P.D.fast }, 0).to(x.real, { opacity: 1, duration: P.D.snap }, 0);   // as mesas reais entram no toque\n"
   "    P.verdict(t, r, {")

# quiz-2: termo `subgrupo` ("a LIVE 24XL não tem") era a A
gl('quiz-2', 'subgrupo', 'subgrupos')

# quiz-4: título "SELEÇÃO E FADER" e visor "SELECIONADO" nomeavam a A; antes do toque viram "PAINEL E FADER" e "CANAL"
tr('quiz-4', 'sec', '<rect x="14" y="1.4" width="174.6" height="23.4" class="zone-cut"/><text x="22" y="20.5" font-size="18" class="t-lbl" text-anchor="start">SELEÇÃO E FADER</text>',
   '<rect x="14" y="1.4" width="164.3" height="23.4" class="zone-cut"/><text x="22" y="20.5" font-size="18" class="t-lbl" text-anchor="start">PAINEL E FADER</text>')
tr('quiz-4', 'sec', '<text x="28" y="348" font-size="18" class="t-lbl" text-anchor="start">SELECIONADO</text>',
   '<text x="28" y="348" font-size="18" class="t-lbl q4-lbl" text-anchor="start">CANAL</text>')
tr('quiz-4', 'js', "mm: [...P.qa(x, '.b-mm'), ...P.qa(x, '.m-main')] });",
   "mm: [...P.qa(x, '.b-mm'), ...P.qa(x, '.m-main')], lbl: P.q(x, '.q4-lbl') });")
tr('quiz-4', 'js', "    x.head.textContent = x.scr.textContent = '- -';",
   "    x.head.textContent = x.scr.textContent = '- -'; x.lbl.textContent = 'CANAL';")
tr('quiz-4', 'js', "    P.verdict(t, r, {",
   "    t.call(() => (x.lbl.textContent = 'SELECIONADO'), null, 0);   // o nome do visor só vira SELECIONADO no toque\n"
   "    P.verdict(t, r, {")
# quiz-4: o (i) repetia os dois nomes
tr('quiz-4', 'inf', 'o desenho "Seleção e fader"', 'o desenho "Painel e fader"')
tr('quiz-4', 'inf', 'o visor "Selecionado"', 'o visor "Canal"')

# quiz-5: `mini-display` e `camada` explicavam juntos que o nome muda pela camada (a B)
gl('quiz-5', 'mini-display', 'mini display')
gl('quiz-5', 'camada', 'camada')

# quiz-7: o (i) avisava que a tela vai mostrar nomes (só a C fala de nome)
tr('quiz-7', 'inf', 'a tela da mesa, ainda sem nomes,', 'a tela da mesa, ainda vazia,')

# quiz-8: termo `medidor` ("mostra o que entra e não é alterado pelo fader") era a A
gl('quiz-8', 'medidor', 'medidor')

# quiz-9: termo `ganho` ("muito ganho causa distorção") apontava a C
gl('quiz-9', 'ganho', 'ganho')
# quiz-9: o knob GANHO quase no fim mostrava a causa; antes do toque fica ao meio-dia e gira para o alto no toque
tr('quiz-9', 'sec', '<g class="b-knob " data-cx="100" data-cy="152" data-a="100">', '<g class="b-knob " data-cx="100" data-cy="152" data-a="0">')
tr('quiz-9', 'sec', '<g class="ptr" transform="rotate(100 100 152)">', '<g class="ptr" transform="rotate(0 100 152)">')
tr('quiz-9', 'js', "x.kn.dataset.a = 100; P.q(x, '.b-knob .ptr').setAttribute('transform', `rotate(100 ${x.kn.dataset.cx}",
   "x.kn.dataset.a = 0; P.q(x, '.b-knob .ptr').setAttribute('transform', `rotate(0 ${x.kn.dataset.cx}")
tr('quiz-9', 'js', "    P.verdict(t, r, {",
   "    P.knob(t, x.kn, 100, 0, P.D.snap);   // o ganho alto só aparece no toque\n"
   "    P.verdict(t, r, {")
tr('quiz-9', 'js', "        P.knob(t, x.kn, 15, at, P.D.slow);\n        P.meter(t, x.m, .62, at + .3, P.D.std);\n        P.lit(t, x.clip, false, at + .45);",
   "        P.knob(t, x.kn, 15, at + .35, P.D.slow);   // depois de subir ao alto, o ganho desce\n"
   "        P.meter(t, x.m, .62, at + .65, P.D.std);\n        P.lit(t, x.clip, false, at + .8);")

# quiz-10: termo `polaridade` ("corrigir dois microfones ... que se anulam") era o cenário com a resposta
gl('quiz-10', 'polaridade', 'polaridade')
# quiz-10: as ondas TOP e BOT em oposição mostravam o cancelamento; antes do toque viram "—" (a SOMA fina fica: é o cenário)
tr('quiz-10', 'sec', '<text x="36" y="316" font-size="18" class="t-ui" text-anchor="start">SOMA</text>',
   '<text x="36" y="316" font-size="18" class="t-ui" text-anchor="start">SOMA</text>'
   '<text x="280" y="126" font-size="18" class="t-ui q10-dash" text-anchor="middle">—</text>'
   '<text x="280" y="216" font-size="18" class="t-ui q10-dash" text-anchor="middle">—</text>')
tr('quiz-10', 'js', "no: P.q(x, '.b-no'), noT: P.qa(x, '.b-no text') });",
   "no: P.q(x, '.b-no'), noT: P.qa(x, '.b-no text'), dash: P.qa(x, '.q10-dash') });")
tr('quiz-10', 'js', "    g.set(x.no, { opacity: 0, y: 8 }); g.set(x.head, { opacity: 1 });",
   "    g.set(x.no, { opacity: 0, y: 8 }); g.set(x.head, { opacity: 1 });\n"
   "    g.set([x.top, x.bot], { opacity: 0 }); g.set(x.dash, { opacity: 1 });   // antes do toque: só os traços")
tr('quiz-10', 'js', "    P.verdict(t, r, {",
   "    t.to(x.dash, { opacity: 0, duration: P.D.fast }, 0).to([x.top, x.bot], { opacity: 1, duration: P.D.fast }, 0);   // as ondas entram no toque\n"
   "    P.verdict(t, r, {")
tr('quiz-10', 'inf', 'as ondas TOP e BOT e a SOMA em vermelho', 'as linhas TOP e BOT e a SOMA em vermelho')

# quiz-11: termo `threshold` (gate corta abaixo, compressor reduz acima) era a B e mostrava que a A é o compressor
gl('quiz-11', 'threshold', 'threshold')

# quiz-14: termo `Assign` ("decide para onde o canal vai: Main…") levava direto à B
gl('quiz-14', 'assign', 'Assign')

# quiz-18: termo `DCA` ("Nenhum áudio passa pelo DCA") era a C
gl('quiz-18', 'dca', 'DCA')
# quiz-18: as linhas verdes VOZ -> MAIN, sem passar pelo DCA, descartavam A e B; antes do toque ficam escondidas
tr('quiz-18', 'js', "g.set(x.aw, { opacity: 1 });", "g.set(x.aw, { opacity: 0 });")
tr('quiz-18', 'js', "        P.show(t, x.ctl, 1, at + .1, .4);\n",
   "        P.show(t, x.ctl, 1, at + .1, .4);\n"
   "        t.to(x.aw, { opacity: 1, duration: P.D.snap }, at);   // as linhas VOZ -> MAIN entram no toque\n")

# quiz-19: termo `PRE` ("no POST ... acompanha o fader") respondia com o verbo da pergunta
gl('quiz-19', 'pre-pos-fader', 'PRE')

# quiz-20: termos `PFL` ("funciona mesmo com o fader no zero") e `AFL` ("depois do fader")
gl('quiz-20', 'afl', 'AFL')
gl('quiz-20', 'pfl', 'PFL')
# quiz-20: o ponto de captura depois do fader no zero, com a seta ao FONE, descartava a A; antes do toque fica escondido
tr('quiz-20', 'js', "P.gsap.set(x.tap, { x: 0 });", "P.gsap.set(x.tap, { x: 0, opacity: 0 });")
tr('quiz-20', 'js', "    P.verdict(t, r, {",
   "    t.to(x.tap, { opacity: 1, duration: P.D.fast }, 0);   // o ponto de captura e a seta ao FONE entram no toque\n"
   "    P.verdict(t, r, {")
tr('quiz-20', 'inf', ' Um ponto de captura leva uma cópia ao quadro FONE.', '')

# quiz-21: termos `ring out` (sobe o envio e acha a frequência) e `RTA` ("ajuda a achar a frequência") eram a A
gl('quiz-21', 'ring-out', 'ring out')
gl('quiz-21', 'rta', 'RTA')

# quiz-22: termo `Automix` ("reduz sozinho o nível dos microfones que não estão em uso") era a B
gl('quiz-22', 'automix', 'Automix')

# quiz-23: termo `cena` ("não move os knobs de ganho") descartava a A
gl('quiz-23', 'cena', 'cena')

# quiz-24: termos `USB` e `driver` ("não precisa de driver") descartavam a C
gl('quiz-24', 'usb', 'USB')
gl('quiz-24', 'driver-software', 'driver')
# quiz-24: só a A repetia "gravação" e "evento" da pergunta
tr('quiz-24', 'sec', '<span class="otx">Testar a gravação antes do evento começar</span>', '<span class="otx">Fazer um teste curto antes do início</span>')
tr('quiz-24', 'inf', '<b>A</b> fala de um teste de gravação;', '<b>A</b> fala de um teste;')

# quiz-25: termo `LAN` ("a WAN ... não deve receber o cabo da mesa") dava a A e descartava B e C
gl('quiz-25', 'lan-wan', 'LAN')

# s22-1 (motion, rótulo errado de gravidade baixa): o LCD termina em "1" com o rótulo no plural "ABERTOS"
tr('s22-1', 'sec', '<text x="574" y="270" font-size="18" class="t-lbl" text-anchor="middle">ABERTOS</text>',
   '<text x="574" y="270" font-size="18" class="t-lbl" text-anchor="middle">ABERTO(S)</text>')

assert h.count('<section') == n_sec, (h.count('<section'), n_sec)
open(dst, 'w', encoding='utf-8').write(h)
print(f'corrigir ok: {n} trocas')
