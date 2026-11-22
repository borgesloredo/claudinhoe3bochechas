// Motor comum: animação por tela, quiz, explicação e áudio.
window.EBOOK = (() => {
  const D = window.EB_DADOS, receitas = {}, linhas = {};
  const reduzido = matchMedia('(prefers-reduced-motion: reduce)');
  const el = id => document.getElementById(id);
  let atual = null;

  function linha(s) {
    if (linhas[s.id]) return linhas[s.id];
    const tl = gsap.timeline({ paused: true });
    receitas[s.id]?.({ el: s, gsap, tl, $: q => s.querySelector(q), $$: q => [...s.querySelectorAll(q)] });
    return (linhas[s.id] = tl);
  }
  function animar(s) {
    const tl = linha(s);
    if (reduzido.matches) tl.progress(1).pause(); else tl.restart();
  }
  function zerar(s) {
    s.querySelectorAll('[data-quiz]').forEach(q => {
      delete q.dataset.resposta;
      q.querySelectorAll('.escolhida').forEach(b => b.classList.remove('escolhida'));
    });
    document.activeElement?.blur();
  }
  function parar() {
    const a = el('eb-audio');
    if (!a) return;
    a.pause();
    el('eb-play').textContent = '▶';
  }
  function entrar(s) {
    if (atual) linhas[atual.id]?.pause();
    parar();
    el('eb-pop')?.close();
    atual = s;
    el('eb-num').textContent = `${Reveal.getSlides().indexOf(s) + 1} / ${Reveal.getTotalSlides()}`;
    if (D.modo === 'autoestudo') {
      const a = el('eb-audio'), src = D.audios[s.id];
      if (src) a.src = src; else a.removeAttribute('src');
      el('eb-play').disabled = !src;
    }
    animar(s);
  }
  function autoestudo() {
    const pop = el('eb-pop'), a = el('eb-audio'), play = el('eb-play');
    el('eb-i').onclick = () => {
      pop.querySelector('.eb-texto').replaceChildren(el(`eb-info-${atual.id}`).content.cloneNode(true));
      pop.querySelector('.eb-def').textContent = '';
      pop.showModal();
      pop.scrollTop = 0;
    };
    pop.addEventListener('click', e => {
      if (e.target === pop || e.target.closest('.eb-x')) pop.close();
      const termo = e.target.closest('.gl'), g = termo && D.glossario[termo.dataset.t];
      if (g) pop.querySelector('.eb-def').textContent = `${g.termo}: ${g.definicao}`;
    });
    pop.addEventListener('close', () => el('eb-i').focus({ preventScroll: true }));
    play.onclick = () => {
      if (a.paused) a.play().then(() => { play.textContent = 'Ⅱ'; }, parar); else parar();
    };
    a.onended = parar;
  }
  function iniciar() {
    gsap.registerPlugin(SplitText, DrawSVGPlugin, MotionPathPlugin, CustomEase);
    document.addEventListener('click', e => {
      const b = e.target.closest('[data-quiz] button');
      if (!b) return;
      const q = b.closest('[data-quiz]');
      q.querySelectorAll('button').forEach(x => x.classList.toggle('escolhida', x === b));
      q.dataset.resposta = b.hasAttribute('data-certa') ? 'certa' : 'errada';
    });
    // o Reveal escuta no document: teclas de botão e de janela param antes de virar navegação
    document.body.addEventListener('keydown', e => {
      if (el('eb-pop')?.open || (e.target.closest('button') && (e.key === ' ' || e.key === 'Enter'))) e.stopPropagation();
    });
    if (D.modo === 'autoestudo') autoestudo();
    Reveal.on('slidechanged', e => entrar(e.currentSlide));
    Reveal.initialize({
      width: 1280, height: 720, margin: 0, center: false, transition: 'none', backgroundTransition: 'none',
      hash: true, respondToHashChanges: true, controls: true, progress: true, scrollActivationWidth: 0,
      plugins: D.modo === 'aula' ? [RevealNotes] : [],
    }).then(() => {
      Reveal.addKeyBinding({ keyCode: 82, key: 'R', description: 'Refazer a tela' }, () => { zerar(atual); animar(atual); });
      entrar(Reveal.getCurrentSlide());
    });
  }
  // para a conferência: leva a uma tela e congela num ponto exato da animação
  function quadro(id, p) {
    const s = el(id), { h, v } = Reveal.getIndices(s);
    if (atual !== s) Reveal.slide(h, v);
    const tl = linha(s);
    tl.progress(p).pause();
    const passos = tl.getChildren(true, true, false);
    const META = new Set('duration delay ease stagger repeat yoyo onStart onUpdate onComplete immediateRender runBackwards startAt overwrite parent stagger id lazy paused inherit data defaults transformOrigin isFromStart'.split(' '));
    const props = passos.flatMap(t => Object.keys({ ...t.vars, ...t.vars.startAt })).filter(k => !META.has(k));
    return {
      passos: passos.length, duracao: tl.totalDuration(),
      semAlvo: passos.filter(t => !t.targets().length).length,
      soOpacidade: props.every(k => k === 'opacity' || k === 'autoAlpha'),
    };
  }
  return { anima: (id, fn) => { receitas[id] = fn; }, iniciar, quadro };
})();
