# Aplicar as decisões da validação — padronização final (Passo 7 da skill curso-mesa-de-som)

Você aplica as correções de UM curso de mesa de som, só na V2 de autoestudo. Exemplo completo de um curso já corrigido: `exemplos/corrigir.py` e `exemplos/audiolab-live-xl-aplicado.md`.
Raiz: `$R/padronizacao` do curso (o caminho absoluto vem no pedido; abaixo, caminhos relativos a ela).
Leia antes: `VALIDACAO.md` (a regra dos quizzes) e o relatório do seu curso `validacao/<c>.md`.
Responda e escreva em português simples.

## Decisão (já tomada; não reabra)
Aplique TODO item marcado CORRIGIR em "Vazamentos". MANTER fica. Defeitos de motion e avisos de título NÃO são aplicados, salvo rótulo errado/cortado de gravidade baixa que se corrige com troca de texto simples (ex.: botão "PRÓXIMO: 08" sem o nome do capítulo).
Se concluir que um item está errado (quebraria o slide ou contradiz o gabarito), não aplique e explique no relatório.
"Certa muito mais longa": encurte a certa ou alongue as erradas até ficarem parecidas, sem mudar o sentido nem o gabarito, e sem criar quebra de linha só na certa.

## Onde mudar
- O deck V2 entregue é `ws/<c>/antes/v2/08-slides-v2/index.html` (HTML plano, sem pilhas). NÃO edite esse arquivo nem nada em `ws/<c>/antes/`, `ws/<c>/depois/`, `ws/<c>/material/` ou fora da raiz.
- Escreva TODAS as mudanças de HTML (desenho, aria-label, texto do (i), termo clicável `<span class="gl" ...>`, alternativas, rótulos) num script `ws/<c>/corrigir.py`:
  uso `python3 -I ws/<c>/corrigir.py entrada.html saida.html`; cada troca é `assert h.count(old) == 1` + `h = h.replace(old, new)`, de preferência buscando dentro da `<section id="quiz-N" ...>` (regex até o próximo `<section id=`) para não pegar outro slide;
  antes de cada troca, um comentário de 1 linha: quiz, o que entregava a resposta.
  No fim, o script confere que o número de `<section` não mudou e imprime "corrigir ok: N trocas".
  Se `ws/<c>/antes/v2/08-slides-v2/` tiver outro .html com quizzes (ex.: `curso-autoestudo.html` na Axios32), o mesmo script deve funcionar nele também (rode nos dois).
- Desenho: o estado neutro antes do toque deve continuar coerente com o estado depois do toque. A animação da certa deve terminar mostrando a resposta. Leia o JS do quiz no próprio HTML para ver como o retorno revela as peças, e use o mesmo mecanismo (classe/atributo que o toque já liga).
- A tecla R (e a entrada no slide) zera o quiz: toda peça escondida antes do toque precisa ser reescondida pelo mesmo reset. Leia a função de reset do quiz e use classe/atributo que o toque liga e o reset desliga. O teste central compara foto da pergunta × foto depois de tocar e apertar R.
- Para tirar um termo clicável do (i) de UM quiz: troque o `<span class="gl" ...>termo</span>` por só o texto, dentro do template `v2i-quiz-N`, sem mexer no glossário geral.
- Se o desenho mudar, ajuste o (i) e a voz que descrevem a peça mudada.
- Voz: o roteiro é `ws/<c>/c/tools/v2/script/quiz-N.txt` (voz Gemini Puck desde 14/11/2026: grafia normal no registro falado, "tá", "aperta", sem letra solta nem `main`/`bus` minúsculos; guia em `ws/<c>/c/tools/v2/tts/README.md`. Curso antigo com grafia fonética do Kokoro, como "pê ême" ou "fêider": nos roteiros que você tocar, volte à grafia normal). Se o HTML também traz o texto da voz (legenda/transcrição), troque no `corrigir.py` também.
  NÃO gere áudio (o TTS roda depois, em `padronizar.sh aplicar`). `ws/<c>/c` é o próprio curso: os roteiros mudam de verdade, por isso o backup abaixo é obrigatório. Liste em `ws/<c>/vozes.txt` um id por linha (ex.: `quiz-7`) de todo roteiro que você mudou.

## Ordem
1. BACKUP antes de editar roteiros: `mkdir -p ws/<c>/bak-validacao && cp -p <cada script/quiz-N.txt que vai mudar> ws/<c>/bak-validacao/` e confira com `ls` que todos estão lá. Se falhar, pare e relate.
2. Escreva `corrigir.py`, edite os roteiros, escreva `vozes.txt`.
3. Teste: `python3 -I ws/<c>/corrigir.py ws/<c>/antes/v2/08-slides-v2/index.html /tmp/<c>-corrigido.html` (nenhum assert pode falhar) e confira com `diff` que só os quizzes previstos mudaram.
4. NÃO abra navegador, NÃO rode node/playwright, TTS ou Whisper, NÃO use git. A conferência visual (fotos antes/depois do toque) e o teste de navegação são centrais.
5. Relatório em `validacao/<c>-aplicado.md`: uma linha por item (quiz, o que foi feito, onde), roteiros mudados, itens não aplicados e por quê. No final, responda só com o caminho e um resumo de 3 linhas.
