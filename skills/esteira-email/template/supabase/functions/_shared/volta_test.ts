import assert from "node:assert/strict";
import { assinaturaOk, voltaDoEvento } from "./volta.ts";

const SEGREDO = "whsec_" + btoa("chave-de-teste-123");
async function assinar(id: string, ts: string, corpo: string) {
  const raw = Uint8Array.from(atob(SEGREDO.slice(6)), (c) => c.charCodeAt(0));
  const key = await crypto.subtle.importKey("raw", raw, { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const s = await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(`${id}.${ts}.${corpo}`));
  return "v1," + btoa(String.fromCharCode(...new Uint8Array(s)));
}

Deno.test("assinatura Svix: aceita a certa, recusa corpo trocado, segredo errado e hora velha", async () => {
  const agora = 1_763_200_000_000, ts = String(agora / 1000), corpo = '{"type":"email.bounced"}';
  const sig = await assinar("msg_1", ts, corpo);
  assert.ok(await assinaturaOk(SEGREDO, "msg_1", ts, `v1,outra ${sig}`, corpo, agora));
  assert.ok(!(await assinaturaOk(SEGREDO, "msg_1", ts, sig, corpo + " ", agora)));
  assert.ok(!(await assinaturaOk("whsec_" + btoa("outra"), "msg_1", ts, sig, corpo, agora)));
  assert.ok(!(await assinaturaOk(SEGREDO, "msg_1", ts, sig, corpo, agora + 600_000)));
  assert.ok(!(await assinaturaOk("", "msg_1", ts, sig, corpo, agora)));
  assert.ok(!(await assinaturaOk(SEGREDO, null, ts, sig, corpo, agora)));
});

Deno.test("evento: bounce permanente e spam marcam; o resto é ignorado", () => {
  const bounce = { type: "email.bounced", data: { email_id: "e1", to: [" Ana@Exemplo.com "], bounce: { type: "Permanent", subType: "General", message: "no such user" } } };
  assert.deepEqual(voltaDoEvento(bounce), { emails: ["ana@exemplo.com"], motivo: "devolvido", detalhe: "Permanent | General | no such user", email_id: "e1" });
  assert.equal(voltaDoEvento({ type: "email.complained", data: { email_id: "e2", to: ["b@x.com"] } })?.motivo, "spam");
  assert.equal(voltaDoEvento({ ...bounce, data: { ...bounce.data, bounce: { type: "Transient" } } }), null);
  assert.equal(voltaDoEvento({ type: "email.delivered", data: { to: ["a@b.com"] } }), null);
  assert.equal(voltaDoEvento({ type: "email.bounced", data: { to: ["não é e-mail"] } }), null);
  assert.equal(voltaDoEvento(null), null);
});
