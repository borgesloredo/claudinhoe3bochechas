// Os 10 e-mails da esteira, como modelo editável. Mude os textos à vontade: assunto, parágrafos, ordem.
// Mantenha: o botão de compra sem cupom no link, o código do cupom escrito por extenso com "digite no checkout",
// e o parágrafo final com o motivo do e-mail e o link de descadastro (lei e filtros de spam pedem os dois).
// Placeholders de marca, preço e produto vêm de config.ts.
import {
  ASSINATURA, CATALOGO, CUPOM_DA_ETAPA, CUPONS, GARANTIA_DIAS, MARCA, precoCom, PRODUTOS, reais, SITE,
} from "./config.ts";
import { BOTAO, RODAPE } from "./layout.ts";

export const ULTIMA = 10;
const esc = (s: string) => s.replace(/[&<>"']/g, (c) => `&#${c.charCodeAt(0)};`);

// Links com UTM: o seu painel de tráfego (GA4 etc.) mostra as vendas que vieram de cada e-mail.
export const comUtm = (url: string, etapa: number) =>
  `${url}${url.includes("?") ? "&" : "?"}utm_source=email&utm_medium=email&utm_campaign=esteira&utm_content=e${etapa}`;

// origem "checkout": a pessoa começou a compra e não pagou (recuperação). O e-mail 1 muda de texto.
export type Contexto = { nome: string | null; produto: string; sair: string; origem?: string | null };

export function emailDaEtapa(etapa: number, c: Contexto): { assunto: string; html: string } {
  const p = PRODUTOS[c.produto];
  if (!p) throw new Error(`produto ${c.produto}`);
  const nome = esc(p.nome);
  const pagina = comUtm(p.pagina, etapa);
  const checkout = comUtm(p.checkout, etapa);
  const preco = reais(p.preco);
  const brinde = p.brinde ? { titulo: esc(p.brinde.titulo), url: comUtm(p.brinde.url, etapa) } : null;
  const oi = c.nome ? `<p>Oi, ${esc(c.nome.trim().split(/\s+/)[0])}!</p>` : "<p>Oi!</p>";
  const btn = (href: string, texto: string) => `<p><a href="${href}" style="${BOTAO}">${texto}</a></p>`;
  const comprar = btn(checkout, `Comprar por ${preco}`);

  const codigo = CUPOM_DA_ETAPA[etapa];
  // O link abre o checkout pelo preço cheio. O comprador digita o código no campo de cupom.
  const cupom = codigo
    ? `<p>Seu cupom: <b style="font-size:1.2em;letter-spacing:.05em">${codigo}</b>. Ele dá ${CUPONS[codigo]}% de desconto e ${nome} sai por ${reais(precoCom(c.produto, codigo))}, com a mesma garantia de ${GARANTIA_DIAS} dias.</p>
<p>No checkout, digite <b>${codigo}</b> no campo <b>cupom de desconto</b> e aplique antes de pagar.</p>
${btn(checkout, "Ir para o checkout")}`
    : "";

  const compra = c.origem === "checkout";
  const corpos: Record<number, { assunto: string; html: string }> = {
    1: compra
      ? {
        assunto: `Ficou alguma dúvida sobre o ${p.nome}?`,
        html: `${oi}
<p>Você começou a compra do <b>${nome}</b> e ela não foi concluída.</p>
${brinde ? `<p>Se quiser ver antes uma parte, de graça: <b>${brinde.titulo}</b>.</p>\n${btn(brinde.url, "Abrir o material grátis")}` : ""}
<p>Para concluir: <a href="${checkout}">voltar ao pagamento</a> (Pix ou cartão, ${GARANTIA_DIAS} dias de garantia).</p>
<p>Se o pagamento deu algum erro, responda este e-mail que eu te ajudo.</p>`,
      }
      : brinde
      ? {
        assunto: `Seu material grátis: ${p.brinde!.titulo}`,
        html: `${oi}
<p>Aqui está o que você pediu: <b>${brinde.titulo}</b>.</p>
${btn(brinde.url, "Abrir o material")}
<p>Ele é uma parte de <b>${nome}</b>. Se quiser ver o que mais tem: <a href="${pagina}">conhecer ${nome}</a>.</p>`,
      }
      : {
        assunto: `Bem-vindo: ${p.nome}`,
        html: `${oi}
<p>Obrigado pelo interesse em <b>${nome}</b>. Nos próximos dias eu te mando o que mais ajuda a decidir, sem encher a sua caixa.</p>
${btn(pagina, "Ver o conteúdo")}`,
      },
    2: {
      assunto: `O que vem no ${p.nome} completo`,
      html: `${oi}
${brinde ? `<p>Deu para ver o <b>${brinde.titulo}</b>? (<a href="${brinde.url}">abrir de novo</a>)</p>` : ""}
<p>O ${nome} completo traz:</p>
<ul><li>ITEM 1 DO QUE A PESSOA RECEBE;</li>
<li>ITEM 2 DO QUE A PESSOA RECEBE;</li>
<li>ITEM 3 DO QUE A PESSOA RECEBE.</li></ul>
<p>É ${preco}, pagamento único, e o acesso chega no seu e-mail logo depois do pagamento.</p>
${btn(checkout, "Quero o completo")}
<p>Ou leia antes a página: <a href="${pagina}">ver o conteúdo</a>.</p>`,
    },
    3: {
      assunto: `Quem fez o ${p.nome}, e como funciona a compra`,
      html: `${oi}
<p>Eu sou ${esc(ASSINATURA)}. ESCREVA AQUI, EM 2 OU 3 FRASES, QUEM VOCÊ É E POR QUE FEZ ESTE PRODUTO.</p>
<p>A compra é feita no site, por Pix ou cartão. Se não for o que você esperava, você tem ${GARANTIA_DIAS} dias para pedir o dinheiro de volta.</p>
${comprar}
<p>Ficou com alguma dúvida? Responda este e-mail.</p>`,
    },
    4: {
      assunto: `${p.nome}: as perguntas que chegam antes da compra`,
      html: `${oi}
<p>Estas são as dúvidas que mais aparecem:</p>
<p><b>Como eu recebo?</b> O acesso chega no seu e-mail logo depois do pagamento aprovado.</p>
<p><b>Funciona no celular?</b> RESPONDA DE ACORDO COM O SEU PRODUTO.</p>
<p><b>E se não for o que eu esperava?</b> Você tem ${GARANTIA_DIAS} dias para pedir o dinheiro de volta.</p>
${comprar}
<p>Tem outra dúvida? Responda este e-mail.</p>`,
    },
    5: {
      assunto: `${CUPONS[CUPOM_DA_ETAPA[5]] ?? ""}% de desconto no ${p.nome}`,
      html: `${oi}
<p>Você ainda está pensando no <b>${nome}</b>? Separei um desconto para você.</p>
${cupom}`,
    },
    6: {
      assunto: "Procura outra coisa?",
      html: `${oi}
<p>Se o <b>${nome}</b> não é bem o que você precisa agora, veja os outros materiais de ${esc(MARCA)}:</p>
${btn(comUtm(CATALOGO, 6), "Ver todos")}
<p>Se for esse mesmo, ele continua aqui: <a href="${pagina}">ver o conteúdo</a>.</p>`,
    },
    7: brinde
      ? {
        assunto: `Seu material grátis continua disponível`,
        html: `${oi}
<p>O <b>${brinde.titulo}</b> continua no mesmo link, se quiser rever:</p>
${btn(brinde.url, "Abrir o material")}
<p>Quando quiser o ${nome} completo: <a href="${checkout}">comprar por ${preco}</a>.</p>`,
      }
      : {
        assunto: `Ainda dá tempo: ${p.nome}`,
        html: `${oi}
<p>O <b>${nome}</b> continua disponível, pelo mesmo preço de ${preco}.</p>
${comprar}`,
      },
    8: {
      assunto: `Cupom de ${CUPONS[CUPOM_DA_ETAPA[8]] ?? ""}% no ${p.nome}`,
      html: `${oi}
<p>Faz uns dois meses que você conheceu o <b>${nome}</b>. Para facilitar, aumentei o seu desconto.</p>
${cupom}
<p>Ou leia antes a página: <a href="${pagina}">ver o conteúdo</a>.</p>`,
    },
    9: {
      assunto: "Uma pergunta rápida",
      html: `${oi}
<p>Me conta, respondendo este e-mail: o que está te travando hoje? Eu leio e respondo pessoalmente.</p>
<p>Se o ${nome} ainda fizer sentido: <a href="${checkout}">comprar por ${preco}</a>.</p>`,
    },
    10: {
      assunto: `Último e-mail: ${CUPONS[CUPOM_DA_ETAPA[10]] ?? ""}% no ${p.nome}`,
      html: `${oi}
<p>Este é o último e-mail sobre o <b>${nome}</b>. Não quero lotar a sua caixa de entrada.</p>
<p>Antes de parar, o maior desconto que eu dou:</p>
${cupom}
<p>Se precisar de ajuda, é só responder este e-mail.</p>`,
    },
  };
  const corpo = corpos[etapa];
  if (!corpo) throw new Error(`etapa ${etapa}`);
  const fim = `<p>Um abraço,<br><b>${esc(ASSINATURA)}</b></p>${RODAPE}
<p>Você recebe este e-mail porque ${compra ? "começou a compra de" : "pediu informações sobre"} ${nome} em ${esc(SITE.replace(/^https?:\/\//, ""))}. Os e-mails param sozinhos em alguns meses, ou na hora em que você pedir: <a href="${c.sair}">não quero mais receber</a>.</p>`;
  return { assunto: corpo.assunto, html: `${corpo.html}\n${fim}` };
}
