# TTS da V2: áudio ▶ dos slides

Gera os áudios do botão ▶ com voz masculina em **português do Brasil**. Roda no Mac (Apple M4) e não precisa de internet depois do download.

> **Troca de voz (21/10).** A voz anterior (Qwen3-TTS clonando `voz/referencia.wav`) saía com sotaque de **Portugal**. O teste objetivo confirmou: o classificador de variedade deu `p(pt_br) = 0,00`. Os áudios antigos estão em `backups/audio-ptPT-descartado/` e o gerador antigo em `backups/tts-qwen-ptPT/`. Evidência completa em [`teste-sotaque.md`](teste-sotaque.md).

## Escolha

| Item | Valor |
|---|---|
| Modelo | **Kokoro-82M** (bf16, conversão MLX `mlx-community/Kokoro-82M-bf16`) |
| Voz | **`pm_alex`**, a voz masculina pt-BR que vem no próprio modelo. Não há clonagem e ela não é a voz de uma pessoa identificada |
| Pronúncia | Fonemas do espeak-ng **pt-br** (via misaki), mais um dicionário de termos técnicos em `gen.py` (`PRON`) |
| Motor | **mlx-audio 0.6.1** (MLX, Apple Silicon) em `.venv/` (Python 3.12, uv) |
| Tom | Masculino, F0 mediano de ~133 Hz (a faixa de homem adulto vai de 85 a 155 Hz) |
| Velocidade | `speed=0.9` do Kokoro dá ~165 palavras/min, um ritmo de aula. `TTS_TEMPO=0.93` deixa mais calmo e `1.05` mais rápido. Agora quem muda a velocidade é o próprio Kokoro, não mais o `atempo` do ffmpeg |
| Saída | `.m4a` com AAC-LC mono 24 kHz a 48 kbps e faststart, normalizado com loudnorm para −16 LUFS (pico −1,5 dBTP). Medido: −16,6 LUFS nos 3 roteiros |
| Tempo | ~10 s para um roteiro de 2 min, incluindo ~3 s para carregar o modelo. Os 144 roteiros levam ~25 min |
| Repetição | A semente vem do texto: gerar de novo o mesmo roteiro dá o mesmo áudio (as diferenças são só de arredondamento, inaudíveis) |

### Por que esta voz (resumo de `teste-sotaque.md`)
Texto de teste com marcadores de pt-BR (noite, tarde, diferente, ativo, verdade, estúdio, mesmo, pois, vamos, "a gente está ajustando"...), medido de forma automática:

| | Voz antiga (Qwen clone) | **Kokoro `pm_alex` (escolhida)** |
|---|---|---|
| Classificador pt_br × pt_pt (`lgris/portuguese-accent-classifier`) | 0,00 | **1,00** (e 62 de 62 janelas nos 3 roteiros reais) |
| ti/te como [tʃ] ("noitchi") | 0 de 4 | **3 de 4** |
| "s" de fim de sílaba como [s] (e não [ʃ]) | 2 de 11 | **11 de 11** |
| Whisper | WER 7%, "António" | **WER 0%** |

Também foram testados: Qwen3-TTS Base clonando referência brasileira (sintética, do Kokoro ou do VoiceDesign), que **sempre voltou ao sotaque de Portugal**; Qwen3-TTS VoiceDesign com descrição forte de sotaque brasileiro, em que o sotaque e o tom mudam a cada semente e a voz não se mantém entre blocos; e Chatterbox Multilingual clonando o `pm_alex`, que tem o sotaque certo, mas errou 4% das palavras nos roteiros reais, contra 0 a 0,7% do Kokoro, e é ~20× mais lento. O Kokoro `pm_santa` também passa, com menos folga, e é o reserva: troque `VOZ` em `gen.py`.

### Licenças (tudo permite uso comercial e roda offline)
- Kokoro-82M (pesos e vozes, incluindo `pm_alex`): **Apache-2.0**. https://huggingface.co/hexgrad/Kokoro-82M · conversão MLX: https://huggingface.co/mlx-community/Kokoro-82M-bf16
- misaki (G2P do Kokoro): **Apache-2.0**. https://github.com/hexgrad/misaki
- mlx-audio: **MIT**. https://github.com/Blaizzy/mlx-audio · MLX: **MIT**. https://github.com/ml-explore/mlx
- espeak-ng (via `espeakng-loader`): **GPL-3.0**. https://github.com/espeak-ng/espeak-ng. É usado só como ferramenta local que converte texto em fonemas. O curso distribui o áudio, não o programa, e a GPL não se aplica ao som gerado. É o mesmo caso do ffmpeg.
- Só na verificação (nada disso entra no áudio): wav2vec2-xlsr-53-espeak-cv-ft, **Apache-2.0** (https://huggingface.co/facebook/wav2vec2-xlsr-53-espeak-cv-ft); portuguese-accent-classifier, **Apache-2.0** (https://huggingface.co/lgris/portuguese-accent-classifier); Whisper large-v3-turbo, **MIT**.
- Descartados pela licença ou por serem serviço online: XTTS-v2 (CPML), F5-TTS pt-BR, MMS-TTS e Voxtral (NC), Fish Speech, vozes do macOS e Edge-TTS. As vozes do macOS e o Piper `pt_PT-tugão` aparecem em `sotaque/calib/` **só como régua de calibração** do teste e não podem ir para o curso.

**Ninguém ouviu as amostras.** A escolha se baseou em medições. Antes de gerar os 144 áudios, ouça `samples-br/capa.m4a`, `samples-br/s12-1-1.m4a`, `samples-br/s2-1-1.m4a` e `samples-br/teste-sotaque.m4a`.

## Uso

```bash
tools/v2/tts/gen.sh roteiro.txt saida.m4a              # um arquivo
tools/v2/tts/gen.sh script/ ../../08-slides-v2/audio/  # pasta inteira; pula .m4a que estão em dia (retomável)
tools/v2/tts/gen.sh --teste                            # autoteste (divisão em blocos e dicionário de pronúncia)
TTS_TEMPO=0.93 tools/v2/tts/gen.sh roteiro.txt saida.m4a   # mais calmo
```

Funciona offline: `HF_HUB_OFFLINE=1` é o padrão no `gen.sh`, e os modelos ficam em `hf/`.

Como o `gen.py` funciona:
1. Divide o roteiro em blocos de até 260 caracteres, terminando sempre no fim de uma frase e sem atravessar parágrafos (linha em branco).
2. Aplica o dicionário `PRON` só no texto que vai para o modelo. O roteiro continua com a grafia normal.
3. Gera cada bloco com o Kokoro, usando uma semente tirada do texto. Se a duração sair fora de 0,55× a 1,8× do esperado, o que indica um corte, aparece `ATENCAO:` no stderr. Outra semente não muda a duração, então não adianta tentar de novo: reescreva a frase.
4. Junta os blocos com pausas: 0,25 s entre blocos do mesmo parágrafo e 0,6 s entre parágrafos.
5. Aplica loudnorm e grava o AAC `.m4a`. O arquivo final só aparece quando o ffmpeg termina, porque antes ele se chama `.parcial.m4a`.

**Conferência depois de gerar** (recomendada para um lote novo):
```bash
cd tools/v2/tts
HF_HOME=$PWD/hf HF_HUB_OFFLINE=1 .venv/bin/python sotaque/confere.py ../script/x.txt saida/x.m4a   # erros do Whisper + p(pt_br)
```
Essa conferência ignora siglas e números soletrados que o Whisper reescreve com algarismos. Em trechos de silêncio no fim, o Whisper às vezes inventa um "Obrigado". Isso é alucinação dele, não erro do áudio.

## Guia de escrita do roteiro (testado com a voz nova)

Cada grafia foi gerada com a voz final numa frase-moldura e transcrita pelo Whisper (`sotaque/guia/termos*.tsv` e `resultado*.json`, 3 rodadas, 164 testes). Os termos que saíam errados viraram regras automáticas em `PRON` (gen.py). **O roteirista escreve a grafia normal** e o gerador troca sozinho.

**Regras gerais (iguais às de antes)**
- Texto corrido, como fala. Nada de markdown, listas com marcadores, parênteses, barras, setas, emoji ou URL.
- Frases curtas, de no máximo 25 a 30 palavras. Separe as ideias com ponto e use linha em branco entre parágrafos, porque ela vira pausa maior.
- Itens de lista ficam separados por vírgula, na mesma frase.
- Escreva como se fala no Brasil: "você", "a gente", "equipe", gerúndio ("estamos ajustando", não "a ajustar").
- Números e unidades por extenso: `menos dezoito dê-bê-éfe-ésse`, `quarenta e oito volts`, `dez milissegundos`, `seis decibéis`, `três quilo-hertz`, `dois para um`.
- Siglas em maiúsculas feitas só de letras romanas (I, V, X, L, C, D, M) viram número no Kokoro: na PM5D, `MIX` saiu "mil e nove" e `MC` saiu "mil e cem". O `PRON` já troca as duas; sigla nova desse tipo precisa de regra antes de gerar.

**O que o gerador troca sozinho** (lista em `PRON`). Sem a troca, o Kokoro lê o termo com regras do português e sai, por exemplo, "gátchi" ou "dka":

| No roteiro | O modelo recebe | Sem a troca |
|---|---|---|
| fader, faders, pré-fader | fêider, fêiders | "fadér" |
| gate | guêit | Whisper ouviu "Get" |
| reverb, delay, insert | rivérbi, dilêi, insérti | "hevérb", "delái" |
| threshold, ratio, release, gain | tréshould, rêiciou, rilís, guêin | "release" saiu "Heliase" |
| feedback, playback, snapshot, preset, setup, master | fídibéque, plêibéque, isnépshót, prisét, setâp, mâster | |
| presets | prisséts | saía "presentes" |
| safe, Safe | sêif | saía "sáfi"/"SAF" |
| phantom power, Wi-Fi | fântom páuer, uai-fai | |
| Main, Main LR | Mêin, Mêin éle érre | "Main" saiu "marim" e "Main LR" saiu "Mainelizeje" |
| Select, Channel, Compact, Behringer | silécti, Tchénel, Cômpact, Bêringuer | "Select" saiu "Selection" |
| MIDI, AES, RTA, DCA, DCAs | mídi, á é ésse, érre tê á, dê cê á, dê cê ás | "midir", "I.S.", "ERETA", "dka" |
| xis Air, X AIR, xis ér | xis éir | "xis Air" é lido "a-ír" e "xis ér" vira "XR" |
| M AIR, ême ér | ême Air | "ême ér" vira "MR" |
| Hi-Z | rái zí | saía "IZ" (H mudo) |

**Funcionam como estão** (não precisam de troca): USB, XLR, TRS, RCA, HPF, LUFS, PA, P16, `pê dezesseis`, `xis érre dezoito`, `xis trinta e dois`, `ême trinta e dois`, `dê-bê-éfe-ésse`, `Mêin éle érre`, solo, show, pan, mono, tablet, patch, firmware, Ultranet, Producer, Midas, Mono Center, Rack (no contexto, "na versão Rack").
- `attack` sai "ataque", que é o nome em português do parâmetro. Se quiser os dois, escreva "o ataque, o attack".
- `Sends` sai "Sans"/"Sensor" e `Room` sai "Hôm": escreva `Séndis` (`Séndis ón Faders`) e `Contról Rúm`. Na primeira vez, diga o que é: "o modo Séndis ón Faders, que põe os envios nos faders".
- Siglas soletradas com hífen pioram (`pê-éfe-éle`). Use maiúsculas ou letras separadas por espaço. Exceções conferidas no Whisper: `dê-bê-éfe-ésse`, `é-i-ene` (EIN) e `á-éfe-éle` (AFL, que em maiúsculas saía "FL").
- Letra soletrada sozinha entre vírgulas: escreva `éh`. Com `ê` sai "e circunflexo" e com `é` sai "é agudo" (o eSpeak lê o nome do acento de letra acentuada solta). Sem vírgula (`tê é quê`) a letra some na emenda (Whisper: "TQ"). Ex.: TEQ = `tê, éh, quê`. Conferido no fonema do eSpeak: `tê, é, quê` vira `tˈe, ˌɛaɡˈudʊ, kˈe` ("é agudo"), `tê, éh, quê` vira `tˈe, ˈɛ, kˈe` (certo) e `tê-é-quê` vira `tˈeɛkˈe` (emenda). Se mesmo com `éh` o Whisper ouvir "I" (s10-1-4: "No T, I que"), o problema é a sigla logo depois de uma palavra curta como "No": ponha uma palavra antes, sem mudar o sentido (`No modo tê, éh, quê, ...`); saiu "No modo T e Q".
- **Grafia de pronúncia direto no roteiro** (não estão em `PRON`; escreva assim): in-ear = `ín-íer` (saía "in-ár"/"INR"), in-ear monitor = `ín-íer mónitor`, Routing = `Ráutin` (saía "Houching"/"HOTING"), mix bus = `mix bás` (saía "Mix Boost"; agora o Whisper escreve "mixbass", que é o som certo em boca brasileira), boxy = `bóksi` (o Whisper escreve "boxe", que em português se fala igual: diga "que em inglês se chama bóksi" para o leigo não pensar no esporte). Routing = `Ráutin` sai "Houtin": o R inicial brasileiro soa como H, é como se fala aqui e não há grafia melhor. MIDI no fim da frase, logo depois de "áudio e", sai "Image"/"MADI"/"MAD" (MADI é outro protocolo, o leigo aprende o termo errado). Não resolveram: `áudio e de mídi` (s11-2-5 ainda sai "MADI"), `áudio e também o mídi` ("MAD") e `áudio e também o sinal mídi` ("MADI"). Resolve: tirar o mídi do fim da frase e da emenda com "áudio", trocando a ordem: `O USB leva o mídi e o áudio.` (quiz-3, conferido). "o MIDI, a rede" saía "o MyD": `a porta mídi, a rede` sai "a porta MIDI" (s2-1-3, conferido). Monitor Source = `Mônitor Sórci` (o eSpeak lia "Source" como "sôu-re-sê").
- **Janela de sotaque baixa sem saber onde**: corte o áudio em trechos de 4 s alinhados (`ffmpeg -ss 0,4,8... -t 4`) numa pasta temporária e passe os trechos ao `qa_batch.sh` (id com caminho relativo a `08-slides-v2/audio/`, ex.: `../../../../../private/tmp/.../w/w21`). Cada trecho é uma janela: o relatório mostra qual cai e o `whisper/` mostra o texto. Em s11-2-5 a janela ruim era só português ("e ele passa a alimentar uma caixa ou um fone. O custo é"); reescrever a frase com o mesmo sentido resolve.
- **Mais grafias direto no roteiro** (rodada de QA dos capítulos 0 a 4): mute = `miúte` (saía "múti"/"Multi"), Mute at Power On = `Miúte at Power On`, Safe Main Levels = `Sêif Main Lévels`, Safe Shutdown = `Sêif Shátdaun`, quiz/quizzes = `cuíz`/`cuízes` (saía "kis"/"keys"/"cases"), Hi-Z = `Rái Zí` (saía "IZ"), DI = `dê i` (saía "501": o espeak lê DI como número romano), Scenes Undo = `Síns, Andú`, com vírgula (sem vírgula, `Síns Andú` saía "cinza undo", que o leigo entende como a cor; `Síns Ându` saía "cinzando"; `Síns, Ându` saía "Sims, ando"), Factory Reset = `Fáctori Reset` (saía "Factor e Reset"), View = `Viú` (saía "vieu"), Devices = `Diváicis` (saía "de vices"), Control Room = `Contról Rúm` (saía "Ctrl Home"), o verbo mixa = `mícsa`, de preferência com objeto, como `mícsa o som` (saía "micha"/"mexa"), Client = `Cláient` (saía "cliente"), Bus = `Bâss` (saía "Bulls"; com `Bâs`, "Base"), SSID = `ésse, ésse, i, dê` (saía "SID"/"SSD"), Library = `Láibrari` (saía "Librarie"). **Nunca escreva `í` sozinho como letra**: o espeak lê "i agudo" (`dê í` saiu "de agudo"); use `i` sem acento. **Sotaque**: uma janela de 4 s com frase curta e repetitiva ("Na opção A, um para um. A entrada um vai no canal um") deu p(pt_br) 0,00 duas vezes, mesmo sem inglês; quebre a repetição reescrevendo a frase com o mesmo sentido.
- **Vírgula separa termo de duas palavras em inglês**: quando o espeak junta duas palavras inglesas numa só, ou a primeira vira palavra portuguesa (Scenes Undo virou "cinza undo"), ponha uma vírgula entre elas no roteiro (`Síns, Andú`). A pausa curta separa as palavras sem mudar o sentido.
- **Palavra curta engolida entre preposição e número**: `em dois fios de um jeito` saiu "em de um jeito" (o "dois fios" sumiu). `por dois fios, de um jeito` sai certo (s2-1-1, conferido): troque a preposição e ponha vírgula depois do trecho que não pode sumir. "mais retornos" saía "mais contornos": `mais saídas de retorno` sai certo.
- **Mais grafias no roteiro (caps. 18 a 22)**: stagebox e stageboxes = `stêidji bóx` (saía "as tagebox", "estágio box"; plural invariável: "várias stêidji bóx"), front of house = `frônt óf ráus` ("front of OZ"), etherCON = `êtercón` ("E3-UN"), Weight = `Uêit` ("E-Aito"), Control Change e Program Change = `Control Tchêindj` e `Program Tchêindj` ("Xange"), Scene Recall = `Sín Ricól` ("CN Recal"), safe = `sêif` ("SAF"), Clock Rate = `Clóck Rêit` ("Clock, Hat"), View e VIEW = `Viú` ("Vieu"), Assign = `Assáin` ("a signa"), SET = `Séth` (o "h" impede o espeak de transformar o "t" final em "tch": `sêt`/`Sét`/`Set` viram "sétch" e, colados na letra, soam "sete A" e saem "7A"; `Séth A` vira /sɛt a/ e o Whisper escreve "Set A, Set B e Set C"; vale para qualquer palavra inglesa terminada em "t" seguida de vogal, confira com o espeak antes de gerar), Library = `Láibrari` ("Librarie"), ASIO = `Ázio` (`Ássio` saiu "ácido"; soletrar "A S I O" saiu "a SEO"), fades = `movimentos de fêider` ("FADs").
- **Mais grafias no roteiro (caps. 23 a 27)**: EIN = `é-i-ene` (com `ê, í, ene` saía "é circunflexo e agudo N"; letra com acento solta entre vírgulas é lida como nome do acento), AFL = `á-éfe-éle` (saía "FL"), "de A até F" = `de á até éfe` (o "A" virava artigo e sumia), backing vocals = `béquin vôcals` ("baquim vocaus"), in-ears = `fones in-ear` (o plural saía "in-earas"; o singular funciona), mix buses = `mix bâssis` ("mix buzzes"), Aux = `Áuks` (o X final ficava mudo: "Aus"), Quick Start Guide = `Kuík Istárt Gáid` ("qui" vira "ki": "Kickstart"). Evite "olho" no sentido de olhar (sai com o aberto, como o verbo: "leia com olho crítico" virou "óleo crético"); use `senso crítico`.
- **Mais grafias no roteiro (caps. 13 a 17)**: de-esser = `di-ésser` ("DSR"), chorus = `córus` ("SHORUS"/"choruz", o "ch" saía como em "chuva"), Hall = `Ról` ("AL"), Plate = `Plêit` ("PLAT"), delays = `dilêis` (o `PRON` só cobre o singular; saía "Delice"), OFF e ON = `óf` e `ôn` ("UFF"/"o FF"), safe e safes = `sêif` e `sêifs` ("SAF"), Recall = `Ricól` ("recal"), mute group = `miút grúp` ("multigrope"), quiz = `cuíz` ("keys"/"Kiz"; vale para TODO roteiro com a palavra, inclusive quando o Whisper já transcreve "quiz", porque a voz lê "kiz"; não há regra `PRON` para quiz, então a grafia fica no roteiro: `grep -il quiz script/*.txt` deve voltar vazio), Subgroup = `Sâbgrup` ("Subgrow"), User In e User Out = `Iúzer In` e `Iúzer Áut` ("Zer In"), front of house = `frônt óv ráus` ("front of oz"), encoders = `encôuders` ("encodeiros"), Linkwitz Riley = `Línquits Ráili` ("linguits relay"; com `Ráilei` saía "Highlight"), Exciter e Enhancer = `Eksáiter` e `Enrrânser` ("estéreo em Anser"), Tube Stage = `Tiúb Stêidj` ("Stagy"), Waves SuperRack = `Uêivs Súper Réck` ("Wav Super Hack"), Wave Designer = `Uêiv Designer`. Rack depois de outra palavra sai "Hack" no Whisper (o R brasileiro), mas soa certo. "Nas mesas xis ér, você" saía "XE" só nessa frase; "Nas mesas da família xis ér" resolveu.
- **Janela de sotaque baixa sem termo estrangeiro**: o classificador usa janelas de 4 s sem tirar silêncio. Uma janela com frase curta + pausa de parágrafo ("...e o outro, o chimbal." + "Um último cuidado.") deu p(pt_br)=0,00. Encher a frase ("e o outro lado equaliza o chimbal") resolveu. Para achar a janela sem rodar o classificador à mão: corte o áudio em janelas de 4 s com `ffmpeg -af "aresample=16000,atrim=start_sample=N:end_sample=N+64000" -c:a alac` numa pasta temporária e passe os caminhos relativos a `08-slides-v2/audio` ao `qa_batch.sh`; apague a pasta e os `whisper/jNN.txt` depois.
- `mute` em fim de frase ("o Mêin em mute") pode sair "Multi": escreva `miút`. No meio da frase ("com o canal em mute, ele") sai certo.
- Rótulo de tela em maiúsculas que não é sigla (REV VOZ) é soletrado letra por letra. Escreva em minúsculas e diga o que é: "o controle marcado rév voz, de reverb da voz".
- Palavra que some no começo de frase curta ("Ganho alto demais, ou..."): reescreva com verbo antes ("Se o ganho estiver alto demais...").
- **Mais grafias direto no roteiro** (QA de 22/10, caps. 5 a 8; o Kokoro deixa o H inicial inglês mudo e lê "ti" como "tchi"):
  headroom = `rédrum` (saía "eadroma"; em fim de frase curta use `réd-rum`), hold = `rôld` (saía "old"), Hi Mid = `Rái Mid` (saía "i mid"),
  sidechain = `sáidtchêin` (saía "se deixa in"), key = `quí` (key source saía "case source"; vale para key filter), ducker = `dâker`, ducking = `dâkin` (saíam "docker", "dukin"),
  Auto Time = `Auto Táim` (saía "auto chame"), Peak = `Píque` (saía "peac"), knee = `níi` (saía "kne"), View = `Viú` (saía "viéu"; o Whisper escreve "VU", mas o som é o do inglês),
  de-esser = `dí ésser` (saía "gesser"), filtro pente = `filtro de pente` (o Whisper ouvia "filtro paint"), "Decibel" abrindo frase = `O decibél` (saía "qual é").
  DI = `dê i` em TODO roteiro (s5-2-8 ainda tinha "A DI ativa" e saía "A 501 ativa": o espeak lê DI como número romano; com `dê i` o Whisper escreve "DEI"; `dê í` com acento sai "de agudo"). Confira com `grep -lw DI script/*.txt`, que deve voltar vazio.
  O verbo `ligue` depois de pausa ("Só depois ligue ou desligue", e também com vírgula "Só depois, ligue...") sai "lag": reescreva no indicativo com sujeito, `Só depois disso, você liga ou desliga o fântom`.
  Essas trocas **não** estão em `PRON` porque mudariam roteiros de outros capítulos sem QA. Os mesmos termos aparecem também em explorador, s2-2-1, s4-1-2, s13-1-1, s21-1-4 e s22-1-1: se forem promovidas a `PRON`, regere e confira esses ids também.
- Para um termo novo em inglês, teste antes: crie `sotaque/guia/termos.tsv` com uma linha por termo (`chave<TAB>grafia1|grafia2`, chave = como o Whisper deve escrever, sem espaço) e rode, em `tools/v2/tts`: `HF_HOME=$PWD/hf HF_HUB_OFFLINE=1 .venv/bin/python sotaque/guia/gera.py` e depois `HF_HUB_OFFLINE=1 ~/.local/share/uv/tools/mlx-whisper/bin/python sotaque/guia/transcreve.py`. Se a grafia normal falhar, acrescente a troca em `PRON` e um caso no `_teste()`.

## Arquivos

```
gen.sh / gen.py        gerador (Kokoro pm_alex; gen.sh --teste = autoteste)
teste-sotaque.md       teste objetivo de sotaque: método, calibração, tabela por candidata e marcador
samples-br/            amostras finais: capa, s12-1-1, s2-1-1 e teste-sotaque (.m4a)
samples-br/cand/       candidatas no texto de teste (Kokoro, Qwen clone, Qwen VoiceDesign, Chatterbox, controle pt-PT)
samples-br/cand-roteiros/  Kokoro × Chatterbox nos 3 roteiros reais
sotaque/               analisa.py (a/b/c), classif.py, confere.py, mos.py, tabela.py, resultados.json,
                       geradores das candidatas (kokoro.py, qwen.py, chatterbox.py), ref/, calib/ (só régua), guia/
voz/referencia.wav, voz/keep/   vozes ANTIGAS do Qwen (pt-PT); não são mais usadas
samples/               avaliação ANTIGA (Qwen, pt-PT); só histórico
hf/                    modelos (17 GB). Em uso: Kokoro-82M-bf16 (0,36 GB). Só para verificação: wav2vec2 espeak (1,3 GB)
                       e portuguese-accent-classifier (0,4 GB). Podem ser removidos (~16 GB): os 4 Qwen3-TTS, chatterbox-fp16,
                       S3TokenizerV2 e models/piper/
.venv/                 Python 3.12 isolado (mlx-audio, misaki, espeakng-loader, torch/transformers para a verificação)
```
