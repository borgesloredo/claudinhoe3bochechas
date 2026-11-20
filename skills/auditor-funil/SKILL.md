---
name: auditor-funil
description: Use quando o usuário quiser um auditor que confere sozinho, a cada 2 horas, o funil de venda inteiro de um produto digital — páginas no ar, botão de compra, preço, checkout e a tela seguinte do gateway (Hotmart, Kiwify, Mercado Pago, Stripe), pixels e conversões, e-mails, acesso do comprador — corrige o que é seguro, mostra uma página "Saúde" e avisa no Telegram. Dispare com "auditar funil", "conferir se o site está vendendo", "saúde do funil", "monitorar checkout", "alerta de venda quebrada", "o botão de comprar sumiu", "ninguém recebeu o acesso", mesmo que a pessoa não diga "skill".
---

# Auditor do funil de venda

## O que esta skill faz
Monta um auditor que, a cada 2 horas, olha o funil como um comprador olharia: abre a página de venda, procura o botão de compra e o preço, confere os pixels, segue o clique até o checkout e lê a tela do gateway (nome do produto, autor, preço). Do lado do servidor, reenvia o que ficou para trás (1º e-mail de quem largou o formulário, e-mail de acesso de quem comprou) e confere as tarefas agendadas. Quando algo quebra, avisa no Telegram. Quando está tudo certo, fica em silêncio. O resultado fica numa página "Saúde".

Nasceu de um funil real: no mesmo dia, o script de uma plataforma apagou o botão "Comprar" de 40 páginas, o checkout externo mostrou o nome errado do autor e a primeira venda travou na página de acesso. O HTML estava certo nos três casos. Por isso a regra central é **conferir como comprador**.

| Arquivo | O que tem |
|---|---|
| `scripts/auditar.py` | O auditor (Python 3.9+, só biblioteca padrão). Lê o `funil.json`, confere, grava `saude/` e avisa no Telegram. `--teste` = ensaio sem Telegram; `--autoteste` = confere o próprio script |
| `modelos/funil.exemplo.json` | Modelo do arquivo de configuração, com todos os campos |
| `modelos/github-actions.yml` | Agendamento a cada 2 h no GitHub Actions |
| `referencias/servidor.md` | Lado do servidor: e-mails, acesso, tarefas agendadas, a tabela `funil_auditoria`, a aba "Saúde" num painel próprio |

Caminho da skill: `K=~/.claude/skills/auditor-funil`. Pasta do projeto do usuário: `P`.

## Passo 1: Conversa inicial (uma rodada só)
Antes de perguntar, leia o que dá: abra a página inicial do site com `curl -sL` e liste os links de venda, checkout e acesso, e os IDs de pixel no HTML. Depois pergunte numa chamada de AskUserQuestion (até 4 perguntas, padrão como 1ª opção "(Recomendado)"). O que não perguntar, use o padrão e diga qual usou.
| Campo | Padrão |
|---|---|
| Páginas do funil | As que você achou: venda, checkout, acesso do comprador, página grátis/isca. Confirme a lista |
| Checkout e gateway | Checkout próprio (Mercado Pago, Stripe, Pagar.me) e/ou plataforma externa (Hotmart, Kiwify, Eduzz). O que o comprador tem que ver na tela do gateway: nome do produto, nome do autor/vendedor, preço |
| E-mail e servidor | Onde ficam pedidos e leads (Supabase, planilha, plataforma) e se existe e-mail de acesso e sequência de e-mails. Sem banco próprio: só o `auditar.py` |
| Pixels | Os IDs achados no HTML. Se o site usa Google Tag Manager, o ID `GTM-...` basta |
| Canal de alerta | Telegram (bot próprio, mensagem direta ou grupo com tópico) |
| Onde roda | GitHub Actions (grátis, não depende do computador ligado) |

## Passo 2: Escrever o `funil.json`
```bash
mkdir -p "$P" && cp "$K/scripts/auditar.py" "$K/modelos/funil.exemplo.json" "$P/" && mv "$P/funil.exemplo.json" "$P/funil.json"
```
Preencha com os dados do Passo 1. Campos de cada página:
- `url`, `nome`; `precisa_ter` (textos que o comprador tem que ver); `nao_pode_ter` (texto velho, "Lorem ipsum", script que apaga botão); `preco` como aparece na página (`"97,00"`).
- `botoes`: `texto` do botão e, opcional, `link_contem` (para onde ele tem que levar).
- `pixels`: `{"Meta": "...", "GA4": "G-...", ...}`. O script procura o ID no HTML e nos scripts do mesmo domínio.
- `previa: true`: exige `og:image` (com https, e a imagem abre) e `og:title`, que formam o cartão do link no WhatsApp e no Instagram.
- `proxima`: segue o link de um botão e confere a tela seguinte com os mesmos campos. Use no botão do checkout externo.
- `lenta_s`: segundos para a página contar como lenta (padrão 10).
- `servidor`: funções que corrigem e devolvem checagens (Passo 4). `funcoes`: funções que só precisam estar no ar (pedido vazio dá 4xx, nunca 5xx).
- `painel_url`: link que vai no fim do aviso do Telegram (opcional).

## Passo 3: Telegram (o token nunca passa pelo chat)
Guie o usuário um passo por vez, em texto simples:
1. "No Telegram, abra o **@BotFather**, mande `/newbot`, escolha um nome e um usuário terminado em `bot`. Ele responde com um token."
2. "**Não cole o token aqui no chat.** Abra o app Terminal, cole o comando abaixo, tecle Enter e, quando ele pedir, cole o token e tecle Enter. O token não aparece na tela, é normal."
   ```bash
   mkdir -p ~/.config/auditor-funil && chmod 700 ~/.config/auditor-funil && printf 'Cole o token do bot e tecle Enter: ' && read -rs k && printf 'TELEGRAM_BOT_TOKEN=%s\n' "$k" > ~/.config/auditor-funil/telegram.env && chmod 600 ~/.config/auditor-funil/telegram.env && echo && echo salvo
   ```
3. "Agora mande um 'oi' para o seu bot no Telegram (ou adicione o bot ao grupo e mande uma mensagem lá)." Depois, ache o número da conversa sem mostrar o token:
   ```bash
   ( set -a; . ~/.config/auditor-funil/telegram.env; curl -s "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getUpdates" ) | python3 -c 'import json,sys; r=json.load(sys.stdin); print(sorted({(u.get("message") or u.get("channel_post") or {}).get("chat",{}).get("id") for u in r.get("result",[])} - {None}) or "nenhuma mensagem ainda: mande um oi para o bot e rode de novo")'
   ```
   Grave o número (não é segredo): `printf 'TELEGRAM_CHAT_ID=%s\n' <numero> >> ~/.config/auditor-funil/telegram.env`. Grupo com tópicos: acrescente `TELEGRAM_THREAD_ID=<n>` do mesmo jeito.
4. Teste: `cd "$P" && python3 auditar.py funil.json --testar-telegram`. Tem que chegar "Auditor do funil ligado".

Outro segredo (ex.: token da função do servidor) usa o mesmo modelo do item 2, num arquivo próprio: `printf 'Cole e tecle Enter: ' && read -rs k && printf 'AUDITOR_TOKEN=%s\n' "$k" > ~/.config/auditor-funil/servidor.env && chmod 600 ~/.config/auditor-funil/servidor.env`. No `funil.json`, use `$AUDITOR_TOKEN`; o script troca na hora. Nunca peça, mostre, imprima nem copie o valor de um token para o chat, para o `funil.json` ou para o repositório.

## Passo 4: Lado do servidor (se houver banco de pedidos e leads)
Siga `referencias/servidor.md`: uma função que reenvia o que ficou para trás e devolve `{"checks": [...]}`. Coloque a URL dela no bloco `servidor` do `funil.json`. Não publique nada no servidor do usuário sem o ok dele.

## Passo 5: Primeira rodada e conferência como comprador
1. `cd "$P" && python3 auditar.py funil.json --teste` (ensaio: imprime tudo e não manda Telegram). Abra `saude/index.html`.
2. Para cada problema: é real (conserte no site, com o ok do usuário) ou a configuração está errada (ajuste o `funil.json`). Repita até sobrar só problema real.
3. Faça a **conferência como comprador** (seção abaixo) e transforme o que achar em linhas novas do `funil.json`.

## Passo 6: Agendar a cada 2 horas
| Opção | Quando usar | Como |
|---|---|---|
| **GitHub Actions** (padrão) | Quase sempre: grátis, não depende de computador ligado | Repositório privado com `auditar.py` + `funil.json` na raiz e `modelos/github-actions.yml` em `.github/workflows/`. Segredos em Settings > Secrets > Actions: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` e os outros. O usuário cola cada valor direto no GitHub |
| **cron num servidor Linux/VPS** | Já existe um servidor ligado 24 h | `crontab -e` e a linha `7 */2 * * * cd /caminho/do/projeto && python3 auditar.py funil.json >> saude/cron.log 2>&1`. Segredos em `~/.config/auditor-funil/` daquele servidor |
| **Supabase cron** | A função do servidor (Passo 4) precisa rodar sozinha | `select cron.schedule('funil-auditor', '7 */2 * * *', $$select net.http_post(url := 'https://SEU-PROJETO.supabase.co/functions/v1/funil-auditor', headers := '{"Content-Type":"application/json"}'::jsonb, body := '{}'::jsonb, timeout_milliseconds := 60000)$$);` (extensões `pg_cron` e `pg_net`). Continue rodando o `auditar.py` numa das opções acima para as páginas e o Telegram |
cron no Mac só serve se o Mac nunca dorme; o macOS também pode bloquear pastas como Mesa e Documentos. Prefira GitHub Actions.

## Checagens, em ordem
A ordem importa: primeiro o que corrige, depois o que procura problema.
| # | Checagem | Como confere | Corrige sozinho | Só avisa |
|---|---|---|---|---|
| 1 | Rotinas do servidor | Bloco `servidor`: chama a função, que roda a sequência de e-mails e reenvia acessos (`referencias/servidor.md`) | 1º e-mail de quem largou formulário ou checkout; passo de e-mail que falhou (até 3 vezes); e-mail de acesso que não saiu | O que falhou de novo |
| 2 | Página no ar | HTTP 200 e tempo de resposta | Nada | Fora do ar, erro, lenta |
| 3 | Conteúdo e preço | `precisa_ter`, `nao_pode_ter`, `preco` no texto e no HTML | Nada | Texto sumido, texto velho, preço diferente |
| 4 | Botão de compra | `botoes`: botão existe com aquele texto e leva ao lugar certo | Nada | Botão sumido ou apontando para outro lugar |
| 5 | Pixels e conversões | `pixels`: o ID está no HTML ou nos scripts do mesmo domínio | Nada | Pixel que sumiu da página. Se o evento chega na plataforma, só a compra de teste prova |
| 6 | Prévia de compartilhamento | `previa`: `og:image` abre, `og:title` existe | Nada | Link sem imagem no WhatsApp e no Instagram |
| 7 | Tela seguinte do checkout | `proxima`: segue o botão e confere a tela do gateway (produto, autor, preço) | Nada | Nome, autor ou preço errado no gateway |
| 8 | Funções no ar | `funcoes`: pedido vazio tem que dar 4xx, nunca 5xx | Nada | Função caída |
| 9 | E-mails em dia | Servidor: ninguém com e-mail vencido há mais de 1h30, ninguém com 3 falhas | (já tentou na 1) | Lista os e-mails |
| 10 | Acesso do comprador | Servidor: toda compra aprovada tem o e-mail de acesso aceito pelo provedor | Reenvia | Os que falharam |
| 11 | Tarefas agendadas | Servidor: cada tarefa existe, está ativa e rodou no prazo | Nada (pausada pelo dono é informação, não problema) | Parada ou falhando |
| 12 | Auditor do auditor | A página "Saúde" marca "atrasado" se a última rodada tem mais de 2,5 h | Nada | O agendamento parou |

**Seguro para corrigir sozinho** é só o que já era devido e não muda nada que o comprador vê: reenviar um e-mail que não saiu, reentregar uma mensagem 1 vez, rodar de novo uma rotina. **Nunca sozinho:** mudar preço, editar ou republicar página, mexer no gateway, estornar, pausar anúncio, apagar dado. Isso vira aviso, e o conserto passa pelo usuário.

## Conferir como comprador (regra fixa)
O `auditar.py` lê o HTML e não roda JavaScript. Um script de terceiro pode apagar o botão depois que a página carrega, e o HTML continua "certo". Por isso, na instalação e depois de **toda** mudança em página, checkout ou conta do gateway:
1. Abra a página publicada num navegador de verdade (a ferramenta de navegador da sessão). Espere carregar tudo e confira, na tela e na largura de celular: o botão de compra aparece e dá para clicar, o preço e o nome estão certos.
2. Clique e leia a **tela seguinte** como comprador: nome do produto, autor/vendedor, preço, imagem. Configuração da conta no gateway (nome social, foto, descrição) também faz parte do produto.
3. Faça **uma compra de teste real** por gateway (modo teste, cupom de 100% ou o menor preço): pagamento, e-mail de acesso, página de acesso abrindo com aquele número de pedido e o evento de compra chegando em cada plataforma de anúncio. Só essa compra prova o funil inteiro.
4. Tudo o que você viu de errado vira uma linha no `funil.json` (`nao_pode_ter`, `precisa_ter`, `proxima`), para o auditor vigiar dali em diante.
Se o ambiente não deixar abrir navegador, não force nem contorne: deixe a conferência como pendente e diga ao usuário o que ele precisa olhar.

## Entrega
Responda com: a lista do que é conferido (uma linha por página), o resultado da primeira rodada, onde roda e de quanto em quanto tempo, e o que depende do usuário (tokens, ok para mexer no servidor, compra de teste).

## Erros comuns
| Erro | Correção |
|---|---|
| Pixel "sumido", mas está no site | O site carrega pelo Google Tag Manager: troque os IDs por `"GTM": "GTM-XXXX"` |
| Página dá 403 só para o auditor | Firewall (Cloudflare etc.) bloqueando robô: libere o User-Agent que contém `auditor-funil` |
| Preço "não encontrado" | Escreva como aparece na página (`"97,00"`, não `"97"`). O script exige `R$` antes |
| Texto que aparece na tela não é encontrado | Ele é montado por JavaScript. Use um texto que já está no HTML (título, `og:title`) e confira o resto no navegador |
| Telegram "chat not found" | O usuário não mandou mensagem ao bot, ou o bot saiu do grupo. Grupo tem número negativo |
| Aviso do mesmo problema a cada 2 h | É o comportamento certo enquanto não for resolvido. Conserte ou tire a linha do `funil.json` com o ok do usuário. Nunca desligue o auditor |
| GitHub Actions parou sozinho | O GitHub pausa agendamentos de repositório sem atividade por 60 dias: reative em Actions |

## Conferir a própria skill
`python3 "$K/scripts/auditar.py" --autoteste` sobe um servidor local de mentira e confere páginas, tela seguinte, pixels, prévia, funções, servidor, segredos, Telegram e a página "Saúde". Não usa internet.
