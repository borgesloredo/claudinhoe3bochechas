-- Esteira de e-mail: 10 e-mails em 120 dias para quem deixou o contato.
-- ANTES DE APLICAR: renomeie este arquivo com data e hora DEPOIS da última migration do seu projeto
-- (supabase migration list) e troque SEU-PROJETO pelo ref do seu projeto no agendamento lá embaixo.

-- Um lead por e-mail e produto.
-- etapa: último e-mail enviado (0 = nenhum ainda). proximo_em: quando sai o próximo (null = esteira acabou).
-- saiu_em: clicou em "não quero mais receber". devolvido_em: o e-mail voltou ou foi marcado como spam.
-- falhas: tentativas que deram erro no e-mail atual (a esteira tenta 3 vezes, de hora em hora).
create table if not exists esteira_leads (
  id bigint generated always as identity primary key,
  email text not null,
  nome text,
  produto text not null,
  origem text,
  etapa smallint not null default 0,
  proximo_em timestamptz default now(),
  ultimo_envio timestamptz,
  saiu_em timestamptz,
  devolvido_em timestamptz,
  falhas int not null default 0,
  criado_em timestamptz not null default now(),
  unique (email, produto)
);
create index if not exists esteira_leads_proximo on esteira_leads (proximo_em) where proximo_em is not null and saiu_em is null;

-- Quem comprou (a esteira para na hora). Preencha pelo webhook da sua plataforma de pagamento ou por um gatilho
-- na sua tabela de pedidos (exemplo no SKILL.md, passo 7).
create table if not exists esteira_compras (
  email text not null,
  produto text not null,
  em timestamptz not null default now(),
  primary key (email, produto)
);

-- Endereços que voltaram (bounce permanente) ou marcaram spam (função esteira-volta).
create table if not exists email_devolvido (
  email text primary key,
  motivo text not null check (motivo in ('devolvido', 'spam')),
  detalhe text,
  email_id text,
  em timestamptz not null default now()
);

-- RLS ligado e sem políticas: só a service role (as Edge Functions) lê e escreve. Ninguém de fora vê os e-mails.
alter table esteira_leads enable row level security;
alter table esteira_compras enable row level security;
alter table email_devolvido enable row level security;

-- Resumo para acompanhar no SQL Editor do Supabase: select * from esteira_resumo;
create or replace view esteira_resumo with (security_invoker = true) as
select produto,
  case when devolvido_em is not null then 'e-mail voltou ou spam'
       when saiu_em is not null then 'pediu para sair'
       when exists (select 1 from esteira_compras c where c.email = l.email and c.produto = l.produto) then 'comprou'
       when proximo_em is null then 'terminou os 10 e-mails'
       when falhas > 0 then 'envio com erro (tentando de novo)'
       else 'recebendo (' || etapa || ' de 10)' end as situacao,
  count(*) as pessoas
from esteira_leads l group by 1, 2 order by 1, 2;

-- Agendamento: chama a esteira-seq de hora em hora, no minuto 17. Ela só envia o que venceu, então a chamada sem
-- senha é inofensiva (verify_jwt = false na função).
create extension if not exists pg_cron with schema pg_catalog;
create extension if not exists pg_net with schema extensions;
select cron.schedule(
  'esteira-seq', '17 * * * *',
  $$select net.http_post(url := 'https://SEU-PROJETO.supabase.co/functions/v1/esteira-seq',
    headers := '{"Content-Type": "application/json"}'::jsonb, body := '{}'::jsonb)$$
);
