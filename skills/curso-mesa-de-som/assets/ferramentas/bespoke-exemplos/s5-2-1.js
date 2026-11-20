/* 5.2.1 · A meta no medidor. A voz anima o medidor (sobe rápido, cai devagar); a média assenta em −18 e os picos tocam o amarelo (−12).
   Bullet 2: a faixa entre os picos e o teto de 0 dBFS acende como headroom; um pico estoura o 0, o LED CLIP acende e a onda achata; depois volta.
   Bullet 3 (rodada 2): canais iguais: A e B em −18 recebem o mesmo threshold de preset e os dois disparam o GR; C, em −30, não.
   Bullet 4 (rodada 2): ganho alto demais deixa a onda áspera (ruído do pré); de volta ao ganho moderado, o traço fica limpo. */
(() => {
  const Y = db => 34 + (-db) * 5, TOP = 34.2, H = 239.6;      // escala do medidor grande (mesma do SVG)
  const VOICE = [[-14, -27], [-12, -22], [-15, -25], [-13, -21], [-12, -24], [-14, -20], [-13, -23]];   // [pico, vale] de cada sílaba
  const fmt = d => Math.round(d) ? '−' + Math.abs(Math.round(d)) : '0';
  bespoke('s5-2-1', {
    init(x) {
      x.sh = $('.mtr .sh', x.svg); x.avg = $('.avg', x.svg); x.pkl = $('.pkl', x.svg); x.hr = $('.hr', x.svg);
      x.ra = $('[data-r="avg"]', x.svg); x.rp = $('[data-r="pk"]', x.svg);
      const q = c => $(c, x.svg), qq = c => $$(c, x.svg);
      Object.assign(x, { clip: q('.clipon'), clipt: q('.clipt'), wcl: q('.w-cl'), wct: q('.w-ct'), wnz: q('.w-nz'), pre: q('.pre'), pm: qq('.pm'), pth: q('.pth'), pgr: qq('.pgr') });
      gsap.set(x.sh, { transformOrigin: '50% 0%' }); gsap.set(x.hr, { transformOrigin: '50% 100%' });
      gsap.set(x.pm, { transformOrigin: '50% 100%' }); gsap.set(x.pgr, { transformOrigin: '50% 50%' });
      x.v = { l: -18, a: -18, p: -12 }; x.k = 0;
    },
    draw(x) {   // medidor, marcadores e números no mesmo tick
      const v = x.v;
      gsap.set(x.sh, { scaleY: Math.max(0, Math.min(1, (Y(v.l) - TOP) / H)) });
      gsap.set(x.avg, { y: Y(v.a) }); gsap.set(x.pkl, { y: Y(v.p) });
      x.ra.textContent = fmt(v.a); x.rp.textContent = fmt(v.p);
    },
    kill(x) { x.tl?.kill(); gsap.killTweensOf([x.v, x.hr, x.clip, x.clipt, x.wcl, x.wct, x.wnz, x.pre, ...x.pm, x.pth, ...x.pgr]); },
    PL: [-18, -18, -30],
    state(x, k) {
      Object.assign(x.v, { l: -18, a: -18, p: -12 }); this.draw(x);
      gsap.set(x.hr, { scaleY: 1 }); gsap.set(x.clip, { opacity: 0 }); x.clipt.style.fill = '';
      gsap.set(x.wcl, { opacity: 1 }); gsap.set([x.wct, x.wnz], { opacity: 0 });
      gsap.set(x.pre, { opacity: k >= 3 ? 1 : .2 }); gsap.set(x.pm, { scaleY: i => k >= 3 ? (262 - Y(this.PL[i])) / 222 : 0 });
      gsap.set(x.pth, { opacity: 1 }); gsap.set(x.pgr, { opacity: i => k >= 3 && i < 2 ? 1 : 0, scale: 1 });
    },
    enter(x, tl) {
      this.kill(x); this.state(x, 0); x.k = 0;
      x.v.l = -48; this.draw(x);
      tl.to(x.v, { l: -18, duration: .35, ease: 'power2.out', onUpdate: () => this.draw(x) }, .3);
    },
    step(x, k) {
      if (k === x.k) return;
      const prev = x.k; x.k = k; this.kill(x);
      if (RM || k !== prev + 1) return this.state(x, k);
      this.state(x, prev);
      const tl = x.tl = gsap.timeline({ onUpdate: () => this.draw(x) });
      if (k === 1) {
        Object.assign(x.v, { a: -27, p: -18 }); this.draw(x);
        let t = .1;
        VOICE.forEach(([pk, lo]) => {
          tl.to(x.v, { l: pk, duration: .07, ease: 'power2.out', onUpdate: () => { x.v.p = Math.max(x.v.p, x.v.l); } }, t)   // sobe rápido
            .to(x.v, { l: lo, duration: .42, ease: 'power1.in' }, t + .07);                                                   // cai devagar
          t += .5;
        });
        tl.to(x.v, { a: -18, duration: t - .1, ease: 'power2.out' }, .1)   // a média assenta no alvo
          .to(x.v, { l: -18, duration: .3, ease: 'power2.out' }, t);
      }
      if (k === 2) tl.fromTo(x.hr, { scaleY: 0 }, { scaleY: 1, duration: .6, ease: 'stage' }, .15);   // a folga até o teto acende
      if (k === 2) {   // um pico estoura o 0: CLIP acende e a onda achata; depois volta
        tl.to(x.v, { l: 2, duration: .07, ease: 'power2.out' }, .55)
          .set(x.clip, { opacity: 1 }, .6).call(() => { x.clipt.style.fill = '#160c02'; }, null, .6)
          .to(x.wcl, { opacity: 0, duration: .1 }, .6).to(x.wct, { opacity: 1, duration: .1 }, .6)
          .to(x.v, { l: -18, duration: .45, ease: 'power1.in' }, 1.25)
          .to(x.clip, { opacity: 0, duration: .2 }, 1.3).call(() => { x.clipt.style.fill = ''; }, null, 1.4)
          .to(x.wct, { opacity: 0, duration: .25 }, 1.35).to(x.wcl, { opacity: 1, duration: .25 }, 1.35);
      }
      if (k === 3) {   // mesmo nível, mesmo preset: A e B disparam juntos; C (−30) não
        tl.to(x.pre, { opacity: 1, duration: .3 }, 0)
          .fromTo(x.pm, { scaleY: 0 }, { scaleY: i => (262 - Y(this.PL[i])) / 222, duration: .35, ease: 'power2.out', stagger: .06 }, .2)
          .fromTo(x.pth, { opacity: 0 }, { opacity: 1, duration: .25 }, .55)
          .fromTo(x.pgr.slice(0, 2), { opacity: 0, scale: .3 }, { opacity: 1, scale: 1, duration: .3, ease: 'back.out(3)', stagger: .08 }, .8);
      }
      if (k === 4) {   // ganho alto: o pré fica áspero; ganho moderado: limpo
        tl.to(x.v, { l: -6, duration: .3, ease: 'power2.out' }, .2)
          .to(x.wcl, { opacity: 0, duration: .2 }, .3).to(x.wnz, { opacity: 1, duration: .2 }, .3)
          .to(x.v, { l: -18, duration: .5, ease: 'fader' }, 1.2)
          .to(x.wnz, { opacity: 0, duration: .3 }, 1.35).to(x.wcl, { opacity: 1, duration: .3 }, 1.35);
      }
    },
    leave(x) { this.kill(x); }
  });
})();
