---
name: organico-personagem
description: Use quando o usuário pedir conteúdo orgânico com personagem — história animada, série de Reels/TikTok em episódios em que o público vota A ou B nos comentários, personagem 2D, mascote, "historinha", desenho que ensina um conceito do nicho. Personagens 2D desenhados em código (sem IA de imagem paga), voz narrada Gemini, render HyperFrames. Dispare mesmo que a pessoa não diga "skill" nem "HyperFrames".
---

# Orgânico com personagem (séries de história em episódios)

## O que esta skill faz
Gera vídeos verticais (9:16, 50 a 90 s) com personagens 2D chapados desenhados em código, cenários, objetos que aparecem quando a narração diz a palavra, legenda grande sincronizada com a voz e cartões finais. É conteúdo orgânico em episódios: cada parte ensina um conceito dentro de uma crise e termina com um dilema; o público comenta A ou B e a mais votada vira a próxima parte. Fecha com o cartão A/B e o cartão "segue o perfil · parte N+1". Comentário e seguidor são o objetivo; não é anúncio.

Junta o conhecimento dos vídeos narrados (regras de voz, mixagem, conferência objetiva) com as séries de história (bíblia, elenco, `historia.py`, guia de episódio). O kit foi feito para o nicho de áudio ao vivo: os cenários e objetos atuais são palco, cabine, mesa, fader, equalizador. Outro nicho pede cenários e objetos novos no `historia.py` (ver "Ampliar o kit").

| Arquivo | O que tem |
|---|---|
| `kit/historia.py` | Desenha tudo em SVG. A lista de fundos, objetos, poses e caras fica no topo do arquivo |
| `kit/produzir.py` | Vídeo de ponta a ponta: voz → cenas → montagem → check → render → conferência → `post.txt` |
| `kit/voz/gen_gemini.py` | Voz Gemini TTS Puck: 1 pedido com todas as falas, recusa texto arriscado antes de gastar, confere cada fala no Whisper |
| `tools/` | `montar.py` (index.html + mixagem), `mixar.py`, `checar.py` (quadro parado, tela preta, volume, folhas de contato), `vv.js` (animações) |
| `referencias/BIBLIA-EXEMPLO.md` | Bíblia de 3 séries reais (mundo, personagens, ganchos por voto): o modelo para escrever a sua |
| `referencias/GUIA-EPISODIO.md` | Como escrever cada `episodio.json`: história, formato, regras da voz, visual |
| `referencias/ERROS-COMUNS.md`, `REGRAS-AGENTE.md` | Conhecimento dos vídeos narrados: erros de voz, roteiro e montagem que custaram retrabalho, e os defeitos que mais reprovaram |
| `exemplos/` | `elenco.json` (7 personagens) e 3 episódios piloto aprovados (`novato`, `preso`, `arena`) |
| `scripts/criar-projeto.sh` | Monta a pasta do projeto, instala ffmpeg/Whisper e baixa as 2 músicas padrão |

Caminho da skill: `K=~/.claude/skills/organico-personagem`.

## Passo 1: Conversa inicial (uma rodada só)
Pergunte numa chamada de AskUserQuestion, com o padrão como 1ª opção "(Recomendado)". Pule o que o pedido já respondeu.
| Campo | Padrão |
|---|---|
| nicho e tema | do pedido ou do projeto (produto, público, o conceito que o vídeo ensina) |
| perfil do cartão final | o @ e a descrição curta que aparecem no cartão "seguir" (ex.: `@seuperfil`, "Áudio ao vivo") |
| quantas séries | 1 piloto (EP. 1) por série; padrão 1 série |

Depois, no mesmo começo de conversa, resolva a chave do Gemini (passo 2). Não pergunte preço nem depoimento: o vídeo só usa fatos do material.

## Passo 2: Chave do Gemini (a voz)
Pule se `~/.config/organico-personagem/gemini.env` ou `~/.config/curso-mesa-de-som/gemini.env` existir, ou se houver variáveis `GEMINI*KEY*` no ambiente. Senão, guie o usuário em texto simples, um passo por vez:
1. "Abra https://aistudio.google.com/apikey e entre com uma conta Google. É grátis e não pede cartão."
2. "Clique em **Create API key** (Criar chave de API), aceite os termos se aparecerem e copie a chave. Ela começa com `AIza`."
3. "**Não cole a chave aqui no chat.** Abra o app Terminal do Mac, cole o comando abaixo, tecle Enter e, quando ele pedir, cole a chave e tecle Enter de novo. A chave não aparece na tela, é normal." Mande o comando num bloco de código:
   ```bash
   mkdir -p ~/.config/organico-personagem && printf 'Cole a chave do Gemini e tecle Enter: ' && read -rs k && printf 'GEMINI_API_KEY=%s\n' "$k" > ~/.config/organico-personagem/gemini.env && chmod 600 ~/.config/organico-personagem/gemini.env && echo && echo salvo
   ```
4. Quando ele disser que apareceu `salvo`, confira sem gastar a cota e sem mostrar a chave:
   ```bash
   ( set -a; . ~/.config/organico-personagem/gemini.env; curl -s -o /dev/null -w '%{http_code}\n' -H "x-goog-api-key: $GEMINI_API_KEY" https://generativelanguage.googleapis.com/v1beta/models )
   ```
   `200` é chave certa. `400` ou `403`: repita os passos 2 e 3.
5. Cota em uma linha: o plano grátis dá ~10 pedidos de voz por dia por chave, e cada vídeo gasta 1 pedido (mais 1 por correção). Mais chaves, cada uma em outra conta Google ou outro projeto, entram no mesmo arquivo como `GEMINI_API_KEY_2=...` (mesmo comando, trocando o nome e `>` por `>>`).
Nunca peça, mostre nem copie o valor da chave para o chat ou para arquivos do projeto.

## Passo 3: Criar o projeto
```bash
"$K/scripts/criar-projeto.sh" "<pasta do projeto>"      # P = caminho absoluto
```
Copia `kit/` e `tools/` para o projeto, põe o `elenco.json` de exemplo, baixa `musica/calma.m4a` e `musica/energica.m4a` (Mixkit, uso comercial sem atribuição: `musica/LICENCAS.md`) e instala ffmpeg, mlx-whisper e o modelo do Whisper. Exige Mac com chip Apple e Node.js. Música própria: ponha `musica/<nome>.m4a` e use `"musica": "<nome>"` no episódio.

## Passo 4: Bíblia e elenco
1. Escreva `$P/BIBLIA.md` no molde de `referencias/BIBLIA-EXEMPLO.md`:
   premissa em 2 linhas (quem é o herói, onde, o que está em jogo), 3 a 5 personagens com uma linha cada, e os ganchos dos próximos episódios com as duas saídas de cada voto. A escolha "errada" também vira episódio: mostra o que dá errado e por quê. O herói vive a mesma dor do público do perfil.
2. Monte o `$P/elenco.json` (pele, cabelo, roupa, acessórios por personagem; formato em `exemplos/elenco.json`, opções no topo de `kit/historia.py`).
3. Confira o desenho antes de escrever qualquer episódio (folha do elenco inteiro, sem voz, ~1 min):
   ```bash
   cd "$P" && python3 kit/historia.py --folha folha && cd folha && cp ../kit/hf-base/*.json . && python3 ../tools/montar.py . --musica nenhuma \
     && python3 -c "import sys; sys.path.insert(0, '../kit'); import produzir as p; print(p.run(p.hf('render', '.', '-q', 'draft', '--quiet', '-o', 'folha.mp4'), '.')[0])" \
     && ffmpeg -v error -y -i folha.mp4 -vf "fps=1/2,scale=270:-1,tile=4x2" -frames:v 1 folha.png
   ```
   Olhe `folha/folha.png` com Read. Ajuste cores e acessórios no `elenco.json` até cada personagem ficar reconhecível de longe.

## Passo 5: Escrever o vídeo
Cada vídeo é uma pasta `$P/<serie>/epNN/` com um `episodio.json`. Siga **`referencias/GUIA-EPISODIO.md` à risca** (formato, 8 a 11 cenas, 150 a 230 palavras de narração, `destaque`, `quando`, regras da voz, posições) e copie a estrutura de um episódio de `exemplos/`.
- Abre com o voto do público (do EP. 2 em diante, campo `votos`), ensina um conceito real dentro da cena, termina com `{"tipo": "escolha"}` e `{"tipo": "segue", "proximo": "PARTE N+1 EM BREVE", "perfil": "@...", "perfil_desc": "..."}`.
- Proibido no vídeo: preço, cupom, link, marca ou modelo de produto de terceiros. Leia `referencias/REGRAS-AGENTE.md` antes do primeiro episódio.
- Regras de voz que mais erram: a letra B sozinha se escreve "bê" na fala (a legenda mostra B); "Tá", nunca "Está"; imperativo coloquial ("Aperta"); número por extenso; termo em português, nunca "mute", "gain", "send". Tabela completa em `referencias/ERROS-COMUNS.md`, seção 1.

## Passo 6: Produzir
```bash
cd "$P" && python3 kit/produzir.py <serie>/ep01 [<serie>/ep02 ...]
```
Rode em segundo plano: a voz leva ~1 min e o render ~5 a 11 min por vídeo. Refaz só o que falta. Saída: `renders/<serie>-<ep>.mp4`, `post.txt` (legenda pronta), `rev/folha-*.png` e `checar.log`.
- `AVISO voz ... a conferir`: ouça o trecho listado em `voz/geracao.log`. Para refazer só uma fala, edite o texto dela no `episodio.json` e rode de novo (1 pedido). Na 2ª falha da mesma frase, reescreva a frase.
- `FALHA voz (cota do Gemini)`: rode o mesmo comando no dia seguinte ou acrescente outra chave.
- `BROWSER_ENVIRONMENT_BLOCKED`: o render abre um navegador sem janela; rode o comando no app Terminal.

## Passo 7: Conferir e entregar
1. Olhe as folhas `rev/folha-*.png` com Read: personagem cortado, legenda cobrindo rosto ou cartão (mude `legenda_y`), objeto antes da hora, cena vazia. Corrija no `episodio.json` e rode o produzir de novo.
2. Responda com uma tabela (vídeo | duração | o que ensina), os caminhos dos MP4 e do `post.txt` e o que depende do usuário.
3. **Nunca publique sem o usuário pedir.**
4. **Série, próximo episódio:** 24 a 48 h depois do post, conte os votos nos comentários (1 voto por pessoa, o perfil não conta) e escreva o próximo `episodio.json` com `"votos": {"titulo": "VOCÊS VOTARAM", "resultado": "7 EM 10: <opção vencedora>"}` seguindo o caminho vencedor da bíblia. Sem votos ou empate: escolha o caminho que ensina mais e diga na fala ("Ninguém votou, então o Léo decidiu sozinho").

## Ampliar o kit (outro nicho)
Cenário, objeto, pose ou cara novos entram em `kit/historia.py` do projeto: acrescente a função no mesmo estilo (formas simples, cores chapadas, contorno escuro), atualize a lista no topo do arquivo e confira com `--folha`. Personagem novo é uma linha no `elenco.json`. Animação nova: use os ajudantes `V.*` de `tools/vv.js`.

## Erros comuns
| Erro | Correção |
|---|---|
| Voz lê "B" solto errado | Escreva "bê" na fala; o cartão e a legenda mostram B |
| Palavra curta no fim da fala vai parar na cena seguinte | Termine a fala com palavra comum, ou use `legenda_troca` (fala "Clipe", tela "Clip") |
| Objeto aparece antes da hora | Todo prop sem `quando` aparece no início da cena; ponha `quando` com uma palavra que existe na fala |
| GSAP não anima um grupo SVG | Não anime um `<g>` que já tem `transform`: embrulhe num `<g>` de fora |
| Legenda em cima do rosto ou do cartão | `legenda_y` na cena (420 para o alto, 1250 abaixo dos cartões) |
| Marca ou modelo de produto de terceiro no orgânico | Conteúdo orgânico não cita marca nem modelo; cenário nunca preso a um só contexto |
| Gastar a cota com texto arriscado | O gerador recusa antes do pedido; corrija o texto apontado em vez de forçar |
