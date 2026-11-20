// Entrada na esteira e saída dela.
// POST {email, nome, produto, origem?}  -> do formulário do seu site (CORS: ESTEIRA_ORIGENS). Grava o lead e manda
//                                         o e-mail 1 na hora. origem "checkout" = recuperação de quem não pagou:
//                                         o e-mail 1 sai 2 h depois, pelo cron, só se a compra não entrou.
// GET  ?a=sair&id&k                     -> link "não quero mais receber" do e-mail: para os e-mails e mostra uma página
// POST ?a=sair&id&k                     -> descadastro em um clique do Gmail/Outlook (List-Unsubscribe-Post)
import { isEmail, json, rest, rows } from "../_shared/db.ts";
import { depsReais, devolvido } from "../_shared/deps.ts";
import { avancar } from "../_shared/esteira.ts";
import { chaveOk, enviar, type Lead } from "../_shared/envio.ts";
import { MARCA, PRODUTOS } from "../_shared/config.ts";

const TOTAL_10MIN = 60; // freio contra robô: no máximo isto de leads novos em 10 minutos
const REENVIO_MIN = 2; // a mesma pessoa pedindo de novo em menos de 2 minutos não recebe outro e-mail
const ESPERA_CHECKOUT_H = 2; // recuperação: primeiro e-mail 2 h depois do checkout abandonado

function cors(req: Request): Record<string, string> | null {
  const origens = (Deno.env.get("ESTEIRA_ORIGENS") ?? "").split(",").map((s) => s.trim()).filter(Boolean);
  const o = req.headers.get("origin") ?? "";
  if (!origens.includes(o)) return null;
  return { "Access-Control-Allow-Origin": o, "Access-Control-Allow-Methods": "POST", "Access-Control-Allow-Headers": "content-type", Vary: "Origin" };
}

Deno.serve(async (req) => {
  const u = new URL(req.url);
  if (u.searchParams.get("a") === "sair") return sair(u, req.method === "POST");
  const c = cors(req);
  if (!c) return json(403, { error: "origem" });
  if (req.method === "OPTIONS") return new Response(null, { status: 204, headers: c });
  if (req.method !== "POST") return json(405, { error: "metodo" }, c);

  let b: Record<string, unknown>;
  try {
    b = await req.json();
  } catch {
    return json(400, { error: "json" }, c);
  }
  const email = String(b.email ?? "").trim().toLowerCase();
  const produto = String(b.produto ?? "");
  if (!isEmail(email)) return json(400, { error: "email" }, c);
  if (!Object.hasOwn(PRODUTOS, produto)) return json(400, { error: "produto" }, c);
  const nome = String(b.nome ?? "").trim().slice(0, 80) || null;
  const origem = b.origem === "checkout" ? "checkout" : "formulario";
  // e-mail que já voltou ou marcou spam recebe a mesma resposta de um endereço que não existe
  if (await devolvido(email)) return json(400, { error: "email" }, c);
  try {
    const desde = encodeURIComponent(new Date(Date.now() - 600_000).toISOString());
    if ((await rows(`esteira_leads?criado_em=gte.${desde}&select=id&limit=${TOTAL_10MIN}`)).length >= TOTAL_10MIN) {
      return json(429, { error: "aguarde" }, c);
    }
  } catch (e) {
    console.error("consulta do freio falhou", String(e));
  }

  const q = encodeURIComponent;
  const [existente] = await rows<Lead>(`esteira_leads?email=eq.${q(email)}&produto=eq.${q(produto)}&select=*`);
  if (!existente) {
    // checkout sem pagamento espera ESPERA_CHECKOUT_H: a pessoa pode estar pagando ainda (o cron confere a compra)
    const espera = origem === "checkout" ? ESPERA_CHECKOUT_H * 3_600_000 : 0;
    const r = await rest("esteira_leads", {
      method: "POST", headers: { Prefer: "return=representation" },
      body: JSON.stringify({ email, produto, nome, origem, proximo_em: new Date(Date.now() + espera).toISOString() }),
    });
    if (!r.ok) {
      console.error("lead não salvo", r.status, await r.text());
      return json(r.status === 409 ? 200 : 502, r.status === 409 ? { ok: true } : { error: "db" }, c);
    }
    const [l] = (await r.json()) as Lead[];
    // formulário: o e-mail 1 sai agora (se falhar, o cron tenta de novo na próxima hora)
    if (!espera) await avancar(l, new Date(), depsReais);
    return json(200, { ok: true }, c);
  }
  if (origem === "checkout") return json(200, { ok: true }, c); // já está na esteira: nada novo
  // pediu o material de novo: reenvia o e-mail 1 (e volta a receber, se tinha saído)
  if (existente.saiu_em) await depsReais.salvar(existente.id, { saiu_em: null });
  if (existente.etapa > 0 && (!existente.ultimo_envio || Date.now() - Date.parse(existente.ultimo_envio) > REENVIO_MIN * 60_000)) {
    try {
      await enviar(existente, 1);
      await depsReais.salvar(existente.id, { ultimo_envio: new Date().toISOString() });
    } catch (e) {
      console.error("reenvio falhou", existente.id, String(e));
      return json(502, { error: "email" }, c);
    }
  }
  return json(200, { ok: true }, c);
});

async function sair(u: URL, umClique: boolean) {
  const id = u.searchParams.get("id") ?? "";
  const ok = await chaveOk(id, u.searchParams.get("k"));
  if (ok) {
    await rest(`esteira_leads?id=eq.${id}`, {
      method: "PATCH", headers: { Prefer: "return=minimal" }, body: JSON.stringify({ saiu_em: new Date().toISOString() }),
    });
  }
  if (umClique) return new Response(ok ? "ok" : "link", { status: ok ? 200 : 400 });
  const texto = ok ? "Pronto. Você não vai mais receber estes e-mails." : "Este link não é válido. Responda qualquer e-mail nosso pedindo para sair.";
  return new Response(
    `<!doctype html><html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${MARCA}</title>` +
      `<body style="font:18px/1.6 Arial,sans-serif;max-width:520px;margin:15vh auto;padding:0 16px;text-align:center"><p>${texto}</p></body></html>`,
    { status: ok ? 200 : 400, headers: { "Content-Type": "text/html; charset=utf-8" } },
  );
}
