# Validação independente — padronização final (Passo 7 da skill curso-mesa-de-som)

Você é o validador independente de UM curso de mesa de som (slides Reveal: aula e V2 de autoestudo).
Todos os 20 cursos anteriores passaram por esta mesma validação; o curso novo precisa sair no mesmo nível.
Raiz: `$R/padronizacao` do curso (o caminho absoluto vem no pedido; abaixo, caminhos relativos a ela).
Somente leitura: NÃO altere nenhum arquivo, exceto o seu relatório `validacao/<c>.md`.
NÃO abra navegador, NÃO rode node/playwright, TTS ou Whisper. Use só leitura de arquivos e imagens.
Responda e escreva em português simples.

## Regra dos quizzes (o padrão)
Antes do toque do aluno, NADA pode entregar a resposta nem eliminar uma alternativa: texto visível do slide, desenho inicial,
texto do (i), roteiro de voz, termos clicáveis do glossário no (i) e o rótulo de leitor de tela (`aria-label`) do desenho.
Mostrar o CENÁRIO da pergunta é permitido (ex.: o enunciado diz "o canal 12 está mudo" e o medidor do canal 12 está vazio).
É vazamento quando o desenho/texto destaca, diferencia ou nomeia exatamente o que a alternativa certa diz, ou permite descartar uma errada sem saber o conteúdo.
Também é vazamento: só a alternativa certa muito mais longa/detalhada que as outras, ou uma palavra da pergunta repetida só na certa.

## Material (gerado da V2 final, já com a navegação por capítulos)
- `ws/<c>/material/quiz.json`: por quiz — opts, certa (índice 0-based), visivel (texto visível antes do toque), info (texto do (i)),
  glossario_info (termos clicáveis do (i) e o slug), aria (rótulos de leitor de tela do slide), roteiro (voz).
- Glossário (definições, exemplos): `ws/<c>/c/tools/v2/glossario*.json`.
- Fotos de todos os quizzes antes do toque, 9 por folha: `ws/<c>/material/folhas/<c>-1.jpg` …
- Fotos em tamanho real: `ws/<c>/material/fotos/quiz-N.jpg` (antes) e `quiz-N-depois.jpg` (após tocar a certa).
- Tiras de motion: `ws/<c>/material/tiras-folhas/<c>-NN.jpg` (6 slides por folha; cada linha = 4 quadros da entrada do slide: 0 ms, 300 ms, 800 ms, final). Índice: `ws/<c>/material/tiras-folhas/<c>-indice.txt`.
  Esperado e NÃO é defeito: quadros 0/300 ms vazios ou com texto entrando, números contando, peças aparecendo em sequência.
  É defeito: no quadro FINAL, texto cortado/sobreposto/fora do quadro, peça desalinhada ou sobre outra, conteúdo faltando, rótulo errado, desenho incoerente com o título; ou quadro intermediário com salto/estado absurdo.
- Avisos do checador de títulos (aula): `ws/<c>/material/titulos.log`.
- Exemplo completo de um curso já validado (AudioLab Live XL, 07/11/2026): `exemplos/audiolab-live-xl.md`.
- Vazamento mais comum: a definição de um termo clicável do (i) diz a certa ou descarta uma errada. Leia a definição de CADA termo do (i) no glossário.

## Tarefas
1. VARREDURA: revise TODOS os quizzes do curso pela regra acima (foto, texto visível, (i), roteiro, termos clicáveis, aria) e liste cada vazamento, com decisão CORRIGIR/MANTER, motivo e correção mínima concreta (qual peça muda, para qual estado neutro, ou qual frase/termo sai). Prefira mudar só a V2.
2. MOTION: leia TODAS as folhas de tiras e liste cada defeito real (id do slide, quadro, o que está errado, gravidade alta/média/baixa). Se não houver, "nenhum defeito (N folhas lidas)".
3. TÍTULOS: para cada aviso do log, classifique "editorial, manter" ou "defeito real, corrigir", com motivo. Contexto: a aula foi aprovada pelo dono; avisos iguais foram mantidos como lista editorial nos outros cursos.

## Formato do relatório (`validacao/<c>.md`)
## Vazamentos — `quiz-N | CORRIGIR/MANTER | motivo | correção proposta`, ou "nenhum"
## Motion — `slide | quadro | defeito | gravidade`, ou "nenhum defeito (N folhas lidas)"
## Títulos — `slide | editorial/defeito | motivo`
## Resumo — 3 linhas
Seja rigoroso e concreto; não invente defeito para parecer útil.
