// Moldura de todos os e-mails (fundo, cabeçalho com a marca, cartão do texto, rodapé) e a cópia em texto puro.
// Só tabelas e estilo inline: Outlook/Hotmail ignoram quase todo CSS.
// Cores: TUDO escuro com texto quase branco, ou TUDO claro com texto quase preto, cada bloco com fundo e cor
// declarados. Cartão branco em fundo escuro deu errado de verdade: o modo escuro do Hotmail pintou o cartão de
// preto e deixou o texto escuro ilegível. Texto cinza no rodapé também ficou ilegível.
import { MARCA, RODAPE_LEGAL, SITE } from "./config.ts";

export const RODAPE = "<!--rodape-->";
export const COR = { fundo: "#0b0e11", cartao: "#161b21", texto: "#eef2f5", acento: "#ff9a2e", link: "#ffad57", rodape: "#e4e8ec" };
const FONTE = "Arial,Helvetica,sans-serif";

export const BOTAO = `display:inline-block;background:${COR.acento};color:#060708;padding:15px 28px;border-radius:8px;` +
  `text-decoration:none;font:bold 16px/1.2 ${FONTE};mso-padding-alt:0`;

function estilizar(html: string, cor: string, tamanho: number) {
  return html
    .replace(/<p>/g, `<p style="margin:0 0 16px;font:${tamanho}px/1.6 ${FONTE};color:${cor}">`)
    .replace(/<p style="/g, `<p style="margin:0 0 16px;font-family:${FONTE};line-height:1.6;color:${cor};`)
    .replace(/<a href="([^"]+)">/g, `<a href="$1" style="color:${COR.link};text-decoration:underline">`)
    .replace(/<ul>/g, `<ul style="margin:0 0 16px;padding-left:20px;font:${tamanho}px/1.6 ${FONTE};color:${cor}">`);
}

// Linha de prévia escondida que aparece ao lado do assunto na caixa de entrada.
export function previa(html: string) {
  const ps = [...html.matchAll(/<p[^>]*>([\s\S]*?)<\/p>/g)].map((m) => m[1].replace(/<[^>]+>/g, "").replace(/\s+/g, " ").trim());
  const t = ps.find((p) => p && !/^Oi[,!]/.test(p)) ?? "";
  return t.length > 140 ? `${t.slice(0, 137)}…` : t;
}

export function moldura(html: string) {
  const [corpo, rodape = ""] = html.split(RODAPE);
  const dominio = SITE.replace(/^https?:\/\//, "");
  return `<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="dark"><meta name="supported-color-schemes" content="dark"><title></title></head>
<body style="margin:0;padding:0;background:${COR.fundo}">
<div style="display:none;max-height:0;overflow:hidden;opacity:0;color:${COR.fundo}">${previa(corpo)}</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="${COR.fundo}" style="background:${COR.fundo}">
<tr><td align="center" style="padding:28px 12px 36px">
<table role="presentation" width="600" cellpadding="0" cellspacing="0" border="0" style="width:100%;max-width:600px">
<tr><td style="padding:0 8px 20px;font:bold 15px/1 ${FONTE};letter-spacing:4px;color:${COR.acento}">${MARCA.toUpperCase()}</td></tr>
<tr><td bgcolor="${COR.cartao}" style="background:${COR.cartao};border-radius:12px;padding:32px 32px 16px;border-top:4px solid ${COR.acento};color:${COR.texto};font:16px/1.6 ${FONTE}">
${estilizar(corpo, COR.texto, 16)}
</td></tr>
<tr><td style="padding:24px 8px 0;color:${COR.rodape}">
${estilizar(rodape, COR.rodape, 14)}
<p style="margin:0;font:13px/1.6 ${FONTE};color:${COR.rodape}">${RODAPE_LEGAL} · <a href="${SITE}/" style="color:${COR.link}">${dominio}</a></p>
</td></tr>
</table></td></tr></table></body></html>`;
}

// Cópia em texto puro: e-mail só com HTML pontua pior nos filtros de spam (Outlook/Hotmail).
export function textoDe(html: string) {
  const ent: Record<string, string> = { amp: "&", lt: "<", gt: ">", quot: '"', nbsp: " " };
  return html.replace(RODAPE, "")
    .replace(/<a\s[^>]*href="([^"]+)"[^>]*>([\s\S]*?)<\/a>/gi, (_, h, t) => `${t.replace(/<[^>]+>/g, "").trim()}: ${h}`)
    .replace(/<br\s*\/?>/gi, "\n").replace(/<\/(p|div|h\d|li|tr)>/gi, "\n\n").replace(/<li[^>]*>/gi, "- ")
    .replace(/<[^>]+>/g, "")
    .replace(/&(#\d+|[a-z]+);/gi, (m, e) => e[0] === "#" ? String.fromCharCode(Number(e.slice(1))) : ent[e.toLowerCase()] ?? m)
    .replace(/[ \t]+\n/g, "\n").replace(/\n{3,}/g, "\n\n").trim();
}
