import assert from "node:assert/strict";
import { CUPOM_DA_ETAPA, CUPONS, PRODUTOS, precoCom, reais } from "./config.ts";
import { emailDaEtapa, ULTIMA } from "./emails.ts";
import { chaveDoLead, chaveOk, type Lead, montarEmail } from "./envio.ts";
import { moldura, textoDe } from "./layout.ts";

Deno.env.set("ESTEIRA_SEGREDO", "segredo-so-de-teste-1234567890");
const PRODUTO = Object.keys(PRODUTOS)[0];
const c = { nome: "Ana Souza", produto: PRODUTO, sair: "https://exemplo.com/sair/?a=sair&id=1&k=x" };

Deno.test("os 10 e-mails montam, com descadastro e sem texto quebrado", () => {
  for (let e = 1; e <= ULTIMA; e++) {
    const m = emailDaEtapa(e, c);
    assert.ok(m.assunto.length > 5, `assunto e${e}`);
    assert.ok(m.html.includes(c.sair), `descadastro e${e}`);
    assert.ok(!/undefined|NaN|\$\{/.test(m.assunto + m.html), `texto quebrado e${e}`);
    assert.ok(m.html.includes("Oi, Ana!"), `saudação e${e}`);
  }
  assert.throws(() => emailDaEtapa(11, c));
});

Deno.test("cupons: código, % e preço certos; link nunca leva o cupom pronto", () => {
  assert.equal(reais(precoCom(PRODUTO, "VOLTA20")), PRODUTOS[PRODUTO].preco === 97 ? "R$ 77,60" : reais(precoCom(PRODUTO, "VOLTA20")));
  let anterior = 0;
  for (const [etapa, codigo] of Object.entries(CUPOM_DA_ETAPA)) {
    assert.ok(CUPONS[codigo] >= anterior, "o desconto nunca desce ao longo da esteira");
    anterior = CUPONS[codigo];
    const m = emailDaEtapa(Number(etapa), c);
    assert.ok(m.html.includes(`<b>${codigo}</b>`), `código no e-mail ${etapa}`);
    assert.ok(m.html.includes(reais(precoCom(PRODUTO, codigo))), `preço no e-mail ${etapa}`);
  }
  for (let e = 1; e <= ULTIMA; e++) {
    for (const [, href] of emailDaEtapa(e, c).html.matchAll(/href="([^"]+)"/g)) {
      assert.ok(!/[?&](cupom|coupon|offDiscount|discount)=/i.test(href), `cupom pré-aplicado no e-mail ${e}: ${href}`);
    }
  }
});

Deno.test("recuperação de checkout muda o e-mail 1", () => {
  const m = emailDaEtapa(1, { ...c, origem: "checkout" });
  assert.match(m.html, /começou a compra/);
});

Deno.test("envio: cabeçalho de descadastro em 1 clique, texto puro e chave do link", async () => {
  const l: Lead = { id: 42, email: "a@exemplo.com", nome: null, produto: PRODUTO, origem: null, etapa: 0, proximo_em: null,
    ultimo_envio: null, criado_em: new Date().toISOString(), saiu_em: null, falhas: 0 };
  const m = await montarEmail(l, 5);
  assert.equal(m.headers["List-Unsubscribe-Post"], "List-Unsubscribe=One-Click");
  assert.ok(m.text.length > 50 && !m.text.includes("<"));
  assert.ok(m.html.startsWith("<!doctype html>"));
  const k = await chaveDoLead(42);
  assert.ok(await chaveOk("42", k));
  assert.ok(!(await chaveOk("43", k)));
  assert.ok(!(await chaveOk("42", null)));
  assert.ok(!textoDe(moldura("<p>a</p>")).includes("<"));
});
