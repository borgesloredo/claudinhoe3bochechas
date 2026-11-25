# Como postamos nas 6 redes na prática

Este é o caminho que roda de verdade hoje, em produção. `publicar.md` é o modelo genérico; aqui está o que foi montado e como cada rede é tratada. Código-fonte: uma pasta de scripts espelhada do servidor.

## Visão geral

- **Quem posta**: o Hermes (VPS), job puro sem IA, `publicador_diario.py`, a cada 10 min. O Mac não precisa estar ligado, exceto para o Kwai (ver abaixo).
- **O que posta por dia**: 8 orgânicos + 1 vídeo de venda + 1 carrossel, janela 8h–21h (Brasília), 7 dias. Passo de 80 min entre itens. Domingo perde a vaga da noite: é do `domingo_noite.py` (21h).
- **Redes, nesta ordem**: `ig, fb, yt, tt, kw, pin` (Instagram, Facebook, YouTube Shorts, TikTok, Kwai, Pinterest).
- **Texto**: vem do `.txt` de cada peça, sem alteração. Um bloco por rede, cabeçalho em maiúsculas em linha própria (`INSTAGRAM`, `FACEBOOK`, `YOUTUBE SHORTS` para vídeo / `YOUTUBE` para carrossel, `TIKTOK`, `KWAI`, `PINTEREST`). `publicador_lib.blocos()` lê. Se o bloco não existe, a rede falha com "bloco de texto não encontrado".
- **Fluxo do tick**: o tick é rápido: entrega a caixa de saída (`publicador.outbox` → Telegram) e, se há item no horário e ninguém trabalhando, dispara um trabalhador em segundo plano (`--worker`). O trabalhador segura o lock e publica rede por rede.
- **Estado**: `~/.hermes/state/publicador.json`. Plano congelado no primeiro uso (horários não andam). Comandos: `publicador_diario.py --status`, `--dry` (não posta), `--item ID`.

## Como cada rede é postada

| Rede | Caminho | Detalhe que importa |
|---|---|---|
| Instagram | API oficial da Meta, `meta.py publish ig` (Reel) e `meta.py carousel ig` | Vídeo precisa estar em link público (R2). Reel de teste (`--trial-auto`) está **desligado** (16/11); se voltar, é extra e só com pedido |
| Facebook (Página) | API oficial da Meta, `meta.py publish fb` e `meta.py carousel fb` | Só a Página. Perfil pessoal não tem API: `fb_compartilhar.py` compartilha os Reels da Página no perfil, por navegador, devagar (máx. 3–4/h, 9h–22h, pausas de 8–25 min, para tudo se aparecer aviso) |
| YouTube Shorts | API oficial (Data API v3) via `yt_upload.py`; autorização guardada por `yt_auth.py` | Título até 100 caracteres. Carrossel (só imagem): `nao_suportado`. Cota diária: status `cota` |
| TikTok | Navegador logado (`social.py tiktok`, social-auto-upload), conferência no TikTok Studio com `tk_confere.py` | Modo aleatório: 3 a 5 itens por dia, sorteados e fixos por dia (`tt_do_dia`). Legenda variada só no TikTok (`tk_legenda.variar`). Carrossel vira slideshow 1080×1920 (ffmpeg, 3,2 s por imagem). **Só com IP do Brasil** (proxy BR) |
| Kwai | Android virtual (`kwai.py publicar`, adb `127.0.0.1:5555`) | Só publica se `kwai.py status` disser BR (túnel pelo Mac). Mac desligado ou túnel caído = `adiado`, **não trava a fila**. Antes de subir, `force-stop` do app. Séries sobem 1 por vez por `series_kwai.py` |
| Pinterest | Vídeo: `pin_video.py` pelo Chromium logado (CDP 9222). Imagem: `social.py pinterest` | Título/Descrição/Link vêm do bloco. Link padrão `https://seu-site.com.br/`. `pin_video.py` apaga rascunhos antigos antes, para nunca publicar o errado |

Carrossel: IG e FB postam as imagens; YouTube não suporta; TikTok e Kwai recebem o slideshow; Pinterest posta a primeira imagem.

## Estados e regras de repetição

`ok`, `provavel`, `incerto`, `nao_suportado`, `cota` são finais. `adiado` e `falhou` são pendentes.

- `falhou` = a rede nem chegou a publicar: repete até 2 vezes.
- `incerto` e `provavel` = o pedido saiu e a resposta não voltou (Kwai fecha o app no envio, TikTok trava depois de postar). **Nunca repete sozinho.** Conferir no app/Studio antes de qualquer reenvio (duplicar vídeo é o pior erro).
- TikTok sem confirmação no log: o código confere na lista do Studio antes de dar `incerto`.
- Tudo que o trabalhador faz vai para a caixa de saída e chega no Telegram com ícone (✅ ok, 🟡 provável, ⚠️ incerto, ❌ falhou, ⏳ adiado, 🚫 cota, ➖ não suportado).

## Regras do dono da conta

- O roteiro dos 10 posts/dia **não** troca post por teste. Reel de teste só como extra e só com pedido.
- Publicar texto exatamente como está no `.txt`. Exceção definida por ele: variação de legenda no TikTok.
- Nunca publicar, agendar nem compartilhar fora do que ele pediu (ver regra fixa no `SKILL.md`).
- Mídia orgânica fica fora do git: `limpar_postados.py` (diário, 23:30) apaga vídeo, imagem e texto de legenda depois de postados (os posts continuam online; vídeos de venda nunca). MP4 de feed fica 5 dias para o campeão dos Reels de teste.

## Jobs irmãos que usam o mesmo caminho

| Job | O que faz |
|---|---|
| `domingo_noite_semana.sh` / `domingo_noite_conferir.sh` | Domingo 21h: principal nas 6 redes + 10 Reels de teste |
| `reels_teste.py` | Só orgânicos; campeão a cada 2 dias; 11 Reels de teste em 56 dias |
| `series_historia.py` + `series_kwai.py` | Episódios em série com voto A/B nos comentários, próximo EP 24 h depois |
| `fb_compartilhar.py` | Página → perfil pessoal, devagar |
| `outras_redes_watch.py` | Vigia comentários do TikTok Studio e caixa do Kwai (só leitura no Kwai) |
| `ig_comentario_dm.py`, `ig_seguidores.py`, `ig_ice_breakers.py` | DM de comentário, boas-vindas ao seguidor, botões de início de conversa |
| `limpar_postados.py` | Limpeza diária do que já foi postado |

## Armadilhas confirmadas neste caminho

1. **TikTok com IP fora do Brasil = 0 visualizações** (31 vídeos zerados; corrigido em 17/11 com proxy BR pelo túnel do Mac). Conferir `locationCreated` na página pública.
2. **Kwai com feed aberto derruba o app** (vídeo com som). O leitor abre direto `kwai://notifications` e fecha (`force-stop`).
3. **Facebook perfil pessoal**: sem API. Só por compartilhamento devagar com navegador; qualquer aviso para tudo.
4. **Instagram** publica na hora (não agenda): a agenda é do próprio publicador.
5. **Mac dormindo**: só o Kwai espera; as outras 5 redes não dependem dele.
6. Se mudar um script na VPS, copiar de volta para a pasta espelho no repositório e commitar. Nunca deixar script só na VPS.
