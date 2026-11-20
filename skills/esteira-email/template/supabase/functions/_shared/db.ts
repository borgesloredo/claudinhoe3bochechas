// Acesso ao banco pela API REST do Supabase com a service role. SUPABASE_URL e SUPABASE_SERVICE_ROLE_KEY já vêm
// prontas dentro de toda Edge Function: não precisa criar esses secrets.
export const rest = (path: string, init: RequestInit = {}) => {
  const key = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
  return fetch(`${Deno.env.get("SUPABASE_URL")}/rest/v1/${path}`, {
    ...init,
    headers: { apikey: key, Authorization: `Bearer ${key}`, "Content-Type": "application/json", ...init.headers },
  });
};

export async function rows<T = Record<string, unknown>>(path: string): Promise<T[]> {
  const r = await rest(path);
  if (!r.ok) throw new Error(`db ${path}: ${r.status} ${await r.text()}`);
  return r.json();
}

export const json = (status: number, body: unknown, headers: Record<string, string> = {}) =>
  new Response(JSON.stringify(body), { status, headers: { ...headers, "Content-Type": "application/json" } });

export const isEmail = (s: unknown): s is string =>
  typeof s === "string" && s.length <= 254 && /^[^\s@<>"',;]+@[^\s@<>"',;]+\.[a-z]{2,}$/i.test(s);

// Comparação em tempo constante (chaves de link e assinaturas).
export function iguais(a: string, b: string) {
  if (a.length !== b.length) return false;
  let d = 0;
  for (let i = 0; i < a.length; i++) d |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return d === 0;
}
