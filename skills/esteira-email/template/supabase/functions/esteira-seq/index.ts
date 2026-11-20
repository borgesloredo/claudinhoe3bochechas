// Chamada de hora em hora pelo pg_cron (migration esteira_email.sql). Só envia o que já venceu, então uma chamada
// de fora não adianta nenhum e-mail. Para em quem comprou, saiu (saiu_em) ou teve e-mail devolvido (proximo_em null).
import { json, rows } from "../_shared/db.ts";
import { depsReais } from "../_shared/deps.ts";
import { avancar } from "../_shared/esteira.ts";
import type { Lead } from "../_shared/envio.ts";

const LOTE = 50;

Deno.serve(async () => {
  const agora = new Date();
  const vencidos = await rows<Lead>(
    `esteira_leads?proximo_em=lte.${encodeURIComponent(agora.toISOString())}&saiu_em=is.null&select=*&order=proximo_em&limit=${LOTE}`,
  );
  const conta: Record<string, number> = { enviado: 0, comprou: 0, ocupado: 0, falhou: 0 };
  for (const l of vencidos) conta[await avancar(l, agora, depsReais)]++;
  return json(200, { vencidos: vencidos.length, ...conta });
});
