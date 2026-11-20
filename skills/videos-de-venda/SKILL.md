---
name: videos-de-venda
description: Use when the user asks for sales/ad videos (vídeo de venda, anúncio, tráfego pago, criativo, vídeo para Mercado Livre, Reels/Stories de oferta) for a product, course, deck or manual they own — especially several variations (consultivo, agressivo, etc.) in the product's own visual identity.
---

# Vídeos de venda (multiagente, HyperFrames)

## Visão geral
Uma execução gera N variantes de vídeo de venda (padrão: 4). O trabalho roda em paralelo máximo, e um revisor dá nota a cada etapa. A orquestração está pronta em `workflow.js`, nesta pasta. Você só monta os `args` e lança o workflow. Não reescreva os prompts.

## Economia de tokens (versão enxuta, 09/11/2026)
O lote de 09/11 (4 mesas, tudo em Opus) gastou ~6,5 M tokens por mesa. 90% foi em build, fix e revisão de vídeo: contexto enorme (skills do HyperFrames lidas em todo agente, ~90 quadros por revisão, mixagem reescrita do zero em cada vídeo). A versão enxuta corta isso assim:

| Micro-tarefa | Modelo | Por quê |
|---|---|---|
| kit visual, roteiro, build | Opus (herda da sessão) | criação: define a qualidade |
| ficha, mapa, revisor de roteiro, revisor de vídeo, fix, revisor cruzado | Sonnet, esforço médio | julgar ou aplicar uma lista de correções |
| mapa reaproveitado, entrega | Haiku, esforço baixo | cópia e resumo |
| pesquisa de vendas, música | nenhum (cópia de `geral/videos-de-venda-compartilhado/`) | é igual para todas as mesas |
| medir áudio, quadro parado, tela preta, texto proibido, palavras por tela | script (`tools/checar.py`, `tools/lint-roteiro.py`) | regra objetiva não precisa de modelo |
| mixagem | script (`tools/mixar.py`) | mesma receita em todo vídeo |
| montar o index.html (raiz, seções, tempos pela voz, áudio, ROTEIRO-FINAL) | script (`tools/montar.py` + ajudantes GSAP `tools/vv.js`) | cada build escrevia o próprio gerador (build.py de 42 KB); agora o Opus escreve só as cenas |
| estrutura do roteiro | `MOLDES-ROTEIRO.md` (batidas por abordagem, tiradas dos aprovados) | menos rodadas de roteiro |

- Regras num arquivo curto por papel: `geral/videos-de-venda-compartilhado/REGRAS-AGENTE.md`. HyperFrames resumido em `HF-RESUMO.md` (no lugar de ~40 KB de skills).
- Revisor olha folhas de contato (4x3 quadros por imagem), não 90 quadros soltos. Construtor: no máximo 8 imagens abertas (as 16 montagens do lote 1 abriram 231).
- Os 9 defeitos que mais reprovaram (análise de 92 pareceres) estão no REGRAS-AGENTE.md; o `checar.py` avisa "faixa vazia", o defeito nº 1.
- Rodadas: roteiro aceita 8,5 já na 2ª rodada; vídeo tem no máximo 2 correções.
- Ferramentas instaladas que ajudam: `rtk` (encurta a saída dos comandos, hook global), caveman (respostas curtas), ponytail. Medir: `rtk gain`.
- Teste das ferramentas: `python3 tools/<x>.py --teste`.

## Passo 1: Verifique o limite de uso
Rode `node "$P/skills/hyperframes/scripts/plugin-cli.mjs" usage --json`. Para achar `$P`, use `ls -d ~/.claude/plugins/cache/hyperframes/hyperframes/*/ | tail -1`. Uma execução completa com 4 variantes usava cerca de 6,5 a 9 milhões de tokens de subagentes, todos em Opus; a versão enxuta deve ficar bem abaixo (medir na primeira mesa). Numa conta Team, 6% do limite semanal não bastou e a execução parou no meio. Se o `weekly.remainingPercent` estiver abaixo de 40, explique isso e pergunte se roda agora ou depois do reset (`resetsAt`). Se o usuário escolher agora, o resume do Passo 4 cobre o que parar.

## Passo 2: Faça as 3 perguntas (uma chamada de AskUserQuestion)
Pergunte sempre os 3 campos, com o padrão como 1ª opção "(Recomendado)". Omita um campo só quando o pedido já trouxer a resposta (exemplo: "vídeo vertical"). Em variantes, use multiSelect.
| Campo | Padrão recomendado |
|---|---|
| formato | `9:16` (Reels, Stories e Clips do Mercado Livre) |
| audio | `musica` (texto animado + música, funciona sem som) |
| variantes | consultivo, agressivo, antes-depois, demonstracao |

Duração (padrão 30–60 s), CTA (padrão "Garanta o seu") e material vêm do pedido ou do projeto. Não pergunte preço nem depoimento: o vídeo só usa fatos do material. Não crie etapa de aprovação de roteiro no meio: o revisor com nota cumpre esse papel, e o usuário quer o trabalho rodando até o fim.

## Passo 3: Monte os args e lance
```js
Workflow({ scriptPath: "~/.claude/skills/videos-de-venda/workflow.js" /* caminho absoluto */, args: {
  base: "/abs/<projeto>/08-videos",            // saída
  produto: "Curso X sobre Y, marca Z",
  fontes: ["/abs/curso.md", "/abs/slides/index.html", "/abs/pdf/"],
  design: "/abs/DESIGN.md", fonts: "/abs/fonts",
  plugin: "<$P sem barra final>",
  formato: "9:16", audio: "musica", duracao: "30-60", cta: "Garanta o seu",
  regras_extra: "- <só o que o REGRAS-AGENTE.md não cobre: layout da mesa, nomes proibidos, features 'em breve'>",
  destino: "/abs/<projeto>/videos-de-venda",    // opcional: a entrega copia os MP4 para cá
  variantes: [
    { id: "consultivo",   abordagem: "consultiva: diagnóstico calmo, autoridade" },
    { id: "agressivo",    abordagem: "agressiva: quebra de padrão, urgência honesta, PAS" },
    { id: "antes-depois", abordagem: "antes/depois/ponte, Story Spine" },
    { id: "demonstracao", abordagem: "demonstração do produto em ação" } ] } })
```
Coloque em `regras_extra` as regras do CLAUDE.md e da memória do projeto (o que nunca citar, a marca, features ainda não lançadas). Antes de lançar, confira que `design`, `fonts` e cada item de `fontes` existem.

## Passo 4: Durante a execução
- Avise o usuário em uma linha a cada fase concluída.
- **O limite acabou ou o workflow travou:** o resultado do Workflow informa o `Transcript dir`. Rode `stat -f %Sm <dir>/journal.jsonl`. Se o arquivo não muda há mais de 30 min, ou se o usuário avisar que o limite resetou, use `TaskStop` e depois `Workflow({scriptPath, resumeFromRunId, args})`, com os mesmos args. As etapas prontas vêm do cache.
- **O workflow retornou `{erro}`:** corrija a causa (caminho errado, fonte ilegível) e retome do mesmo jeito.
- **Mudar algo no meio:** lance um workflow menor só para as variantes afetadas. Antes, copie os MP4 atuais para `entregas-vN/`.

## Passo 5: Feche a entrega
1. `ENTREGA.md` já traz o resultado do `tools/checar.py` de cada MP4. Gere uma folha de contato por vídeo (`ffmpeg -i X.mp4 -vf "fps=1/4,scale=180:-1,tile=6x2" -frames:v 1 X.png`) e olhe com Read.
2. Termos proibidos: o `checar.py` já procura no HTML; confira também nomes vetados do projeto nos `ROTEIRO-FINAL.md`.
3. Responda com uma tabela (vídeo | abordagem | duração | nota), o caminho de `ENTREGA.md` e o que depende do usuário: licença da música, capa no upload, features "em breve".
4. Projeto do dono: o painel (loredoborges.com.br/painel/) só marca os vídeos que estão no R2, e os MP4 ficam fora do git. Com os MP4 finais em `curso-<x>/videos-de-venda/`, rode em `ml-server-pagamentos` do projeto: `bash -c 'set -a; source ../.env; set +a; deno run -A lp/subir-cursos.ts curso-<x>'`. Arquivos iguais aos do R2 são pulados.
5. Na memória persistente (seção Memory do system prompt), atualize o arquivo `type: project` do produto, ou crie um. Registre a pasta, as notas e as pendências.

## Narração (quando o áudio pedir voz)
Gerar áudio demais para o Matheus aprovar depois foi o maior retrabalho. Siga nesta ordem:
1. **Voz:** use a aprovada (Gemini TTS `Puck`, estilo "reels2", `geral/videos-de-venda-compartilhado/voz/` no projeto do dono). Só gere amostras se ele pedir voz nova. Nesse caso, gere no máximo 5, cada uma de uma voz ou modelo diferente (semente ou parâmetro diferente não conta). Não gere narração de vídeo antes do "aprovado".
2. **Texto:** escreva o `.txt` de cada fala no registro em que a voz fala ("Tá", "Aperta", nome da coisa em vez de letra solta, termo em português em vez de inglês minúsculo). A tabela fica em `ERROS-COMUNS.md`, seção 1.
3. **Geração:** uma chamada por vídeo com todas as falas: `gen_gemini.sh voz/c01.txt voz/c01.m4a ...`. O script recusa texto com padrão de risco antes de gastar o pedido. Depois ele confere cada fala no Whisper e mostra `OK` ou `CONFERIR`.
4. **Correção:** se aparecer `CONFERIR`, dê `touch` só nos `.txt` listados e rode de novo (1 pedido). Na 2ª falha da mesma frase, reescreva a frase.
5. Só monte e renderize o vídeo quando todas as falas estiverem `OK`. Para o Matheus vai só o vídeo final, sem falas soltas para aprovar.

## Erros comuns
**Antes de começar, leia `ERROS-COMUNS.md` (nesta pasta).** Ele lista voz, roteiro, montagem, áudio e processo, e o workflow manda todo agente ler. Erro novo que custar retrabalho entra lá. Resumo dos mais antigos:

| Erro | Correção |
|---|---|
| Música sintetizada (soa fraca) | Faixas Mixkit prontas em `geral/videos-de-venda-compartilhado/musica/` |
| Roteiro escrito por um agente só, empacado em 8,2 | O mapa de diferenciação mais um roteirista por variante evita isso |
| Quadros sobrepostos na troca de cena, texto < 36 px | Já está nas REGRAS do workflow; o revisor reprova |
| Telefone, URL ou cupom no vídeo | O Mercado Livre proíbe; o link vai no botão do anúncio |
| Sobrescrever um MP4 aprovado | O fix sempre copia o MP4 para `renders/<id>-rN.mp4` antes |
