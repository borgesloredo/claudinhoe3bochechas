# Auditoria completa

Rode antes de liberar verba de anúncio e depois de qualquer mudança no site, no checkout ou nas chaves. O modelo está em `scripts/auditoria-modelo.sh`: preencha as variáveis do topo e adapte as seções ao seu backend.

## As 8 seções (mais a 6b e a 6c)

1. **Painel ao vivo.** Chame a função do painel com `atualizar: true`. Para cada rede, imprima o estado de navegador, servidor e relatório (ok, FALTA ou n/a), mais o erro curto se houver. Zeros sem campanha são normais; erro não é.
2. **IDs no script publicado.** Baixe o `rastreio.js` **do site no ar**, não o local. Confira que cada ID esperado está lá, e também o envio da origem ao checkout. Se o deploy minifica o JS, acentos viram escapes (`não` → `n\xE3o`): procure por um trecho sem acento.
3. **Páginas.** Leia todas as URLs do `sitemap.xml` e confira que cada uma responde 200 e carrega o script. Mostre `N/N` e liste as que falham.
4. **SEO e verificações.** Confira que respondem 200:
   - `robots.txt`, `sitemap.xml`, `llms.txt`, `llms-full.txt`;
   - os arquivos de verificação.
   Na home, confira:
   - a meta do Pinterest;
   - o `application/ld+json`;
   - o `og:image`.
   Confira também o MX do domínio.
5. **Segredos (só nomes).** Liste os segredos do backend em JSON. Compare com a lista esperada e imprima `presentes X/Y`, os que faltam e os **nomes fora do padrão**, que são candidatos a duplicata. Nunca imprima valor.
6. **Funções no ar.** Mostre status, versão e data de cada função do backend (checkout, webhook, painel).
6b. **Captura de formulário.** Abra cada tipo de página com formulário (um checkout, a isca), digite um e-mail de teste e saia do campo: a chamada à função de captura tem que aparecer na aba Rede e a linha no painel. Confira o link da política de privacidade na página e, nas plataformas externas, o relatório de abandono de carrinho. Apague as linhas de teste depois (com backup).
6c. **Vitrine (o que o comprador vê).** Para cada produto: o checkout próprio responde 200, tem o botão do checkout externo, **não** carrega o widget/script da plataforma externa e tem `og:image`; a página do checkout externo responde 200 e mostra o autor, o preço e o nome certos. Ver "Verificar como comprador" abaixo.
7. **Testes.** Rode os testes do backend (conectores, classificador, envio de conversão) e o harness do script do site. Todos verdes.
8. **Git.** Confira três coisas:
   - cada repositório está sincronizado com o remoto;
   - não há mudanças locais esquecidas;
   - a branch do painel está dentro da principal.

## Verificar como comprador

O grep no HTML diz o que **você** publicou; o comprador vê outra coisa: a página depois que todos os scripts rodaram, mais as telas de terceiros por onde ele passa. Já aconteceu de um script de terceiro apagar o botão de compra em todas as páginas (o HTML continuava com ele) e de o checkout externo mostrar um nome de autor antigo, vindo de um campo da conta. Ninguém percebeu até o dono ver.

Antes de dizer que uma mudança em página de venda, checkout ou funil está pronta:

1. **Abra a página publicada** (não a local) num navegador e confira o elemento **depois do carregamento**: botão, preço, cupom, formulário. Se o ambiente não permite abrir navegador pelo shell, use uma ferramenta de navegador autorizada ou deixe o teste como pendente para o dono rodar, dizendo isso claramente.
2. **Siga o clique** até a tela seguinte (checkout próprio, gateway, checkout externo) e leia como comprador: nome do produto, autor/vendedor, preço, imagem de compartilhamento, forma de pagamento.
3. **Configurações de conta das plataformas** (nome social, nome do vendedor na fatura, e-mail de suporte, material entregue) fazem parte do produto: confira junto.
4. **Automatize a parte que dá** na checagem "vitrine" do auditor do funil (`funil-e-recuperacao.md`), para o problema aparecer em horas, não quando o dono notar.

## Depois da auditoria verde

- **Compra de teste real**, de valor baixo, com cupom ou produto de teste. Ela deve aparecer:
  - no painel, com o canal certo (use um link com UTM de teste);
  - no GA4 em Tempo real, no Gerenciador de Eventos do Meta ("Navegador e servidor", desduplicado), nos eventos do TikTok e do Pinterest;
  - na tabela de estado de envio (`envio:<rede>:ok`).
- **Ferramentas de teste das redes:**
  - Meta: "Testar eventos", com código de teste.
  - TikTok: "Test events".
  - Google: Tag Assistant.
  - Pinterest: Tag Helper.
  - Microsoft: UET Tag Helper.
- **Resultado para o dono:** três listas: feito, pendente e o que depende dele (pagamento, documentos, aceite de termos, aprovações das plataformas).
