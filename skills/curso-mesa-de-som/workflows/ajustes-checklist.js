export const meta = {
  name: 'curso-ajustes-checklist',
  description: 'Curso de mesa de som: aplica ajustes pedidos pelo dono num portão de aprovação (checklist numerado → corretor → verificador item a item)',
  phases: [{ title: 'Ajustes', detail: 'Corrigir e verificar item a item' }],
}

// args: { R, K, escopo: 'pdf' | 'deck' | 'v2', itens: ['pedido 1', ...] }
const { R, K, escopo, itens } = args
const ALVO = {
  pdf: `PDF: fonte ${R}/06-pdf/curso.html (+ ${R}/05-curso-final.md); regenerar com node ${R}/tools/render-pdf.mjs.`,
  deck: `Deck V1: gerador ${R}/tools/build_slides.py (+ slides_template.html, slides_viz.py, enxugamento.py, bespoke/, notes/); regenerar tudo (deck, checadores, folhas de contato, dump e arquivo único) com sh ${R}/tools/integrar.sh ${R} (se faltar, copie integrar.sh e notas_dump.py de ${K}/assets/ferramentas/). Nunca editar o HTML gerado à mão.`,
  v2: `V2: ${R}/tools/v2/ (build_v2.py, info/, script/, glossario.json); áudios só via ${R}/tools/v2/heavy.sh + qa_batch.sh; rodar build_v2.py, check_identico.mjs e refazer ${R}/entregas/v2-autoestudo.zip. Nunca alterar ${R}/entregas/v1-aulas/.`,
}[escopo]
const CTX = `Leia ${K}/references/regras-do-curso.md. ${ALVO}`
// Modelo por função: Opus decide a qualidade (escrita final, design, motion, técnico); Sonnet confere listas, extrai, pesquisa e testa; Haiku só roda comando.
const OPUS = { model: 'opus' }, SONNET = { model: 'sonnet' }, BARATO = { model: 'sonnet', effort: 'low' }
const VERIFY = { type: 'object', properties: { items: { type: 'array', items: { type: 'object', properties: { n: { type: 'number' }, status: { type: 'string' }, note: { type: 'string' } }, required: ['n', 'status', 'note'] } }, regressions: { type: 'array', items: { type: 'string' } } }, required: ['items', 'regressions'] }
const MAX = 3
let todo = itens.map((t, i) => `${i + 1}. ${t}`).join('\n')
for (let r = 1; r <= MAX && todo; r++) {
  await agent(`${CTX}\nO DONO DO CURSO pediu estes ajustes. Aplique TODOS, no espírito do pedido (se um ajuste afeta outras partes — outros slides, notas, PDF —, propague):\n${todo}`, { label: `ajustar r${r}`, phase: 'Ajustes', ...OPUS })
  const v = await agent(`${CTX}\nVERIFICADOR: para cada pedido numerado, confira no resultado se foi atendido (resolvido | pendente) e aponte regressões causadas pelas mudanças.\n${todo}`, { label: `verificar r${r}`, phase: 'Ajustes', schema: VERIFY, ...SONNET })
  if (!v) continue
  if (!v.items.some(i => i.status === 'pendente') && !v.regressions.length) return { complete: true, rounds: r }
  todo = v.items.filter(i => i.status === 'pendente').map(p => `${p.n}. ${(todo.split('\n').find(l => l.startsWith(p.n + '.')) || '').replace(/^\d+\.\s*/, '')} (verificador: ${p.note})`).concat(v.regressions.map(x => `REGRESSÃO: ${x}`)).join('\n')
}
return { complete: false, pendente: todo }
