# Whisper com timestamps de palavra -> <saida>/<nome>.json. Uso: wts.py <saida> <audio> ...
import os, sys, json, mlx_whisper
for f in sys.argv[2:]:
    r = mlx_whisper.transcribe(f, path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language="pt", word_timestamps=True, condition_on_previous_text=False)
    w = [{"w": x["word"], "s": x["start"], "e": x["end"]} for sg in r["segments"] for x in sg.get("words", [])]
    n = os.path.basename(os.path.dirname(f)) if os.path.basename(f).startswith("audio") else os.path.basename(f).rsplit(".", 1)[0]
    json.dump({"text": r["text"].strip(), "words": w}, open(os.path.join(sys.argv[1], n + ".json"), "w"), ensure_ascii=False)
    open(os.path.join(sys.argv[1], n + ".txt"), "w").write(r["text"].strip() + "\n")
