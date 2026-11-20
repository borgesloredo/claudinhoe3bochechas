// Gera os 10 e-mails como arquivos HTML para revisar no navegador, sem enviar nada e sem rede.
// deno run --allow-env --allow-write scripts/previa.ts [--teste] [pasta-de-saida]
// --teste: só confere que os 10 montam (com e sem recuperação de checkout) e não grava arquivo.
import { PRODUTOS } from "../supabase/functions/_shared/config.ts";
import { ULTIMA } from "../supabase/functions/_shared/emails.ts";
import { type Lead, montarEmail } from "../supabase/functions/_shared/envio.ts";

const teste = Deno.args.includes("--teste");
const saida = Deno.args.find((a) => !a.startsWith("--")) ?? "previa";
if (!Deno.env.get("ESTEIRA_SEGREDO")) Deno.env.set("ESTEIRA_SEGREDO", "so-para-a-previa-local-000000");
if (!teste) await Deno.mkdir(saida, { recursive: true });

let n = 0;
for (const produto of Object.keys(PRODUTOS)) {
  for (const origem of ["formulario", "checkout"]) {
    const l: Lead = { id: 1, email: "teste@exemplo.com", nome: "Ana Souza", produto, origem, etapa: 0, proximo_em: null,
      ultimo_envio: null, criado_em: new Date().toISOString(), saiu_em: null, falhas: 0 };
    for (let e = 1; e <= ULTIMA; e++) {
      if (origem === "checkout" && e > 1) break; // só o e-mail 1 muda na recuperação
      const m = await montarEmail(l, e);
      n++;
      if (teste) continue;
      const nome = `${saida}/${produto}-e${String(e).padStart(2, "0")}${origem === "checkout" ? "-checkout" : ""}.html`;
      await Deno.writeTextFile(nome, m.html.replace("<title></title>", `<title>${m.subject}</title>`));
      console.log(`${nome}  |  ${m.subject}`);
    }
  }
}
console.log(teste ? `ok: ${n} e-mails montados, nenhum enviado` : `${n} arquivos em ${saida}/`);
