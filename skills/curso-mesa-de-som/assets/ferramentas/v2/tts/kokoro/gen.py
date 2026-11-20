"""Roteiro (.txt) -> audio .m4a (AAC mono 48 kbps, -16 LUFS), voz masculina pt-BR (Kokoro-82M, voz pm_alex).

Uso (via gen.sh):
  gen.sh roteiro.txt saida.m4a          # um arquivo
  gen.sh pasta_roteiros/ pasta_saida/   # todos os .txt; pula os que ja tem .m4a em dia (retomavel)

Env: TTS_TEMPO (padrao 1.0; 0.93 = 7% mais calmo, 1.05 = 5% mais rapido). Muda a velocidade do proprio Kokoro.
"""
import os, re, sys, wave, zlib, subprocess, tempfile
from pathlib import Path
import numpy as np, mlx.core as mx
from mlx_audio.tts.utils import load_model

HERE = Path(__file__).resolve().parent
FFMPEG = os.path.expanduser("~/.local/bin/ffmpeg")
MODEL, VOZ = "mlx-community/Kokoro-82M-bf16", "pm_alex"
VEL = 0.9 * float(os.environ.get("TTS_TEMPO", "1.0"))  # 0.9 = ~165 palavras/min, ritmo de aula
CPS = 19.0 * VEL      # caracteres/segundo medidos nessa voz (sem as pausas)
MAX_CHARS = 260       # tamanho maximo de um bloco enviado ao modelo
PAUSA_FRASE, PAUSA_PARAGRAFO = 0.25, 0.6

# Pronuncia: o Kokoro le tudo com regras do portugues (espeak pt-br): "gate" vira "gátchi", "DCA" vira "dka".
# Cada troca abaixo foi gerada e transcrita pelo Whisper (sotaque/guia/); o roteiro continua com a grafia normal.
PRON = [(r"\b(?:xis Air|X AIR|xis ér(?!r))", "xis éir"), (r"\b(?:M AIR|ême ér(?!r))", "ême Air"),
        # siglas só com letras romanas em maiúsculas o Kokoro lê como número: MIX = "mil e nove", MC = "mil e cem" (QA da PM5D)
        (r"\bMIX\b", "mix"), (r"\bMC\b", "eme cê"),
        (r"\bfaders\b", "fêiders"), (r"\bfader\b", "fêider"), (r"\breverb\b", "rivérbi"), (r"\bgate\b", "guêit"),
        (r"\bdelay\b", "dilêi"), (r"\binsert\b", "insérti"), (r"\bWi-Fi\b", "uai-fai"), (r"\bphantom\b", "fântom"),
        (r"\bpower\b", "páuer"), (r"\bthreshold\b", "tréshould"), (r"\brelease\b", "rilís"), (r"\bgain\b", "guêin"),
        (r"\bfeedback\b", "fídibéque"), (r"\bplayback\b", "plêibéque"), (r"\bsnapshot\b", "isnépshót"),
        (r"\bpresets\b", "prisséts"), (r"\bpreset\b", "prisét"), (r"\bsafe\b", "sêif"), (r"\bsetup\b", "setâp"), (r"\bratio\b", "rêiciou"), (r"\bmaster\b", "mâster"),
        (r"\bMain LR\b", "Mêin éle érre"), (r"\bMain\b", "Mêin"), (r"\bSelect\b", "silécti"), (r"\bMIDI\b", "mídi"), (r"\bAES\b", "á é ésse"),
        (r"\bRTA\b", "érre tê á"), (r"\bDCAs\b", "dê cê ás"), (r"\bDCA\b", "dê cê á"), (r"\bChannel\b", "Tchénel"),
        (r"\bCompact\b", "Cômpact"), (r"\bBehringer\b", "Bêringuer"), (r"\bHi-Z\b", "rái zí")]


def pronuncia(texto):
    for padrao, troca in PRON:
        texto = re.sub(padrao, troca, texto, flags=re.IGNORECASE)
    return texto


def blocos(texto):
    """[(bloco, pausa_depois)] - agrupa frases ate MAX_CHARS, sem cruzar paragrafo."""
    out = []
    for par in [p for p in re.split(r"\n\s*\n", texto) if p.strip()]:
        frases = re.split(r"(?<=[.!?…:;])\s+", " ".join(par.split()))
        atual = ""
        for f in frases:
            if atual and len(atual) + 1 + len(f) > MAX_CHARS:
                out.append([atual, PAUSA_FRASE]); atual = f
            else:
                atual = f"{atual} {f}".strip()
        out.append([atual, PAUSA_PARAGRAFO])
    return out


def aparar(a, sr, limiar=0.01, margem=0.05):
    idx = np.flatnonzero(np.abs(a) > limiar)
    if not len(idx): return a
    m = int(margem * sr)
    return a[max(0, idx[0] - m): idx[-1] + m]


def falar(model, texto):
    """Um bloco. Semente fixa pelo texto: o decodificador do Kokoro sorteia ruido/fase, assim o audio se repete.
    Refazer com outra semente nao muda texto nem duracao, entao so avisa se a duracao sair implausivel."""
    mx.random.seed(zlib.crc32(texto.encode()))
    a = aparar(np.concatenate([np.array(r.audio) for r in model.generate(
        text=pronuncia(texto), voice=VOZ, lang_code="p", speed=VEL)]), model.sample_rate)
    r = len(a) / model.sample_rate / (len(texto) / CPS)
    if not 0.55 <= r <= 1.8:
        print(f"  ATENCAO: duracao {r:.2f}x do esperado (corte?): {texto[:80]}", file=sys.stderr)
    return a


def gerar(model, roteiro, saida):
    sr = model.sample_rate
    partes = []
    for texto, pausa in blocos(Path(roteiro).read_text()):
        partes += [falar(model, texto), np.zeros(int(pausa * sr), np.float32)]
    partes[-1] = np.zeros(int(0.3 * sr), np.float32)  # final curto
    a = np.concatenate(partes)
    with tempfile.NamedTemporaryFile(suffix=".wav") as tmp:
        w = wave.open(tmp.name, "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((np.clip(a, -1, 1) * 32767).astype("<i2").tobytes()); w.close()
        saida = Path(saida); saida.parent.mkdir(parents=True, exist_ok=True)
        parcial = saida.with_suffix(".parcial.m4a")  # so vira .m4a final se o ffmpeg terminar
        subprocess.run([FFMPEG, "-v", "error", "-y", "-i", tmp.name, "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-ac", "1",
                        "-ar", "24000", "-c:a", "aac", "-b:a", "48k", "-movflags", "+faststart", str(parcial)], check=True)
        os.replace(parcial, saida)
    print(f"{saida}  {len(a) / sr:.0f}s")


def _teste():
    b = blocos("Frase um. Frase dois!\n\n" + "Longa. " * 60)
    assert b[0] == ["Frase um. Frase dois!", PAUSA_PARAGRAFO]
    assert all(len(t) <= MAX_CHARS for t, _ in b) and b[-1][1] == PAUSA_PARAGRAFO
    assert "".join(t for t, _ in b[1:]).count("Longa.") == 60
    assert pronuncia("a família xis ér e ême ér, a xis érre dezoito, o gate e os faders do DCA") == \
        "a família xis éir e ême Air, a xis érre dezoito, o guêit e os fêiders do dê cê á"
    assert pronuncia("pré-fader, Mêin éle érre, X AIR, Main, Main LR") == \
        "pré-fêider, Mêin éle érre, xis éir, Mêin, Mêin éle érre"
    assert pronuncia("a entrada Hi-Z, não tem Hi-Z.") == "a entrada rái zí, não tem rái zí."
    assert pronuncia("Safe, com safe, presets e preset") == "sêif, com sêif, prisséts e prisét"
    print("ok")


def main():
    if sys.argv[1:] == ["--teste"]:
        return _teste()
    if len(sys.argv) != 3:
        sys.exit("uso: gen.sh <roteiro.txt|pasta> <saida.m4a|pasta>")
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    if src.is_dir():
        pares = [(t, dst / f"{t.stem}.m4a") for t in sorted(src.glob("*.txt"))]
        pares = [(t, o) for t, o in pares if not o.exists() or o.stat().st_mtime < t.stat().st_mtime]
    else:
        pares = [(src, dst)]
    if not pares:
        return print("nada a gerar")
    # espeak-ng ignora pasta de dados com 160+ caracteres (e nao aceita symlink): usa copia em caminho curto, com os mesmos dados.
    import espeakng_loader, shutil
    curto = Path.home() / ".cache/curso-tts/espeak-ng-data"
    if not curto.exists(): shutil.copytree(espeakng_loader.get_data_path(), curto)
    espeakng_loader.get_data_path = lambda: str(curto)
    model = load_model(MODEL)
    for t, o in pares:
        gerar(model, t, o)


if __name__ == "__main__":
    main()
