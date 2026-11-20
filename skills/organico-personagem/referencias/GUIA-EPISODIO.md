# Como escrever o próximo episódio (para o Claude do servidor)

Você recebe `<serie>/epNN/PEDIDO.md` com o resultado dos votos do episódio anterior. Escreva
`<serie>/epNN/episodio.json` e rode `python3 kit/automatico.py validar <serie>/epNN` até sair `OK`.
Não rode produzir nem publique: o automático faz isso depois. Se o PEDIDO.md disser que a versão anterior foi
reprovada na revisão, corrija o motivo.

Leia antes: `BIBLIA.md` (mundo, personagens, ganchos), `elenco.json`, todos os `episodio.json` anteriores da série
(continuidade, tom, tamanho) e o topo de `kit/historia.py` (fundos, objetos, poses e caras que existem).

## A história

- Continue de onde o anterior parou, seguindo o caminho que **venceu a votação** (`PEDIDO.md`).
- Se ninguém votou ou deu empate, escolha o caminho que ensina mais e diga na fala, ex.: "Ninguém votou, então o
  Léo decidiu sozinho."
- Escolha errada também vira episódio: mostre o que dá errado e por quê (é aí que se aprende).
- Cada episódio ensina **um** conceito de áudio de verdade (correto tecnicamente, sem exagero), dentro da cena.
- Termine com um novo dilema A ou B, as duas opções plausíveis, curtas (até 6 palavras no cartão).
- Arena do Som: o duelo é o vencedor da votação ("A" ou "B" do cartão da luta anterior). Dois lutadores com
  filosofias opostas (novos podem entrar, ver BIBLIA), placar "vence X de 10" e a próxima votação de duelo.
- Proibido: nome de marca ou modelo de mesa, cenário só de igreja (igreja pode ser um exemplo entre outros),
  preço, cupom, link, @ de terceiros.

## Formato (igual aos `episodio.json` anteriores)

- `serie`, `ep` ("EP. N" ou "LUTA N"), `musica` (mesma da série), `legenda` (título "Parte N: ...", resumo de 1 linha,
  a pergunta, as opções "A) ..." e "B) ...", "Comenta A ou B 👇"), `hashtags` (5).
- `votos`: `{"titulo": "VOCÊS VOTARAM", "resultado": "7 EM 10: CORTA A FREQUÊNCIA"}` — use o "em_10" e a opção
  vencedora do PEDIDO.md. Sem votos: não ponha o campo `votos`.
- `cenas`: 8 a 11. As duas últimas são `{"tipo": "escolha", ...}` e `{"tipo": "segue", "proximo": "PARTE N+1 EM BREVE"}`.
- Narração somada: 150 a 230 palavras (50 a 80 s). Frases curtas, registro de Reels ("tá", "pra", "aperta").
- `destaque`: 1 ou 2 palavras de cada fala, escritas como aparecem na fala (com a pontuação colada, ex.: "MASTER,").
- `quando` / `quando2` / `quando_b`: uma palavra que existe na fala daquela cena.

## Regras da voz (o validador confere)

- A letra B sozinha se escreve "bê" na fala ("Comenta A ou bê"); o cartão e a legenda mostram B.
- Nenhuma outra letra solta, nada de "Está" (use "Tá"), imperativo coloquial ("Aperta", não "Aperte"),
  termos em português (nada de "main", "send", "bus", "mute", "gain", "patch").
- Número por extenso na fala ("vinte minutos").
- Palavra que a voz pode cortar para a cena seguinte no fim de uma fala (nome curto, sigla): prefira terminar a
  fala com uma palavra comum, ou use `legenda_troca` como no Preso na Mesa ("Clipe" falado, "Clip" na tela).

## Visual

- Use só fundos, objetos (`props`), poses e caras listados no topo de `kit/historia.py` e personagens do `elenco.json`.
- Personagem novo: acrescente no `elenco.json` no mesmo formato (pele, cabelo, roupa, extras).
- Posições de referência: personagem em pé `y` 1640-1800, `s` 0.9-1.3; atrás da mesa (cabine) `y` 1800; dentro
  da mesa (Preso na Mesa) `s` 0.6-0.75. Legenda padrão em `y` 1380; mude `legenda_y` se ela cobrir o rosto ou um
  cartão (ex.: 420 para o alto, 1250 abaixo dos cartões de opções).
- Varie o cenário entre as cenas. Mantenha a câmera `push` na maioria, `tremer:<palavra>` no susto, `zoom` para
  reação, `fixa` em diagrama e cartões.
