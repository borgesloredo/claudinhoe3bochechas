---
name: traqueamento-organico
description: Use quando o usuário quiser montar a base de leads orgânica e o lado orgânico das redes sociais — puxar seguidores e contatos de Instagram, Facebook, TikTok, YouTube, Kwai, Pinterest e WhatsApp (inclusive pelo backup do iPhone), juntar a mesma pessoa entre redes, dar nota e fazer o ranking de quem é do nicho numa aba "Orgânico" do painel; criar ou arrumar os perfis (rebranding, bio, destaques, fixados, verificação, o que só dá pelo app); e publicar orgânico nas 6 redes (publicador diário, legenda e CTA por rede, agenda, horários, armadilhas de cada rede). Dispare com "seguidores", "base de leads orgânica", "puxar contatos do WhatsApp", "ranking de seguidores", "quem são meus seguidores mais quentes", "criar perfil no TikTok/YouTube/Kwai", "arrumar meus perfis", "bio", "destaques", "publicar em todas as redes", "publicador", "legenda por rede", "rastreamento orgânico", mesmo que a pessoa não diga "skill". Irmã da skill traqueamento-e-trafego-pago (site, pixels, anúncios).
---

# Rastreamento orgânico: leads, perfis e publicação

Três partes, que podem ser feitas juntas ou separadas:

1. **Buscar o lead orgânico**: todo mundo que segue ou conversa com a pessoa em cada rede vira uma linha num banco SQLite local, a mesma pessoa em redes diferentes vira um lead só, e cada lead ganha nota (aquecimento + nicho). Sai um ranking e uma aba "Orgânico" (HTML local ou JSON para o painel que a pessoa já tem).
2. **Criar e arrumar os perfis**: nome, @, foto, bio, link, destaques, fixados, verificação, em todas as redes, com a lista do que só dá para fazer pelo app do celular.
3. **Publicar orgânico**: um texto base vira o texto certo de cada rede; uma agenda com horários; um publicador opcional (Instagram e Facebook pela API oficial, as outras como lembrete com o texto pronto).

Tudo saiu de um projeto real (cursos de áudio ao vivo vendidos pelo Instagram e por site próprio) e foi generalizado. Os exemplos de palavras do nicho são de áudio: troque pelas do nicho da pessoa.

| Arquivo | O que tem |
|---|---|
| `scripts/base_organica.py` | Importa exportações oficiais (zip/JSON/CSV), contatos (.vcf), conversas exportadas do WhatsApp (.txt) e o backup do iPhone; une, dá nota, faz ranking, painel HTML/JSON, ajustes e descadastro. `--teste` |
| `scripts/textos_por_rede.py` | Texto base -> título, legenda, hashtags e CTA de cada uma das 6 redes. `--teste` |
| `scripts/publicar.py` | Opcional. Agenda + publicador (Meta pela API oficial; outras redes como lembrete). `--teste` |
| `references/buscar-leads.md` | Como baixar a base de cada rede, WhatsApp, nota, união, grupo Pessoal, painel, LGPD |
| `references/perfis.md` | Criação e rebranding rede a rede, bio, destaques, fixados, verificação, só-no-app |
| `references/publicar.md` | Publicador diário, texto por rede, agenda e horários, tokens da Meta, automação não oficial |

Caminho da skill: `K=~/.claude/skills/traqueamento-organico`. Os scripts só usam Python 3.9+ do próprio Mac (sem instalar nada).

## Regras fixas

- **Token e senha nunca no chat.** A pessoa salva pelo app Terminal, com o valor escondido (ver "Tokens" abaixo). Nunca leia, mostre nem copie o valor.
- **Nunca publique, agende, siga, curta nem mande mensagem sem a pessoa pedir aquela ação.** "Feito" ou "pronto" depois de configurar não é autorização. (No projeto de origem, 25 Reels foram agendados sem pedido e tiveram de ser apagados.)
- **Dados de seguidores não aparecem no chat.** O `ranking` mostra só se há e-mail/telefone (`e`/`t`); o contato em si fica no CSV e no painel, com permissão só do dono (600). Não cole listas de pessoas na conversa.
- **LGPD**: a base é para uso próprio (falar com quem já segue ou conversa com a pessoa, sobre o nicho). Só dado público ou que a própria pessoa deu; cada e-mail/telefone guarda de onde veio; texto de mensagem nunca é gravado; nada comprado nem cruzado com base de terceiros; não vender nem repassar; quem pedir para sair é descadastrado (`descadastrar`) e não volta em importação futura. A primeira mensagem para um lead sempre oferece sair ("responde SAIR que eu não te chamo mais").
- **API oficial × não oficial**: diga sempre qual é qual e o risco (tabela abaixo). Quem decide usar o não oficial é o dono da conta, por escrito, depois de saber o risco.

## Passo 1: Conversa inicial (uma rodada só)
Pergunte de uma vez (AskUserQuestion), com a opção padrão primeiro "(Recomendado)". Pule o que o pedido já respondeu.

| Pergunta | Padrão |
|---|---|
| Quais redes você tem (ou quer ter)? Instagram, Facebook (Página e/ou perfil), TikTok, YouTube, Kwai, Pinterest, WhatsApp (comum ou Business) | as que ela citar; se nenhuma, Instagram + WhatsApp |
| Qual é o seu nicho e que palavras o seu público usa? (5 a 10 fortes, que só quem é do nicho fala; 5 a 10 fracas, que contam só em dupla) | tirar do produto/site dela e mostrar a lista para ela corrigir |
| Onde fica o painel? (a) arquivo HTML no Mac, (b) painel próprio que já existe, que recebe JSON, (c) sem painel, só CSV | (a) |

Depois siga sozinho. Decisões no meio do caminho: escolha a recomendada e conte no resumo.

## Passo 2: Buscar o lead orgânico (parte 1)
Leia `references/buscar-leads.md` antes. Em resumo:
1. Pasta de trabalho só dela, fora de qualquer repositório git (dado pessoal): `mkdir -p ~/base-organica && cd ~/base-organica && python3 "$K/scripts/base_organica.py" iniciar`. Edite o `nicho.json` com as palavras do Passo 1, o nome dela no WhatsApp (`meu_nome_no_whatsapp`), sobrenomes da família (`pessoal_palavras`) e conversas a excluir (empresa onde trabalha, família).
2. Peça as exportações oficiais rede a rede (o passo a passo está na referência; a pessoa clica, você não entra na conta dela). O "baixar seus dados" demora de minutos a dias; siga com o que já chegou.
3. Importe cada arquivo como veio (zip inclusive): `python3 "$K/scripts/base_organica.py" importar ~/Downloads/<arquivo>.zip`. Ordem boa: primeiro os contatos (.vcf), depois o resto (assim quem aparece só pelo nome nas conversas ganha o telefone). CSV sem coluna `rede`: `--rede youtube`.
4. WhatsApp: conversas exportadas (.txt/.zip) ou, para o histórico inteiro, o backup local do iPhone: `python3 "$K/scripts/base_organica.py" whatsapp-backup` (pede Acesso Total ao Disco para o Terminal; o backup não pode estar criptografado).
5. Ranking e painel: `ranking --top 30 --csv ranking.csv` e `painel painel-organico.html` (ou `painel organico.json` para o painel próprio). Mostre a ela só o resumo (quantos por nível, por redes), nunca a lista.
6. Ela revisa no painel e você grava os ajustes que ela pedir: `pessoal`, `cliente`, `interesse`, `separar`. Repita a importação todo mês: a lista completa de seguidores marca quem deixou de seguir.

## Passo 3: Criar e arrumar os perfis (parte 2)
Leia `references/perfis.md`. Faça um quadro por rede (o que está, o que muda, quem faz: você no navegador dela ou ela no app) e siga essa ordem: @ e nome iguais em todas as redes (anotar quando cada rede deixa mudar de novo), foto igual, bio na fórmula (frase de impacto / autoridade / oferta como benefício + CTA, até 3 linhas), link, conteúdo antigo de outro assunto **escondido** (privado ou arquivado, nunca apagado sem pedido), destaques, fixados, verificação. No fim, confira cada perfil aberto como visitante e acerte os links do site para os perfis (um @ errado no rodapé do site leva para o perfil de outra pessoa).

## Passo 4: Publicar orgânico (parte 3)
Leia `references/publicar.md`.
1. Para cada peça (vídeo, carrossel), um texto base `NNN.txt` (TÍTULO, TEXTO, CTA, HASHTAGS, LINK) e `python3 "$K/scripts/textos_por_rede.py" NNN.txt [--auto-dm] [--tag-tiktok "#aprendanotiktok"]` -> `NNN.redes.txt` com o bloco de cada rede. `--auto-dm` só se o Instagram dela tem resposta automática no direct.
2. Agenda: 1 a 2 posts por dia, sempre nos mesmos horários (padrão 12:00 e 19:00 no fuso dela). Não poste o mesmo vídeo no mesmo dia em perfis que se cruzam (Instagram e Facebook da mesma pessoa) sem querer: o composer web do Instagram compartilha no Facebook por padrão.
3. Publicador (opcional, só se ela pedir publicação automática): tokens da Meta salvos pelo Terminal (abaixo), vídeos num link público, `publicar.py planejar ...`, conferir `agenda.json` com ela, `publicar.py rodar --seco`, e só então ligar o `rodar` a cada 10 min (launchd/cron). TikTok, YouTube, Kwai e Pinterest chegam como lembrete "postar à mão" com o texto pronto.

## Tokens (quando ela quiser automação)
Guie em texto simples, um passo por vez. **Não cole o token aqui no chat.** No app Terminal:
```bash
mkdir -p ~/.config/traqueamento-organico && printf 'Cole o token e tecle Enter: ' && read -rs k && printf 'META_TOKEN=%s\n' "$k" > ~/.config/traqueamento-organico/meta.env && chmod 600 ~/.config/traqueamento-organico/meta.env && echo && echo salvo
```
Os IDs (não são segredo) entram no mesmo arquivo com `>>`: `printf 'FB_PAGE_ID=%s\nIG_USER_ID=%s\n' 'ID_DA_PAGINA' 'ID_DO_INSTAGRAM' >> ~/.config/traqueamento-organico/meta.env`. Qualquer outro token segue o mesmo modelo: `~/.config/traqueamento-organico/<nome>.env`. Conferir sem mostrar o valor: `( set -a; . ~/.config/traqueamento-organico/meta.env; curl -s -o /dev/null -w '%{http_code}\n' -H "Authorization: OAuth $META_TOKEN" https://graph.facebook.com/v27.0/me )` -> `200` é token bom.

## Oficial × não oficial (o dono decide)

| Caminho | Exemplos | Risco |
|---|---|---|
| Exportação oficial ("baixar seus dados") | Instagram, Facebook, TikTok, Google Takeout | Nenhum. Lenta (minutos a dias) e é uma foto do dia, não tempo real |
| API oficial | Meta Graph (publicar Reels, comentários, DM só depois que a pessoa escreve, 24 h), Pinterest API (seguidores, Pins), YouTube Data API (vídeo, inscritos públicos), TikTok Content Posting (app auditado) | Nenhum para a conta. Exige app de desenvolvedor e token; cada rede limita o que entrega (lista de seguidores só o Pinterest dá) |
| Script na sessão logada, só leitura | ler a lista de seguidores pelo navegador dela, devagar, e salvar um arquivo | Baixo a médio: contra os termos de uso; ritmo rápido dá bloqueio temporário (429) |
| API privada (como se fosse o app) | biblioteca instagrapi para DM de boas-vindas a quem começou a seguir | **Alto**: bloqueio de ação, verificação ("foi você?") ou restrição da conta. Limite baixo (ex.: 5 por rodada, 40 por dia) e parar no primeiro aviso |
| Automação de navegador/celular para publicar | subir vídeo no TikTok/Kwai por robô, compartilhar post da Página no perfil pessoal, figurinha de enquete no Story por emulador Android | Médio a alto: bloqueio ou perda de alcance; perfil pessoal é o mais sensível |

Ferramentas pagas de terceiros (ManyChat e parecidas) são oficiais por trás, mas dão acesso às mensagens a outra empresa: diga isso e deixe ela escolher.

## Armadilhas por rede (aconteceram de verdade)

| Rede | O que acontece | O que fazer |
|---|---|---|
| TikTok | Vídeo subido de servidor fora do Brasil fica com país de origem errado e recebe **0 visualizações** (31 vídeos zerados) | Publicar sempre por internet brasileira (casa/celular ou proxy BR) e recusar postar se o IP não for BR. Conferir: abrir a página pública do vídeo e procurar `locationCreated` |
| TikTok | Link na bio exige 1.000 seguidores **ou** conta comercial verificada; domínio escrito na bio é descartado em silêncio (salva, mas a bio velha fica) | Pedir a verificação da empresa (CNPJ/MEI) e pôr o link pelo app depois de aprovada. Não disfarçar o domínio |
| TikTok | @ só muda a cada 30 dias e nome a cada 7; bio até 80 caracteres; edição de bio demora para aparecer; web não tem campo de site nem troca para conta comercial | Planejar o @ antes; o resto pelo app |
| Instagram | O composer do site marca "Compartilhar no Facebook (perfil pessoal)" sozinho; o corte vem 1:1 | Desligar e escolher "Não compartilhar" a cada post; pôr 4:5 à mão |
| Instagram | Fixar post, reordenar a grade, link na bio, desarquivar post: **só no app** | Lista "para fazer no celular" no fim |
| Instagram | Nome só muda de novo depois de 60 dias; destaque guarda até 100 itens; a ordem dos destaques é a da última adição; o seletor do site não carrega stories muito antigos | Destaques novos no site ou pelo Meta Business Suite; antigos pelo app |
| Instagram | API oficial não dá a lista de seguidores, não avisa quem começou a seguir e não deixa mandar DM para quem nunca escreveu | Lista: exportação oficial. Boas-vindas: só respondendo quem escreve (oficial) ou API privada (risco alto) |
| Instagram | API oficial publica na hora, não agenda (limite de posts por 24 h) | Agendador próprio (`publicar.py`) ou Meta Business Suite |
| Instagram | "Comenta PALAVRA que eu te mando" sem resposta automática configurada = promessa quebrada em público | Só prometer direct onde há auto-DM; senão o CTA é só "Comenta PALAVRA" |
| Facebook | Token de Página não publica no perfil pessoal (não há API); "saudação" do Messenger foi descontinuada; monetização por conteúdo é só por convite (lista de espera) | Perfil pessoal só à mão; não prometer renda de monetização |
| Facebook | Agendamento pela API: até ~29 dias à frente e limite diário de posts | Agendar em lotes pequenos |
| YouTube | O @ desejado pode estar ocupado (variante com ponto); a URL antiga `/c/...` não sai; "conteúdo para crianças" é declaração do dono; o Studio mostra só inscritos públicos | Conferir o @ no site e no rodapé; a declaração ela mesma faz |
| Kwai | Site não edita perfil nem gerencia vídeos e não lista seguidores | Tudo pelo app; seguidores à mão (CSV) |
| Pinterest | Única rede cuja API dá a lista de seguidores; título até 100, descrição até 500; o gesto é salvar | Conta comercial + site verificado; CTA "Salva este Pin" |
| WhatsApp | Aparelho vinculado (WhatsApp Web, ferramentas tipo WAHA) recebe só ~3 meses de histórico; contatos novos aparecem como `@lid` sem número | Histórico inteiro: backup local do iPhone sem criptografia + Acesso Total ao Disco; `@lid` vira telefone pela agenda do próprio WhatsApp (o script faz) |
| WhatsApp | "áudio" sozinho pegava "manda um áudio"; propaganda em massa do próprio dono contava como conversa; conversas do trabalho entravam | Palavra fraca só conta em dupla; só conta o que a pessoa escreveu; `excluir_conversas` no nicho.json |
| Todas | Post "incerto" (a rede recebeu e a resposta não voltou) repetido sozinho = vídeo duplicado | Nunca repetir incerto; conferir no app e só então `publicar.py repetir` |
| Todas | Servidor com relógio em outro fuso posta na hora errada | Agenda sempre com fuso explícito |
| Todas | Navegador bloqueia o 2º download automático de um site; coletores no Console não conseguem enviar direto (CSP da rede) | Coletor salva 1 arquivo .json e a pessoa importa |

## Entrega
Responda curto: o que ficou pronto em cada parte, números agregados (leads por nível, por quantidade de redes, perfis conferidos, posts na agenda), o que é com ela no app, o que ficou pendente (exportação que ainda não chegou, verificação em análise) e os caminhos (`~/base-organica/painel-organico.html`, `agenda.json`). Lembre que o painel e o CSV têm dado pessoal e não devem ser publicados nem enviados.
