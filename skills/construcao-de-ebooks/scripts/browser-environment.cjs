// shortcut: reconhece o seatbelt do Codex; ampliar se outro executor apresentar o mesmo bloqueio.
if (process.platform === 'darwin' && process.env.CODEX_SANDBOX === 'seatbelt') {
  throw new Error(
    'BROWSER_ENVIRONMENT_BLOCKED: este ambiente do Codex bloqueia a abertura de navegadores no macOS, mesmo sem janela. ' +
    'O teste não foi executado. Use o mesmo comando no Terminal do Mac ou uma ferramenta de navegador autorizada. ' +
    'Não repita aqui, não use Reabrir e não altere as proteções do sistema.'
  );
}
