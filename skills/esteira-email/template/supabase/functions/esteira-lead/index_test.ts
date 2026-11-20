// Testa a função de ponta a ponta com um banco falso em memória e envio falso: nenhuma chamada de rede.
import assert from "node:assert/strict";
import { chaveDoLead } from "../_shared/envio.ts";

Deno.env.set("SUPABASE_URL", "http://banco.falso");
Deno.env.set("SUPABASE_SERVICE_ROLE_KEY", "falsa");
Deno.env.set("ESTEIRA_SEGREDO", "segredo-so-de-teste-1234567890");
Deno.env.set("ESTEIRA_ENVIO_FALSO", "1");
Deno.env.set("ESTEIRA_ORIGENS", "https://site.teste");

type Linha = Record<string, unknown>;
const leads: Linha[] = [];
const filtro = (u: URL) => (l: Linha) =>
  [...u.searchParams].every(([k, v]) => !v.startsWith("eq.") || String(l[k]) === v.slice(3));
globalThis.fetch = ((entrada: string | URL | Request, init: RequestInit = {}) => {
  const u = new URL(String(entrada));
  const tabela = u.pathname.split("/").pop();
  const ok = (b: unknown) => new Response(JSON.stringify(b), { status: 200 });
  if (tabela !== "esteira_leads") return Promise.resolve(ok([])); // email_devolvido, esteira_compras: vazias
  if (init.method === "POST") {
    const l = { id: leads.length + 1, etapa: 0, falhas: 0, saiu_em: null, ultimo_envio: null, criado_em: new Date().toISOString(), ...JSON.parse(String(init.body)) };
    leads.push(l);
    return Promise.resolve(ok([l]));
  }
  const achados = u.searchParams.has("criado_em") ? [] : leads.filter(filtro(u));
  if (init.method === "PATCH") achados.forEach((l) => Object.assign(l, JSON.parse(String(init.body))));
  return Promise.resolve(ok(achados));
}) as typeof fetch;

let handler!: (r: Request) => Promise<Response>;
// deno-lint-ignore no-explicit-any
(Deno as any).serve = (h: typeof handler) => (handler = h);
await import("./index.ts");

const post = (corpo: unknown, origem = "https://site.teste") =>
  handler(new Request("http://f/esteira-lead", { method: "POST", headers: { origin: origem, "content-type": "application/json" }, body: JSON.stringify(corpo) }));

Deno.test("formulário: grava o lead e manda o e-mail 1 na hora", async () => {
  const r = await post({ email: " Ana@Exemplo.com ", nome: "Ana", produto: "meu-produto" });
  assert.equal(r.status, 200);
  const l = leads.find((x) => x.email === "ana@exemplo.com")!;
  assert.equal(l.etapa, 1);
  assert.ok(l.ultimo_envio);
});

Deno.test("checkout abandonado: entra sem e-mail e espera 2 h", async () => {
  const antes = Date.now();
  assert.equal((await post({ email: "bia@exemplo.com", produto: "meu-produto", origem: "checkout" })).status, 200);
  const l = leads.find((x) => x.email === "bia@exemplo.com")!;
  assert.equal(l.etapa, 0);
  assert.ok(Date.parse(String(l.proximo_em)) - antes >= 2 * 3_600_000 - 1000);
});

Deno.test("recusa site de fora, e-mail inválido e produto desconhecido", async () => {
  assert.equal((await post({ email: "c@exemplo.com", produto: "meu-produto" }, "https://outro.site")).status, 403);
  assert.equal((await post({ email: "sem-arroba", produto: "meu-produto" })).status, 400);
  assert.equal((await post({ email: "c@exemplo.com", produto: "nao-existe" })).status, 400);
});

Deno.test("descadastro: só com a chave certa", async () => {
  const sair = (id: number, k: string, metodo = "GET") =>
    handler(new Request(`http://f/esteira-lead?a=sair&id=${id}&k=${k}`, { method: metodo }));
  assert.equal((await sair(1, "chave-errada")).status, 400);
  assert.equal(leads[0].saiu_em, null);
  assert.equal((await sair(1, await chaveDoLead(1), "POST")).status, 200);
  assert.ok(leads[0].saiu_em);
});
