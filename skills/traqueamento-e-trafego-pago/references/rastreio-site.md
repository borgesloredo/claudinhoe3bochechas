# Script de rastreamento do site

Um único arquivo JS (ex.: `/assets/rastreio.js`) incluído em todas as páginas. Ele é a fonte da verdade dos IDs públicos e dos eventos.

## Estrutura

```js
var CFG = Object.assign({
  ga4: 'G-XXXXXXX',          // GA4 measurement id
  ads: 'AW-XXXXXXXXX',       // Google Ads tag
  adsLead: 'xxxxxxxx',       // rótulo da conversão de lead
  adsPurchase: 'xxxxxxxx',   // rótulo da conversão de compra
  pixel: '0000000000',       // Meta Pixel
  clarity: 'xxxxxxxx',       // Microsoft Clarity
  tiktok: 'CXXXXXXXXXX',     // TikTok Pixel
  pinterest: '0000000000',   // Pinterest Tag
  uet: '00000000'            // Microsoft Ads UET
}, window.RASTREIO_CFG || {});
```

- **ID vazio = plataforma desligada**, sem erro. Assim você publica o script antes de ter todas as contas.
- `window.RASTREIO_CFG` permite sobrescrever por página/ambiente (útil em testes).
- Um modo debug (`localStorage.debug = '1'`) que loga cada evento no console economiza horas.
- **Todos os IDs vazios** = o script sai logo no começo, não mostra banner e esconde o botão "Preferências de cookies" (não há escolha a mudar).
- Inclua o script em **todas** as páginas pelo gerador do site (ou pelo template), inclusive nas páginas de checkout. Incluir à mão, página por página, sempre esquece alguma.

## Consentimento (LGPD/GDPR)

- Banner com duas escolhas: **análise** e **anúncios**. Guarde `{v, analytics, ads, at}` no localStorage com versão; mudou a política → sobe a versão → banner volta.
- **Google Consent Mode v2**: `gtag('consent','default', {analytics_storage, ad_storage, ad_user_data, ad_personalization})` como `denied` até a escolha; `update` depois.
- Eventos disparados antes da escolha vão para uma fila: aceitou → reenvia; recusou → descarta.
- Pixels de anúncio (Meta, TikTok, Pinterest, UET) só carregam com consentimento de anúncios. Clarity/GA4 com consentimento de análise.
- **Carregue os scripts dos fornecedores depois do evento `load`** da página — protege o LCP/Core Web Vitals.
- O banner cita **só as ferramentas que têm ID** preenchido. Um botão "Preferências de cookies" (na política de privacidade e no rodapé) reabre o banner; se a escolha mudou, recarregue a página.
- **Consentimento dado depois da página de entrada**: GA4 e o vinculador de conversões do Google Ads só leem UTM e gclid **da barra de endereço**. Quando a pessoa aceita numa página seguinte, recoloque uma vez na URL os parâmetros guardados da entrada (`history.replaceState`, sem tirar nada da URL). IDs de clique só voltam com consentimento de anúncios.
- Com consentimento de anúncios e `fbclid` guardado, crie o cookie `_fbc` (`fb.1.<ms>.<fbclid>`, 90 dias) se ele não existir: melhora a correspondência da API de Conversões.

## Atribuição (UTM + IDs de clique)

- Parâmetros guardados: `utm_source, utm_medium, utm_campaign, utm_content, utm_term, fbclid, gclid, gbraid, wbraid, ttclid, epik, msclkid`.
- Guarde o *primeiro toque* (com consentimento) e o *último toque* (sessão) — o painel mostra a jornada entre plataformas com os dois.
- **Sem UTM, classifique pelo referrer**:
  - buscadores (google.*, bing, duckduckgo, yahoo, ecosia, yandex, brave, baidu) → `utm_source=<host>`, `utm_medium=organic`
  - redes sociais (instagram, facebook, tiktok, youtube, pinterest, linkedin, x/twitter, kwai, whatsapp…) → `social`
  - assistentes de IA (chatgpt.com, perplexity.ai, gemini, copilot, claude.ai, meta.ai, deepseek, grok…) → `utm_medium=ai` + evento `ai_referral`
  - outros sites → `referral`
  - **ignore seus próprios domínios e o retorno do gateway de pagamento** (senão toda compra vira "referral do Mercado Pago/Stripe").
- **Antes do consentimento**, UTMs e IDs de clique ficam só na aba (`sessionStorage`). Com consentimento de anúncios, vão para o `localStorage` como primeiro/último toque.
- **Origem para o checkout sem consentimento**: ao enviar o pedido, mande só *nomes* — `{first:{s,m,c,k}, last:{s,m,c,k}}` onde `k` é o **tipo** de ID de clique (`gclid`), nunca o valor. Nomes de canal não identificam pessoa, então dá para guardar sem cookie; o valor do ID só vai com consentimento.
- Não remova parâmetros da URL; se precisar re-adicionar UTMs guardadas, use `history.replaceState` sem tirar nada.

## Eventos

| Evento | Quando | Observação |
|---|---|---|
| `view_item` | página de produto | `items[{item_id, item_name, price}]` |
| `generate_lead` / Lead | formulário do checkout enviado | event_id `lead_<id>` |
| `purchase` / Purchase / CompletePayment / checkout | pagamento aprovado (página de obrigado) | event_id `purchase_<pedido>`, `transaction_id`, `value`, `currency` |
| `ai_referral` | visita vinda de IA | parâmetro `ai_source` |

Mapeie o mesmo evento para o nome de cada rede: GA4 `purchase`, Ads `conversion` (send_to `AW-…/rótulo`), Meta `Purchase`, TikTok `CompletePayment`, Pinterest `checkout` (com `order_id`), UET `purchase` com `revenue_value`.

**Deduplicação**: o event_id do navegador tem que ser exatamente o mesmo que o servidor manda (`purchase_<pedido>`). Meta usa `eventID`, TikTok `event_id`, Pinterest `event_id`, GA4 usa `transaction_id`.

**GA4 `purchase` só pelo servidor.** Pix e boleto costumam ser pagos depois que a aba fechou; o servidor vê o pagamento e o navegador não. Com uma fonte só, também não há contagem dupla. O navegador continua mandando `purchase` para Meta, Ads, TikTok, Pinterest e UET (com event_id) e marca o pedido como já contado (`localStorage`), para não disparar de novo ao recarregar a página de obrigado.

**Isca gratuita** (capítulo, e-book): `generate_lead` com o seu próprio event_id (ex.: `lead_amostra_<id>`, o mesmo que o servidor usa) e o mesmo consentimento e origem do checkout.

### Ligar no checkout sem editar cada página

Se vários checkouts usam o mesmo código para chamar o backend (`fetch` para a função de pagamento e para a consulta de status), o script do site pode **embrulhar o `fetch`** uma vez:
- na chamada de pagamento, acrescenta `rastreio` (cookies, IDs de clique, consentimento) e `origem` (nomes de canal) ao corpo, dispara `add_payment_info` e passa o e-mail para as conversões otimizadas (`gtag('set','user_data',{email})`, `ttq.identify({email})`);
- na resposta com o id do pedido, dispara `generate_lead` (event_id `lead_<id>`);
- na consulta de status que volta `approved`, dispara `purchase` (event_id `purchase_<id>`), uma vez por pedido.

Guarde a referência ao `fetch` original antes de embrulhar: a captura de formulário usa ela.

### Engajamento (opcional, barato e útil)

Profundidade de rolagem (25/50/75/100), tempo com a aba visível, seções vistas (metade na tela por 1 s), cliques em botões e links, FAQ aberta, play/fim de áudio e vídeo, e `web_vitals` (LCP e CLS reais, enviados quando a aba esconde). Todos passam pela mesma fila de consentimento.

## Captura de formulário (abandono de checkout e de cadastro)

Obrigatória em todo site com checkout próprio ou formulário de isca. Sem ela, quem digitou o e-mail e desistiu some sem rastro: o banco de pedidos só ganha linha quando a pessoa clica em pagar.

- **No mesmo script do site**, não página por página: ouça `input` (com espera de ~1,5 s), `change` (envio imediato) e `visibilitychange` → `hidden` (envia o que estiver pendente) no `document`, em fase de captura. Assim cobre todos os checkouts e formulários, inclusive os que a página monta depois.
- **Classifique o campo** por `type`/`autocomplete`/rótulo: `email`, `tel` (ou rótulo com WhatsApp/telefone/celular), `name`; o resto vai para `campos{rótulo: valor}`. Rádio/checkbox: chave = legenda do grupo, valor = opção marcada.
- **Nunca leia**: `password`, `hidden`, `file`, `search`, `autocomplete="cc-*"`, e qualquer campo cujo id/nome/rótulo fale de cartão, CVV, CPF/CNPJ, validade, senha ou token. Pule o painel interno e formulários marcados `data-sem-captura`. Formulários de cartão em iframe do gateway já ficam de fora sozinhos.
- **Envio**: `fetch(..., {keepalive: true})` usando o `fetch` original (antes de qualquer wrapper), com `{sessao, pagina, product, email, telefone, nome, campos, origem, rastreio}`. `sessao` = id aleatório no `sessionStorage`. Só reenvia se o estado do formulário mudou. `origem` (nomes de canal) vai sempre; `rastreio` (cookies/IDs de clique) só com consentimento.
- **Servidor**: função própria (ex.: `lp-captura`), CORS só para os domínios do site, limite de tamanho (~16 KB) e de volume (ex.: 600 linhas novas em 10 min), limpeza dos campos de novo no servidor (e-mail inválido e telefone curto vão para `campos` como "incompleto", sem se perder). **Uma linha por aba e página** (`unique(sessao, pagina)`, upsert): cada envio substitui o anterior. Não manda e-mail nem conversão.
- **LGPD**: não depende do banner de cookies (é o próprio pedido: art. 7º V e IX), mas exige transparência (art. 6º VI e art. 9º): a política de privacidade tem que dizer o que é guardado, para quê e por quanto tempo, e cada página com formulário tem que ter link para ela (o rodapé basta). Uma linha de aviso embaixo do formulário é opcional (pergunte ao dono). Apague sozinho depois de um prazo (ex.: 180 dias, por `pg_cron`).
- **E-mail no campo errado**: se o valor do campo de nome tem cara de e-mail, guarde como e-mail (visitantes fazem isso).
- **Página da isca sem produto na URL**: se a isca escolhe o produto num campo do formulário (e não em `?produto=`), o servidor tem que ler o produto também dos `campos`. Senão essas capturas nunca entram na sequência de e-mails.
- **Painel**: liste as capturas com status cruzado com os pedidos e com a sequência de e-mails, em palavras que não deixam dúvida: *comprou*, *clicou em pagar e não pagou*, *não terminou o formulário*, *recebendo e-mails (3 de 10)*, *e-mail voltou*. Um rótulo vago como "não enviou" foi lido pelo dono como "o e-mail falhou". Telefone vira link `wa.me`. No funil, a etapa "Preencheu dados no checkout" vem antes de "Clicou em pagar".
- **Teste**: no harness em Node, dispare `change` em campos falsos e confira que e-mail/nome saem, CPF/senha não, e que o mesmo estado não é reenviado. No navegador, digite num checkout local e veja a chamada à função na aba Rede.
- **Esteira de e-mail**: captura com e-mail e sem atividade há ~2 h entra na mesma sequência de quem pediu a isca e de quem clicou em pagar sem pagar. Detalhes, entregabilidade e devoluções em `funil-e-recuperacao.md`.
- **Plataformas externas** (Hotmart etc.): já capturam no checkout delas. Confira o relatório "Abandono de carrinho" de cada produto e ligue a recuperação automática.

## Testar sem navegador

Rode o script num `vm` do Node com `window`/`document`/`localStorage` falsos e confira as filas de cada fornecedor (`dataLayer`, `fbq.queue`, `ttq`, `pintrk.queue`, `uetq`). Casos que valem a pena:

1. todos recebem view_item; scripts só depois do `load`
2. purchase leva o mesmo event_id e o pedido para todas as redes
3. sem consentimento de anúncios, TikTok/Pinterest/UET nunca iniciam
4. ID vazio = nada carrega
5. visita do ChatGPT vira `ai` e dispara `ai_referral` uma vez
6. IDs de clique de TikTok/Pinterest/Microsoft são guardados
7. referrer classifica orgânico/social/referral e ignora o gateway
8. o checkout recebe a origem sem consentimento e **nunca** o valor do ID de clique
9. GA4 nunca recebe `purchase` do navegador; as outras redes recebem uma vez por pedido
10. aceitar o banner numa segunda página recoloca as UTMs da entrada na URL
11. a captura manda e-mail/nome, nunca CPF/cartão/senha, e não reenvia o mesmo estado

Isso roda em milissegundos e evita abrir navegador (em alguns ambientes abrir navegador pelo shell nem é permitido).
