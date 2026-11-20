# Guia do roteiro (roteiro.json)

Leia antes de escrever qualquer carrossel. Um carrossel = uma pasta com `roteiro.json`.

## Regras de conteúdo

1. Nunca cite marca, modelo ou fabricante de produto de terceiros. Ponha os nomes da concorrência e do nicho em `proibidas` no `config.json`: o validador recusa.
2. Conteúdo genérico: o cenário nunca fica preso a um só contexto. Ex.: no som ao vivo, igreja aparece como um cenário entre outros (show, evento, casamento, bar, banda). Cada restrição corta público.
3. Português do Brasil simples e direto. Termo técnico novo ganha explicação curta na mesma frase (ex.: "HPF, o filtro que corta o grave que não serve").
4. Conteúdo tecnicamente correto. Números (Hz, dB, ms, preços, prazos) vêm como "ponto de partida, confirme". Na dúvida, não invente número. Número que aparece no slide tem de bater com a fonte (página de venda, manual).
5. Tom: cômico = situação real exagerada, sem humilhar ninguém; negativo = "pare de", "não", "erro", "a maioria"; orgulho = valoriza a profissão; neutro = didático.
6. Nenhuma pessoa real ou famosa. Personagens são arquétipos (juiz, avó, monge, lutador, chef, piloto, astronauta, cowboy, bailarina...). O contraste entre quem é o personagem e o que faz é o que para o scroll. Varie os arquétipos.
7. Produtos e equipamentos nas imagens: genéricos, sem logotipo, sem texto legível.

## Estrutura

- 6 a 10 slides, 4:5 (1080×1350). Educativo: 8 a 10. Dica rápida: 6.
- Slide 1 = capa. Título até 12 palavras, forte, com número quando fizer sentido. Teste: lido em voz alta, a pessoa precisa ver o slide 2?
- Slide 2 pode ser "sobrecapa" (virada que aumenta a curiosidade) ou já o 1º item.
- Um item por slide, sempre no mesmo molde. O contador "3/10" e o @ entram sozinhos na montagem: não escreva.
- Penúltimo pode resumir (checklist, placar, ranking final).
- Último = CTA (pedido de ação). O gerador põe os ícones "Salve / Envie" e o botão "Siga @perfil" sozinho.
  - `info`: salvar, enviar para alguém, marcar o amigo, comentar o número ou o tipo. Nunca prometa envio por DM, a não ser que a automação de DM exista e funcione.
  - `ponte`: liga o assunto ao produto ("O curso da sua área. Link na bio." e/ou "Comenta a sua dúvida"). Sem preço, sem "garanta já". Proporção: cerca de 1 ponte para 4 informativos.
- Limites (o validador confere): `titulo` até 8 palavras; `texto` até 30 palavras (34 é o teto); lista densa (F9) até 90 palavras por slide, em linhas "1. item".

## Gancho da capa (o que mais funcionou)

- Gancho negativo vence positivo: "O erro que estraga seu som" rende mais que "Dica para melhorar seu som".
- Fórmulas: condicional de dor ("Seu X tá Y? Resolva assim"), anti-gasto ("Não pague para aprender X"), ordem com culpa ("Pare de fazer X à mão"), "antes de" ("Antes de pedir mais verba, teste isto"), número grande ("31 coisas para conferir"), identidade ("Qual desses é você?"), "a última muda tudo".
- Capa visual com cena (personagem inusitado) rendeu cerca de 60 vezes mais curtidas que carrossel só de texto em fundo preto, no mesmo perfil. Não publique carrossel só de texto.
- Destaque: a parte do título entre asteriscos sai na cor de destaque: `"Pediram *mais volume*?"`.

## Formatos

| Código | Formato | CTA final |
|---|---|---|
| F1 | Cena + "resolva assim": capa com o problema, passos numerados | salve e envie para a equipe |
| F2 | "Qual desses é você?": um tipo por slide (nome engraçado + comportamento + "frase típica"), imagem por tipo | comenta o número, marca o amigo nº X |
| F3 | Erro → faça assim: "por que acontece", Erro 1..N com a correção, checklist | salve |
| F4 | Ranking / tier list, do pior ao melhor | discorda? comenta o seu ranking |
| F5 | Níveis 1 → N com os sinais de cada um | em qual você está? |
| F6 | Batalha: rounds por situação, placar, vencedor depende do uso | time A ou time B? |
| F7 | Antes × depois em pares de slides, humor + uma linha técnica do porquê | marca quem precisa ver |
| F8 | Orgulho da profissão: frases curtas de impacto | envie para alguém que você respeita |
| F9 | Lista densa: 20 a 40 itens em 3 ou 4 slides | salve para usar depois |
| F10 | Escala física inusitada: a informação vira régua, prédio, mochila, relógio, preço | salve |

## Imagens

As imagens da IA **não têm texto**: o texto entra na montagem (`carrossel.py gerar`), com fonte e acento certos.

- `IMG1` = capa, sempre. Personagem-arquétipo da cintura para cima, olhando para a câmera, numa situação improvável ligada ao tema. Terço de baixo escuro para o título.
- `IMG2` = fundo dos slides de conteúdo, sempre. Ambiente do tema, sem personagem em foco, escuro, com o alto da imagem calmo para o texto.
- `IMG3` a `IMG6` = só quando o formato pede imagem por item (F2, F7, às vezes F4/F8/F10). Máximo 6 por carrossel; média 3 a 4. O texto fica no alto: a cena vai na metade de baixo.
- `prompt` em inglês, só a cena (personagem, ação, cenário, expressão, enquadramento). O estilo e a composição entram sozinhos (`estilo_imagem` do config + `carrossel.py prompts`). Nas IMG2+ escreva "same palette as IMG1".
- Gráfico (curva, régua, placar, diagrama) não é imagem de IA no modo padrão: vire lista no `texto`, ou descreva em `grafico` e use o modo `--slide-inteiro` (a IA desenha o slide todo; confira o texto letra por letra).

## Formato do arquivo

```json
{
  "id": "001",
  "formato": "F1",
  "tipo": "info",
  "tom": "negativo",
  "titulo_capa": "Pediram “mais volume”? Antes de subir o master, confira isto",
  "imagens": [
    {"ref": "IMG1", "uso": "capa", "prompt": "A stern elderly judge in black robes ..."},
    {"ref": "IMG2", "uso": "fundo", "prompt": "Dim live venue seen from behind ..."}
  ],
  "slides": [
    {"n": 1, "imagem": "IMG1", "titulo": "Pediram *“mais volume”?*", "texto": "Antes de subir o master, confira isto"},
    {"n": 3, "imagem": "IMG2", "rotulo": "Passo 1", "titulo": "Pergunte: mais volume de quê?", "texto": "...", "grafico": null}
  ],
  "legenda": "3 a 6 linhas: repete a promessa da capa, diz o que tem no carrossel, última linha = pedido de ação.",
  "hashtags": ["#tag1", "#tag2", "#tag3", "#tag4", "#tag5"]
}
```

- `rotulo` (opcional): linha pequena em caixa alta acima do título ("PASSO 1", "ERRO 3", "TIPO 2").
- `texto`: `\n` quebra a linha (listas).
- `{perfil}` em qualquer texto vira o @ do config.
- 5 a 8 hashtags, sem marca. A legenda não repete o carrossel inteiro: entrega a promessa e pede uma ação.
- Sem emoji e sem setas (→) no texto dos slides: a fonte não tem e vira quadradinho. O validador recusa.
