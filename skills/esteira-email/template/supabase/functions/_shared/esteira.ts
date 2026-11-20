// O coração da esteira: decide e grava o próximo passo de um lead. Lógica pura com as dependências injetadas
// (banco e envio), para testar sem rede (esteira_test.ts).
import { DIAS } from "./config.ts";
import type { Lead } from "./envio.ts";

export const FALHAS_MAX = 3;

// Quando sai o e-mail seguinte, depois de enviado o e-mail `feita` (0 = nenhum ainda). null = esteira acabou.
export const proximoEm = (criado: Date, feita: number) =>
  feita >= 0 && feita < DIAS.length ? new Date(criado.getTime() + DIAS[feita] * 86_400_000) : null;

export type Deps = {
  comprou(email: string, produto: string): Promise<boolean>;
  // grava `mudanca` só se o lead ainda estiver na etapa `etapaAtual`; true = este processo ficou com o envio
  marcar(id: number, etapaAtual: number, mudanca: Record<string, unknown>): Promise<boolean>;
  salvar(id: number, mudanca: Record<string, unknown>): Promise<void>;
  enviar(l: Lead, etapa: number): Promise<void>;
};

export async function avancar(l: Lead, agora: Date, d: Deps): Promise<"enviado" | "comprou" | "ocupado" | "falhou"> {
  // Quem já comprou sai da esteira na hora.
  if (await d.comprou(l.email, l.produto)) {
    await d.marcar(l.id, l.etapa, { proximo_em: null });
    return "comprou";
  }
  const antes = { etapa: l.etapa, falhas: l.falhas ?? 0, ultimo_envio: l.ultimo_envio }; // l pode mudar depois
  const etapa = antes.etapa + 1;
  // Marca a etapa ANTES de enviar: duas execuções do cron ao mesmo tempo nunca mandam o mesmo e-mail duas vezes.
  const meu = await d.marcar(l.id, antes.etapa, {
    etapa, proximo_em: proximoEm(new Date(l.criado_em), etapa)?.toISOString() ?? null, ultimo_envio: agora.toISOString(), falhas: 0,
  });
  if (!meu) return "ocupado";
  try {
    await d.enviar(l, etapa);
    return "enviado";
  } catch (e) {
    console.error("envio falhou", l.id, etapa, String(e));
    // Volta para a etapa anterior e tenta de novo em 1 hora; depois de FALHAS_MAX tentativas pula este e-mail.
    const falhas = antes.falhas + 1;
    await d.salvar(l.id, falhas < FALHAS_MAX
      ? { etapa: antes.etapa, proximo_em: new Date(agora.getTime() + 3_600_000).toISOString(), ultimo_envio: antes.ultimo_envio, falhas }
      : { falhas });
    return "falhou";
  }
}
