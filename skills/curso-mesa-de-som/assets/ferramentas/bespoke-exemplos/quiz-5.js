/* quiz-5 · "Qual é a meta para o ganho de entrada?"
   PERGUNTA: a voz toca com o ganho baixo (média −36); alvo, folga e teto apagados.
   RESPOSTA: (errou: o ganho sobe demais, o medidor bate em 0 e o CLIP acende) → a linha do alvo se desenha → o ganho gira até a média assentar em −18
   (a voz pica em −12/−8) → a folga até o teto acende. Medidor, marcadores e visores mudam no mesmo onUpdate (DESIGN.md 3.5). */
(() => {
  const Y = db => 40 + (-db) * 6.5, TOP = 39, H = 315, G0 = 20, GOK = 38;   // média = ganho − 56
  const VOICE = [[6, -9], [8, -4], [5, -7], [7, -3], [6, -8]];   // [pico, vale] de cada sílaba, em dB acima/abaixo da média
  const fmt = d => Math.round(d) ? '−' + Math.abs(Math.round(d)) : '0';
  const syl = (tl, v, t, onUpdate) => { VOICE.forEach(([pk, lo]) => { tl.to(v, { o: pk, duration: .07, ease: 'power2.out', onUpdate }, t).to(v, { o: lo, duration: .4, ease: 'power1.in', onUpdate }, t + .07); t += .48; }); return t; };   // sobe rápido, cai devagar
  bespoke('quiz-5', {
    init(x) {
      const q = c => $(c, x.svg);
      Object.assign(x, { sh: q('.sh'), avg: q('.avg'), pkl: q('.pkl'), hr: q('.hr'), hrt: q('.hrt'), clip: q('.clip'), tgt: q('.tgt'), tq: q('.tq'), ta: q('.ta'), knob: q('.knob'),
        ra: q('[data-r="avg"]'), rp: q('[data-r="pk"]'), rg: q('[data-r="g"]'), red: q('.mtr .zr') });
      gsap.set(x.sh, { transformOrigin: '50% 0%' });
      x.v = { g: G0, o: 0, p: -48 };
    },
    draw(x) {
      const v = x.v, cl = d => Math.max(-48, Math.min(0, d)), base = cl(v.g - 56), l = cl(v.g - 56 + v.o);   // o medidor não passa do teto
      v.p = Math.max(v.p, l);
      gsap.set(x.sh, { scaleY: (Y(l) - TOP) / H });
      gsap.set(x.avg, { y: Y(base) }); gsap.set(x.pkl, { y: Y(v.p) });
      gsap.set(x.knob, { rotation: -140 + 280 * (v.g - 10) / 50, svgOrigin: '176 317' });
      x.ra.textContent = fmt(base); x.rp.textContent = fmt(v.p); x.rg.textContent = '+' + Math.round(v.g) + ' dB';
    },
    kill(x) { x.xtl?.kill(); x.xtl = null; gsap.killTweensOf([x.v, x.hr, x.hrt, x.clip, x.tgt, x.tq, x.ta, x.red]); },
    ask(x) {   // estado PERGUNTA
      this.kill(x); Object.assign(x.v, { g: G0, o: -8, p: G0 - 56 + 8 }); this.draw(x);   // rodada 2: o pico fica no −28, o mesmo do fim da entrada (R não muda o visor)
      gsap.set(x.hr, { opacity: .2 }); gsap.set([x.hrt, x.clip, x.ta, x.tgt], { opacity: 0 }); gsap.set(x.tq, { opacity: 1 }); gsap.set(x.red, { opacity: 1 });
    },
    done(x) {   // estado RESPOSTA (final)
      this.kill(x); Object.assign(x.v, { g: GOK, o: 0, p: -12 }); this.draw(x);
      gsap.set([x.hr, x.hrt, x.ta], { opacity: 1 }); gsap.set(x.tgt, { opacity: 1, drawSVG: '100%' }); gsap.set([x.tq, x.clip], { opacity: 0 });
    },
    reset(x) { this.ask(x); },
    enter(x, tl) {
      this.ask(x); x.v.g = 0; x.v.p = -48; this.draw(x);
      tl.to(x.v, { g: G0, duration: .4, ease: 'power2.out', onUpdate: () => this.draw(x) }, .35);   // a voz chega fraca: o medidor mal passa do −36
      syl(tl, x.v, .75, () => this.draw(x));
    },
    answer(x, r) {
      if (RM) return this.done(x);
      this.kill(x);
      const v = x.v, tl = x.xtl = gsap.timeline({ onUpdate: () => this.draw(x) });
      let t = .1;
      if (!r.ok) {   // o que a alternativa errada faz: ganho demais, o medidor bate no teto e distorce
        tl.to(v, { g: 58, duration: .5, ease: 'fader' }, t)
          .to(x.hr, { opacity: 1, duration: .2 }, t + .45).to(x.clip, { opacity: 1, duration: .1 }, t + .5)
          .fromTo(x.red, { opacity: 1 }, { opacity: .25, duration: .1, repeat: 5, yoyo: true, ease: 'none' }, t + .5)
          .to(x.clip, { opacity: 0, duration: .2 }, t + 1.2).to(x.hr, { opacity: .2, duration: .2 }, t + 1.2)
          .to(v, { g: G0, duration: .4, ease: 'fader' }, t + 1.1)
          .add(() => { v.p = v.g - 56; }, t + 1.5);
        t += 1.6;
      }
      tl.to(x.tq, { opacity: 0, duration: .15 }, t)
        .set(x.tgt, { opacity: 1 }, t).fromTo(x.tgt, { drawSVG: '0%' }, { drawSVG: '100%', duration: .5, ease: 'power2.inOut' }, t)   // 1) a referência se desenha
        .fromTo(x.ta, { opacity: 0, x: 10 }, { opacity: 1, x: 0, duration: .3 }, t + .3)
        .to(v, { g: GOK, duration: 1.0, ease: 'fader' }, t + .5);                                                                      // 2) o ganho gira: a média sobe junto
      const t2 = syl(tl, v, t + 1.2);                                                                                                  // 3) a voz pica em −12/−8, abaixo do teto
      tl.to(x.hr, { opacity: 1, duration: .3 }, t + 1.6).fromTo(x.hrt, { opacity: 0, y: 8 }, { opacity: 1, y: 0, duration: .4 }, t + 1.7)   // 4) a folga acende
        .to(v, { o: 0, duration: .3 }, t2);
    },
    leave(x) { this.kill(x); }
  });
})();
