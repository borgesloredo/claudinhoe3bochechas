// As dependências reais da esteira (banco Supabase + envio Resend), usadas por esteira-seq e esteira-lead.
import { rest, rows } from "./db.ts";
import { enviar } from "./envio.ts";
import type { Deps } from "./esteira.ts";

const q = encodeURIComponent;
export const depsReais: Deps = {
  // Compras registradas em esteira_compras (ver o passo "parar quando comprar" no SKILL.md).
  comprou: async (email, produto) =>
    (await rows(`esteira_compras?email=eq.${q(email)}&produto=eq.${q(produto)}&select=email&limit=1`)).length > 0,
  marcar: async (id, etapaAtual, mudanca) => {
    const r = await rest(`esteira_leads?id=eq.${id}&etapa=eq.${etapaAtual}`, {
      method: "PATCH", headers: { Prefer: "return=representation" }, body: JSON.stringify(mudanca),
    });
    return r.ok && ((await r.json()) as unknown[]).length > 0;
  },
  salvar: async (id, mudanca) => {
    const r = await rest(`esteira_leads?id=eq.${id}`, { method: "PATCH", headers: { Prefer: "return=minimal" }, body: JSON.stringify(mudanca) });
    if (!r.ok) console.error("lead não salvo", id, r.status, await r.text());
  },
  enviar,
};

// Endereço que voltou ou marcou spam (esteira-volta). Erro na consulta conta como "não".
export const devolvido = (email: string) =>
  rows(`email_devolvido?email=eq.${q(email.trim().toLowerCase())}&select=email&limit=1`)
    .then((r) => r.length > 0, (e) => (console.error("consulta email_devolvido falhou", String(e)), false));
