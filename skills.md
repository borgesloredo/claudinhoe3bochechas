# Skills

Skill = pasta com um `SKILL.md` que ensina o Claude a fazer uma tarefa. Para usar, copie para `~/.claude/skills/` e reabra o Claude Code.

**Para marcar que você usa:** troque o espaço vazio da sua coluna por ✅ e faça commit. Skill nova: adicione uma linha (e a pasta em `skills/<nome>/` se for sua).

Origem: pasta = código está neste repo; link = instale da fonte (não copiamos).

## Criadas por nós (código neste repo)

| Skill | O que faz | Autor | Matheus | Arthur | Lucas |
|---|---|---|:-:|:-:|:-:|
| [`carrossel-lista`](skills/carrossel-lista/) | Carrossel de lista para Instagram/TikTok: pauta, slides 1080×1350, legenda | Matheus | ✅ | | |
| [`organico-videos`](skills/organico-videos/) | Vídeos orgânicos narrados com diagrama animado | Matheus | ✅ | | |
| [`organico-personagem`](skills/organico-personagem/) | Série animada com personagem 2D e votação A/B | Matheus | ✅ | | |
| [`reels-teste-campeao`](skills/reels-teste-campeao/) | Testa variações do Reel campeão como Reel de teste | Matheus | ✅ | | |
| [`videos-de-venda`](skills/videos-de-venda/) | Vídeos de venda/anúncio para tráfego | Matheus | ✅ | | |
| [`lp-de-venda`](skills/lp-de-venda/) | Landing page de venda de produto digital | Matheus | ✅ | | |
| [`esteira-email`](skills/esteira-email/) | Esteira de 10 e-mails em 120 dias (Supabase + Resend) | Matheus | ✅ | | |
| [`traqueamento-e-trafego-pago`](skills/traqueamento-e-trafego-pago/) | Rastreamento e base de tráfego pago | Matheus | ✅ | | |
| [`traqueamento-organico`](skills/traqueamento-organico/) | Base de leads orgânica | Matheus | ✅ | | |
| [`auditor-funil`](skills/auditor-funil/) | Confere o funil de venda a cada 2 horas | Matheus | ✅ | | |
| [`curso-mesa-de-som`](skills/curso-mesa-de-som/) | Monta curso completo de mesa de som (PDF, slides, autoestudo) | Matheus | ✅ | | |
| [`construcao-de-ebooks`](skills/construcao-de-ebooks/) | Pesquisa as dores do nicho e monta e-book animado: slides, PDF e autoestudo com áudio (chave Gemini própria; áudio só em Mac com chip Apple) | Matheus | ✅ | | |

## De terceiros (só link)

Instalar: `npx skills add <dono/repo>`.

| Skill | O que faz | Origem | Licença | Matheus | Arthur | Lucas |
|---|---|---|---|:-:|:-:|:-:|
| `gsap-core, gsap-performance, gsap-plugins, gsap-timeline, gsap-utils` | Animação web com GSAP (oficial) | [greensock/gsap-skills](https://github.com/greensock/gsap-skills) | MIT | ✅ | | |
| `frontend-slides` | Slides HTML animados | [zarazhangrui/frontend-slides](https://github.com/zarazhangrui/frontend-slides) | MIT | ✅ | | |
| `graphify` | Grafo de conhecimento de código/documentos | [safishamsi/graphify](https://github.com/safishamsi/graphify) | Apache-2.0 | ✅ | | |
| `playwright-cli` | Automação de navegador | [microsoft/playwright-cli](https://github.com/microsoft/playwright-cli) | Apache-2.0 | ✅ | | |
| `find-skills` | Busca e instala skills (`npx skills`) | [vercel-labs/skills](https://github.com/vercel-labs/skills) | MIT | ✅ | | |
| `motion-design` | Princípios de motion design | [LottieFiles/motion-design-skill](https://github.com/LottieFiles/motion-design-skill) | MIT | ✅ | | |
| `superset` | Paradev/Superset: agentes e workspaces | [paradevai/paradev](https://github.com/paradevai/paradev) | MIT | ✅ | | |
| `editonny` | Edição de vídeo | [soumatheusgomes/editonny](https://github.com/soumatheusgomes/editonny) | a conferir | ✅ | | |

## Sem origem conhecida (sem cópia aqui)

O Matheus usa estas, mas não lembra de onde vieram e a licença é desconhecida, então o código não está neste repo. Se alguém souber a fonte, troque a linha por um link.

| Skill | O que faz | Matheus | Arthur | Lucas |
|---|---|:-:|:-:|:-:|
| `founder-board` | Conselho que testa uma ideia de negócio | ✅ | | |
| `founder-brand` | Nome, voz e identidade da marca | ✅ | | |
| `founder-cfo` | Economia unitária e ponto de equilíbrio | ✅ | | |
| `founder-competitors` | Mapa de concorrentes e brechas | ✅ | | |
| `founder-consumer` | Painel de 100 compradores simulados | ✅ | | |
| `founder-launch` | Plano de lançamento datado | ✅ | | |
| `founder-marketing` | Posicionamento e campanha de 30 dias | ✅ | | |
| `founder-offer` | Monta uma oferta forte | ✅ | | |
| `founder-ops` | Operação do dia 1 | ✅ | | |
| `founder-plan` | Plano de negócio compilado | ✅ | | |
| `founder-pricing` | Preço que o comprador paga | ✅ | | |
| `storytelling` | Narrativa, roteiro e personagens | ✅ | | |


## Adicionadas por Lucas (código neste repo)

Skills auditadas e testadas pelo Klaus. Cada uma está na mesma estrutura das demais, em `skills/<nome>/`.

| Skill | Área | O que faz | Origem | Licença | Matheus | Arthur | Lucas |
|---|---|---|---|---|:-:|:-:|:-:|
| [`untangle-codebase`](skills/untangle-codebase/) | dev | Refatora um código bagunçado inteiro de uma vez | [caldoai/skills](https://github.com/caldoai/skills) | MIT | | | ✅ |
| [`claude-shorts`](skills/claude-shorts/) | vídeo | Corta vídeo longo em shorts verticais com legenda animada | [AgriciDaniel/claude-shorts](https://github.com/AgriciDaniel/claude-shorts) | MIT | | | ✅ |
| [`hallmark`](skills/hallmark/) | frontend | Faz site sem cara de feito por IA | [nutlope/hallmark](https://github.com/nutlope/hallmark) | MIT | | | ✅ |
| [`security-audit`](skills/security-audit/) | segurança | Auditoria de segurança de app, API e código | [cloudflare/security-audit-skill](https://github.com/cloudflare/security-audit-skill) | MIT | | | ✅ |
| [`vercel-react-best-practices`](skills/vercel-react-best-practices/) | frontend | 72 regras de performance para React e Next.js | [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills) | a conferir | | | ✅ |
| [`first-customer-finder`](skills/first-customer-finder/) | marketing | Acha leads que reclamam em público e rascunha a abordagem | [Kappaemme-git/codex-first-customer-finder-skill](https://github.com/Kappaemme-git/codex-first-customer-finder-skill) | MIT | | | ✅ |
| [`gsap-core`](skills/gsap-core/) | animação web | Fundamentos, tweens, easing, stagger e responsividade no GSAP | [greensock/gsap-skills](https://github.com/greensock/gsap-skills) | MIT | | | ✅ |
| [`gsap-frameworks`](skills/gsap-frameworks/) | animação web | GSAP em Vue, Svelte e outros frameworks | [greensock/gsap-skills](https://github.com/greensock/gsap-skills) | MIT | | | ✅ |
| [`gsap-performance`](skills/gsap-performance/) | animação web | Performance e animação fluida com GSAP | [greensock/gsap-skills](https://github.com/greensock/gsap-skills) | MIT | | | ✅ |
| [`gsap-plugins`](skills/gsap-plugins/) | animação web | Plugins oficiais do GSAP | [greensock/gsap-skills](https://github.com/greensock/gsap-skills) | MIT | | | ✅ |
| [`gsap-react`](skills/gsap-react/) | animação web | GSAP em React e Next.js com limpeza correta | [greensock/gsap-skills](https://github.com/greensock/gsap-skills) | MIT | | | ✅ |
| [`gsap-scrolltrigger`](skills/gsap-scrolltrigger/) | animação web | ScrollTrigger, parallax, pinning e animação por rolagem | [greensock/gsap-skills](https://github.com/greensock/gsap-skills) | MIT | | | ✅ |
| [`gsap-timeline`](skills/gsap-timeline/) | animação web | Sequenciamento e timelines no GSAP | [greensock/gsap-skills](https://github.com/greensock/gsap-skills) | MIT | | | ✅ |
| [`gsap-utils`](skills/gsap-utils/) | animação web | Utilitários de interpolação, clamp, snap e arrays no GSAP | [greensock/gsap-skills](https://github.com/greensock/gsap-skills) | MIT | | | ✅ |
| [`animejs`](skills/animejs/) | animação web | Anime.js 4 com timeline, SVG, stagger e interação | [bowtiedswan/animejs-skills](https://github.com/bowtiedswan/animejs-skills) | MIT | | | ✅ |
| [`gsap-scroll-parallax`](skills/gsap-scroll-parallax/) | animação web | Scroll, parallax e páginas cinematográficas com GSAP e Framer Motion | [github/awesome-copilot](https://github.com/github/awesome-copilot) | MIT | | | ✅ |
| [`remotion-best-practices`](skills/remotion-best-practices/) | vídeo e animação | Roteador das skills oficiais do Remotion | [remotion-dev/skills](https://github.com/remotion-dev/skills) | Remotion license | | | ✅ |
| [`remotion-captions`](skills/remotion-captions/) | vídeo e animação | Transcrição e legendas animadas | [remotion-dev/skills](https://github.com/remotion-dev/skills) | Remotion license | | | ✅ |
| [`remotion-create`](skills/remotion-create/) | vídeo e animação | Cria um projeto de vídeo no Remotion | [remotion-dev/skills](https://github.com/remotion-dev/skills) | Remotion license | | | ✅ |
| [`remotion-docs`](skills/remotion-docs/) | vídeo e animação | Consulta a documentação do Remotion | [remotion-dev/skills](https://github.com/remotion-dev/skills) | Remotion license | | | ✅ |
| [`remotion-interactivity`](skills/remotion-interactivity/) | vídeo e animação | Estrutura camadas editáveis no Remotion Studio | [remotion-dev/skills](https://github.com/remotion-dev/skills) | Remotion license | | | ✅ |
| [`remotion-license`](skills/remotion-license/) | vídeo e animação | Explica licença e termos do Remotion | [remotion-dev/skills](https://github.com/remotion-dev/skills) | Remotion license | | | ✅ |
| [`remotion-maps`](skills/remotion-maps/) | vídeo e animação | Anima mapas em vídeos Remotion | [remotion-dev/skills](https://github.com/remotion-dev/skills) | Remotion license | | | ✅ |
| [`remotion-markup`](skills/remotion-markup/) | vídeo e animação | Boas práticas de conteúdo, animação e efeitos | [remotion-dev/skills](https://github.com/remotion-dev/skills) | Remotion license | | | ✅ |
| [`remotion-multimedia`](skills/remotion-multimedia/) | vídeo e animação | Trabalha mídia com Mediabunny | [remotion-dev/skills](https://github.com/remotion-dev/skills) | Remotion license | | | ✅ |
| [`remotion-render`](skills/remotion-render/) | vídeo e animação | Renderiza vídeos, imagens e timelines | [remotion-dev/skills](https://github.com/remotion-dev/skills) | Remotion license | | | ✅ |
| [`remotion-saas`](skills/remotion-saas/) | vídeo e animação | Constrói apps e SaaS com Remotion | [remotion-dev/skills](https://github.com/remotion-dev/skills) | Remotion license | | | ✅ |
| [`remotion-studio`](skills/remotion-studio/) | vídeo e animação | Visualiza vídeos no Remotion Studio | [remotion-dev/skills](https://github.com/remotion-dev/skills) | Remotion license | | | ✅ |
| [`remotion-upgrade`](skills/remotion-upgrade/) | vídeo e animação | Atualiza Remotion e dependências | [remotion-dev/skills](https://github.com/remotion-dev/skills) | Remotion license | | | ✅ |
| [`figma`](skills/figma/) | vídeo e animação | Leva designs do Figma para vídeos HyperFrames | [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes) | Apache-2.0 | | | ✅ |
| [`hyperframes`](skills/hyperframes/) | vídeo e animação | Cria e renderiza vídeos com HTML, CSS e JavaScript | [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes) | Apache-2.0 | | | ✅ |
| [`hyperframes-cli`](skills/hyperframes-cli/) | vídeo e animação | Opera o CLI do HyperFrames | [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes) | Apache-2.0 | | | ✅ |
| [`hyperframes-registry`](skills/hyperframes-registry/) | vídeo e animação | Busca componentes prontos do HyperFrames | [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes) | Apache-2.0 | | | ✅ |
| [`media-use`](skills/media-use/) | vídeo e animação | Busca, cria e trata mídia para vídeos | [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes) | Apache-2.0 | | | ✅ |
| [`remotion-to-hyperframes`](skills/remotion-to-hyperframes/) | vídeo e animação | Converte projetos Remotion e outras animações para HyperFrames | [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes) | Apache-2.0 | | | ✅ |
| [`reverse-any-video`](skills/reverse-any-video/) | vídeo e animação | Reconstrói vídeos como projetos editáveis | [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes) | Apache-2.0 | | | ✅ |
| [`slideshow`](skills/slideshow/) | vídeo e animação | Cria apresentações interativas no HyperFrames | [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes) | Apache-2.0 | | | ✅ |
| [`style-sampling`](skills/style-sampling/) | vídeo e animação | Replica estilos visuais aprovados em novos vídeos | [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes) | Apache-2.0 | | | ✅ |
