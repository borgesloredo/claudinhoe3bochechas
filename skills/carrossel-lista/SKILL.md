---
name: carrossel-lista
description: Use quando o usuário pedir carrossel de lista para Instagram (e TikTok, Kwai, Pinterest, YouTube, Facebook) — "carrossel", "post de lista", "carrossel do Instagram", "10 slides", "5 erros que...", "3 sinais de...", "qual desses é você?", ranking, tier list, antes e depois, checklist em slides, em lote ou um por um. Faz a pauta, o roteiro slide a slide (gancho da capa, regras de texto, CTA final), os prompts das imagens, monta os slides 1080×1350 com fonte e layout prontos, confere e escreve a legenda e as hashtags de cada rede. Dispare mesmo que a pessoa não diga "skill".
---

# Carrossel de lista

## O que esta skill faz
Transforma um tema do nicho em carrosséis de 6 a 10 slides que param o scroll: capa com um personagem inusitado numa cena improvável, um item por slide no mesmo molde, resumo no penúltimo e pedido de ação no último. O texto entra por cima das imagens com o gerador da skill, então acento e ortografia saem certos. O objetivo é salvar, compartilhar, comentar e seguir. Não é anúncio.

| Arquivo | O que tem |
|---|---|
| `scripts/carrossel.py` | Tudo em um: `validar`, `prompts`, `gerar` (slides PNG), `legenda` (texto de 6 redes), `tudo`, `--teste` |
| `fontes/` | Anton (capa) e Plus Jakarta Sans (miolo), licença OFL (uso comercial livre) |
| `referencias/GUIA-ROTEIRO.md` | Regras de texto, gancho da capa, os 10 formatos, imagens e o formato do `roteiro.json` |
| `referencias/ERROS-REAIS.md` | Regras que saíram de erros de uma produção real de 43 carrosséis |
| `exemplos/` | `config.json` e 3 roteiros reais: `001` passos (F1), `002` "qual desses é você?" (F2), `009` lista densa (F9) |

Caminho da skill: `K=~/.claude/skills/carrossel-lista`.

## Passo 0: Preparar (uma vez)
O gerador precisa de Python 3 com Pillow. Confira com `python3 -c "import PIL"`. Se faltar:
`python3 -m pip install --user pillow`. Se o pip recusar ("externally managed"), rode tudo com `uv run --with pillow python3 ...` no lugar de `python3 ...`.
Rode `python3 "$K/scripts/carrossel.py" --teste`: tem de sair `ok`.

## Passo 1: Conversa inicial (uma rodada só)
Pergunte numa chamada de AskUserQuestion, com o padrão como 1ª opção "(Recomendado)". Pule o que o pedido ou o projeto já responde.
| Campo | Padrão |
|---|---|
| nicho e produto | do pedido ou do projeto (o que o perfil ensina e o que vende) |
| persona e dores | quem segue o perfil e as 3 a 5 dores ou situações que mais aparecem |
| perfil @ | o @ que vai no rodapé e no botão "Siga" |
| cores | fundo escuro quente `#16110E`, destaque laranja `#F5A623`, texto creme (o do exemplo); ou as cores da marca |
| quantos e gerador de imagem | 1 carrossel; imagens no gerador que ele já usa (Higgsfield, ChatGPT, Gemini, Canva...). Sem gerador: degradê, só como rascunho |

Depois não pergunte mais nada: decida pela opção recomendada e conte no resumo final.

## Passo 2: Projeto e config
```bash
P="<pasta do projeto>/carrosseis"; mkdir -p "$P" && cp "$K/exemplos/config.json" "$P/config.json"
```
Edite `$P/config.json`: `perfil`, `nicho`, `cores`, `link` (site), `link_oferta` (página do produto), `palavra_ponte` (o que o CTA de ponte cita: "curso", "mentoria"...), `proibidas` (marcas e modelos de terceiros do nicho, em minúsculas) e `estilo_imagem` (troque a frase do equipamento pela do nicho).

## Passo 3: Pauta
Escreva `$P/PAUTA.md`: uma tabela `ID | formato | tipo | tom | ideia da capa`.
- Cada dor da persona vira 2 ou 3 ganchos. Varie os formatos F1 a F10 (`referencias/GUIA-ROTEIRO.md`).
- Cerca de 4 informativos (`info`) para 1 ponte para o produto (`ponte`).
- Prefira gancho negativo ("pare de", "o erro que", "a maioria") e identidade ("qual desses é você?").

## Passo 4: Roteiro slide a slide
Uma pasta por carrossel: `$P/001/roteiro.json`. **Siga `referencias/GUIA-ROTEIRO.md` à risca** e copie a estrutura de um exemplo de `exemplos/`. O essencial:
- Capa: até 12 palavras, com número quando couber; teste "lido em voz alta, preciso ver o slide 2?". Trecho entre `*` sai na cor de destaque.
- Miolo: um item por slide, `rotulo` curto ("PASSO 1", "ERRO 3"), `titulo` até 8 palavras, `texto` até 30. Termo técnico explicado na mesma frase. Número só com fonte.
- Último slide: um pedido de ação só (salve, envie, comente o número, marque o amigo). O gerador acrescenta os ícones e o botão "Siga @perfil": não repita "siga" no texto. Nada de prometer DM.
- `{perfil}` vira o @ do config.
```bash
python3 "$K/scripts/carrossel.py" validar "$P"/0*/
```
Corrija até todos darem `ok`. Leia `referencias/ERROS-REAIS.md` antes do primeiro lote.

## Passo 5: Imagens
```bash
python3 "$K/scripts/carrossel.py" prompts "$P/001"
```
Gera `$P/001/prompts.md`: um prompt pronto por imagem (cena + estilo + composição + "sem texto"). As imagens são salvas na pasta do carrossel como `IMG1.png`, `IMG2.png`... (png, jpg ou webp; qualquer tamanho, o gerador corta em 4:5).
- Se a sessão tiver uma skill ou conector de imagem (ex.: Higgsfield), gere por ela, com o mesmo modelo em todos os carrosséis. Antes de gerar em lote, mostre o 1º carrossel e diga o custo total.
- Senão, entregue o `prompts.md` ao usuário: ele gera onde preferir e salva os arquivos com esses nomes.
- Imagem que vier com letra, logo ou pessoa famosa: gere de novo.
- Modo B, `prompts "$P/001" --slide-inteiro`: a IA desenha o slide todo, com texto e gráfico. Fica mais rico em diagramas, mas a IA erra letras: confira cada slide letra por letra.

**Chave de API** (só se for gerar imagem por API): nunca no chat. Peça para o usuário abrir o app Terminal e rodar, trocando `NOME`:
```bash
mkdir -p ~/.config/carrossel-lista && printf 'Cole e tecle Enter: ' && read -rs k && printf 'NOME=%s\n' "$k" > ~/.config/carrossel-lista/NOME.env && chmod 600 ~/.config/carrossel-lista/NOME.env && echo && echo salvo
```
Use com `( set -a; . ~/.config/carrossel-lista/NOME.env; <comando> )`. Nunca mostre, copie nem grave o valor em arquivo do projeto.

## Passo 6: Gerar os slides
```bash
python3 "$K/scripts/carrossel.py" tudo "$P/001" ["$P/002" ...]
```
Valida, monta `slides/S01.png` a `S10.png` (1080×1350) e escreve `legenda.txt`. Leva poucos segundos por carrossel.
- `AVISO sem imagem (usei degradê)`: falta `IMGn` na pasta. Serve como rascunho; para publicar, gere a imagem.
- `AVISO ... texto não coube`: encurte o texto daquele slide e rode de novo.

## Passo 7: Conferir
Abra com Read, no mínimo, a capa, um slide do meio e o último de cada carrossel. Reduza antes para não pesar: `sips -Z 700 S01.png --out /tmp/ver-S01.png`.
- Título legível e longe do rosto do personagem; trecho em destaque certo.
- Palavra sozinha no fim da linha ("o", "a"): reescreva.
- Texto em cima de parte clara da imagem: gere a imagem de novo com a área do texto mais escura.
- Número de slides igual ao roteiro; nenhum slide faltando.
- Nenhuma marca, logo ou texto inventado pela IA dentro da imagem.

## Passo 8: Legenda e hashtags
`legenda.txt` sai pronto para Instagram, TikTok, Kwai, Pinterest, YouTube e Facebook, cada um com o ajuste da rede (link do perfil, "manda pro" no lugar de "marca", link no texto do Facebook, Pinterest sem pedido de comentário).
- A `legenda` do roteiro tem 3 a 6 linhas: repete a promessa da capa, diz o que tem no carrossel e termina com um pedido de ação. Não copie o carrossel inteiro.
- Hashtags: 5 a 8, sem marca, do nicho largo ao específico; o Instagram usa as 5 primeiras.

## Passo 9: Entregar
Responda com uma tabela (carrossel | formato | capa | slides), o caminho das pastas `slides/` e do `legenda.txt`, os avisos que sobraram e o que depende do usuário (gerar imagens, postar).
**Nunca publique sem o usuário pedir.** Ao postar pela web: desligue "compartilhar no Facebook" e escolha o corte 4:5.
