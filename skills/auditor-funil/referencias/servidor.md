# Lado do servidor: o que o script de páginas não enxerga

O `auditar.py` confere o que está publicado na internet. E-mail que não saiu, comprador sem acesso e tarefa agendada parada só aparecem no banco de dados do vendedor. Esta parte é uma função no servidor dele (Supabase, Vercel, n8n, o que ele já usa), que o `auditar.py` chama primeiro (bloco `servidor` do `funil.json`) ou que roda sozinha no agendador do próprio servidor.

O desenho abaixo veio de um auditor que está no ar há semanas num funil real de cursos digitais. Adapte nomes de tabela e de função ao que o vendedor já tem. Não crie tabelas novas se as dele já guardam a informação.

## O formato de cada checagem
Toda checagem devolve o mesmo formato. O painel, o Telegram e o `auditar.py` leem só isso:
```json
{"id": "acesso", "nome": "Comprador recebeu o e-mail de acesso", "ok": true,
 "detalhe": "12 compras, todas com o e-mail de acesso (1 reenviado agora)", "corrigidos": 1, "itens": []}
```
- `detalhe` é uma frase para leigo, sem código. `itens` lista o que sobrou de errado (e-mail, pedido), no máximo 30.
- A função responde `{"checks": [...]}`. O `auditar.py` junta essas checagens às dele.

## Regras de construção
1. **Cada checagem dentro de uma proteção.** Se uma quebrar, ela vira "a conferência falhou: ..." e as outras continuam. Uma exceção nunca derruba a auditoria inteira.
2. **Primeiro corrige, depois procura o que sobrou.** Rode a varredura que envia (sequência de e-mails, reenvio de acesso) antes das checagens que procuram pendências. Assim, o que aparecer como problema é problema de verdade.
3. **Só faz o que já estava devido.** Chamar a função de fora não pode adiantar e-mail, duplicar envio nem cobrar ninguém. Reenvio só onde existe a marca "não saiu" (coluna vazia).
4. **Uma tentativa por item em cada caso de reentrega**, com registro (tabela ou coluna) para não repetir na rodada seguinte. Depois de 3 falhas, o item sai da fila e vira aviso.
5. **Guardar cada rodada** numa tabela `funil_auditoria` (`origem`, `rodado_em`, `problemas`, `corrigidos`, `checks` em JSON), com limpeza depois de 90 dias. Leitura e escrita só pelo servidor (RLS ligada, sem políticas públicas).
6. **Proteção da chamada.** Pedido vazio roda a auditoria (é seguro: só faz o que já era devido). Pedido com corpo (um relatório de outro lugar, por exemplo um VPS) exige assinatura HMAC-SHA256 com um segredo do servidor e `rodado_em` de no máximo 15 minutos atrás, para ninguém reenviar um relatório velho.

## Checagens do servidor, em ordem
| # | Checagem | Como confere | Corrige sozinho | Só avisa |
|---|---|---|---|---|
| 1 | Sequência de e-mails rodando | Chama a função da sequência com uma janela larga (ex.: 30 dias) para pegar quem largou formulário ou checkout | Envia o 1º e-mail de quem ficou sem; reenvia passo que falhou (até 3 vezes) | Falha que continua depois da 3ª tentativa |
| 2 | Ninguém com e-mail atrasado | Leads com `proximo_em` vencido há mais de 1h30 e que não saíram da lista | (a varredura da linha 1 já tentou) | Lista os e-mails atrasados |
| 3 | E-mails que falharam 3 vezes | Leads com `falhas >= 3` | Nada | Lista: costuma ser endereço errado ou provedor bloqueando |
| 4 | Formulário ou checkout largado recebeu o 1º e-mail | Capturas de formulário e pedidos não pagos de 2,5 h a 30 dias atrás, sem lead para aquele produto, sem compra e sem e-mail devolvido (bounce) | (a linha 1 já tentou) | Lista quem ficou sem |
| 5 | Comprador recebeu o e-mail de acesso | Compras aprovadas há mais de 15 min com `email_enviado_em` vazio. A coluna só é preenchida quando o provedor de e-mail aceitou o envio | Reenvia o acesso | Os que falharam de novo |
| 6 | Tarefas agendadas rodando | Uma função (RPC) que lê o agendador (no Supabase: `cron.job` + `cron.job_run_details`, `security definer`, sem acesso público) | Nada | Tarefa que não existe, está pausada, falhou ou não roda há mais tempo que o esperado |
| 7 | Funções no ar | Pedido vazio a cada função de pagamento, lead e captura: tem que dar 4xx (recusou o pedido vazio), nunca 5xx (quebrou) ou sem resposta | Nada | A função caída |
| 8 | Outro lado mandou o relatório | Última linha de cada `origem` com menos de 2,5 h | Nada | "o outro lado pode estar parado" |

## Lições que viraram checagem
- **A venda que travou no acesso.** A primeira venda real por uma plataforma externa chegou com um número de pedido em outro formato. A página de acesso só aceitava o formato do checkout do site e mostrou "link incompleto". O servidor aceitava os dois. Regra: toda validação no navegador do número do pedido usa a mesma regra do servidor, e o teste do comprador usa um pedido de cada gateway.
- **O botão que sumiu.** O script oficial de uma plataforma de pagamento apagava o próprio botão "Comprar" quando o servidor dele falhava. O HTML tinha o botão, então conferir o HTML "passava". Regra: `nao_pode_ter` com o nome desse script e conferência no navegador depois do carregamento.
- **O nome errado na tela seguinte.** O checkout externo mostrava um nome antigo de autor, que vinha do cadastro da conta. Regra: o bloco `proxima` confere nome do produto, autor e preço na tela do gateway.
- **Pausado não é quebrado.** Tarefa que o dono pausou de propósito aparece como informação, nunca como problema, para o alerta não virar ruído.
- **Silêncio quando está tudo certo.** O Telegram só recebe mensagem quando há problema ou correção. Mensagem a cada 2 horas dizendo "tudo ok" faz o dono parar de ler.

## Extensão opcional: redes sociais
Quem vende por DM (Instagram, Messenger) pode ter um segundo auditor no servidor onde roda o agente de DM:
- comentário pedindo o material cuja DM falhou nos últimos 7 dias (limite da resposta privada da Meta): reenvia 1 vez;
- conversa cuja última mensagem é do cliente, há 15 min a 23 h: reentrega 1 vez ao agente; se o agente continuar sem responder, só lista;
- tarefas do agente pausadas (informação) ou falhando (problema); sinal de vida do receptor de webhooks com menos de 10 min.
Esse lado manda o relatório assinado (regra 6) para a mesma tabela, e o painel mostra os dois lados.

## Painel "Saúde"
O `auditar.py` já grava `saude/index.html` (abre no navegador, claro e escuro, celular). Se o vendedor tem um painel próprio, crie uma aba "Saúde" que lê a última linha de cada `origem` na `funil_auditoria` e mostra:
- 3 números: problemas agora, corrigidos sozinho nas últimas 24 h, conferências nas últimas 24 h;
- cada checagem com "ok" (verde) ou "problema" (vermelho), o `detalhe` e os `itens`;
- "atrasado: devia rodar a cada 2 h" quando a última rodada tem mais de 2,5 h (o auditor do auditor);
- um botão "Conferir agora" que chama a função (pedido vazio) e recarrega a aba.
Teste a aba com um caso tudo certo, um com problema e um sem nenhuma rodada.
