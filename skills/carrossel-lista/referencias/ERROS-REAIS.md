# Regras que saíram de erros reais

Lições de uma produção real de 100 roteiros e 43 carrosséis publicados num perfil de nicho. Cada linha custou retrabalho ou alcance.

| O que deu errado | Regra |
|---|---|
| A primeira leva de roteiros foi reprovada: citava marca e modelo de produto e prendia tudo a um só cenário | Conteúdo genérico. Marca e modelo vão para `proibidas` no `config.json`; o cenário varia entre carrosséis |
| A IA que desenhou o slide inteiro (texto e gráfico dentro da imagem) errou letras e duplicou rótulos num gráfico | Modo padrão: a IA faz só a cena, sem texto, e o texto entra pelo gerador. No modo `--slide-inteiro`, confira cada slide letra por letra e gere de novo o que vier errado |
| A geração de imagens parou no meio (crédito ou limite): um carrossel ficou com 8 de 10 slides e 57 ficaram sem imagem | Gere carrossel por carrossel. Antes de entregar, compare o número de slides com o roteiro. Nunca publique carrossel incompleto. Anote onde parou |
| A conferência só contou arquivos e não abriu as imagens | Abra as imagens com Read: capa, um slide do meio e o último de cada carrossel, no mínimo |
| A pasta foi criada com erro de digitação no nome e outra automação não achou os carrosséis | Nome fixo e sem acento: `carrosseis/`, uma subpasta `001`, `002`... por carrossel |
| Números na tela diferentes da fonte (página de venda, manual) | Todo número do slide é conferido com a fonte antes de gerar |
| Carrossel só de texto em fundo preto teve cerca de 60 vezes menos curtidas que o de cena ilustrada, no mesmo perfil | Sempre capa com cena (personagem inusitado). Sem imagem, o degradê serve só para rascunho |
| Promessa de "te mando no direct" sem automação de DM funcionando | Não prometa DM no informativo. O validador recusa "DM" e "direct" no último slide |
| Emoji e seta (→) no texto do slide viraram quadradinho | O validador recusa caractere que a fonte não tem |
| Título quebrou deixando "o" ou "a" sozinho no fim da linha | Reescreva o título (ou marque o trecho principal com `*`) até a quebra ficar natural |
| Legenda igual em todas as redes: YouTube não marca amigo; TikTok e Kwai não têm "link da bio"; página do Facebook não tem link na bio | `carrossel.py legenda` adapta cada rede sozinho. Pinterest sai sem o pedido de comentário e com até 500 caracteres |
| No Instagram pela web, "compartilhar no Facebook" vem ligado por padrão e o corte não vem em 4:5 | Ao postar pela web: desligue o compartilhamento e escolha o corte 4:5 à mão. Fixar post no perfil só existe no app |
| Imagens da IA em alta (1792×2240, ~5 MB cada) somaram 2 GB para 43 carrosséis | Não versione as imagens no git. O gerador entrega 1080×1350, o tamanho do Instagram |
