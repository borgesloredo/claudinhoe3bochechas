// vv.js — ajudantes GSAP aprovados nos vídeos de venda (XR18, WING, Axios, 01V96, Audiolab, DM3/DM7, HD96).
// O montar.py cola este arquivo no index.html. Uso dentro das cenas: V.words("#s3 .word", t0 + 0.1) etc.
// Tudo é seekável: só tweens/sets na timeline, sem timers, sem Math.random (use V.rng(semente)).
function VV(tl) {
  gsap.registerPlugin(CustomEase);
  CustomEase.create("hw", "0.2,0,0,1");            // tecla, LED, fader curto
  CustomEase.create("stage", "0.16,1,0.3,1");      // entrada de texto e de peça
  CustomEase.create("fader", "0.65,0,0.35,1");     // fader longo, câmera
  CustomEase.create("flick", "M0,0 L0.18,1 L0.32,0.2 L0.46,1 L1,1");  // acender com tremida
  const ft = (s, a, b, t) => tl.fromTo(s, a, { ...b, immediateRender: false }, t);
  const V = {
    ft,
    // texto: spans .word (o montar.py cria com data-palavras)
    words: (sel, t, st = 0.06, d = 0.3) => tl.fromTo(sel, { y: 30, opacity: 0 }, { y: 0, opacity: 1, duration: d, ease: "stage", stagger: st }, t),
    mask: (sel, t, d = 0.45, st = 0) => tl.fromTo(sel, { yPercent: 125 }, { yPercent: 0, duration: d, ease: "stage", stagger: st }, t),
    fadeIn: (sel, t, d = 0.15) => tl.fromTo(sel, { opacity: 0 }, { opacity: 1, duration: d, ease: "none" }, t),
    out: (sel, t, d = 0.12) => ft(sel, { opacity: 1 }, { opacity: 0, duration: d, ease: "power1.in" }, t),
    capOut: (sel, t) => ft(sel, { y: 0, opacity: 1 }, { y: -40, opacity: 0, duration: 0.15, ease: "power2.in" }, t),
    entra: (sel, t, d = 0.45, y = 60) => tl.fromTo(sel, { y, opacity: 0 }, { y: 0, opacity: 1, duration: d, ease: "stage" }, t),
    // hardware
    press: (sel, t, d = 4) => ft(sel, { y: 0 }, { y: d, duration: 0.045, yoyo: true, repeat: 1, ease: "hw" }, t),
    lit: (sel, t, v = 1, d = 0.06) => tl.to(sel, { opacity: v, duration: d, ease: "hw" }, t),
    flick: (sel, t, d = 0.35) => ft(sel, { opacity: 0 }, { opacity: 1, duration: d, ease: "flick" }, t),
    blink: (sel, t, lo = 0.3, d = 0.1, n = 1) => { for (let k = 0; k < n; k++) tl.to(sel, { opacity: lo, duration: d, ease: "steps(1)" }, t + 2 * d * k).to(sel, { opacity: 1, duration: d, ease: "steps(1)" }, t + 2 * d * k + d); },
    fader: (sel, t, y, d = 0.6) => tl.to(sel, { y, duration: d, ease: "fader" }, t),
    // medidor oscilando (escala Y de baixo para cima), repetição finita
    meter: (sel, t0, t1, lo = 0.35, hi = 0.85, per = 0.4) => { const n = Math.max(0, Math.floor((t1 - t0) / per) - 1); ft(sel, { scaleY: lo, transformOrigin: "50% 100%" }, { scaleY: hi, duration: per, ease: "sine.inOut", yoyo: true, repeat: n }, t0); },
    breathe: (sel, t0, t1, lo = 0.8) => { const n = Math.floor((t1 - t0) / 0.8); if (n > 0) tl.to(sel, { opacity: lo, duration: 0.4, ease: "sine.inOut", yoyo: true, repeat: n * 2 - 1 }, t0); },
    // contador: um set por quadro (seekável)
    count: (sel, a, b, t, d, ease = "power2.out", w = 0) => { const e = gsap.parseEase(ease), n = Math.max(2, Math.round(d * 30)); for (let k = 0; k <= n; k++) tl.set(sel, { innerText: String(Math.round(a + (b - a) * e(k / n))).padStart(w, "0") }, t + (d * k) / n); },
    // câmera: escala s mantendo o ponto (fx, fy) do quadro parado
    push: (sel, t, d, a = 1, b = 1.03) => ft(sel, { scale: a }, { scale: b, duration: d, ease: "none" }, t),
    zoom: (sel, t, d, s, fx = 540, fy = 960, ease = "fader") => tl.to(sel, { scale: s, x: (fx - 540) * (1 - s), y: (fy - 960) * (1 - s), duration: d, ease }, t),
    camSet: (sel, s, fx = 540, fy = 960, t = 0) => tl.set(sel, { transformOrigin: "540px 960px", scale: s, x: (fx - 540) * (1 - s), y: (fy - 960) * (1 - s) }, t),
    shake: (sel, t, a = 6, d = 0.3) => tl.to(sel, { keyframes: { x: [0, a, -a, a, -a, a / 2, 0] }, duration: d, ease: "none" }, t),
    tap: (sel, t, from = 0.4) => ft(sel, { opacity: 0.9, scale: from }, { opacity: 0, scale: 1.3, duration: 0.45, ease: "power2.out" }, t),
    // aleatório com semente (mulberry32)
    rng: (seed = 1) => () => { seed |= 0; seed = (seed + 0x6d2b79f5) | 0; let x = Math.imul(seed ^ (seed >>> 15), 1 | seed); x = (x + Math.imul(x ^ (x >>> 7), 61 | x)) ^ x; return ((x ^ (x >>> 14)) >>> 0) / 4294967296; },
  };
  return V;
}
