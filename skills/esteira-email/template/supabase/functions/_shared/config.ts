// ===== EDITE ESTE ARQUIVO PRIMEIRO =====
// Tudo o que muda de um negócio para outro fica aqui: marca, domínio, produtos, preços, cupons e o calendário.
// Os textos dos 10 e-mails ficam em emails.ts. Antes do deploy, scripts/checar.sh recusa se sobrar algum
// marcador de exemplo (SUA MARCA, SEU-DOMINIO, SEU NOME, NOME DO PRODUTO...).

export const MARCA = "SUA MARCA";
// Endereço do seu site, sem barra no fim. Os links dos e-mails apontam para ele.
export const SITE = "https://SEU-DOMINIO.com.br";
// Quem assina os e-mails ("Um abraço, <ASSINATURA>").
export const ASSINATURA = "SEU NOME";
// Linha do vendedor no rodapé (nome ou empresa, documento, cidade). Ajuda na entrega e passa confiança.
export const RODAPE_LEGAL = "SEU NOME OU EMPRESA · CNPJ 00.000.000/0001-00 · CIDADE-UF";
export const GARANTIA_DIAS = 7;
// Página com todos os seus produtos (e-mail 6). Sem catálogo, deixe a página inicial.
export const CATALOGO = `${SITE}/`;
// Link de descadastro. Melhor no seu domínio (um redirecionamento /sair/ para a função esteira-lead, ver SKILL.md),
// porque link *.supabase.co em e-mail de marketing pesa para cair no spam. Sem o redirecionamento, use
// "https://<ref-do-projeto>.supabase.co/functions/v1/esteira-lead".
export const SAIR_URL = `${SITE}/sair/`;

export type Produto = {
  nome: string; // nome curto, aparece no assunto
  preco: number; // preço cheio em reais
  pagina: string; // página de venda
  checkout: string; // checkout SEM cupom no link: o comprador digita o código
  brinde?: { titulo: string; url: string }; // o material grátis que a pessoa pediu (isca). Sem brinde, apague a linha.
};

// Uma entrada por produto. A chave (ex.: "meu-produto") é o que o formulário manda no campo "produto".
export const PRODUTOS: Record<string, Produto> = {
  "meu-produto": {
    nome: "NOME DO PRODUTO",
    preco: 97,
    pagina: `${SITE}/produto/`,
    checkout: `${SITE}/produto/checkout/`,
    brinde: { titulo: "NOME DO BRINDE", url: `${SITE}/brinde/` },
  },
};

// Os cupons. Crie cada código, com o MESMO percentual, em todos os produtos e ofertas da sua plataforma de
// pagamento (Hotmart, Kiwify, Eduzz, checkout próprio) ANTES de ligar a esteira. O comprador digita o código no
// checkout: o link do e-mail nunca leva o cupom pronto.
export const CUPONS: Record<string, number> = { VOLTA10: 10, VOLTA20: 20, VOLTA30: 30 };

// Dias depois da inscrição em que sai cada e-mail (1 a 10). Semanal no começo, depois mensal, depois para.
export const DIAS = [0, 2, 5, 9, 14, 21, 30, 60, 90, 120];
// Em qual e-mail entra cada cupom. Regra: o desconto nunca desce ao longo da esteira (se o brinde já dá 20%,
// nenhum e-mail depois dele oferece menos que 20%).
export const CUPOM_DA_ETAPA: Record<number, string> = { 5: "VOLTA10", 8: "VOLTA20", 10: "VOLTA30" };

// Preço com o cupom, arredondado em centavos (97 com 20% = 77,60).
export const precoCom = (produto: string, cupom: string) =>
  Math.round(PRODUTOS[produto].preco * (100 - CUPONS[cupom])) / 100;
export const reais = (v: number) => `R$ ${v.toFixed(2).replace(".", ",")}`;
