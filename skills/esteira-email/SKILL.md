---
name: esteira-email
description: Use quando o usuário quiser uma esteira de e-mail automática para quem deixou o contato e ainda não comprou um produto digital (curso, e-book, mentoria) — 10 e-mails em 120 dias, cupons de 10, 20 e 30% que o comprador digita no checkout, recuperação de checkout abandonado, descadastro em um clique e tratamento de e-mail devolvido (bounce) e spam por webhook. Supabase Edge Functions + Resend + pg_cron. Dispare com "esteira de e-mail", "sequência de e-mails", "e-mail para lead", "nutrição", "nutrir leads", "recuperar quem não comprou", "follow-up por e-mail", "carrinho abandonado por e-mail", mesmo que a pessoa não diga "skill".
---

# Esteira de e-mail (10 e-mails em 120 dias)

## O que esta skill faz
Monta, no Supabase do usuário, uma sequência automática de e-mails para quem deixou nome e e-mail (formulário,
material grátis, checkout que não foi pago). Saem 10 e-mails nos dias 0, 2, 5, 9, 14, 21, 30, 60, 90 e 120: semanal
no começo, depois mensal, depois para. Três deles trazem cupom (10% no dia 14, 20% no dia 60, 30% no dia 120). A
pessoa sai da esteira na hora em que compra, clica em "não quero mais receber", ou quando o e-mail volta ou é marcado
como spam. Tudo isso já rodou em produção num negócio real de cursos digitais; os erros da tabela no fim aconteceram
de verdade.

| Arquivo | O que tem |
|---|---|
| `template/supabase/functions/_shared/config.ts` | **O único arquivo que sempre muda**: marca, domínio, produtos, preços, cupons, calendário |
| `template/supabase/functions/_shared/emails.ts` | Os 10 e-mails (assunto + texto) como modelo editável, e a variação de checkout abandonado |
| `template/supabase/functions/_shared/layout.ts` | Moldura do e-mail (tabelas + estilo inline) e a cópia em texto puro |
| `template/supabase/functions/_shared/esteira.ts` | A regra: próximo e-mail, parar em quem comprou, não duplicar, tentar de novo |
| `template/supabase/functions/esteira-seq/` | Chamada de hora em hora pelo cron: envia o que venceu |
| `template/supabase/functions/esteira-lead/` | Entrada (formulário do site) e saída (link de descadastro, 1 clique do Gmail) |
| `template/supabase/functions/esteira-volta/` | Webhook do Resend: bounce permanente e spam tiram o endereço da esteira |
| `template/supabase/migrations/20260101000000_esteira_email.sql` | Tabelas, visão `esteira_resumo` e o agendamento (pg_cron) |
| `template/supabase/config.toml.trecho` | `verify_jwt = false` das 3 funções |
| `template/formulario-exemplo.html` | Formulário mínimo para a página |
| `template/scripts/previa.ts` | Gera os 10 e-mails em HTML para revisar, sem enviar (`--teste` só confere) |
| `template/scripts/checar.sh` | Recusa o deploy se sobrou marcador de exemplo ou segredo no código |
| `referencias/CONTAS.md` | Passo a passo das contas: Supabase, Resend, domínio, SPF/DKIM/DMARC, chaves, webhook |

Caminho da skill: `K=~/.claude/skills/esteira-email`.

## Regras fixas
- **Chave nunca no chat.** O usuário salva pelo app Terminal com `read -rs` em `~/.config/esteira-email/<nome>.env`
  (modelo abaixo) ou direto como secret do Supabase dele. Nunca peça, mostre, copie nem imprima uma chave.
  ```bash
  mkdir -p ~/.config/esteira-email && printf 'Cole e tecle Enter: ' && read -rs k && printf 'NOME=%s\n' "$k" > ~/.config/esteira-email/<nome>.env && chmod 600 ~/.config/esteira-email/<nome>.env && echo && echo salvo
  ```
- O cupom **nunca** vem pré-aplicado: o link do e-mail abre o checkout pelo preço cheio e o texto manda digitar o código.
- Não envie e-mail de verdade, não aplique migration e não faça deploy sem o usuário dizer "pode". Os testes locais
  usam envio falso e banco falso.
- Antes de apagar linhas de teste do banco, salve um backup em JSON e confira que ele está completo.

## Passo 1: Conversa inicial (uma rodada só)
Pergunte numa chamada de AskUserQuestion, com o padrão como 1ª opção "(Recomendado)". Pule o que o pedido já respondeu.
| Campo | Padrão |
|---|---|
| produto(s) | nome, página de venda e checkout de cada um (vários produtos = uma entrada cada em `PRODUTOS`) |
| preço | R$ 97, pagamento único |
| cupons | VOLTA10 / VOLTA20 / VOLTA30 nos e-mails 5, 8 e 10 (dias 14, 60, 120). Se o material grátis já dá cupom, a esteira nunca oferece menos que ele |
| remetente | `Marca <contato@seudominio>`, respostas para o e-mail que a pessoa lê |
| material grátis | se existe (e-book, aula, capítulo) e o link; sem ele, o e-mail 1 vira boas-vindas |
| plataforma de pagamento | onde a venda acontece (Hotmart, Kiwify, Eduzz, Mercado Pago, checkout próprio): define como a esteira sabe que a pessoa comprou (passo 7) |

Depois siga sozinho até o fim. Decisões no meio do caminho: escolha a recomendada e conte no resumo.

## Passo 2: Contas e chaves
Siga `referencias/CONTAS.md`, seções 1 a 4, um passo por vez: Supabase (ref do projeto, CLI, login), Resend (conta,
domínio verificado com DKIM, SPF e DMARC, chave só de envio), segredo dos links e envio das chaves para o Supabase.
Pule o que já existe. Confira só os nomes: `supabase secrets list --project-ref <ref>`.

## Passo 3: Copiar o modelo para o projeto
```bash
P="<pasta do projeto do usuário>"   # onde fica (ou vai ficar) a pasta supabase/
mkdir -p "$P/supabase/functions" "$P/supabase/migrations" "$P/scripts"
cp -R "$K/template/supabase/functions/"* "$P/supabase/functions/"
cp "$K/template/supabase/migrations/"*.sql "$P/supabase/migrations/"
cp "$K/template/scripts/"* "$P/scripts/" && cp "$K/template/formulario-exemplo.html" "$P/"
```
- Projeto sem `supabase/`: rode `supabase init` antes.
- Já existe `_shared/` com arquivos de mesmo nome (`db.ts`, `config.ts`)? Copie para `_shared/esteira/` e ajuste os imports.
- Cole `template/supabase/config.toml.trecho` no fim de `supabase/config.toml`.
- **Renomeie a migration** com data e hora depois da última do projeto (`supabase migration list`) e troque
  `SEU-PROJETO` pelo ref no `cron.schedule`.

## Passo 4: Preencher config.ts e os textos
1. `config.ts`: marca, `SITE`, assinatura, linha legal (nome/CNPJ/cidade), garantia, catálogo, produtos, cupons.
2. `emails.ts`: troque os trechos em MAIÚSCULAS (itens do que a pessoa recebe, quem é você, resposta do celular) e
   ajuste o tom ao público. Texto é trabalho do agente: escreva, não devolva ao usuário para escrever. Cada fato
   (formato, prazo de acesso, garantia, funciona no celular) tem de bater com o produto de hoje.
3. Cores do `layout.ts` (`COR`): tudo escuro com texto claro, ou tudo claro com texto escuro. Nada de cartão branco em fundo escuro, nada de texto cinza.
4. Crie os cupons na plataforma de pagamento, em **todos** os produtos e ofertas, com o mesmo código e percentual, e
   teste cada um no checkout (preço cheio, com cupom, cupom inválido) antes do deploy.

## Passo 5: Testar sem chamada externa
```bash
cd "$P" && deno check supabase/functions/*/index.ts && deno test --allow-env supabase/functions
deno run --allow-env --allow-write scripts/previa.ts previa   # 10 e-mails em previa/*.html para ler
sh scripts/checar.sh                                            # tem de terminar em "ok"
```
Os testes cobrem: calendário dos 10 e-mails, parada em quem comprou, duas execuções sem e-mail duplicado, 3
tentativas em caso de erro, cupons (código, %, preço, nunca descendo, nunca no link), descadastro só com a chave certa,
assinatura do webhook e bounce temporário ignorado. Leia as prévias como texto (o HTML não precisa de navegador):
erro de português, preço errado e fato desatualizado contam como falha.

## Passo 6: Publicar (só com o "pode" do usuário)
```bash
supabase db push --project-ref <ref>     # cria as tabelas e o agendamento de hora em hora (minuto 17)
for f in esteira-seq esteira-lead esteira-volta; do supabase functions deploy $f --project-ref <ref>; done
```
- Webhook de devolução e spam: `referencias/CONTAS.md`, seção 5 (o usuário cria no painel do Resend).
- Descadastro no domínio do site (melhor para não cair no spam): redirecione `/sair/` para a função e deixe
  `SAIR_URL = SITE + "/sair/"` no `config.ts`. Vercel (`vercel.json`):
  `{"rewrites":[{"source":"/sair/","destination":"https://<ref>.supabase.co/functions/v1/esteira-lead"}]}`.
  Netlify (`_redirects`): `/sair/  https://<ref>.supabase.co/functions/v1/esteira-lead  200`. Sem como redirecionar,
  use o endereço da função direto no `SAIR_URL`.
- Ponha o formulário (`formulario-exemplo.html`) na página, com o ref e a chave do produto.

## Passo 7: Parar quando a pessoa compra
A esteira consulta `esteira_compras (email, produto)`. Escolha pela plataforma do passo 1:
- **Vendas numa tabela do Supabase** (checkout próprio): gatilho SQL na tabela de pedidos (troque nomes de tabela, status e colunas):
  ```sql
  create or replace function esteira_marca_compra() returns trigger language plpgsql security definer as $$
  begin
    if new.status = 'approved' then
      insert into esteira_compras (email, produto) values (lower(new.email), new.produto) on conflict do nothing;
    end if;
    return new;
  end $$;
  create trigger esteira_compra after insert or update on pedidos for each row execute function esteira_marca_compra();
  ```
- **Hotmart, Kiwify, Eduzz, Mercado Pago**: escreva uma função `esteira-compra` pequena no mesmo estilo de
  `esteira-volta`: confere o token ou a assinatura do webhook da plataforma (Hotmart manda `X-HOTMART-HOTTOK`), lê
  e-mail + produto da compra aprovada e grava em `esteira_compras`. Cubra **todas** as plataformas onde o produto é vendido.
- Quem compra por fora (Pix direto, WhatsApp): `insert into esteira_compras values ('email', 'produto');` no SQL Editor.

## Passo 8: Recuperar checkout abandonado (opcional)
O checkout manda `POST esteira-lead {email, nome, produto, origem: "checkout"}` assim que a pessoa digita o e-mail.
O e-mail 1 ("ficou alguma dúvida?") sai 2 h depois, pelo cron, e só se a compra não entrou. Daí segue a esteira normal.

## Passo 9: Teste de ponta a ponta (com o "pode" do usuário)
Use os endereços de teste do Resend, que não chegam a ninguém:
1. Formulário com `delivered@resend.dev`: chega o e-mail 1 (Resend > Emails mostra "Delivered").
2. Para ver os próximos sem esperar dias: `update esteira_leads set proximo_em = now() where email = 'delivered@resend.dev';`
   e chame `curl -s -X POST https://<ref>.supabase.co/functions/v1/esteira-seq`. Repita até `proximo_em` ficar nulo.
3. `bounced@resend.dev` e `complained@resend.dev`: cada um tem de aparecer em `email_devolvido` e sair da esteira.
4. Backup das linhas de teste (`select ... ` salvo em JSON), confira, e só então apague-as de `esteira_leads`,
   `email_devolvido` e `esteira_compras`.
5. Mande 1 e-mail real para a caixa do próprio usuário (Gmail e Outlook/Hotmail, celular com modo escuro) e confira
   leitura, botão, link de descadastro e se caiu no spam.

## Passo 10: Acompanhar
- Situação de todo mundo: `select * from esteira_resumo;` no SQL Editor do Supabase.
- O cron está rodando? `select status, return_message, start_time from cron.job_run_details order by start_time desc limit 5;`
- Logs das funções: painel do Supabase > Edge Functions > esteira-seq > Logs ("ENVIO FALSO", "envio falhou").
- Pausar tudo: `select cron.unschedule('esteira-seq');`. Mudar o horário: `unschedule` e `cron.schedule` de novo.
- Mudou preço, garantia ou formato do produto? Revise `config.ts` e `emails.ts` no mesmo dia, rode o passo 5 e publique de novo.

## Erros comuns (todos aconteceram de verdade)
| Erro | Correção |
|---|---|
| Cupom pré-aplicado no link (`?cupom=`) | O dono queria que o comprador digitasse o código. Link sempre sem cupom; o e-mail diz o código, o % e "digite no checkout". Teste em `emails_test.ts` |
| Cupom do e-mail não existe na plataforma: checkout diz "inválido" | Criar o código em todos os produtos e ofertas antes de ligar a esteira. Na Hotmart o campo de % tem máscara: digite `2000` para 20,00% |
| Checkout novo publicado antes do servidor: "Aplicar" dizia inválido | Publique primeiro o servidor que valida o cupom, depois as páginas |
| E-mail ilegível no Hotmail com modo escuro (cartão branco virou preto com texto escuro) | Tudo escuro + texto quase branco (ou tudo claro), fundo e cor declarados em cada bloco |
| Rodapé em cinza ilegível no fundo escuro | Todo texto perto do branco; nada de cinza médio |
| Todos os e-mails de teste no spam, mesmo com SPF/DKIM/DMARC certos | Domínio novo sem reputação + link `*.supabase.co`. Links só no domínio próprio (`/sair/` redirecionado), parte em texto puro, List-Unsubscribe-Post, volume baixo no começo, e as primeiras pessoas (o dono incluso) marcam "não é spam" |
| Tabela de DNS de tutorial antigo (MX amazonses) não verificava | Copiar exatamente os registros que a tela do Resend mostra hoje |
| Webhook de devolução respondendo 401 em tudo | Faltava criar o webhook no painel do Resend e salvar o `whsec_` em `RESEND_WEBHOOK_SECRET`. A chave só de envio não cria webhook pela API |
| E-mail duplicado com duas execuções do cron | Marcar a etapa (`etapa=eq.<atual>`) antes de enviar; quem não conseguiu marcar não envia |
| Falha no envio fazia o lead pular um e-mail | Voltar para a etapa anterior e tentar de novo em 1 h, até 3 vezes (`falhas`) |
| Formulário sem o produto no campo certo: o lead nunca entrava na esteira | O formulário sempre manda `produto` com uma chave de `PRODUTOS`; a função responde 400 se não manda |
| Texto do e-mail desatualizado (dizia "só no computador" depois que passou a abrir no celular) | Revisar `emails.ts` sempre que o produto muda |
| Material grátis dava 20% e a esteira oferecia 10% depois | O desconto nunca desce ao longo da esteira (teste em `emails_test.ts`) |
| Migration com o mesmo número de outra branch | Numerar depois da última aplicada (`supabase migration list`) |
| Painel com rótulo ambíguo ("não enviou" lido como "e-mail falhou") | Situações com nome claro, como na visão `esteira_resumo` |
| Linhas de teste esquecidas no banco | Backup em JSON, conferir, apagar no fim do teste |

## Entrega
Responda com: o que foi instalado (funções, tabelas, cron), a tabela dos 10 e-mails (dia | assunto | cupom), o
resultado dos testes, os caminhos das prévias, e o que depende do usuário (DNS, webhook, cupons na plataforma, "pode"
para publicar, marcar "não é spam" no primeiro e-mail).
