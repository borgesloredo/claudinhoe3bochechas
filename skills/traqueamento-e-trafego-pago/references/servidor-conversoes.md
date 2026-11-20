# Conversões pelo servidor

Bloqueador de anúncio, iOS e recusa de cookie fazem o pixel perder vendas. A conversão enviada pelo backend recupera boa parte. Dispare a partir do **webhook do gateway de pagamento** (venda aprovada) e do momento do lead (formulário salvo).

## Dados que o navegador manda junto com o pedido (só com consentimento)

IDs de clique (gclid, fbclid, ttclid, epik, msclkid), cookies `_fbp`, `_fbc`, `_ttp`, `_epik`, `client_id` do GA4 (cookie `_ga`), user agent e a página. Sem consentimento: nada disso, só a origem por nome (ver `rastreio-site.md`).

## Destinos

| Rede | API | Segredos | Campos-chave |
|---|---|---|---|
| Meta | Conversions API (`/{pixel}/events`) | `META_PIXEL_ID`, `META_CAPI_TOKEN` (gerado no Gerenciador de Eventos) | `event_id`, `action_source=website`, `user_data` com e-mail/telefone em SHA-256, `fbc`, `fbp`, IP, UA |
| Google Analytics | Measurement Protocol | `GA4_MEASUREMENT_ID`, `GA4_API_SECRET` (Admin → Fluxo → Chaves secretas) | `client_id` do cookie, `transaction_id`, `value`, `currency`, `items` |
| TikTok | Events API | `TIKTOK_PIXEL_ID`, `TIKTOK_ACCESS_TOKEN` (Gerenciador de Eventos → pixel → configurações) | `event_id`, `ttclid`, `ttp`, e-mail/telefone em SHA-256. **Erro vem como HTTP 200 com `code ≠ 0`** — trate isso como falha |
| Pinterest | Conversions API | `PINTEREST_AD_ACCOUNT_ID`, `PINTEREST_ACCESS_TOKEN` | `event_id`, `click_id` (epik), e-mail hasheado, `order_id` |
| Google Ads | via GA4 vinculado + conversões otimizadas (enhanced conversions) ligadas na tag | — | não precisa de API própria se GA4 e Ads estão vinculados |

## Padrões que funcionaram

- `sendConversion(evento, pedido)` dispara todos os destinos em paralelo (`Promise.allSettled`) e **devolve o resultado de cada um** (`{nome, ok, erro?}`). Nada de engolir erro em silêncio.
- Grave o último sucesso e o último erro por destino numa tabela de estado (`envio:<rede>:ok|erro` com data). O painel mostra isso em "Conexões" — é como você descobre que um token expirou.
- Rode o envio em segundo plano (`waitUntil`/background) para não atrasar a resposta do webhook.
- Teste com `fetch` falso: confira o corpo de cada destino, que um 500 vira `ok:false` e que o código ≠ 0 do TikTok também.
- Hash: normalize (minúsculas, sem espaços; telefone só dígitos com DDI) **antes** do SHA-256.
- **Limpe o que o navegador mandou** antes de guardar: o corpo é de quem visita, não confiável. Aceite IDs só com caracteres esperados e tamanho máximo, `client_id` do GA4 no formato `123.456`, e a página só se começar com `https://SEU_DOMINIO/`. Sem consentimento (nem análise nem anúncios), guarde `null`.
- **Nomes de evento por rede**: Meta `Lead`/`Purchase`; TikTok `SubmitForm`/`CompletePayment`; Pinterest `lead`/`checkout` (valores numéricos como texto, ex.: `"97.00"`); GA4 `purchase` com `consent.ad_user_data` e `ad_personalization` de acordo com o consentimento de anúncios.
- Sem `fbc` no cookie mas com `fbclid` guardado: monte `fbc = fb.1.<ms>.<fbclid>`.
- **Dispare o Purchase só na primeira aprovação** do pedido (o webhook do gateway pode chegar mais de uma vez).
- Segredo faltando = destino pulado, sem erro. Falha de envio só é registrada: nunca bloqueia a venda nem a entrega.

## Venda feita no checkout externo (Hotmart e parecidos)

O webhook da plataforma avisa o seu backend para entregar o produto e registrar a venda, mas **não mande conversão pelo servidor para essa venda**: o visitante não deu consentimento no seu site, e os pixels e o token de API de conversões configurados **dentro da plataforma** já reportam a compra. Mandar dos dois lados conta duas vezes. Ver `plataformas.md`, seção 10.
