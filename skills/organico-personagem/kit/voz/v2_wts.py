# Whisper com timestamps de palavra -> <saida>/<nome>.json. Uso: wts.py <saida> <audio> ...
# mlx-whisper no Mac; faster-whisper (modelo small, já baixado) no servidor do Hermes.
import os, sys, json
try:
    import mlx_whisper

    def transcreve(f):
        r = mlx_whisper.transcribe(f, path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language="pt", word_timestamps=True, condition_on_previous_text=False)
        return r["text"], [{"w": x["word"], "s": x["start"], "e": x["end"]} for sg in r["segments"] for x in sg.get("words", [])]
except ImportError:
    from faster_whisper import WhisperModel
    M = WhisperModel(os.environ.get("GEN_WHISPER_MODELO", "small"), device="cpu", compute_type="int8")

    def transcreve(f):
        segs, _ = M.transcribe(f, language="pt", word_timestamps=True, condition_on_previous_text=False)
        segs = list(segs)
        return "".join(s.text for s in segs), [{"w": x.word, "s": x.start, "e": x.end} for s in segs for x in (s.words or [])]

for f in sys.argv[2:]:
    texto, w = transcreve(f)
    n = os.path.basename(os.path.dirname(f)) if os.path.basename(f).startswith("audio") else os.path.basename(f).rsplit(".", 1)[0]
    json.dump({"text": texto.strip(), "words": w}, open(os.path.join(sys.argv[1], n + ".json"), "w"), ensure_ascii=False)
    open(os.path.join(sys.argv[1], n + ".txt"), "w").write(texto.strip() + "\n")
