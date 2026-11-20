#!/bin/bash
# Modelo de auditoria de rastreamento/SEO/painel. Imprime só nomes e estados, nunca valores de segredo.
# Preencha as variáveis abaixo e adapte as seções 1, 5 e 6 ao seu backend (o exemplo usa Supabase Edge Functions).
SITE="https://seudominio.com.br"
DOMINIO="seudominio.com.br"
SCRIPT="/assets/rastreio.js"
# IDs públicos esperados no script do site, no formato em que aparecem no arquivo
IDS=("ga4: 'G-XXXXXXX'" "ads: 'AW-XXXXXXXXX'" "pixel: '0000000000'" "tiktok: 'CXXXXXXXXXX'" "pinterest: '0000000000'" "uet: '00000000'" "clarity: 'xxxxxxxx'")
ARQUIVOS_SEO=(robots.txt sitemap.xml llms.txt llms-full.txt)   # acrescente os arquivos de verificação (google<hash>.html, <chave-indexnow>.txt)
META_PINTEREST="p:domain_verify"
SEGREDOS=(GA4_MEASUREMENT_ID GA4_API_SECRET GOOGLE_SA_JSON GA4_PROPERTY_ID META_PIXEL_ID META_CAPI_TOKEN META_ADS_TOKEN META_ADS_ACCOUNT_ID TIKTOK_PIXEL_ID TIKTOK_ACCESS_TOKEN TIKTOK_ADS_TOKEN TIKTOK_ADVERTISER_ID PINTEREST_AD_ACCOUNT_ID PINTEREST_ACCESS_TOKEN PINTEREST_APP_ID PINTEREST_APP_SECRET BING_WEBMASTER_KEY PAINEL_SENHA)
PROJETO=""          # ex.: ref do projeto Supabase (deixe vazio para pular as seções 1, 5 e 6)
PAINEL_FUNCAO="painel"
# Checkout externo (opcional), para a seção 6c: páginas de checkout do site e o texto que o checkout externo deve mostrar
CHECKOUTS=()        # ex.: ("/produto-a/checkout.html" "/produto-b/checkout.html")
EXTERNO_HOST="pay.hotmart.com"      # host do checkout externo (o link tem que estar no checkout do site)
EXTERNO_WIDGET="widget.min.js"      # script da plataforma que NÃO pode estar na página
AUTOR_ESPERADO=""   # ex.: "Seu Nome" (deixe vazio para pular a conferência do autor)

# Segredos locais do dono (salvos com read -rs, ver SKILL.md). Só carrega; nunca imprime.
CONF="$HOME/.config/traqueamento-e-trafego-pago"
for f in "$CONF/PAINEL_SENHA.env"; do [ -f "$f" ] && { set -a; . "$f"; set +a; }; done

ok() { printf "  %-46s %s\n" "$1" "$2"; }
tmp=$(mktemp)

if [ -n "$PROJETO" ] && [ -n "${PAINEL_SENHA:-}" ]; then
  echo "== 1. Painel ao vivo"
  curl -s -m 120 -X POST -H 'Content-Type: application/json' -H "Origin: $SITE" \
    -d "$(python3 -c 'import json,os; print(json.dumps({"senha": os.environ["PAINEL_SENHA"], "atualizar": True}))')" \
    "https://$PROJETO.supabase.co/functions/v1/$PAINEL_FUNCAO" | python3 -c "
import json,sys
d=json.load(sys.stdin); t=d.get('trafego',{}); st=t.get('metricas',{}).get('status',{})
f=lambda v: 'n/a' if v is None else ('ok' if v else 'FALTA')
for c in t.get('conexoes',[]):
    s=st.get(c['id'],{})
    print(f\"  {c['id']:<10} navegador:{f(c.get('navegador')):<6} servidor:{f(c.get('servidor')):<6} relatorio:{f(c.get('relatorio')):<6} {('ERRO '+s['erro'][:90]) if s.get('erro') else ''}\")"
fi

echo "== 2. IDs no script publicado"
R=$(curl -s "$SITE$SCRIPT")
for k in "${IDS[@]}"; do grep -qF "$k" <<<"$R" && ok "$k" ok || ok "$k" FALTA; done

echo "== 3. Páginas do sitemap carregando o script"
n=0; f=0
for u in $(curl -s "$SITE/sitemap.xml" | grep -o '<loc>[^<]*</loc>' | sed 's/<[^>]*>//g'); do
  n=$((n+1)); c=$(curl -s -o "$tmp" -w '%{http_code}' "$u")
  { [ "$c" = 200 ] && grep -q "$(basename "$SCRIPT")" "$tmp"; } || { f=$((f+1)); echo "    falha ($c): $u"; }
done
ok "páginas ok" "$((n-f))/$n"

echo "== 4. SEO e verificações"
for a in "${ARQUIVOS_SEO[@]}"; do ok "$a" "HTTP $(curl -s -o /dev/null -w '%{http_code}' "$SITE/$a")"; done
H=$(curl -s "$SITE/")
for m in "$META_PINTEREST" 'application/ld+json' 'og:image' 'rel="canonical"'; do grep -q "$m" <<<"$H" && ok "$m" ok || ok "$m" FALTA; done
ok "MX do domínio" "$(dig +short MX "$DOMINIO" | tr '\n' ' ')"

if [ -n "$PROJETO" ]; then
  echo "== 5. Segredos (só nomes)"
  supabase secrets list --project-ref "$PROJETO" -o json 2>/dev/null | python3 -c "
import json,sys; d=json.load(sys.stdin); d=d['secrets'] if isinstance(d,dict) else d; n={x['name'] for x in d}
need=sys.argv[1:]; falta=[k for k in need if k not in n]
print('  ', len(need)-len(falta), '/', len(need), 'presentes', ('| FALTAM: '+' '.join(falta)) if falta else '')
fora=[k for k in n if not k.isupper()]
print('   nomes fora do padrão:', ' '.join(sorted(fora)) or 'nenhum')" "${SEGREDOS[@]}"

  echo "== 6. Funções no ar"
  supabase functions list --project-ref "$PROJETO" -o json 2>/dev/null | python3 -c "
import json,sys; d=json.load(sys.stdin); d=d['functions'] if isinstance(d,dict) else d
for f in d: print(f\"   {f['slug']:<16} {f['status']} v{f['version']}\")"
fi

if [ ${#CHECKOUTS[@]} -gt 0 ]; then
  echo "== 6c. Vitrine (o que o comprador vê; o navegador ainda precisa conferir o botão depois do JS)"
  for c in "${CHECKOUTS[@]}"; do
    code=$(curl -s -o "$tmp" -w '%{http_code}' "$SITE$c"); p=""
    [ "$code" = 200 ] || p="$p fora-do-ar($code)"
    link=$(grep -o "https://$EXTERNO_HOST/[A-Za-z0-9]*" "$tmp" | head -1)
    [ -n "$link" ] || p="$p sem-botao-externo"
    grep -q "$EXTERNO_WIDGET" "$tmp" && p="$p widget-que-apaga-o-botao"
    grep -q 'property="og:image" content="https://' "$tmp" || p="$p sem-og:image"
    if [ -n "$link" ]; then
      ec=$(curl -s -L -o "$tmp" -w '%{http_code}' "$link")
      [ "$ec" = 200 ] || p="$p externo-fora-do-ar($ec)"
      [ -z "$AUTOR_ESPERADO" ] || grep -qF "$AUTOR_ESPERADO" "$tmp" || p="$p autor-diferente"
    fi
    ok "$c" "${p:- ok}"
  done
fi

echo "== 7. Testes"
echo "   (rode aqui os testes do backend e o harness do script do site)"

echo "== 8. Git"
for r in .; do printf "  %-22s %s | mudanças locais: %s\n" "$r" "$(git -C "$r" status -sb 2>/dev/null | head -1)" "$(git -C "$r" status --porcelain 2>/dev/null | wc -l | tr -d ' ')"; done
rm -f "$tmp"
