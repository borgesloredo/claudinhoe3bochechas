# Buscar o lead orgânico

Objetivo: uma lista única de pessoas que já seguem ou conversam com o perfil, com nota, para falar primeiro com quem está mais quente e é do nicho. Tudo local, no Mac da pessoa, num SQLite (`base-organica.sqlite`, permissão 600).

## De onde vem cada rede

| Rede | Como pegar | O que vem | O que não vem |
|---|---|---|---|
| Instagram | Central de Contas > Suas informações e permissões > Baixar suas informações > escolher a conta > "Algumas das suas informações" > **Seguidores e seguindo** > Baixar no dispositivo > Desde o início > **JSON**. O link vale 4 dias | `followers_1.json` (`_2`, `_3`... em conta grande) e `following.json`, dentro do zip | Nome, bio, contato, comentários de outras pessoas |
| Instagram (interações) | API oficial (conta profissional ligada a uma Página): `GET /{ig-user-id}/media` e `GET /{media-id}/comments?fields=username,timestamp`. Salvar em CSV (ver formato abaixo), sem o texto | Quem comentou em cada post | Curtidas por pessoa, lista de seguidores |
| Facebook (perfil) | Central de Contas, mesma tela, perfil do Facebook > **Amigos e seguidores** > JSON | `your_friends.json` e listas de seguidores: só o **nome** | @, contato. Página não exporta seguidores |
| TikTok | App > Perfil > menu > Configurações e privacidade > Conta > **Baixar seus dados** > JSON > Solicitar; depois aba "Baixar dados" | `user_data_tiktok.json` com `FansList` (seguidores) e `Following` | Nome, bio, contato |
| YouTube | Studio > Painel > Inscritos recentes > **Ver todos**: só quem deixou a inscrição pública. Copiar para CSV (`usuario;nome`). Comentários: Studio ou YouTube Data API (`commentThreads`) | Parte dos inscritos | Lista completa (o Google Takeout traz quem **você** segue, não quem te segue) |
| Kwai | Só no app; o site não lista seguidores | Nada automático | Tudo: CSV à mão se valer a pena |
| Pinterest | API oficial v5 (lista de seguidores da conta; app de desenvolvedor aprovado + token). Ou CSV à mão | Seguidores com @ | Contato |
| WhatsApp (conversa) | Abrir a conversa > nome do contato/grupo > **Exportar conversa** > **Sem mídia**. iPhone gera `.zip`, Android `.txt` | Quem escreveu, quando, o texto (o script só usa para achar o nicho e **não grava**) | Nada além daquela conversa |
| WhatsApp (contatos) | App Contatos do Mac/iPhone > selecionar > Exportar vCard (`.vcf`) | Nome, telefone, e-mail, empresa | — |
| WhatsApp (histórico inteiro) | Backup local do iPhone no Mac: Finder > iPhone > Geral > "Fazer backup de todos os dados do iPhone neste Mac", **sem** "Criptografar backup local" > Fazer backup agora. Ajustes do Sistema > Privacidade e Segurança > **Acesso Total ao Disco** > ligar o Terminal | Todas as conversas, do WhatsApp comum e do Business, desde sempre | — |

Aparelho vinculado (WhatsApp Web ou ferramentas que usam a sessão do Web) só recebe uns 3 meses de histórico e mostra contatos novos como `@lid` (sem número). Por isso o histórico inteiro vem do backup do iPhone, onde a agenda do próprio WhatsApp (`ContactsV2.sqlite`) traduz `@lid` em telefone. Android não tem backup local legível (o do Google Drive é criptografado): use conversa exportada.

### Script na sessão logada (não oficial, só se o dono aceitar)
Quando a rede não exporta (seguidores do Kwai, interações), dá para escrever um script que roda no Console do navegador **dela**, logada, e lê a lista pelas chamadas internas do próprio site, devagar (uma página a cada 2 a 5 s, parar no primeiro erro 429), salvando **um** arquivo `.json` que depois vira CSV. É contra os termos de uso da rede (risco de bloqueio temporário). Só leitura: nunca seguir, curtir ou mandar mensagem por script. A rede bloqueia envio direto para outro site (CSP) e o navegador bloqueia o segundo download automático: um arquivo por coleta.

## Formatos que o `base_organica.py importar` entende

- `.zip` do "baixar seus dados": lido em memória, sem extrair; pega `followers*.json`, `following*.json`, `user_data*.json`, amigos do Facebook, `.vcf`, `.csv` e conversas do WhatsApp lá dentro.
- `.json` solto das mesmas exportações.
- `.vcf`: vira **agenda** (só para achar telefone e e-mail de quem aparece pelo nome). `--como-leads` quando o vCard já é uma lista de leads que ela filtrou.
- `.txt` (ou `_chat.txt` dentro do zip): conversa do WhatsApp, formato iPhone `[17/11/2026, 10:00:00] Nome: texto` ou Android `17/11/2026 10:00 - Nome: texto`. Ela diz quem é ela em `meu_nome_no_whatsapp` (ou `--eu`). Conversa 1:1 = 1 interação `dm` com a quantidade de mensagens do nicho; grupo = 1 `comentario` por mensagem do nicho.
- `.csv` de qualquer rede (separador `,` `;` ou tab). Colunas reconhecidas: `rede`, `usuario`/`handle`/`@`, `nome`, `email`, `telefone`/`whatsapp`, `bio`, `segue` (0/1). Com `tipo` preenchido a linha é interação: `tipo` (comentario, curtida, dm, mencao, compartilhou, salvou), `ref` (id do post/comentário, evita contar 2 vezes), `quando` (AAAA-MM-DD), `qtd`.

## Só é lead quem é do nicho
- Palavras no `nicho.json`: **fortes** (só quem é do nicho fala: "mesa de som", "mixag*") contam sozinhas; **fracas** ("som", "banda", "curso") só em dupla. `*` no fim = qualquer final. Sem acento e sem maiúscula.
- Conversa: só entra quem **escreveu** sobre o nicho. Mensagem dela própria não conta (propaganda em massa enviada pelo dono fazia todo mundo parecer lead). Conversas de trabalho e família saem por `excluir_conversas` (pelo nome da conversa ou quando o termo aparece em 2% das mensagens).
- Erros reais que viraram regra: "áudio" sozinho pegava "manda um áudio"; uma citação solta de uma palavra excluída não pode tirar uma conversa inteira.

## União (a mesma pessoa em redes diferentes)
Nunca junta dois perfis da mesma rede.
- **Certa**: mesmo @ sem `.` `_` `-` (`ana.souza` = `ana_souza`), mesmo e-mail, mesmo telefone (últimos 11 dígitos).
- **Provável**: @ muito parecido (Jaro-Winkler >= 0,93, 5+ letras, mesmas 3 primeiras) com nome parecido quando os dois têm nome; ou mesmo nome completo (2+ palavras), que é o único elo do Facebook e de quem aparece só pelo nome. O painel marca "(provável)".
- Junção errada: `separar rede:handle` tira aquele perfil de qualquer união.
- Na prática a união por nome entre redes é rara (no projeto de origem, 7 de ~480 pessoas do WhatsApp casaram com o Instagram): o telefone e o e-mail é que unem.

## Nota (aquecimento + nicho)

| Sinal | Pontos |
|---|---|
| Segue em cada rede (agora) | +10 por rede, +10 por rede além da primeira |
| Comentário | +6 cada (até 10) |
| Curtida | +1 cada (até 30) |
| Conversa (dm) | +15 cada (até 3) |
| Menção, compartilhou | +8 cada (até 5) |
| Salvou | +4 cada (até 5) |
| Interagiu nos últimos 30 dias | +10 |
| Tem e-mail ou telefone | +5 |
| Fala do nicho (termo forte na bio/nome ou em conversa) | +15; perto do nicho (2 fracos na bio) +8 |
| Interessado num produto (ajuste `interesse`) | +40 |
| Deixou de seguir | -10 por rede |

Níveis: menos de 15 **frio**, 15-34 **morno**, 35-59 **quente**, 60+ **fervendo**. Quem comprou (ajuste `cliente`) vira **cliente** e continua somando pontos (serve para oferta seguinte). O ranking padrão esconde os frios (`--todos` mostra).

## Grupo Pessoal (escondido, nunca apagado)
Vai para "Pessoal" quem bate em `pessoal_palavras` (sobrenome da família) no nome ou @, ou quem ela segue de volta se `voce_segue_e_pessoal` for `true` (útil quando o Instagram era pessoal antes de virar comercial), ou quem ela marcou: `pessoal rede:handle "motivo"`. `pessoal rede:handle --tirar` devolve ao ranking e vence as regras. Se ela marcar alguém como pessoal de propósito, não "conserte".

## Painel (aba Orgânico)
- (a) **HTML local**: `painel painel-organico.html`. Abre no navegador, sem internet: resumo, filtro por nível, busca, links para cada perfil e para o WhatsApp, grupo Pessoal num botão. Tem dado pessoal: não publicar como página, não mandar por e-mail.
- (b) **Painel próprio**: `painel organico.json` gera `{gerado_em, fontes, resumo, leads[], pessoal[]}`; cada lead tem `id`, `nome`, `perfis[{chave, rede, handle, url, segue, uniao}]`, `email`, `telefone`, `interacoes`, `ultima_interacao`, `pontos`, `nivel`, `motivos[]`, `pessoal`. Se o painel fica num servidor (ex.: Supabase da skill irmã traqueamento-e-trafego-pago), crie as tabelas com RLS ligado e **sem** policy pública (só a função do servidor lê e escreve), proteja a aba com senha e guarde só o JSON calculado:
  ```sql
  create table org_resultado (id int primary key default 1, dados jsonb not null, gerado_em timestamptz default now());
  alter table org_resultado enable row level security;  -- sem policy: só service role
  ```
- (c) só CSV: `ranking --csv ranking.csv`.

## Rotina
Uma vez por mês: nova exportação de cada rede e `importar` de novo (é idempotente: importar 2 vezes não duplica). A lista completa de seguidores marca quem deixou de seguir. Conversas novas do WhatsApp: exportar só as conversas novas ou fazer novo backup.

## LGPD (resumo para explicar à pessoa)
- Base legal: legítimo interesse para falar com quem já se relaciona com o perfil, sobre o assunto do perfil. Uso próprio, nada de vender, emprestar ou cruzar com lista comprada.
- Mínimo necessário: @, nome, contato público ou dado pela própria pessoa, contagem de interações. Texto de conversa nunca vai para o banco (só os termos do nicho que bateram).
- Origem guardada (`email_origem`, `telefone_origem`: `perfil:<rede>`, `bio:<rede>`, `agenda`, `whatsapp`).
- Saída fácil: toda primeira mensagem oferece "responde SAIR". Quem pedir: `descadastrar <e-mail | telefone | rede:handle>` apaga a pessoa em todas as redes unidas e guarda só um código (hash) para ela não voltar numa importação futura. Depois, gere o painel/CSV de novo e apague as cópias antigas.
- Segurança: banco, CSV e painel com permissão 600, fora de pasta sincronizada pública e fora do git.
