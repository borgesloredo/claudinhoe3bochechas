"""Motor de voz: falas (.txt) -> narração .m4a (AAC mono 48 kHz, -16 LUFS). Gemini TTS, voz Puck.
Um pedido por chamada com todas as falas, para manter a entonação e poupar cota. O áudio é cortado em falas
pelo alinhamento de palavras do Whisper. As chaves vêm só do ambiente (GEMINI*KEY*); no 429 passa para a próxima.
"""
import os, re, sys, shutil, json, time, base64, difflib, subprocess, tempfile, unicodedata, urllib.request, urllib.error
from pathlib import Path

HERE = Path(__file__).resolve().parent
RECORTA = False
FFMPEG = shutil.which("ffmpeg") or os.path.expanduser("~/.local/bin/ffmpeg")
FFPROBE = os.path.join(os.path.dirname(FFMPEG), "ffprobe")
WHISPER_PY = os.path.expanduser("~/.local/share/uv/tools/mlx-whisper/bin/python")
MODELO, VOZ = "gemini-3.8-flash-tts", "Puck"
# Estilo aprovado em produção. Não mude sem gerar uma amostra para ouvir.
ESTILO = ("Locutor brasileiro de Reels do Instagram, homem de uns 30 anos, de São Paulo, português do Brasil nativo, sem sotaque "
          "de Portugal nem estrangeiro. Voz média, um pouco rouca. Narração rápida e com punch, umas quatro palavras por segundo, "
          "conversando como quem explica algo legal para um amigo. Sobe a entonação na pergunta, dá ênfase forte nas palavras-chave, "
          "pausas bem curtas, respiração natural e relaxada. Nada robótico, nada de locutor de rádio.")
# Mesmo filtro do gen.py antigo, com as pontas aparadas antes (silencio < -50 dB).
APARA = "silenceremove=start_periods=1:start_threshold=-50dB,areverse,silenceremove=start_periods=1:start_threshold=-50dB,areverse"
# loudnorm de 1 passagem deixava falas curtas (1-3 s) da Gemini em -17,7 a -18,8 LUFS: mede o trecho aparado e aplica o ganho exato.
# Limitador a -2,5 dB (como o gen.py) para o pico ficar abaixo de -1,5 dBTP depois do AAC.
ALVO, LIMITE = -16.0, "alimiter=limit=0.75:level=false"

# Pronuncia: so no texto enviado a voz; o roteiro e o .txt ficam com a grafia normal. Teste cada troca no Whisper.
PRON = []

# Checagem ANTES do pedido (cada pedido gasta 1 de 10 da cota diaria). Padroes que a voz errou em producao.
# --aceito-risco pula a checagem.
RISCO = [
    (r"(?<![\w.(])(?![aeoAEOéÉ]\b)[A-Za-z](?![\w.)])", "letra solta (\"o i explica\" saiu \"o IN\"): escreva o nome da coisa (\"o ícone de informação\")"),
    (r"\b[Ee]stá\b", "\"Está\" sai \"Tá\": escreva \"Tá\" (registro de Reels)"),
    (r"\b(Aperte|Toque|Gire|Ligue|Deslize|Salve)\b", "imperativo formal sai coloquial (\"Aperte\" saiu \"Aperta\"): escreva \"Aperta\", \"Toca\", \"Gira\"..."),
    (r"\b[Pp]atch\b", "\"patch\" sai \"pet\": fale \"roteamento\" e deixe PATCH so na tela"),
    (r"\b(main|send|bus|mute|gain)\b", "termo em inglês minúsculo (\"main\" saiu \"man\"): use o termo em português (\"saída principal\") ou a sigla da tela em maiúsculas"),
]
# Formas faladas que valem como a escrita na conferencia (homofonos e registro coloquial; nao sao erro de audio).
EQUIV = {"hz": "hertz", "khz": "quilohertz", "ghz": "gigahertz", "ta": "esta", "tao": "estao", "pra": "para", "pro": "para o", "aperta": "aperte", "sena": "cena"}


def pronuncia(t):
    for p, r in PRON:
        t = re.sub(p, r, t)
    return t


def riscos(falas):
    return [f"  fala {i + 1}: \"{m.group(0)}\" -> {dica}" for i, f in enumerate(falas) for p, dica in RISCO for m in re.finditer(p, f)]


UNI = "zero um dois tres quatro cinco seis sete oito nove dez onze doze treze quatorze quinze dezesseis dezessete dezoito dezenove".split()
DEZ = "_ _ vinte trinta quarenta cinquenta sessenta setenta oitenta noventa".split()


def extenso(w):  # Whisper escreve "32" / "250" onde o roteiro diz "trinta e dois" / "duzentos e cinquenta"
    return " ".join(_num(int(w))) if w.isdigit() and int(w) < 1000000 else w


def norm(t):  # palavras comparaveis entre roteiro e Whisper
    t = unicodedata.normalize("NFKD", t.lower()).encode("ascii", "ignore").decode()
    return " ".join(EQUIV.get(w, extenso(w)) for w in re.sub(r"[^\w]+", " ", t).split()).split()


def conferir(fala, palavras, ini, fim):
    """Diferencas entre o texto e o que o Whisper ouviu no trecho [ini, fim] do take. Lista vazia = fala certa."""
    ouvido = norm(" ".join(p["w"] for p in palavras if p["s"] >= ini - 0.05 and p["e"] <= fim + 0.05))
    esperado = norm(fala)
    sm = difflib.SequenceMatcher(None, esperado, ouvido, autojunk=False)
    return [f"\"{' '.join(esperado[a:b])}\" -> \"{' '.join(ouvido[c:d])}\"" for op, a, b, c, d in sm.get_opcodes() if op != "equal"]


def CHAVES():  # todas as GEMINI*KEY* do ambiente, sem repetir, em ordem de nome (GEMINI_API_KEY primeiro)
    return list(dict.fromkeys(v.strip("\"' ") for n, v in sorted(os.environ.items()) if n.startswith("GEMINI") and "KEY" in n and v.strip("\"' ")))


def pedir(texto):
    corpo = {"model": MODELO,
             "input": [{"type": "user_input", "content": [{"type": "text", "text": texto,
                        "annotations": [{"type": "speech_metadata", "style": ESTILO}]}]}],
             "response_format": {"type": "audio"}, "generation_config": {"speech_config": [{"voice": VOZ}]}}
    chaves, k, esgotadas = CHAVES(), 0, set()
    if not chaves:
        sys.exit("nenhuma chave GEMINI*KEY* no ambiente (use voz.sh)")
    for tent in range(6 + len(chaves)):
        req = urllib.request.Request("https://generativelanguage.googleapis.com/v1beta/interactions", data=json.dumps(corpo).encode(),
                                     headers={"x-goog-api-key": chaves[k], "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=600) as r:
                d = json.load(r)
            break
        except urllib.error.HTTPError as e:
            msg = e.read().decode(errors="replace")[:200]
            if e.code in (429, 403) and len(esgotadas | {k}) < len(chaves):  # cota acabou (429) ou projeto sem plano gratis (403): passa para a proxima, sem esperar
                esgotadas.add(k); velha, k = k, next(i for i in range(len(chaves)) if i not in esgotadas)
                print(f"  HTTP {e.code} na chave {velha + 1} de {len(chaves)}; usando a chave {k + 1}", flush=True); continue
            if e.code == 429 and "PerDay" in msg:
                sys.exit(f"cota do dia acabou nas {len(chaves)} chaves (volta em ~20 h): {msg}")
            if e.code in (429, 500, 503) and tent < 5 + len(chaves):
                esgotadas.clear()
                print(f"  HTTP {e.code} na chave {k + 1}, nova tentativa em 60 s: {msg}", flush=True); time.sleep(60); continue
            sys.exit(f"Gemini HTTP {e.code} (chave {k + 1} de {len(chaves)}): {msg}")
    else:  # todas as tentativas terminaram em continue (429 em rodizio): sair com mensagem, nao com UnboundLocalError
        sys.exit(f"Gemini sem resposta apos {6 + len(chaves)} tentativas (429 em todas as chaves): {msg}")
    aud = [c for s in d.get("steps", []) if s.get("type") == "model_output" for c in s.get("content", []) if c.get("type") == "audio"]
    if not aud:
        sys.exit("Gemini respondeu sem audio: " + json.dumps(d)[:300])
    return base64.b64decode(aud[-1]["data"])


def loudness(arq, filtro="anull"):
    r = subprocess.run([FFMPEG, "-nostats", "-i", str(arq), "-af", filtro + ",ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True)
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", r.stderr)[-1])


def normaliza(src, saida):
    """Ganho exato para ALVO LUFS + limitador -> AAC mono 48 kHz 160k. Grava em .parcial e so troca no fim."""
    g = ALVO - loudness(src)
    for _ in range(2):  # o limitador come um pouco do ganho em fala com pico alto: uma correcao basta
        g += ALVO - loudness(src, f"volume={g:.2f}dB,{LIMITE}")
    parcial = Path(saida).with_suffix(".parcial.m4a")
    subprocess.run([FFMPEG, "-v", "error", "-y", "-i", str(src), "-af", f"volume={g:.2f}dB,{LIMITE}", "-ac", "1", "-ar", "48000",
                    "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(parcial)], check=True)
    os.replace(parcial, saida)


def vale(take, c, a, b):
    """Instante mais silencioso (janela de 10 ms) entre a e b. O tempo de palavra do Whisper erra alguns décimos: cortar
    no meio do intervalo caía dentro da última sílaba, e o resto dela tocava de novo no começo da fala seguinte ("trava e volta")."""
    a, b = max(0.0, a), max(a + 0.02, b)
    r = subprocess.run([FFMPEG, "-v", "error", "-ss", f"{a:.3f}", "-to", f"{b:.3f}", "-i", str(take), "-af",
                        "aresample=16000,asetnsamples=160,astats=metadata=1:reset=1,ametadata=print:key=lavfi.astats.Overall.RMS_level:file=-",
                        "-f", "null", "-"], capture_output=True, text=True).stdout
    db = [float(x) if "inf" not in x else -120.0 for x in re.findall(r"RMS_level=(\S+)", r)]
    if not db:
        return c
    # pausa entre frases = trecho quieto mais LONGO (uma consoante também afunda, mas por 20-40 ms); empate -> mais perto do corte estimado
    lim = -45.0 if min(db) <= -45 else min(db) + 12; runs, i = [], 0  # voz fica entre -15 e -30 dB; pausa abaixo de -45
    while i < len(db):
        if db[i] <= lim:
            j = i
            while j + 1 < len(db) and db[j + 1] <= lim:
                j += 1
            runs.append((i, j)); i = j + 1
        else:
            i += 1
    i, j = max(runs, key=lambda r: (r[1] - r[0], -abs(a + (r[0] + r[1] + 1) * 0.005 - c)))
    return a + (i + j + 1) * 0.005


def nivel(take, t):
    """dB RMS do take em 20 ms em volta de t."""
    r = subprocess.run([FFMPEG, "-v", "error", "-ss", f"{max(0, t - 0.01):.3f}", "-t", "0.02", "-i", str(take), "-af",
                        "astats=metadata=1,ametadata=print:key=lavfi.astats.Overall.RMS_level:file=-", "-f", "null", "-"], capture_output=True, text=True).stdout
    v = re.findall(r"RMS_level=(\S+)", r)
    return -120.0 if not v or "inf" in v[-1] else float(v[-1])


def refina(take, cs):
    """Leva cada corte interno para o vale de energia mais próximo (até 0,35 s), sem cruzar os vizinhos."""
    out = cs[:]
    for i in range(1, len(cs) - 1):
        out[i] = vale(take, cs[i], max(cs[i] - 0.35, out[i - 1] + 0.15), min(cs[i] + 0.35, cs[i + 1] - 0.15))
    return out


_U = "zero um dois tres quatro cinco seis sete oito nove dez onze doze treze quatorze quinze dezesseis dezessete dezoito dezenove".split()
_D = "_ _ vinte trinta quarenta cinquenta sessenta setenta oitenta noventa".split()
_C = "_ cento duzentos trezentos quatrocentos quinhentos seiscentos setecentos oitocentos novecentos".split()


def _num(n):
    """Número -> palavras sem acento (250 -> duzentos e cinquenta)."""
    if n < 20: return [_U[n]]
    if n < 100: return [_D[n // 10]] + (["e"] + _num(n % 10) if n % 10 else [])
    if n == 100: return ["cem"]
    if n < 1000: return [_C[n // 100]] + (["e"] + _num(n % 100) if n % 100 else [])
    m, r = divmod(n, 1000)
    return (["mil"] if m == 1 else _num(m) + ["mil"]) + ((["e"] if r < 100 or r % 100 == 0 else []) + _num(r) if r else [])


def cortes(falas, palavras, dur):
    """Instantes de corte entre falas: meio do intervalo entre a ultima palavra da fala i e a primeira da i+1 (alinhamento difflib)."""
    ref, dona = [], []
    for i, f in enumerate(falas):
        w = norm(f); ref += w; dona += [i] * len(w)
    # o Whisper escreve "250 Hz" onde o roteiro diz "duzentos e cinquenta hertz": sem casar, o corte caía no meio do número
    hyp, dono = [], []
    for j, p in enumerate(palavras):
        for w in (norm(p["w"]) or [""]):
            hyp.append(w); dono.append(j)
    tempo = {}  # indice no roteiro -> (inicio, fim) da palavra casada
    for a, b, n in difflib.SequenceMatcher(None, ref, hyp, autojunk=False).get_matching_blocks():
        for k in range(n):
            tempo[a + k] = (palavras[dono[b + k]]["s"], palavras[dono[b + k]]["e"])
    cs = []
    for i in range(len(falas) - 1):
        fim = [tempo[k][1] for k in range(len(ref)) if dona[k] == i and k in tempo]
        ini = [tempo[k][0] for k in range(len(ref)) if dona[k] == i + 1 and k in tempo]
        if not fim or not ini:
            sys.exit(f"alinhamento falhou entre a fala {i + 1} e a {i + 2} (palavras nao reconhecidas); gere essas falas separadas")
        e, s = max(fim), min(ini)
        cs.append((e + s) / 2 if s > e else s)
    assert cs == sorted(cs), f"cortes fora de ordem: {cs}"
    return [0.0] + cs + [dur]


def main():
    if sys.argv[1:] == ["--teste"]:
        return _teste()
    if sys.argv[1:2] == ["--renormaliza"]:  # so ajusta o volume de .m4a ja gerados (mantem a data, para nao mascarar fala pendente)
        for a in sys.argv[2:]:
            st = os.stat(a)
            with tempfile.NamedTemporaryFile(suffix=".wav") as tmp:
                subprocess.run([FFMPEG, "-v", "error", "-y", "-i", a, "-ac", "1", "-ar", "48000", tmp.name], check=True)
                normaliza(tmp.name, a)
            os.utime(a, (st.st_atime, st.st_mtime)); print(f"{a}  {loudness(a):.1f} LUFS", flush=True)
        return
    args = sys.argv[1:]
    forca = "--aceito-risco" in args
    global RECORTA
    RECORTA = "--recorta" in args  # refaz os cortes do take salvo (sem pedido): para corrigir falas já geradas
    args = [a for a in args if a not in ("--aceito-risco", "--recorta")]
    if not args or len(args) % 2:
        sys.exit("uso: gen_gemini.sh <texto.txt> <saida.m4a> [<texto2.txt> <saida2.m4a> ...]")
    pares = [(Path(t), Path(s)) for t, s in zip(args[::2], args[1::2])]
    recorta = pares[0][1].parent / "qa" / "gemini-take.json" if RECORTA else None
    velhas = [s for t, s in pares if RECORTA or not (s.exists() and s.stat().st_mtime >= t.stat().st_mtime)]
    if not velhas:
        return print("nada a gerar (saidas em dia)")
    falas = [pronuncia(" ".join(t.read_text().split())) for t, _ in pares]
    if not all(falas):
        sys.exit("texto vazio em " + ", ".join(str(t) for (t, _), f in zip(pares, falas) if not f))
    r = riscos(falas)
    if r and not forca:
        sys.exit("Texto com risco de erro na voz (nenhum pedido gasto). Reescreva o .txt ou rode com --aceito-risco:\n" + "\n".join(r))
    qa = pares[0][1].parent / "qa"; qa.mkdir(parents=True, exist_ok=True)
    take = qa / "gemini-take.wav"
    if RECORTA:
        assert take.exists() and recorta.exists(), f"sem take salvo em {qa}"
    else:
        take.write_bytes(pedir(" ".join(falas)))
    dur = float(subprocess.run([FFPROBE, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(take)],
                               capture_output=True, text=True, check=True).stdout)
    # Whisper sempre: serve para cortar as falas e para conferir cada uma (antes so rodava com 2+ falas)
    if not RECORTA:
        subprocess.run([WHISPER_PY, "-I", str(HERE / "v2_wts.py"), str(qa), str(take)], check=True, env={**os.environ, "HF_HUB_OFFLINE": "1"},
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    palavras = json.load(open(qa / "gemini-take.json"))["words"]
    ts = [0.0, dur] if len(pares) == 1 else refina(take, cortes(falas, palavras, dur))
    altos = [i for i in range(1, len(ts) - 1) if vale(take, ts[i], ts[i] - 0.02, ts[i] + 0.02) and nivel(take, ts[i]) > -40]
    erradas = []
    for i, (t, s) in enumerate(pares):
        if s not in velhas:
            continue
        with tempfile.NamedTemporaryFile(suffix=".wav") as tmp:
            subprocess.run([FFMPEG, "-v", "error", "-y", "-ss", f"{ts[i]:.3f}", "-to", f"{ts[i + 1]:.3f}", "-i", str(take), "-af",
                            APARA + ",afade=t=in:d=0.012,areverse,afade=t=in:d=0.03,areverse,adelay=delays=100:all=1", "-ac", "1", "-ar", "48000", tmp.name], check=True)
            normaliza(tmp.name, s)
        dif = conferir(falas[i], palavras, ts[i], ts[i + 1])
        dif += [f"corte em som alto antes da fala {k + 1} (pode picotar)" for k in altos if k in (i, i + 1) and k == i + 1]
        print(f"{s}  {ts[i + 1] - ts[i]:.1f}s  {'OK' if not dif else 'CONFERIR: ' + '; '.join(dif)}", flush=True)
        if dif:
            erradas.append(t)
    (qa / "conferencia.txt").write_text("".join(f"{t}\n" for t in erradas))
    if erradas:
        # Saida 2: as falas foram gravadas, mas o Whisper ouviu outra coisa. Ouca antes de regerar: pode ser so grafia.
        print(f"{len(erradas)} fala(s) a conferir (lista em {qa / 'conferencia.txt'}). Se errou de verdade: "
                 f"touch {' '.join(map(str, erradas))} e rode o video de novo (1 pedido).", file=sys.stderr)
        sys.exit(2)


def _teste():
    assert norm("250 Hz") == "duzentos e cinquenta hertz".split() and norm("100") == ["cem"] and norm("1500") == "mil e quinhentos".split(), norm("1500")
    assert pronuncia("do pré ao P.A.") == "do pré ao P.A." or PRON, "PRON"
    w = [{"w": x, "s": i * 0.5, "e": i * 0.5 + 0.4} for i, x in enumerate(" Oi, tudo bem? Sim. Garanta o seu.".split())]
    assert cortes(["Oi, tudo bem?", "Sim.", "Garanta o seu."], w, 4.0) == [0.0, 1.45, 1.95, 4.0], cortes(["Oi, tudo bem?", "Sim.", "Garanta o seu."], w, 4.0)
    assert riscos(["Garanta o seu.", "Tá tudo no curso, do pré ao P.A.", "O (i) explica."]) == [], riscos(["Garanta o seu.", "Tá tudo no curso, do pré ao P.A.", "O (i) explica."])
    assert len(riscos(["Salva o patch."])) == 1 and riscos(["Salva o roteamento."]) == []
    assert len(riscos(["o i explica", "Está pronto.", "Aperte SAVE.", "o main"])) == 4, riscos(["o i explica", "Está pronto.", "Aperte SAVE.", "o main"])
    assert conferir("Aperte e tá pronto.", [{"w": x, "s": 0, "e": 1} for x in "Aperta e está pronto.".split()], 0, 1) == []
    assert conferir("Serum trinta e dois e dezesseis", [{"w": x, "s": 0, "e": 1} for x in "Serum 32 e 16".split()], 0, 1) == []
    assert conferir("Na WING.", [{"w": x, "s": 0, "e": 1} for x in "Na Win.".split()], 0, 1) == ['"wing" -> "win"']
    assert CHAVES(), "nenhuma chave GEMINI*KEY* no ambiente (use voz.sh)"
    print(f"{len(CHAVES())} chave(s) Gemini diferentes carregadas")
    print("ok")


if __name__ == "__main__":
    main()
