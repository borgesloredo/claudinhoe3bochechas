# SEO técnico e GEO

SEO = aparecer no Google/Bing. GEO (Generative Engine Optimization) = ser citado por ChatGPT, Perplexity, Gemini, Copilot, Claude. A base técnica é a mesma; GEO acrescenta conteúdo fácil de citar e arquivos para robôs de IA.

## Checklist técnico (todo site)

| Item | Como | Por quê |
|---|---|---|
| `robots.txt` | `User-agent: *` + `Allow: /` + `Sitemap: https://seudominio.com.br/sitemap.xml`. **Não bloqueie** robôs de IA (GPTBot, OAI-SearchBot, PerplexityBot, ClaudeBot, Google-Extended) se quer GEO | Bloquear = não ser citado |
| `sitemap.xml` | Gerado no build com **todas** as páginas públicas e `lastmod` real | Descoberta e reindexação |
| Canonical | `<link rel="canonical">` absoluto em cada página | Evita duplicata com/sem barra, com UTM |
| Título e descrição únicos | `<title>` de 50 a 60 caracteres (curto demais também perde ponto nos analisadores), `meta description` ≤ 155 | CTR na busca |
| Open Graph / Twitter | `og:title`, `og:description`, `og:image` **1200×630** absoluto, `og:url`, `twitter:card=summary_large_image` | Prévia em WhatsApp, redes, Discord |
| JSON-LD | `Product` + `Offer` (preço, moeda, disponibilidade) nas páginas de venda; `Person` ou `Organization` com `sameAs` para todos os perfis oficiais; `FAQPage` quando houver FAQ; `BreadcrumbList` | Rich results e entidade reconhecida pelas IAs |
| `lang` e `hreflang` | `<html lang="pt-BR">` | Sinal de idioma |
| Velocidade | scripts de terceiros depois do `load`, imagens com `width/height` e `loading="lazy"`, fontes com `display=swap` | Core Web Vitals |
| 404 de verdade | página 404 com status 404 | Não indexar lixo |
| HTTPS + redirecionamento único | `http→https` e `www→sem www` (ou o contrário) em 1 salto | Sinal único |
| Endereço provisório da hospedagem | `*.vercel.app`, `*.netlify.app` etc. com redirecionamento 301/308 para o domínio. Na Vercel isso se faz no domínio do projeto (configurações ou API), não no `vercel.json` | Evita uma cópia do site indexada |
| Áreas privadas | `Disallow` só para painel e área do aluno/comprador (ex.: `/painel/`, `/acesso/`) e `noindex` nelas | Não indexar página de login |
| Prévia nas páginas de checkout | `og:title`, `og:description`, `og:image` também no checkout | O link do checkout é o mais compartilhado no WhatsApp |
| Texto alternativo | `alt` descritivo nas capas e imagens de produto (nunca `alt=""` em imagem que informa) | Acessibilidade e busca de imagens |
| Minificação | JS/CSS minificados no deploy, fontes legíveis no git | Peso da página |

## GEO: ser citado por IA

- **`/llms.txt`** — Markdown curto na raiz: o que é o site, para quem, links das páginas principais com uma linha de descrição cada. **`/llms-full.txt`** — versão completa com o conteúdo dos produtos/guias em texto puro. Gere os dois no build a partir da mesma fonte das páginas.
- **Páginas-guia** respondendo perguntas reais do público ("como fazer X", "X vs Y", "melhor X para Y"), com resposta direta no primeiro parágrafo, listas e tabelas, data de atualização e autor. É esse formato que as IAs citam.
- **Entidade consistente**: mesmo nome, foto e descrição no site, nos perfis sociais e no JSON-LD (`sameAs`). Ajuda a IA a ligar "quem é" ao site.
- **Medir**: o script do site classifica visitas de `chatgpt.com`, `perplexity.ai`, `gemini.google.com`, `copilot.microsoft.com`, `claude.ai` etc. como `utm_medium=ai` e dispara `ai_referral` (ver `rastreio-site.md`). No GA4 crie um grupo de canais personalizado "IA" com essa regra. O ChatGPT também adiciona `utm_source=chatgpt.com` nos links — trate os dois.
- **Bing importa para GEO**: ChatGPT e Copilot usam o índice do Bing. Bing Webmaster + IndexNow aceleram aparecer.

## Verificações de propriedade (resumo)

| Plataforma | Método mais simples |
|---|---|
| Google Search Console | arquivo `google<hash>.html` na raiz, ou TXT no DNS para propriedade de domínio |
| Bing Webmaster | importar do Search Console |
| Pinterest | meta `p:domain_verify` na home |
| Meta | meta `facebook-domain-verification` ou TXT no DNS |
| TikTok | arquivo ou TXT no DNS (verificação de domínio no Business Center) |
| IndexNow | arquivo `<chave>.txt` na raiz; avise as URLs no fim de cada deploy (resposta 200 ou 202 = ok) |

Guarde esses arquivos/metas no repositório do site (são públicos, não são segredo) e confira na auditoria que respondem 200.

## E-mail do domínio

Várias plataformas pedem e-mail do domínio (portal de desenvolvedor do TikTok, contas de empresa). Não precisa de caixa paga: um encaminhamento grátis (ImprovMX, Cloudflare Email Routing, Zoho grátis) com registros MX + SPF no DNS recebe os códigos no e-mail pessoal. Confira com `dig +short MX seudominio.com.br` antes de dizer que "não existe".
