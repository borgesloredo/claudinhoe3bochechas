# Design dos slides: as 3 direções e o motion

## Skills de apoio (já vêm dentro da skill)
`assets/vendor-skills/` traz cópias de `frontend-slides` (zarazhangrui, MIT), `gsap-core`, `gsap-timeline`, `gsap-plugins`, `gsap-performance`, `gsap-utils` (GreenSock oficial, MIT) e `motion-design` (LottieFiles, MIT). O `scripts/setup.sh` instala em `~/.claude/skills/` as que faltarem. Agentes de design leem os SKILL.md delas antes de trabalhar. O script de deploy do frontend-slides (Vercel) foi deixado de fora de propósito: nada é publicado na internet.

## As 3 direções (Fase 2)
O padrão é gerar só a 2, Hardware da mesa, que o dono preferiu em quase todos os cursos. A 1 e a 3 só são geradas se ele reprovar.
Cada direção é aplicada aos MESMOS 6 slides de amostra tirados do conteúdo real: capa, abertura de capítulo, tópico com medidores (diagrama), tópico com tabela (ex.: HPF por instrumento), quiz e o caminho do sinal clicável. Os manuais de produção de referência (feitos na primeira execução e aprovados pelo revisor) estão em `assets/direcoes/opcao-N/DESIGN.md`, com a grade de prints em `contato.png`.

| N | Nome | Briefing |
|---|---|---|
| 1 | Palco escuro | Fundo escuro de palco/estúdio, acentos em cores de LED e medidores (verde/amarelo/vermelho), brilho sutil, show ao vivo. **Foi a escolhida na 1ª execução.** Ponto fraco a evitar desde o início: texto pequeno. |
| 2 | Hardware da mesa | Superfície física FIEL à mesa escolhida: cor do painel, display, disposição, serigrafia, LEDs e teclas reais, conferidos nas ilustrações do manual e em fotos. Nada de elementos de outra linha (ex.: scribble strips coloridas só se a mesa tiver). O diagrama parece a própria mesa. |
| 3 | Editorial bold | Claro, editorial e ousado (Swiss/poster): tipografia gigante, blocos de cor fortes por ato/capítulo, grid rígido, alto contraste. |

Adapte as três à identidade da mesa escolhida (cores de marca, formato da superfície), sem perder a separação entre elas. Cada opção sai numa pasta autocontida (`lib/` copiado dentro, sem `../`), com `index.html`, `DESIGN.md`, `shots/contato.png` e `motion.mp4` (gravação do playwright convertida para MP4: o QuickTime não abre WebM).

## Motion (vale para a V1 inteira)
- Motor: reveal.js + GSAP 3 locais (SplitText, DrawSVGPlugin, MotionPathPlugin, Flip, CustomEase são gratuitos).
- Contrato de animação sob medida por slide: `tools/bespoke/<id>.svg` + `tools/bespoke/<id>.js`, documentado em `assets/ferramentas/bespoke-README.md` (eventos de entrada, fragment mostrado/escondido, quiz respondido, reset, reduced-motion). Exemplos reais em `assets/ferramentas/bespoke-exemplos/` (ganho → medidor, HPF, compressor, abertura cap-5, quiz-5).
- Nível exigido: igual ao das amostras aprovadas — a animação demonstra o conceito, não decora. Ritmo ~2–2,5 s por passo; aberturas ~2 s; quizzes: caminho errado mostra a consequência e termina no mesmo estado de resposta.
- Estados idempotentes (avançar = voltar = pular). Sem "ponto piscando na origem" de MotionPath.
- Ponteiro de knob em SVG: **nunca** `tl.from(rotation)` com `svgOrigin`, porque o GSAP interpola a translação em linha reta e o ponteiro sai do knob no meio do giro (RIVAGE PM, 03/11/2026). Gire por proxy: `fromTo(o,{a:-135},{a:alvo,onUpdate:()=>el.setAttribute("transform",`rotate(${o.a} ${ox} ${oy})`)})`.

## Verificação visual
- Contact sheets de todos os slides (24 por imagem, estado final) + tiras de 4 quadros da animação por slide, lidas pelos revisores.
- `check_fonts.mjs` (menor fonte, corpo ≥ 28 px, nada vazando), `verify_slides.mjs` (offline, 0 erros JS, 0 requisições externas, toda seção com nota), `check_titles.mjs`, `check_cuts.py`, checador de notas que acusa repetição do slide.
