/* cap-5 · Abertura "Sinal, fonte e ganho". O sinal entra fraco, passa pelo GANHO e sai no alvo:
   a onda de entrada se desenha, o ponto leva o sinal até o botão, o botão gira e, no MESMO tick, a onda de saída cresce e o medidor sobe até −18. */
bespoke('cap-5', {
  init(x) {
    const q = c => $(c, x.svg);
    Object.assign(x, { win: q('.win'), wout: q('.wout'), knob: q('.knob'), sh: q('.sh'), tgt: q('.tgt'), tl: q('.tl'), dot: q('.dot') });
    gsap.set(x.sh, { transformOrigin: '50% 0%' }); gsap.set(x.wout, { transformOrigin: '50% 50%' });
    x.v = { g: 0 };   // 0 = ganho baixo, 1 = no alvo
  },
  draw(x) {   // botão, onda de saída e medidor andam juntos (DESIGN.md 3.5)
    const g = x.v.g;
    gsap.set(x.knob, { rotation: -130 + 170 * g, svgOrigin: '149 48' });
    gsap.set(x.wout, { scaleY: .25 + .75 * g });
    gsap.set(x.sh, { scaleY: 1 - .62 * g });   // 1 = medidor apagado; .38 = nível em −18
  },
  enter(x, tl) {
    x.v.g = 0; this.draw(x); gsap.set(x.dot, { autoAlpha: 0 });   // README 7.3: o pulso só aparece já no trajeto
    tl.fromTo(x.svg, { autoAlpha: .4, x: 24 }, { autoAlpha: 1, x: 0, duration: .6 }, 0)
      .fromTo(x.win, { drawSVG: '0%' }, { drawSVG: '100%', duration: .6, ease: 'power2.inOut' }, .15)
      .to(x.dot, { motionPath: { path: x.win, align: x.win, alignOrigin: [.5, .5] }, duration: .6, ease: 'power1.in' }, .45)
      .set(x.dot, { autoAlpha: 1 }, .47)
      .to(x.dot, { autoAlpha: 0, duration: .15 }, 1.05)
      .to(x.v, { g: 1, duration: .9, ease: 'fader', onUpdate: () => this.draw(x) }, .95)
      .fromTo(x.wout, { drawSVG: '0%' }, { drawSVG: '100%', duration: .7, ease: 'power2.out' }, .95)
      .fromTo(x.tgt, { drawSVG: '0%' }, { drawSVG: '100%', duration: .35, ease: 'power2.out' }, 1.6)
      .fromTo(x.tl, { autoAlpha: 0, x: -8 }, { autoAlpha: 1, x: 0, duration: .35 }, 1.7);
  }
});
