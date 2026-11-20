/* 8.1.1 · Compressor: como funciona (rodada 2: um acontecimento por bullet atual; o sidechain foi para o 8.2.4).
   Um só proxy x.p (entrada, ratio, Gain/makeup, Mix e o GR extra do detector) e um draw() que põe tudo no lugar:
   ponto na curva, trecho de cima da curva (gira no threshold: rotation + scaleX), grupo da curva (sobe com o Gain),
   medidores IN/OUT/GR e os visores, no mesmo onUpdate.
   Entrada: o ponto sobe de −48 até o threshold (−24): IN e OUT juntos, GR 0.
   B1: o ponto passa do threshold, −24 → −20: IN sobe 4 dB e OUT sobe 1 ("4 dB → 1 dB").
   B2: com a entrada em −8, o ratio gira 4 → 2 → 6 → 10:1; a curva deita e, em 10:1, aparece "limitador".
   B3: ratio de volta a 4:1: o OUT fica baixo; o Gain do compressor sobe +12 dB e o OUT volta; o GR não muda; o ganho de entrada fica parado.
   B4: o Gain volta a 0 e o Mix vai a 0%: a curva volta à reta 1:1, OUT = IN, mas o GR continua em −12 (o detector não sabe do Mix: o 'erro comum').
   B5: Mix de volta a 100%; a mesma entrada vista pelo detector Peak (o GR segue cada golpe) e pelo RMS (envoltória lenta). */
bespoke('s8-1-1', {
  T: -24,
  S: 230 / 48, X(db) { return 46 + (db + 48) * this.S; }, Y(db) { return 280 - (db + 48) * this.S; },
  ST: [{ in: -24, R: 4, M: 0, mix: 1 }, { in: -20, R: 4, M: 0, mix: 1 }, { in: -8, R: 10, M: 0, mix: 1 },
       { in: -8, R: 4, M: 12, mix: 1 }, { in: -8, R: 4, M: 0, mix: 0 }, { in: -8, R: 4, M: 0, mix: 1 }],
  init(x) {
    const q = c => $(c, x.svg), qq = c => $$(c, x.svg);
    Object.assign(x, { mi: q('.m-in'), mo: q('.m-out'), mg: q('.m-gr'), pt: q('.pt'), gap: q('.gap'), v: q('.gr-v'), vi: q('.v-in'), vo: q('.v-out'),
      cv: q('.cv'), up: q('.cv-up'), rt: q('.rt'), lim: q('.lim'), b1m: q('.b1m'), kn: qq('.kn-n'), kv: qq('.kn-v'), kn0: q('.kn'),
      det: q('.det'), dpk: q('.det-pk'), drm: q('.det-rm'), dl: qq('.det-l') });
    gsap.set([x.mi, x.mo], { transformOrigin: '50% 100%' }); gsap.set(x.mg, { transformOrigin: '50% 0%' }); gsap.set(x.gap, { transformOrigin: '50% 100%' });
    gsap.set(x.up, { svgOrigin: '161 165' }); gsap.set(x.kn[1], { svgOrigin: '96 356' }); gsap.set(x.kn[2], { svgOrigin: '186 356' });
    gsap.set(x.dl, { transformOrigin: '50% 50%' });
    x.p = { ...this.ST[0], kick: 0 }; x.k = 0;
    this.draw(x);
  },
  fmt(v) { const r = Math.round(v); return r < 0 ? `−${-r}` : r > 0 ? `+${r}` : '0'; },
  draw(x) {   // um só lugar desenha tudo
    const p = x.p, i = p.in, comp = i <= this.T ? i : this.T + (i - this.T) / p.R, gr = i - comp, o = i - gr * p.mix + p.M;   // GR = detector (antes da mistura); o Mix só vale para a saída
    const eff = 1 - p.mix * (1 - 1 / p.R), ang = -Math.atan(eff) * 180 / Math.PI;
    gsap.set(x.cv, { y: -p.M * this.S }); gsap.set(x.up, { rotation: ang, scaleX: Math.sqrt(1 + eff * eff) });
    gsap.set(x.pt, { x: this.X(i), y: this.Y(o) });
    gsap.set(x.gap, { scaleY: Math.max(.001, (i - o) * this.S / 100) });
    gsap.set(x.mi, { scaleY: (i + 48) / 48 }); gsap.set(x.mo, { scaleY: Math.min(1, Math.max(0, o + 48) / 48) }); gsap.set(x.mg, { scaleY: Math.max(.001, (gr + p.kick) / 48) });
    const g = Math.round(gr + p.kick); x.v.textContent = g ? `−${g} dB` : '0 dB';
    x.vi.textContent = this.fmt(i); x.vo.textContent = this.fmt(o);
    const R = Math.round(p.R);
    x.rt.textContent = `ratio ${R}:1`;
    gsap.set(x.lim, { opacity: p.R >= 9.5 ? 1 : 0 });
    gsap.set(x.kn[1], { rotation: p.M / 24 * 135 }); x.kv[0].textContent = `${this.fmt(p.M)} dB`;
    gsap.set(x.kn[2], { rotation: (p.mix * 2 - 1) * 135 }); x.kv[1].textContent = `${Math.round(p.mix * 100)}%`;
  },
  kill(x) { x.tl?.kill(); x.tl = null; gsap.killTweensOf([x.p, x.b1m, x.det, x.dpk, x.drm, ...x.dl]); },
  state(x, k) {
    this.kill(x); Object.assign(x.p, this.ST[k], { kick: 0 }); this.draw(x);
    gsap.set(x.b1m, { opacity: k === 1 ? 1 : 0, y: 0 });
    gsap.set(x.det, { opacity: k >= 5 ? 1 : .2 }); gsap.set([x.dpk, x.drm], { drawSVG: '100%' }); gsap.set(x.dl, { scale: 1 });
  },
  enter(x, tl) {
    this.state(x, 0); x.k = 0; x.p.in = -48; this.draw(x);
    tl.fromTo($$('.mt, .gr-box, .pt', x.svg), { opacity: .35 }, { opacity: 1, duration: .3 }, 0)
      .to(x.p, { in: this.T, duration: 1.3, ease: 'fader', onUpdate: () => this.draw(x) }, .35);   // abaixo do threshold: IN e OUT juntos
  },
  step(x, k) {
    const prev = x.k; if (k === prev) return; x.k = k;
    if (RM || k !== prev + 1 || k > 5) return this.state(x, Math.min(k, 5));
    this.state(x, prev);
    const tl = x.tl = gsap.timeline(), d = () => this.draw(x), to = (v, dur, at, ease = 'fader') => tl.to(x.p, { ...v, duration: dur, ease, onUpdate: d }, at);
    if (k === 1) { to({ in: -20 }, .8, .2); tl.fromTo(x.b1m, { opacity: 0, y: 8 }, { opacity: 1, y: 0, duration: .4 }, .7); }
    if (k === 2) {
      tl.to(x.b1m, { opacity: 0, duration: .2 }, 0);
      to({ in: -8 }, .5, .1); to({ R: 2 }, .35, .7); to({ R: 6 }, .45, 1.3); to({ R: 10 }, .45, 2.0);
    }
    if (k === 3) { to({ R: 4 }, .4, .1); to({ M: 12 }, .8, .9); }   // o OUT cai; o Gain do compressor devolve o nível (GR igual)
    if (k === 4) { to({ M: 0 }, .35, .1); to({ mix: 0 }, .8, .6); }   // Mix 0%: a curva volta à reta 1:1
    if (k === 5) {
      to({ mix: 1 }, .4, .1);
      tl.to(x.det, { opacity: 1, duration: .3 }, .3)
        .fromTo(x.dl[0], { scale: 1.3 }, { scale: 1, duration: .3, ease: 'back.out(3)' }, .5)
        .fromTo(x.dpk, { drawSVG: '0%' }, { drawSVG: '100%', duration: .6, ease: 'none' }, .55);
      for (let n = 0; n < 3; n++) { to({ kick: 6 }, .06, .6 + n * .2, 'power2.out'); to({ kick: 0 }, .13, .66 + n * .2, 'power1.in'); }   // Peak: o GR segue cada golpe
      tl.fromTo(x.dl[1], { scale: 1.3 }, { scale: 1, duration: .3, ease: 'back.out(3)' }, 1.3)
        .fromTo(x.drm, { drawSVG: '0%' }, { drawSVG: '100%', duration: .9, ease: 'none' }, 1.35);
      to({ kick: 3 }, .45, 1.35, 'sine.inOut'); to({ kick: 0 }, .45, 1.8, 'sine.inOut');   // RMS: envoltória lenta
    }
  },
  leave(x) { this.kill(x); }
});
