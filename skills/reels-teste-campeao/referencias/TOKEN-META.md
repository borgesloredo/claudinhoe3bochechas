# Token da Meta (só para medir e postar automático)

Sem token a skill funciona igual: você mede pelo app, preenche o CSV e posta pelo app. O token só automatiza
`medir`, `postar` e `contas`. Guie o usuário um passo por vez, em texto simples.

**Regra de ouro:** o token **nunca** é colado no chat, nem em arquivo do projeto, nem em print. Ele vai direto do
navegador para o app Terminal, que grava num arquivo só do usuário.

## Antes
- A conta do Instagram precisa ser **profissional** (comercial ou criador de conteúdo) e **pública**. Reel de teste só
  existe nessas contas.
- Ela precisa estar ligada a uma **Página do Facebook** (Instagram → Configurações → Central de Contas, ou pela Página
  no Facebook → Configurações → Contas vinculadas).

## Passo a passo
1. "Abra https://developers.facebook.com/apps e entre com o Facebook que administra a Página. Clique em **Criar
   aplicativo**. Escolha o caso de uso **Outro** e o tipo **Empresa**. O nome pode ser qualquer um (ex.: Reels de teste).
   É grátis. O app pode ficar em modo de desenvolvimento: para a sua própria conta não precisa de análise da Meta."
2. "Abra https://developers.facebook.com/tools/explorer (Explorador da API do Graph). À direita, em **Aplicativo da Meta**,
   escolha o app que você criou. Em **Usuário ou Página**, deixe **Token de usuário**."
3. "Em **Permissões**, adicione estas cinco:
   - `instagram_basic` (ler a conta e os Reels)
   - `instagram_content_publish` (postar o Reel de teste)
   - `instagram_manage_insights` (ler views, alcance, salvamentos e compartilhamentos)
   - `pages_show_list` e `pages_read_engagement` (achar a conta do Instagram ligada à Página)
   Clique em **Generate Access Token** (Gerar token), entre, escolha a Página **e** a conta do Instagram e permita tudo."
4. "O token gerado dura só 1 a 2 horas. Para ele durar 60 dias: copie o token, abra
   https://developers.facebook.com/tools/debug/accesstoken, cole, clique em **Depurar** e depois em
   **Estender token de acesso** (Extend Access Token). Copie o token novo que aparece embaixo. **Não cole aqui no chat.**"
5. "Abra o app **Terminal** do Mac (ou o terminal do Linux), cole o comando abaixo e tecle Enter. Quando ele pedir, cole o
   token e tecle Enter de novo. O token não aparece na tela, é normal."
   ```bash
   mkdir -p ~/.config/reels-teste-campeao && printf 'Cole o token e tecle Enter: ' && read -rs k && printf 'META_TOKEN=%s\n' "$k" > ~/.config/reels-teste-campeao/meta.env && chmod 600 ~/.config/reels-teste-campeao/meta.env && echo && echo salvo
   ```
6. Quando ele disser que apareceu `salvo`, confira sem mostrar o token:
   ```bash
   python3 "$K/scripts/reels_teste.py" contas
   ```
   Deve listar a Página e `IG_USER_ID=<número>`. Com uma conta só, o script usa esse número sozinho. Com várias,
   grave a certa (o número não é segredo):
   ```bash
   printf 'IG_USER_ID=%s\n' 'NUMERO_AQUI' >> ~/.config/reels-teste-campeao/meta.env
   ```

## Erros comuns
| Mensagem | O que fazer |
|---|---|
| `Graph API 190` / token expirado | Passaram 60 dias: repita os passos 2 a 5 (e o `IG_USER_ID`, se você tinha gravado). |
| `Graph API 10` ou `200` / permissão | Faltou marcar uma das 5 permissões ou escolher a conta do Instagram no passo 3. |
| `(sem conta ligada)` em `contas` | A Página não está ligada ao Instagram profissional (ver "Antes"). |
| `trial_params` recusado | A conta não é profissional e pública, ou o Reel de teste ainda não chegou à conta. Poste pelo app. |
| `views` sem valor em `medir` | A Meta mudou o nome da métrica. Rode com `GRAPH_VERSION=v24.0` (ou a versão atual) ou meça pelo app. |

Para apagar o acesso: apague `~/.config/reels-teste-campeao/meta.env` e remova o app em
https://www.facebook.com/settings?tab=business_tools.
