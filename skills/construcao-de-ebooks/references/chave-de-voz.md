# Chave grátis da voz (só para o autoestudo)

Guie um passo por vez.

1. "Abra https://aistudio.google.com/apikey e entre com uma conta Google. O plano grátis não pede cartão."
2. "Clique em **Criar chave de API** e copie a chave."
3. "**Não cole a chave aqui no chat.** Abra o app Terminal, cole o comando abaixo e tecle Enter. Quando ele pedir, cole a chave e tecle Enter. Ela não aparece na tela, é normal."
   ```bash
   mkdir -p ~/.config/construcao-de-ebooks && printf 'Cole a chave do Gemini e tecle Enter: ' && read -rs k && (umask 077; printf 'GEMINI_API_KEY=%s\n' "$k" > ~/.config/construcao-de-ebooks/gemini.env) && echo && echo salvo
   ```
4. Quando aparecer `salvo`, rode `bash "$K/scripts/voz.sh" --chaves`. Deve dizer `1 chave(s)`.
5. Avise da cota: o grátis dá cerca de 10 pedidos por dia e cada pedido leva até 5 telas. 30 telas usam uns 6 pedidos; 50 usam uns 10. Se acabar, retoma no dia seguinte.

Nunca peça, mostre, leia ou copie o valor da chave.
