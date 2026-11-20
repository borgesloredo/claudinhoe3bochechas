# Padrão de qualidade das LPs (XR18 = 100%)

Aprovado pelo Matheus em 05/11/2026. Toda LP nova, e toda LP refeita, segue este padrão de motion, gráficos, animação e acabamento. Só muda o estilo de botões, ícones e painéis, que imitam o hardware da mesa (ou do produto) daquela LP.

## Páginas de referência
- **Motion, estrutura e acabamento:** `/Users/SEU-USUARIO/SEU-PROJETO/curso-xr18/lp/index.html`, publicada em https://loredoborges.com.br/xr18/. É a régua do 100%.
- **O mesmo padrão aplicado a outra mesa:** `/Users/SEU-USUARIO/SEU-PROJETO/curso-01v96/lp/index.html`, aprovada em 05/11/2026 e publicada em https://loredoborges.com.br/01v96/. Use o script de motion dela como ponto de partida, porque ele já é genérico para mesas: `makeConsole`, `knobCtl`, `liveMeter`, `beats`/`onBeat`, `dock`. Troque os nomes das teclas, os modos e os valores técnicos pelos da mesa nova.
- Leia as duas antes de escrever código. Não copie textos nem fatos técnicos de uma mesa para outra: cada número vem do texto do curso novo.

## Hardware da mesa (o que muda de LP para LP)
- Antes do visual, documente em `docs/02-identidade.md` o hardware da mesa, tirado dos slides do curso, da edição interativa ou das fotos:
  - formato e cor das teclas e do LED de cada tecla;
  - cor do visor (LCD verde, tela colorida, OLED);
  - capas de fader e knobs;
  - plaquinhas de rótulo;
  - cores do medidor (verde, amarelo, vermelho, laranja);
  - nomes reais das teclas e dos modos.
- Botões da página = teclas da mesa, com LED que acende no hover e no foco e com 3 px de curso ao apertar. O CTA principal é a tecla de destaque da mesa.
- Ícones e marcadores = LEDs, plaquinhas e visores da própria mesa. Nunca use emoji nem ícones genéricos.
- A identidade de cor e de tipografia do produto continua mandando: o hardware é o "tempero", não substitui a paleta.

## Base técnica (igual em todas)
- GSAP 3.12.5 + ScrollTrigger + CustomEase do cdnjs, com `defer`. Registre duas eases:
  - `hw` = `M0,0 C0.2,0 0,1 1,1` (firme, como fader motorizado);
  - `flick` = `M0,0 L0.18,1 L0.32,0.2 L0.46,1 L1,1` (LED que pisca uma vez e fica aceso).
- Entradas usam `expo.out`. No HTML, anime só `transform` e `opacity` (e variáveis CSS como `--led-a`).
- O HTML estático é o estado final. Sem JS ou com `prefers-reduced-motion`, a página fica completa e os widgets mostram o resultado certo. O script de motion define cada estado inicial antes de animar.
- Classe `pre-anim` no `<html>` com failsafe de **300 ms**. O `window.LP_REDUCED` decide se a camada de motion roda.
- Helpers compartilhados: `rise()`, `riseDim()`, `once()`, `reveal()` com `ST.batch`, `tweenTo()`, `blink()`, `flick()`, `ledOn()`, `say()`, `knobCtl()`, `dock()`, `liveMeter()`.
  - `flick()` e `blink()` não podem receber lista vazia: o GSAP avisa "target not found".
  - `say()` muda a linha de estado de um widget (LED + texto). Ela só reescreve o texto quando ele muda, e escreve com `aria-live="off"` quando quem mudou foi a história, não o leitor.
- Um único loop (`gsap.ticker`) para todos os medidores. Cada medidor só roda enquanto o painel dele está na tela.
- Balística de medidor: ataque rápido, retorno lento (≈ 0,024 dB por ms), picos curtos. Nada de número aleatório pulando.
- Sem cabeçalho fixo do site no topo: o rodapé leva os links.

## Seções e o motion de cada uma
1. **Hero.**
   - Kicker, h1 com line-mask (`yPercent: 110`), depois sub, linha de compatibilidade, CTA e link com stagger.
   - À direita, o print principal do produto inclinado (`perspective(1600px) rotateY(-20deg) rotateX(5deg)`) entra com `x: 56`. A capa do produto, embaixo à esquerda por cima do print, sobe com `y: 110` (`power2.inOut`).
   - Abaixo, um widget da mesa que o leitor mexe, por exemplo GAIN com LEDs SIGNAL/PEAK e medidor.
   - O widget "liga" com teste de lâmpadas: LEDs piscam, o medidor varre a escala, o knob gira até a posição. No desktop isso faz parte da timeline do hero. No celular, acontece quando o widget entra na tela.
2. **Cena de abertura (o domingo que deu errado).**
   - Uma frase por beat, nunca a menos de 0,42 s uma da outra.
   - Um pedaço vivo da mesa ao lado segue a história pelos ganchos `onBeat`: modos, solo, faders motorizados, medidor do PA e da via, e as pegadinhas reais do curso.
   - Teclas citadas no texto (`.k`) "afundam" quando a frase chega.
   - No último beat, a mesa destrava e pede ao leitor a correção (ex.: apertar HOME).
   - Se ele sair sem corrigir, a mesa aparece corrigida na volta, nunca enquanto ele olha.
   - Depois da correção, os ganchos da história param, porque rolagem rápida dispara ganchos atrasados.
   - No celular, a mesa vai para logo abaixo do beat que ela responde (`dock`), com um link de volta.
3. **Virada.** O h2 entra com line-mask. Na tabela antes/depois, o LED vermelho pisca e então a solução entra deslizando, com o LED verde. A tecla da regra é apertada uma vez.
4. **Por dentro.**
   - Caminho do sinal com visor e onda. O ponto sai de IN e acende o LED de cada bloco que cruza. O visor mostra o texto do bloco e o que ele faz com o canal: a onda muda bloco a bloco. No bloco fader, um fader escala a saída e o envio pré-fader fica tracejado.
   - Teclas 1–9 e 0 selecionam os blocos.
   - Ao lado, uma segunda demonstração do curso (ex.: gate com threshold arrastável e fader TH, faixa real da mesa) e o quiz:
     - errar balança a opção;
     - acertar dá um "pop";
     - o visor pisca com o veredito.
   - Abaixo, os prints em 2 colunas.
5. **Percurso.**
   - Timeline com trilho de LED e capa de fader que descem com a rolagem (scrub). Ao abrir uma parte, as linhas dos capítulos se acomodam.
   - Dentro de uma parte, um widget de EQ ou de outro capítulo, com knob de frequência nos passos reais da mesa, varredura ao entrar e tecla liga/desliga.
   - Na lateral sticky, o roteiro de show do curso, lido por um cursor que acende cada tecla, mais o contador no visor.
   - Toda coluna lateral sticky precisa de `align-self: start`.
6. **O que vem / para quem / autor.** Reveals em lote. Os LEDs da lista "para quem é" acendem um a um. Plaquinhas com os modelos cobertos.
7. **Oferta.**
   - Caixa de preço sticky, com o preço num visor que pisca ao chegar.
   - Selo de garantia com persiana que abre.
   - Âncoras numéricas em visores pequenos que contam até o número.
8. **FAQ.** Reveals em lote.
9. **Final (o domingo seguinte).** A mesma mesa da cena, agora operada do jeito certo, pelos mesmos ganchos de beat. Depois, o fechamento com line-mask e o CTA.
- **Em toda a página:**
  - Todo h2 usa line-mask.
  - Trilho de leitura na lateral, feito de LEDs do medidor da mesa, com os do topo na cor de pico. Aparece só no desktop.
  - Névoa de palco à deriva (16 s e 21 s, yoyo), só no desktop.
  - CTA fixo no celular. Ele some enquanto a cena, a oferta, o final ou um CTA da página estão na tela.

## Fidelidade
- Todo valor técnico de widget vem do texto do curso, com capítulo e página num comentário. Exemplos: faixa de threshold, passos de frequência, nomes de modos, ordem do roteiro.
- Widget simulado leva a frase "Simulação" ou "Visor simulado para esta página".
- Teto e piso reais da mesa: ex.: o EQ vai até 20 kHz, não 20,5 kHz.

## Testes que pegaram erros na 01V96
- **Zoom do navegador:** o Chrome do Matheus fica com 67% de zoom, e aí `innerWidth` não bate com o viewport emulado. Confira `innerWidth`. Se vier 2160 em vez de 1440, emule 960×600 para ter 1440×900 em CSS. Abra a prévia numa aba de contexto isolado (`new_page` com `isolatedContext`).
- **Overflow:** com `body { overflow-x: clip }`, o `scrollWidth` não denuncia nada. Procure elementos cujo `getBoundingClientRect().right` passe da largura da tela.
- **Rolagem rápida:** role a página inteira em passos de 400 px a cada 150 ms e confira se o estado final da cena e do final faz sentido.
- **Avisos do GSAP:** intercepte `console.warn` com o `initScript` do `navigate_page` e role a página inteira. Zero avisos.
- Clique em cada widget no celular (390×844, mobile, touch) e no desktop (1440×900). Repita com `prefersReducedMotion: reduce`: nada pode ficar com opacidade abaixo de 0,5.
- **Lado a lado:** abra a LP da XR18 e compare seção por seção. Se uma seção da LP nova tem menos motion ou menos acabamento que a equivalente da XR18, ela não está pronta.
