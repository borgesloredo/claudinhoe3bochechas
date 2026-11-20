# Séries de história (Reels em episódios)

Formato criado em 11/2026, a partir de 4 Reels de referência (rmhkaiser "Otávio" parte 1,
historiasdodespertar "Faxineiro de Masmorra" parte 4, o.siul_ "acordasse sozinho no mundo", chefaofinal.geek
"Jump Arena luta 6").

## O que faz o formato funcionar

1. **Série com número**: selo fixo no topo ("O NOVATO DA MESA · EP. 1") e "Parte N" na legenda.
2. **Abre com o voto do público** (do EP. 2 em diante): "VOCÊS VOTARAM · 7 EM 10: CORTA A FREQUÊNCIA".
   Quem comentou volta para ver se ganhou.
3. **Fecha com uma escolha A ou B**: "O que o Léo faz? Comenta A ou B." A mais votada vira o próximo episódio.
4. **Segue pra ver a parte N+1**.
5. **Ensina sem parecer aula**: o conceito de áudio é a arma da cena (microfonia, ganho, mascaramento).
   A escolha "errada" também vira episódio: mostra o que dá errado e por quê.
6. Visual 2D chapado (personagens de formas simples), legenda grande no centro com uma palavra em amarelo,
   narração em 3ª pessoa (Gemini Puck), 50 a 90 s.

Regras da casa que continuam valendo (conteúdo orgânico): nenhuma marca ou modelo de mesa, cenário nunca preso à
igreja (o espaço do Novato recebe show, culto, casamento e formatura), CTA de comentário.

## Série 1 · O NOVATO DA MESA

O Léo, 19 anos, ajudante de som num espaço de eventos (o Galpão). O técnico titular, Zé Cabo, vive atrasado,
e o Léo cai sozinho na mesa nas piores horas. Cada episódio é uma crise real de evento; o público decide o que
ele faz.

| Personagem | Quem é |
|---|---|
| Léo | Novato, boné, fone no pescoço. Esperto, mas nunca mixou. |
| Zé Cabo | Técnico veterano, barba grisalha, colete. Aparece por áudio no celular, sempre preso em algum lugar. |
| Duda | Vocalista exigente. Sempre quer mais retorno. |
| Seu Ivo | Dono do Galpão. Olha para a cabine quando algo dá errado. |

Ganchos para os próximos episódios (o voto escolhe o caminho):
- EP. 1 microfonia no retorno. A = abaixa o master (apito some, mas ninguém se ouve mais: lição "master não é
  conserto") · B = corta a frequência que apita (lição: achar a frequência, corte estreito, depois posição do
  monitor atrás do microfone).
- Depois: ruído/zumbido no violão (aterramento, DI), pastor/noivo/formando com microfone de lapela sumindo,
  bateria engolindo tudo, banda pedindo "mais de tudo" no retorno, a energia caindo no meio do evento.

## Série 2 · PRESO NA MESA

O Nico dorme em cima da mesa depois de um evento e acorda minúsculo dentro dela. O sinal é um rio de luz; ele
precisa chegar ao MASTER (a saída) antes que alguém desligue a mesa. Cada fase é um bloco do caminho do sinal.

| Fase | Bloco | Vilão / obstáculo |
|---|---|---|
| 1 | Ganho (pré-amplificador) | a comporta e o monstro Clip (distorção) |
| 2 | Corte de graves | o Ronco, um bicho grave que se arrasta |
| 3 | Gate | o Porteiro, que só abre a porta para o som forte |
| 4 | Compressor | o Guarda que aperta quem grita |
| 5 | Equalizador | o Vale das Montanhas (frequências) |
| 6 | Auxiliares | túneis para os retornos |
| 7 | Fader e master | a saída |

EP. 1: A = baixa o ganho e acalma o Clip (certo) · B = passa correndo porque "o fader resolve depois" (errado:
a distorção nasce antes do fader e vai junto até o fim; o EP. 2 mostra o Clip seguindo o Nico).

## Série 3 · ARENA DO SOM

Duelo de técnicos com filosofias diferentes contra o mesmo problema. O narrador mostra os dois golpes, explica
o conceito e dá um placar ("vence 7 de 10"). O público pede o próximo duelo (A ou B).

| Lutador | Canto | Filosofia |
|---|---|---|
| Tonhão do Fader | vermelho | "Não tá ouvindo? Sobe." |
| Bia da EQ | azul | "Não sobe nada: tira o que tá na frente." |

Lutadores que podem entrar: o Medidor (só mixa olhando número), a Velha Guarda (mesa analógica), o Presetzeiro
(cena salva para tudo), a Ouvido Absoluto (só mixa de ouvido).

LUTA 1: voz sumindo na banda (mascaramento). Próximo duelo em votação: A = compressor contra fader na mão ·
B = mixar no fone contra mixar na caixa.

## Ciclo de cada episódio

1. Escrever `episodio.json` (o voto do anterior entra no campo `votos`).
2. `python3 kit/produzir.py <serie>/epNN` → voz, cenas, render, conferência. Sai `renders/<serie>-epNN.mp4` +
   `post.txt` (legenda pronta).
3. O dono do perfil posta (nunca postar sem ele pedir).
4. 24 a 48 h depois: `python3 kit/votos.py <link do Reels>` conta os votos A/B nos comentários (1 voto por
   pessoa, o perfil não conta) e grava `votos.json` no episódio.
5. Volta ao passo 1 com o resultado.
