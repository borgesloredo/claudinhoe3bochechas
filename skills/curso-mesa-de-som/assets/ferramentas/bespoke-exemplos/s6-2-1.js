/* 6.2.1 · Low cut / HPF (gráfico feito à mão do controlador hpf). Por trás da curva, o espectro do som em barras de 1/3 de oitava
   (ronco e vento no grave, a voz no meio). As barras passam pelo filtro: cada vez que o corte anda (entrada, cada linha da tabela, o "Método"),
   as barras abaixo da frequência de corte afundam no MESMO quadro em que a curva e o visor "Freq do corte" se movem (o render do hpf).
   Causa → efeito: o corte sobe → o grave some do espectro; o resto passa igual.
   Rodada 2 · fragment 1 (Benefícios): as barras abaixo do corte (ronco, vento, plosivas) voltam a subir sem filtro, piscam e afundam de novo;
   daí em diante ficam apagadas (o que o filtro tirou). */
(() => {
  const N = 30, F = i => 20 * 2 ** ((i + .5) / 3);   // centros de 1/3 de oitava, 20 Hz a 20 kHz
  const L = f => {   // nível de cada banda em dB (0 = topo do gráfico): ronco/vento no grave + a voz no meio + queda no agudo
    const lg = Math.log10(f);
    return Math.max(-7 - 5.5 * (lg - 2.75) ** 2 - (lg > 3.6 ? 7 * (lg - 3.6) : 0), -6.5 - 9 * (lg - 1.55) ** 2) + 1.5 * Math.sin(f * .37);
  };
  bespoke('s6-2-1', {
    init(x) {
      const c = inst.get(x.s), { X0, X1, Y0, YDB } = c, base = Y0 + 24 * YDB, w = (X1 - X0) / N;
      const g = mk('g', {}, null); x.svg.insertBefore(g, c.g.parentNode);   // atrás da curva e da área vermelha
      x.bars = []; x.lv = [];
      for (let i = 0; i < N; i++) {
        const f = F(i);
        x.bars.push(mk('rect', { x: (X0 + i * w + 2).toFixed(1), y: Y0, width: (w - 4).toFixed(1), height: 24 * YDB, rx: 1.5, fill: C.green, 'fill-opacity': .32 }, g));
        x.lv.push(L(f));
      }
      gsap.set(x.bars, { svgOrigin: (i, el) => `${el.getAttribute('x')} ${base}` });
      x.c = c; x.A = { a: 1 }; x.B = { v: 0, d: 0 }; x.F = F;
      x.h = i => {   // altura (0..1) da barra i com o filtro na posição atual: nível da banda + ganho da curva HPF nessa frequência
        const f = F(i), gdb = -10 * Math.log10(1 + (c.fc / f) ** 4);
        return Math.max(0, Math.min(1, (24 + x.lv[i] + gdb) / 24));
      };
      x.raw = i => Math.max(0, Math.min(1, (24 + x.lv[i]) / 24));   // a banda sem filtro
      x.draw = () => gsap.set(x.bars, { scaleY: i => (F(i) < c.fc ? x.h(i) + (x.raw(i) - x.h(i)) * x.B.v : x.h(i)) * x.A.a,
        opacity: i => F(i) < c.fc ? 1 - .55 * x.B.d : 1 });
      const r = c.render; c.render = function () { r.call(this); x.draw(); };   // o espectro anda no mesmo quadro que a curva e o visor
      x.draw();
    },
    enter(x, tl) {   // as barras sobem junto com a curva que se desenha (0,3–0,8 s); depois o corte sobe e o grave afunda
      x.k = 0; x.B.v = 0; x.B.d = 0; x.A.a = 0; x.draw();
      tl.to(x.A, { a: 1, duration: .5, ease: 'power2.out', onUpdate: x.draw }, .3);
    },
    step(x, k) {
      const prev = x.k ?? 0; x.k = k; if (k === prev) return;
      x.tl?.kill(); gsap.killTweensOf(x.B);
      Object.assign(x.B, { v: 0, d: k >= 1 ? 1 : 0 }); x.draw();
      if (RM || k !== 1 || prev !== 0) return;
      x.B.d = 0; x.draw();
      x.tl = gsap.timeline({ defaults: { onUpdate: x.draw } })   // o grave volta sem filtro, pisca e afunda
        .to(x.B, { v: 1, duration: .25, ease: 'power2.out' }, .1)
        .to(x.B, { d: 1, duration: .12, repeat: 3, yoyo: true, ease: 'none' }, .4)
        .to(x.B, { v: 0, duration: .5, ease: 'power1.in' }, .95).to(x.B, { d: 1, duration: .3 }, 1.0);
    },
    leave(x) { gsap.killTweensOf([x.A, x.B]); x.tl?.kill(); }
  });
})();
