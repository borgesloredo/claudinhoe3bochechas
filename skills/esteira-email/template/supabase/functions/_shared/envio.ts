// Monta e envia um e-mail da esteira pelo Resend.
// Secrets (no Supabase, nunca no código): RESEND_API_KEY, ESTEIRA_REMETENTE ("Marca <contato@seudominio>"),
// ESTEIRA_RESPONDER_PARA (opcional), ESTEIRA_SEGREDO (texto aleatório que assina os links de descadastro).
// ESTEIRA_ENVIO_FALSO=1 só registra no log o que seria enviado: use para testar sem mandar nada.
import { SAIR_URL } from "./config.ts";
import { emailDaEtapa } from "./emails.ts";
import { iguais } from "./db.ts";
import { moldura, textoDe } from "./layout.ts";

export type Lead = {
  id: number; email: string; nome: string | null; produto: string; origem: string | null;
  etapa: number; proximo_em: string | null; ultimo_envio: string | null; criado_em: string;
  saiu_em: string | null; falhas: number;
};

async function hmac(texto: string) {
  const segredo = Deno.env.get("ESTEIRA_SEGREDO");
  if (!segredo || segredo.length < 16) throw new Error("ESTEIRA_SEGREDO ausente ou curto");
  const k = await crypto.subtle.importKey("raw", new TextEncoder().encode(segredo), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const s = new Uint8Array(await crypto.subtle.sign("HMAC", k, new TextEncoder().encode(texto)));
  return [...s].map((b) => b.toString(16).padStart(2, "0")).join("").slice(0, 24);
}
// O id do lead só funciona no link junto com esta chave: ninguém descadastra outra pessoa trocando o número.
export const chaveDoLead = (id: number | string) => hmac(`sair:${id}`);
export const chaveOk = async (id: string, k: string | null) => /^\d{1,12}$/.test(id) && !!k && iguais(k, await chaveDoLead(id));

export async function montarEmail(l: Lead, etapa: number) {
  const sair = `${SAIR_URL}?a=sair&id=${l.id}&k=${await chaveDoLead(l.id)}`;
  const m = emailDaEtapa(etapa, { nome: l.nome, produto: l.produto, origem: l.origem, sair });
  return {
    from: Deno.env.get("ESTEIRA_REMETENTE") ?? "",
    to: [l.email],
    reply_to: Deno.env.get("ESTEIRA_RESPONDER_PARA") || undefined,
    subject: m.assunto,
    html: moldura(m.html),
    text: textoDe(m.html),
    // Descadastro em um clique (RFC 8058): Gmail, Yahoo e Outlook cobram isso em e-mail de marketing.
    headers: { "List-Unsubscribe": `<${sair}>`, "List-Unsubscribe-Post": "List-Unsubscribe=One-Click" },
  };
}

export async function enviar(l: Lead, etapa: number) {
  const m = await montarEmail(l, etapa);
  if (Deno.env.get("ESTEIRA_ENVIO_FALSO") === "1") {
    console.log("ENVIO FALSO", l.id, etapa, m.subject);
    return;
  }
  const key = Deno.env.get("RESEND_API_KEY");
  if (!key || !m.from) throw new Error("RESEND_API_KEY ou ESTEIRA_REMETENTE ausente");
  const r = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: { Authorization: `Bearer ${key}`, "Content-Type": "application/json" },
    body: JSON.stringify(m),
  });
  if (!r.ok) throw new Error(`resend ${r.status} ${await r.text()}`);
}
