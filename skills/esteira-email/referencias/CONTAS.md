# Contas e chaves: passo a passo para o usuário

Guie um passo por vez, em texto simples. Espere a pessoa dizer que terminou antes do próximo.
**Regra fixa: nenhuma chave passa pelo chat.** Toda chave vai do site direto para um arquivo no Mac pelo app Terminal
(`read -rs` não mostra o que foi colado) ou direto para o Supabase dela (`supabase secrets set`). Nunca peça, mostre,
copie ou imprima o valor de uma chave; para conferir, use só "existe / não existe".

## 1. Supabase (o servidor)
1. Crie a conta em https://supabase.com (plano grátis serve) e um projeto. Anote o **ref** do projeto: é o pedaço
   `xxxxxxxx` do endereço `https://xxxxxxxx.supabase.co` (Project Settings > General). O ref não é segredo.
2. Instale a ferramenta de linha de comando: `brew install supabase/tap/supabase`.
3. Entre na conta: `supabase login` (abre o navegador, a pessoa autoriza). Sem navegador, crie um token em
   https://supabase.com/dashboard/account/tokens e salve assim:
   ```bash
   mkdir -p ~/.config/esteira-email && printf 'Cole o token do Supabase e tecle Enter: ' && read -rs k && printf 'SUPABASE_ACCESS_TOKEN=%s\n' "$k" > ~/.config/esteira-email/supabase.env && chmod 600 ~/.config/esteira-email/supabase.env && echo && echo salvo
   ```
   Depois, cada comando `supabase` roda com `set -a; . ~/.config/esteira-email/supabase.env; set +a; supabase ...`.
4. Na pasta do projeto: `supabase link --project-ref <ref>` (pede a senha do banco; a pessoa digita no Terminal).

## 2. Resend (quem entrega os e-mails)
1. Crie a conta em https://resend.com (tem plano grátis com limite diário e mensal; confira o atual em resend.com/pricing).
2. **Domain > Add domain**: use um subdomínio ou o domínio do site (ex.: `seudominio.com.br`). Região: a mais perto
   do público (São Paulo, `sa-east-1`, para o Brasil).
3. O Resend mostra os registros de DNS. Copie **exatamente o que a tela mostrar** no painel onde o domínio está
   (Registro.br, Cloudflare, Hostinger, GoDaddy...). Os nomes mudam de tempos em tempos: tutorial antigo com tabela
   de MX/amazonses já estava desatualizado. Hoje costuma ser:
   - **DKIM**: TXT `resend._domainkey` com uma chave longa. Prova que o e-mail saiu de você.
   - **SPF / retorno**: registros no subdomínio `send` (MX e TXT `v=spf1 include:...`, ou CNAMEs). O SPF diz quais
     servidores podem mandar e-mail pelo seu domínio. Ele fica no subdomínio `send`: **não crie um segundo SPF na raiz**.
     Se a raiz já tem SPF (Google Workspace, ImprovMX, Hostinger), deixe como está.
   - **DMARC**: crie você mesmo, se a tela não pedir: TXT `_dmarc` com `v=DMARC1; p=none;`. Diz aos provedores o que
     fazer com e-mail falso no seu nome. Comece com `p=none`; depois de um mês sem problema, `p=quarantine`.
4. Clique em **Verify**. DNS leva de minutos a algumas horas. Só siga quando o domínio ficar **Verified**.
5. **API Keys > Create API key**, permissão **Sending access** (só envio: se vazar, ninguém lê nem apaga nada).
   Salve sem passar pelo chat:
   ```bash
   mkdir -p ~/.config/esteira-email && printf 'Cole a chave do Resend e tecle Enter: ' && read -rs k && printf 'RESEND_API_KEY=%s\n' "$k" > ~/.config/esteira-email/resend.env && chmod 600 ~/.config/esteira-email/resend.env && echo && echo salvo
   ```
6. Caixa para as respostas: os e-mails pedem "responda este e-mail". O `ESTEIRA_RESPONDER_PARA` precisa ser uma caixa
   que a pessoa lê (Gmail, Outlook, ou `contato@seudominio` redirecionado de graça pelo ImprovMX).

## 3. Segredo dos links de descadastro
Gerado no próprio Mac, sem ninguém ver:
```bash
mkdir -p ~/.config/esteira-email && printf 'ESTEIRA_SEGREDO=%s\n' "$(openssl rand -hex 32)" > ~/.config/esteira-email/esteira.env && chmod 600 ~/.config/esteira-email/esteira.env && echo salvo
```

## 4. Mandar as chaves para o Supabase
```bash
set -a; . ~/.config/esteira-email/supabase.env 2>/dev/null; set +a
for f in resend esteira; do supabase secrets set --project-ref <ref> --env-file ~/.config/esteira-email/$f.env; done
supabase secrets set --project-ref <ref> ESTEIRA_REMETENTE="Sua Marca <contato@seudominio.com.br>" ESTEIRA_RESPONDER_PARA="voce@seuemail.com.br" ESTEIRA_ORIGENS="https://seudominio.com.br,https://www.seudominio.com.br"
supabase secrets list --project-ref <ref>   # mostra só os nomes, nunca os valores
```
Remetente, resposta e origens não são segredo. As outras três chaves só passam pelo arquivo.

## 5. Webhook de devolução e spam (depois do deploy)
A chave de envio não cria webhook (permissão só de envio). A pessoa cria no painel:
1. Resend > **Webhooks > Add endpoint**. URL: `https://<ref>.supabase.co/functions/v1/esteira-volta`.
   Eventos: **email.bounced** e **email.complained**. Salve.
2. Abra o webhook criado, copie o **Signing secret** (começa com `whsec_`) e salve:
   ```bash
   printf 'Cole o signing secret e tecle Enter: ' && read -rs k && printf 'RESEND_WEBHOOK_SECRET=%s\n' "$k" > ~/.config/esteira-email/webhook.env && chmod 600 ~/.config/esteira-email/webhook.env && echo && echo salvo
   supabase secrets set --project-ref <ref> --env-file ~/.config/esteira-email/webhook.env
   ```
Sem esse segredo, a função recusa toda chamada (401): é o esperado até este passo.

## Outro provedor no lugar do Resend
Só `enviar()` em `_shared/envio.ts` fala com o Resend, e só `esteira-volta` + `_shared/volta.ts` leem o webhook.
Para Brevo, SendGrid, Amazon SES ou Postmark: troque a chamada `fetch` de `enviar()` pela API do provedor (mantenha
`html`, `text` e os cabeçalhos List-Unsubscribe) e adapte `voltaDoEvento` + a conferência de assinatura ao formato do
webhook dele. Os testes de `volta_test.ts` mostram o que precisa continuar valendo.
