# Plataformas: onde criar, o que copiar, que acesso dar

Para cada rede: **ID público** (vai no script do site), **segredo do servidor** (vai para o gerenciador de segredos do backend, salvo antes pelo dono em `~/.config/traqueamento-e-trafego-pago/<NOME>.env`, como explica o `SKILL.md`), **acesso de leitura** (para o painel) e **armadilhas** já encontradas.

Os menus mudam com frequência. Se um caminho não existir mais, procure pelo nome da função na busca do próprio painel da plataforma.

**Antes de criar qualquer conta, confira qual conta está logada.** No Google, o navegador pode ter várias contas (`authuser=0`, `authuser=1`); criar GA4, Ads ou Search Console na conta de outra pessoa ou organização obriga a refazer tudo depois e a apagar o que ficou do outro lado.

## Índice
1. Google Analytics 4
2. Google Ads
3. Google Search Console
4. Meta (Facebook/Instagram)
5. TikTok
6. Pinterest
7. Microsoft Ads (UET) e Microsoft Clarity
8. Bing Webmaster Tools e IndexNow
9. Armadilhas gerais de painel de anunciante
10. Checkout externo como 2ª opção (Hotmart e parecidos)

---

## 1. Google Analytics 4

- **ID público:** `G-XXXXXXX`. Fica em Admin → Fluxos de dados → Web.
- **Segredo do servidor:** API secret do Measurement Protocol. Fica no mesmo fluxo, em "Chaves secretas da Measurement Protocol API".
- **Leitura pelo painel:** crie um projeto no Google Cloud e ative a **Google Analytics Data API** e a **Search Console API**. Depois:
  1. Crie uma **conta de serviço** e baixe a chave JSON.
  2. Guarde o JSON inteiro como um segredo só (ex.: `GOOGLE_SA_JSON`).
  3. Guarde o **ID numérico da propriedade** (não o G-) em outro segredo (ex.: `GA4_PROPERTY_ID`).
- **Permissão:** adicione o e-mail da conta de serviço como **Leitor**.
  - **Armadilha:** a página de usuários *da propriedade* às vezes fica em branco ou dá erro de JavaScript. Adicione no **nível da conta**: a permissão herda para a propriedade.
  - **Não marque** "Sem métricas de custo", ou o painel perde o gasto do Google Ads.
- **Gasto do Google Ads sem API do Ads:** vincule Google Ads ↔ GA4 (Admin → Vinculações de produtos). A Data API passa a devolver `advertiserAdCost`, `advertiserAdImpressions` e `advertiserAdClicks` por campanha. Isso evita o *developer token* do Google Ads, que exige aprovação demorada.
- **Canal das visitas:** use a dimensão `sessionDefaultChannelGroup`. Ela já separa Paid Search, Organic Search, Paid Social, Organic Social, Direct, Referral e outros.
- **Eventos-chave:** marque `purchase` e `generate_lead` como eventos-chave (conversões).

## 2. Google Ads

- **IDs públicos:**
  - a tag `AW-XXXXXXXXX`;
  - um **rótulo** por ação de conversão. Crie "Compra" e "Lead" em Metas → Conversões → Site → configuração manual.
- **Conversões otimizadas** (enhanced conversions): ative na ação de conversão. A tag passa e-mail/telefone com hash.
- **Importe as conversões do GA4** só se *não* usar a tag direta para a mesma ação. Senão a conversão conta duas vezes.
- **Auto-tagging** (gclid) ligado na conta.
- **Faturamento:** o país e a moeda da conta não mudam depois de criados. Crie a conta já na moeda certa.
- **Cobranças pequenas no cartão** logo depois de cadastrar (ex.: duas de valor baixo) costumam ser reservas de autorização; somem sozinhas em até ~7 dias. Avise o dono antes que ele estranhe.
- **Ações de conversão:** "Compra" como principal, contando todas; "Lead" contando uma por pessoa.

## 3. Google Search Console

- **Verificação:**
  - pelo arquivo HTML `googleXXXX.html` na raiz do site; ou
  - por DNS (TXT), se quiser a propriedade de **domínio**, que cobre todos os subdomínios e o http/https.
- **Sitemap:** envie `https://seudominio.com.br/sitemap.xml`.
- **Leitura pela API:** adicione a conta de serviço como usuário **Restrito** (só leitura).
  - **Armadilha:** a API distingue os dois tipos de propriedade.
    - Prefixo de URL usa `https://seudominio.com.br/`, com a barra final.
    - Domínio usa `sc-domain:seudominio.com.br`.
  - Use o formato do tipo que você criou, senão a API dá 403.

## 4. Meta (Facebook / Instagram)

- **ID público:** o ID do Pixel, também chamado de "conjunto de dados". Fica no Gerenciador de Eventos.
- **Segredo do servidor:** token da API de Conversões. Gere em Gerenciador de Eventos → pixel → Configurações → "Gerar token de acesso".
- **Leitura pelo painel:** use a Marketing API com um **usuário do sistema**:
  1. Abra Configurações do Negócio (portfólio) → Usuários → Usuários do sistema → Adicionar.
  2. Atribua ao usuário a **conta de anúncios** (permissão de visualizar) e o **app**.
  3. Gere um token com a permissão `ads_read`, com expiração "nunca".
  4. Guarde o token e o ID da conta de anúncios (`act_XXXX`) como segredos.
  - Para o painel mostrar seguidores do Instagram e custo por seguidor, guarde também o ID do usuário do Instagram profissional (`IG_USER_ID`); o mesmo token lê `followers_count`.
- **Armadilha:** o botão "Gerar token" fica desabilitado. Passando o mouse aparece o aviso de que o app precisa fazer parte do portfólio.
  - Solução: em Contas → Apps, **conecte o app existente ao portfólio**.
  - Depois, atribua o app ao usuário do sistema.
- **Domínio:** verifique o domínio no portfólio (Segurança da marca → Domínios), por meta tag ou DNS.
- **Atribuição:** o Meta adiciona `fbclid` a todo link de saída, inclusive de post orgânico.
  - Nos anúncios, coloque nos **parâmetros de URL** do anúncio: `utm_source=meta&utm_medium=paid&utm_campaign={{campaign.name}}`.
  - Sem isso, a venda de anúncio aparece como orgânica no painel.

## 5. TikTok

- **ID público:** o código do Pixel. Fica em Gerenciador de Eventos → Web.
- **Segredo do servidor:** o access token da **Events API**. Fica nas configurações do mesmo pixel.
- **Leitura pelo painel:** a TikTok **Marketing API** exige um app de desenvolvedor.

### Criar o app de desenvolvedor
1. Cadastre-se em `business-api.tiktok.com` (portal de desenvolvedor).
   - **Armadilha:** o cadastro recusa e-mail gratuito (Gmail, Hotmail, Outlook). Use um e-mail do seu domínio. Um encaminhamento (ImprovMX, Cloudflare Email Routing) basta para receber o código.
2. Crie o app pedindo **só o escopo de Reporting** (leitura de relatórios). Informe uma URL de redirecionamento sua, por exemplo a home do site. A aprovação costuma levar de horas a 1–2 dias.
3. Aprovado o app, abra a **URL de autorização** do app logado com o usuário dono da conta de anúncios e autorize.
   - O redirecionamento traz `auth_code=...` na URL.
4. Troque o código pelo token de longa duração:
   ```
   POST https://business-api.tiktok.com/open_api/v1.3/oauth2/access_token/
   { "app_id": "...", "secret": "...", "auth_code": "..." }
   ```
   - A resposta traz `access_token` e `advertiser_ids`.
   - O código expira em minutos e vale uma vez só. Faça a troca num script que o dono roda no Terminal: ele cola o `auth_code` com `read -rs`, e o script grava o token direto em `~/.config/traqueamento-e-trafego-pago/TIKTOK_ADS_TOKEN.env` (e no backend), sem mostrar na tela.

### Ler o relatório
```
GET /open_api/v1.3/report/integrated/get/
```
- Parâmetros:
  - `advertiser_id`
  - `report_type=BASIC`
  - `data_level=AUCTION_CAMPAIGN`
  - `dimensions=["campaign_id","stat_time_day"]`
  - `metrics=["campaign_name","spend","impressions","clicks","complete_payment"]`
  - `start_date` e `end_date`
  - `page` e `page_size`
- Mande o cabeçalho `Access-Token: <token>`.
- **Armadilha:** relatório diário aceita no máximo **30 dias por chamada** (`code 40002`).
  - Divida o período em janelas de até 30 dias.
  - Pagine cada janela.
- **Armadilha:** erro vem com HTTP 200 e `code ≠ 0`. Sempre cheque `code`.

### Armadilhas de conta
- **Autorização bloqueada pedindo para vincular e-mail:** o usuário do TikTok for Business precisa ter e-mail vinculado. Isso exige verificação por telefone.
  - Depois de vincular, a interface pode cair em **chinês**. Troque o idioma no menu do perfil ou pela URL `?lang=pt-BR` / `en`.
- **Business Center exige verificação em duas etapas (2SV)** para os membros. Ative no perfil e defina senha antes de convidar ou gerar acesso.
- **Aviso "contrato pendente" / conta não pode veicular:** quase sempre faltam **dados de faturamento**: razão social, CPF/CNPJ e endereço. Preencha em Pagamentos → Informações de cobrança e o aviso some.
- **Nome antigo aparecendo** (conta, usuário, Business Center): cada um tem seu próprio campo de nome. Padronize os três.
  - Campos de texto em painéis React às vezes ignoram digitação automatizada. Preencha à mão.

## 6. Pinterest

- **ID público:** o ID da tag. Fica em Gerenciador de anúncios → Conversões → Tag.
- **Verificação do domínio:** uma meta tag `p:domain_verify` na home. Também serve para "reivindicar" o site no perfil.
- **Segredo do servidor:**
  - token da API de Conversões. Gere em Gerenciador de anúncios → Conversões → "Gerar token";
  - o ID da conta de anúncios.
- **Leitura pelo painel:**
  1. Crie um app em `developers.pinterest.com`. Ele começa com acesso Trial, e a aprovação chega por e-mail.
  2. Guarde o **App ID** e o **App secret**.
  3. O painel pede um token novo a cada leitura (`grant_type=client_credentials`, escopo `ads:read`). Ele vale 30 dias, então não há refresh token para guardar.
  - **Armadilha:** `client_credentials` só funciona se a conta dona do app tiver **2FA ativo**. Sem 2FA, o erro é genérico de autorização.

## 7. Microsoft Ads (UET) e Microsoft Clarity

### Microsoft Ads
- **ID público:** o ID da tag UET. Fica em Ferramentas → Tag UET.
- **Meta de compra:**
  - tipo "evento", ação `purchase`, receita variável;
  - o script manda `revenue_value` e `currency`.
- **Armadilha:** importe as campanhas e metas do Google Ads (Importar → Google Ads). Isso economiza horas.
- **Para veicular:**
  - cartão de crédito cadastrado (no Brasil, a cobrança local pode ter imposto, ex.: ISS);
  - **verificação de identidade do anunciante**, com documento e às vezes selfie, feita pelo dono da conta.
  - Não há gasto mínimo obrigatório; o orçamento diário é você quem define.
- **Meta de compra recomendada:** categoria compra, ação `purchase`, receita variável na moeda da conta com um valor padrão (o preço), conversões otimizadas desligadas até precisar.
- **Conta suspensa logo depois de cadastrar cartão ou documento** acontece: é revisão automática. O caminho é concluir a verificação de identidade do anunciante (AIV) no próprio painel e, se continuar suspensa, abrir a apelação pelo formulário de suporte. **Não crie outra conta**: conta nova do mesmo dono costuma ser suspensa também.
- **Leitura de custo pelo painel:** é a parte mais burocrática, deixe por último. Ela pede:
  - um **developer token** (Ferramentas → Developer portal; o clique aceita os termos da API, então é do dono);
  - um **app no Azure / Entra ID** com permissão `msads.manage` (+ `offline_access`);
  - um **refresh token** OAuth;
  - o customer ID e o account ID.
  - O relatório é assíncrono pela API REST JSON de Reporting v13: `GenerateReport/Submit` → `GenerateReport/Poll` até `Success` → baixa um **.zip com CSV** (URL vazia = sem dados no período). Datas podem vir `AAAA-MM-DD` ou `M/D/AAAA`; números podem ter vírgula de milhar ou `--`.
  - **A Microsoft troca o refresh token a cada uso.** Quando a resposta trouxer um novo, salve o novo (ex.: numa tabela de estado do backend); se continuar usando o antigo, a leitura para de funcionar dias depois.
- **Microsoft Advertising não tem API de conversão server-side simples** como Meta/TikTok. A UET no navegador com consentimento é o caminho; os IDs `msclkid` ficam guardados para importação offline se precisar.

### Microsoft Clarity
- **ID público:** o ID do projeto.
- Só navegador (gravações de sessão e mapas de calor), sem API de relatório útil para o painel. No painel, mostre como "conectado no navegador", e o status "não se aplica" para servidor e relatório é normal.
- Vincule o Clarity ao GA4 nas configurações do Clarity para ver as gravações por segmento.

## 8. Bing Webmaster Tools e IndexNow

- **Entrada mais rápida:** "Importar do Google Search Console". Ele traz o site verificado e os sitemaps em um clique (o dono autoriza o acesso ao Google; confira depois que o sitemap aparece como "Sucesso").
- **Chave de API:** Configurações → Acesso à API → gerar chave. O painel lê cliques e impressões da busca do Bing com ela.
- **Armadilha:** login em loop ou página em branco. Bloqueadores (Brave Shields, uBlock) quebram o login da Microsoft; desative para o domínio ou use outro navegador.
- **IndexNow:** avisa Bing, Yandex, Seznam e outros na hora em que uma página muda.
  1. Gere uma chave (32 caracteres hex).
  2. Publique o arquivo `https://seudominio.com.br/<chave>.txt` contendo a chave.
  3. No deploy, faça `POST https://api.indexnow.org/indexnow` com `{host, key, keyLocation, urlList}`.
  - O Google **não** usa IndexNow: para ele, valem o sitemap e o Search Console.

## 9. Armadilhas gerais de painel de anunciante

| Sintoma | Causa provável | O que fazer |
|---|---|---|
| Botão desabilitado sem explicação | Falta vínculo (app ↔ portfólio, usuário ↔ ativo) | Passe o mouse no botão: o tooltip costuma dizer o que falta |
| Página de permissões em branco | Bug da página do nível mais baixo | Adicione no nível acima (conta em vez de propriedade) |
| Interface mudou de idioma | Troca de região depois de verificação | Menu de idioma do perfil ou parâmetro `lang` na URL |
| "Contrato/termos pendentes" | Dados de faturamento incompletos | Preencher informações de cobrança |
| Token gerado não lê nada | Permissão de leitura não atribuída ao ativo | Atribua a conta de anúncios ao usuário/app, depois gere de novo |
| Relatório responde vazio | Sem campanha rodando no período | Normal. Confirme com período maior ou campanha ativa |
| API responde 200 mas falhou | TikTok e outras usam `code` no corpo | Sempre cheque o código no JSON |
| Segredo "duplicado" com nomes diferentes | Testes antigos | Compare o digest listado pelo gerenciador de segredos e apague o nome fora do padrão (faça backup da lista antes e mostre ao dono o que sai) |
| Pixel não registra nada no teste | Bloqueador de anúncio no navegador de quem testa | Teste no celular, em janela de outro navegador ou com "Testar eventos" da rede |
| Campo de texto ignora o que foi digitado por automação | Painéis em React só leem o valor pelo evento deles | Preencha à mão, ou defina o valor pelo setter nativo do campo e dispare o evento `input` |
| Campo de porcentagem/valor com máscara grava errado | A máscara conta casas decimais | Digite sem vírgula (ex.: `2000` para 20,00%) e confira o valor salvo |
| Conta suspensa logo após o cadastro | Revisão automática (comum no Microsoft Ads) | Verificação de identidade + apelação; não crie conta nova |

## 10. Checkout externo como 2ª opção (Hotmart e parecidos)

Para quem desconfia de um site que não conhece, ofereça "Comprar pela Hotmart" (ou Kiwify, Eduzz...) ao lado do checkout próprio. A entrega pode continuar sendo a do seu site: a plataforma só recebe o pagamento e avisa o seu backend.

### Montagem
1. **Produto na plataforma**, um por produto do site, com o mesmo nome e preço. Escolhas que **não mudam depois** (ex.: na Hotmart, "parcelado com taxas para o cliente") merecem uma pergunta ao dono antes. A página externa do produto aponta para a página de venda do seu site com `?origem=hotmart`.
2. **Aceites e termos** (ex.: termo de tratamento de dados pessoais) são cliques do dono. Sem eles a plataforma não deixa finalizar o produto nem criar o webhook.
3. **Webhook de compra** (na Hotmart: Ferramentas → Webhook, versão 2.0, eventos de compra) apontando para uma função do seu backend. Ela:
   - confere o token da conta no cabeçalho (na Hotmart, `X-HOTMART-HOTTOK` comparado com um segredo, em tempo constante); sem ele, 401;
   - transforma o evento num pedido na **mesma tabela** do checkout próprio (id da transação da plataforma como id do pagamento) e reusa a mesma entrega;
   - é idempotente: a plataforma reenvia o mesmo evento; grave por id e mande o e-mail de acesso uma vez só;
   - aceita qualquer valor positivo vindo da plataforma: cupom e parcelamento mudam o valor pago, e uma conferência de "valor exato" deixaria o comprador sem acesso;
   - reembolso e chargeback desligam o acesso;
   - produto que não é seu (ou evento de outro tipo) responde 200 e é ignorado, para a plataforma não reenviar para sempre;
   - guarda a origem que a plataforma devolve (`src`, `sck`) no mesmo formato de origem do painel.
4. **Pixels dentro da plataforma** (na Hotmart: Ferramentas → Pixel, por produto): Meta (com o **token da API de Conversões** colado por produto — o dono cola), Google Ads (AW- + rótulo da compra, só vendas), GA4, TikTok, Pinterest, UET. Eventos: vendas realizadas e visitas na página de pagamento. A venda externa **não** sai pelo servidor do seu site (ver `servidor-conversoes.md`).
5. **Recuperação de carrinho da plataforma** ligada (na Hotmart: "recuperador automático" e o relatório "Abandono de carrinho" de cada produto).

### O botão no site
- **Link simples** para o checkout: `https://pay.hotmart.com/<código>?sck=<página>&src=<utm_source>`. **Não carregue o widget/script da plataforma.** O widget da Hotmart apaga todos os links `hotmart.com` da página quando a checagem de saúde dele falha, e o servidor dessa checagem já saiu do ar: o botão sumiu de todas as páginas sem ninguém ver. No HTML o botão estava lá; só a página renderizada mostrava o problema.
- **Visitante que veio da plataforma** (afiliado, marketplace: chega com `?origem=hotmart`, lembre na sessão) vê **só** o checkout da plataforma, aberto em página inteira (o cookie de afiliado precisa ser gravado no domínio da plataforma). Os botões de oferta vão para lá, a página do checkout próprio redireciona para lá, e o `sck`/`src` do afiliado é mantido. Sem isso, a venda do afiliado acontece no seu checkout e ele perde a comissão.
- Teste essa regra num harness em Node (página falsa, com e sem `?origem=`).

### Armadilhas
- **Nome do autor/vendedor no checkout da plataforma** vem de um campo da conta (na Hotmart, "Nome social" em Informações pessoais), não do produto. Leia o checkout como comprador depois de criar os produtos. Mudanças podem levar ~1 h para aparecer (cache).
- **O material entregue pela plataforma** (ex.: PDF "como acessar") tem que bater com o que o comprador vai receber de verdade: nome do remetente do e-mail, endereço da área de acesso.
- **Recursos anunciados que não aparecem** (ex.: pop-up de saída com cupom): a plataforma pode liberar o recurso aos poucos por conta. Configure, confira na página de checkout ao vivo e, se não aparecer, não há o que corrigir do seu lado: anote e pergunte ao suporte.
- **Cupom da plataforma** e cupom do checkout próprio são listas separadas: mantenha os mesmos códigos e porcentagens nos dois lugares (uma lista única no backend ajuda; ver `funil-e-recuperacao.md`).
