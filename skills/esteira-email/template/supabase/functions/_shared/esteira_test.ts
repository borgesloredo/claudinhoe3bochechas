// deno test --allow-env supabase/functions   (sem rede: banco e envio são falsos)
import assert from "node:assert/strict";
import { DIAS } from "./config.ts";
import { avancar, type Deps, FALHAS_MAX, proximoEm } from "./esteira.ts";
import type { Lead } from "./envio.ts";

const DIA = 86_400_000;
const T0 = new Date("2026-01-01T12:00:00Z");
const novo = (x: Partial<Lead> = {}): Lead => ({
  id: 1, email: "a@exemplo.com", nome: "Ana", produto: "meu-produto", origem: "formulario", etapa: 0,
  proximo_em: T0.toISOString(), ultimo_envio: null, criado_em: T0.toISOString(), saiu_em: null, falhas: 0, ...x,
});

// Banco falso em memória com a mesma regra do PATCH "etapa=eq.<atual>".
function falso(l: Lead, o: { comprou?: boolean; falhaEnvio?: boolean; ocupado?: boolean } = {}) {
  const enviados: number[] = [];
  const d: Deps = {
    comprou: () => Promise.resolve(!!o.comprou),
    marcar: (_id, atual, m) => {
      if (o.ocupado || l.etapa !== atual) return Promise.resolve(false);
      Object.assign(l, m);
      return Promise.resolve(true);
    },
    salvar: (_id, m) => (Object.assign(l, m), Promise.resolve()),
    enviar: (_l, e) => o.falhaEnvio ? Promise.reject(new Error("resend 500")) : (enviados.push(e), Promise.resolve()),
  };
  return { d, enviados };
}

Deno.test("calendário: 10 e-mails nos dias da config, depois para", async () => {
  assert.equal(DIAS.length, 10);
  const l = novo();
  const { d, enviados } = falso(l);
  const dias: number[] = [];
  for (let hora = 0; hora <= 200 * 24; hora++) {
    const agora = new Date(T0.getTime() + hora * 3_600_000);
    if (l.proximo_em && Date.parse(l.proximo_em) <= agora.getTime()) {
      assert.equal(await avancar(l, agora, d), "enviado");
      dias.push(Math.round((agora.getTime() - T0.getTime()) / DIA));
    }
  }
  assert.deepEqual(enviados, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]);
  assert.deepEqual(dias, DIAS);
  assert.equal(l.proximo_em, null);
  assert.equal(proximoEm(T0, 10), null);
});

Deno.test("quem comprou sai da esteira sem receber nada", async () => {
  const l = novo({ etapa: 3 });
  const { d, enviados } = falso(l, { comprou: true });
  assert.equal(await avancar(l, T0, d), "comprou");
  assert.equal(l.proximo_em, null);
  assert.deepEqual(enviados, []);
});

Deno.test("duas execuções ao mesmo tempo: só uma envia", async () => {
  const l = novo();
  const { d, enviados } = falso(l, { ocupado: true });
  assert.equal(await avancar(l, T0, d), "ocupado");
  assert.deepEqual(enviados, []);
});

Deno.test("envio com erro volta a etapa e tenta de novo em 1 h; na 3ª falha pula", async () => {
  const l = novo({ etapa: 4, proximo_em: T0.toISOString() });
  const { d } = falso(l, { falhaEnvio: true });
  assert.equal(await avancar(l, T0, d), "falhou");
  assert.equal(l.etapa, 4);
  assert.equal(l.falhas, 1);
  assert.equal(l.proximo_em, new Date(T0.getTime() + 3_600_000).toISOString());
  l.falhas = FALHAS_MAX - 1;
  await avancar(l, T0, d);
  assert.equal(l.etapa, 5); // pulou o e-mail 5 depois de 3 tentativas
  assert.equal(l.falhas, FALHAS_MAX);
});
