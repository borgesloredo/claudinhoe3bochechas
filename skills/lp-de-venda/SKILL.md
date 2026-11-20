---
name: lp-de-venda
description: Use when the user asks for a sales landing page (LP, página de venda, página de vendas, landing page) for a digital product he owns — ebook, livro digital, apostila, curso (inclusive os cursos de mesa de som), edição interativa — especially one close to "Mixagem em mesa de som digital", with checkout (Mercado Pago or an external platform link), animation and conversion copy.
---

# Página de venda (multiagente)

## Visão geral
Uma execução entrega uma página de venda interativa e animada, com checkout, para um produto digital. Cada etapa passa por 3 avaliadores (revisor, storytelling e caça-repetições), com nota mínima 8,5. A orquestração está pronta em `workflow.js`, nesta pasta. Você só faz as perguntas, monta os `args` e lança. Não reescreva os prompts.

Origem: a LP do livro "Mixagem em mesa de som digital" (out/2026). Projeto de referência: `/Users/SEU-USUARIO/SEU-PROJETO/curso-xr18/lp/` (página, checkout e `docs/01..06`). Backend do checkout: `borgesloredo/ml-server/supabase` (funções `lp-pay`, `lp-status`, `lp-webhook`, `lp-dl`, tabela `lp_orders`, branch `feat/lp-checkout`).

**Padrão de qualidade (obrigatório desde 05/11/2026):** a LP da XR18 (`curso-xr18/lp/`, loredoborges.com.br/xr18) é o 100% em motion, gráficos, animação e acabamento. Toda LP segue o padrão. Só o estilo de botões, ícones e painéis muda: eles imitam o hardware da mesa daquela LP. A LP da 01V96 (`curso-01v96/lp/`) foi refeita assim e aprovada, e é o exemplo de como aplicar o padrão a outra mesa. A especificação seção por seção e os testes estão em `padrao-xr18.md`, nesta pasta. O workflow injeta esse arquivo nas etapas Visual, Motion e QA e nos revisores delas.

Etapas: Estudo (conteúdo, identidade e, se não houver `venda_ref`, técnicas de venda; sem revisão) → Copy (3 lentes) → Visual → Motion e Checkout (em paralelo; só o revisor) → QA final (revisor + repetições). De 15 agentes (tudo aprovado de primeira) a ~33 (pior caso; Motion tem 3 rodadas). A 1ª execução, antes do enxugamento de 27/10/2026, usou 32 a 88 agentes, ~14 M tokens e 16 h. Rodadas com navegador levam 1 a 2 h cada.

## Passo 1: Prepare (sem perguntar nada)
1. Ache as fontes do produto: o PDF, a edição interativa (HTML), a descrição já escrita e os prints. Se estiverem num zip, extraia para uma pasta nova no scratchpad.
2. Confira as permissões: `~/.claude/settings.json` não pode ter `mcp__chrome-devtools__*` na lista `ask`. Se tiver, os agentes param a cada clique no navegador, esperando aprovação. Avise o usuário e proponha tirar.
3. Leia a memória do projeto. Lá estão regras que valem aqui: preço sempre R$ 97 (não pergunte), o que nunca citar e o que já está à venda em outro canal.
4. No projeto do dono, um hook bloqueia comandos com a palavra `mercadolivre`. Nos `args`, use caminhos que não contenham essa palavra.

## Passo 2: Pergunte (uma chamada de AskUserQuestion, depois siga sozinho)
Não pergunte o layout: use `layout: "padrao"`. Só use `referencia` se o usuário mandar uma referência própria. Mesmo assim, o padrão de qualidade continua valendo. Faça as outras perguntas só quando o pedido ou a memória não responderem. Ponha a recomendada em 1º lugar, com "(Recomendado)". Se nada faltar, não pergunte e lance.

| Pergunta | Opções (a 1ª é a recomendada) |
|---|---|
| Checkout | **Mercado Pago próprio**: o link temporário mostra um checkout de demonstração, e o backend fica pronto para quando houver credenciais. / **Link de plataforma** (Hubla, Ticto, Kiwify): os CTAs vão para a URL que ele der. / **Só demonstração**. |
| Autor exibido | **Matheus Borges** / nome da loja / sem nome. |
| Produto | Pergunte só se o pedido não deixar claro qual produto e quais arquivos usar. |

Não pergunte preço, depoimentos nem números de venda. A página só usa fatos das fontes. O que faltar vira `<!-- CONFIRMAR -->`. Não crie etapa de aprovação no meio: os avaliadores com nota cumprem esse papel. Depois das respostas, rode até o fim sem pedir ok.

## Passo 3: Monte os args e lance
Antes, crie a pasta de saída e uma branch nova:
```bash
mkdir -p "<base>/img" "<base>/docs"
git -C "<base>" init -q -b main
git -C "<base>" commit -q --allow-empty -m "chore: init"
git -C "<base>" switch -c feat/lp-<slug>
```
No modo `mp`, o backend também precisa de branch nova no repositório `ml-server`. Copie para `<base>/img/` os prints que já existirem.

```js
Workflow({ scriptPath: "/Users/SEU-USUARIO/.claude/skills/lp-de-venda/workflow.js", args: {
  base: "/abs/<projeto>/curso-<mesa>/lp",  // a LP fica dentro da pasta do curso (07/11/2026)
  produto: {
    nome: "Título do produto", subtitulo: "do primeiro cabo ao show",
    formato: "livro digital de N páginas (PDF) + edição interativa (HTML, abre no navegador do computador, funciona offline)",
    preco: 97, autor: "Matheus Borges", garantia_dias: 7,
    publico: "quem opera ... na igreja, banda, evento ...",
    entrega: "após a aprovação, o link de download aparece na tela e chega por e-mail; nada é enviado pelo correio",
    extras: "- texto e diagramas feitos com apoio de IA e organizados por mim (dizer no FAQ, sempre em primeira pessoa)\n- cobre só as famílias X e Y" },
  fontes: { conteudo: "/abs/livro.pdf", interativo: "/abs/edicao.html", outros: ["/abs/descricao.txt"] },
  imagens: "/abs/pasta-de-prints",
  layout: "padrao",                // "padrao" (sempre) | "referencia" (só com referência do usuário)
  layout_ref: "",                  // só no modo "referencia"
  checkout: { modo: "mp",          // "mp" | "externo" | "demo"
    url_externa: "",
    api_base: "https://SEU-PROJETO.supabase.co/functions/v1",
    backend: "/Users/SEU-USUARIO/SEU-PROJETO/ml-server/supabase" },
  regras_extra: "- <regras da memória/CLAUDE.md: o que nunca citar, marcas, features 'em breve'>",
  venda_ref: "/Users/SEU-USUARIO/SEU-PROJETO/curso-xr18/lp/docs/03-tecnicas-venda.md",  // pesquisa já validada: pula o estudo de venda
  autor_fatos: "/Users/SEU-USUARIO/SEU-PROJETO/geral/expert/perfil-expert.md" } })
```
Confira que todo caminho de `fontes` existe antes de lançar. O Workflow só aceita `scriptPath` dentro do diretório de trabalho: copie antes `workflow.js` para `<base>/.workflow.js` e passe esse caminho.

## Passo 4: Durante a execução
- Avise o usuário em uma linha a cada fase concluída. Para ver as notas, leia o `journal.jsonl` no `Transcript dir`: cada linha `result` traz a nota.
- **Travou ou o limite de uso acabou:** se `stat -f %Sm <dir>/journal.jsonl` não muda há mais de 30 min, use `TaskStop` e depois `Workflow({scriptPath, resumeFromRunId, args})`, com os mesmos args. As etapas prontas vêm do cache.
- **O usuário pergunta a previsão:** conte as rodadas que faltam, a 1–2 h cada. Seja honesto: as rodadas com navegador são lentas.

## Passo 5: Feche a entrega
1. Se uma etapa terminou sem aprovação, decida pelo efeito na venda. Estudo e copy são material de trabalho: registre a nota e siga. A página precisa do **QA final aprovado**. Se o QA não passou, rode um workflow pequeno só de QA. Não refaça os docs de estudo: na 1ª execução a nota oscilou entre 7,4 e 8,3 por 7 rodadas, sem convergir.
2. Modo `mp`: rode os testes:
   ```bash
   DENO=$(ls ~/.npm/_npx/*/node_modules/@deno/darwin-arm64/deno | head -1)
   cd <backend>/functions && $DENO test _shared/ && $DENO check lp-*/index.ts
   ```
   Se não houver binário, use `npx -y deno@2.1.4`. Leia o `git diff` de código que já está no ar, que o agente pode ter refatorado, e conte ao usuário.
3. Publique a prévia com a ferramenta Artifact: `file_path` = `<base>/index.html`, e `files` com `checkout.html` e só as imagens usadas (`grep -ohE 'src="img/[^"]+"' index.html checkout.html | sort -u`). Use `root` na pasta pai, `icon: "book"` e uma `description` de uma frase. Para atualizar depois, publique o mesmo `file_path`.
   Entregue também a prévia local, porque o Artifact às vezes não abre para ele. Recrie `<base>/.preview.html` (o QA apaga esse arquivo): doctype, charset e viewport mais o conteúdo de `index.html`. Sirva `<base>` com `python3 -m http.server 8765` em segundo plano e mande `http://localhost:8765/.preview.html`.
4. Responda: link, notas finais por etapa, o que ficou abaixo de 8,5 e por quê, e as pendências do dono (lista abaixo). Explique que o link é privado até ele compartilhar.
5. Atualize a memória do projeto: pasta, link, notas e pendências.

## Pendências que sempre sobram para o dono
Pegue a lista exata com `grep -o 'CONFIRMAR[^>]*' index.html checkout.html`.
- Credenciais do Mercado Pago e os secrets. Passo a passo em `docs/05-checkout-setup.md`. Deploy e migration só com o ok dele.
- Arquivos de entrega no bucket privado `entregas` (zip e PDF), nos caminhos do catálogo.
- E-mail de contato e de reembolso. Dados do vendedor no rodapé (Decreto 7.962/2013). Nota fiscal. Validade do link de download.
- Bio do autor: vem de `autor_fatos` (`expert/perfil-expert.md`); sem esse arquivo, fica oculta.
- Os "Alertas para o dono" de `docs/01-conteudo.md`: capa dizendo "oficial" ou "curso", páginas com propaganda ou telefone, LEIA-ME apontando para outro canal, marcas citadas.
- `og:image` com URL absoluta e o domínio. Para domínio próprio, recomende a Vercel.

## Erros comuns
| Erro | Correção |
|---|---|
| Testar `index.html` cru no navegador e achar que o celular quebrou (renderiza em 980 px) | O workflow testa via `.preview.html` com a meta viewport, igual ao Artifact |
| Agentes parados esperando aprovação de clique no Chrome | Passo 1.2: tirar `mcp__chrome-devtools__*` da lista `ask` |
| Editar a página depois do QA e a nota de repetições cair de 8,7 para 7,4 | Depois do QA, a página é a fonte da verdade. Toda mudança nela pede outro QA |
| Revisor tratando ligação causal editorial como fato do livro | O estudo separa "fatos do produto" de "leitura editorial"; a copy só afirma fatos |
| Checkout real dentro do Artifact | Impossível: o CSP bloqueia o SDK do Mercado Pago e o fetch. Mostre o modo demonstração e diga isso |
| Backend com um produto só | O agente de checkout transforma `lp_logic.ts` num catálogo `PRODUCTS` por slug e adiciona `lp_orders.product`, sem quebrar o produto antigo |
| Afirmar "pronto" sem testes | Rode os testes do Deno (Passo 5.2) antes do resumo |
| LP com 80% do padrão: mesa parada, beats que só esmaecem, sem visor com onda, sem 2ª demonstração, sem trilho de leitura (a 1ª versão da 01V96) | Siga `padrao-xr18.md` seção por seção e compare lado a lado com a XR18 antes de dar por pronto |
| Cena com estado errado depois de rolar rápido (ganchos de beat atrasados sobrescrevem a correção) | Os ganchos da história param quando o leitor ou a correção automática aperta a tecla certa |
| Teste em 1440 que na verdade renderiza em 2160 (Chrome do dono com zoom de 67%) | Confira `innerWidth`. Emule 960x600 para ter 1440x900 em CSS |
| "GSAP target not found" no console | `flick`/`blink` nunca recebem lista vazia. Intercepte `console.warn` e role a página inteira |
