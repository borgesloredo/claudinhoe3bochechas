# Pontuacao CTC de hipoteses BR x PT por marcador: delta = logP(variante BR) - logP(variante PT), mesma janela de audio.
import sys, os, json, re, subprocess, numpy as np, torch
import torch.nn.functional as F
from transformers import Wav2Vec2FeatureExtractor, Wav2Vec2ForCTC
from huggingface_hub import hf_hub_download
M = "facebook/wav2vec2-xlsr-53-espeak-cv-ft"
fe = Wav2Vec2FeatureExtractor.from_pretrained(M); model = Wav2Vec2ForCTC.from_pretrained(M).eval()
voc = json.load(open(hf_hub_download(M, "vocab.json")))
FF = os.path.expanduser("~/.local/bin/ffmpeg")
V = ["i", "ɪ", "ɨ", ""]   # vogal depois do slot (max sobre elas, para isolar so a consoante)
# (palavra, ocorrencia, template com X e V, opcao BR, opcao PT)
MK = [("noite", 0, "n oɪ X V", "tʃ", "t"), ("gente", 0, "ʒ eɪ ŋ X V", "tʃ", "t"), ("diferente", 0, "d i f e ɾ eɪ ŋ X V", "tʃ", "t"),
      ("ativo", 0, "a X i v ʊ", "tʃ", "t"), ("teste", 0, "t ɛ s X V", "tʃ", "t"),
      ("tarde", 0, "t a ɾ X V", "dʒ", "d"), ("verdade", 0, "v e ɾ d a X V", "dʒ", "d"), ("diferente", 0, "X V f e ɾ eɪ ŋ t ɨ", "dʒ", "d"),
      ("desligue", 0, "X V z l i ɡ i", "dʒ", "d"), ("estúdio", 0, "ɨ s t u X V ʊ", "dʒ", "d"), ("de", 0, "X V", "dʒ", "d"),
      ("está", 0, "V X t a", "s", "ʃ"), ("estúdio", 0, "V X t u d j ʊ", "s", "ʃ"), ("depois", 0, "d i p oɪ X", "s", "ʃ"),
      ("mesmo", 0, "m e X m ʊ", "z", "ʒ"), ("teste", 0, "t ɛ X t ɨ", "s", "ʃ"), ("simples", 0, "s i m p l i X", "s", "ʃ"),
      ("pois", 0, "p oɪ X", "s", "ʃ"), ("está", 1, "V X t a", "s", "ʃ"), ("vamos", 0, "v ɐ m ʊ X", "s", "ʃ"), ("desligue", 0, "d i X l i ɡ i", "z", "ʒ")]
# reducao: vogal presente x ausente (PT apaga/reduz)
RED = [("desligue", "d V z l i ɡ i", "d z l i ɡ i"), ("verdade", "v V ɾ d a d V", "v ɾ d a d"), ("equipe", "V k i p V", "k i p"),
       ("depois", "d V p oɪ s", "d p oɪ s"), ("deixe", "d eɪ ʃ V", "d eɪ ʃ"), ("teste", "t ɛ s t V", "t ɛ s t"),
       ("diferente", "d i f V ɾ eɪ ŋ t V", "d i f ɾ eɪ ŋ t"), ("para", "p ɐ ɾ ɐ", "p ɾ ɐ"), ("ataque", "ɐ t a k V", "ɐ t a k"),
       ("noite", "n oɪ t V", "n oɪ t"), ("tarde", "t a ɾ d V", "t a ɾ d")]

def load(p):
    r = subprocess.run([FF, "-v", "error", "-i", p, "-ac", "1", "-ar", "16000", "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(r, np.float32).copy()

def score(lp, seq):
    tg = torch.tensor([[voc[s] for s in seq.split()]])
    return -F.ctc_loss(lp[:, None, :], tg, torch.tensor([lp.shape[0]]), torch.tensor([tg.shape[1]]),
                       blank=voc["<pad>"], reduction="sum", zero_infinity=True).item()

def best(lp, tmpl, x):
    return max(score(lp, " ".join(tmpl.replace("X", x).replace("V", v).split())) for v in V)

def best_v(lp, tmpl):  # todas as combinacoes de V (ate 2 slots)
    n = tmpl.split().count("V"); out = -1e9
    import itertools
    for comb in itertools.product([v for v in V if v], repeat=n):
        s = tmpl
        for c in comb: s = s.replace("V", c, 1)
        out = max(out, score(lp, s))
    return out

for audio in sys.argv[1:]:
    nome = os.path.splitext(os.path.basename(audio))[0]
    a = load(audio)
    with torch.no_grad():
        lp = torch.log_softmax(model(fe(a, sampling_rate=16000, return_tensors="pt").input_values).logits[0], -1)
    words = [(re.sub(r"[^\wà-ü]", "", w["word"].lower()), w["start"], w["end"]) for s in json.load(open(os.path.join(os.path.dirname(audio), "..", "wh", nome + ".json")))["segments"] for w in s["words"]]
    def seg(w, occ=0, pad=0.04):
        h = [x for x in words if x[0] == w]
        if len(h) <= occ: return None
        return lp[max(0, int((h[occ][1] - pad) / 0.02)): int((h[occ][2] + pad) / 0.02) + 1]
    out = {}
    for w, occ, tmpl, br, pt in MK:
        s = seg(w, occ)
        out[f"{br}|{pt} {w}{occ or ''}"] = None if s is None else round(best(s, tmpl, br) - best(s, tmpl, pt), 1)
    for w, full, red in RED:
        s = seg(w)
        out[f"vogal {w}"] = None if s is None else round(best_v(s, full) - score(s, red), 1)
    print(json.dumps({"audio": nome, **out}, ensure_ascii=False))
