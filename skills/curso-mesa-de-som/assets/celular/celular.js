/* === CELULAR: camada comum a todos os autoestudos (tools/celular/aplicar.py injeta entre os marcadores CELULAR) ===
   Telefone = toque + lado menor da tela < 600 px (tablet e computador não mudam).
   Deitado: o palco 16:9 ocupa a tela; deslizar e as setas seguem a ordem de leitura (como a barra de espaço).
   Em pé: aviso para girar; no Android, "Tela cheia" já trava na horizontal; "Ler em pé" mantém a rolagem do reveal.
   Botão "Índice" fixo: lista os capítulos (slides horizontais) e leva ao escolhido.
   iPhone: o Safari não deixa página entrar em tela cheia; "Tela cheia" ensina a pôr o curso na Tela de Início,
   que abre sem as barras do Safari (meta apple-mobile-web-app-capable). */
(() => {
  const S = [window.celScreen, window.screen].find((s) => s instanceof Screen) ?? null;   // celScreen: saved in <head> by aplicar.py, before Axios32, LS9 and Ui24R replace window.screen with a function
  const fone = matchMedia('(pointer: coarse)').matches && (S ? Math.min(S.width, S.height) : Math.min(innerWidth, innerHeight)) < 600;
  if (!fone) return;
  const html = document.documentElement, pe = matchMedia('(orientation: portrait)');
  html.classList.add('cel');
  try { if (sessionStorage.getItem('cel-empe')) html.classList.add('cel-empe'); } catch (e) {}

  // opened from the Home Screen icon: no Safari bars
  for (const [n, c] of [['apple-mobile-web-app-capable', 'yes'], ['mobile-web-app-capable', 'yes'], ['apple-mobile-web-app-status-bar-style', 'black-translucent'], ['apple-mobile-web-app-title', 'Curso']]) {
    if (!document.querySelector(`meta[name="${n}"]`)) document.head.append(Object.assign(document.createElement('meta'), { name: n, content: c }));
  }
  const ios = /iP(hone|od)/.test(navigator.userAgent);
  const app = navigator.standalone === true || matchMedia('(display-mode: standalone), (display-mode: fullscreen)').matches;
  const tela = !ios && document.fullscreenEnabled && S?.orientation && typeof S.orientation.lock === 'function';
  const podeTela = !app && (tela || ios);
  const telaCheia = () => {
    if (tela) return html.requestFullscreen({ navigationUI: 'hide' }).then(() => S.orientation.lock('landscape')).catch(() => {});   // recusa do aparelho: segue sem tela cheia
    ios_.hidden = false; ios_.querySelector('button').focus({ preventScroll: true });
  };

  const av = document.createElement('div');
  av.id = 'cel-gire'; av.setAttribute('role', 'dialog'); av.setAttribute('aria-modal', 'true'); av.setAttribute('aria-labelledby', 'cel-gire-t');
  av.innerHTML = `<svg viewBox="0 0 112 112" aria-hidden="true"><g class="cel-fone"><rect x="34" y="14" width="44" height="84" rx="8"/><path d="M50 86h12"/></g></svg>
    <div class="cel-k"></div><h2 id="cel-gire-t">Gire o celular</h2>
    <p>Na horizontal, cada tela do curso ocupa o celular inteiro e fica fácil de ler.</p>
    ${podeTela ? '<button type="button" class="cel-tela">Abrir em tela cheia</button>' : ''}
    ${tela ? '' : '<p class="cel-dica">Se a tela não girar, desligue o bloqueio de rotação na Central de Controle.</p>'}
    <button type="button" class="cel-empe-b">Ler em pé mesmo assim</button>`;
  av.querySelector('.cel-k').textContent = document.title;
  av.querySelector('.cel-tela')?.addEventListener('click', telaCheia);
  av.querySelector('.cel-empe-b').addEventListener('click', () => {
    html.classList.add('cel-empe');
    try { sessionStorage.setItem('cel-empe', '1'); } catch (e) {}
  });

  // iPhone: how to get the course without Safari bars
  const ios_ = document.createElement('div');
  ios_.id = 'cel-ios'; ios_.hidden = true; ios_.setAttribute('role', 'dialog'); ios_.setAttribute('aria-modal', 'true'); ios_.setAttribute('aria-labelledby', 'cel-ios-t');
  ios_.innerHTML = `<div class="cel-folha"><h2 id="cel-ios-t">Tela cheia no iPhone</h2>
    <p>O Safari não deixa página nenhuma ocupar a tela toda. Com o curso na Tela de Início, ele abre como um aplicativo, sem as barras:</p>
    <ol><li>Toque em <b>Compartilhar</b> <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3v12M7 8l5-5 5 5M5 12v8h14v-8"/></svg> na barra do Safari.</li>
    <li>Toque em <b>Adicionar à Tela de Início</b> e depois em <b>Adicionar</b>.</li>
    <li>Abra o curso pelo ícone novo, com o celular deitado.</li></ol>
    <button type="button">Entendi</button></div>`;
  ios_.querySelector('button').addEventListener('click', () => { ios_.hidden = true; });

  // chapter index: one line per horizontal slide, titled by its first heading
  const bt = document.createElement('button');
  bt.type = 'button'; bt.id = 'cel-ind-b'; bt.setAttribute('aria-haspopup', 'dialog'); bt.setAttribute('aria-label', 'Índice dos capítulos');
  bt.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 6h16M4 12h16M4 18h16"/></svg>';
  const ind = document.createElement('div');
  ind.id = 'cel-ind'; ind.hidden = true; ind.setAttribute('role', 'dialog'); ind.setAttribute('aria-modal', 'true'); ind.setAttribute('aria-labelledby', 'cel-ind-t');
  ind.innerHTML = `<nav class="cel-gaveta"><div class="cel-ind-hd"><h2 id="cel-ind-t">Índice</h2><button type="button" class="cel-x" aria-label="Fechar o índice">✕</button></div>
    <ol class="cel-lista"></ol>${podeTela ? '<button type="button" class="cel-tela2">Tela cheia</button>' : ''}</nav>`;
  const lista = ind.querySelector('.cel-lista');
  const titulo = (sec, i) => {
    const h = sec.querySelector('h1, h2, h3, [data-title]')?.cloneNode(true);
    h?.querySelectorAll('br, div, p').forEach((e) => e.after(' '));   // line breaks and SplitText lines: "Yamaha<br>01V96" -> "Yamaha 01V96"
    const t = (sec.dataset.title || h?.dataset?.title || h?.textContent || '').replace(/\s+/g, ' ').trim();
    return t ? (t.length > 80 ? t.slice(0, 78) + '…' : t) : `Tela ${i + 1}`;
  };
  const monta = () => {
    lista.textContent = '';
    // first slide of each chapter by Reveal's own indices: in scroll view (reading upright) the chapter sections are emptied
    const prim = new Map();
    for (const s of Reveal.getSlides()) { const { h } = Reveal.getIndices(s); if (Number.isInteger(h) && !prim.has(h)) prim.set(h, s); }
    prim.forEach((first, i) => {
      const li = document.createElement('li'), a = document.createElement('button');
      a.type = 'button'; a.dataset.h = i; a.textContent = titulo(first, i);
      a.addEventListener('click', () => { fecha(); Reveal.slide(i, 0); });
      li.append(a); lista.append(li);
    });
  };
  const abre = () => {
    if (!Reveal.isReady?.()) return;   // deck still loading
    if (!lista.childElementCount) monta();
    const atual = Reveal.getIndices().h;
    lista.querySelectorAll('button').forEach((b) => b.toggleAttribute('aria-current', +b.dataset.h === atual));
    ind.hidden = false;
    (lista.querySelector('[aria-current]') || lista.querySelector('button'))?.scrollIntoView({ block: 'center' });
    ind.querySelector('.cel-x').focus({ preventScroll: true });
  };
  const fecha = () => { ind.hidden = true; bt.focus({ preventScroll: true }); };
  bt.addEventListener('click', abre);
  ind.querySelector('.cel-x').addEventListener('click', fecha);
  ind.addEventListener('click', (e) => { if (e.target === ind) fecha(); });
  ind.querySelector('.cel-tela2')?.addEventListener('click', () => { fecha(); telaCheia(); });
  addEventListener('keydown', (e) => { if (e.key === 'Escape') { if (!ind.hidden) fecha(); ios_.hidden = true; } }, true);
  // keep swipes and keys inside the open panels from moving the deck
  for (const el of [ind, ios_]) for (const t of ['touchstart', 'touchmove', 'keydown']) el.addEventListener(t, (e) => e.stopPropagation());

  document.body.append(av, bt, ind, ios_);

  const orienta = () => { html.classList.toggle('cel-pe', pe.matches); if (pe.matches && !html.classList.contains('cel-empe')) av.querySelector('button')?.focus({ preventScroll: true }); };
  pe.addEventListener ? pe.addEventListener('change', orienta) : pe.addListener(orienta);
  orienta();

  // the deck's own (i)/▶ buttons change corner per slide (left in 01V96, right in Axios32): put ☰ in the first free corner
  const CANTOS = [[], ['cel-esq'], ['cel-baixo'], ['cel-esq', 'cel-baixo']];
  const perto = (a, b) => a.left < b.right + 6 && a.right > b.left - 6 && a.top < b.bottom + 6 && a.bottom > b.top - 6;
  const canto = () => {
    if (getComputedStyle(bt).display === 'none') return;
    // any visible control outside this layer (some decks put (i)/▶ outside .reveal); not .controls, which spans the whole screen
    const outros = [...document.querySelectorAll('button, a, [role="button"], .slide-number')].filter((e) => !e.closest('#cel-ind-b, #cel-ind, #cel-ios, #cel-gire'))
      .filter((e) => (e.checkVisibility ? e.checkVisibility({ opacityProperty: true, visibilityProperty: true }) : e.offsetParent))
      .map((e) => [e.matches('.slide-number, .slide-number *'), e.getBoundingClientRect()]).filter(([, r]) => r.width && r.height);
    // first pass: a corner free of everything; second: one that only covers the page counter (text, not a control)
    for (const so of [false, true]) {
      for (const c of CANTOS) {
        bt.classList.remove('cel-esq', 'cel-baixo'); bt.classList.add(...c);
        const r = bt.getBoundingClientRect();
        if (!outros.some(([num, o]) => !(so && num) && perto(r, o))) return;
      }
    }
    bt.classList.remove('cel-esq', 'cel-baixo');   // every corner holds a control: top right, as before
  };
  const vez = () => requestAnimationFrame(() => setTimeout(canto, 450));   // after the slide's own entrance animation places its buttons
  const linear = () => { Reveal.configure({ navigationMode: 'linear' }); vez(); };
  Reveal.isReady?.() ? linear() : Reveal.on('ready', linear);
  Reveal.on('slidechanged', vez);
  addEventListener('resize', vez);
  pe.addEventListener ? pe.addEventListener('change', vez) : pe.addListener(vez);
  bt.addEventListener('focus', canto);
})();
