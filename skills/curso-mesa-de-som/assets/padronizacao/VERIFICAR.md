# Conferência visual das correções — padronização final (Passo 7 da skill curso-mesa-de-som)

Você confere UM curso de mesa de som depois das correções da validação (só V2). Raiz: `$R/padronizacao` do curso (o caminho absoluto vem no pedido; abaixo, caminhos relativos a ela).
Somente leitura: NÃO altere nada, exceto o seu relatório `validacao/<c>-conferido.md`. NÃO abra navegador, NÃO rode node/TTS/Whisper, NÃO use git.
Responda e escreva em português simples.

## Material
- Regra dos quizzes: `VALIDACAO.md`. O que foi pedido: `validacao/<c>.md`. O que foi feito: `validacao/<c>-aplicado.md` e o script `ws/<c>/corrigir.py`.
- Fotos ANTIGAS (antes das correções): `ws/<c>/material/fotos/quiz-N.jpg` e `quiz-N-depois.jpg`.
- Fotos NOVAS (V2 corrigida, já com navegação por capítulos): `ws/<c>/material-r2/fotos/quiz-N.jpg` (antes do toque) e `quiz-N-depois.jpg` (após tocar a certa); folhas 3×3 em `ws/<c>/material-r2/folhas/`; textos novos em `ws/<c>/material-r2/quiz.json` (visivel, info, aria, glossario_info, opts, certa).

## Tarefas (para CADA quiz que o corrigir.py mudou)
1. Foto nova ANTES do toque: nada entrega a resposta nem elimina alternativa (desenho, texto visível); a correção pedida está visível na tela; nada quebrado (peça faltando sem motivo, texto cortado/sobreposto, desenho incoerente com a pergunta).
2. Foto nova DEPOIS do toque na certa: o retorno termina mostrando a resposta (a peça escondida aparece, o estado final faz sentido) e bate com o retorno da foto antiga, salvo a mudança pedida.
3. Textos no `material-r2/quiz.json`: (i), aria, termos clicáveis e alternativas com a correção aplicada e sem novo vazamento; a certa não ficou a mais longa/única em duas linhas; o gabarito (`certa`) igual ao do `material/quiz.json` antigo, salvo troca de alternativa explicada no aplicado.md.
4. Quizzes NÃO mudados: compare as folhas novas com as antigas (`material/folhas/`) e aponte qualquer diferença visual inesperada.

## Relatório `validacao/<c>-conferido.md`
## Itens — `quiz-N | OK/PROBLEMA | o que viu (antes / depois / textos)`
## Problemas — lista com a correção mínima concreta para cada um, ou "nenhum"
## Resumo — 3 linhas
Seja rigoroso e concreto; não invente defeito. No final, responda só com o caminho e o resumo de 3 linhas.
