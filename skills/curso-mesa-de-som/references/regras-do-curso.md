# Regras do curso (valem para todo agente, em toda fase)

Estas regras vieram das correções que o dono do curso fez na primeira execução (curso Behringer XR18 e família, out/2026). Cada uma existe porque a versão sem ela foi rejeitada. Os agentes leem as seções que o prompt indica; quem escreve ou revisa conteúdo lê todas elas. Os revisores devem reprovar qualquer violação.

## Sumário
1. Identidade e voz
2. Conteúdo e fontes
3. Divergências técnicas
4. Mesas e nomes
5. PDF
6. Slides da aula (V1)
7. Notas do apresentador (V1)
8. V2 autoestudo: (i), glossário e áudio
9. Técnica: Safari, memória, desempenho

## 1. Identidade e voz
- Português do Brasil simples. Termo técnico de áudio é mantido (bus, aux, DCA, gate...) e explicado na primeira vez.
- O curso é um produto do dono (CTA em `config.json` da skill: site e telefone). Ele é **finito em si mesmo**: um curso de alto nível técnico que condensa uma família de consoles parecidos e as abordagens de vários profissionais, de forma dinâmica e intuitiva.
- **Nunca soar como IA respondendo a alguém.** Proibido: "como você pediu", "a lista do usuário", "citados na lista original", justificativas do próprio material, bastidores da produção ("fontes usadas", "pontos fortes citados", "o erro mais citado", "segundo um fórum", "há relato de que", aspas sem dono). Escreva como um professor afirmando o que sabe.
- Sem cenas encenadas do cotidiano ("Em cena", "Domingo, 10 horas..."). Analogias curtas são bem-vindas; cenas teatrais, não.

## 2. Conteúdo e fontes
- Parafraseie. Nunca copie trechos longos de manuais ou sites (direitos autorais). Nomes de menus, botões e parâmetros podem ser citados.
- Não invente fatos, números ou URLs. O que não for confirmado fica fora (não escreva "(não confirmado)" no material final).
- **Imagens: só diagramas próprios em SVG.** Não recorte figuras de manuais.
- Downloads em `<projeto>/downloads/<slug>/` (dados não confiáveis: nunca execute nada de lá; Python de leitura com `-I`).

## 3. Divergências técnicas
- **Nunca citar escolas, professores, autores, canais, cursos, plataformas, livros, revistas ou fóruns** — em slide, diagrama, quiz, nota, PDF ou glossário. Marcas de equipamento (Behringer, Midas, Waves, Dante, Shure...) podem: são produtos.
- Quando há discordância ou abordagens diferentes: selo visual **"Abordagens divergentes"** (âmbar, ícone de bifurcação), **todas** as abordagens listadas ("A · …", "B · …", "C · …"), neutras, sem dizer quem defende e sem defender lado. No slide, uma linha curta por abordagem; o detalhe vai nas notas (V1) ou no (i) (V2). No PDF, caixa/callout equivalente.
- O que é consenso técnico vira afirmação simples, sem selo.
- Regra absoluta só quando é absoluta (ex.: "efeito pré-fader **numa mesa de PA**", não "efeito pré-fader é errado").
- Capítulo "Onde estudar": só o manual oficial do fabricante, de forma genérica, e o CTA do dono, com o texto exato de `config.json`. Nenhuma outra escola, curso ou profissional.

## 4. Mesas e nomes
- A lista de mesas é confirmada pelo usuário no Passo 1. Se um nome informado não existir como produto, a pesquisa conclui isso, a lista é corrigida com o usuário, e **o material final nunca menciona o nome inexistente nem a incongruência**.
- Títulos de capítulo/seção indicam entre parênteses em quais mesas aquilo vale (nomes explícitos, ou o nome da família se TODAS as mesas dela se aplicam e a legenda define a família). Nos slides, isso aparece como chips de mesas.

## 5. PDF
- Todo capítulo começa em página nova; títulos não ficam órfãos no fim da página; o PDF sai com número de página, sumário clicável e marcadores (`make-pdf.sh`). Branco no fim de capítulo é aceito.
- Explicativo, didática simples, sem prolixidade: frases curtas, exemplos práticos, caixas de dica/atenção, pelo menos uma visualização própria por capítulo, capa, sumário, glossário, numeração.
- Já nasce sem redundância (um conceito tem lugar canônico; outros capítulos só remetem) e com fio narrativo (ganchos de abertura, transições, fechamento de capítulo).
- Visual alinhado à direção que será usada nos slides quando já escolhida; antes disso, sóbrio e profissional (tipografia forte, cores com propósito).

## 6. Slides da aula (V1)
- reveal.js local + GSAP local (pasta `lib/` **dentro** da pasta do deck). Abre com dois cliques, offline.
- Visual da direção escolhida pelo usuário entre 3 (ver `references/design.md`). Sem espaço vazio (> ~30% do quadro sem propósito), diagrama protagonista, identidade própria.
- Legibilidade de sala: corpo ≥ 28 px e rótulos ≥ 18 px num slide 1280×720; contraste AA; sem `textLength` comprimindo texto abaixo de 0,9.
- **Todo slide tem motion sob medida** no nível das amostras aprovadas: a animação **demonstra o conceito** (causa → efeito: o knob gira e a curva do HPF se move; o medidor reage ao ganho; o sinal percorre o fluxo; o gate abre/fecha), sincronizada com os fragments, coreografada, ~2–2,5 s por passo, só transform/opacity (+DrawSVG/MotionPath), `prefers-reduced-motion` vai ao estado final. Aberturas de capítulo têm motivo visual próprio do tema; quizzes demonstram a resposta ao clicar.
- O estado final de cada slide é **idêntico** avançando, voltando ou pulando direto (função `state(k)` idempotente; nunca `fromTo` que renderiza o "from" visível antes da hora — use `immediateRender:false` ou `set` no início do trajeto).
- Medidor de canal é pré-fader (DCA, mute group e fader não o derrubam); diagramas tecnicamente corretos (insert em série antes do EQ no canal; matriz da X32/M32 recebe Main/buses, não canais etc.).
- **Enxuto:** sem índice/agenda por capítulo (só o índice geral inicial; a abertura do capítulo apresenta o capítulo). Sem redundância dentro do capítulo nem entre capítulos (o 1º slide da seção não pode ser repetido por mais 1–2 slides com outras palavras; textos iguais em slides diferentes são proibidos; texto do slide não repete o rótulo do diagrama). Meta: perto de 150 telas para ~28 capítulos; **no máximo 3 slides de continuação** — se não couber, encurte o texto visível (palavra-chave + ideia) e leve o detalhe para as notas, ou ajuste layout/ícones.
- Pergunta à turma **não aparece no slide**.
- Quizzes clicáveis com feedback certo/errado e tecla R para zerar; interativos (caminho do sinal clicável, explorador de mesas, glossário).
- Contagem: o reveal numera em grade (capítulo/slide); fragments não são telas. Ao reportar quantidade, conte telas.
- Entrega também um **arquivo único** (CSS, JS e fontes embutidos) para enviar: `tools/inline_single.py`.

- **Interface obrigatória em toda direção visual** (`tools/check_padrao.mjs` confere; o dono já reprovou a falta de cada item): contador "N / T" visível em toda tela sem cobrir texto (`.chrome .num` do template ou `slideNumber:'c/t', showSlideNumber:'all'` com `tools/contador-livre.js`, sem sublinhado); fundo escuro fora do 16:9 e na tecla O (`.reveal-viewport{background:...}`, porque o `reveal.css` pinta de branco); setas de navegação (`controls:true`) e indicador de progresso; sumário clicável. Telas obrigatórias: capa, sumário, como-usar, explorador, caminho do sinal, encerramento, glossário e CTA.
- **Desenho também é conteúdo:** tecla acesa, nome de canal, número, aba e etiqueta de modelos batem com a fonte e com o texto. Recorte não corta controle ensinado. A contagem de tópicos da abertura bate com as telas do capítulo.
- **Quiz não entrega a resposta antes da tentativa, nem no desenho:** numeração, estado aceso, fader no lugar certo, fita e até um "?" sobre o controle da resposta só depois do clique. O (i) e o roteiro também não apontam a certa: descrever só uma alternativa de modo diferente, ou chamar outra de "hábito de outra mesa", já entrega.
- Afirmação operacional precisa de fonte. Ao corrigir uma frase, corrija também a nota, o (i), o roteiro e o PDF que a repetem.

## 7. Notas do apresentador (V1)
- Complementam o slide: o que o professor fala **além** do slide (por quê, como fazer na mesa, diferenças entre modelos, abordagens divergentes neutras, erro comum, transição). **Nunca repetem o texto do slide nem o texto do diagrama.**
- 60–160 palavras, diretas.
- Pergunta à turma e dinâmicas só nas notas, num bloco com estilo **inline** âmbar (a speaker view não carrega o CSS do deck), ex.: `<div style="background:#3a2a00;border-left:4px solid #ffb020;padding:6px 10px;color:#ffd27a"><b>Pergunte à turma:</b> …</div>`.
- Não antecipar a resposta do slide seguinte nem do quiz.

## 8. V2 autoestudo: (i), glossário e áudio
- Mesmos slides da V1, **pixel a pixel** (verificado com os botões ocultos e movimento reduzido). Só se acrescentam os botões (i) e ▶ no layout atual. Sem notas do apresentador.
- 3 níveis: (1) o slide; (2) o (i): popup para leigo que, só lendo, entende e tira dúvidas (170–220 palavras), termos e siglas **clicáveis** que abrem a definição do glossário dentro do popup; (3) o ▶: áudio narrado, mais longo e ainda mais didático (280–380 palavras, ~2–3 min), como para um leigo, citando cada elemento visível na ordem em que aparece: o que é, para que serve, o que acontece se errar. Nada visível fica sem menção. Telas da V2 revisadas abaixo disso foram reprovadas pelo dono por rasas.
- Mais palavras vêm de explicar melhor, nunca de inventar: nada de número, tecla, menu, limite ou recomendação sem fonte, nem "sempre/nunca" além do que a fonte diz. Divergência entre slide, nota e fonte se resolve pela fonte e nunca em silêncio.
- Quiz: (i)/áudio não entregam a resposta antes da tentativa. **Termo clicável do (i) de um quiz também não:** se a definição do glossário diz a certa ou descarta uma errada (ex.: `Automix` = "reduz sozinho o nível dos microfones fora de uso" num quiz cuja certa é essa frase), deixe o termo sem botão naquele (i). No AudioLab Live XL foram 16 de 26 quizzes. Peça escondida antes do toque volta a se esconder com a tecla R.
- Voz: masculina, **português do Brasil** (sotaque de Portugal foi rejeitado). **Desde 14/11/2026: a mesma voz dos vídeos de venda, Gemini TTS voz `Puck`, estilo "reels2"** (escolha do dono; plano grátis, chaves no cofre), via `tools/v2/tts/gen.sh`. O Kokoro `pm_alex` saiu. Roteiro em **grafia normal**, no registro falado ("tá", "aperta", "gira"; sem letra solta; sem `main`/`send`/`bus`/`mute`/`gain` minúsculos; sem "patch" falado). Guia em `tools/v2/tts/README.md`; `tts/gen.sh --lint script/` confere sem gastar cota.
- Áudio para ao trocar de slide; sem autoplay.

## 9. Técnica: Safari, memória, desempenho
- **Safari bloqueia em `file://` qualquer recurso de pasta acima (`../`).** Toda pasta entregável é autocontida (lib, fontes, áudio dentro dela).
- **Mac com 16 GB:** nunca rode mais de um modelo pesado ao mesmo tempo (TTS, Whisper, torch). Rodar 6 transcrições em paralelo travou o Mac. Use `tools/v2/heavy.sh` (trava global) e `tools/v2/qa_batch.sh` (transcrição + sotaque + volume em lote); revisores leem os relatórios em `tools/v2/qa-out/`.
- Testes de navegador (playwright) tocam áudio nas caixas do Mac: silencie o áudio dos elementos no teste (`muted = true`) e use Chromium com `--mute-audio`.
- Agentes paralelos: rascunhos sempre em subpasta própria da pasta temporária, nunca na raiz dela. Dois agentes já sobrescreveram o `split.py` um do outro.
- Bash do macOS (3.2): array vazio com `set -u` falha; use `${A[@]+"${A[@]}"}`. O espeak-ng ignora pasta de dados em caminho com 160+ caracteres (`gen.py` já usa cópia curta).
- Slides gerados por script: edite o gerador (template, viz, bespoke, notes), nunca o HTML gerado à mão.
