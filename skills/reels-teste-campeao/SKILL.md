---
name: reels-teste-campeao
description: Use quando o usuário quiser pegar o Reel que mais performou e testar variações dele como Reel de teste do Instagram (trial reel, que aparece só para quem não segue o perfil) — "reel de teste", "trial reel", "testar variação", "campeão", "teste A/B de Reels", "qual vídeo performou", "repostar o vídeo que bombou", "trocar o gancho e repostar". Mede views, alcance, salvamentos e compartilhamentos (Graph API da Meta ou pelo app), escolhe o campeão por regra, gera as variações com ffmpeg (cor, fonte, título, CTA, gancho, voz nova só no trecho trocado), posta como Reel de teste e lê quem venceu. Uma variável por teste. Dispare mesmo que a pessoa não diga "skill".
---

# Reels de teste do campeão

## O que esta skill faz
A cada 2 dias olha os Reels orgânicos postados há 2 a 4 dias. O que tiver mais visualizações, se passar da média do
perfil, vira **campeão**. O campeão ganha 11 Reels de teste em 56 dias:

| Fase | Quando | O que muda |
|---|---|---|
| 1 | dia 0, 2 e 4 (um a cada 48 h) | repostagem sem regravar: cor, enquadramento, fonte e título na tela (`r1`, `r2`, `r3`) |
| 2 | 1 por semana, dias 7 a 56, em rodízio | `cenario` (visual novo), `cta` (chamada mais forte), `gancho` (uma palavra trocada, com a voz regravada só nesse trecho) |

Reel de teste é o recurso do Instagram que mostra o vídeo **só para não seguidores**. Se for bem, ele vai para os
seguidores (sozinho ou quando você manda). Assim dá para repostar o que já funcionou sem cansar quem já segue.

| Arquivo | O que tem |
|---|---|
| `scripts/reels_teste.py` | Tudo: `campeao`, `vencedor`, `variacoes`, `voz`, e com token `medir`, `postar`, `contas`. Só Python 3.8+ e ffmpeg |
| `referencias/TOKEN-META.md` | Como o usuário cria o token da Meta e salva sem passar pelo chat |
| `exemplos/metricas-exemplo.csv` | Modelo do CSV de métricas (para quem mede pelo app) |

Caminho da skill: `K=~/.claude/skills/reels-teste-campeao`. Rode tudo numa pasta de trabalho do usuário (ex.:
`~/reels-teste/`): o `registro.csv` (o que foi postado) e o `metricas.csv` ficam nela.

## Passo 1: Conversa inicial (uma rodada só)
Pergunte numa chamada de AskUserQuestion, com o padrão como 1ª opção "(Recomendado)". Pule o que o pedido já respondeu.
| Campo | Padrão |
|---|---|
| como medir e postar | pelo app (manual). Opção: automático pela API da Meta (passo 2) |
| palavra do CTA e o que a pessoa recebe | "COMENTA CURSO" / "que eu te mando o capítulo grátis". Só use uma palavra que a automação de DM do perfil já atende |
| onde estão os MP4 finais dos Reels | pasta informada pelo usuário |

Confira o ffmpeg (`ffmpeg -version`). Falta? Mac: `brew install ffmpeg`; Windows: `winget install ffmpeg`; Linux: `apt install ffmpeg`.

## Passo 2: Token da Meta (só no modo automático)
Pule se `~/.config/reels-teste-campeao/meta.env` existir. Senão siga `referencias/TOKEN-META.md` com o usuário, um passo
por vez. Permissões: `instagram_basic`, `instagram_content_publish`, `instagram_manage_insights` (mais `pages_show_list`
e `pages_read_engagement` para achar a conta). O token vai do navegador para o Terminal com `read -rs`:
```bash
mkdir -p ~/.config/reels-teste-campeao && printf 'Cole o token e tecle Enter: ' && read -rs k && printf 'META_TOKEN=%s\n' "$k" > ~/.config/reels-teste-campeao/meta.env && chmod 600 ~/.config/reels-teste-campeao/meta.env && echo && echo salvo
```
**Nunca** peça, mostre, copie ou grave o token no chat ou em arquivo do projeto. Nunca rode `cat` nesse arquivo.

## Passo 3: Medir
- **Automático:** `python3 "$K/scripts/reels_teste.py" medir --saida metricas.csv` (últimos 50 Reels + os Reels de teste
  anotados no `registro.csv`; métricas `views`, `reach`, `saved`, `shares`, `likes`, `comments`).
- **Pelo app:** em cada Reel, toque em **Ver insights** e anote Visualizações, Contas alcançadas, Salvamentos e
  Compartilhamentos num CSV igual a `exemplos/metricas-exemplo.csv` (data em `AAAA-MM-DD HH:MM`). Os Reels de teste levam
  o nome da variação na coluna `teste` (ex.: `r1`) e o ID do campeão na coluna `campeao`.
- Deixe de fora **vídeos de venda e anúncios**: eles distorcem a média. Só Reels orgânicos entram na escolha.

## Passo 4: Escolher o campeão (a regra)
```bash
python3 "$K/scripts/reels_teste.py" campeao metricas.csv
```
- Base: os 30 Reels orgânicos mais recentes com 48 h ou mais. Média = média de views deles.
- Janela: Reels postados há 48 a 96 h que ainda não foram campeões (os do `registro.csv` saem).
- Campeão = mais views da janela (desempate: salvos + compartilhamentos), **só se passar da média**. Senão, nada a fazer
  até a próxima medição (2 dias).
- A saída já traz o plano com as 11 datas. Repita a cada 2 dias: mais de um campeão pode correr ao mesmo tempo.

## Passo 5: Gerar as variações
Escreva você os textos, a partir do gancho e da legenda do campeão:
- 3 **títulos** de até ~38 caracteres, estilo texto nativo do Instagram, que despertem curiosidade.
- 2 ou 3 **ganchos**: o gancho de tela original trocando **uma só palavra** por outra mais forte (palavra negativa
  costuma vencer a positiva: "o erro que estraga" > "a dica que melhora").
```bash
python3 "$K/scripts/reels_teste.py" variacoes campeao.mp4 \
  --titulos "O erro que estraga seu som|Ninguém te conta isso|Salva antes de esquecer" \
  --ganchos "O erro que DESTRÓI seu som|O detalhe que estraga seu som" \
  --cta "COMENTA CURSO|que eu te mando o capítulo grátis"
```
Sai em `campeao-variacoes/`: `r1`, `r2`, `r3`, `cenario-1-escuro`, `cenario-2-quente`, `cenario-3-frio`, `cta`,
`gancho-1..N` (1080x1920). Detalhes: o título fica numa faixa no topo só nos 3,5 s iniciais (fora da área que a
interface do Reels cobre); o CTA cobre o meio da tela nos últimos 4,5 s (`--cta-inicio` muda); `--so cta,gancho` gera só
algumas; `--fontes a.ttf|b.ttf|c.ttf` troca as fontes. `cenario-1-escuro` inverte as cores: só serve em vídeo de fundo
claro. Vídeo com rosto: o "visual novo" de verdade é regravar com outro cenário ou roupa; o filtro de cor é a versão sem rosto.

Confira antes de postar: tire um quadro de cada (`ffmpeg -ss 1 -i r1.mp4 -frames:v 1 r1.png`) e olhe com Read.

## Passo 6: Voz nova só no trecho trocado (CTA e gancho)
A fase 2 fala o gancho novo ou o CTA novo; o resto do vídeo fica igual.
1. Gere só a frase nova: gravação no celular ou a voz de IA que o perfil já usa (a mesma voz do vídeo). Duas regras da
   voz de IA: a primeira palavra às vezes some, então comece com uma palavra que pode se perder ("E", "Olha"); e nunca
   comece com a palavra do CTA ("Quer o capítulo? Comenta CURSO…", não "Comenta CURSO…").
2. Ache o trecho: assista e anote em que segundo a fala do gancho termina (gancho: `--de 0 --ate <fim>`) ou em que segundo
   começa a fala final (CTA: `--de <início> --ate <fim do vídeo>`).
3. Troque:
   ```bash
   python3 "$K/scripts/reels_teste.py" voz campeao-variacoes/gancho-1.mp4 --voz fala-nova.wav --de 0 --ate 3.2 \
     [--musica trilha.m4a --musica-inicio 0] --saida gancho-1-final.mp4
   ```
   O volume é igualado ao do trecho original. Fala até 20% mais longa é acelerada; mais que isso, o script recusa
   (encurte a frase). Áudio do vídeo com voz e música misturadas: passe a trilha em `--musica` para ela não sumir no
   trecho; sem a trilha separada, a fala nova entra sozinha. Confira ouvindo o começo e o fim.

## Passo 7: Postar como Reel de teste
- **Pelo app:** crie o Reel com o MP4 e, na tela de compartilhar, ligue a opção **Reel de teste** (Trial). Escolha se o
  Instagram mostra aos seguidores sozinho quando for bem. Anote no `registro.csv` (colunas
  `data,campeao,variante,variavel,media_id,link`) para medir depois.
- **Automático:**
  ```bash
  python3 "$K/scripts/reels_teste.py" postar campeao-variacoes/r1.mp4 --legenda legenda.txt --campeao <id> --variante r1
  ```
  Usa `trial_params={"graduation_strategy":"SS_PERFORMANCE"}` (o Instagram promove sozinho se for bem; `--graduacao
  MANUAL` deixa a decisão com você), envia o arquivo direto (sem precisar de link público) e anota no `registro.csv`.
- Na variação `cta`, ponha a frase do CTA no começo da legenda também.
- **Nunca poste sem o usuário pedir.** Na agenda, poste uma variação por data (o plano do passo 4).

## Passo 8: Ler o resultado e promover o vencedor
Espere 48 h depois de cada Reel de teste, meça de novo (passo 3) e rode:
```bash
python3 "$K/scripts/reels_teste.py" vencedor metricas.csv [--campeao <id>]
```
- Compare os **testes entre si** (todos foram para não seguidores). Vence quem tiver **20% a mais que a mediana dos
  testes e pelo menos 100 views**. Desempate: salvamentos + compartilhamentos por mil views. No teste de CTA, o que vale é
  comentários com a palavra (leads) por mil views.
- Vencedor com `MANUAL`: no app, abra o Reel de teste e compartilhe com os seguidores. Com `SS_PERFORMANCE`, o Instagram
  já faz isso sozinho.
- O vencedor vira a nova base: o próximo teste muda outra coisa a partir dele. Sem vencedor claro, mantenha o original.

## Uma variável por teste
Cada Reel de teste da fase 2 muda **uma** coisa só em relação ao campeão (visual, CTA ou uma palavra do gancho). Se dois
mudarem juntos, não dá para saber o que fez a diferença. A fase 1 é exceção de propósito: ela mede se o assunto aguenta
repostagem, não qual detalhe ganhou.

## Modo semanal (teste em lote, "domingo à noite")
Para quem produz vídeo novo toda semana: escolha um dia e horário fixos. Nesse horário sai 1 vídeo principal no perfil e
até 10 Reels de teste, cada um mudando **uma** coisa do principal. Distribuição que funcionou: gancho (3), dor (1),
consequência ou agressividade (1), estrutura (1), CTA (3) e duração (1, versão de ~20 s).
1. 4 dias depois, meça os 11 (passo 3).
2. Por dimensão, o teste que bateu a regra do passo 8 vence. Novo principal = principal anterior + o vencedor de cada
   dimensão. Sem vencedor numa dimensão, ela fica como estava. Se o CTA não diferenciou nada, teste menos CTA e mais gancho.
3. Escreva os 10 testes novos sem repetir gancho, frase de dor ou texto de tela das semanas anteriores.
Os MP4 dos testes saem da sua ferramenta de vídeo (ou do `variacoes` e do `voz` desta skill).

## Erros comuns
| Erro | Correção |
|---|---|
| Vídeo de venda ou anúncio vira campeão | Só Reels orgânicos no CSV (ou deixe a coluna `teste` vazia só neles e apague os de venda) |
| Campeão escolhido com menos de 48 h | O Reel ainda está crescendo; a regra só olha 48 a 96 h |
| Mudar duas coisas no mesmo teste | Uma variável por teste na fase 2 |
| Trocar a música do vídeo pronto | Com voz e música misturadas no mesmo áudio, não dá para trocar só a música; mude cor, fonte e título |
| A voz nova engole a primeira palavra | Comece a frase com uma palavra que pode sumir; pergunta antes da palavra do CTA |
| CTA com palavra que a DM automática não atende | Use só palavras já configuradas na automação de comentário → DM |
| Opção Reel de teste não aparece no app | Conta precisa ser profissional e pública; atualize o app |
| Token no chat | Nunca. Só pelo Terminal com `read -rs` (passo 2) |

## Autoteste
`python3 "$K/scripts/reels_teste.py" --teste` confere as regras (campeão, vencedor, agenda), lê CSV e JSON, gera um MP4
de 5 s com o ffmpeg, faz as 9 variações e as trocas de voz, e confere pixels e durações. Não chama nenhuma API.
