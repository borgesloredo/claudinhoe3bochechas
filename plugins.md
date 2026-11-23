# Plugins

Plugin = pacote de skills/comandos instalado de um marketplace (loja). Todos de terceiros: só link, sem cópia.

Instalar: `/plugin marketplace add <dono/repo>` e depois `/plugin install <plugin>@<marketplace>`.

**Para marcar que você usa:** troque o espaço vazio da sua coluna por ✅ e faça commit. Plugin novo: adicione uma linha.

| Plugin | O que faz | Origem | Matheus | Arthur | Lucas |
|---|---|---|:-:|:-:|:-:|
| `superpowers` | Brainstorm, plano, TDD, revisão | [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) | ✅ | | |
| `hookify` | Cria regras/hooks a partir de erros | [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) | ✅ | | |
| `pr-review-toolkit` | Revisão de PR com vários agentes | [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) | ✅ | | |
| `commit-commands` | Comandos de commit e PR | [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) | ✅ | | |
| `claude-code-setup` | Recomenda automações para o projeto | [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) | ✅ | | |
| `feature-dev` | Desenvolvimento guiado de funcionalidade | [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) | ✅ | | |
| `code-review` | Revisão de código | [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) | ✅ | | |
| `claude-md-management` | Mantém o CLAUDE.md | [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) | ✅ | | |
| `swift-lsp` | Suporte a Swift | [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) | ✅ | | |
| `vercel` | Deploy e ferramentas Vercel | [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) | ✅ | | |
| `document-skills` | docx, pdf, pptx, xlsx | [anthropics/skills](https://github.com/anthropics/skills) | ✅ | | |
| `example-skills` | Skills de exemplo (design, MCP, slides) | [anthropics/skills](https://github.com/anthropics/skills) | ✅ | | |
| `claude-api` | Referência da API da Anthropic | [anthropics/skills](https://github.com/anthropics/skills) | ✅ | | |
| `caveman` | Respostas curtas, menos token | [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) | ✅ | | |
| `ponytail` | Código mínimo | [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) | ✅ | | |
| `ui-ux-pro-max` | Design UI/UX, slides, marca | [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) | ✅ | | |
| `context7` | Documentação atualizada de bibliotecas | [upstash/context7](https://github.com/upstash/context7) | ✅ | | |
| `understand-anything` | Grafo e guia de um código | [Egonex-AI/Understand-Anything](https://github.com/Egonex-AI/Understand-Anything) | ✅ | | |
| `hyperframes` | Vídeo em HTML/código | [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes) | ✅ | | |
| `aia-harness` | Estrutura e auditoria de projetos | [leandrosilvaferreira/claude-plugins-registry](https://github.com/leandrosilvaferreira/claude-plugins-registry) | ✅ | | |

## Ferramentas externas

Ferramentas investigadas e compartilhadas, mas que não são skills/plugins instaláveis pelo marketplace.

| Ferramenta | O que faz | Origem | Status |
|---|---|---|---|
| `G0DM0D3` | Interface de red team que disputa respostas entre dezenas de modelos usando prompts de jailbreak | [elder-plinius/G0DM0D3](https://github.com/elder-plinius/G0DM0D3) | Não instalado. Exige OpenRouter/Venice ou modelos locais, guarda chave no navegador e ativa telemetria de metadados por padrão |
