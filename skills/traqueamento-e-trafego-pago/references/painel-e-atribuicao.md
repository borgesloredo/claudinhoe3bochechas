# Painel de tráfego e atribuição

O painel interno (área protegida do site) tem uma aba "Tráfego" com quatro blocos.

1. **Conexões**: cada rede com três estados.
   - **navegador**: o ID está no script.
   - **servidor**: os segredos da API de conversão existem, mais o último envio ok ou com erro.
   - **relatório**: os segredos de leitura existem e a última leitura funcionou.
   - Use `null` quando o estado não se aplica (ex.: Clarity não tem servidor nem relatório).
2. **Métricas por plataforma**: gasto, impressões, cliques e conversões por campanha, no período escolhido, lidos pela API de cada rede.
3. **Vendas por canal**: pedidos reais do banco agrupados pelo canal de origem.
   - Separe **pago**, **orgânico** e **direto**.
   - Mostre receita, quantidade e custo por venda (gasto da rede ÷ vendas pagas daquela rede).
4. **Jornada**: primeiro toque → último toque de cada venda, para ver por exemplo "conheceu no TikTok orgânico, comprou pelo Google pago".
5. **Busca e visitas** (opcional): cliques e impressões de Search Console e Bing Webmaster por dia; sessões do GA4 por grupo de canal (`sessionDefaultChannelGroup`).
6. **Seguidores e custo por seguidor** (opcional): as APIs só dão o número de **hoje** (Instagram `followers_count`), então o histórico é seu: guarde um valor por dia e rede (a leitura mais nova do dia vale) e mantenha até ~400 dias. Custo por seguidor = gasto da rede no período ÷ seguidores ganhos no período; com uma leitura só, perda de seguidores ou gasto zero, mostre "—" em vez de número.

Pedidos antigos, de antes de existir a coluna de origem, aparecem como **"Sem informação"** (tipo desconhecido), não como "Direto". Se houver dados de rastreio consentido nesses pedidos, reconstrua o último toque a partir deles.

## Outras abas que valem a pena

O mesmo painel (mesma senha, mesma função no servidor) cresce bem em abas separadas:

| Aba | Mostra |
|---|---|
| Funil | etapas (visitou → preencheu dados → clicou em pagar → pagou) e a lista de capturas com status claro (ver `rastreio-site.md`) |
| Orgânico | seguidores e interações de todas as redes, unidos por @ parecido, e-mail ou telefone, com uma pontuação de "aquecimento" para o dono contatar os mais quentes primeiro |
| Cupons | a lista única de cupons do backend e quantos pedidos usaram cada um |
| Avisos | inscritos de web push, envio manual e cliques (ver `funil-e-recuperacao.md`) |
| Saúde | o último resultado do auditor do funil e um botão "Conferir agora" |

Sobre a aba Orgânico: as APIs oficiais quase nunca dão a **lista** de seguidores (Pinterest dá; YouTube só inscritos públicos). A lista vem de exportação da própria rede ou de um script que o dono roda no Console do navegador logado e que salva um arquivo `.json` para importar no painel (a política de segurança das redes impede o script de mandar direto). Contato (e-mail/telefone) só o que é público ou o que a pessoa deu no seu site: nada de bases compradas (LGPD).

## Classificador de canal

Uma função pura recebe a origem gravada no pedido (`{s: source, m: medium, c: campaign, k: tipo do ID de clique}`) e devolve `{canal, tipo: 'pago'|'organico'|'direto'}`. Ordem das regras:

```ts
const CLIQUE: Record<string, string> = {        // ID de clique → rede paga
  gclid: "Google", gbraid: "Google", wbraid: "Google",
  ttclid: "TikTok", epik: "Pinterest", msclkid: "Microsoft",
};
const PAGO = /^(cpc|ppc|paid|paid[_-]?social|paidsocial|ads?|cpm|cpv|display|retargeting|remarketing)$/i;
const MARCA: [RegExp, string][] = [               // source → nome bonito
  [/google/i, "Google"], [/facebook|instagram|meta|^fb$|^ig$/i, "Meta"],
  [/tiktok/i, "TikTok"], [/pinterest/i, "Pinterest"], [/bing|microsoft/i, "Microsoft"],
  [/youtube/i, "YouTube"], [/whatsapp/i, "WhatsApp"],
];
const marca = (s = "") => MARCA.find(([r]) => r.test(s))?.[1] ?? (s || "Outros");

export function canalDe(o?: { s?: string; m?: string; c?: string; k?: string }) {
  if (!o) return { canal: "Direto", tipo: "direto" };
  const m = (o.m ?? "").toLowerCase();
  if (o.k && o.k !== "fbclid" && CLIQUE[o.k]) return { canal: `${CLIQUE[o.k]} pago`, tipo: "pago" };
  if (PAGO.test(m)) return { canal: `${marca(o.s)} pago`, tipo: "pago" };
  if (o.k === "fbclid") return { canal: "Meta orgânico", tipo: "organico" }; // fbclid sozinho não prova anúncio
  if (m === "ai") return { canal: "IA", tipo: "organico" };
  if (m === "email") return { canal: "E-mail", tipo: "organico" };
  if (m === "referral") return { canal: "Outros sites", tipo: "organico" };
  if (o.s) return { canal: `${marca(o.s)} orgânico`, tipo: "organico" };
  return { canal: "Direto", tipo: "direto" };
}
```

Por que essa ordem:
- **ID de clique de rede paga é a prova mais forte.** Google, TikTok, Pinterest e Microsoft só colocam o ID em clique de anúncio.
- **`fbclid` é exceção.** O Meta põe o `fbclid` em todo link, então ele sozinho não prova anúncio. Só conta como pago se vier com `utm_medium` pago.
- **Origem guardada só com nomes.** Dá para gravar sem consentimento de cookies (ver `rastreio-site.md`), então o painel cobre 100% das vendas, não só quem aceitou o banner.
- **Teste a função com uma tabela de casos.** Inclua gclid → Google pago, fbclid sozinho → Meta orgânico, fbclid + paid → Meta pago, medium=ai → IA e vazio → Direto.

## Conectores de relatório (só leitura)

Cada rede tem um módulo `metricas_<rede>.ts` com uma função `ler(periodo, segredos)`. Ela devolve linhas normalizadas:

```ts
type Linha = { rede: string; campanha: string; dia: string; gasto: number; impressoes: number; cliques: number; conversoes: number };
```

| Rede | Autenticação | Observação |
|---|---|---|
| Google (GA4 + Ads) | JWT RS256 da conta de serviço, assinado com `crypto.subtle` (sem biblioteca), trocado por access token em `oauth2.googleapis.com/token` | Escopos `analytics.readonly` e `webmasters.readonly`; gasto do Ads vem do GA4 vinculado |
| Search Console | mesmo token | `searchanalytics/query` com dimensões `query`/`page` |
| Meta | token do usuário do sistema | `/{act_id}/insights?level=campaign&time_increment=1&fields=campaign_name,spend,impressions,clicks,actions` |
| TikTok | `Access-Token` de longa duração | janelas de ≤ 30 dias + paginação; checar `code` |
| Pinterest | `client_credentials` a cada leitura (App ID + secret) | `/ad_accounts/{id}/campaigns/analytics` |
| Bing Webmaster | `apikey` na query | `GetRankAndTrafficStats` |
| Microsoft Ads | developer token + OAuth (Azure), refresh token que **muda a cada uso** (salve o novo) | Reporting v13 REST JSON: `Submit` → `Poll` → baixa .zip com CSV — deixar por último |
| Instagram (seguidores) | o mesmo token do Meta + `IG_USER_ID` | `/{ig_user_id}?fields=followers_count`; falha aqui só acrescenta um erro, os números de anúncio continuam |

### Padrões

- **Cache de 60 minutos** por rede e período, numa tabela simples (`chave`, `json`, `atualizado_em`). A primeira abertura do painel não pode esperar 6 APIs. O botão "Atualizar" manda `atualizar: true` e ignora o cache.
- **Uma rede com erro não derruba o painel.** Rode as redes com `Promise.allSettled`. Grave para cada uma `status[rede] = {conectado, erro?}` e mostre o erro curto ao lado da rede.
- **Sem segredo = "não conectado", sem chamada.** A tela de conexões mostra só se o segredo **existe** (booleano), nunca o valor nem parte dele.
- **Janela de período fechada.** Converta tudo para o fuso da conta de anúncios e datas `AAAA-MM-DD`. Cada rede tem um limite: TikTok 30 dias por chamada, Meta até 37 meses, GA4 sem limite prático.
- **Teste cada conector antes de ligar.** Use um script local (ex.: `deno run`) que lê os segredos de `~/.config/traqueamento-e-trafego-pago/*.env`, chama `ler()` e imprime só a contagem de linhas e o erro. Mascare qualquer coisa com mais de 20 caracteres.
- **Testes unitários com `fetch` falso** para cada conector:
  - monta a URL certa;
  - pagina;
  - divide janelas;
  - converte centavos/micros;
  - trata `code ≠ 0`.

## Proteção do painel

O painel é uma função no servidor que recebe uma senha (ou sessão) e devolve JSON. Ela checa:

- a origem (`Origin` igual ao seu domínio);
- a senha guardada como segredo;
- um limite de tentativas (no mínimo uma espera de ~2 s em senha errada) e comparação em tempo constante;
- painel fechado (503) se a senha guardada for curta demais. Recomende ao dono uma senha longa: uma senha só protege todas as abas.

Nada de segredo vai para o navegador; o navegador só recebe números agregados. Chamadas de teste feitas por script precisam mandar o cabeçalho `Origin: https://SEU_DOMINIO`, senão a função responde 403.
