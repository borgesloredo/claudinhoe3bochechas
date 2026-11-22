# Contrato de arquivos

Tudo fica em `R`. Os scripts montam. **Nunca edite `entregas/` ou `amostra/` à mão.**

## `pesquisa/fontes.json`
```json
{"cobertura":{"documentacao":"o que buscou e achou","livros":"…","cursos":"…","ebooks":"…","blogs":"…",
              "youtube":"…","instagram":"…","tiktok":"…","kwai":"sem acesso: motivo"},
 "fontes":[{"id":"f1","url":"https://…","titulo":"…","papel":"tecnica","lido":"pagina","usado_para":"…"}]}
```
`papel`: `tecnica` ou `didatica`. `lido`: `pagina`, `resumo`, `transcricao` ou `so-resultado-de-busca`.

## `plano.json`
```json
{"capitulos":["Nome do capítulo 1","Nome do capítulo 2"],
 "telas":[{"id":"capa","cap":0,"tipo":"capa","titulo":"…","conceito":"o que a animação demonstra","fontes":[],"amostra":true}]}
```
- `telas` tem exatamente `paginas` itens, na ordem de leitura.
- Tipos: `capa`, `sumario`, `abertura`, `topico`, `quiz`, `glossario`, `aviso`, `encerramento`.
- Capa, sumário e encerramento têm `cap: 0`. Os capítulos são contados a partir de 1, em ordem.
- `id` em minúsculas, números e hífen. Todo `topico` lista os ids de suas fontes.
- 4 a 6 itens com `amostra: true`, incluindo capa, abertura, tópico com diagrama e quiz.

## `conteudo/`
| Arquivo | Para | O que contém |
|---|---|---|
| `tema.css` | slides, autoestudo | variáveis `--fora`, `--tinta`, `--destaque` e as classes do visual |
| `pagina.css` | PDF | estilo das páginas A4 |
| `telas/<id>.html` | slides, autoestudo | miolo da tela, sem `<section>` |
| `telas/<id>.js` | slides, autoestudo | animação da tela |
| `paginas/<id>.html` | PDF | miolo de uma página, sem `<article>` |
| `notas/<id>.html` | slides | nota do apresentador |
| `info/<id>.html` | autoestudo | texto do (i) |
| `roteiro/<id>.txt` | autoestudo | narração |
| `glossario.json` | autoestudo | `{"comedao":{"termo":"Comedão","definicao":"…"}}` |

Escreva só o que os arquivos pedidos usam. Classes do CSS levam prefixo próprio. No SVG, prefixe os ids com o id da tela.

Marcadores que o montador preenche: `{{titulo}}`, `{{autor}}`, `{{contato}}` e, no sumário, `<nav data-sumario></nav>`. Na página do PDF, `h1` na capa e `h2` nos títulos viram os marcadores laterais: escreva cada um numa linha só e use `p` com classe para subtítulos (`h3` a `h6` são recusados).

O que o montador entrega ao seu CSS:
- tela: `section.tela.tela-<tipo>`, 1280 x 720; quiz: `[data-quiz][data-resposta="certa|errada"]` e `button.escolhida`;
- página: `article.pagina.pagina-<tipo>`, padding 18/16/20 mm, com o número em `.folio`;
- fonte local: `url("fonts/arquivo.woff2")`.

Quiz no PDF: a página traz as alternativas e a resposta de cabeça para baixo no pé, acima do rodapé.

Animação:
```js
EBOOK.anima('id-da-tela', ({ el, tl, gsap, $, $$ }) => {
  tl.from($('.camada-1'), { y: 40, opacity: 0, duration: .6 })
    .from($('.traco'), { drawSVG: 0, duration: 1 })
    .to($('.poro'), { scale: 1.2, duration: .5 });
});
```
`tl` já vem pausada e é tocada na entrada. `$` e `$$` procuram só dentro da tela. SplitText, DrawSVG, MotionPath e CustomEase já estão registrados.

Quiz:
```html
<div data-quiz>
  <button type="button">Alternativa</button>
  <button type="button" data-certa>Alternativa certa</button>
  <p data-retorno="certa">Por que está certa.</p>
  <p data-retorno="errada">O que pensar antes de tentar de novo.</p>
</div>
```
Termo clicável no (i): `<button type="button" class="gl" data-t="comedao">comedão</button>`.

Proibido no conteúdo: script, style, iframe, srcset ou animação SMIL (`set`, `animate`) no HTML, atributos `on...`, endereço externo, caminho `../`, rede ou `eval` no JS.

## Comandos
```bash
node "$K/scripts/montar.cjs" "$R" [--amostra]
node "$K/scripts/conferir.cjs" "$R" [--amostra]   # folhas em qa/amostra ou qa/final
```
