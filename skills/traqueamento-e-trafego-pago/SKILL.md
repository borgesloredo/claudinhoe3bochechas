---
name: traqueamento-e-trafego-pago
description: Monta, confere e audita o rastreamento (tracking) e a base de tráfego pago e orgânico de um site que vende produto próprio — GA4, Google Ads, Meta Pixel + API de Conversões, TikTok, Pinterest, Microsoft Ads/UET, Clarity, Search Console, Bing Webmaster, IndexNow, SEO e GEO. Cobre captura de formulário com contato verificado, web push, checkout externo como 2ª opção (Hotmart e parecidos) com pixels, painel interno (vendas por canal pago × orgânico × direto, gasto por rede, custo por seguidor) e auditor que olha o funil como o comprador vê. Use quando o pedido falar em pixel, traqueamento, rastreamento, conversão, UTM, atribuição, "de onde vem o cliente", ROAS, custo por venda, painel de métricas, abandono de checkout, captura de lead, web push, Hotmart, conectar Google/Meta/TikTok/Pinterest/Microsoft, Search Console, SEO, GEO, auditoria do funil ou "deixar tudo conectado antes de anunciar" — mesmo sem dizer "tracking".
---

# Rastreamento e tráfego pago

Guia prático para deixar um site de venda direta **medindo tudo antes do primeiro real gasto em anúncio**, e para manter isso auditável depois. Foi construído num projeto real (loja de cursos digitais com site estático, checkout próprio e um checkout externo como segunda opção) e generalizado: troque os exemplos pelos dados do seu projeto.

## Primeiro passo: levantar o projeto

Antes de mexer em qualquer coisa, pergunte ao dono (numa rodada só) e anote:

| Dado | Exemplo de placeholder usado nesta skill |
|---|---|
| Domínio do site | `SEU_DOMINIO` (ex.: `seudominio.com.br`) |
| Onde o site é publicado | Vercel, Netlify, servidor próprio... |
| Backend com funções e banco | ex.: Supabase Edge Functions (`<ref-do-projeto>`), Cloudflare Workers, Vercel Functions |
| Gateway de pagamento do checkout próprio | Mercado Pago, Stripe, Pagar.me... |
| Checkout externo (opcional) | Hotmart, Kiwify, Eduzz... |
| Contas que já existem | GA4, Google Ads, Meta, TikTok, Pinterest, Microsoft Ads, Clarity |
| Onde ficam os segredos do backend | o gerenciador de segredos da plataforma (ex.: `supabase secrets`) |

Nada disso vai no código da skill. Os IDs públicos (G-, AW-, ID de pixel) vão no script do site; os segredos seguem a regra abaixo.

## O que "pronto" significa

Um projeto está pronto quando estas sete camadas funcionam e foram testadas:

1. **Navegador** — um único script no site carrega os pixels (GA4, Ads, Meta, TikTok, Pinterest, UET, Clarity) só depois do consentimento, guarda UTMs e IDs de clique e dispara os mesmos eventos (view_item, lead, purchase) para todos.
2. **Servidor** — quando o pagamento é confirmado (webhook do gateway), o backend reenvia Lead/Purchase para as APIs de conversão de cada rede, com o **mesmo event_id** do navegador para não contar duas vezes.
3. **Origem do pedido** — cada pedido guarda o *nome* do canal (utm_source/medium/campaign + qual tipo de ID de clique havia, nunca o valor), mesmo sem consentimento de cookies. É isso que separa venda paga de orgânica.
4. **Leitura de volta** — o painel interno lê gasto, cliques e conversões de cada rede pela API delas (só leitura) e junta com as vendas reais do banco.
5. **Busca orgânica e IA** — Search Console, Bing Webmaster, sitemap, IndexNow, dados estruturados e arquivos para assistentes de IA (llms.txt).
6. **Captura e recuperação** — todo formulário do site salva nome, e-mail, telefone e opções **enquanto a pessoa digita**; quem não terminou entra numa sequência de e-mails; a isca gratuita exige contato verificado; quem aceitar recebe aviso no navegador. Faz parte do mínimo: não espere o dono pedir. Plataformas como a Hotmart já fazem isso no checkout delas; o checkout próprio precisa ter o mesmo.
7. **Conferência contínua** — um auditor agendado confere o funil, corrige o que puder e olha cada página de venda e cada checkout (o seu e o externo) **como o comprador vê**. Grep no HTML não basta: script de terceiro pode apagar um botão depois que a página carrega.

Leia o arquivo de referência da camada em que estiver trabalhando:

| Camada | Arquivo |
|---|---|
| Script do site, consentimento, eventos, UTMs, deduplicação, captura de formulário | `references/rastreio-site.md` |
| APIs de conversão no servidor | `references/servidor-conversoes.md` |
| Cada plataforma: onde criar, que ID copiar, que permissão dar, armadilhas (inclui Hotmart como 2º checkout) | `references/plataformas.md` |
| Painel: atribuição por canal, conectores de relatório, cache, status, custo por seguidor | `references/painel-e-atribuicao.md` |
| Isca com contato verificado, sequência de e-mail, devoluções, web push, auditor do funil | `references/funil-e-recuperacao.md` |
| SEO técnico e GEO | `references/seo-geo.md` |
| Auditoria final, "verificar como comprador" e checklist | `references/auditoria.md` + `scripts/auditoria-modelo.sh` |

## Ordem recomendada

Siga nesta ordem; cada passo depende do anterior.

1. **Contas e IDs** — crie/organize as contas (Google Analytics, Google Ads, Meta Business, TikTok Ads, Pinterest Business, Microsoft Ads, Clarity, Search Console, Bing Webmaster). Anote só IDs públicos (G-, AW-, IDs de pixel/tag). Tudo na conta **do dono** (confira qual conta Google/Microsoft está logada antes de criar), e-mail de domínio próprio quando a plataforma exigir (o portal de desenvolvedor do TikTok recusa Gmail/Hotmail).
2. **Script do site** com todos os IDs, consentimento e eventos. Teste com um harness em Node (sem navegador) antes de publicar.
3. **Metas de conversão** em cada rede (compra e lead), apontando para os eventos que o script dispara.
4. **Conversões pelo servidor** a partir do webhook de pagamento, com o mesmo event_id.
5. **Origem do pedido** salva no banco.
6. **Captura de formulário** ligada em todas as páginas com formulário, política de privacidade atualizada e com link no rodapé de cada página. Isca gratuita com contato verificado.
7. **Checkout externo** (se houver): produtos criados, pixels e token de API de conversões dentro da plataforma, webhook de venda para o seu backend, link simples (sem o widget da plataforma).
8. **Busca**: Search Console (verificação + sitemap), Bing Webmaster (importar do Search Console), IndexNow, dados estruturados, llms.txt.
9. **Painel**: conectores de leitura, uma rede de cada vez, testando cada chave isoladamente antes de ligar no painel.
10. **Recuperação**: sequência de e-mails para quem não terminou, devoluções de e-mail, web push (opcional).
11. **Auditor do funil** agendado, com a checagem "o que o comprador vê".
12. **Auditoria** completa (script), **verificação como comprador** e **uma compra de teste real** — é a única prova de que a venda chega em todas as redes.

## Regras que evitaram problemas

- **Segredos nunca no chat nem em arquivo versionado.** Token, chave de API e senha: o dono salva sozinho, pelo app Terminal, num arquivo só dele, sem a chave aparecer na tela. Passe para ele este comando, trocando `NOME` pelo nome do segredo:

  ```bash
  mkdir -p ~/.config/traqueamento-e-trafego-pago && chmod 700 ~/.config/traqueamento-e-trafego-pago
  printf 'Cole e tecle Enter: ' && read -rs k && printf 'NOME=%s\n' "$k" > ~/.config/traqueamento-e-trafego-pago/NOME.env && chmod 600 ~/.config/traqueamento-e-trafego-pago/NOME.env; unset k; echo
  ```

  Os scripts leem o arquivo com `set -a; . ~/.config/traqueamento-e-trafego-pago/NOME.env; set +a` e mostram só o *nome* da chave. Para mandar ao backend, use o próprio arquivo (ex.: `supabase secrets set --env-file ~/.config/traqueamento-e-trafego-pago/NOME.env --project-ref <ref-do-projeto>`). Para conferir se dois segredos são iguais, compare o *digest* que a plataforma lista, nunca o valor. Nunca rode `cat`, `echo` ou `env` num desses arquivos.
- **Permissão mínima.** Para o painel, peça só leitura: GA4 "Leitor" (sem marcar "sem métricas de custo"), Search Console "Restrito", Meta `ads_read`, TikTok só "Reporting", Pinterest `ads:read`.
- **Teste cada conector com a chave real antes de publicar**, num script que imprime só contagens e erros (com tokens mascarados). Zeros são normais sem campanha rodando; erro não é.
- **Cliques que aceitam termos, contratos, pagamentos, documentos, códigos de verificação, senhas e permissões do navegador são do dono da conta.** O agente prepara a tela e explica; a pessoa clica.
- **Verifique como comprador, não como programador.** Abra a página publicada depois que os scripts rodaram e siga o clique até a tela seguinte (checkout próprio, gateway, plataforma externa): nome do produto, autor, preço, imagem e botão. Configurações de conta da plataforma (nome social, nome do vendedor) fazem parte do produto.
- **Feche o ciclo com uma compra real.** Sem ela, o envio pelo servidor está só "provavelmente funcionando".

## Convenção de UTMs (combine com quem faz os anúncios)

- `utm_source` = rede (`google`, `meta`, `tiktok`, `pinterest`, `bing`), `utm_medium=paid` (ou `cpc`) em todo anúncio, `utm_campaign` = nome da campanha **igual** ao nome dentro da rede (é assim que o painel cruza campanha × venda).
- **Meta precisa de `utm_medium=paid`**: o Facebook/Instagram colocam `fbclid` em todo link de saída, inclusive orgânico, então `fbclid` sozinho conta como orgânico.
- Google/TikTok/Pinterest/Microsoft adicionam IDs de clique próprios (gclid/gbraid/wbraid, ttclid, epik, msclkid) só em anúncio pago — ative o auto-tagging.
- Links para o checkout externo levam a origem junto (na Hotmart: `src=<utm_source>` e `sck=<página>`), para a venda feita lá também cair no canal certo.

## Quando algo não bater

Consulte a seção de armadilhas em `references/plataformas.md` antes de investigar do zero — a maioria dos travamentos de painel de anunciante (botão desabilitado, página em branco, idioma trocado, "contrato pendente", conta suspensa) tem causa conhecida lá. Pixel que "não registra nada" no navegador do dono quase sempre é bloqueador de anúncio: teste no celular ou em outro navegador.
