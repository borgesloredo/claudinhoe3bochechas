# Funil e recuperação

O que acontece depois que alguém deixa um contato: verificar o contato, mandar a sequência de e-mails, saber quando o e-mail voltou, lembrar pelo navegador e conferir tudo isso sozinho a cada poucas horas. A captura de formulário em si está em `rastreio-site.md`.

## 1. Isca gratuita com contato verificado

Quem recebe algo de graça (capítulo, e-book, aula) pode ter de deixar **nome, e-mail e telefone obrigatórios e verificados**. Pergunte ao dono se quer isso; se quiser:

- **Servidor decide**, o navegador só repete as checagens baratas para responder mais rápido.
- **Nome**: pelo menos 2 letras.
- **Telefone (Brasil)**: DDD real (tabela de DDDs válidos), celular com 11 dígitos começando com 9, fixo com 10 dígitos começando com 2–5; aceite o número com `+55`, com `0` na frente ou com código de operadora e normalize para `+55DDNNNNNNNNN`. Recuse sequências (`99999-9999`, `1234-5678`). Número estrangeiro só com `+` e o código do país (8 a 15 dígitos).
- **E-mail**:
  1. sintaxe;
  2. **erros de digitação comuns** dos provedores grandes (`gmial.com`, `hotmial.com`, `gmail.con`, `outlok.com`...) respondidos com uma **sugestão** do endereço corrigido, para a pessoa aceitar com um toque;
  3. **domínios descartáveis** (mailinator, yopmail, 10minutemail...) recusados;
  4. o domínio precisa **receber e-mail**: consulte o registro MX por DNS-over-HTTPS (ex.: `https://cloudflare-dns.com/dns-query?name=<dominio>&type=MX` com `accept: application/dns-json`, tempo limite ~4 s). Domínio inexistente (NXDOMAIN) ou MX nulo = recusa.
  - **Se a consulta de DNS falhar, deixe passar.** Perder uma pessoa real é pior do que aceitar um endereço ruim.
  - A caixa em si só se prova mandando: o link da isca indo para aquele endereço é a prova final.
- Endereço que já **voltou** (devolução permanente) ou marcou spam é recusado com a mesma resposta de "domínio não recebe e-mail".
- Teste com uma tabela de casos (telefones bons e ruins, typos, descartável, DNS fora do ar).

## 2. Sequência de e-mails (esteira)

Uma sequência só para todo mundo que deixou e-mail e não comprou: pediu a isca, preencheu o checkout e saiu, clicou em pagar e não pagou. Antes de criar ferramenta nova, veja se a sequência da isca já não serve de CRM.

- **Entrada**: captura com e-mail e sem atividade há ~2 h (e no máximo ~48 h, para não acordar contato velho sem querer); pedido não pago; pedido da isca.
- **Ritmo**: cada vez mais espaçado, ex.: dias 0, 2, 5, 9, 14, 21, 30, 60, 90, 120 (10 e-mails). Para na compra (inclusive compra feita no checkout externo) e no "sair".
- **Conteúdo típico**: entrega/lembrete, dúvidas frequentes, outros produtos, um cupom no meio e um maior no fim, uma pergunta para a pessoa responder, despedida.
- **Cupons**: uma **lista única** no backend (código, porcentagem, onde vale). O checkout pergunta ao servidor se o código vale e o servidor aceita exatamente o preço com aquele desconto. Quem já viu um desconto não deve receber um menor depois. Decida com o dono se o cupom vem pré-aplicado no link ou se a pessoa digita; se o checkout externo também tem cupom, crie os mesmos códigos lá.
- **Falha de envio**: tente de novo (ex.: até 3 vezes, 1 h depois) antes de desistir.
- A política de privacidade e a página da isca não podem prometer menos e-mails do que a sequência manda.

### Entregabilidade
- SPF, DKIM e DMARC certos no DNS do domínio que envia.
- **Domínio novo cai em spam** nas primeiras semanas mesmo com DNS certo. Peça ao dono para marcar "não é spam" nos primeiros testes e avise que isso melhora com o tempo e o volume.
- Links e descadastro **no seu domínio** (não no domínio genérico do backend): `https://SEU_DOMINIO/sair/` encaminhando para a função.
- Cabeçalhos `List-Unsubscribe` e `List-Unsubscribe-Post: List-Unsubscribe=One-Click` (descadastro com um clique, exigido por Gmail/Yahoo para remetentes em volume) e uma parte em texto puro.
- **Modo escuro**: Outlook/Hotmail invertem cores de cartões claros e deixam texto escuro sobre fundo preto. Funciona: tudo escuro com texto quase branco (inclusive rodapé), ou teste o layout claro no modo escuro dos principais leitores antes de mandar.

### Devoluções e spam
- Configure o webhook do provedor de e-mail (ex.: Resend: eventos `email.bounced` e `email.complained`) para uma função do backend.
- Confira a assinatura (Resend usa Svix: HMAC-SHA256 de `<svix-id>.<svix-timestamp>.<corpo>` com a parte base64 do segredo `whsec_...`; cabeçalho `svix-signature` com um ou mais `v1,<base64>`; recuse carimbo de hora com mais de 5 min de diferença).
- Marque o endereço como devolvido, pare a sequência dele e recuse esse endereço em novos formulários.
- Teste com os endereços de teste do provedor (ex.: `bounced@...`, `complained@...`) e apague as linhas de teste depois (com backup).
- A chave de envio costuma ser **só de envio**: ela não lista e-mails nem cria webhooks. O webhook é criado no painel do provedor, e o segredo de assinatura o dono salva pelo Terminal (ver `SKILL.md`).

## 3. Avisos no navegador (web push)

Remarketing sem anúncio para quem visitou o site e aceitou receber avisos.

### No site
- O cartão "quer receber avisos de desconto e dicas?" só aparece **depois do consentimento de cookies**, a partir da 2ª página da visita ou depois de ~40 s, e **nunca** no checkout, no painel ou na área de acesso. O banner de cookies vai primeiro.
- O pedido de permissão do navegador abre **só a partir do clique** no seu cartão (navegadores bloqueiam ou escondem pedidos que ninguém pediu). "Agora não" esconde por ~14 dias; permissão bloqueada = nunca mais pergunte.
- Aceitou: registre o `/sw.js`, inscreva com a chave pública VAPID e mande a inscrição ao backend com o último produto visto (esquecido depois de ~30 dias).
- O service worker cuida **só** de push: sem cache e sem `fetch`, assim ele nunca muda como as páginas carregam. Trate `push` (mostra a notificação), `notificationclick` (abre o link e conta o clique) e `pushsubscriptionchange` (reinscreve e manda a nova inscrição).
- **iPhone** (iOS 16.4+) só recebe push de site adicionado à Tela de Início, com `manifest.webmanifest`; no Safari comum `PushManager` não existe. Pergunte ao dono se quer um cartão explicando "Adicionar à Tela de Início" ou se prefere alcançar quem usa iPhone por e-mail e redes.
- O clique em "Permitir" é do dono no teste: o Chrome descarta sozinho o pedido quando o clique vem de automação ou extensão.

### No servidor
- Par de chaves **VAPID** (P-256). Pública no `avisos.js` do site; privada só como segredo do backend. Gere o par uma vez; se perder a privada, gere outro e troque a pública no site.
- Dá para enviar sem biblioteca, só com WebCrypto: assinatura VAPID (RFC 8292) e criptografia `aes128gcm` (RFC 8291 + RFC 8188). Coloque o **vetor de teste do apêndice A da RFC 8291** nos testes: é como você sabe que a criptografia está certa.
- O endpoint de inscrição é público, então:
  - aceite só endereços dos serviços de push conhecidos (`fcm.googleapis.com`, `updates.push.services.mozilla.com`, `*.notify.windows.com`, `*.push.apple.com`) e em `https`;
  - confira a chave do navegador (65 bytes começando com `0x04`, `auth` de 16 bytes) **com um ECDH de verdade**: alguns runtimes aceitam ponto inválido no `importKey`, e todo envio para essa linha falharia depois;
  - limite de inscrições novas por IP (com hash) e no site todo, por janela de 10 min;
  - corpo com tamanho máximo.
- Resposta 404/410 (e 400) do serviço de push = inscrição morta: apague a linha. Falha temporária = tente de novo depois (ex.: até 3 vezes).
- Lembrete automático ~24 h depois da inscrição, sobre o produto visto (um cupom pequeno funciona). Envio manual pelo painel (aba Avisos), para todos ou para um produto, com contagem de cliques.
- Política de privacidade com uma seção sobre os avisos.

## 4. Auditor do funil

Um trabalho agendado (ex.: a cada 2 h, por `pg_cron` ou cron do servidor) que **confere e corrige** o funil e grava o resultado para o painel (aba Saúde).

- Cada checagem roda isolada (uma falha não derruba as outras), **corrige o que puder** e só depois registra o que ainda está errado: `{id, nome, ok, detalhe, corrigidos?, itens?}`. Guarde cada rodada numa tabela (limpe depois de ~90 dias).
- Checagens que valeram a pena:
  - sequência de e-mails atrasada e passos que falharam 3 vezes;
  - varredura de formulários e checkouts abandonados que ficaram sem o 1º e-mail (ex.: últimos 30 dias);
  - **e-mail de acesso** de compra aprovada que não saiu: reenviar;
  - trabalhos agendados (cron) ativos e com última execução ok; trabalho pausado de propósito pelo dono aparece como informação, não como problema;
  - páginas principais do site e funções do backend respondendo;
  - **vitrine** — o que o comprador vê: para cada produto, o checkout próprio no ar, com o botão do checkout externo, sem o script da plataforma externa e com `og:image`; a página do checkout externo no ar com autor, preço e nome certos (ver `auditoria.md`);
  - relatório de outra máquina (ex.: um servidor que cuida das mensagens) chegou há pouco tempo.
- Relatório vindo de fora é **assinado** (HMAC com um segredo) e tem carimbo de hora recente (ex.: até 15 min), para um corpo antigo não ser reaproveitado.
- **Silencioso quando está tudo certo**; manda alerta (Telegram, e-mail) só quando sobra problema.
- O painel mostra a última rodada e tem um botão "Conferir agora".
- Teste as partes puras (resumo, regra de "quem ficou sem e-mail", vitrine) com casos falsos.
