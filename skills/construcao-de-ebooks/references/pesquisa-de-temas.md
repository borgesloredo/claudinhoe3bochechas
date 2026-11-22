# Pesquisa de dores e temas

Objetivo: 5 temas que saíram de dores reais do nicho, cada um com prova.

## Onde procurar
Mande as buscas em paralelo, várias na mesma mensagem.

| Camada | O que procurar | Onde | Tipo de prova |
|---|---|---|---|
| Panorama | tamanho do público, mudanças e notícias do último ano | órgãos públicos, associações, imprensa, estudos | `panorama` |
| Voz do público | reclamações, perguntas repetidas, "não consigo", "tenho medo", "já tentei" | **obrigatório:** `python3 -I "$K/scripts/publico.py" "busca" "outra"` (comentários reais do YouTube). Some páginas de perguntas abertas com WebFetch (ex.: Doctoralia), Reddit, avaliações de livros e cursos, Instagram, TikTok, Kwai | `publico` |
| Audiência | quanta gente assiste a esse problema | as visualizações e a data que o `publico.py` traz | `audiencia` |
| Procura | o que digitam | `python3 -I "$K/scripts/demanda.py" "termo" "outro"` e as perguntas relacionadas do Google | `busca` |
| Interesse | comparação e tendência | Google Trends Brasil, 12 meses e 5 anos | `trends` |
| Oferta | o que já se vende, preço, promessa, o que as avaliações dizem que falta | Hotmart, Kiwify, Eduzz, Udemy, Amazon, perfis de referência do nicho | `oferta` |

**Dor sai da boca do público, não de artigo.** Faça de 3 a 5 buscas no `publico.py` (uma por recorte), leia os comentários, agrupe por dor e conte: "apareceu em 9 de 120 comentários, em 4 vídeos". Ignore elogio e propaganda. Separe quem fala: o profissional e o cliente dele têm dores diferentes, e o e-book é para um deles.

Grave a saída dos scripts em arquivo e leia de lá, inteira. Copie as URLs exatamente como vieram.

Comece largo (o nicho), ache 3 a 4 recortes (público + problema) e repita as buscas dentro deles. "Estética" é largo; "esteticista iniciante com medo de manchar a pele da cliente na extração" é um recorte.

## Cuidados com os números
- **Sugestão de busca não é volume.** Descarte as que são só cidade, bairro ou "perto de mim".
- **Google Trends:** use pelo navegador, quando houver um. Só compare termos que estavam **no mesmo gráfico** (até 5), repetindo um termo-âncora entre gráficos. A escala vai de 0 a 100 e é relativa. Se bloquear (429) ou não abrir, escreva "não medido". Não contorne bloqueio.
- **Rede social sem acesso:** tente `site:instagram.com`, `site:tiktok.com`, `site:kwai.com` na busca e diga que leu só o resultado. Costuma vir vazio: registre "não medido" e não insista. Não faça login, não comente, não siga ninguém.
- Uma reclamação isolada não é "a maior dor". Diga em quantos lugares ela apareceu.
- Não transforme amostra pequena em porcentagem.
- Não copie nome ou dado pessoal de quem comentou.

## Nota de cada tema
De 1 a 10 em cada critério. A nota final é a média geométrica, que derruba o tema fraco em qualquer um deles.
- `dor`: quanto aparece e quanto incomoda. Acima de 5 exige prova `publico`.
- `procura`: se as pessoas buscam solução. Acima de 5 exige `busca`, `trends` ou `audiencia`. Para `busca`, a URL é o campo `prova` do `demanda.py`.
- `lacuna`: o que a oferta atual deixa sem resolver. Acima de 5 exige `oferta`. Abra com WebFetch o concorrente mais próximo de cada tema. Se só viu o título, diga "lacuna estimada pelos títulos".
- `aplicacao`: se um e-book curto leva a pessoa a um resultado rápido e com pouco esforço. Tema que só se aprende na prática supervisionada tem nota baixa.

O projeto ainda não existe: grave `temas.json` na pasta temporária da sessão (ou em `mktemp -d`) e copie para `$R/pesquisa/` depois do setup:
```json
[{"titulo":"…","dor":"…","publico":"…","promessa":"…","trends":"não medido",
  "evidencias":[{"tipo":"publico","url":"https://…","achado":"o que foi visto, em suas palavras"}],
  "notas":{"dor":8,"procura":6,"lacuna":7,"aplicacao":8}}]
```
Rode `python3 -I "$K/scripts/temas.py" <arquivo>` e corrija o que reprovar. Baixar a nota é correção válida; criar prova, não.

## Como mostrar
Cada sugestão em 5 linhas curtas:

> **1. Título do e-book** (nota 7,4)
> **Para quem:** …
> **Dor:** …
> **Prova:** quantos comentários, quantas visualizações ou qual busca, com 2 links
> **Por que vale:** o que a concorrência não resolve

Termine com a sua recomendação em uma linha, o que não foi possível medir e "Qual você escolhe? Se quiser, trago outras 5."
