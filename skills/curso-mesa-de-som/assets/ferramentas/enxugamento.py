# EXEMPLO DA 1ª EXECUÇÃO (curso XR18). REESCREVA para o curso atual na Fase 3: é aqui que fica o plano enxuto
# (ordem final dos slides por capítulo, fusões de bullets/títulos/diagramas, quizzes, aberturas). build_slides.py carrega este arquivo.
# Enxugamento do deck (plano: 07-slides/redesign/plano-enxugamento.md). Lido por build_slides.py.
# ORDER  = os slides que existem, na ordem, por capítulo. Todo id que não está aqui sai do deck (agenda-N, fecha-N, fig-N, cap. 00 e as seções fundidas).
# BULLETS = corpo escrito à mão dos slides que absorveram outros ("[M] " = manual, "[C] " = na prática, "[D] Assunto | opção | opção" = selo de abordagens divergentes).
# TITLE / MESAS / DIAG = título, selo de mesas e diagrama do slide que mudou com a fusão. DIAG: chave do slides_viz.D, (chave, args) ou 'bespoke:<id>'.
# As notas do professor ficam em tools/notes/<id>.html.

ORDER = {
 1: ['cap-1', 's1-1-2', 's1-1-3', 's1-1-4', 's1-1-7', 'explorador', 's1-2-10', 'quiz-1'],
 2: ['cap-2', 's2-1-1', 's2-1-3', 's2-1-4', 's2-1-6', 's2-1-7', 's2-1-8', 's2-2-1', 'quiz-2'],
 3: ['cap-3', 's3-1-1', 's3-1-2', 's3-1-3', 's3-2-1', 's3-2-4', 's3-2-8', 'quiz-3'],
 4: ['cap-4', 's4-2-1', 's4-2-2', 's4-2-4', 's4-1-2', 's4-2-9', 's4-1-3', 's4-2-11', 'quiz-4'],
 5: ['cap-5', 'caminho-do-sinal', 's5-1-2', 's5-2-8', 's5-2-1', 's5-2-3', 'quiz-5'],
 6: ['cap-6', 's6-2-1', 's6-2-2', 's6-2-3', 's6-2-4', 'quiz-6'],
 7: ['cap-7', 's7-1-1', 'quiz-7'],
 8: ['cap-8', 's8-1-1', 's8-2-3', 's8-2-4', 's8-2-5', 'quiz-8'],
 9: ['cap-9', 's9-1-2', 's9-1-3', 's9-1-5', 'quiz-9'],
 10: ['cap-10', 's10-1-1', 's10-1-2', 's10-1-3', 's10-1-4', 's10-2-3', 'quiz-10'],
 11: ['cap-11', 's11-1-1', 's11-1-2', 's11-2-2', 's11-2-3', 's11-2-5', 's11-2-6', 'quiz-11'],
 12: ['cap-12', 's12-1-1', 's12-1-2', 's12-1-3', 's12-2-2', 's12-2-3', 'quiz-12'],
 13: ['cap-13', 's13-1-1', 's13-1-2', 's13-1-4', 's13-2-6', 'quiz-13'],
 14: ['cap-14', 's14-1-1', 's14-1-2', 's14-2-2', 'quiz-14'],
 15: ['cap-15', 's15-1-1', 's15-2-2', 's15-2-3', 's15-2-4', 'quiz-15'],
 16: ['cap-16', 's16-1-1', 's16-1-3', 's16-2-3', 'quiz-16'],
 17: ['cap-17', 's17-1-1', 's17-1-2', 's17-1-4', 's17-1-5', 'quiz-17'],
 18: ['cap-18', 's18-1-1', 'quiz-18'],
 19: ['cap-19', 's19-2-1', 's19-2-3', 's19-2-5', 's19-2-10', 'quiz-19'],
 20: ['cap-20', 's20-1-1', 's20-2-2', 's20-1-2', 's20-2-4', 's20-2-6', 'quiz-20'],
 21: ['cap-21', 's21-1-1', 's21-1-4', 's21-1-6', 'quiz-21'],
 22: ['cap-22', 's22-1-1', 's22-1-3', 'quiz-22'],
 23: ['cap-23', 's23-2-1', 's23-2-2', 's23-2-4', 'quiz-23'],
 24: ['cap-24', 'quiz-24'],
 25: ['cap-25', 's25-1-1'],
 26: ['cap-26', 's26-1-1', 's26-2-3', 's26-2-2', 's26-2-6'],
 27: ['cap-27', 's27-1-1'],
}

# título curto (sumário e botão "Próximo"); o completo fica no tooltip do sumário
SHORT = {1: 'Conheça as mesas', 2: 'Painel e ligações', 3: 'Rede e controle remoto', 4: 'Apps e organização', 5: 'Sinal, fonte e ganho',
         6: 'Low cut e EQ', 7: 'Gate, expansor e ducker', 8: 'Compressor', 9: 'Delay, pan e roteiro', 10: 'Buses e envios',
         11: 'Retornos de palco', 12: 'RTA e microfonia', 13: 'Efeitos', 14: 'DCA e grupos', 15: 'Sistema de PA',
         16: 'Cenas e safes', 17: 'Escuta do técnico', 18: 'Automix', 19: 'Gravação e live', 20: 'AES50 e stageboxes',
         21: 'MIDI e Setup', 22: 'Firmware e cuidados', 23: 'Roteiros e checklists', 24: 'Erros comuns', 25: 'Fichas técnicas',
         26: 'Onde estudar', 27: 'Glossário'}
# título do capítulo nos slides quando muda em relação ao PDF
CAPTITLE = {4: 'Apps, navegação e organização', 5: 'Caminho do sinal, fonte e ganho', 9: 'Delay, pan, link e o roteiro do canal', 11: 'Retornos de palco, in-ear e P16',
            15: 'Sistema de PA', 21: 'MIDI, controle externo e Setup', 20: 'Expansão: AES50, stageboxes e split', 22: 'Firmware, manutenção e cuidados', 24: 'Erros comuns', 26: 'Onde estudar'}
# linha-promessa da abertura de cada capítulo: o que o aluno vai saber fazer
PROMISE = {
 1: 'As duas famílias, quem é irmã de quem e o que muda de um modelo para outro.',
 2: 'Entradas e saídas de cada mesa, ligar e desligar sem estalo e voltar ao padrão de fábrica.',
 3: 'Modos de rede, primeira conexão e a rede que não cai no show.',
 4: 'Qual app usar em cada aparelho, como navegar na superfície e deixar a mesa organizada antes de mixar.',
 5: 'O caminho do sinal no canal e o ajuste que mais pesa: o ganho.',
 6: 'Limpar o grave que sobra e moldar o timbre com poucos movimentos.',
 7: 'Silenciar o que não está tocando sem cortar o que importa.',
 8: 'Segurar a dinâmica sem precisar seguir o cantor no fader.',
 9: 'Posicionar e alinhar o canal e ajustar qualquer canal na ordem certa.',
 10: 'De que ponto do canal sai cada envio, e por que o retorno muda sozinho.',
 11: 'Uma mix para cada músico, em caixa, in-ear ou mixer pessoal.',
 12: 'Achar a microfonia com método e afinar o PA sem tirar a vida do som.',
 13: 'Reverb e delay por envio, processadores em insert, e o rack bem planejado.',
 14: 'DCA só controla volume, subgrupo soma e processa, mute group silencia.',
 15: 'Matriz, subwoofer, crossover e delay: a mesa fazendo papel de processador. As X AIR não têm matriz; para elas há truques.',
 16: 'Guardar, recuperar e proteger o que não pode mudar.',
 17: 'Ouvir sem mexer no PA, falar com o palco e testar o sistema.',
 18: 'Muitos microfones de fala abertos sem microfonia e sem precisar mexer no fader.',
 19: 'Gravar multipista, tocar música e entregar uma mix própria para a live.',
 20: 'Um cabo de rede no lugar do multicabo e duas mesas dividindo os mesmos microfones.',
 21: 'Trocar cenas de fora da mesa e usar a mesa como controlador.',
 22: 'Atualizar sem perder o show e manter a mesa viva por anos.',
 23: 'Do carregamento ao fim do evento, numa ordem que não esquece nada.',
 24: 'Os erros que mais derrubam um show, reconhecidos pelo sintoma.',
 25: 'Faixa dinâmica, ruído e limites lado a lado.',
 26: 'Por onde continuar, por família e por idioma.',
 27: 'Todos os termos do curso num só lugar.',
}

TITLE = {}   # num da seção -> título no slide
MESAS = {}   # num da seção -> mesas do selo
DIAG = {}    # id do slide -> diagrama
BULLETS = {} # num da seção -> bullets
QUIZ = {    # cn -> (pergunta, [alternativas], índice da certa, explicação: o porquê, sem repetir a alternativa certa)
 1: ('A X18 é…', ['A XR18 em formato de mesa, sem faders', 'A XR18 com 16 faders motorizados', 'Uma mesa da família X32'], 0,
     'Mesmo motor da XR18; o tampo inclinado serve para apoiar o tablet, e o único controle físico de áudio é o volume do fone.'),
 2: ('Qual é a ordem segura para ligar o sistema?', ['Amplificadores e caixas ativas primeiro, mesa depois', 'Mesa primeiro, amplificadores e caixas ativas por último', 'Tanto faz: a mesa protege o PA sozinha'], 1,
     'Quem amplifica liga por último e desliga primeiro: o estalo da mesa ligando nunca chega ao alto-falante.'),
 3: ('Só o cabo USB está ligado ao notebook e o app não acha a mesa. Por quê?', ['Falta instalar o driver de áudio', 'O controle é sempre pela rede, por Wi-Fi ou cabo', 'O USB só funciona com a mesa desligada'], 1,
     'O USB leva áudio e MIDI; app e mesa conversam por rede. Para controlar e tocar música do mesmo notebook, use os dois cabos.'),
 4: ('O que faz o modo Sends on Faders?', ['Liga todos os efeitos de uma vez', 'Faz os faders montarem a mix de um retorno (Aux ou Mix bus)', 'Manda todos os canais para o Main'], 1,
     'Os mesmos faders passam a controlar o envio de cada canal para o bus escolhido: é o jeito mais rápido de montar um retorno.'),
 5: ('Qual é a meta para o ganho de entrada?', ['Média perto de −18 dBFS, com folga para os picos', 'Sinal sempre encostando em 0 dBFS', 'Medidor no vermelho no refrão'], 0,
     'O digital não tem folga acima do teto: o pico que passa vira distorção na hora. Mirar a média bem abaixo dele guarda espaço para o cantor que cresce no refrão.'),
 6: ('Qual é a regra de ouro do EQ?', ['Reforçar primeiro, cortar depois', 'Cortar antes de reforçar', 'Usar sempre as 4 bandas'], 1,
     'Muitas vezes o agudo que falta está escondido por excesso de grave: tirar o que sobra limpa o som sem empurrar o canal para a microfonia.'),
 7: ('O que o gate faz?', ['Abre acima do threshold e atenua o vazamento entre as batidas', 'Aumenta o volume das notas fracas', 'Atrasa o canal para alinhar com o PA'], 0,
     'Entre as batidas o sinal cai abaixo do limite e a porta fecha; o range decide quanto do vazamento ainda passa.'),
 8: ('No compressor, o que acontece acima do threshold?', ['A saída sobe mais que a entrada', 'A saída sobe menos que a entrada; quanto maior o ratio, mais forte o controle', 'O canal é mutado'], 1,
     'O compressor só mexe no excesso: o que fica abaixo do limite passa intacto, e o ratio diz quanto do que passou dele chega à saída.'),
 9: ('Em qual família existe delay de canal?', ['Só na família X32/M32', 'Só na família X AIR', 'Nas duas famílias'], 0,
     'Na X AIR o atraso só existe como efeito (Stereo Delay) em insert, e cada um gasta um slot do rack.'),
 10: ('Qual é o ponto de captação certo para retorno e para efeito?', ['Retorno pós-fader, efeito pré-fader', 'Retorno pré-fader, efeito pós-fader', 'Os dois sempre pós-fader'], 1,
      'O retorno não pode mudar quando o técnico mexe no PA; o reverb precisa sumir junto quando o fader do canal fecha.'),
 11: ('O retorno está saindo no PA. A causa quase sempre é…', ['Caixa de retorno ativa no palco', 'O bus de monitor atribuído ao Main LR', 'Phantom ligado no canal da voz'], 1,
      'Com o LR ligado no bus, a mix do músico soma ao PA. O conserto fica na aba Main do bus.'),
 12: ('Com o RTA, como tratar uma frequência que apita?', ['Cortar só ela, com banda estreita', 'Baixar o fader master', 'Reforçar a frequência vizinha'], 0,
      'Um corte estreito de poucos dB tira o apito e preserva o resto do timbre; baixar o master derruba a mix inteira.'),
 13: ('No rack do X AIR Edit aparece "OFF" embaixo do slot. O que isso indica?', ['O efeito está desligado', 'O insert está desligado, o certo para reverb e delay por envio', 'O slot está com defeito'], 1,
      'OFF fala do insert, não do efeito: um reverb usado por envio funciona com o insert desligado.'),
 14: ('Qual é a diferença entre DCA e subgrupo?', ['DCA soma o áudio; subgrupo só controla volume', 'DCA comanda volumes sem somar áudio; subgrupo soma e permite processar o conjunto', 'São a mesma coisa com nomes diferentes'], 1,
      'Pelo DCA não passa áudio, então não há onde pôr EQ ou compressor; o subgrupo é um bus de verdade.'),
 15: ('Em quais mesas existem matrizes?', ['Só na família X32/M32', 'Em todas as 13 mesas', 'Só na XR18 e na MR18'], 0,
      'Nas X AIR, um Aux pós-fader ou um subgrupo faz o papel de saída extra para outra sala ou para as torres.'),
 16: ('Para que serve um safe?', ['Para gravar o show no pendrive', 'Para proteger o que a cena não pode mudar', 'Para travar a tela do tablet'], 1,
      'A cena reescreve a mesa inteira; o safe abre uma exceção para o que precisa sobreviver à troca, mesmo que a cena tenha sido gravada com outro valor.'),
 17: ('Ao apertar Solo num canal, o público…', ['Passa a ouvir só aquele canal', 'Continua ouvindo a mesma mix: o solo vai para o fone do técnico', 'Ouve o canal mais alto'], 1,
      'Solo é escuta: troca o que toca no fone e na saída de monitor, sem mexer no Main.'),
 18: ('O que o automix faz?', ['Abaixa automaticamente os microfones de quem não está falando', 'Iguala o volume de todos os instrumentos', 'Mixa a banda sozinho'], 0,
      'Funciona como uma divisão: o grupo tem um total fixo de ganho e ele vai para onde há fala. Por isso abrir mais microfones não aproxima a sala da microfonia.'),
 19: ('Por que não mandar o Main direto para a live?', ['A internet não aceita áudio estéreo', 'A mix do PA depende da sala: o que é alto no palco fica baixo no PA e some na transmissão', 'O Main não tem saída digital'], 1,
      'O PA só completa o que o palco já faz soar na sala. A transmissão não ouve o palco, então precisa de uma mistura montada para ela.'),
 20: ('Quantos canais a AES50 leva por porta?', ['8 em cada sentido', '48 em cada sentido, por cabo Cat5e blindado', 'Ilimitados, por Wi-Fi'], 1,
      'Cada porta leva os dois sentidos ao mesmo tempo, entradas do palco e saídas para ele. Com A e B ocupadas, a mesa chega a 96 × 96 canais.'),
 21: ('A pedaleira manda Program Change 5 e a X32 não troca de cena. O que conferir?', ['Setup › Remote: entrada MIDI ligada e recall de cena por MIDI habilitado', 'Se o phantom do canal 5 está ligado', 'Se o fader do canal 5 está em 0 dB'], 0,
      'O 5 é o número da cena, não de um canal. Se a mensagem chega e nada muda, o bloqueio está na entrada MIDI da mesa.'),
 22: ('A X32 ficou presa na tela de atualização. O que fazer?', ['Desligar e religar sem segurar o botão de atualização', 'Segurar RESET por 10 segundos', 'Atualizar pelo app do tablet'], 0,
      'Sem um arquivo válido no pendrive a mesa fica esperando; ligando sem o botão, ela volta ao firmware instalado.'),
 23: ('Na igreja com voluntários, o que fica na mão de quem opera durante o culto?', ['Poucos faders e DCAs, com o ganho fixo', 'O app completo, para corrigir o que precisar', 'O ganho de cada canal, para seguir o volume'], 0,
      'Cada opção a menos é um erro a menos: com a cena pronta e o ganho travado, o voluntário só equilibra volumes.'),
 24: ('Os canais da bateria vão para um subgrupo, mas continuam no Main. O que acontece?', ['Som em dobro e problema de fase', 'Nada: o subgrupo substitui o Main', 'O subgrupo fica mudo'], 0,
      'O canal chega ao PA por dois caminhos, direto e pelo subgrupo; com processamento no subgrupo, os dois chegam defasados.'),
}

# ---------------------------------------------------------------- cap. 01
TITLE.update({'1.1.2': 'Quem é irmã de quem', '1.1.3': 'X AIR: a mesa é o motor, o app é o volante', '1.2.4': 'XR16 e XR12: faltam conectores, não recursos',
              '1.1.4': 'X32/M32: um cérebro, vários corpos', '1.1.7': 'X AIR × X32/M32: o que muda na prática'})
MESAS.update({'1.2.4': 'XR16, XR12, MR12'})
DIAG.update({'s1-2-4': 'xr1612', 's1-1-4': 'bodies7'})
BULLETS.update({
 '1.1.2': ['[M] Gêmeas: mesmo software e processamento; muda o logotipo.',
           '[C] Nas MR: pré-amps MIDAS PRO e conectores Neutrik com trava.',
           '[M] MR18 sem Hi-Z: violão e baixo passivos entram por DI.',
           '[C] Cenas da XR18 abrem na MR18 sem ajuste.'],
 '1.1.3': ['[M] Sem faders: tudo pelo app, no tablet, celular ou computador.',
           '[C] Se o app cai, o som continua: a mesa guarda o último estado.',
           '[C] Fica no palco, como stagebox: nada de multicabo até a técnica.',
           '[M] Motor igual nas seis: 16 + 1 estéreo, 6 Aux, 4 FX, 4 DCA.',
           '[C] X18: a XR18 em formato de mesa, só com o volume do fone.'],
 '1.2.4': ['[M] XR16: 8 pré-amps, Hi-Z em 15–16, linhas 9–16, 4 Aux.',
           '[M] XR12: 4 pré-amps, mas 16 canais internos e 6 buses.',
           '[C] "Faltam conectores, não recursos".',
           '[M] USB das duas: grava e toca estéreo em pendrive.'],
 '1.1.4': ['[M] Motor comum a X32 e M32: 40 entradas, 25 buses, 8 FX, 8 DCA.',
           '[M] 100 cenas, placa 32 × 32 e duas portas AES50; sem Wi-Fi.',
           '[C] M32 × M32 LIVE: só muda a placa (a LIVE grava em SD).',
           '[C] M32R LIVE, de 2018, é a versão atual da M32R.',
           '[C] M32C: uma M32 inteira em 1U; todo o áudio vai por AES50.'],
 '1.1.7': ['[C] GEQ de bus: livre na X AIR, gasta um slot na X32/M32.',
           '[M] Só na X32/M32: crossover, delay de saída, LCR, oscilador e AES50.',
           '[C] Entre as famílias, só ligação analógica: Ultranet não é AES50.',
           '[C] Ex.: saídas da X32 numa MR18 para mixar a live.'],
 '1.2.10': ['[C] Garantia (XR12, M32C): registrada em 90 dias, vai de 1 para 3 anos.',
            '[C] No Brasil, prefira o distribuidor oficial.',
            '[C] Importada sem garantia: o conserto pode não ser viável.',
            '[C] Usada: faders motorizados presos e encoders falham mais.',
            '[C] X32 Compact usada: 1 hora testando cada entrada e saída.'],
})

# ---------------------------------------------------------------- cap. 02
TITLE.update({'2.1.1': 'Painel das X AIR / M AIR', '2.1.3': 'Superfície X32/M32', '2.1.4': 'Mesas de rack: X32 Rack e M32C', '2.1.6': 'Cinco jeitos de ligar',
              '2.1.7': 'Ligar e desligar sem estalo', '2.1.8': 'Reset de fábrica', '2.2.1': 'Que entrada usar'})
MESAS.update({'2.1.1': 'XR18, X18, XR16, XR12, MR18, MR12', '2.1.4': 'X32 Rack, M32C', '2.2.1': 'XR18, X18, XR16, XR12, MR18, MR12, X32, X32 Compact, X32 Producer, M32R'})
BULLETS.update({
 '1.1.2': ['[M] Gêmeas: mesmo software e processamento; muda o logotipo.',
           '[C] Nas MR: pré-amps MIDAS PRO e conectores Neutrik com trava.',
           '[C] Mesmo app com outro nome: M AIR Edit.',
           '[C] Cenas da XR18 abrem na MR18 sem ajuste.'],
 '2.1.1': ['[M] Em todas: Ethernet, REMOTE, RESET, MIDI, Main em XLR e fone.',
           '[M] USB B 18 × 18 nas de 18 canais; USB A (pendrive) na XR16 e XR12.',
           '[M] Ultranet para P16: só XR18, X18 e MR18.',
           '[M] Aux: 6 XLR, 6 P10 na X18, 4 XLR na XR16, 2 P10 na XR12.',
           '[C] X18: 17/18 em RCA e saída Control Room; as duas têm 6 Aux.'],
 '2.1.3': ['[M] Channel Strip: os controles físicos do canal selecionado.',
           '[M] Faders de entrada com Select, Solo, mini tela e Mute: 16 na X32 e M32, 8 nas outras.',
           '[M] Tela com 6 encoders, camadas e monitoração.',
           '[M] Group/Bus/Main: 8 faders de saída e o Main.'],
 '2.1.4': ['[M] X32 Rack: tela de 5", CHANNEL SELECT e um fader de nível.',
           '[M] Traseira: 16 XLR in, 8 out, AES50 A/B, X-USB, Ultranet.',
           '[M] LED vermelho ao lado do XLR: phantom ligado.',
           '[M] M32C: LCD, SELECT e LEDs AES50 (verde ok, vermelho erro).',
           '[M] Na M32C o mic liga no stagebox; ganho e phantom são remotos.'],
 '2.1.6': ['[M] Show típico: a mesa no palco, a técnica controla pela rede.',
           '[M] iPad com adaptador de câmera grava até 18 pistas no USB.',
           '[M] Bar: pedaleira MIDI troca cenas no pé.',
           '[M] Estúdio X32: S16 e P16 na sala, um só cabo AES50.'],
 '2.1.7': ['[M] Ligar: mesa antes do PA. Desligar: PA antes da mesa.',
           '[M] X AIR: Mute at Power On e Safe Levels mutam as saídas no boot.',
           '[M] X32: Safe Main Levels abaixa o Main e segura a cena.',
           '[M] Safe Shutdown (X32): espera a mesa terminar de gravar o estado.'],
 '2.1.8': ['[M] X AIR: RESET 2 s volta só a rede; 10 s apaga tudo.',
           '[C] ⚠ Erro comum: segurar 10 s para resolver a conexão apaga tudo.',
           '[M] X32: Scenes/Undo no boot, ou Setup › Config › Initialize.',
           '[M] Shows e cenas só saem com a opção Show Data.',
           '[C] M32C: o painel faz DHCP, IP, lock e cena sem app.'],
 '2.2.1': ['[C] Instrumento passivo: entrada Hi-Z; sem Hi-Z (MR18), DI.',
           '[C] Instrumento ativo ou pedaleira: nível de linha, qualquer entrada.',
           '[C] Cabo de instrumento com mais de ~6 m: DI e XLR.',
           '[C] Música de fundo: 17/18 na X AIR; Aux In P10 na X32.',
           '[C] Aux In Remap (X32): as entradas Aux viram canais.'],
})

# ---------------------------------------------------------------- cap. 03
TITLE.update({'3.1.1': 'Chave REMOTE: três modos e quando usar', '3.1.2': 'Primeira conexão', '3.1.3': 'X32/M32: sem Wi-Fi, rede só por cabo',
              '3.2.1': 'Rede controla, USB leva áudio', '3.2.4': 'Roteador externo: a rede do show', '3.2.7': 'Sincronizar: Mixer → PC', '3.2.8': 'Rede de show: senha e trava'})
MESAS.update({'3.2.1': 'XR18, X18, MR18, X32, X32 Compact'})
DIAG.update({'s3-1-3': 'x32net', 's2-1-1': ('panel_xr18', {'hl': {(1, 2): 1, (0, 3): 2, (1, 3): 3, (1, 0): 4, (2, 0): 5}})})
BULLETS.update({
 '3.1.1': ['[M] Chave REMOTE: escolhe o modo; os ajustes ficam em Setup › Network.',
           '[C] Ethernet: show e local grande; o modo mais confiável.',
           '[C] Wi-Fi Client: quando o local já tem roteador.',
           '[C] Access Point: ensaio e sala pequena, até 4 aparelhos.',
           '[M] Roteador: cria a rede; não precisa de internet.'],
 '3.1.2': ['[M] Android: ligue o Wi-Fi Lock, que prende o aparelho na rede da mesa.',
           '[M] iPad: a mesa aparece em Devices; toque no ícone.',
           '[M] Computador: Setup, escolha a mesa e sincronize Mixer → PC.',
           '[M] Rede da mesa: modelo + final do MAC (ex.: XR18-17-BE-C0).'],
 '3.1.3': ['[M] X32 e M32: tablet só com roteador externo na porta Ethernet.',
           '[M] SETUP › Network: encoder 1 escolhe, 2 a 5 ajustam, 6 confirma.',
           '[C] Mesa com IP fixo alto; o resto por DHCP.',
           '[C] Cerca de 10 controles remotos ao mesmo tempo.',
           '[C] M32C: ligue o DHCP no SELECT, senão o tablet não acha a mesa.'],
 '3.2.1': ['[C] Só o cabo USB: o app não acha a mesa.',
           '[C] Notebook que controla e toca música: rede + USB.',
           '[C] X18 e MR18: rede na porta Ultranet faz a mesa "sumir".',
           '[C] X32: para gravar, o USB vai na placa, não no de controle.'],
 '3.2.4': ['[C] Wi-Fi interno: só 2,4 GHz; cai quando o público chega.',
           '[C] Roteador dual band na Ethernet; tablets em 5 GHz com WPA2.',
           '[C] REMOTE em Ethernet, Setup › Search e LAN em DHCP.',
           '[C] Mesa na porta LAN, nunca na WAN; o IP dela muda.',
           '[C] Roteador no alto, teste andando e um notebook no cabo.'],
 '3.2.8': ['[C] Access Point vem aberto: ponha senha (só WEP, mas ajuda).',
           '[M] Porta Ethernet não tem senha: proteja o roteador com WPA2.',
           '[C] Local cheio: SSID oculto e só 5 GHz.',
           '[M] Lock Console (X32): trava a superfície; HOME destrava.',
           '[M] M32C: a trava é pelo botão SELECT.'],
})

# ---------------------------------------------------------------- cap. 04
TITLE.update({'4.2.1': 'Apps de controle hoje', '4.2.2': 'Apps de computador', '4.2.4': 'Mixing Station e OSC', '4.2.5': 'Quem opera com o quê',
              '4.1.2': 'Navegar na X32/M32', '4.2.9': 'Poucos ou nenhum fader', '4.2.11': 'Organizar antes de mixar', '4.2.13': 'Monte o show em casa'})
MESAS.update({'4.2.2': 'XR18, X18, XR16, XR12, MR18, MR12, X32, X32 Rack, X32 Producer, M32, M32R, M32C', '4.2.5': 'XR18, X18, XR12, MR18, MR12, X32, X32 Rack, X32 Producer, M32, M32R, M32C',
              '4.2.9': 'X32 Compact, X32 Producer, X32 Rack, M32C', '4.2.11': 'XR18, X18, XR16, XR12, MR18, MR12, X32, X32 Rack, X32 Compact, X32 Producer, M32, M32R, M32C',
              '4.2.13': 'XR18, X18, XR16, XR12, MR18, MR12, X32, X32 Rack, X32 Compact, X32 Producer, M32, M32R, M32C'})
DIAG.update({'s4-2-1': 'appmatrix', 's4-2-5': ('apps', {'v': 2}), 's4-1-2': 'surf428'})
BULLETS.update({
 '4.2.1': ['[M] Computador: X AIR Edit, M AIR Edit, X32-Edit e M32-Edit.',
           '[C] Tablet e celular: MX-Mix e MX-Q, para as quatro linhas.',
           '[C] Os apps antigos de tablet não rodam em sistemas de 2022 em diante.',
           '[C] Teste o MX-Mix antes do show: as versões mudam rápido.'],
 '4.2.2': ['[C] Abas na ordem do sinal: Input, Gate, EQ, Comp, Sends.',
           '[C] Selecione pelo número do canal; clique direito: nome e cor.',
           '[M] Preferences: Exclusive solo, fader Fine e Auto Select.',
           '[M] Utilities: janelas extras de RTA, Buses, DCA e medidores.',
           '[C] X32-Edit: janela Mixer e "mix to" levam os faders a um bus.'],
 '4.2.4': ['[M] OSC: a língua aberta que app e mesa falam pela rede.',
           '[C] Porta 10024 nas X AIR; 10023 nas X32/M32.',
           '[C] Mixing Station: layouts próprios, RTA e redução de ganho.',
           '[C] Senha por bus: só ele respeita, e não é segurança real.',
           '[C] Sem suporte da Music Tribe; a licença é por modelo: confira na loja de apps.'],
 '4.2.5': ['[C] Técnico: notebook no cabo, mais rápido na emergência.',
           '[C] Músico: só app de retorno, nunca o app completo.',
           '[C] MX-Q: só o bus do músico, com grupos rápidos.',
           '[C] Celular do músico: "não perturbe" e tela sempre acesa.',
           '[C] O app não toca áudio: o músico ouve no fone ou na caixa.'],
 '4.1.2': ['[M] View (X32 e M32): cada seção leva a tela direto à sua página.',
           '[M] Select: sempre há um canal selecionado; DCA não é canal.',
           '[M] Anel de LED apagado: o parâmetro não existe naquele canal.',
           '[C] "No máximo dois toques": bloco → View → aba.',
           '[C] View em Config/Preamp: medidor grande para o ganho.'],
 '4.2.9': ['[M] Compact e Producer: 8 canais por vez, em camadas.',
           '[C] Canais pouco mexidos na camada 17–32, num DCA.',
           '[C] Canal 9 no DCA 1, 10 no DCA 2: até 16 "faders" de entrada.',
           '[C] X32 Rack e M32C: o caminho é o app.',
           '[C] X-Touch pela rede vira faders motorizados (firmware 3.0+).'],
 '4.1.3': ['[M] Os faders montam a mix de um bus: em geral, um retorno.',
           '[M] X AIR / M AIR: escolha o Aux ou o FX no Fader Bank.',
           '[M] X32/M32: só Mix Bus 1–16, não DCA, Main ou Matrix.',
           '[M] Com um canal selecionado, mostra para onde ele vai.'],
 '4.2.11': ['[C] Nome e cor em todos os canais e buses antes do ensaio.',
            '[C] Cor por família de instrumento e por efeito.',
            '[C] Patch 1:1: mude o cabo, não o roteamento.',
            '[M] Copiar canal leva gate, EQ, comp e envios; o ganho não vai.',
            '[M] Library (X32): presets de canal, efeito e roteamento.'],
 '4.2.13': ['[C] Os apps de computador funcionam offline, sem a mesa.',
            '[C] Comece de uma cena em branco e salve como modelo.',
            '[C] Deixe prontos nomes, cores, ganho, envios, FX e EQ.',
            '[C] X32/M32: salve no pendrive e carregue na mesa.',
            '[C] Mapeie entradas e saídas no papel; rotule o multicabo.'],
})

# ---------------------------------------------------------------- cap. 05
TITLE.update({'5.1.2': 'Fonte do canal: entrada, USB e patch', '5.2.8': '+48 V e polaridade', '5.2.1': 'Meta de ganho: −18 dBFS',
              '5.2.3': 'Passagem de som: ganho em 4 passos', '5.2.4': 'O ganho se ajusta uma vez'})
MESAS.update({'5.2.8': 'XR18, X18, XR16, XR12, MR18, MR12, X32, X32 Rack, X32 Compact, X32 Producer, M32, M32R, M32C',
              '5.2.1': 'XR18, X18, XR12, MR18, X32', '5.2.4': 'XR18, MR18, X32, X32 Compact, M32, M32R, M32C'})
BULLETS.update({
 '5.1.2': ['[C] "O canal queimou"? Confira o botão USB: aceso, a entrada é ignorada.',
           '[M] X AIR: patch livre, qualquer canal em qualquer entrada.',
           '[M] X32/M32: fontes em blocos de 8; um canal em Config › Source.',
           '[C] No começo, patch 1:1: entrada 1 no canal 1.',
           '[C] Uma entrada em dois canais: um para o PA, outro para o retorno.'],
 '5.2.8': ['[C] +48 V só para condensador e DI ativa; nunca em microfone de fita.',
           '[M] Mute o canal antes, e os músicos tiram os fones.',
           '[M] XR12: phantom só nos canais 1–4.',
           '[C] Ø: dois mics opostos na mesma fonte; fica o que soa mais cheio.',
           '[C] O "phase" da X32 inverte a polaridade, não o tempo.'],
 '5.2.1': ['<div class="term"><b>Gain staging:</b> o nível certo em cada etapa, nem fraco nem estourado.</div>',
           '[C] Média perto de −18 dBFS, picos 3 a 6 dB acima.',
           '[C] Headroom: acima de 0 dBFS, só distorção.',
           '[C] Canais no mesmo nível: presets de gate e comp funcionam.',
           '[C] O pré soa mais limpo com ganho moderado.'],
 '5.2.3': ['[C] Peça o nível de show: quem "economiza" na passagem estoura depois.',
           '[C] X32: Select, View em Config e Solo dão o medidor grande.',
           '[C] Partida: voz dinâmica 25–30 dB, lapela 15–20, condensador 25–35.',
           '[C] Teste as saídas antes do primeiro microfone.'],
 '5.2.4': ['[C] O ganho muda tudo o que vem depois: PA, retornos, efeitos, gravação.',
           '[C] Ajuste uma vez e mixe com faders e envios.',
           '[C] Só volte ao ganho se o canal estourar.',
           '[C] Canais no alvo, Main perto de 0: o volume da sala fica no PA.'],
})

# ---------------------------------------------------------------- caps. 06 e 07
TITLE.update({'6.2.1': 'Low cut / HPF', '6.2.2': 'O EQ paramétrico do canal', '6.2.3': 'Regras de ouro do EQ', '6.2.4': 'EQ de voz: pontos de partida',
              '7.1.1': 'Gate, expansor e ducker: parâmetros e modos', '7.2.2': 'Gate na prática'})
MESAS.update({'6.2.1': 'XR18, X18, XR16, XR12, MR18, MR12, X32, X32 Rack, X32 Compact, X32 Producer, M32, M32R, M32C',
              '6.2.2': 'XR18, X18, XR16, XR12, MR18, MR12, X32, X32 Rack, X32 Compact, X32 Producer, M32, M32R, M32C'})
BULLETS.update({
 '6.2.2': ['[M] Cada banda: frequência, ganho e largura (Q); em 0 dB, parada.',
           '[C] Os nomes das 4 bandas são só sugestão: qualquer uma vai a qualquer frequência.',
           '[M] Corte e shelf nas pontas; PEQ e VEQ (vintage) em qualquer banda.',
           '[C] Q alto: estreito, para microfonia. Q baixo: largo, para dar cor.'],
 '6.2.3': ['[C] Corte antes de reforçar: o agudo que falta costuma estar sob o grave.',
           '[C] Comece com a EQ plana e mexa em passos pequenos.',
           '[C] Compare ligada e desligada; virou montanha-russa, zere.',
           '[C] Ajuste a voz com a banda tocando, não em solo.'],
 '6.2.4': ['[C] Embolado: ~250 Hz.',
           '[C] Caixa de papelão: 300–500 Hz. Oco: −5 dB em 400–600 Hz.',
           '[C] Fanhoso: ~600 Hz. Clareza: reforço largo em 2–3 kHz.',
           '[C] Sibilância: 5–8 kHz ou de-esser. Ar: leve em ~10 kHz.',
           '[C] Erro comum: +80 Hz para encorpar, quando era 160 Hz.'],
 '7.1.1': ['[M] Gate: fecha abaixo do threshold. Ligue antes de ajustar.',
           '[C] Expansor: abaixa aos poucos; EXP 2:1 na voz falada.',
           '[M] Ducker: abaixa um sinal quando outro aparece.',
           '[C] Key filter: o bumbo abre com o "tum", não com o prato; nunca na voz.',
           '[C] Range de ~9 dB na fala: abaixa sem picotar.'],
 '7.2.2': ['[C] Uso principal: bateria, contra o vazamento entre tambores.',
           '[C] "Ajuste o threshold, não o baterista".',
           '[C] Gate forte corta finais de nota e as ghost notes da caixa.',
           '[C] Na voz, o gate costuma atrapalhar mais que ajudar.'],
})

# ---------------------------------------------------------------- caps. 08 e 09
TITLE.update({'8.1.1': 'Compressor: como funciona', '8.2.3': 'Como ajustar: pontos de partida', '8.2.4': 'Sidechain e ducking', '8.2.5': 'Compressão paralela, de bus e no Main',
              '9.1.2': 'Delay de canal', '9.1.3': 'Pan e stereo link', '9.1.5': 'Roteiro: do microfone ao PA'})
MESAS.update({'8.2.3': 'XR18, X18, XR16, XR12, MR18, MR12, X32'})
DIAG.update({'s8-1-1': 'comp'})
BULLETS.update({
 '8.1.1': ['[M] Acima do threshold, a saída sobe menos: em 4:1, 4 dB viram 1.',
           '[C] 2:1 é suave, 6:1 é forte; de 10:1 para cima, limitador.',
           '[C] Makeup no Gain do compressor, nunca no ganho de entrada.',
           '[C] Mix em 0% não comprime nada: erro comum.',
           '[C] Peak para percussão e para limitar; RMS para voz.'],
 '8.2.3': ['[C] Alvo: cerca de 6 dB de redução, partindo do preset da fonte.',
           '[C] Voz ao vivo: 2:1 a 3:1, só tirando os picos.',
           '[C] Música em geral: 3:1 a 4:1.',
           '[C] Forte demais abafa; release curto demais faz o volume "respirar".',
           '[C] Em série: o comp do canal e um do rack, cada um trabalhando pouco.'],
 '8.2.4': ['[C] Sidechain: o compressor "escuta" outro sinal.',
           '[C] Locução: key source = canal do microfone.',
           '[C] A voz fala, a música abaixa.',
           '[C] Bumbo e baixo: o bumbo abre espaço.'],
 '8.2.5': ['[C] Erro (X AIR): comp do rack em paralelo.',
           '[C] Por quê: atraso; a mix perde agudo.',
           '[C] Certo: a dinâmica do próprio subgrupo.',
           '[C] Atalho: girar o Mix do compressor do canal.',
           '[C] X32: bateria num subgrupo comprimido; no Main, ~3 dB.'],
 '9.1.2': ['[M] Home › Config: atraso por canal, com liga/desliga.',
           '[M] Não é eco: o mesmo som, só mais tarde.',
           '[C] Dois mics a distâncias diferentes: atrase o mais próximo.',
           '[C] Alinha tons com overheads e kick in com kick out.'],
 '9.1.3': ['[M] Fora do Main o que a plateia não deve ouvir: click, talkback.',
           '[M] X32/M32: LR + Mono (padrão) ou LCR, em Setup › Global.',
           '[M] Link: só ímpar com par; fader, ganho e envios iguais.',
           '[C] Na X AIR até o ganho fica comum; Link Preferences mudam isso.',
           '[C] Usos: teclado L/R, playback, saída de DJ.'],
 '9.1.5': ['[M] Antes do mic: fader baixo e 48 V conferido.',
           '[D] EQ e compressor (X32/M32) | EQ antes | compressor antes',
           '[M] No fim: Main LR e pan, fader perto de 0 dB e o Main sobe devagar.'],
})

# ---------------------------------------------------------------- cap. 10
TITLE.update({'10.1.1': 'Aux e Mix buses', '10.1.2': 'Pontos de captação', '10.1.3': 'Bus Pre-Configuration', '10.1.4': 'O processamento do bus',
              '10.2.3': 'Dois pré/pós: o do envio e o da saída'})
MESAS.update({'10.1.3': 'XR16, XR12, MR12, X32, X32 Rack, X32 Compact, X32 Producer, M32, M32R, M32C'})
BULLETS.update({
 '10.1.1': ['[M] X AIR: 6 Aux, 4 envios de FX e o Main LR.',
            '[M] X32/M32: 16 Mix buses, 6 matrizes e o Main LRC.',
            '[M] Uso: retornos de palco, subgrupos e envio aos efeitos.',
            '[M] Nas X AIR menores, nem todo bus tem saída: XR16 4, XR12 e MR12 2.'],
 '10.1.2': ['[C] Pre EQ: ganho, low cut e gate; o retorno mais seguro contra microfonia.',
            '[C] Post EQ: com o EQ do canal, sem a compressão; o padrão de fábrica.',
            '[C] Pre Fader: tudo menos o fader; o retorno não muda com o PA.',
            '[C] Post Fader: efeitos. Fader fechado, reverb fechado.',
            '[M] X32/M32: escolha por par de envios, com a opção Sub-Group.'],
 '10.1.3': ['[M] XR16: buses 5 e 6 já saem como subgrupo; XR12 e MR12: 3 a 6.',
            '[M] X32/M32: Bus Pre-Configuration escolhe como os 16 buses nascem.',
            '[D] Os 16 buses (X32/M32) | 6 pré + 6 sub + 4 pós | 4 pré + 8 sub + 4 pós',
            '[C] Os buses andam em pares: o 1 e o 2 têm o mesmo modo.',
            '[C] Trocar o modelo zera os envios: faça no início.'],
 '10.1.4': ['[M] X AIR (Aux e LR): Insert → EQ de 6 bandas → comp → fader.',
            '[M] X32 (Mix Bus): Insert → EQ → comp → matrizes.',
            '[M] GEQ: gráfico de 31 bandas.',
            '[M] TEQ: a curva real segue os sliders.',
            '[M] X32/M32: o GEQ é um efeito num slot.'],
})

# ---------------------------------------------------------------- cap. 11
TITLE.update({'11.1.1': 'Montar o retorno de um músico', '11.1.2': 'P16 e Ultranet', '11.2.2': 'EQ e GEQ no retorno', '11.2.3': 'In-ear estéreo',
              '11.2.5': 'Mais vias de retorno', '11.2.6': 'Retorno vazando no PA'})
MESAS.update({'11.2.3': 'XR18, X18, XR12, MR18, X32, X32 Compact, M32R'})
BULLETS.update({
 '11.1.1': ['[C] Três caminhos: tela Sends, knobs de Bus Send ou Sends on Faders.',
            '[M] X32/M32: Routing › Analog Out liga o Mix Bus à saída; fader do bus em 0 dB.',
            '[C] Erro clássico: esquecer a camada. Main é o PA; Bus 1 é o retorno 1.',
            '[C] Solo no bus enquanto ajusta: você ouve o que o músico ouve.',
            '[C] Peça a cada músico só o que ele precisa ouvir.'],
 '11.1.2': ['<div class="term"><b>ULTRANET:</b> 16 canais por cabo de rede até os mixers pessoais P16.</div>',
            '[M] Não existe na XR16, na XR12 nem na MR12.',
            '[M] A porta não alimenta: use o P16-D ou fontes próprias.',
            '[C] Submix da bateria num slot e o click pelo USB.',
            '[C] X32: canal estéreo num slot, via um mix bus pré-fader.'],
 '11.2.2': ['[C] Cada bus tem EQ e compressor próprios: o retorno muda, o PA não.',
            '[C] A EQ do canal vale para todos os envios dele.',
            '[C] GEQ no retorno: o caminho clássico contra microfonia.',
            '[C] X32/M32: cada GEQ ocupa um slot de efeito.',
            '[C] Evite compressor no retorno do cantor: ele canta mais alto e cansa.'],
 '11.2.3': ['[C] Estéreo = duas saídas, ímpar + par, com link no bus.',
            '[C] Depois do link, o pan é do envio; o do canal só mexe no PA.',
            '[C] Cabo balanceado até o transmissor; cuidado com beltpack desbalanceado.',
            '[C] Fone direto na Aux: um ouvido pode inverter; use amplificador de fone.',
            '[C] DCA mexendo no in-ear? Os envios estão pós-fader.'],
 '11.2.5': ['[C] Truque 1: a saída de fone vira retorno (Monitor Source = bus).',
            '[C] Envios do bus em pré-fader e o LR do bus desligado.',
            '[C] Truque 2 (XR18, MR18): envio de FX roteado a uma saída.',
            '[C] Custo: um slot de efeito por via, sem EQ nem compressor.',
            '[C] ⚠ Truque 1 na XR18: há relatos dos dois lados; teste antes do evento.'],
 '11.2.6': ['[C] Sintoma: o retorno sai no PA, mesmo com os faders lá embaixo.',
            '[C] Causa: bus de retorno ligado ao Main; apague o LR na aba Main.',
            '[C] XR16 e XR12: os subgrupos de fábrica já saem no LR.',
            '[C] Mute corta todos os envios; para tirar só do PA, tire do Main.'],
})

# ---------------------------------------------------------------- cap. 12
TITLE.update({'12.1.1': 'Telas de medidores', '12.1.2': 'RTA e espectrograma', '12.1.3': 'Afinar o PA com ruído rosa', '12.2.2': 'Primeiro, na fonte', '12.2.3': 'Ring out e o limite'})
MESAS.update({'12.1.2': 'XR18, X18, XR16, XR12, MR18, MR12, X32, X32 Compact, X32 Producer, M32, M32R, M32C',
              '12.1.3': 'XR18, X18, XR16, XR12, MR18, MR12, X32, X32 Compact, M32, M32R, M32C'})
BULLETS.update({
 '12.1.1': ['[M] X32/M32, tela METERS: só leitura.',
            '[M] Channel: entradas, gate e redução de ganho.',
            '[M] Mix Bus: buses, matrizes, Main e Mono.',
            '[M] Aux/FX: aux sends, returns e retornos de FX.',
            '[M] X AIR: tudo pré-fader, menos o Main LR.'],
 '12.1.2': ['<div class="term"><b>Microfonia:</b> o som da caixa volta ao microfone e é amplificado de novo, em ciclo.</div>',
            '[M] RTA: quanto de cada frequência há no som agora, em 100 bandas.',
            '[C] A microfonia é um pico subindo: corte só ele, com banda estreita.',
            '[C] Pré-EQ mostra a entrada; pós-EQ, o efeito da EQ.',
            '[M] Espectrograma: a microfonia vira uma linha reta no tempo.'],
 '12.1.3': ['<div class="term"><b>Ruído rosa:</b> sinal de teste com energia igual por oitava.</div>',
            '[M] Mic de medição num canal livre, como fonte do RTA.',
            '[C] Primeiro o EQ do Main, depois o gráfico.',
            '[C] Subs sozinhos primeiro; depois o L/R, cortando o boxy em 200–400 Hz.',
            '[C] Senoide em varredura lenta acha as ressonâncias da sala.'],
 '12.2.2': ['[C] Cardioide apontado para a boca, a uns 3 dedos; nunca pela cápsula.',
            '[C] Retorno atrás do microfone; PA à frente da linha dos mics.',
            '[C] Ensine o orador a falar perto do microfone.',
            '[C] Às vezes a "microfonia" é uma caixa com faixa sobrando.'],
 '12.2.3': ['[C] Monitor: mics no lugar, EQ zerada, bus em 0 dB.',
            '[C] Suba a voz devagar e olhe o RTA.',
            '[C] No apito: corte estreito de poucos dB (PEQ ou GEQ, cap. 10).',
            '[C] Até 3–4 passadas: EQ demais tira a vida do retorno.',
            '[C] PA: só as vozes abertas, master devagar, RTA no LR.'],
})

# ---------------------------------------------------------------- cap. 13
TITLE.update({'13.1.1': 'Envio × insert', '13.1.2': 'Passo a passo: reverb por envio e insert', '13.1.4': 'O rack e a biblioteca', '13.2.6': 'Planos de rack'})
MESAS.update({'13.2.6': 'XR18, X18, XR16, XR12, MR18, MR12, X32, X32 Rack, X32 Compact, X32 Producer, M32, M32R, M32C'})
DIAG.update({'s13-1-2': 'fxhow'})
BULLETS.update({
 '13.1.1': ['[C] Tempo (reverb, delay, chorus) por envio: vários canais, um efeito.',
            '[C] Processadores (comp, EQ, de-esser) em insert, no caminho do canal.',
            '[M] X AIR: 4 slots estéreo, qualquer um por envio ou insert.',
            '[M] X32/M32: 8 slots; reverbs nos 1–4, e os 5–8 só em insert.',
            '[M] Dual: dois efeitos mono no mesmo slot, um em cada canal.'],
 '13.1.2': ['[C] O reverb precisa de 4 coisas: envio, master do bus, retorno e nada mutado.',
            '[C] X AIR: "OFF" sob o slot é o insert desligado, o certo para reverb.',
            '[C] Erro comum: retorno do FX fechado no LR; o efeito "não funciona".',
            '[M] Insert na X32: Home › Config, encoder 6; ligue no rack e no canal.',
            '[M] Aparelho externo em insert: Aux Out → aparelho → Aux In.'],
 '13.1.4': ['[M] A mesma biblioteca de 60 ou mais efeitos nas duas famílias.',
            '[M] X32 Rack e X32 Producer: os manuais antigos listam 39.',
            '[C] De fábrica na X32: Vintage Room, Hall e Stereo Delay.',
            '[C] Trocar o tipo: toque longo no slot, no app de tablet.',
            '[C] Estude um algoritmo por vez, ouvindo com e sem o efeito.'],
 '13.2.6': ['[D] Quatro slots | por fonte: bateria, voz, utilitário, delay | por tamanho: longo, curto, delay',
            '[C] Não há plano único: depende do repertório e dos slots livres.',
            '[C] Voz: ~1,5 s de decaimento como base, com pré-delay.',
            '[C] Reverb no retorno: suba o FX return no bus do monitor.',
            '[C] Retorno de FX no próprio envio cria um laço que parece microfonia.'],
})

# ---------------------------------------------------------------- caps. 14 e 15
TITLE.update({'14.1.1': 'DCA', '14.1.2': 'Mute groups', '14.2.2': 'Subgrupo',
              '15.1.1': 'Matrizes', '15.2.2': 'Crossover nas matrizes', '15.2.3': 'Subwoofer pelo auxiliar', '15.2.4': 'Alinhar caixas no tempo'})
MESAS.update({'15.2.4': 'XR18, X18, XR16, XR12, MR18, X32, X32 Rack, X32 Compact, X32 Producer, M32, M32C'})
BULLETS.update({
 '14.1.1': ['[M] Um fader comanda o volume de vários canais sem somar o áudio.',
            '[M] 4 DCAs nas X AIR; 8 na X32/M32.',
            '[C] Move o DCA e a mistura fica; não gasta bus.',
            '[D] Canais nos DCAs | um por família | dois: família e banda toda',
            '[C] O medidor do DCA é estimativa, não a soma real.'],
 '14.1.2': ['[M] Um botão silencia de uma vez todos os canais do grupo.',
            '[M] 4 grupos nas X AIR; 6 na X32/M32.',
            '[C] Típicos: a bateria, os mics de fala, as entradas do DJ.',
            '[M] X32/M32: MUTE GRP ligado, segure o grupo e aperte Select.',
            '[C] Soft mute: ao soltar o grupo, o canal mutado sozinho volta junto.'],
 '15.1.1': ['[M] A matriz mistura buses, não canais: o Main e os Mix Bus 1–16.',
            '[M] 6 matrizes, com insert, EQ de 6 bandas e compressor.',
            '[M] Zonas: torre de delay, lobby, outra sala, gravação.',
            '[C] Volume do PA pela matriz, com o LR fixo em 0.',
            '[C] "Não sai som na saída"? Aponte a saída à matriz no Routing.'],
 '15.2.2': ['<div class="term"><b>Crossover:</b> divide o sinal, graves para o sub e o resto para os topos.</div>',
            '[C] Ligue o EQ da matriz, senão os filtros não atuam.',
            '[C] Topos com passa-altas LR24 em ~100 Hz; sub com passa-baixas igual.',
            '[M] Exemplo do fabricante: topos e subs em estéreo, cortes LR24 em 80 Hz.',
            '[C] X AIR: o crossover fica na caixa ativa ou no processador.'],
 '15.2.3': ['<div class="term"><b>Aux-fed sub:</b> o sub ganha um bus próprio; você escolhe quem manda grave.</div>',
            '[C] Ao sub só o que tem grave útil: bumbo, baixo, teclado.',
            '[C] XR18: Aux 6 no sub, envios pós-fader, bus igual ao LR.',
            '[C] Corte em ~100 Hz, na caixa ou no processador.',
            '[C] M32C: sub pelo Mono/Center, com "mono follows main".'],
 '15.2.4': ['[M] X32/M32: Routing › Analog Out, encoder 6, em ms, metros ou pés.',
            '[M] O som anda ~343 m/s: 2,9 ms por metro; 20 m ≈ 58 ms.',
            '[C] Saídas Ultranet não têm delay; mesmo sinal sem delay dá fase.',
            '[C] X AIR: Stereo Delay em insert, Mix 100%, gastando um slot.',
            '[C] Alinhe sempre o fundo à frente, nunca uma caixa atrasada à outra.'],
})

# ---------------------------------------------------------------- caps. 16 e 17
TITLE.update({'16.1.1': 'X AIR: snapshots e cenas', '16.1.2': 'X32/M32: cena, snippet e cue', '16.1.3': 'Safes', '16.2.3': 'Cena zero e backup',
              '17.1.1': 'Solo: só o técnico ouve', '17.1.2': 'O fone do técnico', '17.1.4': 'Talkback', '17.1.5': 'Oscilador'})
MESAS.update({'16.2.3': 'XR18, X18, XR16, XR12, MR18, MR12, X32, X32 Rack, X32 Compact, X32 Producer, M32, M32R, M32C',
              '17.1.4': 'XR18, X18, XR16, XR12, MR18, MR12, X32, X32 Rack, X32 Compact, X32 Producer, M32, M32R, M32C'})
BULLETS.update({
 '16.1.1': ['[M] Snapshot: a foto da mesa inteira, guardada nela, em 64 posições.',
            '[C] Cena: arquivo .scn no computador, para backup ou outra mesa.',
            '[M] Recall filtrado: na hora de carregar, escolha o que volta.',
            '[C] Snapshot como "desfazer": recarregue o último bom.',
            '[C] Um snapshot por local ou tipo de evento acelera a montagem.'],
 '16.1.2': ['[M] Cena: a mesa inteira, inclusive o ganho dos pré-amps; até 100.',
            '[M] Snippet: só uma parte, como 9 canais de bateria + DCA + efeitos.',
            '[M] Cue list: até 500 eventos com botão GO, para teatro e roteiro.',
            '[M] Salvar no View de Scenes; chamar com GO (X32) ou NOW (M32).',
            '[M] Scene Undo: volta ao estado de antes da cena chamada.'],
 '16.1.3': ['[M] Safe: "cadeado" contra a troca de cena.',
            '[M] Recall Safe: roteamento, ganho, efeitos.',
            '[M] Parameter Safe: grupos de ajustes.',
            '[M] Channel Safe: canais inteiros.',
            '[C] O clássico: proteger o ganho dos pré-amps.'],
 '16.2.3': ['[C] Exporte o show para o pendrive, sempre antes de firmware ou reset.',
            '[C] Um snapshot "padrão" de emergência, para quando alguém mexer.',
            '[C] Cena 0 própria: User In/Out preenchidos, no lugar do Initialize.',
            '[C] Ferramentas gratuitas de computador salvam cenas e shows.'],
 '17.1.1': ['[M] Solo manda o canal ao fone do técnico; PA e retornos não mudam.',
            '[C] PFL na passagem de som (ouve com o fader baixo); AFL no show.',
            '[M] Clear Solo limpa todos, até os de camadas fora da tela.',
            '[C] Ligue "Select follows Solo" e o PFL dim.',
            '[M] X AIR: Setup › Monitor. X32/M32: Monitor › Solo Options.'],
 '17.1.2': ['[M] Fonte do monitor: o que toca no fone quando nada está em solo.',
            '[M] Dim abaixa a escuta (−40 a 0 dB na X32/M32).',
            '[M] Mono confere a mix como num "radinho".',
            '[M] X32/M32: delay da escuta alinha o fone com o som da sala.',
            '[M] M32C: sem saída de fone; a escuta sai nos Monitoring Outputs.'],
 '17.1.4': ['[M] Microfone do técnico para os retornos, sem passar pelo PA.',
            '[C] Talk A para o técnico de monitor; Talk B para a banda.',
            '[M] Auto-dim abaixa a escuta enquanto você fala.',
            '[C] M32R: o XLR de talkback já vem com 48 V ligado.',
            '[C] X AIR: um microfone num canal fora do Main faz o papel.'],
 '17.1.5': ['[M] Tipos: senoide, ruído rosa e ruído branco.',
            '[C] Escolha destino e tipo, suba o bus e aperte Generate.',
            '[C] Usos: afinar a sala com o RTA, testar caixas, achar vias.',
            '[C] ⚠ Enquanto toca, o resto daquele destino fica mudo.'],
})

# ---------------------------------------------------------------- caps. 18 e 19
TITLE.update({'18.1.1': 'Automix', '19.2.1': 'Quem grava o quê', '19.2.3': 'Multipista no DAW', '19.2.5': 'Virtual soundcheck', '19.1.3': 'Pendrive: gravar e tocar',
              '19.1.4': 'Cartão SD (LIVE)', '19.2.10': 'Mix separada para a live', '19.2.11': 'Matriz só para o stream'})
MESAS.update({'18.1.1': 'XR18, X18, XR16, XR12, MR18, MR12, X32, X32 Rack, X32 Compact, X32 Producer, M32',
              '19.2.3': 'XR18, X18, MR18, X32, X32 Rack, X32 Compact, X32 Producer, M32, M32R, M32C',
              '19.1.3': 'XR16, XR12, MR12, X32, X32 Rack, X32 Compact, X32 Producer, M32, M32R, M32C', '19.1.4': 'M32, M32R, M32C',
              '19.2.10': 'XR18, X18, XR12, MR18, X32, X32 Compact'})
BULLETS.update({
 '18.1.1': ['[M] O mic de quem fala recebe o ganho que os parados liberam.',
            '[M] Dois grupos, X e Y; o medidor azul mostra quanto cada canal abaixa.',
            '[M] Weight dá prioridade; Last Gate mantém o último mic aberto.',
            '[C] X32/M32: do firmware 3 em diante, só nos canais 1–8.',
            '[C] Para fala: palestra, debate, painel. Não para banda.'],
 '19.2.1': ['<div class="term"><b>Multipista:</b> cada canal num arquivo, para remixar depois.</div>',
            '[M] XR18, X18, MR18: interface USB 18 × 18; não gravam sozinhas.',
            '[M] XR16, XR12, MR12: só estéreo em pendrive; não são interface.',
            '[M] X32/M32: pendrive e placa 32 × 32; SD nas LIVE e com a X-Live.',
            '[C] Mac sem driver, Windows com ASIO; 48 kHz na mesa e no DAW.'],
 '19.2.3': ['[C] X AIR: USB Sends em Analog, o sinal cru logo após o pré.',
            '[C] X32/M32: USB na placa e Setup › Card em 32 in / 32 out.',
            '[C] Card Out igual à fonte de entrada, em blocos de 8.',
            '[C] Reaper: ASIO, 48 kHz, buffer 256, uma pista mono por canal.',
            '[C] Pistas fora do master do DAW; salve como modelo.'],
 '19.2.5': ['[C] Grave o show ou o ensaio em multipista (USB Sends em Analog).',
            '[C] Em In/Out › USB Returns, ligue USB 1 → canal 1 … 16 → 16.',
            '[C] Fonte do canal em USB; o nível vai no USB trim, não no ganho.',
            '[C] Ao terminar, volte todos os canais para analógico.'],
 '19.1.3': ['[M] XR16, XR12 e X32: pendrive FAT32, WAV estéreo de até 2 GB.',
            '[C] X32: o tap padrão é Pre EQ; para levar o EQ do Main, Post EQ.',
            '[M] Tire o pendrive só com o LED de acesso apagado.',
            '[C] Tocar: só WAV, na taxa da mesa; MP3 e AIFF não tocam.',
            '[C] Música do intervalo: pendrive, ou notebook pelo USB na técnica.'],
 '19.1.4': ['[M] 2 slots SD/SDHC, FAT32, de 1 a 32 GB cada.',
            '[M] WAV de 32, 16 ou 8 canais, sem computador.',
            '[M] Bateria CR123A protege a gravação numa queda de energia.',
            '[C] Os cartões não vêm com a mesa; 128 GB está fora do suportado.',
            '[C] M32C: vem com a DN32-USB, sem os slots SD.'],
 '19.2.10': ['[C] O Main direto na live: "música alta, pregação baixa".',
             '[C] Um bus livre chamado LIVE, com o LR desligado.',
             '[D] Envio da live | pós-fader: segue o PA | pré-fader: independente',
             '[C] USB Sends leva o bus ao OBS ou vMix; suba o master do bus.',
             '[C] Atalho: o bus em Sub group segue os faders do LR.'],
 '19.2.11': ['[C] Matriz só para o stream, a partir do Main, com EQ e comp próprios.',
             '[C] Mics de plateia num bus que entra só na matriz da live.',
             '[C] Precision Limiter na matriz; alvo de ~−16 LUFS.',
             '[C] 30 canais + 2 da mix da live na mesma gravação (User Out).'],
})

# ---------------------------------------------------------------- cap. 20
TITLE.update({'20.1.1': 'AES50: um cabo no lugar do multicabo', '20.1.2': 'Split FOH/monitor', '20.2.2': 'Ligar stagebox e clock', '20.2.4': 'User In/Out',
              '20.2.6': 'XR18 e MR18: split pelo DN4816-O'})
MESAS.update({'20.1.2': 'X32, X32 Rack, X32 Compact, X32 Producer, M32, M32R, M32C'})
BULLETS.update({
 '20.1.1': ['[M] 2 portas, A e B, com 48 × 48 canais cada.',
            '[M] Stageboxes: Behringer S16, Midas DL16 e DL32.',
            '[M] Cabo Cat5e blindado com etherCON, até 100 m.',
            '[C] Malha ligada nas duas pontas; o etherCON trava contra puxão.',
            '[D] Cat6 na AES50 | blindado, como alternativa | evitar: relatos de perda de sync'],
 '20.1.2': ['[M] Sem splitter analógico: o sinal digital é copiado pelo cabo.',
            '[M] Com S16: a mesa de palco recebe pela A e repassa à PA pela B.',
            '[M] Com DL32: FOH A → DL32 A; DL32 B → monitor.',
            '[M] Uma mesa só controla os ganhos; ou HA Gain Split.',
            '[C] Sem stagebox: duas mesas ligadas direto pela AES50.'],
 '20.2.2': ['[C] A da mesa → A da stagebox; para encadear, B da 1ª → A da 2ª.',
            '[C] Na stagebox, a porta A recebe o clock; a B é de passagem.',
            '[C] Um só mestre de clock: em geral a mesa, em Sync = Internal.',
            '[C] LED verde fixo: tudo certo; piscando ou vermelho: cabo ou clock.',
            '[M] Setup › Preamps: ganho e phantom de cada pré remoto.'],
 '20.2.4': ['[C] User In/Out (firmware 4): cada canal escolhe entre 168 fontes.',
            '[C] Ex.: 4 canais da stagebox, o click da placa e o talkback num bloco.',
            '[C] Vêm vazios: mudar para "User" sem preencher = sem áudio.',
            '[C] Para engenheiro convidado: preset de roteamento na Library.',
            '[C] M32C: o som sai pelas XLR da stagebox; master mudo? Roteamento.'],
 '20.2.6': ['[C] DN4816-O: converte a Ultranet em 16 saídas analógicas.',
            '[C] Split digital das 16 entradas para a mesa da casa.',
            '[C] A XR18 (ou a MR18) fica só com os in-ears da banda.',
            '[C] O ganho da XR18 vale para a casa: clipou aqui, clipou lá.'],
})

# ---------------------------------------------------------------- caps. 21 e 22
TITLE.update({'21.1.1': 'MIDI nas X AIR', '21.1.2': 'Trocar cenas por MIDI (X32/M32)', '21.1.4': 'A mesa como controlador', '21.1.6': 'Taxa, clock e o menu Setup',
              '22.1.1': 'Atualizar o firmware', '22.1.3': 'Cuidados: calor, poeira e energia'})
DIAG.update({'s22-1-3': 'bespoke:s22-2-3'})
BULLETS.update({
 '21.1.1': ['<div class="term"><b>MIDI:</b> língua de comandos entre equipamentos; não leva áudio.</div>',
            '[M] Canal 1: Program Change 1–64 chama os snapshots.',
            '[M] Canal 1: CC 0–15 nos faders 1–16, CC 21–26 nos Aux, CC 31 no Main.',
            '[M] Canal 2: mutes (127 = mudo). Canal 3: pan (64 = centro).',
            '[M] X-Touch ou qualquer controlador MIDI/Mackie Control.'],
 '21.1.2': ['[M] X32/M32: Program Change 1–100 no canal MIDI 1 carrega a cena.',
            '[M] Setup › Remote: entrada MIDI ligada e Enable MIDI Scene Recall.',
            '[M] Com o pop-up de confirmação ligado, cada troca espera um toque.',
            '[M] M32: snippets no canal 2, cues nos canais 3 a 6, faders em CC 0–79.',
            '[M] Cada cena também manda um comando: troque a luz junto.'],
 '21.1.4': ['[M] Assign: botões e knobs programáveis, em 3 bancos (A, B, C).',
            '[M] Uso típico: um knob fixo no envio de reverb da voz.',
            '[M] Em MIDI, cada controle manda CC, Program Change ou Note.',
            '[M] DAW Remote: HUI e Mackie Control, em bancos de 8 faixas.',
            '[M] A placa X-USB emula HUI/Mackie pela própria USB.'],
 '21.1.6': ['[M] 44,1 kHz para áudio puro; 48 kHz quando há vídeo.',
            '[M] X AIR: Setup › Audio/MIDI; mute o Main antes de trocar a taxa.',
            '[M] X32/M32: Setup › Config; trocar a taxa exige reiniciar.',
            '[M] Clock: a letra no topo da tela diz a fonte (L, A/B, C).',
            '[M] Global: pop-ups de confirmação, modo de pan e brilho.'],
 '22.1.1': ['[M] Backup de shows e cenas antes; nunca no dia do evento.',
            '[C] Só do site oficial; o firmware (ex.: 1.17) não é a versão do app.',
            '[M] X AIR: X AIR Edit › Setup › Connect; a mesa reinicia sozinha.',
            '[C] X32/M32: pendrive FAT32 com o dcp_*.update na raiz, botão ao ligar.',
            '[M] Travou sem arquivo válido: religue sem segurar o botão.'],
 '22.1.3': ['[C] XR16 e XR12 não têm ventoinha: nunca ligadas dentro da bolsa.',
            '[M] Aberturas livres e espaço no case; opera de 5 a 40 °C.',
            '[M] Não abra: manutenção só com técnico qualificado.',
            '[C] Faders motorizados sujos travam: capa contra poeira.',
            '[C] Energia ruim já queimou mesa: use protetor contra surto.'],
})

# ---------------------------------------------------------------- cap. 23
TITLE.update({'23.2.1': 'Duas ordens para montar a mix', '23.2.2': 'Igreja com voluntários', '23.2.4': 'Checklist do dia do evento'})
MESAS.update({'23.2.1': 'MR18, X32, X32 Compact, M32C'})
DIAG.update({'s23-2-4': 'day3'})
BULLETS.update({
 '23.2.1': ['[C] Antes do show: estude o rider e o repertório.',
            '[D] Por onde começar | voz primeiro | base primeiro | só faders',
            '[D] Por onde começar | voz primeiro | base primeiro | só faders',
            '[C] Antes do show: estude o rider e o repertório.'],
 '23.2.2': ['[C] Implantação por semanas: cabo, primeira cena, backup.',
            '[C] Na mão do voluntário, poucos faders: DCAs por grupo.',
            '[C] Treino curto, com o culto gravado e virtual soundcheck.',
            '[C] Exemplo: mute no DCA, in-ear por mix bus, pregação no pendrive.'],
 '23.2.4': ['[M] Mute o canal antes de ligar ou desligar o 48 V.',
            '[M] Click e talkback fora do Main.',
            '[M] X32/M32: reverbs nos slots 1–4, inserts nos 5–8.',
            '[M] Trocar a taxa: Main mudo (X AIR) ou reiniciar (X32/M32).',
            '[M] Palestra com vários mics: automix com Last Gate.'],
})

# ---------------------------------------------------------------- cap. 24
TITLE.update({'24.2.1': 'Os erros que derrubam um show'})
BULLETS.update({
 '24.2.1': ['[C] Wi-Fi interno em show cheio → roteador externo e um aparelho no cabo.',
            '[C] "PC → Mixer" sem querer → sempre Mixer → PC.',
            '[C] RESET de 10 s para consertar a rede → 2 s.',
            '[C] Mixar no ganho durante o show → ganho fixo, mix no fader.',
            '[C] Subgrupo com os canais ainda no Main → tire-os do Main.'],
})

# ---------------------------------------------------------------- caps. 25 a 27
TITLE.update({'25.1.1': 'As duas famílias em números', '26.1.1': 'Manuais oficiais de referência', '26.2.1': 'Para ir além deste curso',
              '27.1.1': 'Glossário'})
MESAS.update({'25.1.1': 'XR18, X18, XR16, XR12, MR18, MR12, X32, X32 Rack, X32 Compact, X32 Producer, M32, M32R, M32C',
              '26.2.3': 'XR18, X18, XR16, XR12, MR18, MR12, X32, X32 Rack, X32 Compact, M32, M32R, M32C',
              '26.2.6': 'XR18, X18, XR16, XR12, MR18, MR12, X32, X32 Rack, X32 Compact, X32 Producer, M32, M32R, M32C'})
DIAG.update({'s26-1-1': 'mantime'})
BULLETS.update({
 '25.1.1': ['[M] Faixa dinâmica: XR 104–106 dB, MR 108, X32 e M32 106.',
            '[M] Ruído do pré (EIN): XR e X32 −128 dBu; MR e M32 −125 dBu.',
            '[M] Conversores de 24 bits; o D/A da M32 chega a 120 dB.',
            '[M] Máximo no XLR: +23 dBu (nas MR, +23,5).',
            '[M] Wi-Fi 2,4 GHz só nas X AIR; todas operam de 5 a 40 °C.'],
 '26.1.1': ['[M] X AIR: um manual só para XR18, X18, XR16 e XR12 (2016).',
            '[M] M AIR: MR18 e MR12 (2016). X32 e Compact: 2016.',
            '[M] X32 Rack (2014) e X32 Producer (2013): os mais antigos.',
            '[M] M32 (2018); M32C sem manual completo próprio.',
            '[M] Os da X32/M32 reaproveitam texto do console grande.'],
})

# ---------------------------------------------------------------- ajustes de layout: versões curtas onde o corpo pedia slide de continuação
BULLETS.update({
 '5.2.1': ['<div class="term"><b>Gain staging:</b> o nível certo em cada etapa.</div>',
           '[C] Média perto de −18 dBFS; picos 3 a 6 dB acima.',
           '[C] Acima de 0 dBFS, só distorção: a folga é o headroom.',
           '[C] Canais iguais: presets de gate e comp funcionam.',
           '[C] Com ganho moderado, o pré soa mais limpo.'],
 '13.1.2': ['[C] O reverb soa com envio, master do bus e retorno abertos.',
            '[C] X AIR: "OFF" sob o slot é o insert desligado.',
            '[C] Retorno do FX fechado no LR: "o efeito não funciona".',
            '[M] Insert na X32: Home › Config, encoder 6.',
            '[M] Aparelho externo: Aux Out → aparelho → Aux In.'],
 '24.2.1': ['[C] Wi-Fi interno no show → roteador externo.',
            '[C] "PC → Mixer" sem querer → Mixer → PC.',
            '[C] RESET de 10 s para a rede → 2 s.',
            '[C] Mixar no ganho → ganho fixo.',
            '[C] Subgrupo com canais no Main → tire do Main.'],
 '25.1.1': ['[M] Faixa dinâmica: XR até 106 dB, MR 108, X32 e M32 106.',
            '[M] EIN: XR e X32 −128 dBu; MR e M32 −125.',
            '[M] D/A de 120 dB na M32; 114 a 115 nas outras.',
            '[M] Máximo no XLR: +23 dBu (nas MR, +23,5).',
            '[M] Wi-Fi só nas X AIR; todas de 5 a 40 °C.'],
})
BULLETS.update({
 '24.2.1': ['[C] Cabo de rede na porta Ultranet → porta Ethernet.',
            '[C] Retorno pós-fader → pré-fader.',
            '[C] Efeito pré-fader → pós-fader.',
            '[C] Bus de retorno ligado ao LR → LR do bus apagado.',
            '[C] Phantom com o canal aberto → mute antes.'],
})
BULLETS.update({
 '26.1.1': ['[M] X AIR: um manual só para XR18, X18, XR16 e XR12.',
            '[M] M32C: sem manual completo; vale o guia rápido + o manual da M32.',
            '[M] Rack e Producer listam 39 efeitos; os manuais de 2016, 60.',
            '[M] Os da X32/M32 reaproveitam texto do console grande.'],
})
BULLETS.update({
 '14.2.2': ['[C] X AIR: em Sends, com o globo aceso, o bus vira Subgroup.',
            '[C] Ligue os canais ao subgrupo.',
            '[C] No bus, aba Main: LR ligado.',
            '[C] Nos canais: LR desligado, senão o som sai em dobro.'],
})

# ---------------------------------------------------------------- rodada 5 (revisão de redundância): cada ideia num lugar só; o diagrama mostra a relação, o bullet traz o que o desenho não mostra
TITLE.update({'3.1.3': 'X32/M32: sem Wi-Fi, rede só por cabo', '3.2.8': 'Travas: senha e bloqueio', '4.2.1': 'Apps: quem usa qual', '4.2.11': 'Prepare o show antes do ensaio',
              '7.1.1': 'Threshold, range e key filter', '13.1.2': 'O efeito não soa? Três conferências', '16.1.1': 'Cenas nas duas famílias', '18.1.1': 'Grupos X/Y, Weight e Last Gate',
              '19.2.10': 'Mix própria para a live', '20.1.1': 'AES50: portas, cabo e stageboxes', '21.1.1': 'Mapa MIDI das duas famílias', '23.2.4': 'Checklist do dia do evento',
              '25.1.1': 'Fichas lado a lado'})
MESAS.update({'3.2.4': 'XR18, X18, XR16, XR12, MR18, MR12, X32, X32 Rack, X32 Compact, X32 Producer, M32, M32R, M32C',
              '4.2.1': 'XR18, X18, XR16, XR12, MR18, MR12, X32, X32 Rack, X32 Compact, X32 Producer, M32, M32R, M32C',
              '16.1.1': 'XR18, X18, XR16, XR12, MR18, MR12, X32, X32 Rack, X32 Compact, X32 Producer, M32, M32R, M32C',
              '19.2.10': 'XR18, X18, XR16, XR12, MR18, MR12, X32, X32 Rack, X32 Compact, X32 Producer, M32, M32R, M32C',
              '21.1.1': 'XR18, X18, XR16, XR12, MR18, MR12, X32, X32 Rack, X32 Compact, X32 Producer, M32, M32R, M32C',
              '26.2.3': 'XR18, X18, XR16, XR12, MR18, MR12, X32, X32 Rack, X32 Compact, X32 Producer, M32, M32R, M32C'})
DIAG.update({'s16-1-1': 'scenes2', 's21-1-1': 'midimap2', 's26-2-2': 'paidcourses', 's26-2-3': 'freeseries', 's26-2-6': 'readpicks'})
BULLETS.update({
 '1.1.2': ['[M] Gêmeas: mesmo software e processamento; muda o logotipo.',
           '[C] Nas MR: pré-amps MIDAS PRO e conectores Neutrik com trava.',
           '[C] Mesmo app com outro nome: M AIR Edit.',
           '[C] Cenas da XR18 abrem na MR18 sem ajuste.'],
 '1.1.3': ['[M] Sem faders: tudo pelo app, no tablet, celular ou computador.',
           '[C] Se o app cai, o som continua: a mesa guarda o último estado.',
           '[C] Fica no palco, como stagebox: nada de multicabo até a técnica.',
           '[M] Motor igual nas seis: 16 + 1 estéreo, 6 Aux, 4 FX, 4 DCA, até na XR12.',
           '[C] X18: a XR18 em formato de mesa, só com o volume do fone.'],
 '1.1.4': ['[M] Motor comum a X32 e M32: 40 entradas, 25 buses, 8 FX, 8 DCA.',
           '[M] 100 cenas e placa de expansão 32 × 32.',
           '[C] M32 × M32 LIVE: só muda a placa (a LIVE grava em SD).',
           '[C] M32R LIVE, de 2018, é a versão atual da M32R.',
           '[C] M32C: uma M32 inteira em 1U; todo o áudio vai por AES50.'],
 '1.1.7': ['[M] Só na X32/M32: crossover, delay de saída, LCR, oscilador e AES50.',
           '[C] Entre as famílias, só ligação analógica: Ultranet não é AES50.',
           '[C] Ex.: saídas da X32 numa MR18 para mixar a live.'],
 '1.2.10': ['[C] Garantia (XR12, M32C): registrada em 90 dias, vai de 1 para 3 anos.',
            '[C] Leve uma caixa ativa e teste cada entrada, saída, fone, rede e USB.',
            '[C] Muito "defeito" é roteamento: peça ao vendedor para mostrar o patch.',
            '[C] Antes do primeiro uso: reset completo (cap. 2).'],
 '2.1.1': ['[M] Em todas: Ethernet, REMOTE, RESET, MIDI, Main em XLR e fone.',
           '[M] USB: tipo B nas de 18 canais; tipo A (pendrive) na XR16 e XR12.',
           '[M] Ultranet para P16: só XR18, X18 e MR18.',
           '[M] Aux: 6 XLR, 6 P10 na X18, 4 XLR na XR16, 2 P10 na XR12.',
           '[C] X18: 17/18 em RCA e saída Control Room; as duas têm 6 Aux.'],
 '2.1.7': ['[M] O transiente da mesa ligando só vira "tum" se o PA já estiver ligado.',
           '[M] X AIR: Mute at Power On e Safe Levels mutam as saídas no boot.',
           '[M] X32: Safe Main Levels abaixa o Main e segura a cena.',
           '[M] Safe Shutdown (X32): espera a mesa terminar de gravar o estado.'],
 '2.1.8': ['[M] X AIR: o tempo segurando o RESET decide o que volta.',
           '[C] ⚠ Erro comum: segurar 10 s para resolver a conexão apaga tudo.',
           '[M] X32: Scenes/Undo no boot, ou Setup › Config › Initialize.',
           '[M] Shows e cenas só saem com a opção Show Data.',
           '[C] M32C: o painel faz DHCP, IP, lock e cena sem app.'],
 '3.1.1': ['[M] Chave REMOTE: escolhe o modo; os ajustes ficam em Setup › Network.',
           '[C] Ethernet: show e local grande; o modo mais confiável.',
           '[C] Wi-Fi Client: quando o local já tem roteador.',
           '[C] Access Point: ensaio e sala pequena, até 4 aparelhos.'],
 '3.1.2': ['[M] Android: ligue o Wi-Fi Lock, que prende o aparelho na rede da mesa.',
           '[M] iPad: a mesa aparece em Devices; toque no ícone.',
           '[M] Sincronizar: Mixer → PC traz a mesa; PC → Mixer apaga o show dela.',
           '[M] Rede da mesa: modelo + final do MAC (ex.: XR18-17-BE-C0).'],
 '3.1.3': ['[M] X32/M32, SETUP › Network: encoder 1 escolhe, 2 a 5 ajustam, 6 confirma.',
           '[C] Cerca de 10 controles remotos ao mesmo tempo.',
           '[C] M32C: ligue o DHCP no SELECT, senão o tablet não acha a mesa.'],
 '3.2.1': ['[C] Só o cabo USB: o app não acha a mesa.',
           '[C] Notebook que controla e toca música: rede + USB.',
           '[C] X18 e MR18: rede na porta Ultranet faz a mesa "sumir".',
           '[C] X32: para gravar, o USB vai na placa, não no de controle.'],
 '3.2.4': ['[C] Wi-Fi interno (X AIR): só 2,4 GHz; cai quando o público chega.',
           '[C] Roteador dual band; tablets em 5 GHz com WPA2.',
           '[C] Mesa na porta LAN, nunca na WAN; na X AIR, REMOTE em Ethernet.',
           '[C] Mesa com IP fixo alto; o resto por DHCP.',
           '[C] Local cheio: SSID oculto; teste andando, com o salão cheio.'],
 '3.2.8': ['[C] Access Point vem aberto: ponha senha, mesmo sendo só WEP.',
           '[M] A porta Ethernet não pede senha: quem entra na rede mexe na mesa.',
           '[M] Lock Console (X32): trava a superfície; HOME destrava.',
           '[M] M32C: a trava é pelo botão SELECT.'],
 '4.2.1': ['[M] Computador: X AIR Edit, M AIR Edit, X32-Edit e M32-Edit.',
           '[C] Técnico: notebook no cabo, o mais rápido na emergência.',
           '[C] Músico: MX-Q no celular, só com o bus dele; nunca o app completo.',
           '[C] Os apps antigos de tablet não rodam em sistemas de 2022 em diante.',
           '[C] Teste o MX-Mix antes do show: as versões mudam rápido.'],
 '4.2.2': ['[C] Abas na ordem do sinal: Input, Gate, EQ, Comp, Sends.',
           '[C] Selecione pelo número do canal, nunca pelo meio da faixa.',
           '[M] Preferences: Exclusive solo, fader Fine e Auto Select.',
           '[M] Utilities: janelas extras de RTA, Buses, DCA e medidores.'],
 '4.1.2': ['[M] View (X32 e M32): cada seção leva a tela direto à sua página.',
           '[M] Select: sempre há um canal selecionado; DCA não é canal.',
           '[M] Anel de LED apagado: o parâmetro não existe naquele canal.',
           '[C] "No máximo dois toques": bloco → View → aba.'],
 '4.1.3': ['[M] Os faders montam a mix de um bus: em geral, um retorno.',
           '[M] X AIR / M AIR: escolha o Aux ou o FX no Fader Bank.',
           '[M] X32/M32: só Mix Bus 1–16, não DCA, Main ou Matrix.',
           '[M] Com um canal selecionado, mostra para onde ele vai.',
           '[C] X32-Edit: janela Mixer e "mix to" levam os faders a um bus.'],
 '4.2.11': ['[C] Offline: monte o show em casa, numa cena-modelo.',
            '[C] Nome e cor por família de instrumento e por efeito.',
            '[C] Patch 1:1: mude o cabo, não o roteamento.',
            '[M] Copiar canal leva gate, EQ, comp e envios; o ganho não vai.',
            '[M] Library (X32): presets de canal, efeito e roteamento.'],
 '5.2.3': ['[C] Peça o nível de show, não o de ensaio.',
           '[C] X32: Select + View: medidor grande.',
           '[C] Partida: voz 25–30 dB, condensador 25–35.',
           '[C] Teste as saídas antes.',
           '[C] Ajuste uma vez; só volte se estourar.'],
 '7.1.1': ['[M] Gate: fecha abaixo do threshold; ligue antes de ajustar.',
           '[C] "Ajuste o threshold, não o baterista".',
           '[C] Na voz, expansor: EXP 2:1, range ~9 dB.',
           '[C] Key filter: o bumbo abre com o "tum", não com o prato.',
           '[M] Ducker: um canal abaixa quando outro toca (cap. 8).'],
 '8.2.4': ['[C] Sidechain: o compressor "escuta" outro sinal.',
           '[C] Locução: key source = canal do microfone.',
           '[C] Bumbo e baixo: o bumbo abre espaço.'],
 '10.1.1': ['[M] X AIR: 6 Aux, 4 envios de FX e o Main LR.',
            '[M] X32/M32: 16 Mix buses, 6 matrizes e o Main LRC.',
            '[M] Uso: retornos de palco, subgrupos e envio aos efeitos.'],
 '10.1.2': ['[C] Pre EQ: ganho, low cut e gate; o retorno mais seguro contra microfonia.',
            '[C] Post EQ: com o EQ do canal, sem a compressão; padrão nos Aux da X AIR.',
            '[C] Pre Fader: tudo menos o fader; o retorno não muda com o PA.',
            '[C] Post Fader: efeitos. Fader fechado, reverb fechado.',
            '[M] X32/M32: escolha por par de envios, com a opção Sub-Group.'],
 '11.2.2': ['[C] A EQ do canal vale para todos os envios; a do bus, só para aquele retorno.',
            '[C] GEQ no retorno: o caminho clássico contra microfonia (na X32/M32, um slot; cap. 13).',
            '[C] Evite compressor no retorno do cantor: ele canta mais alto e cansa.'],
 '12.1.2': ['<div class="term"><b>Microfonia:</b> o som da caixa volta ao microfone e é amplificado de novo, em ciclo.</div>',
            '[M] RTA: quanto de cada frequência há no som agora, em 100 bandas.',
            '[C] Microfonia no RTA: um pico estreito que sobe e não desce.',
            '[C] Pré-EQ mostra a entrada; pós-EQ, o efeito da EQ.',
            '[M] Espectrograma: a microfonia vira uma linha reta no tempo.'],
 '12.1.3': ['[C] Fonte de teste: ruído rosa no PA (o gerador está no cap. 17).',
            '[M] Mic de medição num canal livre, como fonte do RTA.',
            '[C] Primeiro o EQ do Main, depois o gráfico.',
            '[C] Subs sozinhos primeiro; depois o L/R, cortando o boxy em 200–400 Hz.',
            '[C] Senoide em varredura lenta acha as ressonâncias da sala.'],
 '13.1.2': ['[C] Envio do canal aberto: sem envio, o reverb não recebe nada.',
            '[C] Master do bus de FX aberto: na X32, o Mix Bus 13 alimenta o FX 1.',
            '[C] FX return subido e ligado ao LR.',
            '[C] X AIR: "OFF" sob o slot é o insert desligado, o certo por envio.',
            '[M] Em insert (X32): ligue no rack e no canal, em Home › Config.'],
 '13.1.4': ['[M] A mesma biblioteca de 60 ou mais efeitos nas duas famílias.',
            '[C] De fábrica na X32: Vintage Room, Hall e Stereo Delay.',
            '[C] Trocar o tipo: toque longo no slot, no app de tablet.',
            '[C] Estude um algoritmo por vez, ouvindo com e sem o efeito.'],
 '15.2.3': ['<div class="term"><b>Aux-fed sub:</b> o sub ganha um bus próprio; você escolhe quem manda grave.</div>',
            '[C] Ao sub só o que tem grave útil: bumbo, baixo, teclado.',
            '[C] XR18: Aux 6 no sub, envios pós-fader, bus igual ao LR.',
            '[C] M32C: sub pelo Mono/Center, com "mono follows main".'],
 '15.2.4': ['[M] X32/M32: Routing › Analog Out, encoder 6, em ms, metros ou pés.',
            '[M] Torre a 20 m da frente: cerca de 58 ms (a conta está no cap. 9).',
            '[C] Saídas Ultranet não têm delay; mesmo sinal sem delay dá fase.',
            '[C] X AIR: Stereo Delay em insert, Mix 100%, gastando um slot.',
            '[C] Alinhe sempre o fundo à frente, nunca uma caixa atrasada à outra.'],
 '16.1.1': ['[M] X AIR: snapshot é a mesa inteira, guardado nela, em 64 posições.',
            '[C] X AIR: cena é um arquivo .scn no aparelho, para backup ou outra mesa.',
            '[M] X32/M32: cena é a mesa inteira, com o ganho dos pré-amps; até 100.',
            '[M] X32/M32: snippet guarda só uma parte; cue list encadeia cenas com GO.',
            '[C] Snapshot como "desfazer": recarregue o último bom.'],
 '16.2.3': ['[C] Exporte o show para o pendrive, sempre antes de firmware ou reset.',
            '[C] Cena 0 própria: User In/Out preenchidos, no lugar do Initialize.',
            '[C] Ferramentas gratuitas de computador salvam cenas e shows.'],
 '18.1.1': ['[M] O mic de quem fala recebe o ganho que os parados liberam.',
            '[M] Dois grupos, X e Y; o medidor azul mostra quanto cada canal abaixa.',
            '[M] Weight dá prioridade; Last Gate mantém o último mic aberto.',
            '[C] X32/M32: do firmware 3 em diante, só nos canais 1–8.',
            '[C] Para fala: palestra, debate, painel. Não para banda.'],
 '19.2.1': ['<div class="term"><b>Multipista:</b> cada canal num arquivo, para remixar depois.</div>',
            '[C] Pendrive: grava o Main ou um bus; toca só WAV, na taxa da mesa.',
            '[C] X32: o gravador grava em Pre EQ; Post EQ leva o EQ do Main.',
            '[C] SD: os cartões não vêm com a mesa; 128 GB está fora do suportado.'],
 '19.2.5': ['[C] Grave o show ou o ensaio em multipista.',
            '[C] Em In/Out › USB Returns, ligue USB 1 → canal 1 … 16 → 16.',
            '[C] Fonte do canal em USB; o nível vai no USB trim, não no ganho.',
            '[C] Ao terminar, volte todos os canais para analógico.'],
 '19.2.10': ['[C] Um bus livre chamado LIVE, com o LR desligado.',
             '[D] Envio da live | pós-fader: segue o PA | pré-fader: independente',
             '[C] USB Sends leva o bus ao OBS ou vMix; suba o master do bus.',
             '[C] X32/M32: matriz da live a partir do Main, com mics de plateia só nela.',
             '[C] Precision Limiter na saída da live; alvo de ~−16 LUFS.'],
 '20.1.2': ['[M] Sem splitter analógico: o sinal digital é copiado pelo cabo.',
            '[M] Uma mesa só controla os ganhos; a outra usa trim ou HA Gain Split.',
            '[M] Clock: a FOH é a mestre; a de monitor segue pela AES50.',
            '[C] Sem stagebox: duas mesas ligadas direto pela AES50.'],
 '21.1.1': ['<div class="term"><b>MIDI:</b> comandos entre aparelhos, sem áudio.</div>',
            '[M] X32/M32: MIDI In e Scene Recall em Setup › Remote.',
            '[M] Pop-up de confirmação: cada troca espera um toque.',
            '[M] Safe vale por MIDI: o canal protegido não muda.'],
 '23.2.1': ['[D] Por onde começar | voz primeiro | base primeiro | só faders',
            '[D] Por onde começar | voz primeiro | base primeiro | só faders',
            '[C] Antes do show: estude o rider e o repertório.'],
 '23.2.2': ['[C] Na mão do voluntário, poucos faders: DCAs por grupo.',
            '[C] Treino curto, com o culto gravado e virtual soundcheck.',
            '[C] Exemplo: mute no DCA, in-ear por mix bus, pregação no pendrive.'],
 '23.2.4': ['[M] Click e talkback fora do Main.',
            '[C] Cabo de rede na porta Ethernet, nunca na Ultranet.',
            '[M] X32/M32: reverbs nos slots 1–4, inserts nos 5–8.',
            '[M] Trocar a taxa: Main mudo (X AIR) ou reiniciar (X32/M32).',
            '[M] Palestra com vários mics: automix com Last Gate.'],
 '26.1.1': ['[M] X AIR: um manual para XR18, X18, XR16 e XR12; M AIR: MR18 e MR12.',
            '[M] X32 e Compact; Rack e Producer têm os seus, mais antigos.',
            '[M] M32 e M32R; M32C: guia rápido + o manual da M32.',
            '[C] Manual e mesa diferentes? Vale a tela da sua mesa.'],
})
# rodada 5, passada final: bullet que o próprio diagrama já escreve sai (ou passa a dizer o porquê)
BULLETS.update({
 '3.2.1': ['[C] Só o cabo USB: o app não acha a mesa.',
           '[C] Notebook que controla e toca música: rede + USB.',
           '[C] X18 e MR18: Ultranet e Ethernet usam o mesmo plugue.',
           '[C] X32: para gravar, o USB vai na placa, não no de controle.'],
 '4.2.1': ['[C] Técnico: notebook no cabo, o mais rápido na emergência.',
           '[C] Músico: MX-Q no celular, só com o bus dele; nunca o app completo.',
           '[C] Os apps antigos de tablet não rodam em sistemas de 2022 em diante.',
           '[C] Teste o MX-Mix antes do show: as versões mudam rápido.'],
 '6.2.2': ['[M] Cada banda: frequência, ganho e largura (Q); em 0 dB, parada.',
           '[C] Os nomes das 4 bandas são só sugestão: qualquer uma vai a qualquer frequência.',
           '[C] Q alto: estreito, para microfonia. Q baixo: largo, para dar cor.'],
 '9.1.2': ['[M] Home › Config: atraso por canal, com liga/desliga.',
           '[C] Dois mics a distâncias diferentes: atrase o mais próximo.',
           '[C] Alinha tons com overheads e kick in com kick out.'],
 '12.2.2': ['[C] Cardioide rejeita o que vem de trás; nunca segure pela cápsula.',
            '[C] Ensine o orador a falar perto do microfone.',
            '[C] Às vezes a "microfonia" é uma caixa com faixa sobrando.'],
 '14.2.2': ['[C] X AIR: em Sends, com o globo aceso, o bus vira Subgroup.',
            '[C] Ligue os canais ao subgrupo.',
            '[C] O subgrupo segue para o Main pela aba Main do bus.',
            '[C] Nos canais: LR desligado, senão o som sai em dobro.'],
 '15.2.3': ['<div class="term"><b>Aux-fed sub:</b> o sub ganha um bus próprio; você escolhe quem manda grave.</div>',
            '[C] XR18: Aux 6 no sub, envios pós-fader, bus igual ao LR.',
            '[C] M32C: sub pelo Mono/Center, com "mono follows main".'],
})

# ---------------------------------------------------------------- rodada 6 (revisão final de redundância): bullet não repete rótulo do diagrama nem slide vizinho; fusões e cortes
BULLETS.update({
 '1.1.4': ['[M] Motor comum a X32 e M32: 40 entradas, 25 buses, 8 FX, 8 DCA.',
           '[M] 100 cenas e placa de expansão 32 × 32.',
           '[C] M32 × M32 LIVE: só muda a placa (a LIVE grava em SD).',
           '[C] M32R LIVE, de 2018, é a versão atual da M32R.'],
 '1.1.7': ['[M] Só na X32/M32 também: crossover, LCR, oscilador e AES50.',
           '[C] Entre as famílias, só ligação analógica: Ultranet não é AES50.',
           '[C] Ex.: saídas da X32 numa MR18 para mixar a live.'],
 '2.1.1': ['[M] Em todas: Ethernet, REMOTE, RESET, MIDI, Main em XLR e fone.',
           '[M] USB: tipo B nas de 18 canais; tipo A (pendrive) na XR16 e XR12.',
           '[M] Ultranet para P16: só XR18, X18 e MR18.',
           '[M] Aux: 6 XLR na XR18 e MR18, 4 XLR na XR16, 2 P10 na XR12.',
           '[M] X18: Aux em P10, 17/18 em RCA e saída Control Room.'],
 '2.1.3': ['[M] Channel Strip: um knob para cada parâmetro do canal.',
           '[M] Faders de entrada com Select, Solo, mini tela e Mute.',
           '[M] Tela com 6 encoders, camadas e monitoração.',
           '[M] Group/Bus/Main: 8 faders de saída e o Main.'],
 '2.1.4': ['[M] X32 Rack: tela de 5", CHANNEL SELECT e um fader de nível.',
           '[M] LED vermelho ao lado do XLR: phantom ligado.',
           '[M] M32C: LCD, botão SELECT e LEDs de AES50.',
           '[M] Na M32C o mic liga no stagebox; ganho e phantom são remotos.'],
 '2.1.6': ['[M] A X AIR fica no palco e a técnica só controla; na X32/M32, quem sobe ao palco é o stagebox.'],
 '2.2.1': ['[C] Instrumento ativo ou pedaleira: nível de linha, qualquer entrada.',
           '[C] Celular por cabo desbalanceado dá ruído de terra: DI.',
           '[C] Aux In Remap (X32): as entradas Aux viram canais.'],
})
DIAG.update({'s2-1-1': ('panel_xr18', {'hl': {(1, 2): 1, (0, 3): 2, (1, 3): 3, (1, 0): 4, (0, 1): 5}})})
ORDER[3] = ['cap-3', 's3-1-1', 's3-1-2', 's3-2-1', 's3-2-4', 's3-2-8', 'quiz-3']   # 3.1.3 (X32/M32 sem Wi-Fi) entrou em 3.1.2
MESAS.update({'3.1.2': 'XR18, X18, XR16, XR12, MR18, MR12, X32, X32 Rack, X32 Compact, X32 Producer, M32, M32R, M32C'})
BULLETS.update({
 '3.1.1': ['[M] A chave escolhe o modo; nome, senha e IP se ajustam no app.',
           '[C] Ethernet: show e local grande; o modo mais confiável.',
           '[C] Wi-Fi Client: instalação fixa, na rede que a casa já tem.',
           '[C] Access Point: ensaio e sala pequena.'],
 '3.1.2': ['[M] Android: ligue o Wi-Fi Lock, que prende o aparelho na rede da mesa.',
           '[M] iPad: a mesa aparece em Devices; toque no ícone.',
           '[M] Sincronizar: Mixer → PC traz a mesa; PC → Mixer apaga o show dela.',
           '[M] Rede da mesa: modelo + final do MAC (ex.: XR18-17-BE-C0).',
           '[M] X32/M32: sem Wi-Fi; o tablet entra por um roteador na porta Ethernet.'],
 '3.2.1': ['[C] Só o cabo USB: o app não acha a mesa.',
           '[C] Notebook que controla e toca música: rede + USB.',
           '[C] X18 e MR18: rede na porta Ultranet, e a mesa some do app.'],
})
BULLETS.update({
 '4.2.4': ['[M] OSC: a língua aberta que app e mesa falam pela rede.',
           '[C] Porta 10024 nas X AIR; 10023 nas X32/M32.',
           '[C] Ordem de ensino: primeiro o app oficial, depois o Mixing Station.'],
})
BULLETS.update({
 '4.2.4': ['[M] OSC: a língua aberta que app e mesa falam pela rede.',
           '[C] Porta 10024 nas X AIR; 10023 nas X32/M32.',
           '[C] Ordem de ensino: primeiro o app oficial, depois o Mixing Station.'],
})
BULLETS.update({
 '5.1.2': ['[M] X AIR: patch livre, qualquer canal em qualquer entrada.',
           '[C] Uma entrada em dois canais: um para o PA, outro para o retorno.',
           '[M] X32/M32: fontes em blocos de 8; um canal em Config › Source.',
           '[C] "O canal queimou"? Confira o botão USB: aceso, a entrada é ignorada (cap. 19).',
           '[C] No começo, patch 1:1: entrada 1 no canal 1.'],
})
BULLETS.update({
 '6.2.2': ['[M] Cada banda: frequência, ganho e largura (Q); em 0 dB, parada.',
           '[C] Estreito para tirar um apito; largo para dar cor.'],
 '6.2.4': ['[C] Caixa de papelão: 300–500 Hz. Oco: −5 dB em 400–600 Hz.',
           '[C] Fanhoso: ~600 Hz. Clareza: reforço largo em 2–3 kHz.',
           '[C] Sibilância: 5–8 kHz ou de-esser. Ar: leve em ~10 kHz.',
           '[C] Erro comum: +80 Hz para encorpar, quando era 160 Hz.'],
 '7.1.1': ['[M] Gate: fecha abaixo do threshold; ligue antes de ajustar.',
           '[C] "Ajuste o threshold, não o baterista".',
           '[C] Na voz, expansor: EXP 2:1, range ~9 dB.',
           '[C] Key filter: o bumbo abre com o "tum", não com o prato.'],
})
TITLE.update({'7.1.1': 'Threshold, expansor e key filter'})
BULLETS.update({
 '8.2.5': ['[C] Erro (X AIR): comp do rack em paralelo.',
           '[C] Por quê: atraso; a mix perde agudo.',
           '[C] Certo: a dinâmica do próprio subgrupo.',
           '[C] Atalho: girar o Mix do compressor do canal.',
           '[C] No Main, só ~3 dB de redução.'],
})
ORDER[9] = ['cap-9', 's9-1-2', 's9-1-3', 'quiz-9']   # 9.1.5 (roteiro do canal) repetia o caminho do sinal do cap. 5: a variação de ordem foi para a nota dele
SHORT[9] = 'Delay, pan e link'
CAPTITLE[9] = 'Delay, pan e stereo link'
PROMISE[9] = 'Alinhar o canal no tempo e posicioná-lo no estéreo.'
SHORT[7] = 'Gate e expansor'
CAPTITLE[7] = 'Gate e expansor'
ORDER[10] = ['cap-10', 's10-1-1', 's10-1-2', 's10-1-4', 'quiz-10']   # 10.1.3 entrou em 10.1.1; 10.2.3 (pré/pós da saída) em 10.1.2
ORDER[11] = ['cap-11', 's11-1-1', 's11-1-2', 's11-2-3', 's11-2-5', 's11-2-6', 'quiz-11']   # 11.2.2 (EQ e GEQ no retorno) entrou em 10.1.4
TITLE.update({'10.1.1': 'Aux, Mix buses e como eles nascem'})
MESAS.update({'10.1.1': 'XR18, X18, XR16, XR12, MR18, MR12, X32, X32 Rack, X32 Compact, X32 Producer, M32, M32R, M32C'})
DIAG.update({'s11-1-1': 'retorno1'})
BULLETS.update({
 '10.1.1': ['[M] X AIR: 6 Aux e 4 envios de FX, além do Main LR.',
            '[M] X32/M32: 16 Mix buses e 6 matrizes, além do Main LRC.',
            '[M] Uso: retornos de palco, subgrupos e envio aos efeitos.',
            '[D] Os 16 buses (X32/M32) | 6 pré + 6 sub + 4 pós | 4 pré + 8 sub + 4 pós',
            '[M] XR16: buses 5 e 6 já saem como subgrupo; XR12 e MR12: 3 a 6.'],
 '10.1.2': ['[C] Pre EQ: ganho, low cut e gate; o retorno mais seguro contra microfonia.',
            '[C] Post EQ: com o EQ do canal, sem a compressão; padrão nos Aux da X AIR.',
            '[C] Pre Fader: tudo menos o fader; o retorno não muda com o PA.',
            '[C] Post Fader: efeitos. Fader fechado, reverb fechado.',
            '[M] A saída do bus tem outra chave pré/pós: Aux Out (X AIR) ou Routing › Out (X32/M32).'],
 '10.1.4': ['[M] X AIR (Aux e LR): Insert → EQ de 6 bandas → comp → fader.',
            '[M] X32 (Mix Bus): Insert → EQ → comp → matrizes.',
            '[C] GEQ de 31 bandas no retorno: o caminho clássico contra microfonia.',
            '[M] TEQ: a curva real segue os sliders.',
            '[C] X32/M32: cada GEQ ocupa um slot de efeito.'],
 '11.1.1': ['[M] X32/M32: Routing › Analog Out liga o Mix Bus à saída; fader do bus em 0 dB.',
            '[C] Erro clássico: esquecer a camada. Main é o PA; Bus 1 é o retorno 1.',
            '[C] Solo no bus enquanto ajusta: você ouve o que o músico ouve.',
            '[C] Peça a cada músico só o que ele precisa ouvir.'],
 '11.2.5': ['[C] Quando os Aux acabam, cada truque dá mais uma via de retorno.',
            '[C] Envio em pré e LR do bus desligado: senão a via nova sai no PA.',
            '[C] ⚠ Truque 1 na XR18: há relatos dos dois lados; teste antes do evento.'],
 '11.2.6': ['[C] Sintoma: o retorno sai no PA, mesmo com os faders lá embaixo.',
            '[C] Causa: o bus de retorno ligado ao Main.',
            '[C] Conserto: apague o LR na aba Main do bus.',
            '[C] Mute corta todos os envios; para tirar só do PA, tire do Main.',
            '[C] XR16 e XR12: confira os subgrupos de fábrica (cap. 10).'],
})
BULLETS.update({
 '12.1.1': ['[M] X AIR: tudo pré-fader, menos o Main LR.',
            '[M] Por isso o medidor do canal mostra o ganho, não o volume na mix.',
            '[M] X32/M32: com solo ativo, a coluna M/C passa a mostrar o solo.'],
})
BULLETS.update({
 '14.1.2': ['[M] Um botão silencia de uma vez todos os canais do grupo.',
            '[M] 4 grupos nas X AIR; 6 na X32/M32.',
            '[C] Típicos: a bateria, os mics de fala, as entradas do DJ.',
            '[M] X32/M32: MUTE GRP ligado, segure o grupo e aperte Select.',
            '[C] Soft mute (X AIR): ao soltar o grupo, o canal mutado sozinho volta junto.'],
})
ORDER[17] = ['cap-17', 's17-1-1', 's17-1-4', 's17-1-5', 'quiz-17']   # 17.1.2 (o fone do técnico) entrou em 17.1.1
TITLE.update({'17.1.1': 'Solo e o fone do técnico'})
MESAS.update({'17.1.1': 'XR18, X18, XR16, XR12, MR18, MR12, X32, X32 Rack, X32 Compact, X32 Producer, M32, M32R, M32C'})
BULLETS.update({
 '16.1.1': ['[M] Recall filtrado (X AIR): na hora de carregar, escolha o que volta.',
            '[C] Snapshot como "desfazer": recarregue o último bom.'],
 '17.1.1': ['[M] Solo manda o canal ao fone do técnico; PA e retornos não mudam.',
            '[C] PFL na passagem de som (ouve com o fader baixo); AFL no show.',
            '[M] Nada em solo: o fone toca a fonte do monitor, em geral o Main.',
            '[M] Dim abaixa a escuta; Mono confere a mix como num "radinho".',
            '[C] Ligue "Select follows Solo" e o PFL dim.'],
 '17.1.5': ['[M] Tipos: senoide, ruído rosa e ruído branco.',
            '[C] Escolha destino e tipo, suba o bus e aperte Generate.',
            '[C] Usos: testar caixas e achar qual caixa é qual via.',
            '[C] ⚠ Enquanto toca, o resto daquele destino fica mudo.'],
})
ORDER[19] = ['cap-19', 's19-2-1', 's19-2-5', 's19-2-10', 'quiz-19']   # 19.2.3 (multipista no DAW) entrou em 19.2.5
TITLE.update({'19.2.5': 'Multipista e virtual soundcheck'})
MESAS.update({'19.2.5': 'XR18, X18, MR18, X32, X32 Rack, X32 Compact, X32 Producer, M32, M32R, M32C'})
BULLETS.update({
 '19.2.5': ['[C] X AIR: USB Sends em Analog, o sinal cru logo após o pré.',
            '[C] X32/M32: grave pela placa X-USB, não pelo USB de controle.',
            '[C] Reaper: ASIO, 48 kHz, buffer 256; pistas fora do master, salvas como modelo.',
            '[C] Na reprodução, o nível vai no USB trim, não no ganho.'],
})
BULLETS.update({
 '20.2.4': ['[C] User In/Out (firmware 4): cada canal escolhe entre 168 fontes.',
            '[C] Ex.: 4 canais da stagebox, o click da placa e o talkback num bloco.',
            '[C] Vêm vazios: mudar para "User" sem preencher = sem áudio.',
            '[C] Para engenheiro convidado: preset de roteamento na Library.'],
})
BULLETS.update({
 '21.1.4': ['[M] Assign: botões e knobs programáveis, trocados por banco.',
            '[M] Uso típico: um knob fixo no envio de reverb da voz.',
            '[M] Em MIDI, cada controle manda CC, Program Change ou Note.',
            '[M] DAW Remote: HUI e Mackie Control, em bancos de 8 faixas.',
            '[M] A placa X-USB emula HUI/Mackie pela própria USB.'],
 '21.1.6': ['[M] 44,1 kHz para áudio puro; 48 kHz quando há vídeo.',
            '[M] X AIR: Setup › Audio/MIDI; mute o Main antes de trocar a taxa.',
            '[M] X32/M32: Setup › Config; trocar a taxa exige reiniciar.',
            '[M] Clock: a letra no topo da tela diz a fonte (L, A/B, C).'],
 '22.1.1': ['[C] X32/M32: pendrive FAT32, com o dcp_*.update na raiz.',
            '[C] O firmware (ex.: 1.17) não é a versão do app; nunca atualize no dia.'],
 '22.1.3': ['[M] Aberturas livres e espaço no case; opera de 5 a 40 °C.',
            '[M] Não abra: manutenção só com técnico qualificado.',
            '[C] Faders motorizados sujos travam: capa contra poeira.',
            '[C] Energia ruim já queimou mesa: use protetor contra surto.'],
})
# cap. 24: sete erros e o conserto (24.2.1), o slide que faltava entre a abertura e o quiz
ORDER[24] = ['cap-24', 's24-2-1', 'quiz-24']
TITLE.update({'24.2.1': 'Sete erros e o conserto'})
ERRFIX = [('RESET de 10 s para consertar a rede', 'RESET de 2 s: só a rede volta ao padrão'),
          ('Conectar o app em PC → Mixer', 'Sempre Mixer → PC: a mesa manda no app'),
          ('Controlar a mesa pelo cabo USB', 'Controle pela rede; o USB leva áudio'),
          ('Cabo de rede na porta Ultranet', 'Ethernet na porta Ethernet'),
          ('Envio de efeito pré-fader', 'Efeito pós-fader; retorno pré-fader'),
          ('Mixar mexendo no ganho', 'Ganho fixo; a mix é nos faders'),
          ('Wi-Fi interno com a casa cheia', 'Roteador externo em 5 GHz')]
QUIZ[24] = ('O app não acha a XR18 e alguém sugere segurar o RESET por 10 s. O que acontece?',
            ['Volta só a configuração de rede', 'A mesa volta ao padrão de fábrica e perde cenas e shows', 'O firmware é atualizado'], 1,
            'O toque longo entrega a mesa limpa; para recuperar só a rede, o toque é de 2 s. Antes de qualquer reset, o show vai para o pendrive ou o computador.')
BULLETS.update({
 '23.2.2': ['[C] Na mão do voluntário, poucos faders: DCAs por grupo.',
            '[C] Treino curto, com o culto gravado e virtual soundcheck.',
            '[C] Exemplo: mute no DCA, in-ear por mix bus, pregação no pendrive.'],
 '23.2.4': ['[C] Imprima, risque o que a sua mesa não tem e leia em voz alta com quem opera.'],
})
BULLETS.update({
 '25.1.1': ['[M] Faixa dinâmica: X32 e M32 106 dB, no nível das X AIR.',
            '[M] EIN: XR e X32 −128 dBu; MR e M32 −125.',
            '[M] D/A de 120 dB na M32; 114 a 115 nas outras.',
            '[M] Máximo no XLR: +23 dBu (nas MR, +23,5).',
            '[M] Todas operam de 5 a 40 °C.'],
})
BULLETS.update({
 '25.1.1': ['[M] Faixa dinâmica: X32 e M32 106 dB, no nível das X AIR.',
            '[M] EIN: XR e X32 −128 dBu; MR e M32 −125.',
            '[M] D/A de 120 dB na M32; 114 a 115 nas outras.',
            '[M] Máximo no XLR: +23 dBu (nas MR, +23,5).',
            '[M] Todas operam de 5 a 40 °C.'],
})
# rodada 6, ajuste de altura: versões curtas onde o corpo gerava slide de continuação
BULLETS['5.1.2'][3] = '[C] "O canal queimou"? Botão USB aceso ignora a entrada (cap. 19).'
BULLETS.update({
 '10.1.1': ['[M] X AIR: 6 Aux, 4 envios de FX e o Main LR.',
            '[M] X32/M32: 16 Mix buses, 6 matrizes e o Main LRC.',
            '[M] Uso: retornos, subgrupos e efeitos.',
            '[D] Os 16 buses (X32/M32) | 6 pré + 6 sub + 4 pós | 4 pré + 8 sub + 4 pós',
            '[M] XR16: buses 5–6 já são subgrupo; XR12 e MR12: 3 a 6.'],
 '10.1.2': ['[C] Pre EQ: antes do EQ; o retorno mais seguro contra microfonia.',
            '[C] Post EQ: com o EQ, sem a compressão; padrão nos Aux da X AIR.',
            '[C] Pre Fader: tudo menos o fader; o retorno não muda com o PA.',
            '[C] Post Fader: efeitos. Fader fechado, reverb fechado.',
            '[M] A saída tem outra chave pré/pós: Aux Out ou Routing › Out.'],
 '12.1.2': ['<div class="term"><b>Microfonia:</b> o som da caixa volta ao microfone, em ciclo.</div>',
            '[M] RTA: quanto de cada frequência há no som agora, em 100 bandas.',
            '[C] Microfonia no RTA: um pico estreito que sobe e não desce.',
            '[C] Pré-EQ mostra a entrada; pós-EQ, o efeito da EQ.',
            '[M] Espectrograma: a microfonia vira uma linha reta no tempo.'],
})
ERRFIX = [('RESET de 10 s para a rede', 'RESET de 2 s: volta só a rede'), ('Conectar em PC → Mixer', 'Conectar em Mixer → PC'),
          ('Controlar pelo cabo USB', 'Controle pela rede; USB é áudio'), ('Cabo de rede na Ultranet', 'Cabo de rede na porta Ethernet'),
          ('Efeito em pré-fader', 'Efeito pós-fader; retorno pré'), ('Mixar mexendo no ganho', 'Ganho fixo; mix nos faders'),
          ('Wi-Fi interno com casa cheia', 'Roteador externo em 5 GHz')]   # uma linha por célula, a 28 px
MESAS.update({'8.2.5': 'XR18, X18, XR16, XR12, MR18, MR12, X32, X32 Rack, X32 Compact, X32 Producer, M32, M32R, M32C'})
# rodada 6, revisão final: bullet que repetia o rótulo do diagrama no mesmo slide
BULLETS['17.1.5'][0] = '[M] Ruído rosa: energia igual por oitava; o branco soa bem mais agudo.'
BULLETS['20.1.1'][0] = '[M] AES50 é ponto a ponto: não passa por switch nem roteador.'
BULLETS['20.1.2'][0] = '[M] O sinal digital é copiado pelo cabo: as duas mesas ouvem os mesmos pré-amps.'

# ---------------------------------------------------------------- checklist final (07-slides/redesign/checklist-final.json; status em checklist-status.md)
# P02: 11.2.6 sai (a regra "LR do bus desligado" fica no diagrama de 11.1.1 e no de 11.2.5)
ORDER[11] = ['cap-11', 's11-1-1', 's11-1-2', 's11-2-3', 's11-2-5', 'quiz-11']
BULLETS['11.1.1'] = BULLETS['11.1.1'] + ['[C] Retorno no PA? Apague o LR na aba Main do bus.']
BULLETS['11.2.5'] = [BULLETS['11.2.5'][0], BULLETS['11.2.5'][2]]
# P03 + P69: 14.2.2 (subgrupo) entra em 14.1.1, que já desenha DCA × subgrupo; sai o 1º bullet de 14.1.1 e o de 14.1.2
ORDER[14] = ['cap-14', 's14-1-1', 's14-1-2', 'quiz-14']
TITLE.update({'14.1.1': 'DCA × subgrupo'})
BULLETS['14.1.1'] = ['[M] 4 DCAs nas X AIR, 8 na X32/M32; o medidor do DCA é só estimativa.',
                     '[C] Move o DCA e a mistura fica; não gasta bus.',
                     '[D] Canais nos DCAs | um por família | dois: família e banda toda',
                     '[C] Subgrupo na X AIR: em Sends, com o globo aceso, o bus vira Subgroup.',
                     '[C] Nos canais do subgrupo: LR desligado, senão o som sai em dobro.']
BULLETS['14.1.2'] = ['[M] 4 grupos nas X AIR; 6 na X32/M32.',
                     '[C] Típicos: a bateria, os mics de fala, as entradas do DJ.',
                     '[C] Soft mute (X AIR): ao soltar o grupo, o canal mutado sozinho volta junto.',
                     '[M] X32/M32: MUTE GRP ligado, segure o grupo e aperte Select.']
# P04 + P71: 1.1.4 fica com o motor comum e a placa; o desenho vira "mesmo motor, corpos diferentes" (os números por modelo ficam só no explorador)
DIAG.update({'s1-1-4': 'motorbodies'})
BULLETS['1.1.4'] = ['[M] Motor comum a X32 e M32: 40 entradas, 25 buses, 8 FX, 8 DCA.',
                    '[M] A placa de expansão troca: USB 32 × 32, Dante, MADI ou ADAT; na Midas, DN32.',
                    '[C] M32 × M32 LIVE: só muda a placa (a LIVE grava em SD).']
# P05: o "só na X32/M32" passou para dentro da tabela de 1.1.7
BULLETS['1.1.7'] = BULLETS['1.1.7'][1:]
# P06 / P65: diagramas de 8.2.5 e 8.2.3 (slides_viz: parcomp, stackcomp)
# P07: 20.1.2 sem o bullet de clock (o clock fica em 20.2.2); diagrama simples "uma stagebox, duas mesas" (bespoke); a porta B saiu do desenho de 20.1.1
BULLETS['20.1.2'] = [BULLETS['20.1.2'][0], BULLETS['20.1.2'][1], BULLETS['20.1.2'][3],
                     '[M] Setup › Preamps: Lock trava o ganho; HA promote passa o controle adiante.']
# P08 + P64: "vida" só em 12.2.3; a fonte de ruído rosa certa para cada família; o bullet do PA sai de 12.2.3
PROMISE[12] = 'Achar a microfonia com método e afinar o PA com ruído rosa e RTA.'
BULLETS['12.1.3'] = ['[C] Ruído rosa: oscilador na X32/M32; nas X AIR, arquivo pelo USB/Aux ou gerador do Mixing Station (cap. 17).'] + BULLETS['12.1.3'][1:]
BULLETS['12.2.3'] = BULLETS['12.2.3'][:4]
# P09: 15.2.2 fica só com o selo de abordagens; 15.2.4 sem os 58 ms (o desenho faz a conta)
BULLETS['15.2.2'] = [BULLETS['15.2.2'][0], BULLETS['15.2.2'][1], '[D] Corte do crossover | ~80 Hz | ~100 Hz', BULLETS['15.2.2'][4]]
BULLETS['15.2.4'] = [b for b in BULLETS['15.2.4'] if '58 ms' not in b]
# P10 + P58: 23.2.1 sem o 1º bullet (o critério de cada um vai para as notas); 23.2.2 deixa os DCAs só no diagrama e ganha um fato das notas
BULLETS['23.2.1'] = BULLETS['23.2.1'][1:]
BULLETS['23.2.2'] = [b for b in BULLETS['23.2.2'] if 'DCAs por grupo' not in b] + ['[C] Seis Aux atendem uma banda de igreja; passou disso, P16.']
# P11 + P72: a X32/M32 entra em 3.2.4 (roteador obrigatório); IP fixo na faixa do roteador
BULLETS['3.1.2'] = [b for b in BULLETS['3.1.2'] if not b.startswith('[M] X32/M32: sem Wi-Fi')]
BULLETS['3.2.4'] = ['[C] Wi-Fi interno (X AIR): só 2,4 GHz; cai com o público.',
                    '[M] Na X32/M32, roteador obrigatório.',
                    '[C] Tablets em 5 GHz; mesa na LAN, nunca na WAN.',
                    '[C] IP fixo na faixa do roteador; o resto em DHCP.',
                    '[C] Local cheio: SSID oculto; teste com o salão cheio.']
# P12: cada informação num lugar só (texto OU diagrama)
BULLETS['6.2.2'] = BULLETS['6.2.2'][:1]
BULLETS['17.1.4'] = BULLETS['17.1.4'][1:]
BULLETS['17.1.1'] = ['[M] Solo manda o canal ao fone do técnico.'] + BULLETS['17.1.1'][1:]
BULLETS['19.2.5'] = [b for b in BULLETS['19.2.5'] if 'X-USB' not in b]
# P13 (registro): "patch 1:1" já está em 4.2.11
BULLETS['5.1.2'] = [b for b in BULLETS['5.1.2'] if 'patch 1:1' not in b]
# P15: quiz-24 sobre um diagnóstico pelo sintoma (antes repetia o RESET do cap. 2)
QUIZ[24] = ('O fader do cantor fecha e o reverb da voz continua soando. Qual é a causa?',
            ['O envio do reverb está em pré-fader', 'O reverb está em insert no canal da voz', 'O phantom do canal ficou ligado'], 0,
            'Em pré-fader, o envio ignora o fader: o canal fecha e o efeito segue recebendo a voz. Em pós-fader, o reverb some junto.')
# P16 + P61: a tabela de 24.2.1 vira consulta rápida, com o capítulo de cada linha; sem riscado
ERRFIX = [('RESET de 10 s para a rede', 'RESET de 2 s: volta só a rede', 2), ('Conectar em PC → Mixer', 'Conectar em Mixer → PC', 3),
          ('Controlar pelo cabo USB', 'Controle pela rede; USB é áudio', 3), ('Cabo de rede na Ultranet', 'Cabo na porta Ethernet', 3),
          ('Efeito em pré-fader', 'Efeito pós; retorno pré', 10), ('Mixar mexendo no ganho', 'Ganho fixo; mix nos faders', 5),
          ('Wi-Fi interno com casa cheia', 'Roteador externo em 5 GHz', 3)]
# P21 + P46: 2.1.6 sem a frase de abertura (o conceito fica no cap. 1); diagrama na largura toda
BULLETS['2.1.6'] = []
WIDE = {'s2-1-6', 's23-2-4'}
DIAG.update({'s2-1-6': 'ligacoes_w', 's23-2-4': 'day3_w'})
# P27: legenda do par "≈" (slides_viz.siblings)
# P56: 22.1.1 ganha o que só estava nas notas; P70: terra e zumbido voltam a 22.1.3
BULLETS['22.1.1'] = BULLETS['22.1.1'] + ['[M] X AIR: a conexão cai durante a atualização; depois, reconecte.',
                                         '[M] Baixe o arquivo do seu modelo: há revisões como XR18V2 e XR12W.']
BULLETS['22.1.3'] = BULLETS['22.1.3'] + ['[M] Zumbido de terra: desligue a malha numa ponta, só em linha balanceada.']
# P57: 16.2.3 (cena zero e backup) entra em 16.1.1: o diagrama "onde mora cada memória" já tem o aparelho e o .scn
ORDER[16] = ['cap-16', 's16-1-1', 's16-1-3', 'quiz-16']
TITLE.update({'16.1.1': 'Cenas e backup'})
BULLETS['16.1.1'] = BULLETS['16.1.1'] + BULLETS['16.2.3']
# P58: 19.2.1 ganha um fato útil que estava só nas notas
BULLETS['19.2.1'] = BULLETS['19.2.1'] + ['[C] Teste o pendrive antes: modelo lento falha e NTFS não é lido.']
# P59: cap-25 e 25.1.1 não repetem "lado a lado"
TITLE.update({'25.1.1': 'As duas famílias em números'})
# P68: o condensador pede menos ganho que o dinâmico; P67: picos até −12/−6
BULLETS['5.2.3'] = [b if not b.startswith('[C] Partida') else '[C] Partida: voz dinâmica ~25–30 dB; condensador pede menos.' for b in BULLETS['5.2.3']]
BULLETS['5.2.1'] = [b if '3 a 6' not in b else '[C] Média perto de −18 dBFS; picos até −12/−6, com folga até 0.' for b in BULLETS['5.2.1']]
# P71: plug-ins externos (Waves) no rack
BULLETS['13.1.4'] = BULLETS['13.1.4'] + ['[C] Waves SuperRack/MultiRack: pelo USB (XR18, MR18) ou pela placa (X32); atenção à latência.']
# P45/P58/P10: colunas que ficaram curtas depois dos cortes ganham um fato que estava só nas notas (não no diagrama)
BULLETS['6.2.2'] = BULLETS['6.2.2'] + ['[C] Erro comum: girar o ganho com a banda parada no grave; confira a frequência antes.']
BULLETS['23.2.1'] = ['[C] Antes de qualquer ordem: ganho no alvo e low cut feitos.'] + BULLETS['23.2.1']
BULLETS['11.2.5'] = BULLETS['11.2.5'] + ['[C] Dois mixes num fone: um bus à esquerda, outro à direita, cabo Y TRS.']
BULLETS['1.1.7'] = ['[C] Entre X AIR e X32/M32, só ligação analógica: Ultranet não é AES50.'] + BULLETS['1.1.7'][1:]

# Motion total (21/10/2026): estes tópicos ganharam tools/bespoke/<id>.svg + .js feitos para o conteúdo já enxugado (mesmo título e bullets).
# O sob medida vence o diagrama genérico daqui; tirar o id do DIAG faz o build usar o SVG sob medida e incluir o JS dele.
for _k in ('s1-1-4', 's2-1-1', 's2-1-6', 's4-2-1', 's4-1-2', 's8-1-1', 's11-1-1', 's13-1-2', 's16-1-1', 's21-1-1',
           's22-1-3', 's23-2-4', 's26-1-1', 's26-2-2', 's26-2-3'):
    DIAG.pop(_k, None)

# Neutralidade (21/10/2026): o curso é completo em si; nenhum autor, escola ou curso externo. Onde há mais de um jeito
# correto de fazer, o slide mostra o selo "Abordagens divergentes" ("[D] Assunto | opção | opção"), sem escolher lado.
# Cada [D] fica na posição do bullet que antes trazia a regra de um lado só, para os passos (data-step) dos desenhos sob medida não mudarem.
BULLETS['1.2.10'] = [b if not b.startswith('[C] Garantia') else '[C] Garantia (XR12, M32C): registro em 90 dias pode estendê-la; no Brasil, consulte o distribuidor.' for b in BULLETS['1.2.10']]
BULLETS['3.2.4'] = ['[C] Wi-Fi interno (X AIR): só 2,4 GHz; cai com o público.',
                    '[M] Na X32/M32, roteador obrigatório.',
                    '[C] Tablets em 5 GHz; mesa na LAN, nunca na WAN.',
                    '[D] Endereço da mesa | DHCP em tudo | IP fixo só na mesa',
                    '[C] Local cheio: senha WPA2 e teste com o salão cheio.']
BULLETS['4.2.1'] = ['[D] Aparelho do técnico | notebook no cabo | tablet na plateia' if b.startswith('[C] Técnico:') else b for b in BULLETS['4.2.1']]
BULLETS['4.2.4'] = ['[D] Por qual app começar | o oficial | o de terceiros' if 'Ordem de ensino' in b else b for b in BULLETS['4.2.4']]
BULLETS['4.2.11'] = ['[D] Patch | 1:1: muda o cabo | livre: muda o roteamento' if b.startswith('[C] Patch 1:1') else b for b in BULLETS['4.2.11']]
BULLETS['7.1.1'] = ['[D] Gate na voz | sem gate | expansor 2:1 ou range ~9 dB' if b.startswith('[C] Na voz, expansor') else b for b in BULLETS['7.1.1']]
BULLETS['8.2.3'] = ['[C] Partida: o preset da fonte, ajustando o threshold.',
                    '[C] Voz ao vivo: 2:1 a 4:1, redução leve (~3–6 dB).',
                    '[D] Quem está começando | preset e threshold | compressor desligado',
                    '[C] Forte demais abafa; release curto demais faz o volume "respirar".',
                    '[C] Em série: o comp do canal e um do rack, cada um trabalhando pouco.']
BULLETS['8.2.5'] = ['[D] Processar o Main | ~2–3 dB de compressão | sem compressão | só limitador' if '~3 dB' in b else b for b in BULLETS['8.2.5']]
BULLETS['10.1.2'] = ['[D] Retorno feito da mesa de PA | Pre EQ: a EQ da sala fica fora | Post EQ ou Pre Fader: a EQ vai junto' if b.startswith('[C] Pre EQ') else b for b in BULLETS['10.1.2']]
BULLETS['10.1.4'] = ['[D] EQ contra microfonia | GEQ de 31 bandas | PEQ com Q alto' if 'GEQ de 31 bandas no retorno' in b else b for b in BULLETS['10.1.4']]
BULLETS['11.2.3'] = ['[D] Fone direto na Aux | direto, em ensaio | com amplificador de fone' if b.startswith('[C] Fone direto') else b for b in BULLETS['11.2.3']]
BULLETS['15.1.1'] = ['[D] Volume da sala | no amplificador | pela matriz, LR em 0 | no fader do Main' if 'Volume do PA pela matriz' in b else b for b in BULLETS['15.1.1']]
BULLETS['19.2.10'] = ['[C] Precision Limiter na saída da live; ~−16 LUFS é referência comum.' if 'LUFS' in b else b for b in BULLETS['19.2.10']]
BULLETS['20.1.2'] = ['[D] Qual mesa controla o ganho | a de monitor | a de FOH | as duas em trim (Gain Split)' if b.startswith('[M] Uma mesa só controla') else b for b in BULLETS['20.1.2']]
BULLETS['23.2.1'] = ['[C] Antes de qualquer ordem: ganho no alvo e low cut feitos.',
                     '[D] Por onde começar | voz primeiro | base primeiro | só faders',
                     '[C] Antes do show: estude o rider e o repertório.']
TITLE.update({'23.2.1': 'Por onde começar a mix'})
# cap. 26: só o fechamento com o próximo passo (slide s26-2-1, montado no build_slides.py)
ORDER[26] = ['cap-26', 's26-2-1']
PROMISE[26] = 'O manual da sua mesa e o próximo passo depois deste curso.'
TITLE.update({'26.2.1': 'Para ir além deste curso'})
for _k in ('s26-1-1', 's26-2-1', 's26-2-2', 's26-2-3', 's26-2-6'):
    DIAG.pop(_k, None)
# selo no slide (não só nas notas) onde o assunto inteiro é um ponto com abordagens diferentes (D17, D15, D12)
BULLETS['2.1.7'] = ['[D] X AIR: Mute at Power On e Safe Levels | ligados: as saídas sobem mudas | desligados: vale a ordem de energia' if 'Mute at Power On' in b else b for b in BULLETS['2.1.7']]
BULLETS['12.1.3'] = BULLETS['12.1.3'] + ['[D] Afinar o PA | ruído rosa + RTA | de ouvido, com música conhecida | senoide em varredura | mic de medição']
BULLETS['15.2.3'] = BULLETS['15.2.3'] + ['[D] Alimentar o sub | crossover a partir do Main | auxiliar só com as fontes escolhidas']

# Rodada 3 dos verificadores (21/10/2026): todas as opções da tabela 24.2.3 no selo do slide, e o selo no slide onde a divergência estava só nas notas
BULLETS['3.2.4'] = [b if not b.startswith('[D] Endereço') else '[D] Endereço da mesa | DHCP em tudo | IP fixo só na mesa | reserva de DHCP no roteador | IP fixo em tudo' for b in BULLETS['3.2.4']]
BULLETS['7.1.1'] = [b if not b.startswith('[D] Gate na voz') else '[D] Gate na voz | sem gate | expansor 2:1 ou range ~9 dB | automix, com vários mics de fala' for b in BULLETS['7.1.1']]
BULLETS['8.2.3'] = [b if not b.startswith('[D] Quem está') else '[D] Quem está começando | preset e threshold | compressor desligado | preset com makeup menor' for b in BULLETS['8.2.3']]
BULLETS['14.1.1'] = [b if not b.startswith('[D] Canais nos DCAs') else '[D] Canais nos DCAs | um por família | dois: família e banda toda | três grandes grupos' for b in BULLETS['14.1.1']]
BULLETS['19.2.10'] = [b if not b.startswith('[D] Envio da live') else '[D] Envio da live | pós-fader: segue o PA | pré-fader: independente | subgrupo (X AIR) | matriz (X32/M32)' for b in BULLETS['19.2.10']]
BULLETS['20.1.1'] = [b if not b.startswith('[D] Cat6') else '[D] Cabo na AES50 | Cat5e blindado (especificação) | Cat6 blindado, como alternativa | evitar Cat6: relatos de perda de sync' for b in BULLETS['20.1.1']]
BULLETS['23.2.1'] = [b if not b.startswith('[D] Por onde') else '[D] Por onde começar | voz primeiro | base primeiro | só faders | de cima para baixo: EQ geral no Main' for b in BULLETS['23.2.1']]
BULLETS['5.2.3'] = BULLETS['5.2.3'] + ['[D] Volume da sala | no amplificador ou caixa ativa | pela matriz, LR em 0 | no fader do Main']
BULLETS['6.2.3'] = BULLETS['6.2.3'] + ['[D] Achar a frequência ruim | reforçar e varrer | varrer já cortando, sem reforço']
BULLETS['16.1.1'] = BULLETS['16.1.1'] + ['[D] Quantas cenas | uma por música ou ato | uma por local ou evento | uma cena base, ajustes à mão']
BULLETS['19.2.1'] = BULLETS['19.2.1'] + ['[D] Ponto de gravação | multipista crua | multipista processada | estéreo do Main, pré ou pós | mix própria (bus ou matriz)']

# Rodada 4 de neutralidade (checklist-neutralidade.json, N24/N09/N12): selo compacto, sem slide de continuação.
# No slide: o assunto e uma etiqueta curta por abordagem ("A · …"); o detalhe de cada uma fica no bloco .divn das notas. Nenhuma abordagem sai.
def _setD(sec, d):
    BULLETS[sec] = [d if b.startswith('[D]') else b for b in BULLETS[sec]]
for _sec, _d in {
    '2.1.7': '[D] Proteção ao ligar (X AIR) | saídas mudas no boot | sem proteção: ordem de energia',
    '3.2.4': '[D] Endereço da mesa | DHCP em tudo | IP fixo na mesa | reserva no roteador | IP fixo em tudo',
    '5.2.3': '[D] Volume da sala | amplificador ou caixa | matriz, LR em 0 | fader do Main',
    '6.2.3': '[D] Achar a frequência ruim | reforçar e varrer | varrer cortando',
    '8.2.3': '[D] Quem está começando | preset e threshold | comp desligado | makeup menor',
    '8.2.5': '[D] Processar o Main | ~2–3 dB de comp | sem comp | só limitador',
    '10.1.2': '[D] Retorno feito da mesa de PA | Pre EQ | Post EQ | Pre Fader',   # N09: Post EQ (EQ sem compressão) e Pre Fader (EQ e compressão) separados
    '11.2.3': '[D] Fone direto na Aux | direto, em ensaio | com amplificador',
    '12.1.3': '[D] Afinar o PA | ruído rosa + RTA | de ouvido | senoide | mic de medição',
    '13.2.6': '[D] Planos de rack | por fonte | por tamanho | reverb, delay e 2 comps | banda completa | evento: reverb e delay',   # N12: os cinco planos do 13.2.6
    '14.1.1': '[D] Canais nos DCAs | um por família | família e banda toda | três grupos',
    '15.1.1': '[D] Volume da sala | amplificador | matriz, LR em 0 | fader do Main',
    '15.2.3': '[D] Alimentar o sub | crossover do Main | auxiliar',
    '16.1.1': '[D] Quantas cenas | por música ou ato | por local ou evento | uma base, à mão',
    '19.2.1': '[D] Ponto de gravação | multipista crua | multipista processada | Main pré-fader | Main pós-fader | mix própria',
    '19.2.10': '[D] Envio da live | pós-fader | pré-fader | subgrupo (X AIR) | matriz (X32/M32)',
    '20.1.1': '[D] Cabo na AES50 | Cat5e blindado | Cat6 blindado | evitar Cat6',
}.items():
    _setD(_sec, _d)
# N24: textos mais curtos onde o selo ainda empurrava o corpo para uma continuação (mesma posição de cada bullet: os passos dos desenhos não mudam)
def _rep(sec, old, new):
    assert any(b.startswith(old) for b in BULLETS[sec]), (sec, old)
    BULLETS[sec] = [new if b.startswith(old) else b for b in BULLETS[sec]]
_rep('3.2.4', '[C] Local cheio', '[C] Local cheio: WPA2 e teste com público.')
_rep('8.2.3', '[C] Partida:', '[C] Partida: preset da fonte + threshold.')
_rep('8.2.3', '[C] Em série:', '[C] Em série: canal e rack, cada um com pouco.')
_rep('12.1.3', '[C] Ruído rosa:', '[C] Ruído rosa: oscilador na X32/M32; arquivo ou app nas X AIR (cap. 17).')
_rep('12.1.3', '[C] Subs sozinhos', '[C] Subs primeiro; depois o L/R (boxy em 200–400 Hz).')
_rep('13.2.6', '[C] Não há plano único', '[C] O plano depende do repertório e dos slots.')
_rep('13.2.6', '[C] Retorno de FX no próprio', '[C] FX return no próprio envio: laço, soa como microfonia.')
_rep('16.1.1', '[M] Recall filtrado', '[M] Recall filtrado (X AIR): escolha o que volta.')
_rep('16.1.1', '[C] Exporte o show', '[C] Exporte o show antes de firmware ou reset.')
_rep('19.2.1', '<div class="term"><b>Multipista:', '<div class="term"><b>Multipista:</b> um arquivo por canal.</div>')
_rep('19.2.1', '[C] Pendrive:', '[C] Pendrive: Main ou bus; toca só WAV.')
_rep('19.2.1', '[C] X32: o gravador', '[C] X32: Pre EQ ou Post EQ do Main.')
_rep('19.2.1', '[C] SD:', '[C] SD: cartão à parte; 128 GB não serve.')
_rep('19.2.1', '[C] Teste o pendrive', '[C] Teste o pendrive: lento falha; NTFS não lê.')
_rep('3.2.4', '[C] Local cheio', '[C] Senha WPA2; teste com público.')
_rep('8.2.3', '[C] Voz ao vivo', '[C] Voz ao vivo: 2:1 a 4:1, ~3–6 dB.')
_rep('12.1.3', '[M] Mic de medição', '[M] Mic de medição num canal livre → RTA.')
_rep('12.1.3', '[C] Primeiro o EQ do Main', '[C] EQ do Main primeiro; depois o gráfico.')
_rep('13.2.6', '[C] O plano depende', '[C] Depende do repertório e dos slots.')
_rep('13.2.6', '[C] Voz:', '[C] Voz: ~1,5 s de decaimento, com pré-delay.')
_setD('13.2.6', '[D] Quatro slots | por fonte | por tamanho | reverb, delay e 2 comps | banda completa | evento: reverb e delay')
_rep('16.1.1', '[C] Cena 0 própria', '[C] Cena 0 própria no lugar do Initialize.')
_rep('16.1.1', '[C] Ferramentas gratuitas', '[C] Programas de computador salvam cenas e shows.')
_setD('19.2.1', '[D] De onde gravar | multipista crua | multipista processada | Main pré-fader | Main pós-fader | mix própria')
_rep('16.1.1', '[C] Snapshot como', '[C] Snapshot: recarregue o último bom.')
_rep('13.2.6', '[C] Reverb no retorno', '[C] Reverb no retorno: FX return no bus do monitor.')
_rep('13.2.6', '[C] Voz:', '[C] Voz: decaimento ~1,5 s, com pré-delay.')
_rep('13.2.6', '[C] Reverb no retorno', '[C] Reverb no retorno: FX return no monitor.')
# N15: o ⚠ do deck tem um só sentido (o da legenda): o dado muda com a unidade, a versão ou o firmware. Erro comum e aviso geral ficam sem o sinal.
BULLETS['2.1.8'] = [b.replace('[C] ⚠ Erro comum:', '[C] Erro comum:') for b in BULLETS['2.1.8']]
BULLETS['17.1.5'] = [b.replace('[C] ⚠ Enquanto toca', '[C] Enquanto toca') for b in BULLETS['17.1.5']]
# N16: a troca "efeito pré → pós" vale numa mesa de PA (há usos válidos de efeito pré-fader: reverb de monitor num slot próprio, mesa só de monitor)
ERRFIX = [(e, c, *n) if e != 'Efeito em pré-fader' else ('Efeito pré-fader na mesa de PA', c, *n) for e, c, *n in ERRFIX]
BULLETS['24.2.1'] = [b.replace('[C] Efeito pré-fader → pós-fader.', '[C] Efeito pré-fader numa mesa de PA → pós-fader.') for b in BULLETS.get('24.2.1', [])]
