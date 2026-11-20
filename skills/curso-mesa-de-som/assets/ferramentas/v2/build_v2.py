#!/usr/bin/env python3
"""Gera a V2 dos slides (autoestudo) a partir da V1, sem mexer na V1.

Uso: python3 -I tools/v2/build_v2.py [--info DIR] [--out DIR] [--audio-ext EXT]

- Lê a V1 (entregas/v1-aulas/deck/index.html, só leitura) e escreve tools/v2/slides.json.
- Copia lib/ (sem o plugin de notas) e fonts/ para a saída.
- Tira as <aside class="notes"> e o plugin de notas; injeta os botões (i) e ▶, o popup e o player.
- Conteúdo: info/<id>.html (popup), glossario.json + glossario-extra-*.json (termos .gl),
  <saída>/audio/<id>.<ext> (áudio). Slide sem info ou sem áudio: o botão fica desabilitado.
"""
import argparse, glob, html, json, re, shutil, sys
from html.parser import HTMLParser
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
V1 = ROOT / "entregas/v1-aulas/deck"
EXTS = ["m4a", "mp3", "ogg", "opus", "wav"]
INLINE = {"b", "strong", "i", "em", "span", "a", "sub", "sup", "small", "u", "abbr", "code", "tspan"}
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}


class Deck(HTMLParser):
    """Lista as <section> folha da V1: id, h/v, capítulo, título, texto visível e nota."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.secs, self.open, self.h = [], [], -1   # open = pilha de sections abertas
        self.skip = 0   # dentro de <script>/<style>
        self.note = 0   # dentro da <aside class="notes">
        self.head = 0   # dentro do 1º h1/h2/h3 do slide

    def handle_starttag(self, tag, a):
        a = dict(a)
        if tag == "section":
            if not self.open:
                self.h += 1
                v = 0
            else:
                par = self.open[-1]
                par["stack"] = True
                v = par["kids"]
                par["kids"] += 1
            self.open.append({"id": a.get("id", ""), "h": self.h, "v": v, "tipo": a.get("data-anim", ""),
                              "cls": a.get("class", ""), "kids": 0, "stack": False,
                              "titulo": [], "linhas": [], "texto": [], "nota": [], "has_title": False})
        elif tag in ("script", "style"):
            self.skip += 1
        elif tag == "aside" and "notes" in a.get("class", "").split():
            self.note = 1
        elif self.note and tag in ("p", "li", "div", "br"):
            self.open[-1]["nota"].append("\n")
        elif tag in ("h1", "h2", "h3") and self.open and not self.note and not self.open[-1]["has_title"]:
            self.head = 1
        self.gap(tag)

    def gap(self, tag):   # fronteira de bloco = espaço no texto (inline, como <b>, não separa palavra)
        if self.open and not self.note and tag not in INLINE:
            self.open[-1]["texto"].append(" ")
            if self.head:
                self.open[-1]["titulo"].append(" ")
                self.open[-1]["linhas"].append("\n")   # <br> ou bloco dentro do título = quebra de linha (vira " · " no popup)

    def handle_endtag(self, tag):
        self.gap(tag)
        if tag == "section" and self.open:
            s = self.open.pop()
            if not s["stack"]:
                self.secs.append(s)
        elif tag in ("script", "style"):
            self.skip -= 1
        elif tag == "aside" and self.note:
            self.note = 0
        elif tag in ("h1", "h2", "h3") and self.head:
            self.head = 0
            self.open[-1]["has_title"] = True

    def handle_data(self, d):
        if self.skip or not self.open:
            return
        s = self.open[-1]
        if self.note:
            s["nota"].append(d)
        else:
            s["texto"].append(d)
            if self.head:
                s["titulo"].append(d)
                s["linhas"].append(d)


def titulo_popup(t):
    """Título do popup: cada linha do título da V1 (<br> ou bloco) separada por " · ", ou por espaço se a linha já termina/começa em "·"."""
    out = ""
    for l in filter(None, (re.sub(r"\s+", " ", x).strip() for x in t.split("\n"))):
        out = l if not out else out + (" " if out.endswith("·") or l.startswith("·") else " · ") + l
    return out


def slides_of(src):
    p = Deck()
    p.feed(src)
    norm = lambda t: re.sub(r"\s+", " ", "".join(t)).strip()
    out, cap_da_pilha = [], {}
    for s in p.secs:
        m = re.match(r"cap-(\d+)$", s["id"])
        if m:
            cap_da_pilha[s["h"]] = int(m.group(1))
    for s in p.secs:
        m = re.match(r"(?:cap|quiz)-(\d+)$|s(\d+)-", s["id"])
        cap = int(m.group(1) or m.group(2)) if m else cap_da_pilha.get(s["h"])
        nota = re.sub(r"[ \t]+", " ", "".join(s["nota"]))
        nota = re.sub(r"\s*\n\s*", "\n", nota).strip()
        out.append({"id": s["id"], "capitulo": cap, "h": s["h"], "v": s["v"], "tipo": s["tipo"],
                    "titulo": norm(s["titulo"]), "texto": norm(s["texto"]), "nota_v1": nota,
                    "_titulo_popup": titulo_popup("".join(s["linhas"]))})
    return out


def glossario():
    arqs = [HERE / "glossario.json"] + sorted(map(Path, glob.glob(str(HERE / "glossario-extra-*.json"))))
    g = {}
    for a in arqs:
        if a.exists():
            for t in json.loads(a.read_text(encoding="utf8")):
                g[t["slug"]] = [t["termo"], t["definicao"], t.get("exemplo_curto", "")]
    return g


GL = re.compile(r'<span\b([^>]*\bclass="gl"[^>]*)>(.*?)</span>', re.S)


def info_html(path, gl, avisos):
    """Conteúdo do popup: os termos <span class="gl" data-t="slug"> viram botões (teclado e leitor de tela)."""
    s = path.read_text(encoding="utf8")
    if re.search(r"<script|<[^>]*\son\w+\s*=|\.\./", s, re.I):
        sys.exit(f"ERRO {path.name}: <script>, on*= ou ../ não são permitidos no popup")

    def rep(m):
        t = re.search(r'data-t="([^"]+)"', m.group(1))
        slug = t and t.group(1)
        if slug not in gl:
            avisos.append(f"{path.name}: termo sem verbete no glossário: {slug or '(sem data-t)'}")
            return m.group(2)
        return f'<button type="button" class="gl" data-t="{slug}" aria-haspopup="dialog">{m.group(2)}</button>'

    return GL.sub(rep, s).strip()


def js_json(o):
    return json.dumps(o, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


CSS = """<style id="v2-css">
/* === V2: botões (i) e ▶ no canto superior direito, espelhando o atalho do sumário (canto superior esquerdo).
   Ficam no palco 1280×720 (escalam junto), na faixa vazia x ≥ 1220 / y ≤ 100: área de clique 40×40 em x 1234–1274, (i) y 14–54, ▶ y 58–98.
   Abaixo da escala 1, o script recalcula posição e tamanho para manter 40 px de tela (cresce para a margem preta, nunca para cima do conteúdo).
   Não entram no cromo (o cromo some na capa). === */
.v2ctl { position: absolute; left: 0; top: 0; width: 1280px; height: 720px; pointer-events: none; z-index: 21; --v2u: 1; }
.v2b { position: absolute; right: 6px; width: 40px; height: 40px; padding: 0; margin: 0; border: 0; border-radius: 50%; background: none;
  color: var(--ink-2); cursor: pointer; pointer-events: auto; display: grid; place-items: center; transition: color .15s, opacity .2s; }
.v2b.i { top: 14px; } .v2b.p { top: 58px; }
.v2b svg { grid-area: 1 / 1; width: 100%; height: 100%; overflow: visible; fill: none; stroke: currentColor; stroke-width: 2.2; stroke-linecap: round; stroke-linejoin: round; }
.v2b .ring { transform: rotate(-90deg); stroke-width: 2; }
.v2b .trk { transition: stroke .2s, fill .15s; }   /* o mesmo círculo nos dois botões: no ▶ é também o trilho do progresso */
.v2b .bar { fill: none; stroke: var(--lamp); stroke-width: 2.4; stroke-dasharray: 100; stroke-dashoffset: 100; opacity: 0; transition: opacity .2s; }
.v2b.on .bar, .v2b.half .bar { opacity: 1; }
.v2b.on .trk, .v2b.half .trk { stroke: var(--line-2); }   /* tocando: o trilho apaga e a parte já tocada acende em --lamp */
.v2b .pa { display: none; } .v2b.on .pl { display: none; } .v2b.on .pa { display: block; }
.v2b:hover:not(:disabled), .v2b:focus-visible, .v2b.on { color: var(--accent); outline: none; }
.v2b:hover:not(:disabled) .trk, .v2b:focus-visible .trk { fill: rgba(255, 154, 46, .10); }
.v2b:focus-visible { outline: calc(2px * var(--v2u)) solid var(--accent); outline-offset: calc(3px * var(--v2u)); }   /* foco afastado do anel de progresso */
.v2b:disabled { opacity: .3; cursor: default; }
.v2b.i.oi::after { content: ""; position: absolute; inset: 15%; border-radius: 50%; border: calc(2px * var(--v2u)) solid var(--accent); pointer-events: none;
  opacity: 0; animation: v2oi 1.6s cubic-bezier(.16, 1, .3, 1) .8s 1; }   /* 1ª visita: um único pulso no (i) */
@keyframes v2oi { from { opacity: .9; transform: scale(1); } to { opacity: 0; transform: scale(1.7); } }
@media (prefers-reduced-motion: reduce) { .v2b.i.oi::after { display: none; } }
.v2ctl.v2rol { position: fixed; }   /* celular em pé (rolagem do reveal): botões presos à tela */
.v2-test .v2ctl { visibility: hidden !important; }

/* === V2: popup (i) — paleta do deck; fora do palco, em px de tela === */
#v2pop { width: min(760px, calc(100vw - 32px)); max-height: min(84vh, 820px); margin: auto; padding: 0; border: 1.5px solid var(--line-2); border-radius: 10px;
  background: var(--bg-2); color: var(--ink-2); font: 400 22px/1.6 var(--f-body); box-shadow: 0 24px 80px rgba(0, 0, 0, .65); overflow: hidden; }
#v2pop[open] { display: flex; flex-direction: column; animation: v2in .2s cubic-bezier(.16, 1, .3, 1); }
@keyframes v2in { from { opacity: 0; transform: translateY(10px); } }
@media (prefers-reduced-motion: reduce) { #v2pop[open] { animation: none; } }
#v2pop::backdrop { background: rgba(6, 7, 8, .72); }
#v2pop [hidden] { display: none !important; }   /* o reset.css do reveal põe section { display: block } */
.v2-hd { display: flex; gap: 16px; align-items: flex-start; padding: 22px 22px 14px 28px; border-bottom: 1px solid var(--line); }
.v2-hd > div { flex: 1; min-width: 0; }
.v2-k { font: 500 16px/1.2 var(--f-mono); letter-spacing: .14em; text-transform: uppercase; color: var(--ink-3); }
.v2-t { margin: 10px 0 0; font: 800 30px/1.08 var(--f-display); color: var(--ink); }
.v2-x { flex: none; width: 44px; height: 44px; margin: -8px -8px 0 0; padding: 0; border: 0; border-radius: 50%; background: none; color: var(--ink-3); cursor: pointer; display: grid; place-items: center; }
.v2-x svg { width: 20px; height: 20px; stroke: currentColor; stroke-width: 2.4; stroke-linecap: round; fill: none; }
.v2-x:hover, .v2-x:focus-visible { color: var(--accent); outline: none; }
.v2-x:focus-visible { outline: 2px solid var(--accent); outline-offset: -2px; }
.v2-bd { overflow-y: auto; overscroll-behavior: contain; padding: 18px 28px 28px; outline: none; scrollbar-color: var(--ink-3) transparent; }
/* texto continua abaixo: degradê no pé do popup (some quando a rolagem chega ao fim); --v2sb = largura da barra, que fica de fora */
#v2pop::after { content: ''; position: absolute; left: 0; right: var(--v2sb, 0px); bottom: 0; height: 40px; pointer-events: none;
  background: linear-gradient(rgba(0, 0, 0, 0), var(--bg-2) 85%); opacity: 0; transition: opacity .2s; }
#v2pop.v2-more::after { opacity: 1; }
.v2-bd p, .v2-bd ul, .v2-bd ol { margin: 0 0 14px; } .v2-bd > :last-child, .v2-bd section > :last-child { margin-bottom: 0; }
.v2-bd ul, .v2-bd ol { padding-left: 1.3em; } .v2-bd li { margin: 0 0 6px; }
.v2-bd h3, .v2-bd h4 { margin: 22px 0 8px; font: 600 24px/1.2 var(--f-display); color: var(--ink); letter-spacing: .005em; }
.v2-bd b, .v2-bd strong { font-weight: 600; color: #fff; }
.v2-bd em { color: var(--ink); }
.v2-bd .gl { font: inherit; color: var(--ink); background: none; border: 0; border-radius: 0; padding: 0; margin: 0; cursor: pointer;
  text-decoration: underline dotted var(--accent); text-decoration-thickness: 2px; text-underline-offset: 4px; text-decoration-skip-ink: none; }
.v2-bd .gl:hover, .v2-bd .gl:focus-visible { color: var(--accent); outline: none; background: rgba(255, 154, 46, .1); }
.v2-back { display: inline-flex; gap: 8px; align-items: center; min-height: 40px; margin: 0 0 16px; padding: 11px 14px; border: 1.5px solid var(--line-2); border-radius: 3px;
  background: none; color: var(--ink-2); font: 500 16px/1 var(--f-mono); letter-spacing: .1em; text-transform: uppercase; cursor: pointer; }
.v2-back:hover, .v2-back:focus-visible { color: var(--accent); border-color: var(--accent); outline: none; }
.v2-back svg { width: 16px; height: 16px; stroke: currentColor; stroke-width: 2.4; fill: none; stroke-linecap: round; stroke-linejoin: round; }
.v2-def h3 { margin-top: 0; font-size: 28px; }
.v2-def .ex { padding: 10px 14px; border-left: 3px solid var(--line-2); background: var(--bg-1); color: var(--ink-2); font-size: 22px; }
</style>
"""

CTL = """<div class="v2ctl"><button type="button" class="v2b i" aria-haspopup="dialog" aria-label="Explicação deste slide" title="Explicação deste slide">\
<svg class="ring" viewBox="0 0 40 40" aria-hidden="true"><circle class="trk" cx="20" cy="20" r="13"/></svg>\
<svg viewBox="0 0 40 40" aria-hidden="true"><path d="M20 18.5v7"/><path d="M20 14h.01" stroke-width="3"/></svg></button>\
<button type="button" class="v2b p" aria-label="Ouvir a explicação" title="Ouvir a explicação">\
<svg class="ring" viewBox="0 0 40 40" aria-hidden="true"><circle class="trk" cx="20" cy="20" r="13"/><circle class="bar" cx="20" cy="20" r="13" pathLength="100"/></svg>\
<svg class="pl" viewBox="0 0 40 40" aria-hidden="true"><path d="M17.3 15.2v9.6l7.6-4.8z" stroke-width="2"/></svg>\
<svg class="pa" viewBox="0 0 40 40" aria-hidden="true"><path d="M17 15.5v9M23 15.5v9"/></svg></button></div>"""

POP = """<dialog id="v2pop" aria-labelledby="v2-t"><div class="v2-hd"><div><p class="v2-k" id="v2-k"></p><h2 class="v2-t" id="v2-t"></h2></div>\
<button type="button" class="v2-x" aria-label="Fechar (Esc)" title="Fechar (Esc)"><svg viewBox="0 0 20 20" aria-hidden="true"><path d="M4 4l12 12M16 4L4 16"/></svg></button></div>\
<div class="v2-bd" tabindex="-1"><section class="v2-info"></section><section class="v2-def" hidden aria-live="polite">\
<button type="button" class="v2-back"><svg viewBox="0 0 14 14" aria-hidden="true"><path d="M12 7H2M6 3L2 7l4 4"/></svg>Voltar à explicação</button>\
<h3></h3><p class="df"></p><p class="ex" hidden></p></section></div></dialog>"""

JS = r"""<script>
/* V2: popup (i), termos do glossário e player (▶). Nada aqui mexe nos slides. */
(() => {
  const $ = (s, r = document) => r.querySelector(s);
  const AUD = JSON.parse($('#v2-aud').textContent), GL = JSON.parse($('#v2-gl').textContent), TIT = JSON.parse($('#v2-tit').textContent);
  const base = id => id.replace(/-c\d+$/, '');   // continuação "(continuação)" usa a explicação do slide de origem se não tiver a sua
  const tplOf = id => $('#v2i-' + CSS.escape(id)) || $('#v2i-' + CSS.escape(base(id)));
  const audOf = id => AUD[id] || AUD[base(id)];
  /* os botões ficam dentro do .slides, que o reveal regrava (innerHTML) ao sair da rolagem do celular em pé: sempre buscar de novo, nunca guardar o nó */
  const bi = () => $('.v2b.i'), bp = () => $('.v2b.p'), arc = () => $('.v2b.p .bar'), ctl = () => $('.v2ctl');
  const dlg = $('#v2pop'), bd = $('.v2-bd', dlg),
    info = $('.v2-info', dlg), def = $('.v2-def', dlg), au = new Audio();
  au.preload = 'none';
  let sid = '', from = null, top = 0, raf = 0;

  const ring = f => { const a = arc(); if (a) a.style.strokeDashoffset = 100 - 100 * f; };
  const tick = () => { ring(au.duration ? au.currentTime / au.duration : 0); raf = au.paused ? 0 : requestAnimationFrame(tick); };
  const state = () => { const on = !au.paused, b = bp(); if (!b || b.disabled) return; b.classList.toggle('on', on); b.classList.toggle('half', !on && au.currentTime > 0);
    b.setAttribute('aria-label', on ? 'Pausar a explicação' : 'Ouvir a explicação'); b.title = b.getAttribute('aria-label'); b.setAttribute('aria-pressed', on); };
  function stop() { au.pause(); if (au.getAttribute('src')) { au.removeAttribute('src'); au.load(); } ring(0); state(); }
  au.addEventListener('play', () => { state(); if (!raf) tick(); });
  au.addEventListener('pause', state);
  au.addEventListener('ended', () => { au.currentTime = 0; ring(0); state(); });
  let falhou = '';   // áudio que não carregou: o ▶ fica desabilitado
  au.addEventListener('error', () => { if (au.getAttribute('src')) { falhou = sid; sync(); } });
  function play() {
    if (!au.paused) return au.pause();
    if (!au.getAttribute('src')) au.src = audOf(sid);
    au.play().catch(() => {});
  }

  function sync() {   // os botões refletem o que existe para o slide atual (sem mexer no áudio)
    const i = bi(), b = bp(); if (!i || !b) return;
    i.disabled = !tplOf(sid); b.disabled = !audOf(sid) || falhou === sid;
    i.title = i.disabled ? 'Explicação ainda não disponível' : 'Explicação deste slide'; i.setAttribute('aria-label', i.title);
    if (b.disabled) { b.classList.remove('on', 'half'); b.title = falhou === sid ? 'Áudio não encontrado' : 'Áudio ainda não disponível'; b.setAttribute('aria-label', b.title); }
    else state();
  }
  function update() {   // troca de slide: o áudio para; os botões refletem o que existe para o slide novo
    sid = Reveal.getCurrentSlide().id; stop(); sync();
  }

  /* reserva (slide sem h1–h3, ex.: kicker): cada <br> ou bloco vira " · " (ou espaço, se a linha já termina/começa em "·"). Não usa innerText, que muda com o layout. */
  const BLOCO = /^(BR|DIV|P|LI|UL|OL|H[1-6]|SECTION|TABLE|TR|TD|TH)$/;
  function titulo(el) {
    const ls = [''];
    (function walk(n) {
      for (const c of n.childNodes) {
        if (c.nodeType === 3) ls[ls.length - 1] += c.data;
        else if (c.nodeType === 1 && !/^(SCRIPT|STYLE|svg)$/.test(c.nodeName)) {
          const b = BLOCO.test(c.nodeName); if (b) ls.push(''); walk(c); if (b) ls.push('');
        }
      }
    })(el);
    return ls.map(l => l.replace(/\s+/g, ' ').trim()).filter(Boolean)
      .reduce((a, l) => !a ? l : a + (/·$/.test(a) || /^·/.test(l) ? ' ' : ' · ') + l, '');
  }

  /* botões ≥ 40 px de tela em qualquer escala: abaixo da escala 1 crescem para a margem preta, nunca para cima do conteúdo.
     Faixa sem conteúdo no palco: x ≥ 1220 e y ≤ 100 (unidades do palco). Fora do palco (margem preta) tudo é livre. */
  function lay() {
    const c = ctl(), I = bi(), B = bp(); if (!c || !I || !B) return;
    sync(); ring(au.duration ? au.currentTime / au.duration : 0);
    const put = (S, a, b) => [[I, a], [B, b]].forEach(([el, [l, t]]) => Object.assign(el.style, { left: l + 'px', top: t + 'px', right: 'auto', width: S + 'px', height: S + 'px' }));
    if (Reveal.isScrollView?.()) {   // celular em pé: o reveal vira rolagem e o palco não escala; os botões ficam fixos na borda direita da tela, como o atalho do sumário na esquerda
      c.classList.add('v2rol'); const v = Reveal.getViewportElement?.() || document.documentElement, r = v.getBoundingClientRect(), x = r.left + v.clientWidth - 46;
      put(40, [x, 14], [x, 58]); return c.style.setProperty('--v2u', 1);
    }
    c.classList.remove('v2rol');
    const s = Reveal.getScale() || 1, u = 1 / s, S = Math.max(40, 40 * u), g = 4 * Math.max(1, u), pad = 4 * Math.max(1, u);
    const R = $('.reveal').getBoundingClientRect(), P = $('.reveal .slides').getBoundingClientRect();
    const mR = Math.max(0, (R.right - P.right) * u), mT = Math.max(0, (P.top - R.top) * u);
    const ok = rs => rs.every(([x, y]) => x + S <= 1280 + mR + .5 && y >= -mT - .5 &&   // cabe na tela
      (x >= 1280 || y + S <= 0 || (x >= 1220 && y + S <= 100.5)));                        // fora do palco ou na faixa vazia
    const xr = Math.min(1234 + S, 1280 + mR - pad), x = xr - S;                          // coluna: borda esquerda fica em 1234 se der
    const y = Math.min(14, Math.max(98 - 2 * S - g, -mT + pad));                         // sobe para a margem de cima se precisar
    const cand = [
      [[x, y], [x, y + S + g]],                                                          // coluna no canto (o padrão em 1280×720)
      [[1280 + pad, 14], [1280 + pad, 14 + S + g]],                                     // coluna inteira na margem da direita
      [[1280 + mR - pad - 2 * S - g, -S - pad], [1280 + mR - pad - S, -S - pad]],        // lado a lado na margem de cima
    ];
    put(S, ...(cand.find(ok) || cand[0]));
    c.style.setProperty('--v2u', Math.max(1, u));
  }
  let lf = 0;
  const relay = () => { cancelAnimationFrame(lf); lf = requestAnimationFrame(lay); };

  /* 1ª visita: um único pulso no (i), para quem estuda sozinho achar a explicação (sem animação se o sistema pede menos movimento) */
  try { if (!localStorage.getItem('v2-oi') && !matchMedia('(prefers-reduced-motion: reduce)').matches) {
    const i = bi(); i.classList.add('oi'); i.addEventListener('animationend', () => i.classList.remove('oi'), { once: true }); localStorage.setItem('v2-oi', '1'); } } catch (e) {}

  function view(d) { info.hidden = d; def.hidden = !d; requestAnimationFrame(fade); }
  function abre() {
    const s = Reveal.getCurrentSlide(), t = $('h1, h2, h3', s) || $('.kicker', s);   // slide sem título (ex.: glossário): usa o kicker
    $('#v2-k').textContent = `Explicação · slide ${Reveal.getSlides().indexOf(s) + 1} de ${Reveal.getTotalSlides()}`;
    $('#v2-t').textContent = TIT[s.id] || (t ? titulo(t) : '');   // título vem do HTML da V1 (build); o DOM do slide pode estar dividido pela animação
    info.replaceChildren(tplOf(sid).content.cloneNode(true)); view(false);
    dlg.showModal(); bi().setAttribute('aria-expanded', 'true');
    bd.scrollTop = 0; bd.focus({ preventScroll: true });
  }
  document.addEventListener('click', e => {   // delegação: vale também para os botões regravados pelo reveal
    const b = e.target.closest?.('.v2b'); if (!b || b.disabled) return;
    b.classList.contains('i') ? abre() : play();
  });
  dlg.addEventListener('close', () => { const i = bi(); i?.setAttribute('aria-expanded', 'false'); i?.focus({ preventScroll: true }); });   // sempre: no Safari o foco fica preso no popup fechado
  $('.v2-x', dlg).addEventListener('click', () => dlg.close());
  dlg.addEventListener('click', e => {   // clique fora (no fundo escurecido) fecha
    if (e.target !== dlg) return;
    const r = dlg.getBoundingClientRect();
    if (e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom) dlg.close();
  });
  info.addEventListener('click', e => {   // termo técnico: abre a definição no próprio popup
    const g = e.target.closest('.gl'); if (!g) return;
    const [termo, df, ex] = GL[g.dataset.t];
    from = g; top = bd.scrollTop;
    $('h3', def).textContent = termo; $('.df', def).textContent = df;
    $('.ex', def).textContent = ex; $('.ex', def).hidden = !ex;
    view(true); bd.scrollTop = 0; $('.v2-back', def).focus();
  });
  $('.v2-back', def).addEventListener('click', () => { view(false); bd.scrollTop = top; from?.focus({ preventScroll: true }); });

  /* teclado: com o popup aberto, nenhuma tecla chega ao reveal nem ao deck (Esc fecha pelo próprio <dialog>; Tab, setas e Enter seguem o padrão do navegador).
     Enter/Espaço num botão da V2 também não viram "próximo slide". Em captura no window: chega antes dos ouvintes do deck (document, captura). */
  window.addEventListener('keydown', e => {
    if (dlg.open || ((e.key === 'Enter' || e.key === ' ') && e.target.closest?.('.v2b'))) e.stopPropagation();
  }, true);

  /* degradê no pé enquanto houver texto abaixo */
  const fade = () => { if (!dlg.open) return; dlg.style.setProperty('--v2sb', (bd.offsetWidth - bd.clientWidth) + 'px');
    dlg.classList.toggle('v2-more', bd.scrollHeight - bd.scrollTop - bd.clientHeight > 2); };
  bd.addEventListener('scroll', fade, { passive: true });
  window.addEventListener('resize', fade);
  if (window.ResizeObserver) { const ro = new ResizeObserver(fade); ro.observe(info); ro.observe(def); ro.observe(bd); }
  new MutationObserver(fade).observe(dlg, { attributes: true, attributeFilter: ['open'] });

  const go = () => { document.querySelectorAll('.slides aside.notes').forEach(a => a.remove()); update(); Reveal.on('slidechanged', update);
    lay(); Reveal.on('resize', relay); addEventListener('resize', relay); };
  Reveal.isReady?.() ? go() : Reveal.on('ready', go);   // antes do initialize, o reveal enfileira o on()
})();
</script>
"""


def main():
    global V1
    ap = argparse.ArgumentParser()
    ap.add_argument("--info", default=str(HERE / "info"), help="pasta com <id>.html do popup")
    ap.add_argument("--out", default=str(ROOT / "08-slides-v2"))
    ap.add_argument("--audio-ext", help="força a extensão do áudio (padrão: a que existir em <saída>/audio)")
    ap.add_argument("--base", default=str(V1 / "index.html"), help="HTML da V1 (padrão: a V1 congelada; revisão: 07-slides/index.html)")
    a = ap.parse_args()
    V1 = Path(a.base).resolve().parent
    out, info_dir = Path(a.out), Path(a.info)

    src = (V1 / "index.html").read_text(encoding="utf8")
    slides = slides_of(src)
    ids = [s["id"] for s in slides]
    assert len(ids) == len(set(ids)) and all(ids), "ids de slide vazios ou repetidos na V1"
    tit = {s["id"]: s.pop("_titulo_popup") for s in slides}
    tit = {k: v for k, v in tit.items() if v}
    (HERE / "slides.json").write_text(json.dumps(slides, ensure_ascii=False, indent=1) + "\n", encoding="utf8")

    # 1) notas e plugin de notas fora
    h, n = re.subn(r'<aside class="notes">.*?</aside>', "", src, flags=re.S)
    assert n == len(slides), f"{n} notas para {len(slides)} slides"
    for old, new in [('<script src="lib/plugin/notes/notes.js"></script>\n', ""), ("plugins: [RevealNotes]", "plugins: [PreserveSlideNodes]")]:
        assert h.count(old) == 1, f"trecho da V1 não encontrado (a V1 mudou?): {old!r}"
        h = h.replace(old, new)

    # 2) conteúdo
    gl, avisos = glossario(), []
    infos = {}
    for i in ids:
        p = info_dir / f"{i}.html"
        if p.exists():
            infos[i] = info_html(p, gl, avisos)
    sobra = sorted(p.stem for p in info_dir.glob("*.html") if p.stem not in ids) if info_dir.exists() else []
    aud_dir = out / "audio"
    aud_dir.mkdir(parents=True, exist_ok=True)
    exts = [a.audio_ext.lstrip(".")] if a.audio_ext else EXTS
    aud = {}
    for i in ids:
        f = next((aud_dir / f"{i}.{e}" for e in exts if (aud_dir / f"{i}.{e}").exists()), None)
        if f:
            aud[i] = f"audio/{f.name}"
    usados = {t for v in infos.values() for t in re.findall(r'class="gl" data-t="([^"]+)"', v)}

    # 3) injeção: CSS no <head>, botões no palco (logo depois do cromo), popup/dados/JS no fim do <body>
    chrome_end = h.index("</a></div>", h.index('<div class="chrome">')) + len("</a></div>")   # o cromo termina no atalho do sumário
    h = h[:chrome_end] + CTL + h[chrome_end:]
    h = h.replace("</head>", CSS + "<script>\n" + (HERE / "preserve-slide-nodes.js").read_text(encoding="utf8") + "\n</script></head>", 1)
    tpls = "".join(f'<template id="v2i-{i}">{infos[i]}</template>\n' for i in ids if i in infos)
    data = (f'<script type="application/json" id="v2-aud">{js_json(aud)}</script>\n'
            f'<script type="application/json" id="v2-tit">{js_json(tit)}</script>\n'
            f'<script type="application/json" id="v2-gl">{js_json({k: gl[k] for k in sorted(usados)})}</script>\n')
    h = h.replace("</body>", POP + "\n" + tpls + data + JS + "</body>", 1)
    assert "../" not in h, "a saída não pode ter caminhos ../ (o Safari bloqueia)"
    assert not re.search(r'(?:src|href)="(?:https?:)?//', h), "a saída não pode depender de rede"

    # 4) saída
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(h, encoding="utf8")
    for d in ("lib", "fonts"):
        shutil.copytree(V1 / d, out / d, dirs_exist_ok=True, copy_function=shutil.copyfile,
                        ignore=shutil.ignore_patterns("notes") if d == "lib" else None)
        for p in [out / d, *(out / d).rglob("*")]:   # a V1 é só leitura e o copytree copia a permissão das pastas: a saída precisa ser regravável
            p.chmod(p.stat().st_mode | 0o200)

    print(f"V2 em {out}/index.html | slides {len(ids)} | popup {len(infos)} | áudio {len(aud)} | termos usados {len(usados)}/{len(gl)}")
    if sobra:
        print("AVISO info/ sem slide correspondente:", ", ".join(sobra))
    for x in avisos:
        print("AVISO", x)


if __name__ == "__main__":
    main()
