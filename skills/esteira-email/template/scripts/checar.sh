#!/bin/sh
# Antes do deploy: recusa se sobrou marcador de exemplo ou se algum segredo foi parar no código.
# Uso: sh scripts/checar.sh   (rodar na raiz do projeto, onde fica a pasta supabase/)
cd "$(dirname "$0")/.." || exit 1
erro=0
achou=$(grep -rnE "SUA MARCA|SEU-DOMINIO|SEU NOME|SEU-PROJETO|NOME DO PRODUTO|NOME DO BRINDE|00\.000\.000|CIDADE-UF|ITEM [0-9] DO QUE|ESCREVA AQUI|RESPONDA DE ACORDO" \
  supabase/functions supabase/migrations formulario-exemplo.html 2>/dev/null | grep -v "checar.sh" | grep -v "_test.ts")
if [ -n "$achou" ]; then
  echo "FALTA PREENCHER (troque pelos seus dados):"; echo "$achou"; erro=1
fi
seg=$(grep -rnE "re_[A-Za-z0-9]{20,}|whsec_[A-Za-z0-9+/=]{20,}|eyJ[h]bGciOi|sk-[A-Za-z0-9]{20,}" supabase scripts 2>/dev/null | grep -v "_test.ts")
if [ -n "$seg" ]; then
  echo "SEGREDO NO CÓDIGO (apague e use supabase secrets set):"; echo "$seg" | cut -c1-80; erro=1
fi
ls supabase/migrations/20260101000000_esteira_email.sql >/dev/null 2>&1 && { echo "RENOMEIE a migration com data e hora depois da sua última (supabase migration list)"; erro=1; }
[ $erro = 0 ] && echo "ok: nada de exemplo nem segredo no código"
exit $erro
