# Transcreve vários áudios num só processo (modelo carregado uma vez). Uso: <python do mlx-whisper> qa_whisper.py <saida_dir> <a.m4a> ...
import os, sys
import mlx_whisper
out = sys.argv[1]
for f in sys.argv[2:]:
    r = mlx_whisper.transcribe(f, path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language="pt",
                               condition_on_previous_text=False)  # com o texto anterior, o fim do arquivo entrava em loop ("O próximo capítulo. O próximo capítulo...")
    open(os.path.join(out, os.path.basename(f).rsplit(".", 1)[0] + ".txt"), "w").write(r["text"].strip() + "\n")
    print("ok", os.path.basename(f), flush=True)
