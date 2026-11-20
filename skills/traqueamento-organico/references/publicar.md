# Publicar orgânico nas 6 redes

## Fluxo
1. Peça pronta (vídeo vertical 9:16, carrossel 4:5) + texto base `NNN.txt`.
2. `textos_por_rede.py NNN.txt` -> `NNN.redes.txt` com um bloco por rede.
3. Agenda (`publicar.py planejar`) com horários fixos no fuso dela.
4. Publicação: automática na Meta (opcional), lembrete com texto pronto nas outras, ou tudo à mão a partir do `.redes.txt`.
5. Uma vez por semana: ler os números (visualizações, salvamentos, compartilhamentos, seguidores ganhos, comentários com a palavra do CTA) e decidir o que repetir.

## Texto por rede (regras do `textos_por_rede.py`)

| Rede | Título | Legenda / CTA | Hashtags | Link |
|---|---|---|---|---|
| Instagram (Reels) | — | Corpo + CTA. "Comenta X que eu te mando Y" só com resposta automática no direct, e então "Me segue antes, senão a mensagem não chega" | até 5 (limite da rede) | "Link na bio" (link na legenda não é clicável) |
| TikTok | — | Corpo + "Comenta X." (sem prometer direct) | 4 + uma tag da rede se ela quiser (ex.: #aprendanotiktok) | Só na bio (ver verificação) |
| Kwai | — | Igual ao TikTok | 4 | — |
| YouTube Shorts | até 100 com " #Shorts" | Corpo + CTA sem marcar ninguém; "Segue" vira "Se inscreve" | #Shorts + 2 | Na descrição |
| Facebook (Reels) | Headline em cima (frase curta que para o rolar) | Corpo + "Comenta X." | 3 | Na descrição (clicável) |
| Pinterest (Pin de vídeo) | até 100 | Até 500; tira "comenta/marca"; fecha com "Salva este Pin pra consultar depois." | 3 | Link de destino do Pin (home se o conteúdo é informativo; catálogo se cita produto) |

Regras de conteúdo que mais renderam no projeto de origem:
- Conteúdo orgânico **genérico**: ensina um conceito que vale para qualquer marca e qualquer cenário do nicho. Restringir (uma marca, um tipo de cliente) diminui o público. O produto específico aparece pelo CTA ("Comenta o modelo do seu equipamento"), que ainda qualifica o lead.
- Gancho duplo: o que a voz diz nos 3 primeiros segundos é diferente do texto na tela. Gancho negativo ("o erro que estraga...") vence o positivo.
- Legenda entrega valor e não repete o vídeo; termina pedindo uma ação.
- Voz sintética ou imagem gerada: marque o rótulo de conteúdo de IA quando a rede pedir.
- Reel de teste do Instagram (aparece só para quem não segue): ótimo para testar UMA variável por vez (gancho, CTA, capa) do vídeo que mais performou.

## Agenda e horários
- Ritmo sustentável: 1 a 2 vídeos por dia, sempre nos mesmos horários (padrão 12:00 e 19:00 no fuso dela) + stories todo dia + 2 carrosséis por semana. Consistência vale mais que horário "perfeito".
- Um horário especial por semana pode ter outra pegada (ex.: domingo à noite, copy de dor bem direta, sem ensinar) e testes em volta dele.
- A mesma peça nas 6 redes no mesmo horário é normal; no Instagram e no Facebook da mesma pessoa, cuidado com o compartilhamento automático (o composer do site do Instagram vem marcado para o perfil pessoal do Facebook).
- Cada rede tem limite de posts por 24 h na API e o Facebook agenda até ~29 dias à frente: agendar em lotes pequenos.

## Publicador (`publicar.py`, opcional)
- **Automático só com pedido explícito** dela para isso, depois de ver a `agenda.json`. "Pronto" após configurar não é ok para publicar.
- Instagram e Facebook pela **API oficial da Meta** (Reels). O vídeo precisa estar num **link público** (o servidor da Meta baixa de lá): um bucket público (Cloudflare R2, S3), um site estático, ou similar. Link do Google Drive/Dropbox de "compartilhar" não serve (é página, não o arquivo).
- TikTok, YouTube, Kwai e Pinterest: o publicador avisa "postar à mão" com o vídeo e o texto. Automatizar essas redes:
  - YouTube: API oficial (Data API v3, `videos.insert`), exige projeto no Google Cloud, OAuth da conta e tem cota diária. Oficial, sem risco para a conta.
  - Pinterest: API oficial v5 (Pins de vídeo), exige app aprovado. Oficial.
  - TikTok: Content Posting API oficial exige app **auditado**; sem auditoria o post sai privado. A alternativa comum é robô de navegador (não oficial, risco de bloqueio) e, nesse caso, **sempre por internet brasileira**: vídeo subido de servidor no exterior ganha país de origem errado e fica com 0 visualizações.
  - Kwai: sem API pública; só app ou robô (não oficial, mesma regra do IP brasileiro).
- Estados: `pendente` -> `ok`; `falhou` (a rede recusou; repete até 2 vezes); `incerto` (o pedido final saiu e a resposta não voltou: **não repete sozinho**; conferir no app e, se não saiu, `publicar.py repetir ID REDE`); `manual` -> `avisado`.
- 1 post por rede por rodada (atraso não vira rajada), trava contra 2 rodadas ao mesmo tempo, fuso explícito na agenda, grava o estado a cada post.
- Rodar a cada 10 min no Mac: `crontab -e` e a linha
  `*/10 * * * * cd ~/publicacao && /usr/bin/python3 ~/.claude/skills/traqueamento-organico/scripts/publicar.py rodar >> publicador.log 2>&1`
  Mac dormindo = nada sai (o próximo `rodar` publica o atrasado, 1 por rede). Para não depender do Mac, um servidor pequeno serve para a Meta; TikTok e Kwai continuam precisando de IP brasileiro.
- O que o `rodar` imprime é só o que aconteceu (silêncio quando nada venceu): dá para mandar o log para um bot de Telegram ou e-mail.

## Token da Meta (passo a passo para ela)
1. developers.facebook.com > Meus apps > Criar app > tipo "Empresa"/"Outro" > casos de uso "Gerenciar tudo na sua Página" e "Gerenciar mensagens e conteúdo no Instagram".
2. A conta do Instagram precisa ser profissional e estar ligada à Página (Central de Contas ou configurações da Página).
3. Permissões: `pages_show_list`, `pages_read_engagement`, `pages_manage_posts`, `instagram_basic`, `instagram_content_publish` (e `instagram_manage_comments` se for ler comentários). Para uso só na própria conta, o app pode ficar em modo de desenvolvimento.
4. Ferramenta Explorador da Graph API: gerar token de usuário com essas permissões, trocar por token de longa duração e pegar o **token da Página** (`/me/accounts`), que não expira enquanto a senha não mudar. Ou usar um usuário do sistema no Gerenciador de Negócios (token que não depende do login dela).
5. IDs: `FB_PAGE_ID` (Página > Sobre, ou `/me/accounts`) e `IG_USER_ID` (`/{page-id}?fields=instagram_business_account`).
6. Salvar pelo Terminal com `read -rs` (SKILL.md, "Tokens") em `~/.config/traqueamento-organico/meta.env`. Nunca colar no chat, nunca em arquivo do projeto, nunca no git.

## Boas-vindas e DM (para ela decidir)
- Oficial: responder automaticamente quem **comenta** uma palavra ou **escreve** primeiro (janela de 24 h), botões de início de conversa (ice breakers) no Instagram e no Messenger, cartão com botão em vez de link solto. A Meta não deixa mandar mensagem para quem só seguiu e nunca escreveu.
- Não oficial: DM para cada novo seguidor pela API privada (risco alto de bloqueio; limite baixo, para no primeiro aviso, texto sem link pedindo resposta, e só depois da resposta o cartão oficial).
- Nunca prometer no vídeo um direct que ninguém vai mandar.
