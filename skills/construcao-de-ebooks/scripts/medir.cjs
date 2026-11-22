// Roda dentro do navegador: mede o texto visível de uma tela ou página e devolve os defeitos.
module.exports = function medir({ id, corpo, rotulo, livres }) {
  const raiz = document.getElementById(id), R = raiz.getBoundingClientRect(), g = document.createRange();
  const defeitos = new Set(), itens = [];
  const cor = s => {
    const m = /^rgba?\(([^)]+)\)$/.exec(s || '');
    if (!m) return null;
    const [r, v, b, a = 1] = m[1].split(/[\s,/]+/).filter(Boolean).map(Number);
    return { rgb: [r, v, b], a };
  };
  const luz = c => c.map(x => x / 255).map(x => (x <= 0.03928 ? x / 12.92 : ((x + 0.055) / 1.055) ** 2.4)).reduce((s, x, i) => s + x * [0.2126, 0.7152, 0.0722][i], 0);
  const opacidade = e => { let o = 1; for (let x = e; x && x !== raiz; x = x.parentElement) o *= Number(getComputedStyle(x).opacity); return o; };
  const escala = e => {
    if (e instanceof SVGElement) { const m = e.getScreenCTM?.(); return m ? Math.hypot(m.c, m.d) : 1; }
    let k = 1;
    for (let x = e; x && x !== raiz; x = x.parentElement) {
      const t = getComputedStyle(x).transform;
      if (t && t !== 'none') { const m = new DOMMatrix(t); k *= Math.hypot(m.c, m.d); }
    }
    return k;
  };
  const bloco = e => {
    if (e instanceof SVGElement) return e.closest('text') || e;
    let x = e;
    while (x !== raiz && getComputedStyle(x).display.startsWith('inline') && x.tagName !== 'BUTTON') x = x.parentElement;
    return x;
  };
  // o que está pintado num elemento: fundo HTML ou preenchimento SVG
  const pintura = x => {
    const s = getComputedStyle(x);
    if (x instanceof SVGElement) {
      if (['svg', 'g', 'text', 'tspan'].includes(x.tagName) || s.fill === 'none') return null;
      const c = cor(s.fill);
      if (!c) return 'imagem';
      return c.a * Number(s.fillOpacity) * opacidade(x) > 0.9 ? c.rgb : null;
    }
    if (s.backgroundImage !== 'none') return 'imagem';
    const c = cor(s.backgroundColor);
    return c && c.a * opacidade(x) > 0.9 ? c.rgb : null;
  };

  const w = document.createTreeWalker(raiz, NodeFilter.SHOW_TEXT);
  for (let n; (n = w.nextNode());) {
    const e = n.parentElement, txt = n.textContent.trim();
    if (!txt || e.closest('aside, style, title, desc, .folio') || getComputedStyle(e).visibility === 'hidden' || opacidade(e) < 0.1) continue;
    g.selectNodeContents(n);
    const rs = [...g.getClientRects()].filter(r => r.width > 1 && r.height > 1);
    if (!rs.length) { if (getComputedStyle(e).display !== 'none' && escala(e) < 0.05) defeitos.add(`texto reduzido a nada: "${txt.slice(0, 30)}"`); continue; }
    const b = bloco(e), curto = txt.slice(0, 35), s = getComputedStyle(e);
    const px = parseFloat(s.fontSize) * escala(e);
    const ehCorpo = !(e instanceof SVGElement) && b.textContent.trim().split(/\s+/).length > 6;
    const min = ehCorpo ? corpo : rotulo;
    if (px < min - 0.5) defeitos.add(`letra de ${px.toFixed(0)} px em "${curto}" (mínimo ${min})`);

    for (const r of rs) {
      itens.push({ b, r, curto });
      if (r.left < R.left - 1 || r.top < R.top - 1 || r.right > R.right + 1 || r.bottom > R.bottom + 1) { defeitos.add(`texto cortado: "${curto}"`); continue; }
      for (const l of livres) {
        if (r.right - R.left > l.x0 && r.left - R.left < l.x1 && r.bottom - R.top > l.y0 && r.top - R.top < l.y1) defeitos.add(`texto sob ${l.nome}: "${curto}"`);
      }
      if (e instanceof SVGElement) continue;
      for (let x = e; x && x !== raiz; x = x.parentElement) {
        const o = getComputedStyle(x);
        if (o.overflow === 'visible' || o.display === 'inline') continue;
        const c = x.getBoundingClientRect();
        if (r.bottom > c.bottom + r.height / 3 || r.top < c.top - r.height / 3 || r.right > c.right + 4 || r.left < c.left - 4) defeitos.add(`texto cortado por caixa: "${curto}"`);
      }
    }

    const r = rs[0], pilha = document.elementsFromPoint(r.left + r.width / 2, r.top + r.height / 2);
    const k = pilha.findIndex(x => x === e || e.contains(x));
    if (k < 0) continue;
    for (const x of pilha.slice(0, k)) {
      if (raiz.contains(x) && !x.contains(e) && !e.contains(x) && pintura(x)) { defeitos.add(`texto coberto: "${curto}"`); break; }
    }
    const frente = cor(e instanceof SVGElement ? s.fill : s.color);
    let fundo = null;
    for (const x of pilha.slice(k)) {
      if (x instanceof SVGElement && (x === e || e.contains(x))) continue;
      if ((fundo = pintura(x))) break;
    }
    if (frente && Array.isArray(fundo)) {
      const [a, c] = [luz(frente.rgb), luz(fundo)].sort((m, n) => n - m);
      if ((a + 0.05) / (c + 0.05) < (px >= corpo * 1.3 || px >= 24 ? 3 : 4.5)) defeitos.add(`contraste baixo: "${curto}"`);
    }
  }
  // sobreposição entre blocos diferentes; desconta a folga da entrelinha
  for (let i = 0; i < itens.length; i++) for (let j = i + 1; j < itens.length; j++) {
    const A = itens[i], B = itens[j];
    if (A.b === B.b || A.b.contains(B.b) || B.b.contains(A.b)) continue;
    const x = Math.min(A.r.right, B.r.right) - Math.max(A.r.left, B.r.left);
    const y = Math.min(A.r.bottom - A.r.height * 0.22, B.r.bottom - B.r.height * 0.22) - Math.max(A.r.top + A.r.height * 0.22, B.r.top + B.r.height * 0.22);
    if (x > 4 && y > 1) defeitos.add(`texto sobre texto: "${A.curto}" e "${B.curto}"`);
  }
  return [...defeitos];
};
