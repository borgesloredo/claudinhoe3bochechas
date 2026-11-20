// Só para deck com o contador do Reveal (slideNumber 'c/t'), sem faixa reservada. Chame contadorLivre(slide) em slidechanged, depois da animação de entrada, e uma vez no ready.
// contador foge do texto: fica no primeiro canto sem letra da tela (folga: o número ainda é o da tela anterior ao medir)
const CANTOS = ['left:14px;bottom:10px', 'left:14px;top:10px', 'left:50%;bottom:10px', 'left:50%;top:10px', 'left:320px;top:8px', 'right:60px;top:10px', 'right:130px;bottom:10px'];
function contadorLivre(s) {
  const n = document.querySelector('.reveal .slide-number'); if (!n || !s) return;
  const g = document.createRange(), txt = [], w = document.createTreeWalker(s, NodeFilter.SHOW_TEXT);
  for (let t; (t = w.nextNode());) { if (!t.textContent.trim() || t.parentElement.closest('aside,script,style')) continue; g.selectNodeContents(t); txt.push(...g.getClientRects()); }
  for (const c of CANTOS) { n.style.cssText = 'right:auto;bottom:auto;' + c; const q = n.getBoundingClientRect(); if (!txt.some(t => t.width && t.left < q.right + 12 && q.left - 12 < t.right && t.top < q.bottom && q.top < t.bottom)) return; }
  n.style.cssText = '';
}
