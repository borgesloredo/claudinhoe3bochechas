// Webhook do Resend para e-mail que voltou (bounce permanente) ou foi marcado como spam.
// O Resend assina no padrão Svix: HMAC-SHA256 de "<svix-id>.<svix-timestamp>.<corpo>" com a parte base64 do
// segredo "whsec_..."; o cabeçalho svix-signature traz um ou mais "v1,<base64>" separados por espaço.
import { iguais, isEmail } from "./db.ts";

const TOLERANCIA_S = 300;
const b64 = (b: ArrayBuffer) => btoa(String.fromCharCode(...new Uint8Array(b)));

export async function assinaturaOk(
  segredo: string, id: string | null, ts: string | null, sig: string | null, corpo: string, agora = Date.now(),
) {
  if (!segredo.startsWith("whsec_") || !id || !ts || !sig || !/^\d{1,12}$/.test(ts)) return false;
  if (Math.abs(agora / 1000 - Number(ts)) > TOLERANCIA_S) return false;
  let raw: Uint8Array<ArrayBuffer>;
  try {
    raw = Uint8Array.from(atob(segredo.slice(6)), (c) => c.charCodeAt(0));
  } catch {
    return false;
  }
  const key = await crypto.subtle.importKey("raw", raw, { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const esperado = b64(await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(`${id}.${ts}.${corpo}`)));
  return sig.split(" ").some((p) => {
    const [v, s] = p.split(",");
    return v === "v1" && !!s && iguais(s, esperado);
  });
}

export type Volta = { emails: string[]; motivo: "devolvido" | "spam"; detalhe: string; email_id: string };

// email.bounced (só "Permanent": o endereço não existe) e email.complained. Qualquer outro evento: null.
// Bounce temporário (caixa cheia, servidor fora) não tira ninguém da esteira.
// deno-lint-ignore no-explicit-any
export function voltaDoEvento(ev: any): Volta | null {
  const motivo = ev?.type === "email.bounced" ? "devolvido" : ev?.type === "email.complained" ? "spam" : null;
  if (!motivo) return null;
  if (motivo === "devolvido" && ev.data?.bounce?.type && ev.data.bounce.type !== "Permanent") return null;
  const emails = (Array.isArray(ev.data?.to) ? ev.data.to : []).map((e: unknown) => String(e).trim().toLowerCase()).filter(isEmail);
  if (!emails.length) return null;
  const b = ev.data?.bounce;
  const detalhe = b ? [b.type, b.subType, b.message].filter(Boolean).join(" | ").slice(0, 300) : "";
  return { emails, motivo, detalhe, email_id: String(ev.data?.email_id ?? "") };
}
