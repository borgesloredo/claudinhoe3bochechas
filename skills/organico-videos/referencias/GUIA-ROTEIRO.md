# Guia de roteiro dos vídeos orgânicos

Regras tiradas de 200 vídeos orgânicos publicados (Reels, TikTok, Kwai, Shorts) e das referências que funcionaram no nicho. Os exemplos são de áudio ao vivo; troque pelo seu nicho.

## O padrão que funciona
1. **Gancho em até 3 s** que quebra um mito ou nomeia a dor ("Fader no talo e a voz baixa?"). Varie a abertura: pergunta, gancho negativo ("Pare de..."), gancho duplo (texto na tela diferente da fala), número, cena de bastidor. Ver `INSIGHTS-INSTAGRAM.md`.
2. **A causa verdadeira** com um diagrama limpo no meio do quadro (a peça do kit que mostra a ideia).
3. **O conserto**: o gesto real, o valor quando ele é regra geral da área.
4. **A regra numa frase** ("Ganho prepara o sinal. Fader faz a mistura.").
5. **Ponte** para o produto, opcional, na cena antes do CTA ("No curso da sua mesa isso tá tecla por tecla"). Vídeo só informativo não tem ponte.
6. **CTA orgânico** na última cena.

**Um conceito por vídeo.** Sempre ancore numa dor concreta de quem é o seu público. O mito sem dor e sem contexto não engaja.

## Conteúdo genérico (alcance maior)
- Ensine o que vale em qualquer marca e em qualquer cenário do público. Nada de marca ou modelo de produto de terceiros: nem na fala, nem na tela, nem na legenda, nem nas hashtags. Restringir é perder público.
- Cenário específico (ex.: igreja, casamento) no máximo 1 vez por vídeo, como um exemplo entre outros; em ~70% dos roteiros, nenhum.
- Afirmação técnica só se estiver no seu material (confira antes de escrever). Valor que só vale num produto não entra.
- Quem quer o produto específico se qualifica sozinho pelo CTA: "Comenta o modelo da sua mesa que eu te mando o curso dela".

## Regras de roteiro
- **Narrado:** 30 a 60 s (alvo 40 a 50 s), **até 120 palavras de fala**, ~3 palavras/s, frases curtas. Cenas de 1,5 a 4 s.
- **Registro falado da voz:** "Tá" (não "Está"); imperativo coloquial ("Aperta", "Gira", "Sobe"); nada de letra solta ("o botão de informação", não "o i"); termo em português na fala ("mix principal", não "main"; "envio", não "send"; "mudo", não "mute"). Na tela fica a sigla (MAIN, GAIN, MUTE). Número por extenso na fala. Tabela completa em `ERROS-COMUNS.md`, seção 1.
- **Tela:** até 9 palavras por cena (título + pílula + rótulos). O vídeo precisa fazer sentido no mudo.
- "Não é X, é Y" no máximo 1 vez por roteiro. Palavra de conteúdo no máximo 2 vezes.
- `visual`: diga o que ocupa o meio do quadro em cada cena, usando as peças do kit pelo nome (CANAL, KNOB, FADER, MEDIDOR, TELA, CÍRCULOS, QUIZ, CHECKLIST, CAMINHO, PÍLULA, SETA-RÓTULO, PRODUTO). Nunca cena vazia.
- **Proibido:** "oficial", URL, @ na fala, telefone, preço, cupom, desconto, prazo, garantia, depoimento, número de alunos, promessa de resultado financeiro, falar mal de concorrente pelo nome, estatística inventada.
- Público sensível (fé, profissão): sem ironia; o tom é de colega que faz junto.

## CTA (última cena)
Varie dentro do lote:
| Tipo | Quanto | Exemplo |
|---|---|---|
| Comenta | ~40% | metade "Comenta o modelo da sua mesa que eu te mando o curso dela", metade "Comenta PALAVRA que eu te mando…" (palavra do tema, MAIÚSCULA, sem repetir a mesma em mais de 3 vídeos) |
| Salva | ~30% | "Salva pra rever antes da próxima passagem de som" |
| Marca | ~20% | "Marca quem opera o som com você" |
| Segue | ~10% | "Segue pra próxima dica" |
"Comenta PALAVRA" só funciona com resposta automática no direct (ManyChat ou similar) já montada antes de postar. O `texto_tela` da última cena leva o CTA + o selo (`marca.json`). Gancho que precisa de pergunta antes do CTA: a voz às vezes engole a 1ª palavra da fala ("Comenta"); ponha uma pergunta antes ("Quer o resumo? Comenta...").

## Formato (um arquivo por vídeo: `json/NNN-slug.json`)
```json
{"id": "001-fader-no-talo-ganho", "nome": "Fader no talo e a voz baixa: é o ganho",
 "dor": [7], "abordagem": "analogia", "cta_tipo": "comenta", "musica": "calma",
 "legenda_post": "texto do post (até 600 caracteres, sem @ nem link; termina com a pergunta ou o CTA; 3 a 5 hashtags)",
 "cenas": [{"t_ini": 0, "t_fim": 3.6, "texto_tela": "Fader no talo e a voz baixa?", "fala": "Fader lá no alto e a voz ainda baixa?",
            "visual": "CANAL no centro: FADER no topo e MEDIDOR quase apagado", "motion": "fader sobe até o topo; medidor mal acende"}]}
```
- Abordagens (varie): `mito`, `erro-comum`, `antes-depois`, `analogia`, `passo-a-passo`, `pergunta-quiz`, `bastidor`, `checklist`.
- `musica` é opcional: `calma`, `energica` ou o nome de um arquivo em `musica/`.
- Exemplos completos em `exemplos/` (um vídeo que cita o produto e um só informativo).

## Conferir cada roteiro
```bash
python3 tools/lint-roteiro.py json/NNN-slug.json --narrado --cta "comenta|salva|marca|segue"
```
Repita até zero FALHA. AVISO de pronúncia: reescreva a fala.
