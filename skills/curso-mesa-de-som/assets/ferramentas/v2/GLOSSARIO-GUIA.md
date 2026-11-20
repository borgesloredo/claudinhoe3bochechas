# Guia do glossário da V2

O glossário fica em `tools/v2/glossario.json`. É uma lista de verbetes neste formato:

```json
{"slug": "dbfs", "termo": "dBFS", "variantes": ["dBFS"],
 "definicao": "1 a 3 frases simples.", "exemplo_curto": "opcional"}
```

- `slug`: identificador único, em minúsculas, com hífens (`pre-pos-fader`).
- `termo`: o título que aparece no topo da definição dentro do popup.
- `variantes`: como o termo aparece escrito nos textos. Serve para procurar ocorrências. Não é preciso listar todas para poder marcar o termo.
- `definicao`: 1 a 3 frases para leigo, sem jargão. Se usar outro termo técnico, esse termo também precisa ter verbete.

## Como marcar um termo no popup (i)

Nos arquivos `info/<id>.html`, envolva o termo assim:

```html
<span class="gl" data-t="dbfs">dBFS</span>
```

- `data-t` recebe o **slug**. O texto de dentro fica **exatamente como está na frase** (mesma grafia, plural e maiúsculas).
- Marque só a **1ª ocorrência de cada termo em cada popup**. As seguintes ficam como texto normal.
- Marque só quando a palavra tiver o sentido técnico. Exemplos: “mesa” no sentido de móvel não leva marca; “fonte” no sentido de origem da informação também não.
- Não marque dentro de outra marca, de link ou de título.
- **Nunca** marque nada nos slides (eles não podem mudar) nem nos roteiros de áudio `script/<id>.txt`, que são texto puro para a voz.
- As definições do glossário são texto puro, sem marcas.

### Variantes ambíguas: escolha o slug pelo sentido

| Escrito no texto | Sentido | slug |
|---|---|---|
| delay / Delay | atraso para alinhar microfones ou caixas, sem eco | `delay-alinhamento` |
| delay / Delay / Stereo Delay | efeito de eco | `delay-efeito` |
| driver | programa que o computador precisa para o USB | `driver-software` |
| driver | o alto-falante dentro da caixa | `driver-alto-falante` |
| feedback | apito, microfonia | `microfonia` |
| feedback | repetições do eco do delay | `feedback-delay` |
| pré | pré-amplificador | `pre-amp` |
| pré / pós | envio antes ou depois do fader | `pre-pos-fader` |
| Post Fader | saída direta do canal | `direct-out` |
| Post Fader | ponto de envio ou de saída | `pre-pos-fader` |
| rack | armário ou gabinete de equipamentos, 1U, 3U | `rack` |
| rack | conjunto de efeitos da mesa | `rack-efeitos` |
| tap | ponto de captação de um envio | `tap-point` |
| tap / TAP | bater o tempo do delay | `tap-tempo` |
| PC | Program Change (MIDI) | `program-change` (computador não leva marca) |
| Monitor / monitor | retorno do músico | `monitor-retorno` |
| Monitor Source, Control Room, fone do técnico | escuta do técnico | `fone-tecnico` |
| Mix (do compressor) | mistura entre sinal comprimido e original | `mix-compressor` |
| mix / mixagem | a mistura em geral | `mix` |
| Lock Console / LOCK | trava da superfície da X32/M32 | `lock-console` |
| Lock (Setup › Preamps) | trava do ganho entre duas mesas | `lock-ha-promote` |
| LED | luz indicadora do painel | `led` (barra de nível → `medidor`) |
| Amp | efeito que imita amplificador de guitarra | `amp-sim` |
| amp / amplificador | aparelho que dá força ao sinal para a caixa | `caixa-ativa` |
| Mono | sinal de um canal só (× estéreo) | `estereo-mono` |
| Mono / Center | saída principal extra da X32/M32 | `mono-center` |
| MONO | botão da escuta do técnico | `mono-escuta` |
| REMOTE | chave de rede das X AIR | `chave-remote` |
| Remote | aba do Setup | `setup` |

O script de conferência lista as ambiguidades atuais no fim da saída.

## Como propor um termo novo

1. Antes, procure o termo: `grep -i "<termo>" tools/v2/glossario.json`. Se ele já existe com outra grafia, apenas use o slug que já existe no `data-t` e não proponha nada.
2. Se não existe, crie `tools/v2/glossario-extra-<faixa>.json`, em que `<faixa>` é o trecho que você está escrevendo (ex.: `glossario-extra-cap05-09.json`). O formato é o mesmo: uma lista JSON de verbetes. Não edite o `glossario.json` principal: os extras são juntados a ele no build e, depois de revisados, incorporados a ele (os já incorporados ficam em `_glossario-extras-incorporados/`).
3. Regras do verbete:
   - slug novo, que não exista em nenhum arquivo;
   - definição de 1 a 3 frases, tecnicamente correta, para quem nunca operou uma mesa;
   - todo termo técnico usado na definição precisa ter verbete (já existente ou proposto no mesmo arquivo);
   - nada de nomes de escolas, professores, autores, canais ou fóruns; nada de X16/X12;
   - se houver mais de um jeito correto, a definição descreve o que a coisa é, sem defender um jeito.
4. Confira:

```sh
python3 -I tools/v2/check_glossario.py
```

O comando precisa terminar com `0 erro(s)`. Ele confere o formato, os slugs repetidos, as definições com mais de 3 frases, as siglas sem verbete e as variantes que não aparecem nas fontes, além de listar as ambiguidades.
