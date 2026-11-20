// Webhook do Resend (eventos email.bounced e email.complained, criado no painel do Resend; segredo de assinatura em
// RESEND_WEBHOOK_SECRET). Bounce permanente ou spam põe o endereço em email_devolvido: os leads dele saem da esteira
// (proximo_em = null, devolvido_em) e esteira-lead recusa o endereço. Sem o segredo, toda chamada é recusada (401).
import { rest } from "../_shared/db.ts";
import { assinaturaOk, voltaDoEvento } from "../_shared/volta.ts";

Deno.serve(async (req) => {
  if (req.method !== "POST") return new Response("method not allowed", { status: 405 });
  const corpo = await req.text();
  const h = (n: string) => req.headers.get(n);
  if (!(await assinaturaOk(Deno.env.get("RESEND_WEBHOOK_SECRET") ?? "", h("svix-id"), h("svix-timestamp"), h("svix-signature"), corpo))) {
    return new Response("invalid signature", { status: 401 });
  }
  let ev: unknown;
  try {
    ev = JSON.parse(corpo);
  } catch {
    return new Response("json", { status: 400 });
  }
  const v = voltaDoEvento(ev);
  if (!v) return new Response("ignored");
  const agora = new Date().toISOString();
  try {
    const r = await rest("email_devolvido?on_conflict=email", {
      method: "POST", headers: { Prefer: "resolution=merge-duplicates,return=minimal" },
      body: JSON.stringify(v.emails.map((email) => ({ email, motivo: v.motivo, detalhe: v.detalhe, email_id: v.email_id, em: agora }))),
    });
    if (!r.ok) throw new Error(`email_devolvido ${r.status} ${await r.text()}`);
    const lista = encodeURIComponent(`(${v.emails.map((e) => `"${e}"`).join(",")})`);
    const p = await rest(`esteira_leads?email=in.${lista}&devolvido_em=is.null`, {
      method: "PATCH", headers: { Prefer: "return=minimal" }, body: JSON.stringify({ proximo_em: null, devolvido_em: agora }),
    });
    if (!p.ok) throw new Error(`esteira_leads ${p.status} ${await p.text()}`);
  } catch (e) {
    console.error(String(e));
    return new Response("error", { status: 500 }); // o Resend tenta de novo
  }
  return new Response("ok");
});
