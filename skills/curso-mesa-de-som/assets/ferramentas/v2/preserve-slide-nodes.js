/* Conserva os nós para manter os controladores ativos ao sair da rolagem. */
// shortcut: contrato interno do Reveal 5.1.0; revisar ao atualizar a biblioteca.
const PreserveSlideNodes = {
  id: 'preserve-slide-nodes',
  init(deck) {
    const scroll = deck.scroll;
    if (deck.VERSION !== '5.1.0' || !scroll || typeof scroll.activate !== 'function' || typeof scroll.deactivate !== 'function') {
      throw new Error('PreserveSlideNodes exige o Reveal 5.1.0 auditado');
    }
    const activate = scroll.activate, syncPosition = scroll.syncScrollPosition, scrollToSlide = scroll.scrollToSlide;
    const setCurrentScrollPage = deck.setCurrentScrollPage;
    // Reveal 5.1 emite slidechanged até para o mesmo slide, reiniciando os exercícios.
    deck.setCurrentScrollPage = function (slide, h, v) {
      if (deck.getCurrentSlide() !== slide) return setCurrentScrollPage.call(this, slide, h, v);
    };
    let activating = false;
    scroll.syncScrollPosition = function () {
      if (!activating) return syncPosition.call(this);
    };
    scroll.scrollToSlide = function (slide) {
      if (!this.active) return scrollToSlide.call(this, slide);
      const trigger = this.getScrollTriggerBySlide(slide);
      if (!trigger?.page.pageElement) return scrollToSlide.call(this, slide);
      // No layout full destes cursos, a posição real evita cair no snap do slide anterior.
      this.viewportElement.scrollTop = trigger.page.pageElement.offsetTop;
    };
    let saved = null;
    scroll.activate = function (...args) {
      if (!this.active) {
        const root = deck.getSlidesElement();
        const sections = [...root.querySelectorAll('section')];
        saved = {
          root,
          children: [...root.childNodes],
          stacks: sections.filter(s => s.querySelector(':scope > section')).map(s => [s, [...s.childNodes]]),
          indices: sections.map(s => [s, s.getAttribute('data-index-h'), s.getAttribute('data-index-v')])
        };
      }
      const current = deck.isReady() ? deck.getCurrentSlide() : null;
      const state = current ? deck.getState() : null;
      let result;
      activating = true;
      try {
        result = activate.apply(this, args);
        if (current) {
          this.scrollToSlide(current);
          const page = this.getScrollTriggerBySlide(current)?.page;
          if (state.indexf >= 0 && page?.scrollTriggers.length > 1) {
            this.viewportElement.scrollTop += Math.min(state.indexf + 1, page.scrollTriggers.length - 1) * this.scrollTriggerHeight;
          }
        }
      } finally {
        activating = false;
      }
      if (this.active) this.syncScrollPosition();
      return result;
    };
    scroll.deactivate = function () {
      if (!this.active) return;
      if (!saved) throw new Error('Scroll ativado sem captura dos nós originais');
      const state = deck.getState(), tree = saved;
      this.active = false;
      this.viewportElement.removeEventListener('scroll', this.onScroll);
      this.viewportElement.classList.remove('reveal-scroll');
      this.removeProgressBar();
      // Mesma ordem de deactivate() em Reveal 5.1.0; troca somente a restauração do DOM.
      // Conserva cada section E todos os descendentes: controladores, SVG, listeners e estado.
      for (const [stack, children] of [...tree.stacks].reverse()) stack.replaceChildren(...children);
      tree.root.replaceChildren(...tree.children);
      for (const [s, h, v] of tree.indices) {
        for (const [name, value] of [['data-index-h', h], ['data-index-v', v]]) {
          if (value === null) s.removeAttribute(name); else s.setAttribute(name, value);
        }
      }
      this.slideHTMLBeforeActivation = null;
      saved = null;
      deck.sync();
      deck.setState(state);
    };
  }
};
